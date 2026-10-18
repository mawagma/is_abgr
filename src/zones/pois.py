"""Abruf, Kategorisierung, Bereinigung."""
import time

import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd


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
    pois["weight"] = pois["category"].map(cfg["weights"]).astype(float)
    return dedupe(pois.reset_index(drop=True), cfg["dedupe_m"])


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
