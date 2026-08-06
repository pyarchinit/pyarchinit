# Tutorial 38: Importar desde QField (GPKG)

## Introducción

La función **Importar desde QField (GPKG)** incorpora a pyArchInit los datos
recogidos en el campo con **QField** mediante el complemento asociado
**pyarchinit-qfield**. El comando lee los GeoPackages (`.gpkg`) del proyecto
QField y las fotografías tomadas en el campo, y **añade** los registros a la base
de datos de pyArchInit sin duplicar las UE y los materiales ya existentes: de los
registros existentes rellena **solo los campos vacíos**, sin sobrescribir nunca
los valores ya presentes.

El flujo está pensado para ser **seguro**: primero se ejecuta una **Vista previa
(simulación)** que simula todo sin escribir nada, y después —solo tras
confirmación— se lanza la **Importación** real en una única transacción.

> Requisito: los datos deben haberse recogido en el campo con **QField** usando
> el complemento asociado **pyarchinit-qfield**.

---

## 1. Requisitos previos

- Datos recogidos en el campo con **QField** mediante el complemento
  **pyarchinit-qfield**.
- La carpeta del proyecto QField contiene los archivos **`.gpkg`** y las fotos
  bajo **`DCIM/pyarchinit`**.
- Una base de datos pyArchInit configurada (SQLite/Spatialite o
  PostgreSQL/PostGIS): la BD se **resuelve automáticamente** desde la
  configuración del complemento.

---

## 2. Abrir el diálogo

El comando puede abrirse de **dos maneras**:

1. **Menú**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Barra de herramientas** (novedad): en la barra de herramientas de
   pyArchInit, abre el **botón desplegable de las herramientas de análisis**
   —el mismo que agrupa GeoArchaeo, MoveCost, Palimpsest y otras
   herramientas— y elige **Importa da QField (GPKG)**. La entrada se reconoce
   por su **nuevo icono dedicado**: una tesela verde redondeada al estilo
   QField con un marcador blanco que desciende hacia una bandeja de
   importación.

En ambos casos se abre el diálogo *Importar desde QField*: QGIS **no se
bloquea** durante la operación porque la copia de fotos y el acceso a WebDAV se
ejecutan en un hilo separado.

---

## 3. Seleccionar la fuente: carpeta o archivo ZIP

1. Pulsa **Examinar…** y elige la **carpeta del proyecto QField**, o pulsa
   **Archivo ZIP…** y elige un archivo **`.zip`** del proyecto QField (el
   selector de archivos filtra por `*.zip`). En ambos casos, la ruta elegida
   aparece en el mismo campo de origen.
2. Si eliges una carpeta, el diálogo **escanea los GeoPackages** y rellena
   automáticamente el desplegable **Sitio** con los sitios encontrados.
3. Si eliges un archivo ZIP, se **extrae automáticamente** a una carpeta
   temporal y el desplegable **Sitio** se restablece a **Todos los sitios**
   (no se realiza ningún escaneo previo de sitios desde un zip): la
   importación (Vista previa/simulación o Importar, fotos y miniaturas
   incluidas) se ejecuta sobre el árbol extraído, y la carpeta temporal se
   **elimina automáticamente** al finalizar la operación, incluso en caso de
   error.
4. Elige un sitio concreto o deja **Todos los sitios** para importarlo todo.

> Mientras una importación está en curso, tanto **Examinar…** como
> **Archivo ZIP…** están **deshabilitados**, como el resto de controles del
> diálogo.

> Si el archivo elegido está **corrupto o no es válido**, se muestra un error
> claro: **«Archivio ZIP non valido o corrotto: …»**. Si el zip no contiene
> ningún archivo **`.gpkg`**, se muestra en su lugar el habitual error de
> «no se han encontrado capas».

---

## 4. Opciones de importación

| Opción | Significado |
|---|---|
| **SRID (vacío = del GPKG)** | sistema de referencia; déjalo vacío para leerlo del GeoPackage |
| **Destino de fotos** | precargado con la carpeta de medios configurada (local o WebDAV) |
| **Deduplicar geometrías** | evita reinsertar geometrías idénticas ya presentes |
| **Copiar fotos** | copia las fotos al backend de medios |
| **Generar miniaturas** | crea automáticamente las miniaturas de las fotos |

Las tres casillas están **activadas por defecto**.

---

## 5. Vista previa (simulación)

Pulsa **Vista previa (simulación)**: toda la importación se ejecuta en
**simulación**, **sin escribir nada** en la base de datos. El registro muestra:

- cuántas **UE**, **materiales**, **geometrías**, **puntos de cota**, **fotos** y
  **enlaces** se importarían;
- exactamente **qué campos vacíos** de los registros existentes se rellenarían.

Es el paso que debe usarse siempre para comprobar el resultado antes de escribir.

---

## 6. Importar

Pulsa **Importar** (se solicita una **confirmación**). La operación:

- **añade** los registros en **una única transacción**;
- **no duplica** las UE y los materiales existentes: rellena **solo sus campos
  vacíos**, sin sobrescribir nunca los valores ya presentes;
- **copia las fotos** al backend de medios y **genera sus miniaturas**
  automáticamente;
- asigna a los registros importados un **`node_uuid`** y los marca con
  **`created_by = 'qfield_import'`**.

---

## 7. Después de la importación

Comprueba las **relaciones estratigráficas** de las UE importadas: **no se
deducen automáticamente** y deben completarse a mano en la ficha UE.

---

## 8. Alternativa por línea de comandos (CLI)

Para usos avanzados o sin interfaz hay un script CLI disponible. La **simulación
es el comportamiento predeterminado**; añade `--apply` para escribir realmente.
El parámetro `--qfield-dir` acepta tanto la **carpeta del proyecto** como un
**archivo `.zip`**: si apunta a un zip, se extrae automáticamente a una
carpeta temporal, que se elimina al finalizar la ejecución. Un origen
inexistente termina con el error **«Sorgente non trovata (cartella o archivio
.zip): …»**.

```bash
# Vista previa (simulación, por defecto) desde una carpeta
python3 scripts/import_qfield.py --qfield-dir <carpeta>

# Vista previa (simulación, por defecto) desde un archivo ZIP
python3 scripts/import_qfield.py --qfield-dir <archivo.zip>

# Importación real
python3 scripts/import_qfield.py --qfield-dir <carpeta> --apply
```

---

*Documentación PyArchInit — Julio 2026*
