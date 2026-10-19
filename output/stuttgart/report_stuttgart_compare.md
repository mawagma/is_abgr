# Lagevergleich Stuttgart, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T09:38:01Z, Lauf 2026-10-19T11:56:09+00:00, params_hash `91342a3ca4`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Stuttgart, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 2.01 | 1.276 | 6.15 | 2.79 | 165 | 100 | 0.345 | 0.63 |
| lage_1b | 1.0–2.0 | 2.95 | 2.344 | 9.79 | 3.93 | 182 | 197 | 0.275 | 0.198 |
| lage_2 | 2.0–4.0 | 6.15 | 3.457 | 20.22 | 5.51 | 257 | 211 | 0.218 | 0.19 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.276 | 2.79 | 100 | 11.54 | 0.63 |
| lage_1b | 2.344 | 3.93 | 197 | 9.65 | 0.198 |
| lage_2 | 3.457 | 5.51 | 211 | 6.97 | 0.19 |

## Straßennamen je Lage

- **lage_1a**: Alte Poststraße; Büchsenstraße; Gymnasiumstraße; Königstraße; Neue Brücke; Schulstraße; Stiftstraße
- **lage_1b**: Arnulf-Klett-Platz; Bärenstraße; Calwer Straße; Gloria-Passage; Hirschstraße; Kienestraße; Kirchstraße; Kronenstraße; Königstraße; Lautenschlagerstraße; Marienstraße; Marktplatz; Nadlerstraße; Neue Brücke; Schulstraße; Sophienstraße; Sporerstraße; Tübinger Straße
- **lage_2**: Alte Poststraße; Arnulf-Klett-Platz; Calwer Passage; Calwer Platz; Calwer Straße; Dornstraße; Eberhardstraße; Geißstraße; Gymnasiumstraße; Hirschstraße; Kienestraße; Kleine Königstraße; Kronenstraße; Kronprinzstraße; Krumme Straße; Königstraße; Lange Straße; Marienstraße; Marktplatz; Nadlerstraße; Rathauspassage; Rotebühlplatz; Sophienstraße; Steinstraße; Therese-Huber-Gasse; Töpferplatz; Töpferstraße; Tübinger Straße; Unter der Mauer

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct | alt_min_density | alt_min_brand_share |
|---|---|---|---|---|---|---|
| lage_1a | 7.24 | 0.287 | 0.2 | – | – | – |
| lage_1b | 3.1 | – | – | 0.9 | 6.21 | 0.108 |
| lage_2 | 4.14 | – | – | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.05 | 2 | 1.0 | lage_1b | Lautenschlagerstraße |
| 2 | 0.05 | 4 | 0.5 | keine | Wilhelmstraße |
| 3 | 0.028 | 3 | 0.667 | keine | Hauptstätter Straße |
| 4 | 0.017 | 3 | 0.667 | keine | Bandstraße |
| 5 | 0.15 | 10 | 0.3 | lage_2 | Lange Straße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 11.54 > 9.65 > 6.97 je 100 m | True |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 1.276 km → lage_1a.min_density (7.24) erhöhen | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 2.344 km → lage_1b.min_density (3.1) erhöhen | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.457 km | False |
| OK | Plausibilität: 1a enthält „Königstraße“ | 778 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
