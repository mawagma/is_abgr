"""Abruf, Kategorisierung, Bereinigung."""
import time

import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd


def configure_osmnx(cfg):
    """Cache-Schlüssel hängen an der Abfrage (inkl. Timeout) → Einstellungen immer gemeinsam setzen."""
    ox.settings.use_cache = True
    ox.settings.cache_folder = cfg["cache_dir"]
    ox.settings.overpass_url = cfg["overpass_url"]
    ox.settings.requests_timeout = cfg["requests_timeout_s"]


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
    for attempt in range(cfg["overpass_retries"] + 1):
        try:
            raw = ox.features_from_polygon(aoi_4326, tags).reset_index()
            return raw.to_crs(cfg["crs_metric"])
        except ox._errors.ResponseStatusCodeError as e:  # öffentliche Overpass-Server liefern sporadisch 5xx
            if attempt == cfg["overpass_retries"]:
                raise
            print(f"Overpass-Fehler ({str(e)[:60]}…), neuer Versuch in {cfg['overpass_retry_wait_s']} s")
            time.sleep(cfg["overpass_retry_wait_s"])


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
    cat = label(raw, cfg["categories"])
    keep = ["element", "id", "name"] if "name" in raw else ["element", "id"]
    pois = raw.loc[cat.notna(), keep + ["geometry"]].copy()
    pois["category"] = cat[cat.notna()]
    pois["geometry"] = pois.geometry.representative_point()
    pois["chain"] = (raw.loc[cat.notna(), "brand"].notna() if "brand" in raw else False) & (pois["category"] == "retail")
    pois["size_factor"] = size_factor(raw.loc[cat.notna()], pois["category"], cfg["size_weighting"])
    pois["weight"] = pois["category"].map(cfg["weights"]).astype(float) * pois["size_factor"]
    return dedupe(pois.reset_index(drop=True), cfg["dedupe_m"])


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
