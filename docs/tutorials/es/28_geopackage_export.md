# Tutorial 28: Export GeoPackage

## Introducción

La función **Export GeoPackage** permite empaquetar las capas vectoriales y raster de PyArchInit en un único archivo GeoPackage (.gpkg). Este formato es ideal para compartir, archivar y la portabilidad de los datos GIS.

### Ventajas del GeoPackage

| Aspecto | Ventaja |
|---------|---------|
| Archivo único | Todos los datos en un solo archivo |
| Portabilidad | Fácil de compartir |
| Estándar OGC | Compatibilidad universal |
| Multi-capa | Vectoriales y raster juntos |
| Basado en SQLite | Ligero y rápido |

## Acceso

### Desde el Menú
**PyArchInit** → **Empaquetar para GeoPackage**

## Interfaz

### Panel de Export

```
+--------------------------------------------------+
|        Importar en GeoPackage                     |
+--------------------------------------------------+
| Destino:                                          |
|   [____________________________] [Examinar]      |
+--------------------------------------------------+
| [Exportar Capas Vectoriales]                     |
| [Exportar Capas Raster]                          |
+--------------------------------------------------+
```

## Procedimiento

### Export de Capas Vectoriales

1. Seleccionar las capas a exportar en el panel de Capas de QGIS
2. Abrir la herramienta GeoPackage Export
3. Especificar ruta y nombre del archivo de destino
4. Hacer clic en **"Exportar Capas Vectoriales"**

### Export de Capas Raster

1. Seleccionar las capas raster en el panel de Capas
2. Especificar destino (mismo archivo o nuevo)
3. Hacer clic en **"Exportar Capas Raster"**

### Export Combinado

Para incluir vectoriales y raster en el mismo GeoPackage:
1. Primero exportar los vectoriales
2. Luego exportar los raster en el mismo archivo
3. El sistema añade las capas al GeoPackage existente

## Selección de Capas

### Método

1. En el panel de Capas de QGIS, seleccionar las capas deseadas
   - Ctrl+clic para selección múltiple
   - Shift+clic para rango
2. Abrir Export GeoPackage
3. Las capas seleccionadas serán exportadas

### Capas Recomendadas

| Capa | Tipo | Notas |
|------|------|-------|
| pyunitastratigrafiche | Vectorial | UE de depósito |
| pyunitastratigrafiche_usm | Vectorial | UE murarias |
| pyarchinit_quote | Vectorial | Puntos de cota |
| pyarchinit_siti | Vectorial | Sitios |
| Ortofoto | Raster | Ortofoto de excavación |

## Output

### Estructura del GeoPackage

```
output.gpkg
├── pyunitastratigrafiche (vector)
├── pyunitastratigrafiche_usm (vector)
├── pyarchinit_quote (vector)
└── ortofoto (raster)
```

### Ruta por Defecto

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Opciones de Export

### Capas Vectoriales

- Mantiene las geometrías originales
- Preserva todos los atributos
- Convierte automáticamente nombres con espacios (usa guión bajo)

### Capas Raster

- Soporta formatos comunes (GeoTIFF, etc.)
- Mantiene la georreferenciación
- Preserva el sistema de referencia

## Usos Típicos

### Compartir Proyecto

```
1. Seleccionar todas las capas del proyecto
2. Exportar en GeoPackage
3. Compartir el archivo .gpkg
4. El destinatario lo abre directamente en QGIS
```

### Archivo de Campaña

```
1. Al final de la campaña, seleccionar capas finales
2. Exportar en GeoPackage con fecha
3. Archivar con la documentación
```

### Backup GIS

```
1. Periódicamente exportar estado actual
2. Mantener versiones con fecha
3. Usar para recuperación ante desastres
```

## Buenas Prácticas

### 1. Antes del Export

- Verificar completitud de capas
- Controlar sistema de referencia
- Guardar proyecto QGIS

### 2. Nomenclatura

- Usar nombres descriptivos para el archivo
- Incluir fecha en el nombre
- Evitar caracteres especiales

### 3. Verificación

- Abrir GeoPackage creado
- Verificar que todas las capas estén presentes
- Controlar atributos

## Resolución de Problemas

### Export Fallido

**Causas**:
- Capa no válida
- Ruta no escribible
- Espacio de disco insuficiente

**Soluciones**:
- Verificar validez de la capa
- Controlar permisos de la carpeta
- Liberar espacio de disco

### Capas Faltantes

**Causa**: Capa no seleccionada

**Solución**: Verificar selección en el panel de Capas

### Raster No Exportado

**Causas**:
- Formato no soportado
- Archivo fuente no accesible

**Soluciones**:
- Convertir raster a GeoTIFF
- Verificar ruta del archivo fuente

## Referencias

### Archivos Fuente
- `tabs/gpkg_export.py` - Interfaz de export
- `gui/ui/gpkg_export.ui` - Layout UI

### Documentación
- [GeoPackage Standard](https://www.geopackage.org/)
- [QGIS GeoPackage Support](https://docs.qgis.org/)

---

## Video Tutorial

### Export GeoPackage
`[Placeholder: video_geopackage.mp4]`

**Contenidos**:
- Selección de capas
- Export de vectoriales y raster
- Verificación del output
- Buenas prácticas

**Duración prevista**: 8-10 minutos

---

*Última actualización: Enero 2026*
