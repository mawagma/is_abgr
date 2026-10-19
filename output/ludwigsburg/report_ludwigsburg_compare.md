# Lagevergleich Ludwigsburg, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T20:04:23+00:00, params_hash `7218b1279e`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Ludwigsburg, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 0.12 | 1.804 | 1.44 | 5.51 | 43 | 149 | 0.558 | 0.389 |
| lage_1b | 1.0–2.0 | 1.85 | 0.839 | 8.59 | 1.35 | 148 | 54 | 0.264 | 0.111 |
| lage_2 | 2.0–4.0 | 2.69 | 1.069 | 9.89 | 1.25 | 81 | 60 | 0.049 | 0.067 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.804 | 5.51 | 149 | 11.45 | 0.389 |
| lage_1b | 0.839 | 1.35 | 54 | 7.13 | 0.111 |
| lage_2 | 1.069 | 1.25 | 60 | 6.08 | 0.067 |

## Straßennamen je Lage

- **lage_1a**: Bahnhofstraße; Hermannstraße; Kirchstraße; Kronenstraße; Körnerstraße; Myliusstraße; Reithausberg; Reithausplatz; Seestraße; Wilhelmstraße
- **lage_1b**: Arsenalstraße; Bietigheimer Straße; Schillerstraße; Seestraße; Wilhelmstraße
- **lage_2**: Asperger Straße; Bahnhofstraße; Eberhardstraße; Holzmarkt; Holzmarktstraße; Kaffeeberg; Obere Marktstraße; Untere Marktstraße; Wilhelmstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 7.19 | 0.154 | 0.2 | – |
| lage_1b | 2.7 | – | – | 0.9 |
| lage_2 | 3.6 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

keine

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 11.45 / 1b 7.13 / 2 6.08 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 11.45 / 1b 7.13 / 2 6.08 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 1.804 km → lage_1a.min_density (7.19) erhöhen | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.839 km → lage_1b.min_density (2.7) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 1.069 km → lage_2.min_density (3.6) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
