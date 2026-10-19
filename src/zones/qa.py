"""Prüfungen. hard=True → Exit-Code ≠ 0 bei Fehlschlag."""
from itertools import combinations


def iou(a, b):
    u = a.union(b).area
    return a.intersection(b).area / u if u else 0.0


def run_checks(zones, cfg, sens=(), plaus=None):
    """zones: GeoDataFrame mit Attributen; sens: [(label, z1_geom)]; plaus: {name: GeoSeries}."""
    q, out = cfg["qa"], []
    add = lambda name, hard, ok, detail: out.append(
        {"check": name, "hard": hard, "ok": bool(ok), "status": "OK" if ok else ("FEHLER" if hard else "WARNUNG"),
         "detail": detail})
    g = list(zones.geometry)
    ok = len(g) == 3 and all(x.is_valid and not x.is_empty for x in g)
    add("Genau 3 Zonen, gültig, nicht leer", True, ok,
        f"{len(g)} Zonen; leer: {[z for z, x in zip(zones.zone_id, g) if x.is_empty]}")
    ov = max((a.intersection(b).area for a, b in combinations(g, 2)), default=0.0)
    add(f"Überlappung < {q['max_overlap_m2']} m²", True, ov < q["max_overlap_m2"], f"max. {ov:.4f} m²")
    for z, m2 in cfg.get("min_zone_m2", {}).items():
        a = zones.loc[zones["zone_id"] == z].area.sum()
        add(f"{z}: Fläche ≥ {m2} m²", True, a >= m2, f"{a:.0f} m²")
    if "poi_density_ha" in zones:
        d = zones["poi_density_ha"].round(2).tolist()
        add("POI-Dichte Z1 > Z2 > Z3", True, len(d) == 3 and d[0] > d[1] > d[2], " > ".join(map(str, d)) + " POI/ha")
    for z, x in zip(zones.zone_id, g):
        n = len(getattr(x, "geoms", [x]))
        add(f"{z}: ein Polygon", False, x.geom_type == "Polygon", f"{x.geom_type}, {n} Teil(e)")
    for z, x in zip(zones.zone_id, g):
        pp = 4 * 3.141592653589793 * x.area / x.length**2 if x.length else 0.0
        add(f"{z}: Polsby-Popper ≥ {q['min_compactness']}", False, pp >= q["min_compactness"], f"{pp:.3f}")
    for label, z1s in sens:
        v = iou(g[0], z1s)
        add(f"Sensitivität {label}: IoU(Z1) ≥ {q['min_iou']}", False, v >= q["min_iou"], f"IoU = {v:.3f}")
    for name, geoms in (plaus or {}).items():
        hit = len(geoms) > 0 and bool(geoms.intersects(g[0]).any())
        add(f"Plausibilität: Z1 schneidet „{name}“", False, hit, f"{len(geoms)} OSM-Objekt(e) mit diesem Namen")
    return out


def street_checks(res, cfg):
    """Prüfungen Street-Modus. Warnungen zu Zielgrößen nennen die Schwelle und die Richtung."""
    st, q, out = cfg["street"], cfg["qa"], []
    add = lambda name, hard, ok, detail: out.append(
        {"check": name, "hard": hard, "ok": bool(ok), "status": "OK" if ok else ("FEHLER" if hard else "WARNUNG"),
         "detail": detail})
    z = res["zones"]
    g = list(z.geometry)
    may_be_empty = {"lage_1b"} if st.get("allow_empty_1b") else set()  # Kleinstädte: 1a + 2-Lage genügt
    empty = [l for l, x in zip(z["lage"], g) if x.is_empty]
    add("Genau 3 Lagen, gültig, nicht leer" + (" (1b darf leer sein)" if may_be_empty else ""), True,
        len(g) == 3 and all(x.is_valid for x in g) and set(empty) <= may_be_empty, f"leer: {empty}")
    ov = max((a.intersection(b).area for a, b in combinations(g, 2)), default=0.0)
    add(f"Überlappung < {q['max_overlap_m2']} m²", True, ov < q["max_overlap_m2"], f"max. {ov:.4f} m²")
    d = [v for v, l in zip(z["density_per_100m"], z["lage"]) if l not in empty]  # leere 1b überspringen
    add("Dichte 1a > 1b > 2", True, all(a > b for a, b in zip(d, d[1:])),
        " > ".join(map(str, z["density_per_100m"])) + " je 100 m")
    th = res["thresholds"]
    for r in z.itertuples():
        lo, hi = res["targets_km"][r.lage]
        dens = f"{r.lage}.min_density ({th[r.lage]['min_density']})"
        tip = "" if lo <= r.length_km <= hi else (f" → {dens} erhöhen" if r.length_km > hi else f" → {dens} senken"
            + (f" oder lage_1a.min_brand_share ({th['lage_1a']['min_brand_share']}) senken"
               if r.lage == "lage_1a" else ""))
        add(f"{r.lage}: Länge {lo}–{hi} km", False, lo <= r.length_km <= hi, f"{r.length_km} km{tip}")
        if "target_ranges_ha" not in st:
            continue
        lo_a, hi_a = st["target_ranges_ha"][r.lage]
        in_len = lo <= r.length_km <= hi
        tip = "" if lo_a <= r.area_ha <= hi_a else (
            f" → buffer_m ({st['buffer_m']}) {'verkleinern' if r.area_ha > hi_a else 'vergrößern'}" if in_len
            else " → folgt der Länge (siehe oben)")
        add(f"{r.lage}: Fläche {lo_a}–{hi_a} ha", False, lo_a <= r.area_ha <= hi_a, f"{r.area_ha} ha{tip}")
    for l, m in (res.get("reference_match") or {}).items():
        add(f"{l}: Übereinstimmung mit Referenz (F1 ≥ 0.8)", False, m["f1"] >= 0.8,
            f"F1 {m['f1']}, Precision {m['precision']}, Recall {m['recall']}")
    seg = res["segments"]
    names = set(seg.loc[seg["lage"] == "lage_1a", "street"].dropna())
    for n in st["plausibility"].get(cfg["city"], []):
        add(f"Plausibilität: 1a enthält „{n}“", False, n in names,
            f"{(seg[(seg['street'] == n) & (seg['lage'] == 'lage_1a')]['length_m'].sum()):.0f} m in 1a")
    return out
