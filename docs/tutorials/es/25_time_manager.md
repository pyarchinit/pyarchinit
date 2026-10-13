# Tutorial 25: Time Manager (GIS Time Controller)

## Introducción

El **Time Manager** (GIS Time Controller) es una herramienta avanzada para visualizar la secuencia estratigráfica en el tiempo. Permite "navegar" a través de los niveles estratigráficos usando un control temporal, visualizando progresivamente las UE desde la más antigua a la más reciente (la formación del sitio).

### Funcionalidades Principales

- Visualización progresiva de los niveles estratigráficos
- Control mediante dial/slider
- Modo acumulativo o nivel individual
- Impresión automática de las láminas del atlas, una por nivel
- Integración con Matrix de Harris

## Acceso

### Desde el Menú
**PyArchInit** → **Time Manager**

### Prerrequisitos

- Capa con campo `order_layer` (índice estratigráfico)
- UE con order_layer completado
- Capas cargadas en QGIS

## Interfaz

### Panel Principal

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Capas disponibles:                                |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] otra_capa                                    |
+--------------------------------------------------+
|              [Dial Circular]                     |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Nivel: [SpinBox: 0-N]                   |
+--------------------------------------------------+
| [x] Modo Acumulativo (muestra <= nivel)         |
+--------------------------------------------------+
| [ ] Mostrar matriz                               |
| [Atlas Imprimir Tablas de Período]               |
| [Detener proceso de impresión]                   |
+--------------------------------------------------+
| [Preview Matrix/Imagen]                          |
+--------------------------------------------------+
```

### Controles

| Control | Función |
|---------|---------|
| Checkbox Capa | Selecciona capa a controlar |
| Dial | Navega entre los niveles (rotación) |
| SpinBox | Introducción directa del nivel |
| Modo Acumulativo | Muestra todos los niveles hasta el seleccionado |
| Mostrar matriz | Visualiza Matrix de Harris sincronizado |

## Campo order_layer

### ¿Qué es order_layer?

El campo `order_layer` define el orden estratigráfico de visualización:
- **0** = Nivel más antiguo (profundo)
- **N** = Nivel más reciente (superficial)

Es la convención del botón **Orden estratigráfico** con la casilla "Orden: Antiguo → Reciente" activa (configuración predeterminada, ver Tutorial 03): si la ordenación se calculó al revés, el Time Manager y el mapa muestran la secuencia invertida.

### Completar order_layer

En la Ficha de UE, pestaña **Ayuda** → **Tool Box**, el botón **Orden estratigráfico** calcula `order_layer` a partir de las relaciones estratigráficas (ver Tutorial 03); el valor de la UE actual aparece en el campo bajo el botón. Reglas:
1. 0 a las UE más antiguas, valores crecientes hacia las más recientes (en superficie)
2. UE contemporáneas pueden tener el mismo valor
3. Seguir la secuencia del Matrix

### Ejemplo

| UE | order_layer | Descripción |
|----|-------------|-------------|
| US001 | 4 | Humus superficial |
| US002 | 3 | Estrato de arado |
| US003 | 2 | Derrumbe |
| US004 | 1 | Plano de uso |
| US005 | 0 | Cimentación |

Desde la 5.13.19-alpha las capas de UE y USM que pyArchInit carga en el mapa (ver Tutorial 14, *Elección del Estilo*) se dibujan en el mismo orden que usa el Time Manager: por cronología del período y después por `order_layer` (0 = más antiguo), de modo que las unidades más recientes quedan encima.

## Modos de Visualización

### Modo Nivel Individual

Checkbox **NO** activo:
- Muestra SOLO las UE del nivel seleccionado
- Útil para aislar estratos individuales
- Visualización "por capas"

### Modo Acumulativo

Checkbox **ACTIVO**:
- Muestra todas las UE desde el nivel 0 (más antiguo) hasta el seleccionado
- Muestra la formación del sitio, de las UE más antiguas a las más recientes
- Visualización más realista

## Integración con Matrix

### Visualización Sincronizada

Con checkbox **"Mostrar matriz"** activo:
- El Matrix de Harris aparece en el panel
- Se actualiza en sincronía con el nivel
- Resalta las UE del nivel actual

### Generación de Imágenes

El Time Manager puede generar:
- Una lámina por cada nivel, maquetada con la plantilla de layout elegida (imagen JPG)
- La matriz de Harris de ese nivel dentro de la lámina, si **Mostrar matriz** está activo

## Impresión de las Láminas

### Proceso

1. Seleccionar capas a incluir
2. Activar **Mostrar matriz** si la matriz debe aparecer en las láminas (si no, la imagen de la matriz de la plantilla queda oculta)
3. Hacer clic en **Atlas Imprimir Tablas de Período**
4. En la ventana que se abre, elegir la plantilla de layout (véase la nota «Qué plantilla elegir» al final) y confirmar
5. Elegir la carpeta donde guardar las láminas
6. Responder a la pregunta de si abrir el Layout Designer para retocar la plantilla antes de empezar
7. Esperar: una barra de progreso muestra la lámina en curso y, al terminar, un mensaje dice dónde se han guardado
8. Para detener la generación, hacer clic en **Detener proceso de impresión**: las láminas ya escritas se quedan en la carpeta

### Output

- Una `Tavola_N.jpg` por cada nivel (N es el valor de `order_layer`), en la carpeta elegida: el mapa en ese nivel, en el modo activo (acumulativo o nivel individual)
- El título «Tavola N» y la imagen de la matriz aparecen si la plantilla los prevé (la matriz solo con **Mostrar matriz** activo)
- Los niveles en los que ninguna UE tiene la datación rellenada se omiten: esos números faltan en la secuencia de archivos
- Con una plantilla de dos páginas cada nivel produce dos imágenes, la segunda es `Tavola_N_2.jpg` (véase la nota «Hacer apta cualquier plantilla» al final)

**Etiquetas de la lámina.** Mientras genera las láminas del atlas, el Time Manager pone en las capas elegidas las etiquetas de la lámina —el número de la unidad en un círculo en las UE, la cota en los puntos— y las quita al terminar la generación, devolviendo las que había antes. Desde la 5.13.110-alpha las quita en cualquier caso, incluso si una lámina falla: antes, en ese caso, se quedaban en las capas del proyecto y acababan en el archivo del proyecto al guardarlo.

## Workflow Típico

### 1. Preparación

```
1. Abrir proyecto QGIS con capas de UE
2. Verificar que order_layer esté completado
3. Abrir Time Manager
```

### 2. Selección de Capas

```
1. Seleccionar las capas a controlar
2. Normalmente: pyunitastratigrafiche y/o _usm
```

### 3. Navegación

```
1. Usar el dial o spinbox
2. Observar el cambio de visualización
3. Activar/desactivar modo acumulativo
```

### 4. Documentación

```
1. Activar "Mostrar matriz"
2. Imprimir las láminas con "Atlas Imprimir Tablas de Período"
3. Revisar los archivos Tavola_N.jpg en la carpeta elegida
```

## Plantillas de Layout

### Carga de Plantilla

El Time Manager soporta plantillas QGIS para:
- Layouts de impresión personalizados
- Encabezados y leyendas
- Formatos estándar

### Plantillas Disponibles

La ventana de elección lista los archivos `.qpt` encontrados en la carpeta del plugin, en `resources/dbfiles/` y en `~/pyarchinit_5/bin/profile/template/`:
- `layout_TimeManager`: la plantilla del Time Manager, con el título «Tavola N» y la imagen de la matriz
- las plantillas de impresión del perfil de pyArchInit (por ejemplo las «Modello adArte…»)
- cualquier otro `.qpt`, elegido con el botón **Sfoglia...** (Examinar)

## Buenas Prácticas

### 1. order_layer

- Completar ANTES de usar Time Manager
- Usar valores consecutivos
- UE contemporáneas = mismo valor

### 2. Visualización

- Comenzar desde el nivel 0 (más antiguo)
- Proceder en orden creciente
- Usar modo acumulativo para presentaciones

### 3. Documentación

- Capturar pantalla en niveles significativos
- Documentar cambios de fase
- Imprimir las láminas para las memorias (una por nivel)

## Resolución de Problemas

### Capas No Visibles en la Lista

**Causa**: Capa sin campo order_layer

**Solución**:
- Añadir campo order_layer a la capa
- Rellenarlo con valores apropiados

### Sin Cambio Visual

**Causas**:
- order_layer no completado
- Filtro no aplicado

**Soluciones**:
- Verificar valores order_layer en las UE
- Controlar que la capa esté seleccionada

### El Dial No Responde

**Causa**: Ninguna capa seleccionada

**Solución**: Seleccionar al menos una capa de la lista

## Referencias

### Archivos Fuente
- `tabs/Gis_Time_controller.py` - Interfaz principal
- `gui/ui/Gis_Time_controller.ui` - Layout UI

### Campo de Base de Datos
- `us_table.order_layer` - Índice estratigráfico

---

## Video Tutorial

### Time Manager
`[Placeholder: video_time_manager.mp4]`

**Contenidos**:
- Configuración de order_layer
- Navegación temporal
- Generación de video
- Integración con Matrix

**Duración prevista**: 15-18 minutos

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/pyarchinit_timemanager_animation.html)

---

## La matriz, desde la 5.13.44

La matriz del Time Manager ya no pasa por Graphviz. La dibuja el mismo motor de composición del panel **Ver la matriz**, dentro de QGIS y sin subprocesos.

- **Es inmediata.** En el sitio de ejemplo (51 UE, 81 relaciones) el dibujo cuesta unos milisegundos en lugar de unas tres décimas de segundo, y han desaparecido los procesos `dot` y `tred` que a veces se quedaban colgados. Los periodos del sitio se leen **una sola vez**: antes se releían con una consulta por cada área y por cada periodo, en cada clic del dial.
- **En el atlas la matriz es vectorial.** La imagen de la lámina es un SVG de unas decenas de KB en lugar de un JPEG de megabytes.
- **Es la misma matriz** del panel Extended Matrix: mismas bandas de periodo, misma simbología, misma reducción de redundancias. Las flechas que **suben** las bandas — donde la estratigrafía contradice la cronología — se dibujan en **rojo**.
- La matriz sigue conteniendo solo las UE visibles en la posición actual del dial.

- Las UE que **no son visibles** en la posición actual pero que una relación menciona entran igualmente en el dibujo, **atenuadas**: sin ellas la secuencia parecería rota, y dibujadas como las demás parecerían estar en el mapa.

> **Qué plantilla elegir.** En el selector cada plantilla está marcada: **✓** tiene el título y la imagen de la matriz (la del Time Manager), **•** solo el mapa — las láminas salen más sobrias pero salen — **✗** no tiene mapa. Antes elegir una sin esos elementos hacía que el generador volviera atrás sin decir nada.

> **Hacer apta cualquier plantilla.** Con `scripts/prepare_atlas_templates.py` (ejecutado con el Python de QGIS) se escribe junto a cada plantilla una copia con el sufijo « + Time Manager» que lleva el título y la imagen de la matriz en una **página nueva**. Los originales no se tocan. Cada nivel produce entonces dos imágenes.
