# Tutorial 21: Ficha UT - Unidades Topográficas

## Introducción

La **Ficha UT** (Unidades Topográficas) es el módulo de PyArchInit dedicado a la documentación de las prospecciones arqueológicas de superficie (survey). Permite registrar los datos relativos a las concentraciones de materiales, anomalías del terreno y sitios identificados durante las prospecciones.

### Conceptos Básicos

**Unidad Topográfica (UT):**
- Área delimitada con características arqueológicas homogéneas
- Identificada durante prospección de superficie
- Definida por concentración de materiales o anomalías visibles

**Prospección (Survey):**
- Prospección sistemática del territorio
- Recogida de datos sobre presencia antrópica antigua
- Documentación sin excavación

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha UT** (o **TU form**)

### Vía Toolbar
1. Localizar la toolbar PyArchInit
2. Hacer clic en el icono **UT**

---

## Vista General de la Interfaz

La ficha contiene numerosos campos para documentar todos los aspectos de la prospección.

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | Campos Identificativos | Proyecto, Nr. UT |
| 3 | Localización | Datos geográficos y administrativos |
| 4 | Descripción | Definición, descripción, interpretación |
| 5 | Datos Survey | Condiciones, metodología |
| 6 | Cronología | Períodos y dataciones |

---

## Campos Identificativos

### Proyecto

**Campo**: `lineEdit_progetto`
**Base de datos**: `progetto`

Nombre del proyecto de prospección.

### Número UT

**Campo**: `lineEdit_nr_ut`
**Base de datos**: `nr_ut`

Número progresivo de la Unidad Topográfica.

### UT Literal

**Campo**: `lineEdit_ut_letterale`
**Base de datos**: `ut_letterale`

Eventual sufijo alfabético (ej. UT 15a, 15b).

---

## Campos de Localización

### Datos Administrativos

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| País | `nazione` | Estado |
| Región | `regione` | Región administrativa |
| Provincia | `provincia` | Provincia |
| Municipio | `comune` | Municipio |
| Fracción | `frazione` | Fracción/localidad |
| Localidad | `localita` | Topónimo local |
| Dirección | `indirizzo` | Calle/carretera |
| Nr. cívico | `nr_civico` | Número cívico |

### Datos Cartográficos

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Carta IGM | `carta_topo_igm` | Hoja IGM |
| Carta CTR | `carta_ctr` | Elemento CTR |
| Hoja catastral | `foglio_catastale` | Referencia catastro |

### Coordenadas

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Coord. geográficas | `coord_geografiche` | Lat/Long |
| Coord. planas | `coord_piane` | UTM/Gauss-Boaga |
| Cota | `quota` | Altitud s.n.m. |
| Precisión coord. | `coordinate_precision` | Exactitud GPS |
| Método GPS | `gps_method` | Tipo de levantamiento |

---

## Campos Descriptivos

### Definición UT

**Campo**: `comboBox_def_ut`
**Base de datos**: `def_ut`

Clasificación tipológica de la UT.

**Valores:**
- Concentración de materiales
- Área de fragmentos
- Anomalía del terreno
- Estructura aflorante
- Sitio arqueológico

### Descripción UT

**Campo**: `textEdit_descrizione`
**Base de datos**: `descrizione_ut`

Descripción detallada de la Unidad Topográfica.

**Contenidos:**
- Extensión y forma del área
- Densidad de los materiales
- Características del terreno
- Visibilidad y condiciones

### Interpretación UT

**Campo**: `textEdit_interpretazione`
**Base de datos**: `interpretazione_ut`

Interpretación funcional/histórica.

---

## Datos Ambientales

### Pendiente del Terreno

**Campo**: `comboBox_terreno`
**Base de datos**: `andamento_terreno_pendenza`

Morfología y pendiente.

**Valores:**
- Llano
- Pendiente suave
- Pendiente media
- Pendiente fuerte
- Aterrazado

### Uso del Suelo

**Campo**: `comboBox_suolo`
**Base de datos**: `utilizzo_suolo_vegetazione`

Uso del suelo en el momento de la prospección.

**Valores:**
- Arado
- Prado/pasto
- Viñedo
- Olivar
- Sin cultivar
- Bosque
- Urbano

### Descripción del Suelo

**Campo**: `textEdit_suolo`
**Base de datos**: `descrizione_empirica_suolo`

Características pedológicas observadas.

### Descripción del Lugar

**Campo**: `textEdit_luogo`
**Base de datos**: `descrizione_luogo`

Contexto paisajístico.

---

## Datos de Survey

### Método de Prospección

**Campo**: `comboBox_metodo`
**Base de datos**: `metodo_rilievo_e_ricognizione`

Metodología adoptada.

**Valores:**
- Prospección sistemática
- Prospección extensiva
- Prospección dirigida
- Control de señalización

### Tipo de Survey

**Campo**: `comboBox_survey_type`
**Base de datos**: `survey_type`

Tipología de prospección.

### Visibilidad

**Campo**: `spinBox_visibility`
**Base de datos**: `visibility_percent`

Porcentaje de visibilidad del suelo (0-100%).

### Cobertura de Vegetación

**Campo**: `comboBox_vegetation`
**Base de datos**: `vegetation_coverage`

Grado de cobertura vegetal.

### Condición de Superficie

**Campo**: `comboBox_surface`
**Base de datos**: `surface_condition`

Estado de la superficie.

**Valores:**
- Arado reciente
- Arado no fresado
- Hierba baja
- Hierba alta
- Rastrojos

### Accesibilidad

**Campo**: `comboBox_accessibility`
**Base de datos**: `accessibility`

Facilidad de acceso al área.

### Fecha

**Campo**: `dateEdit_data`
**Base de datos**: `data`

Fecha de la prospección.

### Hora/Meteorología

**Campo**: `lineEdit_meteo`
**Base de datos**: `ora_meteo`

Condiciones meteorológicas y hora.

### Responsable

**Campo**: `comboBox_responsabile`
**Base de datos**: `responsabile`

Responsable de la prospección.

### Equipo

**Campo**: `textEdit_team`
**Base de datos**: `team_members`

Componentes del grupo.

---

## Datos de Materiales

### Dimensiones UT

**Campo**: `lineEdit_dimensioni`
**Base de datos**: `dimensioni_ut`

Extensión en m².

### Hallazgos por m²

**Campo**: `lineEdit_rep_mq`
**Base de datos**: `rep_per_mq`

Densidad de materiales.

### Hallazgos Diagnósticos

**Campo**: `textEdit_rep_datanti`
**Base de datos**: `rep_datanti`

Descripción de materiales diagnósticos.

---

## Cronología

### Período I

| Campo | Base de datos |
|-------|---------------|
| Período I | `periodo_I` |
| Datación I | `datazione_I` |
| Interpretación I | `interpretazione_I` |

### Período II

| Campo | Base de datos |
|-------|---------------|
| Período II | `periodo_II` |
| Datación II | `datazione_II` |
| Interpretación II | `interpretazione_II` |

---

## Otros Campos

### Geometría

**Campo**: `comboBox_geometria`
**Base de datos**: `geometria`

Forma de la UT.

### Bibliografía

**Campo**: `textEdit_bibliografia`
**Base de datos**: `bibliografia`

Referencias bibliográficas.

### Documentación

**Campo**: `textEdit_documentazione`
**Base de datos**: `documentazione`

Documentación producida (fotos, dibujos).

### Documentación Fotográfica

**Campo**: `textEdit_photo_doc`
**Base de datos**: `photo_documentation`

Lista de documentación fotográfica.

### Organismos de Tutela/Restricciones

**Campo**: `textEdit_vincoli`
**Base de datos**: `enti_tutela_vincoli`

Restricciones y organismos de tutela.

### Investigaciones Preliminares

**Campo**: `textEdit_indagini`
**Base de datos**: `indagini_preliminari`

Eventuales investigaciones ya realizadas.

---

## Workflow Operativo

### Registro de Nueva UT

1. **Apertura de ficha**
   - Vía menú o toolbar

2. **Nuevo registro**
   - Clic en "New Record"

3. **Datos identificativos**
   ```
   Proyecto: Survey Valle del Tíber 2024
   Nr. UT: 25
   ```

4. **Localización**
   ```
   Región: Lacio
   Provincia: Roma
   Municipio: Fiano Romano
   Localidad: Colle Alto
   Coord.: 42.1234 N, 12.5678 E
   Cota: 125 m
   ```

5. **Descripción**
   ```
   Definición: Concentración de materiales
   Descripción: Área elíptica de aprox. 50x30 m
   con concentración de fragmentos cerámicos
   y ladrillos en ladera colinar expuesta
   al sur...
   ```

6. **Datos de survey**
   ```
   Método: Prospección sistemática
   Visibilidad: 80%
   Condición: Arado reciente
   Fecha: 15/04/2024
   Responsable: Equipo A
   ```

7. **Materiales y cronología**
   ```
   Dimensiones: 1500 m²
   Hall/m²: 5-8
   Hallazgos diagnósticos: Cerámica común,
   sigillata itálica, ladrillos

   Período I: Romano
   Datación I: siglos I-II d.C.
   Interpretación I: Villa rústica
   ```

8. **Guardado**
   - Clic en "Save"

---

## Integración GIS

La ficha UT está estrechamente integrada con QGIS:

- **Capa UT**: visualización de geometrías
- **Atributos conectados**: datos desde la ficha
- **Selección desde mapa**: clic en geometría abre la ficha

---

## Export PDF

La ficha soporta la exportación en PDF para:
- Fichas UT individuales
- Listados por proyecto
- Informes de survey

---

## Buenas Prácticas

### Nomenclatura

- Numeración progresiva por proyecto
- Usar sufijos para subdivisiones
- Documentar las convenciones

### Geolocalización

- Usar GPS diferencial cuando sea posible
- Indicar siempre el método y la precisión
- Verificar las coordenadas en el mapa

### Documentación

- Fotografiar cada UT
- Producir croquis planimétricos
- Registrar condiciones de visibilidad

### Materiales

- Recoger muestras diagnósticas
- Estimar densidad por área
- Documentar distribución espacial

---

## Resolución de Problemas

### Problema: Coordenadas no válidas

**Causa**: Formato incorrecto o sistema de referencia.

**Solución**:
1. Verificar el formato (DD o DMS)
2. Controlar el sistema de referencia
3. Usar la herramienta de conversión de QGIS

### Problema: UT no visible en el mapa

**Causa**: Geometría no asociada.

**Solución**:
1. Verificar que exista la capa UT
2. Controlar que el registro tenga geometría
3. Verificar la proyección de la capa

---

## Referencias

### Base de Datos

- **Tabla**: `ut_table`
- **Clase mapper**: `UT`
- **ID**: `id_ut`

### Archivos Fuente

- **UI**: `gui/ui/UT_ui.ui`
- **Controlador**: `tabs/UT.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_UTsheet_pdf.py`

---

## Video Tutorial

### Documentación de Prospecciones
**Duración**: 15-18 minutos
- Registro de UT
- Datos de survey
- Geolocalización

[Placeholder video: video_ut_survey.mp4]

### Integración GIS Survey
**Duración**: 10-12 minutos
- Capas y atributos
- Visualización de resultados
- Análisis espacial

[Placeholder video: video_ut_gis.mp4]

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
