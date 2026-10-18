# Vergleichszonen Heilbronn, Germany – Methode `equal_area`

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL), abgerufen über Overpass (https://overpass.kumi.systems/api).  
OSM-Datenstand (Overpass `timestamp_osm_base`): 2026-07-24T11:04:51Z  
Abrufzeitpunkt (Cache): 2026-10-18T20:37:06+00:00  
Lauf: 2026-10-18T20:38:51+00:00 · params_hash `32858996eb`

## Zonen

| zone_id | rank | area_ha | poi_count | poi_density_ha | share_retail | share_gastro | share_service | share_culture_leisure | share_health | perimeter_m | compactness |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | 1 | 9.98 | 175 | 17.53 | 0.6 | 0.269 | 0.074 | 0.051 | 0.006 | 1445.1 | 0.601 |
| Z2 | 2 | 9.9 | 116 | 11.72 | 0.603 | 0.216 | 0.069 | 0.034 | 0.078 | 3030.7 | 0.135 |
| Z3 | 3 | 9.89 | 60 | 6.07 | 0.383 | 0.35 | 0.183 | 0.083 | 0.0 | 4039.2 | 0.076 |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Zonen, gültig, nicht leer | 3 Zonen; leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | POI-Dichte Z1 > Z2 > Z3 | 17.53 > 11.72 > 6.07 POI/ha | True |
| OK | Z1: ein Polygon | Polygon, 1 Teil(e) | False |
| OK | Z2: ein Polygon | Polygon, 1 Teil(e) | False |
| WARNUNG | Z3: ein Polygon | MultiPolygon, 2 Teil(e) | False |
| OK | Z1: Polsby-Popper ≥ 0.2 | 0.601 | False |
| WARNUNG | Z2: Polsby-Popper ≥ 0.2 | 0.135 | False |
| WARNUNG | Z3: Polsby-Popper ≥ 0.2 | 0.076 | False |
| WARNUNG | Sensitivität h3_resolution=11: IoU(Z1) ≥ 0.7 | IoU = 0.628 | False |
| OK | Sensitivität smoothing={'k': 2, 'sigma': 1.5}: IoU(Z1) ≥ 0.7 | IoU = 0.753 | False |
| OK | Plausibilität: Z1 schneidet „Fleiner Straße“ | 3 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Sülmerstraße“ | 7 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Kaiserstraße“ | 13 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Marktplatz“ | 4 OSM-Objekt(e) mit diesem Namen | False |

## Suchraum und Daten

- Zentrum: place=city (49.14229, 9.21866), Radius 2000 m, Suchraum 1254.6 ha (mit Verwaltungsgrenze verschnitten)
- POIs nach Bereinigung: 1354 (retail: 571, gastro: 303, culture_leisure: 268, service: 158, health: 54)
- H3-Zellen: 895 (Auflösung 10, Ø 1.40 ha), davon Dichte > 0: 893
- Inseln (klassifiziert, nicht mit Z1 verbunden): 0 Zellen, 0.0 ha

## Parameter

Overrides gegenüber `config.yaml`: classification='equal_area'

Abweichungen/Auslegungen gegenüber CLAUDE.md:

- Ringe aus kumulativen Zellmengen (Z1, Z1+Z2, Z1+Z2+Z3) gebildet, damit zwischen den Zonen keine Lücken durch getrenntes Schließen/Vereinfachen entstehen; anschließend Z2 −= Z1, Z3 −= Z1 ∪ Z2.
- Zusätzlicher Parameter `min_part_m2` (500 m²): Polygonteile darunter sind Splitter aus dem getrennten Vereinfachen der kumulativen Flächen und werden verworfen (kleine Lücken möglich).
- Dateinamen mit Methodensuffix, damit die drei Läufe einander nicht überschreiben.
- Polsby-Popper wird auf die Ringfläche gerechnet; Ringe (Z2, Z3) haben dadurch systematisch niedrige Werte.

```yaml
city: Heilbronn, Germany
search_radius_m: 2000
h3_resolution: 10
smoothing:
  k: 2
  sigma: 1.0
classification: equal_area
quantiles:
- 0.5
- 0.75
- 0.9
equal_area_ha:
- 10
- 20
- 30
closing_buffer_m: 25
min_hole_ha: 0.5
simplify_m: 5
weights:
  retail: 1.0
  gastro: 1.0
  service: 0.5
  culture_leisure: 0.7
  health: 0.5
crs_metric: EPSG:25832
crs_export: EPSG:4326
cache_dir: cache
output_dir: output
overpass_url: https://overpass.kumi.systems/api
requests_timeout_s: 300
overpass_retries: 20
overpass_retry_wait_s: 30
random_seed: 42
dedupe_m: 15
min_part_m2: 500
categories:
  retail:
    shop:
      exclude:
      - vacant
  gastro:
    amenity:
    - restaurant
    - cafe
    - fast_food
    - bar
    - pub
    - ice_cream
    - biergarten
  service:
    amenity:
    - bank
    - pharmacy
    - post_office
    craft: true
    office: true
  culture_leisure:
    tourism:
    - museum
    - gallery
    - attraction
    amenity:
    - cinema
    - theatre
    - library
    - arts_centre
    leisure:
      exclude:
      - park
      - garden
      - pitch
      - playground
  health:
    healthcare: true
    amenity:
    - doctors
    - dentist
exclude_prefixes:
- 'disused:'
- 'abandoned:'
context:
  pedestrian:
    highway:
    - pedestrian
    - living_street
  transit_stop:
    highway:
    - bus_stop
    public_transport:
    - platform
    - stop_position
    - station
    railway:
    - tram_stop
    - station
    - halt
qa:
  max_overlap_m2: 1.0
  min_compactness: 0.2
  sensitivity:
  - h3_resolution: 11
  - smoothing:
      k: 2
      sigma: 1.5
  min_iou: 0.7
  plausibility:
    Heilbronn, Germany:
    - Fleiner Straße
    - Sülmerstraße
    - Kaiserstraße
    - Marktplatz
```
