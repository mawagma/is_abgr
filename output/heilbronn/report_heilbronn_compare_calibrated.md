# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-18T21:26:21Z, Lauf 2026-10-18T21:44:47+00:00, params_hash `a42a4b59a6`.  
Street-Modus: auto_calibrate = **True**, seed = **max_density**. Overrides: street.auto_calibrate=True. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Gleiche Zählweise für beide Modi: Straßenlänge = Länge der Straßensegmente im Polygon, POIs = Erdgeschoss-POIs im Polygon, Filialanteil = Anteil Filialisten (brand/brand:wikidata) an diesen POIs.

| Lage | Ziel km | Raster km | Street km | Ziel ha | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.38 | 0.49 | 3–6 | 5.94 | 1.18 | 126 | 8 | 0.429 | 0.625 |
| lage_1b | 1.0–2.0 | 2.55 | 9.11 | 5–10 | 9.94 | 25.67 | 138 | 287 | 0.188 | 0.209 |
| lage_2 | 2.0–4.0 | 5.95 | 4.41 | 10–20 | 19.98 | 12.9 | 116 | 49 | 0.112 | 0.061 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.426 | 1.18 | 15 | 5.46 | 0.733 |
| lage_1b | 8.136 | 25.67 | 310 | 4.44 | 0.219 |
| lage_2 | 3.791 | 12.9 | 63 | 1.82 | 0.127 |

## Straßennamen je Lage

- **lage_1a**: Allerheiligenstraße; Fischergasse; Metzgergasse
- **lage_1b**: Allee; Am Kieselmarkt; Am Wollhaus; Berliner Platz; Biedermanngasse; Deutschhofstraße; Eichgasse; Endgasse; Falkenstraße; Fischergasse; Fleiner Straße; Gemmingergasse; Gerberstraße; Glockengießerhof; Große Bahngasse; Gustav-Binder-Straße; Götzenturmstraße; Hämmerlinggasse; Jakobgasse; Kaiserstraße; Karlstraße; Kasernengasse; Kiliansplatz; Kilianstraße; Kirchbrunnenstraße; Klarastraße; Kramstraße; Lammgasse; Lohtorstraße; Marktplatz; Moltkestraße; Obere Neckarstraße; Platz am Bollwerksturm; Rathausgasse; Schellengasse; Schwibbogengasse; Schäfergasse; Schöntaler Gasse; Siebeneichgasse; Sonnengasse; Sülmermühlstraße; Sülmerstraße; Titotstraße; Turmstraße; Untere Neckarstraße; Windgasse; Wolfganggasse; Zehentgasse
- **lage_2**: Allee; Am Wollhaus; Bahnhofstraße; Gymnasiumstraße; Herbststraße; Innsbrucker Straße; Kaiserstraße; Karlstraße; Kurt-Schumacher-Platz; Moltkestraße; Mönchseestraße; Obere Neckarstraße; Siebeneichgasse; Südstraße; Urbanstraße; Werderstraße; Wilhelmstraße; Wollhausstraße; Zehentgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 1.2 | 0.4 |
| lage_1b | 1.2 | – |
| lage_2 | 0.92 | – |

Automatisch kalibriert (Bisektion auf die Mitte von target_ranges_km; Schwellen bleiben absteigend, die Obergrenze je Lage ist die Schwelle der Lage darüber):

| lage | ziel_km | schwelle | start | erreicht_km |
|---|---|---|---|---|
| lage_1a | 0.8999999999999999 | 1.2 | 8 | 0.426 |
| lage_1b | 1.5 | 1.2 | 5 | 8.136 |
| lage_2 | 3.0 | 0.92 | 2 | 3.791 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 1.064 | 59 | 0.525 | lage_1b | Am Wollhaus; Biedermanngasse; Deutschhofstraße; Fleiner Straße; Götzenturmstraße; Kiliansplatz; Kilianstraße; Klarastraße; Siebeneichgasse |
| 2 | 0.05 | 0 | 0.0 | keine | Neckarsulmer Straße |
| 3 | 0.217 | 3 | 0.667 | keine | August-Häußer-Straße |
| 4 | 0.104 | 3 | 0.667 | lage_1b | Sülmermühlstraße |
| 5 | 0.248 | 4 | 0.75 | keine | Mannheimer Straße; Weinsberger Straße |
| 6 | 0.05 | 1 | 1.0 | lage_1b | Moltkestraße |
| 7 | 0.1 | 2 | 0.5 | keine | Hans-Seyfer-Straße |
| 8 | 0.057 | 1 | 1.0 | keine | Alfred-Finkbeiner-Straße |
| 9 | 0.05 | 1 | 1.0 | keine | Schmollerstraße |
| 10 | 0.167 | 3 | 0.667 | lage_1b | Titotstraße |
| 11 | 0.185 | 5 | 0.6 | lage_1b | Obere Neckarstraße; Untere Neckarstraße |
| 12 | 0.05 | 4 | 0.25 | lage_1b | Kaiserstraße |
| 13 | 0.02 | 0 | 0.0 | lage_1b | Kaiserstraße |
| 14 | 0.15 | 2 | 0.5 | keine | Fügerstraße |
| 15 | 0.05 | 0 | 0.0 | keine | Stuttgarter Straße |
| 16 | 0.05 | 0 | 0.0 | keine | Rosenbergstraße |
| 17 | 0.1 | 2 | 0.5 | lage_1b | Lammgasse |
| 18 | 0.187 | 2 | 0.5 | keine | Neckargartacher Straße |
| 19 | 0.002 | 5 | 0.6 | keine | Deutschhofstraße |
| 20 | 0.15 | 3 | 0.333 | lage_2 | Südstraße |
| 21 | 0.05 | 0 | 0.0 | keine | Neckarsulmer Straße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 5.46 > 4.44 > 1.82 je 100 m | True |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.426 km → lage_1a.min_density (1.2) senken oder lage_1a.min_brand_share (0.4) senken | False |
| WARNUNG | lage_1a: Fläche 3–6 ha | 1.18 ha → folgt der Länge (siehe oben) | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 8.136 km → lage_1b.min_density (1.2) erhöhen | False |
| WARNUNG | lage_1b: Fläche 5–10 ha | 25.67 ha → folgt der Länge (siehe oben) | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.791 km | False |
| OK | lage_2: Fläche 10–20 ha | 12.9 ha | False |
| WARNUNG | Plausibilität: 1a enthält „Fleiner Straße“ | 0 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Sülmerstraße“ | 0 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Kaiserstraße“ | 0 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
