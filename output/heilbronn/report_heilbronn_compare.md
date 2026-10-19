# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T20:03:19+00:00, params_hash `deb9e50840`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: keine. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.39–0.65 | 1.45 | 0.4 | 5.94 | 1.3 | 128 | 33 | 0.266 | 0.606 |
| lage_1b | 0.44–0.73 | 2.84 | 0.553 | 9.93 | 2.2 | 104 | 31 | 0.231 | 0.258 |
| lage_2 | 2.0–4.0 | 5.53 | 4.112 | 20.37 | 5.34 | 99 | 177 | 0.101 | 0.153 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.4 | 1.3 | 33 | 14.18 | 0.606 |
| lage_1b | 0.553 | 2.2 | 31 | 6.9 | 0.258 |
| lage_2 | 4.112 | 5.34 | 177 | 4.86 | 0.153 |

## Straßennamen je Lage

- **lage_1a**: Deutschhofstraße; Fleiner Straße; Kiliansplatz
- **lage_1b**: Kaiserstraße; Sülmerstraße
- **lage_2**: Allee; Am Kieselmarkt; Am Wollhaus; Berliner Platz; Deutschhofstraße; Eichgasse; Falkenstraße; Fischergasse; Gemmingergasse; Gerberstraße; Glockengießerhof; Große Bahngasse; Gustav-Binder-Straße; Götzenturmstraße; Hämmerlinggasse; Jakobgasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Klarastraße; Kramstraße; Lohtorstraße; Marktplatz; Obere Neckarstraße; Rathausgasse; Schellengasse; Sonnengasse; Sülmerstraße; Titotstraße; Turmstraße; Untere Neckarstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 5.42 | 0.352 | 0.2 | – |
| lage_1b | 2.03 | – | – | 0.9 |
| lage_2 | 2.71 | – | – | – |

## Übereinstimmung mit der Referenz (Expertenabgrenzung, Segmentlänge)

Referenz: `reference/heilbronn_lagen.geojson`; km-Ziele für 1a/1b = Referenzlänge ± 25%.

| lage | precision | recall | f1 |
|---|---|---|---|
| lage_1a | 1.0 | 0.773 | 0.872 |
| lage_1b | 0.731 | 0.69 | 0.71 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 14.18 / 1b 6.9 / 2 4.86 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 14.18 / 1b 6.9 / 2 4.86 je 100 m | False |
| OK | lage_1a: Länge 0.39–0.65 km | 0.4 km | False |
| OK | lage_1b: Länge 0.44–0.73 km | 0.553 km | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 4.112 km → lage_2.min_density (2.71) erhöhen | False |
| OK | lage_1a: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.872, Precision 1.0, Recall 0.773 | False |
| WARNUNG | lage_1b: Übereinstimmung mit Referenz (F1 ≥ 0.8) | F1 0.71, Precision 0.731, Recall 0.69 | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 335 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
