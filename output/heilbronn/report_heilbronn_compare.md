# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:54:28+00:00, params_hash `0deb39f0ef`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: keine. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.39–0.65 | 1.45 | 0.301 | 5.94 | 1.3 | 128 | 26 | 0.266 | 0.577 |
| lage_1b | 0.44–0.73 | 2.84 | 1.152 | 9.93 | 3.15 | 104 | 53 | 0.231 | 0.283 |
| lage_2 | 2.0–4.0 | 5.53 | 3.543 | 20.37 | 4.39 | 99 | 162 | 0.101 | 0.154 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.301 | 1.3 | 26 | 14.94 | 0.577 |
| lage_1b | 1.152 | 3.15 | 53 | 5.75 | 0.283 |
| lage_2 | 3.543 | 4.39 | 162 | 5.18 | 0.154 |

## Straßennamen je Lage

- **lage_1a**: Deutschhofstraße; Fleiner Straße; Kiliansplatz
- **lage_1b**: Fischergasse; Fleiner Straße; Gerberstraße; Kaiserstraße; Kramstraße; Sülmerstraße
- **lage_2**: Allee; Am Kieselmarkt; Am Wollhaus; Berliner Platz; Deutschhofstraße; Eichgasse; Falkenstraße; Gemmingergasse; Glockengießerhof; Große Bahngasse; Gustav-Binder-Straße; Götzenturmstraße; Hämmerlinggasse; Jakobgasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Klarastraße; Lohtorstraße; Marktplatz; Obere Neckarstraße; Schellengasse; Sonnengasse; Sülmerstraße; Titotstraße; Turmstraße; Untere Neckarstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 4.75 | 0.469 | 0.2 | – |
| lage_1b | 2.03 | – | – | 0.9 |
| lage_2 | 2.71 | – | – | – |

## Übereinstimmung mit der Referenz (Expertenabgrenzung, Segmentlänge)

Referenz: `reference/heilbronn_lagen.geojson`; km-Ziele für 1a/1b = Referenzlänge ± 25%.

| lage | precision | recall | f1 |
|---|---|---|---|
| lage_1a | 1.0 | 0.582 | 0.736 |
| lage_1b | 0.437 | 0.861 | 0.58 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.054 | 2 | 0.5 | keine | Sülmermühlstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 14.94 / 1b 5.75 / 2 5.18 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 14.94 / 1b 5.75 / 2 5.18 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.39–0.65 km | 0.301 km → lage_1a.min_density (4.75) senken oder lage_1a.min_brand_share (0.469) senken | False |
| WARNUNG | lage_1b: Länge 0.44–0.73 km | 1.152 km → lage_1b.min_density (2.03) erhöhen | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.543 km | False |
| WARNUNG | lage_1a: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.736, Precision 1.0, Recall 0.582 | False |
| WARNUNG | lage_1b: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.58, Precision 0.437, Recall 0.861 | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 237 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
