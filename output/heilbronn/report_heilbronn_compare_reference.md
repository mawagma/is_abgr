# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T06:41:06Z, Lauf 2026-10-19T07:13:12+00:00, params_hash `c0820c51db`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: street.lagen_from_reference=True. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.39–0.65 | 1.07 | 0.518 | 3.69 | 0.93 | 74 | 35 | 0.351 | 0.629 |
| lage_1b | 0.44–0.73 | 2.6 | 0.585 | 9.93 | 1.15 | 142 | 31 | 0.19 | 0.226 |
| lage_2 | 2.0–4.0 | 6.08 | 5.056 | 20.73 | 9.17 | 102 | 195 | 0.137 | 0.149 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.518 | 0.93 | 35 | 9.95 | 0.629 |
| lage_1b | 0.585 | 1.15 | 31 | 6.19 | 0.226 |
| lage_2 | 5.056 | 9.17 | 195 | 4.29 | 0.149 |

## Straßennamen je Lage

- **lage_1a**: Am Wollhaus; Deutschhofstraße; Fleiner Straße; Kiliansplatz
- **lage_1b**: Kaiserstraße; Sülmerstraße
- **lage_2**: Allee; Am Kieselmarkt; Am Wollhaus; Berliner Platz; Biedermanngasse; Deutschhofstraße; Eichgasse; Falkenstraße; Fischergasse; Gemmingergasse; Gerberstraße; Große Bahngasse; Gustav-Binder-Straße; Götzenturmstraße; Hämmerlinggasse; Jakobgasse; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Klarastraße; Kramstraße; Lammgasse; Lohtorstraße; Marktplatz; Obere Neckarstraße; Rathausgasse; Schellengasse; Schwibbogengasse; Schöntaler Gasse; Siebeneichgasse; Sonnengasse; Sülmerstraße; Titotstraße; Turmstraße; Untere Neckarstraße; Windgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 8 | 0.4 |
| lage_1b | 5 | – |
| lage_2 | 2 | – |

## Übereinstimmung mit der Referenz (Expertenabgrenzung, Segmentlänge)

Referenz: `reference/heilbronn_lagen.geojson`; km-Ziele für 1a/1b = Referenzlänge ± 25%.

| lage | precision | recall | f1 |
|---|---|---|---|
| lage_1a | 1.0 | 1.0 | 1.0 |
| lage_1b | 1.0 | 1.0 | 1.0 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 9.95 > 6.19 > 4.29 je 100 m | True |
| OK | lage_1a: Länge 0.39–0.65 km | 0.518 km | False |
| OK | lage_1b: Länge 0.44–0.73 km | 0.585 km | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 5.056 km → lage_2.min_density (2) erhöhen | False |
| OK | lage_1a: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 1.0, Precision 1.0, Recall 1.0 | False |
| OK | lage_1b: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 1.0, Precision 1.0, Recall 1.0 | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 335 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
