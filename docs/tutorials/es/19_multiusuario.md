# Tutorial 19: Trabajo Multiusuario con PostgreSQL

## Introducción

PyArchInit soporta el trabajo **multiusuario** a través del uso de **PostgreSQL/PostGIS** como backend de base de datos. Esta configuración permite que varios operadores trabajen simultáneamente en el mismo proyecto arqueológico desde diferentes estaciones de trabajo.

### Ventajas del Multiusuario

| Aspecto | SQLite | PostgreSQL Multiusuario |
|---------|--------|-------------------------|
| Usuarios simultáneos | 1 | Ilimitados |
| Acceso remoto | No | Sí |
| Gestión de permisos | No | Sí |
| Backup centralizado | Manual | Automatizable |
| Rendimiento | Bueno | Óptimo |
| Escalabilidad | Limitada | Elevada |

## Prerrequisitos

### Servidor PostgreSQL

1. **PostgreSQL** 12 o superior
2. **PostGIS** 3.0 o superior
3. Servidor accesible en red (LAN o Internet)

### Cliente

1. QGIS con PyArchInit instalado
2. Conexión de red al servidor
3. Credenciales de acceso

## Configuración del Servidor

### Instalación de PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Descargar instalador desde [postgresql.org](https://www.postgresql.org/download/windows/)
- Instalar con Stack Builder para PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Creación de la Base de Datos

```sql
-- Conectarse como superusuario
sudo -u postgres psql

-- Crear base de datos
CREATE DATABASE pyarchinit_db;

-- Habilitar PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Crear usuario de aplicación
CREATE USER pyarchinit WITH PASSWORD 'contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Configuración de Acceso de Red

Modificar `pg_hba.conf`:
```
# Permitir conexiones desde la red local
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# O desde cualquier IP (menos seguro)
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

## Configuración del Cliente PyArchInit

### Setup Inicial

1. **PyArchInit** → **Configuración**
2. Tab **Base de datos**
3. Seleccionar **PostgreSQL**
4. Completar los campos:

| Campo | Valor |
|-------|-------|
| Server | Dirección IP o hostname |
| Puerto | 5432 (por defecto) |
| Base de datos | pyarchinit_db |
| Usuario | pyarchinit |
| Contraseña | contraseña_segura |

### Test de Conexión

1. Hacer clic en **Test Conexión**
2. Verificar mensaje de éxito
3. Guardar configuración

### Creación del Esquema

Si la base de datos es nueva:
1. Hacer clic en **Crear Esquema**
2. Esperar la creación de tablas
3. Verificar estructura

## Gestión de Usuarios

### Creación de Usuarios Adicionales

```sql
-- Usuario con acceso completo
CREATE USER arqueologo1 WITH PASSWORD 'contraseña1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO arqueologo1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO arqueologo1;

-- Usuario en solo lectura
CREATE USER consultor1 WITH PASSWORD 'contraseña2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultor1;
```

### Niveles de Acceso Sugeridos

| Rol | Permisos | Uso |
|-----|----------|-----|
| Admin | ALL | Configuración, gestión |
| Arqueólogo | SELECT, INSERT, UPDATE, DELETE | Trabajo diario |
| Especialista | SELECT, INSERT, UPDATE (tablas específicas) | Inserción de datos especializados |
| Consultor | SELECT | Consulta de datos |
| Backup | SELECT | Scripts de backup |

### Gestión de Roles

```sql
-- Crear rol de grupo
CREATE ROLE arqueologos;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO arqueologos;

-- Asignar usuarios al grupo
GRANT arqueologos TO arqueologo1;
GRANT arqueologos TO arqueologo2;
```

## Workflow Multiusuario

### Organización del Trabajo

#### Por Área
- Asignar áreas diferentes a operadores diferentes
- Evitar solapamientos

#### Por Tipología
- Un operador: UE de depósito
- Otro operador: UE murarias
- Otro operador: Hallazgos

#### Por Sitio
- Sitios diferentes a equipos diferentes

### Gestión de Conflictos

#### Bloqueo de Registro (recomendado)
1. Antes de modificar, verificar que nadie esté trabajando en el mismo registro
2. Comunicarse con el equipo

#### Resolución de Conflictos
En caso de modificaciones concurrentes:
1. La última modificación prevalece
2. Verificar los datos después de cada sesión
3. Usar el campo "fecha de modificación" para rastrear

### Sincronización

Con PostgreSQL la sincronización es automática:
- Cada modificación es inmediatamente visible para los demás
- No es necesaria sincronización manual
- Actualizar la ficha para ver actualizaciones

## Backup y Seguridad

### Backup Automático

Script de backup diario:
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Mantener solo los últimos 30 días
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Programar con cron:
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Restore

```bash
# Restore desde backup
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Seguridad

1. **Contraseñas fuertes**: Mínimo 12 caracteres, mezcla mayúsculas/minúsculas/números
2. **Conexiones SSL**: Habilitar SSL para conexiones remotas
3. **Firewall**: Limitar acceso al puerto 5432
4. **Actualizaciones**: Mantener PostgreSQL actualizado
5. **Audit log**: Habilitar logging de conexiones

### SSL para Conexiones Remotas

En `postgresql.conf`:
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

En `pg_hba.conf`:
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Monitorización

### Conexiones Activas

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

### Tamaño de la Base de Datos

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Bloqueos Activos

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

## Migración desde SQLite

### Export desde SQLite

1. Abrir PyArchInit con base de datos SQLite
2. **PyArchInit** → **Utilities** → **Export Database**
3. Exportar en formato SQL

### Import en PostgreSQL

1. Configurar conexión PostgreSQL
2. Crear esquema vacío
3. Importar datos exportados

### Script de Migración

```python
# Ejemplo conceptual
# Usar herramientas específicas de migración
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copiar tablas
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Buenas Prácticas

### 1. Planificación

- Definir roles y responsabilidades
- Establecer convenciones de trabajo
- Documentar procedimientos

### 2. Comunicación

- Canal de comunicación del equipo (chat, email)
- Señalar inicio/fin de sesiones de trabajo
- Comunicar áreas en modificación

### 3. Backup

- Backups diarios automáticos
- Test periódico de restore
- Backup off-site

### 4. Formación

- Training sobre workflow multiusuario
- Documentación de procedimientos
- Soporte técnico disponible

## Resolución de Problemas

### Conexión Rechazada

**Causas**:
- Servidor no accesible
- Firewall bloqueando
- Credenciales incorrectas

**Soluciones**:
- Verificar conectividad de red
- Controlar reglas del firewall
- Verificar credenciales

### Timeout de Conexión

**Causas**:
- Red lenta
- Servidor sobrecargado
- Demasiadas conexiones

**Soluciones**:
- Optimizar red
- Aumentar recursos del servidor
- Limitar conexiones simultáneas

### Bloqueo de Base de Datos

**Causa**: Transacciones no completadas

**Solución**:
```sql
-- Identificar procesos bloqueantes
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminar proceso (con precaución)
SELECT pg_terminate_backend(pid);
```

## Referencias

### Configuración
- `modules/db/pyarchinit_conn_strings.py` - Cadenas de conexión
- `gui/pyarchinit_Setting.py` - Interfaz de configuración

### Documentación Externa
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)

---

## Video Tutorial

### Setup Multiusuario
`[Placeholder: video_multiusuario_setup.mp4]`

**Contenidos**:
- Instalación de PostgreSQL
- Configuración del servidor
- Setup del cliente
- Gestión de usuarios

**Duración prevista**: 20-25 minutos

### Workflow Colaborativo
`[Placeholder: video_multiusuario_workflow.mp4]`

**Contenidos**:
- Organización del trabajo
- Gestión de conflictos
- Buenas prácticas

**Duración prevista**: 12-15 minutos

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../animations/pyarchinit_concurrency_animation.html)
