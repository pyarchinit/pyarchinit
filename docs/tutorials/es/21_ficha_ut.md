# Tutorial 21: Ficha UT - Unidades Topograficas

## Introduccion

La **Ficha UT** (Unidades Topograficas) es el modulo de PyArchInit dedicado a la documentacion de las prospecciones arqueologicas de superficie (survey). Permite registrar los datos relativos a las concentraciones de materiales, anomalias del terreno y sitios identificados durante las prospecciones.

### Conceptos Basicos

**Unidad Topografica (UT):**
- Area delimitada con caracteristicas arqueologicas homogeneas
- Identificada durante prospeccion de superficie
- Definida por concentracion de materiales o anomalias visibles

**Prospeccion (Survey):**
- Exploracion sistematica del territorio
- Recogida de datos sobre presencia antropica antigua
- Documentacion sin excavacion

---

## Acceso a la Ficha

### Via Menu
1. Menu **PyArchInit** en la barra de menus de QGIS
2. Seleccionar **Ficha UT** (o **TU form**)

### Via Barra de Herramientas
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **UT**

---

## Vista General de la Interfaz

La ficha esta organizada en varias pestanas para documentar todos los aspectos de la prospeccion.

### Pestanas Principales

| # | Pestana | Descripcion |
|---|---------|-------------|
| 1 | Identificacion | Proyecto, Nr. UT, Ubicacion |
| 2 | Descripcion | Definicion, descripcion, interpretacion |
| 3 | Datos UT | Condiciones, metodologia, fechas |
| 4 | Analisis | Potencial y riesgo arqueologico |

### Barra de Herramientas Principal

| Boton | Funcion |
|-------|---------|
| Primero | Ir al primer registro |
| Anterior | Registro anterior |
| Siguiente | Registro siguiente |
| Ultimo | Ir al ultimo registro |
| Buscar | Busqueda avanzada |
| Guardar | Guardar registro |
| Eliminar | Eliminar registro |
| PDF | Exportar ficha PDF |
| **Lista PDF** | Exportar listado UT en PDF |
| **Exportar GNA** | Exportar en formato GNA |
| Mostrar Capa | Visualizar capa en mapa |

---

## Campos Identificativos

### Proyecto

**Campo**: `comboBox_progetto`
**Base de datos**: `progetto`

Nombre del proyecto de prospeccion.

### Numero UT

**Campo**: `comboBox_nr_ut`
**Base de datos**: `nr_ut`

Numero progresivo de la Unidad Topografica.

### UT Literal

**Campo**: `lineEdit_ut_letterale`
**Base de datos**: `ut_letterale`

Sufijo alfabetico opcional (ej. UT 15a, 15b).

---

## Campos de Localizacion

### Datos Administrativos

| Campo | Base de datos | Descripcion |
|-------|---------------|-------------|
| Pais | `nazione` | Estado |
| Region | `regione` | Region administrativa |
| Provincia | `provincia` | Provincia |
| Municipio | `comune` | Municipio |
| Fraccion | `frazione` | Fraccion/localidad |
| Localidad | `localita` | Toponimo local |
| Direccion | `indirizzo` | Calle/carretera |
| Nr. civico | `nr_civico` | Numero civico |

### Datos Cartograficos

| Campo | Base de datos | Descripcion |
|-------|---------------|-------------|
| Carta IGM | `carta_topo_igm` | Hoja IGM |
| Carta CTR | `carta_ctr` | Elemento CTR |
| Hoja catastral | `foglio_catastale` | Referencia catastro |

### Coordenadas

| Campo | Base de datos | Descripcion |
|-------|---------------|-------------|
| Coord. geograficas | `coord_geografiche` | Lat/Long (formato: lat, lon) |
| Coord. planas | `coord_piane` | UTM/Gauss-Boaga (formato: x, y) |
| Cota | `quota` | Altitud s.n.m. |
| Precision coord. | `coordinate_precision` | Precision GPS en metros |

**IMPORTANTE**: Las coordenadas se utilizan para la generacion de mapas de calor. Al menos uno entre `coord_geografiche` y `coord_piane` debe estar rellenado para cada UT.

---

## Campos Descriptivos

### Definicion UT

**Campo**: `comboBox_def_ut`
**Base de datos**: `def_ut`
**Tesauro**: Codigo 12.7

Clasificacion tipologica de la UT. Los valores se cargan del tesauro y se traducen automaticamente al idioma actual.

**Valores estandar:**
| Codigo | Espanol | Ingles |
|--------|---------|--------|
| scatter | Area de dispersion de materiales | Material scatter |
| site | Yacimiento arqueologico | Archaeological site |
| anomaly | Anomalia del terreno | Terrain anomaly |
| structure | Estructura aflorante | Outcropping structure |
| concentration | Concentracion de hallazgos | Finds concentration |
| traces | Trazas antropicas | Anthropic traces |
| findspot | Hallazgo esporadico | Sporadic find |
| negative | Resultado negativo | Negative result |

### Descripcion UT

**Campo**: `textEdit_descrizione`
**Base de datos**: `descrizione_ut`

Descripcion detallada de la Unidad Topografica.

**Contenidos:**
- Extension y forma del area
- Densidad de los materiales
- Caracteristicas del terreno
- Visibilidad y condiciones

### Interpretacion UT

**Campo**: `textEdit_interpretazione`
**Base de datos**: `interpretazione_ut`

Interpretacion funcional/historica.

---

## Campos Survey con Tesauro

Los siguientes campos utilizan el sistema de tesauro para garantizar terminologia estandarizada y traducida a 7 idiomas (IT, EN, DE, ES, FR, AR, CA).

### Tipo Survey (12.1)

**Campo**: `comboBox_survey_type`
**Base de datos**: `survey_type`

| Codigo | Espanol | Descripcion |
|--------|---------|-------------|
| intensive | Prospeccion intensiva | Prospeccion sistematica intensiva |
| extensive | Prospeccion extensiva | Prospeccion por muestreo |
| targeted | Prospeccion dirigida | Investigacion de areas especificas |
| random | Muestreo aleatorio | Metodologia aleatoria |

### Cobertura Vegetal (12.2)

**Campo**: `comboBox_vegetation_coverage`
**Base de datos**: `vegetation_coverage`

| Codigo | Espanol | Descripcion |
|--------|---------|-------------|
| none | Ausente | Suelo desnudo |
| sparse | Escasa | Cobertura < 25% |
| moderate | Moderada | Cobertura 25-50% |
| dense | Densa | Cobertura 50-75% |
| very_dense | Muy densa | Cobertura > 75% |

### Metodo GPS (12.3)

**Campo**: `comboBox_gps_method`
**Base de datos**: `gps_method`

| Codigo | Espanol | Descripcion |
|--------|---------|-------------|
| handheld | GPS portatil | Dispositivo GPS portatil |
| dgps | GPS diferencial | DGPS con estacion base |
| rtk | GPS RTK | Cinematico en tiempo real |
| total_station | Estacion total | Levantamiento con estacion total |

### Condicion de Superficie (12.4)

**Campo**: `comboBox_surface_condition`
**Base de datos**: `surface_condition`

| Codigo | Espanol | Descripcion |
|--------|---------|-------------|
| ploughed | Arado | Campo recien arado |
| stubble | Rastrojo | Presencia de rastrojos |
| pasture | Pasto | Terreno de pasto/pradera |
| woodland | Bosque | Area boscosa |
| urban | Urbano | Area urbana/edificada |

### Accesibilidad (12.5)

**Campo**: `comboBox_accessibility`
**Base de datos**: `accessibility`

| Codigo | Espanol | Descripcion |
|--------|---------|-------------|
| easy | Acceso facil | Sin restricciones |
| moderate_access | Acceso moderado | Algunas dificultades |
| difficult | Acceso dificil | Problemas significativos |
| restricted | Acceso restringido | Solo con autorizacion |

### Condiciones Meteorologicas (12.6)

**Campo**: `comboBox_weather_conditions`
**Base de datos**: `weather_conditions`

| Codigo | Espanol | Descripcion |
|--------|---------|-------------|
| sunny | Soleado | Tiempo despejado |
| cloudy | Nublado | Condiciones nubosas |
| rainy | Lluvioso | Lluvia durante prospeccion |
| windy | Ventoso | Viento fuerte |

---

## Datos Ambientales

### Porcentaje de Visibilidad

**Campo**: `spinBox_visibility_percent`
**Base de datos**: `visibility_percent`

Porcentaje de visibilidad del suelo (0-100%). Valor numerico importante para el calculo del potencial arqueologico.

### Pendiente del Terreno

**Campo**: `lineEdit_andamento_terreno_pendenza`
**Base de datos**: `andamento_terreno_pendenza`

Morfologia y pendiente del terreno.

### Uso del Suelo

**Campo**: `lineEdit_utilizzo_suolo_vegetazione`
**Base de datos**: `utilizzo_suolo_vegetazione`

Uso del suelo en el momento de la prospeccion.

---

## Datos de Materiales

### Dimensiones UT

**Campo**: `lineEdit_dimensioni_ut`
**Base de datos**: `dimensioni_ut`

Extension en m2.

### Hallazgos por m2

**Campo**: `lineEdit_rep_per_mq`
**Base de datos**: `rep_per_mq`

Densidad de materiales por metro cuadrado. Valor critico para el calculo del potencial.

### Hallazgos Diagnosticos

**Campo**: `lineEdit_rep_datanti`
**Base de datos**: `rep_datanti`

Descripcion de materiales diagnosticos.

---

## Cronologia

### Periodo I

| Campo | Base de datos |
|-------|---------------|
| Periodo I | `periodo_I` |
| Datacion I | `datazione_I` |
| Interpretacion I | `interpretazione_I` |

### Periodo II

| Campo | Base de datos |
|-------|---------------|
| Periodo II | `periodo_II` |
| Datacion II | `datazione_II` |
| Interpretacion II | `interpretazione_II` |

---

## Pestana Analisis - Potencial y Riesgo Arqueologico

La pestana **Analisis** proporciona herramientas avanzadas para el calculo automatico del potencial y riesgo arqueologico.

### Potencial Arqueologico

El sistema calcula una puntuacion de 0 a 100 basandose en varios factores ponderados:

| Factor | Peso | Descripcion | Como se calcula |
|--------|------|-------------|-----------------|
| Definicion UT | 30% | Tipo de evidencia arqueologica | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, etc. |
| Periodo historico | 25% | Cronologia de los materiales | Periodos antiguos pesan mas (Prehistorico = 90, Romano = 85, Medieval = 70, etc.) |
| Densidad de hallazgos | 20% | Materiales por m2 | >10/m2 = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Condicion de superficie | 15% | Visibilidad y accesibilidad | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentacion | 10% | Calidad de la documentacion | Presencia de fotos = +20, bibliografia = +30, investigaciones = +50 |

**Clasificacion de la puntuacion:**

| Puntuacion | Nivel | Color | Significado |
|------------|-------|-------|-------------|
| 80-100 | Alto | Verde | Alta probabilidad de depositos significativos |
| 60-79 | Medio-Alto | Amarillo-Verde | Buena probabilidad, verificacion recomendada |
| 40-59 | Medio | Naranja | Probabilidad moderada |
| 20-39 | Bajo | Rojo | Baja probabilidad |
| 0-19 | No evaluable | Gris | Datos insuficientes |

### Riesgo Arqueologico

Evalua el riesgo de impacto/perdida del patrimonio:

| Factor | Peso | Descripcion | Como se calcula |
|--------|------|-------------|-----------------|
| Accesibilidad | 25% | Facilidad de acceso al area | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Uso del suelo | 25% | Actividades agricolas/constructivas | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Restricciones existentes | 20% | Protecciones legales | Sin restricciones = 80, restriccion paisajistica = 40, restriccion arqueologica = 10 |
| Investigaciones previas | 15% | Estado de los conocimientos | Ninguna investigacion = 60, prospeccion = 40, excavacion = 20 |
| Potencial | 15% | Inversamente proporcional al potencial | Alto potencial = alto riesgo de perdida |

**Clasificacion del riesgo:**

| Puntuacion | Nivel | Color | Accion recomendada |
|------------|-------|-------|-------------------|
| 75-100 | Alto | Rojo | Intervencion urgente, medidas de proteccion inmediatas |
| 50-74 | Medio | Naranja | Monitoreo activo, evaluar proteccion |
| 25-49 | Bajo | Amarillo | Monitoreo periodico |
| 0-24 | Nulo | Verde | Ninguna intervencion inmediata necesaria |

### Campos de Base de Datos para el Analisis

| Campo | Base de datos | Descripcion |
|-------|---------------|-------------|
| Puntuacion Potencial | `potential_score` | Valor 0-100 calculado |
| Puntuacion Riesgo | `risk_score` | Valor 0-100 calculado |
| Factores Potencial | `potential_factors` | JSON con detalle de factores |
| Factores Riesgo | `risk_factors` | JSON con detalle de factores |
| Fecha Analisis | `analysis_date` | Timestamp del calculo |
| Metodo Analisis | `analysis_method` | Algoritmo utilizado |

---

## Capas Geometricas UT

PyArchInit gestiona tres tipos de geometrias para las Unidades Topograficas:

### Tablas Geometricas

| Capa | Tabla | Tipo de Geometria | Uso |
|------|-------|-------------------|-----|
| UT Puntos | `pyarchinit_ut_point` | Point | Localizacion puntual |
| UT Lineas | `pyarchinit_ut_line` | LineString | Trazados, recorridos |
| UT Poligonos | `pyarchinit_ut_polygon` | Polygon | Areas de dispersion |

### Creacion de Capas UT

1. **Via QGIS Browser:**
   - Abrir la base de datos en Browser
   - Localizar la tabla `pyarchinit_ut_point/line/polygon`
   - Arrastrar al mapa

2. **Via Menu PyArchInit:**
   - Menu **PyArchInit** > **GIS Tools** > **Load UT Layers**
   - Seleccionar el tipo de geometria

### Enlace UT-Geometria

Cada registro geometrico esta enlazado a la ficha UT mediante:

| Campo | Descripcion |
|-------|-------------|
| `progetto` | Nombre del proyecto (debe coincidir) |
| `nr_ut` | Numero UT (debe coincidir) |

### Flujo de Trabajo para Crear Geometrias

1. **Activar edicion** en la capa UT deseada
2. **Dibujar** la geometria en el mapa
3. **Rellenar** los atributos `progetto` y `nr_ut`
4. **Guardar** la capa
5. **Verificar** el enlace desde la ficha UT

---

## Generacion de Mapas de Calor

El modulo de generacion de mapas de calor permite visualizar la distribucion espacial del potencial y del riesgo arqueologico.

### Requisitos Minimos

- **Al menos 2 UT** con coordenadas validas (`coord_geografiche` O `coord_piane`)
- **Puntuaciones calculadas** para potencial y/o riesgo
- **CRS definido** en el proyecto QGIS

### Metodos de Interpolacion

| Metodo | Descripcion | Cuando usarlo |
|--------|-------------|---------------|
| **KDE** (Kernel Density) | Estimacion de densidad kernel gaussiana | Distribucion continua, muchos puntos |
| **IDW** (Inverse Distance) | Peso inverso de la distancia | Datos dispersos, valores puntuales importantes |
| **Grid** | Interpolacion sobre cuadricula regular | Analisis sistematicos |

### Parametros del Mapa de Calor

| Parametro | Valor por Defecto | Descripcion |
|-----------|-------------------|-------------|
| Tamano de Celda | 50 m | Resolucion de la cuadricula |
| Ancho de Banda (KDE) | Auto | Radio de influencia |
| Potencia (IDW) | 2 | Exponente de ponderacion |

### Procedimiento de Generacion

1. **Desde la ficha UT:**
   - Ir a la pestana **Analisis**
   - Verificar que las puntuaciones esten calculadas
   - Hacer clic en **Generar Mapa de Calor**

2. **Seleccion de parametros:**
   - Tipo: Potencial o Riesgo
   - Metodo: KDE, IDW, o Grid
   - Tamano de celda: tipicamente 25-100 m

3. **Salida:**
   - Capa raster anadida a QGIS
   - Guardada en `pyarchinit_Raster_folder`
   - Simbologia aplicada automaticamente

### Mapa de Calor con Mascara Poligonal (GNA)

Para generar mapas de calor **dentro de un area de proyecto** (ej. perimetro de estudio):

1. **Preparar el poligono** del area de proyecto
2. **Usar Exportar GNA** (ver seccion siguiente)
3. El sistema **enmascara** automaticamente el mapa de calor al poligono

---

## Exportacion GNA - Geoportal Nacional de Arqueologia

### Que es el GNA?

El **Geoportal Nacional de Arqueologia** (GNA) es el sistema informativo del Ministerio de Cultura italiano para la gestion de datos arqueologicos territoriales. PyArchInit soporta la exportacion en formato GeoPackage estandar GNA.

### Estructura GeoPackage GNA

| Capa | Tipo | Descripcion |
|------|------|-------------|
| **MOPR** | Polygon | Area/Perimetro de proyecto |
| **MOSI** | Point/Polygon | Sitios arqueologicos (UT) |
| **VRP** | MultiPolygon | Carta del Potencial Arqueologico |
| **VRD** | MultiPolygon | Carta del Riesgo Arqueologico |

### Mapeo de Campos UT a MOSI GNA

| Campo GNA | Campo UT PyArchInit | Notas |
|-----------|---------------------|-------|
| ID | `{progetto}_{nr_ut}` | Identificador compuesto |
| AMA | `def_ut` | Vocabulario controlado GNA |
| OGD | `interpretazione_ut` | Definicion del objeto |
| OGT | `geometria` | Tipo de geometria |
| DES | `descrizione_ut` | Descripcion (max 10000 caracteres) |
| OGM | `metodo_rilievo_e_ricognizione` | Modalidad de identificacion |
| DTSI | `periodo_I` -> fecha | Fecha inicio (negativo para a.C.) |
| DTSF | `periodo_II` -> fecha | Fecha fin |
| PRVN | `nazione` | Pais |
| PVCR | `regione` | Region |
| PVCP | `provincia` | Provincia |
| PVCC | `comune` | Municipio |
| LCDQ | `quota` | Cota s.n.m. |

### Clasificacion VRP (Potencial)

| Rango | Codigo GNA | Etiqueta | Color |
|-------|------------|----------|-------|
| 0-20 | NV | No evaluable | Gris |
| 20-40 | NU | Nulo | Verde |
| 40-60 | BA | Bajo | Amarillo |
| 60-80 | ME | Medio | Naranja |
| 80-100 | AL | Alto | Rojo |

### Clasificacion VRD (Riesgo)

| Rango | Codigo GNA | Etiqueta | Color |
|-------|------------|----------|-------|
| 0-25 | NU | Nulo | Verde |
| 25-50 | BA | Bajo | Amarillo |
| 50-75 | ME | Medio | Naranja |
| 75-100 | AL | Alto | Rojo |

### Procedimiento de Exportacion GNA

1. **Preparacion de datos:**
   - Verificar que todas las UT tengan coordenadas
   - Calcular las puntuaciones de potencial/riesgo
   - Preparar el poligono del area de proyecto (MOPR)

2. **Inicio de exportacion:**
   - Desde la ficha UT, hacer clic en **Exportar GNA**
   - O menu **PyArchInit** > **GNA** > **Export**

3. **Configuracion:**
   ```
   Proyecto: [seleccionar proyecto]
   Area de proyecto: [seleccionar capa poligono MOPR]
   Salida: [ruta archivo .gpkg]

   [x] Exportar MOSI (sitios)
   [x] Generar VRP (potencial)
   [x] Generar VRD (riesgo)

   Metodo mapa de calor: KDE
   Tamano de celda: 50 m
   ```

4. **Ejecucion:**
   - Hacer clic en **Exportar**
   - Esperar la generacion (puede requerir algunos minutos)
   - El GeoPackage se guarda en la ruta especificada

5. **Verificacion de la salida:**
   - Abrir el GeoPackage en QGIS
   - Verificar las capas MOPR, MOSI, VRP, VRD
   - Comprobar que las geometrias VRP/VRD esten recortadas al MOPR

### Validacion GNA

Para validar la salida contra las especificaciones GNA:

1. Cargar el GeoPackage en la **plantilla GNA oficial**
2. Verificar que las capas sean reconocidas
3. Controlar los vocabularios controlados
4. Verificar las relaciones geometricas (MOSI dentro de MOPR)

---

## Exportacion PDF

### Ficha UT Individual

Exporta la ficha UT completa en formato PDF profesional.

**Contenido:**
- Cabecera con proyecto y numero UT
- Seccion Identificacion
- Seccion Localizacion
- Seccion Terreno
- Seccion Datos Survey
- Seccion Cronologia
- Seccion Analisis (potencial/riesgo con barras coloreadas)
- Seccion Documentacion

**Procedimiento:**
1. Seleccionar el registro UT
2. Hacer clic en el boton **PDF** en la barra de herramientas
3. El PDF se guarda en `pyarchinit_PDF_folder`

### Listado UT (Lista PDF)

Exporta un listado tabular de todas las UT en formato horizontal.

**Columnas:**
- UT, Proyecto, Definicion, Interpretacion
- Municipio, Coordenadas, Periodo I, Periodo II
- Hall/m2, Visibilidad, Potencial, Riesgo

**Procedimiento:**
1. Cargar las UT a exportar (busqueda o visualizar todo)
2. Hacer clic en el boton **Lista PDF** en la barra de herramientas
3. El PDF se guarda como `Listado_UT.pdf`

### Informe de Analisis UT

Genera un informe detallado del analisis potencial/riesgo.

**Contenido:**
1. Datos identificativos de la UT
2. Seccion Potencial Arqueologico
   - Puntuacion con indicador grafico
   - Texto narrativo descriptivo
   - Tabla de factores con contribuciones
3. Seccion Riesgo Arqueologico
   - Puntuacion con indicador grafico
   - Texto narrativo con recomendaciones
   - Tabla de factores con contribuciones
4. Seccion Metodologia

---

## Flujo de Trabajo Operativo Completo

### Fase 1: Configuracion del Proyecto

1. **Crear nuevo proyecto** en PyArchInit o usar uno existente
2. **Definir el area de estudio** (poligono MOPR)
3. **Configurar el CRS** del proyecto QGIS

### Fase 2: Registro de UT en Campo

1. **Apertura de la ficha UT**
2. **Nuevo registro** (clic en "New Record")
3. **Rellenar datos identificativos:**
   ```
   Proyecto: Survey Valle del Tiber 2024
   Nr. UT: 25
   ```

4. **Rellenar localizacion:**
   ```
   Region: Lacio
   Provincia: Roma
   Municipio: Fiano Romano
   Localidad: Colle Alto
   Coord. geograficas: 42.1234, 12.5678
   Cota: 125 m
   Precision GPS: 3 m
   ```

5. **Rellenar descripcion** (usando tesauro):
   ```
   Definicion: Concentracion de hallazgos
   Descripcion: Area eliptica de aprox. 50x30 m
   con concentracion de fragmentos ceramicos
   y ladrillos en ladera colinar...
   ```

6. **Rellenar datos survey** (usando tesauro):
   ```
   Tipo Survey: Prospeccion intensiva
   Cobertura Vegetal: Escasa
   Metodo GPS: GPS diferencial
   Condicion Superficie: Arado
   Accesibilidad: Acceso facil
   Condiciones Meteo: Soleado
   Visibilidad: 80%
   Fecha: 15/04/2024
   Responsable: Equipo A
   ```

7. **Rellenar materiales y cronologia:**
   ```
   Dimensiones: 1500 m2
   Hall/m2: 5-8
   Hallazgos diagnosticos: Ceramica comun,
   sigillata italica, ladrillos

   Periodo I: Romano
   Datacion I: siglos I-II d.C.
   Interpretacion I: Villa rustica
   ```

8. **Guardar** (clic en "Save")

### Fase 3: Creacion de Geometrias

1. **Cargar capa** `pyarchinit_ut_polygon`
2. **Activar edicion**
3. **Dibujar** el perimetro de la UT en el mapa
4. **Rellenar atributos**: progetto, nr_ut
5. **Guardar** la capa

### Fase 4: Analisis

1. **Abrir pestana Analisis** en la ficha UT
2. **Verificar** las puntuaciones calculadas automaticamente
3. **Generar mapa de calor** si es necesario
4. **Exportar informe PDF** del analisis

### Fase 5: Exportacion GNA (si es necesario)

1. **Verificar completitud de datos** para todas las UT
2. **Preparar poligono MOPR** del area de proyecto
3. **Ejecutar Exportacion GNA**
4. **Validar salida** contra especificaciones GNA

---

## Consejos y Trucos

### Optimizacion del Flujo de Trabajo

1. **Preconfigurar los tesauros** antes de iniciar las prospecciones
2. **Usar plantillas de proyecto** con datos comunes preestablecidos
3. **Sincronizar coordenadas** del GPS al campo `coord_geografiche`
4. **Guardar frecuentemente** durante la compilacion

### Mejorar la Calidad de los Datos

1. **Rellenar TODOS los campos** relevantes para cada UT
2. **Usar siempre los tesauros** en lugar de texto libre
3. **Verificar las coordenadas** en el mapa antes de guardar
4. **Documentar fotograficamente** cada UT

### Optimizacion de Mapas de Calor

1. **Tamano de celda apropiado**: usar 25-50m para areas pequenas, 100-200m para areas extensas
2. **Metodo KDE** para distribuciones continuas y homogeneas
3. **Metodo IDW** cuando los valores puntuales son criticos
4. **Verificar siempre** que las coordenadas sean correctas antes de generar

### Exportacion GNA Eficiente

1. **Preparar el poligono MOPR** con antelacion como capa separada
2. **Verificar que todas las UT** tengan coordenadas validas
3. **Calcular las puntuaciones** antes de la exportacion
4. **Usar nombres de archivo** descriptivos para los GeoPackage

### Gestion Multiusuario

1. **Definir convenciones** de numeracion UT compartidas
2. **Usar base de datos PostgreSQL** para acceso concurrente
3. **Sincronizar periodicamente** los datos
4. **Documentar las modificaciones** en los campos de notas

---

## Solucion de Problemas

### Problema: Combobox de Tesauro Vacios

**Sintomas:** Los menus desplegables para survey_type, vegetation, etc. estan vacios.

**Causas:**
- Entradas del tesauro no presentes en la base de datos
- Codigo de idioma incorrecto
- Tabla de tesauro no actualizada

**Soluciones:**
1. Menu **PyArchInit** > **Database** > **Actualizar base de datos**
2. Verificar tabla `pyarchinit_thesaurus_sigle` para entradas `ut_table`
3. Comprobar configuracion de idioma
4. Si es necesario, reimportar los tesauros desde la plantilla

### Problema: Coordenadas No Validas

**Sintomas:** Error al guardar o coordenadas visualizadas en posicion incorrecta.

**Causas:**
- Formato incorrecto (coma vs punto decimal)
- Sistema de referencia no correspondiente
- Orden lat/lon invertido

**Soluciones:**
1. Formato correcto `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Formato correcto `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Usar siempre el punto como separador decimal
4. Verificar CRS del proyecto QGIS

### Problema: UT No Visible en el Mapa

**Sintomas:** Despues de guardar, la UT no aparece en el mapa.

**Causas:**
- Geometria no creada en la capa
- Atributos `progetto`/`nr_ut` no correspondientes
- Capa no cargada u oculta
- CRS diferente entre capa y proyecto

**Soluciones:**
1. Verificar que exista la capa `pyarchinit_ut_point/polygon`
2. Comprobar que los atributos esten correctamente rellenados
3. Activar la visibilidad de la capa en el panel Capas
4. Usar "Zoom a la Capa" para verificar la extension

### Problema: Mapa de Calor No Generado

**Sintomas:** Error "Se necesitan al menos 2 puntos con coordenadas validas".

**Causas:**
- Menos de 2 UT con coordenadas
- Coordenadas en formato incorrecto
- Campos de coordenadas vacios

**Soluciones:**
1. Verificar que al menos 2 UT tengan `coord_geografiche` O `coord_piane` rellenados
2. Comprobar el formato de las coordenadas (punto decimal, orden correcto)
3. Recalcular las puntuaciones antes de generar el mapa de calor
4. Verificar que los campos no contengan caracteres especiales

### Problema: Puntuacion Potencial/Riesgo No Calculada

**Sintomas:** Los campos potencial_score y risk_score estan vacios o son cero.

**Causas:**
- Campos obligatorios no rellenados
- Valores del tesauro no reconocidos
- Error en el calculo

**Soluciones:**
1. Rellenar al menos: `def_ut`, `periodo_I`, `visibility_percent`
2. Usar valores del tesauro (no texto libre)
3. Guardar el registro y reabrirlo
4. Verificar en los logs de QGIS posibles errores

### Problema: Exportacion GNA Fallida

**Sintomas:** El GeoPackage no se crea o esta incompleto.

**Causas:**
- Modulo GNA no disponible
- Datos UT incompletos
- Poligono MOPR no valido
- Permisos de escritura insuficientes

**Soluciones:**
1. Verificar que el modulo `modules/gna` este instalado
2. Comprobar que todas las UT tengan coordenadas validas
3. Verificar que el poligono MOPR sea valido (sin autointersecciones)
4. Comprobar permisos en la carpeta de salida
5. Verificar espacio en disco suficiente

### Problema: Exportacion PDF con Campos Faltantes

**Sintomas:** El PDF generado no muestra algunos campos o muestra valores incorrectos.

**Causas:**
- Campos de base de datos no actualizados
- Version del esquema de base de datos obsoleta
- Datos no guardados antes de la exportacion

**Soluciones:**
1. Guardar el registro antes de exportar
2. Actualizar la base de datos si es necesario
3. Verificar que los nuevos campos (v4.9.67+) existan en la tabla

### Problema: Error Qt6/QGIS 4.x

**Sintomas:** El plugin no carga en QGIS 4.x con error `AllDockWidgetFeatures`.

**Causas:**
- Incompatibilidad Qt5/Qt6
- Archivo UI no actualizado

**Soluciones:**
1. Actualizar PyArchInit a la ultima version
2. El archivo `UT_ui.ui` debe usar flags explicitos en lugar de `AllDockWidgetFeatures`

---

## Referencias

### Base de Datos

- **Tabla**: `ut_table`
- **Clase mapper**: `UT`
- **ID**: `id_ut`

### Tablas Geometricas

- **Puntos**: `pyarchinit_ut_point`
- **Lineas**: `pyarchinit_ut_line`
- **Poligonos**: `pyarchinit_ut_polygon`

### Archivos Fuente

| Archivo | Descripcion |
|---------|-------------|
| `gui/ui/UT_ui.ui` | Interfaz de usuario Qt |
| `tabs/UT.py` | Controlador principal |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | Exportacion PDF fichas |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | Exportacion PDF analisis |
| `modules/analysis/ut_potential.py` | Calculo de potencial |
| `modules/analysis/ut_risk.py` | Calculo de riesgo |
| `modules/analysis/ut_heatmap_generator.py` | Generacion de mapas de calor |
| `modules/gna/gna_exporter.py` | Exportacion GNA |
| `modules/gna/gna_vocabulary_mapper.py` | Mapeo de vocabularios GNA |

### Codigos de Tesauro UT

| Codigo | Campo | Descripcion |
|--------|-------|-------------|
| 12.1 | survey_type | Tipo de prospeccion |
| 12.2 | vegetation_coverage | Cobertura vegetal |
| 12.3 | gps_method | Metodo GPS |
| 12.4 | surface_condition | Condicion de superficie |
| 12.5 | accessibility | Accesibilidad |
| 12.6 | weather_conditions | Condiciones meteorologicas |
| 12.7 | def_ut | Definicion UT |

---

## Video Tutorial

### Documentacion de Prospecciones
**Duracion**: 15-18 minutos
- Registro de UT
- Datos de survey con tesauro
- Geolocalizacion

### Analisis de Potencial y Riesgo
**Duracion**: 10-12 minutos
- Calculo automatico de puntuaciones
- Interpretacion de resultados
- Generacion de mapas de calor

### Exportacion GNA
**Duracion**: 12-15 minutos
- Preparacion de datos
- Configuracion de exportacion
- Validacion de la salida

### Exportacion de Informes PDF
**Duracion**: 8-10 minutos
- Ficha UT estandar
- Listado UT
- Informe de analisis con mapas

---

*Ultima actualizacion: Enero 2026*
*PyArchInit v4.9.68 - Sistema de Gestion de Datos Arqueologicos*
