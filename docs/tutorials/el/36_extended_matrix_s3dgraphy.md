# Οδηγός 36: Εξαγωγή Extended Matrix και Γέφυρα s3dgraphy

## Εισαγωγή

Από την έκδοση **5.2.0-alpha** το PyArchInit ενσωματώνει μια **αμφίδρομη γέφυρα** με τη βιβλιοθήκη **s3dgraphy** (μοντέλο δεδομένων Extended Matrix του Emanuel Demetrescu). Η γέφυρα επιτρέπει:

- **Εξαγωγή** του στρωματογραφικού διαγράμματος ως Extended Matrix σε GraphML (με χρονικά swimlanes, μεταβατική μείωση, edge styling EM 1.5)
- **Επανεισαγωγή** τροποποιήσεων που έγιναν στο yEd (μετακινήσεις ΣΕ μεταξύ περιόδων/ομάδων) ενημερώνοντας τη βάση δεδομένων SQL
- **Επισύναψη paradata** (Author / License / Embargo) σε επίπεδο τοποθεσίας
- **Ομαδοποίηση** ΣΕ ανά διάσταση (struttura, area, attivita, settore, ambient, saggio, quad_par ή ad-hoc ομάδες)

Τρέχουσα ετικέτα: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Προαπαιτούμενα

- Βάση δεδομένων SQLite (PostgreSQL μη υποστηριζόμενη ακόμη)
- **Phase 1 node_uuid migration** εφαρμόζεται αυτόματα κατά το άνοιγμα της βάσης
- **yEd Graph Editor** για προβολή της εξόδου (https://www.yworks.com/products/yed)

> ⚠️ Για βάσεις pre-5.2.0-alpha η migration μπορεί να απαιτήσει επανεκκίνηση του QGIS.

---

## 2. Εξαγωγή Extended Matrix (πράσινο κουμπί)

### 2.1 Άνοιγμα του διαλόγου

1. Άνοιξε τη **Φόρμα ΣΕ** της επιθυμητής τοποθεσίας
2. Κάνε κλικ στο πράσινο κουμπί **"Esporta Extended Matrix"** (κάτω από το tab Rapporti)

### 2.2 Καρτέλα "Export"

Ο διάλογος εμφανίζει:

- **Output formats**: επιλέξτε DOT / GraphML / JSON / phased JSON (συνιστάται: GraphML)
- **Group US by (optional)**: 7 checkboxes διαστάσεων + 1 "ad-hoc"
  - Οι διαστάσεις με τιμές στη βάση **επιλέγονται αυτόματα** κατά το άνοιγμα
- **Combobox κύριας διάστασης** (προεπιλογή `struttura`): όταν μια ΣΕ έχει συμμετοχή σε 2+ διαστάσεις, η κύρια διάσταση κερδίζει ως ορατός φάκελος yEd (ιεραρχικός γονέας). Οι άλλες διαστάσεις εμφανίζονται ως inline σήματα κάτω από τον κόμβο ΣΕ. Η `toponym` ποτέ δεν είναι κύρια, ανεξάρτητα από την επιλογή.
- **"Select Output Directory"**: φάκελος προορισμού

Από 5.6.0-alpha μπορείτε να επιλέξετε **2+ διαστάσεις**: η εξαγωγή λειτουργεί εγγενώς χάρη στο μοντέλο m:n με `is_primary` (δείτε ενότητα "Πολυδιάστατη ένταξη").

### 2.3 Κλικ στο "Export"

Δημιουργούνται 4 αρχεία με πρόθεμα `Extended_Matrix_<θέση>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix για yEd (κύριος στόχος)
- `_s3dgraphy.json` — εγγενής μορφή s3dgraphy
- `_phased.json` — προβολή ανά εποχή

---

## 3. Διάλογος "Manage paradata" (4 καρτέλες)

### 3.1 Πρόσβαση
Κάντε κλικ στο κουμπί **"Manage paradata"** στη φόρμα ΣΕ (δίπλα στο πράσινο κουμπί Export).

### 3.2 Οι 4 καρτέλες

| Καρτέλα | Περιεχόμενο | Παραγόμενο αρχείο |
|---|---|---|
| **Authors** | Προσθήκη συγγραφέων (όνομα + ORCID + ρόλος) | `paradata_<θέση>.graphml` |
| **Licenses** | Άδεια dataset (π.χ. CC-BY-NC-4.0 + URL) | ίδιο |
| **Embargoes** | Ημερομηνίες embargo + αιτιολογία | ίδιο |
| **Groups** | Ομάδες ad-hoc (όνομα + επιλογή ΣΕ μελών) | `groups_<θέση>.graphml` |

Τα αρχεία αποθηκεύονται δίπλα στη βάση SQLite και είναι **διαχειρίσιμα στο Git**.

---

## 4. Οπτικό στυλ ανά διάσταση (5.5.1-alpha + 5.6.0-alpha)

Κάθε διάσταση ομαδοποίησης έχει ξεχωριστό χρώμα στο GraphML:

| Διάσταση | Fill (50% διαφάνεια) | Border |
|---|---|---|
| `area` | παστέλ ροζ `#FFE0E680` | `#C84A5F` |
| `struttura` | παστέλ πορτοκαλί `#FFE6CC80` | `#C66B33` |
| `attivita` | παστέλ κίτρινο `#FFF5CC80` | `#A89A33` |
| `settore` | παστέλ πράσινο `#E6FFCC80` | `#6BC633` |
| `ambient` | παστέλ aqua `#CCFFE680` | `#33A86B` |
| `saggio` | παστέλ γαλάζιο `#CCF5FF80` | `#3389A8` |
| `quad_par` | παστέλ βιολετί `#E0CCFF80` | `#6633C6` |
| `adhoc` | παστέλ γκρι `#F5F5F580` | `#666666` |

Από 5.6.0-alpha, τα `LocationNodeGroup` διακρίνονται από το `kind`:

| `kind` | Fill (50% διαφάνεια) | Border |
|---|---|---|
| `toponym` | παστέλ λεβάντα `#E6E6FA80` | `#9370DB` |
| `study` | παστέλ ιβουάρ `#FFFFE080` | `#888888` |
| `functional` | παστέλ κυανό `#E0FFFF80` | `#008B8B` |

Το alpha 50% αφήνει ορατές τις swimlanes των εποχών πίσω από το ορθογώνιο της ομάδας.

### 4.1 Αλυσίδα τοπωνυμίων (5.6.0-alpha)

Τα πεδία `site_table.{nazione, regione, provincia, comune}` εκπέμπονται αυτόματα ως αναδρομική αλυσίδα `LocationNodeGroup(kind="toponym")` (γονέας: nazione → regione → provincia → comune). Τα κενά διοικητικά επίπεδα παραλείπονται χωρίς να σπάσει η αλυσίδα. Μια cross-site αποπολλαπλασίαση εγγυάται ότι η ίδια `comune` που υπάρχει σε 2 sites γίνεται **ένας μοιραζόμενος κόμβος** στο GraphML.

---

## 4.2 Πολυδιάστατη ένταξη (5.6.0-alpha)

Από 5.6.0-alpha μια ΣΕ μπορεί να ανήκει σε **πολλαπλές διαστάσεις ταυτόχρονα** χάρη στο μοντέλο m:n με τη σημαία `is_primary`. Μόνο η κύρια διάσταση γίνεται ο ορατός φάκελος yEd· οι άλλες εμφανίζονται ως **inline σήματα** κάτω από τον κόμβο ΣΕ και ως JSON στο `<data key="s3d:other_locations">` για downstream εργαλεία.

Παράδειγμα: μια ΣΕ με `struttura=basilica` και `area=B` (κύρια `struttura`) δίνει:
- φάκελο yEd "struttura: basilica" ως ορατό γονέα·
- κάτω από τον κόμβο ΣΕ, ένα inline σήμα `also: B (study), TestCity (toponym)`·
- στο GraphML, το χαρακτηριστικό `s3d:other_locations` με JSON πίνακα των δευτερευουσών εντάξεων.

Η κύρια διάσταση ελέγχεται μέσω του combobox στην §2.2.

---

## 5. Round-trip (καρτέλα Import)

Για τροποποίηση της βάσης SQL μετακινώντας ΣΕ μεταξύ ομάδων στο GraphML:

1. Άνοιξε το GraphML στο **yEd**
2. Σύρε μια ΣΕ σε άλλη ομάδα, αποθήκευσε
3. Επιστροφή στον διάλογο → καρτέλα **"Import"**
4. **Επίλεξε** το checkbox *"Update SQL on import (struttura/area/...)"*
5. Φόρτωσε το τροποποιημένο GraphML

Το σύστημα εκτελεί ατομική συναλλαγή: σε αποτυχία, **πλήρες rollback** (η βάση παραμένει αμετάβλητη). Οι ομάδες `adhoc` ποτέ δεν γράφουν SQL — ενημερώνουν μόνο το `groups_<θέση>.graphml`.

Από 5.6.0-alpha ο walker εισαγωγής είναι **αναδρομικός** και υποστηρίζει εμφωλευμένους φακέλους (π.χ. αλυσίδα τοπωνυμίων `nazione > regione > provincia > comune > ΣΕ`). Όταν εντοπίζονται κύκλοι στο γράφο φακέλων, σηκώνεται η εξαίρεση `CycleDetectedError` και η εισαγωγή ακυρώνεται με rollback.

---

## 6. CLI (εναλλακτική στον διάλογο)

Για scripts / batch:

```bash
# Εξαγωγή
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Λίστα ad-hoc ομάδων
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Προσθήκη συγγραφέα
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = επιτυχία, 1 = σφάλμα γέφυρας, 2 = σφάλμα argparse.

---

## 7. Επίλυση προβλημάτων

| Σύμπτωμα | Αιτία | Λύση |
|---|---|---|
| "no such column: node_uuid" | Phase 1 migration δεν εκτελέστηκε | Επανεκκίνηση QGIS, επανάνοιγμα βάσης |
| Άδειο GraphML | Βάση χωρίς rapporti / area filter πολύ αυστηρό | Έλεγξε us_table.rapporti |
| "rapporti πρέπει να είναι TEXT" | Έβαλες αριθμό ως integer | Τα πεδία ΣΕ/Area είναι **TEXT**, όχι integer |
| Λάθος κεφαλαία/πεζά στα rapporti | "copre" με μικρά στη βάση | Χρησιμοποίησε "Copre", "Coperto da" κεφαλαιοποιημένα |
| `DeprecationWarning` σε αρχείο 5.5.x | Παλαιότερο αρχείο `ActivityNodeGroup + group_kind` | Ο projector το προάγει στη μνήμη σε `LocationNodeGroup`. Ξανα-εξάγετε για να μεταφερθεί το αρχείο στον δίσκο. |

---

## 8. Τεχνική τεκμηρίωση

Για βαθύτερη ανάλυση αρχιτεκτονικής, αποφάσεων σχεδίασης και roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Αναβληθέντα carry-over:
- **AI08-F3**: ευρετικές auto-layout (bin-packing υπο-ομάδων) — εξακολουθεί να αναβάλλεται
- **AI09**: TimeBranchNodeGroup mapping — μελλοντικό
- **Phase 3**: SyncEngine + REST API — μελλοντικό
- **Phase 4**: GraphDBBackend + SPARQL — μελλοντικό

Παραδόθηκαν:
- **AI07** (5.6.0-alpha, 2026-05-10): migration `LocationNodeGroup` με enum `kind` + αλυσίδα τοπωνυμίων + πολυδιάστατες εντάξεις
- **AI08-F1** (συγχωνεύθηκε στο AI07): εγγενής ιεραρχική φωλιά μέσω `is_primary`

---

## 5. yEd-aware Import — εισαγωγή graphml επεξεργασμένων εξωτερικά (5.8.x)

Από την έκδοση **5.8.0-alpha** η γέφυρα (bridge) είναι **αμφίδρομη και για graphml που δημιουργήθηκαν απευθείας στο yEd** (δηλαδή χωρίς να περάσουν πρώτα από εξαγωγή pyarchinit). Το pyarchinit αναγνωρίζει αυτόματα τα graphml «yEd-raw» — αυτά που δεν φέρουν data keys `pyarchinit.*` — και τα εισάγει μέσω αποκλειστικού dispatch που χαρτογραφεί το πρόθεμα label του κόμβου → στρωματογραφικό τύπο, αναγνωρίζει τις γραμμές TableNode ως περιόδους, διασχίζει τα group folders ως αρχαιολογικές διαστάσεις και αφήνει τον χρήστη να επιλέξει πολιτική για τα edges που ακουμπούν folders.

### 5.1 Κυκλοφορία σε 6 ορόσημα

| Ορόσημο | Tag | Τι προσθέτει |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` με 13 τιμές (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex ευαίσθητο στη σειρά |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate από γραμμές TableNode) + `yed_group_walker.py` (FolderCandidate με auto-dimension από το πρόθεμα του label: VA01→attivita / AR01→area / κ.λπ.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orchestrator `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata μέσω `ParadataStore` + sentinel `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` με 5 σελίδες (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + αποθήκευση sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Αυτή η τεκμηρίωση + dev-log + CHANGELOG. |

### 5.2 Πώς δουλεύει — ροή χρήστη

1. **Ανοίξτε ένα graphml στο QGIS μέσω του μενού Import GraphML** (ίδιο path με την υπάρχουσα ροή pyarchinit-projected).
2. Το pyarchinit ανιχνεύει αυτόματα ότι είναι yEd-raw (χωρίς keys `pyarchinit.*`) → κάνει dispatch στον νέο branch αντί να πέσει στο legacy path.
3. Ανοίγει ο οδηγός `YedImportDialog` με **5 σελίδες**:
   - **1/5 Classifier** — πίνακας με μία γραμμή ανά leaf node. Κάθε γραμμή δείχνει `label` + `auto_kind` (π.χ. `us_real` / `usv_virtual` / `property`) + ένα combobox override `user_kind`. Το κουμπί **Αποδοχή auto** επαναφέρει κάθε γραμμή στο `auto_kind` (καθαρίζει όλα τα overrides).
   - **2/5 Periods** — μία γραμμή ανά TableNode-row που έχει παρσαριστεί, στήλες επεξεργάσιμες `periodo` + `fase`. Οι ημερομηνίες (`datazione_iniziale`/`finale`) παραμένουν κενές: τα graphml yEd-raw δεν φέρουν ημερομηνίες.
   - **3/5 Folders** — μία γραμμή ανά group folder. Combobox `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` για αποκλεισμό). `value` επεξεργάσιμο (default = `auto_value` που προκύπτει από το πρόθεμα του label).
   - **4/5 Rapporti policy** — 4 radio buttons για τον χειρισμό των edges που ακουμπούν folders:
     - **SKIP** (default): απορρίπτει τα edges folder-touching. Τα edges leaf-to-leaf περνούν ανέπαφα.
     - **FAN_OUT**: ένα edge `folder_A → folder_B` επεκτείνεται σε `N×M` ζεύγη leaves (καρτεσιανό γινόμενο των μελών).
     - **REPRESENTATIVE**: χρησιμοποιεί το πρώτο μέλος κάθε folder ως proxy.
     - **SYNTHETIC**: δημιουργεί μία γραμμή us_table ανά folder (`unita_tipo='VA'` virtual activity) + επανασυνδέει τα edges μέσω αυτών των αγκυρών.
   - **5/5 Preview** — dry-run του `import_yed_raw(overrides=..., dry_run=True)`. Δείχνει counts (us / inv / period / paradata) **χωρίς commit**. Κλικ στο **Finish** επικυρώνει, **Cancel** ακυρώνει.
4. Στο **Finish** ο οδηγός αποθηκεύει τα overrides σας σε ένα **sidecar JSON** `<graphml>.yed_overrides.json` δίπλα στο αρχείο. Ξανανοίγοντας το ίδιο graphml προφορτώνεται το sidecar, οπότε τα προηγούμενα overrides επιστρέφουν προεφαρμοσμένα.

### 5.3 Δρομολόγηση προορισμών

Το dispatch χρησιμοποιεί τη `_classify_destination` (στο `yed_import_pipeline.py`) για να κατατάξει κάθε leaf:

| ClassificationKind | Προορισμός | Σημείωση |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | από label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | από `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | από `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | από `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` που προκύπτει από το πρόθεμα του label: USVs/USVn/USVc) | από `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | από `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | από `^SF\d+` |
| VIRTUAL_FIND | `paradata` (μέσω `ParadataStore`) | από `^VSF\d+` |
| DOCUMENT | `paradata` | από `^D\.\d+` |
| COMBINER | `paradata` | από `^C\.\d+` |
| PROPERTY | `paradata` | keyword στο label (`material`/`position`/`width`/...) |

**Απόφαση χρήστη 2026-05-13**: οι USV* (εικονικές) είναι «unità tipo» (εξακολουθούν να είναι στρωματογραφικές μονάδες) και πάνε στον `us_table`, όχι στα paradata. Μόνο DOC/COMB/PROP/VIRTUAL_FIND παραμένουν στα paradata.

### 5.4 Sidecar JSON — σχήμα

Εκδοτικά αριθμημένο για forward-compat:

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

Αποθηκεύονται μόνο τα πεδία που ΤΡΟΠΟΠΟΙΗΣΕ ο χρήστης (diff). Άγνωστες τιμές `ClassificationKind` (π.χ. από μελλοντικές εκδόσεις του s3dgraphy) παρακάμπτονται σιωπηρά κατά τη φόρτωση.

### 5.5 CLI για scripted ingest

Για CI / επανεκτελέσεις σε batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` για backend SQLite vs PostgreSQL. Το `--overrides` είναι προαιρετικό (χωρίς overrides = defaults yE-D). Το `--auto-defaults` είναι no-op flag forward-compat.

### 5.6 Γνωστοί περιορισμοί

- **Όχι επεξεργασία ημερομηνιών στον οδηγό**: τα graphml yEd-raw δεν φέρουν `datazione_iniziale`/`datazione_finale`. Η σελίδα Periods επεξεργάζεται μόνο `periodo` + `fase` (targets FK).
- **Μερική API ParadataStore**: η upstream s3dgraphy δεν παρέχει ακόμα τα `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. Το yE-D καταγράφει «skip — method missing» για κάθε leaf paradata αλλά μετρά τις προσπάθειες στο preview.
- **PropertyNode → Path B (χωρίς σύνδεση US)**: οι κόμβοι PROPERTY γράφονται χωρίς US target. Ο οδηγός εκδίδει warning. Μέλλον: follow-up yE-Closure για προσθήκη «assign target» στο UI.
- **Multi-DB**: το sidecar JSON είναι ανά graphml, όχι ανά DB. Εισάγοντας το ίδιο graphml σε διαφορετικές DBs χρησιμοποιούνται τα ίδια overrides για όλες.

### 5.7 Τελική κάλυψη tests

| Suite | Test | Κάλυψη |
|---|---|---|
| yE-A | `test_yed_detector.py` | ανίχνευση flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex ευαίσθητο στη σειρά |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 περιλ. 2 L1 overrides e2e) | πολιτικές + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | αποθήκευση sidecar + CLI |

**Συνολική suite μετά το rollout**: 354 passed / 42 skipped (PG-L1 απαιτούν psycopg2).

### 5.8 Ενημέρωση 5.8.5-alpha (yed-fastfix)

Πακέτο διορθώσεων συμπεριφοράς πάνω από την `5.8.3-alpha` που βελτιώνει την ποιότητα του re-export GraphML μετά από ένα import yEd-aware. Αλλαγές που αφορούν τον τελικό χρήστη:

- **Paradata multi-folder**: οι ετικέτες DOC / Combinar / Extractor / property που μοιράζονται μεταξύ πολλαπλών folders yEd (π.χ. `material` που αναφέρεται από VA01 + VA04 + VA05) δημιουργούν τώρα ΜΙΑ γραμμή στο `us_table` ΑΝΑ εμφάνιση — αποκαταστάθηκε η ορατότητα multi-folder στο επανεξαγόμενο GraphML. Συμβιβασμός: το dedup ανά ταυτότητα (σύμπτυξη `D.01` / `D.01-2` / `D.01bis` σε μία γραμμή) δεν εφαρμόζεται πλέον για τη δεύτερη/τρίτη εμφάνιση.
- **Αμοιβαία rapporti**: κάθε edge yEd `a → b` γράφει το ευθύ rapporto στη γραμμή του `a` ΚΑΙ το αντίστροφο στη γραμμή του `b` (`<<` / «Coperto da» / κ.λπ.). Τα DOCs δείχνουν τώρα όλες τις εισερχόμενες συνδέσεις extractor στη φόρμα Scheda US.
- **Strip του αριθμητικού προθέματος `us`**: `US100` → `us='100'` `unita_tipo='US'` (πριν `us='US100'`). Τα SF/VSF/RSF γράφονται διπλά σε `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: η ένταξη μιας γραμμής TableNode yEd σε μια περίοδο διαδίδεται στο `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — διατηρεί τη σημασιολογική διάκριση EM 1.5.
- **Idempotent re-import**: η επανεκτέλεση του ίδιου import παραλείπει τις ήδη υπάρχουσες γραμμές· κανένα rollback για σύγκρουση UNIQUE στην επαναλαμβανόμενη διαδρομή.
- **Παλέτα USV**: οι κόμβοι USV αποδίδονται τώρα με το κανονικό μπλε παραλληλόγραμμο EM (πριν ορθογώνιο με κόκκινο περίγραμμα).

### 5.9 yE-F paradata πολλαπλών φακέλων (5.9.0-alpha)

Δομική εξέλιξη της `yed-fastfix-5.8.5-alpha`: ο συμβιβασμός του Bug R B1 (μία γραμμή `us_table` ανά εμφάνιση, με `us='D.01_2'` / `us='D.01_3'`) έχει ξεπεραστεί. Ένα φύλλο paradata (DOC / Combinar / Extractor / property) που μοιράζεται μεταξύ πολλαπλών φακέλων yEd παράγει τώρα **μία μόνο γραμμή** στο `us_table` ανά κανονικό label, και η πολλαπλή συμμετοχή διατηρείται σε μια νέα στήλη `other_locations`.

Ορατές αλλαγές για τον τελικό χρήστη:

1. **Νέο widget «Άλλες δραστηριότητες» στη φόρμα US/USM**: στην καρτέλα *Periodizzazione* εμφανίζεται ένα `QListWidget` με ετικέτα «Άλλες δραστηριότητες» — ορατό **μόνο** όταν το `unita_tipo` είναι τυπολογία paradata (`DOC`, `Combinar`, `Extractor`, `property`). Ο χρήστης μπορεί να επιλέξει πολλούς κωδικούς δραστηριότητας· η επιλογή αποθηκεύεται ως λίστα JSON στη νέα στήλη `other_locations`.
2. **Νέο στοιχείο μενού QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Πρέπει να εκτελεστεί **μία φορά** σε κάθε προϋπάρχουσα DB για την προσθήκη της νέας στήλης (οι DB που δημιουργήθηκαν μετά την 5.9 έχουν ήδη τη στήλη).
3. **Βελτιωμένο import yEd-aware**: ένα φύλλο paradata που εμφανίζεται σε N φακέλους yEd παράγει τώρα **μόνο 1** γραμμή `us_table` (όχι πλέον N γραμμές με κατάληξη `_2`/`_3` όπως στην 5.8.5). Ο πρώτος φάκελος που συναντάται γίνεται η κύρια `attivita`· οι δευτερεύοντες φάκελοι παρατίθενται στο `other_locations`. Κατά την **εξαγωγή** εκπέμπονται N οπτικά αντίγραφα yEd (ένα ανά φάκελο), όλα μοιραζόμενα το ίδιο κανονικό `node_uuid` για την εγγύηση της ταυτότητας round-trip.

**Συμβατότητα προς τα πίσω**: τα δεδομένα που παρήχθησαν από το Bug R B1 στην 5.8.5-alpha (γραμμές με κατάληξη `_2`/`_3`) παραμένουν αναγνώσιμα χωρίς αυτόματη μετατροπή. Η νέα λογική εφαρμόζεται σε νέα imports· οι γραμμές legacy συνεχίζουν να συμπεριφέρονται όπως πριν.

Προκάτοχος: βλ. ενότητα 5.8 (`yed-fastfix-5.8.5-alpha`) για τη συμπεριφορά που αντικαθίσταται.

---

## Αναφορές

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Αποθετήριο pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
