# Tutorial 22: Media Manager

## Introducción

El **Media Manager** es la herramienta central de PyArchInit para la gestión de las imágenes y de los contenidos multimedia asociados a los registros arqueológicos. Permite conectar fotos, dibujos, videos y otros media a UE, hallazgos, tumbas, estructuras y otras entidades.

### Funcionalidades Principales

- Gestión centralizada de todos los media
- Conexión a entidades arqueológicas (UE, Hallazgos, Pottery, Tumbas, Estructuras, UT)
- Visualización de thumbnails e imágenes a tamaño original
- Etiquetado y categorización
- Búsqueda avanzada
- Integración con GPT para análisis de imágenes

## Acceso

### Desde el Menú
**PyArchInit** → **Media Manager**

### Desde la Toolbar
Icono **Media Manager** en la toolbar PyArchInit

## Interfaz

### Panel Principal

```
+----------------------------------------------------------+
|                    Media Manager                          |
+----------------------------------------------------------+
| Sitio: [ComboBox]  Área: [ComboBox]  UE: [ComboBox]      |
+----------------------------------------------------------+
| [Cuadrícula Thumbnail de Imágenes]                        |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Tags: [Lista de tags asociados]                           |
+----------------------------------------------------------+
| [Navegación] << < Registro X de Y > >>                    |
+----------------------------------------------------------+
```

### Filtros de Búsqueda

| Campo | Descripción |
|-------|-------------|
| Sitio | Filtra por sitio arqueológico |
| Área | Filtra por área de excavación |
| UE | Filtra por Unidad Estratigráfica |
| Sigla Estructura | Filtra por sigla de estructura |
| Nr. Estructura | Filtra por número de estructura |

### Controles de Thumbnail

| Control | Función |
|---------|---------|
| Slider de tamaño | Ajusta el tamaño del thumbnail |
| Doble clic | Abre imagen a tamaño original |
| Selección múltiple | Ctrl+clic para seleccionar varias imágenes |

## Gestión de Media

### Añadir Nuevas Imágenes

1. Abrir Media Manager
2. Seleccionar el sitio de destino
3. Hacer clic en **"Nuevo Registro"** o usar el menú contextual
4. Seleccionar las imágenes a añadir
5. Completar los metadatos

### Conectar Media a Entidades

1. Seleccionar la imagen en la cuadrícula
2. En el panel Tags, seleccionar:
   - **Tipo de entidad**: UE, Hallazgo, Pottery, Tumba, Estructura, UT
   - **Identificativo**: Número/código de la entidad
3. Hacer clic en **"Conectar"**

### Tipos de Entidades Soportadas

| Tipo | Tabla BD | Descripción |
|------|----------|-------------|
| US | us_table | Unidades Estratigráficas |
| REPERTO | inventario_materiali_table | Hallazgos/Materiales |
| CERAMICA | pottery_table | Cerámica |
| TOMBA | tomba_table | Sepulturas |
| STRUTTURA | struttura_table | Estructuras |
| UT | ut_table | Unidades Topográficas |

### Visualizar Imagen Original

- **Doble clic** en thumbnail
- Se abre viewer con:
  - Zoom (rueda del ratón)
  - Pan (arrastre)
  - Rotación
  - Medición

## Funcionalidades Avanzadas

### Búsqueda Avanzada

El Media Manager soporta búsqueda por:
- Nombre de archivo
- Fecha de inserción
- Entidad conectada
- Tag/categorías

### Integración GPT

Botón **"GPT Sketch"** para:
- Análisis automático de la imagen
- Generación de descripción
- Sugerencias de clasificación

### Carga Remota

Soporte para imágenes en servidores remotos:
- URLs directas
- Servidor FTP
- Almacenamiento en la nube

## Base de Datos

### Tablas Implicadas

| Tabla | Descripción |
|-------|-------------|
| `media_table` | Metadatos media |
| `media_thumb_table` | Thumbnails |
| `media_to_entity_table` | Conexiones a entidades |

### Mapper Classes

- `MEDIA` - Entidad media principal
- `MEDIA_THUMB` - Thumbnail
- `MEDIATOENTITY` - Relación media-entidad

## Buenas Prácticas

### 1. Organización de Archivos

- Usar nombres de archivo descriptivos
- Organizar por sitio/área/año
- Mantener backup de originales

### 2. Metadatos

- Completar siempre sitio y área
- Añadir descripciones significativas
- Usar tags consistentes

### 3. Calidad de Imágenes

- Resolución mínima recomendada: 1920x1080
- Formato: JPG para fotos, PNG para dibujos
- Compresión moderada

### 4. Conexiones

- Conectar cada imagen a las entidades pertinentes
- Verificar conexiones después de importación masiva
- Usar la búsqueda para imágenes no conectadas

## Resolución de Problemas

### Thumbnails No Visualizados

**Causas**:
- Ruta de imagen incorrecta
- Archivo faltante
- Problemas de permisos

**Soluciones**:
- Verificar ruta en base de datos
- Controlar existencia del archivo
- Verificar permisos de carpeta

### Imagen No Conectable

**Causas**:
- Entidad no existente
- Tipo de entidad incorrecto

**Soluciones**:
- Verificar existencia del registro
- Controlar tipo de entidad seleccionado

## Referencias

### Archivos Fuente
- `tabs/Image_viewer.py` - Interfaz principal
- `modules/utility/pyarchinit_media_utility.py` - Utility media

### Base de Datos
- `media_table` - Datos media
- `media_to_entity_table` - Conexiones

---

## Video Tutorial

### Media Manager Completo
`[Placeholder: video_media_manager.mp4]`

**Contenidos**:
- Añadir imágenes
- Conexión a entidades
- Búsqueda y filtros
- Funcionalidades avanzadas

**Duración prevista**: 15-18 minutos

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../animations/pyarchinit_media_manager_animation.html)
