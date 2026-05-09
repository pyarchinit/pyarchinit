# Οδηγός 36: Εξαγωγή Extended Matrix και Γέφυρα s3dgraphy

## Εισαγωγή

Από την έκδοση **5.2.0-alpha** το PyArchInit ενσωματώνει μια **αμφίδρομη γέφυρα** με τη βιβλιοθήκη **s3dgraphy** (μοντέλο δεδομένων Extended Matrix του Emanuel Demetrescu). Η γέφυρα επιτρέπει:

- **Εξαγωγή** του στρωματογραφικού διαγράμματος ως Extended Matrix σε GraphML (με χρονικά swimlanes, μεταβατική μείωση, edge styling EM 1.5)
- **Επανεισαγωγή** τροποποιήσεων που έγιναν στο yEd (μετακινήσεις ΣΕ μεταξύ περιόδων/ομάδων) ενημερώνοντας τη βάση δεδομένων SQL
- **Επισύναψη paradata** (Author / License / Embargo) σε επίπεδο τοποθεσίας
- **Ομαδοποίηση** ΣΕ ανά διάσταση (struttura, area, attivita, settore, ambient, saggio, quad_par ή ad-hoc ομάδες)

Τρέχουσα ετικέτα: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

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
- **"Select Output Directory"**: φάκελος προορισμού

### 2.3 Όριο μίας διάστασης (5.5.2-alpha)

Αν επιλέξετε **2 ή περισσότερα** checkboxes ομαδοποίησης, εμφανίζεται προειδοποίηση:

> *"Εξαγωγή πολλαπλών διαστάσεων μη υποστηριζόμενη ακόμη. Συνέχεια ΜΟΝΟ με την πρώτη επιλεγμένη διάσταση;"*

Επιλέξτε **Ναι** (εξαγωγή με την πρώτη επιλεγμένη) ή **Άκυρο** (τροποποίηση επιλογής). Η ιεραρχική φωλιά (struttura > attivita > ΣΕ) έρχεται με AI08-F1.

### 2.4 Κλικ στο "Export"

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

## 4. Οπτικό στυλ ανά διάσταση (5.5.1-alpha)

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

Το alpha 50% αφήνει ορατές τις swimlanes των εποχών πίσω από το ορθογώνιο της ομάδας.

---

## 5. Round-trip (καρτέλα Import)

Για τροποποίηση της βάσης SQL μετακινώντας ΣΕ μεταξύ ομάδων στο GraphML:

1. Άνοιξε το GraphML στο **yEd**
2. Σύρε μια ΣΕ σε άλλη ομάδα, αποθήκευσε
3. Επιστροφή στον διάλογο → καρτέλα **"Import"**
4. **Επίλεξε** το checkbox *"Update SQL on import (struttura/area/...)"*
5. Φόρτωσε το τροποποιημένο GraphML

Το σύστημα εκτελεί ατομική συναλλαγή: σε αποτυχία, **πλήρες rollback** (η βάση παραμένει αμετάβλητη). Οι ομάδες `adhoc` ποτέ δεν γράφουν SQL — ενημερώνουν μόνο το `groups_<θέση>.graphml`.

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
| Άδειος φάκελος ομάδας στο yEd | Επιλέγεις 2+ διαστάσεις (όριο 5.5.2-alpha) | Επίλεξε μόνο μία, ξαναπροσπάθησε |
| "rapporti πρέπει να είναι TEXT" | Έβαλες αριθμό ως integer | Τα πεδία ΣΕ/Area είναι **TEXT**, όχι integer |
| Λάθος κεφαλαία/πεζά στα rapporti | "copre" με μικρά στη βάση | Χρησιμοποίησε "Copre", "Coperto da" κεφαλαιοποιημένα |

---

## 8. Τεχνική τεκμηρίωση

Για βαθύτερη ανάλυση αρχιτεκτονικής, αποφάσεων σχεδίασης και roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Αναβληθέντα carry-over:
- **AI07**: migration `LocationNodeGroup` (upstream deadline 2026-05-23)
- **AI08-F1**: ιεραρχική φωλιά (για καθαρή πολυδιάστατη εξαγωγή)
- **AI08-F3**: ευρετικές auto-layout (bin-packing υπο-ομάδων)
- **AI09**: TimeBranchNodeGroup mapping
- **Phase 3**: SyncEngine + REST API
- **Phase 4**: GraphDBBackend + SPARQL

---

## Αναφορές

- Upstream issue LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Αποθετήριο pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
