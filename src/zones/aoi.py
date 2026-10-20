"""Zentrum + Suchraum."""
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point

from .pois import features


def build_aoi(cfg):
    """Suchraum = Kreis um place=city/town-Knoten, verschnitten mit der Verwaltungsgrenze (metrisch)."""
    city, crs = cfg["city"], cfg["crs_metric"]
    if cfg.get("data_source") == "postgis":  # offline: Zentrum und Grenze aus der Datenbank, keine Geokodierung
        from . import db
        center, boundary = db.city_center_boundary(cfg)
        circle = center.buffer(cfg["search_radius_m"])
        src = "place=city/town (PostGIS)" if not cfg.get("center_lonlat") else "center_lonlat"
        return (circle.intersection(boundary) if boundary is not None else circle), center, (
            src + ("" if boundary is not None else ", ohne Verwaltungsgrenze"))
    boundary = ox.geocode_to_gdf(city).to_crs(crs).union_all()
    name = city.split(",")[0].strip()
    center, source = None, "place=city/town"
    try:
        nodes = features(gpd.GeoSeries([boundary], crs=crs).to_crs(4326).iloc[0], {"place": ["city", "town"]}, cfg)
        if "name" in nodes:
            nodes = nodes[(nodes.geom_type == "Point") & (nodes["name"] == name)]
            if len(nodes):
                center = nodes.geometry.iloc[0]
    except ox._errors.InsufficientResponseError:
        pass
    if center is None:
        lat, lon = ox.geocode(city)
        center, source = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(crs).iloc[0], "geocode"
    aoi = center.buffer(cfg["search_radius_m"]).intersection(boundary)
    return aoi, center, source
