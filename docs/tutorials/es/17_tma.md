# Tutorial 17: TMA - Tabla de Materiales Arqueológicos

## Introducción

La **Ficha TMA** (Tabla de Materiales Arqueológicos) es el módulo avanzado de PyArchInit para la gestión de los materiales de excavación según los estándares ministeriales italianos. Permite una catalogación detallada conforme a las normativas ICCD (Istituto Centrale per il Catalogo e la Documentazione).

### Características Principales

- Catalogación conforme a estándares ICCD
- Gestión de materiales por caja/contenedor
- Campos cronológicos detallados
- Tabla de materiales asociados
- Gestión de media integrada
- Export de etiquetas y fichas PDF

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha TMA**

### Vía Toolbar
1. Localizar la toolbar PyArchInit
2. Hacer clic en el icono **TMA**

---

## Vista General de la Interfaz

La ficha presenta una interfaz compleja con muchos campos.

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | Campos Identificativos | Sitio, Área, UE, Caja |
| 3 | Campos Localización | Ubicación, Ambiente, Sondeo |
| 4 | Campos Cronológicos | Franja, Fracción, Cronologías |
| 5 | Tabla Materiales | Detalle de materiales asociados |
| 6 | Tab Media | Imágenes y documentos |

---

## Campos Identificativos

### Sitio

**Campo**: `comboBox_sito`
**Base de datos**: `sito`

Sitio arqueológico (SCAN - Denominación excavación ICCD).

### Área

**Campo**: `comboBox_area`
**Base de datos**: `area`

Área de excavación.

### UE (DSCU)

**Campo**: `comboBox_us`
**Base de datos**: `dscu`

Unidad Estratigráfica de procedencia (DSCU = Descrizione Scavo Unità).

### Sector

**Campo**: `comboBox_settore`
**Base de datos**: `settore`

Sector de excavación.

### Inventario

**Campo**: `lineEdit_inventario`
**Base de datos**: `inventario`

Número de inventario.

### Caja

**Campo**: `lineEdit_cassetta`
**Base de datos**: `cassetta`

Número de la caja/contenedor.

---

## Campos de Localización ICCD

### LDCT - Tipología de Ubicación

**Campo**: `comboBox_ldct`
**Base de datos**: `ldct`

Tipo de lugar de ubicación.

**Valores ICCD:**
- museo
- soprintendenza
- deposito
- laboratorio
- otro

### LDCN - Denominación Ubicación

**Campo**: `lineEdit_ldcn`
**Base de datos**: `ldcn`

Nombre específico del lugar de conservación.

### Antigua Ubicación

**Campo**: `lineEdit_vecchia_coll`
**Base de datos**: `vecchia_collocazione`

Eventual ubicación anterior.

### SCAN - Denominación Excavación

**Campo**: `lineEdit_scan`
**Base de datos**: `scan`

Nombre oficial de la excavación/investigación.

### Sondeo

**Campo**: `comboBox_saggio`
**Base de datos**: `saggio`

Sondeo/trinchera de referencia.

### Ambiente/Locus

**Campo**: `lineEdit_vano`
**Base de datos**: `vano_locus`

Ambiente o locus de procedencia.

---

## Campos Cronológicos

### DTZG - Franja Cronológica

**Campo**: `comboBox_dtzg`
**Base de datos**: `dtzg`

Período cronológico general.

**Ejemplos ICCD:**
- edad del bronce
- edad del hierro
- época romana
- época medieval

### DTZS - Fracción Cronológica

**Campo**: `comboBox_dtzs`
**Base de datos**: `dtzs`

Subdivisión del período.

**Ejemplos:**
- antiguo/a
- medio/a
- tardío/a
- final

### Cronologías

**Campo**: `tableWidget_cronologie`
**Base de datos**: `cronologie`

Tabla para cronologías múltiples o detalladas.

---

## Campos de Adquisición

### AINT - Tipo de Adquisición

**Campo**: `comboBox_aint`
**Base de datos**: `aint`

Modalidad de adquisición de los materiales.

**Valores ICCD:**
- excavación
- prospección
- compra
- donación
- incautación

### AIND - Fecha de Adquisición

**Campo**: `dateEdit_aind`
**Base de datos**: `aind`

Fecha de la adquisición.

### RCGD - Fecha de Prospección

**Campo**: `dateEdit_rcgd`
**Base de datos**: `rcgd`

Fecha de la prospección (si aplica).

### RCGZ - Especificaciones de Prospección

**Campo**: `textEdit_rcgz`
**Base de datos**: `rcgz`

Notas sobre la prospección.

---

## Campos de Materiales

### OGTM - Material

**Campo**: `comboBox_ogtm`
**Base de datos**: `ogtm`

Material principal (Oggetto Tipo Materiale).

**Valores ICCD:**
- cerámica
- vidrio
- metal
- hueso
- piedra
- ladrillo

### N. Hallazgos

**Campo**: `spinBox_n_reperti`
**Base de datos**: `n_reperti`

Número total de hallazgos.

### Peso

**Campo**: `doubleSpinBox_peso`
**Base de datos**: `peso`

Peso total en gramos.

### DESO - Indicación de Objetos

**Campo**: `textEdit_deso`
**Base de datos**: `deso`

Descripción sintética de los objetos.

---

## Tabla de Detalle de Materiales

**Widget**: `tableWidget_materiali`
**Tabla asociada**: `tma_materiali`

Permite registrar los materiales individuales contenidos en la caja.

### Columnas

| Campo ICCD | Descripción |
|------------|-------------|
| MADI | Inventario del material |
| MACC | Categoría |
| MACL | Clase |
| MACP | Precisión tipológica |
| MACD | Definición |
| Cronología | Datación específica |
| MACQ | Cantidad |

### Gestión de Filas

| Botón | Función |
|-------|---------|
| + | Añadir material |
| - | Eliminar material |

---

## Campos de Documentación

### FTAP - Tipo de Fotografía

**Campo**: `comboBox_ftap`
**Base de datos**: `ftap`

Tipo de documentación fotográfica.

### FTAN - Código de Foto

**Campo**: `lineEdit_ftan`
**Base de datos**: `ftan`

Código identificativo de la foto.

### DRAT - Tipo de Dibujo

**Campo**: `comboBox_drat`
**Base de datos**: `drat`

Tipo de documentación gráfica.

### DRAN - Código de Dibujo

**Campo**: `lineEdit_dran`
**Base de datos**: `dran`

Código identificativo del dibujo.

### DRAA - Autor del Dibujo

**Campo**: `lineEdit_draa`
**Base de datos**: `draa`

Autor del dibujo.

---

## Tab Media

Gestión de imágenes asociadas a la caja/TMA.

### Funcionalidades

- Visualización de miniaturas
- Drag & drop para añadir imágenes
- Doble clic para visualizar
- Conexión a base de datos de media

---

## Tab Table View

Vista tabular de todos los registros TMA para consulta rápida.

### Funcionalidades

- Visualización en cuadrícula
- Ordenación por columna
- Filtros rápidos
- Selección múltiple

---

## Export e Impresión

### Export PDF

| Opción | Descripción |
|--------|-------------|
| Ficha TMA | Ficha completa |
| Etiquetas | Etiquetas para cajas |

### Etiquetas de Cajas

Generación automática de etiquetas para:
- Identificación de cajas
- Contenido sintético
- Datos de procedencia
- Código de barras (opcional)

---

## Workflow Operativo

### Registro de Nueva TMA

1. **Apertura de ficha**
   - Vía menú o toolbar

2. **Nuevo registro**
   - Clic en "New Record"

3. **Datos identificativos**
   ```
   Sitio: Villa Romana
   Área: 1000
   UE: 150
   Caja: C-001
   ```

4. **Localización**
   ```
   LDCT: deposito
   LDCN: Depósito Soprintendenza Roma
   SCAN: Excavaciones Villa Romana 2024
   ```

5. **Cronología**
   ```
   DTZG: época romana
   DTZS: imperial
   ```

6. **Materiales** (tabla)
   ```
   | Inv | Cat | Clase | Def | Cant |
   |-----|-----|-------|-----|------|
   | 001 | cerámica | común | olla | 5 |
   | 002 | cerámica | sigillata | plato | 3 |
   | 003 | vidrio | - | ungüentario | 1 |
   ```

7. **Guardado**
   - Clic en "Save"

---

## Buenas Prácticas

### Estándares ICCD

- Utilizar los vocabularios controlados ICCD
- Respetar las siglas oficiales
- Mantener coherencia terminológica

### Organización de Cajas

- Numeración progresiva única
- Una TMA por caja física
- Separar por UE cuando sea posible

### Documentación

- Conectar siempre fotos y dibujos
- Usar códigos únicos para los media
- Registrar autor y fecha

---

## Resolución de Problemas

### Problema: Vocabularios ICCD no disponibles

**Causa**: Tesauro no configurado.

**Solución**:
1. Importar los vocabularios ICCD estándar
2. Verificar la configuración del tesauro

### Problema: Materiales no guardados

**Causa**: Tabla de materiales no sincronizada.

**Solución**:
1. Verificar que todos los campos obligatorios estén completados
2. Guardar la ficha principal antes de añadir materiales

---

## Referencias

### Base de Datos

- **Tabla principal**: `tma_materiali_archeologici`
- **Tabla de detalle**: `tma_materiali`
- **Clase mapper**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### Archivos Fuente

- **UI**: `gui/ui/Tma.ui`
- **Controlador**: `tabs/Tma.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Etiquetas**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Video Tutorial

### Catalogación TMA
**Duración**: 15-18 minutos
- Estándares ICCD
- Compilación completa
- Gestión de materiales

[Placeholder video: video_tma_catalogazione.mp4]

### Generación de Etiquetas
**Duración**: 5-6 minutos
- Configuración de etiquetas
- Impresión en lote
- Personalización

[Placeholder video: video_tma_etichette.mp4]

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
