# PyArchInit - Ficha UE/UEM (Unidad Estratigráfica)

## Índice
1. [Introducción](#introducción)
2. [Conceptos Fundamentales](#conceptos-fundamentales)
3. [Acceso a la Ficha](#acceso-a-la-ficha)
4. [Interfaz General](#interfaz-general)
5. [Campos Identificativos](#campos-identificativos)
6. [Pestaña Localización](#pestaña-localización)
7. [Pestaña Datos Descriptivos](#pestaña-datos-descriptivos)
8. [Pestaña Periodización](#pestaña-periodización)
9. [Pestaña Relaciones Estratigráficas](#pestaña-relaciones-estratigráficas)
10. [Pestaña Datos Físicos](#pestaña-datos-físicos)
11. [Pestaña Datos de Fichado](#pestaña-datos-de-fichado)
12. [Pestaña Medidas UE](#pestaña-medidas-ue)
13. [Pestaña Documentación](#pestaña-documentación)
14. [Pestaña Técnica Edilicia UEM](#pestaña-técnica-edilicia-uem)
15. [Pestaña Aglutinantes UEM](#pestaña-aglutinantes-uem)
16. [Pestaña Media](#pestaña-media)
17. [Pestaña Ayuda - Tool Box](#pestaña-ayuda---tool-box)
18. [Matrix de Harris](#matrix-de-harris)
19. [Funcionalidades SIG](#funcionalidades-sig)
20. [Exportaciones](#exportaciones)
21. [Workflow Operativo](#workflow-operativo)
22. [Resolución de Problemas](#resolución-de-problemas)

---

## Introducción

La **Ficha UE/UEM** (Unidad Estratigráfica / Unidad Estratigráfica Muraria) es el corazón de la documentación arqueológica en PyArchInit. Representa la herramienta principal para registrar toda la información relativa a las unidades estratigráficas individualizadas durante la excavación.

Esta ficha implementa los principios del **método estratigráfico** desarrollado por Edward C. Harris, permitiendo documentar:
- Las características físicas de cada estrato
- Las relaciones estratigráficas entre las unidades
- La cronología relativa y absoluta
- La documentación gráfica y fotográfica asociada

---

## Conceptos Fundamentales

### Qué es una Unidad Estratigráfica (UE)

Una **Unidad Estratigráfica** es la unidad más pequeña de excavación individualizable y distinguible de las demás. Puede ser:
- **Estrato**: depósito de tierra con características homogéneas
- **Interfaz**: superficie de contacto entre estratos (ej. corte de fosa)
- **Elemento estructural**: parte de una construcción

### Tipos de Unidades

| Tipo | Código | Descripción |
|------|--------|-------------|
| UE | Unidad Estratigráfica | Estrato genérico |
| UEM | Unidad Estratigráfica Muraria | Elemento constructivo de muro |
| UEVA | Unidad Estratigráfica Vertical A | Alzado vertical tipo A |
| UEVB | Unidad Estratigráfica Vertical B | Alzado vertical tipo B |
| UEVC | Unidad Estratigráfica Vertical C | Alzado vertical tipo C |
| UED | Unidad Estratigráfica de Demolición | Estrato de derrumbe/demolición |
| CON | Sillares | Bloques arquitectónicos |
| VSF | Virtual Stratigraphic Feature | Elemento virtual |
| SF | Stratigraphic Feature | Feature estratigráfica |
| SUE | Sub-Unidad Estratigráfica | Subdivisión de UE |
| DOC | Documentación | Elemento documentario |

### Relaciones Estratigráficas

Las relaciones estratigráficas definen las relaciones temporales entre las UE:

| Relación | Inversa | Significado |
|----------|---------|-------------|
| **Cubre** | Cubierta por | La UE se superpone físicamente |
| **Corta** | Cortada por | La UE interrumpe/atraviesa |
| **Rellena** | Rellenada por | La UE colma una cavidad |
| **Se apoya en** | Le apoya | Relación de apoyo |

---

## Acceso a la Ficha

Para acceder a la Ficha UE:

1. Menú **PyArchInit** → **Archaeological record management** → **SU/WSU**
2. O desde la barra de herramientas PyArchInit, hacer clic en el icono **UE/UEM**

---

## Interfaz General

La Ficha UE está organizada en diferentes áreas funcionales:

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | **Campos Identificativos** | Sitio, Área, UE, Tipo, Definiciones |
| 2 | **Toolbar DBMS** | Navegación, guardado, búsqueda |
| 3 | **Pestañas de Datos** | Fichas temáticas para los datos |
| 4 | **Toolbar SIG** | Herramientas de visualización en mapa |
| 5 | **Pestaña Tool Box** | Herramientas avanzadas y Matrix |

### Toolbar DBMS

| Botón | Función | Descripción |
|-------|---------|-------------|
| **New record** | Nuevo | Crea una nueva ficha UE |
| **Save** | Guardar | Guarda las modificaciones |
| **Delete** | Eliminar | Elimina la ficha actual |
| **View all** | Ver todos | Muestra todos los registros |
| **First/Prev/Next/Last** | Navegación | Navega entre los registros |
| **new search** | Búsqueda | Inicia modo búsqueda |
| **search !!!** | Ejecutar | Ejecuta la búsqueda |
| **Order by** | Ordenar | Ordena los registros |
| **Report** | Imprimir | Genera informe PDF |
| **Lista UE/Fotos** | Lista | Genera listados |

---

## Campos Identificativos

Los campos identificativos están siempre visibles en la parte superior de la ficha.

### Campos Obligatorios

| Campo | Descripción | Formato |
|-------|-------------|---------|
| **Sitio** | Nombre del sitio arqueológico | Texto (desde combobox) |
| **Área** | Número del área de excavación | Número entero (1-20) |
| **UE/UEM** | Número de la unidad estratigráfica | Número entero |
| **Tipo de unidad** | Tipo de unidad (UE, UEM, etc.) | Selección |

### Campos Descriptivos

| Campo | Descripción |
|-------|-------------|
| **Definición estratigráfica** | Clasificación estratigráfica (desde tesauro) |
| **Definición interpretativa** | Interpretación funcional (desde tesauro) |

### Definiciones Estratigráficas (Ejemplos)

| Definición | Descripción |
|------------|-------------|
| Estrato | Depósito genérico |
| Relleno | Material de colmatación |
| Corte | Interfaz negativa |
| Suelo de uso | Superficie de paso |
| Derrumbe | Material de derrumbe |
| Solera | Pavimento de tierra apisonada |

### Definiciones Interpretativas (Ejemplos)

| Definición | Descripción |
|------------|-------------|
| Actividad de obra | Fase constructiva |
| Abandono | Fase de abandono |
| Pavimentación | Superficie de pavimento |
| Muro | Estructura muraria |
| Fosa | Excavación intencional |
| Nivelación | Estrato de preparación |

---

## Pestaña Localización

Contiene los datos de posicionamiento dentro de la excavación.

### Campos de Localización

| Campo | Descripción | Nota |
|-------|-------------|------|
| **Sector** | Sector de excavación | Letras A-H o números 1-20 |
| **Cuadro/Pared** | Referencia espacial | Para excavaciones en cuadrícula |
| **Ambiente** | Número del ambiente | Para edificios/estructuras |
| **Sondeo** | Número del sondeo | Para sondeos de verificación |

### Números de Catálogo

| Campo | Descripción |
|-------|-------------|
| **Nº Cat. General** | Número de catálogo general |
| **Nº Cat. Interno** | Número de catálogo interno |
| **Nº Cat. Internacional** | Código internacional |

---

## Pestaña Datos Descriptivos

Contiene la descripción textual de la unidad estratigráfica.

### Campos Descriptivos

| Campo | Descripción | Sugerencias |
|-------|-------------|-------------|
| **Descripción** | Descripción física de la UE | Color, consistencia, composición, límites |
| **Interpretación** | Interpretación funcional | Función, formación, significado |
| **Elementos datantes** | Materiales para datación | Cerámica, monedas, objetos datantes |
| **Observaciones** | Notas adicionales | Dudas, hipótesis, comparaciones |

### Cómo Describir una UE

**Descripción física:**
```
Estrato de tierra arcillosa, de color marrón oscuro (10YR 3/3),
consistencia compacta, con inclusiones de fragmentos de ladrillo (2-5 cm),
cantos de caliza (1-3 cm) y carbón. Límites netos en la parte superior,
difusos en la inferior. Espesor variable 15-25 cm.
```

**Interpretación:**
```
Estrato de abandono formado tras el cese de las actividades
en el ambiente. La presencia de material edilicio
fragmentado sugiere un derrumbe parcial de las estructuras.
```

---

## Pestaña Periodización

Gestiona la cronología de la unidad estratigráfica.

### Periodización Relativa

| Campo | Descripción |
|-------|-------------|
| **Periodo Inicial** | Periodo de formación |
| **Fase Inicial** | Fase de formación |
| **Periodo Final** | Periodo de obliteración |
| **Fase Final** | Fase de obliteración |

**Nota**: Los periodos y las fases deben crearse primero en la **Ficha de Periodización**.

### Cronología Absoluta

| Campo | Descripción |
|-------|-------------|
| **Datación** | Fecha absoluta o intervalo |
| **Año** | Año de excavación |

### Otros Campos

| Campo | Descripción | Valores |
|-------|-------------|---------|
| **Actividad** | Tipo de actividad | Texto libre |
| **Estructura** | Código de estructura asociada | Desde Ficha Estructura |
| **Excavada** | Estado de excavación | Sí / No |
| **Método de excavación** | Modalidad de excavación | Mecánico / Estratigráfico |

### Campo Estructura

El campo **Estructura** (`comboBox_struttura`) es un campo de selección múltiple sincronizado con la Ficha de Estructura.

**Características importantes:**
- El campo muestra todas las estructuras definidas en la Ficha de Estructura para el sitio actual
- Puede seleccionar múltiples estructuras marcando las casillas correspondientes
- Después de guardar, los datos se sincronizan entre UE y Estructura

**Cómo asignar estructuras:**
1. Hacer clic en el campo Estructura para abrir el desplegable
2. Seleccionar las estructuras deseadas marcando las casillas
3. Guardar el registro

**Cómo eliminar todas las estructuras:**
1. **Clic derecho** en el campo Estructura
2. Seleccionar **"Vaciar campo Estructura"** en el menú contextual
3. Se eliminarán todas las selecciones
4. Guardar el registro para confirmar el cambio

> **Nota**: Vaciar el campo elimina las selecciones en el registro actual. Para deseleccionar solo algunas estructuras, desmarque manualmente las casillas en el desplegable.

### Campo Orden de Capa

El campo **Orden de Capa** (`order_layer`) define la posición de la UE en la secuencia estratigráfica.

**Reglas importantes:**
- El orden debe ser **siempre secuencial**: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13...
- **No se permiten saltos**: no puede tener 1, 2, 5, 8 (faltan 3, 4, 6, 7)
- **Sin duplicados**: cada UE debe tener un número de orden único
- Si usa orden alfabético: A, B, C, D, E, F... (tampoco se permiten saltos)

**Cálculo automático:**
El orden de capa se calcula automáticamente a partir de las relaciones estratigráficas. El sistema analiza las relaciones entre las UE (cubre, cubierta por, corta, etc.) y asigna un número de orden secuencial a cada una.

**Ejemplo de orden correcto:**
| UE | Orden de capa |
|----|---------------|
| UE 1 | 1 |
| UE 2 | 2 |
| UE 3 | 3 |
| UE 4 | 4 |

**Ejemplo de orden incorrecto (evitar):**
| UE | Orden de capa |
|----|---------------|
| UE 1 | 1 |
| UE 2 | 3 | ← Incorrecto, falta 2 |
| UE 3 | 7 | ← Incorrecto, faltan 4, 5, 6 |

---

## Pestaña Relaciones Estratigráficas

**Esta es la pestaña más importante de la ficha UE.** Define las relaciones estratigráficas con las otras unidades.

### Estructura de la Tabla de Relaciones

| Columna | Descripción |
|---------|-------------|
| **Sitio** | Sitio de la UE correlacionada |
| **Área** | Área de la UE correlacionada |
| **UE** | Número de la UE correlacionada |
| **Tipo de relación** | Tipo de relación |

### Tipos de Relación Disponibles

| Español | English | Deutsch |
|---------|---------|---------|
| Cubre | Covers | Liegt über |
| Cubierta por | Covered by | Liegt unter |
| Corta | Cuts | Schneidet |
| Cortada por | Cut by | Geschnitten von |
| Rellena | Fills | Verfüllt |
| Rellenada por | Filled by | Verfüllt von |
| Se apoya en | Abuts | Stützt sich auf |
| Le apoya | Supports | Wird gestützt von |
| Igual a (=) | Same as | Gleich |
| Anterior (>>) | Earlier | Früher |
| Posterior (<<) | Later | Später |

### Inserción de Relaciones

1. Hacer clic en **+** para añadir una fila
2. Insertar Sitio, Área, UE de la UE correlacionada
3. Seleccionar el tipo de relación
4. Guardar

### Botones de Relaciones

| Botón | Función |
|-------|---------|
| **+** | Añadir fila |
| **-** | Eliminar fila |
| **Insert or update inverse relat.** | Crea automáticamente la relación inversa |
| **Ir a la UE** | Navega a la UE seleccionada |
| **visualizar matrix** | Muestra el Matrix de Harris |
| **Fix** | Corrige errores en las relaciones |

### Relaciones Inversas Automáticas

Cuando insertas una relación, puedes crear automáticamente la inversa:

| Si insertas | Se crea |
|-------------|---------|
| UE 1 **cubre** UE 2 | UE 2 **cubierta por** UE 1 |
| UE 1 **corta** UE 2 | UE 2 **cortada por** UE 1 |
| UE 1 **rellena** UE 2 | UE 2 **rellenada por** UE 1 |

### Control de Relaciones

El botón **Check relaciones** verifica la coherencia de las relaciones:
- Detecta relaciones faltantes
- Encuentra inconsistencias
- Señala errores lógicos

---

## Pestaña Datos Físicos

Describe las características físicas de la unidad estratigráfica.

### Características Generales

| Campo | Valores |
|-------|---------|
| **Color** | Marrón, Amarillo, Gris, Negro, etc. |
| **Consistencia** | Arcillosa, Compacta, Friable, Arenosa |
| **Formación** | Artificial, Natural |
| **Posición** | - |
| **Modo de formación** | Aporte, Sustracción, Acumulación, Desplome |
| **Criterios de distinción** | Texto libre |

### Tablas de Componentes

| Tabla | Contenido |
|-------|-----------|
| **Comp. orgánicos** | Huesos, madera, carbones, semillas, etc. |
| **Comp. inorgánicos** | Piedras, ladrillos, cerámica, etc. |
| **Inclusiones Artificiales** | Materiales antrópicos incluidos |

### Muestreos

| Campo | Valores |
|-------|---------|
| **Flotación** | Sí / No |
| **Tamizado** | Sí / No |
| **Fiabilidad** | Escasa, Buena, Discreta, Óptima |
| **Estado de conservación** | Insuficiente, Escaso, Bueno, Discreto, Óptimo |

---

## Pestaña Datos de Fichado

Información sobre la compilación de la ficha.

### Entidad y Responsables

| Campo | Descripción |
|-------|-------------|
| **Entidad Responsable** | Entidad que gestiona la excavación |
| **Superintendencia** | SABAP competente |
| **Responsable científico** | Director de la excavación |
| **Responsable de la compilación** | Quien ha rellenado la ficha en campo |
| **Responsable de la reelaboración** | Quien ha reelaborado los datos |

### Referencias

| Campo | Descripción |
|-------|-------------|
| **Ref. TM** | Referencia ficha TM (Tabla de Materiales) |
| **Ref. RA** | Referencia ficha RA (Materiales Arqueológicos) |
| **Ref. Pottery** | Referencia ficha Cerámica |

### Fechas

| Campo | Formato |
|-------|---------|
| **Fecha de relevamiento** | DD/MM/AAAA |
| **Fecha de fichado** | DD/MM/AAAA |
| **Fecha de reelaboración** | DD/MM/AAAA |

---

## Pestaña Medidas UE

Contiene todas las mediciones de la unidad estratigráfica.

### Cotas

| Campo | Descripción | Unidad |
|-------|-------------|--------|
| **Cota absoluta** | Cota sobre el nivel del mar | metros |
| **Cota relativa** | Cota respecto a punto de referencia | metros |
| **Cota máx absoluta** | Cota máxima absoluta | metros |
| **Cota máx relativa** | Cota máxima relativa | metros |
| **Cota mín absoluta** | Cota mínima absoluta | metros |
| **Cota mín relativa** | Cota mínima relativa | metros |

### Dimensiones

| Campo | Descripción | Unidad |
|-------|-------------|--------|
| **Longitud máx** | Longitud máxima | metros |
| **Anchura media** | Anchura media | metros |
| **Altura máx** | Altura máxima | metros |
| **Altura mín** | Altura mínima | metros |
| **Espesor** | Espesor del estrato | metros |
| **Profundidad máx** | Profundidad máxima | metros |
| **Profundidad mín** | Profundidad mínima | metros |

---

## Pestaña Documentación

Gestiona las referencias a la documentación gráfica y fotográfica.

### Tabla Documentación

| Columna | Descripción |
|---------|-------------|
| **Tipo documentación** | Foto, Planta, Sección, Alzado, etc. |
| **Referencias** | Número/código del documento |

### Tipos de Documentación

| Tipo | Descripción |
|------|-------------|
| Foto | Documentación fotográfica |
| Planta | Planta de excavación |
| Sección | Sección estratigráfica |
| Alzado | Alzado murario |
| Levantamiento | Levantamiento gráfico |
| 3D | Modelo tridimensional |

---

## Pestaña Técnica Edilicia UEM

Pestaña específica para las Unidades Estratigráficas Murarias (UEM).

### Datos Específicos UEM

| Campo | Descripción |
|-------|-------------|
| **Longitud UEM** | Longitud de la estructura muraria (metros) |
| **Altura UEM** | Altura de la estructura muraria (metros) |
| **Superficie analizada** | Porcentaje analizado |
| **Sección muraria** | Tipo de sección |
| **Módulo** | Módulo constructivo |
| **Tipología de la obra** | Tipo de fábrica |
| **Orientación** | Orientación de la estructura |
| **Reutilización** | Sí / No |

### Materiales y Técnicas

| Sección | Campos |
|---------|--------|
| **Ladrillos** | Materiales, Labrado, Consistencia, Forma, Color, Pasta, Colocación |
| **Elementos Líticos** | Materiales, Labrado, Consistencia, Forma, Color, Talla, Colocación |

---

## Pestaña Aglutinantes UEM

Describe las características de los aglutinantes (mortero) en las estructuras murarias.

### Características del Aglutinante

| Campo | Descripción |
|-------|-------------|
| **Tipo de aglutinante** | Mortero, Barro, Ausente, etc. |
| **Consistencia** | Tenaz, Friable, etc. |
| **Color** | Color del aglutinante |
| **Acabado** | Tipo de acabado |
| **Espesor del aglutinante** | Espesor en cm |

### Composición

| Sección | Descripción |
|---------|-------------|
| **Áridos** | Componentes gruesos |
| **Inertes** | Componentes finos |
| **Inclusiones** | Materiales incluidos |

---

## Pestaña Media

Visualiza las imágenes asociadas a la unidad estratigráfica.

### Lista UE

La tabla muestra todas las UE con las imágenes asociadas:
- Ir a la ficha
- Casilla de verificación para selección múltiple
- Vista previa de miniatura

### Botones

| Botón | Función |
|-------|---------|
| **Buscar imágenes** | Busca imágenes asociadas |
| **Save** | Guarda asociaciones |
| **Revert** | Cancela modificaciones |

---

## Pestaña Ayuda - Tool Box

Contiene herramientas avanzadas para el control y la exportación.

### Sistemas de Control

| Herramienta | Descripción |
|-------------|-------------|
| **Check relaciones estratigráficas** | Verifica coherencia de las relaciones |
| **Check, go!!!!** | Ejecuta el control |

### Exportación Matrix

| Botón | Salida |
|-------|--------|
| **Exportar Matrix** | Archivo DOT para Graphviz |
| **Export Graphml** | Archivo GraphML para yEd |
| **Export to Extended Matrix** | Formato S3DGraphy |
| **Interactive Matrix** | Visualización interactiva |

### Funciones SIG

| Botón | Función |
|-------|---------|
| **Dibujar UE** | Carga capa para dibujo |
| **Preview planta UE** | Vista previa en el mapa |
| **Abrir fichas UE** | Abre fichas seleccionadas |
| **Pan** | Herramienta panorámica |
| **Mostrar imágenes** | Visualiza fotos |

---

## Matrix de Harris

El Matrix de Harris es una representación gráfica de las relaciones estratigráficas.

### Generación del Matrix

1. Seleccionar el sitio y el área
2. Verificar que las relaciones sean correctas
3. Ir a **Pestaña Ayuda** → **Tool Box**
4. Hacer clic en **Export Matrix**

### Formatos de Exportación

| Formato | Software | Uso |
|---------|----------|-----|
| DOT | Graphviz | Visualización básica |
| GraphML | yEd, Gephi | Edición avanzada |
| Extended Matrix | S3DGraphy | Visualización 3D |
| CSV | Excel | Análisis de datos |

### Extended Matrix

El Extended Matrix añade información suplementaria:
- Periodización
- Definiciones interpretativas
- Datos cronológicos
- Compatibilidad con CIDOC-CRM

---

## Funcionalidades SIG

La Ficha UE está estrechamente integrada con QGIS.

### Toolbar SIG

| Botón | Función |
|-------|---------|
| **GIS Viewer** | Carga capas UE |
| **Preview planta UE** | Vista previa de geometría |
| **Dibujar UE** | Activa dibujo |

### Capas SIG Asociadas

| Capa | Geometría | Descripción |
|------|-----------|-------------|
| PYUS | Polígono | Unidades estratigráficas |
| PYUSM | Polígono | Unidades murarias |
| PYQUOTE | Punto | Cotas |
| PYQUOTEUSM | Punto | Cotas UEM |
| PYUS_NEGATIVE | Polígono | UE negativas |

---

## Exportaciones

### Fichas UE PDF

1. Hacer clic en **Report** en la barra de herramientas
2. Elegir formato (PDF, Word)
3. Seleccionar las fichas a exportar

### Listados

| Tipo | Contenido |
|------|-----------|
| **Listado UE** | Lista de todas las UE |
| **Listado Fotos con Miniatura** | Lista con vistas previas |
| **Listado Fotos sin Miniatura** | Lista simple |
| **Fichas UE** | Fichas completas |

---

## Workflow Operativo

### Crear una Nueva UE

#### Paso 1: Abrir la Ficha

#### Paso 2: Hacer clic en New Record

#### Paso 3: Insertar Identificativos
- Seleccionar Sitio
- Insertar Área
- Insertar número UE
- Seleccionar Tipo

#### Paso 4: Definiciones
- Seleccionar definición estratigráfica
- Seleccionar definición interpretativa

#### Paso 5: Descripción
- Rellenar la descripción física
- Rellenar la interpretación

#### Paso 6: Relaciones Estratigráficas
- Insertar las relaciones con las otras UE
- Crear las relaciones inversas

#### Paso 7: Datos Físicos y Medidas
- Rellenar características físicas
- Insertar las medidas

#### Paso 8: Guardar
- Hacer clic en Save
- Verificar el guardado

---

## Resolución de Problemas

### Error en el guardado
- Verificar que Sitio, Área y UE estén rellenados
- Verificar que la combinación sea única

### Relaciones no coherentes
- Usar el control de relaciones
- Verificar las relaciones inversas
- Corregir con el botón Fix

### El Matrix no se genera
- Verificar que Graphviz esté instalado
- Controlar la ruta en la configuración
- Verificar que haya relaciones

### Las capas SIG no se cargan
- Verificar la conexión a la base de datos
- Comprobar que existan geometrías
- Verificar el sistema de referencia

---

## Notas Técnicas

### Base de Datos

- **Tabla principal**: `us_table`
- **Campos principales**: más de 80 campos
- **Clave primaria**: `id_us`
- **Clave compuesta**: sitio + área + ue

### Tesauro

Los campos con tesauro (definiciones) usan la tabla `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' para definición estratigráfica
- tipologia_sigla = '1.2' para definición interpretativa

---

*Documentación PyArchInit - Ficha UE/UEM*
*Versión: 4.9.x*
*Última actualización: Enero 2026*
