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
| PDF poster | Genera también un PDF póster multipágina para imprimir matrix más anchos que una hoja: las hojas se solapan 2 cm y cada hoja lleva la etiqueta "foglio n/N - riga r/R, colonna c/C - A0 scala 1:x" (hoja n/N - fila r/R, columna c/C - A0 escala 1:x). Para matrix muy grandes (cuando hay que reducir el DPI del JPG) el póster se genera de todos modos, aunque la casilla no esté marcada | Sí (para impresión) |
| Formato | Formato de las hojas del póster: A0, A1, A2, A3 | A0 |
| Scala (Escala) | Escala del póster: "Adatta all'altezza" (ajustar a la altura: una fila de hojas, la altura del matrix llena la hoja), "Adatta alla pagina" (ajustar a la página: una sola hoja con todo el matrix), 1:1, 1:2, 1:3 (escala fija, más hojas). El dibujo nunca se amplía; la orientación (vertical/horizontal) se elige automáticamente para usar menos hojas | Adatta all'altezza |

Los controles **PDF poster**, **Formato** y **Scala** están en la segunda fila de la ventana (las etiquetas están en italiano en todos los idiomas de la interfaz).

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

### Matrix de Gran Tamaño

Con matrix muy grandes (p. ej. 1300 UE y unas 2000 relaciones) la exportación con conexiones ortogonales podía tardar más de 25 minutos y producir un JPG vacío (0 bytes). Desde esta versión **Exportar Matrix** y **View Matrix** se adaptan automáticamente:

| Situación | Qué ocurre |
|-----------|------------|
| Más de **600** relaciones | Las conexiones pasan automáticamente de ortogonales (`ortho`) a polilíneas rectas con espaciado más compacto: el mismo matrix se compagina en aproximadamente un segundo. Por debajo del umbral el estilo ortogonal no cambia |
| Imagen que supera el límite del renderizador bitmap (32 767 px por lado) | El DPI de JPG/PNG se reduce automáticamente (el valor configurado en Setting_Matrix es un máximo) y junto a la imagen, en `pyarchinit_Matrix_folder`, se guardan las copias vectoriales `.svg` y `.pdf` (`Harris_matrix_tred.dot.svg/.pdf`; para View Matrix `Harris_matrix_viewtred.dot.svg/.pdf`) |
| Aviso "Matrix molto grande" (matrix muy grande: el JPG se ha generado a N dpi, usa los archivos .svg / .pdf) | Abrir el archivo `.svg` o `.pdf` (navegador, Inkscape, visor PDF) para una versión legible y ampliable sin pérdida de calidad |

Los archivos `.dot` se generan como antes.

**Exportación con periodización** (checkbox de periodos en Setting_Matrix):

- La exportación ya no se interrumpe con el error `Errore durante il rendering del file DOT: 'NoneType' object has no attribute 'write'`, que aparecía cuando Graphviz emitía un aviso y QGIS no tenía la consola Python abierta (típico en Windows). Los avisos de Graphviz ahora se escriben en la consola Python / el registro de QGIS en lugar de abortar la exportación.
- En DB grandes la exportación con periodos es mucho más rápida (la misma base de datos de 1311 UE pasó de unos 25–45 s y un DOT de 51 MB a unos 3 s) y cada fase obtiene su propio clúster invisible, de modo que Graphviz no ignora silenciosamente ninguna fase.
- Para matrix con periodos muy anchos el JPG ahora puede generarse incluso por debajo de 12 dpi si es necesario (como referencia, el matrix de 1311 UE con periodos sale a 49 dpi): es solo una vista general; para la versión legible usa las copias `.svg` / `.pdf` guardadas al lado.

**Copias vectoriales e impresión del póster**:

- Las copias `.pdf` / `.svg` se mantienen ahora siempre dentro de 200 pulgadas (14 400 pt) por lado, el límite a partir del cual Acrobat y Vista Previa muestran solo una parte de la página: todo el matrix queda así visible y ampliable (vectorial, sin pérdida de calidad). En la base de datos de 1311 UE con periodos el PDF mide 14 400 × 2 591 pt.
- Para imprimirlo usa el PDF póster (checkbox **PDF poster** en Setting_Matrix): para la misma base de datos, A0 con "Adatta all'altezza" (ajustar a la altura) da 5 hojas A0 horizontales a escala 1:3,4 (texto ≈ 4 pt: legible en un plóter; usa A0 "1:2" o "1:1" para texto más grande y más hojas). Una sola hoja A0 ("Adatta alla pagina", ajustar a la página) es solo una vista general.

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
├── Harris_matrix_tred.dot.svg  # Vectorial (solo matrix grandes)
├── Harris_matrix_tred.dot.pdf  # Vectorial (solo matrix grandes)
├── Harris_matrix_poster_A0.pdf # PDF póster multipágina para impresión
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
| *.svg/*.pdf | Versión vectorial ampliable (matrix grandes) |
| _poster_A0.pdf | PDF póster multipágina para impresión; el nombre sigue el formato elegido (p. ej. `_poster_A3.pdf`), para Export Matrix 2ED el prefijo es `Harris_matrix2ED` |

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

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/harris_matrix_animation.html)
