"""Vereinigung, Schließen, Löcher, Vereinfachung, Ringe."""
import geopandas as gpd
import shapely
from shapely.geometry import MultiPolygon, Polygon


def _fill_holes(geom, min_m2):
    fill = lambda p: Polygon(p.exterior, [r for r in p.interiors if Polygon(r).area >= min_m2])
    if isinstance(geom, Polygon):
        return fill(geom)
    return MultiPolygon([fill(p) for p in geom.geoms])


def _polygonal(geom, min_m2):
    parts = [p for p in shapely.get_parts(shapely.get_parts(shapely.make_valid(geom))) if isinstance(p, Polygon) and p.area >= min_m2]
    return shapely.union_all(parts) if parts else Polygon()


def zone_polygons(cells, cfg):
    """Je Stufe die kumulative Zellmenge (Z1, Z1+Z2, Z1+Z2+Z3) glätten, dann Ringe bilden.
    Getrenntes Vereinfachen lässt an gemeinsamen Kanten Splitter zurück → Teile < min_part_m2 verwerfen."""
    cb = cfg["closing_buffer_m"]
    cum = []
    for z in (1, 2, 3):
        g = shapely.union_all(cells.loc[cells["zone"].between(1, z), "geometry"].to_numpy())
        if not g.is_empty:
            g = _fill_holes(g.buffer(cb).buffer(-cb), cfg["min_hole_ha"] * 1e4).simplify(cfg["simplify_m"])
        cum.append(g)
    m = cfg["min_part_m2"]
    z1 = _polygonal(cum[0], m)
    z2 = _polygonal(cum[1].difference(z1), m)
    z3 = _polygonal(cum[2].difference(z1.union(z2)), m)
    return gpd.GeoDataFrame({"zone_id": ["Z1", "Z2", "Z3"], "rank": [1, 2, 3]},
                            geometry=[z1, z2, z3], crs=cells.crs)
