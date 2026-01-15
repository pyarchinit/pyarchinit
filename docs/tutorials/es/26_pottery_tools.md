# Tutorial 26: Pottery Tools

## Introducción

**Pottery Tools** es un módulo avanzado para el procesamiento de imágenes cerámicas. Ofrece herramientas para extraer imágenes de PDF, generar layouts de láminas, procesar dibujos con AI (PotteryInk) y otras funcionalidades especializadas para la documentación cerámica.

### Funcionalidades Principales

- Extracción de imágenes desde PDF
- Generación de layouts de láminas cerámicas
- Procesamiento de imágenes con AI
- Conversión de formato de dibujos
- Integración con la Ficha Pottery

## Acceso

### Desde el Menú
**PyArchInit** → **Pottery Tools**

## Interfaz

### Panel Principal

```
+--------------------------------------------------+
|              Pottery Tools                        |
+--------------------------------------------------+
| [Tab: Extracción PDF]                            |
| [Tab: Layout Generator]                          |
| [Tab: Image Processing]                          |
| [Tab: PotteryInk AI]                             |
+--------------------------------------------------+
| [Barra de Progreso]                              |
| [Mensajes de Log]                                |
+--------------------------------------------------+
```

## Tab Extracción PDF

### Función

Extrae automáticamente las imágenes de documentos PDF que contienen láminas cerámicas.

### Uso

1. Seleccionar archivo PDF fuente
2. Especificar carpeta de destino
3. Hacer clic en **"Extraer"**
4. Las imágenes se guardan como archivos separados

### Opciones

| Opción | Descripción |
|--------|-------------|
| DPI | Resolución de extracción (150-600) |
| Formato | PNG, JPG, TIFF |
| Páginas | Todas o rango específico |

## Tab Layout Generator

### Función

Genera automáticamente láminas de cerámica con layout estandarizado.

### Tipos de Layout

| Layout | Descripción |
|--------|-------------|
| Cuadrícula | Imágenes en cuadrícula regular |
| Secuencia | Imágenes en secuencia numerada |
| Comparación | Layout para comparación |
| Catálogo | Formato catálogo con leyendas |

### Uso

1. Seleccionar imágenes a incluir
2. Elegir tipo de layout
3. Configurar parámetros (dimensiones, márgenes)
4. Generar lámina

### Parámetros de Layout

| Parámetro | Descripción |
|-----------|-------------|
| Tamaño de página | A4, A3, Personalizado |
| Orientación | Vertical, Horizontal |
| Márgenes | Espacio de bordes |
| Espaciado | Distancia entre imágenes |
| Leyendas | Texto bajo las imágenes |

## Tab Image Processing

### Función

Procesamiento por lotes de imágenes cerámicas.

### Operaciones Disponibles

| Operación | Descripción |
|-----------|-------------|
| Redimensionar | Escalar imágenes |
| Recortar | Crop automático/manual |
| Rotar | Rotación en grados |
| Convertir | Cambio de formato |
| Optimizar | Compresión de calidad |

### Procesamiento por Lotes

1. Seleccionar carpeta fuente
2. Elegir operaciones a aplicar
3. Especificar destino
4. Ejecutar procesamiento

## Tab PotteryInk AI

### Función

Utiliza inteligencia artificial para:
- Conversión de foto → dibujo técnico
- Reconocimiento de formas cerámicas
- Sugerencias de clasificación
- Medición automática

### Requisitos

- Entorno virtual de Python configurado
- Modelos AI descargados (YOLO, etc.)
- GPU recomendada (pero no obligatoria)

### Uso

1. Cargar imagen de cerámica
2. Seleccionar tipo de procesamiento
3. Esperar el procesamiento AI
4. Verificar y guardar el resultado

### Tipos de Procesamiento AI

| Tipo | Descripción |
|------|-------------|
| Ink Conversion | Convierte foto en dibujo técnico |
| Shape Detection | Reconoce la forma del vaso |
| Profile Extraction | Extrae el perfil cerámico |
| Decoration Analysis | Analiza decoraciones |

## Entorno Virtual

### Configuración Automática

En el primer inicio, Pottery Tools:
1. Crea entorno virtual en `~/pyarchinit/bin/pottery_venv/`
2. Instala las dependencias necesarias
3. Descarga modelos AI (si se requieren)

### Dependencias

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Verificación de Instalación

El log muestra el estado:
```
✓ Virtual environment created
✓ Dependencies installed
✓ Models downloaded
✓ Pottery Tools initialized successfully!
```

## Integración con Base de Datos

### Conexión a la Ficha Pottery

Las imágenes procesadas pueden ser:
- Conectadas automáticamente a registros Pottery
- Guardadas con metadatos apropiados
- Organizadas por sitio/inventario

## Buenas Prácticas

### 1. Calidad de Imágenes de Entrada

- Resolución mínima: 300 DPI
- Iluminación uniforme
- Fondo neutro (blanco/gris)
- Escala métrica visible

### 2. Procesamiento AI

- Verificar siempre los resultados AI
- Corregir manualmente si es necesario
- Guardar originales y procesados

### 3. Organización del Output

- Usar nomenclatura consistente
- Organizar por sitio/campaña
- Mantener trazabilidad

## Resolución de Problemas

### Entorno Virtual No Creado

**Causas**:
- Python no encontrado
- Permisos insuficientes

**Soluciones**:
- Verificar instalación de Python
- Controlar permisos de la carpeta

### Procesamiento AI Lento

**Causas**:
- Ninguna GPU disponible
- Imágenes demasiado grandes

**Soluciones**:
- Reducir el tamaño de las imágenes
- Usar CPU (más lento pero funciona)

### Extracción de PDF Fallida

**Causas**:
- PDF protegido
- Formato no soportado

**Soluciones**:
- Verificar protección del PDF
- Probar con otro software PDF

## Referencias

### Archivos Fuente
- `tabs/Pottery_tools.py` - Interfaz principal
- `modules/utility/pottery_utilities.py` - Utility de procesamiento
- `gui/ui/Pottery_tools.ui` - Layout UI

### Carpetas
- `~/pyarchinit/bin/pottery_venv/` - Entorno virtual
- `~/pyarchinit/models/` - Modelos AI

---

## Video Tutorial

### Pottery Tools Completo
`[Placeholder: video_pottery_tools.mp4]`

**Contenidos**:
- Extracción desde PDF
- Generación de layout
- Procesamiento AI
- Integración con base de datos

**Duración prevista**: 20-25 minutos

---

*Última actualización: Enero 2026*
