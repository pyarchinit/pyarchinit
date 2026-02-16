# Tutorial 18: Copie de siguranta si restaurare

## Introducere

Gestionarea **copiilor de siguranta** este fundamentala pentru securitatea datelor arheologice. PyArchInit ofera instrumente pentru realizarea copiilor de siguranta ale bazei de date si fisierelor asociate, atat pentru SQLite cat si pentru PostgreSQL.

### Importanta copiilor de siguranta

- **Protectia datelor**: protectie impotriva pierderii accidentale
- **Versionare**: posibilitatea de a reveni la stari anterioare
- **Migrare**: transfer intre sisteme
- **Arhivare**: conservarea proiectelor finalizate

---

## Tipuri de copii de siguranta

### Copia de siguranta a bazei de date SQLite

Pentru bazele de date SQLite (fisiere `.sqlite`):
- Copiere directa a fisierului bazei de date
- Simpla si rapida
- Include toate datele

### Copia de siguranta a bazei de date PostgreSQL

Pentru bazele de date PostgreSQL:
- Export prin `pg_dump`
- Format SQL sau personalizat
- Poate include schema si/sau datele

### Copia de siguranta completa

Include:
- Baza de date
- Fisiere media (imagini, videoclipuri)
- Fisiere de configurare
- Rapoarte generate

---

## Accesarea functiilor de copie de siguranta

### Prin panoul de configurare

1. Meniul **PyArchInit** > **Sketchy GPT** > **Setari** (sau Setari direct)
2. In fereastra de configurare
3. Fila sau sectiunea dedicata copiilor de siguranta

### Prin sistemul de fisiere

Pentru SQLite, puteti copia direct:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Copia de siguranta SQLite

### Procedura manuala

1. **Inchideti** toate formularele PyArchInit deschise
2. **Localizati** fisierul bazei de date:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   Pe Windows:
   ```
   C:\Users\[utilizator]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copiati** fisierul intr-un folder de copii de siguranta:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Verificati** integritatea deschizand copia cu un instrument SQLite

### Script automat (optional)

Pentru copii de siguranta automate, creati un script:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Copia de siguranta finalizata: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Copia de siguranta finalizata: %DEST%
```

---

## Copia de siguranta PostgreSQL

### Utilizarea pg_dump

1. **Deschideti** un terminal/prompt de comanda

2. **Executati** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Parametri:
   - `-h`: gazda bazei de date
   - `-U`: utilizator
   - `-d`: numele bazei de date
   - `-F c`: format personalizat (comprimat)
   - `-f`: fisier de iesire

3. **Introduceti** parola cand vi se solicita

### Copia de siguranta doar a datelor

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_data.sql
```

### Copia de siguranta doar a schemei

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Copia de siguranta a fisierelor media

### Folderul media

Fisierele media se afla in folderul:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procedura

1. **Localizati** folderul:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copiati** intregul folder:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Comprimati** (optional):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restaurare

### Restaurare SQLite

1. **Inchideti** QGIS si PyArchInit
2. **Redenumiti** baza de date curenta (pentru siguranta):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copiati** copia de siguranta in folderul original:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Reporniti** QGIS

### Restaurare PostgreSQL

1. **Creati** o baza de date goala (daca este necesar):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Restaurati** copia de siguranta:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Actualizati** configuratia PyArchInit pentru a utiliza noua baza de date

### Restaurarea fisierelor media

1. **Copiati** fisierele din copia de siguranta in folderul media:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Copia de siguranta completa a proiectului

### Ce sa includeti

| Element | Cale |
|---------|------|
| Baza de date SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Media | `pyarchinit_image_folder/` |
| PDF-uri generate | `pyarchinit_PDF_folder/` |
| Rapoarte | `pyarchinit_Report_folder/` |
| Configurare | `pyarchinit_Logo_folder/`, fisiere .txt |

### Script complet de copie de siguranta

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Baza de date
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Media
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF si rapoarte
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Comprimare
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Copia de siguranta completa: $BACKUP_DIR.tar.gz"
```

---

## Bune practici

### Frecventa copiilor de siguranta

| Tipul activitatii | Frecventa recomandata |
|--------------------|-----------------------|
| Excavare activa | Zilnic |
| Post-excavare | Saptamanal |
| Arhivare | Inainte de fiecare modificare semnificativa |

### Pastrare

- Pastrati cel putin **3 copii** in locatii diferite
- Utilizati **stocarea in cloud** pentru redundanta
- **Verificati periodic** integritatea copiilor de siguranta

### Denumire

Format recomandat:
```
[proiect]_[tip]_[data]_[versiune]
Exemplu: vila_romana_db_20240115_v1.sqlite
```

### Documentatie

Creati un jurnal al copiilor de siguranta:
```
Data: 2024-01-15
Tip: Copia de siguranta completa
Fisier: vila_romana_backup_20240115.tar.gz
Dimensiune: 2.5 GB
Note: Pre-inchidere campanie 2024
```

---

## Automatizarea copiilor de siguranta

### Cron Job (Linux/Mac)

Adaugati in crontab (`crontab -e`):
```
# Copia de siguranta zilnica la 23:00
0 23 * * * /path/to/backup_script.sh
```

### Planificator de sarcini (Windows)

1. Deschideti **Planificatorul de sarcini**
2. Creati o sarcina de baza
3. Setati declansatorul (zilnic)
4. Actiune: Porniti programul > script batch

---

## Depanare

### Problema: Baza de date corupta dupa restaurare

**Cauza**: Fisier de copia de siguranta incomplet sau deteriorat.

**Solutie**:
1. Verificati integritatea cu `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Utilizati o copia de siguranta anterioara
3. Incercati recuperarea cu instrumente SQLite

### Problema: Dimensiune excesiva a copiei de siguranta

**Cauza**: Multe fisiere media sau baza de date foarte mare.

**Solutie**:
1. Comprimati copiile de siguranta
2. Executati VACUUM pe baza de date
3. Arhivati separat fisierele media mai vechi

### Problema: Eroare de conexiune pg_dump

**Cauza**: Parametri de conexiune incorecti.

**Solutie**:
1. Verificati gazda, portul, utilizatorul
2. Verificati pg_hba.conf pentru permisiuni
3. Testati conexiunea cu psql

---

## Migrarea intre baze de date

### De la SQLite la PostgreSQL

1. Exportati datele din SQLite
2. Creati schema in PostgreSQL
3. Importati datele

PyArchInit gestioneaza acest lucru prin setarile de configurare.

### De la PostgreSQL la SQLite

1. Exportati datele din PostgreSQL
2. Creati baza de date SQLite
3. Importati datele

---

## Referinte

### Cai standard

| Sistem | Calea de baza |
|--------|---------------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[utilizator]\pyarchinit\` |

### Instrumente utile

- **SQLite Browser**: Vizualizare/editare baze de date SQLite
- **pgAdmin**: Gestionare PostgreSQL
- **7-Zip/tar**: Comprimarea copiilor de siguranta
- **rsync**: Sincronizare incrementala

---

## Tutorial video

### Copii de siguranta si securitatea datelor
**Durata**: 10-12 minute
- Proceduri de copiere de siguranta
- Restaurarea bazei de date
- Automatizare

[Video placeholder: video_backup_restore.mp4]

---

*Ultima actualizare: ianuarie 2026*
*PyArchInit - Sistem de gestionare a datelor arheologice*
