import geopandas as gpd
import numpy as np
import pytest
import yaml
from shapely.geometry import LineString, Point

import pandas as pd
import shapely

from zones.cli import build_zones
from zones.pois import categorize, size_factor
from zones.qa import run_checks, street_checks
from zones.street import run_street

CFG = yaml.safe_load(open("config.yaml", encoding="utf-8"))
CENTER = (515000.0, 5444000.0)  # ~Heilbronn in EPSG:25832


def synthetic():
    """Dichter Cluster (600 POIs, r=300 m) im Zentrum, schwacher Cluster (40 POIs, r=300 m) 1 km östlich, Streuung."""
    rng = np.random.default_rng(0)

    def cluster(cx, cy, n, r):
        a, d = rng.uniform(0, 2 * np.pi, n), r * np.sqrt(rng.uniform(0, 1, n))
        return [Point(cx + di * np.cos(ai), cy + di * np.sin(ai)) for ai, di in zip(a, d)]

    pts = cluster(*CENTER, 600, 300) + cluster(CENTER[0] + 1000, CENTER[1], 40, 300) + cluster(*CENTER, 80, 1900)
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
    # Zellebene: Polygon-Nachbearbeitung (Löcher < min_hole_ha füllen) liegt bei Res. 11 über einer Zellfläche
    areas = res["cells"].groupby("zone")["area_ha"].sum().reindex([1, 2, 3]).tolist()
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


def test_max_area_limits_zones():
    pois, aoi = synthetic()
    cfg = {**CFG, "max_area_ha": [1.0, 2.0, 3.0]}
    cells = build_zones(pois, aoi, cfg, "peak_share")["cells"]
    areas = cells.groupby("zone")["area_ha"].sum()
    for z, lim in zip((1, 2, 3), cfg["max_area_ha"]):
        assert 0 < areas.get(z, 0) <= lim


def synthetic_street():
    """600 m gerade Straße: 0–300 m dichter Besatz (10 je 100 m, jeder zweite Filialist), 300–600 m schwach (3 je 100 m)."""
    x0, y0 = CENTER
    streets = gpd.GeoDataFrame({"name": ["Teststraße"], "highway": ["pedestrian"]},
                               geometry=[LineString([(x0, y0), (x0 + 600, y0)])], crs=CFG["crs_metric"])
    xs = list(np.arange(5, 300, 10)) + list(np.arange(310, 600, 100 / 3))
    chain = [x < 300 and i % 2 == 0 for i, x in enumerate(xs)]
    pois = gpd.GeoDataFrame({"category": "retail", "chain": chain,
                             "weight": [CFG["street"]["brand_weight"] if c else 1.0 for c in chain]},
                            geometry=[Point(x0 + x, y0 + (10 if i % 2 else -10)) for i, x in enumerate(xs)],
                            crs=CFG["crs_metric"])
    return streets, pois


def test_street_dense_section_is_1a():
    streets, pois = synthetic_street()
    res = run_street(streets, pois, {**CFG, "city": "Teststadt"}, auto_calibrate=False)
    seg, zones = res["segments"], res["zones"]
    L = CFG["street"]["segment_length_m"]
    len_1a = seg.loc[seg["lage"] == "lage_1a", "length_m"].sum()
    assert abs(len_1a - 300) <= L
    assert (seg.loc[seg["lage"] == "lage_1a"].geometry.centroid.x - CENTER[0] < 300 + L).all()
    assert list(zones["lage"]) == ["lage_1a", "lage_1b", "lage_2"] and not zones.geometry.is_empty.any()
    checks = street_checks(res, CFG)
    assert all(c["ok"] for c in checks if c["hard"]), checks


def test_street_calibration_hits_target_length():
    streets, pois = synthetic_street()
    cfg = {**CFG, "city": "Teststadt", "street": {**CFG["street"], "target_ranges_km": {"lage_1a": [0.1, 0.1], "lage_1b": [0.1, 0.1],
                                                                    "lage_2": [0.1, 0.1]}}}
    res = run_street(streets, pois, cfg, auto_calibrate=True)
    km = res["zones"].set_index("lage")["length_km"]
    assert abs(km["lage_1a"] - 0.1) <= CFG["street"]["segment_length_m"] / 1000


def test_street_reference_calibration(tmp_path):
    """Referenz = dichter Abschnitt 0–200 m als 1a → Kalibrierung trifft sie (F1 hoch)."""
    streets, pois = synthetic_street()
    x0, y0 = CENTER
    ref = gpd.GeoDataFrame({"lage": ["lage_1a"]}, geometry=[LineString([(x0, y0), (x0 + 200, y0)])],
                           crs=CFG["crs_metric"])
    ref.to_file(tmp_path / "ref.geojson", driver="GeoJSON")
    cfg = {**CFG, "city": "Teststadt",
           "street": {**CFG["street"], "reference": {"Teststadt": str(tmp_path / "ref.geojson")}}}
    res = run_street(streets, pois, cfg, auto_calibrate=True)
    assert res["reference_match"]["lage_1a"]["f1"] >= 0.8
    assert res["targets_km"]["lage_1a"] == [0.15, 0.25]


def test_street_space_excludes_buildings():
    streets, pois = synthetic_street()
    x0, y0 = CENTER
    building = shapely.box(x0 + 50, y0 + 5, x0 + 150, y0 + 30)  # Gebäude an der Nordseite des 1a-Abschnitts
    res = run_street(streets, pois, {**CFG, "city": "Teststadt"}, auto_calibrate=False, obstacles=building)
    assert all(g.intersection(building).area < 1e-6 for g in res["zones"].geometry)
    assert res["zones"].geometry.iloc[0].contains(Point(x0 + 100, y0))  # Straßenachse bleibt drin


def test_mall_tenants_excluded():
    mall = shapely.box(0, 0, 100, 100)
    raw = gpd.GeoDataFrame({"element": ["way", "node", "node"], "id": [1, 2, 3], "shop": ["mall", "clothes", "shoes"],
                            "name": ["Center", "In Mall", "Straße"]},
                           geometry=[mall, Point(50, 50), Point(150, 50)], crs=CFG["crs_metric"])
    assert list(categorize(raw, CFG)["name"]) == ["Straße"]


def test_lagen_from_reference(tmp_path):
    streets, pois = synthetic_street()
    x0, y0 = CENTER
    ref = gpd.GeoDataFrame({"lage": ["lage_1a", "lage_1b"]},
                           geometry=[LineString([(x0, y0), (x0 + 100, y0)]), LineString([(x0 + 100, y0), (x0 + 200, y0)])],
                           crs=CFG["crs_metric"])
    ref.to_file(tmp_path / "ref.geojson", driver="GeoJSON")
    cfg = {**CFG, "city": "Teststadt", "street": {**CFG["street"], "lagen_from_reference": True,
                                                 "reference": {"Teststadt": str(tmp_path / "ref.geojson")}}}
    km = run_street(streets, pois, cfg, auto_calibrate=False)["zones"].set_index("lage")["length_km"]
    assert km["lage_1a"] == 0.1 and km["lage_1b"] == 0.1 and km["lage_2"] > 0


def test_secondary_1a_chain():
    """Zwei dichte Abschnitte, getrennt durch 300 m ohne Besatz → beide 1a (zweite Kette ≥ 20 % der ersten)."""
    x0, y0 = CENTER
    streets = gpd.GeoDataFrame({"name": ["Teststraße"], "highway": ["pedestrian"]},
                               geometry=[LineString([(x0, y0), (x0 + 900, y0)])], crs=CFG["crs_metric"])
    xs = list(np.arange(5, 300, 10)) + list(np.arange(605, 800, 10))
    chain = [i % 2 == 0 for i in range(len(xs))]
    pois = gpd.GeoDataFrame({"category": "retail", "chain": chain,
                             "weight": [CFG["street"]["brand_weight"] if c else 1.0 for c in chain]},
                            geometry=[Point(x0 + x, y0 + 10) for x in xs], crs=CFG["crs_metric"])
    seg = run_street(streets, pois, {**CFG, "city": "Teststadt"}, auto_calibrate=False)["segments"]
    x1a = seg.loc[seg["lage"] == "lage_1a"].geometry.centroid.x - x0
    assert (x1a < 300).any() and (x1a > 600).any()


def test_smooth_runs_fills_short_gaps():
    from zones.street import smooth_runs
    seg = pd.DataFrame({"chain_id": [0] * 6, "length_m": [50.0] * 6})
    lage = np.array(["lage_1a", "lage_1a", "lage_2", "lage_1a", "lage_1b", "lage_1b"], dtype=object)
    out = smooth_runs(seg, lage, 100)
    assert list(out) == ["lage_1a", "lage_1a", "lage_1a", "lage_1a", "lage_1b", "lage_1b"]


def test_excluded_area_removes_lage():
    """Abschnitte in einer Gewerbegebietsfläche bekommen keine Lage."""
    streets, pois = synthetic_street()
    x0, y0 = CENTER
    gewerbe = shapely.box(x0 - 10, y0 - 50, x0 + 150, y0 + 50)
    seg = run_street(streets, pois, {**CFG, "city": "Teststadt"}, auto_calibrate=False, excluded=gewerbe)["segments"]
    mid = seg.geometry.interpolate(0.5, normalized=True)
    assert (seg.loc[mid.within(gewerbe).to_numpy(), "lage"] == "").all()
    assert (seg["lage"] == "lage_1a").any()
