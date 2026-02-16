# Tutorial 19: Lucrul multi-utilizator cu PostgreSQL

## Introducere

PyArchInit suporta lucrul **multi-utilizator** prin utilizarea **PostgreSQL/PostGIS** ca backend pentru baza de date. Aceasta configuratie permite mai multor operatori sa lucreze simultan pe acelasi proiect arheologic de la statii de lucru diferite.

### Avantajele multi-utilizator

| Aspect | SQLite | PostgreSQL Multi-utilizator |
|--------|--------|----------------------------|
| Utilizatori simultani | 1 | Nelimitat |
| Acces la distanta | Nu | Da |
| Gestionarea permisiunilor | Nu | Da |
| Copie de siguranta centralizata | Manuala | Automatizabila |
| Performanta | Buna | Excelenta |
| Scalabilitate | Limitata | Ridicata |

## Cerinte prealabile

### Server PostgreSQL

1. **PostgreSQL** 12 sau superior
2. **PostGIS** 3.0 sau superior
3. Server accesibil in retea (LAN sau Internet)

### Client

1. QGIS cu PyArchInit instalat
2. Conexiune de retea la server
3. Credentiale de acces

## Configurarea serverului

### Instalarea PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Descarcati programul de instalare de pe [postgresql.org](https://www.postgresql.org/download/windows/)
- Instalati cu Stack Builder pentru PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Crearea bazei de date

```sql
-- Conectati-va ca superutilizator
sudo -u postgres psql

-- Crearea bazei de date
CREATE DATABASE pyarchinit_db;

-- Activarea PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Crearea utilizatorului aplicatiei
CREATE USER pyarchinit WITH PASSWORD 'parola_sigura';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Configurarea accesului in retea

Editati `pg_hba.conf`:
```
# Permiteti conexiuni din reteaua locala
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# Sau de la orice IP (mai putin sigur)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Editati `postgresql.conf`:
```
listen_addresses = '*'
```

Reporniti PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Configurarea clientului PyArchInit

### Configurare initiala

1. **PyArchInit** > **Configurare**
2. Fila **Baza de date**
3. Selectati **PostgreSQL**
4. Completati campurile:

| Camp | Valoare |
|------|---------|
| Server | Adresa IP sau numele gazdei |
| Port | 5432 (implicit) |
| Baza de date | pyarchinit_db |
| Utilizator | pyarchinit |
| Parola | parola_sigura |

### Testarea conexiunii

1. Faceti clic pe **Testare conexiune**
2. Verificati mesajul de succes
3. Salvati configuratia

### Crearea schemei

Daca este o baza de date noua:
1. Faceti clic pe **Creare schema**
2. Asteptati crearea tabelelor
3. Verificati structura

## Gestionarea utilizatorilor

### Crearea utilizatorilor suplimentari

```sql
-- Utilizator cu acces complet
CREATE USER archeolog1 WITH PASSWORD 'parola1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO archeolog1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO archeolog1;

-- Utilizator doar cu acces de citire
CREATE USER consultant1 WITH PASSWORD 'parola2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultant1;
```

### Niveluri de acces sugerate

| Rol | Permisiuni | Utilizare |
|-----|-----------|-----------|
| Administrator | ALL | Configurare, gestionare |
| Arheolog | SELECT, INSERT, UPDATE, DELETE | Lucru zilnic |
| Specialist | SELECT, INSERT, UPDATE (tabele specifice) | Introducere date specializate |
| Consultant | SELECT | Consultare date |
| Copie de siguranta | SELECT | Scripturi de copiere |

### Gestionarea rolurilor

```sql
-- Crearea unui rol de grup
CREATE ROLE archeologi;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO archeologi;

-- Atribuirea utilizatorilor la grup
GRANT archeologi TO archeolog1;
GRANT archeologi TO archeolog2;
```

## Fluxul de lucru multi-utilizator

### Organizarea muncii

#### Pe arii
- Atribuiti arii diferite operatorilor diferiti
- Evitati suprapunerile

#### Pe tip
- Un operator: US de depozit
- Alt operator: US de zid
- Alt operator: Descoperiri

#### Pe sit
- Situri diferite echipelor diferite

### Gestionarea conflictelor

#### Blocarea inregistrarilor (recomandat)
1. Inainte de modificare, verificati ca nimeni nu lucreaza pe aceeasi inregistrare
2. Comunicati cu echipa

#### Rezolvarea conflictelor
In cazul modificarilor concurente:
1. Ultima modificare prevaleaza
2. Verificati datele dupa fiecare sesiune
3. Utilizati campul "data modificarii" pentru urmarire

### Sincronizare

Cu PostgreSQL sincronizarea este automata:
- Fiecare modificare este imediat vizibila celorlalti
- Nu este necesara sincronizare manuala
- Reimprospatati formularul pentru a vedea actualizarile

## Copii de siguranta si securitate

### Copie de siguranta automata

Script de copiere zilnica:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Pastrati doar ultimele 30 de zile
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Programati cu cron:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Restaurare

```bash
# Restaurare din copia de siguranta
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Securitate

1. **Parole puternice**: Minim 12 caractere, combinatie de majuscule/minuscule/cifre
2. **Conexiuni SSL**: Activati SSL pentru conexiuni la distanta
3. **Firewall**: Limitati accesul la portul 5432
4. **Actualizari**: Mentineti PostgreSQL actualizat
5. **Jurnal de audit**: Activati jurnalizarea conexiunilor

### SSL pentru conexiuni la distanta

In `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

In `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Monitorizare

### Conexiuni active

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

### Dimensiunea bazei de date

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Blocari active

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

## Migrarea de la SQLite

### Export din SQLite

1. Deschideti PyArchInit cu baza de date SQLite
2. **PyArchInit** > **Utilitare** > **Export baza de date**
3. Exportati in format SQL

### Import in PostgreSQL

1. Configurati conexiunea PostgreSQL
2. Creati schema goala
3. Importati datele exportate

### Script de migrare

```python
# Exemplu conceptual
# Utilizati instrumente specifice de migrare
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copierea tabelelor
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Bune practici

### 1. Planificare

- Definiti rolurile si responsabilitatile
- Stabiliti conventii de lucru
- Documentati procedurile

### 2. Comunicare

- Canal de comunicare in echipa (chat, e-mail)
- Semnalati inceputul/sfarsitul sesiunilor de lucru
- Comunicati ariile care sunt modificate

### 3. Copii de siguranta

- Copii de siguranta zilnice automate
- Testare periodica a restaurarii
- Copie de siguranta in afara sitului

### 4. Instruire

- Instruire privind fluxul de lucru multi-utilizator
- Documentatia procedurilor
- Suport tehnic disponibil

## Depanare

### Conexiune refuzata

**Cauze**:
- Server inaccesibil
- Firewall care blocheaza
- Credentiale gresite

**Solutii**:
- Verificati conectivitatea retelei
- Verificati regulile firewall-ului
- Verificati credentialele

### Expirarea conexiunii

**Cauze**:
- Retea lenta
- Server suprasolcitat
- Prea multe conexiuni

**Solutii**:
- Optimizati reteaua
- Cresteti resursele serverului
- Limitati conexiunile simultane

### Blocare baza de date

**Cauza**: Tranzactii nefinalizate

**Solutie**:
```sql
-- Identificati procesele care blocheaza
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminati procesul (cu precautie)
SELECT pg_terminate_backend(pid);
```

## Referinte

### Configurare
- `modules/db/pyarchinit_conn_strings.py` - Siruri de conexiune
- `gui/pyarchinit_Setting.py` - Interfata de configurare

### Documentatie externa
- [Documentatie PostgreSQL](https://www.postgresql.org/docs/)
- [Documentatie PostGIS](https://postgis.net/documentation/)

---

## Tutorial video

### Configurare multi-utilizator
`[Placeholder: video_multiutente_setup.mp4]`

**Continut**:
- Instalarea PostgreSQL
- Configurarea serverului
- Configurarea clientului
- Gestionarea utilizatorilor

**Durata estimata**: 20-25 minute

### Flux de lucru colaborativ
`[Placeholder: video_multiutente_workflow.mp4]`

**Continut**:
- Organizarea muncii
- Gestionarea conflictelor
- Bune practici

**Durata estimata**: 12-15 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/pyarchinit_concurrency_animation.html)
