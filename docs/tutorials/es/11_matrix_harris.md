# Tutorial 11: Matrix de Harris

## Introducción

El **Matrix de Harris** (o diagrama estratigráfico) es una herramienta fundamental en arqueología para representar gráficamente las relaciones estratigráficas entre las diferentes Unidades Estratigráficas (UE). PyArchInit genera automáticamente el Matrix de Harris a partir de las relaciones estratigráficas introducidas en las fichas de UE.

### ¿Qué es el Matrix de Harris?

El Matrix de Harris es un diagrama que representa:
- La **secuencia temporal** de las UE (de la más reciente arriba a la más antigua abajo)
- Las **relaciones físicas** entre las UE (cubre/cubierta por, corta/cortada por, se une a)
- La **periodización** de la excavación (agrupación por periodos y fases)

### Tipos de Relaciones Representadas

| Relación | Significado | Representación |
|----------|-------------|----------------|
| Cubre/Cubierta por | Superposición física | Línea continua hacia abajo |
| Corta/Cortada por | Acción negativa (interfaz) | Línea discontinua |
| Se une a/Igual que | Contemporaneidad | Línea horizontal bidireccional |
| Rellena/Rellenada por | Relleno de corte | Línea continua |
| Se apoya en/Le apoya | Apoyo estructural | Línea continua |

## Acceso a la Función

### Desde el Menú Principal
1. **PyArchInit** en la barra del menú
2. Seleccionar **Matrix de Harris**

### Desde la Ficha de UE
1. Abrir la Ficha de UE
2. Pestaña **Map**
3. Botón **"Exportar Matrix"** o **"View Matrix"**

### Prerequisitos
- Base de datos conectada correctamente
- UE con relaciones estratigráficas completadas
- Periodización definida (opcional pero recomendado)
- Graphviz instalado en el sistema

## Configuración del Matrix

### Ventana de Ajustes (Setting_Matrix)

Antes de la generación, aparece una ventana de configuración:

#### Pestaña General

| Campo | Descripción | Valor Recomendado |
|-------|-------------|-------------------|
| DPI | Resolución de la imagen | 150-300 |
| Mostrar Periodos | Agrupar UE por periodo/fase | Sí |
| Mostrar Leyenda | Incluir leyenda en el gráfico | Sí |

#### Pestaña Nodos "Ante/Post" (Relaciones Normales)

| Parámetro | Descripción | Opciones |
|-----------|-------------|----------|
| Forma nodo | Forma geométrica | box, ellipse, diamond |
| Color relleno | Color interno | white, lightblue, etc. |
| Estilo | Aspecto del borde | solid, dashed |
| Grosor línea | Anchura del borde | 0.5 - 2.0 |
| Tipo flecha | Punta de la flecha | normal, diamond, none |
| Tamaño flecha | Tamaño de la punta | 0.5 - 1.5 |

#### Pestaña Nodos "Negative" (Cortes)

| Parámetro | Descripción | Opciones |
|-----------|-------------|----------|
| Forma nodo | Forma geométrica | box, ellipse, diamond |
| Color relleno | Color distintivo | gray, lightcoral |
| Estilo línea | Aspecto de la conexión | dashed (discontinuo) |

#### Pestaña Nodos "Contemporáneo"

| Parámetro | Descripción | Opciones |
|-----------|-------------|----------|
| Forma nodo | Forma geométrica | box, ellipse |
| Color relleno | Color distintivo | lightyellow, white |
| Estilo línea | Aspecto de la conexión | solid |
| Flecha | Tipo de conexión | none (bidireccional) |

#### Pestaña Conexiones Especiales (">", ">>")

Para relaciones estratigráficas especiales o conexiones documentales:

| Parámetro | Descripción |
|-----------|-------------|
| Forma | box, ellipse |
| Color | lightgreen, etc. |
| Estilo | solid, dashed |

## Tipos de Exportación

### 1. Export Matrix Estándar

Genera el matrix básico con:
- Todas las relaciones estratigráficas
- Agrupación por periodo/fase
- Layout vertical (TB - Top to Bottom)

**Output**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Export Matrix 2ED (Extendido)

Versión extendida con:
- Información adicional en los nodos (UE + definición + datación)
- Conexiones especiales (>, >>)
- Exportación también en formato GraphML

**Output**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. View Matrix (Visualización Rápida)

Para visualización rápida sin opciones de configuración:
- Usa ajustes predeterminados
- Generación más rápida
- Ideal para controles rápidos

## Proceso de Generación

### Paso 1: Recopilación de Datos

El sistema recopila automáticamente:
```
Para cada UE en el sitio/área seleccionado:
  - Número UE
  - Tipo de unidad (US/USM)
  - Relaciones estratigráficas
  - Periodo y fase inicial
  - Definición interpretativa
```

### Paso 2: Construcción del Grafo

Creación de las relaciones:
```
Secuencia (Ante/Post):
  UE1 -> UE2 (UE1 cubre UE2)

Negativo (Cortes):
  UE3 -> UE4 (UE3 corta UE4)

Contemporáneo:
  UE5 <-> UE6 (UE5 se une a UE6)
```

### Paso 3: Clustering por Periodos

Agrupación jerárquica:
```
Sitio
  └── Área
      └── Periodo 1 : Fase 1 : "Época Romana"
          ├── UE101
          ├── UE102
          └── UE103
      └── Periodo 1 : Fase 2 : "Antigüedad Tardía"
          ├── UE201
          └── UE202
```

### Paso 4: Reducción Transitiva (tred)

El comando `tred` de Graphviz elimina las relaciones redundantes:
- Si UE1 -> UE2 y UE2 -> UE3, elimina UE1 -> UE3
- Simplifica el diagrama
- Mantiene solo relaciones directas

### Paso 5: Renderizado Final

Generación de imagen con formatos múltiples:
- DOT (fuente Graphviz)
- JPG (imagen comprimida)
- PNG (imagen sin pérdida)

## Interpretación del Matrix

### Lectura Vertical

```
     [UE más recientes]
           ↓
        UE 001
           ↓
        UE 002
           ↓
        UE 003
           ↓
     [UE más antiguas]
```

### Lectura de los Clusters

Las cajas coloreadas representan periodos/fases:
- **Azul claro**: Cluster de periodo
- **Amarillo**: Cluster de fase
- **Gris**: Fondo del sitio

### Tipos de Conexiones

```
─────────→  Línea continua = Cubre/Rellena/Se apoya
- - - - →  Línea discontinua = Corta
←────────→  Bidireccional = Contemporáneo/Igual a
```

### Colores de los Nodos

| Color | Significado Típico |
|-------|-------------------|
| Blanco | UE depósito normal |
| Gris | UE negativa (corte) |
| Amarillo | UE contemporáneas |
| Azul | UE con relaciones especiales |

## Resolución de Problemas

### Error: "Loop Detected"

**Causa**: Existen ciclos en las relaciones (A cubre B, B cubre A)

**Solución**:
1. Abrir la Ficha de UE
2. Verificar las relaciones de las UE indicadas
3. Corregir las relaciones circulares
4. Regenerar el matrix

### Error: "tred command not found"

**Causa**: Graphviz no instalado

**Solución**:
- **Windows**: Instalar Graphviz desde graphviz.org
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matrix No Generado

**Posibles causas**:
1. Ninguna relación estratigráfica introducida
2. UE sin periodo/fase asignado
3. Problemas de permisos en la carpeta de salida

**Verificación**:
1. Comprobar que las UE tengan relaciones
2. Verificar la periodización
3. Comprobar los permisos de `pyarchinit_Matrix_folder`

### Matrix Demasiado Grande

**Problema**: Imagen ilegible con muchas UE

**Soluciones**:
1. Reducir el DPI (100-150)
2. Filtrar por área específica
3. Usar el View Matrix para áreas individuales
4. Exportar en formato vectorial (DOT) y abrir con yEd

### UE No Agrupadas por Periodo

**Causa**: Falta la periodización o no está habilitada

**Solución**:
1. Completar la Ficha de Periodización
2. Asignar periodo/fase inicial a las UE
3. Habilitar "Mostrar Periodos" en los ajustes

## Output y Archivos Generados

### Carpeta de Salida

```
~/pyarchinit/pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Fuente Graphviz
├── Harris_matrix_tred.dot      # Después de reducción transitiva
├── Harris_matrix_tred.dot.jpg  # Imagen final JPG
├── Harris_matrix_tred.dot.png  # Imagen final PNG
├── Harris_matrix2ED.dot        # Versión extendida
├── Harris_matrix2ED_graphml.dot # Para export GraphML
└── matrix_error.txt            # Log de errores
```

### Uso de los Archivos

| Archivo | Uso |
|---------|-----|
| *.jpg/*.png | Inserción en informes |
| *.dot | Modificación con editor Graphviz |
| _graphml.dot | Import en yEd para edición avanzada |

## Buenas Prácticas

### 1. Antes de la Generación

- Verificar completitud de relaciones estratigráficas
- Comprobar ausencia de ciclos
- Asignar periodo/fase a todas las UE
- Completar la definición interpretativa

### 2. Durante la Compilación de UE

- Introducir relaciones bidireccionales correctas
- Usar terminología consistente
- Verificar área correcta en las relaciones

### 3. Optimización del Output

- Para impresión: DPI 300
- Para pantalla: DPI 150
- Para excavaciones complejas: subdividir por áreas

### 4. Control de Calidad

- Comparar matrix con documentación de excavación
- Verificar secuencias lógicas
- Comprobar agrupaciones por periodo

## Workflow Completo

### 1. Preparación de Datos

```
1. Completar fichas UE con todas las relaciones
2. Completar ficha de Periodización
3. Asignar periodo/fase a las UE
4. Verificar consistencia de datos
```

### 2. Generación del Matrix

```
1. Menú PyArchInit → Matrix de Harris
2. Configurar ajustes (DPI, colores)
3. Habilitar cluster por periodos
4. Generar el matrix
```

### 3. Verificación y Corrección

```
1. Comprobar el matrix generado
2. Identificar posibles errores
3. Corregir relaciones en las fichas de UE
4. Regenerar si es necesario
```

### 4. Uso Final

```
1. Insertar en memoria de excavación
2. Exportar para publicación
3. Archivar con documentación
```

## Integración con Otras Herramientas

### Export para yEd

El archivo `_graphml.dot` puede abrirse en yEd para:
- Edición manual del layout
- Adición de anotaciones
- Exportación en diferentes formatos

### Export para s3egraph

PyArchInit soporta la exportación para el sistema s3egraph:
- Formato compatible
- Mantiene relaciones estratigráficas
- Soporte para visualización 3D

## Referencias

### Archivos Fuente
- `tabs/Interactive_matrix.py` - Interfaz interactiva
- `modules/utility/pyarchinit_matrix_exp.py` - Clases HarrisMatrix y ViewHarrisMatrix

### Base de Datos
- `us_table` - Datos UE y relaciones
- `periodizzazione_table` - Periodos y fases

### Dependencias
- Graphviz (dot, tred)
- Python graphviz library

---

*Última actualización: Enero 2026*
