# Lageabgrenzung Innenstädte (1a / 1b / 2-Lage) aus OSM

Grenzt Lagen über Straßenabschnitte mit Geschäftsbesatz ab (Street-Modus) bzw. über ein H3-Raster (Rastermodus).
Ausgabe je Stadt: GeoPackage, GeoJSON (EPSG:4326), Karte (HTML) und Bericht. Alle Parameter stehen in `config.yaml`.

Daten: © OpenStreetMap-Mitwirkende (ODbL).

## Einrichtung (Windows, nur pip)

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

## Datenbank (osm2pgsql)

Erwartet wird das klassische osm2pgsql-Schema (`planet_osm_point`, `_line`, `_polygon`). Für Filialisten
(`brand:wikidata`), Leerstand (`disused:*`) usw. muss mit `--hstore` (oder `--hstore-all`) importiert worden sein.

In `config.yaml`:

```yaml
data_source: postgis
postgis:
  dsn: "postgresql://BENUTZER@HOST:5432/DATENBANK"
  prefix: planet_osm
```

Das Passwort nicht in die Config schreiben, sondern als Umgebungsvariable setzen (`set PGPASSWORD=...`) oder
in `%APPDATA%\postgresql\pgpass.conf` hinterlegen.

Prüfen, ob alle benötigten Tags abfragbar sind:

```bat
python -m zones.cli --check-db
```

## Stapellauf

Städteliste als CSV (Komma oder Semikolon, UTF-8), siehe `staedte_beispiel.csv`:

| Spalte | Pflicht | Bedeutung |
|---|---|---|
| city | ja | Ortsname wie in OSM, z. B. `Würzburg, Germany` (Teil vor dem Komma muss dem OSM-Namen entsprechen) |
| lon, lat | nein | Zentrum, falls der Name nicht eindeutig ist oder kein `place=city/town`-Knoten existiert |
| reference | nein | Expertenabgrenzung (GeoJSON-Linien mit Attribut `lage` = `lage_1a`/`lage_1b`) zur Kontrolle |

```bat
python -m zones.batch staedte.csv --source postgis
```

Ergebnis in `output\<stadt>\` je Stadt, dazu `output\vergleich_staedte.md` (alle Städte) und
`output\batch_protokoll.csv` (Status je Stadt und Modus). Fehler in einer Stadt brechen den Stapel nicht ab.

## Einzelne Stadt

```bat
python -m zones.cli --city "Würzburg, Germany" --mode street --source postgis
python -m zones.cli --city "Würzburg, Germany" --mode grid --source postgis
```

## Regeln (Street-Modus, Kurzfassung)

- Erdgeschoss-POIs (Einzelhandel, Gastronomie, Banken), ohne Einkaufszentren; Gewicht Filialist 1,75,
  zusätzlich typische Verkaufsfläche.
- Straßen in 50-m-Abschnitte; Dichte = gewichtete Betriebe je 100 m; Schwellen relativ zur stärksten 300-m-Front der Stadt.
- 1a: dichte, filialstarke Kette(n); 1b: Laufachsen (lokale Netzzentralität) mit Besatz; 2-Lage: übriger Besatz.
- Kurze Wechsel (< 100 m) werden geglättet, großflächige Gewerbegebiete ausgeschlossen.
- Polygon = Straßenraum zwischen den Fassaden (ohne Gebäude, ohne Hinterhöfe), angrenzende Plätze inklusive.

Tests: `python -m pytest -q`
