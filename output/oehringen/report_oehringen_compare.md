# Lagevergleich Öhringen, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T09:38:01Z, Lauf 2026-10-19T12:00:26+00:00, params_hash `889d7457c5`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Öhringen, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.42 | 0.633 | 4.29 | 1.04 | 73 | 46 | 0.096 | 0.109 |
| lage_1b | 1.0–2.0 | 1.6 | 0.094 | 5.08 | 0.16 | 38 | 3 | 0.105 | 0.333 |
| lage_2 | 2.0–4.0 | 1.81 | 1.57 | 8.3 | 2.95 | 20 | 51 | 0.15 | 0.059 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.633 | 1.04 | 46 | 7.86 | 0.109 |
| lage_1b | 0.094 | 0.16 | 3 | 4.01 | 0.333 |
| lage_2 | 1.57 | 2.95 | 51 | 3.39 | 0.059 |

## Straßennamen je Lage

- **lage_1a**: Kirchgasse; Marktplatz; Marktstraße; Poststraße
- **lage_1b**: Bahnhofstraße
- **lage_2**: Bahnhofstraße; Bismarckstraße; Büttelbronner Straße; Farbgasse; Haagweg; Heilbronner Straße; Hirschgasse; Ledergasse; Poststraße; Probsthof; Rathausstraße; Schafgasse; Schillerstraße; Untere Torstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct | alt_min_density | alt_min_brand_share |
|---|---|---|---|---|---|---|
| lage_1a | 3.34 | 0.067 | 0.2 | – | – | – |
| lage_1b | 1.43 | – | – | 0.9 | 2.86 | 0.025 |
| lage_2 | 1.91 | – | – | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.046 | 2 | 0.5 | keine | Bahnhof |
| 2 | 0.05 | 2 | 0.5 | keine | Karlsvorstadt |
| 3 | 0.05 | 1 | 1.0 | lage_2 | Büttelbronner Straße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 7.86 > 4.01 > 3.39 je 100 m | True |
| OK | lage_1a: Länge 0.6–1.2 km | 0.633 km | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.094 km → lage_1b.min_density (1.43) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 1.57 km → lage_2.min_density (1.91) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
