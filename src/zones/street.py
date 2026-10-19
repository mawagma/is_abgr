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


def classify_segments(seg, adj, th, gap, seed="max_density"):
    """lage je Segment ('' = keine) und Liste der Nebenlagen (weitere 1a-Ketten ohne Verbindung zur 1a).
    seed: max_density = 1a-Kette mit dem dichtesten Segment; strongest_chain = 1a-Kette mit der größten
    gewichteten POI-Summe (robust gegen kurze Hotspots, z. B. Mall-Mieter an einer Hintergasse)."""
    d, bs = seg["density"].to_numpy(), seg["brand_share"].to_numpy()
    ok1a = (d >= th["lage_1a"]["min_density"]) & (bs >= th["lage_1a"].get("min_brand_share", 0.0))
    lage = np.full(len(seg), "", dtype=object)
    if not ok1a.any():
        return lage, []
    if seed == "strongest_chain":
        w, rest, z1 = seg["poi_w"].to_numpy(), set(np.flatnonzero(ok1a)), set()
        while rest:
            c = _chain({rest.pop()}, ok1a, adj, gap)
            rest -= c
            if w[list(c)].sum() > w[list(z1)].sum():
                z1 = c
    else:
        z1 = _chain({int(np.flatnonzero(ok1a)[np.argmax(d[ok1a])])}, ok1a, adj, gap)
    ok = d >= th["lage_1b"]["min_density"]
    if "min_centrality_pct" in th["lage_1b"]:  # 1b nur auf zentralen Laufachsen
        ok &= seg["central_pct"].to_numpy() >= th["lage_1b"]["min_centrality_pct"]
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


def centrality_pct(seg, adj, cfg, core=None):
    """Lokale Netzzentralität (Betweenness über das Segmentnetz, Gewicht = Länge) als Perzentil.
    Nur Segmente im Umkreis centrality_radius_m um core (die 1a) – fußläufiges Zentrum statt Durchgangsstraßen
    der ganzen Stadt. Außerhalb = 0. Misst Laufachsen: über welche Abschnitte viele kürzeste Wege führen.
    Perzentil nur unter den Segmenten außerhalb der 1a (in Kleinstädten ist die 1a selbst die zentralste Achse)."""
    import networkx as nx
    st, L = cfg["street"], seg["length_m"].to_numpy()
    inside = np.ones(len(seg), bool) if core is None else (
        seg.distance(shapely.union_all(seg.geometry.to_numpy()[list(core)])) <= st["centrality_radius_m"]).to_numpy()
    idx = np.flatnonzero(inside)
    G = nx.Graph()
    G.add_nodes_from(idx)
    G.add_edges_from((i, j, {"w": (L[i] + L[j]) / 2}) for i in idx for j in adj[i] if i < j and inside[j])
    bc = nx.betweenness_centrality(G, weight="w", k=min(st["centrality_samples"], len(idx)), seed=st["centrality_seed"])
    cand = [i for i in idx if core is None or i not in set(core)]
    out = np.zeros(len(seg))
    if cand:
        out[cand] = pd.Series([bc[i] for i in cand]).rank(pct=True).to_numpy()
    return out


def relative_thresholds(seg, cfg):
    """Schwellen relativ zur Stadt: Bezug = Dichte und Filialanteil der dichtesten relative_reference_m Straße."""
    st = cfg["street"]
    s = seg.sort_values("density", ascending=False)
    top = s[s["length_m"].cumsum() <= st["relative_reference_m"]]
    D = float(np.average(top["density"], weights=top["length_m"])) if len(top) else 0.0
    B = float(top["brand_count"].sum() / top["poi_count"].sum()) if top["poi_count"].sum() else 0.0
    f = st["relative_thresholds"]
    th = {"lage_1a": {"min_density": round(f["lage_1a"]["density"] * D, 2),
                      "min_brand_share": round(f["lage_1a"]["brand_share"] * B, 3)},
          "lage_1b": {"min_density": round(f["lage_1b"]["density"] * D, 2),
                      "min_centrality_pct": f["lage_1b"]["centrality_pct"]},
          "lage_2": {"min_density": round(f["lage_2"]["density"] * D, 2)}}
    return th, {"D_ref": round(D, 2), "B_ref": round(B, 3)}


def lage_lengths_km(seg, lage):
    return {l: seg["length_m"].to_numpy()[lage == l].sum() / 1000 for l in LAGEN}


def reference_labels(seg, cfg):
    """Referenzlage je Segment ('' = keine) aus der Expertenabgrenzung der Stadt, sonst None."""
    st = cfg["street"]
    path = (st.get("reference") or {}).get(cfg["city"])
    if not path:
        return None
    ref = gpd.read_file(path).to_crs(seg.crs)
    mid = seg.geometry.interpolate(0.5, normalized=True)
    lab = np.full(len(seg), "", dtype=object)
    for l in ("lage_1b", "lage_1a"):  # 1a zuletzt: gewinnt bei Überschneidung
        g = ref.loc[ref["lage"] == l].union_all()
        if not g.is_empty:
            lab[(mid.distance(g) <= st["reference_match_m"]).to_numpy()] = l
    return lab


def reference_match(seg, lage, ref):
    """Precision/Recall/F1 über Segmentlänge je Lage."""
    L, out = seg["length_m"].to_numpy(), {}
    for l in ("lage_1a", "lage_1b"):
        pred, truth = lage == l, ref == l
        tp, p, r = L[pred & truth].sum(), L[pred].sum(), L[truth].sum()
        out[l] = {"precision": round(tp / p, 3) if p else 0.0, "recall": round(tp / r, 3) if r else 0.0,
                  "f1": round(2 * tp / (p + r), 3) if p + r else 0.0}
    return out


def calibrate(seg, adj, cfg, ref=None):
    """Dichteschwellen nacheinander für 1a, 1b, 2; absteigend (1a ≥ 1b ≥ 2).
    Mit Referenz: 1a und 1b per Gittersuche über alle Segmentdichten mit maximalem F1 zur Referenz.
    Ohne Referenz (und immer für die 2-Lage): Bisektion auf die Mitte von target_ranges_km."""
    st = cfg["street"]
    th = copy.deepcopy(st["thresholds"])
    log = []
    hi_cap = float(seg["density"].max())
    cls = lambda: classify_segments(seg, adj, th, st["max_gap_segments"], st["seed"])[0]
    for l in LAGEN:
        if ref is not None and l != "lage_2":
            best = None
            for t in sorted({round(x, 2) for x in seg["density"] if 0 < x <= hi_cap}):
                th[l]["min_density"] = t
                m = reference_match(seg, cls(), ref)[l]
                if best is None or m["f1"] > best[1]["f1"]:
                    best = (t, m)
            th[l]["min_density"] = hi_cap = best[0]
            log.append({"lage": l, "verfahren": "Referenz (max. F1)", "start": st["thresholds"][l]["min_density"],
                        "schwelle": best[0], **best[1]})
            continue
        target = float(np.mean(st["target_ranges_km"][l]))
        lo, hi = 0.0, hi_cap
        best = (np.inf, th[l]["min_density"], None)
        for _ in range(st["calibration_iterations"]):
            mid = (lo + hi) / 2
            th[l]["min_density"] = mid
            km = lage_lengths_km(seg, classify_segments(seg, adj, th, st["max_gap_segments"], st["seed"])[0])[l]
            if abs(km - target) < best[0]:
                best = (abs(km - target), mid, km)
            if km > target:
                lo = mid
            else:
                hi = mid
        th[l]["min_density"] = round(best[1], 2)
        hi_cap = th[l]["min_density"]
        log.append({"lage": l, "verfahren": "Bisektion auf Ziel-km", "ziel_km": target, "schwelle": th[l]["min_density"],
                    "start": st["thresholds"][l]["min_density"], "erreicht_km": round(best[2] or 0, 3)})
    return th, log


def street_polygons(seg, cfg, obstacles=None):
    """Segmente je Lage puffern (flache Enden), vereinigen, Löcher füllen; Ringe 1b −= 1a, 2 −= 1a ∪ 1b.
    obstacles (Gebäude, Malls): werden abgezogen → nur Straßenraum; Teile ohne Kontakt zur Achse entfallen."""
    st = cfg["street"]
    cum = []
    for k in range(3):
        sel = seg[seg["lage"].isin(LAGEN[:k + 1])]
        g = shapely.union_all(sel.geometry.buffer(st["buffer_m"], cap_style="flat").to_numpy())
        if not g.is_empty:
            g = _fill_holes(g, st["min_hole_ha"] * 1e4)
            if obstacles is not None:
                axes = shapely.union_all(sel.geometry.to_numpy())
                g = shapely.union_all([p for p in shapely.get_parts(g.difference(obstacles)) if p.intersects(axes)])
        cum.append(g)
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


def run_street(streets, pois, cfg, auto_calibrate=None, obstacles=None):
    """Kern-Pipeline ohne Netz (Tests): Segmente → Zuordnung → Kennwerte → (Kalibrierung) → Lagen → Polygone."""
    st = cfg["street"]
    seg, nb, adj = build_segments(streets, cfg)
    pois = assign_pois(pois, seg, cfg)
    seg = segment_metrics(seg, pois, nb, cfg)
    auto = st["auto_calibrate"] if auto_calibrate is None else auto_calibrate
    ref = reference_labels(seg, cfg)
    base = st["calibrated_thresholds"] if st.get("use_calibrated_thresholds") else st["thresholds"]
    rel = None
    if st.get("threshold_mode") == "relative":
        base, rel = relative_thresholds(seg, cfg)
    # Zentralität hängt von der 1a ab (Umkreis); die 1a selbst nutzt sie nicht → erst 1a bestimmen
    seg["central_pct"] = 0.0
    pre = classify_segments(seg, adj, base, st["max_gap_segments"], st["seed"])[0]
    seg["central_pct"] = centrality_pct(seg, adj, cfg, np.flatnonzero(pre == "lage_1a") if (pre == "lage_1a").any() else None)
    th, log = calibrate(seg, adj, cfg, ref) if auto else (copy.deepcopy(base), [])
    lage, neben = classify_segments(seg, adj, th, st["max_gap_segments"], st["seed"])
    if ref is not None and st.get("lagen_from_reference"):
        # Expertenabgrenzung übernehmen: 1a/1b aus der Referenz, 2-Lage regelbasiert daran angeschlossen
        fixed = set(np.flatnonzero(ref != ""))
        ok = seg["density"].to_numpy() >= th["lage_2"]["min_density"]
        ok[list(fixed)] = True
        lage = np.full(len(seg), "", dtype=object)
        lage[list(_chain(fixed, ok, adj, st["max_gap_segments"]))] = "lage_2"
        lage[ref != ""] = ref[ref != ""]
    seg["lage"] = lage
    targets = {l: list(v) for l, v in st["target_ranges_km"].items()}
    if ref is not None:  # km-Ziele aus der Referenz ableiten
        seg["ref_lage"] = ref
        tol = st["reference_tolerance"]
        for l in ("lage_1a", "lage_1b"):
            km = seg.loc[ref == l, "length_m"].sum() / 1000
            targets[l] = [round(km * (1 - tol), 2), round(km * (1 + tol), 2)]
    zones = zone_attributes(street_polygons(seg, cfg, obstacles), seg)
    return {"segments": seg, "pois": pois, "zones": zones, "nebenlagen": nebenlagen_gdf(seg, neben),
            "thresholds": th, "relative_reference": rel, "calibration": log, "auto_calibrate": auto, "targets_km": targets,
            "reference_match": reference_match(seg, lage, ref) if ref is not None else None}


def load_buildings(center, cfg):
    """Gebäudeumrisse im Kreis building_query_radius_m um das Zentrum (fester Abfragekreis → stabiler Cache).
    shortcut: Lagen außerhalb des Kreises werden nicht um Gebäude bereinigt; bei größeren Städten Radius erhöhen."""
    crs = cfg["crs_metric"]
    circle = gpd.GeoSeries([center.buffer(cfg["street"]["building_query_radius_m"])], crs=crs).to_crs(4326).iloc[0]
    b = features(circle, {"building": True}, cfg)
    return b.loc[b.geom_type.isin(["Polygon", "MultiPolygon"]), "geometry"]
