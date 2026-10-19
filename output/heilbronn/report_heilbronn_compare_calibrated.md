# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T06:41:06Z, Lauf 2026-10-19T07:15:45+00:00, params_hash `b5738decde`.  
Street-Modus: auto_calibrate = **True**, seed = **strongest_chain**. Overrides: street.auto_calibrate=True. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.39–0.65 | 1.07 | 0.566 | 3.69 | 0.97 | 74 | 37 | 0.351 | 0.622 |
| lage_1b | 0.44–0.73 | 2.6 | 2.571 | 9.93 | 4.62 | 142 | 152 | 0.19 | 0.158 |
| lage_2 | 2.0–4.0 | 6.08 | 2.923 | 20.73 | 5.46 | 102 | 68 | 0.137 | 0.162 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.566 | 0.97 | 37 | 9.58 | 0.622 |
| lage_1b | 2.571 | 4.62 | 152 | 6.61 | 0.158 |
| lage_2 | 2.923 | 5.46 | 68 | 2.61 | 0.162 |

## Straßennamen je Lage

- **lage_1a**: Am Wollhaus; Deutschhofstraße; Fleiner Straße; Kiliansplatz; Kilianstraße
- **lage_1b**: Allee; Am Kieselmarkt; Am Wollhaus; Berliner Platz; Deutschhofstraße; Eichgasse; Falkenstraße; Fischergasse; Gustav-Binder-Straße; Götzenturmstraße; Hämmerlinggasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Klarastraße; Kramstraße; Lohtorstraße; Marktplatz; Sonnengasse; Sülmerstraße; Turmstraße
- **lage_2**: Allee; Berliner Platz; Biedermanngasse; Gemmingergasse; Gerberstraße; Große Bahngasse; Jakobgasse; Kaiserstraße; Karlstraße; Lammgasse; Lohtorstraße; Obere Neckarstraße; Rathausgasse; Schellengasse; Schwibbogengasse; Schöntaler Gasse; Titotstraße; Untere Neckarstraße; Windgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 4.2 | 0.4 |
| lage_1b | 3.76 | – |
| lage_2 | 2.03 | – |

## Übereinstimmung mit der Referenz (Expertenabgrenzung, Segmentlänge)

Referenz: `reference/heilbronn_lagen.geojson`; km-Ziele für 1a/1b = Referenzlänge ± 25%.

| lage | precision | recall | f1 |
|---|---|---|---|
| lage_1a | 0.912 | 0.997 | 0.952 |
| lage_1b | 0.147 | 0.645 | 0.239 |

Automatisch kalibriert (Bisektion auf die Mitte von target_ranges_km; Schwellen bleiben absteigend, die Obergrenze je Lage ist die Schwelle der Lage darüber):

| lage | verfahren | start | schwelle | precision | recall | f1 | ziel_km | erreicht_km |
|---|---|---|---|---|---|---|---|---|
| lage_1a | Referenz (max. F1) | 8 | 4.2 | 0.912 | 0.997 | 0.952 | nan | nan |
| lage_1b | Referenz (max. F1) | 5 | 3.76 | 0.147 | 0.645 | 0.239 | nan | nan |
| lage_2 | Bisektion auf Ziel-km | 2 | 2.03 | nan | nan | nan | 3.0 | 2.923 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.051 | 4 | 0.5 | lage_1b | Kasernengasse |
| 2 | 0.054 | 2 | 0.5 | keine | Sülmermühlstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 9.58 > 6.61 > 2.61 je 100 m | True |
| OK | lage_1a: Länge 0.39–0.65 km | 0.566 km | False |
| WARNUNG | lage_1b: Länge 0.44–0.73 km | 2.571 km → lage_1b.min_density (3.76) erhöhen | False |
| OK | lage_2: Länge 2.0–4.0 km | 2.923 km | False |
| OK | lage_1a: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.952, Precision 0.912, Recall 0.997 | False |
| WARNUNG | lage_1b: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.239, Precision 0.147, Recall 0.645 | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 335 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
