# Tutorial 18: Còpia de Seguretat i Restauració

## Introducció

La gestió de les **còpies de seguretat** és fonamental per a la seguretat de les dades arqueològiques. PyArchInit ofereix eines per executar còpies de seguretat de la base de dades i dels fitxers associats, tant per SQLite com per PostgreSQL.

### Importància de la Còpia de Seguretat

- **Protecció dades**: salvaguarda de pèrdues accidentals
- **Versionat**: possibilitat de tornar a estats anteriors
- **Migració**: transferència entre sistemes
- **Arxivament**: conservació projectes completats

---

## Tipus de Còpia de Seguretat

### Còpia de Seguretat Base de Dades SQLite

Per a bases de dades SQLite (fitxer `.sqlite`):
- Còpia directa del fitxer base de dades
- Simple i ràpida
- Inclou totes les dades

### Còpia de Seguretat Base de Dades PostgreSQL

Per a bases de dades PostgreSQL:
- Export mitjançant `pg_dump`
- Format SQL o custom
- Pot incloure esquema i/o dades

### Còpia de Seguretat Completa

Inclou:
- Base de dades
- Fitxers media (imatges, vídeos)
- Fitxers de configuració
- Informes generats

---

## Accés a les Funcions de Còpia de Seguretat

### Via Panell Configuració

1. Menú **PyArchInit** > **Sketchy GPT** > **Settings** (o Settings directament)
2. A la finestra de configuració
3. Tab o secció dedicada a la còpia de seguretat

### Via Sistema de Fitxers

Per SQLite, és possible copiar directament:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Còpia de Seguretat SQLite

### Procediment Manual

1. **Tancar** totes les fitxes PyArchInit obertes
2. **Localitzar** el fitxer base de dades:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   A Windows:
   ```
   C:\Users\[usuari]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copiar** el fitxer a una carpeta de còpia de seguretat:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Verificar** la integritat obrint la còpia amb una eina SQLite

### Script Automàtic (opcional)

Per a còpies de seguretat automàtiques, crear un script:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Còpia de seguretat completada: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Còpia de seguretat completada: %DEST%
```

---

## Còpia de Seguretat PostgreSQL

### Usant pg_dump

1. **Obrir** un terminal/prompt de comandes

2. **Executar** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Paràmetres:
   - `-h`: host de la base de dades
   - `-U`: usuari
   - `-d`: nom base de dades
   - `-F c`: format custom (comprimit)
   - `-f`: fitxer de sortida

3. **Inserir** la contrasenya quan es demani

### Còpia de Seguretat Només Dades

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_dades.sql
```

### Còpia de Seguretat Només Esquema

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_esquema.sql
```

---

## Còpia de Seguretat Fitxers Media

### Carpeta Media

Els fitxers media són a la carpeta:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procediment

1. **Localitzar** la carpeta:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copiar** tota la carpeta:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Comprimir** (opcional):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restauració

### Restauració SQLite

1. **Tancar** QGIS i PyArchInit
2. **Reanomenar** la base de dades actual (per seguretat):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copiar** la còpia de seguretat a la carpeta original:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Reiniciar** QGIS

### Restauració PostgreSQL

1. **Crear** una base de dades buida (si és necessari):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Restaurar** la còpia de seguretat:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Actualitzar** la configuració de PyArchInit per usar la nova base de dades

### Restauració Fitxers Media

1. **Copiar** els fitxers de còpia de seguretat a la carpeta media:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Còpia de Seguretat Completa del Projecte

### Què Incloure

| Element | Ruta |
|---------|------|
| Base de dades SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Media | `pyarchinit_image_folder/` |
| PDF generats | `pyarchinit_PDF_folder/` |
| Informes | `pyarchinit_Report_folder/` |
| Configuració | `pyarchinit_Logo_folder/`, fitxers .txt |

### Script Còpia de Seguretat Completa

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Base de dades
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Media
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF i Informes
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Comprimir
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Còpia de seguretat completa: $BACKUP_DIR.tar.gz"
```

---

## Bones Pràctiques

### Freqüència Còpia de Seguretat

| Tipus activitat | Freqüència recomanada |
|-----------------|----------------------|
| Excavació activa | Diari |
| Post-excavació | Setmanal |
| Arxivament | Abans de cada modificació significativa |

### Conservació

- Mantenir almenys **3 còpies** en llocs diferents
- Utilitzar **emmagatzematge al núvol** per redundància
- **Verificar periòdicament** la integritat de les còpies de seguretat

### Nomenclatura

Format recomanat:
```
[projecte]_[tipus]_[data]_[versió]
Exemple: vil·la_romana_db_20240115_v1.sqlite
```

### Documentació

Crear un registre de les còpies de seguretat:
```
Data: 2024-01-15
Tipus: Còpia de seguretat completa
Fitxer: vil·la_romana_backup_20240115.tar.gz
Mida: 2.5 GB
Notes: Pre-tancament campanya 2024
```

---

## Automatització Còpia de Seguretat

### Cron Job (Linux/Mac)

Afegir a crontab (`crontab -e`):
```
# Còpia de seguretat diària a les 23:00
0 23 * * * /path/to/backup_script.sh
```

### Programador de Tasques (Windows)

1. Obrir **Programador de tasques**
2. Crear tasca bàsica
3. Establir trigger (diari)
4. Acció: Iniciar programa > script batch

---

## Resolució de Problemes

### Problema: Base de dades corrupta després de restauració

**Causa**: Fitxer còpia de seguretat incomplet o danyat.

**Solució**:
1. Verificar integritat amb `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Usar una còpia de seguretat anterior
3. Intentar recuperació amb eines SQLite

### Problema: Mida còpia de seguretat excessiva

**Causa**: Molts fitxers media o base de dades molt gran.

**Solució**:
1. Comprimir les còpies de seguretat
2. Executar VACUUM a la base de dades
3. Arxivar separadament els media menys recents

### Problema: pg_dump error de connexió

**Causa**: Paràmetres de connexió erronis.

**Solució**:
1. Verificar host, port, usuari
2. Controlar pg_hba.conf per permisos
3. Testejar connexió amb psql

---

## Migració entre Bases de Dades

### De SQLite a PostgreSQL

1. Exportar dades de SQLite
2. Crear esquema a PostgreSQL
3. Importar dades

PyArchInit gestiona això mitjançant les configuracions.

### De PostgreSQL a SQLite

1. Exportar dades de PostgreSQL
2. Crear base de dades SQLite
3. Importar dades

---

## Referències

### Rutes Estàndard

| Sistema | Ruta base |
|---------|-----------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[usuari]\pyarchinit\` |

### Eines Útils

- **SQLite Browser**: visualització/modificació base de dades SQLite
- **pgAdmin**: gestió PostgreSQL
- **7-Zip/tar**: compressió còpies de seguretat
- **rsync**: sincronització incremental

---

## Vídeo Tutorial

### Còpia de Seguretat i Seguretat Dades
**Durada**: 10-12 minuts
- Procediments de còpia de seguretat
- Restauració base de dades
- Automatització

[Placeholder vídeo: video_copia_seguretat.mp4]

---

*Última actualització: Gener 2026*
*PyArchInit - Sistema de Gestió de Dades Arqueològiques*
