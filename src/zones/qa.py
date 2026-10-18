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
