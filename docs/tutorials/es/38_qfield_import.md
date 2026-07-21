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

Barra de menú **pyArchInit → Importar desde QField (GPKG)**.

Se abre el diálogo *Importar desde QField*: QGIS **no se bloquea** durante la
operación porque la copia de fotos y el acceso a WebDAV se ejecutan en un hilo
separado.

---

## 3. Seleccionar la carpeta del proyecto QField

1. Pulsa **Examinar…** y elige la **carpeta del proyecto QField**.
2. El diálogo **escanea los GeoPackages** y rellena automáticamente el
   desplegable **Sitio** con los sitios encontrados.
3. Elige un sitio concreto o deja **Todos los sitios** para importarlo todo.

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
es el comportamiento predeterminado**; añade `--apply` para escribir realmente:

```bash
# Vista previa (simulación, por defecto)
python3 scripts/import_qfield.py --qfield-dir <carpeta>

# Importación real
python3 scripts/import_qfield.py --qfield-dir <carpeta> --apply
```

---

*Documentación PyArchInit — Julio 2026*
