"""Abruf, Kategorisierung, Bereinigung."""
import time

import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd
import requests
import shapely


def configure_osmnx(cfg):
    """Cache-Schlüssel hängen an der Abfrage (inkl. Timeout) → Einstellungen immer gemeinsam setzen."""
    ox.settings.use_cache = True
    ox.settings.cache_folder = cfg["cache_dir"]
    ox.settings.overpass_url = cfg["overpass_url"]
    ox.settings.requests_timeout = cfg["requests_timeout_s"]
    # Server-Timeout fest im Abfragetext (= Cache-Schlüssel), damit ein kurzes HTTP-Timeout ihn nicht verändert
    ox.settings.overpass_settings = f"[out:json][timeout:{cfg['requests_timeout_s']}]{{maxsize}}"
    # Statusabfrage vor jedem Request hängt bei gestörten Spiegeln minutenlang und verhindert den Cache-Treffer
    # beim Ersatzserver → abschaltbar
    ox.settings.overpass_rate_limit = cfg.get("overpass_rate_limit", True)


def _rule_mask(df, key, rule):
    if key not in df:
        return pd.Series(False, index=df.index)
    v = df[key]
    if rule is True:
        return v.notna()
    if isinstance(rule, dict):
        return v.notna() & ~v.isin(rule["exclude"])
    return v.isin(rule)


def _query_tags(rule_sets):
    tags = {}
    for rules in rule_sets:
        for key, rule in rules.items():
            if rule is True or isinstance(rule, dict) or tags.get(key) is True:
                tags[key] = True
            else:
                tags[key] = sorted(set(tags.get(key, [])) | set(rule))
    return tags


def fetch_osm(aoi_4326, cfg):
    """Ein Overpass-Abruf für POIs, Kontext und Plausibilitäts-Objekte."""
    tags = _query_tags(list(cfg["categories"].values()) + list(cfg["context"].values()))
    names = cfg["qa"]["plausibility"].get(cfg["city"])
    if names:
        tags["name"] = names
    return features(aoi_4326, tags, cfg)


def features(polygon_4326, tags, cfg):
    """ox.features_from_polygon mit Wiederholung bei 5xx/Netzfehlern, reihum über die Spiegel; Ergebnis metrisch."""
    urls = [cfg["overpass_url"]] + cfg.get("overpass_fallback_urls", [])
    try:
        # Runde 0: alle Spiegel mit kurzem Timeout → Cache-Treffer (unter der URL des liefernden Spiegels) sofort,
        # gestörte Server blockieren nicht minutenlang
        ox.settings.requests_timeout = cfg.get("cache_probe_timeout_s", 10)
        for url in urls:
            ox.settings.overpass_url = url
            try:
                return ox.features_from_polygon(polygon_4326, tags).reset_index().to_crs(cfg["crs_metric"])
            except (ox._errors.ResponseStatusCodeError, requests.exceptions.RequestException):
                pass
        ox.settings.requests_timeout = cfg["requests_timeout_s"]
        for attempt in range(cfg["overpass_retries"] + 1):
            for url in urls:
                ox.settings.overpass_url = url
                try:
                    return ox.features_from_polygon(polygon_4326, tags).reset_index().to_crs(cfg["crs_metric"])
                except (ox._errors.ResponseStatusCodeError, requests.exceptions.RequestException) as e:
                    print(f"Overpass-Fehler {url} ({str(e)[:60]}…)", flush=True)
            if attempt < cfg["overpass_retries"]:
                time.sleep(cfg["overpass_retry_wait_s"])
        raise RuntimeError("Overpass: alle Spiegel und Wiederholungen fehlgeschlagen")
    finally:
        ox.settings.overpass_url = cfg["overpass_url"]
        ox.settings.requests_timeout = cfg["requests_timeout_s"]


def label(raw, rule_dict):
    """Erste passende Regelgruppe je Objekt (Reihenfolge = Priorität)."""
    lab = pd.Series(None, index=raw.index, dtype=object)
    for name, rules in rule_dict.items():
        m = np.logical_or.reduce([_rule_mask(raw, k, r) for k, r in rules.items()])
        lab = lab.where(lab.notna() | ~m, name)
    return lab


def categorize(raw, cfg):
    """POIs als Punkte (metrisch) mit category, weight; ohne disused/abandoned; dedupliziert."""
    dead = np.logical_or.reduce(
        [raw[c].notna() for c in raw.columns if any(c.startswith(p) for p in cfg["exclude_prefixes"])]
        or [pd.Series(False, index=raw.index)]
    )
    raw = raw[~dead]
    if cfg.get("exclude_malls"):
        malls = mall_polygons(raw)
        inside = raw.geometry.representative_point().within(malls) if not malls.is_empty else False
        shop = raw["shop"] if "shop" in raw else pd.Series(None, index=raw.index, dtype=object)
        raw = raw[~(inside | (shop == "mall"))]
    ground = cfg.get("poi_model", "categories") == "ground_floor"
    cat = label(raw, cfg["ground_floor_categories"] if ground else cfg["categories"])
    sel = raw[cat.notna()]
    keep = ["element", "id", "name"] if "name" in raw else ["element", "id"]
    pois = sel[keep + ["geometry"]].copy()
    pois["category"] = cat[cat.notna()]
    pois["geometry"] = pois.geometry.representative_point()
    col = lambda c: sel[c] if c in sel else pd.Series(None, index=sel.index, dtype=object)
    if ground:  # Erdgeschoss-Nutzungen; Filialist = brand oder brand:wikidata
        pois["chain"] = col("brand").notna() | col("brand:wikidata").notna()
        pois["size_factor"] = 1.0
        pois["weight"] = np.where(pois["chain"], cfg["street"]["brand_weight"], 1.0)
    else:
        pois["chain"] = col("brand").notna() & (pois["category"] == "retail")
        pois["size_factor"] = size_factor(sel, pois["category"], cfg["size_weighting"])
        pois["weight"] = pois["category"].map(cfg["weights"]).astype(float) * pois["size_factor"]
    return dedupe(pois.reset_index(drop=True), cfg["dedupe_m"])


def mall_polygons(raw):
    """Vereinigte Flächen der Einkaufszentren (shop=mall), metrisch."""
    if "shop" not in raw:
        return shapely.Polygon()
    m = raw[(raw["shop"] == "mall") & raw.geom_type.isin(["Polygon", "MultiPolygon"])]
    return shapely.union_all(m.geometry.to_numpy())


def size_factor(raw, category, sw):
    """Zusatzgewicht Einzelhandel nach typischer Verkaufsfläche (brand → name → shop-Typ) und Filialist-Bonus."""
    f = pd.Series(1.0, index=raw.index)
    if not sw["enabled"]:
        return f
    col = lambda c: raw[c] if c in raw else pd.Series(None, index=raw.index, dtype=object)
    area = (col("brand").map(sw["brand_area_m2"]).combine_first(col("name").map(sw["brand_area_m2"]))
            .combine_first(col("shop").map(sw["shop_area_m2"])).fillna(sw["ref_area_m2"]).astype(float))
    f = np.clip((area / sw["ref_area_m2"]) ** sw["exponent"], *sw["clip"]) * np.where(
        col("brand").notna(), sw["chain_factor"], 1.0)
    f = f.where(~col("shop").isin(sw["not_central"]), sw["not_central_factor"])
    return f.where(category == "retail", 1.0)


def dedupe(pois, dist_m):
    """Gleicher Name und < dist_m Abstand → nur das erste Objekt behalten."""
    if "name" not in pois:
        return pois
    xy = np.column_stack([pois.geometry.x, pois.geometry.y])
    keep = np.ones(len(pois), bool)
    for pos in pois.groupby("name").indices.values():
        kept = []
        for p in pos:
            if kept and np.min(np.hypot(*(xy[kept] - xy[p]).T)) < dist_m:
                keep[p] = False
            else:
                kept.append(p)
    return pois[keep].reset_index(drop=True)


def context(raw, cfg):
    """Fußgängerzonen und Haltestellen (nur für die Karte)."""
    lab = label(raw, cfg["context"])
    ctx = raw.loc[lab.notna(), ["element", "id", "geometry"] + (["name"] if "name" in raw else [])].copy()
    ctx["kind"] = lab[lab.notna()]
    return gpd.GeoDataFrame(ctx, crs=raw.crs)
