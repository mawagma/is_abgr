"""python -m zones.cli --city "Heilbronn, Germany" [--classification jenks|quantile|equal_area]"""
import argparse
import hashlib
import json
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import pandas as pd
import shapely
import yaml

from .aoi import build_aoi
from .classify import assign_zones, classify, limit_area
from .export import write_all, write_street, zone_attributes
from .grid import build_grid
from .polygons import zone_polygons
from .pois import categorize, configure_osmnx, context, fetch_osm, mall_polygons
from .qa import run_checks, street_checks
from .street import commercial_areas, load_buildings, load_squares, load_streets, run_street


def build_zones(pois, aoi, cfg, method):
    """Kern-Pipeline ohne Netz: Raster → Glättung → Klassen → Zusammenhang → Polygone."""
    sm = cfg["smoothing"]
    cells = build_grid(aoi, pois, cfg, cfg["h3_resolution"], sm["radius_m"], sm["sigma_m"])
    cells, islands = assign_zones(classify(cells, cfg, method))
    if cfg.get("max_area_ha") and method != "equal_area":
        cells = limit_area(cells, cfg["max_area_ha"])
    return {"cells": cells, "islands": islands, "zones": zone_polygons(cells, cfg)}


def slug(city):
    s = city.split(",")[0].strip().lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().replace(" ", "_")


def osm_timestamps(cfg):
    """(Datenstand, Abrufzeit) aus den Overpass-Antworten im osmnx-Cache.
    shortcut: nimmt das Maximum über alle Cache-Dateien, auch anderer Städte; bei gemischtem Cache je Stadt filtern."""
    if cfg.get("data_source") == "postgis":
        from . import db
        return (db.timestamp(cfg),) * 2
    cache_dir = cfg["cache_dir"]
    base, mtimes = [], []
    for f in Path(cache_dir).glob("*.json"):
        try:
            d = json.loads(f.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(d, dict) and "osm3s" in d:
            base.append(d["osm3s"].get("timestamp_osm_base", ""))
            mtimes.append(f.stat().st_mtime)
    fetched = datetime.fromtimestamp(max(mtimes), timezone.utc).isoformat(timespec="seconds") if mtimes else "?"
    return (max(base) if base else "?"), fetched


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--city")
    ap.add_argument("--classification", choices=["peak_share", "jenks", "quantile", "equal_area"])
    ap.add_argument("--mode", choices=["street", "grid"])
    ap.add_argument("--auto-calibrate", action=argparse.BooleanOptionalAction, default=None,
                    help="Street-Modus: Schwellen auf target_ranges_km kalibrieren (überschreibt config)")
    ap.add_argument("--seed", choices=["max_density", "strongest_chain"], help="Street-Modus: 1a-Startpunkt")
    ap.add_argument("--from-reference", action="store_true", help="Street-Modus: 1a/1b aus der Referenz übernehmen")
    ap.add_argument("--source", choices=["overpass", "postgis"], help="Datenquelle (überschreibt data_source)")
    ap.add_argument("--dsn", help="PostGIS-Verbindung, z. B. postgresql://osm@localhost:5432/osm")
    ap.add_argument("--check-db", action="store_true", help="nur prüfen, ob alle benötigten Tags in der DB abfragbar sind")
    ap.add_argument("--center", help="Zentrum „lon,lat“, falls der Ortsname in der DB nicht eindeutig ist")
    ap.add_argument("--reference", help="Street-Modus: Referenzabgrenzung (GeoJSON mit Attribut lage) für diese Stadt")
    a = ap.parse_args(argv)
    cfg = yaml.safe_load(Path(a.config).read_text(encoding="utf-8"))
    args = (("city", a.city), ("classification", a.classification), ("mode", a.mode))
    overrides = [f"{k}={v!r}" for k, v in args if v and v != cfg[k]]
    cfg.update({k: v for k, v in args if v})
    if a.auto_calibrate is not None:
        if a.auto_calibrate != cfg["street"]["auto_calibrate"]:
            overrides.append(f"street.auto_calibrate={a.auto_calibrate}")
        cfg["street"] = {**cfg["street"], "auto_calibrate": a.auto_calibrate}
    if a.source:
        cfg["data_source"] = a.source
    if a.dsn:
        cfg["postgis"] = {**cfg["postgis"], "dsn": a.dsn}
    if a.center:
        cfg["center_lonlat"] = [float(v) for v in a.center.split(",")]
    if a.reference:
        cfg["street"] = {**cfg["street"], "reference": {**(cfg["street"].get("reference") or {}), cfg["city"]: a.reference}}
    if a.check_db:
        return check_db(cfg)
    if a.from_reference:
        overrides.append("street.lagen_from_reference=True")
        cfg["street"] = {**cfg["street"], "lagen_from_reference": True}
    if a.seed and a.seed != cfg["street"]["seed"]:
        overrides.append(f"street.seed={a.seed!r}")
        cfg["street"] = {**cfg["street"], "seed": a.seed}
    method = cfg["classification"]

    configure_osmnx(cfg)

    crs = cfg["crs_metric"]
    aoi, center, center_src = build_aoi(cfg)
    raw = fetch_osm(gpd.GeoSeries([aoi], crs=crs).to_crs(4326).iloc[0], cfg)
    pois = categorize(raw, cfg)
    pois = pois[pois.within(aoi)].reset_index(drop=True)  # Flächen am Rand: repräsentativer Punkt außerhalb
    if cfg["mode"] == "street":
        return main_street(cfg, aoi, center, raw, pois, overrides)
    res = build_zones(pois, aoi, cfg, method)

    sens = []
    for ov in cfg["qa"]["sensitivity"]:
        label = ", ".join(f"{k}={v}" for k, v in ov.items())
        sens.append((label, build_zones(pois, aoi, {**cfg, **ov}, method)["zones"].geometry.iloc[0]))
    plaus = {}
    if "name" in raw:
        named = raw[raw.filter(["highway", "place", "area:highway"]).notna().any(axis=1)]
        plaus = {n: named[named["name"] == n].geometry for n in cfg["qa"]["plausibility"].get(cfg["city"], [])}

    params_hash = hashlib.sha1(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:10]
    osm_ts, fetched = osm_timestamps(cfg)
    ctx = context(raw, cfg)
    ped = ctx[(ctx["kind"] == "pedestrian") & ctx.geom_type.isin(["LineString", "MultiLineString"])].geometry
    res["zones"] = zone_attributes(res["zones"], pois, cfg, method, params_hash, osm_ts, ped)
    checks = run_checks(res["zones"], cfg, sens, plaus)

    c_ll = gpd.GeoSeries([center], crs=crs).to_crs(4326).iloc[0]
    meta = {"method": method, "params_hash": params_hash, "osm_timestamp": osm_ts, "fetched_at": fetched,
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "overrides": overrides,
            "center_source": center_src, "center_ll": f"{c_ll.y:.5f}, {c_ll.x:.5f}"}
    res.update(pois=pois, context=ctx, aoi=aoi)
    s = slug(cfg["city"])
    write_all(Path(cfg["output_dir"]) / s, f"{s}_{method}", res, cfg, checks, meta)

    cols = ["zone_id", "area_ha", "poi_count", "poi_density_ha", "weighted_density_ha", "chain_share", "ped_street_m",
            "compactness"]
    print(f"\n{cfg['city']} – {method} (params_hash {params_hash}, OSM {osm_ts})")
    print(pd.DataFrame(res["zones"][cols]).to_string(index=False))
    for c in checks:
        print(f"  [{c['status']:7}] {c['check']}: {c['detail']}")
    return 1 if any(c["hard"] and not c["ok"] for c in checks) else 0


def required_keys(cfg):
    keys = {"name", "brand", "brand:wikidata", "place", "boundary", "admin_level", "building", "landuse", "tunnel",
            "highway", "shop"}
    for group in ("categories", "ground_floor_categories", "context"):
        for rules in cfg[group].values():
            keys |= set(rules)
    return keys


def check_db(cfg):
    from . import db
    cfg = {**cfg, "data_source": "postgis"}
    s = db.schema(cfg)
    print("Tabellen:", ", ".join(f"{cfg['postgis']['prefix']}_{t} (SRID {v['srid']}, tags {v['tags'] or 'fehlt'})"
                                 for t, v in s.items()))
    missing = db.check_schema(cfg, required_keys(cfg))
    print("Alle benötigten Tags abfragbar." if not missing else
          f"Nicht abfragbar: {', '.join(missing)} – Import mit --hstore (oder Flex-Output mit diesen Tags) nötig.")
    if not s["point"]["tags"]:
        print("Hinweis: ohne tags-Spalte fehlen auch disused:*/abandoned:* (Leerstand wird nicht ausgefiltert).")
    print("Datenstand:", db.timestamp(cfg))
    return 1 if {"brand", "name", "highway", "shop"} & set(missing) else 0


def main_street(cfg, aoi, center, raw, pois, overrides):
    """Street-Modus; zum Vergleich wird der Rastermodus mit denselben POIs mitgerechnet."""
    st = cfg["street"]
    buildings = load_buildings(center, cfg) if st["street_space_only"] or st.get("exclude_landuse") else None
    obstacles = None
    if st["street_space_only"]:  # Auswertungspolygon nur Straßenraum: ohne Gebäude und Malls
        obstacles = shapely.union_all([*buildings.to_numpy(), mall_polygons(raw)])
    res = run_street(load_streets(aoi, cfg), pois, cfg, obstacles=obstacles,
                     squares=load_squares(aoi, cfg) if st.get("include_squares") else None,
                     excluded=commercial_areas(aoi, buildings, cfg) if st.get("exclude_landuse") else None)
    grid_zones = build_zones(pois, aoi, cfg, cfg["classification"])["zones"]
    checks = street_checks(res, cfg)
    params_hash = hashlib.sha1(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:10]
    osm_ts, fetched = osm_timestamps(cfg)
    meta = {"params_hash": params_hash, "osm_timestamp": osm_ts, "fetched_at": fetched, "overrides": overrides,
            "run_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    s = slug(cfg["city"])
    seed = cfg["street"]["seed"]
    stem = (f"{s}_street" + ("_reference" if cfg["street"].get("lagen_from_reference") else "")
            + ("_calibrated" if res["auto_calibrate"] else "") + ("" if seed == "strongest_chain" else f"_{seed}"))
    write_street(Path(cfg["output_dir"]) / s, stem, s, res, grid_zones, cfg, checks, meta)
    print(f"\n{cfg['city']} – street, auto_calibrate={res['auto_calibrate']}, seed={seed} (params_hash {params_hash})")
    print(pd.DataFrame(res["zones"].drop(columns="geometry")).to_string(index=False))
    print("Schwellen:", res["thresholds"])
    for c in checks:
        print(f"  [{c['status']:7}] {c['check']}: {c['detail']}")
    return 1 if any(c["hard"] and not c["ok"] for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
