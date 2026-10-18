# Lagevergleich Heilbronn, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-18T21:26:21Z, Lauf 2026-10-18T21:45:53+00:00, params_hash `f66ede8c4b`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: street.seed='strongest_chain'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Gleiche Zählweise für beide Modi: Straßenlänge = Länge der Straßensegmente im Polygon, POIs = Erdgeschoss-POIs im Polygon, Filialanteil = Anteil Filialisten (brand/brand:wikidata) an diesen POIs.

| Lage | Ziel km | Raster km | Street km | Ziel ha | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.38 | 0.69 | 3–6 | 5.94 | 1.73 | 126 | 44 | 0.429 | 0.568 |
| lage_1b | 1.0–2.0 | 2.55 | 2.51 | 5–10 | 9.94 | 7.39 | 138 | 137 | 0.188 | 0.153 |
| lage_2 | 2.0–4.0 | 5.95 | 4.24 | 10–20 | 19.98 | 12.19 | 116 | 89 | 0.112 | 0.18 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.516 | 1.73 | 41 | 11.72 | 0.634 |
| lage_1b | 2.21 | 7.39 | 138 | 7.06 | 0.174 |
| lage_2 | 3.904 | 12.19 | 114 | 3.42 | 0.228 |

## Straßennamen je Lage

- **lage_1a**: Am Wollhaus; Deutschhofstraße; Fleiner Straße; Kiliansplatz
- **lage_1b**: Am Kieselmarkt; Am Wollhaus; Berliner Platz; Deutschhofstraße; Eichgasse; Falkenstraße; Gerberstraße; Gustav-Binder-Straße; Hämmerlinggasse; Kaiserstraße; Karlstraße; Kasernengasse; Kilianstraße; Kirchbrunnenstraße; Kramstraße; Lohtorstraße; Sonnengasse; Sülmerstraße; Turmstraße
- **lage_2**: Allee; Allerheiligenstraße; Biedermanngasse; Fischergasse; Gemmingergasse; Gerberstraße; Große Bahngasse; Götzenturmstraße; Jakobgasse; Kaiserstraße; Karlstraße; Kilianstraße; Klarastraße; Lammgasse; Lohtorstraße; Marktplatz; Metzgergasse; Obere Neckarstraße; Rathausgasse; Schellengasse; Schwibbogengasse; Schöntaler Gasse; Siebeneichgasse; Titotstraße; Untere Neckarstraße; Windgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share |
|---|---|---|
| lage_1a | 8 | 0.4 |
| lage_1b | 5 | – |
| lage_2 | 2 | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.06 | 7 | 0.857 | lage_2 | Metzgergasse |
| 2 | 0.002 | 5 | 0.6 | keine | Deutschhofstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b > 2 | 11.72 > 7.06 > 3.42 je 100 m | True |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.516 km → lage_1a.min_density (8) senken oder lage_1a.min_brand_share (0.4) senken | False |
| WARNUNG | lage_1a: Fläche 3–6 ha | 1.73 ha → folgt der Länge (siehe oben) | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 2.21 km → lage_1b.min_density (5) erhöhen | False |
| OK | lage_1b: Fläche 5–10 ha | 7.39 ha | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.904 km | False |
| OK | lage_2: Fläche 10–20 ha | 12.19 ha | False |
| OK | Plausibilität: 1a enthält „Fleiner Straße“ | 335 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Sülmerstraße“ | 0 m in 1a | False |
| WARNUNG | Plausibilität: 1a enthält „Kaiserstraße“ | 0 m in 1a | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
