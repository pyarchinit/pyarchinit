# Tutorial 04: Ficha de Periodización

## Índice
1. [Introducción](#introducción)
2. [Acceso a la Ficha](#acceso-a-la-ficha)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Conceptos Fundamentales](#conceptos-fundamentales)
5. [Campos de la Ficha](#campos-de-la-ficha)
6. [Toolbar DBMS](#toolbar-dbms)
7. [Funcionalidades SIG](#funcionalidades-sig)
8. [Export PDF](#export-pdf)
9. [Integración IA](#integración-ia)
10. [Workflow Operativo](#workflow-operativo)
11. [Buenas Prácticas](#buenas-prácticas)
12. [Resolución de Problemas](#resolución-de-problemas)

---

## Introducción

La **Ficha de Periodización** es una herramienta fundamental para la gestión de las fases cronológicas de una excavación arqueológica. Permite definir los periodos y las fases que caracterizan la secuencia estratigráfica del sitio, asociando a cada par periodo/fase una datación cronológica y una descripción.

### Propósito de la Ficha

- Definir la secuencia cronológica de la excavación
- Asociar periodos y fases a las unidades estratigráficas
- Gestionar la cronología absoluta (años) y relativa (periodos históricos)
- Visualizar las UE por periodo/fase en el mapa SIG
- Generar informes PDF de la periodización

### Relación con otras Fichas

La Ficha de Periodización está estrechamente vinculada a:
- **Ficha UE/UEM**: Cada UE se asigna a un periodo y una fase
- **Ficha de Sitio**: Los periodos son específicos para cada sitio
- **Matrix de Harris**: Los periodos colorean el Matrix por fase cronológica

---

## Acceso a la Ficha

### Desde Menú

1. Abrir QGIS con el plugin PyArchInit activo
2. Menú **PyArchInit** → **Archaeological record management** → **Excavation - Loss of use calculation** → **Period and Phase**

### Desde Toolbar

1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Periodización** (icono sitio con reloj)

---

## Interfaz de Usuario

La interfaz de la Ficha de Periodización está organizada de forma sencilla y lineal:

### Áreas Principales

| Área | Descripción |
|------|-------------|
| **1. DBMS Toolbar** | Barra de herramientas para navegación y gestión de registros |
| **2. Indicadores de Estado** | DB Info, Status, Ordenamiento |
| **3. Datos Identificativos** | Sitio, Periodo, Fase, Código de periodo |
| **4. Datos Descriptivos** | Descripción textual del periodo |
| **5. Cronología** | Años inicial y final |
| **6. Datación Extendida** | Selección desde vocabulario de épocas históricas |

---

## Conceptos Fundamentales

### Periodo y Fase

El sistema de periodización en PyArchInit se basa en una estructura jerárquica de dos niveles:

#### Periodo
El **Periodo** representa una macro-fase cronológica de la excavación. Se identifica con un número entero (1, 2, 3, ...) y representa las grandes subdivisiones de la secuencia estratigráfica.

Ejemplos de periodos:
- Periodo 1: Época contemporánea
- Periodo 2: Época medieval
- Periodo 3: Época romana imperial
- Periodo 4: Época romana republicana

#### Fase
La **Fase** representa una subdivisión interna del periodo. También se identifica con un número entero y permite detallar más la secuencia.

Ejemplos de fases en el Periodo 3 (Época romana imperial):
- Fase 1: Siglos III-IV d.C.
- Fase 2: Siglo II d.C.
- Fase 3: Siglo I d.C.

### Código de Periodo

El **Código de Periodo** es un identificador numérico único que vincula el par periodo/fase a las UE. Cuando se asigna un periodo/fase a una UE en la Ficha UE, se utiliza este código.

> **Importante**: El código de periodo debe ser único para cada combinación sitio/periodo/fase.

### Esquema Conceptual

```
Sitio
└── Periodo 1 (Época contemporánea)
│   ├── Fase 1 → Código 101
│   └── Fase 2 → Código 102
├── Periodo 2 (Época medieval)
│   ├── Fase 1 → Código 201
│   ├── Fase 2 → Código 202
│   └── Fase 3 → Código 203
└── Periodo 3 (Época romana)
    ├── Fase 1 → Código 301
    └── Fase 2 → Código 302
```

---

## Campos de la Ficha

### Campos Identificativos

#### Sitio
- **Tipo**: ComboBox (solo lectura en modo navegación)
- **Obligatorio**: Sí
- **Descripción**: Selecciona el sitio arqueológico al que pertenece la periodización

#### Periodo
- **Tipo**: ComboBox editable
- **Obligatorio**: Sí
- **Valores**: Números enteros del 1 al 15 (predefinidos) o valores personalizados
- **Descripción**: Número del periodo cronológico
- **Nota**: Los números bajos indican periodos más recientes, los números altos periodos más antiguos

#### Fase
- **Tipo**: ComboBox editable
- **Obligatorio**: Sí
- **Valores**: Números enteros del 1 al 15 (predefinidos) o valores personalizados
- **Descripción**: Número de la fase dentro del periodo

#### Código de Periodo
- **Tipo**: LineEdit (texto)
- **Obligatorio**: No (pero muy recomendado)
- **Descripción**: Código numérico único para identificar el par periodo/fase
- **Sugerencia**: Usar una convención como `[periodo][fase]` (ej. 101, 102, 201, 301)

### Campos Descriptivos

#### Descripción
- **Tipo**: TextEdit (multilínea)
- **Obligatorio**: No
- **Descripción**: Descripción textual del periodo/fase
- **Contenido sugerido**:
  - Características generales del periodo
  - Eventos históricos relacionados
  - Tipologías de estructuras/materiales esperados
  - Referencias bibliográficas

### Campos Cronológicos

#### Cronología Inicial
- **Tipo**: LineEdit (numérico)
- **Obligatorio**: No
- **Formato**: Año numérico
- **Notas**:
  - Valores positivos = d.C.
  - Valores negativos = a.C.
  - Ejemplo: `-100` para 100 a.C., `200` para 200 d.C.

#### Cronología Final
- **Tipo**: LineEdit (numérico)
- **Obligatorio**: No
- **Formato**: Año numérico (mismas convenciones que Cronología Inicial)

#### Datación Extendida (Épocas Históricas)
- **Tipo**: ComboBox editable con vocabulario precargado
- **Obligatorio**: No
- **Descripción**: Selección desde un vocabulario de épocas históricas predefinidas
- **Funcionalidad automática**: Al seleccionar una época, los campos Cronología Inicial y Final se rellenan automáticamente

### Vocabulario de Épocas Históricas

El vocabulario incluye una amplia gama de periodos históricos:

| Categoría | Ejemplos |
|-----------|----------|
| **Época Contemporánea** | Siglo XXI, Siglo XX |
| **Época Moderna** | Siglos XIX-XVI |
| **Época Medieval** | Siglos XV-VIII |
| **Época Antigua** | Siglos VII-I |
| **Imperio Romano** | Periodos específicos (Julio-Claudio, Flavio, etc.) |
| **Imperio Bizantino** | Periodos específicos |
| **Prehistoria** | Paleolítico, Mesolítico, Neolítico, Edad del Bronce, Edad del Hierro |

---

## Toolbar DBMS

La barra de herramientas DBMS permite la gestión completa de los registros.

### Botones de Navegación

| Icono | Nombre | Función |
|-------|--------|---------|
| ![First] | First | Ir al primer registro |
| ![Prev] | Prev | Ir al registro anterior |
| ![Next] | Next | Ir al registro siguiente |
| ![Last] | Last | Ir al último registro |

### Botones de Gestión de Registros

| Icono | Nombre | Función |
|-------|--------|---------|
| ![New] | New record | Crear un nuevo registro |
| ![Save] | Save | Guardar las modificaciones |
| ![Delete] | Delete | Eliminar el registro actual |
| ![View All] | View all | Ver todos los registros |

### Botones de Búsqueda

| Icono | Nombre | Función |
|-------|--------|---------|
| ![New Search] | New search | Activar modo búsqueda |
| ![Search] | Search!!! | Ejecutar la búsqueda |
| ![Sort] | Order by | Ordenar los registros |

### Indicadores de Estado

| Indicador | Descripción |
|-----------|-------------|
| **Status** | Modo actual: "Usar" (navegación), "Buscar" (búsqueda), "Nuevo Registro" |
| **Ordenamiento** | "No ordenados" u "Ordenados" |
| **registro n.** | Número del registro actual |
| **registro tot.** | Número total de registros |

---

## Funcionalidades SIG

La Ficha de Periodización ofrece potentes funcionalidades de visualización SIG para ver las UE asociadas a cada periodo/fase.

### Botones SIG

#### Visualizar Periodo Individual (Icono SIG)
- **Función**: Carga en el mapa QGIS todas las UE asociadas al periodo/fase actual
- **Requisito**: El campo Código de Periodo debe estar rellenado
- **Capas cargadas**: UE y UEM filtradas por código de periodo

#### Visualizar Todos los Periodos - UE (Icono Capas múltiples)
- **Función**: Carga en el mapa todos los periodos como capas separadas (solo UE)
- **Resultado**: Una capa para cada combinación periodo/fase

#### Visualizar Todos los Periodos - UEM (Icono SIG3)
- **Función**: Carga en el mapa todos los periodos como capas separadas (solo UEM)
- **Resultado**: Una capa para cada combinación periodo/fase para las unidades murarias

### Visualización en Mapa

Cuando se cargan las capas por periodo:
- Cada periodo/fase tiene un color distintivo
- Las UE están filtradas según el código de periodo asignado
- Es posible activar/desactivar las capas individuales

---

## Export PDF

La ficha ofrece dos modos de exportación PDF:

### Exportar Ficha Individual

- **Icono**: PDF
- **Función**: Genera un PDF con los datos del periodo/fase actual
- **Contenido**:
  - Información identificativa (Sitio, Periodo, Fase)
  - Cronología (inicial, final, datación extendida)
  - Descripción completa

### Exportar Lista de Periodización

- **Icono**: Hoja/Sheet
- **Función**: Genera un PDF con el listado de todos los periodos/fases del sitio
- **Contenido**: Tabla resumen con todos los periodos

---

## Integración IA

La Ficha de Periodización incluye una integración con GPT para obtener sugerencias automáticas sobre la descripción de los periodos históricos.

### Botón Sugerencias

### Funcionamiento

1. Seleccionar una época histórica del campo **Datación Extendida**
2. Hacer clic en el botón **Sugerencias**
3. Seleccionar el modelo GPT a utilizar (gpt-4o o gpt-4)
4. El sistema genera automáticamente:
   - Una descripción del periodo histórico
   - 3 enlaces de Wikipedia relevantes
5. El texto generado puede insertarse en el campo Descripción

### Configuración de API Key

Para utilizar esta funcionalidad:
1. Obtener una API Key de OpenAI
2. En el primer uso, el sistema pide insertar la clave
3. La clave se guarda en `PYARCHINIT_HOME/bin/gpt_api_key.txt`

> **Nota**: Esta funcionalidad requiere conexión a internet y una cuenta OpenAI con créditos disponibles.

---

## Workflow Operativo

### Creación de una Nueva Periodización

#### Paso 1: Acceso a la Ficha
1. Abrir la Ficha de Periodización desde el menú o la barra de herramientas
2. Verificar la conexión a la base de datos (indicador Status)

#### Paso 2: Nuevo Registro
1. Hacer clic en el botón **New record**
2. El Status cambia a "Nuevo Registro"
3. Los campos se vuelven editables

#### Paso 3: Selección del Sitio
1. Si no está preestablecido, seleccionar el **Sitio** del menú desplegable
2. El sitio debe existir ya en la Ficha de Sitio

#### Paso 4: Definición de Periodo y Fase
1. Seleccionar o escribir el número del **Periodo**
2. Seleccionar o escribir el número de la **Fase**
3. Insertar el **Código de Periodo** único

#### Paso 5: Cronología
1. Seleccionar la **Datación Extendida** del vocabulario de épocas
2. Los campos Cronología Inicial y Final se rellenan automáticamente
3. O bien insertar manualmente los años

#### Paso 6: Descripción
1. Rellenar el campo **Descripción** con la información sobre el periodo
2. Opcional: usar el botón **Sugerencias** para obtener un texto con IA

#### Paso 7: Guardado
1. Hacer clic en el botón **Save**
2. El registro se guarda en la base de datos
3. El Status vuelve a "Usar"

### Esquema de Periodización Recomendado

Para una excavación típica, se recomienda crear la periodización siguiendo este esquema:

| Periodo | Fase | Código | Descripción |
|---------|------|--------|-------------|
| 1 | 1 | 101 | Época contemporánea - Arado |
| 1 | 2 | 102 | Época contemporánea - Abandono |
| 2 | 1 | 201 | Época medieval - Fase tardía |
| 2 | 2 | 202 | Época medieval - Fase central |
| 2 | 3 | 203 | Época medieval - Fase inicial |
| 3 | 1 | 301 | Época romana - Fase imperial |
| 3 | 2 | 302 | Época romana - Fase republicana |
| 4 | 1 | 401 | Época prerromana |

---

## Buenas Prácticas

### Convenciones de Numeración

1. **Periodos**: Numerar del más reciente (1) al más antiguo
2. **Fases**: Numerar de la más reciente (1) a la más antigua dentro del periodo
3. **Códigos**: Usar la fórmula `[periodo * 100 + fase]` para códigos únicos

### Descripciones Eficaces

Una buena descripción del periodo debería incluir:
- Encuadramiento cronológico
- Características principales del periodo
- Tipos de estructuras/materiales esperados
- Comparaciones con otros sitios coetáneos
- Referencias bibliográficas

### Gestión de la Cronología

- Usar siempre años numéricos para las cronologías
- Para fechas a.C., usar números negativos
- Verificar la coherencia: la cronología final debe ser >= inicial (en valor absoluto para a.C.)

### Vinculación con las UE

Después de crear la periodización:
1. Abrir la Ficha UE
2. En la pestaña **Periodización**, asignar Periodo inicial/final y Fase inicial/final
3. El sistema asociará automáticamente la UE a la periodización

---

## Resolución de Problemas

### Problemas Comunes

#### "Period code not add"
- **Causa**: El campo Código de Periodo está vacío
- **Solución**: Rellenar el campo Código de Periodo antes de usar las funciones SIG

#### La cronología no se rellena automáticamente
- **Causa**: La época seleccionada no tiene datos asociados
- **Solución**: Verificar que la época esté presente en el archivo CSV de épocas históricas

#### Error en el guardado: registro duplicado
- **Causa**: Ya existe un registro con la misma combinación Sitio/Periodo/Fase
- **Solución**: Verificar los valores y usar una combinación única

#### Las UE no aparecen en la visualización SIG
- **Causa**: Las UE no tienen el código de periodo asignado
- **Solución**:
  1. Verificar en la Ficha UE que los campos Periodo/Fase estén rellenados
  2. Verificar que el Código de Periodo corresponda

#### Sugerencias IA no funciona
- **Causa**: API Key faltante o no válida
- **Solución**:
  1. Verificar la conexión a internet
  2. Comprobar la validez de la API Key
  3. Reinstalar las librerías: `pip install --upgrade openai pydantic`

---

## Resumen de Campos

| Campo | Tipo | Obligatorio | Base de datos |
|-------|------|-------------|---------------|
| Sitio | ComboBox | Sí | sito |
| Periodo | ComboBox | Sí | periodo |
| Fase | ComboBox | Sí | fase |
| Código de Periodo | LineEdit | No | cont_per |
| Descripción | TextEdit | No | descrizione |
| Cronología Inicial | LineEdit | No | cron_iniziale |
| Cronología Final | LineEdit | No | cron_finale |
| Datación Extendida | ComboBox | No | datazione_estesa |

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
