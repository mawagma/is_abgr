# Lagevergleich Waiblingen, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T16:57:33+00:00, params_hash `0b1bdcccf0`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Waiblingen, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.61 | 1.214 | 4.12 | 2.28 | 97 | 75 | 0.196 | 0.307 |
| lage_1b | 1.0–2.0 | 1.57 | 1.314 | 5.69 | 2.86 | 65 | 53 | 0.154 | 0.057 |
| lage_2 | 2.0–4.0 | 1.89 | 1.188 | 8.94 | 1.88 | 43 | 62 | 0.116 | 0.113 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.214 | 2.28 | 75 | 7.6 | 0.307 |
| lage_1b | 1.314 | 2.86 | 53 | 4.2 | 0.057 |
| lage_2 | 1.188 | 1.88 | 62 | 5.66 | 0.113 |

## Straßennamen je Lage

- **lage_1a**: Albert-Roller-Straße; Alter Postplatz; Am Stadtgraben; Bahnhofstraße; Bürgermühlenweg; Fronackerstraße; Kurze Straße; Lange Straße; Postplatz
- **lage_1b**: Alter Postplatz; Am Stadtgraben; Blumenstraße; Fronackerstraße; Hadergasse; Lange Straße; Ludwigsburger Straße; Schmidener Straße; Winnender Straße
- **lage_2**: Bahnhofstraße; Beim Hochwachtturm; Bürgermühlenweg; Heinrich-Küderli-Straße; Kurze Straße; Marktgasse; Marktplatz; Obere Sackgasse; Untere Lindenstraße; Untere Sackgasse; Zehnthof; Zwerchgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 4.19 | 0.119 | 0.2 | – |
| lage_1b | 1.8 | – | – | 0.9 |
| lage_2 | 2.39 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.034 | 5 | 0.2 | keine | Marktgasse |
| 2 | 0.057 | 5 | 0.2 | lage_2 | Marktgasse |
| 3 | 0.049 | 7 | 0.286 | lage_2 | Marktgasse |
| 4 | 0.15 | 10 | 0.3 | lage_2 | Bahnhofstraße |
| 5 | 0.079 | 0 | 0.0 | lage_1b | Lange Straße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 7.6 / 1b 4.2 / 2 5.66 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 7.6 / 1b 4.2 / 2 5.66 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 1.214 km → lage_1a.min_density (4.19) erhöhen | False |
| OK | lage_1b: Länge 1.0–2.0 km | 1.314 km | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 1.188 km → lage_2.min_density (2.39) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
