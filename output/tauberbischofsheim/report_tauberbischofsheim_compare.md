# Lagevergleich Tauberbischofsheim, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T15:32:06Z, Lauf 2026-10-19T16:22:37+00:00, params_hash `6aaeb260b3`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Tauberbischofsheim, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.28 | 0.555 | 3.65 | 0.95 | 53 | 30 | 0.113 | 0.167 |
| lage_1b | 1.0–2.0 | 1.24 | 0.386 | 3.65 | 0.76 | 24 | 19 | 0.042 | 0.053 |
| lage_2 | 2.0–4.0 | 0.91 | 0.322 | 4.01 | 0.41 | 7 | 8 | 0.0 | 0.0 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.555 | 0.95 | 30 | 6.08 | 0.167 |
| lage_1b | 0.386 | 0.76 | 19 | 5.11 | 0.053 |
| lage_2 | 0.322 | 0.41 | 8 | 2.49 | 0.0 |

## Straßennamen je Lage

- **lage_1a**: Hauptstraße; Marktplatz
- **lage_1b**: Bahnhofstraße; Hauptstraße; Sonnenplatz; Würzburger Straße
- **lage_2**: Eichstraße; Martinsgasse; Museumstraße; Rosengasse; Schloßweg; Schmiederstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 3.28 | 0.1 | 0.2 | – |
| lage_1b | 1.41 | – | – | 0.9 |
| lage_2 | 1.87 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.083 | 2 | 0.5 | keine | Krautgartenweg |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 6.08 / 1b 5.11 / 2 2.49 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 6.08 / 1b 5.11 / 2 2.49 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.555 km → lage_1a.min_density (3.28) senken oder lage_1a.min_brand_share (0.1) senken | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.386 km → lage_1b.min_density (1.41) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 0.322 km → lage_2.min_density (1.87) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
