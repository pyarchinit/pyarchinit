# Tutorial 10: Ficha de Documentación

## Introducción

La **Ficha de Documentación** es el módulo de PyArchInit para la gestión de la documentación gráfica de excavación: plantas, secciones, alzados, levantamientos y cualquier otro elaborado gráfico producido durante las actividades arqueológicas.

### Tipos de Documentación

- **Plantas**: plantas de estrato, de fase, generales
- **Secciones**: secciones estratigráficas
- **Alzados**: alzados murarios, frentes de excavación
- **Levantamientos**: levantamientos topográficos, fotogramétricos
- **Ortofotos**: elaboraciones desde dron/fotogrametría
- **Dibujos de hallazgos**: cerámica, metales, etc.

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha de Documentación** (o **Documentation form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Documentación**

---

## Vista General de la Interfaz

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | DB Info | Estado del registro, ordenamiento, contador |
| 3 | Campos Identificativos | Sitio, Nombre, Fecha |
| 4 | Campos Tipológicos | Tipo, Fuente, Escala |
| 5 | Campos Descriptivos | Dibujante, Notas |

---

## Toolbar DBMS

### Botones Estándar

| Función | Descripción |
|---------|-------------|
| First/Prev/Next/Last rec | Navegación entre registros |
| New record | Crear nuevo registro |
| Save | Guardar las modificaciones |
| Delete | Eliminar el registro |
| New search / Search | Funciones de búsqueda |
| Order by | Ordenar resultados |
| View all | Ver todos los registros |

---

## Campos de la Ficha

### Sitio

**Campo**: `comboBox_sito_doc`
**Base de datos**: `sito`

Sitio arqueológico de referencia.

### Nombre de Documentación

**Campo**: `lineEdit_nome_doc`
**Base de datos**: `nome_doc`

Nombre identificativo del documento.

**Convenciones de nomenclatura:**
- `P` = Planta (ej. P001)
- `S` = Sección (ej. S001)
- `PR` = Alzado (ej. PR001)
- `R` = Levantamiento (ej. R001)

### Fecha

**Campo**: `dateEdit_data`
**Base de datos**: `data`

Fecha de ejecución del dibujo/levantamiento.

### Tipo de Documentación

**Campo**: `comboBox_tipo_doc`
**Base de datos**: `tipo_documentazione`

Tipología del documento.

**Valores típicos:**
| Tipo | Descripción |
|------|-------------|
| Planta de estrato | UE individual |
| Planta de fase | Varias UE coetáneas |
| Planta general | Vista de conjunto |
| Sección estratigráfica | Perfil vertical |
| Alzado | Alzado murario |
| Levantamiento topográfico | Planimetría general |
| Ortofoto | Desde fotogrametría |
| Dibujo de hallazgo | Cerámica, metal, etc. |

### Fuente

**Campo**: `comboBox_sorgente`
**Base de datos**: `sorgente`

Fuente/método de producción.

**Valores:**
- Levantamiento directo
- Fotogrametría
- Escáner láser
- GPS/Estación total
- Digitalización CAD
- Ortofoto de dron

### Escala

**Campo**: `comboBox_scala`
**Base de datos**: `scala`

Escala de representación.

**Escalas comunes:**
| Escala | Uso típico |
|--------|------------|
| 1:1 | Dibujos de hallazgos |
| 1:5 | Detalles |
| 1:10 | Secciones, detalles |
| 1:20 | Plantas de estrato |
| 1:50 | Plantas generales |
| 1:100 | Planimetrías |
| 1:200+ | Mapas topográficos |

### Dibujante

**Campo**: `comboBox_disegnatore`
**Base de datos**: `disegnatore`

Autor del dibujo/levantamiento.

### Notas

**Campo**: `textEdit_note`
**Base de datos**: `note`

Notas adicionales sobre el documento.

---

## Workflow Operativo

### Registro de Nueva Documentación

1. **Apertura de la ficha**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en "New Record"

3. **Datos identificativos**
   ```
   Sitio: Villa Romana de Settefinestre
   Nombre: P025
   Fecha: 15/06/2024
   ```

4. **Clasificación**
   ```
   Tipo: Planta de estrato
   Fuente: Levantamiento directo
   Escala: 1:20
   ```

5. **Autor y notas**
   ```
   Dibujante: M. Rossi
   Notas: Planta UE 150. Evidencia los
   límites del pavimento de mortero.
   ```

6. **Guardado**
   - Clic en "Save"

### Búsqueda de Documentación

1. Clic en "New Search"
2. Completar criterios:
   - Sitio
   - Tipo de documentación
   - Escala
   - Dibujante
3. Clic en "Search"
4. Navegar entre los resultados

---

## Export PDF

La ficha soporta la exportación a PDF para:
- Lista de documentación
- Fichas detalladas

---

## Buenas Prácticas

### Nomenclatura

- Usar códigos coherentes en todo el proyecto
- Numeración progresiva por tipo
- Documentar las convenciones adoptadas

### Organización

- Conectar siempre al sitio de referencia
- Indicar la escala efectiva
- Registrar fecha y autor

### Archivo

- Conectar los archivos digitales mediante la gestión de medios
- Mantener copias de seguridad
- Usar formatos estándar (PDF, TIFF)

---

## Resolución de Problemas

### Problema: Tipo de documentación no disponible

**Causa**: Tesauro no configurado.

**Solución**:
1. Abrir la Ficha de Tesauro
2. Añadir los tipos faltantes para `documentazione_table`

### Problema: Archivo no visualizado

**Causa**: Ruta incorrecta o archivo faltante.

**Solución**:
1. Verificar que el archivo exista
2. Comprobar la ruta en la configuración de medios

---

## Referencias

### Base de Datos

- **Tabla**: `documentazione_table`
- **Clase mapper**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### Archivos Fuente

- **UI**: `gui/ui/Documentazione.ui`
- **Controlador**: `tabs/Documentazione.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
