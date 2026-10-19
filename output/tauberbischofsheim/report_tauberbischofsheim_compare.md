# Lagevergleich Tauberbischofsheim, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T20:05:25+00:00, params_hash `102090776b`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Tauberbischofsheim, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 1.28 | 0.535 | 3.65 | 1.17 | 53 | 35 | 0.113 | 0.114 |
| lage_1b | 1.0–2.0 | 1.22 | 0.28 | 3.65 | 0.56 | 24 | 9 | 0.042 | 0.111 |
| lage_2 | 2.0–4.0 | 0.97 | 0.358 | 4.21 | 0.39 | 7 | 12 | 0.0 | 0.083 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.535 | 1.17 | 35 | 7.39 | 0.114 |
| lage_1b | 0.28 | 0.56 | 9 | 3.25 | 0.111 |
| lage_2 | 0.358 | 0.39 | 12 | 3.59 | 0.083 |

## Straßennamen je Lage

- **lage_1a**: Hauptstraße; Marktplatz
- **lage_1b**: Bahnhofstraße; Hauptstraße; Sonnenplatz
- **lage_2**: Eichstraße; Marktplatz; Martinsgasse; Museumstraße; Schloßweg; Schmiederstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 3.81 | 0.083 | 0.2 | – |
| lage_1b | 1.43 | – | – | 0.9 |
| lage_2 | 1.91 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 7.39 / 1b 3.25 / 2 3.59 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 7.39 / 1b 3.25 / 2 3.59 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.535 km → lage_1a.min_density (3.81) senken oder lage_1a.min_brand_share (0.083) senken | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.28 km → lage_1b.min_density (1.43) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 0.358 km → lage_2.min_density (1.91) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
