# Sezioni lungo linee dai proxy 3D — disegno

Data: 2026-10-18 · ramo `Stratigraph_00001` · plugin 5.13.134-alpha → 5.13.135-alpha · s3dgraphy dev57.

## Da dove viene

È il secondo pezzo della richiesta di Enzo del 18 ottobre 2026; il primo, piante e prospetti all'import, è la 5.13.134-alpha (spec `2026-10-18-geometrie-dai-proxy-3d-design.md`). Fra le viste dei disegni verticali Enzo ha scelto anche «Sezioni lungo linee: tracci una linea di sezione in pianta (layer delle sezioni): il 3D viene tagliato lungo quel piano. Siccome le linee si tracciano sulle piante già importate, è un comando che si lancia dopo l'import». Poi ha detto: «procedi con tutto quello che consigli senza chiedermi conferma».

Le regole del primo pezzo valgono anche qui:
- i disegni verticali vanno in `pyunitastratigrafiche_usm`, in coordinate del disegno;
- `tipo_doc` e `nome_doc` sono gli stessi nel documento, nei poligoni e nella lista Documentazione della scheda US;
- l'em.json non cambia.

### Che cosa c'è

- `pyarchinit_sezioni`, che la scheda Documentazione carica con la vista `pyarchinit_sezioni_view` filtrata per sito, tipo e nome del documento: `gid`, `id_sezione`, `sito`, `area`, `descr`, `the_geom` LINESTRING, `tipo_doc`, `nome_doc`. Nel template SQLite l'SRID è `-1`, in `pyarchinit_db.sqlite` è 3004.
- L'em.json importato è ricordato per sito (`em_sources.load_source(db, sito)`, contenuto intero; il percorso no).
- I proxy sono media delle schede: `em_project.media_index` e `media_file_for` li ritrovano dal locatore, come per la scena 3D della narrativa.
- Dal primo pezzo: `glb_mesh`, `em_drawings` (posizione, `_union_2d`, `_clean`, `crs_kind`, nomi e coppie) e `sync/em_drawings_import` (schede, scrittura, `_auto_id`, coppie rifatte da tutti i poligoni ricavati, `unfilter_usm_view`).

## Obiettivo

Un comando del menu, **Extended Matrix → Sezioni dai modelli 3D…**, taglia i proxy delle unità di un sito lungo le linee di `pyarchinit_sezioni` di quel sito che si scelgono. Ogni linea diventa una **sezione** in `pyunitastratigrafiche_usm`: il profilo tagliato di ogni unità che la linea attraversa, X = metri lungo la linea dal suo primo punto, Y = quota. Ogni sezione è un documento di tipo **Sezione** (thesaurus 9.1 `SEZ`), con il nome `3D-SEZ-<id_sezione>`, legato ai poligoni, alla lista Documentazione delle schede e, se è libera, alla linea stessa.

## Non obiettivi

- Disegnare nella sezione quello che si vede oltre il taglio (il prospetto dietro).
- Tagliare modelli aperti: un proxy che non è chiuso non dà un profilo chiuso, e si salta.
- Linee prese da un layer qualunque: valgono solo quelle di `pyarchinit_sezioni`.
- Cambiare il primo pezzo, salvo quanto serve perché un reimport non cancelli le sezioni.

## Decisioni

**S1 — Moduli.**

| Modulo | Cosa fa |
|---|---|
| `em_drawings.section_geometry(tri_map, a, b)` | il taglio di un tratto di linea, puro |
| `sync/em_sections.py` | linee, unità, calcolo, scrittura |
| `em_sections_dialog.py` | la finestra |
| `pyarchinitPlugin._run_em_sections` | la voce di menu |

**S2 — Il taglio.** Un tratto A→B definisce un piano verticale. `r = (B−A)/|B−A|` è l'asse del disegno e `d = (−r_y, r_x)` la direzione di chi guarda: per una linea tracciata da ovest a est, chi guarda sta a sud e A è a sinistra. Il calcolo:
1. Per ogni triangolo che attraversa il piano, il segmento d'intersezione. La distanza con segno da `d` di un vertice che sta proprio sul piano vale +ε.
2. In coordinate del disegno, `u = (P − A)·r` e `v = quota`.
3. I segmenti si uniscono (noding) e si chiudono in poligoni (`QgsGeometry.polygonize`).
4. I poligoni si ritagliano fra `u = 0` e `u = |AB|`.
5. `_clean`.

Una linea spezzata si taglia tratto per tratto, con `u` che continua da un tratto all'altro. Un'unità che il piano attraversa senza che il profilo si chiuda risulta saltata, con il motivo «la sezione non si chiude (modello aperto)».

**S3 — Sistemi.**
- Le unità si mettono sulla mappa come nel primo pezzo: em.json, `place`, spostamento Z scelto.
- Le linee si leggono nel sistema del loro layer e si portano in quello dell'em.json con `QgsCoordinateTransform`, se diverso. Se il layer delle sezioni non ha un sistema (`-1` o `0`), le coordinate si prendono così come sono, come se fossero nell'EPSG dell'em.json, e il riepilogo lo dice.
- Il layer USM deve essere metrico; altrimenti ci si ferma, prima di scrivere, come nel primo pezzo.
- Senza un em.json georeferenziato il comando si ferma: senza posizione le linee della mappa e i modelli non si incontrano.

**S4 — Nomi e documenti.**
- Il nome è `3D-SEZ-<id_sezione>`, ripulito come nel primo pezzo. Una linea senza `id_sezione` usa `3D-SEZ-G<gid>`; due linee con lo stesso nome prendono `-<gid>`.
- Il tipo viene dal thesaurus `SEZ` nella lingua del plugin, poi IT, poi «Sezione».
- La nota del documento dice la linea, il riferimento del disegno e lo spostamento Z.
- `is_derived_name` riconosce anche `3D-SEZ-…`. L'export dell'em.json le lascia fuori e il reimport le conserva, come le altre.
- La linea di sezione prende `tipo_doc`/`nome_doc` del documento se li ha vuoti. Se ne ha già altri non si toccano, e il riepilogo lo dice.

**S5 — Sostituzione.** Il comando sostituisce solo le sezioni che calcola: poligoni e documenti con quei nomi, e disegnatore «pyArchInit 3D». Il reimport con piante e prospetti (primo pezzo) sostituisce solo `3D-PLA` e `3D-PRO-…`, non più tutto il `3D-%`; le sezioni restano. Le coppie della scheda si rifanno sempre da tutti i poligoni ricavati del sito.

**S6 — Impaginazione.** Le sezioni stanno a sinistra di `u = 0`, dove i prospetti del primo pezzo non arrivano mai. La prima comincia `GAP` a sinistra del disegno ricavato più a sinistra che resta nel sito (o di 0), le altre seguono verso sinistra, ognuna separata da `GAP`.

**S7 — La finestra.** Contiene:
- il sito scelto;
- la posizione dell'em.json ricordato;
- lo **Spostamento Z**, con le quote che ne risultano;
- la tabella delle linee del sito: **Sezione** (`id_sezione`), **Descrizione**, **Area**, **Tratti**, **Lunghezza** e la casella per sceglierla;
- quante unità hanno un proxy che si trova fra i media.

**Taglia** calcola e scrive, con la barra; il riepilogo dice quante sezioni, quante unità tagliate per sezione, le unità saltate col motivo e le linee che hanno già un altro documento. Senza em.json ricordato, senza linee nel sito o senza proxy, un messaggio dice che cosa manca (importare l'em.json con i media, tracciare le linee nel layer delle sezioni).

## Errori e casi limite

- Linea con meno di due punti, o tratti di lunghezza zero: si salta, col motivo.
- Il piano non incontra un'unità: l'unità non è nella sezione; non è un errore.
- Proxy non trovato fra i media, o GLB che non si legge: l'unità si salta, col motivo.
- Una riga che non si scrive: SAVEPOINT, come nel primo pezzo.
- Una sezione senza nessun profilo: niente documento, e il riepilogo la conta come vuota.

## Verifica

- Test puri:
  - una scatola tagliata a metà dà un rettangolo largo come la scatola e alto quanto lei;
  - il taglio si ritaglia al tratto;
  - una linea spezzata ha `u` continuo;
  - un modello aperto non dà profilo;
  - una linea che non incontra niente dà None;
  - un vertice sul piano non rompe il taglio;
  - a sinistra c'è A.
- Test con DB (fixture del primo pezzo, linea scritta nel layer delle sezioni):
  - poligoni, documento «Sezione», coppie della scheda e linea collegata;
  - la seconda volta sostituisce;
  - il reimport con piante e prospetti non tocca le sezioni;
  - linee in un altro sistema metrico;
  - layer delle sezioni senza sistema;
  - impaginazione a sinistra;
  - PostgreSQL in uno schema temporaneo.
- Finestra e voce di menu (costruzione e collegamenti).
- TempluMare vero: una linea attraverso la cella; immagine della sezione resa da QGIS.
- Suite intera verde.

## Fuori da questa release

- Il prospetto oltre il taglio.
- Il riempimento dei profili per tipo di unità (stili).
