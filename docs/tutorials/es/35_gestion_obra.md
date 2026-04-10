# PyArchInit - Gestion de Obra (Site Management)

## Indice

1. [Introduccion](#introduccion)
2. [Acceso al modulo](#acceso-al-modulo)
3. [Panel de Obra (Dashboard)](#panel-de-obra-dashboard)
4. [Formulario de Personal](#formulario-de-personal)
5. [Formulario de Asistencia](#formulario-de-asistencia)
6. [Formulario de Equipamiento](#formulario-de-equipamiento)
7. [Formulario de Presupuesto](#formulario-de-presupuesto)
8. [Visualizacion 2D y 3D del Computo Metrico](#visualizacion-2d-y-3d-del-computo-metrico)
9. [Exportacion PDF y CSV del Panel](#exportacion-pdf-y-csv-del-panel)
10. [Flujo de trabajo operativo](#flujo-de-trabajo-operativo)
11. [Preguntas frecuentes (FAQ)](#preguntas-frecuentes-faq)
12. [Notas tecnicas](#notas-tecnicas)

---

## Introduccion

El modulo **Gestion de Obra** (*Gestione Cantiere*) es el componente de PyArchInit dedicado a la gestion administrativa y logistica de una excavacion arqueologica. Aborda los aspectos operativos del trabajo de campo: personal, asistencia, equipamiento y presupuesto.

El modulo esta compuesto por **cinco herramientas** independientes pero interconectadas:

| # | Herramienta | Funcion |
|---|-------------|---------|
| 1 | **Panel de Obra** | Dashboard central con resumen de presupuesto, personal, equipamiento y topografia |
| 2 | **Personal** | Registro CRUD de los trabajadores del proyecto |
| 3 | **Asistencia** | Registro CRUD de jornadas laborales, ausencias y costes diarios |
| 4 | **Equipamiento** | Registro CRUD de maquinaria, instrumentos y herramientas |
| 5 | **Presupuesto** | Registro CRUD de partidas presupuestarias (previstos vs. efectivos) |

<!-- IMAGE: Vista general del modulo Gestion de Obra con los 5 iconos de la barra de herramientas -->
> **Fig. 1**: Los cinco iconos del modulo Gestion de Obra en la barra de herramientas de PyArchInit

---

## Acceso al modulo

El modulo se accede desde la barra de herramientas **Gestion de Obra**, que contiene **5 iconos**: Panel de Obra, Personal, Asistencia, Equipamiento y Presupuesto. Al abrir cualquier formulario por primera vez, las tablas necesarias se crean automaticamente en la base de datos.

<!-- IMAGE: Barra de herramientas Gestion de Obra con los 5 botones resaltados -->
> **Fig. 2**: La barra de herramientas Gestion de Obra con los cinco botones de acceso

---

## Panel de Obra (Dashboard)

El **Panel de Obra** es el dashboard central del modulo. En la parte superior se encuentran los selectores de **Sitio** y **Ano** que filtran todos los indicadores.

### Seccion Presupuesto

| Indicador | Descripcion |
|-----------|-------------|
| **Importe previsto** | Suma total de las partidas planificadas |
| **Importe efectivo** | Suma total del gasto ejecutado |
| **Barra de progreso** | Porcentaje de ejecucion (verde <75%, amarillo 75-90%, rojo >90%) |
| **Grafico de sectores** | Distribucion del gasto por categorias |

<!-- IMAGE: Seccion Presupuesto del dashboard con barra de progreso y grafico de sectores -->
> **Fig. 3**: El resumen presupuestario con la barra de progreso y el grafico de sectores

### Seccion Personal

| Indicador | Descripcion |
|-----------|-------------|
| **Presentes / Vacaciones / Baja** | Contadores de estado del personal en el dia actual |
| **Horas mensuales** | Total de horas trabajadas en el mes en curso |
| **Coste mensual** | Coste total del personal en el mes en curso |

<!-- IMAGE: Seccion Personal del dashboard con los indicadores de presencia -->
> **Fig. 4**: El resumen de personal con los contadores de presencia y los totales mensuales

### Seccion Equipamiento

| Indicador | Descripcion |
|-----------|-------------|
| **Total / En uso / En mantenimiento** | Contadores de estado del inventario |
| **Alertas de mantenimiento** | Equipos con mantenimiento vencido (resaltados en rojo) |

<!-- IMAGE: Seccion Equipamiento del dashboard con indicadores y alertas -->
> **Fig. 5**: El resumen de equipamiento con los indicadores de estado y las alertas

### Seccion Topografia (Computo Metrico)

| Metodo | Descripcion |
|--------|-------------|
| **Diferencia de DEM** | Volumen comparando dos DEM (antes y despues de la excavacion) |
| **DEM + Poligono** | Volumen dentro de un area poligonal definida sobre un DEM |

Procedimiento: seleccionar los rasters (y poligono si aplica), hacer clic en **Calcular** y el resultado se muestra en metros cubicos.

A partir de la version 5.1, junto al boton **Calcular** estan tambien disponibles los botones **Mostrar 2D**, **Mostrar 3D** y **Crear malla 3D** para visualizar el resultado del calculo directamente en el mapa y en una vista tridimensional interactiva. Ver la seccion [Visualizacion 2D y 3D del Computo Metrico](#visualizacion-2d-y-3d-del-computo-metrico).

<!-- IMAGE: Seccion Topografia con los dos metodos de calculo de volumenes y los botones 2D/3D -->
> **Fig. 6**: Los dos metodos de computo metrico y los nuevos botones de visualizacion 2D / 3D

### Tabla de historial

En la parte inferior del panel, una tabla muestra los eventos recientes del proyecto con columnas: **Fecha**, **Tipo**, **Descripcion** y **Usuario**.

<!-- IMAGE: Tabla de historial en la parte inferior del Panel de Obra -->
> **Fig. 7**: La tabla de historial del Panel de Obra

### Nuevo diseno por pestanas del Panel de Obra

A partir de la version actual, la ventana **Panel de Obra** se ha reorganizado en **tres pestanas** para dar cabida al nuevo panel de **Analisis de Costes** sin recargar la vista. La fila de cabecera con **Sitio**, **Ano** y el boton **Actualizar** se mantiene visible encima de las pestanas, de modo que se puede cambiar de sitio o de ano en cualquier momento y todas las pestanas se actualizan automaticamente.

| Pestana | Contenido |
|---------|-----------|
| **Resumen** | Es la vista que se muestra al abrir el panel. Arriba, a todo lo ancho, el **Resumen de Presupuesto** (barra de progreso y grafico de sectores); debajo, en paralelo, los resumenes de **Personal** y **Equipamiento** |
| **Computo Metrico** | Agrupa todo el flujo de calculo DEM: combos **DEM Pre**, **DEM Post** y **Poligono**, radios **Diferencia de DEM** / **DEM sobre Poligono**, boton **Calcular**, etiquetas de **area** y **volumen**, el nuevo grupo **Analisis de Costes** (EUR/m3, m3/dia -> coste total, dias estimados, coste diario), boton **Guardar Registro**, botones **Mostrar 2D** / **Mostrar 3D** / **Exportar 2DM + 3D** y la **tabla de historial** abajo |
| **Exportacion** | Los botones de **exportacion PDF** y **CSV** con una breve descripcion |

<!-- IMAGE: Nuevo diseno por pestanas del Panel de Obra (Resumen / Computo Metrico / Exportacion) -->
> **Fig. 7a**: El nuevo diseno por pestanas del Panel de Obra con la cabecera Sitio / Ano / Actualizar siempre visible

**Fix**: los DEM ya no desaparecen al pulsar **Calcular** (regresion de la 5.0.13-alpha en la que la actualizacion automatica de los combos reiniciaba la seleccion actual).

---

## Formulario de Personal

Permite registrar los datos de trabajadores y colaboradores del proyecto.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **Nombre** | Texto | Si |
| **Apellidos** | Texto | Si |
| **Cualificacion** | ComboBox (arqueologo, tecnico, operario...) | No |
| **Rol** | ComboBox (director, responsable de area, excavador...) | No |
| **Fecha de contratacion** | Fecha | No |
| **Fecha de fin** | Fecha (vacia si activo) | No |
| **Coste diario** | Numerico (euros) | No |
| **Notas** | Texto | No |

**Crear registro**: New record > completar campos > Save. **Buscar**: new search > criterios > search !!!

<!-- IMAGE: Formulario de Personal con todos los campos visibles -->
> **Fig. 8**: El formulario de Personal con los campos de registro

---

## Formulario de Asistencia

Registra las jornadas laborales de cada trabajador.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **ID Personal** | ComboBox (vinculado a Personal) | Si |
| **Fecha** | Fecha | Si |
| **Tipo de jornada** | ComboBox: Laboral / Vacaciones / Baja / Permiso | Si |
| **Horas ordinarias** | Numerico | No |
| **Horas extra** | Numerico | No |
| **Coste jornada** | Numerico (calculo automatico o manual) | No |
| **Notas** | Texto | No |

**Registrar jornada**: New record > seleccionar trabajador, fecha y tipo > insertar horas > Save. El coste puede calcularse automaticamente a partir del coste diario del trabajador.

<!-- IMAGE: Formulario de Asistencia con un registro de jornada laboral -->
> **Fig. 9**: El formulario de Asistencia con un registro completado

---

## Formulario de Equipamiento

Gestiona el inventario de maquinaria e instrumentos.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **Nombre** | Texto | Si |
| **Tipo** | ComboBox (maquinaria, instrumento topografico, herramienta...) | No |
| **Marca** / **Modelo** | Texto | No |
| **Estado** | ComboBox: `en_uso` / `mantenimiento` / `fuera_servicio` | Si |
| **Fecha de compra** | Fecha | No |
| **Coste** | Numerico (euros) | No |
| **Fecha ultimo mantenimiento** | Fecha | No |
| **Fecha proximo mantenimiento** | Fecha | No |
| **Notas** | Texto | No |

Cuando la fecha de proximo mantenimiento se supera, el **Panel de Obra** muestra una alerta en rojo.

<!-- IMAGE: Formulario de Equipamiento con un registro de instrumento topografico -->
> **Fig. 10**: El formulario de Equipamiento con un registro de estacion total

---

## Formulario de Presupuesto

Planifica y controla los costes del proyecto por ano y categoria.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **Ano** | Numerico | Si |
| **Categoria** | ComboBox (Personal, Materiales, Equipamiento, Logistica, Documentacion, Laboratorio, Otros) | Si |
| **Partida** | Texto (descripcion de la linea de gasto) | Si |
| **Importe previsto** | Numerico (euros) | No |
| **Importe efectivo** | Numerico (euros) | No |
| **Notas** | Texto | No |

**Crear partida**: New record > seleccionar sitio, ano y categoria > insertar partida e importe previsto > Save. Actualizar el importe efectivo cuando se conozca el gasto real.

<!-- IMAGE: Formulario de Presupuesto con una partida registrada -->
> **Fig. 11**: El formulario de Presupuesto con una partida presupuestaria registrada

---

## Visualizacion 2D y 3D del Computo Metrico

A partir de la version 5.1, despues de pulsar el boton **Calcular** en el panel Computo Metrico, el Panel de Obra no se limita a mostrar los valores numericos (area y volumen): crea automaticamente un conjunto de capas cartograficas y ofrece una vista 3D interactiva.

### Que ocurre al pulsar "Calcular"

Al finalizar un calculo de diferencia de DEM, el Panel de Obra realiza automaticamente los siguientes pasos:

1. **Guardado permanente del raster diferencia**: el raster resultante (DEM post - DEM pre) se guarda como GeoTIFF permanente en `<PYARCHINIT_HOME>/site_dashboard/<nombre del sitio>/`. De esta manera el raster no se pierde al cerrar QGIS y puede reutilizarse en cualquier momento.
2. **Anadido al proyecto QGIS**: el raster se anade al panel de capas dentro de un grupo dedicado llamado **"Site Dashboard - Computi"**, para mantener organizados todos los calculos.
3. **Estilo automatico**: al raster se le aplica una **rampa de colores divergente**:
   - **Rojo** para las zonas de excavacion (valores negativos, terreno retirado)
   - **Azul** para las zonas de relleno (valores positivos, terreno anadido)
   - **Transparente / neutro** para celdas con variacion despreciable (|diff| <= 1 cm)
4. **Poligonalizacion del area de intervencion**: las celdas raster con |diff| > 1 cm se convierten en un layer vectorial de poligonos, anadido tambien al grupo "Site Dashboard - Computi" con un estilo destacado, para mostrar de un vistazo la extension total de la intervencion.
5. **Zoom automatico**: el lienzo principal del mapa de QGIS se centra automaticamente en la extension del calculo.

### Requisitos

Para utilizar las nuevas visualizaciones 2D / 3D es necesario:

- Tener **dos capas raster DEM** cargadas en el proyecto QGIS (tipicamente un DEM **pre** y un DEM **post** excavacion)
- Seleccionarlas en los combos **DEM Pre** y **DEM Post** del panel Computo Metrico
- El sistema de referencia (CRS) de los dos rasters debe ser coherente

### Nuevos botones

Junto al boton **Calcular** hay ahora tres nuevos botones:

| Boton | Descripcion |
|-------|-------------|
| **Mostrar 2D** | Centra nuevamente el mapa de QGIS en la extension del ultimo calculo. Util para volver rapidamente al Computo Metrico activo despues de trabajar en otras areas. |
| **Mostrar 3D** | Abre un dialogo 3D interactivo que usa el DEM **pre** como terreno y superpone el raster diferencia. Incluye: un control para la **exageracion vertical**, casillas para activar / desactivar capas individuales y un boton **Reiniciar vista**. |
| **Crear malla 3D** | Construye mallas TIN a partir de los DEMs pre y post (a traves de los algoritmos de QGIS Processing). Las mallas pueden mostrarse dentro del visualizador 3D para comparar visualmente las dos superficies y el volumen entre ellas. |

<!-- IMAGE: Los nuevos botones Mostrar 2D, Mostrar 3D y Crear malla 3D junto al boton Calcular -->
> **Fig. 14**: Los nuevos botones **Mostrar 2D**, **Mostrar 3D** y **Crear malla 3D** junto al boton **Calcular**

<!-- IMAGE: Dialogo 3D interactivo con el DEM pre como terreno y el raster diferencia superpuesto -->
> **Fig. 15**: El dialogo 3D interactivo del Computo Metrico con exageracion vertical y control de capas

### Flujo de trabajo tipico

1. Cargar en el proyecto QGIS los dos rasters DEM (pre y post)
2. Abrir el **Panel de Obra**
3. En la seccion **Computo Metrico** seleccionar los dos DEMs en **DEM Pre** y **DEM Post**
4. Pulsar **Calcular**: se crean automaticamente el raster diferencia y el poligono de intervencion y el mapa se centra en la extension
5. Leer los valores numericos (area, volumen, excavacion, relleno) directamente en el panel
6. Pulsar **Mostrar 3D** para abrir la vista tridimensional
7. (Opcional) Pulsar **Crear malla 3D** para generar y visualizar las mallas TIN de los dos DEMs
8. Pulsar **Guardar Computo** para archivar el resultado en el historial

### Organizacion en disco

Todos los rasters y capas generados por el Computo Metrico se almacenan en:

```
<PYARCHINIT_HOME>/site_dashboard/<nombre del sitio>/
```

donde `<PYARCHINIT_HOME>` es la carpeta de trabajo configurada en los ajustes de PyArchInit y `<nombre del sitio>` es el sitio actualmente seleccionado en el panel. Esto mantiene un historial fisico de todos los calculos y permite reutilizar las capas en otros proyectos de QGIS.

### Actualizacion: "Mostrar 2D" -- Dialogo de seccion analitica

A partir de la proxima version, el boton **Mostrar 2D** del panel Computo Metrico ya no se limita a centrar el mapa sobre el ultimo calculo: ahora abre un **dialogo analitico basado en matplotlib** que presenta los resultados de la excavacion como una seccion arqueologica clasica.

El dialogo esta disponible **solo cuando el calculo se ha realizado en modo "Diferencia DEM"** (con DEM pre y DEM post). Si se ha utilizado el modo **DEM + Poligono**, el boton se comporta como antes y simplemente hace zoom al lienzo de QGIS en la extension del calculo.

Cuando esta disponible, el dialogo contiene los siguientes paneles:

| Panel | Descripcion |
|-------|-------------|
| **Mapa de calor de diferencia DEM** | Mapa de calor 2D del raster de corte/relleno con una rampa de colores divergente (rojo para excavacion, azul para relleno) |
| **Histograma** | Distribucion de profundidades de **excavacion** y alturas de **relleno**, para obtener de inmediato un resumen estadistico del volumen movido |
| **Seccion longitudinal (E-O)** | La clasica seccion arqueologica: el **DEM pre** se dibuja en **azul**, el **DEM post** en **rojo** y el volumen excavado queda **relleno** entre ambas lineas |
| **Seccion transversal (N-S)** | Misma idea que la seccion E-O pero a lo largo de la direccion Norte-Sur |
| **Spinbox fila / columna** | Permiten desplazar interactivamente la posicion de ambas secciones sobre el raster para explorar toda la excavacion |
| **Boton "Guardar PNG"** | Exporta la figura completa (mapa de calor, histograma y ambas secciones) como imagen PNG, lista para incluir en el informe de excavacion |

<!-- IMAGE: Dialogo analitico Mostrar 2D con mapa de calor, histograma y secciones E-O / N-S -->
> **Fig. 16**: El nuevo dialogo analitico **Mostrar 2D** con mapa de calor de diferencia DEM, histograma de excavacion / relleno y ambas secciones longitudinal y transversal (DEM pre en azul, DEM post en rojo, volumen excavado relleno entre las dos lineas)

### Actualizacion: "Mostrar 3D" -- Fallback con matplotlib

El boton **Mostrar 3D** gestiona ahora automaticamente dos escenarios segun la version de QGIS instalada:

1. **QGIS con modulo 3D nativo (Qt3D disponible)**: como antes, se abre el dialogo `Qgs3DMapCanvas` embebido, con terreno basado en el DEM pre, exageracion vertical y control de capas.
2. **QGIS sin modulo 3D (error "QGIS 3D module not available")**: el Panel de Obra pasa automaticamente a un **visualizador 3D basado en matplotlib**. Como matplotlib forma parte de las dependencias que ya instala el plugin, este visualizador **siempre funciona**, incluso en compilaciones de QGIS sin soporte 3D.

El visualizador de fallback ofrece:

| Control | Descripcion |
|---------|-------------|
| **Modo de visualizacion** | Tres modos seleccionables: **Pre + Post** (ambas superficies superpuestas), **Solo diferencia** (solo la superficie de corte/relleno), **Solo pre** (el DEM pre como superficie de referencia) |
| **Exageracion vertical** | Un deslizador para enfatizar la diferencia de cota entre las dos superficies, util cuando la excavacion es poco profunda |
| **Rotacion interactiva** | Arrastrando con el raton es posible rotar la escena 3D en tiempo real para explorar la excavacion desde cualquier angulo |

<!-- IMAGE: Visualizador 3D matplotlib de fallback en modo Pre + Post -->
> **Fig. 17**: El visualizador 3D matplotlib de fallback cuando QGIS no dispone del modulo Qt3D nativo: muestra las superficies pre y post con exageracion vertical ajustable

### Actualizacion: "Crear malla 3D" -- Estilo automatico de terreno

El boton **Crear malla 3D** aplica ahora automaticamente una **rampa de colores tipo terreno** al grupo de datasets de elevacion de la malla (**Bed Elevation**). Antes la malla se veia como una superficie plana y poco legible; ahora se convierte de inmediato en un mapa de cotas expresivo:

- **Verde** para las cotas mas bajas
- **Naranja** para las cotas intermedias
- **Marron** para las cotas mas altas

De este modo la malla resulta visible y significativa en el lienzo de QGIS incluso antes de abrir la vista 3D. Despues de construirla basta con pulsar **Mostrar 3D** para verla renderizada como superficie tridimensional, ya sea a traves del modulo 3D nativo de QGIS o del visualizador matplotlib de fallback descrito arriba.

<!-- IMAGE: Malla 3D con la nueva rampa verde / naranja / marron tipo terreno -->
> **Fig. 18**: La malla 3D con la nueva rampa de colores tipo terreno aplicada automaticamente a su dataset de elevacion

### Actualizacion: poligono como mascara de recorte

Si en el panel Computo Metrico, ademas de los dos DEMs, se selecciona tambien una capa vectorial en el combo **Capa Poligono** manteniendo activa la modalidad **Diferencia DEM**, el poligono se utiliza ahora como **mascara de recorte**: ambos DEMs se recortan sobre el poligono antes del calculo de la diferencia, de modo que la seccion analitica 2D, el fallback 3D con matplotlib y la malla TIN trabajan exclusivamente sobre el area de intervencion. El flujo tipico es: dibujar un poligono alrededor de la excavacion, seleccionar los DEMs pre y post, elegir el poligono en el combo **Capa Poligono** y pulsar **Calcular**. Los dos rasters recortados se anaden automaticamente al grupo **"Cruscotto Cantiere - Computi"** del arbol de capas, listos para ser reutilizados.

### Actualizacion: "Crear malla 3D" -- se acabaron los crashes

Las versiones anteriores podian provocar un crash de QGIS en algunas compilaciones debido a un segfault de C++ dentro de los algoritmos de Processing utilizados para construir la malla. La generacion se ha reescrito en **Python puro**: el Panel lee el DEM con GDAL y escribe directamente un archivo 2DM con una **malla de cuadrangulos en cuadricula regular**, sin depender de los algoritmos nativos. El resultado es seguro en cualquier version de QGIS. Las mallas con mas de unas **15 000 celdas** se remuestrean automaticamente para mantener la construccion rapida y el archivo ligero, mientras que las celdas con valor nodata se descartan: si hay una mascara poligonal activa, la malla sigue exactamente la forma del area de intervencion recortada. En el raro caso de que la generacion falle por otros motivos (disco lleno, permisos), el dialogo sugiere ahora abrir directamente **Mostrar 3D**, que utiliza el visualizador matplotlib de fallback y no necesita ninguna capa de malla.

### Actualizacion: auto-refresco de los combos al pulsar "Calcular"

El panel Computo Metrico ahora **actualiza automaticamente las listas de DEM y poligono cada vez que se pulsa "Calcular"**: ya no es necesario cerrar y reabrir el Panel de Obra despues de cargar un nuevo raster o dibujar un nuevo poligono en el proyecto. Basta con anadir la capa en QGIS, volver al panel y pulsar **Calcular** -- los combos **DEM Pre**, **DEM Post** y **Capa Poligono** se rellenan al vuelo con el estado actual del proyecto. La eventual diagnostica del recorte (exito, CRS no compatible, interseccion vacia) aparece en la **barra de mensajes de QGIS**, de modo que siempre quede claro que capas se han usado realmente en el calculo.

### Actualizacion: boton renombrado "Exportar 2DM + 3D"

El boton anteriormente llamado **Crear malla 3D** se ha renombrado a **Exportar 2DM + 3D** para reflejar su nuevo comportamiento: **ya no** carga la malla como capa en el proyecto QGIS (la API de malla nativa puede provocar crashes en algunas compilaciones de QGIS) y en su lugar realiza dos acciones seguras y complementarias. Escribe los archivos **2DM** en disco a partir de los DEMs pre y post (utiles para importar en software externo de post-procesado) y abre directamente la **vista 3D matplotlib** sobre los DEMs recortados, de manera que el resultado se puede valorar visualmente de inmediato. De este modo se elimina por completo el riesgo de crash, porque la API de malla de QGIS ya no se utiliza.

### Actualizacion: recorte del poligono con diagnostica visible

Cuando se selecciona una capa en el combo **Capa Poligono** junto con los dos DEMs, el recorte de los rasters sobre el poligono se **registra ahora en la barra de mensajes de QGIS**: en caso de exito se muestra la lista de los archivos recortados escritos en disco, mientras que en caso de fallo se indica el motivo concreto (por ejemplo poligono en un CRS distinto al de los DEMs, ninguna interseccion geometrica entre poligono y raster, archivo de origen no encontrado o ilegible). De este modo es inmediato comprender por que no se aplico un recorte y que corregir (reproyectar el poligono, moverlo sobre el area de los DEMs, revisar la ruta del archivo), sin tener que abrir logs ni la consola de Python.

### Actualizacion: recorte del poligono tambien en modo "DEM sobre Poligono"

El recorte del poligono funciona ahora tambien cuando se selecciona el radio button **DEM sobre Poligono** (modo zonal-stats con un solo DEM): el raster se recorta a la extension del poligono **antes** de ser pasado a los visores **Mostrar 2D**, **Mostrar 3D** y **Exportar 2DM + 3D**, de modo que la seccion y la vista 3D muestran unicamente el area de intervencion en lugar del DEM completo como ocurria antes. El mensaje de diagnostica del recorte aparece en la **barra de mensajes de QGIS** exactamente igual que en el modo Diferencia DEM. En este escenario con un solo DEM, el visor **Mostrar 2D** se adapta automaticamente: el heat-map muestra las cotas con una rampa de color **terrain**, el histograma representa la distribucion de cotas con la linea de la media, y las dos secciones longitudinal/transversal dibujan una sola linea de cota (sin relleno entre pre y post, porque no existe DEM post).

### Actualizacion: Analisis de Costes del Computo Metrico

En el panel Computo Metrico del Panel de Obra se ha anadido un nuevo bloque **Analisis de Costes** con dos parametros de entrada: **Coste unitario** (en euros/m3) y **Productividad** (en m3/dia). Cada vez que se pulsa **Calcular**, el panel actualiza automaticamente tres valores derivados visibles de un vistazo: **Coste total** (volumen x coste unitario), **Dias estimados** (volumen / productividad) y **Coste diario** (coste unitario x productividad). Ambos inputs se guardan automaticamente **por sitio** en la configuracion de QGIS (claves `pyArchInit/site_dashboard/costs/<sitio>/...`), por lo que solo es necesario introducirlos una vez para cada obra: al cambiar de sitio los valores guardados se recargan automaticamente, y los tres totales se recalculan en tiempo real con cada nuevo computo.

### Actualizacion: recorte pre/post alineado

El calculo de la diferencia DEM requiere que los dos DEM (pre y post) esten exactamente alineados sobre la misma cuadricula de pixeles. En versiones anteriores, al usar un poligono de recorte, los dos DEM recortados podian terminar en cuadriculas ligeramente diferentes y el calculo `pre - post` resultaba erroneo o vacio. Ahora ambos recortes utilizan la **resolucion nativa del DEM pre** como referencia (misma `xRes` / `yRes` y misma alineacion de cuadricula), de modo que los dos rasters recortados coinciden siempre a nivel de pixel y la diferencia produce un resultado valido. Incluso las trincheras minimas en las que se han retirado solo "10 cubos de tierra" (aproximadamente 1 m3) se capturan ahora correctamente en el computo.

### Actualizacion: nuevo combo "Muros / Estructuras"

En el panel Computo Metrico se ha anadido un segundo combo **Muros / Estructuras** que permite seleccionar una capa de poligonos que representan muros, estructuras en alzado, pilares u otras partes construidas que **no deben contarse** en el calculo de los metros cubicos de excavacion. Cuando se pulsa **Calcular**, los poligonos de los muros se rasterizan como NODATA sobre el raster de diferencia recortado y sus celdas se excluyen del total de volumen; la diagnostica aparece en la barra de mensajes de QGIS (por ejemplo `walls masked: muri_trincea_42`). Flujo de trabajo arqueologico tipico: cargar DEM pre + DEM post + poligono del area de excavacion + poligono de los muros hallados, seleccionarlos ambos en los dos combos y pulsar **Calcular** -- el volumen excavado excluye automaticamente el volumen de las estructuras.

---

## Exportacion PDF y CSV del Panel

El Panel de Obra permite exportar un resumen completo de los datos de gestion en dos formatos: **PDF** (documento paginado, ideal para entrega a cliente o archivo) y **CSV** (ideal para analisis posteriores en Excel u otras hojas de calculo).

### Exportacion PDF

El boton **Exportar PDF** genera un informe completo del estado de la obra. A partir de la version 5.1 el PDF incluye:

- **Portada renovada** con nombre del sitio, ano de referencia y fecha de generacion
- **Resumen de presupuesto** con tablas detalladas por categoria y totales (previsto vs efectivo)
- **Resumen de personal** con estadisticas de asistencia, horas trabajadas y costes
- **Resumen de equipamiento** con estado del inventario y mantenimientos vencidos
- **Nueva seccion "Computo Metrico"** con:
  - Tabla detallada de todos los calculos guardados
  - **Totales**: area total (m2) y volumen total (m3)
  - **Estadisticas**: volumen de excavacion, volumen de relleno, area afectada
- **Nueva seccion "Analisis de Costes"** (insertada entre **Computo Metrico** y **Estadisticas**) con una tarjeta de parametros de los valores configurados (coste unitario en euros/m3 y productividad en m3/dia), tabla detallada por registro (fecha, tipo, volumen, coste, dias estimados, coste diario) y fila de **totales** al final de la tabla; el bloque **Estadisticas** se ha extendido con **coste total** y **dias totales** de obra
- **Soporte completo de caracteres especiales**: el renderizado del PDF ha sido corregido para todos los idiomas soportados, incluidas las letras acentuadas del rumano (**a**, **a**, **i**, **s**, **t**), los caracteres **griegos**, **arabes**, **portugueses** y **catalanes**.

### Exportacion CSV

El boton **Exportar CSV** genera un archivo CSV compatible con las principales hojas de calculo. A partir de la version 5.1:

- **Codificacion UTF-8 con BOM**: garantiza que Excel (especialmente la version europea) abra el archivo correctamente sin corromper las letras acentuadas y los caracteres especiales
- **Separador `;`** (punto y coma): compatible con la configuracion regional europea de Excel
- **Seccion COMPUTO METRICO**: incluye todos los datos de computo metrico, con tipologia, area, volumen y notas de cada calculo
- **Nueva seccion `=== ANALISIS DE COSTES ===`**: comienza con los dos parametros (coste unitario en euros/m3 y productividad en m3/dia) y a continuacion la tabla detallada por registro (fecha, tipo, volumen, coste, dias estimados, coste diario), lista para ser filtrada o agregada en Excel
- **Bloque SUMMARY final ampliado**: un resumen agregado con totales y estadisticas, util para analisis rapidos sin tener que escribir formulas; ahora incluye tambien **Coste total** y **Dias totales** calculados a partir del nuevo Analisis de Costes

<!-- IMAGE: PDF exportado con la nueva seccion Computo Metrico -->
> **Fig. 16**: PDF exportado con la nueva seccion **Computo Metrico** (tabla, totales y estadisticas)

<!-- IMAGE: CSV exportado abierto en Excel con la seccion COMPUTO METRICO y el bloque SUMMARY -->
> **Fig. 17**: CSV exportado abierto en Excel con la seccion **COMPUTO METRICO** y el bloque final **SUMMARY**

---

## Flujo de trabajo operativo

### Configuracion inicial

1. **Crear el sitio** en la Ficha de Sitio (ver [Tutorial Ficha de Sitio](02_ficha_sitio.md))
2. **Registrar el personal**: abrir Personal, crear un registro por trabajador con cualificacion, rol y coste diario
3. **Crear el presupuesto**: abrir Presupuesto, insertar las partidas con importes previstos
4. **Registrar el equipamiento**: abrir Equipamiento, registrar cada equipo con estado y fechas de mantenimiento
5. **Verificar en el Panel de Obra**: seleccionar sitio y ano, comprobar que los indicadores reflejan los datos

### Gestion diaria

- **Asistencia**: registrar la jornada de cada trabajador (tipo, horas, coste)
- **Presupuesto**: actualizar el importe efectivo cuando se produce un gasto
- **Equipamiento**: actualizar el estado cuando un equipo entra o sale de mantenimiento
- **Panel de Obra**: consultar los indicadores para verificar el estado general del proyecto

<!-- IMAGE: Diagrama del flujo de trabajo diario con los formularios interconectados -->
> **Fig. 12**: El flujo de trabajo diario: asistencia, presupuesto y equipamiento

---

## Preguntas frecuentes (FAQ)

**P: Es necesario crear el sitio antes de usar el modulo?**
R: Si. Todos los formularios requieren un sitio previamente registrado en la Ficha de Sitio.

**P: Funciona con SQLite y PostgreSQL?**
R: Si. Todas las funcionalidades estan disponibles en ambos motores de base de datos.

**P: Como se vincula un registro de asistencia a un trabajador?**
R: El campo **ID Personal** del formulario de Asistencia se vincula al identificador unico del registro en el formulario de Personal.

**P: El coste de la jornada se calcula automaticamente?**
R: Si, a partir del coste diario del trabajador y las horas registradas. Tambien se puede insertar manualmente.

**P: Que sucede cuando un equipo tiene el mantenimiento vencido?**
R: El Panel de Obra muestra una alerta en rojo en la seccion de Equipamiento.

**P: Que ocurre si el importe efectivo supera el previsto?**
R: La barra de progreso del Panel de Obra cambia a rojo, indicando sobrecosto.

**P: Se puede tener presupuesto para varios anos?**
R: Si. Cada partida tiene un campo de ano. Se filtran desde el selector del Panel de Obra.

---

## Notas tecnicas

### Tablas de base de datos

| Formulario | Tabla |
|------------|-------|
| Personal | `cantiere_personale_table` |
| Asistencia | `cantiere_presenze_table` |
| Equipamiento | `cantiere_attrezzature_table` |
| Presupuesto | `cantiere_budget_table` |

### Archivos fuente

| Archivo | Descripcion |
|---------|-------------|
| `tabs/Cantiere_Dashboard.py` | Controlador del Panel de Obra |
| `tabs/Cantiere_Personale.py` | Controlador del formulario de Personal |
| `tabs/Cantiere_Presenze.py` | Controlador del formulario de Asistencia |
| `tabs/Cantiere_Attrezzature.py` | Controlador del formulario de Equipamiento |
| `tabs/Cantiere_Budget.py` | Controlador del formulario de Presupuesto |
| `gui/ui/Cantiere_*.ui` | Disenos de interfaz Qt Designer |

### Compatibilidad

| Componente | Version minima |
|------------|---------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| SQLite | 3.x |
| PostgreSQL | 12+ |

---

*Documentacion PyArchInit - Gestion de Obra*
*Version: 5.0.x*
*Ultima actualizacion: Febrero 2026*
