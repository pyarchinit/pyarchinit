# Tutorial 36: Export Extended Matrix și Bridge s3dgraphy

## Introducere

Începând cu versiunea **5.2.0-alpha** PyArchInit integrează un **bridge bidirecțional** cu biblioteca **s3dgraphy** (modelul de date Extended Matrix al lui Emanuel Demetrescu). Bridge-ul permite:

- **Exportarea** diagramei stratigrafice ca Extended Matrix în **em.json**, formatul pe care îl deschide EMStudio (vechiul export GraphML este retras)
- **Re-importul** modificărilor făcute în yEd (mutarea UE între perioade/grupuri) actualizând baza de date SQL
- **Atașarea paradatelor** (Author / License / Embargo) la nivelul sitului
- **Gruparea** UE după dimensiune (struttura, area, attivita, settore, ambient, saggio, quad_par sau grupuri ad-hoc)

Tag curent: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Cerințe

- Bază de date SQLite (PostgreSQL încă nesuportată)
- **Migrarea Phase 1 node_uuid** aplicată automat la deschiderea bazei
- **yEd Graph Editor** pentru vizualizarea ieșirii (https://www.yworks.com/products/yed)

> ⚠️ Pentru baze pre-5.2.0-alpha migrarea poate necesita repornirea QGIS.

---

## 2. Export Extended Matrix (butonul verde)

### 2.1 Deschiderea dialogului

1. Deschide **Fișa UE** a sitului dorit
2. Click pe butonul verde **"Esporta Extended Matrix"** (sub tab-ul Rapporti)

### 2.2 Tab "Export"

Fereastra spune în partea de sus la ce servește fiecare format. Conține:

- **Formati** (Formate): **DOT (Graphviz) — matrice di Harris** și **em.json (Extended Matrix, per EMStudio)**, bifate din start, plus **Matrice per fasi** (matrice pe faze, analiză cronologică), opțională. GraphML nu se mai exportă: JSON-ul acestei ferestre **este em.json**, exact fișierul pe care îl produce meniul **Extended Matrix → Esporta sito in em.json…** — același proiector, aceeași simbologie.
- **Opzioni** (Opțiuni): **Controlla la sequenza stratigrafica e segnala i problemi** (verifică secvența stratigrafică și semnalează problemele). Este singura opțiune rămasă, și acum este citită cu adevărat: fără bifă, verificarea nu se face. Cele două casete vechi care vorbeau cu yEd (sugestii de auto-layout, culori pe perioadă) au plecat împreună cu exportul GraphML.
- **Extended Matrix**: patru butoane lângă export — **Apri in EMStudio** și **Vedi la matrice** (ambele se aprind după un export em.json reușit; al doilea desenează matricea în QGIS, fără EMStudio), **Consegna alla stanza…** și **Apri la stanza**. Sunt aceleași intrări din meniul pyArchInit, la îndemână.

La apăsarea pe **Esporta** se cere **dosarul de destinație**.

Autorii, licențele, embargourile și grupurile se gestionează în fereastra **"Manage paradata"** (§3).

### 2.2.1 Sondaje: un singur graf sau unul pe sondaj

Un grup de trei alegeri, in aceeasi fereastra, decide **cum se imparte
em.json** cand situl are mai multe sondaje:

- **Automat**: un singur graf daca situl are un sondaj, un graf pe
  sondaj daca are mai multe. Este alegerea de pornire.
- **Un singur graf pentru tot situl**: tot situl intr-un graf, ca pana
  acum.
- **Un graf pe sondaj**: **un singur fisier**, care duce in el un graf
  pentru fiecare sondaj, plus unul pentru unitatile care l-au lasat gol.
  Relatiile care **ies** din sondaj nu se pierd: rama in fisier ca
  legaturi intre grafuri (`graph.links`).

> **EMStudio 1.6.0 arata unul pe rand.** Fisierul este corect — cititorul
> bibliotecii reciteste toate grafurile, fara avertismente — dar
> EMStudio deschide graful declarat in `active_graph_id`, primul sondaj,
> si nu are un selector pentru celelalte. Matricea din QGIS, **Arata
> matricea**, le uneste pe toate si deseneaza tot situl. Masurat la
> 2026-10-12 pe situl de exemplu: 4 grafuri (52/49/56/51 noduri), 32 de
> legaturi intre sondaje, 51 de unitati in matricea unita.

Sondajul este campul **Saggio** din fisa US: unitatile care l-au lasat gol
ajung intr-un graf separat, in acelasi fisier.

### 2.3 Click pe "Esporta"

Fișierele care se nasc, în funcție de formatele bifate:
- `<sit>.em.json` — Extended Matrix, de deschis în EMStudio sau de livrat într-o cameră
- `Extended_Matrix_<sit>[_<area>].dot` — Graphviz DOT, pentru matricea Harris clasică
- `Extended_Matrix_<sit>[_<area>]_phased.json` — vizualizare per epocă

> **Locurile nu intra in em.json.** Situl, aria si sectorul raman in fisa fiecarei unitati, dar nu mai calatoresc ca noduri de grup cu muchiile lor: cat timp fisierul contine chiar si o singura muchie `is_in_location`, vederea **Matrix** din EMStudio ingramadeste toate unitatile in prima banda in loc sa le distribuie pe epoci (masurat la 2026-10-08 cu EMStudio 1.6.0-dev.26, prin bisectie pe cinci fisiere). Nu se pierde nicio informatie — doar un mod de a o reprezenta.

Rezumatul final listează fișierele și, pentru em.json, **câte noduri și câte muchii** au ieșit, cu eventualele avertismente.

> **GraphML nu se mai exportă**: matricea se privește și se validează în EMStudio, care citește em.json. Rândurile temporale (swimlane) ale vechiului GraphML au plecat cu el. GraphML supraviețuiește doar la **intrare**, pentru fișierele desenate în yEd (§5).

---

## 3. Dialog "Manage paradata" (4 tab-uri)

### 3.1 Acces
Click pe butonul **"Manage paradata"** în fișa UE (lângă butonul verde Export).

### 3.2 Cele 4 tab-uri

| Tab | Conținut | Fișier generat |
|---|---|---|
| **Authors** | Adaugă autori (nume + ORCID + rol) | `paradata_<sit>.graphml` |
| **Licenses** | Licență dataset (ex. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Date embargo + motiv | idem |
| **Groups** | Grupuri ad-hoc (nume + selecție UE membre) | `groups_<sit>.graphml` |

Fișierele se salvează lângă DB SQLite și sunt **versionabile în Git**.

---

## 4. Stil vizual per dimensiune (5.5.1-alpha + 5.6.0-alpha)

Fiecare dimensiune de grupare are o culoare distinctivă în GraphML:

| Dimensiune | Fill (50% transparență) | Border |
|---|---|---|
| `area` | roz pastel `#FFE0E680` | `#C84A5F` |
| `struttura` | portocaliu pastel `#FFE6CC80` | `#C66B33` |
| `attivita` | galben pastel `#FFF5CC80` | `#A89A33` |
| `settore` | verde pastel `#E6FFCC80` | `#6BC633` |
| `ambient` | aqua pastel `#CCFFE680` | `#33A86B` |
| `saggio` | azur pastel `#CCF5FF80` | `#3389A8` |
| `quad_par` | violet pastel `#E0CCFF80` | `#6633C6` |
| `adhoc` | gri pastel `#F5F5F580` | `#666666` |

Începând cu 5.6.0-alpha, elementele `LocationNodeGroup` se disting prin `kind`:

| `kind` | Fill (50% transparență) | Border |
|---|---|---|
| `toponym` | lavandă pastel `#E6E6FA80` | `#9370DB` |
| `study` | fildeș pastel `#FFFFE080` | `#888888` |
| `functional` | cyan pastel `#E0FFFF80` | `#008B8B` |

Alpha 50% lasă vizibile swimlane-urile epocilor în spatele dreptunghiului grupului.

### 4.1 Lanț toponim (5.6.0-alpha)

Câmpurile `site_table.{nazione, regione, provincia, comune}` sunt emise automat ca un lanț recursiv de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Nivelurile administrative goale sunt sărite fără a întrerupe lanțul. O deduplicare cross-sit garantează că aceeași `comune` prezentă în 2 situri devine **un singur nod partajat** în GraphML.

---

## 4.2 Apartenență multidimensională (5.6.0-alpha)

Începând cu 5.6.0-alpha o UE poate aparține **mai multor dimensiuni simultan** datorită modelului m:n cu flag-ul `is_primary`. Doar dimensiunea primară devine folderul yEd vizibil; celelalte apar ca **insigne inline** sub nodul UE și ca JSON în `<data key="s3d:other_locations">` pentru tool-urile downstream.

Exemplu: o UE cu `struttura=basilica` și `area=B` (primar `struttura`) produce:
- folder yEd "struttura: basilica" ca parent vizibil;
- sub nodul UE, o insignă inline `also: B (study), TestCity (toponym)`;
- în GraphML, atributul `s3d:other_locations` cu array JSON al apartenențelor secundare.

Dimensiunea primară urmează o ordine predefinită, cu `struttura` pe primul loc; `toponym` nu este niciodată primar.

---

## 5. Round-trip (tab Import)

> **Ce se poate importa**: tab-ul Import citește acum și **em.json** — cel de la EMStudio sau de la nodul StratiGraph — și alege cititorul după extensia fișierului; un `.graphml` de yEd rămâne acceptat pentru fișierele de dinainte. Procedura de mai jos, mutarea UE între grupuri, se referă la calea yEd/GraphML.

Pentru a modifica baza SQL mutând UE între grupuri în GraphML:

1. Deschide GraphML în **yEd**
2. Trage o UE într-un alt grup, salvează
3. Înapoi la dialog → tab **"Import"**
4. **Bifează** checkbox-ul *"Update SQL on import (struttura/area/...)"*
5. Încarcă GraphML modificat

Sistemul rulează o tranzacție atomică: la eșec, **rollback complet** (DB rămâne nealterată). Grupurile `adhoc` nu scriu niciodată SQL — actualizează doar `groups_<sit>.graphml`.

Începând cu 5.6.0-alpha walker-ul de import este **recursiv** și suportă foldere imbricate (de ex. lanț toponim `nazione > regione > provincia > comune > UE`). La detectarea ciclurilor în graful folderelor, este ridicată excepția `CycleDetectedError` și importul este abandonat cu rollback.

---

## 6. CLI (alternativă la dialog)

Pentru scripts / batch:

```bash
# Export
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Listează grupuri ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Adaugă autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = succes, 1 = eroare bridge, 2 = eroare argparse.

---

## 7. Rezolvarea problemelor

| Simptom | Cauză | Soluție |
|---|---|---|
| "no such column: node_uuid" | Migrarea Phase 1 neexecutată | Repornește QGIS, redeschide DB |
| GraphML gol | DB fără rapporti / filtru area prea strict | Verifică us_table.rapporti |
| "rapporti trebuie să fie TEXT" | Ai introdus un număr ca integer | Câmpurile UE/Area sunt **TEXT**, nu integer |
| Capitalizare greșită în rapporti | "copre" cu litere mici în DB | Folosește "Copre", "Coperto da" capitalizate |
| `DeprecationWarning` pe fișier 5.5.x | Fișier legacy `ActivityNodeGroup + group_kind` | Projector-ul îl promovează în memorie la `LocationNodeGroup`. Reexportă pentru a migra fișierul pe disc. |
| Rândurile swimlane-ului afișează un text foarte lung | Versiunile anterioare foloseau Descrizione din periodizare ca etichetă | Actualizează plugin-ul și reexportă, și/sau completează **Datazione estesa** cu un nume scurt |
| Epocile din swimlane sunt în ordine greșită (ex. Bronz deasupra Antichității târzii) | Rândurile sunt ordonate după **Cronologia Inițială**; datele î.Hr. introduse ca numere pozitive (1650 în loc de -1650) sunt ordonate ca d.Hr. | În Fișa de Periodizare introdu anii î.Hr. ca numere negative și reexportă. Rezumatul exportului afișează acum un avertisment „⚠️ Periodizzazione: ..." cu lista perioadelor de corectat |

---

## 8. Documentație tehnică

Pentru aprofundare arhitectură, decizii de design și roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over amânate:
- **AI08-F3**: euristici auto-layout (bin-packing sub-grupuri) — încă amânat
- **AI09**: TimeBranchNodeGroup mapping — viitor
- **Phase 3**: SyncEngine + REST API — viitor
- **Phase 4**: GraphDBBackend + SPARQL — viitor

Livrate:
- **AI07** (5.6.0-alpha, 2026-05-10): migrare `LocationNodeGroup` cu enum `kind` + lanț toponim + apartenențe multidimensionale
- **AI08-F1** (fuzionat în AI07): nesting ierarhic nativ via `is_primary`

---

## 5. yEd-aware Import — importul de graphml editate extern (5.8.x)

Începând cu **5.8.0-alpha** bridge-ul este **bidirecțional și pentru graphml-uri create direct în yEd** (adică fără să treci mai întâi printr-un export pyarchinit). Pyarchinit recunoaște automat graphml-urile „yEd-raw" — cele care nu au data keys `pyarchinit.*` — și le importă printr-un dispatch dedicat care mapează prefixul label-ului nodului → tip stratigrafic, recunoaște rândurile de TableNode ca perioade, parcurge group folders ca dimensiuni arheologice și lasă utilizatorul să aleagă o politică pentru edges care ating folders.

### 5.1 Rollout în 6 etape

| Etapă | Tag | Ce adaugă |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` cu 13 valori (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate din rândurile de TableNode) + `yed_group_walker.py` (FolderCandidate cu auto-dimension din prefixul label-ului: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orchestrator `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + sentinel `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` cu 5 pagini (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistență sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Această documentație + dev-log + CHANGELOG. |

### 5.2 Cum funcționează — flux utilizator

1. **Deschide un graphml în QGIS prin meniul Import GraphML** (același path ca fluxul pyarchinit-projected existent).
2. Pyarchinit detectează automat că este yEd-raw (fără keys `pyarchinit.*`) → face dispatch pe noul branch în loc să cadă pe path-ul legacy.
3. Se deschide wizard-ul `YedImportDialog` cu **5 pagini**:
   - **1/5 Classifier** — tabel cu un rând per leaf node. Fiecare rând arată `label` + `auto_kind` (de ex. `us_real` / `usv_virtual` / `property`) + un combobox de override `user_kind`. Butonul **Acceptă auto** resetează fiecare rând la `auto_kind` (șterge toate override-urile).
   - **2/5 Periods** — un rând per TableNode-row parsat, coloane editabile `periodo` + `fase`. Datele (`datazione_iniziale`/`finale`) rămân goale: graphml-urile yEd-raw nu poartă date.
   - **3/5 Folders** — un rând per group folder. Combobox de `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` pentru excludere). `value` editabil (default = `auto_value` derivat din prefixul label-ului).
   - **4/5 Rapporti policy** — 4 radio buttons pentru tratarea edges care ating folders:
     - **SKIP** (default): aruncă edges folder-touching. Edges leaf-to-leaf trec intacte.
     - **FAN_OUT**: o edge `folder_A → folder_B` se expandează la `N×M` perechi de leaves (produs cartezian al membrilor).
     - **REPRESENTATIVE**: folosește primul membru al fiecărui folder ca proxy.
     - **SYNTHETIC**: creează un rând us_table per folder (`unita_tipo='VA'` virtual activity) + reconectează edges prin aceste ancore.
   - **5/5 Preview** — dry-run al `import_yed_raw(overrides=..., dry_run=True)`. Afișează counts (us / inv / period / paradata) **fără commit**. Click pe **Finish** confirmă, **Cancel** abandonează.
4. La **Finish** wizard-ul salvează override-urile tale într-un **sidecar JSON** `<graphml>.yed_overrides.json` lângă fișier. Redeschiderea aceluiași graphml preîncarcă sidecar-ul, deci override-urile anterioare revin preaplicate.

### 5.3 Rutarea destinațiilor

Dispatch-ul folosește `_classify_destination` (în `yed_import_pipeline.py`) pentru a clasifica fiecare leaf:

| ClassificationKind | Destinație | Notă |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | din label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | din `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | din `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | din `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derivat din prefixul label-ului: USVs/USVn/USVc) | din `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | din `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | din `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | din `^VSF\d+` |
| DOCUMENT | `paradata` | din `^D\.\d+` |
| COMBINER | `paradata` | din `^C\.\d+` |
| PROPERTY | `paradata` | cuvânt-cheie în label (`material`/`position`/`width`/...) |

**Decizie utilizator 2026-05-13**: USV* (virtuale) sunt „unità tipo" (rămân unități stratigrafice) și aparțin în `us_table`, nu în paradata. Doar DOC/COMB/PROP/VIRTUAL_FIND rămân în paradata.

### 5.4 Sidecar JSON — schemă

Versionat pentru forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
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

Se persistă doar câmpurile MODIFICATE de utilizator (diff). Valorile `ClassificationKind` necunoscute (de ex. din release-uri viitoare s3dgraphy) sunt skip-uite tăcut la încărcare.

### 5.5 CLI pentru ingest scripted

Pentru CI / re-runs în batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` pentru backend SQLite vs PostgreSQL. `--overrides` este opțional (fără overrides = defaults yE-D). `--auto-defaults` este un flag no-op forward-compat.

### 5.6 Limite cunoscute

- **Fără editare de date în wizard**: graphml-urile yEd-raw nu poartă `datazione_iniziale`/`datazione_finale`. Pagina Periods editează doar `periodo` + `fase` (targets FK).
- **API ParadataStore parțial**: upstream s3dgraphy încă nu furnizează `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D loghează „skip — method missing" pentru fiecare leaf paradata dar numără încercările în preview.
- **PropertyNode → Path B (fără legătură US)**: nodurile PROPERTY se scriu fără US target. Wizard-ul emite un warning. Viitor: follow-up yE-Closure pentru a adăuga „assign target" în UI.
- **Multi-DB**: sidecar-ul JSON este per graphml, nu per DB. Dacă imporți același graphml în DB-uri diferite, se reutilizează aceleași overrides pentru toate.

### 5.7 Acoperire teste finală

| Suite | Test | Acoperire |
|---|---|---|
| yE-A | `test_yed_detector.py` | detectare flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | politici + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistență sidecar + CLI |

**Suite totală post-rollout**: 354 passed / 42 skipped (PG-L1 necesită psycopg2).

### 5.8 Actualizare 5.8.5-alpha (yed-fastfix)

Pachet de corecții comportamentale peste `5.8.3-alpha` care îmbunătățește calitatea re-exportului GraphML după un import yEd-aware. Modificări relevante pentru utilizatorul final:

- **Paradata multi-folder**: label-urile DOC / Combinar / Extractor / property partajate între mai multe foldere yEd (de ex. `material` referențiat din VA01 + VA04 + VA05) generează acum UN rând în `us_table` PER apariție — vizibilitate multi-folder restabilită în GraphML-ul re-exportat. Compromis: dedup-ul după identitate (colapsarea `D.01` / `D.01-2` / `D.01bis` într-un singur rând) nu se mai aplică pentru a doua/a treia apariție.
- **Rapporti reciproce**: fiecare edge yEd `a → b` scrie rapporto-ul direct pe rândul lui `a` ȘI inversul pe rândul lui `b` (`<<` / „Coperto da" / etc.). DOC-urile arată acum toate conexiunile extractor de intrare în formularul Scheda US.
- **Strip al prefixului `us` numeric**: `US100` → `us='100'` `unita_tipo='US'` (înainte `us='US100'`). SF/VSF/RSF se scriu dual în `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fază**: apartenența unui rând TableNode yEd la o perioadă se propagă către `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — păstrează distincția semantică EM 1.5.
- **Re-import idempotent**: re-rularea aceluiași import sare peste rândurile deja prezente; fără rollback pentru coliziune UNIQUE la pasul repetat.
- **Paletă USV**: nodurile USV se randează acum cu paralelogramul albastru canonic EM (înainte dreptunghi cu bordură roșie).

### 5.9 yE-F paradata multi-folder (5.9.0-alpha)

Evoluție structurală a `yed-fastfix-5.8.5-alpha`: compromisul Bug R B1 (un rând `us_table` per apariție, cu `us='D.01_2'` / `us='D.01_3'`) a fost depășit. O frunză paradata (DOC / Combinar / Extractor / property) partajată între mai multe foldere yEd produce acum **un singur rând** în `us_table` per label canonic, iar apartenența multiplă este păstrată într-o nouă coloană `other_locations`.

Modificări vizibile pentru utilizatorul final:

1. **Widget nou „Alte activități" în fișa US/USM**: în tab-ul *Periodizzazione* apare un `QListWidget` etichetat „Alte activități" — vizibil **doar** când `unita_tipo` este o tipologie paradata (`DOC`, `Combinar`, `Extractor`, `property`). Utilizatorul poate selecta mai multe coduri de activitate; selecția este serializată ca listă JSON în noua coloană `other_locations`.
2. **Element de meniu QGIS nou**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Trebuie executat **o singură dată** pe fiecare DB preexistentă pentru a adăuga noua coloană (DB-urile create post-5.9 au deja coloana).
3. **Import yEd-aware îmbunătățit**: o frunză paradata care apare în N foldere yEd generează acum **doar 1** rând `us_table` (nu N rânduri cu sufix `_2`/`_3` ca în 5.8.5). Primul folder întâlnit devine `attivita` principală; folderele secundare sunt listate în `other_locations`. La **export** se emit N copii vizuale yEd (una per folder), toate împărtășind același `node_uuid` canonic pentru a garanta identitatea round-trip.

**Compatibilitate înapoi**: datele produse de Bug R B1 în 5.8.5-alpha (rânduri cu sufix `_2`/`_3`) rămân lizibile fără nicio conversie automată. Logica nouă se aplică noilor importuri; rândurile legacy continuă să se comporte ca înainte.

Predecesor: vezi secțiunea 5.8 (`yed-fastfix-5.8.5-alpha`) pentru comportamentul înlocuit.

---

## 6. Generare continuitate (fișe CON)

În panoul **„Verifica rapporti"** — disponibil ca tab în interiorul dialogului de import/export s3dgraphy — există butonul **„Genera continuità"** (etichetă păstrată în italiană ca în plugin). Pentru situl selectat curent, această funcție creează automat **fișele de continuitate** ale US/USM a căror viață se întinde pe mai mult de o perioadă.

### 6.1 Ce face

1. Scanează toate US/USM din sit la care **perioada inițială ≠ perioada finală** (adică a căror viață se întinde pe mai multe perioade).
2. Pentru fiecare creează sau actualizează o fișă de continuitate denumită **`CON_<us>`** (de ex. `US5` → `CON_US5`).
3. Fișa CON **moștenește** de la unitatea-mamă: situl, aria (plus ariile secundare), structura și întregul interval de perioade (inițială → finală). Descrierea ei este generată automat.
4. Scrie o **relație de continuitate reciprocă** pe ambele părți: pe CON și pe unitatea-mamă.

> **Faza, de la sine, nu conteaza.** Regula se uita la **perioada**: o USM care merge de la **2/3 la 2/4** — aceeasi perioada, se schimba doar faza — nu genereaza nimic. Daca unitatile tale supravietuiesc din faza in faza in interiorul aceleiasi perioade, bifeaza **„anche i salti di fase"** („si salturile de faza") langa buton: atunci conteaza si acele salturi, cu conditia ca **ambele** faze sa fie completate. O unitate care nu se misca — aceeasi perioada si aceeasi faza — nu este niciodata o continuitate. Caseta porneste **nebifata** si este valabila pentru previzualizare si pentru scriere deopotriva.

### 6.2 Idempotență

Operația este **idempotentă**: rularea repetată nu duplică fișele existente — actualizează `CON_<us>` existente dacă datele unității-mamă s-au schimbat.

### 6.3 Previzualizare (dry-run) și backup

Înainte de scriere se afișează o **previzualizare dry-run** cu numărătorile: câte fișe trebuie **create**, **actualizate**, **neschimbate** și câte **orfane**. Modificările se aplică **doar după confirmare** (butonul „Genera"). La aplicare se face mai întâi un **backup al bazei de date** automat.

O fișă CON este **orfană** atunci când unitatea ei mamă nu se mai întinde pe mai multe perioade (de ex. perioada inițială și cea finală au fost făcute egale). În mod implicit orfanele sunt doar **semnalate**; o **casetă de bifare** („Rimuovi anche le CON orfane") permite optarea pentru eliminarea lor.

**O continuitate scrisa de mana este recunoscuta.** O fisa CON ale carei relatii numesc o singura unitate — `> 12`, sau „Continuitate dupa 12” — este continuitatea acelei unitati, oricum s-ar numi: generatorul o **actualizeaza** (intervalul de perioade, eticheta canonica) iar numele ramane al ei. Nu se naste o a doua: continuitatea este **una pe unitate**. Daca exista si o `CON_<us>` canonica, castiga aceea, iar cealalta ramane orfana, de decis de mana.

### 6.4 În exportul Extended Matrix

Fișele `CON_<us>` generate astfel apar în **em.json** al Extended Matrix ca **elemente de continuitate** (exportul GraphML este pensionat, §2.3).

---

## 7. Verificarea paradoxurilor temporale (stratigrafice)

În panoul **"Verifica rapporti"** (Verificarea relațiilor — o filă din dialogul de import/export s3dgraphy), verificarea semnalează acum și **paradoxurile temporale**: când perioada/faza atribuită unei unități contrazice stratigrafia observată. Stratigrafia este data de referință, prin urmare corecțiile automate mută **perioadele**, nu relațiile.

### 7.1 Ce detectează
- **Inversiune temporală**: două unități datate legate printr-o relație de ordine (de ex. US5 «acoperă» US7) în care unitatea mai recentă din stratigrafie se dovedește a fi în întregime mai **veche** ca perioadă.
- **Contemporaneitate incoerentă**: unități declarate contemporane (egalitate fizică / legătură) dar cu intervale cronologice **disjuncte**.
- **Neevaluabil**: relație de ordine în care cel puțin una dintre cele două unități nu are o perioadă databilă (doar semnalat, fără corecție).

Notă privind limita: două perioade **adiacente care se ating** într-un singur punct cronologic sunt considerate suprapuse → **nu** constituie un paradox (prezumția de bună-credință).

### 7.2 Corecție automată și sugestii
- Când o singură mutare rezolvă conflictul, verificarea propune mutarea unității **mono-perioadă** aflate în conflict cu majoritatea vecinilor săi, alegând perioada cu mutarea minimă; pentru contemporaneitățile cu o unitate nedatabilă copiază perioada vecinului datat.
- În cazurile ambigue — egalitate, unități **multi-perioadă** (de ex. fișe CON), nicio perioadă validă — nu corectează automat: oferă o **sugestie «ce + cum»** (de ex. «Mută US5 la o perioadă ≥ 3, sau US7 la o perioadă ≤ 1, sau verifică relația»).

### 7.3 Previzualizare și backup
- **Previzualizarea** arată modificările de perioadă propuse înainte de a le aplica.
- Înainte de scrierea perioadelor se efectuează un **backup automat al bazei de date** (SQLite și PostgreSQL).
- După aplicare, relansează verificarea pentru a controla eventualele paradoxuri reziduale.

---

## 8. Verificarea cronologiei (periodizare și fișe)

În același panou **"Verifica rapporti"** (Verificarea relațiilor — o filă din dialogul de import/export s3dgraphy), începând cu versiunea 5.13.64-alpha verificarea găsește și corectează și probleme de **cronologie** ale sitului selectat. Verificarea paradoxurilor temporale (secțiunea 7) compară perioada unei unități cu stratigrafia; aceasta compară periodizarea cu ea însăși și cu fișele US care o copiază.

### 8.1 Ce detectează

Panoul grupează problemele pe tipuri. Alături de grupurile relațiilor apar patru grupuri noi:

| Grup | Ce semnalează | Cum este tratat |
|------|---------------|-----------------|
| **Faze cu intervale suprapuse** | Două rânduri ale periodizării ale căror intervale de ani se intersectează | Manual: panoul propune îngustarea intervalelor doar dacă, după îngustare, rămâne un interval utilizabil |
| **Datare a fișei dezaliniată** | Câmpul `datazione` al fișei US spune altceva decât `datazione_estesa` a perioadei/fazei sale | Automat: periodizarea este sursa, iar fișa este copia, deci copia este rescrisă din sursă. Un câmp gol se completează la fel. O US fără perioadă este sărită, pentru că nu există nimic de copiat |
| **Periodizare cu începutul după sfârșit** | `cron_iniziale` mai mare decât `cron_finale` | Manual: sunt probabil date î.Hr. fără semnul minus — panoul propune rescrierea celor doi ani ca numere negative (`-1650` în loc de `1650`); dacă este însă o greșeală de tastare, inversează manual cele două valori |
| **Fază fără ani** | O fază ai cărei ani lipsesc sau nu pot fi citiți | Doar semnalată: nu există nimic de la care să îi moștenească |

Un exemplu pentru suprapuneri. Baza de date de exemplu are două și niciuna nu are propunere: cele două faze au intervale **identice**, iar orice îngustare ar face ca o fază să se termine înainte de a începe. Panoul doar o spune; decizia (unirea fazelor, corectarea anilor, lăsarea așa cum este) aparține arheologului.

### 8.2 Corecție automată și sugestii

**Corecții automate și propuneri.** Corecțiile automate sunt **deja bifate**; propunerile **nu**, și sunt aplicate doar dacă se bifează caseta. Înainte regula era alta: o problemă a cărei corecție cerea o decizie umană putea fi doar citită. Acum are o casetă, lăsată nebifată. Acest lucru este valabil și pentru cele două categorii mai vechi de relații care oferă o sugestie, adică contradicția directă și ciclul stratigrafic.

Pentru a folosi panoul:

1. Selectați în panou **situl** de verificat. Verificarea este **pe sit**: se uită doar la situl ales și corectează doar acel sit. Într-o bază de date cu zece situri acest lucru contează, pentru că aceleași numere de US există în toate.
2. Citiți **linia de rezumat** de deasupra arborelui: spune câte probleme sunt, câte pot fi corectate automat și **câte sunt propunerile de bifat manual**.
3. Deschideți grupurile și selectați o problemă pentru a-i citi detaliul în panoul de previzualizare.
4. Verificați casetele. Corecțiile automate sunt deja bifate: debifați-le pe cele pe care nu doriți să le aplicați. Bifați propunerile cu care sunteți de acord.
5. Aplicați corecțiile. Înainte de a scrie orice se creează o **copie de siguranță automată** (copie a fișierului SQLite sau `pg_dump` pentru PostgreSQL în `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); copia, care exista deja pentru corecțiile câmpurilor de perioadă, acoperă acum și corecțiile cronologice.
6. Dacă rezultatul nu convinge, apăsați **Annulla ultimo fix** (anulează ultima corecție): anularea readuce și corecțiile scrise în tabela periodizării.

### 8.3 Previzualizare și backup

**Previzualizarea arată data calculată.** Pentru fiecare unitate citată de o problemă, panoul de previzualizare arată data ei calculată într-o linie ca aceasta:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

Linia indică, în ordine, intervalul de ani, regula care l-a produs și relația de-a lungul căreia a călătorit constrângerea, împreună cu nodul de la care provine. Când cele două capete ale intervalului vin pe drumuri diferite, fiecare capăt are eticheta lui (`inizio …` și `fine …`), astfel încât o dată nu este niciodată atribuită relației greșite. Astăzi, într-o bază de date normală, fiecare unitate își ia datele din propria perioadă, deci majoritatea liniilor vor spune `epoca`. Rostul liniei nu este să surprindă, ci să lase să se vadă **de unde vine** o dată.

---

## 9. Cum se citesc arcele matricei

Unele alegeri din desenul matricei pot parea ciudate, dar nu sunt erori:

- **O sageata nu trece niciodata pe sub un nod.** Cand coloana de sosire este ocupata, sageata intra in casuta **din lateral**: este normal.
- **Egalitatea nu este o suprapunere.** O relatie «Uguale a» (Egal cu) sau «Si lega a» (Se leaga de) pune cele doua unitati pe **acelasi rand**, alaturate, unite prin **doua linii orizontale** (semnul egal) **fara varf de sageata**.
- **Arcele redundante nu se deseneaza.** Daca US 1 acopera US 2 si US 2 acopera US 3, sageata de la 1 la 3 nu apare, pentru ca nu adauga nimic. In interiorul unui **ciclu**, in schimb, toate arcele raman, pentru ca un ciclu este o eroare care trebuie vazuta.
- **Liniile spun ce relatie sunt.** Gri si continua: secventa (acopera, umple, se sprijina). **Punctata verde**: o taietura (`Taglia` / `Tagliato da`), oricare ar fi definitia stratigrafica si in orice limba. **Groasa si neagra**: continuitatea — un romb mic si negru fara nume (numele apare la trecerea mouse-ului), in coloana unitatii sale, asa ca linia e dreapta. **Rosie**: o sageata care urca prin benzi, adica o contradictie intre stratigrafie si cronologie; o taietura care urca e rosie **si** ramane punctata.
- **Paradatele nu sunt niciodata o linie continua.** Iau culoarea si trasatura din regulile Extended Matrix (`em_visual_rules.json`): brun-rosu punctat „extras din", portocaliu intrerupt „provenienta datei", auriu intrerupt „proprietate", gri intrerupt „conexiune generica", rosu-tomata intrerupt „combina" (in fisier ar fi continua: e singura abatere, pentru ca un arc catre un document nu trebuie sa para o suprapunere).
- **Marginea bruna este o zidarie.** USM — WSU, MSE, UEM, USZ, ΤΣΜ in celelalte limbi — au aceeasi caseta ca US, cu margine bruna in loc de rosie.

---

## 10. Narațiune cu AI

Începând cu versiunea **5.13.106-alpha**, panoul matricei din QGIS (§2.2, „Vedi la matrice”) are două file în coloana din dreapta: **Units** (*Unità*) — detaliile unității alese, zoomul pe geometrie și fișierele media, ca până acum — și **Narrative** (*Narrativa*), cea nouă. Fila Narrative pune un AI să scrie **povestea sitului**, câte un capitol pentru fiecare epocă, apoi o poți citi, o poate valida o persoană și o poți exporta în HTML sau DOCX. Citește și scrie **același em.json** pe care îl deschide EMStudio, în formatul bibliotecii s3dgraphy: narațiunea pe care o vezi aici este cea pe care EMStudio o arată în fila sa *Narrative*.

> **Nicio setare nouă.** Fila nu are o fereastră de configurare proprie: folosește AI-ul pe care l-ai configurat deja în altă parte din pyArchInit (§10.2).

> **AI-ul scrie ciorne, nu texte definitive.** Fiecare paragraf scris de model rămâne „AI draft” (ciornă AI) până când o persoană îl validează (§10.6), iar în documentele exportate poartă semnul ⚠.

Numele filelor și ale butoanelor din fila Narrative există în italiană și în engleză: **sunt în italiană dacă QGIS este în italiană, în engleză cu orice altă limbă**. Aici le găsești întotdeauna pe amândouă. Intrările de meniu și ferestrele de dialog ale pluginului (precum „Vedi la matrice…” sau cele trei butoane din §10.9) sunt, în schimb, doar în italiană; traducerea în română este dată între paranteze.

### 10.1 Deschiderea filei Narrative

1. Deschide meniul **Plugins → pyArchInit - Archaeological GIS Tools** și alege intrarea **Extended Matrix → Vedi la matrice…** (Vezi matricea).
2. Alege **situl**.
3. Dacă situl are **sondaje** (*saggi*), pyArchInit întreabă „Il sito ha N saggi. Come divido il file?” (Situl are N sondaje. Cum împart fișierul?) cu două răspunsuri: „Un grafo per ogni saggio (…)” (un graf pentru fiecare sondaj), cel propus implicit, sau „Un grafo solo per tutto il sito” (un singur graf pentru tot situl). Este aceeași alegere ca în §2.2.1 și în intrarea „Esporta sito in em.json…”: cele două intrări scriu **același fișier**, cu aceeași formă.
4. pyArchInit exportă situl din baza de date în `<home>/pyarchinit_EM_folder/<sit>.em.json` — `<home>` este `~/pyarchinit_5`, sau folderul indicat de variabila de mediu `PYARCHINIT_HOME` — și deschide panoul **„Matrice — `<sit>`”**, ancorat în dreapta ferestrei QGIS. Numele fișierului este numele sitului, cu caracterele speciale înlocuite cu „_” (de exemplu „Scavo 1” devine `Scavo_1.em.json`).
5. În coloana din dreapta a panoului, apasă fila **Narrative**.

<!-- IMMAGINE: Captură de ecran a meniului Plugins → pyArchInit - Archaeological GIS Tools cu intrarea „Extended Matrix → Vedi la matrice…” -->
![Meniul Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: Intrarea „Extended Matrix → Vedi la matrice…” în meniul pluginului*

<!-- IMMAGINE: Captură de ecran a întrebării despre sondaje, cu cele două răspunsuri -->
![Întrebarea despre sondaje](images/36_extended_matrix_s3dgraphy/02_domanda_saggi.png)
*Figura 2: Întrebarea despre sondaje: un graf pentru fiecare sondaj sau un singur graf*

<!-- IMMAGINE: Captură de ecran a panoului matricei ancorat în dreapta, cu filele Units și Narrative -->
![Panou cu două file](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 3: Panoul matricei cu filele Units și Narrative*

Fișierul este **unul pentru fiecare sit și rămâne pe disc**: nu se mai află într-un folder temporar. Este fișierul pe care îl deschide EMStudio și în el se scrie narațiunea. De fiecare dată când alegi „Vedi la matrice…”, situl este **exportat din nou din baza de date** și fișierul este rescris; narațiunea deja prezentă în el se păstrează (§10.8).

La filă se ajunge și din alte două locuri:

- din intrarea **Extended Matrix → Esporta sito in em.json…** (Exportă situl în em.json), care la final oferă butonul „Narrativa con l'AI” (§10.9);
- din butonul **Vedi la matrice** al ferestrei „Esporta Extended Matrix” din fișa US (§2.2): deschide același panou pe fișierul pe care tocmai l-ai exportat, în folderul pe care l-ai ales.

### 10.2 Ce AI este folosit

În partea de sus a filei Narrative, o linie spune ce AI va folosi: **„Model: `<model>` (`<where it comes from>`)”**, urmată de reamintirea despre EMStudio. Dacă nu găsește niciunul, scrie **„No AI configured: set it in the US form → AI report (or in the AI database query).”** (niciun AI configurat: configurează-l în fișa US → raportul AI sau în interogarea AI a bazei de date), iar butoanele **Generate with AI** și **Regenerate chapter** rămân dezactivate.

Fila citește setările AI **deja salvate** de celelalte ferestre ale pyArchInit, în această ordine, și o folosește pe **prima** care are un model și — pentru furnizorii online — cheia API:

| # | Unde se setează | Cum o numește fila (en / it) |
|---|-----------------|------------------------------|
| 1 | Fișa US, butonul „Report” → fereastra „Generatore di Report” (Generator de rapoarte), grupul „Provider AI” | AI report of the US form / Relazione AI della scheda US |
| 2 | Fișa US, butonul „Query AI Database” | AI database query / Interrogazione AI del database |
| 3 | Fereastra palimpsestr, butonul „Report AI (analisi descrittiva)…”, selectorul „Provider AI” | Palimpsest report / Relazione Palimpsest |
| 4 | Fereastra „Generazione SQL con AI” (text în SQL: vezi tutorialul 30) | Text to SQL / Testo in SQL |

Furnizorii sunt cei din selectoarele „Provider AI”: **OpenAI** și **Anthropic (Claude)** online, cu cheia API scrisă în câmpul „API key”; **Ollama** și **LM Studio** pe computerul tău, fără cheie. Selectorul salvează alegerea de îndată ce o schimbi. Dacă vrei alt model, schimbă-l în fereastra pe care fila o indică între paranteze (sau într-una care vine mai devreme în listă). Fila recitește setările **când se deschide panoul**: după ce le-ai schimbat, deschide din nou matricea.

### 10.3 Fila Narrative

```
┌─ Units ─┬─ Narrative ────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the     │
│ file open, close it first: the last writer wins.                 │
├──────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                     │
│ Early 15th century — AI draft                                    │
│ 15th century — endorsed                                          │
│ Modern age — AI draft, truncated                                 │
├──────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.            │
├──────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                 │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]             │
│ [Prepare the chapters]  [Export…]  [Open in EMStudio]  [Cancel]* │
└──────────────────────────────────────────────────────────────────┘
```

\* Linia de progres și butonul „Cancel” se văd doar cât timp AI-ul scrie. În această schemă, rândurile listei sunt cele ale sitului de exemplu.

<!-- IMMAGINE: Captură de ecran a filei Narrative, cu lista capitolelor, textul capitolului ales și cele șase butoane -->
![Fila Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 4: Fila Narrative*

De sus în jos:

- **linia de stare**: modelul folosit (§10.2) și reamintirea *„If EMStudio has the file open, close it first: the last writer wins.”* (dacă EMStudio are fișierul deschis, închide-l mai întâi: cine scrie ultimul câștigă);
- **lista capitolelor**, un rând pentru fiecare capitol: *Titlu — stare*. Cu exportul pe sondaje (§2.2.1), fiecare sondaj are propria narațiune, iar fiecare rând este precedat de numele sondajului între paranteze drepte, de exemplu `[Saggio A] 15th century — AI draft`;
- **textul capitolului ales**: textul narativ, cu unitățile citate pe nume. Dacă capitolul nu are încă text, vezi substituentul său „[to be written: …]”;
- **linia de progres**, doar în timpul generării: „Chapter 3 of 9 · 15th century”;
- **butoanele**, pe două rânduri.

Rezultatul fiecărei operații apare în bara de mesaje a QGIS, cu titlul „Narrative”.

Când fișierul **nu are încă o narațiune**, lista este goală și un text spune: *„No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it.”* (nicio narațiune în fișier: „Prepare the chapters” creează scheletul, cu N capitole între epoci și activități, iar „Generate with AI” îl scrie).

#### Stările unui capitol

| Stare (en / it) | Ce înseamnă |
|-----------------|-------------|
| **to be written** / da scrivere | Capitolul conține doar substituentul „[to be written: …]”. |
| **AI draft** / bozza AI | Există text scris de model pe care nicio persoană nu l-a validat. Este suficient un paragraf: dacă un capitol are chiar și un singur paragraf nevalidat, aceasta este starea lui, chiar dacă există și alt text. |
| **endorsed** / convalidato | Tot textul scris de AI a fost validat de o persoană. |
| **written** / scritto | Text scris de o persoană (în EMStudio). |
| **truncated** / troncato | Se adaugă la stare (de exemplu „AI draft, truncated”): modelul s-a oprit pentru că a atins limita de lungime, iar textul se termină la jumătate. |

#### Butoanele

| Buton (en) | În italiană | Ce face |
|------------|-------------|---------|
| **Generate with AI** | Genera con l'AI | Scrie, **pe rând**, toate capitolele de epocă (și de activitate) încă „to be written”; cele deja scrise nu sunt atinse. Dacă narațiunea nu există încă, creează mai întâi scheletul. Arată progresul și butonul **Cancel**. Activ doar cu un fișier deschis și un AI configurat. |
| **Regenerate chapter** | Rigenera capitolo | Rescrie **capitolul ales** în listă (cu mai multe sondaje, doar cel al sondajului ales): ciorna AI nevalidată este înlocuită — dar numai după ce modelul a răspuns: dacă apelul eșuează, ciorna de dinainte rămâne — iar blocurile deja validate rămân. Se activează când alegi un capitol de epocă sau de activitate și un AI este configurat; pentru „Presentation” și „Where it is” rămâne dezactivat. |
| **Endorse…** | Convalida… | Deschide un meniu cu „This chapter” și „All chapters”, apoi întreabă cine validează (§10.6). Activ când există o narațiune. |
| **Prepare the chapters** | Prepara i capitoli | Creează **doar scheletul** capitolelor, fără AI: funcționează chiar dacă nu este configurat niciun AI, ca să poți scrie manual în EMStudio. Nu atinge textul deja scris și adaugă capitolele epocilor noi. Rezultat: „Chapters prepared: N.” (Capitole pregătite: N.) |
| **Export…** | Esporta… | Salvează narațiunea în HTML sau DOCX (§10.7). Activ când există o narațiune. |
| **Open in EMStudio** | Apri in EMStudio | Deschide em.json în EMStudio. Dacă EMStudio nu este instalat, bara de mesaje trimite la intrarea de meniu **Extended Matrix → Installa EMStudio…** (Instalează EMStudio). |
| **Cancel** | Annulla | Apare doar în timpul generării: AI-ul se oprește **după capitolul în curs**, iar ce s-a scris este salvat. |

În timpul generării, toate butoanele sunt dezactivate, în afară de **Cancel**.

### 10.4 Ce scrie AI-ul

**Ce capitole.** Scheletul este cel al bibliotecii s3dgraphy (șablonul „site_story”):

- **Presentation** (Prezentare) și **Where it is** (Unde se află) sunt capitole canonice: rămân ca substituenți „[to be written: …]”, de scris manual în EMStudio, pentru că în graf nu există nimic din care să fie scrise fără a inventa. „Where it is” există doar dacă graful poartă o poziție geografică. AI-ul nu le generează.
- **Un capitol pentru fiecare epocă** (perioadă/fază) care are unități, de la cea mai veche la cea mai recentă. Titlul este numele epocii, adică „Datazione estesa” (datare extinsă) din periodizare; dacă lipsește, rezultă un nume generic, de exemplu „Period 8 Phase 1”: completeaz-o în Fișa de Periodizare pentru a avea titluri ușor de citit. O unitate apare în capitolul epocii în care se naște și în cele ale epocilor în care supraviețuiește.
- **Un capitol pentru fiecare activitate**, dacă graful conține grupuri de activități. Un sit exportat din baza de date, în mod normal, nu are niciunul — câmpul Activity (activitate) din fișa US călătorește ca proprietate a unității — și atunci capitolele sunt cele de epocă.

**Ce primește modelul.** Pentru fiecare capitol, un *briefing* cu, pentru fiecare unitate: nume, tip și descriere; câmpurile completate ale fișei US (definiția stratigrafică și interpretativă, interpretarea, perioada și faza, datarea, activitatea, structura, sondajul, încăperea, sectorul, aria); epocile; **relațiile stratigrafice** cu celelalte unități (acoperă, taie, umple, se sprijină pe, egal cu…), cu numele lor; și, dacă există, sursele documentare legate. Unitățile sunt listate **de la cea mai veche la cea mai recentă**, urmând relațiile. Peste **80 de unități** pe capitol, briefingul este limitat la primele 80. Are și o limită de lungime (aproximativ 25.000 de caractere): peste aceasta, textele lungi ale fișelor sunt scurtate, relațiile repetate și lanțurile de dovezi sunt eliminate și, dacă nici asta nu ajunge, unitățile cele mai recente sunt omise. În ambele cazuri modelul este informat câte unități lipsesc.

**Regulile.** Modelul primește cele cinci reguli ale bibliotecii: să scrie doar ceea ce susține contextul (fără date, materiale, funcții sau evenimente inventate); să păstreze incertitudinea (o unitate virtuală este o ipoteză, nu un fapt); să nu citeze surse care nu sunt prezente; să scrie text continuu, fără liste sau titluri; să spună deschis când contextul este prea sărac. I se cer de la unul la trei paragrafe.

**Limba.** Textul este în **limba narațiunii**, care se stabilește când este creat pentru prima dată scheletul: **italiană dacă în acel moment QGIS este în italiană, engleză cu orice altă limbă** (modelul primește instrucțiunile doar în aceste două limbi). O narațiune deja creată își păstrează limba chiar dacă mai târziu schimbi limba QGIS. Același lucru este valabil pentru titlurile capitolelor canonice și pentru substituenți.

**Cum se salvează.** În formatul bibliotecii, același pe care îl citește EMStudio: un nod de narațiune (`NarrativeNode`) care conține capitolele; fiecare paragraf scris de model este un bloc „AI draft” atribuit **autorului AI** al acelui model; **promptul** folosit este înregistrat ca extractor legat de surse, astfel încât se poate afla ce s-a cerut. Unitățile citate în text sunt **mențiuni** (`[[name]]`): în fișier rămân legate de nodul unității, iar în filă și în exporturi apar cu numele ei. O mențiune care nu corespunde niciunei unități din graf este redusă la simple cuvinte, fără paranteze.

**Costuri și durate.** Modelul este apelat **o dată pentru fiecare capitol**. Cu un furnizor online, fiecare apel are un cost și un timp de așteptare (în încercări cu un model online, câteva zeci de secunde pe capitol: un sit cu aproximativ zece epoci durează câteva minute); cu Ollama sau LM Studio nu se plătește nimic, dar duratele depind de computerul tău.

### 10.5 Pas cu pas

1. Deschide matricea sitului (§10.1) și apasă fila **Narrative**. Verifică sus **ce model** va folosi.
2. **Închide EMStudio** dacă are fișierul deschis: pyArchInit și EMStudio scriu același fișier, iar cine scrie ultimul câștigă.
3. Opțional: **Prepare the chapters**, ca să vezi scheletul, fără AI.
4. Apasă **Generate with AI**. Urmărește progresul („Chapter 3 of 9 · …”); poți continua să folosești QGIS. La final, bara de mesaje spune, de exemplu, *„7 chapters generated, 1 failed: Modern age — …”* (7 capitole generate, 1 eșuat: Modern age — …), cu *„(cancelled)”* (anulat) dacă ai anulat, iar lista se reîncarcă: capitolele scrise sunt „AI draft”.
5. **Citește**: alege pe rând câte un capitol și citește textul de sub listă. Confruntă-l cu stratigrafia: este o ciornă construită din datele fișei US.
6. Dacă un capitol nu te convinge, alege rândul lui și apasă **Regenerate chapter**. Noua ciornă **înlocuiește** ciorna anterioară nevalidată: dacă vrei să păstrezi versiunea de dinainte, exportă-o mai întâi. Dacă un capitol este „truncated”, regenerează-l **înainte** de a-l valida.
7. Când un capitol este în regulă, apasă **Endorse…** (§10.6).
8. Apasă **Export…** pentru a salva în HTML sau DOCX (§10.7), sau **Open in EMStudio** pentru a scrie manual „Presentation” și „Where it is” și a finisa restul.
9. Mai târziu poți deschide din nou matricea: narațiunea rămâne (§10.8).

<!-- IMMAGINE: Captură de ecran a generării în curs: linia de progres „Chapter 3 of 9 · …” și butonul Cancel -->
![Generare în curs](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 5: Generare în curs, cu linia de progres și butonul Cancel*

Un capitol care eșuează nu le oprește pe celelalte: rezumatul spune care. Pentru a reîncerca, este suficient să apeși din nou **Generate with AI**, care scrie doar capitolele încă „to be written”.

### 10.6 Validarea: cine semnează

A valida înseamnă că o **persoană** își asumă răspunderea pentru textul scris de model. Nu se întâmplă niciodată de la sine: nici prin generare, nici prin salvare.

1. Apasă **Endorse…**. Se deschide un meniu mic: **„This chapter”** (Acest capitol) — activ doar dacă capitolul ales este „AI draft” — sau **„All chapters”** (Toate capitolele), adică toate ciornele AI încă nevalidate, în toate grafurile fișierului.
2. O fereastră întreabă **„Who endorses? Pick an author or type a new name.”** (Cine validează? Alege un autor sau scrie un nume nou.) Lista conține **autorii umani deja existenți în graf** — persoanele numite în fișa US drept compilator (*schedatore*), director US și responsabil US — și poți scrie un nume nou, care devine un nou autor al grafului (cu mai multe sondaje, în fiecare graf care are ciorne de semnat).
3. Bara de mesaje spune **„N blocks endorsed by `<name>`.”** (N blocuri validate de autorul ales.) sau „Nothing to endorse.” (Nimic de validat.) Fișierul este salvat.

<!-- IMMAGINE: Captură de ecran a meniului Endorse… („This chapter” / „All chapters”) și a ferestrei de alegere a autorului -->
![Validare](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 6: Validarea: meniul și alegerea autorului*

Blocurile trec de la „AI draft” la „endorsed”. În documentul exportat, persoana apare printre responsabili („a cura di”, îngrijit de), modelul apare ca asistent („con l'assistenza di”, cu asistența), iar paragrafele validate nu mai poartă semnul ⚠. Regenerarea nu șterge blocurile validate: o semnătură este un act și nu se pierde prin rescriere.

### 10.7 Exportul în HTML sau DOCX

Apasă **Export…**: se deschide fereastra de salvare, cu două formate, „HTML page (\*.html)” și „Word document (\*.docx)” (pagină HTML, document Word). Numele propus este `<sit>_narrativa.html`, în folderul fișierului em.json; dacă scrii tu extensia (`.html` sau `.docx`), aceasta are prioritate, altfel decide formatul ales. Cu exportul pe sondaje se scrie **un fișier pentru fiecare sondaj**, adăugând numele sondajului la numele ales. Bara de mesaje confirmă: „Narrative exported to `<path>`” (Narațiune exportată în fișierul ales).

Documentul conține:

- titlul narațiunii (de exemplu „Scavo archeologico — the story of the site”, adică „Săpătură arheologică — povestea sitului”), responsabilii („a cura di”) și modelul ca asistent („con l'assistenza di”);
- pentru fiecare capitol, textul, cu unitățile citate prin numele lor, și lista unităților capitolului;
- la sfârșit, secțiunea **Fonti** (surse): documentele pe care se sprijină povestea și intrarea „Prompt”, care trimite la promptul înregistrat în fișier.

Câteva lucruri de știut:

- **ciornele nevalidate intră în document**, fiecare precedată de „⚠︎ non validato da una persona” (nevalidat de o persoană), iar antetul spune câte blocuri se află în această stare. Pentru un document fără semne, validează mai întâi (§10.6);
- **intră toate capitolele**, chiar și cele încă „to be written”: substituentul lor „[to be written: …]” rămâne în text;
- figurile pe care un autor le-a prevăzut în EMStudio (de exemplu matricea unei epoci) nu sunt desenate de exportul pyArchInit: în document rămâne un substituent;
- HTML-ul este un singur fișier, autonom; DOCX-ul se deschide cu Word sau LibreOffice și are nevoie de pachetul `python-docx`, care face parte din cerințele pluginului.

<!-- IMMAGINE: Captură de ecran a documentului HTML exportat: un capitol cu o ciornă precedată de „⚠︎ non validato da una persona” -->
![Document HTML exportat](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 7: Documentul HTML exportat, cu o ciornă nevalidată marcată*

### 10.8 Reexportarea sitului: narațiunea rămâne

Reexportarea sitului din baza de date — cu **Vedi la matrice…**, cu **Esporta sito in em.json…** sau cu fereastra „Esporta Extended Matrix” din fișa US — **păstrează narațiunea** deja prezentă în fișierul de destinație: textul, validările, autorul AI și prompturile. Epocile apărute între timp primesc un capitol „to be written”. O notificare o spune: **„Narrative kept from the previous file (N chapters).”** (Narațiune păstrată din fișierul anterior, N capitole.) O vezi în bara de mesaje cu „Vedi la matrice…”, în rezumatul ferestrei „Esporta Extended Matrix” și, cu „Esporta sito in em.json…”, în detaliile ferestrei finale.

**Celelalte modificări** făcute în fișier în EMStudio — pozițiile nodurilor, descrierile rescrise — **nu supraviețuiesc**, ca până acum: fișierul este regenerat din baza de date. Se păstrează doar narațiunea.

Înainte de a rescrie un fișier care conține o narațiune, pyArchInit face o **copie de siguranță** alături de el: `<sit>.em.json.bak` (fiecare reexportare nouă înlocuiește copia precedentă).

Dacă schimbi forma fișierului — treci de la „Un grafo per ogni saggio” la „Un grafo solo per tutto il sito” sau invers — grafurile își schimbă numele, iar narațiunea **nu poate trece** în fișierul nou. O notificare o spune: *„The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …”* (Narațiunea fișierului anterior (grafuri: …) nu a trecut în fișierul nou (grafuri: …): forma fișierului s-a schimbat. Copie de siguranță în …). Textul nu este pierdut: se află în copia `.bak`, care însă este înlocuită la următoarea reexportare a unui fișier care conține o narațiune — pune-o într-un loc sigur. Pentru a-l recupera, redenumește copia în `.em.json` și exportă din nou cu alegerea de dinainte.

Dacă fișierul anterior nu poate fi citit (de exemplu un fișier rămas scris pe jumătate), exportul merge înainte oricum: fișierul necitibil este **redenumit** `<sit>.em.json.broken`, iar o notificare spune *„The previous file cannot be read (…): its narrative, if any, was not kept.”* (Fișierul anterior nu poate fi citit (…): narațiunea lui, dacă exista, nu a fost păstrată.)

> **Narațiunea nu se află în baza de date pyArchInit: există doar în em.json.** Backup-ul bazei de date nu o copiază. Copiază din când în când folderul `pyarchinit_EM_folder`.

### 10.9 Din intrarea „Esporta sito in em.json…”

Intrarea **Extended Matrix → Esporta sito in em.json…** pune aceeași întrebare despre sondaje și scrie același fișier `<sit>.em.json` în `pyarchinit_EM_folder`. La final afișează „Esportato `<cale>`” (Exportat), cu numărul de noduri, muchii și notificări (textul notificărilor se află în detaliile ferestrei), și **trei butoane**:

| Buton | Ce face |
|-------|---------|
| **Apri in EMStudio** (Deschide în EMStudio) | Deschide fișierul în EMStudio; dacă nu este instalat, oferă să îl instaleze. |
| **Narrativa con l'AI** (Narațiune cu AI) | Apare **doar dacă un AI este configurat** (§10.2): deschide panoul matricei direct pe fila Narrative. |
| **Chiudi** (Închide) | Închide fereastra. |

<!-- IMMAGINE: Captură de ecran a ferestrei finale „Esporta sito in em.json…” cu cele trei butoane -->
![Esporta sito in em.json: trei butoane](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 8: Fereastra finală a intrării „Esporta sito in em.json…”*

### 10.10 Avertismente

- **Închide EMStudio înainte de a genera sau a valida.** Dacă EMStudio are fișierul deschis, cine scrie ultimul câștigă. Cu mai multe sondaje, EMStudio arată câte un graf pe rând (nota din §2.2.1): fila Narrative le arată pe toate.
- **Un AI scrie doar din ceea ce găsește în graf și poate greși.** Regulile îl țin în frâu, dar nu îl fac infailibil: citește fiecare capitol înainte de a-l valida.
- **Cu un furnizor online, datele ies din computerul tău.** Briefingul fiecărui capitol (numele, definițiile, descrierile și relațiile unităților) este trimis serviciului ales; cu Ollama sau LM Studio rămâne local.
- **Fișierul se scrie la final.** Generarea salvează când se termină, chiar dacă ai anulat-o: nu închide QGIS cât timp AI-ul scrie. Salvarea este sigură: fișierul este scris alături, recitit și abia apoi înlocuiește fișierul real; dacă ceva merge prost, **fișierul anterior rămâne așa cum era**.
- **Nu redeschide matricea cât timp AI-ul scrie.** Fila rămâne pe fișierul de dinainte și avertizează: *„Generation in progress: wait for it to finish, or press Cancel, before changing file.”* (Generare în curs: așteaptă să se termine sau apasă Cancel înainte de a schimba fișierul.)
- **Textul se modifică în EMStudio**, nu în pyArchInit.
- Narațiunea și nodurile care o susțin (autorul AI, prompturile) **nu apar în desenul matricei**.

### 10.11 Rezolvarea problemelor

| Mesaj (en / it) | Cauză | Soluție |
|-----------------|-------|---------|
| „No AI configured…” / «Nessuna AI impostata…» | Niciuna dintre cele patru ferestre din §10.2 nu are un model (și, pentru OpenAI și Anthropic, cheia API). | Setează furnizorul și modelul — și cheia — într-una dintre acele ferestre, apoi **deschide din nou matricea**: fila recitește setările doar când se deschide. Chiar și fără AI poți pregăti capitolele, valida, exporta și deschide EMStudio. |
| „No narrative in the file…” / «Nessuna narrativa nel file…» | Fișierul nu are încă o narațiune (este normal prima dată). | Apasă **Prepare the chapters** (schelet) sau **Generate with AI** (schelet și text). N este numărul capitolelor de epocă și de activitate pe care le va avea scheletul (o epocă fără unități nu primește niciunul); mesajul „Chapters prepared” include în număr și „Presentation” și, dacă există, „Where it is”. |
| „EMStudio is not installed…” / «EMStudio non risulta installato…» | Programul nu a fost găsit pe computer. | Folosește intrarea de meniu **Extended Matrix → Installa EMStudio…** (are acest nume cu orice limbă a QGIS). |
| „truncated” / «troncato» lângă stare | Modelul s-a oprit la limita de lungime, iar textul se termină la jumătate. | Înainte de a valida, folosește **Regenerate chapter**; dacă se repetă, termină capitolul în EMStudio. |
| „N chapters generated, M failed: `<title>` — `<reason>`” / «N capitoli generati, M falliti: …» | Furnizorul a refuzat cererea (cheie nevalidă, cotă depășită, model indisponibil) sau serverul local nu răspunde. „the model wrote nothing” (modelul nu a scris nimic) înseamnă că răspunsul era gol. | Elimină cauza și apasă din nou **Generate with AI**: scrie doar capitolele rămase „to be written”. |
| „The previous file cannot be read (…)” / «Il file precedente non si legge (…)» | La reexportare, fișierul existent nu era un em.json care să poată fi citit. | Exportul a mers înainte: fișierul necitibil a fost păstrat lângă cel nou ca `….broken`, iar narațiunea pe care o conținea, dacă exista, nu a trecut în fișierul nou. Dacă ai nevoie de ea, recuperează-o din acel fișier sau dintr-un backup. |
| „The previous file's narrative (graphs: …) did not travel into the new file…” / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | Ai schimbat forma fișierului (un graf pentru fiecare sondaj ↔ un singur graf): grafurile au nume diferite și narațiunea nu poate trece. | Fișierul de dinainte se află în copia `.bak`: redenumește-o în `.em.json` și exportă din nou cu alegerea de dinainte. |
| „Could not write … The previous file is intact.” / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Salvarea a eșuat (disc plin, fișier blocat, permisiuni). | Rezolvă problema și repetă: capitolele generate în acea sesiune nu fuseseră salvate. |
| „DocX export needs python-docx — install the extra: …” (întotdeauna în engleză) | Pachetul `python-docx` nu este instalat în Python-ul QGIS: este necesar doar pentru DOCX. | Instalează `python-docx` (face parte din cerințele pluginului) sau exportă în HTML, care nu necesită nimic. |

---

## Referințe

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
