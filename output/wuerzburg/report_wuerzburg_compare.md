# Lagevergleich Würzburg, Germany: Rastermodus gegen Street-Modus

Datenquelle: © OpenStreetMap-Mitwirkende (ODbL). OSM-Datenstand 2026-10-19T16:39:21Z, Lauf 2026-10-19T19:54:51+00:00, params_hash `40e5ebdf18`.  
Street-Modus: auto_calibrate = **False**, seed = **strongest_chain**. Overrides: city='Würzburg, Germany'. Rastermodus: `peak_share`, Res. 11, max_area_ha [6, 10, 20].

## Vergleich je Lage

Raster: Straßenlänge = Segmente im Polygon, POIs = Erdgeschoss-POIs im Polygon. Street: Länge der Lage-Segmente, POIs = den Segmenten zugeordnete POIs (das Straßenraum-Polygon enthält keine Gebäude und damit kaum POIs). Filialanteil = Anteil Filialisten (brand/brand:wikidata).

| Lage | Ziel km | Raster km | Street km | Raster ha | Street ha | Raster POIs | Street POIs | Raster Filialanteil | Street Filialanteil |
|---|---|---|---|---|---|---|---|---|---|
| lage_1a | 0.6–1.2 | 2.26 | 1.574 | 6.09 | 5.0 | 173 | 140 | 0.301 | 0.407 |
| lage_1b | 1.0–2.0 | 2.99 | 0.887 | 10.12 | 0.67 | 220 | 87 | 0.15 | 0.069 |
| lage_2 | 2.0–4.0 | 5.78 | 3.638 | 19.99 | 3.31 | 233 | 252 | 0.086 | 0.111 |

## Street-Modus: Lagen (Kennwerte über die zugeordneten Segmente)

| lage | length_km | area_ha | poi_count | density_per_100m | brand_share |
|---|---|---|---|---|---|
| lage_1a | 1.574 | 5.0 | 140 | 12.44 | 0.407 |
| lage_1b | 0.887 | 0.67 | 87 | 10.11 | 0.069 |
| lage_2 | 3.638 | 3.31 | 252 | 7.42 | 0.111 |

## Straßennamen je Lage

- **lage_1a**: Blasiusgasse; Eichhornstraße; Herzogenstraße; Juliuspromenade; Kaiserplatz; Kaiserstraße; Kürschnerhof; Marktplatz; Otto-Wels-Straße; Reisgrubengasse; Schmalzmarkt; Schönbornstraße; Wilhelmstraße
- **lage_1b**: Bronnbachergasse; Eichhornstraße; Marktplatz; Semmelstraße; Spiegelstraße
- **lage_2**: Augustinerstraße; Beim Grafeneckart; Bockgasse; Bronnbachergasse; CC Passage; Dominikanergasse; Dominikanerpassage; Dominikanerplatz; Dompassage; Domstraße; Grabenberg; Grabengasse; Herrnstraße; Herzogenstraße; Häfnergasse; Juliuspromenade; Kaiserstraße; Karmelitenstraße; Katharinengasse; Ludwigstraße; Marienplatz; Marktplatz; Maulhardgasse; Plattnerstraße; Schustergasse; Schwanenhof; Spiegelstraße; Textorstraße; Theaterstraße; Ulmer Hof; Untere Bockgasse; Wolfhartsgasse

## Schwellen (gewichtete Betriebe je 100 m Straßenfront)

| lage | min_density | min_brand_share | secondary_chain_share | min_centrality_pct |
|---|---|---|---|---|
| lage_1a | 6.77 | 0.215 | 0.2 | – |
| lage_1b | 2.9 | – | – | 0.9 |
| lage_2 | 3.87 | – | – | – |

## Nebenlagen (erfüllen die 1a-Schwelle, ohne Verbindung zur 1a)

| nebenlage_id | length_km | poi_count | brand_share | lage_im_ergebnis | street_names |
|---|---|---|---|---|---|
| 1 | 0.05 | 3 | 0.0 | keine | Neubaustraße |
| 2 | 0.217 | 17 | 0.353 | lage_2 | Dominikanerplatz; Grabenberg |
| 3 | 0.068 | 2 | 0.0 | keine | Glockengasse |

## Prüfungen

| status | check | detail | hart |
|---|---|---|---|
| OK | Genau 3 Lagen, gültig, nicht leer (1b darf leer sein) | leer: [] | True |
| OK | Überlappung < 1.0 m² | max. 0.0000 m² | True |
| OK | Dichte 1a > 1b und 1a > 2 | 1a 12.44 / 1b 10.11 / 2 7.42 je 100 m | True |
| OK | Dichte 1b > 2 | 1a 12.44 / 1b 10.11 / 2 7.42 je 100 m | False |
| WARNUNG | lage_1a: Länge 0.6–1.2 km | 1.574 km → lage_1a.min_density (6.77) erhöhen | False |
| WARNUNG | lage_1b: Länge 1.0–2.0 km | 0.887 km → lage_1b.min_density (2.9) senken | False |
| OK | lage_2: Länge 2.0–4.0 km | 3.638 km | False |

## Hinweise zur Methode

- Gleichnamige verbundene Wege werden zusammengeführt und in Abschnitte von 50 m geteilt; kürzere Restketten zählen für die Dichte mit 50 m (sonst erzeugen Stummel extreme Werte).
- Glättung über Segmente mit gemeinsamem Endpunkt; Zusammenhang der Lagen über Berührung (Endpunkte und Kreuzungen), Lücken bis max_gap_segments werden überbrückt und der Lage zugeschlagen.
- Auswertungspolygon: Puffer 20 m um die Achsen minus OSM-Gebäude und Einkaufszentren (nur Straßenraum); Teile ohne Kontakt zur Achse entfallen. Die Rasterpolygone enthalten dagegen Gebäude – Flächen nicht direkt vergleichbar.
- POIs in Einkaufszentren (shop=mall) zählen nicht.
- Fußgängerflächen (Plätze als Fläche) gehen nicht als Segment ein; POIs dort werden der nächsten Straße zugeordnet.
- Doppelt geführte Straßen (zwei Richtungsfahrbahnen) zählen mit doppelter Länge → niedrigere Dichte.
