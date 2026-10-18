import geopandas as gpd
import numpy as np
import pytest
import yaml
from shapely.geometry import Point

import pandas as pd

from zones.cli import build_zones
from zones.pois import size_factor
from zones.qa import run_checks

CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))
CENTER = (515000.0, 5444000.0)  # ~Heilbronn in EPSG:25832


def synthetic():
    """Dichter Cluster (300 POIs, r=150 m) im Zentrum, schwacher Cluster (40 POIs, r=300 m) 1 km östlich, Streuung."""
    rng = np.random.default_rng(0)

    def cluster(cx, cy, n, r):
        a, d = rng.uniform(0, 2 * np.pi, n), r * np.sqrt(rng.uniform(0, 1, n))
        return [Point(cx + di * np.cos(ai), cy + di * np.sin(ai)) for ai, di in zip(a, d)]

    pts = cluster(*CENTER, 300, 150) + cluster(CENTER[0] + 1000, CENTER[1], 40, 300) + cluster(*CENTER, 80, 1900)
    pois = gpd.GeoDataFrame({"category": ["retail"] * len(pts), "weight": 1.0}, geometry=pts, crs=CFG["crs_metric"])
    return pois, Point(CENTER).buffer(CFG["search_radius_m"])


@pytest.mark.parametrize("method", ["peak_share", "jenks", "quantile", "equal_area"])
def test_synthetic_two_clusters(method):
    pois, aoi = synthetic()
    zones = build_zones(pois, aoi, CFG, method)["zones"]
    assert len(zones) == 3 and not zones.geometry.is_empty.any() and zones.geometry.is_valid.all()
    assert zones.geometry.iloc[0].distance(Point(CENTER)) == 0  # Z1 liegt im dichten Cluster
    assert zones.geometry.iloc[0].centroid.distance(Point(CENTER)) < 200
    checks = {c["check"]: c for c in run_checks(zones, CFG)}
    assert all(c["ok"] for c in checks.values() if c["hard"]), checks


def test_equal_area_targets():
    pois, aoi = synthetic()
    res = build_zones(pois, aoi, CFG, "equal_area")
    cell_ha = res["cells"]["area_ha"].mean()
    t = CFG["equal_area_ha"]
    target = [t[0], t[1] - t[0], t[2] - t[1]]
    areas = (res["zones"].area / 1e4).tolist()
    for a, tg in zip(areas, target):
        assert abs(a - tg) <= cell_ha, (areas, target, cell_ha)


def test_size_factor():
    sw = CFG["size_weighting"]
    raw = pd.DataFrame({"shop": ["clothes", "car", "kiosk", "clothes", None],
                        "brand": [None, "BMW", None, "H&M", None], "name": ["X", "BMW", "K", "H&M", "Apotheke"]})
    cat = pd.Series(["retail", "retail", "retail", "retail", "gastro"])
    f = size_factor(raw, cat, sw).tolist()
    assert f[1] == sw["not_central_factor"]                      # Autohaus trotz Marke abgewertet
    assert f[2] == sw["clip"][0]                                  # Kiosk an der Untergrenze
    assert f[3] > f[0] > f[2]                                     # Filialist mit großer Fläche > Fachgeschäft > Kiosk
    assert f[4] == 1.0                                            # nur Einzelhandel wird skaliert


def test_peak_share_min_area():
    pois, aoi = synthetic()
    zones = build_zones(pois, aoi, CFG, "peak_share")["zones"]
    assert zones.area.iloc[0] >= CFG["min_zone_m2"]["Z1"]
