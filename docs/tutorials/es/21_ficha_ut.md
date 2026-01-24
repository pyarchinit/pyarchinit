# Tutorial 21: Ficha UT - Unidades Topográficas

## Introducción

La **Ficha UT** (Unidades Topográficas) es el módulo de PyArchInit dedicado a la documentación de las prospecciones arqueológicas de superficie. Permite registrar los datos relativos a las concentraciones de materiales, anomalías del terreno y sitios identificados durante las prospecciones.

### Conceptos Básicos

**Unidad Topográfica (UT):**
- Área delimitada con características arqueológicas homogéneas
- Identificada durante prospección de superficie
- Definida por concentración de materiales o anomalías visibles

**Prospección (Survey):**
- Exploración sistemática del territorio
- Recogida de datos sobre presencia antrópica antigua
- Documentación sin excavación

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha UT**

### Vía Barra de Herramientas
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **UT**

---

## Vista General de la Interfaz

La ficha está organizada en varias pestañas para documentar todos los aspectos de la prospección.

### Pestañas Principales

| # | Pestaña | Descripción |
|---|---------|-------------|
| 1 | Identificación | Proyecto, Nr. UT, Ubicación |
| 2 | Descripción | Definición, descripción, interpretación |
| 3 | Datos UT | Condiciones, metodología, fechas |
| 4 | Análisis | Potencial y riesgo arqueológico |

---

## Campos Identificativos

### Proyecto

**Campo**: `comboBox_progetto`
**Base de datos**: `progetto`

Nombre del proyecto de prospección.

### Número UT

**Campo**: `comboBox_nr_ut`
**Base de datos**: `nr_ut`

Número progresivo de la Unidad Topográfica.

### UT Literal

**Campo**: `lineEdit_ut_letterale`
**Base de datos**: `ut_letterale`

Sufijo alfabético opcional (ej. UT 15a, 15b).

---

## Campos de Localización

### Datos Administrativos

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| País | `nazione` | País |
| Región | `regione` | Región administrativa |
| Provincia | `provincia` | Provincia |
| Municipio | `comune` | Municipio |
| Fracción | `frazione` | Fracción/localidad |
| Localidad | `localita` | Topónimo local |
| Dirección | `indirizzo` | Calle/carretera |
| Nr. | `nr_civico` | Número |

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
| Precisión coord. | `coordinate_precision` | Precisión GPS |

---

## Campos Descriptivos

### Definición UT ⭐ NUEVO

**Campo**: `comboBox_def_ut`
**Base de datos**: `def_ut`
**Tesauro**: Código 12.7

Clasificación tipológica de la UT. Los valores se cargan del tesauro y se traducen automáticamente al idioma actual.

**Valores estándar:**
| Código | Español | Italiano |
|--------|---------|----------|
| scatter | Dispersión de materiales | Area di dispersione materiali |
| site | Yacimiento arqueológico | Sito archeologico |
| anomaly | Anomalía del terreno | Anomalia del terreno |
| structure | Estructura aflorante | Struttura affiorante |
| concentration | Concentración de hallazgos | Concentrazione reperti |
| traces | Trazas antrópicas | Tracce antropiche |
| findspot | Hallazgo esporádico | Rinvenimento sporadico |
| negative | Resultado negativo | Esito negativo |

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

## Campos Tesauro Survey ⭐ NUEVO

Los siguientes campos utilizan el sistema de tesauro para garantizar terminología estandarizada traducida a 7 idiomas (IT, EN, DE, ES, FR, AR, CA).

### Tipo de Survey (12.1)

**Campo**: `comboBox_survey_type`
**Base de datos**: `survey_type`

| Código | Español | Descripción |
|--------|---------|-------------|
| intensive | Prospección intensiva | Batida sistemática intensiva |
| extensive | Prospección extensiva | Reconocimiento extensivo |
| targeted | Prospección dirigida | Investigación de áreas específicas |
| random | Muestreo aleatorio | Metodología de muestreo aleatorio |

### Cobertura Vegetal (12.2)

**Campo**: `comboBox_vegetation_coverage`
**Base de datos**: `vegetation_coverage`

| Código | Español | Descripción |
|--------|---------|-------------|
| none | Sin vegetación | Suelo desnudo |
| sparse | Vegetación escasa | Cobertura < 25% |
| moderate | Vegetación moderada | Cobertura 25-50% |
| dense | Vegetación densa | Cobertura 50-75% |
| very_dense | Vegetación muy densa | Cobertura > 75% |

### Método GPS (12.3)

**Campo**: `comboBox_gps_method`
**Base de datos**: `gps_method`

| Código | Español | Descripción |
|--------|---------|-------------|
| handheld | GPS de mano | Dispositivo GPS portátil |
| dgps | GPS diferencial | DGPS con estación base |
| rtk | GPS RTK | Cinemático en tiempo real |
| total_station | Estación total | Levantamiento con estación total |

### Condición de Superficie (12.4)

**Campo**: `comboBox_surface_condition`
**Base de datos**: `surface_condition`

| Código | Español | Descripción |
|--------|---------|-------------|
| ploughed | Arado | Campo recién arado |
| stubble | Rastrojo | Presencia de rastrojos |
| pasture | Pasto | Pradera/pasto |
| woodland | Bosque | Área boscosa |
| urban | Urbano | Área urbana/edificada |

### Accesibilidad (12.5)

**Campo**: `comboBox_accessibility`
**Base de datos**: `accessibility`

| Código | Español | Descripción |
|--------|---------|-------------|
| easy | Acceso fácil | Sin restricciones |
| moderate_access | Acceso moderado | Algunas dificultades |
| difficult | Acceso difícil | Problemas significativos |
| restricted | Acceso restringido | Solo con permiso |

### Condiciones Meteorológicas (12.6)

**Campo**: `comboBox_weather_conditions`
**Base de datos**: `weather_conditions`

| Código | Español | Descripción |
|--------|---------|-------------|
| sunny | Soleado | Despejado y soleado |
| cloudy | Nublado | Condiciones nubosas |
| rainy | Lluvioso | Lluvia durante prospección |
| windy | Ventoso | Vientos fuertes |

---

## Datos Ambientales

### Porcentaje de Visibilidad

**Campo**: `spinBox_visibility_percent`
**Base de datos**: `visibility_percent`

Porcentaje de visibilidad del suelo (0-100%). Valor numérico.

### Pendiente del Terreno

**Campo**: `lineEdit_andamento_terreno_pendenza`
**Base de datos**: `andamento_terreno_pendenza`

Morfología y pendiente del terreno.

### Uso del Suelo

**Campo**: `lineEdit_utilizzo_suolo_vegetazione`
**Base de datos**: `utilizzo_suolo_vegetazione`

Uso del suelo en el momento de la prospección.

---

## Datos de Materiales

### Dimensiones UT

**Campo**: `lineEdit_dimensioni_ut`
**Base de datos**: `dimensioni_ut`

Extensión del área en m².

### Hallazgos por m²

**Campo**: `lineEdit_rep_per_mq`
**Base de datos**: `rep_per_mq`

Densidad de materiales por metro cuadrado.

### Hallazgos Diagnósticos

**Campo**: `lineEdit_rep_datanti`
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

## Pestaña Análisis ⭐ NUEVO

La pestaña **Análisis** proporciona herramientas avanzadas para el cálculo automático del potencial y riesgo arqueológico.

### Potencial Arqueológico

El sistema calcula una puntuación de 0 a 100 basándose en:

| Factor | Peso | Descripción |
|--------|------|-------------|
| Definición UT | 30% | Tipo de evidencia arqueológica |
| Período histórico | 25% | Cronología de materiales |
| Densidad de hallazgos | 20% | Materiales por m² |
| Condición superficie | 15% | Visibilidad y accesibilidad |
| Documentación | 10% | Calidad de documentación |

**Visualización:**
- Barra de progreso coloreada (verde = alto, amarillo = medio, rojo = bajo)
- Tabla detallada de factores con puntuaciones individuales
- Texto narrativo automático con interpretación

### Riesgo Arqueológico

Evalúa el riesgo de impacto/pérdida del patrimonio:

| Factor | Peso | Descripción |
|--------|------|-------------|
| Accesibilidad | 25% | Facilidad de acceso al área |
| Uso del suelo | 25% | Actividades agrícolas/constructivas |
| Restricciones existentes | 20% | Protecciones legales |
| Investigaciones previas | 15% | Estado del conocimiento |
| Visibilidad | 15% | Exposición del sitio |

### Generación de Mapas de Calor

El botón **Generar Mapa de Calor** crea capas ráster que muestran:
- **Mapa de Potencial**: distribución espacial del potencial arqueológico
- **Mapa de Riesgo**: mapa de riesgo de impacto

**Métodos disponibles:**
- Estimación de Densidad Kernel (KDE)
- Ponderación por Distancia Inversa (IDW)
- Vecino Natural

---

## Exportación PDF ⭐ MEJORADO

### Ficha UT Estándar

Exporta la ficha UT completa con todos los campos rellenados.

### Informe de Análisis UT

Genera un informe PDF que incluye:

1. **Datos de identificación UT**
2. **Sección Potencial Arqueológico**
   - Puntuación con indicador gráfico
   - Texto narrativo descriptivo
   - Tabla de factores con contribuciones
   - Imagen del mapa de potencial (si se generó)
3. **Sección Riesgo Arqueológico**
   - Puntuación con indicador gráfico
   - Texto narrativo con recomendaciones
   - Tabla de factores con contribuciones
   - Imagen del mapa de riesgo (si se generó)
4. **Sección Metodología**
   - Descripción de algoritmos utilizados
   - Notas sobre ponderación de factores

El informe está disponible en los 7 idiomas soportados.

---

## Flujo de Trabajo Operativo

### Registro de Nueva UT

1. **Abrir ficha**
   - Vía menú o barra de herramientas

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

5. **Descripción** (usando tesauro)
   ```
   Definición: Concentración de hallazgos (del tesauro)
   Descripción: Área elíptica de aprox. 50x30 m
   con concentración de fragmentos cerámicos
   y ladrillos en ladera colinar expuesta
   al sur...
   ```

6. **Datos de survey** (usando tesauro)
   ```
   Tipo Survey: Prospección intensiva
   Cobertura Vegetal: Escasa
   Método GPS: GPS diferencial
   Condición Superficie: Arado
   Accesibilidad: Acceso fácil
   Condiciones Meteo: Soleado
   Visibilidad: 80%
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

8. **Análisis** (pestaña Análisis)
   - Verificar puntuación Potencial
   - Verificar puntuación Riesgo
   - Generar Mapa de Calor si es necesario

9. **Guardar**
   - Clic en "Save"

---

## Integración GIS

La ficha UT está estrechamente integrada con QGIS:

- **Capa UT**: visualización de geometrías
- **Atributos conectados**: datos desde la ficha
- **Selección desde mapa**: clic en geometría abre la ficha
- **Mapa de calor como capa**: los mapas generados se guardan como capas ráster

---

## Buenas Prácticas

### Uso del Tesauro

- Preferir siempre valores del tesauro para consistencia
- Los valores se traducen automáticamente al idioma del usuario
- Para nuevos valores, añadirlos primero al tesauro

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

### Análisis

- Verificar siempre las puntuaciones calculadas
- Generar mapas de calor para proyectos completos
- Exportar informes para documentación

---

## Códigos Tesauro UT

| Código | Campo | Descripción |
|--------|-------|-------------|
| 12.1 | survey_type | Tipo de survey |
| 12.2 | vegetation_coverage | Cobertura vegetal |
| 12.3 | gps_method | Método GPS |
| 12.4 | surface_condition | Condición de superficie |
| 12.5 | accessibility | Accesibilidad |
| 12.6 | weather_conditions | Condiciones meteorológicas |
| 12.7 | def_ut | Definición UT |

---

## Resolución de Problemas

### Problema: Comboboxes vacíos

**Causa**: Entradas del tesauro no presentes en la base de datos.

**Solución**:
1. Actualizar base de datos vía "Update database"
2. Verificar que la tabla `pyarchinit_thesaurus_sigle` contenga entradas para `ut_table`
3. Comprobar código de idioma en configuración

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

### Problema: Mapa de calor no generado

**Causa**: Datos insuficientes o error de cálculo.

**Solución**:
1. Verificar que existan al menos 3 UTs con datos completos
2. Comprobar que las geometrías sean válidas
3. Verificar espacio en disco disponible

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
- **PDF Análisis**: `modules/utility/pyarchinit_exp_UT_analysis_pdf.py`
- **Calculador Potencial**: `modules/analysis/ut_potential.py`
- **Calculador Riesgo**: `modules/analysis/ut_risk.py`
- **Generador Mapa Calor**: `modules/analysis/ut_heatmap_generator.py`

---

## Video Tutorial

### Documentación de Prospecciones
**Duración**: 15-18 minutos
- Registro de UT
- Datos de survey con tesauro
- Geolocalización

[Placeholder video: video_ut_survey.mp4]

### Análisis de Potencial y Riesgo
**Duración**: 10-12 minutos
- Cálculo automático de puntuaciones
- Interpretación de resultados
- Generación de mapas de calor

[Placeholder video: video_ut_analysis.mp4]

### Exportación de Informes PDF
**Duración**: 8-10 minutos
- Ficha UT estándar
- Informe de análisis con mapas
- Personalización de salida

[Placeholder video: video_ut_pdf.mp4]

---

*Última actualización: Enero 2026*
*PyArchInit v4.9.68 - Sistema de Gestión de Datos Arqueológicos*
