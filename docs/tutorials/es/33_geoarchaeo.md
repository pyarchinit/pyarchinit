# PyArchInit - GeoArchaeo - Analisis Geoestadistico

## Indice
1. [Introduccion](#introduccion)
2. [Acceso a la herramienta](#acceso-a-la-herramienta)
3. [Interfaz de usuario](#interfaz-de-usuario)
4. [Pestana Datos](#pestana-datos)
5. [Pestana Variograma](#pestana-variograma)
6. [Pestana Kriging](#pestana-kriging)
7. [Pestana Machine Learning](#pestana-machine-learning)
8. [Pestana Muestreo](#pestana-muestreo)
9. [Pestana Informe](#pestana-informe)
10. [Flujo de trabajo operativo](#flujo-de-trabajo-operativo)
11. [Solucion de problemas](#solucion-de-problemas)
12. [Notas tecnicas](#notas-tecnicas)

---

## Introduccion

**GeoArchaeo** es el modulo de analisis geoestadistico integrado en PyArchInit. Proporciona un conjunto completo de herramientas para el analisis espacial de datos arqueologicos, desde la modelizacion de variogramas hasta la interpolacion kriging, pasando por predicciones con aprendizaje automatico y el diseno de estrategias de muestreo.

<!-- VIDEO: Introduccion a GeoArchaeo -->
> **Video Tutorial**: [Insertar enlace de video introduccion GeoArchaeo]

### Por que el analisis geoestadistico en arqueologia?

El analisis geoestadistico permite:

- **Interpolar** valores entre puntos de muestreo conocidos, creando superficies continuas a partir de datos discretos
- **Cuantificar** la correlacion espacial en los datos arqueologicos (ej. densidad de hallazgos, espesor de estratos)
- **Predecir** distribuciones espaciales en areas aun no excavadas
- **Optimizar** estrategias de muestreo para prospecciones futuras
- **Generar** informes analiticos completos para la documentacion cientifica

### Vision general del flujo de trabajo

```
1. Cargar datos         2. Variograma          3. Kriging/ML
   (Pestana Datos)         (Pestana Variograma)   (Pestana Kriging/ML)
        |                      |                      |
   Seleccionar capa       Calcular y modelar     Interpolacion o
   y campos               variograma             prediccion espacial
                               |                      |
                          4. Muestreo            5. Informe
                             (Pestana Muestreo)     (Pestana Informe)
                                  |                      |
                             Disenar              Generar informe
                             estrategia           de analisis
```

---

## Acceso a la herramienta

GeoArchaeo es accesible desde la barra de herramientas de PyArchInit a traves del boton desplegable de Herramientas de Analisis.

### Desde la barra de herramientas

1. Localizar el boton **Herramientas de Analisis** (icono desplegable) en la barra de herramientas de PyArchInit
2. Hacer clic en la flecha del menu desplegable
3. Seleccionar **GeoArchaeo** de la lista

<!-- IMAGE: Boton Herramientas de Analisis en la barra de herramientas -->
> **Fig. 1**: El menu desplegable Herramientas de Analisis en la barra de herramientas de PyArchInit

El panel GeoArchaeo aparece como un **widget acoplable** en la interfaz de QGIS. Se puede arrastrar, redimensionar o desacoplar como cualquier otro panel de QGIS.

<!-- IMAGE: Panel GeoArchaeo acoplado en QGIS -->
> **Fig. 2**: El panel GeoArchaeo acoplado en la ventana de QGIS

### Selector de idioma

El panel GeoArchaeo incluye un **selector de idioma** en la parte superior, que permite cambiar el idioma de la interfaz sin reiniciar QGIS. Los idiomas soportados incluyen italiano, ingles, aleman, frances, espanol, arabe, catalan, rumano, portugues y griego.

---

## Interfaz de usuario

El panel GeoArchaeo esta organizado en **6 pestanas principales**, cada una dedicada a una fase del flujo de trabajo de analisis geoestadistico.

| Pestana | Icono | Funcion |
|---------|-------|---------|
| **Datos** | Tabla | Cargar y explorar datos espaciales desde capas QGIS |
| **Variograma** | Grafico | Calcular y modelar variogramas experimentales |
| **Kriging** | Cuadricula | Realizar interpolacion kriging (ordinario, universal) |
| **ML** | Cerebro | Predicciones espaciales con aprendizaje automatico |
| **Muestreo** | Diana | Disenar estrategias de muestreo para prospecciones arqueologicas |
| **Informe** | Documento | Generar informes de analisis |

<!-- IMAGE: Vision general de las 6 pestanas de GeoArchaeo -->
> **Fig. 3**: Las seis pestanas del panel GeoArchaeo

### Barra de herramientas del panel

En la parte superior del panel se encuentran:

- **Selector de idioma**: Menu desplegable para cambiar el idioma de la interfaz
- **Cargar datos de ejemplo**: Boton para cargar un conjunto de datos de prueba
- **Ayuda**: Boton para acceder a la documentacion

---

## Pestana Datos

La pestana **Datos** es el punto de partida para cualquier analisis geoestadistico. Permite cargar y visualizar los datos espaciales disponibles en las capas QGIS.

### Carga de datos

1. Abrir la pestana **Datos**
2. Seleccionar una **capa vectorial** del menu desplegable (se listan todas las capas de puntos del proyecto QGIS)
3. Seleccionar el **campo de analisis** (el campo numerico a analizar)
4. Hacer clic en **Cargar datos**

<!-- IMAGE: Pestana Datos con capa y campo seleccionados -->
> **Fig. 4**: La pestana Datos con una capa y un campo de analisis seleccionados

### Datos de ejemplo

Para familiarizarse con la herramienta, es posible cargar un **conjunto de datos de ejemplo** haciendo clic en el boton dedicado. El conjunto de datos de ejemplo contiene datos arqueologicos simulados con coordenadas y valores numericos adecuados para el analisis geoestadistico.

### Exploracion de datos

Despues de la carga, la pestana muestra:

| Informacion | Descripcion |
|-------------|-------------|
| **Numero de puntos** | Total de puntos cargados |
| **Extension** | Caja envolvente del conjunto de datos (xmin, ymin, xmax, ymax) |
| **Estadisticas** | Media, mediana, desviacion estandar, min, max |
| **Vista previa** | Tabla con las primeras filas del conjunto de datos |

### Requisitos de los datos

- La capa debe ser una **capa vectorial de puntos**
- El campo de analisis debe contener **valores numericos**
- Los puntos deben tener **coordenadas validas** en el sistema de referencia del proyecto
- Se recomiendan al menos **30 puntos** para un analisis geoestadistico significativo

---

## Pestana Variograma

La pestana **Variograma** permite calcular y modelar variogramas experimentales, que describen la estructura de la correlacion espacial en los datos.

### Que es un variograma?

Un variograma es un grafico que muestra como la **varianza** entre pares de puntos cambia en funcion de la **distancia** que los separa. Los parametros clave son:

| Parametro | Descripcion |
|-----------|-------------|
| **Nugget** | Varianza a distancia cero (error de medicion + variabilidad a microescala) |
| **Sill** | Varianza maxima alcanzada (meseta del variograma) |
| **Rango (Range)** | Distancia mas alla de la cual no hay correlacion espacial |

### Calculo del variograma experimental

1. Asegurarse de haber cargado datos en la pestana Datos
2. Abrir la pestana **Variograma**
3. Configurar los parametros:
   - **Numero de lags**: Numero de intervalos de distancia (por defecto: 15)
   - **Distancia maxima**: Distancia maxima a considerar (por defecto: auto)
   - **Tolerancia angular**: Para variogramas direccionales (por defecto: omnidireccional)
4. Hacer clic en **Calcular variograma**

<!-- IMAGE: Variograma experimental calculado -->
> **Fig. 5**: Un variograma experimental calculado a partir de datos arqueologicos

### Modelizacion del variograma

Tras calcular el variograma experimental, es posible ajustar un **modelo teorico**:

1. Seleccionar el **tipo de modelo**:
   - **Esferico**: El modelo mas comun, alcanza el sill a una distancia finita
   - **Exponencial**: Alcanza el sill asintoticamente
   - **Gaussiano**: Transicion gradual, adecuado para fenomenos muy regulares
   - **Lineal**: Variograma sin sill definido
2. Hacer clic en **Ajustar modelo**
3. Verificar los parametros estimados (nugget, sill, rango) y la bondad de ajuste

<!-- IMAGE: Modelo de variograma ajustado -->
> **Fig. 6**: Modelo esferico ajustado al variograma experimental

### Variogramas direccionales

Para verificar la **anisotropia** (variacion de la estructura espacial en diferentes direcciones):

1. Establecer una **tolerancia angular** (ej. 22,5 grados)
2. Seleccionar las **direcciones** a analizar (0, 45, 90, 135 grados)
3. Comparar los variogramas en las diferentes direcciones

---

## Pestana Kriging

La pestana **Kriging** permite realizar la interpolacion kriging, el metodo geoestadistico de referencia para la prediccion espacial optima.

### Tipos de kriging disponibles

| Tipo | Descripcion | Cuando usarlo |
|------|-------------|---------------|
| **Kriging ordinario** | Asume una media local constante pero desconocida | Caso mas comun, datos estacionarios |
| **Kriging universal** | Tiene en cuenta una tendencia espacial (deriva) | Cuando los datos muestran una tendencia direccional |

### Ejecucion del kriging

1. Asegurarse de haber modelado el variograma en la pestana Variograma
2. Abrir la pestana **Kriging**
3. Seleccionar el **tipo de kriging** (ordinario o universal)
4. Configurar los parametros de la cuadricula de salida:
   - **Resolucion**: Tamano de las celdas de la cuadricula (en unidades del CRS)
   - **Extension**: Automatica desde el conjunto de datos o personalizada
5. Configurar los parametros del kriging:
   - **Puntos minimos**: Numero minimo de puntos cercanos a usar
   - **Puntos maximos**: Numero maximo de puntos cercanos a usar
   - **Radio de busqueda**: Distancia maxima para los puntos cercanos
6. Hacer clic en **Ejecutar kriging**

<!-- IMAGE: Resultado de la interpolacion kriging -->
> **Fig. 7**: Mapa de interpolacion kriging con la cuadricula de prediccion

### Resultados del kriging

El analisis produce dos capas raster:

- **Prediccion**: Los valores interpolados en la cuadricula
- **Varianza de kriging**: La incertidumbre de la prediccion en cada celda

Las capas se anaden automaticamente al proyecto QGIS y se muestran en el mapa.

> **Nota**: El analisis se ejecuta en un **hilo en segundo plano**, por lo que la interfaz de QGIS permanece utilizable durante el calculo. Una barra de progreso indica el estado del procesamiento.

---

## Pestana Machine Learning

La pestana **ML** ofrece metodos de aprendizaje automatico para predicciones espaciales, como alternativa o complemento al kriging.

### Algoritmos disponibles

| Algoritmo | Descripcion | Ventajas |
|-----------|-------------|----------|
| **Random Forest** | Conjunto de arboles de decision | Robusto, maneja relaciones no lineales |
| **Gradient Boosting** | Arboles de decision secuenciales | Alta precision, adecuado para patrones complejos |
| **SVR** | Regresion por vectores de soporte | Bueno con pocos datos, kernels flexibles |

### Flujo de trabajo ML

1. Abrir la pestana **ML**
2. Seleccionar el **algoritmo** deseado
3. Configurar las **variables predictoras**:
   - Coordenadas (X, Y)
   - Campos adicionales de la capa (ej. elevacion, pendiente, distancia a un rio)
4. Establecer los **parametros** del algoritmo (o usar los valores por defecto)
5. Seleccionar el metodo de **validacion**:
   - Validacion cruzada k-fold (por defecto: 5 folds)
   - Hold-out (porcentaje de prueba)
6. Hacer clic en **Entrenar modelo**

<!-- IMAGE: Configuracion del modelo ML -->
> **Fig. 8**: Configuracion de un modelo Random Forest en la pestana ML

### Resultados ML

| Resultado | Descripcion |
|-----------|-------------|
| **Mapa de prediccion** | Capa raster con los valores predichos |
| **Importancia de variables** | Grafico de la importancia relativa de las variables predictoras |
| **Metricas de validacion** | R-cuadrado, RMSE, MAE de la validacion cruzada |
| **Grafico de residuos** | Diagrama de dispersion de valores observados vs predichos |

### Comparacion Kriging vs ML

Para comparar resultados:

1. Ejecutar tanto el kriging como el ML con los mismos datos
2. Comparar las metricas de validacion en la pestana Informe
3. Visualizar mapas de diferencias

---

## Pestana Muestreo

La pestana **Muestreo** permite disenar estrategias de muestreo optimas para prospecciones arqueologicas futuras.

### Estrategias de muestreo

| Estrategia | Descripcion | Cuando usarla |
|------------|-------------|---------------|
| **Aleatorio simple** | Puntos distribuidos aleatoriamente en el area | Cuando no se tiene informacion previa |
| **Aleatorio estratificado** | Puntos aleatorios dentro de estratos definidos | Cuando el area tiene zonas con diferentes caracteristicas |
| **Cuadricula regular** | Puntos en una cuadricula regular | Para cobertura uniforme del area |
| **Optimizado** | Puntos posicionados para minimizar la varianza de kriging | Cuando se dispone de un variograma |

### Diseno del plan de muestreo

1. Abrir la pestana **Muestreo**
2. Seleccionar la **estrategia** de muestreo
3. Establecer el **numero de puntos** deseado
4. Definir el **area de estudio**:
   - Desde la extension de la capa actual
   - Desde una capa poligonal
   - Dibujando manualmente sobre el mapa
5. Establecer posibles **restricciones**:
   - Distancia minima entre puntos
   - Areas de exclusion
6. Hacer clic en **Generar muestreo**

<!-- IMAGE: Puntos de muestreo generados -->
> **Fig. 9**: Puntos de muestreo optimizado superpuestos al mapa del area de estudio

### Resultados del muestreo

- Una **capa vectorial de puntos** con los puntos de muestreo se anade al proyecto QGIS
- Una **tabla de atributos** con las coordenadas e identificadores de los puntos
- Un **informe** con las estadisticas de la estrategia (cobertura, distancias, etc.)

---

## Pestana Informe

La pestana **Informe** permite generar informes completos del analisis geoestadistico.

### Contenido del informe

El informe incluye automaticamente todos los analisis realizados durante la sesion:

| Seccion | Contenido |
|---------|-----------|
| **Resumen** | Vision general del conjunto de datos y los analisis realizados |
| **Datos** | Estadisticas descriptivas, distribucion, mapa de puntos |
| **Variograma** | Variograma experimental, modelo, parametros |
| **Interpolacion** | Mapa de kriging/ML, metricas de validacion |
| **Muestreo** | Estrategia, mapa de puntos, estadisticas |
| **Conclusiones** | Interpretacion sintetica de los resultados |

### Generacion del informe

1. Abrir la pestana **Informe**
2. Seleccionar las **secciones** a incluir (todas por defecto)
3. Establecer el **formato de salida**:
   - PDF (recomendado para documentacion)
   - HTML (para consulta interactiva)
   - Markdown (para edicion posterior)
4. Introducir posibles **notas adicionales** o comentarios
5. Hacer clic en **Generar informe**

<!-- IMAGE: Vista previa del informe generado -->
> **Fig. 10**: Vista previa de un informe de analisis geoestadistico generado por GeoArchaeo

### Exportacion

El informe puede guardarse localmente o exportarse en los formatos disponibles. Las imagenes (graficos, mapas) se incorporan directamente en el informe.

---

## Flujo de trabajo operativo

A continuacion se presenta un flujo de trabajo tipico para un analisis geoestadistico completo en GeoArchaeo:

### Paso 1: Preparacion de datos

1. Cargar la capa vectorial de puntos en QGIS
2. Verificar que el campo numerico a analizar esta presente y es correcto
3. Comprobar el sistema de referencia de coordenadas

### Paso 2: Exploracion de datos

1. Abrir GeoArchaeo desde la barra de herramientas
2. En la pestana **Datos**, seleccionar la capa y el campo
3. Examinar las estadisticas descriptivas
4. Verificar la distribucion de los datos (buscar valores atipicos o anomalos)

### Paso 3: Analisis del variograma

1. En la pestana **Variograma**, calcular el variograma experimental
2. Probar diferentes modelos (esferico, exponencial, gaussiano)
3. Elegir el modelo con el mejor ajuste
4. Anotar los parametros (nugget, sill, rango)

### Paso 4: Interpolacion

1. En la pestana **Kriging**, configurar los parametros de la cuadricula
2. Ejecutar el kriging ordinario
3. Examinar el mapa de prediccion y la varianza
4. Opcionalmente, comparar con un modelo ML en la pestana ML

### Paso 5: Muestreo (opcional)

1. En la pestana **Muestreo**, disenar una estrategia para prospecciones futuras
2. Utilizar el variograma para el muestreo optimizado

### Paso 6: Informe

1. En la pestana **Informe**, generar el informe final
2. Exportar en PDF para documentacion

---

## Solucion de problemas

### Problemas comunes

| Problema | Causa | Solucion |
|----------|-------|----------|
| No hay capas disponibles | No hay capas de puntos en el proyecto | Anadir una capa vectorial de puntos al proyecto QGIS |
| No hay campos numericos | La capa no tiene campos numericos | Verificar la tabla de atributos de la capa |
| Variograma plano | Datos sin correlacion espacial | Verificar los datos, aumentar la distancia maxima |
| El kriging falla | Modelo de variograma no ajustado | Ajustar primero un modelo en la pestana Variograma |
| Malos resultados ML | Datos insuficientes o variables no informativas | Anadir variables predictoras o aumentar los datos |
| Panel no visible | Widget cerrado accidentalmente | Reabrir desde el menu Herramientas de Analisis |

### Errores frecuentes

- **"Datos insuficientes"**: Se necesitan al menos 30 puntos para un analisis fiable
- **"Modelo de variograma no definido"**: Ajustar un modelo antes de ejecutar el kriging
- **"CRS incompatible"**: Todas las capas deben usar el mismo sistema de referencia

### Rendimiento

- El analisis se ejecuta en un **hilo en segundo plano**: la interfaz de QGIS permanece utilizable
- Para conjuntos de datos muy grandes (>10.000 puntos), el procesamiento puede tardar mas
- Es posible monitorizar el progreso mediante la barra en la parte inferior del panel

---

## Notas tecnicas

### Dependencias

GeoArchaeo utiliza las siguientes bibliotecas Python:

| Biblioteca | Uso |
|-----------|-----|
| **NumPy** | Calculos numericos y matriciales |
| **SciPy** | Optimizacion y ajuste de modelos |
| **scikit-learn** | Algoritmos de aprendizaje automatico |
| **Matplotlib** | Generacion de graficos |

### Sistemas de referencia

- GeoArchaeo trabaja en el sistema de referencia del proyecto QGIS actual
- Se recomienda un **CRS proyectado** (en metros) para el analisis geoestadistico
- Los sistemas geograficos (en grados) pueden producir resultados imprecisos

### Exportacion de resultados

Los resultados pueden exportarse en varios formatos:

- **Capas raster** (GeoTIFF) para superficies interpoladas
- **Capas vectoriales** (GeoPackage, Shapefile) para puntos de muestreo
- **Graficos** (PNG, SVG) para variogramas y diagnosticos
- **Informes** (PDF, HTML, Markdown) para documentacion

### Integracion con QGIS

- Las capas de salida se anaden automaticamente al panel de **Capas** de QGIS
- El estilo de las capas raster puede personalizarse con las propiedades de capa de QGIS
- Los resultados son compatibles con todas las herramientas de analisis espacial de QGIS

---

> **Nota**: GeoArchaeo esta en desarrollo activo. Para reportar errores o sugerir mejoras, utilice el sistema de seguimiento de incidencias del proyecto PyArchInit en GitHub.
