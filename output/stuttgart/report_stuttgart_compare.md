# Lagevergleich Stuttgart, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T20:03:44+00:00, params_hash `dd7bc8554a`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Stuttgart, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.56 | 1.146 | 5.36 | 8.12 | 139 | 98 | 0.388 | 0.633 |
| lage_1b | 1.0–2.0 | 3.47 | 0.685 | 10.03 | 0.44 | 229 | 39 | 0.218 | 0.231 |
| lage_2 | 2.0–4.0 | 5.74 | 4.101 | 20.16 | 5.49 | 228 | 329 | 0.263 | 0.191 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.146 | 8.12 | 98 | 15.2 | 0.633 |
| lage_1b | 0.685 | 0.44 | 39 | 6.26 | 0.231 |
| lage_2 | 4.101 | 5.49 | 329 | 9.02 | 0.191 |

## Straßennamen je Lage

- **lage_1a**: Alte Poststraße; Büchsenstraße; Gymnasiumstraße; Königstraße; Schulstraße; Thouretstraße
- **lage_1b**: Hirschstraße; Kirchstraße; Königstraße; Marktplatz; Neue Brücke; Stiftstraße
- **lage_2**: Alte Poststraße; Arnulf-Klett-Platz; Bärenstraße; Calwer Passage; Calwer Platz; Calwer Straße; Dornstraße; Eberhardstraße; Geißstraße; Gloria-Passage; Gymnasiumstraße; Hirschstraße; Kienestraße; Kronenstraße; Königstraße; Lange Straße; Lautenschlagerstraße; Marienstraße; Nadlerstraße; Rathauspassage; Schulstraße; Sophienstraße; Sporerstraße; Therese-Huber-Gasse; Töpferplatz; Töpferstraße; Tübinger Straße; Unter der Mauer

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 9.27 | 0.237 | 0.2 | – |
| lage_1b | 3.48 | – | – | 0.9 |
| lage_2 | 4.64 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.1 | 12 | 0.333 | lage_2 | Marienstraße |
| 2 | 0.05 | 4 | 0.5 | keine | Wilhelmstraße |
| 3 | 0.028 | 3 | 0.667 | keine | Hauptstätter Straße |
| 4 | 0.05 | 7 | 0.286 | lage_2 | Kronenstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 15.2 / 1b 6.26 / 2 9.02 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 15.2 / 1b 6.26 / 2 9.02 je 100 m | False |
| OK | lage_1a: Länge 0.6–1.2 km | 1.146 km | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.685 km → lage_1b.min_density (3.48) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 4.101 km → lage_2.min_density (4.64) erhöhen | False |
| OK | Plausibilität: 1a enthält „Königstraße“ | 822 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
