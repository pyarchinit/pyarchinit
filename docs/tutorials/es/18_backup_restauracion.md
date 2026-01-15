# Tutorial 18: Backup y Restauración

## Introducción

La gestión del **backup** es fundamental para la seguridad de los datos arqueológicos. PyArchInit ofrece herramientas para realizar backup de la base de datos y de los archivos asociados, tanto para SQLite como para PostgreSQL.

### Importancia del Backup

- **Protección de datos**: salvaguarda ante pérdidas accidentales
- **Versionado**: posibilidad de volver a estados anteriores
- **Migración**: transferencia entre sistemas
- **Archivo**: conservación de proyectos completados

---

## Tipos de Backup

### Backup de Base de Datos SQLite

Para bases de datos SQLite (archivo `.sqlite`):
- Copia directa del archivo de base de datos
- Simple y rápido
- Incluye todos los datos

### Backup de Base de Datos PostgreSQL

Para bases de datos PostgreSQL:
- Export mediante `pg_dump`
- Formato SQL o custom
- Puede incluir esquema y/o datos

### Backup Completo

Incluye:
- Base de datos
- Archivos media (imágenes, videos)
- Archivos de configuración
- Informes generados

---

## Acceso a las Funciones de Backup

### Vía Panel de Configuración

1. Menú **PyArchInit** > **Sketchy GPT** > **Settings** (o Settings directamente)
2. En la ventana de configuración
3. Tab o sección dedicada al backup

### Vía Sistema de Archivos

Para SQLite, es posible copiar directamente:
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Backup SQLite

### Procedimiento Manual

1. **Cerrar** todas las fichas de PyArchInit abiertas
2. **Localizar** el archivo de base de datos:
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   En Windows:
   ```
   C:\Users\[usuario]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copiar** el archivo en una carpeta de backup:
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Verificar** la integridad abriendo la copia con una herramienta SQLite

### Script Automático (opcional)

Para backups automáticos, crear un script:

**Linux/Mac (bash):**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Backup completado: $DEST"
```

**Windows (batch):**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Backup completado: %DEST%
```

---

## Backup PostgreSQL

### Usando pg_dump

1. **Abrir** un terminal/símbolo del sistema

2. **Ejecutar** pg_dump:
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Parámetros:
   - `-h`: host de la base de datos
   - `-U`: usuario
   - `-d`: nombre de la base de datos
   - `-F c`: formato custom (comprimido)
   - `-f`: archivo de salida

3. **Introducir** la contraseña cuando se solicite

### Backup Solo Datos

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_datos.sql
```

### Backup Solo Esquema

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_esquema.sql
```

---

## Backup de Archivos Media

### Carpeta Media

Los archivos media están en la carpeta:
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procedimiento

1. **Localizar** la carpeta:
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copiar** toda la carpeta:
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Comprimir** (opcional):
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restore (Restauración)

### Restore SQLite

1. **Cerrar** QGIS y PyArchInit
2. **Renombrar** la base de datos actual (por seguridad):
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copiar** el backup en la carpeta original:
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Reiniciar** QGIS

### Restore PostgreSQL

1. **Crear** una base de datos vacía (si es necesario):
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Restaurar** el backup:
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Actualizar** la configuración de PyArchInit para usar la nueva base de datos

### Restore de Archivos Media

1. **Copiar** los archivos de backup en la carpeta media:
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Backup Completo del Proyecto

### Qué Incluir

| Elemento | Ruta |
|----------|------|
| Base de datos SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Media | `pyarchinit_image_folder/` |
| PDF generados | `pyarchinit_PDF_folder/` |
| Informes | `pyarchinit_Report_folder/` |
| Configuración | `pyarchinit_Logo_folder/`, archivos .txt |

### Script de Backup Completo

**Linux/Mac:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Base de datos
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Media
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF e Informes
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Comprimir
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Backup completo: $BACKUP_DIR.tar.gz"
```

---

## Buenas Prácticas

### Frecuencia de Backup

| Tipo de actividad | Frecuencia recomendada |
|-------------------|------------------------|
| Excavación activa | Diario |
| Post-excavación | Semanal |
| Archivo | Antes de cada modificación significativa |

### Conservación

- Mantener al menos **3 copias** en lugares diferentes
- Utilizar **almacenamiento cloud** para redundancia
- **Verificar periódicamente** la integridad de los backups

### Nomenclatura

Formato recomendado:
```
[proyecto]_[tipo]_[fecha]_[versión]
Ejemplo: villa_romana_db_20240115_v1.sqlite
```

### Documentación

Crear un registro de los backups:
```
Fecha: 2024-01-15
Tipo: Backup completo
Archivo: villa_romana_backup_20240115.tar.gz
Tamaño: 2.5 GB
Notas: Pre-cierre campaña 2024
```

---

## Automatización del Backup

### Cron Job (Linux/Mac)

Añadir a crontab (`crontab -e`):
```
# Backup diario a las 23:00
0 23 * * * /path/to/backup_script.sh
```

### Task Scheduler (Windows)

1. Abrir **Programador de tareas**
2. Crear tarea básica
3. Configurar trigger (diario)
4. Acción: Iniciar programa > script batch

---

## Resolución de Problemas

### Problema: Base de datos corrupta después de restore

**Causa**: Archivo de backup incompleto o dañado.

**Solución**:
1. Verificar integridad con `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Usar un backup anterior
3. Intentar recuperación con herramientas SQLite

### Problema: Tamaño de backup excesivo

**Causa**: Muchos archivos media o base de datos muy grande.

**Solución**:
1. Comprimir los backups
2. Ejecutar VACUUM en la base de datos
3. Archivar separadamente los media menos recientes

### Problema: Error de conexión en pg_dump

**Causa**: Parámetros de conexión incorrectos.

**Solución**:
1. Verificar host, puerto, usuario
2. Controlar pg_hba.conf para permisos
3. Probar conexión con psql

---

## Migración entre Bases de Datos

### De SQLite a PostgreSQL

1. Exportar datos desde SQLite
2. Crear esquema en PostgreSQL
3. Importar datos

PyArchInit gestiona esto a través de la configuración.

### De PostgreSQL a SQLite

1. Exportar datos desde PostgreSQL
2. Crear base de datos SQLite
3. Importar datos

---

## Referencias

### Rutas Estándar

| Sistema | Ruta base |
|---------|-----------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[usuario]\pyarchinit\` |

### Herramientas Útiles

- **SQLite Browser**: visualización/modificación de base de datos SQLite
- **pgAdmin**: gestión de PostgreSQL
- **7-Zip/tar**: compresión de backups
- **rsync**: sincronización incremental

---

## Video Tutorial

### Backup y Seguridad de Datos
**Duración**: 10-12 minutos
- Procedimientos de backup
- Restore de base de datos
- Automatización

[Placeholder video: video_backup_restore.mp4]

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
