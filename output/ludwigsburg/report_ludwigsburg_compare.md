# Lagevergleich Ludwigsburg, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:05:39+00:00, params_hash `544c974c7e`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Ludwigsburg, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 0.19 | 1.381 | 1.43 | 2.71 | 48 | 123 | 0.5 | 0.407 |
| lage_1b | 1.0–2.0 | 2.0 | 0.589 | 9.82 | 1.21 | 154 | 43 | 0.266 | 0.07 |
| lage_2 | 2.0–4.0 | 2.5 | 1.643 | 9.08 | 2.94 | 74 | 94 | 0.041 | 0.16 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.381 | 2.71 | 123 | 11.63 | 0.407 |
| lage_1b | 0.589 | 1.21 | 43 | 7.68 | 0.07 |
| lage_2 | 1.643 | 2.94 | 94 | 6.41 | 0.16 |

## Straßennamen je Lage

- **lage_1a**: Bahnhofstraße; Kirchstraße; Kronenstraße; Körnerstraße; Myliusstraße; Seestraße; Wilhelmstraße
- **lage_1b**: Arsenalstraße; Bietigheimer Straße; Seestraße; Wilhelmstraße
- **lage_2**: Asperger Straße; Bahnhofstraße; Eberhardstraße; Hermannstraße; Holzmarkt; Holzmarktstraße; Kaffeeberg; Körnerstraße; Myliusstraße; Obere Marktstraße; Reithausberg; Reithausplatz; Schillerstraße; Untere Marktstraße

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 6.54 | 0.206 | 0.2 | – |
| lage_1b | 2.8 | – | – | 0.9 |
| lage_2 | 3.74 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.139 | 12 | 0.417 | lage_2 | Hermannstraße; Reithausberg |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 11.63 / 1b 7.68 / 2 6.41 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 11.63 / 1b 7.68 / 2 6.41 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 1.381 km → lage_1a.min_density (6.54) erhöhen | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.589 km → lage_1b.min_density (2.8) senken | False |
| WARNUNG | lage_2: Länge 2.0–4.0 km | 1.643 km → lage_2.min_density (3.74) senken | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
