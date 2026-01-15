# Tutorial 23: Búsqueda de Imágenes

## Introducción

La función **Búsqueda de Imágenes** permite buscar rápidamente imágenes en la base de datos PyArchInit filtrando por sitio, tipo de entidad y otros criterios. Es una herramienta complementaria al Media Manager para la búsqueda global.

## Acceso

### Desde el Menú
**PyArchInit** → **Búsqueda de Imágenes**

## Interfaz

### Panel de Búsqueda

```
+--------------------------------------------------+
|           Búsqueda de Imágenes                   |
+--------------------------------------------------+
| Filtros:                                          |
|   Sitio: [ComboBox]                              |
|   Tipo Entidad: [-- Todos -- | UE | Pottery | ...]|
|   [ ] Solo imágenes sin etiquetar                |
+--------------------------------------------------+
| [Buscar]  [Limpiar]                              |
+--------------------------------------------------+
| Resultados:                                       |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Abrir Imagen] [Exportar] [Ir al Registro]       |
+--------------------------------------------------+
```

### Filtros Disponibles

| Filtro | Descripción |
|--------|-------------|
| Sitio | Selecciona sitio específico o todos |
| Tipo Entidad | UE, Pottery, Materiales, Tumba, Estructura, UT |
| Solo sin etiquetar | Muestra solo imágenes sin conexiones |

### Tipos de Entidad

| Tipo | Descripción |
|------|-------------|
| -- Todos -- | Todas las entidades |
| US | Unidades Estratigráficas |
| Pottery | Cerámica |
| Materiales | Hallazgos/Inventario |
| Tumba | Sepulturas |
| Estructura | Estructuras |
| UT | Unidades Topográficas |

## Funcionalidades

### Búsqueda Básica

1. Seleccionar los filtros deseados
2. Hacer clic en **"Buscar"**
3. Visualizar los resultados en la cuadrícula

### Acciones sobre Resultados

| Botón | Función |
|-------|---------|
| Abrir Imagen | Visualiza imagen a tamaño original |
| Exportar | Exporta imagen seleccionada |
| Ir al Registro | Abre la ficha de la entidad conectada |
| Abrir Media Manager | Abre el Media Manager con la imagen seleccionada |

### Menú Contextual (Clic derecho)

- **Abrir imagen**
- **Exportar imagen...**
- **Ir al registro**

### Búsqueda de Imágenes Sin Etiquetar

Checkbox **"Solo imágenes sin etiquetar"**:
- Encuentra imágenes en la base de datos sin conexiones
- Útil para limpieza y organización
- Permite identificar imágenes por catalogar

## Workflow Típico

### 1. Encontrar Imágenes de un Sitio

```
1. Seleccionar sitio del ComboBox
2. Dejar "-- Todos --" para tipo de entidad
3. Hacer clic en Buscar
4. Navegar por los resultados
```

### 2. Encontrar Imágenes de UE Específicas

```
1. Seleccionar sitio
2. Seleccionar "UE" como tipo de entidad
3. Hacer clic en Buscar
4. Doble clic para abrir imagen
```

### 3. Identificar Imágenes No Catalogadas

```
1. Seleccionar sitio (o todos)
2. Activar "Solo imágenes sin etiquetar"
3. Hacer clic en Buscar
4. Para cada resultado:
   - Abrir imagen
   - Identificar contenido
   - Conectar mediante Media Manager
```

## Exportación

### Export de Imagen Individual

1. Seleccionar imagen en los resultados
2. Hacer clic en **"Exportar"** o menú contextual
3. Seleccionar destino
4. Guardar

### Export Múltiple

Para exportar varias imágenes, usar la función **Exportar Imágenes** dedicada (Tutorial 24).

## Buenas Prácticas

### 1. Búsqueda Eficiente

- Usar filtros específicos para resultados precisos
- Empezar con filtros amplios, luego restringir
- Usar la búsqueda sin etiquetar periódicamente

### 2. Organización

- Catalogar imágenes sin etiquetar regularmente
- Verificar conexiones después de importación
- Mantener nomenclatura consistente

## Resolución de Problemas

### Sin Resultados

**Causas**:
- Filtros demasiado restrictivos
- Ninguna imagen para los criterios

**Soluciones**:
- Ampliar los filtros
- Verificar existencia de datos

### Imagen No Visualizable

**Causas**:
- Archivo no encontrado
- Formato no soportado

**Soluciones**:
- Verificar ruta del archivo
- Controlar formato de imagen

## Referencias

### Archivos Fuente
- `tabs/Image_search.py` - Interfaz de búsqueda
- `gui/ui/pyarchinit_image_search_dialog.ui` - Layout UI

### Base de Datos
- `media_table` - Datos media
- `media_to_entity_table` - Conexiones

---

## Video Tutorial

### Búsqueda de Imágenes
`[Placeholder: video_busqueda_imagenes.mp4]`

**Contenidos**:
- Uso de filtros
- Búsqueda avanzada
- Export de resultados

**Duración prevista**: 8-10 minutos

---

*Última actualización: Enero 2026*
