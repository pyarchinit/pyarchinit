# PyArchInit - Guía de Configuración

## Índice
1. [Introducción](#introducción)
2. [Acceso a la Configuración](#acceso-a-la-configuración)
3. [Pestaña Parámetros de Conexión](#pestaña-parámetros-de-conexión)
4. [Pestaña Instalación BD](#pestaña-instalación-bd)
5. [Pestaña Herramientas de Importación](#pestaña-herramientas-de-importación)
6. [Pestaña Graphviz](#pestaña-graphviz)
7. [Pestaña PostgreSQL](#pestaña-postgresql)
8. [Pestaña Ayuda](#pestaña-ayuda)
9. [Pestaña FTP a Lizmap](#pestaña-ftp-a-lizmap)

---

## Introducción

La ventana de configuración de PyArchInit permite establecer todos los parámetros necesarios para el correcto funcionamiento del plugin. Antes de comenzar a documentar una excavación arqueológica, es necesario configurar correctamente la conexión a la base de datos y las rutas de los recursos.

> **Video Tutorial**: [Insertar enlace video introducción configuración]

---

## Acceso a la Configuración

Para acceder a la configuración:
1. Abrir QGIS
2. Menú **PyArchInit** → **Config**

O desde la barra de herramientas de PyArchInit hacer clic en el icono **Ajustes**.

![Acceso a la configuración](images/01_configuracion/01_menu_config.png)
*Figura 1: Acceso a la ventana de configuración desde el menú PyArchInit*

![Toolbar PyArchInit](images/01_configuracion/02_toolbar_config.png)
*Figura 2: Icono configuración en la barra de herramientas*

---

## Pestaña Parámetros de Conexión

Esta es la pestaña principal para configurar la conexión a la base de datos.

![Pestaña Parámetros de Conexión](images/01_configuracion/03_tab_parametros_conexion.png)
*Figura 3: Pestaña Parámetros de Conexión - Vista completa*

### Sección DB Settings

| Campo | Descripción |
|-------|-------------|
| **Database** | Seleccionar el tipo de base de datos: `sqlite` (local) o `postgres` (servidor) |
| **Host** | Dirección del servidor PostgreSQL (ej. `localhost` o IP del servidor) |
| **DBname** | Nombre de la base de datos (ej. `pyarchinit`) |
| **Port** | Puerto de conexión (predeterminado: `5432` para PostgreSQL) |
| **User** | Nombre de usuario para la conexión |
| **Password** | Contraseña del usuario |
| **SSL Mode** | Modo SSL para PostgreSQL: `allow`, `prefer`, `require`, `disable` |

#### Elección de la Base de Datos

**SQLite/Spatialite** (Recomendado para uso individual):
- Base de datos local, no requiere servidor
- Ideal para proyectos individuales o de pequeñas dimensiones
- El archivo `.sqlite` se guarda en la carpeta `pyarchinit_DB_folder`

**PostgreSQL/PostGIS** (Recomendado para equipos):
- Base de datos en servidor, acceso multiusuario
- Necesario tener PostgreSQL con extensión PostGIS instalado
- Soporta gestión de usuarios y permisos
- Ideal para proyectos grandes con múltiples operadores

### Sección Path Settings

| Campo | Descripción | Botón |
|-------|-------------|-------|
| **Thumbnail path** | Ruta donde guardar las miniaturas de las imágenes | `...` para explorar |
| **Image resize** | Ruta para las imágenes redimensionadas | `...` para explorar |
| **Logo path** | Ruta del logo personalizado para los informes | `...` para explorar |

#### Rutas Remotas Soportadas

PyArchInit soporta también almacenamiento remoto:
- **Google Drive**: `gdrive://folder/path/`
- **Dropbox**: `dropbox://folder/path/`
- **Amazon S3**: `s3://bucket/path/`
- **Cloudinary**: `cloudinary://cloud_name/folder/`
- **WebDAV**: `webdav://server/path/`
- **HTTP/HTTPS**: `https://server/path/`

### Sección Experimental

| Campo | Descripción |
|-------|-------------|
| **Experimental** | Activa funcionalidades experimentales (`Sí`/`No`) |

### Sección Activación de Sitio

| Campo | Descripción |
|-------|-------------|
| **Activar query de sitio** | Selecciona el sitio activo para filtrar los datos en las fichas |

Esta opción es fundamental cuando se trabaja con varios sitios arqueológicos en la misma base de datos. Al seleccionar un sitio, todas las fichas mostrarán solo los datos relativos a ese sitio.

### Botones de Acción

| Botón | Función |
|-------|---------|
| **Guardar los parámetros** | Guarda todos los ajustes configurados |
| **Actualizar BD** | Actualiza el esquema de la base de datos existente sin perder datos |

### Funciones de Alineación de Base de Datos

| Botón | Descripción |
|-------|-------------|
| **Alinear Postgres** | Alinea y actualiza la estructura de la base de datos PostgreSQL |
| **Alinear Spatialite** | Alinea y actualiza la estructura de la base de datos SQLite |
| **EPSG code** | Insertar el código EPSG del sistema de referencia de la base de datos |

### Summary (Resumen)

La sección Summary muestra un resumen de los ajustes actuales en formato HTML.

---

## Pestaña Instalación BD

Esta pestaña permite crear una nueva base de datos desde cero.

![Pestaña Instalación BD](images/01_configuracion/12_tab_instalacion_db.png)
*Figura 12: Pestaña Instalación BD - Vista completa*

### Instalar la base de datos (PostgreSQL/PostGIS)

| Campo | Descripción |
|-------|-------------|
| **host** | Dirección del servidor (predeterminado: `localhost`) |
| **port (5432)** | Puerto del servidor PostgreSQL |
| **user** | Usuario con permisos de creación de base de datos (ej. `postgres`) |
| **password** | Contraseña del usuario |
| **db name** | Nombre de la nueva base de datos (predeterminado: `pyarchinit`) |
| **Seleccionar SRID** | Sistema de referencia espacial (ej. `4326` para WGS84, `32632` para UTM 32N) |

**Botón Instalar**: Crea la base de datos con todas las tablas necesarias.

### Instalar la base de datos (SpatiaLite)

| Campo | Descripción |
|-------|-------------|
| **db name** | Nombre del archivo de base de datos (predeterminado: `pyarchinit`) |
| **Seleccionar SRID** | Sistema de referencia espacial |

**Botón Instalar**: Crea la base de datos SQLite local.

### SRID Comunes en España

| SRID | Descripción |
|------|-------------|
| 4326 | WGS 84 (coordenadas geográficas) |
| 25830 | ETRS89 / UTM zone 30N (Península) |
| 25831 | ETRS89 / UTM zone 31N (Cataluña, Baleares) |
| 25829 | ETRS89 / UTM zone 29N (Galicia, Portugal) |
| 32628 | WGS 84 / UTM zone 28N (Canarias) |

---

## Pestaña Herramientas de Importación

Esta pestaña permite importar datos de otras bases de datos o archivos CSV.

### Sección Importación de Datos

#### Base de Datos Origen (Recurso)

| Campo | Descripción |
|-------|-------------|
| **Database** | Tipo de base de datos origen (`sqlite` o `postgres`) |
| **Host/Port/Username/Password** | Credenciales para PostgreSQL origen |
| **...** | Seleccionar archivo SQLite origen |

#### Base de Datos Destino

| Campo | Descripción |
|-------|-------------|
| **Database** | Tipo de base de datos destino |
| **Host/Port/Username/Password** | Credenciales para PostgreSQL destino |
| **...** | Seleccionar archivo SQLite destino |

### Tablas Disponibles para Importación

| Tabla | Descripción |
|-------|-------------|
| SITE | Sitios arqueológicos |
| US | Unidades Estratigráficas |
| PERIODIZZAZIONE | Periodización y fases |
| INVENTARIO_MATERIALI | Inventario de materiales |
| TMA | Tablas de Materiales Arqueológicos |
| POTTERY | Cerámica |
| STRUTTURA | Estructuras |
| TOMBA | Tumbas |
| SCHEDAIND | Fichas de individuos antropológicos |
| ARCHEOZOOLOGY | Datos arqueozoológicos |
| CAMPIONI | Muestras |
| DOCUMENTAZIONE | Documentación |
| MEDIA | Archivos multimedia |
| UT | Unidades Topográficas |
| ALL | Todas las tablas |

### Opciones de Importación

| Opción | Descripción |
|--------|-------------|
| **Replace** | Reemplaza los registros existentes |
| **Ignore** | Ignora los duplicados |
| **Abort** | Interrumpe en caso de error |
| **Apply Constraints** | Aplica restricciones de unicidad al tesauro |

### Botones

| Botón | Función |
|-------|---------|
| **Import Table** | Importa los datos de la tabla seleccionada |
| **Import Geometry** | Importa las geometrías seleccionadas |
| **Convertir db a spatialite** | Convierte de PostgreSQL a SQLite |
| **Convertir db a postgres** | Convierte de SQLite a PostgreSQL |

---

## Pestaña Graphviz

Graphviz es necesario para generar los diagramas del Matrix de Harris.

### Configuración

| Campo | Descripción |
|-------|-------------|
| **Ruta bin** | Ruta a la carpeta `/bin` de Graphviz |
| **...** | Explorar para seleccionar la carpeta |
| **Guardar** | Guarda la ruta en la variable de entorno PATH |

### Instalación de Graphviz

**Windows**: Descargar de https://graphviz.org/download/ e instalar

**macOS**:
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install graphviz
```

Si Graphviz ya está instalado correctamente en el PATH del sistema, los campos estarán deshabilitados automáticamente.

---

## Pestaña PostgreSQL

Configuración de la ruta de PostgreSQL para operaciones avanzadas.

| Campo | Descripción |
|-------|-------------|
| **Ruta bin** | Ruta a la carpeta `/bin` de PostgreSQL |
| **...** | Explorar para seleccionar la carpeta |
| **Guardar** | Guarda la ruta en la variable de entorno PATH |

Necesario para operaciones como dump/restore de la base de datos.

---

## Pestaña Ayuda

Contiene recursos de ayuda y documentación.

### Enlaces Útiles

| Recurso | Descripción |
|---------|-------------|
| **Video Tutorial** | Enlace a los video tutoriales en YouTube |
| **Documentación Online** | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| **Facebook** | Página UnaQuantum |

---

## Pestaña FTP a Lizmap

Permite publicar los datos en un servidor Lizmap para la visualización web.

### Parámetros de Conexión FTP

| Campo | Descripción |
|-------|-------------|
| **ip address** | Dirección IP del servidor FTP |
| **Port** | Puerto FTP (predeterminado: 21) |
| **User** | Nombre de usuario FTP |
| **Password** | Contraseña FTP |

### Operaciones Disponibles

| Botón | Función |
|-------|---------|
| **Connect** | Conectar al servidor FTP |
| **Disconnect** | Desconectar del servidor |
| **Change directory** | Cambiar directorio actual |
| **Create Directory** | Crear un nuevo directorio |
| **Upload file** | Subir un archivo al servidor |
| **Download file** | Descargar un archivo del servidor |
| **Delete file** | Eliminar un archivo |
| **Delete directory** | Eliminar un directorio |

---

## Funciones de Administrador (Solo PostgreSQL)

Si se conecta como administrador, aparece una sección adicional:

### Gestión de Usuarios y Permisos
Permite crear, modificar y eliminar usuarios con diferentes niveles de acceso.

### Monitor de Actividad en Tiempo Real
Visualiza en tiempo real las actividades en la base de datos y los usuarios conectados.

### Actualizar Esquema de Base de Datos
Aplica actualizaciones al esquema sin perder datos.

### Aplicar Sistema de Concurrencia
Añade el sistema de control de concurrencia para evitar conflictos de modificación.

---

## Workflow Recomendado para Nuevo Proyecto

1. **Abrir la Configuración** desde el menú PyArchInit

2. **Elegir el tipo de base de datos** (SQLite para uso individual, PostgreSQL para equipos)

3. **Pestaña Instalación BD**: Crear una nueva base de datos con el SRID apropiado

4. **Pestaña Parámetros de Conexión**: Configurar los parámetros de conexión

5. **Establecer las rutas** para thumbnail, resize y logo

6. **Guardar los parámetros**

7. **Probar la conexión** abriendo cualquier ficha (ej. Sitio)

---

## Resolución de Problemas Comunes

### Error de conexión PostgreSQL

- Verificar que el servidor PostgreSQL esté iniciado
- Comprobar host, puerto y credenciales
- Verificar que la extensión PostGIS esté instalada

### Base de datos SQLite no encontrada
- Verificar que el archivo exista en la carpeta `pyarchinit_DB_folder`
- Comprobar los permisos de lectura/escritura

### Graphviz no funciona
- Verificar la instalación de Graphviz
- Establecer manualmente la ruta en la pestaña Graphviz
- Reiniciar QGIS después de la configuración

### Imágenes no visualizadas
- Verificar las rutas Thumbnail path e Image resize
- Comprobar que las carpetas existan y sean accesibles

---

## Notas Técnicas

- Los ajustes se guardan en las QgsSettings de QGIS
- La base de datos predeterminada es `Home/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite`
- Los logs de debug se guardan en `[TEMP]/pyarchinit_debug.log`
- La variable de entorno `PYARCHINIT_HOME` apunta a la carpeta `pyarchinit` instalada en el Home del usuario

---

*Documentación PyArchInit - Ficha Configuración*
*Versión: 4.9.x*
*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para comprender mejor el proceso de instalación y configuración.

[Abrir Animación de Instalación](../../animations/pyarchinit_installation_animation.html)

Explora la animación interactiva para la gestión del almacenamiento remoto.

[Abrir Animación de Almacenamiento Remoto](../../animations/pyarchinit_remote_storage_animation.html)
