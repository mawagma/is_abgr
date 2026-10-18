# Vergleichszonen Heilbronn, Germany – Methode `equal_area`

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL), abgerufen über Overpass (https://overpass.kumi.systems/api).  
OSM-Datenstand (Overpass `timestamp_osm_base`): 2026-07-24T11:04:51Z  
Abrufzeitpunkt (Cache): 2026-10-18T20:37:06+00:00  
Lauf: 2026-10-18T20:50:46+00:00 · params_hash `2722fa69d8`

## Zonen

| zone_id | rank | area_ha | poi_count | poi_density_ha | weighted_density_ha | retail_count | chain_share | ped_street_m | share_retail | share_gastro | share_service | share_culture_leisure | share_health | perimeter_m | compactness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | 1 | 10.22 | 207 | 20.26 | 18.24 | 126 | 0.437 | 2115.0 | 0.609 | 0.208 | 0.13 | 0.039 | 0.014 | 2533.5 | 0.2 |
| Z2 | 2 | 10.07 | 118 | 11.72 | 7.39 | 44 | 0.25 | 1227.0 | 0.373 | 0.347 | 0.178 | 0.068 | 0.034 | 5202.0 | 0.047 |
| Z3 | 3 | 10.06 | 71 | 7.06 | 3.83 | 19 | 0.105 | 518.0 | 0.268 | 0.366 | 0.239 | 0.099 | 0.028 | 5509.7 | 0.042 |

## Vergleichbarkeit zwischen Städten

- Abgrenzung mit derselben Regel in jeder Stadt: Glättung in Metern ({'radius_m': 100, 'sigma_m': 40}), Klassen relativ zum Spitzenwert der Stadt (`peak_share` [0.5, 0.25, 0.1]).
- Größere Polygone sammeln mehr GPS-Signale. Frequenzen deshalb nicht absolut, sondern normiert vergleichen: **Frequenz je ha** (`area_ha`) und **je 100 m Fußgängerzone** (`ped_street_m`).
- `weighted_density_ha` = gewichtete POIs je ha; `chain_share` = Filialisierungsgrad (Anteil Einzelhandel mit OSM-Tag `brand`), ein typisches Merkmal von 1A-Lagen.

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Zonen, gültig, nicht leer | 3 Zonen; leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Z1: Fläche ≥ 2000 m² | 102157 m² | True |
| OK | POI-Dichte Z1 > Z2 > Z3 | 20.26 > 11.72 > 7.06 POI/ha | True |
| OK | Z1: ein Polygon | Polygon, 1 Teil(e) | False |
| WARNUNG | Z2: ein Polygon | MultiPolygon, 2 Teil(e) | False |
| WARNUNG | Z3: ein Polygon | MultiPolygon, 7 Teil(e) | False |
| OK | Z1: Polsby-Popper ≥ 0.2 | 0.200 | False |
| WARNUNG | Z2: Polsby-Popper ≥ 0.2 | 0.047 | False |
| WARNUNG | Z3: Polsby-Popper ≥ 0.2 | 0.042 | False |
| OK | Sensitivität h3_resolution=12: IoU(Z1) ≥ 0.7 | IoU = 0.781 | False |
| OK | Sensitivität smoothing={'radius_m': 150, 'sigma_m': 60}: IoU(Z1) ≥ 0.7 | IoU = 0.788 | False |
| OK | Plausibilität: Z1 schneidet „Fleiner Straße“ | 3 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Sülmerstraße“ | 7 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Kaiserstraße“ | 13 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Marktplatz“ | 4 OSM-Objekt(e) mit diesem Namen | False |

## Suchraum und Daten

- Zentrum: place=city (49.14229, 9.21866), Radius 2000 m, Suchraum 1254.6 ha (mit Verwaltungsgrenze verschnitten)
- POIs nach Bereinigung: 1351 (retail: 455, gastro: 303, service: 271, culture_leisure: 268, health: 54)
- H3-Zellen: 6250 (Auflösung 11, Ø 0.20 ha), davon Dichte > 0: 4611
- Inseln (klassifiziert, nicht mit Z1 verbunden): 0 Zellen, 0.0 ha

## Parameter

Overrides gegenüber `config.yaml`: classification='equal_area'

Abweichungen/Auslegungen gegenüber CLAUDE.md:

- Ringe aus kumulativen Zellmengen (Z1, Z1+Z2, Z1+Z2+Z3) gebildet, damit zwischen den Zonen keine Lücken durch getrenntes Schließen/Vereinfachen entstehen; anschließend Z2 −= Z1, Z3 −= Z1 ∪ Z2.
- Zusätzlicher Parameter `min_part_m2` (500 m²): Polygonteile darunter sind Splitter aus dem getrennten Vereinfachen der kumulativen Flächen und werden verworfen (kleine Lücken möglich).
- Z1 = 1A-Lage, Z2 = 1B-Lage, Z3 = 2R-Lage; Mindestfläche 1A siehe `min_zone_m2`.
- POI-Gewicht = Kategoriegewicht × Flächenfaktor (nur Einzelhandel, `size_weighting`; Flächen sind Schätzwerte).
- Dateinamen mit Methodensuffix, damit die drei Läufe einander nicht überschreiben.
- Polsby-Popper wird auf die Ringfläche gerechnet; Ringe (Z2, Z3) haben dadurch systematisch niedrige Werte.

```yaml
city: Heilbronn, Germany
search_radius_m: 2000
h3_resolution: 11
smoothing:
  radius_m: 100
  sigma_m: 40
classification: equal_area
peak_share:
- 0.5
- 0.25
- 0.1
min_zone_m2:
  Z1: 2000
quantiles:
- 0.5
- 0.75
- 0.9
equal_area_ha:
- 10
- 20
- 30
closing_buffer_m: 10
min_hole_ha: 0.5
simplify_m: 5
weights:
  retail: 1.0
  gastro: 0.5
  service: 0.3
  culture_leisure: 0.15
  health: 0.15
size_weighting:
  enabled: true
  ref_area_m2: 200
  exponent: 0.5
  clip:
  - 0.5
  - 4.0
  chain_factor: 1.2
  not_central_factor: 0.2
  not_central:
  - car
  - car_repair
  - car_parts
  - tyres
  - motorcycle
  - truck
  - furniture
  - kitchen
  - bed
  - carpet
  - doityourself
  - hardware
  - garden_centre
  - wholesale
  - gas
  - bathroom_furnishing
  - farm
  - trade
  - building_materials
  - boat
  - caravan
  - fuel
  shop_area_m2:
    department_store: 5000
    mall: 200
    clothes: 350
    shoes: 300
    sports: 600
    outdoor: 400
    electronics: 800
    books: 400
    toys: 400
    variety_store: 400
    chemist: 600
    supermarket: 200
    cosmetics: 150
    perfumery: 200
    bag: 150
    jewelry: 80
    watches: 80
    optician: 120
    hearing_aids: 80
    gift: 100
    bakery: 60
    butcher: 80
    confectionery: 60
    coffee: 60
    tea: 60
    deli: 80
    mobile_phone: 60
    telecommunication: 80
    kiosk: 30
    tobacco: 30
    e-cigarette: 30
    convenience: 80
    beverages: 150
    alcohol: 80
  brand_area_m2:
    Galeria Kaufhof: 12000
    Galeria: 12000
    Primark: 5000
    C&A: 2000
    H&M: 1800
    TK Maxx: 1500
    Müller: 1500
    Decathlon: 2500
    Intersport: 1000
    Osiander: 1000
    Thalia: 1000
    MediaMarkt: 3000
    Saturn: 3000
    Woolworth: 800
    Action: 800
    New Yorker: 700
    dm: 600
    Rossmann: 500
    TEDi: 500
    Takko: 500
    KiK: 450
    NKD: 450
    Deichmann: 400
    Zeeman: 400
    s.Oliver: 400
    Ernsting's family: 300
    Vero Moda: 300
    Snipes: 300
    Nanu-Nana: 300
    EuroShop: 300
    Douglas: 300
    Jack Wolfskin: 250
    BONITA: 250
    Fielmann: 250
    engbers: 200
    comma: 200
    Tally Weijl: 200
    Foot Locker: 200
    Hunkemöller: 150
    OLYMP: 150
    Tchibo: 120
    Christ: 100
    Calzedonia: 100
    Intimissimi: 100
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
      - hairdresser
      - beauty
      - massage
      - tattoo
      - travel_agency
      - dry_cleaning
      - laundry
      - tailor
      - funeral_directors
      - bookmaker
      - lottery
      - pawnbroker
      - money_lender
      - gold_buyer
      - copyshop
      - international_calls
      - ticket
      - storage_rental
      - tool_hire
      - rental
      - repair
      - license_plates
      - cannabis
      - erotic
      - nails
    amenity:
    - pharmacy
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
    shop:
    - hairdresser
    - beauty
    - massage
    - tattoo
    - travel_agency
    - dry_cleaning
    - laundry
    - tailor
    - funeral_directors
    - bookmaker
    - lottery
    - pawnbroker
    - money_lender
    - gold_buyer
    - copyshop
    - international_calls
    - ticket
    - storage_rental
    - tool_hire
    - rental
    - repair
    - license_plates
    - nails
    amenity:
    - bank
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
  - h3_resolution: 12
  - smoothing:
      radius_m: 150
      sigma_m: 60
  min_iou: 0.7
  plausibility:
    Heilbronn, Germany:
    - Fleiner Straße
    - Sülmerstraße
    - Kaiserstraße
    - Marktplatz
```
