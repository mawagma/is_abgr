"""Stapellauf über eine Städteliste: je Stadt Street- und Rastermodus, danach Vergleichstabelle.

python -m zones.batch staedte.csv [--source postgis] [--dsn postgresql://osm@host:5432/osm] [--modes street grid]

CSV (Komma oder Semikolon, UTF-8): Spalte city (z. B. „Würzburg, Germany“), optional lon, lat (Zentrum, falls der
Ortsname nicht eindeutig ist) und reference (Pfad zu einer Referenzabgrenzung)."""
import argparse
import subprocess
import sys
import traceback
from pathlib import Path

import pandas as pd

from .cli import main, slug


def run(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cities")
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--source", choices=["overpass", "postgis"])
    ap.add_argument("--dsn")
    ap.add_argument("--modes", nargs="+", default=["street", "grid"], choices=["street", "grid"])
    a = ap.parse_args(argv)
    df = pd.read_csv(a.cities, sep=None, engine="python", encoding="utf-8-sig", dtype=str).fillna("")
    if "city" not in df:
        sys.exit("Spalte city fehlt in der Städteliste")
    common = ["--config", a.config] + (["--source", a.source] if a.source else []) + (["--dsn", a.dsn] if a.dsn else [])
    log = []
    for r in df.itertuples():
        extra = ["--city", r.city]
        if getattr(r, "lon", "") and getattr(r, "lat", ""):
            extra += ["--center", f"{r.lon},{r.lat}"]
        for mode in a.modes:
            args = common + extra + ["--mode", mode] + (["--reference", r.reference] if mode == "street" and getattr(
                r, "reference", "") else []) + (["--no-auto-calibrate"] if mode == "street" else [])
            print(f"\n=== {r.city} – {mode} ===", flush=True)
            try:
                code, err = main(args), ""
            except Exception as e:  # eine Stadt darf den Stapel nicht abbrechen
                traceback.print_exc()
                code, err = 2, f"{type(e).__name__}: {e}"
            log.append({"city": r.city, "mode": mode, "exit": code,
                        "status": "OK" if code == 0 else "harte Prüfung verletzt" if code == 1 else "Fehler", "detail": err})
    out = Path("output")
    out.mkdir(exist_ok=True)
    pd.DataFrame(log).to_csv(out / "batch_protokoll.csv", index=False, sep=";", encoding="utf-8-sig")
    ok = [slug(c) for c in df["city"] if (out / slug(c) / f"zones_{slug(c)}_street.gpkg").exists()]
    if "street" in a.modes and ok:
        subprocess.run([sys.executable, str(Path(__file__).parents[2] / "tools" / "compare_cities.py"),
                        *[f"{s}:street" for s in ok]], check=False)
    print(f"\nProtokoll: {out / 'batch_protokoll.csv'} · Vergleich: {out / 'vergleich_staedte.md'}")
    return 0 if all(x["exit"] == 0 for x in log) else 1


if __name__ == "__main__":
    sys.exit(run())
