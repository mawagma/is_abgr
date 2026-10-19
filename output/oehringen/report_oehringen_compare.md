# Lagevergleich Öhringen, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T08:28:36Z, Lauf 2026-10-19T08:30:40+00:00, params_hash `61571f6770`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Öhringen, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.42 | 0.046 | 4.29 | 0.11 | 73 | 2 | 0.096 | 0.5 |
| lage_1b | 1.0–2.0 | 1.6 | 0.0 | 5.08 | 0.0 | 38 | 0 | 0.105 | 0.0 |
| lage_2 | 2.0–4.0 | 1.81 | 0.0 | 8.3 | 0.0 | 20 | 0 | 0.15 | 0.0 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.046 | 0.11 | 2 | 5.97 | 0.5 |
| lage_1b | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| lage_2 | 0.0 | 0.0 | 0 | 0.0 | 0.0 |

## Straßennamen je Lage

- **lage_1a**: Bahnhof
- **lage_1b**: –
- **lage_2**: –

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 4.2 | 0.4 |
| lage_1b | 3.76 | – |
| lage_2 | 2.0 | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| FEHLER | Genau 3 Lagen, gültig, nicht leer | leer: ['lage_1b', 'lage_2'] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| FEHLER | Dichte 1a > 1b > 2 | 5.97 > 0.0 > 0.0 je 100 m | True |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.046 km → lage_1a.min_density (4.2) senken oder lage_1a.min_brand_share (0.4) senken | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.0 km → lage_1b.min_density (3.76) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 0.0 km → lage_2.min_density (2.0) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
