"""Einmalig: Heilbronn-Referenzlagen (Expertenabgrenzung) als GeoJSON-Linien erzeugen.
1a = 1a-Segmente der freigegebenen Karte (seed strongest_chain, Lauf vom 18.10.2026).
1b = Kaiserstraße von der Allee bis zum Käthchenhof + Sülmerstraße vom Kiliansplatz bis zur Höhe Hafenmarkt/Lohtorstraße.
Die Datei kann in QGIS nachbearbeitet werden (Attribut lage = lage_1a | lage_1b)."""
import sys

import geopandas as gpd
import pandas as pd

seg = gpd.read_file("output/heilbronn/zones_heilbronn_street_strongest_chain.gpkg", layer="segments")
raw = pd.read_pickle(sys.argv[1])  # Overpass-POI-Abruf (enthält Käthchenhof, Hafenmarkt, Lohtorstraße)
c = seg.centroid
a1 = seg[seg["lage"] == "lage_1a"]
kaethchen_x = raw[raw["name"] == "Käthchenhof"].geometry.total_bounds[0]  # Westkante
north_y = min(raw[raw["name"] == "Hafenmarkt"].geometry.centroid.y.max(), seg[seg["street"] == "Lohtorstraße"].geometry.centroid.y.min())
kaiser = seg[(seg["street"] == "Kaiserstraße") & (c.x >= kaethchen_x)]
suelmer = seg[(seg["street"] == "Sülmerstraße") & (c.y <= north_y) & (seg["lage"] != "lage_1a")]
ref = pd.concat([a1.assign(lage="lage_1a"), pd.concat([kaiser, suelmer]).assign(lage="lage_1b")])
ref = ref[~ref["seg_id"].duplicated()][["lage", "street", "geometry"]]
ref.to_crs(4326).to_file("reference/heilbronn_lagen.geojson", driver="GeoJSON")
print(ref.groupby(["lage", "street"]).geometry.apply(lambda g: round(g.length.sum())).to_string())
