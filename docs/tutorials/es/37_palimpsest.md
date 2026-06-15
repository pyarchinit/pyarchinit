# Tutorial 37: Análisis de palimpsestos (palimpsestr / SEF)

## Introducción

PyArchInit integra **palimpsestr**, una librería R que aplica el modelo
**SEF — Stratigraphic Entanglement Field** para la *descomposición probabilística
de los palimpsestos*: separa, sobre una base estadística, los hallazgos de un
depósito complejo en **fases** latentes, estimando para cada unidad estratigráfica
(US) la fase de pertenencia, la residualidad y las eventuales **intrusiones**.

El cuadro de diálogo **palimpsestr** (icono de estratos coloreados en la barra de
herramientas pyArchInit) permite:

- **Fit SEF**: estimar las fases y producir capas vectoriales (fases, enlaces) y una
  tabla diagnóstica;
- **Intrusiones**: detectar hallazgos/US fuera de lugar cronológicamente;
- **Informe narrado (PDF/DOCX)**: un informe interpretativo con texto, gráficos
  diagnósticos y tablas;
- **Informe IA**: un informe descriptivo generado por agentes de IA especializados,
  en cualquier idioma de pyArchInit;
- trabajar tanto en **SQLite/Spatialite** como en **PostgreSQL/PostGIS**;
- usar una **cronología absoluta** (fechas calibradas OxCal) en lugar de la
  datación textual.

> Requiere palimpsestr **≥ 0.22.0** instalado en la librería R utilizada por el
> *Processing R Provider* de QGIS.

---

## 1. Requisitos previos

- **R** instalado y el plugin **Processing R Provider** activo en QGIS.
- Paquete R **palimpsestr ≥ 0.22.0** (y dependencias: `sf`, `DBI`, `RSQLite`;
  `RPostgres` para PostgreSQL).
- Para el **informe PDF/DOCX**: **pandoc** y un motor **LaTeX** (p. ej. TinyTeX). Si
  faltan, igualmente se produce la narrativa Markdown `.md` + las figuras PNG.
- Para la **cronología OxCal**: paquete R **oxcAAR** y **Java** (el motor OxCal
  se descarga automáticamente en el primer uso mediante `oxcAAR::quickSetupOxcal()`).
- Para el **informe IA**: un proveedor LLM configurado (OpenAI, Anthropic, Ollama o
  LM Studio) mediante el selector Proveedor IA.

Los scripts R (`.rsx`) están **incluidos en el plugin** e instalados automáticamente
al abrir el cuadro de diálogo; el botón *Install/update R scripts* (Instalar/actualizar scripts R) los
reinstala manualmente.

---

## 2. Abrir el cuadro de diálogo

1. Barra de herramientas pyArchInit → menú de análisis → **palimpsestr - Analisi
   palinsesti**.
2. El cuadro de diálogo muestra la base de datos activa (SQLite o PostgreSQL) y los parámetros.

---

## 3. Parámetros del análisis

| Parámetro | Significado |
|---|---|
| **Número de fases (K)** | cuántas fases latentes estimar (2–12) |
| **Modelo de clase** | `multinomial` (recomendado) o `gaussiano` (legacy) |
| **Componente de ruido/outlier** | activa la estimación de intrusiones/residualidad |
| **Umbral de intrusiones** | posterior mínima para señalar un hallazgo como intrusión |
| **Hallazgos (source)** | **Ambos** / **Materiales** / **Cerámica** |
| **Sitio (filtro)** | limita el análisis a un sitio (vacío = todos) |

El selector **Hallazgos** es compartido por Fit, Intrusiones e Informe: todos respetan
la misma selección de hallazgos.

---

## 4. Fit SEF e Intrusiones

- **Fit SEF model**: ejecuta la descomposición y carga en el proyecto las capas
  *SEF phases* (puntos coloreados por fase) y *SEF links*, además de la tabla
  diagnóstica.
- **Detect intrusions**: carga una capa de puntos con `intrusion_prob`,
  `direction` e `intrusion_type`.

---

## 5. Informe narrado (PDF/DOCX)

1. Establece **Idioma del informe** (Italiano/English) y **Formato** (PDF+DOCX / PDF /
   DOCX).
2. Pulsa **Genera report (PDF/DOCX)** (Generar informe).
3. El **panel de resultados** muestra la narrativa leyendo el archivo `.md` que
   se escribe **siempre** junto al resultado.
4. Los botones **Apri PDF / Apri DOCX / Apri cartella** (Abrir PDF / Abrir DOCX / Abrir carpeta) se habilitan según los
   archivos efectivamente producidos.

> Si aparecen solo la narrativa `.md` y las figuras (sin PDF/DOCX), faltan
> pandoc/LaTeX: el cuadro de diálogo intenta añadirlos automáticamente al `PATH`; en
> caso contrario instálalos (en R: `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

Los análisis funcionan también sobre la conexión **PostgreSQL** activa de
pyArchInit, no solo sobre SQLite. El cuadro de diálogo convierte automáticamente la URL de
conexión en una DSN libpq y la pasa a los algoritmos (parámetro
`PG_connection`); con PostgreSQL activo no se solicita ningún archivo SQLite.

---

## 7. Cronología absoluta (OxCal)

La tabla opcional **`palimpsest_chronology`** proporciona fechas **calibradas por
US** (años calendarios, a.C. negativos) que palimpsestr usa **en lugar** de la
`datazione` textual.

1. Pulsa **Cronologia assoluta (OxCal)…** (Cronología absoluta).
2. **Crea/aggiorna tabella** (Crear/actualizar tabla): crea `palimpsest_chronology` sobre el backend activo
   (SQLite o PostgreSQL), de modo idempotente.
3. **Calibración en vivo**: introduce para cada US las fechas radiocarbónicas
   (BP ± error, código lab) y pulsa **Calibra e salva (OxCal)** (Calibrar y guardar): un driver R
   (`oxcAAR::oxcalCalibrate` + `palimpsestr::chronology_from_oxcal`) calcula los
   intervalos calendarios y los guarda como `start`/`end`.
4. **Importación CSV**: como alternativa, importa un CSV ya calibrado con columnas
   `sito, area, us, start, end, lab_code, source`.

Los datos de ejemplo están en `docs/examples/`:
`palimpsest_oxcal_samples_villa_romana.csv` (muestras C14 para la calibración) y
`palimpsest_chronology_villa_romana.csv` (intervalos ya calibrados).

> Una vez poblada, la tabla se detecta **automáticamente**: no hace falta
> modificar nada en los algoritmos.

---

## 8. Informe IA (análisis descriptivo)

El botón **Report AI (analisi descrittiva)…** (Informe IA - análisis descriptivo) genera un informe
**descriptivo y didáctico** con una pipeline de **agentes de IA especializados**:

1. **Metodólogo** — explica las decisiones: el modelo (multinomial vs gaussiano), el
   valor de **K** y las evidencias diagnósticas que lo justifican, la
   componente de ruido y el **umbral**, la selección de hallazgos y el uso de la
   cronología OxCal; indica límites y cautelas.
2. **Analista** — interpreta fases, cronología (con las fechas absolutas si
   están presentes), residualidad/intrusiones y patrón espacial.
3. **Redactor** — compone un único informe cohesionado, remitiendo a las figuras.

Procedimiento:

1. Elige el **Proveedor IA** y el modelo en el selector.
2. Elige el **Idioma del informe** (todos los idiomas de pyArchInit:
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Pulsa **Genera report AI** (Generar informe IA): el texto aparece en tiempo real.
4. Guarda como **DOCX** (con las figuras incorporadas) o **Markdown**.

El informe explica explícitamente **por qué** se eligieron el modelo, el K y
el umbral, e interpreta los resultados de modo comprensible — lo ideal para la
relación de excavación.

---

*Documentación PyArchInit — Junio 2026*
