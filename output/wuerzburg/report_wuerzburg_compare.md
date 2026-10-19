# Lagevergleich Würzburg, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T16:54:29+00:00, params_hash `b63d8e7809`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Würzburg, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 2.22 | 1.547 | 6.1 | 2.13 | 174 | 145 | 0.253 | 0.366 |
| lage_1b | 1.0–2.0 | 3.0 | 1.357 | 10.13 | 2.41 | 233 | 101 | 0.176 | 0.149 |
| lage_2 | 2.0–4.0 | 5.87 | 3.493 | 20.16 | 4.69 | 218 | 246 | 0.096 | 0.089 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.547 | 2.13 | 145 | 11.94 | 0.366 |
| lage_1b | 1.357 | 2.41 | 101 | 8.27 | 0.149 |
| lage_2 | 3.493 | 4.69 | 246 | 7.52 | 0.089 |

## Straßennamen je Lage

- **lage_1a**: Blasiusgasse; Eichhornstraße; Herzogenstraße; Juliuspromenade; Kaiserstraße; Kürschnerhof; Marktplatz; Martinstraße; Otto-Wels-Straße; Plattnerstraße; Reisgrubengasse; Schmalzmarkt; Wilhelmstraße
- **lage_1b**: Bronnbachergasse; Dominikanergasse; Dominikanerplatz; Eichhornstraße; Juliuspromenade; Marktplatz; Schönbornstraße; Semmelstraße; Spiegelstraße; Theaterplatz; Theaterstraße
- **lage_2**: Augustinerstraße; Beim Grafeneckart; Bockgasse; Bronnbachergasse; CC Passage; Dominikanerpassage; Dominikanerplatz; Dompassage; Domstraße; Grabenberg; Grabengasse; Herrnstraße; Herzogenstraße; Häfnergasse; Juliuspromenade; Kaiserstraße; Karmelitenstraße; Katharinengasse; Ludwigstraße; Marienplatz; Marktplatz; Maulhardgasse; Plattnerstraße; Schustergasse; Schwanenhof; Semmelstraße; Spiegelstraße; Textorstraße; Theaterstraße; Ulmer Hof; Untere Bockgasse; Unterer Markt; Wolfhartsgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 6.36 | 0.215 | 0.2 | – |
| lage_1b | 2.73 | – | – | 0.9 |
| lage_2 | 3.63 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.167 | 14 | 0.286 | lage_1b, lage_2 | Dominikanerplatz |
| 2 | 0.05 | 3 | 0.0 | keine | Neubaustraße |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 11.94 / 1b 8.27 / 2 7.52 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 11.94 / 1b 8.27 / 2 7.52 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 1.547 km → lage_1a.min_density (6.36) erhöhen | False |
| OK | lage_1b: Länge 1.0–2.0 km | 1.357 km | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.493 km | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
