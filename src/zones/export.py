"""GPKG, GeoJSON, Folium-Karte, Markdown-Bericht."""
import math

import branca.colormap as bcm
import folium
import geopandas as gpd
import pandas as pd
import yaml

ATTR = "© OpenStreetMap-Mitwirkende"
ZONE_COLORS = {"Z1": "#d7191c", "Z2": "#fdae61", "Z3": "#ffe94d"}
CAT_COLORS = {"retail": "#1f77b4", "gastro": "#e377c2", "service": "#7f7f7f", "culture_leisure": "#2ca02c",
              "health": "#9467bd"}


def zone_attributes(zones, pois, cfg, method, params_hash, osm_ts):
    z = zones.copy()
    z["area_ha"] = (z.area / 1e4).round(2)
    j = gpd.sjoin(pois, z[["zone_id", "geometry"]], predicate="within")
    z["poi_count"] = z["zone_id"].map(j.groupby("zone_id").size()).fillna(0).astype(int)
    z["poi_density_ha"] = (z["poi_count"] / (z.area / 1e4)).round(2)
    shares = pd.crosstab(j["zone_id"], j["category"], normalize="index").reindex(columns=list(cfg["weights"]),
                                                                                  fill_value=0)
    for cat in cfg["weights"]:
        z[f"share_{cat}"] = z["zone_id"].map(shares[cat]).fillna(0).round(3)
    z["perimeter_m"] = z.length.round(1)
    z["compactness"] = [round(4 * math.pi * g.area / g.length**2, 3) if g.length else 0.0 for g in z.geometry]
    z["method"], z["params_hash"], z["osm_timestamp"] = method, params_hash, osm_ts
    return z


def write_all(out_dir, stem, res, cfg, checks, meta):
    out_dir.mkdir(parents=True, exist_ok=True)
    gpkg = out_dir / f"zones_{stem}.gpkg"
    gpkg.unlink(missing_ok=True)
    res["zones"].to_file(gpkg, layer="zones")
    res["cells"].to_file(gpkg, layer="cells")
    res["pois"].to_file(gpkg, layer="pois")
    res["islands"].to_file(gpkg, layer="islands")  # darf leer sein
    res["zones"].to_crs(cfg["crs_export"]).to_file(out_dir / f"zones_{stem}.geojson", driver="GeoJSON")
    write_map(out_dir / f"map_{stem}.html", res)
    write_report(out_dir / f"report_{stem}.md", res, cfg, checks, meta)


def write_map(path, res):
    ll = lambda g: g.to_crs(4326)
    aoi = ll(gpd.GeoSeries([res["aoi"]], crs=res["zones"].crs))
    c = aoi.iloc[0].centroid
    m = folium.Map(location=[c.y, c.x], zoom_start=15, tiles=None, control_scale=True)
    folium.TileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", attr=ATTR, name="OSM").add_to(m)
    cells = ll(res["cells"][res["cells"]["dens"] > 0][["h3", "dens", "cls", "zone", "geometry"]])
    cmap = bcm.linear.YlOrRd_09.scale(0, float(cells["dens"].max()))
    cmap.caption = "geglättete gewichtete POI-Dichte je ha"
    folium.GeoJson(cells, name="Dichte-Hexagone", style_function=lambda f: {
        "fillColor": cmap(f["properties"]["dens"]), "color": "#666", "weight": 0.3, "fillOpacity": 0.45},
        tooltip=folium.GeoJsonTooltip(["h3", "dens", "cls", "zone"])).add_to(m)
    cmap.add_to(m)
    folium.GeoJson(ll(res["zones"]), name="Zonen", style_function=lambda f: {
        "fillColor": ZONE_COLORS[f["properties"]["zone_id"]], "color": "#222", "weight": 2, "fillOpacity": 0.35},
        tooltip=folium.GeoJsonTooltip(["zone_id", "area_ha", "poi_count", "poi_density_ha"])).add_to(m)
    if len(res["islands"]):
        folium.GeoJson(ll(res["islands"][["h3", "cls", "geometry"]]), name="Inseln", style_function=lambda f: {
            "fillOpacity": 0, "color": "#333", "weight": 1.5, "dashArray": "4 4"}).add_to(m)
    folium.GeoJson(aoi, name="Suchraum", style_function=lambda f: {"fillOpacity": 0, "color": "#000",
                                                                  "weight": 1, "dashArray": "8 6"}).add_to(m)
    ctx = res["context"]
    ped = ctx[ctx["kind"] == "pedestrian"]
    if len(ped):
        folium.GeoJson(ll(ped[["kind", "geometry"]]), name="Fußgängerzonen", show=False,
                       style_function=lambda f: {"color": "#0050a0", "weight": 3}).add_to(m)
    stops = ll(ctx[ctx["kind"] == "transit_stop"])
    fg = folium.FeatureGroup("ÖPNV-Haltestellen", show=False).add_to(m)
    for p in stops.geometry.representative_point():
        folium.CircleMarker([p.y, p.x], radius=3, color="#000", fill=True, fill_opacity=1, weight=0).add_to(fg)
    pois = ll(res["pois"])
    for cat, grp in pois.groupby("category"):
        fg = folium.FeatureGroup(f"POI: {cat}").add_to(m)
        for p, name in zip(grp.geometry, grp.get("name", pd.Series(index=grp.index))):
            folium.CircleMarker([p.y, p.x], radius=2, color=CAT_COLORS.get(cat, "#000"), weight=0, fill=True,
                                fill_opacity=0.9, tooltip=f"{cat}: {name}" if isinstance(name, str) else cat
                                ).add_to(fg)
    folium.LayerControl(collapsed=False).add_to(m)
    m.save(path)


def _md_table(df):
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    rows += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


def write_report(path, res, cfg, checks, meta):
    z = pd.DataFrame(res["zones"].drop(columns="geometry"))
    isl = res["islands"]
    lines = [
        f"# Vergleichszonen {cfg['city']} – Methode `{meta['method']}`", "",
        f"Datenquelle: {ATTR} (ODbL), abgerufen über Overpass ({cfg['overpass_url']}).  ",
        f"OSM-Datenstand (Overpass `timestamp_osm_base`): {meta['osm_timestamp']}  ",
        f"Abrufzeitpunkt (Cache): {meta['fetched_at']}  ",
        f"Lauf: {meta['run_at']} · params_hash `{meta['params_hash']}`", "",
        "## Zonen", "", _md_table(z.drop(columns=["method", "params_hash", "osm_timestamp"])), "",
        "## Prüfungen", "",
        _md_table(pd.DataFrame(checks)[["status", "check", "detail", "hard"]].rename(columns={"hard": "hart"})), "",
        "## Suchraum und Daten", "",
        f"- Zentrum: {meta['center_source']} ({meta['center_ll']}), Radius {cfg['search_radius_m']} m, "
        f"Suchraum {res['aoi'].area / 1e4:.1f} ha (mit Verwaltungsgrenze verschnitten)",
        f"- POIs nach Bereinigung: {len(res['pois'])} "
        f"({', '.join(f'{k}: {v}' for k, v in res['pois']['category'].value_counts().items())})",
        f"- H3-Zellen: {len(res['cells'])} (Auflösung {cfg['h3_resolution']}, "
        f"Ø {res['cells']['area_ha'].mean():.2f} ha), davon Dichte > 0: {(res['cells']['dens'] > 0).sum()}",
        f"- Inseln (klassifiziert, nicht mit Z1 verbunden): {len(isl)} Zellen, {isl['area_ha'].sum():.1f} ha"
        + (f" – Klassen {isl['cls'].value_counts().sort_index().to_dict()}" if len(isl) else ""), "",
        "## Parameter", "",
        "Overrides gegenüber `config.yaml`: " + (", ".join(meta["overrides"]) or "keine"), "",
        "Abweichungen/Auslegungen gegenüber CLAUDE.md:", "",
        "- Ringe aus kumulativen Zellmengen (Z1, Z1+Z2, Z1+Z2+Z3) gebildet, damit zwischen den Zonen keine Lücken"
        " durch getrenntes Schließen/Vereinfachen entstehen; anschließend Z2 −= Z1, Z3 −= Z1 ∪ Z2.",
        f"- Zusätzlicher Parameter `min_part_m2` ({cfg['min_part_m2']} m²): Polygonteile darunter sind Splitter aus dem"
        " getrennten Vereinfachen der kumulativen Flächen und werden verworfen (kleine Lücken möglich).",
        "- Dateinamen mit Methodensuffix, damit die drei Läufe einander nicht überschreiben.",
        "- Polsby-Popper wird auf die Ringfläche gerechnet; Ringe (Z2, Z3) haben dadurch systematisch niedrige Werte.",
        "", "```yaml", yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False).strip(), "```", "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
