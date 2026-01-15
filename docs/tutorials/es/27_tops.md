# Tutorial 27: TOPS - Total Open Station

## Introducción

**TOPS** (Total Open Station) es la integración de PyArchInit con el software de código abierto para la descarga y conversión de datos de estaciones totales. Permite importar directamente los levantamientos topográficos en el sistema PyArchInit.

### ¿Qué es Total Open Station?

Total Open Station es un software libre para:
- Descarga de datos de estaciones totales
- Conversión entre formatos
- Export en formatos compatibles con GIS

PyArchInit integra TOPS para simplificar la importación de los datos de excavación.

## Acceso

### Desde el Menú
**PyArchInit** → **TOPS (Total Open Station)**

## Interfaz

### Panel Principal

```
+--------------------------------------------------+
|         Total Open Station to PyArchInit          |
+--------------------------------------------------+
| Input:                                            |
|   Archivo: [___________________] [Examinar]      |
|   Formato input: [ComboBox formatos]             |
+--------------------------------------------------+
| Output:                                           |
|   Archivo: [___________________] [Examinar]      |
|   Formato output: [csv | dxf | ...]              |
+--------------------------------------------------+
| [ ] Convertir coordenadas                        |
+--------------------------------------------------+
| [Vista Previa de Datos - TableView]              |
+--------------------------------------------------+
|              [Exportar]                           |
+--------------------------------------------------+
```

## Formatos Soportados

### Formatos de Input (Estaciones Totales)

| Formato | Fabricante | Extensión |
|---------|------------|-----------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| CSV genérico | - | .csv |

### Formatos de Output

| Formato | Uso |
|---------|-----|
| CSV | Import en PyArchInit Quote |
| DXF | Import en CAD/GIS |
| GeoJSON | Import directo GIS |
| Shapefile | Estándar GIS |

## Workflow

### 1. Importar Datos de Estación Total

```
1. Conectar estación total al PC
2. Descargar archivo de datos (formato nativo)
3. Guardar en carpeta de trabajo
```

### 2. Conversión con TOPS

```
1. Abrir TOPS en PyArchInit
2. Seleccionar archivo de input (Examinar)
3. Elegir formato de input correcto
4. Establecer archivo de output
5. Elegir formato de output (CSV recomendado)
6. Hacer clic en Exportar
```

### 3. Import en PyArchInit

Después del export en CSV:
1. El sistema solicita automáticamente:
   - **Nombre del sitio** arqueológico
   - **Unidad de medida** (metros)
   - **Nombre del dibujante**
2. Los puntos se cargan como capa QGIS
3. Opcional: copia en capa Quote US

### 4. Conversión de Coordenadas (Opcional)

Si checkbox **"Convertir coordenadas"** activo:
- Introducir offset X, Y, Z
- Aplicar traslación de coordenadas
- Útil para sistemas de referencia locales

## Vista Previa de Datos

### TableView

Muestra vista previa de los datos importados:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Modificación de Datos

- Seleccionar filas a eliminar
- Botón **Delete** elimina filas seleccionadas
- Útil para filtrar puntos innecesarios

## Integración con Quote US

### Copia Automática

Después del import, TOPS puede copiar los puntos en la capa **"Quote US disegno"**:
1. Se solicita el nombre del sitio
2. Se solicita la unidad de medida
3. Se solicita el dibujante
4. Los puntos se copian con atributos correctos

### Atributos Completados

| Atributo | Valor |
|----------|-------|
| sito_q | Nombre del sitio introducido |
| area_q | Extraído de point_name |
| unita_misu_q | Unidad introducida (metros) |
| disegnatore | Nombre introducido |
| data | Fecha actual |

## Convenciones de Nomenclatura

### Formato point_name

Para la extracción automática del área:
```
[AREA]-[NOMBRE_PUNTO]
Ejemplo: 1000-P001
```

El sistema separa automáticamente:
- `area_q` = 1000
- `point_name` = P001

## Buenas Prácticas

### 1. En Campo

- Usar nomenclatura consistente para los puntos
- Incluir código de área en el nombre del punto
- Anotar el sistema de referencia usado

### 2. Importación

- Verificar formato de input correcto
- Controlar la vista previa antes de exportar
- Eliminar puntos erróneos/duplicados

### 3. Post-Importación

- Verificar coordenadas en QGIS
- Controlar la capa Quote US
- Conectar puntos a las UE correctas

## Resolución de Problemas

### Formato No Reconocido

**Causa**: Formato de estación no soportado

**Solución**:
- Exportar desde la estación en formato genérico (CSV)
- Verificar documentación de la estación

### Coordenadas Incorrectas

**Causas**:
- Sistema de referencia diferente
- Offset no aplicado

**Soluciones**:
- Verificar sistema de referencia del proyecto
- Aplicar conversión de coordenadas

### Capa No Creada

**Causa**: Error durante la importación

**Solución**:
- Controlar log de errores
- Verificar formato del archivo de output
- Repetir la conversión

## Referencias

### Archivos Fuente
- `tabs/tops_pyarchinit.py` - Interfaz principal
- `gui/ui/Tops2pyarchinit.ui` - Layout UI

### Software Externo
- [Total Open Station](https://tops.iosa.it/) - Software principal
- Documentación de formatos de estaciones

---

## Video Tutorial

### TOPS Import
`[Placeholder: video_tops.mp4]`

**Contenidos**:
- Descarga de estación total
- Conversión de formatos
- Import en PyArchInit
- Integración con Quote US

**Duración prevista**: 12-15 minutos

---

*Última actualización: Enero 2026*
