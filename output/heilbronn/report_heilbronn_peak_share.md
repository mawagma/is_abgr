# Vergleichszonen Heilbronn, Germany – Methode `peak_share`

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL), abgerufen über Overpass (https://overpass.kumi.systems/api).  
OSM-Datenstand (Overpass `timestamp_osm_base`): 2026-10-19T06:41:06Z  
Abrufzeitpunkt (Cache): 2026-10-19T07:12:03+00:00  
Lauf: 2026-10-19T07:13:20+00:00 · params_hash `1bf7cc4932`

## Zonen

| zone_id | rank | area_ha | poi_count | poi_density_ha | weighted_density_ha | retail_count | chain_share | ped_street_m | share_retail | share_gastro | share_service | share_culture_leisure | share_health | perimeter_m | compactness |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Z1 | 1 | 3.69 | 74 | 20.08 | 25.37 | 61 | 0.377 | 927.0 | 0.824 | 0.176 | 0.0 | 0 | 0 | 1186.7 | 0.329 |
| Z2 | 2 | 9.93 | 142 | 14.29 | 16.33 | 86 | 0.233 | 1768.0 | 0.606 | 0.38 | 0.014 | 0 | 0 | 3378.1 | 0.109 |
| Z3 | 3 | 20.73 | 102 | 4.92 | 5.43 | 52 | 0.096 | 1400.0 | 0.51 | 0.402 | 0.088 | 0 | 0 | 6384.4 | 0.064 |

## Vergleichbarkeit zwischen Städten

- Abgrenzung mit derselben Regel in jeder Stadt: Glättung in Metern ({'radius_m': 50, 'sigma_m': 40}), Klassen relativ zum Spitzenwert der Stadt (`peak_share` [0.5, 0.25, 0.1]).
- Größere Polygone sammeln mehr GPS-Signale. Frequenzen deshalb nicht absolut, sondern normiert vergleichen: **Frequenz je ha** (`area_ha`) und **je 100 m Fußgängerzone** (`ped_street_m`).
- `weighted_density_ha` = gewichtete POIs je ha; `chain_share` = Filialisierungsgrad (Anteil Einzelhandel mit OSM-Tag `brand`), ein typisches Merkmal von 1A-Lagen.

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Zonen, gültig, nicht leer | 3 Zonen; leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Z1: Fläche ≥ 2000 m² | 36860 m² | True |
| OK | POI-Dichte Z1 > Z2 > Z3 | 20.08 > 14.29 > 4.92 POI/ha | True |
| OK | Z1: ein Polygon | Polygon, 1 Teil(e) | False |
| WARNUNG | Z2: ein Polygon | MultiPolygon, 4 Teil(e) | False |
| OK | Z3: ein Polygon | Polygon, 1 Teil(e) | False |
| OK | Z1: Polsby-Popper ≥ 0.2 | 0.329 | False |
| WARNUNG | Z2: Polsby-Popper ≥ 0.2 | 0.109 | False |
| WARNUNG | Z3: Polsby-Popper ≥ 0.2 | 0.064 | False |
| WARNUNG | Sensitivität h3_resolution=12: IoU(Z1) ≥ 0.7 | IoU = 0.584 | False |
| WARNUNG | Sensitivität smoothing={'radius_m': 150, 'sigma_m': 60}: IoU(Z1) ≥ 0.7 | IoU = 0.345 | False |
| OK | Plausibilität: Z1 schneidet „Fleiner Straße“ | 3 OSM-Objekt(e) mit diesem Namen | False |
| WARNUNG | Plausibilität: Z1 schneidet „Sülmerstraße“ | 7 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Kaiserstraße“ | 13 OSM-Objekt(e) mit diesem Namen | False |
| OK | Plausibilität: Z1 schneidet „Marktplatz“ | 4 OSM-Objekt(e) mit diesem Namen | False |

## Suchraum und Daten

- Zentrum: place=city (49.14229, 9.21866), Radius 2000 m, Suchraum 1254.6 ha (mit Verwaltungsgrenze verschnitten)
- POIs nach Bereinigung: 860 (retail: 545, gastro: 293, service: 22)
- H3-Zellen: 6250 (Auflösung 11, Ø 0.20 ha), davon Dichte > 0: 1991
- Inseln (klassifiziert, nicht mit Z1 verbunden): 211 Zellen, 42.3 ha – Klassen {2: 10, 3: 201}

## Parameter

Overrides gegenüber `config.yaml`: mode='grid'

Abweichungen/Auslegungen gegenüber CLAUDE.md:

- Ringe aus kumulativen Zellmengen (Z1, Z1+Z2, Z1+Z2+Z3) gebildet, damit zwischen den Zonen keine Lücken durch getrenntes Schließen/Vereinfachen entstehen; anschließend Z2 −= Z1, Z3 −= Z1 ∪ Z2.
- Zusätzlicher Parameter `min_part_m2` (500 m²): Polygonteile darunter sind Splitter aus dem getrennten Vereinfachen der kumulativen Flächen und werden verworfen (kleine Lücken möglich).
- Z1 = 1A-Lage, Z2 = 1B-Lage, Z3 = 2R-Lage; Mindestfläche 1A siehe `min_zone_m2`.
- POI-Gewicht = Kategoriegewicht × Flächenfaktor (nur Einzelhandel, `size_weighting`; Flächen sind Schätzwerte).
- Dateinamen mit Methodensuffix, damit die drei Läufe einander nicht überschreiben.
- Polsby-Popper wird auf die Ringfläche gerechnet; Ringe (Z2, Z3) haben dadurch systematisch niedrige Werte.

```yaml
city: Heilbronn, Germany
mode: grid
poi_model: ground_floor
search_radius_m: 2000
h3_resolution: 11
smoothing:
  radius_m: 50
  sigma_m: 40
classification: peak_share
peak_share:
- 0.5
- 0.25
- 0.1
min_zone_m2:
  Z1: 2000
max_area_ha:
- 6
- 10
- 20
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
overpass_fallback_urls:
- https://overpass.private.coffee/api
- https://maps.mail.ru/osm/tools/overpass/api
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
exclude_malls: true
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
ground_floor_categories:
  retail:
    shop:
      exclude:
      - vacant
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
    amenity:
    - bank
street:
  segment_length_m: 50
  snap_max_dist_m: 30
  buffer_m: 20
  smoothing_neighbors: 1
  brand_weight: 1.75
  thresholds:
    lage_1a:
      min_density: 8
      min_brand_share: 0.4
    lage_1b:
      min_density: 5
    lage_2:
      min_density: 2
  max_gap_segments: 1
  seed: strongest_chain
  min_hole_ha: 0.2
  target_ranges_km:
    lage_1a:
    - 0.6
    - 1.2
    lage_1b:
    - 1.0
    - 2.0
    lage_2:
    - 2.0
    - 4.0
  auto_calibrate: false
  reference:
    Heilbronn, Germany: reference/heilbronn_lagen.geojson
  reference_match_m: 5
  reference_tolerance: 0.25
  lagen_from_reference: false
  street_space_only: true
  building_query_radius_m: 1000
  calibration_iterations: 40
  highway:
  - pedestrian
  - living_street
  - residential
  - unclassified
  - tertiary
  - secondary
  - primary
  highway_named_only:
  - footway
  - path
  touch_tolerance_m: 0.5
  plausibility:
    Heilbronn, Germany:
    - Fleiner Straße
```
