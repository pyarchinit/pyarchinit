# Tutorial 09: Ficha de Muestras

## Introducción

La **Ficha de Muestras** es el módulo de PyArchInit dedicado a la gestión de los muestreos arqueológicos. Permite registrar y rastrear todos los tipos de muestras tomadas durante la excavación: tierras, carbón, semillas, huesos, morteros, metales y otro material destinado a análisis especializados.

### Tipos de Muestras

Las muestras arqueológicas comprenden:
- **Sedimentos**: para análisis sedimentológicos, granulométricos
- **Carbones**: para dataciones radiométricas (C14)
- **Semillas/Polen**: para análisis arqueobotánicos
- **Huesos**: para análisis arqueozoológicos, isotópicos, ADN
- **Morteros/Enlucidos**: para análisis arqueométricos
- **Metales/Escorias**: para análisis metalúrgicos
- **Cerámicas**: para análisis de pasta, procedencia

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha de Muestras** (o **Samples form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Muestras**

---

## Vista General de la Interfaz

La ficha presenta un diseño simplificado para la gestión rápida de las muestras.

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | DB Info | Estado del registro, ordenamiento, contador |
| 3 | Campos Identificativos | Sitio, Nr. Muestra, Tipo |
| 4 | Campos Descriptivos | Descripción, notas |
| 5 | Campos de Conservación | Caja, Lugar |

---

## Toolbar DBMS

### Botones de Navegación

| Icono | Función | Descripción |
|-------|---------|-------------|
| First rec | Ir al primer registro |
| Prev rec | Ir al registro anterior |
| Next rec | Ir al registro siguiente |
| Last rec | Ir al último registro |

### Botones CRUD

| Icono | Función | Descripción |
|-------|---------|-------------|
| New record | Crear un nuevo registro de muestra |
| Save | Guardar las modificaciones |
| Delete | Eliminar el registro actual |

### Botones de Búsqueda

| Icono | Función | Descripción |
|-------|---------|-------------|
| New search | Iniciar nueva búsqueda |
| Search!!! | Ejecutar búsqueda |
| Order by | Ordenar resultados |
| View all | Ver todos los registros |

---

## Campos de la Ficha

### Sitio

**Campo**: `comboBox_sito`
**Base de datos**: `sito`

Selecciona el sitio arqueológico de pertenencia.

### Número de Muestra

**Campo**: `lineEdit_nr_campione`
**Base de datos**: `nr_campione`

Número identificativo progresivo de la muestra.

### Tipo de Muestra

**Campo**: `comboBox_tipo_campione`
**Base de datos**: `tipo_campione`

Clasificación tipológica de la muestra. Los valores provienen del tesauro.

**Tipos comunes:**
| Tipo | Descripción |
|------|-------------|
| Sedimento | Muestra de tierra |
| Carbón | Para dataciones C14 |
| Semillas | Restos carpológicos |
| Huesos | Restos faunísticos |
| Mortero | Aglutinantes de construcción |
| Cerámica | Para análisis de pasta |
| Metal | Para análisis metalúrgicos |
| Polen | Para análisis palinológicos |

### Descripción

**Campo**: `textEdit_descrizione`
**Base de datos**: `descrizione`

Descripción detallada de la muestra.

**Contenidos recomendados:**
- Características físicas de la muestra
- Cantidad tomada
- Modalidad de toma
- Motivo del muestreo
- Análisis previstos

### Área

**Campo**: `comboBox_area`
**Base de datos**: `area`

Área de excavación de procedencia.

### UE

**Campo**: `comboBox_us`
**Base de datos**: `us`

Unidad Estratigráfica de procedencia.

### Número de Inventario de Material

**Campo**: `lineEdit_nr_inv_mat`
**Base de datos**: `numero_inventario_materiale`

Si la muestra está conectada a un hallazgo inventariado, indicar el número de inventario.

### Número de Caja

**Campo**: `lineEdit_nr_cassa`
**Base de datos**: `nr_cassa`

Caja o contenedor de conservación.

### Lugar de Conservación

**Campo**: `comboBox_luogo_conservazione`
**Base de datos**: `luogo_conservazione`

Dónde está conservada la muestra.

**Ejemplos:**
- Laboratorio de excavación
- Depósito del museo
- Laboratorio de análisis externo
- Universidad

---

## Workflow Operativo

### Creación de Nueva Muestra

1. **Apertura de la ficha**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en "New Record"

3. **Datos identificativos**
   ```
   Sitio: Villa Romana de Settefinestre
   Nr. Muestra: C-2024-001
   Tipo de muestra: Carbón
   ```

4. **Procedencia**
   ```
   Área: 1000
   UE: 150
   ```

5. **Descripción**
   ```
   Muestra de carbón tomada de la
   superficie de concotto UE 150.
   Cantidad: 50 gr aproximadamente.
   Tomada para datación C14.
   ```

6. **Conservación**
   ```
   Nr. Caja: Camp-1
   Lugar: Laboratorio de excavación
   ```

7. **Guardado**
   - Clic en "Save"

### Búsqueda de Muestras

1. Clic en "New Search"
2. Completar criterios:
   - Sitio
   - Tipo de muestra
   - UE
3. Clic en "Search"
4. Navegar entre los resultados

---

## Export PDF

La ficha soporta la exportación a PDF para:
- Lista de muestras
- Fichas detalladas individuales

---

## Buenas Prácticas

### Nomenclatura

- Usar códigos únicos y descriptivos
- Formato recomendado: `SITIO-AÑO-PROGRESIVO`
- Ejemplo: `VRS-2024-C001`

### Toma de Muestras

- Documentar siempre las coordenadas de toma
- Fotografiar el punto de toma
- Anotar profundidad y contexto

### Conservación

- Usar contenedores apropiados al tipo
- Etiquetar claramente cada muestra
- Mantener condiciones idóneas

### Documentación

- Conectar siempre a la UE de procedencia
- Indicar los análisis previstos
- Registrar el envío a laboratorios externos

---

## Resolución de Problemas

### Problema: Tipo de muestra no disponible

**Causa**: Tesauro no configurado.

**Solución**:
1. Abrir la Ficha de Tesauro
2. Añadir el tipo faltante para `campioni_table`
3. Guardar y volver a abrir la Ficha de Muestras

### Problema: UE no visualizada

**Causa**: UE no registrada para el sitio seleccionado.

**Solución**:
1. Verificar que la UE exista en la Ficha de UE
2. Comprobar que pertenezca al mismo sitio

---

## Referencias

### Base de Datos

- **Tabla**: `campioni_table`
- **Clase mapper**: `CAMPIONI`
- **ID**: `id_campione`

### Archivos Fuente

- **UI**: `gui/ui/Campioni.ui`
- **Controlador**: `tabs/Campioni.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
