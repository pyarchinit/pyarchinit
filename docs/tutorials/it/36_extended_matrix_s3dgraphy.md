# Tutorial 36: Extended Matrix Export e Bridge s3dgraphy

## Introduzione

A partire dalla versione **5.2.0-alpha** PyArchInit integra un **bridge bidirezionale** con la libreria **s3dgraphy** (modello dati Extended Matrix di Emanuel Demetrescu). Il bridge consente di:

- **Esportare** il diagramma stratigrafico come Extended Matrix in **em.json**, il formato che apre EMStudio (il vecchio export GraphML è in pensione)
- **Reimportare** modifiche fatte in yEd (movimenti di US tra periodi/gruppi) aggiornando il database SQL pyarchinit
- **Allegare paradata** (Author / License / Embargo) a livello sito
- **Raggruppare** US per dimensione (struttura, area, attivita, settore, ambient, saggio, quad_par o gruppi ad-hoc)

Tag corrente: `narrativa-media-5.13.130-alpha` (2026-10-17).

---

## 1. Prerequisiti

- Database SQLite/Spatialite **oppure PostgreSQL/PostGIS**: l'esportazione in em.json è la stessa sui due motori (la connessione è quella del progetto; `export_site` accetta `sqlite://` e `postgresql://`)
- Migrazione **Phase 1 node_uuid** applicata automaticamente all'apertura del DB
- **EMStudio** per aprire l'em.json (si installa da **Extended Matrix → Installa EMStudio…**), oppure il pannello **Vedi la matrice…** dentro QGIS, che non ha bisogno di niente. **yEd** (https://www.yworks.com/products/yed) serve solo se importi file GraphML disegnati lì (§5)

> ⚠️ Per DB pre-5.2.0-alpha la migrazione potrebbe richiedere riavvio di QGIS.

---

## 2. Esporta Extended Matrix (pulsante verde)

### 2.1 Aprire il dialog

1. Apri la **Scheda US** del sito desiderato
2. Click sul pulsante verde **"Esporta Extended Matrix"** (sotto la tab Rapporti)

### 2.2 Tab "Export"

La finestra dice in alto a cosa serve ogni formato. Contiene:

- **Formati**: **DOT (Graphviz) — matrice di Harris** ed **em.json (Extended Matrix, per EMStudio)**, spuntati di partenza, più **Matrice per fasi (analisi cronologica)**, facoltativa. Il GraphML non si esporta più: il JSON di questa finestra **è l'em.json**, lo stesso file che fa il menu **Extended Matrix → Esporta sito in em.json…** — stesso proiettore, stessa simbologia.
- **Opzioni**: **Controlla la sequenza stratigrafica e segnala i problemi**. È l'unica opzione rimasta, ed è davvero letta: togliendo la spunta, il controllo non viene fatto. Le due vecchie caselle che parlavano a yEd (suggerimenti di auto-layout, colori per periodo) sono sparite insieme all'export GraphML.
- **Extended Matrix**: quattro pulsanti accanto all'export — **Apri in EMStudio** e **Vedi la matrice** (si accendono dopo un'esportazione em.json riuscita; il secondo disegna la matrice dentro QGIS, senza EMStudio), **Consegna alla stanza…** e **Apri la stanza**. Sono le stesse voci del menu pyArchInit, a portata di mano.

Premendo **Esporta** viene chiesta la **cartella di destinazione**.

Autori, licenze, embargo e gruppi si gestiscono nella finestra **"Manage paradata"** (§3).

### 2.2.1 Saggi: un grafo solo per tutto il sito

Dalla versione **5.13.109-alpha** l'em.json porta **un grafo solo**, con le unità di tutti i saggi: non c'è niente da scegliere. La finestra «Esporta Extended Matrix» non ha più il gruppo «Saggi», e le voci di menu **Esporta sito in em.json…** e **Vedi la matrice…** chiedono soltanto il sito.

Il saggio è il campo **Saggio** della scheda US: resta un campo come gli altri, che si può usare come dimensione per raggruppare le unità (`saggio`, §4) e che finisce nel *briefing* della narrativa (§10.4), ma non divide più il file. Un file esportato con le versioni precedenti (fino alla 5.13.108-alpha), con un grafo per saggio, si apre ancora nel pannello della matrice (§10.8).

### 2.3 Click "Esporta"

I file che nascono, secondo i formati spuntati:
- `<sito>.em.json` — Extended Matrix, da aprire in EMStudio o da consegnare alla stanza
- `Extended_Matrix_<sito>[_<area>].dot` — Graphviz DOT, per la matrice di Harris classica
- `Extended_Matrix_<sito>[_<area>]_phased.json` — vista per epoche

> **I luoghi viaggiano nell'em.json.** Il luogo del sito, la catena dei toponimi e i gruppi di aree, settori, saggi e ambienti escono insieme alle unità, legati da archi `is_in_location` (§4).

Il riepilogo finale elenca i file e, per l'em.json, **quanti nodi e quanti archi** sono usciti, con gli eventuali avvisi.

> **Dalla 5.13.122-alpha l'em.json esce più pulito.** Ogni unità ha **un solo** arco verso l'epoca in cui nasce (prima ne aveva due uguali: la libreria aggiungeva il suo dopo aver già riagganciato quello dell'importatore); la **descrizione** del nodo è la definizione stratigrafica o, se è vuota, la descrizione della scheda (prima usciva la parola «None»); il grafo ha un **nome**, quello del sito (prima EMStudio lo apriva come «Untitled»); un'unità che sopravvive fino a un'epoca più recente ha l'arco `survive_in_epoch` verso **ogni** epoca intermedia, non solo verso l'ultima. Per un sito che viene da un em.json di EMStudio vedi anche §5.0, «L'em.json resta ricordato».

> **Il GraphML non si esporta più**: la matrice si guarda e si valida in EMStudio, che legge em.json. Le righe temporali (swimlane) del vecchio GraphML sono andate via con lui. Il GraphML resta solo in **entrata**, per i file disegnati in yEd (§5).

---

## 3. Dialog "Manage paradata" (4 tab)

### 3.1 Accesso
Click sul pulsante **"Manage paradata"** nella scheda US (vicino al pulsante verde Export).

### 3.2 I 4 tab

| Tab | Contenuto | File generato |
|---|---|---|
| **Authors** | Aggiungi autori (nome + ORCID + ruolo) | `paradata_<sito>.graphml` |
| **Licenses** | Licenza dataset (es. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Date di embargo + motivazione | idem |
| **Groups** | Gruppi ad-hoc (nome + selezione US membri) | `groups_<sito>.graphml` |

I file vengono salvati accanto al DB SQLite e sono **versionabili in Git**.

---

## 4. Dimensioni e tipi di gruppo nell'em.json

L'em.json che esporta pyArchInit porta i **gruppi di luogo** (`LocationNodeGroup`) della scheda US, distinti dal tipo `kind`: `toponym`, la catena nazione → regione → provincia → comune e il luogo del sito (§4.1); `study`, le **aree**, i **settori** e i **saggi**; `functional`, gli **ambienti**. Ogni unità è legata ai gruppi in cui sta da archi `is_in_location`; l'identificatore del gruppo dice il campo da cui nasce (per esempio `loc::area::study::1`). Il file non porta colori: li decide chi lo legge, EMStudio con il suo stile e il pannello della matrice in QGIS con le regole visive della libreria s3dgraphy. Il vecchio export GraphML colorava i gruppi per dimensione: quella tavolozza è andata in pensione con lui. La libreria sa anche raggruppare per **struttura**, **attività**, **quadrato** e per gruppi ad-hoc, con un'appartenenza primaria e le altre secondarie (`is_primary`): pyArchInit oggi non glielo chiede, e nel file quell'attributo compare solo sugli archi della catena dei toponimi, sempre falso.

### 4.1 Catena toponym (5.6.0-alpha)

I campi `site_table.{nazione, regione, provincia, comune}` vengono emessi automaticamente come catena ricorsiva di `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). I livelli amministrativi vuoti vengono saltati senza interrompere la catena. Un dedupe cross-sito garantisce che lo stesso comune presente in 2 siti diventi **un solo nodo condiviso** nell'em.json.

---

## 4.2 Membership multidimensionale (5.6.0-alpha)

Un'unità può stare in più gruppi insieme — un'area, un settore, un saggio, un ambiente, oltre al luogo del sito — e nel file ha un arco `is_in_location` per ciascuno, tutti alla pari. Esempio: una US con `area=1`, `settore=1` e `ambient=Ambiente 3` ha tre archi, verso «1» (area, `study`), «1» (settore, `study`) e «Ambiente 3» (`functional`), più quello verso il luogo del sito, da cui sale la catena dei toponimi. La distinzione fra appartenenza primaria e secondaria (`is_primary`, con `struttura` al primo posto e `toponym` mai primario) è del modello della libreria, per chi le chiede i gruppi per dimensione: nell'em.json di pyArchInit non c'è.

---

## 5. Round-trip (Tab Import)

> **Che cosa si può importare**: la tab Import legge adesso anche **em.json** — quello di EMStudio o del nodo StratiGraph — e sceglie il lettore dall'estensione del file; il `.graphml` di yEd resta accettato per i file di prima. La procedura qui sotto, spostare le US fra i gruppi, riguarda la via yEd/GraphML.

### 5.0 Importare un em.json di EMStudio (anche con il database vuoto)

Un em.json scritto da **EMStudio** (non da pyArchInit) si importa nel database di pyArchInit **anche quando il database è vuoto** (dalla 5.13.121-alpha): il sito, i periodi, le schede, i rapporti e i media nascono dal file, senza dover creare prima nessun sito.

1. Apri il menu **Plugins → pyArchInit - Archaeological GIS Tools** e scegli la voce **Extended Matrix → Importa em.json…**: la finestra dell'Extended Matrix si apre già sulla tab **Import**, anche se il database non ha nessun sito. Dalla scheda US arrivi allo stesso punto: il pulsante verde **Esporta Extended Matrix**, senza un sito scelto, apre la stessa finestra sulla tab Import invece di fermarsi (l'**esportazione**, invece, continua a chiedere un sito).
2. Premi **Browse…** e scegli l'em.json.
3. Controlla il **Sito target:**. Se è vuoto — il caso di un database senza siti — viene proposto il nome del grafo scritto nell'em.json (per esempio «Temple») o, se manca, il nome del file senza «.em.json»; si può modificare. Se invece il campo mostra già un sito (con un database che ne ha: quello della scheda US da cui sei partito o, dal menu, il primo in ordine alfabetico), nessun nome viene proposto: scrivi il nome del sito nuovo o scegli quello in cui importare. Sotto ci sono due caselle, spuntate per default: **Crea periodi mancanti se assenti** (se la togli e il sito non ha già i periodi del file, l'importazione si ferma con l'errore «MissingEpochError») e **Importa anche i media citati (immagini, video, 3D, documenti)**. Sotto c'è il campo **Cartella dei file**, facoltativo, con il bottone **Sfoglia…**: serve quando l'em.json è stato copiato da solo, lontano dai file che cita — indica la cartella del progetto di EMStudio (quella con `EM/`, `DosCo`, `proxies`, `RB`…).
4. Premi **Anteprima**: non scrive niente, e dice quante schede sono nuove, aggiornate e invariate, quanti periodi sono nuovi e, in elenco, quante schede di che tipo, quanti nodi del file non diventano schede e quante unità hanno il loro **proxy 3D** (dalla 5.13.124-alpha; per TempluMare «65 unità su 112 hanno il loro proxy 3D.»: le stesse 65 che mostra EMStudio, che conta 114 unità perché include anche i 2 nodi di continuità).
5. Premi **Applica** (si abilita dopo l'anteprima): importa e mostra lo stesso riepilogo, più quello dei media.

Che cosa succede, in breve:

- **Che cosa diventa scheda.** Solo le unità di cui pyArchInit conosce il tipo (US, USM, USD, USVs, USVn, serUSVn, SF, VSF, RSF, USN, USNt…) e i paradati: le proprietà (`property`), gli estrattori (`Extractor`), i combinatori (`Combinar`) e i documenti (`DOC`). Risorse, file, modelli 3D, forme semantiche, processi del gemello digitale, gruppi, epoche e narrativa **non** diventano schede: prima della 5.13.121-alpha diventavano tutti «US».
- **I nomi (campo US).** Il nome del nodo senza il prefisso del tipo: USV105 → 105, D.05 → 05, D.05.02 → 05.02. Le proprietà che hanno lo stesso nome (per esempio «height», che compare per molte unità) prendono tra parentesi il nome dell'unità a cui appartengono: «height (105)». Se due tipi diversi darebbero lo stesso numero — il combinatore «C.10» e il documento «D.10», la US «SU002» e la USD «USD002» — il tipo più forte (la US, poi le altre unità, poi i documenti, gli estrattori, i combinatori) tiene il numero e l'altro tiene il nome completo di EMStudio («C.10», «USD002»), così i rapporti non si confondono.
- **I rapporti.** Fra due US/USM sono quelli di sempre di pyArchInit («Copre», «Taglia»…), e il «viene dopo» (`is_after`: l'unità è più recente dell'altra, senza dire che la tocca) si scrive con la freccia `>` (`A > B`: A è più recente di B), fra due US come fra tutti gli altri tipi: fino alla 5.13.130-alpha fra due US diventava «Copre», un contatto fisico che il file non dice, e l'esportazione lo rifaceva `overlies` (i nove `is_after` di TempluMare). Fra unità di tipo diverso i rapporti fisici si scrivono per esteso («Taglia», «Si appoggia a»), la catena dei paradati — unità → proprietà → estrattore o combinatore → documento, e il reperto «parte di» un reperto virtuale — con `>>`. Periodi, attività, gruppi e risorse non sono rapporti. All'esportazione questi segni ridiventano gli archi dell'Extended Matrix (`is_after`, `has_property`, `has_data_provenance`, `extracted_from`, `combines`, `is_part_of`). Ogni rapporto è scritto su **tutte e due** le schede, rovesciato sulla seconda — «Copre»/«Coperto da», «Taglia»/«Tagliato da», `>`/`<`, `>>`/`<<` —, come vuole la verifica dei rapporti della scheda US; una scheda senza rapporti ha la lista vuota, non il campo vuoto. Prima della 5.13.125-alpha la verifica dava «malformed node or string: None» e «Rapporto reciproco non trovato».
- **Attività e descrizione.** L'attività del nodo (il gruppo ActivityNodeGroup) va nel campo **Attività** della scheda; la descrizione del nodo nel campo **Descrizione**.
- **Periodizzazione.** Le epoche di EMStudio, che hanno solo nome e date, si ritrovano per nome nella periodizzazione del sito; quelle che non ci sono diventano periodi nuovi, dal più antico, numerati dopo l'ultimo periodo del sito, in fase 1, con le date di inizio e di fine e il nome come datazione estesa. Ogni unità prende periodo e fase iniziali dall'epoca in cui nasce e quelli finali dall'ultima epoca in cui sopravvive (o uguali agli iniziali). I periodi senza **codice periodo** lo ricevono in sequenza, 1, 2, 3…, in ordine di periodo e fase; ogni unità prende la **datazione** del suo periodo iniziale e il **codice periodo** come lo scrive «Crea codice periodo» (per esempio 1/2/3 per un'unità che vive dal periodo 1 al 3), se non li ha già (dalla 5.13.125-alpha).
- **Scheda sito.** Se il sito non esiste viene creato. La **definizione** è il bene di cui parla lo studio, se l'em.json lo dichiara, altrimenti il nome del grafo (per TempluMare «Temple»); **nazione, regione, provincia e comune** vengono dalla catena dei luoghi dell'em.json, quando c'è. Tutti e cinque finiscono anche nel **thesaurus** (scheda sito, codici 1.1–1.5), da cui la scheda sito li legge. La descrizione viene dal grafo: nome, codice, autori e posizione (EPSG e origine). Se il sito c'è già si riempie solo quello che è vuoto, e la definizione «Extended Matrix», scritta dalle versioni prima della 5.13.125-alpha, viene sostituita.
- **Media.** Seguendo i legami dell'em.json — scheda → risorsa → file, scheda → modello 3D → risorsa → file, e l'url del documento o dell'estrattore — i file citati diventano media della scheda. Si cercano come li cerca EMStudio: nella cartella dell'em.json e nell'albero del suo progetto EM (`EM/`, `EM/DosCo`, `EM/proxies`, `RB`, `RM`, `SB`), più la **Cartella dei file**, se l'hai indicata. Valgono immagini, video, modelli 3D (anche **GLB** e **GLTF**) e documenti (**PDF, Word, Excel, ODT, ODS, RTF, CSV, TXT**). Il media punta al **file originale**, come quelli aggiunti dalla scheda; la miniatura e la copia vanno nelle cartelle **Thumbnail path** e **Image resize** della configurazione (tutorial 01): i modelli 3D hanno la loro vista, i PDF la prima pagina, gli altri documenti un'icona col tipo. Il **proxy 3D** di un'unità — nel grafo sta sulla sua proprietà «geometry» — va sulla scheda dell'unità. Se la proprietà è condivisa da più unità — una USV che eredita la geometria della US che completa — il proxy va all'unità che l'ha creata, come in EMStudio (prima della 5.13.124-alpha andava alla prima unità trovata nel file). Il riepilogo dice quanti media sono nuovi e di che tipo, quanti già presenti, quante miniature, quanti file citati non sono stati trovati (con il consiglio di indicare la cartella del progetto), quante copie sono vuote (segnaposti del cloud, da scaricare di nuovo), quanti riferimenti esterni (web, rete, cloud) restano indirizzi e quali file non sono media (`.blend`, `.mtl`, `.zip`…). Un file archiviato in un bucket che ha anche una copia sul disco (nell'em.json, più indirizzi per la stessa risorsa) si importa dalla copia sul disco; prima della 5.13.124-alpha restava un riferimento esterno. Una seconda importazione non duplica niente. Prima della 5.13.122-alpha i file finivano copiati nella cartella principale di pyArchInit, i GLB non avevano miniatura (e la scheda non li mostrava), i proxy stavano sulla proprietà invece che sull'unità, e i PDF restavano fuori. Dalla 5.13.127-alpha le viste dei modelli 3D si disegnano tutte insieme in un processo Python a parte, fuori da QGIS: prima, su macOS, QGIS si chiudeva da solo alla chiusura del riepilogo dell'importazione.
- **Reimportare.** Importare di nuovo lo stesso file non duplica né i periodi né le schede: quelle già presenti risultano «invariate» o «aggiornate», e dove il database e il file differiscono vince il file (il riepilogo li conta come «conflitti»). L'anteprima conta come «aggiornate» anche le schede a cui l'importazione aggiunge rapporti, datazione o codice periodo (prima risultavano «invariate»). Reimportare l'em.json in un database importato prima della 5.13.125-alpha lo ripara: definizione del sito, rapporti su tutte e due le schede, datazione e codici periodo.
- **L'em.json resta ricordato.** pyArchInit tiene nelle sue tabelle le unità, i paradati, i rapporti e le epoche; tutto il resto del grafo — risorse, file, modelli, forme semantiche, processi del gemello digitale, gruppi di paradati e di attività, autori, licenze, la narrativa — insieme al titolo, al **codice dello studio** (per esempio GT16: è il prefisso con cui Blender riattacca i proxy), alla georeferenziazione (EPSG e spostamenti) e ai nomi di EMStudio, viene ricordato all'importazione (tabella `pyarchinit_em_sources`, una riga per sito; l'ultima importazione vince). All'**esportazione** dell'em.json del sito tutto questo torna: i nomi originali (SU006, D.07.08, height…) per le schede che hanno ancora il numero dato all'importazione — una scheda rinominata in pyArchInit tiene il nome nuovo —, i dati dei nodi (per esempio la proprietà «geometry» con la sua forma, da cui EMStudio conta i proxy), e i nodi che non sono schede con i loro archi, agganciati alle schede che esistono ancora: un ramo rimasto senza scheda (per esempio la forma di una proprietà cancellata) non torna. Rapporti, periodi e descrizioni vengono sempre dal database. Il messaggio di fine esportazione dice quanto è tornato, per esempio «Dall'em.json importato tornano 851 nomi, 1090 nodi e 1969 archi, codice dello studio GT16.». Provato su TempluMare_v3.2 (1946 nodi): nessun nome e nessuna descrizione diversi dall'originale, e in EMStudio 65 unità su 114 con il proxy e 2 epoche su 3 con un modello, come nell'originale. Restano diversi i 9 «viene dopo» fra due US, che pyArchInit scrive «Copre», e i gruppi di luogo del sito e dell'area con lo studio, che pyArchInit aggiunge.

La via yEd/GraphML, per spostare le unità fra i gruppi, è quella che segue.

Per modificare il database SQL spostando US tra gruppi nel GraphML:

1. Apri il GraphML in **yEd**
2. Trascina una US in un altro gruppo, salva
3. Torna al dialog → tab **"Import"**
4. **Spunta** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Carica il GraphML modificato

Il sistema esegue una transazione atomica: se qualcosa fallisce, **rollback completo** (il DB resta invariato). I gruppi `adhoc` non scrivono mai SQL — aggiornano solo `groups_<sito>.graphml`.

Da 5.6.0-alpha il walker di import è **ricorsivo** e supporta folder annidati (es. catena toponym `nazione > regione > provincia > comune > US`). In presenza di cicli nel grafo dei folder viene sollevata l'eccezione `CycleDetectedError` e l'import viene abortito con rollback.

---

## 6. CLI (alternativa al dialog)

Per script / batch:

```bash
# Esporta
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <nome> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Lista gruppi ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <nome>

# Aggiungi autore
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <nome> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = success, 1 = errore di bridge, 2 = errore argparse.

---

## 7. Risoluzione dei problemi

| Sintomo | Causa | Soluzione |
|---|---|---|
| "no such column: node_uuid" | Migrazione Phase 1 non eseguita | Riavvia QGIS, riapri il DB |
| GraphML vuoto | DB privo di rapporti / area filter troppo stretto | Verifica us_table.rapporti popolato |
| "i campi rapporti devono essere TESTO" | Hai inserito un numero come integer | I campi US/Area sono **TEXT**, non integer |
| Capitalizzazione errata sui rapporti | "copre" minuscolo nel DB | Usa "Copre", "Coperto da" capitalizzati |
| `DeprecationWarning` su file 5.5.x | File legacy `ActivityNodeGroup + group_kind` | Il projector promuove in-memory a `LocationNodeGroup`. Ri-esporta per migrare il file su disco. |
| Le righe della swimlane mostrano un testo lunghissimo | Nelle versioni precedenti come etichetta veniva usata la Descrizione della periodizzazione | Aggiorna il plugin e ri-esporta, e/o compila **Datazione estesa** con un nome breve |
| Le epoche della swimlane sono in ordine sbagliato (es. Bronzo sopra il Tardoantico) | Le righe sono ordinate per **Cronologia iniziale**; date a.C. inserite come numeri positivi (1650 invece di -1650) vengono ordinate come d.C. | Nella scheda Periodizzazione inserisci gli anni a.C. come numeri negativi e ri-esporta. Il riepilogo dell'export mostra ora un avviso "⚠️ Periodizzazione: ..." con l'elenco dei periodi da correggere |

---

## 8. Documentazione tecnica

Per approfondimenti su architettura, decisioni di design e roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over deferiti:
- **AI08-F3**: auto-layout heuristics (bin-packing dei sub-gruppi) — ancora differito
- **AI09**: TimeBranchNodeGroup mapping — futuro
- **Phase 3**: SyncEngine + REST API — futuro
- **Phase 4**: GraphDBBackend + SPARQL — futuro

Completati:
- **AI07** (5.6.0-alpha, 2026-05-10): migrazione `LocationNodeGroup` con `kind` enum + catena toponym + multi-dim memberships
- **AI08-F1** (fuso in AI07): hierarchical nesting nativo grazie a `is_primary`

---

## 5. yEd-aware Import — importare graphml editati esternamente (5.8.x)

A partire dalla **5.8.0-alpha** il bridge è **bidirezionale anche per graphml authored direttamente in yEd** (cioè senza prima passare da un export pyarchinit). Pyarchinit riconosce automaticamente i graphml "yEd-raw" — quelli che non hanno le data keys `pyarchinit.*` — e li importa con un dispatch dedicato che mappa node-label-prefix → tipo stratigrafico, riconosce TableNode-rows come periodi, walka i group folder come dimensioni archeologiche, e sceglie una policy per le edge che toccano folder.

### 5.1 Rollout in 6 milestone

| Milestone | Tag | Cosa aggiunge |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — `ClassificationKind` enum 13 valori (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive `^USVs|^USV|^USM|^US|^VSF|^RSF|^SF|^D\.|^C\.|property-keywords` |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate da TableNode rows) + `yed_group_walker.py` (FolderCandidate con auto-dimension da prefisso label: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orchestrator `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + `_DryRunRollback` sentinel + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` 5 pagine (classifier / periods / folders / policy / preview) + `YedOverrides` dataclass + sidecar `<graphml>.yed_overrides.json` persistence |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Questa documentazione + dev-log + CHANGELOG. |

### 5.2 Come funziona — flow utente

1. **Apri un graphml in QGIS via menu Import GraphML** (stesso path del flusso pyarchinit-projected esistente).
2. Pyarchinit rileva automaticamente che è yEd-raw (no `pyarchinit.*` keys) → dispatcha al nuovo branch invece di passare al legacy.
3. Si apre il wizard `YedImportDialog` con **5 pagine**:
   - **1/5 Classifier** — tabella con 1 riga per leaf node. Per ogni riga vedi `label` + `auto_kind` (es. `us_real` / `usv_virtual` / `property`) + combobox `user_kind` per override. Bottone **Accetta auto** azzera gli override (ritorna a `auto_kind` per ogni riga).
   - **2/5 Periods** — 1 riga per TableNode-row trovata, colonne editable `periodo` + `fase`. Le date (`datazione_iniziale`/`finale`) restano vuote: yEd-raw graphml non porta date.
   - **3/5 Folders** — 1 riga per group folder. Combobox per `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` per escludere). `value` editabile (default = `auto_value` derivato dal prefisso label).
   - **4/5 Rapporti policy** — 4 radio button per scegliere come trattare le edge che toccano folder:
     - **SKIP** (default): scarta le edge folder-touching. Le edge leaf-to-leaf passano intatte.
     - **FAN_OUT**: edge `folder_A → folder_B` espande in `N×M` leaf pairs (cartesian product dei membri).
     - **REPRESENTATIVE**: usa il primo membro del folder come proxy.
     - **SYNTHETIC**: crea 1 us_table row per folder (`unita_tipo='VA'` virtual activity) + rewire edge attraverso questi anchor.
   - **5/5 Preview** — dry-run di `import_yed_raw(overrides=..., dry_run=True)`. Mostra counts (us / inv / period / paradata) **senza committare**. Click **Finish** committa, **Cancel** abbandona.
4. Su **Finish** il wizard salva i tuoi override nel **sidecar JSON** `<graphml>.yed_overrides.json` accanto al file. Riaprire lo stesso graphml fa preload del sidecar → vedi i tuoi override pre-applicati.

### 5.3 Routing destinazioni

Il dispatch usa `_classify_destination` (in `yed_import_pipeline.py`) per smistare ogni leaf:

| ClassificationKind | Destinazione | Note |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | da label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | da `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | da `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | da `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` dal prefisso del label: USVs/USVn/USVc) | da `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | da `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | da `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | da `^VSF\d+` |
| DOCUMENT | `paradata` | da `^D\.\d+` |
| COMBINER | `paradata` | da `^C\.\d+` |
| PROPERTY | `paradata` | label keyword (`material`/`position`/`width`/...) |

**Decisione utente 2026-05-13**: USV* (virtuali) sono "unità tipo" e vanno in `us_table`, non in paradata. Solo DOC/COMB/PROP/VIRTUAL_FIND restano paradata.

### 5.4 Sidecar JSON — formato

Schema versionato per garantire forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/path/assoluto/al/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Solo i campi MODIFICATI dall'utente vengono salvati (diff). `ClassificationKind` values sconosciuti (es. da future s3dgraphy releases) sono skippati silently al load.

### 5.5 CLI per ingest scripted

Per CI / re-run batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` per backend SQLite vs PostgreSQL. `--overrides` è opzionale (no overrides = defaults yE-D). `--auto-defaults` è no-op forward-compat.

### 5.6 Limiti noti

- **No editing date in wizard**: yEd-raw graphml non porta `datazione_iniziale`/`datazione_finale`. La pagina Periods edita solo `periodo` + `fase` (gli FK target).
- **ParadataStore API parziale**: i metodi `add_virtual_us`/`add_document`/`add_combiner`/`add_property` non sono ancora implementati upstream. yE-D logga "skip — method missing" per ogni paradata leaf ma conta gli attempt nel preview.
- **PropertyNode → Path B (no US linkage)**: i nodi PROPERTY vengono scritti senza target US. Il wizard avvisa con warning. Futuro: yE-Closure follow-up per aggiungere "assign target" nell'interfaccia.
- **Multi-DB**: il sidecar JSON è per-graphml, non per-DB. Se importi lo stesso graphml in DB diversi, il sidecar contiene gli override applicabili a entrambi.

### 5.7 Test coverage finale

| Suite | Test | Coverage |
|---|---|---|
| yE-A | `test_yed_detector.py` | flavor detection |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | PeriodCandidate + FolderCandidate parse |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | sidecar persistence + CLI |

**Suite totale post-rollout**: 354 passed / 42 skipped (PG-L1 require psycopg2).

### 5.8 Aggiornamento 5.8.5-alpha (yed-fastfix)

Pacchetto di correzioni comportamentali sopra `5.8.3-alpha` che alza la qualità del re-export GraphML dopo un import yEd-aware. Modifiche rilevanti per l'utente finale:

- **Paradata multi-folder**: DOC / Combinar / Extractor / property label condivisi fra più folder yEd (es. `material` referenziato da VA01 + VA04 + VA05) generano ora UNA riga in `us_table` PER occorrenza — visibilità multi-folder ripristinata nel GraphML ri-esportato. Trade-off: il dedup per identità (`D.01` / `D.01-2` / `D.01bis` collassati su un'unica riga) non si applica più alla seconda/terza occorrenza.
- **Rapporti reciproci**: ogni edge yEd `a → b` scrive il rapporto diretto sulla riga di `a` E l'inverso sulla riga di `b` (`<<` / "Coperto da" / ecc.). I DOC mostrano ora tutte le connessioni extractor entranti nella Scheda US.
- **Strip del prefisso `us` numerico**: `US100` → `us='100'` `unita_tipo='US'` (prima `us='US100'`). SF/VSF/RSF scritti in dual-write su `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: l'appartenenza di una row di TableNode yEd al periodo si propaga a `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserva la distinzione semantica EM 1.5.
- **Re-import idempotente**: ri-eseguire lo stesso import salta le righe già presenti; nessun rollback per collisione UNIQUE alla seconda passata.
- **Palette USV**: i nodi USV sono ora resi col parallelogramma blu canonico EM (prima rettangolo con bordo rosso).

### 5.9 yE-F paradata multi-folder (5.9.0-alpha)

Evoluzione strutturale di `yed-fastfix-5.8.5-alpha`: il trade-off del Bug R B1 (una riga `us_table` per occorrenza, con `us='D.01_2'` / `us='D.01_3'`) è stato superato. Ora una foglia paradata (DOC / Combinar / Extractor / property) condivisa fra più folder yEd produce **una sola riga** in `us_table` per label canonico, e la multi-appartenenza è preservata in un nuovo campo `other_locations`.

Modifiche visibili all'utente finale:

1. **Nuovo widget "Altre attività" nella Scheda US/USM**: nel tab *Periodizzazione* compare un `QListWidget` etichettato "Altre attività" — visibile **solo** quando `unita_tipo` è una tipologia paradata (`DOC`, `Combinar`, `Extractor`, `property`). L'utente può selezionare più codici attività; la selezione viene serializzata come JSON list nella nuova colonna `other_locations`.
2. **Nuova voce di menu QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Va eseguita **una volta** su ogni DB pre-esistente per aggiungere la nuova colonna (i DB creati post-5.9 hanno già la colonna).
3. **Import yEd-aware migliorato**: una foglia paradata che compare in N folder yEd genera **1 sola** riga `us_table` (non più N righe con suffisso `_2`/`_3` come in 5.8.5). Il primo folder incontrato diventa l'`attivita` primario; i folder secondari vengono elencati in `other_locations`. In **export** vengono emesse N copie visuali yEd (una per folder), tutte condividenti lo stesso `node_uuid` canonico per garantire la round-trip identity.

**Backward compatibility**: i dati prodotti dal Bug R B1 in 5.8.5-alpha (righe con suffisso `_2`/`_3`) restano leggibili senza alcuna conversione automatica. La nuova logica si applica ai nuovi import; le righe legacy continuano a comportarsi come prima.

Predecessore: vedi sezione 5.8 (`yed-fastfix-5.8.5-alpha`) per il comportamento sostituito.

---

## 6. Genera continuità (schede CON)

Nel pannello **"Verifica rapporti"** — disponibile come tab all'interno del dialog di import/export s3dgraphy — è presente il pulsante **"Genera continuità"**. La funzione crea automaticamente, per il sito attualmente selezionato, le **schede di continuità** delle US/USM che attraversano più di un periodo.

### 6.1 Cosa fa

1. Scansiona tutte le US/USM del sito in cui **periodo iniziale ≠ periodo finale** (cioè la cui vita si estende su più periodi).
2. Per ognuna crea o aggiorna una scheda di continuità denominata **`CON_<us>`** (es. `US5` → `CON_US5`).
3. La scheda CON **eredita** dall'unità madre: sito, area (più le aree secondarie), struttura e l'intero arco di periodi (iniziale → finale). La descrizione viene generata automaticamente.
4. Scrive un **rapporto di continuità reciproco** su entrambi i lati: sulla CON e sull'unità madre.

> **La fase, di suo, non conta.** La regola guarda il **periodo**: una USM che va da **2/3 a 2/4** — stesso periodo, cambia solo la fase — non genera niente. Se le tue unità sopravvivono di fase in fase dentro lo stesso periodo, spunta **«anche i salti di fase»** accanto al pulsante: allora contano anche quei salti, purché **entrambe** le fasi siano compilate. Un'unità che non si muove — stesso periodo e stessa fase — non è mai una continuità. La spunta parte **spenta**, e vale per l'anteprima e per la scrittura insieme.

### 6.2 Idempotenza

L'operazione è **idempotente**: rilanciarla non duplica le schede già presenti, ma aggiorna le `CON_<us>` esistenti se i dati dell'unità madre sono cambiati.

### 6.3 Anteprima (dry-run) e backup

Prima di scrivere viene mostrata un'**anteprima dry-run** con i conteggi: quante schede da **creare**, da **aggiornare**, **invariate** e quante **orfane**. Le modifiche vengono applicate **solo dopo conferma** (pulsante "Genera"). Al momento dell'applicazione viene eseguito automaticamente un **backup del database**.

Una scheda CON è **orfana** quando l'unità madre non attraversa più periodi (ad es. periodo iniziale e finale sono stati resi uguali). Di default le orfane vengono solo **segnalate**; una **casella di spunta** ("Rimuovi anche le CON orfane") consente di rimuoverle.

**Una continuità scritta a mano si riconosce.** Una scheda CON che nei suoi rapporti nomina una sola unità — `> 12`, o «Continuità successiva a 12» — è la continuità di quella unità, comunque si chiami: il generatore la **aggiorna** (arco di periodi, etichetta canonica) e il nome resta suo. Non ne nasce una seconda: la continuità è **una per unità**. Se esiste già anche la `CON_<us>` col nome canonico, vince quella e l'altra resta un'orfana da decidere a mano.

### 6.4 In export Extended Matrix

Le schede `CON_<us>` così generate compaiono nell'**em.json** dell'Extended Matrix come **elementi di continuità** (il GraphML in uscita è in pensione, §2.3).

---

## 7. Verifica paradossi temporali (stratigrafici)

Nel pannello **"Verifica rapporti"** (tab del dialog di import/export s3dgraphy), la verifica ora segnala anche i **paradossi temporali**: quando il periodo/fase assegnato a un'unità contraddice la stratigrafia osservata. La stratigrafia è il dato di riferimento, quindi le correzioni automatiche spostano i **periodi**, non i rapporti.

### 7.1 Cosa rileva
- **Inversione temporale**: due unità datate legate da un rapporto d'ordine (es. US5 «copre» US7) in cui l'unità più recente in stratigrafia risulta interamente più **antica** per periodo.
- **Contemporaneità incoerente**: unità dichiarate contemporanee (uguaglianza fisica / legame) ma con intervalli cronologici **disgiunti**.
- **Non valutabile**: rapporto d'ordine in cui almeno una delle due unità non ha un periodo databile (solo segnalato, nessuna correzione).

Nota sul confine: due periodi **adiacenti che si toccano** in un solo punto cronologico sono considerati sovrapposti → **non** sono un paradosso (beneficio del dubbio).

### 7.2 Correzione automatica e suggerimenti
- Quando un solo spostamento risolve il conflitto, la verifica propone di spostare l'unità **mono-periodo** in conflitto con la maggioranza dei vicini, scegliendo il periodo a spostamento minimo; per le contemporaneità con un'unità non databile copia il periodo del vicino datato.
- Nei casi ambigui — pareggio, unità **multi-periodo** (es. schede CON), nessun periodo valido — non corregge automaticamente: fornisce un **suggerimento «cosa + come»** (es. «Sposta US5 a un periodo ≥ 3, oppure US7 a un periodo ≤ 1, oppure verifica il rapporto»).

### 7.3 Anteprima e backup
- L'**anteprima** mostra le modifiche di periodo proposte prima di applicarle.
- Prima di scrivere i periodi viene eseguito un **auto-backup del database** (SQLite e PostgreSQL).
- Dopo l'applicazione, rilancia la verifica per controllare eventuali paradossi residui.

---

## 8. Verifica della cronologia (periodizzazione e schede)

Nello stesso pannello **"Verifica rapporti"** (tab del dialog di import/export s3dgraphy), dalla versione 5.13.64-alpha, la verifica trova e corregge anche i problemi di **cronologia** del sito selezionato. Il controllo dei paradossi temporali (sezione 7) confronta il periodo di un'unità con la stratigrafia; questo confronta la periodizzazione con se stessa e con le schede US che la copiano.

### 8.1 Cosa rileva

L'albero del pannello raggruppa i problemi per tipo. Accanto ai gruppi dei rapporti compaiono quattro gruppi nuovi:

| Gruppo | Che cosa segnala | Come viene trattato |
|--------|------------------|---------------------|
| **Fasi con intervalli sovrapposti** | Due righe della periodizzazione i cui intervalli di anni si intersecano | Manuale: il pannello propone di restringere gli intervalli solo se, dopo la restrizione, resta un intervallo utilizzabile |
| **Datazione della scheda disallineata** | Il campo `datazione` della scheda US dice una cosa diversa dalla `datazione_estesa` della sua periodizzazione | Automatico: la periodizzazione è la fonte, la scheda è la copia, quindi la copia viene riscritta dalla fonte. Un campo vuoto si compila allo stesso modo. Una US senza periodo viene saltata, perché non c'è nulla da cui copiare |
| **Periodizzazione con inizio dopo la fine** | `cron_iniziale` maggiore di `cron_finale` | Manuale: sono probabili date a.C. senza il segno meno — il pannello propone di riscrivere i due anni negativi (`-1650` invece di `1650`); se invece è un refuso, scambia i due valori a mano |
| **Fase senza anni** | Una fase i cui anni mancano o non sono leggibili | Solo segnalata: non c'è nulla da cui ereditarli |

Un esempio per le sovrapposizioni. Nel database di esempio ce ne sono due, e nessuna delle due ha una proposta: le due fasi hanno intervalli **identici**, e qualunque restrizione farebbe finire una fase prima del suo inizio. Il pannello si limita a dirlo; la decisione (accorpare le fasi, correggere gli anni, lasciare le cose come stanno) spetta all'archeologo.

### 8.2 Correzione automatica e suggerimenti

**Correzioni automatiche e proposte.** Le correzioni automatiche sono **già spuntate**; le proposte **non lo sono** e vengono applicate solo se si spunta la casella. Prima la regola era diversa: un problema la cui correzione richiedeva una decisione umana poteva solo essere letto. Ora ha una casella, lasciata vuota. Questo vale anche per le due categorie più vecchie dei rapporti che offrono un suggerimento, cioè la contraddizione diretta e il ciclo stratigrafico.

Per usare il pannello:

1. Selezionare nel pannello il **sito** da verificare. La verifica è **per sito**: guarda solo il sito scelto e corregge solo quello. In un database con dieci siti la cosa conta, perché gli stessi numeri di US esistono in tutti.
2. Leggere la **riga di riepilogo** sopra l'albero: dice quanti problemi ci sono, quanti sono correggibili in automatico e **quante sono le proposte da spuntare a mano**.
3. Aprire i gruppi e selezionare un problema per leggerne il dettaglio nel pannello di anteprima.
4. Controllare le caselle. Le correzioni automatiche sono già spuntate: togliere la spunta a quelle che non si vogliono applicare. Spuntare le proposte che si condividono.
5. Applicare le correzioni. Prima di scrivere qualsiasi cosa viene creato un **backup automatico** (copia del file SQLite oppure `pg_dump` per PostgreSQL in `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); il backup, che già esisteva per le correzioni dei campi periodo, ora copre anche quelle cronologiche.
6. Se il risultato non convince, premere **Annulla ultimo fix**: l'annullamento riporta indietro anche le correzioni scritte nella tabella della periodizzazione.

### 8.3 Anteprima e backup

**L'anteprima mostra la data calcolata.** Per ogni unità citata da un problema il pannello di anteprima riporta la sua data calcolata, in una riga come questa:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

La riga dice, nell'ordine, l'intervallo di anni, la regola che lo ha prodotto e il rapporto lungo il quale il vincolo è arrivato, con il nodo da cui proviene. Quando i due estremi dell'intervallo arrivano da strade diverse, ciascuno è etichettato (`inizio …` e `fine …`), così una data non viene mai attribuita al rapporto sbagliato. Oggi, in un database normale, ogni unità prende le sue date dal proprio periodo: la maggior parte delle righe dirà quindi `epoca`. Il senso della riga non è sorprendere, è permettere di vedere **da dove viene** una data.

---

## 9. Come leggere gli archi della matrice

Nel disegno della matrice alcune scelte possono sembrare strane, ma non sono errori:

- **Una freccia non passa mai sotto a un nodo.** Quando la colonna d'arrivo è occupata, la freccia entra nella casella **dal fianco**: è normale.
- **L'uguaglianza non è una sovrapposizione.** Un rapporto «Uguale a» o «Si lega a» mette le due unità sulla **stessa riga**, accostate, collegate da **due linee orizzontali** (il segno di uguale) **senza punta di freccia**.
- **Gli archi ridondanti non si disegnano.** Se la US 1 copre la 2 e la 2 copre la 3, la freccia da 1 a 3 non compare, perché non aggiunge niente. Dentro un **ciclo** invece gli archi restano tutti, perché un ciclo è un errore da vedere.
- **Le linee dicono che rapporto sono.** Grigia e piena: la sequenza (copre, riempie, si appoggia). **Punteggiata verde**: un taglio (`Taglia` / `Tagliato da`), qualunque sia la definizione stratigrafica e in qualunque lingua. **Spessa e nera**: la continuità — un rombo piccolo e nero, senza nome sopra (il nome compare passando col mouse), nella colonna della sua unità, così la linea è dritta. **Rossa**: una freccia che risale le fasce, cioè una contraddizione fra stratigrafia e cronologia; un taglio che risale è rosso **e** resta punteggiato.
- **I paradati non sono mai una linea piena.** Prendono colore e tratto dalle regole dell'Extended Matrix (`em_visual_rules.json`): bruno-rosso punteggiato «estratto da», arancio tratteggiato «provenienza del dato», oro tratteggiato «proprietà», grigio tratteggiato «connessione generica», rosso-pomodoro tratteggiato «combina» (nel file sarebbe pieno: è l'unica deroga, perché un arco verso un documento non deve sembrare una sovrapposizione).
- **I paradati stanno sotto la loro unità.** Proprietà, estrattori, combinatori e documenti di un'unità sono nel suo **gruppo**, la cornice tratteggiata sotto la sua casella, come i gruppi di paradati di EMStudio: una riga per ogni passo della catena (le proprietà, poi estrattori e combinatori, poi i documenti), e non contano nei livelli della stratigrafia. Un documento usato da più unità compare nel gruppo di ognuna, come in EMStudio, e le linee dei paradati restano dentro il gruppo. I paradati che nessuna unità raggiunge hanno una fascia loro, in fondo («Paradati senza unità»). L'intestazione del pannello li conta a parte: «114 unità · 739 paradati · 3 epoche · 90 rapporti» per TempluMare (dalla 5.13.126-alpha; prima i paradati entravano nei livelli come unità, e la matrice di un sito come TempluMare diventava un ammasso).
- **Il bordo bruno è una muratura.** Le USM — WSU, MSE, UEM, USZ, ΤΣΜ nelle altre lingue — hanno la stessa casella delle US, con il bordo bruno invece che rosso.

---

## 10. Narrativa con l'AI

Dalla versione **5.13.106-alpha** il pannello della matrice dentro QGIS (§2.2, «Vedi la matrice») ha due schede nella colonna di destra: **Unità** (*Units*) — la scheda dell'unità scelta, lo zoom sulla geometria e i media, come prima — e **Narrativa** (*Narrative*), nuova. La scheda Narrativa fa scrivere a un'AI la **storia del sito**, un capitolo per ogni epoca, e poi te la fa leggere, convalidare da una persona ed esportare in HTML, DOCX o PDF. Legge e scrive **lo stesso em.json** che apre EMStudio, nel formato della libreria s3dgraphy: la narrativa che vedi qui è quella che EMStudio mostra nella sua scheda *Narrative*.

> **Nessuna impostazione nuova.** La scheda non ha una finestra di configurazione: usa l'AI che hai già impostato altrove in pyArchInit (§10.2).

> **L'AI scrive bozze, non testi definitivi.** Ogni paragrafo scritto dal modello resta «bozza AI» finché una persona non lo convalida (§10.6), e nei documenti esportati porta il segno ⚠.

I nomi delle schede e dei pulsanti della scheda Narrativa esistono in italiano e in inglese: **sono in italiano se QGIS è in italiano, in inglese con qualsiasi altra lingua**. Qui trovi sempre tutti e due. Le voci di menu e le finestre di dialogo del plugin (come «Vedi la matrice…» o i tre bottoni di §10.9) sono invece solo in italiano.

### 10.1 Aprire la scheda Narrativa

1. Apri il menu **Plugins → pyArchInit - Archaeological GIS Tools** e scegli la voce **Extended Matrix → Vedi la matrice…**
2. Scegli il **sito**.
3. pyArchInit esporta il sito dal database in `<home>/pyarchinit_EM_folder/<sito>.em.json` — `<home>` è `~/pyarchinit_5`, o la cartella indicata dalla variabile d'ambiente `PYARCHINIT_HOME` — e apre il pannello **«Matrice — `<sito>`»**, agganciato a destra della finestra di QGIS. Il nome del file è quello del sito, con i caratteri speciali sostituiti da «_» (ad esempio «Scavo 1» diventa `Scavo_1.em.json`).
4. Nella colonna di destra del pannello clicca la scheda **Narrativa**.

<!-- IMMAGINE: Screenshot del menu Plugins → pyArchInit - Archaeological GIS Tools con la voce «Extended Matrix → Vedi la matrice…» -->
![Menu Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: La voce «Extended Matrix → Vedi la matrice…» nel menu del plugin*

<!-- IMMAGINE: Screenshot del pannello della matrice agganciato a destra, con le schede Unità e Narrativa -->
![Pannello con due schede](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 2: Il pannello della matrice con le schede Unità e Narrativa*

Il file è **uno per sito e resta sul disco**: non sta più in una cartella temporanea. È il file che apre EMStudio ed è lì che la narrativa viene scritta. Ogni volta che scegli «Vedi la matrice…» il sito viene **esportato di nuovo dal database** e il file viene riscritto; la narrativa già presente si conserva (§10.8).

Alla scheda si arriva anche da altre due parti:

- dalla voce **Extended Matrix → Esporta sito in em.json…**, che alla fine offre il bottone «Narrativa con l'AI» (§10.9);
- dal pulsante **Vedi la matrice** della finestra «Esporta Extended Matrix» della scheda US (§2.2): apre lo stesso pannello sul file appena esportato, nella cartella che hai scelto.

### 10.2 Quale AI viene usata

In alto, nella scheda Narrativa, una riga dice quale AI userà: **«Modello: `<modello>` (`<da dove>`)»**, seguita dal promemoria su EMStudio. Se non ne trova nessuna scrive **«Nessuna AI impostata: impostala nella scheda US con «Report» (Provider AI) o con «Query AI Database».»** e i pulsanti **Genera con l'AI** e **Rigenera capitolo** restano spenti.

La scheda legge le impostazioni AI **già salvate** dalle altre finestre di pyArchInit, in quest'ordine, e usa la **prima** che ha un modello e — per i provider in rete — la chiave API:

| # | Dove è impostata | Come la chiama la scheda (it / en) |
|---|------------------|-------------------------------------|
| 1 | Scheda US, pulsante «Report» → finestra «Generatore di Report», gruppo «Provider AI» | Generatore di Report della scheda US / Report generator of the US form |
| 2 | Scheda US, pulsante «Query AI Database» | Query AI Database / Query AI Database |
| 3 | Finestra palimpsestr, pulsante «Report AI (analisi descrittiva)…», selettore «Provider AI» | Relazione Palimpsest / Palimpsest report |
| 4 | Finestra «Generazione SQL con AI» (testo in SQL: vedi il tutorial 30) | Testo in SQL / Text to SQL |

I provider sono quelli dei selettori «Provider AI»: **OpenAI** e **Anthropic (Claude)** in rete, con la chiave API da scrivere nel campo «API key»; **Ollama** e **LM Studio** sul tuo computer, senza chiave. Il selettore salva la scelta appena la cambi. Se vuoi un altro modello, cambialo nella finestra che la scheda indica tra parentesi (o in una che viene prima nell'elenco). La scheda rilegge le impostazioni **quando il pannello si apre**: dopo averle cambiate, riapri la matrice.

### 10.3 La scheda Narrativa

```
┌─ Unità ─┬─ Narrativa ──────────────────────────────────────────────────────────────────┐
│ Modello: <modello> (<da dove>) · Se EMStudio ha il file                                │
│ aperto, chiudilo prima: chi scrive per ultimo vince.                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Presentazione — da scrivere                                                            │
│ Inizi XV secolo — bozza AI                                                             │
│ XV secolo — convalidato                                                                │
│ Età moderna — bozza AI, troncato                                                       │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Il testo del capitolo scelto, con le unità citate per nome.                            │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Capitolo 3 di 9 · XV secolo  *                                                         │
│ Lingua della prosa: [Italiano ▾]                                                       │
│ [Genera con l'AI]  [Rigenera capitolo]  [Convalida…]                                   │
│ [Prepara i capitoli]  [Scegli i media]  [Mostra sulla mappa]  [Esporta…]               │
│ [Apri in EMStudio]  [Annulla]*                                                         │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

\* La riga di avanzamento e il pulsante «Annulla» si vedono solo mentre l'AI sta scrivendo. In questo schema le righe dell'elenco sono quelle del sito di esempio.

<!-- IMMAGINE: Screenshot della scheda Narrativa con l'elenco dei capitoli, il testo del capitolo scelto e i sette pulsanti -->
![Scheda Narrativa](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 3: La scheda Narrativa*

Dall'alto in basso:

- **la riga di stato**: il modello in uso (§10.2) e il promemoria *«Se EMStudio ha il file aperto, chiudilo prima: chi scrive per ultimo vince.»*;
- **l'elenco dei capitoli**, una riga per capitolo: *Titolo — stato*. Un file di una versione precedente, diviso per saggio, mostra tutti i grafi: ogni riga è preceduta dal nome del grafo tra parentesi quadre, ad esempio `[Saggio A] XV secolo — bozza AI`;
- **il testo del capitolo scelto**: la prosa, con le unità citate per nome — i nomi sono **link**: un clic mostra l'unità sulla mappa (§10.10); sotto il paragrafo in cui un'unità è nominata la prima volta compaiono fino a due sue foto (§10.11). Se il capitolo non ha ancora prosa vedi il suo segnaposto «[da scrivere: …]»;
- **la riga di avanzamento**, solo durante la generazione: «Capitolo 3 di 9 · XV secolo»;
- **la lingua della prosa** (dalla 5.13.128-alpha): la lingua in cui l'AI scrive i capitoli e in cui nascono i titoli dei capitoli nuovi (§10.4, «La lingua»);
- **i pulsanti**, in due righe.

L'esito di ogni operazione compare nella barra dei messaggi di QGIS, con il titolo «Narrativa».

Quando il file **non ha ancora una narrativa** l'elenco è vuoto e un testo dice: *«Nessuna narrativa nel file: “Prepara i capitoli” crea lo scheletro (N capitoli fra epoche e attività), “Genera con l'AI” lo scrive.»*

#### Gli stati di un capitolo

| Stato (it / en) | Che cosa significa |
|-----------------|--------------------|
| **da scrivere** / to be written | Il capitolo ha solo il segnaposto «[da scrivere: …]». |
| **bozza AI** / AI draft | C'è prosa scritta dal modello che nessuna persona ha convalidato. Basta un paragrafo: se il capitolo ne ha anche solo uno non convalidato, lo stato è questo, anche se c'è altra prosa. |
| **convalidato** / endorsed | Tutta la prosa dell'AI è stata convalidata da una persona. |
| **scritto** / written | Prosa scritta da una persona (in EMStudio). |
| **troncato** / truncated | Si aggiunge allo stato (ad esempio «bozza AI, troncato»): il modello si è fermato perché ha raggiunto il limite di lunghezza, e il testo finisce a metà. |

#### I pulsanti

| Pulsante (it) | In inglese | Che cosa fa |
|---------------|------------|-------------|
| **Genera con l'AI** | Generate with AI | Scrive, **uno alla volta**, tutti i capitoli ancora «da scrivere» — per prima la **Presentazione**, poi quelli di epoca (e di attività); quelli già scritti non si toccano. Se la narrativa non c'è, crea prima lo scheletro. Mostra l'avanzamento e il pulsante **Annulla**. Acceso solo con un file aperto e un'AI impostata. Su una narrativa che il file porta di suo — per esempio quella di TempluMare, scritta in EMStudio — non aggiunge capitoli: scrive solo quelli di pyArchInit ancora da scrivere, se li hai aggiunti con «Prepara i capitoli» (fino alla 5.13.127-alpha li aggiungeva da sé). |
| **Rigenera capitolo** | Regenerate chapter | Riscrive **il capitolo scelto** nell'elenco: la bozza AI non convalidata viene sostituita — ma solo quando il modello ha risposto: se la chiamata fallisce, la bozza di prima resta — e i blocchi già convalidati restano. Si accende scegliendo la Presentazione o un capitolo di epoca o di attività, con un'AI impostata; per «Dove si trova» resta spento. La Presentazione è quella di pyArchInit: il primo capitolo di una narrativa del file (l'introduzione di TempluMare) non lo è, e non si rigenera. |
| **Convalida…** | Endorse… | Apre un menu con «Questo capitolo» e «Tutti i capitoli», poi chiede chi convalida (§10.6). Acceso quando c'è una narrativa. |
| **Prepara i capitoli** | Prepare the chapters | Crea **solo lo scheletro** dei capitoli, senza AI: serve anche se non c'è nessuna AI impostata, per scrivere a mano in EMStudio. Non tocca la prosa già scritta e aggiunge i capitoli delle epoche nuove. Esito: «Capitoli preparati: N.» Se il file porta una narrativa sua, prima chiede: **Solo i capitoli del file** (non si aggiunge niente: «Restano i N capitoli del file: nessun capitolo aggiunto.»), **Aggiungi quelli di pyArchInit** (la Presentazione, Dove si trova, un capitolo per ogni epoca e per ogni attività che non ne ha uno, in coda ai capitoli del file, che restano intatti) o **Annulla**. Lo chiede ogni volta, finché non li aggiungi. I titoli dei capitoli nuovi sono nella **lingua della prosa**. |
| **Scegli i media** | Choose the media | Dalla 5.13.130-alpha. Per ogni capitolo sceglie, fra i media delle unità di cui parla — i modelli 3D, le immagini e i video delle schede, e quelli della loro catena di prova (l'immagine dell'estrattore, la tavola del documento); i PDF no, sono fonti —, quelli da mettere **dentro il testo**, dopo il paragrafo che ne parla, con una didascalia nella **lingua della prosa**. Con un'AI impostata sceglie l'AI, con **temperatura zero**, solo fra quei media, al massimo quattro per capitolo; senza AI, o se la risposta non si legge, la scelta è automatica: un media per unità, nell'ordine in cui il testo le nomina, al massimo tre. La scelta **resta nel file** (nei dati della narrativa) e l'esportazione HTML la usa sempre uguale, finché non premi di nuovo il pulsante. Serve il database del progetto con i media delle schede (per TempluMare, quelli importati dall'em.json). Esito: «Media scelti: N in M capitoli (con l'AI)». Acceso quando c'è una narrativa. |
| **Mostra sulla mappa** | Show on the map | Seleziona e inquadra sulla mappa, **tutte insieme**, le unità di cui parla il capitolo scelto (§10.10): quelle citate nella prosa o, se il capitolo non è ancora scritto, tutte quelle della sua fascia. Acceso solo se almeno una delle unità di cui parla il capitolo scelto è una riga della scheda US. |
| **Esporta…** | Export… | Salva la narrativa in HTML (con la mappa interattiva del sito, §10.7), DOCX o PDF stampabile (§10.7), con le foto delle unità citate quando ci sono (§10.11). Acceso quando c'è una narrativa. |
| **Apri in EMStudio** | Open in EMStudio | Apre l'em.json in EMStudio. Se EMStudio non c'è, la barra dei messaggi rimanda alla voce di menu **Extended Matrix → Installa EMStudio…** |
| **Annulla** | Cancel | Compare solo durante la generazione: l'AI si ferma **dopo il capitolo in corso** e quanto è stato scritto viene salvato. |

Durante la generazione tutti i pulsanti sono spenti tranne **Annulla**.

### 10.4 Che cosa scrive l'AI

**Quali capitoli.** Lo scheletro è quello della libreria s3dgraphy (il modello «site_story»):

- Dalla **5.13.110-alpha** la **Presentazione** è un capitolo canonico che l'AI scrive come gli altri, da un briefing del sito intero (vedi «Il briefing della Presentazione» più sotto); prima restava un segnaposto. **Dove si trova** è l'altro capitolo canonico e resta un segnaposto «[da scrivere: …]» da scrivere a mano in EMStudio: nasce dalla posizione del sito e la mappa ce la mette la libreria. Esiste solo se il grafo porta una posizione geografica. L'AI non lo genera.
- **Un capitolo per ogni epoca** (periodo/fase) che ha unità, dalla più antica alla più recente. Il titolo è il nome dell'epoca, cioè la «Datazione estesa» della periodizzazione; se manca, ne esce un nome generico come «Period 8 Phase 1»: compilala nella scheda Periodizzazione per avere titoli leggibili. Un'unità compare nel capitolo dell'epoca in cui nasce e in quelli delle epoche in cui sopravvive.
- **Un capitolo per ogni attività**, se il grafo contiene gruppi di attività. Un sito esportato dal database di norma non ne ha — il campo Attività della scheda US viaggia come proprietà dell'unità — e allora i capitoli sono quelli di epoca.

**La narrativa del file.** Un em.json di EMStudio può arrivare con una narrativa sua: TempluMare porta 13 capitoli di Emanuel Demetrescu, in inglese, scritti da lui. pyArchInit la tiene com'è: i suoi capitoli non si toccano, e quelli del modello «site_story» si aggiungono solo con **Prepara i capitoli** → **Aggiungi quelli di pyArchInit** (fino alla 5.13.127-alpha li aggiungevano anche «Genera con l'AI» e ogni riesportazione del sito). Un capitolo del file ancorato a un'attività vale come capitolo di quell'attività: in TempluMare «Virtual Activity 2: colonnade» è ancorato all'attività VAct.03 e «Virtual Activity 4: Temple» a VAct.01, quindi VAct.02 e VAct.04 restano senza capitolo e pyArchInit ne aggiunge uno («VAct.02 Columnade», «VAct.04 Temple»): sono le àncore del file da correggere.

**Che cosa riceve il modello.** Per ogni capitolo di epoca o di attività un *briefing* con, per ciascuna unità: nome, tipo e descrizione; i campi compilati della scheda US (definizione stratigrafica e interpretativa, interpretazione, periodo e fase, datazione, attività, struttura, saggio, ambiente, settore, area); le epoche; **i rapporti stratigrafici** con le altre unità (copre, taglia, riempie, si appoggia, uguale a…) con i nomi; e, se ci sono, le fonti documentarie collegate. Le unità sono elencate **dalla più antica alla più recente**, seguendo i rapporti. Oltre **80 unità** per capitolo il briefing si taglia alle prime 80. Ha anche un tetto di lunghezza (circa 25.000 caratteri): oltre, si accorciano i testi lunghi delle schede, si tolgono i rapporti ripetuti e le catene di prova e, se ancora non basta, si omettono le unità più recenti. In entrambi i casi il modello è informato di quante unità mancano.

**Le regole.** Il modello riceve le cinque regole della libreria: scrivere solo ciò che il contesto sostiene (niente date, materiali, funzioni o eventi inventati); mantenere l'incertezza (un'unità virtuale è un'ipotesi, non un fatto); non citare fonti che non ci sono; scrivere prosa continua, senza elenchi né titoli; dire apertamente che il contesto è troppo povero, quando lo è. Chiede da uno a tre paragrafi.

**Il briefing della Presentazione.** La Presentazione non ha unità proprie: il modello riceve un briefing del **sito intero**, preso dal grafo e non dal database, con il nome del sito; la catena dei toponimi (nazione → regione → provincia → comune); i luoghi della scheda US (aree, settori, saggi, ambienti); le epoche dalla più antica alla più recente, ciascuna con quante unità vi sono presenti (una stessa unità può stare in più epoche, quindi la somma può superare il totale); quante unità ci sono e di che tipo, e quanti rapporti stratigrafici; i documenti; le persone nominate nelle schede US; i titoli dei capitoli del racconto. Le istruzioni sono quelle della Presentazione, non le cinque regole qui sopra: chiedono da due a quattro paragrafi che dicano che cos'è il sito e dove si trova, quali epoche copre la storia, come si legge il racconto (un capitolo per epoca e per attività, con le unità citate per nome e le bozze segnate come tali finché una persona non le convalida) e su quali fonti si appoggia; di usare solo il briefing, senza inventare date o fatti, e di lasciare fuori un dato che sembra strano invece di commentarlo. La prosa va **in testa** al capitolo; le schede delle fonti (i documenti) restano dopo di lei e i segnaposto «[da scrivere: presentazione di …]» e «[da scrivere: come si legge questo racconto…]» spariscono.

**La lingua.** Dalla 5.13.128-alpha la sceglie chi scrive, nella tendina **Lingua della prosa** della scheda: parte dalla lingua della narrativa del file, se ne ha una (TempluMare: inglese), altrimenti da quella di QGIS. Vale per la prosa che l'AI scrive con «Genera con l'AI» e «Rigenera capitolo» e per i titoli dei capitoli nuovi che «Prepara i capitoli» aggiunge («Presentazione», «Dove si trova»); i capitoli già scritti non si traducono, e lo stesso capitolo fisso in un'altra lingua non si aggiunge una seconda volta. Le istruzioni del modello esistono in italiano e in inglese: per le altre lingue (tedesco, francese, spagnolo, catalano, portoghese, rumeno, greco, arabo) il modello riceve quelle inglesi con la richiesta di scrivere in quella lingua. Fino alla 5.13.127-alpha la prosa nasceva sempre nella lingua della narrativa: con TempluMare, in inglese anche con QGIS in italiano.

**Come viene salvata.** Nel formato della libreria, lo stesso che legge EMStudio: un nodo narrativa (`NarrativeNode`) con i capitoli; ogni paragrafo scritto dal modello è un blocco «bozza AI» attribuito all'**autore AI** di quel modello; il **prompt** usato è registrato come estrattore collegato alle fonti, così si può risalire a che cosa è stato chiesto. Le unità citate nel testo sono **menzioni** (`[[nome]]`): nel file restano legate al nodo dell'unità, e nella scheda e negli export compaiono con il suo nome. Una menzione che non corrisponde a nessuna unità del grafo viene ridotta a semplici parole, senza parentesi.

**Costi e tempi.** Il modello viene chiamato **una volta per capitolo**, Presentazione compresa. Con un provider in rete ogni chiamata ha un costo e un tempo di attesa (nelle prove con un modello in rete, qualche decina di secondi per capitolo: un sito con una decina di epoche richiede alcuni minuti); con Ollama o LM Studio non si paga nulla, ma i tempi dipendono dal computer.

### 10.5 Passo per passo

1. Apri la matrice del sito (§10.1) e clicca la scheda **Narrativa**. Controlla in alto **quale modello** userà.
2. **Chiudi EMStudio** se ha il file aperto: pyArchInit e EMStudio scrivono lo stesso file e chi scrive per ultimo vince.
3. Facoltativo: **Prepara i capitoli** per vedere lo scheletro, senza AI.
4. Clicca **Genera con l'AI**. Guarda l'avanzamento: la Presentazione, se è ancora «da scrivere», va per prima («Capitolo 1 di 9 · Presentazione»), poi i capitoli di epoca («Capitolo 3 di 9 · …»); puoi continuare a usare QGIS. Alla fine la barra dei messaggi dice, ad esempio, *«7 capitoli generati, 1 falliti: Età moderna — …»* (con *«(interrotto)»* se hai annullato) e l'elenco si ricarica: i capitoli scritti sono «bozza AI».
5. **Leggi**: scegli un capitolo dopo l'altro e leggi il testo sotto l'elenco. Controllalo sulla stratigrafia: è una bozza costruita dai dati della scheda. Per vedere dove stanno le unità di cui parla, clicca i loro nomi o usa **Mostra sulla mappa** (§10.10).
6. Se un capitolo non convince, scegli la sua riga e clicca **Rigenera capitolo**. La nuova bozza **sostituisce** quella precedente non convalidata: se vuoi conservare la versione di prima, esportala prima. Se un capitolo è «troncato», rigeneralo **prima** di convalidare.
7. Quando un capitolo è a posto, clicca **Convalida…** (§10.6).
8. **Esporta…** in HTML, DOCX o PDF (§10.7), oppure **Apri in EMStudio** per scrivere a mano «Dove si trova» e rifinire il resto.
9. In seguito puoi riaprire la matrice: la narrativa resta (§10.8).

<!-- IMMAGINE: Screenshot della generazione in corso: riga di avanzamento «Capitolo 3 di 9 · …» e pulsante Annulla -->
![Generazione in corso](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 4: Generazione in corso, con l'avanzamento e il pulsante Annulla*

Un capitolo che fallisce non ferma gli altri: il riepilogo dice quali. Per riprovare basta un altro clic su **Genera con l'AI**, che scrive solo i capitoli ancora «da scrivere».

### 10.6 Convalidare: chi firma

Convalidare vuol dire che una **persona** si assume la responsabilità del testo scritto dal modello. Non avviene mai da solo: né generando, né salvando.

1. Clicca **Convalida…**. Si apre un piccolo menu: **«Questo capitolo»** — acceso solo se il capitolo scelto è in «bozza AI» — oppure **«Tutti i capitoli»**, cioè tutte le bozze AI non ancora convalidate, in tutti i grafi del file. La Presentazione si convalida come ogni altro capitolo: sceglila nell'elenco e «Questo capitolo» la firma da sola.
2. Una finestra chiede **«Chi convalida? Scegli un autore o scrivi un nome nuovo.»** L'elenco contiene gli **autori umani già nel grafo** — le persone nominate nella scheda US come schedatore, direttore US e responsabile US — e puoi scrivere un nome nuovo, che diventa un nuovo autore del grafo.
3. La barra dei messaggi dice **«N blocchi convalidati da `<nome>`.»**, oppure «Niente da convalidare.» Il file viene salvato.

<!-- IMMAGINE: Screenshot del menu Convalida… («Questo capitolo» / «Tutti i capitoli») e della finestra con la scelta dell'autore -->
![Convalida](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 5: Convalida: il menu e la scelta dell'autore*

I blocchi passano da «bozza AI» a «convalidato». Nel documento esportato la persona compare tra i responsabili («a cura di») e il modello come assistente («con l'assistenza di»), e i paragrafi convalidati non portano più il segno ⚠. Rigenerare non cancella i blocchi convalidati: la firma è un atto, non si perde riscrivendo.

### 10.7 Esportare in HTML, DOCX o PDF

Clicca **Esporta…**: si apre la finestra di salvataggio con tre formati: «Pagina HTML» (`.html`), «Documento Word» (`.docx`) e «PDF stampabile» (`.pdf`). Il nome proposto è `<sito>_narrativa`, senza estensione, nella cartella dell'em.json: l'estensione la mette il formato scelto nel filtro della finestra; un'estensione scritta a mano (`.html`, `.docx` o `.pdf`) vince sul filtro. La barra dei messaggi conferma: «Narrativa esportata in `<percorso>`».

Il documento contiene:

- il titolo della narrativa (ad esempio «Scavo archeologico — la storia del sito»), i responsabili («a cura di») e il modello come assistente («con l'assistenza di»);
- **l'indice** (dalla 5.13.129-alpha), dopo il titolo: i capitoli — raggruppati per parte quando i titoli la dicono, come «Rilievo e analisi — Introduction» —, sotto ciascuno i suoi sottotitoli, e per ultime le Fonti. Nell'HTML ogni voce porta al capitolo; nel PDF l'indice ha i numeri di pagina e i capitoli sono anche segnalibri del PDF; nel Word è un indice vero (un campo), con i titoli già scritti, che Word aggiorna con i numeri di pagina all'apertura del file (rispondi «Sì» quando chiede di aggiornare i campi; in LibreOffice: tasto destro sull'indice → Aggiorna);
- per ogni capitolo la prosa in testa, con le unità citate col loro nome, poi l'elenco delle unità del capitolo; per le unità citate che hanno foto, al posto della loro riga c'è una striscia di foto (§10.11);
- i **sottotitoli** scritti nella prosa con «### » (TempluMare ne porta dodici, da «Past researches» in poi) diventano titoli, nell'HTML, nel Word e nel PDF, e il corsivo scritto «\*…\*» è corsivo anche nel Word e nel PDF (dalla 5.13.129-alpha; prima si stampavano i segni);
- in fondo a ogni capitolo la riga **Fonti del capitolo** (dalla 5.13.129-alpha): i documenti su cui poggiano le unità di cui il capitolo parla — si seguono i paradati: unità → proprietà → estrattore (o combinatore) → documento — e quelli che il capitolo cita da sé. Nell'HTML ogni fonte è un **hotspot**: passandoci sopra col mouse compare una scheda con l'anteprima (la prima pagina del PDF o l'immagine), il tipo e la descrizione; cliccandoci si apre a destra un pannello con il file — il PDF si legge lì, l'immagine si vede intera —, il link «Apri il file», il percorso dell'originale e le **letture** che ne vengono (unità — proprietà, con l'estrattore). Esc o la × chiudono il pannello. Il file entra nella pagina se pesa fino a 2 MB (25 MB in tutto); oltre, scheda e pannello mostrano l'anteprima e il link all'originale, che si apre sul computer che ha esportato la pagina. I file si trovano come quelli della scheda: i media della riga del documento, l'originale o la sua copia nella cartella delle ridotte; senza database collegato le fonti hanno titolo, descrizione e letture ma non i file. Nel Word e nel PDF la riga elenca le fonti con la loro descrizione;
- **i media scelti** (dalla 5.13.130-alpha, nell'HTML) con **Scegli i media**: ognuno dopo il suo paragrafo, con la didascalia e sotto l'unità e il nome del file. Sono hotspot come le fonti: passandoci sopra la scheda, cliccandoci il pannello a destra — l'immagine intera, il video con il suo lettore, e per un **modello 3D** (GLB) il **visore interattivo**: si gira col mouse o col dito e si avvicina con la rotella. Il visore (model-viewer di Google) si carica da internet la prima volta che lo apri: senza rete resta la vista del modello e il file si apre con «Apri il file». Le viste grandi dei modelli si disegnano all'esportazione, in un processo a parte (qualche secondo in più); i modelli GLB e i video entrano nella pagina fino a 15 MB l'uno e 60 MB in tutto. Nel Word e nel PDF restano le strisce di foto delle unità citate (§10.11);
- **le unità del capitolo** (dalla 5.13.130-alpha, nell'HTML): al posto delle schede in fila della libreria — unità, paradati, documenti e strisce di foto, nel capitolo «II A.D.» di TempluMare 367 note una sotto l'altra, i paradati senza dire di quale unità — un blocco **Unità del capitolo** («104 unità, 339 paradati»), con una riga per unità — nome, tipo, descrizione — che si apre sulla tabella dei suoi paradati: proprietà, valore e da dove viene, un documento per volta con i suoi estrattori, il documento come hotspot; e sulla foto o la vista del modello dell'unità, se c'è. I documenti restano nella riga delle fonti del capitolo;
- **la mappa del sito** (dalla 5.13.115-alpha, solo nell'HTML), in un riquadro fisso: a destra sugli schermi larghi, in cima sul telefono. Con la mappa la pagina si allarga (dalla 5.13.116-alpha) e il testo tiene una colonna leggibile. Da ferma mostra tutte le unità del grafo in grigio chiaro; cliccando il nome di un'unità nel testo mostra **solo le unità del periodo di quel capitolo** come contorni con il numero sopra, la cliccata **colorata**, e inquadra il gruppo; cliccando il titolo di un capitolo lo stesso, senza l'unità colorata. La riga sotto la mappa dice il periodo e quante unità; «tutto il sito» torna alla vista intera. Le geometrie vengono dalle viste US e USM del database del progetto al momento dell'export (sito del grafo, unità legate per area e numero): un'unità citata ma senza disegno ha il link e niente sulla mappa; senza database collegato il documento non ha la mappa;
- in fondo la sezione **Fonti**: i documenti su cui si appoggia il racconto e la voce «Prompt», che richiama il prompt registrato nel file. Dalla 5.13.129-alpha l'elenco ha anche le fonti dei capitoli, ciascuna con la sua descrizione, e nell'HTML sono hotspot come quelle dei capitoli; lo sono anche le schede «fonte» dentro i capitoli e i documenti citati nel testo.

Alcune cose da sapere:

- le **bozze non convalidate entrano**, ciascuna preceduta da «⚠︎ non validato da una persona», e l'intestazione dice quanti blocchi sono in questo stato. Per un documento senza segni, convalida prima (§10.6). Nell'HTML la bozza si legge come il resto del testo, con lo stesso carattere e lo stesso sfondo: sopra il paragrafo c'è la riga di avviso e a sinistra un filetto ambra. Nel Word e nel PDF l'avviso sta davanti al paragrafo (nel PDF su una riga sua, senza il segno ⚠, §10.11);
- entrano **tutti i capitoli**, anche quelli ancora «da scrivere»: il loro segnaposto «[da scrivere: …]» resta nel testo;
- la prosa sta **in testa** al capitolo, prima dell'elenco delle unità; in una narrativa scritta con una versione precedente può stare ancora in fondo, e si mette a posto riesportando il sito (§10.8) o con **Prepara i capitoli**;
- le figure che un autore ha previsto in EMStudio (ad esempio la matrice di un'epoca) non vengono disegnate dall'esportazione di pyArchInit: nel documento resta un segnaposto;
- l'HTML è un file solo e autosufficiente (anche le foto sono incorporate, e la mappa è un SVG dentro il file, senza librerie esterne: si apre anche sul telefono senza rete); il DOCX si apre con Word o LibreOffice e richiede il pacchetto `python-docx`, e il PDF la libreria ReportLab (§10.11): sono entrambi fra i requisiti del plugin; dalla 5.13.129-alpha l'HTML porta dentro di sé anche i file delle fonti, fino a 2 MB l'uno e 25 MB in tutto: con molti PDF la pagina pesa di più.

<!-- IMMAGINE: Screenshot del documento HTML esportato: un capitolo con una bozza preceduta da «⚠︎ non validato da una persona» -->
![Documento HTML esportato](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 6: Il documento HTML esportato, con una bozza non convalidata segnata*

### 10.8 Riesportare il sito: la narrativa resta

Riesportare il sito dal database — con **Vedi la matrice…**, con **Esporta sito in em.json…** o con la finestra «Esporta Extended Matrix» della scheda US — **conserva la narrativa** già presente nel file di destinazione: prosa, convalide, autore AI e prompt. Le epoche nate nel frattempo ricevono un capitolo «da scrivere». Un avviso lo dice: **«Narrativa conservata dal file precedente (N capitoli).»** Lo vedi nella barra dei messaggi con «Vedi la matrice…», nel riepilogo della finestra «Esporta Extended Matrix» e, con «Esporta sito in em.json…», nei dettagli della finestra finale.

**Un sito importato da un em.json** (§5) ha anche la narrativa del file importato, che la memoria dell'importazione rimette nell'esportazione. Dalla 5.13.128-alpha vince la più recente: se il file di lavoro è stato salvato dopo l'importazione — «Prepara i capitoli», «Genera con l'AI», «Convalida…», o EMStudio sullo stesso file — passa la sua, con l'avviso di sempre; se l'em.json è stato importato dopo, resta quello importato, e un avviso lo dice: *«Narrativa del file precedente non conservata: l'em.json importato il … è più recente, e vale la sua. Copia di sicurezza del file precedente in ….»* Fino alla 5.13.127-alpha vinceva sempre quella importata: i capitoli preparati e scritti nel pannello sparivano alla riesportazione successiva, con un avviso che dava la colpa, a torto, alla forma del file.

Le **altre modifiche** fatte al file in EMStudio — posizioni dei nodi, descrizioni riscritte — **non sopravvivono**, come prima: il file si rigenera dal database. Si conserva soltanto la narrativa.

Prima di riscrivere un file che porta una narrativa, pyArchInit ne fa una **copia di sicurezza** accanto: `<sito>.em.json.bak` (a ogni riesportazione sostituisce la copia precedente).

Se il file di prima era diviso per saggio (le versioni fino alla 5.13.108-alpha potevano esportare un grafo per saggio), alla prima riesportazione il file nuovo ha **un grafo solo** per tutto il sito: i grafi hanno nomi diversi e la narrativa **non può passare** nel file nuovo. Un avviso lo dice: *«La narrativa del file precedente (grafi: …) non è passata nel file nuovo (grafi: …): la forma del file è cambiata. Copia di sicurezza in …»*. Il testo non è perso: sta nella copia `.bak`, che però viene sostituita alla prossima riesportazione di un file con una narrativa — mettila al sicuro. Se ti serve la narrativa vecchia, apri quella copia (rinominandola in un file `.em.json` con un altro nome); altrimenti rigenera i capitoli nel file nuovo (§10.5). Dalla 5.13.109-alpha il file ha sempre un grafo solo e la narrativa passa da una riesportazione all'altra.

Se il file precedente non si legge (ad esempio un file rimasto a metà), l'esportazione va avanti lo stesso: il file illeggibile viene **rinominato** `<sito>.em.json.broken` e un avviso dice *«Il file precedente non si legge (…): la narrativa, se c'era, non è stata conservata.»*

> **La narrativa non è nel database di pyArchInit: vive solo nell'em.json.** Il backup del database non la copia. Copia ogni tanto la cartella `pyarchinit_EM_folder`.

### 10.9 Dalla voce «Esporta sito in em.json…»

La voce **Extended Matrix → Esporta sito in em.json…** scrive lo stesso file `<sito>.em.json` in `pyarchinit_EM_folder`. Alla fine mostra «Esportato `<percorso>`», con i conti di nodi, archi e avvisi (il testo degli avvisi è nei dettagli della finestra), e **tre bottoni**:

| Bottone | Che cosa fa |
|---------|-------------|
| **Apri in EMStudio** | Apre il file in EMStudio; se non è installato, offre di installarlo. |
| **Narrativa con l'AI** | Compare **solo se un'AI è impostata** (§10.2): apre il pannello della matrice già sulla scheda Narrativa. |
| **Chiudi** | Chiude la finestra. |

<!-- IMMAGINE: Screenshot della finestra finale di «Esporta sito in em.json…» con i tre bottoni -->
![Esporta sito in em.json: tre bottoni](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 7: La finestra finale di «Esporta sito in em.json…»*

### 10.10 Le unità sulla mappa

Dalla versione **5.13.108-alpha** la scheda Narrativa porta sulla **mappa di QGIS** le unità di cui parla il capitolo, in due modi:

- **Un'unità sola: clicca il suo nome.** Nel testo del capitolo scelto i nomi delle unità citate sono **link**: un clic seleziona quell'unità sul layer US caricato e inquadra la mappa su di lei, con un lampeggio. Non apre nulla.
- **Tutte insieme: «Mostra sulla mappa»** (*Show on the map*), nella seconda riga di pulsanti, tra «Prepara i capitoli» ed «Esporta…». Seleziona e inquadra insieme tutte le unità di cui parla il capitolo scelto: quelle citate nella prosa o, se la prosa non ne cita nessuna (per esempio perché il capitolo non è ancora scritto), tutte le unità della sua fascia (l'epoca). La selezione è una sola per layer — sostituisce quella che c'era — e l'inquadratura abbraccia tutte le geometrie trovate, che lampeggiano.

<!-- IMMAGINE: Screenshot di QGIS con le unità del capitolo selezionate sulla mappa e, in alto, la barra dei messaggi «Evidenziate 5 unità su 6 in «US view» (7 geometrie). Non disegnate: 1.US9.» -->
![Le unità del capitolo sulla mappa](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Figura 8: Le unità di cui parla il capitolo, selezionate sulla mappa, e la barra dei messaggi*

Serve un layer con le geometrie delle US già caricato nel progetto, per esempio la **vista US** di pyArchInit: la scheda lo cerca fra i layer caricati, come il pulsante «Zoom sulla geometria» della scheda Unità (tutorial 01), riconoscendo le unità dai campi `sito`, `area` e `us`. **Il progetto non viene modificato**: non si aggiunge nessun layer, cambiano solo la selezione e l'inquadratura della mappa. Dalla **5.13.110-alpha**, se più layer portano gli stessi campi — come la vista US (poligoni) e la vista delle quote (punti) —, la scheda prova prima la geometria più piena: poligoni, poi linee, poi punti; l'ordine dei layer nella legenda conta solo se tutto il resto è uguale. Vale anche per il pulsante «Zoom sulla geometria»: non serve più mettere la vista US in cima alla legenda.

La barra dei messaggi («Narrativa») dice che cosa è stato trovato, per esempio *«Evidenziate 5 unità su 6 in «US view» (7 geometrie). Non disegnate: 1.US9.»*. Tra virgolette c'è il layer in cui sono state trovate le unità, col nome che ha nel pannello dei layer di QGIS; un'unità può avere più di una geometria, quindi le geometrie possono essere più delle unità. Si cercano solo le unità che sono righe della scheda US: un documento o un nodo di continuità non ha geometria e non entra nel conteggio. Se le unità non disegnate sono più di cinque, i nomi si fermano ai primi cinque, seguiti da «…» e dal totale.

Un clic su un nome che non è una riga della scheda US non trova niente, e la barra lo dice. Se nessun layer caricato porta i campi per riconoscere le unità, il messaggio lo dice: carica la vista US (§10.13).

### 10.11 Le foto delle unità e il PDF

Dalla versione **5.13.108-alpha** la narrativa mostra anche le **foto** delle unità di cui parla — nel testo della scheda e negli export — e si salva anche in **PDF stampabile**.

**Nel testo del capitolo.** Sotto il paragrafo in cui un'unità è nominata la prima volta compaiono **fino a due anteprime** dei suoi media: sono le stesse della scheda Unità, lette dalla cartella delle anteprime del progetto, e sotto di loro, in piccolo, c'è il nome dell'unità e quello dei media. Se l'unità è nominata di nuovo nello stesso capitolo, le foto non si ripetono.

**Negli export.** In tutti e tre i formati, per ogni unità citata nella prosa che ha immagini sul disco, una **striscia con una o due foto affiancate** prende il posto della riga di testo dell'unità, con il nome dell'unità come didascalia: si usa la copia ridotta se c'è, altrimenti l'anteprima. Le unità non citate nella prosa restano una riga di testo. Le foto sono incorporate nel file: HTML e DOCX sono scritti dalla libreria s3dgraphy, il PDF da pyArchInit.

**Il PDF stampabile.** È un A4 scritto con ReportLab, nel font Cambria come gli altri PDF del plugin (se il file del font non è nella cartella `bin` di pyArchInit, usa Helvetica). Contiene il titolo, i responsabili («a cura di») e il modello come assistente («con l'assistenza di»); in testa, se ci sono bozze non convalidate, compare anche un avviso con il loro numero; poi tutti i capitoli, come negli altri formati, ciascuno con la prosa — le unità citate scritte per nome, e davanti a ogni paragrafo non convalidato una riga «non validato da una persona», senza il segno ⚠ — seguita dalle foto con la loro didascalia e dalle altre unità in piccolo; in fondo le fonti. A piè di pagina ci sono «Generato da pyArchInit il …» con la data e il numero di pagina.

<!-- IMMAGINE: Screenshot affiancati: il testo di un capitolo con le anteprime sotto la prima menzione di un'unità, e una pagina del PDF stampabile con la striscia di foto e la didascalia -->
![Foto delle unità nel testo e nel PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Figura 9: Le foto delle unità nel testo del capitolo e in una pagina del PDF*

**Che cosa serve.** Le foto non stanno nell'em.json: si leggono dal database del progetto e dalle sue cartelle. Servono quindi il database collegato (la matrice aperta dal progetto), i percorsi **Thumbnail path** e **Image resize** impostati nella configurazione (tutorial 01) e i file presenti sul disco; per il testo basta la cartella delle anteprime. Le immagini su un archivio remoto non si usano. Se manca qualcosa non c'è nessun messaggio: le foto semplicemente non compaiono, e l'export riesce lo stesso (§10.13).

### 10.12 Avvertenze

- **Chiudi EMStudio prima di generare o convalidare.** Se EMStudio ha il file aperto, chi scrive per ultimo vince.
- **Un'AI scrive solo da quello che trova nel grafo, e può sbagliare.** Le regole la tengono a freno, non la rendono infallibile: leggi ogni capitolo prima di convalidarlo.
- **Con un provider in rete i dati escono dal computer.** Il briefing di ogni capitolo (nomi, definizioni, descrizioni e rapporti delle unità) e quello della Presentazione (nome del sito, toponimi, luoghi, epoche, documenti e nomi delle persone nominate nelle schede US) vengono inviati al servizio scelto; con Ollama o LM Studio restano in locale.
- **Il file si scrive alla fine.** La generazione salva quando termina, anche se l'hai annullata: non chiudere QGIS mentre l'AI sta scrivendo. Il salvataggio è sicuro: il file viene scritto accanto, riletto e solo allora sostituisce il vero; se qualcosa va storto, **il file precedente resta com'era**.
- **Non riaprire la matrice mentre l'AI scrive.** La scheda resta sul file di prima e avvisa: *«Generazione in corso: aspetta che finisca, o premi Annulla, prima di cambiare file.»*
- **Il testo si modifica in EMStudio**, non in pyArchInit.
- La narrativa e i nodi che la reggono (autore AI, prompt) **non compaiono nel disegno della matrice**.

### 10.13 Risoluzione dei problemi

| Messaggio (it / en) | Causa | Rimedio |
|---------------------|-------|---------|
| «Nessuna AI impostata…» / “No AI configured…” | Nessuna delle quattro finestre di §10.2 ha un modello (e, per OpenAI e Anthropic, la chiave API). | Imposta provider e modello — e la chiave — in una di quelle finestre, poi **riapri la matrice**: la scheda rilegge le impostazioni solo all'apertura. Anche senza AI puoi preparare i capitoli, convalidare, esportare e aprire EMStudio. |
| «Nessuna narrativa nel file…» / “No narrative in the file…” | Il file non ha ancora una narrativa (è normale la prima volta). | Clicca **Prepara i capitoli** (scheletro) o **Genera con l'AI** (scheletro e prosa). Il numero N conta i capitoli di epoca e di attività che lo scheletro avrà (un'epoca senza unità non ne ha); il messaggio «Capitoli preparati» conta anche «Presentazione» ed, eventualmente, «Dove si trova». «Genera con l'AI» scrive anche la «Presentazione», che N non conta: l'avanzamento conta un capitolo in più. |
| «EMStudio non risulta installato…» / “EMStudio is not installed…” | Il programma non è stato trovato sul computer. | Usa la voce di menu **Extended Matrix → Installa EMStudio…** (la voce ha questo nome con qualsiasi lingua di QGIS). |
| «troncato» / “truncated” accanto allo stato | Il modello si è fermato al limite di lunghezza e il testo finisce a metà. | Prima di convalidare, **Rigenera capitolo**; se si ripete, completa il capitolo in EMStudio. |
| «N capitoli generati, M falliti: `<titolo>` — `<motivo>`» / “N chapters generated, M failed: …” | Il fornitore ha rifiutato la richiesta (chiave non valida, quota, modello non disponibile) o il server locale non risponde. «il modello non ha scritto niente» vuol dire che la risposta era vuota. | Rimuovi la causa e clicca di nuovo **Genera con l'AI**: scrive solo i capitoli rimasti «da scrivere». |
| «Il file precedente non si legge (…)» / “The previous file cannot be read (…)” | Alla riesportazione il file esistente non era un em.json leggibile. | L'esportazione è andata avanti: il file illeggibile è stato conservato accanto come `….broken` e la narrativa che conteneva, se c'era, non è passata nel file nuovo. Se ti serve, recuperala da quel file o da una copia di sicurezza. |
| «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» / “The previous file's narrative (graphs: …) did not travel into the new file…” | Il file di prima era diviso per saggio (versioni fino alla 5.13.108-alpha): i grafi hanno nomi diversi e la narrativa non può passare. | Il file di prima è nella copia `.bak`: apri quella se ti serve la narrativa vecchia, oppure rigenera i capitoli nel file nuovo. |
| «Non sono riuscito a scrivere … Il file precedente è intatto.» / “Could not write … The previous file is intact.” | Il salvataggio è fallito (disco pieno, file bloccato, permessi). | Rimedia e ripeti: i capitoli generati in quella sessione non erano stati salvati. |
| «DocX export needs python-docx — install the extra: …» (sempre in inglese) | Il pacchetto `python-docx` non è installato nel Python di QGIS: serve solo per il DOCX. | Installa `python-docx` (è fra i requisiti del plugin), oppure esporta in HTML, che non richiede niente. |
| «Nessuno dei layer caricati porta i campi per riconoscere le unità…» / “None of the loaded layers has the fields to recognise the units…” | Nel progetto aperto non c'è nessun layer che porti i campi `sito`, `area` e `us` delle unità (per esempio la vista US di pyArchInit): la scheda cerca solo fra i layer già caricati. | **Carica la vista US** di pyArchInit (o un layer con gli stessi campi) nel progetto e clicca di nuovo sul nome o su **Mostra sulla mappa**. La scheda non aggiunge layer da sola. Dalla 5.13.110-alpha non serve metterla in cima alla legenda: a parità di campi la scheda prova prima i poligoni (§10.10). Caricata dalla scheda US con uno stile scelto (finestra «Scelta Stile», tutorial 14), la vista US porta anche il numero dell'unità in un cerchio. Dalla 5.13.111-alpha anche la vista delle quote (punti), caricata dalla scheda US, porta la quota (due decimali) sopra il simbolo. Lo stile e le etichette della vista si impostano nella finestra «Stili delle viste» (tutorial 14); dalla 5.13.112-alpha un predefinito salvato lì comanda al caricamento. |
| Nessun messaggio: le foto non compaiono nel testo del capitolo né negli export | Le foto si leggono dal database del progetto e dalle sue cartelle, e qualcosa manca: il database non è collegato (la matrice è stata aperta senza), il percorso **Thumbnail path** non esiste su questo computer o è un archivio remoto, i file non ci sono sul disco, oppure l'unità non è una riga della scheda US o non ha media. | Controlla nella scheda **Unità**: se lì l'unità mostra le sue anteprime, le troverai anche qui. Altrimenti apri la matrice dal progetto, verifica **Thumbnail path** e **Image resize** nella configurazione (tutorial 01) e che i file ci siano sul computer: le immagini su un archivio remoto non entrano. L'export riesce comunque, senza foto. |

---

## Riferimenti

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
