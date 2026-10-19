"""Städtevergleich Street-Modus: liest output/<stadt>/zones_<stadt>_<variante>.gpkg und schreibt output/vergleich_staedte.md.
Aufruf: python tools/compare_cities.py heilbronn:street heilbronn:street_reference stuttgart:street oehringen:street"""
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

rows = []
for arg in sys.argv[1:]:
    slug, variant = arg.split(":")
    z = gpd.read_file(Path("output") / slug / f"zones_{slug}_{variant}.gpkg", layer="zones")
    seg = gpd.read_file(Path("output") / slug / f"zones_{slug}_{variant}.gpkg", layer="segments")
    for r in z.itertuples():
        top = (seg[seg["lage"] == r.lage].groupby("street")["length_m"].sum().sort_values(ascending=False)
               .head(5).index.tolist())
        rows.append({"Stadt": slug, "Variante": variant, "Lage": r.lage.removeprefix("lage_"), "Länge km": r.length_km,
                     "Straßenraum ha": r.area_ha, "POIs": r.poi_count, "Betriebe je 100 m": r.density_per_100m,
                     "Filialanteil": f"{r.brand_share:.0%}", "Hauptstraßen (nach Länge)": ", ".join(top)})
df = pd.DataFrame(rows)
lines = ["# Städtevergleich Lagen (Street-Modus)", "",
         "Gleiche Regel in allen Städten: Schwellen aus der Heilbronn-Kalibrierung (config.yaml, "
         "`street.calibrated_thresholds`), Erdgeschoss-POIs ohne Einkaufszentren, Polygon = Straßenraum ohne Gebäude. "
         "Daten: © OpenStreetMap-Mitwirkende (ODbL).", "",
         "| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
Path("output/vergleich_staedte.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(df.drop(columns="Hauptstraßen (nach Länge)").to_string(index=False))
