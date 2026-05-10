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

## Αναφορές

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Αποθετήριο pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
