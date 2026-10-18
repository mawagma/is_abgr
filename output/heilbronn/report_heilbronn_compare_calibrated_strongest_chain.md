# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-18T21:26:21Z, Lauf 2026-10-18T21:46:59+00:00, params_hash `abd2cc82ea`.  
Street-Modus: auto_calibrate = **True**, seed = **strongest_chain**. Overrides: street.auto_calibrate=True, street.seed='strongest_chain'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Gleiche Zählweise für beide Modi: Straßenlänge = Länge der Straßensegmente im Polygon, POIs = Erdgeschoss-POIs im Polygon, Filialanteil = Anteil Filialisten (brand/brand:wikidata) an diesen POIs.

| Lage | Ziel km | Raster km | Street km | Ziel ha | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.38 | 1.06 | 3–6 | 5.94 | 2.91 | 126 | 57 | 0.429 | 0.491 |
| lage_1b | 1.0–2.0 | 2.55 | 3.3 | 5–10 | 9.94 | 9.52 | 138 | 151 | 0.188 | 0.152 |
| lage_2 | 2.0–4.0 | 5.95 | 3.18 | 10–20 | 19.98 | 9.21 | 116 | 67 | 0.112 | 0.164 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.899 | 2.91 | 57 | 8.84 | 0.526 |
| lage_1b | 2.8 | 9.52 | 158 | 6.31 | 0.158 |
| lage_2 | 3.024 | 9.21 | 84 | 3.3 | 0.25 |

## Straßennamen je Lage

- **lage_1a**: Am Wollhaus; Deutschhofstraße; Fleiner Straße; Götzenturmstraße; Kiliansplatz; Kilianstraße; Klarastraße
- **lage_1b**: Allee; Am Kieselmarkt; Berliner Platz; Deutschhofstraße; Eichgasse; Falkenstraße; Fischergasse; Gerberstraße; Gustav-Binder-Straße; Hämmerlinggasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Kramstraße; Lohtorstraße; Marktplatz; Rathausgasse; Sonnengasse; Sülmerstraße; Turmstraße; Windgasse
- **lage_2**: Allee; Allerheiligenstraße; Biedermanngasse; Fischergasse; Gemmingergasse; Gerberstraße; Große Bahngasse; Jakobgasse; Kaiserstraße; Karlstraße; Lammgasse; Lohtorstraße; Marktplatz; Metzgergasse; Obere Neckarstraße; Schellengasse; Schwibbogengasse; Schöntaler Gasse; Siebeneichgasse; Titotstraße; Untere Neckarstraße; Wolfganggasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 3.61 | 0.4 |
| lage_1b | 3.6 | – |
| lage_2 | 1.91 | – |

Automatisch kalibriert (Bisektion auf die Mitte von target_ranges_km; Schwellen bleiben absteigend, die Obergrenze je Lage ist die Schwelle der Lage darüber):

| lage | ziel_km | schwelle | start | erreicht_km |
|---|---|---|---|---|
| lage_1a | 0.8999999999999999 | 3.61 | 8 | 0.899 |
| lage_1b | 1.5 | 3.6 | 5 | 2.8 |
| lage_2 | 3.0 | 1.91 | 2 | 3.024 |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.162 | 4 | 0.75 | keine | Weinsberger Straße |
| 2 | 0.05 | 4 | 0.25 | lage_1b | Kaiserstraße |
| 3 | 0.002 | 5 | 0.6 | keine | Deutschhofstraße |
| 4 | 0.249 | 12 | 0.75 | lage_2 | Fischergasse; Metzgergasse |
| 5 | 0.054 | 2 | 0.5 | keine | Sülmermühlstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 8.84 > 6.31 > 3.3 je 100 m | True |
| OK | lage_1a: Länge 0.6–1.2 km | 0.899 km | False |
| WARNUNG | lage_1a: Fläche 3–6 ha | 2.91 ha → buffer_m (20) vergrößern | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 2.8 km → lage_1b.min_density (3.6) erhöhen | False |
| OK | lage_1b: Fläche 5–10 ha | 9.52 ha | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.024 km | False |
| WARNUNG | lage_2: Fläche 10–20 ha | 9.21 ha → buffer_m (20) vergrößern | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 335 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Sülmerstraße“ | 0 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Kaiserstraße“ | 0 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
