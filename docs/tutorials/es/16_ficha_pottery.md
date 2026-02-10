# Tutorial 16: Ficha Pottery (Cerámica Especializada)

## Índice
1. [Introducción](#introducción)
2. [Acceso a la Ficha](#acceso-a-la-ficha)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Campos Principales](#campos-principales)
5. [Pestañas de la Ficha](#pestañas-de-la-ficha)
6. [Pottery Tools](#pottery-tools)
7. [Búsqueda por Similaridad Visual](#búsqueda-por-similaridad-visual)
8. [Cuantificaciones](#cuantificaciones)
9. [Gestión de Media](#gestión-de-media)
10. [Export y Reportes](#export-y-reportes)
11. [Workflow Operativo](#workflow-operativo)
12. [Buenas Prácticas](#buenas-prácticas)
13. [Resolución de Problemas](#resolución-de-problemas)

---

## Introducción

La **Ficha Pottery** es una herramienta especializada para la catalogación detallada de la cerámica arqueológica. A diferencia de la ficha Inventario de Materiales (más generalista), esta ficha está diseñada específicamente para el análisis ceramológico profundo, con campos dedicados a fabric, ware, decoraciones y medidas específicas de los vasos.

### Diferencias con la Ficha Inventario de Materiales

| Aspecto | Inventario Materiales | Pottery |
|---------|---------------------|---------|
| **Objetivo** | Todos los tipos de hallazgos | Solo cerámica |
| **Detalle** | General | Especializado |
| **Campos fabric** | Cuerpo cerámico (genérico) | Fabric detallado |
| **Decoraciones** | Campo único | Interna/Externa separadas |
| **Medidas** | Genéricas | Específicas para vasos |
| **AI Tools** | SketchGPT | PotteryInk, YOLO, Similarity Search |

### Funcionalidades Avanzadas

La ficha Pottery incluye funcionalidades AI de vanguardia:
- **PotteryInk**: Generación automática de dibujos arqueológicos desde foto
- **YOLO Detection**: Reconocimiento automático de formas cerámicas
- **Visual Similarity Search**: Búsqueda de cerámicas similares mediante embedding visuales
- **Layout Generator**: Generación automática de láminas cerámicas

![Panorámica Ficha Pottery](images/16_scheda_pottery/01_panoramica.png)
*Figura 1: Vista general de la Ficha Pottery*

---

## Acceso a la Ficha

### Desde Menú

1. Abrir QGIS con el plugin PyArchInit activo
2. Menú **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery**

![Menú Pottery](images/16_scheda_pottery/02_menu_accesso.png)
*Figura 2: Acceso a la ficha desde el menú*

### Desde Toolbar

1. Localizar la toolbar PyArchInit
2. Hacer clic en el icono **Pottery** (icono vaso/ánfora cerámica)

![Toolbar Pottery](images/16_scheda_pottery/03_toolbar_accesso.png)
*Figura 3: Icono en la toolbar*

---

## Interfaz de Usuario

La interfaz está organizada de forma eficiente para la catalogación ceramológica:

![Interfaz Completa](images/16_scheda_pottery/04_interfaccia_completa.png)
*Figura 4: Layout completo de la interfaz*

### Áreas Principales

| Área | Descripción |
|------|-------------|
| **1. Header** | DBMS Toolbar, indicadores de estado, filtros |
| **2. Identificación** | Sitio, Área, UE, ID Number, Box, Bag |
| **3. Clasificación** | Form, Ware, Fabric, Material |
| **4. Tab Detalle** | Description, Technical Data, Supplements |
| **5. Media Panel** | Viewer de imágenes, vista previa |

### Pestañas Disponibles

| Pestaña | Contenido |
|---------|-----------|
| **Description data** | Descripción, decoraciones, notas |
| **Technical Data** | Medidas, tratamiento superficie, Munsell |
| **Supplements** | Bibliografía, Estadísticas |

---

## Campos Principales

### Campos Identificativos

#### ID Number
- **Tipo**: Integer
- **Obligatorio**: Sí
- **Descripción**: Número identificativo único del fragmento cerámico
- **Restricción**: Único por sitio

#### Sitio
- **Tipo**: ComboBox
- **Obligatorio**: Sí
- **Descripción**: Sitio arqueológico de procedencia

#### Área
- **Tipo**: ComboBox editable
- **Descripción**: Área de excavación

#### UE (Unidad Estratigráfica)
- **Tipo**: Integer
- **Descripción**: Número de la UE de hallazgo

#### Sector
- **Tipo**: Text
- **Descripción**: Sector específico de hallazgo

![Campos Identificativos](images/16_scheda_pottery/05_campi_identificativi.png)
*Figura 5: Campos identificativos*

### Campos de Depósito

#### Box
- **Tipo**: Integer
- **Descripción**: Número de la caja de depósito

#### Bag
- **Tipo**: Integer
- **Descripción**: Número de la bolsa

#### Year (Año)
- **Tipo**: Integer
- **Descripción**: Año de hallazgo/catalogación

### Campos de Clasificación Cerámica

#### Form (Forma)
- **Tipo**: ComboBox editable
- **Obligatorio**: Recomendado
- **Valores típicos**: Bowl, Jar, Jug, Plate, Cup, Amphora, Lid, etc.
- **Descripción**: Forma general del vaso

![Campo Form](images/16_scheda_pottery/06_campo_form.png)
*Figura 6: Selección de forma*

#### Specific Form (Forma Específica)
- **Tipo**: ComboBox editable
- **Descripción**: Tipología específica (ej. Hayes 50, Dressel 1)

#### Specific Shape
- **Tipo**: Text
- **Descripción**: Variante morfológica detallada

#### Ware
- **Tipo**: ComboBox editable
- **Descripción**: Clase cerámica
- **Ejemplos**:
  - African Red Slip
  - Italian Sigillata
  - Thin Walled Ware
  - Coarse Ware
  - Amphora
  - Cooking Ware

![Campo Ware](images/16_scheda_pottery/07_campo_ware.png)
*Figura 7: Selección de ware*

#### Material
- **Tipo**: ComboBox editable
- **Descripción**: Material base
- **Valores**: Ceramic, Terracotta, Porcelain, etc.

#### Fabric
- **Tipo**: ComboBox editable
- **Descripción**: Tipo de pasta cerámica
- **Características a considerar**:
  - Color de la pasta
  - Granulometría de inclusiones
  - Dureza
  - Porosidad

![Campo Fabric](images/16_scheda_pottery/08_campo_fabric.png)
*Figura 8: Selección de fabric*

### Campos de Conservación

#### Percent
- **Tipo**: ComboBox editable
- **Descripción**: Porcentaje conservado del vaso
- **Valores típicos**: <10%, 10-25%, 25-50%, 50-75%, >75%, Complete

#### QTY (Quantity)
- **Tipo**: Integer
- **Descripción**: Número de fragmentos

### Campos de Documentación

#### Photo
- **Tipo**: Text
- **Descripción**: Referencia fotográfica

#### Drawing
- **Tipo**: Text
- **Descripción**: Referencia de dibujo

---

## Pestañas de la Ficha

### Pestaña 1: Description Data

Pestaña principal para la descripción del fragmento.

![Tab Description](images/16_scheda_pottery/09_tab_description.png)
*Figura 9: Pestaña Description Data*

#### Decoraciones

| Campo | Descripción |
|-------|-------------|
| **External Decoration** | Tipo de decoración externa |
| **Internal Decoration** | Tipo de decoración interna |
| **Description External Deco** | Descripción detallada decoración externa |
| **Description Internal Deco** | Descripción detallada decoración interna |
| **Decoration Type** | Tipología decorativa (Painted, Incised, Applique, etc.) |
| **Decoration Motif** | Motivo decorativo (Geometric, Vegetal, Figurative) |
| **Decoration Position** | Posición de la decoración (Rim, Body, Base, Handle) |

#### Wheel Made
- **Tipo**: ComboBox
- **Valores**: Yes, No, Unknown
- **Descripción**: Indica si el vaso fue producido a torno

#### Note
- **Tipo**: TextEdit multilínea
- **Descripción**: Notas adicionales y observaciones

#### Media Viewer
Área para visualizar las imágenes asociadas:
- Drag & drop para asociar imágenes
- Doble clic para abrir viewer completo
- Botones para gestión de tags

### Pestaña 2: Technical Data

Datos técnicos y mediciones.

![Tab Technical](images/16_scheda_pottery/10_tab_technical.png)
*Figura 10: Pestaña Technical Data*

#### Munsell Color
- **Tipo**: ComboBox editable
- **Descripción**: Código de color Munsell de la pasta
- **Formato**: ej. "10YR 7/4", "5YR 6/6"
- **Notas**: Referirse a la Munsell Soil Color Chart

![Campo Munsell](images/16_scheda_pottery/11_campo_munsell.png)
*Figura 11: Selección de color Munsell*

#### Surface Treatment
- **Tipo**: ComboBox editable
- **Descripción**: Tratamiento superficial
- **Valores típicos**:
  - Slip (engobe)
  - Burnished (bruñido)
  - Glazed (vidriado)
  - Painted (pintado)
  - Plain (simple)

#### Medidas (en cm)

| Campo | Descripción |
|-------|-------------|
| **Diameter Max** | Diámetro máximo del vaso |
| **Diameter Rim** | Diámetro del borde |
| **Diameter Bottom** | Diámetro del fondo |
| **Total Height** | Altura total (si es reconstruible) |
| **Preserved Height** | Altura conservada |

![Campos Medidas](images/16_scheda_pottery/12_campi_misure.png)
*Figura 12: Campos de medidas*

#### Datación
- **Tipo**: ComboBox editable
- **Descripción**: Encuadramiento cronológico
- **Formato**: Textual (ej. "siglos I-II d.C.")

### Pestaña 3: Supplements

Pestaña con subsecciones para datos suplementarios.

![Tab Supplements](images/16_scheda_pottery/13_tab_supplements.png)
*Figura 13: Pestaña Supplements*

#### Sub-Tab: Bibliography
Gestión de referencias bibliográficas para comparaciones tipológicas.

| Columna | Descripción |
|---------|-------------|
| Author | Autor/es |
| Year | Año de publicación |
| Title | Título abreviado |
| Page | Página de referencia |
| Figure | Figura/Lámina |

#### Sub-Tab: Statistic
Acceso a las funcionalidades de cuantificación y gráficos estadísticos.

---

## Pottery Tools

La ficha Pottery incluye un potente conjunto de herramientas AI para el procesamiento de imágenes cerámicas.

### Acceso a Pottery Tools

1. Menú **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery Tools**

O desde el botón dedicado en la ficha Pottery.

![Pottery Tools](images/16_scheda_pottery/14_pottery_tools.png)
*Figura 14: Interfaz Pottery Tools*

### PotteryInk - Generación de Dibujos

Transforma automáticamente las fotos de cerámica en dibujos arqueológicos estilizados.

![PotteryInk](images/16_scheda_pottery/15_potteryink.png)
*Figura 15: PotteryInk en acción*

#### Uso

1. Seleccionar una imagen de cerámica
2. Hacer clic en "Generate Drawing"
3. El sistema procesa la imagen con AI
4. El dibujo se genera en estilo arqueológico

#### Requisitos
- Virtual environment dedicado (creado automáticamente)
- Modelos AI pre-entrenados
- GPU recomendada para rendimiento óptimo

### YOLO Pottery Detection

Reconocimiento automático de las formas cerámicas en las imágenes.

![YOLO Detection](images/16_scheda_pottery/16_yolo_detection.png)
*Figura 16: YOLO Detection*

#### Funcionalidades

- Identifica automáticamente la forma del vaso
- Sugiere clasificación
- Detecta partes anatómicas (borde, pared, fondo, asa)

### Layout Generator

Genera automáticamente láminas cerámicas para publicación.

![Layout Generator](images/16_scheda_pottery/17_layout_generator.png)
*Figura 17: Layout Generator*

#### Output

- Láminas en formato estándar arqueológico
- Escala métrica automática
- Disposición optimizada
- Export en PDF o imagen

### PDF Extractor

Extrae imágenes de cerámica de publicaciones PDF para comparaciones.

---

## Búsqueda por Similaridad Visual

Funcionalidad avanzada para encontrar cerámicas visualmente similares en la base de datos.

### Cómo Funciona

El sistema utiliza **embedding visuales** generados por modelos de deep learning para representar cada imagen cerámica como un vector numérico. La búsqueda encuentra las cerámicas con vectores más similares.

![Similarity Search](images/16_scheda_pottery/18_similarity_search.png)
*Figura 18: Búsqueda por similaridad visual*

### Uso

1. Seleccionar una imagen de referencia
2. Hacer clic en "Find Similar"
3. El sistema busca en la base de datos
4. Se muestran las cerámicas más similares ordenadas por similaridad

### Modelos Disponibles

- **ResNet50**: Buen equilibrio velocidad/precisión
- **EfficientNet**: Rendimiento óptimo
- **CLIP**: Búsqueda multimodal (texto + imagen)

### Actualización de Embedding

Los embedding se generan automáticamente cuando se añaden nuevas imágenes. Es posible forzar la actualización desde el menú Pottery Tools.

---

## Cuantificaciones

### Acceso

1. Hacer clic en el botón **Quant** en la toolbar
2. Seleccionar el parámetro de cuantificación
3. Visualizar el gráfico

![Panel Cuantificaciones](images/16_scheda_pottery/19_pannello_quant.png)
*Figura 19: Panel de cuantificaciones*

### Parámetros Disponibles

| Parámetro | Descripción |
|-----------|-------------|
| **Fabric** | Distribución por tipo de pasta |
| **US** | Distribución por unidad estratigráfica |
| **Area** | Distribución por área de excavación |
| **Material** | Distribución por material |
| **Percent** | Distribución por porcentaje conservado |
| **Shape/Form** | Distribución por forma |
| **Specific form** | Distribución por forma específica |
| **Ware** | Distribución por clase cerámica |
| **Munsell color** | Distribución por color |
| **Surface treatment** | Distribución por tratamiento superficial |
| **External decoration** | Distribución por decoración externa |
| **Internal decoration** | Distribución por decoración interna |
| **Wheel made** | Distribución torno sí/no |

### Export de Cuantificaciones

Los datos se exportan en:
- Archivo CSV en `pyarchinit_Quantificazioni_folder`
- Gráfico visualizado en pantalla

---

## Gestión de Media

### Asociación de Imágenes

![Gestión Media](images/16_scheda_pottery/20_gestione_media.png)
*Figura 20: Gestión de media*

#### Métodos

1. **Drag & Drop**: Arrastrar imágenes a la lista
2. **Botón All Images**: Carga todas las imágenes asociadas
3. **Search Images**: Busca imágenes específicas

### Video Player

Para cerámicas con documentación en video, está disponible un reproductor integrado.

### Integración Cloudinary

Soporte para imágenes remotas en Cloudinary:
- Carga automática de thumbnails
- Cache local para rendimiento
- Sincronización con la nube

---

## Export y Reportes

### Export PDF Ficha

![Export PDF](images/16_scheda_pottery/21_export_pdf.png)
*Figura 21: Export PDF*

Genera una ficha PDF completa con:
- Datos identificativos
- Clasificación
- Medidas
- Imágenes asociadas
- Notas

### Export Lista

Genera listado PDF de todos los registros visualizados.

### Export Datos

Botón para export en formato tabular (CSV/Excel).

---

## Workflow Operativo

### Catalogación de Nuevo Fragmento Cerámico

#### Paso 1: Apertura y Nuevo Registro
1. Abrir la Ficha Pottery
2. Hacer clic en **New record**

![Workflow Step 1](images/16_scheda_pottery/22_workflow_step1.png)
*Figura 22: Nuevo registro*

#### Paso 2: Datos Identificativos
1. Verificar/seleccionar **Sitio**
2. Introducir **ID Number** (progresivo)
3. Introducir **Area**, **US**, **Sector**
4. Introducir **Box** y **Bag**

![Workflow Step 2](images/16_scheda_pottery/23_workflow_step2.png)
*Figura 23: Datos identificativos*

#### Paso 3: Clasificación
1. Seleccionar **Form** (Bowl, Jar, etc.)
2. Seleccionar **Ware** (clase cerámica)
3. Seleccionar **Fabric** (tipo de pasta)
4. Indicar **Material** y **Percent**

![Workflow Step 3](images/16_scheda_pottery/24_workflow_step3.png)
*Figura 24: Clasificación*

#### Paso 4: Datos Técnicos
1. Abrir pestaña **Technical Data**
2. Introducir **Munsell color**
3. Seleccionar **Surface treatment**
4. Introducir las **medidas** (diámetros, alturas)
5. Indicar **Wheel made**

![Workflow Step 4](images/16_scheda_pottery/25_workflow_step4.png)
*Figura 25: Datos técnicos*

#### Paso 5: Decoraciones (si están presentes)
1. Volver a la pestaña **Description data**
2. Seleccionar tipo **External/Internal decoration**
3. Completar descripciones detalladas
4. Indicar **Decoration type**, **motif**, **position**

![Workflow Step 5](images/16_scheda_pottery/26_workflow_step5.png)
*Figura 26: Decoraciones*

#### Paso 6: Documentación
1. Asociar fotos (drag & drop)
2. Introducir referencia **Photo** y **Drawing**
3. Completar **Note** con observaciones

#### Paso 7: Datación y Comparaciones
1. Introducir **Datación**
2. Abrir pestaña **Supplements** → **Bibliography**
3. Añadir referencias bibliográficas

#### Paso 8: Guardado
1. Hacer clic en **Save**
2. Verificar confirmación

![Workflow Step 8](images/16_scheda_pottery/27_workflow_step8.png)
*Figura 27: Guardado*

---

## Buenas Prácticas

### Clasificación Coherente

- Utilizar vocabularios estandarizados para Form, Ware, Fabric
- Mantener coherencia en la nomenclatura
- Actualizar el tesauro cuando sea necesario

### Documentación Fotográfica

- Fotografiar cada fragmento con escala
- Incluir vista interna y externa
- Documentar detalles decorativos

### Mediciones

- Usar calibre para medidas precisas
- Indicar siempre la unidad de medida (cm)
- Para fragmentos, medir solo las partes conservadas

### Color Munsell

- Usar siempre la Munsell Soil Color Chart
- Medir sobre fractura fresca
- Indicar condiciones de luz

### Uso de AI Tools

- Verificar siempre los resultados automáticos
- PotteryInk funciona mejor con fotos de buena calidad
- La similarity search es útil para comparaciones, no sustitutiva del análisis

---

## Resolución de Problemas

### Problemas Comunes

#### ID Number duplicado
- **Error**: "Ya existe un registro con este ID"
- **Solución**: Verificar el siguiente número disponible

#### Pottery Tools no se inicia
- **Causa**: Virtual environment no configurado
- **Solución**:
  1. Verificar conexión a internet
  2. Esperar configuración automática
  3. Controlar log en `pyarchinit/bin/pottery_venv`

#### PotteryInk lento
- **Causa**: Procesamiento CPU en lugar de GPU
- **Solución**:
  1. Instalar drivers CUDA (NVIDIA)
  2. Verificar que PyTorch use GPU

#### Similarity Search vacío
- **Causa**: Embedding no generados
- **Solución**:
  1. Abrir Pottery Tools
  2. Hacer clic en "Update Embeddings"
  3. Esperar la finalización

#### Imágenes no cargadas
- **Causa**: Path incorrecto o Cloudinary no configurado
- **Solución**:
  1. Verificar configuración de path en Settings
  2. Para Cloudinary: verificar credenciales

---

## Video Tutorial

### Video 1: Panorámica Ficha Pottery
*Duración: 5-6 minutos*

[Placeholder para video]

### Video 2: Catalogación Cerámica Completa
*Duración: 8-10 minutos*

[Placeholder para video]

### Video 3: Pottery Tools y AI
*Duración: 10-12 minutos*

[Placeholder para video]

### Video 4: Búsqueda por Similaridad
*Duración: 5-6 minutos*

[Placeholder para video]

---

## Resumen de Campos de Base de Datos

| Campo | Tipo | Base de datos | Obligatorio |
|-------|------|---------------|-------------|
| ID Number | Integer | id_number | Sí |
| Sitio | Text | sito | Sí |
| Area | Text | area | No |
| US | Integer | us | No |
| Box | Integer | box | No |
| Bag | Integer | bag | No |
| Sector | Text | sector | No |
| Photo | Text | photo | No |
| Drawing | Text | drawing | No |
| Year | Integer | anno | No |
| Fabric | Text | fabric | No |
| Percent | Text | percent | No |
| Material | Text | material | No |
| Form | Text | form | No |
| Specific Form | Text | specific_form | No |
| Specific Shape | Text | specific_shape | No |
| Ware | Text | ware | No |
| Munsell Color | Text | munsell | No |
| Surface Treatment | Text | surf_trat | No |
| External Decoration | Text | exdeco | No |
| Internal Decoration | Text | intdeco | No |
| Wheel Made | Text | wheel_made | No |
| Descrip. External Deco | Text | descrip_ex_deco | No |
| Descrip. Internal Deco | Text | descrip_in_deco | No |
| Note | Text | note | No |
| Diameter Max | Numeric | diametro_max | No |
| QTY | Integer | qty | No |
| Diameter Rim | Numeric | diametro_rim | No |
| Diameter Bottom | Numeric | diametro_bottom | No |
| Total Height | Numeric | diametro_height | No |
| Preserved Height | Numeric | diametro_preserved | No |
| Decoration Type | Text | decoration_type | No |
| Decoration Motif | Text | decoration_motif | No |
| Decoration Position | Text | decoration_position | No |
| Datación | Text | datazione | No |

---

*Última actualización: Enero 2026*
*PyArchInit - Análisis de Cerámica Arqueológica*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../pyarchinit_pottery_tools_animation.html)
