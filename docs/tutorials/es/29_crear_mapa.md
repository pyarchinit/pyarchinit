# Tutorial 29: Make Your Map (Crear tu Mapa)

## Introducción

**Make Your Map** es la función de PyArchInit para generar mapas y layouts de impresión profesionales directamente desde la visualización actual de QGIS. Utiliza las plantillas de layout predefinidas para crear outputs cartográficos estandarizados.

### Funcionalidades

- Generación rápida de mapas desde la vista actual
- Plantillas predefinidas para diferentes formatos
- Personalización de encabezados y leyendas
- Export en PDF, PNG, SVG

## Acceso

### Desde la Toolbar
Icono **"Make your Map"** (impresora) en la toolbar PyArchInit

### Desde el Menú
**PyArchInit** → **Make your Map**

## Uso Básico

### Generación Rápida

1. Configurar la vista del mapa deseada en QGIS
2. Establecer zoom y extensión correctos
3. Hacer clic en **"Make your Map"**
4. Seleccionar la plantilla deseada
5. Introducir título e información
6. Generar mapa

## Plantillas Disponibles

### Formatos Estándar

| Plantilla | Formato | Orientación | Uso |
|-----------|---------|-------------|-----|
| A4 Portrait | A4 | Vertical | Documentación estándar |
| A4 Landscape | A4 | Horizontal | Vistas extensas |
| A3 Portrait | A3 | Vertical | Láminas detalladas |
| A3 Landscape | A3 | Horizontal | Planimetrías |

### Elementos de la Plantilla

Cada plantilla incluye:
- **Área del mapa** - Vista principal
- **Encabezado** - Título e información del proyecto
- **Escala** - Barra de escala gráfica
- **Norte** - Flecha del norte
- **Leyenda** - Símbolos de las capas
- **Cajetín** - Información técnica

## Personalización

### Información que se puede Introducir

| Campo | Descripción |
|-------|-------------|
| Título | Nombre del mapa |
| Subtítulo | Descripción adicional |
| Sitio | Nombre del sitio arqueológico |
| Área | Número de área |
| Fecha | Fecha de creación |
| Autor | Nombre del autor |
| Escala | Escala de representación |

### Estilo del Mapa

Antes de generar:
1. Configurar estilos de capas en QGIS
2. Activar/desactivar capas deseadas
3. Establecer etiquetas
4. Verificar leyenda

## Export

### Formatos Disponibles

| Formato | Uso | Calidad |
|---------|-----|---------|
| PDF | Impresión, archivo | Vectorial |
| PNG | Web, presentaciones | Raster |
| SVG | Edición, publicación | Vectorial |
| JPG | Web, vista previa | Raster comprimido |

### Resolución

| DPI | Uso |
|-----|-----|
| 96 | Pantalla/vista previa |
| 150 | Publicación web |
| 300 | Impresión estándar |
| 600 | Impresión alta calidad |

## Integración con Time Manager

### Generación de Secuencia

En combinación con Time Manager:
1. Configurar Time Manager
2. Para cada nivel estratigráfico:
   - Establecer nivel
   - Generar mapa
   - Guardar con nombre progresivo

### Output de Animación

Serie de mapas para:
- Presentaciones
- Video time-lapse
- Documentación progresiva

## Workflow Típico

### 1. Preparación

```
1. Cargar capas necesarias
2. Configurar estilos apropiados
3. Establecer sistema de referencia
4. Definir extensión del mapa
```

### 2. Configuración de la Vista

```
1. Hacer zoom sobre el área de interés
2. Activar/desactivar capas
3. Verificar etiquetas
4. Controlar leyenda
```

### 3. Generación

```
1. Hacer clic en Make your Map
2. Seleccionar plantilla
3. Completar la información
4. Elegir formato de export
5. Guardar
```

## Buenas Prácticas

### 1. Antes de la Generación

- Verificar completitud de datos
- Controlar estilos de capas
- Establecer escala apropiada

### 2. Plantilla

- Usar plantillas consistentes en el proyecto
- Personalizar encabezados para la institución
- Mantener estándares cartográficos

### 3. Output

- Guardar en alta resolución para impresión
- Mantener copia PDF para archivo
- Usar nomenclatura descriptiva

## Personalización de Plantillas

### Modificar Plantilla

Las plantillas QGIS pueden ser modificadas:
1. Abrir Layout Manager en QGIS
2. Modificar plantilla existente
3. Guardar como nueva plantilla
4. Disponible en Make your Map

### Crear Plantilla

1. Crear nuevo layout en QGIS
2. Añadir elementos necesarios
3. Configurar variables para campos dinámicos
4. Guardar en la carpeta de templates

## Resolución de Problemas

### Mapa Vacío

**Causas**:
- Ninguna capa activa
- Extensión incorrecta

**Soluciones**:
- Activar capas visibles
- Hacer zoom sobre el área con datos

### Leyenda Incompleta

**Causa**: Capas no configuradas correctamente

**Solución**: Verificar propiedades de capas en QGIS

### Export Fallido

**Causas**:
- Ruta no escribible
- Formato no soportado

**Soluciones**:
- Verificar permisos de la carpeta
- Elegir formato diferente

## Referencias

### Archivos Fuente
- `pyarchinitPlugin.py` - Función runPrint
- Plantillas en la carpeta `resources/templates/`

### QGIS
- Layout Manager
- Print Composer

---

## Video Tutorial

### Make Your Map
`[Placeholder: video_make_map.mp4]`

**Contenidos**:
- Preparación de la vista
- Uso de plantillas
- Personalización
- Export de formatos

**Duración prevista**: 10-12 minutos

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../animations/pyarchinit_create_map_animation.html)
