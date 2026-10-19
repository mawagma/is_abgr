# Lagevergleich Essen, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T18:11:13+00:00, params_hash `5e451f1c7a`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Essen, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 0.03 | 0.676 | 1.34 | 1.29 | 37 | 73 | 0.703 | 0.452 |
| lage_1b | 1.0–2.0 | 1.66 | 0.862 | 4.43 | 1.98 | 78 | 26 | 0.41 | 0.385 |
| lage_2 | 2.0–4.0 | 5.8 | 1.037 | 20.36 | 1.27 | 182 | 37 | 0.302 | 0.324 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.676 | 1.29 | 73 | 14.46 | 0.452 |
| lage_1b | 0.862 | 1.98 | 26 | 3.88 | 0.385 |
| lage_2 | 1.037 | 1.27 | 37 | 4.44 | 0.324 |

## Straßennamen je Lage

- **lage_1a**: Kettwiger Straße; Kornmarkt; Limbecker Straße
- **lage_1b**: I. Dellbrügge; Kastanienallee; Kennedyplatz; Kettwiger Straße; Limbecker Platz; Theaterplatz; Willy-Brandt-Platz
- **lage_2**: Am Glockenspiel; An St. Quintin; Flachsmarkt; Friedensplatz; Friedrich-Ebert-Straße; Kapuzinergasse; Kettwiger Straße; Limbecker Platz; Limbecker Straße; Porschekanzel; Porscheplatz; Rathenaustraße; Salzmarkt; Schwarze Horn

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 6.56 | 0.186 | 0.2 | – |
| lage_1b | 2.81 | – | – | 0.9 |
| lage_2 | 3.75 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.036 | 3 | 0.333 | lage_2 | Salzmarkt |
| 2 | 0.085 | 5 | 0.6 | keine | Feilenstraße |
| 3 | 0.007 | 3 | 0.667 | keine | Am Hauptbahnhof |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 14.46 / 1b 3.88 / 2 4.44 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 14.46 / 1b 3.88 / 2 4.44 je 100 m | False |
| OK | lage_1a: Länge 0.6–1.2 km | 0.676 km | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.862 km → lage_1b.min_density (2.81) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 1.037 km → lage_2.min_density (3.75) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
