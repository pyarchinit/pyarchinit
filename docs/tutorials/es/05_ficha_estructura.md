# Tutorial 05: Ficha de Estructura

## Introducción

La **Ficha de Estructura** es el módulo de PyArchInit dedicado a la documentación de las estructuras arqueológicas. Una estructura es un conjunto organizado de Unidades Estratigráficas (UE/UEM) que forman una entidad constructiva o funcional reconocible, como un muro, una pavimentación, una tumba, un horno, o cualquier otro elemento construido.

### Conceptos Básicos

**Estructura vs Unidad Estratigráfica:**
- Una **UE** es la unidad individual (estrato, corte, relleno)
- Una **Estructura** agrupa varias UE relacionadas funcionalmente
- Ejemplo: un muro (estructura) está compuesto por cimentación, alzado, mortero (diferentes UE)

**Jerarquías:**
- Las estructuras pueden tener relaciones entre ellas
- Cada estructura pertenece a uno o más periodos/fases cronológicas
- Las estructuras están vinculadas a las UE que las componen

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Gestión de Estructuras** (o **Structure form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Estructura** (edificio estilizado)

---

## Vista General de la Interfaz

La ficha presenta un diseño organizado en secciones funcionales:

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | DB Info | Estado del registro, ordenamiento, contador |
| 3 | Campos Identificativos | Sitio, Sigla, Número de estructura |
| 4 | Campos de Clasificación | Categoría, Tipología, Definición |
| 5 | Área de Pestañas | Pestañas temáticas para datos específicos |

---

## Toolbar DBMS

La barra de herramientas principal proporciona todas las herramientas para la gestión de registros.

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
| New record | Crear un nuevo registro de estructura |
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
| Map preview | Activar/desactivar vista previa del mapa |
| Media preview | Activar/desactivar vista previa de medios |
| Draw structure | Dibujar estructura en el mapa |
| Load to GIS | Cargar estructura en el mapa |
| Load all | Cargar todas las estructuras |
| PDF export | Exportar a PDF |
| Open directory | Abrir carpeta de exportación |

---

## Campos Identificativos

Los campos identificativos definen de forma única la estructura en la base de datos.

### Sitio

**Campo**: `comboBox_sito`
**Base de datos**: `sito`

Selecciona el sitio arqueológico de pertenencia. El menú desplegable muestra todos los sitios registrados en la base de datos.

**Notas:**
- Campo obligatorio
- La combinación Sitio + Sigla + Número debe ser única
- Bloqueado después de la creación del registro

### Sigla de Estructura

**Campo**: `comboBox_sigla_struttura`
**Base de datos**: `sigla_struttura`

Código alfanumérico que identifica el tipo de estructura. Convenciones comunes:

| Sigla | Significado | Ejemplo |
|-------|-------------|---------|
| MR | Muro | MR 1 |
| ST | Estructura | ST 5 |
| PV | Pavimentación | PV 2 |
| FO | Horno | FO 1 |
| VA | Balsa | VA 3 |
| TM | Tumba | TM 10 |
| PT | Pozo | PT 2 |
| CN | Canal | CN 1 |

### Número de Estructura

**Campo**: `numero_struttura`
**Base de datos**: `numero_struttura`

Número progresivo de la estructura dentro de la sigla.

**Notas:**
- Campo numérico
- Debe ser único para la combinación Sitio + Sigla
- Bloqueado después de la creación

---

## Campos de Clasificación

Los campos de clasificación definen la naturaleza de la estructura.

### Categoría de Estructura

**Campo**: `comboBox_categoria_struttura`
**Base de datos**: `categoria_struttura`

Macro-categoría funcional de la estructura.

**Valores típicos:**
- Residencial
- Productiva
- Funeraria
- Religiosa
- Defensiva
- Hidráulica
- Viaria
- Artesanal

### Tipología de Estructura

**Campo**: `comboBox_tipologia_struttura`
**Base de datos**: `tipologia_struttura`

Tipología específica dentro de la categoría.

**Ejemplos por categoría:**
| Categoría | Tipologías |
|-----------|------------|
| Residencial | Casa, Villa, Palacio, Cabaña |
| Productiva | Horno, Molino, Almazara |
| Funeraria | Tumba de fosa, Tumba de cámara, Sarcófago |
| Hidráulica | Pozo, Cisterna, Acueducto, Canal |

### Definición de Estructura

**Campo**: `comboBox_definizione_struttura`
**Base de datos**: `definizione_struttura`

Definición sintética y específica del elemento estructural.

**Ejemplos:**
- Muro perimetral
- Pavimentación de opus signinum
- Umbral de piedra
- Escalinata
- Basa de columna

---

## Pestaña Datos Descriptivos

La primera pestaña contiene los campos textuales para la descripción detallada.

### Descripción

**Campo**: `textEdit_descrizione_struttura`
**Base de datos**: `descrizione`

Campo de texto libre para la descripción física de la estructura.

**Contenidos recomendados:**
- Técnica constructiva
- Materiales utilizados
- Estado de conservación
- Dimensiones generales
- Orientación
- Características peculiares

**Ejemplo:**
```
Muro de opus incertum realizado con bloques de caliza local
de dimensiones variables (15-30 cm). Aglutinante de mortero de cal
de color blanquecino. Conservado hasta una altura máxima de 1,20 m.
Anchura media 50 cm. Orientación NE-SW. Presenta restos
de enlucido en la cara interior.
```

### Interpretación

**Campo**: `textEdit_interpretazione_struttura`
**Base de datos**: `interpretazione`

Interpretación funcional e histórica de la estructura.

**Contenidos recomendados:**
- Función original hipotética
- Fases de uso/reutilización
- Paralelos tipológicos
- Encuadramiento cronológico
- Relaciones con otras estructuras

---

## Pestaña Periodización

Esta pestaña gestiona el encuadramiento cronológico de la estructura.

### Periodo y Fase Inicial

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Periodo Inicial | `periodo_iniziale` | Periodo de construcción/inicio de uso |
| Fase Inicial | `fase_iniziale` | Fase dentro del periodo |

Los valores se rellenan automáticamente según los periodos definidos en la Ficha de Periodización para el sitio seleccionado.

### Periodo y Fase Final

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Periodo Final | `periodo_finale` | Periodo de abandono/amortización |
| Fase Final | `fase_finale` | Fase dentro del periodo |

### Datación Extendida

**Campo**: `comboBox_datazione_estesa`
**Base de datos**: `datazione_estesa`

Datación literal calculada automáticamente o insertada manualmente.

**Formatos:**
- "Siglo I a.C. - Siglo II d.C."
- "100 a.C. - 200 d.C."
- "Época romana imperial"

---

## Pestaña Relaciones

Esta pestaña gestiona las relaciones entre estructuras.

### Tabla de Relaciones de Estructura

**Widget**: `tableWidget_rapporti`
**Base de datos**: `rapporti_struttura`

Registra las relaciones entre la estructura actual y otras estructuras.

**Columnas:**
| Columna | Descripción |
|---------|-------------|
| Tipo de relación | Relación estratigráfica/funcional |
| Sitio | Sitio de la estructura relacionada |
| Sigla | Sigla de la estructura relacionada |
| Número | Número de la estructura relacionada |

**Tipos de relación:**

| Relación | Inversa | Descripción |
|----------|---------|-------------|
| Se une a | Se une a | Conexión física contemporánea |
| Cubre | Cubierta por | Relación de superposición |
| Corta | Cortada por | Relación de corte |
| Rellena | Rellenada por | Relación de relleno |
| Se apoya en | Le apoya | Relación de apoyo |
| Igual a | Igual a | Misma estructura con nombre diferente |

### Gestión de Filas

| Botón | Función |
|-------|---------|
| + | Añadir nueva fila |
| - | Eliminar fila seleccionada |

---

## Pestaña Elementos Constructivos

Esta pestaña documenta los materiales y elementos que componen la estructura.

### Materiales Empleados

**Widget**: `tableWidget_materiali_impiegati`
**Base de datos**: `materiali_impiegati`

Lista de los materiales utilizados en la construcción.

**Ejemplos de materiales:**
- Bloques de caliza
- Ladrillos
- Mortero de cal
- Cantos de río
- Tejas
- Mármol
- Tufo

### Elementos Estructurales

**Widget**: `tableWidget_elementi_strutturali`
**Base de datos**: `elementi_strutturali`

Lista de los elementos constructivos con cantidad.

**Columnas:**
| Columna | Descripción |
|---------|-------------|
| Tipología del elemento | Tipo de elemento |
| Cantidad | Número de elementos |

---

## Pestaña Medidas

Esta pestaña registra las dimensiones de la estructura.

### Tabla de Mediciones

**Widget**: `tableWidget_misurazioni`
**Base de datos**: `misure_struttura`

**Columnas:**
| Columna | Descripción |
|---------|-------------|
| Tipo de medida | Tipo de dimensión |
| Unidad de medida | m, cm, m², etc. |
| Valor | Valor numérico |

### Tipos de Medida Comunes

| Tipo | Descripción |
|------|-------------|
| Longitud | Dimensión mayor |
| Anchura | Dimensión menor |
| Altura conservada | Alzado conservado |
| Altura original | Alzado estimado original |
| Profundidad | Para estructuras excavadas |
| Diámetro | Para estructuras circulares |
| Espesor | Para muros, pavimentos |
| Superficie | Área en m² |

---

## Pestaña Media

Gestión de imágenes, videos y modelos 3D asociados a la estructura.

### Funcionalidades

**Widget**: `iconListWidget`

Visualiza las miniaturas de los medios asociados.

### Drag & Drop

Es posible arrastrar archivos directamente sobre la ficha:

**Formatos soportados:**
- Imágenes: JPG, JPEG, PNG, TIFF, TIF, BMP
- Video: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Visualización

- **Doble clic** en miniatura: abre el visualizador
- Para videos: abre el reproductor de video integrado
- Para 3D: abre el visualizador 3D PyVista

---

## Pestaña Mapa

Vista previa de la posición de la estructura en el mapa.

### Funcionalidades

- Visualiza la geometría de la estructura
- Zoom automático al elemento
- Integración con las capas SIG del proyecto

---

## Integración SIG

### Visualización en Mapa

| Botón | Función |
|-------|---------|
| Map Preview | Toggle vista previa en la pestaña Mapa |
| Draw Structure | Resalta la estructura en el mapa QGIS |
| Load to GIS | Carga capa de estructuras |
| Load All | Carga todas las estructuras del sitio |

### Capa SIG

La ficha utiliza la capa **pyarchinit_strutture** para la visualización:
- Geometría: polígono o multipolígono
- Atributos vinculados a los campos de la ficha

---

## Exportación e Impresión

### Export PDF

El botón PDF abre un panel con opciones de exportación:

| Opción | Descripción |
|--------|-------------|
| Lista de Estructuras | Lista sintética de las estructuras |
| Fichas de Estructuras | Fichas completas detalladas |
| Imprimir | Genera el PDF |
| Convertir a Word | Convierte PDF a formato Word |

---

## Workflow Operativo

### Creación de Nueva Estructura

1. **Apertura de la ficha**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en el botón "New Record"
   - Los campos identificativos se vuelven editables

3. **Datos identificativos**
   ```
   Sitio: Villa Romana de las Musas
   Sigla: MR
   Número: 15
   ```

4. **Clasificación**
   ```
   Categoría: Residencial
   Tipología: Muro perimetral
   Definición: Muro de opus incertum
   ```

5. **Datos descriptivos** (Pestaña 1)
   ```
   Descripción: Muro realizado en opus incertum con
   bloques de caliza local...

   Interpretación: Límite norte de la domus, fase I
   del complejo residencial...
   ```

6. **Periodización** (Pestaña 2)
   ```
   Periodo inicial: I - Fase: A
   Periodo final: II - Fase: B
   Datación: Siglo I a.C. - Siglo II d.C.
   ```

7. **Relaciones** (Pestaña 3)
   ```
   Se une a: MR 16, MR 17
   Cortada por: ST 5
   ```

8. **Guardado**
    - Clic en "Save"
    - Verificar confirmación de guardado

---

## Buenas Prácticas

### Nomenclatura

- Usar siglas coherentes en todo el proyecto
- Documentar las convenciones usadas
- Evitar duplicaciones de numeración

### Descripción

- Ser sistemáticos en la descripción
- Seguir un esquema: técnica > materiales > dimensiones > estado
- Separar descripción objetiva de interpretación

### Periodización

- Vincular siempre a periodos definidos en la Ficha de Periodización
- Indicar tanto fase inicial como final
- Usar la datación extendida para síntesis

### Media

- Asociar fotos representativas
- Incluir fotos de detalle constructivo
- Documentar las fases de excavación

---

## Resolución de Problemas

### Problema: Estructura no visible en el mapa

**Causa**: Geometría no asociada o capa no cargada.

**Solución**:
1. Verificar que exista la capa `pyarchinit_strutture`
2. Comprobar que la estructura tenga una geometría asociada
3. Verificar el sistema de referencia

### Problema: Periodos no disponibles

**Causa**: Periodos no definidos para el sitio.

**Solución**:
1. Abrir la Ficha de Periodización
2. Definir los periodos para el sitio actual
3. Volver a la Ficha de Estructura

### Problema: Error de guardado "registro existente"

**Causa**: La combinación Sitio + Sigla + Número ya existe.

**Solución**:
1. Verificar la numeración existente
2. Usar un número progresivo libre
3. Comprobar que no haya duplicados

---

## Relaciones con Otras Fichas

| Ficha | Relación |
|-------|----------|
| **Ficha de Sitio** | El sitio contiene las estructuras |
| **Ficha UE** | Las UE componen las estructuras |
| **Ficha de Periodización** | Proporciona la cronología |
| **Ficha de Inventario de Materiales** | Materiales asociados a las estructuras |
| **Ficha de Tumba** | Tumbas como tipo especial de estructura |

---

## Referencias

### Base de Datos

- **Tabla**: `struttura_table`
- **Clase mapper**: `STRUTTURA`
- **ID**: `id_struttura`

### Archivos Fuente

- **UI**: `gui/ui/Struttura.ui`
- **Controlador**: `tabs/Struttura.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
