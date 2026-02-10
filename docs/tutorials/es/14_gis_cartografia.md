# Tutorial 14: SIG y Cartografía

## Introducción

PyArchInit está profundamente integrado con **QGIS**, aprovechando todas sus funcionalidades SIG para la gestión espacial de los datos arqueológicos. Este tutorial cubre la integración cartográfica, las capas predefinidas y las funcionalidades avanzadas como la **segmentación automática SAM**.

### Funcionalidades SIG Principales

- Visualización de UE en mapa
- Capas vectoriales predefinidas
- Estilos QML personalizados
- Cotas y mediciones SIG
- Segmentación automática (SAM)
- Exportación cartográfica

## Capas Predefinidas de PyArchInit

### Capas Vectoriales Principales

| Capa | Geometría | Descripción |
|------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | UE de depósito |
| `pyunitastratigrafiche_usm` | MultiPolygon | UE murarias |
| `pyarchinit_quote` | Point | Puntos de cota |
| `pyarchinit_siti` | Point | Localización de sitios |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Áreas de excavación |
| `pyarchinit_strutture_ipotesi` | Polygon | Estructuras hipotéticas |
| `pyarchinit_documentazione` | Point | Referencias de documentación |

### Atributos de Capa UE

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `gid` | Integer | ID único |
| `scavo_s` | Text | Nombre del sitio |
| `area_s` | Text | Número de área |
| `us_s` | Text | Número de UE |
| `stratigraph_index_us` | Integer | Índice estratigráfico |
| `tipo_us_s` | Text | Tipo de UE |
| `rilievo_originale` | Text | Levantamiento de origen |
| `disegnatore` | Text | Autor del levantamiento |
| `data` | Date | Fecha del levantamiento |

## Visualización de UE en Mapa

### Desde la Pestaña "Map" en la Ficha de UE

1. Abrir una ficha de UE
2. Seleccionar la pestaña **Map**
3. Funciones disponibles:

| Botón | Función |
|-------|---------|
| View US | Visualiza UE actual en mapa |
| View All | Visualiza todas las UE del área |
| New Record | Crear nueva geometría |
| Pan to | Centrar mapa en UE |

### Visualización desde Búsqueda

1. Ejecutar una búsqueda de UE
2. Botón **"View Record"** → visualiza individual
3. Botón **"View All"** → visualiza todos los resultados

## Estilos de las Capas

### Archivos QML

PyArchInit incluye estilos predefinidos en formato QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicación del Estilo

1. Seleccionar la capa en la leyenda
2. Clic derecho → **Propiedades**
3. Pestaña **Estilo**
4. **Cargar estilo** → seleccionar QML

### Personalización

Los estilos pueden personalizarse para:
- Colores según tipo de UE
- Etiquetas con número de UE
- Transparencia
- Bordes y rellenos

## Cotas y Mediciones

### Capa de Cotas

La capa `pyarchinit_quote` almacena:
- Coordenadas X, Y
- Cota Z (absoluta)
- Tipo de punto de cota
- UE de referencia
- Área de referencia

### Cálculo Automático de Cotas

Desde la Ficha de UE, las cotas mín/máx se calculan:
1. Query a los puntos de cota asociados a la UE
2. Extracción del valor mínimo y máximo
3. Visualización en el informe

### Inserción de Cotas

1. Capa de cotas en edición
2. Dibujar punto en el mapa
3. Completar atributos:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentación Automática SAM

### ¿Qué es SAM?

**SAM (Segment Anything Model)** es un modelo de inteligencia artificial desarrollado por Meta para la segmentación automática de imágenes. PyArchInit lo integra para:
- Digitalización automática de piedras/elementos
- Segmentación de ortofotos
- Aceleración del levantamiento

### Acceso a la Función

1. **PyArchInit** → **SAM Segmentation**
2. O desde la barra de herramientas: icono **SAM**

### Interfaz SAM

```
+--------------------------------------------------+
|        SAM Stone Segmentation                     |
+--------------------------------------------------+
| Input:                                            |
|   Raster Layer: [ComboBox ortofoto]              |
+--------------------------------------------------+
| Target Layer:                                     |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Default Attributes:                               |
|   Site (sito): [campo automático]                |
|   Area: [input área]                             |
|   Stratigraphic Index: [1-10]                    |
|   Type US: [piedra|capa|acumulación|corte]       |
+--------------------------------------------------+
| Segmentation Mode:                                |
|   [o] Automatic (detectar todas las piedras)     |
|   [ ] Click mode (clic en cada piedra)           |
|   [ ] Box mode (dibujar rectángulo)              |
|   [ ] Polygon mode (dibujar a mano alzada)       |
|   [ ] From layer (usar polígono existente)       |
+--------------------------------------------------+
| Model:                                            |
|   [ComboBox modelo]                              |
|   API Key: [******]                              |
+--------------------------------------------------+
|        [Start Segmentation]  [Cancel]             |
+--------------------------------------------------+
```

### Modos de Segmentación

#### 1. Automatic Mode
- Segmenta automáticamente todos los objetos visibles
- Ideal para áreas con muchas piedras
- Requiere ortofoto de buena calidad

#### 2. Click Mode
- Clic en cada objeto a segmentar
- Clic derecho o Enter para terminar
- Escape para cancelar
- Más preciso para objetos específicos

#### 3. Box Mode
- Dibujar rectángulo sobre el área
- Segmenta solo el área seleccionada
- Útil para zonas delimitadas

#### 4. Polygon Mode
- Dibujar polígono libre
- Clic para añadir vértices
- Clic derecho para completar
- Para áreas irregulares

#### 5. From Layer Mode
- Usa polígono existente como máscara
- Seleccionar capa poligonal
- Segmenta solo dentro del polígono

### Modelos Disponibles

| Modelo | Tipo | Requisitos | Calidad |
|--------|------|------------|---------|
| Replicate SAM-2 | Cloud API | API Key | Óptima |
| Roboflow SAM-3 | Cloud API | API Key | Óptima + Text Prompt |
| SAM vit_b | Local | 375MB VRAM | Buena |
| SAM vit_l | Local | 1.2GB VRAM | Muy buena |
| SAM vit_h | Local | 2.5GB VRAM | Excelente |
| OpenCV | Local | Ninguno | Básica |

### SAM-3 con Text Prompt

La versión SAM-3 (Roboflow) soporta **prompts textuales**:
- "stones" - piedras
- "pottery fragments" - fragmentos cerámicos
- "bones" - huesos
- Cualquier descripción textual

### Configuración de API

#### Replicate API (SAM-2)
1. Registrarse en [replicate.com](https://replicate.com)
2. Obtener API key
3. Introducir en la configuración

#### Roboflow API (SAM-3)
1. Registrarse en [roboflow.com](https://roboflow.com)
2. Obtener API key
3. Introducir en la configuración

### Instalación Local de SAM

Para uso local sin API:
```bash
# Crear entorno virtual
cd ~/pyarchinit/bin
python -m venv sam_venv

# Activar entorno
source sam_venv/bin/activate

# Instalar dependencias
pip install segment-anything torch torchvision

# Descargar modelos (opcional)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### Workflow SAM

1. **Preparación**
   - Cargar ortofoto como capa raster
   - Verificar sistema de referencia
   - Preparar capa de destino

2. **Configuración**
   - Seleccionar raster de entrada
   - Configurar atributos por defecto
   - Elegir modo y modelo

3. **Ejecución**
   - Clic en "Start Segmentation"
   - Esperar el procesamiento
   - Verificar resultados

4. **Post-procesamiento**
   - Comprobar polígonos generados
   - Asignar números de UE
   - Corregir posibles errores

## Integración Cartográfica

### Exportar Datos SIG

Desde la Ficha de UE, pestaña Map:
- **Export GeoPackage**: Capa como GPKG
- **Export Shapefile**: Capa como SHP
- **Export GeoJSON**: Capa como JSON

### Importar Datos SIG

Importar geometrías existentes:
1. Cargar capa en QGIS
2. Seleccionar feature
3. Usar función de importación

### Geoprocesamiento

Operaciones espaciales disponibles:
- Buffer
- Intersección
- Unión
- Diferencia
- Centroides

## Buenas Prácticas

### 1. Ortofotos

- Resolución mínima: 1-2 cm/pixel
- Formato: GeoTIFF georreferenciado
- Sistema de referencia: coherente con el proyecto

### 2. Digitalización

- Usar snap para precisión
- Verificar topología
- Mantener consistencia de atributos

### 3. Segmentación SAM

- Ortofoto de alta calidad
- Iluminación uniforme
- Contraste adecuado objetos/fondo
- Post-verificación siempre necesaria

### 4. Organización de Capas

- Agrupar por tipología
- Usar estilos consistentes
- Mantener orden en la leyenda

## Resolución de Problemas

### Capas No Visualizadas

**Posibles causas**:
- Extensión errónea
- Sistema de referencia diferente
- Filtro activo

**Soluciones**:
- Zoom to Layer
- Verificar CRS
- Eliminar filtros

### SAM No Funciona

**Posibles causas**:
- API key no válida
- Raster no georreferenciado
- Modelo local no instalado

**Soluciones**:
- Verificar API key
- Comprobar georreferenciación
- Instalar modelo

### Geometrías Corruptas

**Posibles causas**:
- Errores de digitalización
- Importación problemática

**Soluciones**:
- Usar "Fix Geometries"
- Redibujar elemento

## Referencias

### Archivos Fuente
- `modules/gis/pyarchinit_pyqgis.py` - Integración SIG
- `tabs/Sam_Segmentation_Dialog.py` - Diálogo SAM
- `modules/gis/sam_map_tools.py` - Herramientas de mapa SAM

### Capas
- `pyunitastratigrafiche` - UE de depósito
- `pyunitastratigrafiche_usm` - UE murarias
- `pyarchinit_quote` - Cotas

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/pyarchinit_image_classification_animation.html)
