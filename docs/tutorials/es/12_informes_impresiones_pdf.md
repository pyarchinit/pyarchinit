# Tutorial 12: Informes e Impresiones PDF

## Introducción

PyArchInit ofrece un sistema completo de generación de **informes PDF** para todas las fichas arqueológicas. Esta funcionalidad permite exportar la documentación en formato imprimible, conforme a los estándares ministeriales y listo para el archivo.

### Tipos de Informes Disponibles

| Tipo | Descripción | Ficha de Origen |
|------|-------------|-----------------|
| Fichas UE | Informes completos UE/UEM | Ficha UE |
| Índice UE | Lista sintética UE | Ficha UE |
| Fichas Periodización | Informes periodos/fases | Ficha Periodización |
| Fichas Estructura | Informes estructuras | Ficha Estructura |
| Fichas Hallazgos | Informes inventario materiales | Ficha Inventario |
| Fichas Tumba | Informes sepulturas | Ficha Tumba |
| Fichas Muestras | Informes muestreos | Ficha Muestras |
| Fichas Individuos | Informes antropológicos | Ficha Individuos |

## Acceso a la Función

### Desde el Menú Principal
1. **PyArchInit** en la barra del menú
2. Seleccionar **Export PDF**

### Desde la Toolbar
Hacer clic en el icono **PDF** en la barra de herramientas de PyArchInit

## Interfaz de Exportación

### Vista General de la Ventana

La ventana de exportación PDF presenta:

```
+------------------------------------------+
|        PyArchInit - Export PDF            |
+------------------------------------------+
| Sitio: [ComboBox selección sitio]    [v]  |
+------------------------------------------+
| Fichas a exportar:                        |
| [x] Fichas UE                             |
| [x] Fichas Periodización                  |
| [x] Fichas Estructura                     |
| [x] Fichas Hallazgos                      |
| [x] Fichas Tumba                          |
| [x] Fichas Muestras                       |
| [x] Fichas Individuos                     |
+------------------------------------------+
| [Abrir Carpeta]  [Exportar PDF]  [Cancelar] |
+------------------------------------------+
```

### Selección de Sitio

| Campo | Descripción |
|-------|-------------|
| ComboBox Sitio | Lista de todos los sitios en la base de datos |

**Nota**: La exportación se realiza por sitio individual. Para exportar varios sitios, repetir la operación.

### Checkbox de Fichas

Cada checkbox habilita la exportación de un tipo específico:

| Checkbox | Genera |
|----------|--------|
| Fichas UE | Fichas completas + Índice UE |
| Fichas Periodización | Fichas periodos + Índice |
| Fichas Estructura | Fichas estructuras + Índice |
| Fichas Hallazgos | Fichas materiales + Índice |
| Fichas Tumba | Fichas sepulturas + Índice |
| Fichas Muestras | Fichas muestras + Índice |
| Fichas Individuos | Fichas antropológicas + Índice |

## Proceso de Exportación

### Paso 1: Selección de Datos

```python
# El sistema ejecuta para cada tipo seleccionado:
1. Query a base de datos para el sitio seleccionado
2. Ordenación de datos (por número, área, etc.)
3. Preparación de lista para generación
```

### Paso 2: Generación de PDF

Para cada tipo de ficha:
1. **Ficha individual**: PDF detallado para cada registro
2. **Índice**: PDF resumido con todos los registros

### Paso 3: Guardado

Salida en la carpeta:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Contenido de los Informes

### Ficha UE

Información incluida:
- **Datos identificativos**: Sitio, Área, Número UE, Tipo de unidad
- **Definiciones**: Estratigráfica, Interpretativa
- **Descripción**: Texto descriptivo completo
- **Interpretación**: Análisis interpretativo
- **Periodización**: Periodo/Fase inicial y final
- **Características físicas**: Color, consistencia, formación
- **Medidas**: Cotas mín/máx, dimensiones
- **Relaciones**: Lista de relaciones estratigráficas
- **Documentación**: Referencias gráficas y fotográficas
- **Datos UEM**: (si aplica) Técnica muraria, materiales

### Índice UE

Tabla resumen con columnas:
| Sitio | Área | UE | Def. Estratigráfica | Def. Interpretativa | Periodo |

### Ficha Periodización

- Sitio
- Número de Periodo
- Número de Fase
- Cronología inicial/final
- Datación extendida
- Descripción del periodo

### Ficha Estructura

- Datos identificativos (Sitio, Sigla, Número)
- Categoría, Tipología, Definición
- Descripción e Interpretación
- Periodización
- Materiales empleados
- Elementos estructurales
- Relaciones de estructura
- Medidas y cotas

### Ficha Hallazgos

- Sitio, Número de inventario
- Tipo de hallazgo, Definición
- Descripción
- Procedencia (Área, UE)
- Estado de conservación
- Datación
- Elementos y mediciones
- Bibliografía

### Ficha Tumba

- Datos identificativos
- Rito (inhumación/cremación)
- Tipo de sepultura y deposición
- Descripción e interpretación
- Ajuar (presencia, tipo, descripción)
- Periodización
- Cotas de estructura e individuo
- UE asociadas

### Ficha Muestras

- Sitio, Número de muestra
- Tipo de muestra
- Descripción
- Procedencia (Área, UE)
- Lugar de conservación
- Número de caja

### Ficha Individuos

- Datos identificativos
- Sexo, Edad (mín/máx), Clases de edad
- Posición del esqueleto
- Orientación (eje, acimut)
- Estado de conservación
- Observaciones

## Idiomas Soportados

El sistema genera informes según el idioma del sistema:

| Idioma | Código | Template |
|--------|--------|----------|
| Italiano | IT | `build_*_sheets()` |
| Alemán | DE | `build_*_sheets_de()` |
| Inglés | EN | `build_*_sheets_en()` |

El idioma se detecta automáticamente desde los ajustes de QGIS.

## Carpeta de Salida

### Ruta Estándar
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Estructura de Archivos Generados

```
pyarchinit_PDF_folder/
├── US_[sitio]_schede.pdf           # Fichas UE completas
├── US_[sitio]_indice.pdf           # Índice UE
├── Periodizzazione_[sitio].pdf     # Fichas Periodización
├── Struttura_[sitio]_schede.pdf    # Fichas Estructura
├── Struttura_[sitio]_indice.pdf    # Índice Estructura
├── Reperti_[sitio]_schede.pdf      # Fichas Hallazgos
├── Reperti_[sitio]_indice.pdf      # Índice Hallazgos
├── Tomba_[sitio]_schede.pdf        # Fichas Tumba
├── Campioni_[sitio]_schede.pdf     # Fichas Muestras
├── Individui_[sitio]_schede.pdf    # Fichas Individuos
└── ...
```

### Apertura de Carpeta

El botón **"Abrir Carpeta"** abre directamente el directorio de salida en el gestor de archivos del sistema.

## Personalización de Informes

### Templates PDF

Los templates están definidos en los módulos:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Librería Utilizada

Los PDF se generan con **ReportLab**, que permite:
- Layouts personalizables
- Inserción de imágenes
- Tablas formateadas
- Encabezados/pies de página

### Fuentes Requeridas

El sistema utiliza fuentes específicas:
- **Cambria** (fuente principal)
- Instalación automática en el primer inicio del plugin

## Workflow Recomendado

### 1. Preparación de Datos

```
1. Completar todas las fichas del sitio
2. Verificar completitud de los datos
3. Comprobar periodización
4. Verificar relaciones estratigráficas
```

### 2. Exportación

```
1. Abrir Export PDF
2. Seleccionar el sitio
3. Seleccionar los tipos de fichas
4. Hacer clic en "Exportar PDF"
5. Esperar la finalización
```

### 3. Verificación

```
1. Abrir carpeta de salida
2. Comprobar los PDF generados
3. Verificar el formato
4. Imprimir o archivar
```

## Resolución de Problemas

### Error: "No form to print"

**Causa**: Ningún registro encontrado para el tipo seleccionado

**Solución**:
- Verificar que existan datos para el sitio seleccionado
- Comprobar la base de datos

### PDF Vacíos o Incompletos

**Posibles causas**:
1. Campos obligatorios no completados
2. Problemas de codificación de caracteres
3. Fuentes faltantes

**Soluciones**:
- Completar los campos obligatorios
- Verificar instalación de fuente Cambria

### Error de Fuente

**Causa**: Fuente Cambria no instalada

**Solución**:
- El plugin intenta la instalación automática
- En caso de problemas, instalar manualmente

### Exportación Lenta

**Causa**: Muchos registros a exportar

**Solución**:
- Exportar por tipología separadamente
- Esperar la finalización

## Buenas Prácticas

### 1. Organización

- Exportar regularmente durante la excavación
- Crear copias de seguridad de los PDF generados
- Organizar por campaña/año

### 2. Completitud de Datos

- Completar todos los campos antes de la exportación
- Verificar las cotas desde las mediciones SIG
- Comprobar las relaciones estratigráficas

### 3. Archivo

- Guardar PDF en almacenamiento seguro
- Incluir en la documentación final
- Adjuntar a la memoria de excavación

### 4. Impresión

- Usar papel sin ácido para archivo
- Imprimir en formato A4
- Encuadernar por campaña

## Integración con Otras Funciones

### Cotas desde SIG

El sistema recupera automáticamente:
- Cotas mínimas y máximas desde las geometrías
- Referencias a las plantas SIG

### Documentación Fotográfica

Los informes pueden incluir referencias a:
- Fotografías conectadas
- Dibujos y levantamientos

### Periodización

Los informes de UE incluyen automáticamente:
- Datación extendida del periodo/fase asignado
- Referencias cronológicas

## Referencias

### Archivos Fuente
- `tabs/Pdf_export.py` - Interfaz de exportación
- `modules/utility/pyarchinit_exp_*_pdf.py` - Generadores PDF

### Dependencias
- ReportLab (generación PDF)
- Fuente Cambria

---

*Última actualización: Enero 2026*
