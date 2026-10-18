# Import em.json: piante e prospetti dai proxy 3D — disegno

Data: 2026-10-18 · ramo `Stratigraph_00001` · plugin 5.13.133-alpha → 5.13.134-alpha · s3dgraphy dev57.

## Da dove viene

Enzo, 18 ottobre 2026: «è vero che non ci sono geometrie gis (quindi 2d) dello scavo ma è anche vero che c'è il 3D. quindi se convertissimo per gis tutte le geometrie in 2d quindi in pianta, dalle geometrie 3d e le inserissimo in pyunitastratigrafiche e pyunitastratigrafiche_usm (sezioni muri verticali)? lo si potrebbe fare come opzione quando importiamo l'em.json e scegliamo cosa convertire».

Poi: «in pianta (visto dall'alto) vanno in pyunitastratigrafiche, mentre in pyunitastratigrafiche_usm vanno tutti i prospetti che possono essere sezioni, prospetti di muro, cioè tutte le geometrie verticali che vedi di fronte». Le viste scelte sono tre: i quattro lati del sito, un prospetto per unità, e le sezioni lungo linee. Le sezioni lungo linee sono il secondo pezzo, con una spec e una release a parte.

Il 17 ottobre Enzo aveva detto «No non ricavare le geometrie dai 3D», ma parlava dell'em.json. Qui le geometrie restano in pyArchInit e l'em.json non cambia.

Due regole date da Enzo durante il disegno:

- **Sistema di riferimento.** Se il DB è in un EPSG diverso da quello dell'em.json, deve dirlo. Se serve, l'import si annulla, perché il DB va ricreato nel sistema giusto. Senza geometrie da scrivere si importano solo le schede, come oggi.
- **Documenti.** «nome doc e tipo doc in documentazione sono connessi con nome doc e tipo doc nel layer pyunitastratigrafiche e pyunitastratigrafiche_usm quindi devono corrispondere per essere richiamati insieme». Anche `us_table.documentazione` è una lista di coppie `[tipo, nome]`.

### Misure

TempluMare v3.2, `/Volumes/Extreme Pro/TempluMare_v2_for_3DR_2026-10-06/EM/proxies`, letto in sola lettura:

- 65 GLB, nessuna estensione (`extensionsUsed` vuoto), solo primitive `mode 4` (TRIANGLES). Ogni GLB ha un nodo con `translation` e `rotation`.
- Il nodo `geo_Temple` dell'em.json dice `epsg 31700` (Stereo 70), `shift_x 327300`, `shift_y 448370`, `shift_z 500`, `rotation 0`, `rotation_reference "grid"`.
- La quota dei nodi glTF (`translation[1]`) è circa 495 m e le mesh scendono di 2–4 m. Con lo `shift_z` dell'em.json le quote verrebbero 991–995 m. Ulpia Traiana Sarmizegetusa sta intorno ai 500 m, quindi probabilmente lo `shift_z` è sbagliato, oppure le quote del GLB sono già assolute. È da dire a Emanuel; nel frattempo lo spostamento Z si corregge nella finestra (D12).

### pyArchInit, com'è oggi

- `pyunitastratigrafiche`: piante, «US orizzontali». `pyunitastratigrafiche_usm`: «Unità Stratigrafiche Verticali disegno», cioè sezioni e prospetti. Le due tabelle hanno la stessa forma: `gid, area_s, scavo_s, us_s, stratigraph_index_us, tipo_us_s, rilievo_originale, disegnatore, data, tipo_doc, nome_doc, coord, the_geom MULTIPOLYGON, unita_tipo_s`.
- Nel template SQLite e sul DB PostgreSQL di test `area_s`, `scavo_s` e `us_s` sono `TEXT`. `structures/*.py` dice `Integer`, ma è stantio. Le viste `pyarchinit_us_view` e `pyarchinit_usm_view` uniscono il disegno alla scheda con `area_s = area AND scavo_s = sito AND us_s = us`. La vista USM ordina per `order_layer`, poi `stratigraph_index_us DESC`, poi `gid`.
- La scheda Documentazione (`charge_vector_layers_doc`) carica «US orizzontali» da `pyarchinit_us_view` e «US verticali» da `pyarchinit_usm_view`, con il filtro `sito = … AND nome_doc = … AND tipo_doc = …`, dove `tipo_doc` è il `tipo_documentazione` del documento. Dalla scheda US il pulsante «disegna doc» fa lo stesso con la coppia `[tipo, nome]` della riga scelta in `tableWidget_documentazione`.
- `documentazione_table`: `id_documentazione, sito, nome_doc, data, tipo_documentazione, sorgente, scala, disegnatore, note, entity_uuid`.
- Thesaurus `documentazione_table`, tipologia `9.1` (IT): `PLA` Planimetria, `PRO` Prospetto, `SEZ` Sezione, `MOD` Modello tridimensionale, e altre.
- `us_table.documentazione` è la `repr` di una lista di coppie, per esempio `[['Fotografie', 'Si'], ['Sezione', 'AA1']]`. La scrive `table2dict` e la si legge con `literal_eval`.
- Le schede importate da un em.json hanno `us_table.node_uuid` uguale all'id del nodo EM (`SU002` → `38961f2e-…`).
- Il template `resources/dbfiles/pyarchinit_db.sqlite` ha i layer in SRID 3004. Ci sono DB con SRID `-1`.
- L'export dell'em.json (`graph_projector`) porta `us_table.documentazione` dentro l'em.json come attributo dell'unità, e da lì diventano nodi documento `<uuid>_doc_<nome>`.
- `qfield_importer` ha già `target_srid(conn, engine, tabella, colonna)`, `next_id` e `reflected`, e scrive riga per riga in un SAVEPOINT.
- `shapely` non è una dipendenza di pyArchInit: non è in `requirements.txt` e nessun modulo lo importa. `numpy` sì.

## Obiettivo

Nella finestra «Importa em.json…», un'opzione ricava dai proxy 3D delle unità:

1. la **pianta** di ogni unità scelta, in `pyunitastratigrafiche`, nel sistema dell'em.json (eventualmente convertito, D8);
2. i **prospetti del sito** da nord, est, sud e ovest, e il **prospetto di ogni unità** scelta, in `pyunitastratigrafiche_usm`, in coordinate del disegno (metri lungo la vista, quota);
3. un **documento** per ogni disegno, nella scheda Documentazione, con lo stesso tipo e nome nei poligoni e nella lista Documentazione della scheda US: così si richiamano insieme da tutte e due le schede.

## Non obiettivi

- Le sezioni lungo linee: sono il secondo pezzo, con spec e release a parte.
- Togliere le parti nascoste nei prospetti (linee nascoste): ogni unità ha la sagoma intera.
- I punti quota (`pyarchinit_quote`, `pyarchinit_quote_usm`).
- Scrivere qualcosa nell'em.json: né geometrie, né documenti ricavati (D11).
- GLB compressi (Draco, meshopt, quantizzazione), `.gltf` con buffer esterni, OBJ, PLY, `.blend`.
- Cambiare l'SRID del DB, o ricrearlo.
- Geometrie per le unità senza proxy, o per i paradati.

## Decisioni

**D1 — Moduli.**

| Modulo | Cosa fa | Dipende da |
|---|---|---|
| `modules/s3dgraphy/glb_mesh.py` | legge un GLB e dà i triangoli nel sistema della scena glTF | numpy |
| `modules/s3dgraphy/em_drawings.py` | sistemi, proiezioni, poligoni, viste, impaginazione, nomi | numpy, `qgis.core.QgsGeometry` |
| `modules/s3dgraphy/sync/em_drawings_import.py` | scelta delle unità, regola dell'SRID, scrittura nel DB, sostituzione | SQLAlchemy, i due moduli sopra |
| `modules/s3dgraphy/em_drawings_dialog.py` | la finestra «Geometrie dai modelli 3D» | Qt |

I collegamenti stanno in `s3dgraphy_dot_bridge.py` (scheda Import) e in `sync/graph_projector.py` (D11). I primi due moduli non toccano Qt né il DB.

**D2 — Lettura del GLB.** Il GLB 2.0 ha un chunk JSON e un chunk BIN. Si legge la scena `scene`, oppure la prima. I nodi si percorrono ricorsivamente, componendo `matrix` (column-major) o `translation`, `rotation` (quaternione `[x, y, z, w]`) e `scale`.
- Primitive accettate: `mode` 4 (TRIANGLES), 5 (STRIP) e 6 (FAN), con o senza `indices` (5121, 5123, 5125). Le altre (punti, linee) si ignorano.
- `POSITION`: float32 VEC3, con `byteOffset` e `byteStride`.
- Sono **non supportati**, con il nome del motivo: `extensionsRequired` (Draco, meshopt, quantizzazione), accessori sparsi, buffer esterni, un file che non comincia con `glTF` versione 2.
- Limiti: `MAX_TRIANGLES = 200_000` per file e `MAX_FILE = 100 MB`. Oltre, il modello è «troppo grande».

**D3 — Sistemi di riferimento.**
- Dalla scena glTF (Y in alto) alla scena EM (Z in alto): `X = gx`, `Y = −gz`, `Z = gy`.
- In pianta: la regola di s3dgraphy, `api.georeference_scene(graph, punti, epsg_target=<epsg dell'em.json>)`, cioè rotazione oraria dal nord, poi spostamento, senza PROJ. Così pyArchInit mette la scena dove la mette EMStudio.
- Quota assoluta: `Z + spostamento Z`. Lo spostamento parte dallo `shift_z` dell'em.json e si cambia nella finestra.
- La georeferenziazione si legge con `api.georeference_state(graph)`. Con `"undeclared"` o `"legacy_default"` (EPSG:4326 a 0,0) non si fanno piante (D8).

**D4 — Pianta.** I triangoli si proiettano su XY. Si scartano quelli con area sotto 1 mm², per esempio le facce verticali. Si uniscono a blocchi di 2.000 con `QgsGeometry.unaryUnion`, poi si fa l'unione dei blocchi. Poi, in ordine:
1. `makeValid()`
2. `simplify(0.01)`
3. `makeValid()`
4. via le parti e i buchi sotto 1 cm²

Il risultato è un MultiPolygon. Se viene vuoto, il modello è «vuoto in pianta».

**D5 — Viste verticali.** Una vista ha una direzione orizzontale `d`, da chi guarda verso la scena, e un asse destro `r = (d_y, −d_x)`. Un punto della scena diventa `u = (P − O)·r`, `v = quota assoluta`. `O` è l'angolo minimo dell'ingombro in pianta del sito. Le sagome si ottengono come in D4, ma sul piano (u, v).
- **Lati del sito.** Chi guarda sta dal lato che dà il nome alla vista:

  | Vista | d | r | a sinistra |
  |---|---|---|---|
  | N | (0, −1) | (−1, 0) | est |
  | E | (−1, 0) | (0, 1) | sud |
  | S | (0, 1) | (1, 0) | ovest |
  | W | (1, 0) | (0, −1) | nord |

  Le direzioni sono quelle della griglia della mappa, dopo la rotazione di D3.
- **Prospetto di un'unità.** Si prende `orientedMinimumBoundingBox` della sua pianta. Se il rapporto lato lungo / lato corto è almeno 1,5, `d` è perpendicolare al lato lungo, con il verso scelto in modo che `d·(C_unità − C_sito) > 0`: chi guarda sta dal lato del centro dello scavo. Altrimenti `d = normalizza(C_unità − C_sito)`; se l'unità sta al centro, `d = (0, 1)`. La direzione da cui si guarda, `−d`, si dice con gli otto punti della rosa (N, NE, E…) e va nella nota del documento.

**D6 — Impaginazione dei disegni verticali.** L'ordine è: `3D-PRO-N`, `3D-PRO-E`, `3D-PRO-S`, `3D-PRO-W`, poi i prospetti delle unità in ordine di nome. Ogni disegno si sposta in `u` in modo da cominciare al cursore. Il cursore poi avanza della larghezza del disegno più `GAP = 10 m`. La `v` non si tocca, così la quota si legge sempre come Y.

**D7 — Ordine di scrittura.** In ogni vista le unità si scrivono dalla più lontana alla più vicina (`C·d` decrescente), con `stratigraph_index_us = 1`. Nella tabella QGIS disegna per `gid`, quindi la più vicina sta sopra. La vista USM ordina prima per `order_layer` (la matrice), e solo a parità per `gid`.

**D8 — Il sistema del DB.** Le geometrie da scrivere ci sono se l'opzione è accesa e almeno una unità ha un modello che si legge. In quel caso, all'Anteprima e prima di scrivere qualsiasi cosa (anche le schede), si legge l'SRID di `pyunitastratigrafiche` e di `pyunitastratigrafiche_usm` (`target_srid`). Per sapere se un sistema è in gradi si usa `QgsCoordinateReferenceSystem.fromEpsgId(srid).isGeographic()`.

| Layer del DB | em.json georeferenziato | Cosa succede |
|---|---|---|
| stesso EPSG | sì | si scrive |
| altro EPSG metrico | sì | domanda «Converto le piante in EPSG:<srid> del DB?», **Converti** o **Annulla**. Con Converti le piante si convertono in Python con `QgsCoordinateTransform`; i prospetti mai |
| in gradi, oppure `-1`, `0` o assente | — | ci si ferma, prima di scrivere: «ricrea il DB in EPSG:<epsg dell'em.json>, oppure togli la casella e importa solo le schede» |
| metrico | no | niente piante; prospetti con le quote locali |

La regola vale per ogni layer che riceve qualcosa. Le piante seguono la tabella. I prospetti chiedono solo un layer metrico, di qualunque EPSG, perché le loro coordinate sono del disegno: non si convertono mai, e un layer USM in gradi, `-1` o assente ferma l'import.

Senza geometrie da scrivere, nessun controllo. Annulla, o il fermo, annullano tutto l'import: nel DB non entra niente.

**D9 — Documenti e collegamenti.**
- Tipo: dal thesaurus `documentazione_table` 9.1, nella lingua del plugin: `PLA` per la pianta, `PRO` per i prospetti. Se manca, «Planimetria» e «Prospetto».
- Nome, cioè codice: `3D-PLA` per la pianta del sito; `3D-PRO-N`, `-E`, `-S`, `-W` per i lati; `3D-PRO-<unita_tipo><us>` per un'unità, per esempio `3D-PRO-US002`. Se due unità scelte avrebbero lo stesso nome, perché hanno lo stesso tipo e numero in aree diverse, a tutte e due si aggiunge `-A<area>`.
- In `documentazione_table` c'è una riga per disegno:
  - `sito`
  - `nome_doc`
  - `tipo_documentazione`
  - `data` (AAAA-MM-GG)
  - `sorgente` («em.json: <nome del file>»)
  - `disegnatore` («pyArchInit 3D»)
  - `note` (it/en): cosa è, il sistema o il riferimento del disegno, la direzione e lo spostamento Z
- Ogni poligono ha:
  - `scavo_s` = sito
  - `area_s`, `us_s`, `unita_tipo_s` dalla scheda (trovata per `node_uuid`)
  - `tipo_doc` e `nome_doc` **identici** a quelli del suo documento
  - `stratigraph_index_us` = 1
  - `disegnatore` = «pyArchInit 3D»
  - `rilievo_originale` = il locatore del proxy
  - `data`
  - `coord` = il centroide, `POINT(x y)`, come lo scrive il trigger `update_coord_on_geom` di pyArchInit. Il sistema della pianta e il riferimento del disegno verticale (X lungo la vista, Y quota) stanno nella nota del documento
- `us_table.documentazione` di ogni unità con almeno un disegno: si legge con `literal_eval`, si tolgono le coppie ricavate di prima (D10) e si aggiungono quelle di adesso. Si riscrive con `str(lista)`, come `table2dict`. Le altre coppie restano come sono. Un valore che non si legge non si tocca, e finisce nel riepilogo.

**D10 — Provenienza e reimport.** Un poligono o un documento è ricavato se ha `disegnatore = 'pyArchInit 3D'` e `nome_doc` comincia con `3D-`. Una coppia della scheda è ricavata se il nome rispetta `^3D-(PLA|PRO-.+)$`.

Reimportare un sito sostituisce l'insieme ricavato:
- si tolgono i poligoni ricavati del sito, nei due layer, e si scrivono quelli della scelta di adesso;
- un documento ricavato che non viene più prodotto si toglie solo se nessun poligono, ricavato o no, lo cita ancora;
- chi cambia il disegnatore di un poligono ricavato lo tiene, perché non è più ricavato.

Un'unità che ha già un disegno a mano compare nella finestra («ha già una pianta a mano», «ha già un disegno verticale a mano») con la casella spenta. Se la si accende, restano tutti e due.

**D11 — L'em.json non cambia.** `graph_projector`, quando porta `documentazione` nell'em.json, lascia fuori le coppie ricavate (D10). I poligoni non vanno nell'em.json, perché non c'è il posto. La mappa della narrativa li vede, perché legge le viste US e USM: TempluMare avrà la sua mappa.

**D12 — La finestra.** Nella scheda Import compare la casella «Ricava piante e prospetti dai modelli 3D», spenta, con il pulsante «Scegli…». Il pulsante apre «Geometrie dai modelli 3D», con:
- la posizione letta dall'em.json;
- lo spostamento Z modificabile, con le quote che ne risultano, aggiornate a ogni cambio;
- le caselle Nord, Est, Sud, Ovest;
- la tabella Unità / Tipo / Pianta / Prospetto / Stato, con i pulsanti Tutte e Nessuna. Lo Stato può essere: ok · file non trovato · formato non supportato: … · troppo grande · usa il 3D di <unità> · ha già una pianta a mano · ha già un disegno verticale a mano;
- la nota sulla sostituzione.

Senza aprire «Scegli…» vale la scelta predefinita: tutte le unità proprietarie di un proxy che si legge, pianta e prospetto, tranne quelle con un disegno a mano; i quattro lati; lo spostamento Z dell'em.json. Le unità che usano il 3D di un'altra unità restano spente. L'Anteprima aggiunge la riga «Dal 3D: N piante, 4 prospetti del sito, M prospetti di unità (si calcolano all'Applica)». Applica scrive le schede, poi i media, poi i disegni, con una barra di avanzamento. Il riepilogo finale aggiunge «Dal 3D: …», con le unità saltate e il motivo, e la conversione se c'è stata.

**D13 — Unità e proxy.** Si usa `em_narrative_3d.scene_proxies(graph)`: un proxy per risorsa con il suo proprietario, e `unit_proxies` con chi usa la stessa proprietà «geometry» (D12: spento). Il file si cerca con `em_media_import.search_dirs_for(emjson, [cartella dei file])` e `s3dgraphy.resources.locate.resolve`, come per i media. Un'unità con più proxy li unisce in un solo poligono per disegno.

## Che cosa vede chi usa pyArchInit

1. Sceglie l'em.json e il sito, accende «Ricava piante e prospetti dai modelli 3D», e se vuole sceglie unità e viste.
2. Anteprima: le schede, più la riga «Dal 3D». Se il DB è nel sistema sbagliato, l'avviso arriva già qui.
3. Applica: le schede, i media, poi i disegni. Se serve conversione, la domanda viene prima di scrivere.
4. In QGIS, la vista US mostra le piante sulla mappa e la vista USM i prospetti. Dalla scheda Documentazione, il documento `3D-PRO-N` (Prospetto) carica le sue «US verticali». Dalla scheda US, la riga `[Prospetto, 3D-PRO-US002]` della Documentazione fa lo stesso.

## Errori e casi limite

- File non trovato, formato non supportato, troppo grande, vuoto, poligono che non si ripara: l'unità si salta, con il motivo, e l'import va avanti.
- Errore nello scrivere una riga: SAVEPOINT. Si salta la riga, le altre si scrivono, e l'errore va nel riepilogo.
- Un errore in tutto il passo dei disegni non tocca le schede già scritte: il riepilogo lo dice.
- L'em.json non è georeferenziato: niente piante; prospetti con quote locali; lo dice la finestra.
- Una scheda dell'unità non si trova dopo l'import, perché manca `node_uuid`: l'unità si salta.
- Su PostgreSQL e SQLite la scrittura è la stessa (SQLAlchemy, WKT con SRID). La geometria si scrive con `ST_GeomFromText`/`GeomFromText` più `ST_Multi`/`CastToMultiPolygon`, senza `Transform` in SQL, perché la conversione la fa già Python.

## Verifica

- Test puri con GLB sintetici scritti nei test (un cubo, un muro lungo, un anello con buco, un nodo ruotato e uno con figli, una STRIP):
  - area e buchi della pianta;
  - spostamento e rotazione di s3dgraphy;
  - le quattro viste (chi sta a sinistra);
  - la direzione del prospetto di un muro;
  - l'impaginazione con GAP;
  - l'ordine dal lontano al vicino;
  - i nomi, e il caso dei nomi doppi;
  - i rifiuti: Draco, sparse, non GLB, troppo grande.
- Regola dell'SRID: le quattro righe di D8, con il DB SQLite in 31700, 3004, 4326 e -1.
- Scrittura su SQLite (copia del template, mod_spatialite) e su PostgreSQL (`conftest_pg`):
  - poligoni, documenti, coppie della scheda;
  - la vista US che unisce il poligono alla scheda (anche con `us = '002'`);
  - il filtro della scheda Documentazione che trova le «US verticali»;
  - il reimport, che non duplica, toglie solo il ricavato e lascia i disegni a mano;
  - il documento ricavato che resta, finché un poligono lo cita.
- Export: un em.json esportato da un sito con coppie ricavate non le ha; le altre coppie restano.
- TempluMare vero, su copie in sola lettura dell'em.json e dei proxy: DB nuovo in EPSG:31700, import con l'opzione accesa. Poi:
  - conteggi;
  - immagine della vista US e dei quattro prospetti resa da QGIS senza schermo;
  - la pianta del tempio sopra l'ingombro del 3D;
  - la narrativa con la mappa.
- Suite intera verde.

## Fuori da questa release, da decidere dopo

- Le sezioni lungo linee (secondo pezzo).
- Le linee nascoste nei prospetti.
- I punti quota ricavati dal 3D.
- Lo `shift_z` di TempluMare: da chiedere a Emanuel.
- I GLB compressi.
