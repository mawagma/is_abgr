# Lagevergleich Öhringen, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:55:09+00:00, params_hash `b0079a805f`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Öhringen, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.18 | 0.633 | 3.67 | 0.87 | 67 | 46 | 0.09 | 0.109 |
| lage_1b | 1.0–2.0 | 1.68 | 0.0 | 5.08 | 0.0 | 39 | 0 | 0.128 | 0.0 |
| lage_2 | 2.0–4.0 | 1.72 | 1.597 | 7.9 | 2.46 | 23 | 53 | 0.13 | 0.094 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.633 | 0.87 | 46 | 7.85 | 0.109 |
| lage_1b | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| lage_2 | 1.597 | 2.46 | 53 | 3.62 | 0.094 |

## Straßennamen je Lage

- **lage_1a**: Kirchgasse; Marktplatz; Marktstraße; Poststraße
- **lage_1b**: –
- **lage_2**: Bahnhofstraße; Bismarckstraße; Büttelbronner Straße; Heilbronner Straße; Hirschgasse; Kirchbrunnengasse; Ledergasse; Poststraße; Probsthof; Rathausstraße; Schafgasse; Schillerstraße; Untere Torstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 3.55 | 0.089 | 0.2 | – |
| lage_1b | 1.52 | – | – | 0.9 |
| lage_2 | 2.03 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.092 | 0 | 0.0 | keine | Friedrichsruher Straße |
| 2 | 0.046 | 2 | 0.5 | keine | Bahnhof |
| 3 | 0.05 | 2 | 0.5 | keine | Karlsvorstadt |
| 4 | 0.1 | 2 | 1.0 | lage_2 | Büttelbronner Straße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: ['lage_1b'] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 7.85 / 1b 0.0 / 2 3.62 je 100 m | True |
| OK | lage_1a: Länge 0.6–1.2 km | 0.633 km | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.0 km → lage_1b.min_density (1.52) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 1.597 km → lage_2.min_density (2.03) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
