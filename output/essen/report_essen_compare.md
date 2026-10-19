# Lagevergleich Essen, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:54:19+00:00, params_hash `9ae0b972b4`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Essen, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 0.03 | 0.723 | 1.34 | 3.92 | 37 | 75 | 0.703 | 0.493 |
| lage_1b | 1.0–2.0 | 1.79 | 0.458 | 5.36 | 0.9 | 85 | 9 | 0.412 | 0.444 |
| lage_2 | 2.0–4.0 | 5.79 | 0.962 | 20.52 | 0.93 | 174 | 40 | 0.293 | 0.275 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 0.723 | 3.92 | 75 | 14.94 | 0.493 |
| lage_1b | 0.458 | 0.9 | 9 | 2.62 | 0.444 |
| lage_2 | 0.962 | 0.93 | 40 | 6.23 | 0.275 |

## Straßennamen je Lage

- **lage_1a**: Kettwiger Straße; Limbecker Straße; Porschekanzel; Porscheplatz
- **lage_1b**: I. Dellbrügge; Kettwiger Straße; Limbecker Platz; Theaterplatz
- **lage_2**: Am Glockenspiel; An St. Quintin; Flachsmarkt; Friedensplatz; Friedrich-Ebert-Straße; Kornmarkt; Limbecker Platz; Limbecker Straße; Rathenaustraße; Schwarze Horn

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 6.91 | 0.215 | 0.2 | – |
| lage_1b | 2.96 | – | – | 0.9 |
| lage_2 | 3.95 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.036 | 3 | 0.333 | keine | Salzmarkt |
| 2 | 0.085 | 5 | 0.6 | keine | Feilenstraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 14.94 / 1b 2.62 / 2 6.23 je 100 m | True |
| WARNUNG | Dichte 1b > 2 | 1a 14.94 / 1b 2.62 / 2 6.23 je 100 m | False |
| OK | lage_1a: Länge 0.6–1.2 km | 0.723 km | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.458 km → lage_1b.min_density (2.96) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 0.962 km → lage_2.min_density (3.95) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
