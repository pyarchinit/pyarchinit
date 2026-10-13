# Tutorial 14: SIG y Cartografía

## Introducción

PyArchInit está profundamente integrado con **QGIS**, aprovechando todas sus funcionalidades SIG para la gestión espacial de los datos arqueológicos. Este tutorial cubre la integración cartográfica, las capas predefinidas y las funcionalidades avanzadas como la **segmentación automática SAM**.

### Funcionalidades SIG Principales

- Visualización de UE en mapa
- Capas vectoriales predefinidas
- Estilos QML personalizados
- Cotas y mediciones SIG
- Segmentación automática (SAM)
- Exportación cartográfica

## Capas Predefinidas de PyArchInit

### Capas Vectoriales Principales

| Capa | Geometría | Descripción |
|------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | UE de depósito |
| `pyunitastratigrafiche_usm` | MultiPolygon | UE murarias |
| `pyarchinit_quote` | Point | Puntos de cota |
| `pyarchinit_siti` | Point | Localización de sitios |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Áreas de excavación |
| `pyarchinit_strutture_ipotesi` | Polygon | Estructuras hipotéticas |
| `pyarchinit_documentazione` | Point | Referencias de documentación |

### Atributos de Capa UE

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `gid` | Integer | ID único |
| `scavo_s` | Text | Nombre del sitio |
| `area_s` | Text | Número de área |
| `us_s` | Text | Número de UE |
| `stratigraph_index_us` | Integer | Índice estratigráfico |
| `tipo_us_s` | Text | Tipo de UE |
| `rilievo_originale` | Text | Levantamiento de origen |
| `disegnatore` | Text | Autor del levantamiento |
| `data` | Date | Fecha del levantamiento |

## Visualización de UE en Mapa

### Desde la Pestaña "Map" en la Ficha de UE

1. Abrir una ficha de UE
2. Seleccionar la pestaña **Map**
3. Funciones disponibles:

| Botón | Función |
|-------|---------|
| View US | Visualiza UE actual en mapa |
| View All | Visualiza todas las UE del área |
| New Record | Crear nueva geometría |
| Pan to | Centrar mapa en UE |

### Visualización desde Búsqueda

1. Ejecutar una búsqueda de UE
2. Botón **"View Record"** → visualiza individual
3. Botón **"View All"** → visualiza todos los resultados

### Elección del Estilo (UE y USM)

Cuando las UE o las UE murarias (USM) de los resultados de búsqueda se cargan en el mapa aparece la ventana **Style Choice** ("How do you want to manage the layer style?"). Los botones se muestran en inglés:

| Botón | Efecto |
|-------|--------|
| **Save new style** | Crea el estilo según el campo elegido y lo guarda en la base de datos con un nombre |
| **Load existing style** | Usa como plantilla un estilo ya preparado, elegido de una lista (ver abajo), y crea el estilo según el campo elegido sin guardarlo en la base de datos |
| **Use temporary style** | Crea el estilo según el campo elegido sin guardarlo en la base de datos |
| **Single symbol (outline only)** | Dibuja solo el contorno de las geometrías, sin relleno |

Desde la 5.13.19-alpha **Load existing style** abre la ventana **Existing style** ("Choose the style to use as a template:", en inglés) con la lista de los estilos disponibles: los estilos guardados en la base de datos (*Database: nombre*), los estilos QML incluidos en pyArchInit (`us_*.qml`, listados como *pyArchInit: …*) y **Other QML file…**, para elegir cualquier archivo `.qml`. El estilo elegido se carga en la capa (la transparencia y el modo de fusión vienen con él, las etiquetas no: en las vistas US y USM de polígonos son, desde la 5.13.110-alpha, las del párrafo **Etiquetas** más abajo, el número de la unidad en círculo, diga lo que diga el estilo usado como plantilla) y sirve de **plantilla**: tras elegir el campo de categorización, los valores que el estilo ya tiene conservan su color y su símbolo, los demás reciben una copia de su símbolo con un color propio. Si se cancela la elección, funciona como **Use temporary style**. Antes solo buscaba entre los estilos de la base de datos y, si no encontraba ninguno, pasaba directamente a la ventana de categorización.

Con **Save new style**, **Load existing style** y **Use temporary style** se elige después el campo de categorización (ventana **Seleccionar Campo de Categorización**): **Definición Estratigráfica**, **Tipo UE**, **Definición Interpretativa** o **Período/Fase (cont_per)** (desde la 5.13.19-alpha); cada valor del campo recibe su propio color, que desde la 5.13.19-alpha es el mismo cada vez que se carga la capa. Con **Período/Fase (cont_per)** la entrada de la leyenda de cada código muestra también la datación del período/fase tomada de la periodización. Solo aparecen los campos presentes en la capa.

**Orden de dibujo.** Desde la 5.13.19-alpha las unidades se dibujan en el orden que usa el Time Manager: primero las que no tienen período, luego por cronología del período (según la periodización del período/fase inicial de la UE, o según `cont_per`), después por `order_layer` (0 = más antiguo) y por último el corte sobre su relleno, de modo que las unidades más recientes quedan encima. Vale para todas las opciones de estilo, también para **Single symbol (outline only)**. Cuando las capas se cargan período por período, el estilo se pide una sola vez y se usa para todos los períodos.

**Etiquetas.** Desde la 5.13.110-alpha, con el estilo elegido la vista US (y USM) recibe también sus **etiquetas**: el número de la unidad en **negrita dentro de un círculo blanco con borde rojo oscuro**, **una por unidad**, en su dibujo más grande si se ve (no cubierto por entero por uno de nivel superior), con la misma receta de las láminas del atlas del Time Manager (tutorial 25). Cuando dos números se taparían, uno se desplaza y una línea de llamada lo une a su dibujo. Vale para UE y USM, con SQLite y con PostgreSQL, y para todas las opciones de estilo, también para **Single symbol (outline only)**; si el estilo cargado con **Load existing style** ya tenía etiquetas, el número en círculo ocupa su lugar. Las capas de puntos, como las cotas, no reciben etiquetas desde aquí.

Desde la 5.13.18-alpha el estilo elegido (y el campo de categorización) se respeta también con las bases de datos SQLite, tanto para las UE como para las USM; antes el mapa salía siempre con un color para cada UE.

## Estilos de las Capas

### Archivos QML

PyArchInit incluye estilos predefinidos en formato QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicación del Estilo

1. Seleccionar la capa en la leyenda
2. Clic derecho → **Propiedades**
3. Pestaña **Estilo**
4. **Cargar estilo** → seleccionar QML

### Personalización

Los estilos pueden personalizarse para:
- Colores según tipo de UE
- Etiquetas con número de UE
- Transparencia
- Bordes y rellenos

## Cotas y Mediciones

### Capa de Cotas

La capa `pyarchinit_quote` almacena:
- Coordenadas X, Y
- Cota Z (absoluta)
- Tipo de punto de cota
- UE de referencia
- Área de referencia

### Cálculo Automático de Cotas

Desde la Ficha de UE, las cotas mín/máx se calculan:
1. Query a los puntos de cota asociados a la UE
2. Extracción del valor mínimo y máximo
3. Visualización en el informe

### Inserción de Cotas

1. Capa de cotas en edición
2. Dibujar punto en el mapa
3. Completar atributos:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentación Automática SAM

### ¿Qué es SAM?

**SAM (Segment Anything Model)** es el modelo de inteligencia artificial de Meta que divide una imagen en sus objetos. En pyArchInit la ventana SAM convierte una imagen en **polígonos**, a partir de:

- una **ortofoto** (un archivo ráster: GeoTIFF, JPEG georreferenciado…);
- o una **capa de teselas o un servicio** cargado en QGIS: XYZ como ESRI World Imagery o Google, WMS, ArcGIS REST.

No solo piedras: también **edificios, carreteras, campos, ríos, muros**. Los modelos son de dos familias:

- **SAM 2.1** (Meta) encuentra los contornos de los objetos —todos, o los que se indiquen con puntos, un rectángulo o un polígono—, pero no dice qué son;
- las **clases de texto** (YOLOE-26 en local, SAM 3 en la nube) buscan lo que se escribe («building, road, river, field») y cada polígono lleva su etiqueta.

Los polígonos van a la capa que se elija: las capas de UE de pyArchInit, cualquier capa de polígonos del proyecto o una capa temporal nueva.

### Acceso a la Función

1. Desde la barra de herramientas de pyArchInit: botón desplegable **Herramientas de análisis** (Analysis Tools) → «SAM - Segmentation (stones, buildings, roads, fields…)». Es la acción predeterminada del botón: un clic en el icono abre directamente la ventana.
2. O desde el menú **pyArchInit** → «SAM - Segmentation (stones, buildings, roads, fields…)».

La ventana se titula «SAM — Segmentation (stones, buildings, roads, fields, rivers…)». Sus etiquetas solo existen en italiano y en inglés: con QGIS en español aparece en inglés, como en el esquema. A continuación, cada etiqueta traducida va seguida de la inglesa entre paréntesis.

### Interfaz SAM

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Cinco grupos, que se rellenan de arriba abajo: «Entorno local» (*Local environment*), «Imagen» (*Image*), «Qué segmentar» (*What to segment*), «Modelo» (*Model*), «Destino» (*Target*). Debajo están la línea de estado («Listo», *Ready*), donde también aparecen los mensajes del trabajo en curso, y los botones «Iniciar» (*Start*), «Cancelar» (*Cancel*, visible solo durante el trabajo) y «Cerrar» (*Close*). Algunas filas solo aparecen cuando hacen falta: «Clave API:» (*API key:*) en lugar del estado de los pesos para los modelos en la nube; «Sitio:» (*Site:*), «Área:» (*Area:*), «Índice estratigráfico:» (*Stratigraphic index:*) y «Tipo de UE:» (*US type:*) para las capas de UE; «Campo para la etiqueta:» (*Field for the label:*) para las demás capas. La ventana recuerda la última área de UE, las clases, el lado máximo, el modelo elegido y las claves API.

Las entradas de la lista de modelos están siempre escritas en italiano («Locale» = local), igual que algunos mensajes de servicio citados más abajo.

#### Entorno local

Los modelos locales (SAM 2.1 y YOLOE) no se ejecutan en el Python de QGIS, sino en un **Python separado**, que la ventana crea y comprueba por sí misma. Al abrirse, el grupo muestra «comprobando…» (*checking…*) y después:

- en verde «listo — ultralytics …, torch …, mps» (*ready — …*): el entorno está instalado; la última palabra es el dispositivo de cálculo (`mps`, `cuda` o `cpu`);
- en naranja «no instalado: necesario para los modelos locales (SAM 2.1, YOLOE). Un Python del sistema 3.10–3.13, ~1,5 GB de paquetes.» (*not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.*).

«Instalar / actualizar» (*Install / update*) crea el entorno o actualiza sus paquetes (véase más abajo «Instalación Local de SAM»); «Mostrar registro» (*Show log*) abre y cierra el registro de la instalación, con la salida de pip línea a línea. Los modelos en la nube no necesitan el entorno.

#### Imagen

- «Capa ráster:» (*Raster layer:*): la imagen que se va a segmentar, elegida entre los ráster del proyecto: una ortofoto (archivo) o una capa de teselas/servicio. Debajo, en gris, se indica cuál de los dos es: nombre del archivo y tamaño en píxeles (`orthophoto.tif — 12000 × 9000 px`) o el tipo de servicio, renderizado desde la vista (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)`; esta línea está en italiano, *reso dalla vista* = renderizado desde la vista).
- «Extensión:» (*Area:*): «vista actual» (*current view*, lo que se ve en el mapa) o «ráster completo» (*whole raster*). «ráster completo» solo se puede elegir para los archivos: un servicio de teselas no tiene borde, así que se trabaja siempre sobre la vista (o sobre un rectángulo o un polígono).
- «Resolución (unidades de mapa/px):» (*Resolution (map units/px):*): solo para las teselas: cuántas unidades de mapa (metros, o grados si el mapa está en coordenadas geográficas) por cada píxel de la imagen renderizada. El valor propuesto es el de la vista al abrir la ventana o al elegir la capa: si después se cambia el zoom, hay que corregirlo a mano. Cuanto más pequeño, más detalle.
- «Lado máximo (px):» (*Max side (px):*): el lado más largo de la imagen que se pasa al modelo: 2048 por defecto, de 512 a 8192. Por encima de ese lado la imagen se reduce; SAM trabaja de todos modos a 1024 px internos.

### Modos de Segmentación

El grupo «Qué segmentar» (*What to segment*) ofrece seis modos. Al elegir un modo cambia la lista de modelos (véase «Modelos Disponibles») y debajo aparece, en azul, la instrucción de ese modo.

#### 1. Todo automático

«Todo (automático)» (*Everything (automatic)*): SAM 2.1 segmenta cada objeto que encuentra en la «Extensión:» elegida («vista actual» o «ráster completo»). Los polígonos no tienen clase: en la capa temporal reciben la etiqueta «segment». Se lanza con «Iniciar» (*Start*).

#### 2. Puntos

«Puntos: haz clic en los objetos del mapa» (*Points: click the objects on the map*): pulsar «Iniciar la selección» (*Start selection*); la ventana se oculta y la barra de mensajes de QGIS recuerda los comandos. Hacer clic en los objetos uno a uno: cada clic es un objeto. Clic derecho o Intro para terminar, Retroceso quita el último punto, Esc cancela. La ventana vuelve a aparecer y la segmentación se ejecuta sobre la «Extensión:» elegida, un objeto por punto; los puntos fuera de la imagen se ignoran.

#### 3. Rectángulo

«Rectángulo: dibuja un rectángulo» (*Box: draw a rectangle*): pulsar «Iniciar la selección» y arrastrar un rectángulo en el mapa (Esc o clic derecho cancela). La imagen se recorta al rectángulo y se segmenta todo lo que hay dentro.

#### 4. Polígono

«Polígono: dibuja el área» (*Polygon: draw the area*): pulsar «Iniciar la selección» y hacer clic en los vértices; clic derecho, Intro o doble clic cierran el polígono (hacen falta al menos tres vértices), Retroceso quita el último vértice, Esc cancela. Solo se segmenta el interior del polígono.

#### 5. Polígono desde capa

«Polígono desde capa:» (*Polygon from layer:*): elegir una capa de polígonos en el desplegable de al lado. Se usa la entidad seleccionada de la capa, o todas si no hay ninguna seleccionada (varias entidades se unen en una). Como con el polígono dibujado, solo se segmenta el interior: útil para trabajar dentro de un sondeo, un área de excavación o un límite ya dibujado. Se lanza con «Iniciar».

#### 6. Clases de texto

«Clases de texto:» (*Text classes:*): escribir en el campo de al lado qué buscar: palabras en **inglés** separadas por comas (por defecto «building, road, river, field»; otros ejemplos: stone, wall). Cada clase se convierte en una etiqueta de los polígonos. Funciona con YOLOE-26 en local o con SAM 3 de Roboflow en la nube, sobre la «Extensión:» elegida. Se lanza con «Iniciar».

**«Umbral:»** (*Threshold:*; 0,30 por defecto, de 0,05 a 0,95) es la confianza mínima para que un resultado se conserve: más bajo da más polígonos, también inciertos; más alto da menos, pero más seguros. El modelo en la nube de Replicate no lo usa.

### Modelos Disponibles

El grupo «Modelo» (*Model*) tiene un desplegable «Modelo:» (*Model:*) cuyo contenido depende del modo elegido:

| Modelo | Tipo | Requisitos | Modos |
|--------|------|------------|-------|
| SAM 2.1 Tiny | Local | entorno local + pesos ~78 MB | todos salvo las clases de texto; el más ligero y rápido |
| SAM 2.1 Small | Local | entorno local + pesos ~92 MB | todos salvo las clases de texto |
| SAM 2.1 Base+ | Local | entorno local + pesos ~162 MB | todos salvo las clases de texto |
| SAM 2.1 Large | Local | entorno local + pesos ~449 MB | todos salvo las clases de texto; el más preciso y el más lento |
| Cloud: Replicate SAM-2 | Nube | clave API de Replicate | solo segmentación automática (en el modo «Puntos» los clics se ignoran, con un aviso) |
| YOLOE-26 S | Local | entorno local + pesos ~31 MB + MobileCLIP2 254 MB (una vez) | clases de texto |
| YOLOE-26 M | Local | entorno local + pesos ~70 MB + MobileCLIP2 254 MB (una vez) | clases de texto |
| YOLOE-26 L | Local | entorno local + pesos ~79 MB + MobileCLIP2 254 MB (una vez) | clases de texto |
| Cloud: Roboflow SAM 3 | Nube | clave API de Roboflow | clases de texto |

En el desplegable las entradas se leen así: «Locale: SAM 2.1 Tiny — ~78 MB», «Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB», «Cloud: Replicate SAM-2 (solo automatico, chiave API)», «Cloud: Roboflow SAM 3 (classi a testo, chiave API)» (*locale* = local, *classi a testo* = clases de texto, *solo automatico* = solo automático, *chiave* = clave).

**Pesos.** Para un modelo local, bajo el desplegable aparece el estado de los pesos: «pesos presentes ✓» (*weights present ✓*, verde) o «faltan los pesos (~N MB)» (*weights missing (~N MB)*, naranja), con el botón «Descargar pesos» (*Download weights*). La descarga, con barra de progreso, toma los archivos de los assets públicos de ultralytics en GitHub (no hace falta cuenta). Para YOLOE se descarga también el codificador de texto MobileCLIP2 (254 MB), una sola vez para S, M y L. Los pesos se guardan en `~/pyarchinit_5/bin/models/sam/`.

**Clave API.** Para un modelo en la nube, el campo «Clave API:» (*API key:*) y el enlace para obtenerla sustituyen al estado de los pesos (véase «Configuración de API»).

### SAM-3 con Text Prompt

Con el modo «Clases de texto» no se pide «divídelo todo», sino «encuentra estas cosas»:

- se escriben una o varias clases en inglés, separadas por comas: `building, road, river, field`, o bien `stone, wall`…;
- **YOLOE-26** (local, S/M/L) entiende las palabras gracias al codificador de texto MobileCLIP2; **SAM 3** de Roboflow (nube) recibe las mismas clases como prompts de texto (16 como máximo);
- cada polígono lleva la clase que lo encontró: en la capa temporal, en el campo `label`; en una capa propia, en el «Campo para la etiqueta:» (*Field for the label:*). En las capas de UE de pyArchInit la clase no se escribe.

SAM 2.1 en «Todo (automático)», en cambio, no asigna clases: encuentra contornos, no nombres.

### Configuración de API

Las claves solo hacen falta para los modelos en la nube. Elegir el modelo en la nube en el desplegable, pegar la clave en el campo «Clave API:» (*API key:*; el texto queda oculto) y pulsar «Iniciar»: la clave se guarda en la configuración de QGIS y se vuelve a proponer la vez siguiente. Con los modelos en la nube la imagen preparada se envía al servicio.

#### Replicate API (SAM-2)
1. Crear una cuenta en [replicate.com](https://replicate.com)
2. Crear un token en [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) (el enlace «Clave de Replicate» (*Replicate key*) junto al campo abre la misma página)
3. Pegarlo en «Clave API:» con el modelo «Cloud: Replicate SAM-2»

#### Roboflow API (SAM-3)
1. Crear una cuenta en [roboflow.com](https://roboflow.com)
2. Copiar la clave desde [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) (enlace «Clave de Roboflow» (*Roboflow key*) junto al campo)
3. Pegarla en «Clave API:» con el modelo «Cloud: Roboflow SAM 3»

### Instalación Local de SAM

No hace falta ningún comando en la terminal: el entorno de los modelos locales se instala desde la ventana.

1. Hace falta un **Python del sistema 3.10–3.13**: los paquetes no se instalan en el Python de QGIS, para no arriesgarse a estropearlo. La ventana lo busca por sí sola: en **macOS** el Python de [python.org](https://www.python.org/downloads/) o de Homebrew, en **Windows** el lanzador `py` del Python de python.org, en **Linux** `python3.10`…`python3.13` o el `python3` del sistema.
2. Pulsar «Instalar / actualizar» (*Install / update*) en el grupo «Entorno local»: se crea el entorno virtual `~/pyarchinit_5/bin/sam_venv` y se instalan en él `ultralytics` (que trae consigo torch, torchvision, OpenCV, numpy) y `requests`: unos **1,5 GB** de paquetes, una sola vez. En Linux sin tarjeta NVIDIA se instala torch para CPU, mucho más ligero.
3. «Mostrar registro» (*Show log*) permite ver pip trabajando. Al final el estado se pone en verde: «listo — ultralytics …, torch …, mps».
4. Descargar los pesos del modelo que se quiera usar con «Descargar pesos» (*Download weights*, grupo «Modelo»).

Pulsando de nuevo «Instalar / actualizar» se actualizan los paquetes. El dispositivo de cálculo se elige solo: **MPS** en los Mac con Apple Silicon, **CUDA** con una tarjeta NVIDIA y, si no, **CPU** (funciona, pero es más lento). Si MPS o CUDA fallan, el trabajo vuelve a empezar solo en la CPU.

| Qué | Dónde |
|-----|-------|
| Entorno Python | `~/pyarchinit_5/bin/sam_venv` |
| Pesos de los modelos | `~/pyarchinit_5/bin/models/sam/` |
| Claves API | configuración de QGIS |

`~/pyarchinit_5` es la carpeta de datos de pyArchInit (o la indicada por la variable `PYARCHINIT_HOME`).

### Destino y Atributos

El grupo «Destino» (*Target*) decide adónde van los polígonos. El desplegable «Capa:» (*Layer:*) contiene las capas de polígonos del proyecto y «— nueva capa temporal —» (*— new temporary layer —*); si `pyunitastratigrafiche` está cargada, se propone esa.

| Destino | Qué se escribe |
|---------|----------------|
| «— nueva capa temporal —» | una capa en memoria `SAM_<ráster>_<fecha_hora>`, en el SRC de la imagen, con los campos `label` (la clase, o «segment»), `score` (confianza), `area`, `source` (el modelo) y `created` (fecha y hora) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = «Sitio:» (*Site:*; de la configuración, no editable), `area_s` = «Área:» (*Area:*; obligatoria), `stratigraph_index_us` = «Índice estratigráfico:» (*Stratigraphic index:*; 1 = piedras/objetos, 2 = estrato/superficie), `tipo_us_s` = «Tipo de UE:» (*US type:*; pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <modelo>` (p. ej. `SAM sam2.1_t.pt`), `data` = hoy; `us_s` queda vacío |
| otra capa de polígonos | la clase en el «Campo para la etiqueta:» (*Field for the label:*), un campo de texto (se propone `label`, `etichetta`, `classe`, `class`, `tipo` o `nome`, si existe; vacío = no escribir); si la capa tiene campos `score`, `area`, `source` o `created`, también se rellenan |

- En las capas de UE el número de UE se asigna después, en la tabla de atributos; el mensaje final lo recuerda: «Asigna después los números de UE en la tabla de atributos.» (*Then assign the US numbers in the attribute table.*).
- Los polígonos se reproyectan al SRC de la capa de destino y se guardan en ella enseguida (si la capa ya estaba en edición, también se guardan sus cambios pendientes).
- La capa temporal solo dura hasta que se cierra QGIS: para conservarla, exportarla a un archivo (clic derecho sobre la capa → Exportar).

### Cómo Funciona

1. **La imagen.** En un archivo, la extensión se recorta y, si hace falta, se reduce con GDAL: los píxeles son los reales del archivo, no los dibujados en el mapa (el estilo de la capa no cuenta; los ráster que no son de 8 bits se reescalan a 0–255). Las teselas y los servicios no tienen archivo: QGIS renderiza la vista con su propio motor de dibujo, a la resolución elegida —solo esa capa, sin las demás capas del mapa—, y se segmenta ese renderizado.
2. **El área.** Con un polígono (dibujado o desde capa) se toma el rectángulo que lo contiene, se pinta de blanco todo lo que queda fuera y, al final, los resultados se recortan al polígono.
3. **El modelo.** El trabajo lo hace `scripts/sam_worker.py`, que se ejecuta fuera de QGIS con el Python de `sam_venv` (o llama al servicio en la nube): QGIS no se bloquea. Sus mensajes de progreso (las líneas `[sam] …` del worker, en italiano) aparecen en la línea de estado: modelo y dispositivo, y luego cuántos polígonos en cuántos segundos. Los polígonos de menos de 20 píxeles se descartan y los contornos se simplifican.
4. **La vuelta al mapa.** El worker devuelve los polígonos en píxeles; pyArchInit los pasa a coordenadas con la georreferencia de la imagen, repara las geometrías no válidas y las reproyecta al SRC de la capa de destino.

### Workflow SAM

**1. Preparación**
- Cargar la ortofoto, o una capa de teselas (p. ej. ESRI World Imagery como teselas XYZ)
- Comprobar el sistema de referencia del proyecto
- Para escribir en las UE: cargar `pyunitastratigrafiche` (o `pyunitastratigrafiche_usm`) y comprobar el sitio en la configuración
- La primera vez, para los modelos locales: «Instalar / actualizar» y después «Descargar pesos»

**2. Configuración**
- «Imagen»: capa ráster, extensión, resolución (para las teselas) y lado máximo
- «Qué segmentar»: el modo, el umbral y, para las clases de texto, las clases
- «Modelo»: un modelo local con los pesos presentes, o un modelo en la nube con su clave
- «Destino»: la capa y sus atributos

**3. Ejecución**
- «Iniciar», o «Iniciar la selección» y después puntos, rectángulo o polígono en el mapa
- Seguir la línea de estado; «Cancelar» interrumpe el trabajo
- Al final aparece «Hecho: N polígonos añadidos a “capa” (modelo).» (*Done: N polygons added to “layer” (model).*)

**4. Post-procesamiento**
- Revisar los polígonos; los posibles avisos aparecen en la barra de mensajes de QGIS
- Capas de UE: asignar los números de UE (`us_s`) en la tabla de atributos
- Corregir, unir o borrar los polígonos erróneos con las herramientas de edición de QGIS
- Capa temporal: exportarla si hay que conservarla

## Integración Cartográfica

### Exportar Datos SIG

Desde la Ficha de UE, pestaña Map:
- **Export GeoPackage**: Capa como GPKG
- **Export Shapefile**: Capa como SHP
- **Export GeoJSON**: Capa como JSON

### Importar Datos SIG

Importar geometrías existentes:
1. Cargar capa en QGIS
2. Seleccionar feature
3. Usar función de importación

### Geoprocesamiento

Operaciones espaciales disponibles:
- Buffer
- Intersección
- Unión
- Diferencia
- Centroides

## Buenas Prácticas

### 1. Ortofotos

- Resolución mínima: 1-2 cm/pixel
- Formato: GeoTIFF georreferenciado
- Sistema de referencia: coherente con el proyecto

### 2. Digitalización

- Usar snap para precisión
- Verificar topología
- Mantener consistencia de atributos

### 3. Segmentación SAM

- Ortofoto de buena calidad, iluminación uniforme, buen contraste entre objetos y fondo
- **Ortofotos grandes**: trabajar por vista o por rectángulo, no sobre «ráster completo». SAM trabaja a 1024 px internos y, por encima del «Lado máximo (px):», la imagen se reduce: en un área demasiado grande los objetos pequeños se pierden
- **Teselas**: elegir un nivel de zoom en el que los objetos se reconozcan a simple vista (p. ej. 0,3–0,6 m/px para edificios y carreteras). La «Resolución (unidades de mapa/px):» propone la de la vista; si la extensión es grande, la imagen se reduce al lado máximo y la resolución real empeora
- **Clases de texto**: sustantivos ingleses sencillos (building, road, river, field, stone, wall)
- Las clases solo las dan YOLOE o SAM 3: SAM 2.1 en «Todo (automático)» encuentra contornos pero no asigna clases
- **Hardware**: los Mac con Apple Silicon usan MPS, una tarjeta NVIDIA usa CUDA y, si no, la CPU, más lenta (mejor entonces SAM 2.1 Tiny o Small, YOLOE-26 S y áreas pequeñas)
- Post-verificación siempre necesaria

### 4. Organización de Capas

- Agrupar por tipología
- Usar estilos consistentes
- Mantener orden en la leyenda

## Resolución de Problemas

### Capas No Visualizadas

**Posibles causas**:
- Extensión errónea
- Sistema de referencia diferente
- Filtro activo

**Soluciones**:
- Zoom to Layer
- Verificar CRS
- Eliminar filtros

### SAM No Funciona

| Mensaje o síntoma | Qué hacer |
|-------------------|-----------|
| «Entorno local» en naranja: «no instalado…» (*not installed…*), o «El entorno local no está instalado: pulsa “Instalar / actualizar” (o elige un modelo en la nube).» (*The local environment is not installed: press “Install / update” (or choose a cloud model).*) | Pulsar «Instalar / actualizar». Hace falta un Python del sistema 3.10–3.13; si no lo hay, aparece `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` (no se encontró ningún Python 3.10–3.13: instalar Python desde python.org o Homebrew). Si pip falla, el error está en «Mostrar registro». En Linux sin tarjeta NVIDIA se instala torch para CPU |
| «faltan los pesos (~N MB)» (*weights missing (~N MB)*), o «Faltan los pesos del modelo: pulsa “Descargar pesos”.» (*The model weights are missing: press “Download weights”.*) | Pulsar «Descargar pesos» (hace falta conexión a internet) |
| «Hace falta la clave API del servicio.» (*The service API key is needed.*) | Con un modelo en la nube, pegar la clave en «Clave API:» (véase «Configuración de API») |
| «No se ha encontrado ningún polígono: prueba con un área más pequeña, un umbral más bajo u otro modelo.» (*No polygon found: try a smaller area, a lower threshold or another model.*) | Extensión más pequeña, «Umbral:» más bajo, otro modelo (un SAM 2.1 más grande, o las clases de texto); para las teselas, una resolución más fina |
| «El área elegida no cubre el ráster» (mensaje en italiano: `l'area scelta non copre il raster`) | La vista, el rectángulo o el polígono caen fuera del ráster: encuadrar el ráster y volver a probar |
| «Rellena el área para la capa de UE.» (*Fill in the area for the US layer.*) | Escribir el «Área:» en el grupo «Destino» |
| «Ráster girado: no admitido (reproyéctalo antes)» (mensaje en italiano: `raster ruotato: non supportato (riproiettalo prima)`) | Reproyectar el ráster con gdalwarp (menú Ráster de QGIS) y usar el archivo nuevo |
| «La segmentación ha fallado» (*Segmentation failed*) con las últimas líneas del worker | Leer las líneas del mensaje; volver a probar con una extensión o un «Lado máximo (px):» más pequeños, o con un modelo más pequeño |

### Geometrías Corruptas

**Posibles causas**:
- Errores de digitalización
- Importación problemática

**Soluciones**:
- Usar "Fix Geometries"
- Redibujar elemento

### Capa cargada pero geometrías no visibles (SQLite)

**Síntoma**:
- Una capa pyArchInit de una base de datos SQLite/SpatiaLite (p. ej. UE `pyunitastratigrafiche`, UEM, materiales, UE negativas) se carga y la tabla de atributos muestra los registros, pero en el mapa no se dibuja nada y "Zoom to Layer" no funciona

**Causa**:
- El índice espacial (R*Tree) de la capa no se ha mantenido: sus triggers se perdieron al recrear una tabla (p. ej. con antiguos scripts de actualización del esquema) o los datos se importaron eludiéndolos
- QGIS elige las entidades que dibujar a través de ese índice, por lo que permanecen invisibles
- También se ven afectadas las bases de datos creadas con la plantilla SQLite entre octubre de 2025 y septiembre de 2026

**Solución (automática)**:
- Al conectarse a una base de datos SQLite, pyArchInit comprueba todos los índices espaciales (unos instantes; si la base de datos está sana no escribe nada) y reconstruye automáticamente los dañados
- Desde la versión 5.13.16-alpha la misma comprobación repara también las **vistas espaciales** (`pyarchinit_us_view`, `pyarchinit_quote_view`, estructuras, materiales, las vistas UT, etc.):
  - cada vista se vincula al ROWID de su tabla geométrica
  - se eliminan los registros de vistas que ya no existen
  - se recrean las vistas estándar que faltan
  - las vistas UT se registran como vistas espaciales
  - las tablas geométricas sin índice espacial reciben uno: es necesario cuando el GDAL incluido en QGIS no tiene las funciones SpatiaLite (p. ej. QGIS en macOS), donde sin índice esas capas no dibujaban nada
- Antes de modificar nada guarda UNA sola copia de seguridad junto a la base de datos: `<base_de_datos>.sqlite.pre_spatial_index_repair_<fecha-hora UTC>`
- El resultado se escribe en el panel de registro de QGIS (Ver → Paneles → Mensajes de registro, pestaña "PyArchInit")

**Qué hacer**:
- Nada que iniciar a mano: la comprobación se ejecuta automáticamente en la PRIMERA conexión a cada base de datos en cada sesión de QGIS (es decir, tras actualizar el plugin o tras reiniciar QGIS)
- Si las capas ya estaban cargadas, quitarlas y volver a añadirlas (o reabrir el proyecto) después de la reparación
- Si el registro "PyArchInit" indica que un índice NO se ha podido reparar (p. ej. SpatiaLite no se puede cargar), resolver la causa y reiniciar QGIS: la comprobación se repite solo en una nueva sesión
- El archivo de copia de seguridad puede eliminarse una vez verificadas las capas
- Para repetir la comprobación (p. ej. tras restaurar una copia de seguridad), reiniciar QGIS
- Nota: en `inventario_materiali_view` el punto del sitio se repite para cada material, por lo que "Identify" sobre ese punto muestra uno de los materiales

## Referencias

### Archivos Fuente
- `modules/gis/pyarchinit_pyqgis.py` - Integración SIG
- `tabs/Sam_Segmentation_Dialog.py` - Ventana SAM: grupos, modos, destino
- `modules/utility/sam_environment.py` - Entorno Python separado, paquetes y pesos
- `modules/gis/sam_raster_source.py` - Imagen que se segmenta (recorte GDAL o renderizado de la vista) y georreferencia
- `modules/gis/sam_map_tools.py` - Herramientas de mapa para puntos, rectángulo y polígono
- `scripts/sam_worker.py` - Worker fuera de QGIS: SAM 2.1, YOLOE, Replicate, Roboflow

### Capas
- `pyunitastratigrafiche` - UE de depósito
- `pyunitastratigrafiche_usm` - UE murarias
- `pyarchinit_quote` - Cotas

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/pyarchinit_image_classification_animation.html)
