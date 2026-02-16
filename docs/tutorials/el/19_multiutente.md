# Εκπαιδευτικό 19: Πολυχρηστική Εργασία με PostgreSQL

## Εισαγωγή

Το PyArchInit υποστηρίζει **πολυχρηστική** εργασία μέσω της χρήσης **PostgreSQL/PostGIS** ως υποδομής βάσης δεδομένων. Αυτή η ρύθμιση επιτρέπει σε πολλούς χειριστές να εργάζονται ταυτόχρονα στο ίδιο αρχαιολογικό έργο από διαφορετικούς σταθμούς εργασίας.

### Πλεονεκτήματα Πολυχρηστικής Εργασίας

| Πτυχή | SQLite | PostgreSQL Πολυχρηστικό |
|-------|--------|------------------------|
| Ταυτόχρονοι χρήστες | 1 | Απεριόριστοι |
| Απομακρυσμένη πρόσβαση | Όχι | Ναι |
| Διαχείριση δικαιωμάτων | Όχι | Ναι |
| Κεντρικό αντίγραφο | Χειρονακτικό | Αυτοματοποιημένο |
| Απόδοση | Καλή | Εξαιρετική |
| Κλιμακωσιμότητα | Περιορισμένη | Υψηλή |

## Προαπαιτούμενα

### Εξυπηρετητής PostgreSQL

1. **PostgreSQL** 12 ή νεότερο
2. **PostGIS** 3.0 ή νεότερο
3. Εξυπηρετητής προσβάσιμος στο δίκτυο (LAN ή Internet)

### Πελάτης

1. QGIS με εγκατεστημένο PyArchInit
2. Σύνδεση δικτύου με τον εξυπηρετητή
3. Διαπιστευτήρια πρόσβασης

## Ρύθμιση Εξυπηρετητή

### Εγκατάσταση PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Κατεβάστε τον εγκαταστάτη από [postgresql.org](https://www.postgresql.org/download/windows/)
- Εγκαταστήστε με Stack Builder για PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Δημιουργία Βάσης Δεδομένων

```sql
-- Σύνδεση ως υπερχρήστης
sudo -u postgres psql

-- Δημιουργία βάσης δεδομένων
CREATE DATABASE pyarchinit_db;

-- Ενεργοποίηση PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Δημιουργία χρήστη εφαρμογής
CREATE USER pyarchinit WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Ρύθμιση Πρόσβασης Δικτύου

Επεξεργασία `pg_hba.conf`:
```
# Επιτρέψτε συνδέσεις από τοπικό δίκτυο
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# Ή από οποιαδήποτε IP (λιγότερο ασφαλές)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Επεξεργασία `postgresql.conf`:
```
listen_addresses = '*'
```

Επανεκκίνηση PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Ρύθμιση Πελάτη PyArchInit

### Αρχική Εγκατάσταση

1. **PyArchInit** → **Configuration**
2. Καρτέλα **Database**
3. Επιλέξτε **PostgreSQL**
4. Συμπληρώστε τα πεδία:

| Πεδίο | Τιμή |
|-------|------|
| Server | Διεύθυνση IP ή hostname |
| Port | 5432 (προεπιλογή) |
| Database | pyarchinit_db |
| User | pyarchinit |
| Password | secure_password |

### Δοκιμή Σύνδεσης

1. Κάντε κλικ στο **Test Connection**
2. Επαληθεύστε το μήνυμα επιτυχίας
3. Αποθηκεύστε τη ρύθμιση

### Δημιουργία Σχήματος

Εάν η βάση είναι νέα:
1. Κάντε κλικ στο **Create Schema**
2. Περιμένετε τη δημιουργία πινάκων
3. Επαληθεύστε τη δομή

## Διαχείριση Χρηστών

### Δημιουργία Πρόσθετων Χρηστών

```sql
-- Χρήστης με πλήρη πρόσβαση
CREATE USER archaeologist1 WITH PASSWORD 'password1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO archaeologist1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO archaeologist1;

-- Χρήστης μόνο για ανάγνωση
CREATE USER consultant1 WITH PASSWORD 'password2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultant1;
```

### Προτεινόμενα Επίπεδα Πρόσβασης

| Ρόλος | Δικαιώματα | Χρήση |
|-------|-----------|-------|
| Διαχειριστής | ALL | Ρύθμιση, διαχείριση |
| Αρχαιολόγος | SELECT, INSERT, UPDATE, DELETE | Καθημερινή εργασία |
| Ειδικός | SELECT, INSERT, UPDATE (συγκεκριμένοι πίνακες) | Εξειδικευμένη εισαγωγή δεδομένων |
| Σύμβουλος | SELECT | Συμβουλή δεδομένων |
| Αντίγραφο | SELECT | Σενάρια αντιγράφων ασφαλείας |

### Διαχείριση Ρόλων

```sql
-- Δημιουργία ρόλου ομάδας
CREATE ROLE archaeologists;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO archaeologists;

-- Αντιστοίχιση χρηστών σε ομάδα
GRANT archaeologists TO archaeologist1;
GRANT archaeologists TO archaeologist2;
```

## Πολυχρηστική Ροή Εργασίας

### Οργάνωση Εργασίας

#### Ανά Τομέα
- Αντιστοίχιση διαφορετικών τομέων σε διαφορετικούς χειριστές
- Αποφυγή επικαλύψεων

#### Ανά Τύπο
- Ένας χειριστής: ΣΕ αποθέσεων
- Άλλος χειριστής: ΣΕ τοίχων
- Άλλος χειριστής: Ευρήματα

#### Ανά Θέση
- Διαφορετικές θέσεις σε διαφορετικές ομάδες

### Διαχείριση Συγκρούσεων

#### Κλείδωμα Εγγραφών (συνιστάται)
1. Πριν από την τροποποίηση, επαληθεύστε ότι κανείς δεν εργάζεται στην ίδια εγγραφή
2. Επικοινωνήστε με την ομάδα

#### Επίλυση Συγκρούσεων
Σε περίπτωση ταυτόχρονων τροποποιήσεων:
1. Η τελευταία τροποποίηση υπερισχύει
2. Επαληθεύστε τα δεδομένα μετά από κάθε περίοδο εργασίας
3. Χρησιμοποιήστε το πεδίο «ημερομηνία τροποποίησης» για παρακολούθηση

### Συγχρονισμός

Με PostgreSQL ο συγχρονισμός είναι αυτόματος:
- Κάθε τροποποίηση είναι αμέσως ορατή στους άλλους
- Δεν απαιτείται χειρονακτικός συγχρονισμός
- Ανανεώστε το δελτίο για να δείτε ενημερώσεις

## Αντίγραφα Ασφαλείας και Ασφάλεια

### Αυτόματο Αντίγραφο

Σενάριο καθημερινού αντιγράφου:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Διατήρηση μόνο τελευταίων 30 ημερών
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Προγραμματισμός με cron:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Επαναφορά

```bash
# Επαναφορά από αντίγραφο
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Ασφάλεια

1. **Ισχυροί κωδικοί πρόσβασης**: Ελάχιστο 12 χαρακτήρες, μίξη κεφαλαίων/πεζών/αριθμών
2. **Συνδέσεις SSL**: Ενεργοποίηση SSL για απομακρυσμένες συνδέσεις
3. **Τείχος προστασίας**: Περιορισμός πρόσβασης στη θύρα 5432
4. **Ενημερώσεις**: Διατηρήστε ενημερωμένο το PostgreSQL
5. **Αρχείο ελέγχου**: Ενεργοποίηση καταγραφής συνδέσεων

### SSL για Απομακρυσμένες Συνδέσεις

Στο `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

Στο `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Παρακολούθηση

### Ενεργές Συνδέσεις

```sql
SELECT
    usename,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE datname = 'pyarchinit_db';
```

### Μέγεθος Βάσης Δεδομένων

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Ενεργά Κλειδώματα

```sql
SELECT
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted,
    a.usename,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = 'pyarchinit_db');
```

## Μετεγκατάσταση από SQLite

### Εξαγωγή από SQLite

1. Ανοίξτε το PyArchInit με βάση SQLite
2. **PyArchInit** → **Utilities** → **Export Database**
3. Εξαγωγή σε μορφή SQL

### Εισαγωγή στο PostgreSQL

1. Ρυθμίστε τη σύνδεση PostgreSQL
2. Δημιουργήστε κενό σχήμα
3. Εισαγάγετε τα εξαγόμενα δεδομένα

### Σενάριο Μετεγκατάστασης

```python
# Εννοιολογικό παράδειγμα
# Χρησιμοποιήστε ειδικά εργαλεία μετεγκατάστασης
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Αντιγραφή πινάκων
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Βέλτιστες Πρακτικές

### 1. Σχεδιασμός

- Ορίστε ρόλους και αρμοδιότητες
- Καθιερώστε συμβάσεις εργασίας
- Τεκμηριώστε τις διαδικασίες

### 2. Επικοινωνία

- Κανάλι επικοινωνίας ομάδας (chat, email)
- Ειδοποίηση έναρξης/τέλους περιόδων εργασίας
- Κοινοποίηση τομέων υπό τροποποίηση

### 3. Αντίγραφα Ασφαλείας

- Καθημερινά αυτόματα αντίγραφα
- Περιοδικός έλεγχος επαναφοράς
- Αντίγραφο εκτός τοποθεσίας

### 4. Εκπαίδευση

- Εκπαίδευση στην πολυχρηστική ροή εργασίας
- Τεκμηρίωση διαδικασιών
- Διαθέσιμη τεχνική υποστήριξη

## Αντιμετώπιση Προβλημάτων

### Σύνδεση Απορρίφθηκε

**Αιτίες**:
- Μη προσβάσιμος εξυπηρετητής
- Τείχος προστασίας που μπλοκάρει
- Λανθασμένα διαπιστευτήρια

**Λύσεις**:
- Επαληθεύστε τη συνδεσιμότητα δικτύου
- Ελέγξτε τους κανόνες τείχους προστασίας
- Επαληθεύστε τα διαπιστευτήρια

### Λήξη Χρόνου Σύνδεσης

**Αιτίες**:
- Αργό δίκτυο
- Υπερφορτωμένος εξυπηρετητής
- Πάρα πολλές συνδέσεις

**Λύσεις**:
- Βελτιστοποίηση δικτύου
- Αύξηση πόρων εξυπηρετητή
- Περιορισμός ταυτόχρονων συνδέσεων

### Κλείδωμα Βάσης Δεδομένων

**Αιτία**: Μη ολοκληρωμένες συναλλαγές

**Λύση**:
```sql
-- Αναγνώριση διεργασιών που μπλοκάρουν
SELECT * FROM pg_locks WHERE NOT granted;

-- Τερματισμός διεργασίας (με προσοχή)
SELECT pg_terminate_backend(pid);
```

## Αναφορές

### Ρυθμίσεις
- `modules/db/pyarchinit_conn_strings.py` - Συμβολοσειρές σύνδεσης
- `gui/pyarchinit_Setting.py` - Διεπαφή ρυθμίσεων

### Εξωτερική Τεκμηρίωση
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## Βιντεοεκπαίδευση

### Εγκατάσταση Πολυχρηστικού Περιβάλλοντος
`[Placeholder: video_multiutente_setup.mp4]`

**Περιεχόμενα**:
- Εγκατάσταση PostgreSQL
- Ρύθμιση εξυπηρετητή
- Εγκατάσταση πελάτη
- Διαχείριση χρηστών

**Αναμενόμενη διάρκεια**: 20-25 λεπτά

### Συνεργατική Ροή Εργασίας
`[Placeholder: video_multiutente_workflow.mp4]`

**Περιεχόμενα**:
- Οργάνωση εργασίας
- Διαχείριση συγκρούσεων
- Βέλτιστες πρακτικές

**Αναμενόμενη διάρκεια**: 12-15 λεπτά

---

*Τελευταία ενημέρωση: Ιανουάριος 2026*

---

## Διαδραστική Κινούμενη Εικόνα

Εξερευνήστε τη διαδραστική κινούμενη εικόνα για να μάθετε περισσότερα σχετικά με αυτό το θέμα.

[Open Interactive Animation](../../animations/pyarchinit_concurrency_animation.html)
