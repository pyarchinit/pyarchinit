# PyArchInit - Ficha de Sitio

## Índice
1. [Introducción](#introducción)
2. [Acceso a la Ficha](#acceso-a-la-ficha)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Datos Descriptivos del Sitio](#datos-descriptivos-del-sitio)
5. [Barra de Herramientas DBMS](#barra-de-herramientas-dbms)
6. [Funcionalidades SIG](#funcionalidades-sig)
7. [Generación de Fichas UE](#generación-de-fichas-ue)
8. [MoveCost - Análisis de Rutas](#movecost---análisis-de-rutas)
9. [Exportación de Informes](#exportación-de-informes)
10. [Workflow Operativo](#workflow-operativo)

---

## Introducción

La **Ficha de Sitio** es el punto de partida para la documentación de una excavación arqueológica en PyArchInit. Cada proyecto arqueológico comienza con la creación de un sitio, que funciona como contenedor principal para toda la demás información (Unidades Estratigráficas, Estructuras, Materiales, etc.).

Un **sitio arqueológico** en PyArchInit representa un área geográfica definida donde se desarrollan las actividades de investigación arqueológica. Puede ser una excavación, un área de prospección, un monumento, etc.

> **Video Tutorial**: [Insertar enlace video introducción ficha sitio]

---

## Acceso a la Ficha

Para acceder a la Ficha de Sitio:

1. Menú **PyArchInit** → **Archaeological record management** → **Site**
2. O desde la barra de herramientas PyArchInit, hacer clic en el icono **Sitio**

![Acceso Ficha Sitio](images/02_ficha_sitio/01_menu_ficha_sitio.png)
*Figura 1: Acceso a la Ficha de Sitio desde el menú PyArchInit*

---

## Interfaz de Usuario

La Ficha de Sitio está dividida en diferentes áreas funcionales:

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | **DBMS Toolbar** | Barra de herramientas para navegación y gestión de registros |
| 2 | **Datos Descriptivos** | Campos para insertar la información del sitio |
| 3 | **Generador UE** | Herramienta para crear fichas UE en lote |
| 4 | **GIS Viewer** | Controles para visualización cartográfica |
| 5 | **MoveCost** | Herramientas de análisis espacial avanzado |
| 6 | **Ayuda** | Documentación y video tutoriales |

---

## Datos Descriptivos del Sitio

### Pestaña Datos Descriptivos

#### Campos Obligatorios

| Campo | Descripción | Nota |
|-------|-------------|------|
| **Sitio** | Nombre identificativo del sitio | Campo obligatorio, debe ser único |

#### Campos Geográficos

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **País** | Estado donde se encuentra el sitio | España |
| **Región** | Comunidad autónoma | Andalucía |
| **Provincia** | Provincia | Sevilla |
| **Municipio** | Municipio | Sevilla |

#### Campos Descriptivos

| Campo | Descripción |
|-------|-------------|
| **Nombre** | Nombre extendido/descriptivo del sitio |
| **Definición** | Tipología del sitio (desde tesauro) |
| **Descripción** | Campo de texto libre para descripción detallada |
| **Carpeta** | Ruta a la carpeta local del proyecto |

### Definición del Sitio (Tesauro)

El campo **Definición** utiliza un vocabulario controlado (tesauro). Las opciones disponibles incluyen:

| Definición | Descripción |
|------------|-------------|
| Área de excavación | Zona sometida a investigación estratigráfica |
| Área de prospección | Área de reconocimiento de superficie |
| Sitio arqueológico | Localidad con evidencias arqueológicas |
| Monumento | Estructura monumental individual |
| Necrópolis | Área sepulcral |
| Asentamiento | Área habitacional |
| Santuario | Área sacra/cultual |

### Carpeta del Proyecto

El campo **Carpeta** permite asociar un directorio local al sitio para organizar los archivos del proyecto.

| Botón | Función |
|-------|---------|
| **...** | Explorar para seleccionar la carpeta |
| **Abrir** | Abre la carpeta en el gestor de archivos |

---

## Barra de Herramientas DBMS

La barra de herramientas DBMS proporciona todos los controles para la gestión de registros.

### Indicadores de Estado

| Indicador | Descripción |
|-----------|-------------|
| **DB Info** | Muestra el tipo de base de datos conectada (SQLite/PostgreSQL) |
| **Status** | Estado actual: `Usar` (navegación), `Buscar` (búsqueda), `Nuevo Registro` |
| **Ordenamiento** | Indica si los registros están ordenados |
| **registro n.** | Número del registro actual |
| **registro tot.** | Total de registros |

### Navegación de Registros

| Botón | Icono | Función |
|-------|-------|---------|
| **First rec** | |< | Ir al primer registro |
| **Prev rec** | < | Ir al registro anterior |
| **Next rec** | > | Ir al registro siguiente |
| **Last rec** | >| | Ir al último registro |

### Gestión de Registros

| Botón | Función | Descripción |
|-------|---------|-------------|
| **New record** | Crear nuevo | Prepara el formulario para insertar un nuevo sitio |
| **Save** | Guardar | Guarda las modificaciones o el nuevo registro |
| **Delete record** | Eliminar | Elimina el registro actual (con confirmación) |
| **View all records** | Ver todos | Muestra todos los registros en la base de datos |

### Búsqueda y Ordenamiento

| Botón | Función | Descripción |
|-------|---------|-------------|
| **new search** | Nueva búsqueda | Inicia modo búsqueda |
| **search !!!** | Ejecutar búsqueda | Ejecuta la búsqueda con los criterios insertados |
| **Order by** | Ordenar | Abre panel de ordenamiento |

#### Cómo Realizar una Búsqueda

1. Hacer clic en **new search** - el status cambia a "Buscar"
2. Completar los campos con los criterios de búsqueda
3. Hacer clic en **search !!!** para ejecutar
4. Los resultados se muestran y se puede navegar entre ellos

---

## Funcionalidades SIG

La Ficha de Sitio ofrece diversas funcionalidades de integración SIG.

### Carga de Capas

| Botón | Función |
|-------|---------|
| **GIS viewer** | Carga todas las capas para insertar geometrías |
| **Cargar capa sitio** (icono globo) | Carga solo las capas del sitio actual |
| **Cargar todos los sitios** (icono globo múltiple) | Carga las capas de todos los sitios |

### Geocodificación - Búsqueda de Dirección

La función de geocodificación permite localizar una dirección en el mapa.

1. Insertar la dirección en el campo de texto
2. Hacer clic en **Zoom on**
3. El mapa se centra en la posición encontrada

| Campo | Descripción |
|-------|-------------|
| **Dirección** | Insertar calle, ciudad, país |
| **Zoom on** | Centra el mapa en la dirección |

### Modo SIG Activo

El toggle **Habilitar la carga de búsquedas** activa/desactiva la visualización automática de los resultados de búsqueda en el mapa.

- **Activo**: Las búsquedas se visualizan automáticamente en el mapa
- **Desactivo**: Las búsquedas no modifican la visualización del mapa

### WMS Protecciones Arqueológicas

El botón WMS carga la capa de protecciones arqueológicas del Ministerio de Cultura italiano.

### Base Maps

El botón Base Maps permite cargar mapas base (Google Maps, OpenStreetMap, etc.).

---

## Generación de Fichas UE

Esta funcionalidad permite crear automáticamente un número arbitrario de fichas UE para el sitio actual.

### Parámetros

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Número de Área** | Número del área de excavación | 1 |
| **Número de ficha UE desde el que empezar** | Número inicial UE | 1 |
| **Número de fichas a crear** | Cuántas UE generar | 100 |
| **Tipo** | UE o UEM | UE |

### Procedimiento

1. Asegurarse de estar en el sitio correcto
2. Insertar el número del área
3. Insertar el número UE de inicio
4. Insertar cuántas fichas crear
5. Seleccionar el tipo (UE o UEM)
6. Hacer clic en **Generar UE**

---

## MoveCost - Análisis de Rutas

La sección **MovecostToPyarchinit** integra funciones R para el análisis de rutas de menor coste (Least Cost Path Analysis).

### Prerequisitos

- **R** instalado en el sistema
- Paquete R **movecost** instalado
- **Processing R Provider** plugin activo en QGIS

### Funciones Disponibles

| Función | Descripción |
|---------|-------------|
| **movecost** | Calcula el coste de movimiento y rutas de menor coste desde un punto de origen |
| **movecost by polygon** | Como el anterior, usando un polígono para descargar el DTM |
| **movebound** | Calcula los límites del coste de caminata alrededor de puntos |
| **movcorr** | Calcula corredores de menor coste entre puntos |
| **movalloc** | Asignación territorial basada en costes |

### Add Scripts

El botón **Add scripts** instala automáticamente los scripts R necesarios en el perfil QGIS.

---

## Exportación de Informes

### Exportar Memoria de Excavación

El botón **Exportar** genera un PDF con la memoria de excavación para el sitio actual.

**Nota**: Esta función está en versión de desarrollo y podría contener errores.

El informe incluye:
- Datos identificativos del sitio
- Listado de las UE
- Secuencia estratigráfica
- Matrix de Harris (si está disponible)

---

## Workflow Operativo

### Crear un Nuevo Sitio

#### Paso 1: Abrir la Ficha de Sitio

#### Paso 2: Hacer clic en "New record"
El status cambia a "Nuevo Registro" y los campos se vacían.

#### Paso 3: Completar los Datos Obligatorios
Insertar al menos el nombre del sitio (campo obligatorio).

#### Paso 4: Completar los Datos Geográficos
Insertar país, comunidad autónoma, provincia, municipio.

#### Paso 5: Seleccionar la Definición
Elegir la tipología del sitio desde el tesauro.

#### Paso 6: Añadir Descripción
Completar el campo descripción con información detallada.

#### Paso 7: Guardar
Hacer clic en **Save** para guardar el nuevo sitio.

#### Paso 8: Verificar
El sitio ha sido creado, el status vuelve a "Usar".

### Modificar un Sitio Existente

1. Navegar al sitio a modificar
2. Modificar los campos deseados
3. Hacer clic en **Save**
4. Confirmar el guardado de las modificaciones

### Eliminar un Sitio

**Atención**: La eliminación de un sitio NO elimina automáticamente las UE, estructuras y materiales asociados.

1. Navegar al sitio a eliminar
2. Hacer clic en **Delete record**
3. Confirmar la eliminación

---

## Pestaña Ayuda

La pestaña Ayuda proporciona acceso rápido a la documentación.

| Recurso | Enlace |
|---------|--------|
| Video Tutorial | YouTube |
| Documentación | pyarchinit.github.io |
| Comunidad | Facebook UnaQuantum |

---

## Gestión de Concurrencia (PostgreSQL)

Cuando se usa PostgreSQL en entorno multiusuario, el sistema gestiona automáticamente los conflictos de modificación:

- **Indicador de bloqueo**: Muestra si el registro está siendo modificado por otro usuario
- **Control de versión**: Detecta modificaciones concurrentes
- **Resolución de conflictos**: Permite elegir qué versión mantener

---

## Resolución de Problemas

### El sitio no se guarda
- Verificar que el campo "Sitio" esté completado
- Verificar que el nombre no exista ya en la base de datos

### Las capas SIG no se cargan
- Verificar la conexión a la base de datos
- Verificar que existan geometrías asociadas al sitio

### Error en la geocodificación
- Verificar la conexión a internet
- Comprobar que la dirección esté escrita correctamente

### MoveCost no funciona
- Verificar que R esté instalado
- Verificar que el plugin Processing R Provider esté activo
- Instalar el paquete movecost en R

---

## Notas Técnicas

- **Tabla de base de datos**: `site_table`
- **Campos de base de datos**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Capas SIG asociadas**: PYSITO_POLYGON, PYSITO_POINT
- **Tesauro**: tipologia_sigla = '1.1'

---

*Documentación PyArchInit - Ficha de Sitio*
*Versión: 4.9.x*
*Última actualización: Enero 2026*
