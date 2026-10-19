# Lagevergleich Stuttgart, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:54:53+00:00, params_hash `31c0278e2f`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Stuttgart, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.56 | 1.096 | 5.36 | 8.04 | 139 | 98 | 0.388 | 0.633 |
| lage_1b | 1.0–2.0 | 3.47 | 0.779 | 10.03 | 0.69 | 229 | 44 | 0.218 | 0.227 |
| lage_2 | 2.0–4.0 | 5.74 | 4.057 | 20.16 | 5.32 | 228 | 324 | 0.263 | 0.191 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.096 | 8.04 | 98 | 15.9 | 0.633 |
| lage_1b | 0.779 | 0.69 | 44 | 6.34 | 0.227 |
| lage_2 | 4.057 | 5.32 | 324 | 8.96 | 0.191 |

## Straßennamen je Lage

- **lage_1a**: Alte Poststraße; Büchsenstraße; Gymnasiumstraße; Königstraße; Thouretstraße
- **lage_1b**: Hirschstraße; Kirchstraße; Königstraße; Marktplatz; Neue Brücke; Stiftstraße; Tübinger Straße
- **lage_2**: Alte Poststraße; Arnulf-Klett-Platz; Bärenstraße; Calwer Passage; Calwer Platz; Calwer Straße; Dornstraße; Eberhardstraße; Geißstraße; Gloria-Passage; Gymnasiumstraße; Hirschstraße; Kienestraße; Kronenstraße; Königstraße; Lange Straße; Lautenschlagerstraße; Marienstraße; Nadlerstraße; Rathauspassage; Schulstraße; Sophienstraße; Sporerstraße; Therese-Huber-Gasse; Töpferplatz; Töpferstraße; Tübinger Straße; Unter der Mauer

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 8.11 | 0.316 | 0.2 | – |
| lage_1b | 3.48 | – | – | 0.9 |
| lage_2 | 4.64 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.05 | 4 | 0.5 | keine | Wilhelmstraße |
| 2 | 0.028 | 3 | 0.667 | keine | Hauptstätter Straße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 15.9 / 1b 6.34 / 2 8.96 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 15.9 / 1b 6.34 / 2 8.96 je 100 m | False |
| OK | lage_1a: Länge 0.6–1.2 km | 1.096 km | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.779 km → lage_1b.min_density (3.48) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 4.057 km → lage_2.min_density (4.64) erhöhen | False |
| OK | Plausibilität: 1a enthält „Königstraße“ | 822 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
