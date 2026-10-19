# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T06:41:06Z, Lauf 2026-10-19T07:08:43+00:00, params_hash `50aebe15af`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: keine. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.39–0.65 | 1.07 | 0.301 | 3.69 | 0.56 | 74 | 26 | 0.351 | 0.577 |
| lage_1b | 0.44–0.73 | 2.6 | 1.987 | 9.93 | 3.41 | 142 | 127 | 0.19 | 0.189 |
| lage_2 | 2.0–4.0 | 6.08 | 3.964 | 20.73 | 7.48 | 102 | 109 | 0.137 | 0.174 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.301 | 0.56 | 26 | 12.36 | 0.577 |
| lage_1b | 1.987 | 3.41 | 127 | 7.3 | 0.189 |
| lage_2 | 3.964 | 7.48 | 109 | 3.11 | 0.174 |

## Straßennamen je Lage

- **lage_1a**: Deutschhofstraße; Fleiner Straße; Kiliansplatz
- **lage_1b**: Am Kieselmarkt; Berliner Platz; Deutschhofstraße; Eichgasse; Falkenstraße; Fleiner Straße; Gustav-Binder-Straße; Hämmerlinggasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Lohtorstraße; Sonnengasse; Sülmerstraße; Turmstraße
- **lage_2**: Allee; Am Wollhaus; Biedermanngasse; Fischergasse; Gemmingergasse; Gerberstraße; Große Bahngasse; Götzenturmstraße; Jakobgasse; Kaiserstraße; Karlstraße; Kilianstraße; Klarastraße; Kramstraße; Lammgasse; Lohtorstraße; Marktplatz; Obere Neckarstraße; Rathausgasse; Schellengasse; Schwibbogengasse; Schöntaler Gasse; Siebeneichgasse; Titotstraße; Untere Neckarstraße; Windgasse

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
| lage_1a | 1.0 | 0.582 | 0.736 |
| lage_1b | 0.13 | 0.44 | 0.2 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 12.36 > 7.3 > 3.11 je 100 m | True |
| WARNUNG | lage_1a: Länge 0.39–0.65 km | 0.301 km → lage_1a.min_density (8) senken oder lage_1a.min_brand_share (0.4) senken | False |
| WARNUNG | lage_1b: Länge 0.44–0.73 km | 1.987 km → lage_1b.min_density (5) erhöhen | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.964 km | False |
| WARNUNG | lage_1a: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.736, Precision 1.0, Recall 0.582 | False |
| WARNUNG | lage_1b: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.2, Precision 0.13, Recall 0.44 | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 237 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
