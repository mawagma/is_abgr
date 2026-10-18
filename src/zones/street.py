"""Straßenbasierte Lageabgrenzung (1a / 1b / 2-Lage) über Straßenabschnitte mit Geschäftsbesatz."""
import copy

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.ops import substring

from .pois import features
from .polygons import _fill_holes, _polygonal

LAGEN = ["lage_1a", "lage_1b", "lage_2"]


def load_streets(aoi, cfg):
    """Benannte bzw. relevante Wege im Suchraum, ohne Tunnel, metrisch und auf den Suchraum zugeschnitten."""
    st = cfg["street"]
    aoi_ll = gpd.GeoSeries([aoi], crs=cfg["crs_metric"]).to_crs(4326).iloc[0]
    raw = features(aoi_ll, {"highway": st["highway"] + st["highway_named_only"]}, cfg)
    # shortcut: Fußgängerflächen (area=yes, z. B. Plätze) werden übersprungen; POIs dort snappen an die Nachbarstraße
    raw = raw[raw.geom_type.isin(["LineString", "MultiLineString"])]
    name = raw["name"] if "name" in raw else pd.Series(None, index=raw.index, dtype=object)
    ok = raw["highway"].isin(st["highway"]) | (raw["highway"].isin(st["highway_named_only"]) & name.notna())
    if "tunnel" in raw:
        ok &= raw["tunnel"].isna() | (raw["tunnel"] == "no")
    streets = gpd.GeoDataFrame({"name": name[ok], "highway": raw.loc[ok, "highway"]},
                               geometry=raw.loc[ok].geometry.intersection(aoi), crs=raw.crs)
    return streets[~streets.is_empty].reset_index(drop=True)


def build_segments(streets, cfg):
    """Gleichnamige verbundene Wege zusammenführen, in Abschnitte von segment_length_m teilen (Rest an den letzten).
    Liefert Segmente, Endpunkt-Nachbarn (Glättung) und Berührungs-Nachbarn (Zusammenhang inkl. Kreuzungen)."""
    st = cfg["street"]
    L = st["segment_length_m"]
    chains = []
    named = streets[streets["name"].notna()]
    for name, grp in named.groupby("name"):
        merged = shapely.line_merge(shapely.union_all(grp.geometry.to_numpy()))
        chains += [(name, g) for g in shapely.get_parts(merged)]
    chains += [(None, g) for g in shapely.get_parts(streets.loc[streets["name"].isna()].geometry.to_numpy())]
    rows = []
    for chain_id, (name, line) in enumerate(chains):
        n = max(1, int(line.length // L))
        for i in range(n):
            end = (i + 1) * L if i < n - 1 else line.length
            rows.append({"street": name, "chain_id": chain_id, "geometry": substring(line, i * L, end)})
    seg = gpd.GeoDataFrame(rows, geometry="geometry", crs=streets.crs)
    seg = seg[seg.length > 0].reset_index(drop=True)
    seg.insert(0, "seg_id", np.arange(len(seg)))
    seg["length_m"] = seg.length

    ends = {}
    for i, g in enumerate(seg.geometry):
        for x, y in (g.coords[0], g.coords[-1]):
            ends.setdefault((round(x, 1), round(y, 1)), set()).add(i)
    nb = [set() for _ in range(len(seg))]
    for ids in ends.values():
        for i in ids:
            nb[i] |= ids - {i}
    adj = [set(s) for s in nb]
    a, b = shapely.STRtree(seg.geometry.to_numpy()).query(seg.geometry.to_numpy(), predicate="dwithin",
                                                         distance=st["touch_tolerance_m"])
    for i, j in zip(a, b):
        if i != j:
            adj[i].add(int(j))
    seg["neighbors"] = [",".join(map(str, sorted(s))) for s in nb]
    return seg, nb, adj


def assign_pois(pois, seg, cfg):
    """Jeder POI an das nächste Segment (≤ snap_max_dist_m), jeder POI genau einmal."""
    j = gpd.sjoin_nearest(pois, seg[["seg_id", "geometry"]], max_distance=cfg["street"]["snap_max_dist_m"],
                          distance_col="snap_dist_m")
    j = j[~j.index.duplicated()]
    pois = pois.copy()
    pois["seg_id"] = j["seg_id"].reindex(pois.index)
    pois["snap_dist_m"] = j["snap_dist_m"].reindex(pois.index)
    return pois


def _hood(nb, i, hops):
    out, ring = {i}, {i}
    for _ in range(hops):
        ring = set().union(*(nb[r] for r in ring)) - out
        out |= ring
    return out


def segment_metrics(seg, pois, nb, cfg):
    """density = gewichtete POIs je 100 m; brand_share = Filialanteil; beides über Nachbarsegmente geglättet."""
    st = cfg["street"]
    seg = seg.copy()
    a = pois.dropna(subset=["seg_id"]).groupby("seg_id").agg(
        poi_w=("weight", "sum"), poi_count=("weight", "size"), brand_count=("chain", "sum"))
    for c in a.columns:
        seg[c] = seg["seg_id"].map(a[c]).fillna(0).astype(float)
    # Stummel (< segment_length_m) mit voller Länge rechnen, sonst erzeugt ein POI an 5 m Straße Dichte 20
    denom = np.maximum(seg["length_m"].to_numpy(), st["segment_length_m"])
    raw_d = seg["poi_w"].to_numpy() / denom * 100
    cnt, brd = seg["poi_count"].to_numpy(), seg["brand_count"].to_numpy()
    seg["density_raw"] = raw_d
    seg["brand_share_raw"] = np.divide(brd, cnt, out=np.zeros_like(cnt), where=cnt > 0)
    dens, bs = np.empty(len(seg)), np.empty(len(seg))
    for i in range(len(seg)):
        h = list(_hood(nb, i, st["smoothing_neighbors"]))
        dens[i] = raw_d[h].mean()
        bs[i] = brd[h].sum() / cnt[h].sum() if cnt[h].sum() else 0.0
    seg["density"], seg["brand_share"] = dens, bs
    return seg


def _chain(seeds, ok, adj, gap):
    """Zusammenhang über ok-Segmente; bis zu `gap` nicht erfüllende Segmente dazwischen werden überbrückt
    (und der Lage zugeschlagen, z. B. Kreuzungen)."""
    comp, todo = set(seeds), list(seeds)
    while todo:
        u = todo.pop()
        frontier, seen = [(u, ())], {u}
        for depth in range(gap + 1):
            nxt = []
            for v, path in frontier:
                for w in adj[v]:
                    if w in seen or w in comp:
                        continue
                    seen.add(w)
                    if ok[w]:
                        comp.add(w)
                        comp.update(path)
                        todo.append(w)
                    elif depth < gap:
                        nxt.append((w, path + (w,)))
            frontier = nxt
    return comp


def classify_segments(seg, adj, th, gap):
    """lage je Segment ('' = keine) und Liste der Nebenlagen (weitere 1a-Ketten ohne Verbindung zur 1a)."""
    d, bs = seg["density"].to_numpy(), seg["brand_share"].to_numpy()
    ok1a = (d >= th["lage_1a"]["min_density"]) & (bs >= th["lage_1a"].get("min_brand_share", 0.0))
    lage = np.full(len(seg), "", dtype=object)
    if not ok1a.any():
        return lage, []
    seed = int(np.flatnonzero(ok1a)[np.argmax(d[ok1a])])
    z1 = _chain({seed}, ok1a, adj, gap)
    ok = d >= th["lage_1b"]["min_density"]
    ok[list(z1)] = True
    z12 = _chain(z1, ok, adj, gap)
    ok = d >= th["lage_2"]["min_density"]
    ok[list(z12)] = True
    z123 = _chain(z12, ok, adj, gap)
    lage[list(z123)] = "lage_2"
    lage[list(z12)] = "lage_1b"
    lage[list(z1)] = "lage_1a"
    neben, rest = [], set(np.flatnonzero(ok1a)) - z1
    while rest:
        c = _chain({rest.pop()}, ok1a, adj, gap)
        rest -= c
        neben.append(sorted(c))
    return lage, neben


def lage_lengths_km(seg, lage):
    return {l: seg["length_m"].to_numpy()[lage == l].sum() / 1000 for l in LAGEN}


def calibrate(seg, adj, cfg):
    """Dichteschwelle je Lage (nacheinander 1a, 1b, 2) per Bisektion, bis die Straßenlänge möglichst nah an der
    Mitte von target_ranges_km liegt. Schwellen bleiben absteigend (1a ≥ 1b ≥ 2)."""
    st = cfg["street"]
    th = copy.deepcopy(st["thresholds"])
    log = []
    hi_cap = float(seg["density"].max())
    for l in LAGEN:
        target = float(np.mean(st["target_ranges_km"][l]))
        lo, hi = 0.0, hi_cap
        best = (np.inf, th[l]["min_density"], None)
        for _ in range(st["calibration_iterations"]):
            mid = (lo + hi) / 2
            th[l]["min_density"] = mid
            km = lage_lengths_km(seg, classify_segments(seg, adj, th, st["max_gap_segments"])[0])[l]
            if abs(km - target) < best[0]:
                best = (abs(km - target), mid, km)
            if km > target:
                lo = mid
            else:
                hi = mid
        th[l]["min_density"] = round(best[1], 2)
        hi_cap = th[l]["min_density"]
        log.append({"lage": l, "ziel_km": target, "schwelle": th[l]["min_density"],
                    "start": st["thresholds"][l]["min_density"], "erreicht_km": round(best[2] or 0, 3)})
    return th, log


def street_polygons(seg, cfg):
    """Segmente je Lage puffern (flache Enden), vereinigen, Löcher füllen; Ringe 1b −= 1a, 2 −= 1a ∪ 1b."""
    st = cfg["street"]
    cum = []
    for k in range(3):
        sel = seg[seg["lage"].isin(LAGEN[:k + 1])]
        g = shapely.union_all(sel.geometry.buffer(st["buffer_m"], cap_style="flat").to_numpy())
        cum.append(_fill_holes(g, st["min_hole_ha"] * 1e4) if not g.is_empty else g)
    m = cfg["min_part_m2"]
    z1 = _polygonal(cum[0], m)
    z2 = _polygonal(cum[1].difference(z1), m)
    z3 = _polygonal(cum[2].difference(z1.union(z2)), m)
    return gpd.GeoDataFrame({"lage": LAGEN}, geometry=[z1, z2, z3], crs=seg.crs)


def zone_attributes(zones, seg):
    z = zones.copy()
    rows = []
    for l in z["lage"]:
        s = seg[seg["lage"] == l]
        length, n = s["length_m"].sum(), s["poi_count"].sum()
        rows.append({"length_km": round(length / 1000, 3), "poi_count": int(n),
                     "density_per_100m": round(s["poi_w"].sum() / length * 100, 2) if length else 0.0,
                     "brand_share": round(s["brand_count"].sum() / n, 3) if n else 0.0,
                     "street_names": "; ".join(sorted(s["street"].dropna().unique()))})
    z["area_ha"] = (z.area / 1e4).round(2)
    for c in rows[0]:
        z[c] = [r[c] for r in rows]
    return z[["lage", "length_km", "area_ha", "poi_count", "density_per_100m", "brand_share", "street_names",
              "geometry"]]


def nebenlagen_gdf(seg, neben):
    rows = []
    for k, ids in enumerate(neben, 1):
        s = seg.iloc[ids]
        n = s["poi_count"].sum()
        rows.append({"nebenlage_id": k, "length_km": round(s["length_m"].sum() / 1000, 3), "poi_count": int(n),
                     "brand_share": round(s["brand_count"].sum() / n, 3) if n else 0.0,
                     "lage_im_ergebnis": ", ".join(sorted(set(s["lage"]) - {""})) or "keine",
                     "street_names": "; ".join(sorted(s["street"].dropna().unique())),
                     "geometry": shapely.union_all(s.geometry.to_numpy())})
    return gpd.GeoDataFrame(rows, geometry="geometry", crs=seg.crs) if rows else gpd.GeoDataFrame(
        {"nebenlage_id": [], "geometry": []}, geometry="geometry", crs=seg.crs)


def run_street(streets, pois, cfg, auto_calibrate=None):
    """Kern-Pipeline ohne Netz (Tests): Segmente → Zuordnung → Kennwerte → (Kalibrierung) → Lagen → Polygone."""
    st = cfg["street"]
    seg, nb, adj = build_segments(streets, cfg)
    pois = assign_pois(pois, seg, cfg)
    seg = segment_metrics(seg, pois, nb, cfg)
    auto = st["auto_calibrate"] if auto_calibrate is None else auto_calibrate
    th, log = calibrate(seg, adj, cfg) if auto else (copy.deepcopy(st["thresholds"]), [])
    lage, neben = classify_segments(seg, adj, th, st["max_gap_segments"])
    seg["lage"] = lage
    zones = zone_attributes(street_polygons(seg, cfg), seg)
    return {"segments": seg, "pois": pois, "zones": zones, "nebenlagen": nebenlagen_gdf(seg, neben),
            "thresholds": th, "calibration": log, "auto_calibrate": auto}
