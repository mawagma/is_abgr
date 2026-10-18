# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-18T21:26:21Z, Lauf 2026-10-18T21:43:36+00:00, params_hash `94f0bedfd2`.  
Street-Modus: auto_calibrate = **False**, seed = **max_density**. Overrides: keine. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Gleiche Zählweise für beide Modi: Straßenlänge = Länge der Straßensegmente im Polygon, POIs = Erdgeschoss-POIs im Polygon, Filialanteil = Anteil Filialisten (brand/brand:wikidata) an diesen POIs.

| Lage | Ziel km | Raster km | Street km | Ziel ha | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.38 | 0.08 | 3–6 | 5.94 | 0.24 | 126 | 2 | 0.429 | 1.0 |
| lage_1b | 1.0–2.0 | 2.55 | 0.0 | 5–10 | 9.94 | 0.0 | 138 | 0 | 0.188 | 0.0 |
| lage_2 | 2.0–4.0 | 5.95 | 7.33 | 10–20 | 19.98 | 20.94 | 116 | 268 | 0.112 | 0.224 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.06 | 0.24 | 7 | 19.24 | 0.857 |
| lage_1b | 0.0 | 0.0 | 0 | 0.0 | 0.0 |
| lage_2 | 6.57 | 20.94 | 287 | 5.17 | 0.244 |

## Straßennamen je Lage

- **lage_1a**: Metzgergasse
- **lage_1b**: –
- **lage_2**: Allee; Allerheiligenstraße; Am Kieselmarkt; Am Wollhaus; Berliner Platz; Biedermanngasse; Deutschhofstraße; Eichgasse; Falkenstraße; Fischergasse; Fleiner Straße; Gemmingergasse; Gerberstraße; Große Bahngasse; Gustav-Binder-Straße; Götzenturmstraße; Hämmerlinggasse; Jakobgasse; Kaiserstraße; Karlstraße; Kasernengasse; Kiliansplatz; Kilianstraße; Kirchbrunnenstraße; Klarastraße; Kramstraße; Lammgasse; Lohtorstraße; Marktplatz; Obere Neckarstraße; Rathausgasse; Schellengasse; Schwibbogengasse; Schöntaler Gasse; Siebeneichgasse; Sonnengasse; Sülmerstraße; Titotstraße; Turmstraße; Untere Neckarstraße; Windgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 8 | 0.4 |
| lage_1b | 5 | – |
| lage_2 | 2 | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.516 | 41 | 0.634 | lage_2 | Am Wollhaus; Deutschhofstraße; Fleiner Straße; Kiliansplatz |
| 2 | 0.002 | 5 | 0.6 | keine | Deutschhofstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| FEHLER | Genau 3 Lagen, gültig, nicht leer | leer: ['lage_1b'] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| FEHLER | Dichte 1a > 1b > 2 | 19.24 > 0.0 > 5.17 je 100 m | True |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.06 km → lage_1a.min_density (8) senken oder lage_1a.min_brand_share (0.4) senken | False |
| WARNUNG | lage_1a: Fläche 3–6 ha | 0.24 ha → folgt der Länge (siehe oben) | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.0 km → lage_1b.min_density (5) senken | False |
| WARNUNG | lage_1b: Fläche 5–10 ha | 0.0 ha → folgt der Länge (siehe oben) | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 6.57 km → lage_2.min_density (2) erhöhen | False |
| WARNUNG | lage_2: Fläche 10–20 ha | 20.94 ha → folgt der Länge (siehe oben) | False |
| WARNUNG | Plausibilität: 1a enthält „Fleiner Straße“ | 0 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Sülmerstraße“ | 0 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Kaiserstraße“ | 0 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
