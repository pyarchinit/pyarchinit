# Tutorial 19: Treball Multi-usuari amb PostgreSQL

## Introducció

PyArchInit suporta el treball **multi-usuari** mitjançant l'ús de **PostgreSQL/PostGIS** com a backend de base de dades. Aquesta configuració permet que diversos operadors treballin simultàniament en el mateix projecte arqueològic des de diferents estacions.

### Avantatges del Multi-usuari

| Aspecte | SQLite | PostgreSQL Multi-usuari |
|---------|--------|------------------------|
| Usuaris simultanis | 1 | Il·limitats |
| Accés remot | No | Sí |
| Gestió permisos | No | Sí |
| Còpia de seguretat centralitzada | Manual | Automatitzable |
| Rendiment | Bones | Òptimes |
| Escalabilitat | Limitada | Elevada |

## Prerequisits

### Servidor PostgreSQL

1. **PostgreSQL** 12 o superior
2. **PostGIS** 3.0 o superior
3. Servidor accessible en xarxa (LAN o Internet)

### Client

1. QGIS amb PyArchInit instal·lat
2. Connexió de xarxa al servidor
3. Credencials d'accés

## Configuració Servidor

### Instal·lació PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Descarregar instal·lador des de [postgresql.org](https://www.postgresql.org/download/windows/)
- Instal·lar amb Stack Builder per PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Creació Base de Dades

```sql
-- Connectar-se com a superuser
sudo -u postgres psql

-- Crear base de dades
CREATE DATABASE pyarchinit_db;

-- Habilitar PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Crear usuari aplicació
CREATE USER pyarchinit WITH PASSWORD 'contrasenya_segura';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Configuració Accés Xarxa

Modificar `pg_hba.conf`:
```
# Permetre connexions des de la xarxa local
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# O des de qualsevol IP (menys segur)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Modificar `postgresql.conf`:
```
listen_addresses = '*'
```

Reiniciar PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Configuració Client PyArchInit

### Configuració Inicial

1. **PyArchInit** → **Configuració**
2. Tab **Database**
3. Seleccionar **PostgreSQL**
4. Emplenar els camps:

| Camp | Valor |
|------|-------|
| Servidor | Adreça IP o hostname |
| Port | 5432 (per defecte) |
| Base de dades | pyarchinit_db |
| Usuari | pyarchinit |
| Contrasenya | contrasenya_segura |

### Test Connexió

1. Fer clic **Test Connexió**
2. Verificar missatge d'èxit
3. Desar configuració

### Creació Esquema

Si base de dades nova:
1. Fer clic **Crea Esquema**
2. Esperar creació taules
3. Verificar estructura

## Gestió Usuaris

### Creació Usuaris Addicionals

```sql
-- Usuari amb accés complet
CREATE USER arqueoleg1 WITH PASSWORD 'contrasenya1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO arqueoleg1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO arqueoleg1;

-- Usuari en només lectura
CREATE USER consultor1 WITH PASSWORD 'contrasenya2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultor1;
```

### Nivells d'Accés Suggerits

| Rol | Permisos | Ús |
|-----|----------|-----|
| Admin | ALL | Configuració, gestió |
| Arqueòleg | SELECT, INSERT, UPDATE, DELETE | Treball quotidià |
| Especialista | SELECT, INSERT, UPDATE (taules específiques) | Inserció dades especialitzades |
| Consultor | SELECT | Consulta dades |
| Backup | SELECT | Scripts de còpia de seguretat |

### Gestió Rols

```sql
-- Crear rol grup
CREATE ROLE arqueolegs;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arqueolegs;

-- Assignar usuaris al grup
GRANT arqueolegs TO arqueoleg1;
GRANT arqueolegs TO arqueoleg2;
```

## Flux de Treball Multi-usuari

### Organització Treball

#### Per Àrea
- Assignar àrees diferents a operadors diferents
- Evitar superposicions

#### Per Tipologia
- Un operador: US dipòsit
- Altre operador: US muràries
- Altre operador: Troballes

#### Per Lloc
- Llocs diferents a equips diferents

### Gestió Conflictes

#### Bloqueig Registre (recomanat)
1. Abans de modificar, verificar que ningú estigui treballant en el mateix registre
2. Comunicar-se amb l'equip

#### Resolució Conflictes
En cas de modificacions concurrents:
1. L'última modificació preval
2. Verificar les dades després de cada sessió
3. Usar el camp "data modificació" per rastrejar

### Sincronització

Amb PostgreSQL la sincronització és automàtica:
- Cada modificació és immediatament visible als altres
- No cal sincronització manual
- Refrescar la fitxa per veure actualitzacions

## Còpia de Seguretat i Seguretat

### Còpia de Seguretat Automàtica

Script de còpia de seguretat diari:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Mantenir només últims 30 dies
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Programar amb cron:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Restauració

```bash
# Restaurar des de còpia de seguretat
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Seguretat

1. **Contrasenyes fortes**: Mínim 12 caràcters, barreja majúscules/minúscules/números
2. **Connexions SSL**: Habilitar SSL per connexions remotes
3. **Firewall**: Limitar accés al port 5432
4. **Actualitzacions**: Mantenir PostgreSQL actualitzat
5. **Registre auditoria**: Habilitar logging de les connexions

### SSL per Connexions Remotes

A `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

A `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Monitorització

### Connexions Actives

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

### Mida Base de Dades

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Bloquejos Actius

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

## Migració des de SQLite

### Export des de SQLite

1. Obrir PyArchInit amb base de dades SQLite
2. **PyArchInit** → **Utilities** → **Export Database**
3. Exportar en format SQL

### Import a PostgreSQL

1. Configurar connexió PostgreSQL
2. Crear esquema buit
3. Importar dades exportades

### Script Migració

```python
# Exemple conceptual
# Usar eines específiques de migració
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copiar taules
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Bones Pràctiques

### 1. Planificació

- Definir rols i responsabilitats
- Establir convencions de treball
- Documentar procediments

### 2. Comunicació

- Canal de comunicació equip (xat, correu)
- Senyalitzar inici/fi sessions de treball
- Comunicar àrees en modificació

### 3. Còpia de Seguretat

- Còpies de seguretat diàries automàtiques
- Test periòdic de restauració
- Còpia de seguretat fora del lloc

### 4. Formació

- Entrenament en flux de treball multi-usuari
- Documentació procediments
- Suport tècnic disponible

## Resolució de Problemes

### Connexió Rebutjada

**Causes**:
- Servidor no accessible
- Firewall blocant
- Credencials errònies

**Solucions**:
- Verificar connectivitat xarxa
- Controlar regles firewall
- Verificar credencials

### Timeout Connexió

**Causes**:
- Xarxa lenta
- Servidor sobrecarregat
- Massa connexions

**Solucions**:
- Optimitzar xarxa
- Augmentar recursos servidor
- Limitar connexions simultànies

### Bloqueig Base de Dades

**Causa**: Transaccions no completades

**Solució**:
```sql
-- Identificar processos blocants
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminar procés (amb precaució)
SELECT pg_terminate_backend(pid);
```

## Referències

### Configuració
- `modules/db/pyarchinit_conn_strings.py` - Cadenes connexió
- `gui/pyarchinit_Setting.py` - Interfície configuració

### Documentació Externa
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## Vídeo Tutorial

### Setup Multi-usuari
`[Placeholder: video_multiusuari_setup.mp4]`

**Continguts**:
- Instal·lació PostgreSQL
- Configuració servidor
- Setup client
- Gestió usuaris

**Durada prevista**: 20-25 minuts

### Flux de Treball Col·laboratiu
`[Placeholder: video_multiusuari_workflow.mp4]`

**Continguts**:
- Organització treball
- Gestió conflictes
- Bones pràctiques

**Durada prevista**: 12-15 minuts

---

*Última actualització: Gener 2026*

---

## Animació Interactiva

Explora l'animació interactiva per aprendre més sobre aquest tema.

[Obre Animació Interactiva](../animations/pyarchinit_concurrency_animation.html)
