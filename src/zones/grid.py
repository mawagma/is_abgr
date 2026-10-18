"""H3-Raster, Zählung, Glättung."""
import geopandas as gpd
import h3
import numpy as np
from shapely.geometry import Polygon


def smoothing_cells(res, radius_m, sigma_m):
    """Glättung in Metern → (k, σ) in Zellschritten; Zellabstand = √3 × Kantenlänge."""
    step = np.sqrt(3) * h3.average_hexagon_edge_length(res, "m")
    return max(1, round(radius_m / step)), sigma_m / step


def build_grid(aoi, pois, cfg, res, radius_m, sigma_m):
    """Zellen im Suchraum mit gewichteter POI-Zahl (raw), Gauß-Mittel (smooth) und Dichte je ha (dens)."""
    crs = cfg["crs_metric"]
    k, sigma = smoothing_cells(res, radius_m, sigma_m)
    aoi_ll = gpd.GeoSeries([aoi], crs=crs).to_crs(4326).iloc[0]
    cells = sorted(h3.geo_to_cells(aoi_ll, res))
    raw = dict.fromkeys(cells, 0.0)
    pts = pois.to_crs(4326)
    for c, w in zip((h3.latlng_to_cell(p.y, p.x, res) for p in pts.geometry), pts["weight"]):
        if c in raw:
            raw[c] += w
    smooth = {}
    for c in cells:
        num = den = 0.0
        for n in h3.grid_disk(c, k):
            if n in raw:  # außerhalb des Suchraums gibt es keine Daten → nicht mitgewichtet
                w = np.exp(-h3.grid_distance(c, n) ** 2 / (2 * sigma**2))
                num += w * raw[n]
                den += w
        smooth[c] = num / den
    geoms = [Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(c)]) for c in cells]
    g = gpd.GeoDataFrame({"h3": cells, "raw": [raw[c] for c in cells], "smooth": [smooth[c] for c in cells]},
                         geometry=geoms, crs=4326).to_crs(crs)
    g["area_ha"] = g.area / 1e4
    g["dens"] = g["smooth"] / g["area_ha"]
    return g
