# Tutorial 24: Exportar Imágenes

## Introducción

La función **Exportar Imágenes** permite exportar en masa las imágenes asociadas a los registros arqueológicos, organizándolas automáticamente en carpetas por período, fase, tipo de entidad.

## Acceso

### Desde el Menú
**PyArchInit** → **Exportar Imágenes**

## Interfaz

### Panel de Export

```
+--------------------------------------------------+
|           Exportar Imágenes                       |
+--------------------------------------------------+
| Sitio: [ComboBox selección sitio]                |
| Año: [ComboBox año de excavación]                |
+--------------------------------------------------+
| Tipo de Export:                                   |
|   [o] Todas las imágenes                         |
|   [ ] Solo UE                                    |
|   [ ] Solo Hallazgos                             |
|   [ ] Solo Pottery                               |
+--------------------------------------------------+
| [Abrir Carpeta]           [Exportar]             |
+--------------------------------------------------+
```

### Opciones de Export

| Opción | Descripción |
|--------|-------------|
| Todas las imágenes | Exporta todo el material fotográfico |
| Solo UE | Exporta solo imágenes conectadas a UE |
| Solo Hallazgos | Exporta solo imágenes de los hallazgos |
| Solo Pottery | Exporta solo imágenes de cerámica |

## Estructura del Output

### Organización de Carpetas

El export crea una estructura jerárquica:

```
pyarchinit_image_export/
└── [Nombre Sitio] - Todas las imágenes/
    ├── Periodo - 1/
    │   ├── Fase - 1/
    │   │   ├── US_001/
    │   │   │   ├── foto_001.jpg
    │   │   │   └── foto_002.jpg
    │   │   └── US_002/
    │   │       └── foto_003.jpg
    │   └── Fase - 2/
    │       └── US_003/
    │           └── foto_004.jpg
    └── Periodo - 2/
        └── ...
```

### Convención de Nombres

Los archivos mantienen el nombre original, organizados por:
1. **Período** - Período cronológico inicial
2. **Fase** - Fase cronológica inicial
3. **Entidad** - UE, Hallazgo, etc.

## Proceso de Export

### Paso 1: Selección de Parámetros

1. Seleccionar el **Sitio** del ComboBox
2. Seleccionar el **Año** (opcional)
3. Elegir el **Tipo de export**

### Paso 2: Ejecución

1. Hacer clic en **"Exportar"**
2. Esperar la finalización
3. Mensaje de confirmación

### Paso 3: Verificación

1. Hacer clic en **"Abrir Carpeta"**
2. Verificar la estructura creada
3. Controlar la completitud

## Carpeta de Output

### Ruta Estándar

```
~/pyarchinit/pyarchinit_image_export/
```

### Contenido

- Carpetas organizadas por sitio
- Subcarpetas por período/fase
- Imágenes originales (no redimensionadas)

## Filtro por Año

El ComboBox **Año** permite:
- Exportar solo imágenes de una campaña específica
- Organizar export por año de excavación
- Reducir el tamaño del export

## Buenas Prácticas

### 1. Antes del Export

- Verificar conexiones imágenes-entidades
- Controlar periodización de UE
- Asegurar espacio de disco suficiente

### 2. Durante el Export

- No interrumpir el proceso
- Esperar el mensaje de finalización

### 3. Después del Export

- Verificar la estructura de carpetas
- Controlar la completitud de imágenes
- Crear backup si es necesario

## Usos Típicos

### Preparación de Memoria

```
1. Seleccionar sitio
2. Exportar todas las imágenes
3. Utilizar la estructura para los capítulos de la memoria
```

### Entrega a la Administración

```
1. Seleccionar sitio y año
2. Exportar por tipología requerida
3. Organizar según estándares ministeriales
```

### Backup de Campaña

```
1. Al final de la campaña, exportar todo
2. Archivar en almacenamiento externo
3. Verificar integridad
```

## Resolución de Problemas

### Export Incompleto

**Causas**:
- Imágenes no conectadas
- Rutas de archivo incorrectas

**Soluciones**:
- Verificar conexiones en Media Manager
- Controlar existencia de archivos fuente

### Estructura No Correcta

**Causas**:
- Periodización faltante
- UE sin período/fase

**Soluciones**:
- Completar periodización de UE
- Asignar período/fase a todas las UE

## Referencias

### Archivos Fuente
- `tabs/Images_directory_export.py` - Interfaz de export
- `gui/ui/Images_directory_export.ui` - Layout UI

### Carpetas
- `~/pyarchinit/pyarchinit_image_export/` - Output del export

---

## Video Tutorial

### Export de Imágenes
`[Placeholder: video_export_imagenes.mp4]`

**Contenidos**:
- Configuración del export
- Estructura del output
- Organización del archivo

**Duración prevista**: 10-12 minutos

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/pyarchinit_image_export_animation.html)
