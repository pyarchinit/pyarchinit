# PyArchInit - MoveCost - Analisis de Rutas de Menor Coste

## Indice

1. [Introduccion](#introduccion)
2. [Acceso a la herramienta](#acceso-a-la-herramienta)
3. [Requisitos previos](#requisitos-previos)
4. [Interfaz de usuario](#interfaz-de-usuario)
5. [Pestana Algoritmos](#pestana-algoritmos)
6. [Pestana Resultados](#pestana-resultados)
7. [Pestana Exportacion](#pestana-exportacion)
8. [Pestana Configuracion](#pestana-configuracion)
9. [Flujo de trabajo operativo](#flujo-de-trabajo-operativo)
10. [Solucion de problemas](#solucion-de-problemas)
11. [Notas tecnicas](#notas-tecnicas)

---

## Introduccion

**MoveCost** es una herramienta autonoma de PyArchInit para el analisis de rutas de menor coste (Least-Cost Path Analysis, LCPA) basada en scripts R. El analisis de rutas de menor coste es una metodologia fundamental en arqueologia del paisaje que permite modelar las rutas mas probables entre localizaciones, teniendo en cuenta la topografia del terreno y el coste energetico del movimiento.

### Historia

Anteriormente, la funcionalidad MoveCost estaba integrada directamente en el formulario de Sitio (Site form) de PyArchInit. A partir de la version actual, MoveCost ha sido extraido como **herramienta de analisis independiente**, accesible a traves de un QDialog dedicado. Esta separacion ofrece varias ventajas:

- **Interfaz dedicada**: Un dialogo con 4 pestanas organizadas por funcion
- **Mejor organizacion**: Algoritmos, resultados, exportacion y configuracion claramente separados
- **Acceso rapido**: Disponible desde la barra de herramientas sin abrir el formulario de Sitio
- **Extensibilidad**: Estructura modular que facilita la adicion de nuevos algoritmos

### Que es el analisis de rutas de menor coste?

El analisis de rutas de menor coste calcula la ruta optima entre dos o mas puntos sobre una superficie de coste derivada de un modelo digital del terreno (MDT). El coste del movimiento depende de la pendiente del terreno y se calcula utilizando funciones de coste anisotropicas que tienen en cuenta la direccion del movimiento (subida vs bajada).

<!-- IMAGE: Ejemplo de ruta de menor coste sobre MDT -->
> **Fig. 1**: Ejemplo de ruta de menor coste calculada sobre un modelo digital del terreno

---

## Acceso a la herramienta

### Desde la barra de herramientas

1. Localizar el boton desplegable **Herramientas de Analisis** (Analysis Tools) en la barra de herramientas de PyArchInit -- tiene un icono de grafico/analisis
2. Hacer clic en la flecha del menu desplegable
3. Seleccionar **MoveCost** del menu

<!-- IMAGE: Boton Herramientas de Analisis en la barra de herramientas -->
> **Fig. 2**: El boton Herramientas de Analisis en la barra de herramientas de PyArchInit con el menu desplegable abierto

### Ventana de dialogo

Al hacer clic, se abre un **QDialog modal** con cuatro pestanas:

```
+-----------------------------------------------------------+
|  MoveCost - Analisis de Rutas de Menor Coste               |
+-----------------------------------------------------------+
| [Algoritmos] | [Resultados] | [Exportacion] | [Config.]  |
+-----------------------------------------------------------+
|                                                           |
|              (Contenido de la pestana activa)               |
|                                                           |
+-----------------------------------------------------------+
|                              [Cerrar]                      |
+-----------------------------------------------------------+
```

---

## Requisitos previos

Antes de utilizar MoveCost, verificar que los siguientes componentes estan instalados y configurados:

### 1. R (Lenguaje estadistico)

| Requisito | Detalle |
|-----------|---------|
| **Software** | R (version >= 4.0 recomendada) |
| **Descarga** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verificacion** | Abrir una terminal y escribir `R --version` |

### 2. Paquete R `movecost`

Instalar el paquete desde R:

```r
install.packages("movecost")
```

Dependencias principales instaladas automaticamente: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Requisito | Detalle |
|-----------|---------|
| **Complemento** | Processing R Provider |
| **Instalacion** | QGIS > Complementos > Administrar e instalar complementos > Buscar "Processing R Provider" |
| **Configuracion** | Opciones de procesamiento > Sketcher > R > Ruta de la carpeta R |

### 4. Datos de entrada

- **MDT/MDE**: Un raster del modelo digital del terreno para el area de estudio
- **Capa de puntos**: Puntos de origen y destino para el analisis
- **Capa de poligonos**: (Opcional) Para las variantes "by polygon" de los algoritmos

### Lista de verificacion rapida

```
+-------------------------------------------+
| Lista de verificacion de requisitos        |
+-------------------------------------------+
| [x] R instalado y en el PATH             |
| [x] Paquete movecost instalado en R      |
| [x] Processing R Provider activo en QGIS |
| [x] MDT cargado en el proyecto QGIS       |
| [x] Capa de puntos con origenes/destinos  |
+-------------------------------------------+
```

---

## Interfaz de usuario

El dialogo MoveCost esta organizado en **4 pestanas**, cada una con una funcion especifica.

### Vista general de las pestanas

| Pestana | Icono | Funcion |
|---------|-------|---------|
| **Algoritmos** | Engranaje | Seleccionar y ejecutar los 14 algoritmos de analisis |
| **Resultados** | Grafico | Visualizar estadisticas de coste y graficos R |
| **Exportacion** | Disco | Exportar resultados a CSV, PDF o HTML |
| **Configuracion** | Llave inglesa | Configurar scripts R, idioma, organizacion de capas |

<!-- IMAGE: Vista general del dialogo MoveCost con 4 pestanas -->
> **Fig. 3**: El dialogo MoveCost con las cuatro pestanas visibles

---

## Pestana Algoritmos

La pestana **Algoritmos** es el nucleo de la herramienta MoveCost. Contiene **14 algoritmos** basados en scripts R, organizados en **3 grupos funcionales**.

### Grupo 1: Superficie de coste y rutas

Algoritmos para el calculo de superficies de coste acumuladas y rutas de menor coste.

| Algoritmo | Descripcion |
|-----------|-------------|
| **movecost** | Calcula la superficie de coste acumulada anisotropica dependiente de la pendiente y las rutas de menor coste desde un punto de origen |
| **movecost by polygon** | Igual, pero utilizando un area poligonal para definir la extension del MDT |
| **movebound** | Calcula los limites de coste de desplazamiento dependientes de la pendiente alrededor de localizaciones puntuales |
| **movebound by polygon** | Igual, pero utilizando un poligono |

### Grupo 2: Analisis de corredores y redes

Algoritmos para el analisis de corredores de coste y redes de rutas optimas.

| Algoritmo | Descripcion |
|-----------|-------------|
| **movecorr** | Calcula el corredor de menor coste entre localizaciones puntuales |
| **movecorr by polygon** | Igual, pero utilizando un poligono |
| **movealloc** | Calcula la asignacion de coste de desplazamiento dependiente de la pendiente a los origenes |
| **movealloc by polygon** | Igual, pero utilizando un poligono |
| **movenetw** | Calcula la red de rutas de menor coste entre multiples puntos |
| **movenetw by polygon** | Igual, pero utilizando un poligono |

### Grupo 3: Comparacion y clasificacion

Algoritmos para comparar funciones de coste y clasificar destinos.

| Algoritmo | Descripcion |
|-----------|-------------|
| **movecomp** | Compara rutas de menor coste generadas utilizando diferentes funciones de coste |
| **movecomp by polygon** | Igual, pero utilizando un poligono |
| **moverank** | Clasifica los destinos por coste de desplazamiento desde un origen |
| **moverank by polygon** | Igual, pero utilizando un poligono |

### Como ejecutar un algoritmo

1. Seleccionar el algoritmo deseado de la lista
2. La interfaz de procesamiento de QGIS se abre con los parametros especificos del algoritmo
3. Configurar los parametros de entrada:
   - **MDT/MDE**: Seleccionar el raster del terreno
   - **Punto(s) de origen**: Seleccionar la capa de puntos
   - **Poligono** (si variante "by polygon"): Seleccionar el area de estudio
   - **Funcion de coste**: Elegir entre las funciones disponibles (Tobler, Minetti, etc.)
4. Hacer clic en **Ejecutar**
5. Los resultados se anaden automaticamente al proyecto QGIS

<!-- IMAGE: Pestana Algoritmos con 3 grupos -->
> **Fig. 4**: La pestana Algoritmos con los tres grupos de algoritmos resaltados

<!-- IMAGE: Interfaz de procesamiento para un algoritmo movecost -->
> **Fig. 5**: La interfaz de procesamiento de QGIS para el algoritmo movecost con los parametros configurados

### Variantes "by polygon"

Las variantes "by polygon" de cada algoritmo permiten:
- **Limitar el area de analisis** a una region especifica
- **Reducir el tiempo de calculo** trabajando con un MDT recortado
- **Focalizar el analisis** en un area de interes arqueologico

---

## Pestana Resultados

La pestana **Resultados** permite visualizar los resultados de los analisis ejecutados.

### Resumen de costes (Cost Summary)

Un area de texto (QTextEdit) muestra las estadisticas resumidas de las capas de coste generadas:

| Estadistica | Descripcion |
|-------------|-------------|
| **Minimo** | Valor minimo de coste en la superficie |
| **Maximo** | Valor maximo de coste en la superficie |
| **Media** | Valor medio de coste |
| **Desv. Estandar** | Desviacion estandar de los valores de coste |

```
+---------------------------------------------------+
| Resumen de costes                                  |
+---------------------------------------------------+
| Capa: movecost_accumulated_cost                    |
| Minimo: 0.00                                       |
| Maximo: 15234.56                                   |
| Media: 4521.89                                     |
| Desv. Estandar: 2103.45                            |
|                                                    |
| Capa: movecost_back_link                           |
| Minimo: 0.00                                       |
| Maximo: 8.00                                       |
| Media: 4.12                                        |
+---------------------------------------------------+
```

### Visor de graficos R (R Plot Viewer)

El visor de graficos R muestra el ultimo grafico generado por los scripts R:

| Funcion | Descripcion |
|---------|-------------|
| **Visualizacion automatica** | Muestra el ultimo grafico R del directorio temporal |
| **Actualizar** | Recarga el ultimo grafico disponible |
| **Guardar** | Guarda el grafico actual en un archivo de imagen (PNG, JPG) |
| **Seleccion manual** | Permite abrir un grafico R especifico desde cualquier ubicacion |

<!-- IMAGE: Pestana Resultados con resumen de costes y grafico R -->
> **Fig. 6**: La pestana Resultados mostrando las estadisticas de coste y un grafico R

### Ubicaciones de los graficos R

Los graficos R se guardan en los directorios temporales de QGIS/R. El visor busca automaticamente en las siguientes ubicaciones:

- Directorio temporal de QGIS Processing
- Directorio temporal de R (`tempdir()`)
- Carpeta de salida especificada por el usuario

---

## Pestana Exportacion

La pestana **Exportacion** ofrece tres opciones para exportar los resultados del analisis.

### Exportar tabla de costes (CSV)

Exporta las estadisticas de las capas de coste a un archivo CSV:

1. Hacer clic en **Exportar tabla de costes**
2. Seleccionar la ubicacion y el nombre del archivo
3. El archivo CSV contiene: nombre de capa, minimo, maximo, media, desviacion estandar

| Columna | Descripcion |
|---------|-------------|
| `layer_name` | Nombre de la capa de coste |
| `min_value` | Valor minimo |
| `max_value` | Valor maximo |
| `mean_value` | Valor medio |
| `std_dev` | Desviacion estandar |

### Exportar informe (PDF)

> **Nota**: Esta funcionalidad se encuentra actualmente en desarrollo (stub). Estara disponible en una version futura.

### Exportar informe (HTML)

Genera un informe HTML completo y estilizado que incluye:

- **Encabezado** con titulo del proyecto y fecha
- **Parametros del analisis** utilizados
- **Estadisticas de las capas** en formato tabular
- **Graficos R** incorporados como imagenes
- **Estilo CSS integrado** para una presentacion profesional

1. Hacer clic en **Exportar informe (HTML)**
2. Seleccionar la ubicacion y el nombre del archivo
3. El informe se abre automaticamente en el navegador predeterminado

<!-- IMAGE: Ejemplo de informe HTML exportado -->
> **Fig. 7**: Un ejemplo de informe HTML generado por MoveCost con estadisticas y graficos

---

## Pestana Configuracion

La pestana **Configuracion** permite configurar la herramienta MoveCost.

### Instalar scripts R

| Funcion | Descripcion |
|---------|-------------|
| **Instalar scripts R** | Copia los scripts R de movecost en el directorio de procesamiento de QGIS |

Esta operacion es necesaria en la **primera configuracion** o despues de una actualizacion del complemento. Los scripts se copian en la carpeta de scripts R de Processing:

```
{QGIS_HOME}/processing/rscripts/
```

### Seleccion de idioma

MoveCost admite **5 idiomas** para la interfaz:

| Idioma | Codigo |
|--------|--------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

El idioma seleccionado se aplica a:
- Etiquetas de la interfaz del dialogo
- Mensajes de estado y error
- Encabezados de las tablas de resultados

### Organizacion de capas

| Funcion | Descripcion |
|---------|-------------|
| **Organizar capas** | Organizacion y estilizacion automatica de las capas de salida de movecost |

Esta funcion:
1. Agrupa las capas de salida en grupos logicos en el panel de Capas de QGIS
2. Aplica estilos de color predefinidos (rampas de color para superficies de coste)
3. Renombra las capas con nombres descriptivos

### Documentacion

| Funcion | Descripcion |
|---------|-------------|
| **Ayuda** | Abre la documentacion en linea de la herramienta |

<!-- IMAGE: Pestana Configuracion con todas las opciones -->
> **Fig. 8**: La pestana Configuracion de MoveCost con las opciones de configuracion

---

## Flujo de trabajo operativo

### Ejemplo paso a paso: Calculo de una ruta de menor coste

Este ejemplo muestra como calcular una ruta de menor coste entre un asentamiento y una fuente de agua.

### Paso 1: Preparacion de datos

```
1. Cargar el MDT del area de estudio en el proyecto QGIS
2. Crear una capa de puntos con:
   - Punto de origen (asentamiento)
   - Punto(s) de destino (fuente de agua)
3. Verificar que el sistema de referencia de coordenadas es consistente
```

### Paso 2: Verificacion de requisitos

```
1. Abrir MoveCost desde la barra de herramientas
2. Ir a la pestana Configuracion
3. Hacer clic en "Instalar scripts R" (si es la primera vez)
4. Verificar que no se reportan errores
```

### Paso 3: Ejecucion del analisis

```
1. Cambiar a la pestana Algoritmos
2. Seleccionar "movecost" del Grupo 1
3. En la ventana de procesamiento:
   - MDT: seleccionar el raster del terreno
   - Origen: seleccionar el punto del asentamiento
   - Destino: seleccionar el punto de la fuente de agua
   - Funcion de coste: Tobler (recomendada por defecto)
4. Hacer clic en Ejecutar
5. Esperar a que se complete el procesamiento
```

### Paso 4: Analisis de resultados

```
1. Cambiar a la pestana Resultados
2. Revisar el Resumen de costes para las estadisticas
3. Examinar el grafico R para la visualizacion
4. En el lienzo de QGIS, observar:
   - La superficie de coste acumulada (raster coloreado)
   - La ruta de menor coste (linea vectorial)
```

### Paso 5: Exportacion

```
1. Cambiar a la pestana Exportacion
2. Exportar la tabla de costes a CSV para analisis adicionales
3. Generar el informe HTML para la documentacion
4. Guardar el grafico R desde la pestana Resultados
```

### Paso 6: Organizacion

```
1. Volver a la pestana Configuracion
2. Hacer clic en "Organizar capas" para ordenar los resultados
3. Las capas se agrupan y estilizan automaticamente
```

<!-- IMAGE: Flujo de trabajo completo con capturas de pantalla anotadas -->
> **Fig. 9**: El flujo de trabajo completo desde la preparacion de datos hasta los resultados finales

---

## Solucion de problemas

### R no encontrado

**Sintoma**: Mensaje de error "R no encontrado" o "R is not installed"

**Soluciones**:
1. Verificar que R esta instalado: abrir una terminal y escribir `R --version`
2. Comprobar la ruta de R en la configuracion de Processing:
   - **QGIS** > **Configuracion** > **Opciones** > **Sketcher** > **Sketcher** > **R**
   - Establecer la **ruta de la carpeta R** correctamente
3. En macOS, R puede estar en `/Library/Frameworks/R.framework/Resources/`
4. En Windows, normalmente en `C:\Program Files\R\R-4.x.x\`
5. En Linux, verificar con `which R`

### Scripts R ausentes

**Sintoma**: Los algoritmos no aparecen en la caja de herramientas de procesamiento

**Soluciones**:
1. Abrir MoveCost > Configuracion > hacer clic en **Instalar scripts R**
2. Reiniciar QGIS despues de instalar los scripts
3. Verificar que el Processing R Provider esta activo:
   - **QGIS** > **Complementos** > **Administrar e instalar complementos** > Verificar "Processing R Provider"
4. Comprobar la carpeta de scripts R: `{QGIS_HOME}/processing/rscripts/`

### Graficos R no se muestran

**Sintoma**: La pestana Resultados no muestra ningun grafico

**Soluciones**:
1. Hacer clic en **Actualizar** en la pestana Resultados
2. Usar **Seleccion manual** para navegar a la carpeta de graficos
3. Verificar que el analisis se completo exitosamente
4. Comprobar los directorios temporales:
   - macOS/Linux: `/tmp/` o `$TMPDIR`
   - Windows: `%TEMP%`
5. Algunos algoritmos pueden no generar graficos

### Paquete movecost no instalado en R

**Sintoma**: Error "there is no package called 'movecost'"

**Soluciones**:
1. Abrir R o RStudio
2. Ejecutar: `install.packages("movecost")`
3. Verificar: `library(movecost)` -- no debe producir errores
4. Si hay problemas de dependencias: `install.packages("movecost", dependencies = TRUE)`

### Analisis muy lento

**Sintoma**: El procesamiento tarda mucho tiempo

**Soluciones**:
1. Usar las variantes **"by polygon"** para limitar el area de calculo
2. Reducir la resolucion del MDT (remuestreo)
3. Comprobar las dimensiones del MDT:
   - MDTs muy grandes (>10000x10000 pixeles) requieren tiempo considerable
   - Recortar el MDT al area de interes antes del analisis
4. Cerrar otras aplicaciones para liberar RAM

### Error de proyeccion / SRC

**Sintoma**: Resultados inconsistentes o error de sistema de referencia de coordenadas

**Soluciones**:
1. Verificar que el MDT y las capas de puntos tienen el **mismo SRC**
2. Usar un **SRC proyectado** (metrico), no geografico
3. SRC recomendados: UTM (p.ej. EPSG:32632 para Italia central)
4. Reproyectar las capas si es necesario antes del analisis

---

## Notas tecnicas

### Arquitectura de la herramienta

MoveCost esta implementado como un **QDialog** autonomo (`MoveCostDialog`) que:
- Se interfaza con el QGIS Processing Framework para la ejecucion de algoritmos R
- Lee los resultados desde las capas cargadas en el proyecto
- Gestiona la visualizacion de graficos R mediante QLabel/QPixmap
- Genera informes HTML utilizando plantillas predefinidas

### Archivos fuente

| Archivo | Descripcion |
|---------|-------------|
| `tabs/MoveCost.py` | Dialogo principal y logica de la interfaz |
| `gui/ui/MoveCost.ui` | Diseno de la interfaz Qt Designer |
| `resources/r_scripts/` | Scripts R para los algoritmos movecost |

### Funciones de coste soportadas

El paquete R `movecost` soporta varias funciones de coste anisotropicas:

| Funcion | Autor | Descripcion |
|---------|-------|-------------|
| **Tobler** | Tobler (1993) | Funcion de coste de marcha clasica |
| **Minetti** | Minetti et al. (2002) | Basada en el coste metabolico |
| **Herzog** | Herzog (2010) | Variante modificada |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Modelo energetico |
| **Otras** | Varios | Ver documentacion del paquete R |

### Referencias bibliograficas

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibilidad

| Componente | Version minima |
|------------|---------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| Paquete movecost (R) | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Tutorial en video

### MoveCost - Analisis de Rutas de Menor Coste
`[Marcador: video_movecost.mp4]`

**Contenido**:
- Configuracion de R y el paquete movecost
- Instalacion de los scripts R en QGIS
- Ejecucion del algoritmo movecost basico
- Visualizacion de resultados y graficos R
- Exportacion de informes

**Duracion estimada**: 20-25 minutos

---

*Documentacion PyArchInit - MoveCost*
*Version: 5.0.x*
*Ultima actualizacion: Febrero 2026*
