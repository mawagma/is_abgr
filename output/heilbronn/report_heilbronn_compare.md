# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T09:38:01Z, Lauf 2026-10-19T11:52:52+00:00, params_hash `7937e8dac4`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: keine. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.39–0.65 | 1.07 | 0.566 | 3.69 | 0.97 | 74 | 37 | 0.351 | 0.622 |
| lage_1b | 0.44–0.73 | 2.6 | 1.465 | 9.93 | 2.81 | 142 | 71 | 0.19 | 0.239 |
| lage_2 | 2.0–4.0 | 6.08 | 3.685 | 20.73 | 6.53 | 102 | 144 | 0.137 | 0.118 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.566 | 0.97 | 37 | 9.58 | 0.622 |
| lage_1b | 1.465 | 2.81 | 71 | 5.72 | 0.239 |
| lage_2 | 3.685 | 6.53 | 144 | 4.25 | 0.118 |

## Straßennamen je Lage

- **lage_1a**: Am Wollhaus; Deutschhofstraße; Fleiner Straße; Kiliansplatz; Kilianstraße
- **lage_1b**: Allee; Am Wollhaus; Berliner Platz; Götzenturmstraße; Kaiserstraße; Karlstraße; Kilianstraße; Klarastraße; Sülmerstraße; Turmstraße
- **lage_2**: Allee; Am Kieselmarkt; Biedermanngasse; Deutschhofstraße; Eichgasse; Falkenstraße; Fischergasse; Gemmingergasse; Gerberstraße; Glockengießerhof; Große Bahngasse; Gustav-Binder-Straße; Hämmerlinggasse; Jakobgasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Kramstraße; Lammgasse; Lohtorstraße; Marktplatz; Obere Neckarstraße; Rathausgasse; Schellengasse; Sonnengasse; Sülmerstraße; Titotstraße; Untere Neckarstraße; Windgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct | alt_min_density | alt_min_brand_share |
|---|---|---|---|---|---|---|
| lage_1a | 4.34 | 0.462 | 0.2 | – | – | – |
| lage_1b | 1.86 | – | – | 0.9 | 3.72 | 0.173 |
| lage_2 | 2.48 | – | – | – | – | – |

## Übereinstimmung mit der Referenz (Expertenabgrenzung, Segmentlänge)

Referenz: `reference/heilbronn_lagen.geojson`; km-Ziele für 1a/1b = Referenzlänge ± 25%.

| lage | precision | recall | f1 |
|---|---|---|---|
| lage_1a | 0.912 | 0.997 | 0.952 |
| lage_1b | 0.276 | 0.69 | 0.394 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.051 | 4 | 0.5 | lage_2 | Kasernengasse |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 9.58 > 5.72 > 4.25 je 100 m | True |
| OK | lage_1a: Länge 0.39–0.65 km | 0.566 km | False |
| WARNUNG | lage_1b: Länge 0.44–0.73 km | 1.465 km → lage_1b.min_density (1.86) erhöhen | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.685 km | False |
| OK | lage_1a: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.952, Precision 0.912, Recall 0.997 | False |
| WARNUNG | lage_1b: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.394, Precision 0.276, Recall 0.69 | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 335 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
