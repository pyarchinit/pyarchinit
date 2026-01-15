# Tutorial 18: Backup e Restore

## Introduzione

La gestione dei **backup** e fondamentale per la sicurezza dei dati archeologici. PyArchInit offre strumenti per eseguire backup del database e dei file associati, sia per SQLite che per PostgreSQL.

### Importanza del Backup

- **Protezione dati**: salvaguardia da perdite accidentali
- **Versioning**: possibilita di tornare a stati precedenti
- **Migrazione**: trasferimento tra sistemi
- **Archiviazione**: conservazione progetti completati

---

## Tipi di Backup

### Backup Database SQLite

Per database SQLite (file `.sqlite`):
- Copia diretta del file database
- Semplice e veloce
- Include tutti i dati

### Backup Database PostgreSQL

Per database PostgreSQL:
- Export tramite `pg_dump`
- Formato SQL o custom
- Puo includere schema e/o dati

### Backup Completo

Include:
- Database
- File media (immagini, video)
- File di configurazione
- Report generati

---

## Accesso alle Funzioni di Backup

### Via Pannello Configurazione

1. Menu **PyArchInit** > **Sketchy GPT** > **Settings** (o Settings direttamente)
2. Nella finestra di configurazione
3. Tab o sezione dedicata al backup

### Via File System

Per SQLite, e possibile copiare direttamente:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Backup SQLite

### Procedura Manuale

1. **Chiudere** tutte le schede PyArchInit aperte
2. **Individuare** il file database:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   Su Windows:
   ```
   C:\Users\[utente]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copiare** il file in una cartella di backup:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Verificare** l'integrita aprendo la copia con un tool SQLite

### Script Automatico (opzionale)

Per backup automatici, creare uno script:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Backup completato: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Backup completato: %DEST%
```

---

## Backup PostgreSQL

### Usando pg_dump

1. **Aprire** un terminale/prompt comandi

2. **Eseguire** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Parametri:
   - `-h`: host del database
   - `-U`: utente
   - `-d`: nome database
   - `-F c`: formato custom (compresso)
   - `-f`: file di output

3. **Inserire** la password quando richiesto

### Backup Solo Dati

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_dati.sql
```

### Backup Solo Schema

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Backup File Media

### Cartella Media

I file media sono nella cartella:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procedura

1. **Individuare** la cartella:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copiare** l'intera cartella:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Comprimere** (opzionale):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restore (Ripristino)

### Restore SQLite

1. **Chiudere** QGIS e PyArchInit
2. **Rinominare** il database corrente (per sicurezza):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copiare** il backup nella cartella originale:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Riavviare** QGIS

### Restore PostgreSQL

1. **Creare** un database vuoto (se necessario):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Ripristinare** il backup:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Aggiornare** la configurazione di PyArchInit per usare il nuovo database

### Restore File Media

1. **Copiare** i file di backup nella cartella media:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Backup Completo del Progetto

### Cosa Includere

| Elemento | Percorso |
|----------|----------|
| Database SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Media | `pyarchinit_image_folder/` |
| PDF generati | `pyarchinit_PDF_folder/` |
| Report | `pyarchinit_Report_folder/` |
| Configurazione | `pyarchinit_Logo_folder/`, file .txt |

### Script Backup Completo

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Database
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Media
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF e Report
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Comprimi
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Backup completo: $BACKUP_DIR.tar.gz"
```

---

## Best Practices

### Frequenza Backup

| Tipo attivita | Frequenza consigliata |
|---------------|----------------------|
| Scavo attivo | Giornaliero |
| Post-scavo | Settimanale |
| Archiviazione | Prima di ogni modifica significativa |

### Conservazione

- Mantenere almeno **3 copie** in luoghi diversi
- Utilizzare **storage cloud** per ridondanza
- **Verificare periodicamente** l'integrita dei backup

### Nomenclatura

Formato consigliato:
```
[progetto]_[tipo]_[data]_[versione]
Esempio: villa_romana_db_20240115_v1.sqlite
```

### Documentazione

Creare un log dei backup:
```
Data: 2024-01-15
Tipo: Backup completo
File: villa_romana_backup_20240115.tar.gz
Dimensione: 2.5 GB
Note: Pre-chiusura campagna 2024
```

---

## Automazione Backup

### Cron Job (Linux/Mac)

Aggiungere a crontab (`crontab -e`):
```
# Backup giornaliero alle 23:00
0 23 * * * /path/to/backup_script.sh
```

### Task Scheduler (Windows)

1. Aprire **Utilita di pianificazione**
2. Creare attivita di base
3. Impostare trigger (giornaliero)
4. Azione: Avvia programma > script batch

---

## Troubleshooting

### Problema: Database corrotto dopo restore

**Causa**: File backup incompleto o danneggiato.

**Soluzione**:
1. Verificare integrita con `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Usare un backup precedente
3. Tentare recupero con strumenti SQLite

### Problema: Dimensione backup eccessiva

**Causa**: Molti file media o database molto grande.

**Soluzione**:
1. Comprimere i backup
2. Eseguire VACUUM sul database
3. Archiviare separatamente i media meno recenti

### Problema: pg_dump errore di connessione

**Causa**: Parametri di connessione errati.

**Soluzione**:
1. Verificare host, porta, utente
2. Controllare pg_hba.conf per permessi
3. Testare connessione con psql

---

## Migrazione tra Database

### Da SQLite a PostgreSQL

1. Esportare dati da SQLite
2. Creare schema in PostgreSQL
3. Importare dati

PyArchInit gestisce questo tramite le impostazioni di configurazione.

### Da PostgreSQL a SQLite

1. Esportare dati da PostgreSQL
2. Creare database SQLite
3. Importare dati

---

## Riferimenti

### Percorsi Standard

| Sistema | Percorso base |
|---------|---------------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[utente]\pyarchinit\` |

### Strumenti Utili

- **SQLite Browser**: visualizzazione/modifica database SQLite
- **pgAdmin**: gestione PostgreSQL
- **7-Zip/tar**: compressione backup
- **rsync**: sincronizzazione incrementale

---

## Video Tutorial

### Backup e Sicurezza Dati
**Durata**: 10-12 minuti
- Procedure di backup
- Restore database
- Automazione

[Placeholder video: video_backup_restore.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
