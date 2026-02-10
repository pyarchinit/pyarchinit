# Tutorial 19: Lavoro Multi-utente con PostgreSQL

## Introduzione

PyArchInit supporta il lavoro **multi-utente** attraverso l'utilizzo di **PostgreSQL/PostGIS** come database backend. Questa configurazione permette a piu operatori di lavorare contemporaneamente sullo stesso progetto archeologico da postazioni diverse.

### Vantaggi del Multi-utente

| Aspetto | SQLite | PostgreSQL Multi-utente |
|---------|--------|------------------------|
| Utenti simultanei | 1 | Illimitati |
| Accesso remoto | No | Si |
| Gestione permessi | No | Si |
| Backup centralizzato | Manuale | Automatizzabile |
| Prestazioni | Buone | Ottime |
| Scalabilita | Limitata | Elevata |

## Prerequisiti

### Server PostgreSQL

1. **PostgreSQL** 12 o superiore
2. **PostGIS** 3.0 o superiore
3. Server accessibile in rete (LAN o Internet)

### Client

1. QGIS con PyArchInit installato
2. Connessione di rete al server
3. Credenziali di accesso

## Configurazione Server

### Installazione PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Scaricare installer da [postgresql.org](https://www.postgresql.org/download/windows/)
- Installare con Stack Builder per PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Creazione Database

```sql
-- Connettersi come superuser
sudo -u postgres psql

-- Creare database
CREATE DATABASE pyarchinit_db;

-- Abilitare PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Creare utente applicazione
CREATE USER pyarchinit WITH PASSWORD 'password_sicura';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Configurazione Accesso Rete

Modificare `pg_hba.conf`:
```
# Permettere connessioni dalla rete locale
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# O da qualsiasi IP (meno sicuro)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Modificare `postgresql.conf`:
```
listen_addresses = '*'
```

Riavviare PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Configurazione Client PyArchInit

### Setup Iniziale

1. **PyArchInit** → **Configurazione**
2. Tab **Database**
3. Selezionare **PostgreSQL**
4. Compilare i campi:

| Campo | Valore |
|-------|--------|
| Server | Indirizzo IP o hostname |
| Porta | 5432 (default) |
| Database | pyarchinit_db |
| Utente | pyarchinit |
| Password | password_sicura |

### Test Connessione

1. Cliccare **Test Connessione**
2. Verificare messaggio di successo
3. Salvare configurazione

### Creazione Schema

Se database nuovo:
1. Cliccare **Crea Schema**
2. Attendere creazione tabelle
3. Verificare struttura

## Gestione Utenti

### Creazione Utenti Aggiuntivi

```sql
-- Utente con accesso completo
CREATE USER archeologo1 WITH PASSWORD 'password1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO archeologo1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO archeologo1;

-- Utente in sola lettura
CREATE USER consulente1 WITH PASSWORD 'password2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consulente1;
```

### Livelli di Accesso Suggeriti

| Ruolo | Permessi | Utilizzo |
|-------|----------|----------|
| Admin | ALL | Configurazione, gestione |
| Archeologo | SELECT, INSERT, UPDATE, DELETE | Lavoro quotidiano |
| Specialista | SELECT, INSERT, UPDATE (tabelle specifiche) | Inserimento dati specialistici |
| Consulente | SELECT | Consultazione dati |
| Backup | SELECT | Script di backup |

### Gestione Ruoli

```sql
-- Creare ruolo gruppo
CREATE ROLE archeologi;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO archeologi;

-- Assegnare utenti al gruppo
GRANT archeologi TO archeologo1;
GRANT archeologi TO archeologo2;
```

## Workflow Multi-utente

### Organizzazione Lavoro

#### Per Area
- Assegnare aree diverse a operatori diversi
- Evitare sovrapposizioni

#### Per Tipologia
- Un operatore: US deposito
- Altro operatore: US murarie
- Altro operatore: Reperti

#### Per Sito
- Siti diversi a team diversi

### Gestione Conflitti

#### Blocco Record (consigliato)
1. Prima di modificare, verificare che nessuno stia lavorando sullo stesso record
2. Comunicare con il team

#### Risoluzione Conflitti
In caso di modifiche concorrenti:
1. L'ultima modifica prevale
2. Verificare i dati dopo ogni sessione
3. Usare il campo "data modifica" per tracciare

### Sincronizzazione

Con PostgreSQL la sincronizzazione e automatica:
- Ogni modifica e immediatamente visibile agli altri
- Non serve sincronizzazione manuale
- Refresh della scheda per vedere aggiornamenti

## Backup e Sicurezza

### Backup Automatico

Script di backup giornaliero:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Mantenere solo ultimi 30 giorni
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Schedulare con cron:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Restore

```bash
# Restore da backup
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Sicurezza

1. **Password forti**: Minimo 12 caratteri, mix maiuscole/minuscole/numeri
2. **Connessioni SSL**: Abilitare SSL per connessioni remote
3. **Firewall**: Limitare accesso alla porta 5432
4. **Aggiornamenti**: Mantenere PostgreSQL aggiornato
5. **Audit log**: Abilitare logging delle connessioni

### SSL per Connessioni Remote

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

## Monitoraggio

### Connessioni Attive

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

### Dimensione Database

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Lock Attivi

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

## Migrazione da SQLite

### Export da SQLite

1. Aprire PyArchInit con database SQLite
2. **PyArchInit** → **Utilities** → **Export Database**
3. Esportare in formato SQL

### Import in PostgreSQL

1. Configurare connessione PostgreSQL
2. Creare schema vuoto
3. Importare dati esportati

### Script Migrazione

```python
# Esempio concettuale
# Usare strumenti specifici di migrazione
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copiare tabelle
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Best Practices

### 1. Pianificazione

- Definire ruoli e responsabilita
- Stabilire convenzioni di lavoro
- Documentare procedure

### 2. Comunicazione

- Canale di comunicazione team (chat, email)
- Segnalare inizio/fine sessioni di lavoro
- Comunicare aree in modifica

### 3. Backup

- Backup giornalieri automatici
- Test periodico restore
- Backup off-site

### 4. Formazione

- Training su workflow multi-utente
- Documentazione procedure
- Supporto tecnico disponibile

## Risoluzione Problemi

### Connessione Rifiutata

**Cause**:
- Server non raggiungibile
- Firewall bloccante
- Credenziali errate

**Soluzioni**:
- Verificare connettivita rete
- Controllare regole firewall
- Verificare credenziali

### Timeout Connessione

**Cause**:
- Rete lenta
- Server sovraccarico
- Troppe connessioni

**Soluzioni**:
- Ottimizzare rete
- Aumentare risorse server
- Limitare connessioni simultanee

### Lock Database

**Causa**: Transazioni non completate

**Soluzione**:
```sql
-- Identificare processi bloccanti
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminare processo (con cautela)
SELECT pg_terminate_backend(pid);
```

## Riferimenti

### Configurazione
- `modules/db/pyarchinit_conn_strings.py` - Stringhe connessione
- `gui/pyarchinit_Setting.py` - Interfaccia configurazione

### Documentazione Esterna
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## Video Tutorial

### Setup Multi-utente
`[Placeholder: video_multiutente_setup.mp4]`

**Contenuti**:
- Installazione PostgreSQL
- Configurazione server
- Setup client
- Gestione utenti

**Durata prevista**: 20-25 minuti

### Workflow Collaborativo
`[Placeholder: video_multiutente_workflow.mp4]`

**Contenuti**:
- Organizzazione lavoro
- Gestione conflitti
- Best practices

**Durata prevista**: 12-15 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../animations/pyarchinit_concurrency_animation.html)
