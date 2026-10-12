# PyArchInit - GeoArchaeo - Análisis Geoestadístico

## Índice
1. [Introducción](#introducción)
2. [Acceso a la herramienta](#acceso-a-la-herramienta)
3. [Interfaz de usuario](#interfaz-de-usuario)
4. [Pestaña Datos](#pestaña-datos)
5. [Pestaña Variograma](#pestaña-variograma)
6. [Pestaña Kriging](#pestaña-kriging)
7. [Pestaña Patrones (ML)](#pestaña-patrones-ml)
8. [Pestaña Muestreo](#pestaña-muestreo)
9. [Pestaña Informe](#pestaña-informe)
10. [Flujo de trabajo operativo](#flujo-de-trabajo-operativo)
11. [Solución de problemas](#solución-de-problemas)
12. [Notas técnicas](#notas-técnicas)

---

## Introducción

**GeoArchaeo** es el módulo de análisis geoestadístico integrado en PyArchInit y corresponde a la versión **1.3.1** del plugin GeoArchaeo. Trabaja con cualquier capa de puntos del proyecto QGIS que tenga un campo numérico (número de fragmentos, medidas geofísicas, análisis de suelo, medidas de las tumbas…) y acompaña el análisis desde las estadísticas descriptivas hasta el variograma, la interpolación mediante kriging ordinario con su incertidumbre, la búsqueda de grupos y anomalías con aprendizaje automático, la propuesta de nuevos puntos de muestreo y, por último, un informe.

La interfaz de GeoArchaeo solo existe en italiano y en inglés. En este tutorial las etiquetas están traducidas y entre paréntesis se indica la etiqueta inglesa que aparece en el panel.

<!-- VIDEO: Introduccion a GeoArchaeo -->
> **Video Tutorial**: [Insertar enlace de video introduccion GeoArchaeo]

### ¿Por qué el análisis geoestadístico en arqueología?

El análisis geoestadístico permite:

- **Describir** la distribución de los valores medidos (media, dispersión, asimetría, valores atípicos)
- **Cuantificar** la correlación espacial, es decir, hasta qué distancia se parecen los valores (variograma)
- **Interpolar** los valores entre los puntos conocidos, obteniendo una superficie continua acompañada de su incertidumbre (kriging)
- **Reconocer** grupos de puntos similares y anomalías (aprendizaje automático)
- **Planificar** dónde muestrear o excavar en las próximas campañas
- **Documentar** los análisis en un informe

### Visión general del flujo de trabajo

```
Datos de entrada: capa de puntos + campo numérico (elegidos arriba, una sola vez)
  │
  ├─ 1 Datos ............ estadísticas descriptivas, histograma
  ├─ 2 Variograma ....... pepita, meseta, alcance, anisotropía
  ├─ 3 Kriging .......... rásteres de la estimación y de la incertidumbre, validación cruzada
  ├─ 4 Patrones (ML) .... grupos y anomalías (capa de puntos)
  ├─ 5 Muestreo ......... nuevos puntos propuestos (capa de puntos)
  └─ 6 Informe .......... documento HTML con gráficos interactivos, o PDF
```

### Novedades de la versión 1.3.1

- La capa y el campo se eligen **una sola vez** arriba y valen para todas las pestañas; cada pestaña conserva sus propios resultados
- Los gráficos aparecen en el panel incluso sin QtWebEngine (vista previa estática y botón para abrirlos en el navegador)
- El kriging produce también el **ráster de incertidumbre**, aplica la rampa de colores y calcula una verdadera **validación cruzada leave-one-out**
- La anisotropía se comprueba con verdaderos **variogramas direccionales**; pepita, meseta y alcance pueden fijarse a mano
- Variograma y kriging son mucho más rápidos (búsqueda de vecinos con KD-tree): cuadrículas de hasta **500 × 500 celdas**
- Los valores NULL ya no bloquean las estadísticas ni el kriging; el informe contiene los gráficos; los datos de ejemplo proceden de la carpeta del módulo
- El idioma del panel se guarda en la configuración de QGIS

---

## Acceso a la herramienta

GeoArchaeo forma parte del grupo de herramientas de análisis de PyArchInit.

### Desde la barra de herramientas

1. En la barra de herramientas de PyArchInit, localizar el botón desplegable de las **herramientas de análisis** (el mismo grupo que contiene, entre otros, SAM, Pottery Tools y MoveCost)
2. Hacer clic en la flecha junto al botón: el icono visible puede ser el de otra herramienta del grupo
3. Elegir **GeoArchaeo - Geostatistical Analysis** (etiqueta de la acción en PyArchInit cuando QGIS está en español)

<!-- IMAGE: Boton desplegable de las herramientas de analisis en la barra de herramientas -->
> **Fig. 1**: El menú desplegable de las herramientas de análisis en la barra de herramientas de PyArchInit

La misma entrada se encuentra en el menú **pyArchInit** de la barra de menús de QGIS y en el menú de complementos, bajo **pyArchInit - Archaeological GIS Tools**.

El panel GeoArchaeo se abre como **panel acoplable** en el lado derecho de la ventana de QGIS: se puede mover, redimensionar o desacoplar como cualquier panel de QGIS. Si se cierra, la misma entrada lo vuelve a abrir con los resultados de la sesión todavía presentes.

<!-- IMAGE: Panel GeoArchaeo acoplado a la derecha en QGIS -->
> **Fig. 2**: El panel GeoArchaeo acoplado en el lado derecho de la ventana de QGIS

### Selector de idioma

Arriba a la derecha, la lista **«Idioma:»** (*Language:*) ofrece **Italiano** y **English**, los dos únicos idiomas de la interfaz de GeoArchaeo. El cambio es inmediato, sin reiniciar QGIS, y la elección se guarda en la configuración de QGIS. Mientras no se elija, el panel sigue el idioma de QGIS: italiano si QGIS está en italiano, inglés en todos los demás casos, por tanto también con QGIS en español.

---

## Interfaz de usuario

De arriba abajo, el panel contiene: la cabecera con sus botones, el grupo **«Datos de entrada (usados por todas las pestañas)»** (*Input data (used by all tabs)*), las **6 pestañas** del análisis y, durante los cálculos, la barra de progreso con el botón **«Cancelar»** (*Cancel*).

### Cabecera

| Elemento | Función |
|----------|---------|
| **«Cargar datos de ejemplo»** (*Load example data*) | Abre la lista de los conjuntos de datos de prueba incluidos en el módulo (ver la pestaña Datos) |
| **«Tutorial»** (*Tutorial*) | Abre la guía integrada de GeoArchaeo, en italiano o en inglés, que también se puede abrir en el navegador |
| **«Idioma:»** (*Language:*) | Lista Italiano / English |

### Datos de entrada

En el grupo **«Datos de entrada (usados por todas las pestañas)»** (*Input data (used by all tabs)*) se elige una sola vez:

- **«Capa de puntos:»** (*Point layer:*): una capa vectorial de puntos del proyecto
- **«Campo de valor (numérico):»** (*Value field (numeric):*): el campo que se va a analizar (la lista solo muestra campos numéricos)

Debajo aparece un resumen con los puntos válidos sobre el total, el SRC y la extensión de la capa, por ejemplo «500 puntos válidos de 500 · SRC EPSG:32633 · …» (*500 valid points of 500 · CRS EPSG:32633 · …*). Los puntos sin valor (NULL o texto no numérico) no se cuentan como válidos. El resumen avisa también cuando el proyecto no tiene capas de puntos, cuando la capa no tiene campos numéricos o cuando el SRC es geográfico (grados).

Al cambiar de capa, el panel propone además la distancia máxima del variograma y el tamaño de celda del kriging, y preselecciona la capa en la pestaña Patrones (ML) si allí todavía no hay nada seleccionado.

### Las seis pestañas

| Pestaña | Función | Resultado |
|---------|---------|-----------|
| **Datos** (*Data*) | Estadísticas descriptivas del campo | Tabla de estadísticas, histograma con diagrama de caja |
| **Variograma** (*Variogram*) | Estructura espacial de los valores | Pepita, meseta, alcance, anisotropía, gráfico |
| **Kriging** (*Kriging*) | Interpolación sobre una cuadrícula regular | Rásteres de la estimación y de la incertidumbre, validación cruzada |
| **Patrones (ML)** (*Patterns (ML)*) | Grupos y anomalías con aprendizaje automático | Capa de puntos con la etiqueta del grupo |
| **Muestreo** (*Sampling*) | Propuesta de nuevos puntos de muestreo | Capa de puntos y tabla de coordenadas |
| **Informe** (*Report*) | Recopilación de los análisis de la sesión | Archivo HTML con gráficos interactivos, o PDF |

<!-- IMAGE: Cabecera, grupo Datos de entrada y las seis pestanas de GeoArchaeo -->
> **Fig. 3**: La cabecera, el grupo «Datos de entrada» y las seis pestañas del panel GeoArchaeo

### Resultados y gráficos

Cada pestaña muestra sus resultados en un **recuadro** bajo el botón de cálculo, que sigue visible hasta que se repite el análisis, y el **gráfico** en el panel:

- si QGIS dispone de QtWebEngine, el gráfico Plotly es interactivo directamente en el panel (zoom, valores al pasar el ratón)
- si no, aparece una **vista previa estática** con la nota «Vista previa estática (QtWebEngine no disponible en esta instalación de QGIS).» (*Static preview (QtWebEngine not available in this QGIS installation).*)
- en ambos casos, el botón **«Abrir gráfico interactivo en el navegador»** (*Open interactive chart in browser*) abre la versión interactiva en el navegador web

Las pestañas Datos, Variograma y Kriging terminan con un enlace al paso siguiente, por ejemplo **«Siguiente paso: Variograma →»** (*Next step: Variogram →*).

### Análisis en curso

Variograma, kriging, reconocimiento de patrones y muestreo se calculan en un **hilo separado**: QGIS sigue siendo utilizable y en la parte inferior del panel aparecen la **barra de progreso** (en porcentaje para el kriging) y el botón **«Cancelar»** (*Cancel*). Se ejecuta un análisis cada vez: al iniciar otro aparece «Ya hay un análisis en curso: espere a que termine o cancélelo.» (*An analysis is already running: wait for it to finish or cancel it.*)

---

## Pestaña Datos

La pestaña **Datos** (*Data*, «1. Análisis exploratorio» / *1. Exploratory analysis*) describe la distribución de los valores antes de interpolarlos.

### Cálculo de las estadísticas

1. En el grupo «Datos de entrada», elegir la capa de puntos y el campo numérico
2. Abrir la pestaña **Datos**
3. Hacer clic en **«Calcular estadísticas»** (*Calculate statistics*)

<!-- IMAGE: Pestana Datos con estadisticas e histograma -->
> **Fig. 4**: La pestaña Datos con la tabla de estadísticas y el histograma del campo elegido

### Estadísticas e interpretación

| Estadística | Descripción |
|-------------|-------------|
| **Número de valores** (*Number of values*), **Valores ausentes** (*Missing values*) | Puntos con un valor válido y puntos excluidos (NULL o texto no numérico) |
| **Mínimo**, **Máximo**, **Media** (*Mean*), **Mediana** (*Median*) | Rango y posición de los valores |
| **Desv. estándar** (*Std. deviation*), **Coef. de variación** (*Coeff. of variation*) | Dispersión absoluta y relativa |
| **Primer cuartil (Q1)**, **Tercer cuartil (Q3)** (*First/Third quartile*) | Límites del 50 % central de los valores |
| **Asimetría** (*Skewness*), **Curtosis** (*Kurtosis*) | Forma de la distribución |

Bajo la tabla, el panel añade una lectura en palabras:

- asimetría mayor que 1: distribución asimétrica a la derecha (pocos valores muy altos); conviene valorar una transformación logarítmica antes del kriging, por ejemplo creando un nuevo campo con la calculadora de campos
- asimetría menor que -1: distribución asimétrica a la izquierda (pocos valores muy bajos)
- en los demás casos: distribución aproximadamente simétrica, adecuada para el kriging
- el número de posibles valores atípicos, es decir, más allá de 3 desviaciones estándar de la media

El gráfico muestra el **histograma** de los valores con un **diagrama de caja** (en la vista previa estática, solo el histograma).

### Datos de ejemplo

El botón **«Cargar datos de ejemplo»** (*Load example data*) abre la ventana «Datos de ejemplo de GeoArchaeo» (*GeoArchaeo example data*) con los conjuntos de datos de la carpeta `test_layers` del módulo; la ruta se indica en **«Carpeta:»** (*Folder:*) y se puede cambiar con **«Examinar…»** (*Browse…*). Los GeoPackage y los GeoJSON ya están marcados. Los CSV solo aparecen si no existe un GeoPackage o un GeoJSON con el mismo nombre; hay que marcarlos a mano y se cargan como texto delimitado (campos `x` e `y`, EPSG:32633). Con **OK** las capas se añaden al proyecto y la primera capa de puntos cargada se convierte en la capa de entrada del panel.

| Conjunto de datos | Puntos | Principales campos numéricos | Uso recomendado |
|-------------------|--------|------------------------------|-----------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Estadísticas, variograma, kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Los mismos que `villa_ceramica` | Prueba de todas las pestañas |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, prueba con un conjunto grande |
| `necropoli` (GeoPackage) | 120 tumbas | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN o K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging de propiedades del suelo |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Kriging de la densidad, muestreo |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variograma y kriging con pocos puntos |
| `area_studio` (GeoJSON) | 1 polígono | — | Área de estudio para el muestreo |

Entre los CSV, `magnetometria_grid` (2500 puntos, campo `mag_nT`) contiene anomalías magnéticas simuladas (dos muros, una fosa, un horno). Todos los datos son simulados y están en EPSG:32633 (UTM 33N, metros). El polígono `area_studio` cubre la zona de `ricognizione_survey`, `unita_scavo_ceramica` y `magnetometria_grid`, no la de los demás conjuntos de datos.

### Requisitos de los datos

- La capa debe ser una capa vectorial de **puntos** (en los multipuntos se usa el primer punto)
- El campo debe ser **numérico**: un campo de texto que contenga números debe convertirse con la calculadora de campos
- Los valores NULL o no numéricos se excluyen automáticamente y se cuentan como ausentes
- Se necesitan al menos **5 puntos** con un valor válido para el variograma y el kriging (1 para las estadísticas); un variograma fiable suele requerir algunas decenas de puntos
- Se recomienda un **SRC proyectado** en metros (por ejemplo UTM): con un SRC geográfico el resumen avisa y el variograma y el kriging piden confirmación

---

## Pestaña Variograma

La pestaña **Variograma** (*Variogram*, «2. Variograma» / *2. Variogram*) mide cómo crece la diferencia entre los valores con la distancia: describe la estructura espacial de los datos y guía el kriging.

### ¿Qué es un variograma?

El variograma relaciona la **semivarianza** de los pares de puntos con la **distancia** que los separa. Los parámetros del modelo son:

| Parámetro | Descripción |
|-----------|-------------|
| **Pepita** (*nugget*) | Variabilidad a distancia casi nula: error de medida y variabilidad a pequeña escala |
| **Meseta** (*sill*) | Varianza total alcanzada por el modelo (la "meseta") |
| **Alcance** (*range*) | Distancia a partir de la cual los valores dejan de estar correlacionados; en GeoArchaeo es el alcance práctico (95 % de la meseta) |

### Cálculo del variograma

1. Abrir la pestaña **Variograma**
2. En el grupo **«Parámetros»** (*Parameters*), revisar **«Distancia máxima:»** (*Maximum distance:*): el botón **«Auto»** propone aproximadamente 1/3 de la diagonal del área ocupada por los puntos (el mismo valor se propone al cambiar de capa)
3. Elegir el **«Modelo teórico:»** (*Theoretical model:*)
4. Si es necesario, marcar **«Comprobar anisotropía (variogramas direccionales)»** (*Check anisotropy (directional variograms)*)
5. Hacer clic en **«Calcular variograma»** (*Calculate variogram*)

Los pares de puntos se agrupan en **15 clases de distancia** (lags) entre cero y la distancia máxima; el número de clases no se puede cambiar desde el panel. Por encima de **3000 puntos**, el variograma se calcula sobre una submuestra aleatoria de 3000 puntos, porque el número de pares crece con el cuadrado del número de puntos. El modelo se ajusta por mínimos cuadrados ponderados por el número de pares de cada clase.

<!-- IMAGE: Pestana Variograma con parametros y resultados -->
> **Fig. 5**: La pestaña Variograma con los parámetros, el modelo teórico y el recuadro de resultados

### Modelos teóricos

| Modelo | Comportamiento | Cuándo usarlo |
|--------|----------------|---------------|
| **«Esférico (recomendado)»** (*Spherical (recommended)*) | Crece hasta el alcance y luego permanece constante | El más usado: densidades de materiales, distribuciones con límites netos |
| **«Exponencial»** (*Exponential*) | Crece rápido cerca del origen y alcanza la meseta de forma gradual | Fenómenos de decaimiento continuo, por ejemplo elementos químicos en el suelo |
| **«Gaussiano»** (*Gaussian*) | Muy regular cerca del origen | Fenómenos muy "suaves" (superficies); usar con precaución |
| **«Matérn»** (*Matérn*) | Intermedio entre exponencial y gaussiano (ν = 1,5) | Alternativa flexible |

Regla práctica: empezar con el modelo esférico y comparar el RMSE de su ajuste con el de los demás modelos. El kriging usa el **último** variograma calculado: después de las comparaciones, volver a calcular el elegido.

### Parámetros manuales

El grupo **«Parámetros manuales (opcional)»** (*Manual parameters (optional)*), desactivado por defecto, permite fijar **«Pepita:»** (*Nugget:*), **«Meseta (varianza total):»** (*Sill (total variance):*) y **«Alcance (distancia de correlación):»** (*Range (correlation distance):*). Con el grupo activo, los valores distintos de cero quedan fijos y los que se dejan en «Auto» (cero) se estiman.

### Lectura de los resultados

El recuadro de resultados indica:

- el modelo con **pepita**, **meseta**, **alcance** (en unidades del SRC) y el **RMSE** del ajuste
- el número de pares de puntos y de clases de distancia, con la submuestra usada si la hay
- una lectura del alcance: hasta esa distancia los valores están correlacionados espacialmente; más allá no se influyen
- la relación pepita/meseta: por debajo del 25 % fuerte continuidad a pequeña escala, hasta el 60 % continuidad moderada, por encima del 60 % mucha variabilidad a pequeña escala o error de medida (el kriging será poco informativo)

El gráfico muestra los puntos del variograma experimental (más grandes donde hay más pares), la curva del modelo y las líneas de pepita, meseta y alcance.

<!-- IMAGE: Variograma experimental con el modelo ajustado -->
> **Fig. 6**: Variograma experimental y modelo esférico con las líneas de pepita, meseta y alcance

### Variogramas direccionales (anisotropía)

Con **«Comprobar anisotropía (variogramas direccionales)»** marcada, GeoArchaeo calcula también los variogramas en las direcciones **0°, 45°, 90° y 135°** (ángulos medidos desde el este en sentido antihorario, tolerancia ±22,5°). Pepita y meseta son las del variograma global; para cada dirección se estima el alcance.

- Si la relación entre el alcance mayor y el menor supera **2**, el recuadro señala la anisotropía y la dirección principal (por ejemplo a lo largo de un muro, un camino o una pendiente)
- Si no, indica «Ninguna anisotropía relevante» (*No relevant anisotropy*) con la relación calculada
- Con pocos pares por dirección aparece «No hay suficientes pares para los variogramas direccionales.» (*Not enough pairs for directional variograms.*)

En el gráfico interactivo, los variogramas direccionales son entradas de la leyenda ocultas al principio: hacer clic en 0°, 45°, 90° o 135° para mostrarlos (en la vista previa estática siempre se dibujan). El kriging del panel usa el modelo omnidireccional: la anisotropía sirve para la interpretación.

---

## Pestaña Kriging

La pestaña **Kriging** (*Kriging*, «3. Kriging ordinario» / *3. Ordinary kriging*) interpola los valores sobre una cuadrícula regular usando el variograma, produce también el mapa de incertidumbre y añade los rásteres al proyecto.

### El kriging ordinario

El panel ejecuta **kriging ordinario** (media local constante pero desconocida), adecuado para la mayoría de los datos arqueológicos. Para cada celda usa los **20 puntos más cercanos**, encontrados con un KD-tree; este número no se puede cambiar desde el panel. El cokriging, el kriging espacio-temporal y el kriging por bloques para conjuntos de datos muy grandes solo existen como algoritmos de Processing del plugin GeoArchaeo independiente y no están disponibles en PyArchInit.

### Ejecución del kriging

1. Abrir la pestaña **Kriging** y leer la línea de estado del variograma (ver más abajo); el botón **«← Ir al variograma»** (*← Go to Variogram*) vuelve a la pestaña anterior
2. Ajustar **«Tamaño de celda:»** (*Cell size:*), es decir, el tamaño de una celda en unidades del SRC: el panel propone unas 100 celdas en el lado mayor de la capa y muestra debajo la cuadrícula resultante («Cuadrícula: … × … = … celdas» / *Grid: … × … = … cells*)
3. Dejar marcada **«Usar el variograma calculado»** (*Use the calculated variogram*) para usar el variograma de la pestaña anterior; si está desmarcada, el variograma se estima automáticamente
4. Dejar marcada **«Crear también el ráster de incertidumbre (desv. estándar)»** (*Also create the uncertainty raster (std. deviation)*) si se necesita el mapa de incertidumbre
5. Hacer clic en **«Ejecutar kriging»** (*Run kriging*): la barra de progreso muestra el porcentaje y **«Cancelar»** (*Cancel*) interrumpe el cálculo

La línea de estado puede indicar:

- «Variograma disponible: …, alcance … ✓» (*Variogram available: …, range … ✓*): se usa el variograma calculado con la misma capa y el mismo campo
- «Ningún variograma calculado: se estimará automáticamente (modelo esférico).» (*No variogram calculated: it will be estimated automatically (spherical model).*)
- «El variograma se calculó con otra capa/otro campo: se volverá a calcular.» (*The variogram was calculated on another layer/field: it will be recalculated.*), también en este caso con una estimación automática

> **Cuadrícula**: la cuadrícula cubre la extensión de la capa de puntos y está limitada a **500 celdas por lado**. Si el tamaño de celda elegido es demasiado fino, se aumenta automáticamente y la línea de la cuadrícula lo indica («tamaño de celda mínimo … (máx. 500 celdas por lado)» / *minimum cell size … (max 500 cells per side)*). Por encima de **40.000 celdas** la línea se vuelve naranja y, al iniciar, el panel pide confirmación porque el cálculo puede tardar algunos minutos.

<!-- IMAGE: Rasteres del kriging y metricas de validacion cruzada -->
> **Fig. 7**: Los rásteres de la estimación y de la incertidumbre en el mapa, con el recuadro de resultados y la validación cruzada

### Resultados del kriging

El kriging añade al proyecto dos rásteres GeoTIFF en el SRC de la capa de puntos:

| Capa | Contenido | Estilo |
|------|-----------|--------|
| `Kriging_<campo>` | Valor estimado en cada celda | Rampa de colores del azul al rojo pasando por el amarillo; visible |
| `Kriging_<campo>_uncertainty` | Desviación estándar de la estimación (incertidumbre) | Rampa del amarillo claro al rojo; añadida en lo alto de la lista de capas, pero oculta |

Con el panel en italiano, el segundo ráster se llama `Kriging_<campo>_incertezza`. Los archivos se escriben en una **carpeta temporal**: para conservarlos, exportarlos desde el menú contextual de la capa (**Exportar**).

El recuadro de resultados resume los puntos usados, el tamaño de la cuadrícula, el tamaño de celda, el modelo y el alcance; el gráfico muestra el mapa de los valores estimados y el de la incertidumbre, con los puntos de muestra superpuestos.

### Validación cruzada leave-one-out

Tras el kriging, GeoArchaeo realiza una **validación cruzada leave-one-out**: cada punto se elimina y se vuelve a estimar a partir de los demás (sobre un máximo de 200 puntos elegidos al azar en los conjuntos grandes). Las métricas aparecen en el recuadro de resultados:

| Métrica | Significado | Valor deseable |
|---------|-------------|----------------|
| **RMSE** (*root mean squared error*) | Error típico de la estimación | El más bajo posible, comparado con la desviación estándar de los datos |
| **MAE** (*mean absolute error*) | Error medio en valor absoluto | El más bajo posible |
| **ME** (*mean error, bias*) | Sobreestimación o subestimación sistemática | Cercano a 0 |
| **R²** (*explained variance*) | Capacidad predictiva | Desde 0,5 buena, por debajo de 0,2 baja |
| **MSDR** (*standardized error*) | Realismo de la incertidumbre estimada | Alrededor de 1; por encima de 1,5 incertidumbre subestimada, por debajo de 0,5 sobreestimada |

El panel añade un juicio en palabras sobre la capacidad predictiva (buena, moderada o baja) y, cuando procede, sobre el MSDR.

> **Nota**: el kriging se ejecuta en un **hilo en segundo plano**, por lo que la interfaz de QGIS sigue siendo utilizable durante el cálculo; la barra de progreso indica el estado del procesamiento.

---

## Pestaña Patrones (ML)

La pestaña **Patrones (ML)** (*Patterns (ML)*, «4. Reconocimiento de patrones (aprendizaje automático)» / *4. Pattern recognition (machine learning)*) agrupa los puntos por posición y atributos numéricos, o detecta anomalías, y crea una capa con la etiqueta de cada punto.

### Métodos disponibles

| Método (entrada de la lista) | Qué hace | Parámetros |
|------------------------------|----------|------------|
| **«K-Means – grupos por similitud»** (*K-Means – groups by similarity*) | Divide los puntos en K grupos similares por posición y atributos | **«Número de grupos (0 = automático):»** (*Number of groups (0 = automatic):*); con 0 el número se elige según la cantidad de puntos (de 2 a 5) |
| **«DBSCAN – grupos por densidad (también encuentra puntos aislados)»** (*DBSCAN – groups by density (also finds isolated points)*) | Encuentra grupos por densidad sin fijar su número; los puntos aislados forman el grupo «Aislados / ruido» (*Isolated / noise*) | Automáticos |
| **«Isolation Forest – detección de anomalías»** (*Isolation Forest – anomaly detection*) | Señala como «Anomalía» (*Anomaly*) aproximadamente el 10 % de los puntos más distintos de los demás; el resto son «Normal» (*Normal*) | Automáticos |

### Ejecución

1. Abrir la pestaña **Patrones (ML)**
2. En la lista **«Capas de puntos a analizar (una o varias):»** (*Point layers to analyse (one or more):*), seleccionar una o varias capas de puntos (si no hay nada seleccionado, se preselecciona la capa de entrada)
3. Elegir el **«Método:»** (*Method:*)
4. Solo para K-Means, ajustar **«Número de grupos (0 = automático):»**
5. Hacer clic en **«Iniciar reconocimiento de patrones»** (*Run pattern recognition*)

Las variables analizadas son las **coordenadas X e Y** y **todos los campos numéricos** de las capas seleccionadas, estandarizados; los valores ausentes se sustituyen por la media del campo. Por tanto, no se usa solo el campo de valor elegido arriba: entran todos los campos numéricos, incluidos identificadores y números correlativos, y si distorsionan los grupos conviene analizar una copia de la capa con solo los campos útiles. Si se analizan varias capas juntas, conviene que tengan los mismos campos numéricos en el mismo orden y el mismo SRC (la capa creada usa el SRC de la primera capa seleccionada).

<!-- IMAGE: Pestana Patrones (ML) con la capa de grupos -->
> **Fig. 8**: La pestaña Patrones (ML) con el gráfico de los grupos y la capa `ML_groups` en el mapa

### Resultados

- El recuadro de resultados indica el método, el número de grupos y cuántos puntos caen en cada uno (por ejemplo «Grupo A (n=42)» / *Group A (n=42)*)
- El gráfico muestra los puntos en el plano de las dos primeras componentes principales (PC1, PC2) de las variables, coloreados por grupo
- Se crea una capa de puntos temporal, `ML_groups` (K-Means, DBSCAN) o `ML_anomalies` (Isolation Forest), con una leyenda por categorías: gris para los puntos aislados, rojo y más grande para las anomalías; con el panel en italiano los nombres son `Gruppi_ML` y `Anomalie_ML`

| Campo | Contenido |
|-------|-----------|
| `cluster_id` | Número del grupo (-1 = aislados con DBSCAN; 1 = anomalía y 0 = normal con Isolation Forest) |
| `cluster_name` | Nombre legible, por ejemplo «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Número de puntos del grupo |
| `method` | Método usado |
| `x_coord`, `y_coord` | Coordenadas del punto |

### Clasificación supervisada

Bajo el método, el panel recuerda que la clasificación supervisada (Random Forest con un campo de etiquetas) se encuentra en **Processing → GeoArchaeo**. Ese algoritmo pertenece al plugin GeoArchaeo independiente: en PyArchInit el proveedor de Processing de GeoArchaeo no se registra, así que Random Forest no está disponible. Para usarlo se necesita el plugin GeoArchaeo separado.

---

## Pestaña Muestreo

La pestaña **Muestreo** (*Sampling*, «5. Nuevos puntos de muestreo» / *5. New sampling locations*) sugiere dónde muestrear o excavar en el futuro a partir de los puntos existentes y crea una capa con los puntos propuestos.

### Criterios de muestreo

| Criterio (entrada de la lista) | Cómo elige los puntos | Cuándo usarlo |
|--------------------------------|-----------------------|---------------|
| **«Cobertura (maximin)»** (*Coverage (maximin)*) | Cada nuevo punto está lo más lejos posible de todos los demás | Rellenar los vacíos de forma uniforme |
| **«Reducción de la incertidumbre (varianza de kriging)»** (*Uncertainty reduction (kriging variance)*) | Cada nuevo punto va donde la varianza de kriging es máxima | Reducir el error del kriging donde es mayor |
| **«Cuadrícula estratificada»** (*Stratified grid*) | Una posición por celda de una cuadrícula regular, con una ligera perturbación aleatoria | Cobertura regular de un área definida |
| **«Adaptativo (zonas menos densas)»** (*Adaptive (sparser areas)*) | Extracción aleatoria con mayor probabilidad donde hay pocos puntos | Favorecer las zonas menos muestreadas manteniendo un componente aleatorio |

El criterio «Reducción de la incertidumbre» usa el variograma calculado si corresponde a la misma capa y al mismo campo y si en la pestaña Kriging está marcada «Usar el variograma calculado»; si no, usa un modelo genérico basado en la distancia típica entre los puntos.

### Diseño del muestreo

1. Comprobar **«Puntos existentes:»** (*Existing points:*): es la capa elegida arriba en el grupo «Datos de entrada» (para el muestreo no hace falta el campo numérico)
2. Opcional: elegir en **«Área de estudio (polígono, opcional):»** (*Study area (polygon, optional):*) una capa de polígonos; todos sus polígonos se unen y se reproyectan al SRC de los puntos, aunque la capa esté en otro SRC
3. Ajustar **«Nuevos puntos a proponer:»** (*New points to propose:*) (de 1 a 500, 10 por defecto)
4. Elegir el **«Criterio:»** (*Criterion:*): bajo la lista aparece su descripción
5. Hacer clic en **«Calcular nuevos puntos»** (*Calculate new points*)

Sin área de estudio, los puntos se buscan en el rectángulo que contiene los puntos existentes, ampliado un 20 % por cada lado.

<!-- IMAGE: Nuevos puntos de muestreo propuestos -->
> **Fig. 9**: Los nuevos puntos de muestreo (estrellas amarillas) propuestos dentro del área de estudio

### Resultados del muestreo

- El recuadro de resultados indica cuántos puntos se han propuesto y con qué criterio; debajo, la tabla «Coordenadas de los puntos propuestos:» (*Coordinates of the proposed points:*) enumera número, X e Y
- Se crea la capa de puntos temporal `New_sampling_points` (`Nuovi_punti_campionamento` con el panel en italiano), con símbolo de estrella amarilla y los campos `point_id`, `x_coord`, `y_coord` y `type` (valor `suggested`)

---

## Pestaña Informe

La pestaña **Informe** (*Report*, «6. Informe» / *6. Report*) reúne en un único documento los análisis realizados en la sesión: estadísticas, gráficos interactivos, parámetros y validación.

### Contenido del informe

En el grupo **«Secciones a incluir»** (*Sections to include*), cada sección se marca como «disponible» (*available*) o «aún no calculado» (*not yet calculated*); las secciones no calculadas no se pueden elegir.

| Sección | Contenido |
|---------|-----------|
| **Estadísticas descriptivas** (*Descriptive statistics*) | Capa y campo, tabla de estadísticas con la lectura en palabras, histograma |
| **Variograma** (*Variogram*) | Modelo, pepita, meseta, alcance, RMSE, distancia máxima, interpretación, gráfico |
| **Kriging y validación cruzada** (*Kriging and cross-validation*) | Método, tamaño de celda, dimensiones de la cuadrícula, métricas de validación cruzada, gráfico |
| **Reconocimiento de patrones** (*Pattern recognition*) | Capas analizadas, grupos con su número de puntos, gráfico |
| **Nuevos puntos de muestreo** (*New sampling locations*) | Criterio, capa, tabla de coordenadas |

Cada sección contiene el **último** análisis de su tipo realizado en la sesión.

### Generación del informe

1. Realizar los análisis deseados en las otras pestañas
2. Abrir la pestaña **Informe** y dejar marcadas las secciones que se quieren incluir (están marcadas por defecto)
3. Hacer clic en **«Guardar informe HTML»** (*Save HTML report*) o en **«Guardar informe PDF»** (*Save PDF report*) y elegir el nombre del archivo

Al guardar, el panel muestra también una vista previa del informe sin gráficos; la nota «Vista previa: los gráficos interactivos están incluidos en el archivo HTML guardado.» (*Preview: the interactive charts are included in the saved HTML file.*) recuerda dónde están.

<!-- IMAGE: Informe HTML de GeoArchaeo abierto en el navegador -->
> **Fig. 10**: Un informe HTML de GeoArchaeo con gráficos interactivos, abierto en el navegador

### Exportación

| Formato | Contenido | Notas |
|---------|-----------|-------|
| **HTML** (`geoarchaeo_report.html`) | Texto, tablas y **gráficos interactivos** | El archivo es autónomo (la biblioteca de gráficos va incluida, funciona también sin conexión) y se abre enseguida en el navegador |
| **PDF** (`geoarchaeo_report.pdf`) | Texto y tablas, **sin gráficos** | Si el PDF no se puede crear, guardar el informe HTML e imprimirlo en PDF desde el navegador |

Si no se ha realizado ningún análisis aparece «Ningún análisis disponible: ejecute primero al menos un análisis.» (*No analysis available: run at least one analysis first.*); si no hay ninguna sección marcada, «Seleccione al menos una sección» (*Select at least one section*).

---

## Flujo de trabajo operativo

Un ejemplo completo con los datos de ejemplo incluidos en el módulo (panel en inglés).

### Paso 1: Preparación de los datos

1. Abrir GeoArchaeo desde la barra de herramientas de PyArchInit
2. Hacer clic en **«Cargar datos de ejemplo»** (*Load example data*) y confirmar con **OK** (se cargan los GeoPackage y los GeoJSON)
3. En el grupo «Datos de entrada», elegir la capa `villa_ceramica` y el campo `ceramic_count`
4. Comprobar el resumen: 500 puntos válidos de 500, SRC EPSG:32633

### Paso 2: Exploración de los datos

1. Pestaña **Datos** → **«Calcular estadísticas»** (*Calculate statistics*)
2. Leer la asimetría y los valores atípicos; con una fuerte asimetría a la derecha, valorar una transformación logarítmica

### Paso 3: Análisis del variograma

1. Pestaña **Variograma** → **«Auto»** para la distancia máxima, modelo **«Esférico (recomendado)»** (*Spherical (recommended)*) → **«Calcular variograma»** (*Calculate variogram*)
2. Repetir con **«Exponencial»** (*Exponential*) y comparar el RMSE del ajuste
3. Opcional: volver a calcular con **«Comprobar anisotropía (variogramas direccionales)»**
4. Calcular en último lugar el modelo elegido y anotar pepita, meseta y alcance

### Paso 4: Interpolación

1. Pestaña **Kriging**: comprobar la línea «Variograma disponible … ✓» (*Variogram available … ✓*)
2. Mantener el tamaño de celda propuesto o indicar 1 (metro)
3. **«Ejecutar kriging»** (*Run kriging*)
4. Examinar los rásteres `Kriging_ceramic_count` y `Kriging_ceramic_count_uncertainty` y los valores de R² y MSDR

### Paso 5: Patrones y muestreo (opcionales)

1. Pestaña **Patrones (ML)**: dejar seleccionada en la lista solo `necropoli`, método DBSCAN → **«Iniciar reconocimiento de patrones»** (*Run pattern recognition*); la capa `ML_groups` muestra los grupos de tumbas y los puntos aislados
2. Arriba, elegir la capa `ricognizione_survey` (campo `densita_mq`); pestaña **Muestreo**: área de estudio `area_studio`, 10 puntos, criterio «Cobertura (maximin)» (*Coverage (maximin)*) → **«Calcular nuevos puntos»** (*Calculate new points*)

### Paso 6: Informe

1. Pestaña **Informe**: dejar marcadas las secciones disponibles
2. **«Guardar informe HTML»** (*Save HTML report*): el informe se abre en el navegador con los gráficos interactivos
3. Exportar los rásteres y las capas temporales que se quieran conservar

---

## Solución de problemas

### Problemas comunes

| Problema | Causa | Solución |
|----------|-------|----------|
| «No hay ninguna capa de puntos en el proyecto…» (*No point layer in the project: load one or use the example data.*) | El proyecto no tiene capas de puntos | Añadir una capa de puntos o usar **«Cargar datos de ejemplo»** |
| «La capa no tiene campos numéricos…» (*The layer has no numeric fields…*) | El campo que se va a analizar es de texto | Convertirlo en número con la calculadora de campos |
| «Se necesitan al menos 5 puntos con un valor válido…» (*At least 5 points with a valid value are required (found …)*) | Demasiados valores NULL o no numéricos | Revisar la tabla de atributos o elegir otro campo |
| Aviso «SRC geográfico (grados)» (*geographic CRS (degrees)*) | La capa no está en un SRC proyectado | Reproyectar la capa, por ejemplo a UTM, y repetir el análisis |
| Error «No point pairs within the maximum distance…» | Distancia máxima del variograma demasiado pequeña | Aumentar **«Distancia máxima:»** o usar **«Auto»** |
| «No hay suficientes pares para los variogramas direccionales.» (*Not enough pairs for directional variograms.*) | Muy pocos pares por dirección | Aumentar la distancia máxima o renunciar a la comprobación de la anisotropía |
| Kriging lento, petición de confirmación o «Memoria insuficiente: aumente el tamaño de celda.» (*Out of memory: increase the cell size.*) | Cuadrícula con demasiadas celdas | Aumentar **«Tamaño de celda:»** |
| R² bajo en la validación cruzada | Poca correlación espacial o demasiado ruido | Considerar el mapa solo orientativo y consultar el ráster de incertidumbre |
| DBSCAN pone casi todos los puntos en «Aislados / ruido» (*Isolated / noise*) | Densidad uniforme o demasiadas variables | Probar K-Means o reducir los campos numéricos |
| «Machine Learning features not available. Please install scikit-learn.» | Falta scikit-learn | Instalar scikit-learn en el entorno Python de QGIS |
| «Plotly visualization not available. Please install plotly.» | Falta Plotly | Instalar plotly en el entorno Python de QGIS |
| Gráfico solo como imagen estática | QtWebEngine no disponible | Usar **«Abrir gráfico interactivo en el navegador»** (*Open interactive chart in browser*) |
| «No se puede crear el PDF…» (*Cannot create the PDF…*) | Error al imprimir el PDF | Guardar el informe HTML e imprimirlo desde el navegador |
| Panel no visible | Panel cerrado | Volver a abrirlo desde la barra de herramientas o el menú pyArchInit: los resultados de la sesión siguen ahí |

### Errores frecuentes

- **«Ya hay un análisis en curso…»** (*An analysis is already running: wait for it to finish or cancel it.*): esperar a que termine el cálculo o pulsar «Cancelar»
- **«Análisis cancelado»** (*Analysis cancelled*): el análisis se interrumpió con «Cancelar» y no produjo resultados
- **«Seleccione al menos una capa»** (*Select at least one layer*, pestaña Patrones): seleccionar al menos una capa en la lista
- **«Seleccione la capa de los puntos existentes (arriba)»** (*Select the existing points layer (above)*, pestaña Muestreo): elegir la capa en el grupo «Datos de entrada»
- **«Seleccione una capa de puntos y un campo numérico (en la parte superior del panel)»** (*Select a point layer and a numeric field (at the top of the panel)*): completar la elección en el grupo «Datos de entrada»

### Rendimiento

- Los análisis se ejecutan en un **hilo en segundo plano**: QGIS sigue siendo utilizable y el cálculo se puede cancelar
- El variograma usa como máximo 3000 puntos (submuestra aleatoria) y la validación cruzada como máximo 200
- El kriging usa los 20 puntos más cercanos a cada celda: el tiempo depende sobre todo del número de celdas
- La cuadrícula está limitada a 500 × 500 celdas; por encima de 40.000 celdas el panel pide confirmación
- Con conjuntos de datos grandes (por ejemplo los 4800 puntos de `geofisica_survey`), aumentar el tamaño de celda

---

## Notas técnicas

### Versión y origen

- El módulo `modules/geoarchaeo/` está alineado con **GeoArchaeo 1.3.1**, el plugin independiente de Enzo Cocca (github.com/enzococca/GeoArchaeo)
- En PyArchInit solo está integrado el panel: el proveedor de Processing de GeoArchaeo (cokriging, kriging espacio-temporal, kriging por bloques, análisis composicional, Random Forest) **no** se registra
- El módulo es compatible con QGIS 3 (Qt5) y QGIS 4 (Qt6)

### Dependencias

| Biblioteca | Uso |
|------------|-----|
| **NumPy** | Cálculos numéricos |
| **SciPy** | Ajuste de los modelos de variograma, búsqueda de vecinos (KD-tree), estadísticas |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, componentes principales (necesaria para la pestaña Patrones) |
| **Plotly** | Gráficos interactivos en el panel y en el informe HTML |
| **Matplotlib** | Vistas previas estáticas de los gráficos cuando falta QtWebEngine |
| **QtWebEngine** (opcional) | Gráficos interactivos directamente en el panel |
| **threadpoolctl** (opcional) | Limita los hilos de cálculo durante los análisis en segundo plano |
| **GDAL** | Escritura de los rásteres GeoTIFF (incluido en QGIS) |

### Sistemas de referencia

- Las distancias (distancia máxima, alcance, tamaño de celda) se expresan en las **unidades del SRC de la capa de puntos**
- Usar un **SRC proyectado** en metros: con un SRC geográfico el resumen avisa y el variograma y el kriging piden confirmación
- Los rásteres del kriging y las capas creadas usan el SRC de la capa de puntos (en la pestaña Patrones, el de la primera capa seleccionada)
- El área de estudio se reproyecta automáticamente al SRC de los puntos

### Capas y archivos generados

| Producto | Tipo | Ubicación |
|----------|------|-----------|
| `Kriging_<campo>`, `Kriging_<campo>_uncertainty` | Ráster GeoTIFF (compresión LZW) | Carpeta temporal del sistema |
| `ML_groups` / `ML_anomalies` | Capa de puntos temporal (en memoria) | Solo en el proyecto abierto |
| `New_sampling_points` | Capa de puntos temporal (en memoria) | Solo en el proyecto abierto |
| Informe | HTML o PDF | Ruta elegida al guardar |

Los rásteres y las capas temporales deben exportarse (menú contextual de la capa → **Exportar**) para no perderlos al cerrar el proyecto. Los nombres de las capas siguen el idioma del panel en el momento del cálculo.

### Configuración

- El idioma del panel se guarda en la configuración de QGIS (clave `GeoArchaeo/language`)
- Los resultados permanecen en memoria mientras QGIS esté abierto: cerrar el panel no los borra

---

> **Nota**: GeoArchaeo está en desarrollo continuo. Para informar de errores o sugerir mejoras, utilizar el sistema de seguimiento de incidencias (issues) del proyecto PyArchInit en GitHub.
