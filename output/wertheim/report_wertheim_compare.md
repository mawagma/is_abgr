# Lagevergleich Wertheim, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:04:39+00:00, params_hash `5f12424a4d`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Wertheim, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 0.87 | 0.539 | 2.22 | 0.97 | 47 | 33 | 0.043 | 0.182 |
| lage_1b | 1.0–2.0 | 0.78 | 0.32 | 2.21 | 0.59 | 25 | 8 | 0.0 | 0.0 |
| lage_2 | 2.0–4.0 | 1.36 | 0.809 | 3.21 | 1.05 | 9 | 35 | 0.0 | 0.0 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.539 | 0.97 | 33 | 6.95 | 0.182 |
| lage_1b | 0.32 | 0.59 | 8 | 2.5 | 0.0 |
| lage_2 | 0.809 | 1.05 | 35 | 4.33 | 0.0 |

## Straßennamen je Lage

- **lage_1a**: Bahnhofstraße; Brückengasse; Eichelgasse; Maingasse; Marktplatz; Weingärtnerstraße
- **lage_1b**: Eichelgasse; Rechte Tauberstraße; Tauberbrücke
- **lage_2**: Friedleinsgasse; Haspelgäßchen; Lindenstraße; Marktplatz; Mühlenstraße; Münzgasse; Nebenmaingasse; Nebenneugasse; Rathausgasse; Tauber-Promenade; Weingärtnerstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 3.02 | 0.035 | 0.2 | – |
| lage_1b | 1.3 | – | – | 0.9 |
| lage_2 | 1.73 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 6.95 / 1b 2.5 / 2 4.33 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 6.95 / 1b 2.5 / 2 4.33 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 0.539 km → lage_1a.min_density (3.02) senken oder lage_1a.min_brand_share (0.035) senken | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.32 km → lage_1b.min_density (1.3) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 0.809 km → lage_2.min_density (1.73) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
