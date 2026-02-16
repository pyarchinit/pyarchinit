# Εκπαιδευτικό 18: Αντίγραφα Ασφαλείας και Επαναφορά

## Εισαγωγή

Η διαχείριση **αντιγράφων ασφαλείας** είναι θεμελιώδης για την ασφάλεια των αρχαιολογικών δεδομένων. Το PyArchInit προσφέρει εργαλεία για τη δημιουργία αντιγράφων ασφαλείας της βάσης δεδομένων και των συσχετιζόμενων αρχείων, τόσο για SQLite όσο και για PostgreSQL.

### Σπουδαιότητα Αντιγράφων Ασφαλείας

- **Προστασία δεδομένων**: ασφάλιση έναντι τυχαίας απώλειας
- **Εκδοσιοποίηση**: δυνατότητα επιστροφής σε προηγούμενες καταστάσεις
- **Μετεγκατάσταση**: μεταφορά μεταξύ συστημάτων
- **Αρχειοθέτηση**: διατήρηση ολοκληρωμένων έργων

---

## Τύποι Αντιγράφων Ασφαλείας

### Αντίγραφο Βάσης SQLite

Για βάσεις δεδομένων SQLite (αρχεία `.sqlite`):
- Απευθείας αντιγραφή αρχείου βάσης
- Απλό και γρήγορο
- Περιλαμβάνει όλα τα δεδομένα

### Αντίγραφο Βάσης PostgreSQL

Για βάσεις δεδομένων PostgreSQL:
- Εξαγωγή μέσω `pg_dump`
- Μορφή SQL ή προσαρμοσμένη
- Μπορεί να περιλαμβάνει σχήμα ή/και δεδομένα

### Πλήρες Αντίγραφο

Περιλαμβάνει:
- Βάση δεδομένων
- Αρχεία πολυμέσων (εικόνες, βίντεο)
- Αρχεία ρυθμίσεων
- Παραγόμενες αναφορές

---

## Πρόσβαση στις Λειτουργίες Αντιγράφων Ασφαλείας

### Μέσω Πίνακα Ρυθμίσεων

1. Μενού **PyArchInit** > **Sketchy GPT** > **Settings** (ή απευθείας Settings)
2. Στο παράθυρο ρυθμίσεων
3. Καρτέλα ή ενότητα αφιερωμένη στα αντίγραφα ασφαλείας

### Μέσω Συστήματος Αρχείων

Για SQLite, μπορείτε απευθείας να αντιγράψετε:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Αντίγραφο Ασφαλείας SQLite

### Χειρονακτική Διαδικασία

1. **Κλείστε** όλα τα ανοιχτά δελτία PyArchInit
2. **Εντοπίστε** το αρχείο βάσης δεδομένων:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   Σε Windows:
   ```
   C:\Users\[user]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Αντιγράψτε** το αρχείο σε φάκελο αντιγράφων ασφαλείας:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Επαληθεύστε** την ακεραιότητα ανοίγοντας το αντίγραφο με εργαλείο SQLite

### Αυτοματοποιημένο Σενάριο (προαιρετικά)

Για αυτόματα αντίγραφα ασφαλείας, δημιουργήστε ένα σενάριο:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Backup completed: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Backup completed: %DEST%
```

---

## Αντίγραφο Ασφαλείας PostgreSQL

### Χρήση pg_dump

1. **Ανοίξτε** τερματικό/γραμμή εντολών

2. **Εκτελέστε** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Παράμετροι:
   - `-h`: κεντρικός υπολογιστής βάσης δεδομένων
   - `-U`: χρήστης
   - `-d`: όνομα βάσης δεδομένων
   - `-F c`: προσαρμοσμένη μορφή (συμπιεσμένη)
   - `-f`: αρχείο εξόδου

3. **Εισαγάγετε** τον κωδικό πρόσβασης όταν ζητηθεί

### Αντίγραφο Μόνο Δεδομένων

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_data.sql
```

### Αντίγραφο Μόνο Σχήματος

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Αντίγραφο Αρχείων Πολυμέσων

### Φάκελος Πολυμέσων

Τα αρχεία πολυμέσων βρίσκονται στον φάκελο:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Διαδικασία

1. **Εντοπίστε** τον φάκελο:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Αντιγράψτε** ολόκληρο τον φάκελο:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Συμπιέστε** (προαιρετικά):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Επαναφορά

### Επαναφορά SQLite

1. **Κλείστε** το QGIS και το PyArchInit
2. **Μετονομάστε** την τρέχουσα βάση δεδομένων (για ασφάλεια):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Αντιγράψτε** το αντίγραφο ασφαλείας στον αρχικό φάκελο:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Επανεκκινήστε** το QGIS

### Επαναφορά PostgreSQL

1. **Δημιουργήστε** μια κενή βάση δεδομένων (εάν χρειάζεται):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Επαναφέρετε** το αντίγραφο ασφαλείας:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Ενημερώστε** τις ρυθμίσεις PyArchInit για χρήση της νέας βάσης

### Επαναφορά Αρχείων Πολυμέσων

1. **Αντιγράψτε** τα αρχεία αντιγράφου ασφαλείας στον φάκελο πολυμέσων:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Πλήρες Αντίγραφο Έργου

### Τι να Συμπεριλάβετε

| Στοιχείο | Διαδρομή |
|----------|----------|
| Βάση δεδομένων SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Πολυμέσα | `pyarchinit_image_folder/` |
| Παραγόμενα PDF | `pyarchinit_PDF_folder/` |
| Αναφορές | `pyarchinit_Report_folder/` |
| Ρυθμίσεις | `pyarchinit_Logo_folder/`, αρχεία .txt |

### Σενάριο Πλήρους Αντιγράφου

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Βάση δεδομένων
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Πολυμέσα
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF και Αναφορές
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Συμπίεση
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Complete backup: $BACKUP_DIR.tar.gz"
```

---

## Βέλτιστες Πρακτικές

### Συχνότητα Αντιγράφων

| Τύπος Δραστηριότητας | Συνιστώμενη Συχνότητα |
|----------------------|----------------------|
| Ενεργή ανασκαφή | Καθημερινά |
| Μετα-ανασκαφική επεξεργασία | Εβδομαδιαία |
| Αρχειοθέτηση | Πριν από κάθε σημαντική αλλαγή |

### Διατήρηση

- Κρατήστε τουλάχιστον **3 αντίγραφα** σε διαφορετικές τοποθεσίες
- Χρησιμοποιήστε **αποθήκευση νέφους** για πλεονασμό
- **Επαληθεύστε περιοδικά** την ακεραιότητα αντιγράφων

### Ονοματολογία

Συνιστώμενη μορφή:
```
[project]_[type]_[date]_[version]
Παράδειγμα: roman_villa_db_20240115_v1.sqlite
```

### Τεκμηρίωση

Δημιουργήστε αρχείο καταγραφής αντιγράφων:
```
Ημερομηνία: 2024-01-15
Τύπος: Πλήρες αντίγραφο
Αρχείο: roman_villa_backup_20240115.tar.gz
Μέγεθος: 2.5 GB
Σημειώσεις: Πριν το κλείσιμο ανασκαφικής περιόδου 2024
```

---

## Αυτοματοποίηση Αντιγράφων

### Cron Job (Linux/Mac)

Προσθέστε στο crontab (`crontab -e`):
```
# Καθημερινό αντίγραφο στις 23:00
0 23 * * * /path/to/backup_script.sh
```

### Task Scheduler (Windows)

1. Ανοίξτε τον **Προγραμματιστή Εργασιών** (Task Scheduler)
2. Δημιουργήστε βασική εργασία
3. Ορίστε ενεργοποίηση (καθημερινά)
4. Ενέργεια: Εκκίνηση προγράμματος > σενάριο batch

---

## Αντιμετώπιση Προβλημάτων

### Πρόβλημα: Κατεστραμμένη βάση δεδομένων μετά την επαναφορά

**Αιτία**: Ελλιπές ή κατεστραμμένο αρχείο αντιγράφου.

**Λύση**:
1. Επαληθεύστε ακεραιότητα με `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Χρησιμοποιήστε προηγούμενο αντίγραφο
3. Επιχειρήστε ανάκτηση με εργαλεία SQLite

### Πρόβλημα: Υπερβολικό μέγεθος αντιγράφου

**Αιτία**: Πολλά αρχεία πολυμέσων ή πολύ μεγάλη βάση δεδομένων.

**Λύση**:
1. Συμπίεση αντιγράφων
2. Εκτέλεση VACUUM στη βάση δεδομένων
3. Αρχειοθέτηση παλαιότερων πολυμέσων ξεχωριστά

### Πρόβλημα: Σφάλμα σύνδεσης pg_dump

**Αιτία**: Εσφαλμένες παράμετροι σύνδεσης.

**Λύση**:
1. Επαληθεύστε host, port, user
2. Ελέγξτε το pg_hba.conf για δικαιώματα
3. Δοκιμάστε σύνδεση με psql

---

## Μετεγκατάσταση Μεταξύ Βάσεων Δεδομένων

### Από SQLite σε PostgreSQL

1. Εξαγωγή δεδομένων από SQLite
2. Δημιουργία σχήματος σε PostgreSQL
3. Εισαγωγή δεδομένων

Το PyArchInit διαχειρίζεται αυτό μέσω ρυθμίσεων.

### Από PostgreSQL σε SQLite

1. Εξαγωγή δεδομένων από PostgreSQL
2. Δημιουργία βάσης SQLite
3. Εισαγωγή δεδομένων

---

## Αναφορές

### Τυπικές Διαδρομές

| Σύστημα | Βασική Διαδρομή |
|---------|-----------------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[user]\pyarchinit\` |

### Χρήσιμα Εργαλεία

- **SQLite Browser**: Προβολή/επεξεργασία βάσης SQLite
- **pgAdmin**: Διαχείριση PostgreSQL
- **7-Zip/tar**: Συμπίεση αντιγράφων
- **rsync**: Σταδιακός συγχρονισμός

---

## Βιντεοεκπαίδευση

### Αντίγραφα Ασφαλείας και Ασφάλεια Δεδομένων
**Διάρκεια**: 10-12 λεπτά
- Διαδικασίες αντιγράφων ασφαλείας
- Επαναφορά βάσης δεδομένων
- Αυτοματοποίηση

[Video placeholder: video_backup_restore.mp4]

---

*Τελευταία ενημέρωση: Ιανουάριος 2026*
*PyArchInit - Σύστημα Διαχείρισης Αρχαιολογικών Δεδομένων*
