# Tutorial 15: Ficha de Arqueozoología (Fauna)

## Introducción

La **Ficha de Arqueozoología/Fauna** (FICHA FR - Fauna Record) es el módulo de PyArchInit dedicado al análisis y documentación de los restos faunísticos. Permite registrar datos arqueozoológicos detallados para el estudio de las economías de subsistencia antiguas.

### Conceptos Básicos

**Arqueozoología:**
- Estudio de los restos animales de contextos arqueológicos
- Análisis de las relaciones hombre-animal en el pasado
- Reconstrucción de dietas, ganadería, caza

**Datos registrados:**
- Identificación taxonómica (especie)
- Partes esqueléticas presentes
- NMI (Número Mínimo de Individuos)
- Estado de conservación
- Huellas tafonómicas
- Marcas de carnicería

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha de Fauna** (o **Fauna form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Fauna** (hueso estilizado)

---

## Vista General de la Interfaz

La ficha está organizada en pestañas temáticas:

### Pestañas Principales

| # | Pestaña | Contenido |
|---|---------|-----------|
| 1 | Datos Identificativos | Sitio, Área, UE, Contexto |
| 2 | Datos Arqueozoológicos | Especie, NMI, Partes esqueléticas |
| 3 | Datos Tafonómicos | Conservación, Fragmentación, Huellas |
| 4 | Datos Contextuales | Contexto deposicional, Asociaciones |
| 5 | Estadísticas | Gráficos y cuantificaciones |

---

## Toolbar

La barra de herramientas proporciona las funciones estándar:

| Icono | Función |
|-------|---------|
| First/Prev/Next/Last | Navegación de registros |
| New | Nuevo registro |
| Save | Guardar |
| Delete | Eliminar |
| Search | Búsqueda |
| View All | Ver todos |
| PDF | Exportar PDF |

---

## Pestaña Datos Identificativos

### Selección de UE

**Campo**: `comboBox_us_select`

Selecciona la UE de procedencia. Muestra las UE disponibles en el formato "Sitio - Área - UE".

### Sitio

**Campo**: `comboBox_sito`
**Base de datos**: `sito`

Sitio arqueológico.

### Área

**Campo**: `comboBox_area`
**Base de datos**: `area`

Área de excavación.

### Sondeo

**Campo**: `comboBox_saggio`
**Base de datos**: `saggio`

Sondeo/trinchera de procedencia.

### UE

**Campo**: `comboBox_us`
**Base de datos**: `us`

Unidad Estratigráfica.

### Datación UE

**Campo**: `lineEdit_datazione`
**Base de datos**: `datazione_us`

Encuadramiento cronológico de la UE.

### Responsable

**Campo**: `comboBox_responsabile`
**Base de datos**: `responsabile_scheda`

Autor de la catalogación.

### Fecha de Compilación

**Campo**: `dateEdit_data`
**Base de datos**: `data_compilazione`

Fecha de compilación de la ficha.

---

## Pestaña Datos Arqueozoológicos

### Contexto

**Campo**: `comboBox_contesto`
**Base de datos**: `contesto`

Tipo de contexto deposicional.

**Valores:**
- Hábitat
- Vertedero/Basurero
- Relleno
- Estrato de ocupación
- Sepultura
- Ritual

### Especie

**Campo**: `comboBox_specie`
**Base de datos**: `specie`

Identificación taxonómica.

**Especies comunes en arqueozoología:**
| Especie | Nombre científico |
|---------|-------------------|
| Bovino | Bos taurus |
| Ovino | Ovis aries |
| Caprino | Capra hircus |
| Porcino | Sus domesticus |
| Equino | Equus caballus |
| Ciervo | Cervus elaphus |
| Jabalí | Sus scrofa |
| Liebre | Lepus europaeus |
| Perro | Canis familiaris |
| Gato | Felis catus |
| Aves de corral | Gallus gallus |

### Número Mínimo de Individuos (NMI)

**Campo**: `spinBox_nmi`
**Base de datos**: `numero_minimo_individui`

Estimación del número mínimo de individuos representados.

### Partes Esqueléticas

**Campo**: `tableWidget_parti`
**Base de datos**: `parti_scheletriche`

Tabla para registrar las partes anatómicas presentes.

**Columnas:**
| Columna | Descripción |
|---------|-------------|
| Elemento | Hueso/parte anatómica |
| Lado | Dcho/Izq/Axial |
| Cantidad | Número de fragmentos |
| NMI | Contribución al NMI |

### Medidas de Huesos

**Campo**: `tableWidget_misure`
**Base de datos**: `misure_ossa`

Mediciones osteométricas estándar.

---

## Pestaña Datos Tafonómicos

### Estado de Fragmentación

**Campo**: `comboBox_frammentazione`
**Base de datos**: `stato_frammentazione`

Grado de fragmentación de los restos.

**Valores:**
- Íntegro
- Poco fragmentado
- Fragmentado
- Muy fragmentado

### Estado de Conservación

**Campo**: `comboBox_conservazione`
**Base de datos**: `stato_conservazione`

Condiciones generales de conservación.

**Valores:**
- Óptimo
- Bueno
- Regular
- Malo
- Pésimo

### Huellas de Combustión

**Campo**: `comboBox_combustione`
**Base de datos**: `tracce_combustione`

Presencia de huellas de fuego.

**Valores:**
- Ausentes
- Ennegrecimiento
- Carbonización
- Calcinación

### Marcas Tafonómicas

**Campo**: `comboBox_segni_tafo`
**Base de datos**: `segni_tafonomici_evidenti`

Huellas de alteración post-deposicional.

**Tipos:**
- Weathering (agentes atmosféricos)
- Root marks (raíces)
- Gnawing (roeduras)
- Trampling (pisoteo)

### Alteraciones Morfológicas

**Campo**: `textEdit_alterazioni`
**Base de datos**: `alterazioni_morfologiche`

Descripción detallada de las alteraciones observadas.

---

## Pestaña Datos Contextuales

### Metodología de Recuperación

**Campo**: `comboBox_metodologia`
**Base de datos**: `metodologia_recupero`

Método de recogida de los restos.

**Valores:**
- A simple vista
- Cribado en seco
- Flotación
- Cribado húmedo

### Restos en Conexión Anatómica

**Campo**: `checkBox_connessione`
**Base de datos**: `resti_connessione_anatomica`

Presencia de partes en conexión.

### Clases de Hallazgos en Asociación

**Campo**: `textEdit_associazioni`
**Base de datos**: `classi_reperti_associazione`

Otros materiales asociados a los restos faunísticos.

### Observaciones

**Campo**: `textEdit_osservazioni`
**Base de datos**: `osservazioni`

Notas generales.

### Interpretación

**Campo**: `textEdit_interpretazione`
**Base de datos**: `interpretazione`

Interpretación del contexto faunístico.

---

## Pestaña Estadísticas

Proporciona herramientas para:
- Gráficos de distribución por especie
- Cálculo de NMI totales
- Comparaciones entre UE/fases
- Exportación de datos estadísticos

---

## Workflow Operativo

### Catalogación de Restos Faunísticos

1. **Apertura de la ficha**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en "New Record"

3. **Datos identificativos**
   ```
   Sitio: Villa Romana
   Área: 1000
   UE: 150
   Responsable: G. Verdi
   Fecha: 20/07/2024
   ```

4. **Datos arqueozoológicos** (Pestaña 2)
   ```
   Contexto: Vertedero/Basurero
   Especie: Bos taurus
   NMI: 3

   Partes esqueléticas:
   - Húmero / Dcho / 2 / 1
   - Tibia / Izq / 3 / 2
   - Metapodio / - / 5 / 1
   ```

5. **Datos tafonómicos** (Pestaña 3)
   ```
   Fragmentación: Fragmentado
   Conservación: Bueno
   Combustión: Ausentes
   Marcas tafonómicas: Root marks
   ```

6. **Interpretación**
   ```
   Vertedero de residuos alimentarios.
   Presencia de marcas de carnicería
   en algunos huesos largos.
   ```

7. **Guardado**
   - Clic en "Save"

---

## Buenas Prácticas

### Identificación

- Utilizar colecciones de referencia
- Indicar el grado de certeza de la ID
- Registrar también los restos no identificables

### NMI

- Calcular para cada especie por separado
- Considerar lado y edad de los restos
- Documentar el método de cálculo

### Tafonomía

- Observar sistemáticamente cada resto
- Documentar las huellas antes del lavado
- Fotografiar casos significativos

### Contexto

- Conectar siempre a la UE de procedencia
- Registrar el método de recuperación
- Anotar asociaciones significativas

---

## Export PDF

La ficha permite generar:
- Fichas individuales detalladas
- Listas por UE o fase
- Informes estadísticos

---

## Resolución de Problemas

### Problema: Especie no disponible

**Causa**: Lista de especies incompleta.

**Solución**:
1. Verificar el tesauro de fauna
2. Añadir las especies faltantes
3. Contactar al administrador

### Problema: NMI no calculado

**Causa**: Partes esqueléticas no registradas.

**Solución**:
1. Completar la tabla de partes esqueléticas
2. Indicar lado y cantidad
3. El sistema calculará automáticamente

---

## Referencias

### Base de Datos

- **Tabla**: `fauna_table`
- **Clase mapper**: `FAUNA`
- **ID**: `id_fauna`

### Archivos Fuente

- **Controlador**: `tabs/Fauna.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
