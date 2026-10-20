"""OSM-Daten aus einer osm2pgsql-Datenbank (klassisches Schema <prefix>_point/_line/_polygon) statt Overpass.
Gleiche Rückgabe wie pois.features(): ein GeoDataFrame mit element, id, je Tag eine Spalte und Geometrie (metrisch).
Tags werden aus der gleichnamigen Spalte oder – falls vorhanden – aus der Spalte tags (hstore/jsonb) gelesen."""
import json

import geopandas as gpd
import pandas as pd
import psycopg2
from shapely import wkb

TABLES = {"point": "node", "line": "way", "polygon": "way"}
_conn, _schema = {}, {}


def connect(cfg):
    dsn = cfg["postgis"]["dsn"]  # Passwort über PGPASSWORD oder .pgpass, nicht in der Config
    if dsn not in _conn:
        _conn[dsn] = psycopg2.connect(dsn)
        _conn[dsn].autocommit = True
    return _conn[dsn]


def schema(cfg):
    """Spalten, Typ der tags-Spalte (hstore | jsonb | None) und SRID je Tabelle."""
    p = cfg["postgis"]["prefix"]
    if p not in _schema:
        cur, out = connect(cfg).cursor(), {}
        for t in TABLES:
            cur.execute("select column_name, udt_name from information_schema.columns where table_name = %s",
                        (f"{p}_{t}",))
            cols = dict(cur.fetchall())
            if "way" not in cols:
                raise RuntimeError(f"Tabelle {p}_{t} mit Geometriespalte way nicht gefunden (prefix in config.yaml?)")
            cur.execute("select Find_SRID(current_schema()::text, %s, 'way')", (f"{p}_{t}",))
            out[t] = {"cols": set(cols) - {"way", "tags", "osm_id", "z_order", "way_area"},
                      "tags": cols.get("tags"), "srid": cur.fetchone()[0]}
        _schema[p] = out
    return _schema[p]


def _expr(s, key):
    """SQL-Ausdruck für einen Tag (Spalte, sonst tags), oder None wenn nicht abfragbar. Rückgabe (sql, params)."""
    tag = {"hstore": ("tags -> %s", [key]), "jsonb": ("tags ->> %s", [key])}.get(s["tags"])
    if key in s["cols"]:
        col = '"' + key.replace('"', '""') + '"'
        return (f"coalesce({col}, {tag[0]})", tag[1]) if tag else (col, [])  # --hstore-all: Wert auch in tags
    return tag


def features(polygon_4326, tags, cfg):
    """Wie ox.features_from_polygon: alle Objekte im Polygon, die einen der Tags erfüllen (True = beliebiger Wert)."""
    p, rows = cfg["postgis"]["prefix"], []
    cur = connect(cfg).cursor()
    for t, element in TABLES.items():
        s = schema(cfg)[t]
        conds, params = [], []
        for key, val in tags.items():
            e = _expr(s, key)
            if e is None:
                continue  # Tag in dieser Datenbank nicht vorhanden (siehe check_schema)
            if val is True:
                conds.append(f"{e[0]} is not null")
                params += e[1]
            else:
                conds.append(f"{e[0]} = any(%s)")
                params += e[1] + [list(val)]
        if not conds:
            continue
        cols = sorted(s["cols"])
        sel = ", ".join('"' + c.replace('"', '""') + '"' for c in cols)
        tagsql = {"hstore": "hstore_to_json(tags)::text", "jsonb": "tags::text"}.get(s["tags"], "null")
        cur.execute(
            f"select osm_id, {sel}{',' if sel else ''} {tagsql}, ST_AsBinary(ST_Transform(way, 4326)) "
            f"from {p}_{t} where way && ST_Transform(ST_GeomFromText(%s, 4326), {s['srid']}) "
            f"and ST_Intersects(way, ST_Transform(ST_GeomFromText(%s, 4326), {s['srid']})) and ({' or '.join(conds)})",
            [polygon_4326.wkt, polygon_4326.wkt] + params)
        for r in cur.fetchall():
            osm_id, vals, extra, geom = r[0], r[1:1 + len(cols)], r[1 + len(cols)], r[-1]
            d = {k: v for k, v in (json.loads(extra) if extra else {}).items()}
            d.update({c: v for c, v in zip(cols, vals) if v is not None})
            el = element if osm_id > 0 or t == "point" else "relation"
            rows.append({"element": el, "id": abs(osm_id), **d, "geometry": wkb.loads(bytes(geom))})
    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs=4326) if rows else gpd.GeoDataFrame(
        {"element": [], "id": []}, geometry=[], crs=4326)
    gdf = gdf.drop_duplicates(["element", "id"])  # geschlossene Wege können in line und polygon stehen
    return gdf.reset_index(drop=True).to_crs(cfg["crs_metric"])


def city_center_boundary(cfg):
    """Ortszentrum (place=city/town-Knoten, bei mehreren der einwohnerstärkste) und Verwaltungsgrenze, die ihn enthält
    (lokalste Ebene). Ohne Grenze → None (Suchraum = Kreis)."""
    p, name = cfg["postgis"]["prefix"], cfg["city"].split(",")[0].strip()
    sp, sg = schema(cfg)["point"], schema(cfg)["polygon"]
    cur = connect(cfg).cursor()
    if cfg.get("center_lonlat"):
        cur.execute("select ST_AsBinary(ST_Transform(ST_SetSRID(ST_Point(%s, %s), 4326), %s))",
                    [*cfg["center_lonlat"], sp["srid"]])
        node = cur.fetchone()[0]
    else:
        place, pp = _expr(sp, "place")
        nm, pn = _expr(sp, "name")
        pop = _expr(sp, "population") or ("null", [])
        cur.execute(f"select ST_AsBinary(way) from {p}_point where {nm} = %s and {place} in ('city', 'town') "
                    f"order by ({place} = 'city') desc, nullif(regexp_replace({pop[0]}, '[^0-9]', '', 'g'), '')::bigint "
                    f"desc nulls last limit 1", pn + [name] + pp + pp + pop[1])
        r = cur.fetchone()
        if r is None:
            raise RuntimeError(f"Kein place=city/town-Knoten „{name}“ in der Datenbank – center_lonlat angeben")
        node = r[0]
    b, pb = _expr(sg, "boundary")
    nm, pn = _expr(sg, "name")
    lvl = _expr(sg, "admin_level") or ("null", [])
    cur.execute(f"select ST_AsBinary(ST_Transform(way, 4326)) from {p}_polygon where {b} = 'administrative' "
                f"and {nm} = %s and ST_Contains(way, ST_GeomFromWKB(%s, {sg['srid']})) "
                f"order by nullif(regexp_replace({lvl[0]}, '[^0-9]', '', 'g'), '')::int desc nulls last limit 1",
                pb + pn + [name, psycopg2.Binary(bytes(node))] + lvl[1])
    r = cur.fetchone()
    cur.execute(f"select ST_AsBinary(ST_Transform(ST_GeomFromWKB(%s, {sp['srid']}), 4326))", [psycopg2.Binary(bytes(node))])
    center = gpd.GeoSeries([wkb.loads(bytes(cur.fetchone()[0]))], crs=4326).to_crs(cfg["crs_metric"]).iloc[0]
    boundary = gpd.GeoSeries([wkb.loads(bytes(r[0]))], crs=4326).to_crs(cfg["crs_metric"]).iloc[0] if r else None
    return center, boundary


def timestamp(cfg):
    """Datenstand aus osm2pgsql_properties (falls vorhanden)."""
    try:
        cur = connect(cfg).cursor()
        cur.execute("select property, value from osm2pgsql_properties where property in "
                    "('replication_timestamp', 'import_timestamp', 'current_timestamp')")
        d = dict(cur.fetchall())
        return d.get("replication_timestamp") or d.get("import_timestamp") or d.get("current_timestamp") or "unbekannt"
    except psycopg2.Error:
        return "unbekannt"


def check_schema(cfg, keys):
    """Welche benötigten Tags in der Datenbank abfragbar sind (Spalte oder tags). Rückgabe: Liste fehlender Keys."""
    missing = []
    for k in sorted(keys):
        if all(_expr(schema(cfg)[t], k) is None for t in TABLES):
            missing.append(k)
    return missing
