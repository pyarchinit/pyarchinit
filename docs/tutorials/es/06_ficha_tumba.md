# Tutorial 06: Ficha de Tumba

## Introducción

La **Ficha de Tumba** es el módulo de PyArchInit dedicado a la documentación de las sepulturas arqueológicas. Esta herramienta permite registrar todos los aspectos de una tumba: desde la estructura funeraria hasta el rito, desde el ajuar hasta los individuos enterrados.

### Conceptos Básicos

**Tumba en PyArchInit:**
- Una tumba es una estructura funeraria que contiene uno o más individuos
- Está conectada a la Ficha de Estructura (la estructura física de la sepultura)
- Está conectada a la Ficha de Individuos (para los datos antropológicos)
- Documenta rito, ajuar y características de la deposición

**Relaciones:**
```
Tumba → Estructura (contenedor físico)
     → Individuo/s (restos humanos)
     → Ajuar (objetos de acompañamiento)
     → Inventario de Materiales (hallazgos asociados)
```

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha de Tumba** (o **Grave form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Tumba** (símbolo de sepultura)

---

## Vista General de la Interfaz

La ficha presenta un diseño organizado en secciones funcionales:

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | DB Info | Estado del registro, ordenamiento, contador |
| 3 | Campos Identificativos | Sitio, Área, N. Ficha, Estructura |
| 4 | Campos Individuo | Conexión con el individuo |
| 5 | Área de Pestañas | Pestañas temáticas para datos específicos |

---

## Toolbar DBMS

La barra de herramientas principal proporciona las herramientas para la gestión de registros.

### Botones de Navegación

| Icono | Función | Descripción |
|-------|---------|-------------|
| First rec | Ir al primer registro |
| Prev rec | Ir al registro anterior |
| Next rec | Ir al registro siguiente |
| Last rec | Ir al último registro |

### Botones CRUD

| Icono | Función | Descripción |
|-------|---------|-------------|
| New record | Crear un nuevo registro de tumba |
| Save | Guardar las modificaciones |
| Delete | Eliminar el registro actual |

### Botones de Búsqueda

| Icono | Función | Descripción |
|-------|---------|-------------|
| New search | Iniciar nueva búsqueda |
| Search!!! | Ejecutar búsqueda |
| Order by | Ordenar resultados |
| View all | Ver todos los registros |

### Botones Especiales

| Icono | Función | Descripción |
|-------|---------|-------------|
| GIS | Cargar tumba en el mapa |
| PDF export | Exportar a PDF |
| Open directory | Abrir carpeta de exportación |

---

## Campos Identificativos

Los campos identificativos definen de forma única la tumba en la base de datos.

### Sitio

**Campo**: `comboBox_sito`
**Base de datos**: `sito`

Selecciona el sitio arqueológico de pertenencia.

### Área

**Campo**: `comboBox_area`
**Base de datos**: `area`

Área de excavación dentro del sitio.

### Número de Ficha

**Campo**: `lineEdit_nr_scheda`
**Base de datos**: `nr_scheda_taf`

Número progresivo de la ficha de tumba. Se propone automáticamente el siguiente número disponible.

### Sigla y Número de Estructura

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Sigla estructura | `sigla_struttura` | Sigla de la estructura (ej. TM, TB) |
| Nr estructura | `nr_struttura` | Número de la estructura |

Estos campos conectan la tumba con la correspondiente Ficha de Estructura.

### Número de Individuo

**Campo**: `comboBox_nr_individuo`
**Base de datos**: `nr_individuo`

Número del individuo enterrado. Conecta la tumba con la Ficha de Individuos.

**Notas:**
- Una tumba puede contener varios individuos (sepultura múltiple)
- El menú muestra los individuos disponibles para la estructura seleccionada

---

## Pestaña Datos Descriptivos

La primera pestaña contiene los campos fundamentales para describir la sepultura.

### Rito

**Campo**: `comboBox_rito`
**Base de datos**: `rito`

Tipo de ritual funerario practicado.

**Valores típicos:**
| Rito | Descripción |
|------|-------------|
| Inhumación | Deposición del cuerpo entero |
| Cremación | Incineración de los restos |
| Incineración primaria | Cremación in situ |
| Incineración secundaria | Cremación en otro lugar y deposición |
| Mixto | Combinación de ritos |
| Indeterminado | No determinable |

### Tipo de Sepultura

**Campo**: `comboBox_tipo_sepoltura`
**Base de datos**: `tipo_sepoltura`

Clasificación tipológica de la sepultura.

**Ejemplos:**
- Tumba de fosa simple
- Tumba de caja
- Tumba de cámara
- Tumba a la cappuccina
- Tumba de enchytrismos
- Sarcófago
- Osario

### Tipo de Deposición

**Campo**: `comboBox_tipo_deposizione`
**Base de datos**: `tipo_deposizione`

Modalidad de deposición del cuerpo.

**Valores:**
- Primaria (deposición directa)
- Secundaria (reducción/desplazamiento)
- Múltiple simultánea
- Múltiple sucesiva

### Estado de Conservación

**Campo**: `comboBox_stato_conservazione`
**Base de datos**: `stato_di_conservazione`

Evaluación del estado de conservación.

**Escala:**
- Óptimo
- Bueno
- Regular
- Malo
- Pésimo

### Descripción

**Campo**: `textEdit_descrizione`
**Base de datos**: `descrizione_taf`

Descripción detallada de la tumba.

**Contenidos recomendados:**
- Forma y dimensiones de la fosa
- Orientación
- Profundidad
- Características del relleno
- Estado en el momento de la excavación

### Interpretación

**Campo**: `textEdit_interpretazione`
**Base de datos**: `interpretazione_taf`

Interpretación histórico-arqueológica de la sepultura.

---

## Características de la Tumba

### Señalizadores

**Campo**: `comboBox_segnacoli`
**Base de datos**: `segnacoli`

Presencia y tipo de señalizadores funerarios.

**Valores:**
- Ausente
- Estela
- Cipo
- Túmulo
- Recinto
- Otro

### Canal Libatorio

**Campo**: `comboBox_canale_libatorio`
**Base de datos**: `canale_libatorio_si_no`

Presencia de canal para libaciones rituales.

**Valores:** Sí / No

### Cubierta

**Campo**: `comboBox_copertura_tipo`
**Base de datos**: `copertura_tipo`

Tipo de cubierta de la tumba.

**Ejemplos:**
- Tejas
- Losas de piedra
- Tablas de madera
- Tierra
- Ausente

### Contenedor de Restos

**Campo**: `comboBox_tipo_contenitore`
**Base de datos**: `tipo_contenitore_resti`

Tipo de contenedor para los restos.

**Ejemplos:**
- Fosa terragna
- Caja de madera
- Caja de piedra
- Ánfora
- Urna
- Sarcófago

### Objetos Externos

**Campo**: `comboBox_oggetti_esterno`
**Base de datos**: `oggetti_rinvenuti_esterno`

Objetos encontrados fuera de la tumba pero asociados a ella.

---

## Pestaña Ajuar

Esta pestaña gestiona la documentación del ajuar funerario.

### Presencia de Ajuar

**Campo**: `comboBox_corredo_presenza`
**Base de datos**: `corredo_presenza`

Indica si la tumba contenía ajuar.

**Valores:**
- Sí
- No
- Probable
- Retirado

### Tipo de Ajuar

**Campo**: `comboBox_corredo_tipo`
**Base de datos**: `corredo_tipo`

Clasificación general del ajuar.

**Categorías:**
- Personal (joyas, fíbulas)
- Ritual (vasos, lucernas)
- Simbólico (monedas, amuletos)
- Instrumental (herramientas)
- Mixto

### Descripción del Ajuar

**Campo**: `textEdit_corredo_descrizione`
**Base de datos**: `corredo_descrizione`

Descripción detallada de los objetos del ajuar.

### Tabla de Ajuar

**Widget**: `tableWidget_corredo_tipo`

Tabla para registrar los elementos individuales del ajuar.

**Columnas:**
| Columna | Descripción |
|---------|-------------|
| ID Hallazgo | Número de inventario del hallazgo |
| ID Indiv. | Individuo asociado |
| Material | Tipo de material |
| Posición del ajuar | Dónde estaba colocado en la tumba |
| Posición en el ajuar | Posición respecto al cuerpo |

**Notas:**
- Los elementos están conectados a la Ficha de Inventario de Materiales
- La tabla se completa automáticamente con los hallazgos de la estructura

---

## Pestaña Otras Características

Esta pestaña contiene información adicional sobre la sepultura.

### Periodización

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Periodo inicial | `periodo_iniziale` | Periodo de inicio de uso |
| Fase inicial | `fase_iniziale` | Fase en el periodo |
| Periodo final | `periodo_finale` | Periodo de fin de uso |
| Fase final | `fase_finale` | Fase en el periodo |
| Datación extendida | `datazione_estesa` | Datación literal |

Los valores se completan según la Ficha de Periodización del sitio.

---

## Pestaña Herramientas

La pestaña Herramientas contiene funcionalidades adicionales.

### Gestión de Medios

Permite:
- Visualizar imágenes asociadas
- Añadir nuevas fotos mediante drag & drop
- Buscar medios en la base de datos

### Exportación

Opciones de exportación:
- Lista de Tumbas (lista sintética)
- Fichas de Tumbas (fichas completas)
- Conversión PDF a Word

---

## Integración SIG

### Visualización en Mapa

| Botón | Función |
|-------|---------|
| GIS Toggle | Activar/desactivar carga automática |
| Load to GIS | Cargar la tumba en el mapa |

### Capa SIG

La ficha utiliza capas específicas para las tumbas:
- **pyarchinit_tomba**: geometría de las tumbas
- Conexión con capas de estructuras y UE

---

## Exportación e Impresión

### Export PDF

El botón PDF abre un panel con opciones:

| Opción | Descripción |
|--------|-------------|
| Lista de Tumbas | Lista sintética de las tumbas |
| Fichas de Tumbas | Fichas completas detalladas |
| Imprimir | Genera el PDF |

### Contenido de la Ficha PDF

La ficha PDF incluye:
- Datos identificativos
- Rito y tipo de sepultura
- Descripción e interpretación
- Datos del ajuar
- Periodización
- Imágenes asociadas

---

## Workflow Operativo

### Creación de Nueva Tumba

1. **Apertura de la ficha**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en "New Record"
   - El número de ficha se propone automáticamente

3. **Datos identificativos**
   ```
   Sitio: Necrópolis de Isola Sacra
   Área: 1
   N. Ficha: 45
   Sigla estructura: TM
   Nr estructura: 45
   ```

4. **Conexión con individuo**
   ```
   Nr Individuo: 1
   ```

5. **Datos descriptivos** (Pestaña 1)
   ```
   Rito: Inhumación
   Tipo sepultura: Tumba de fosa simple
   Tipo deposición: Primaria
   Estado conservación: Bueno

   Descripción: Fosa rectangular con esquinas
   redondeadas, orientada E-W...

   Señalizadores: Cipo
   Cubierta: Tejas a la cappuccina
   ```

6. **Ajuar** (Pestaña 2)
   ```
   Presencia: Sí
   Tipo: Personal
   Descripción: Fíbula de bronce junto al
   hombro derecho, moneda junto a la boca...
   ```

7. **Periodización**
   ```
   Periodo inicial: II - Fase A
   Periodo final: II - Fase A
   Datación: siglo II d.C.
   ```

8. **Guardado**
   - Clic en "Save"

### Búsqueda de Tumbas

1. Clic en "New Search"
2. Completar criterios:
   - Sitio
   - Rito
   - Tipo de sepultura
   - Periodo
3. Clic en "Search"
4. Navegar entre los resultados

---

## Relaciones con Otras Fichas

| Ficha | Relación |
|-------|----------|
| **Ficha de Sitio** | El sitio contiene las tumbas |
| **Ficha de Estructura** | La estructura física de la tumba |
| **Ficha de Individuos** | Los restos humanos en la tumba |
| **Ficha de Inventario de Materiales** | Los hallazgos del ajuar |
| **Ficha de Periodización** | La cronología |

### Flujo de Trabajo Recomendado

1. Crear la **Ficha de Sitio** (si no existe)
2. Crear la **Ficha de Estructura** para la tumba
3. Crear la **Ficha de Tumba** conectándola a la estructura
4. Crear la **Ficha de Individuos** para cada individuo
5. Registrar el ajuar en la **Ficha de Inventario de Materiales**

---

## Buenas Prácticas

### Nomenclatura

- Usar siglas coherentes (TM, TB, SEP)
- Numeración progresiva dentro del sitio
- Documentar las convenciones adoptadas

### Descripción

- Describir sistemáticamente forma, dimensiones, orientación
- Documentar el estado en el momento de la excavación
- Separar observaciones objetivas de interpretaciones

### Ajuar

- Registrar posición exacta de cada objeto
- Conectar cada elemento al Inventario de Materiales
- Documentar asociaciones significativas

### Periodización

- Basar la datación en elementos diagnósticos
- Indicar el grado de fiabilidad
- Comparar con sepulturas similares

---

## Resolución de Problemas

### Problema: Individuo no disponible en el menú

**Causa**: El individuo no ha sido creado todavía o no está asociado a la estructura.

**Solución**:
1. Verificar que exista la Ficha de Individuos
2. Comprobar que el individuo esté asociado a la misma estructura

### Problema: Ajuar no visualizado en la tabla

**Causa**: Los hallazgos no están conectados a la estructura.

**Solución**:
1. Abrir la Ficha de Inventario de Materiales
2. Verificar que los hallazgos tengan la estructura correcta
3. Actualizar la ficha de Tumba

### Problema: Tumba no visible en el mapa

**Causa**: Geometría no asociada.

**Solución**:
1. Verificar que exista la capa de tumbas
2. Comprobar que la estructura tenga geometría
3. Verificar el sistema de referencia

---

## Referencias

### Base de Datos

- **Tabla**: `tomba_table`
- **Clase mapper**: `TOMBA`
- **ID**: `id_tomba`

### Archivos Fuente

- **UI**: `gui/ui/Tomba.ui`
- **Controlador**: `tabs/Tomba.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
