# Tutorial 08: Ficha de Inventario de Materiales

## Índice
1. [Introducción](#introducción)
2. [Acceso a la Ficha](#acceso-a-la-ficha)
3. [Interfaz de Usuario](#interfaz-de-usuario)
4. [Campos Principales](#campos-principales)
5. [Pestañas de la Ficha](#pestañas-de-la-ficha)
6. [Toolbar DBMS](#toolbar-dbms)
7. [Gestión de Medios](#gestión-de-medios)
8. [Funcionalidades SIG](#funcionalidades-sig)
9. [Cuantificaciones y Estadísticas](#cuantificaciones-y-estadísticas)
10. [Exportación e Informes](#exportación-e-informes)
11. [Integración IA](#integración-ia)
12. [Workflow Operativo](#workflow-operativo)
13. [Buenas Prácticas](#buenas-prácticas)
14. [Resolución de Problemas](#resolución-de-problemas)

---

## Introducción

La **Ficha de Inventario de Materiales** es la herramienta principal para la gestión de los hallazgos arqueológicos en PyArchInit. Permite catalogar, describir y cuantificar todos los materiales encontrados durante la excavación, desde cerámicas hasta metales, desde vidrios hasta huesos de animales.

### Propósito de la Ficha

- Inventariar todos los hallazgos encontrados
- Asociar los hallazgos a las UE de procedencia
- Gestionar la clasificación tipológica
- Documentar las características físicas y tecnológicas
- Calcular cuantificaciones (formas mínimas, EVE, peso)
- Conectar fotos y dibujos a los hallazgos
- Generar informes y estadísticas

### Tipos de Materiales Gestionables

La ficha soporta diferentes tipos de materiales:
- **Cerámica**: Vajilla, terracotas, ladrillos
- **Metales**: Bronce, hierro, plomo, oro, plata
- **Vidrio**: Contenedores, vidrio de ventana
- **Hueso/Marfil**: Manufacturas en materia dura animal
- **Piedra**: Herramientas líticas, esculturas
- **Monedas**: Numismática
- **Orgánicos**: Madera, tejidos, cuero

---

## Acceso a la Ficha

### Desde Menú

1. Abrir QGIS con el plugin PyArchInit activo
2. Menú **PyArchInit** → **Archaeological record management** → **Artefact** → **Artefact form**

### Desde Toolbar

1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Hallazgos** (icono de ánfora/vasija)

### Atajo de Teclado

- **Ctrl+G**: Activar/desactivar visualización SIG del hallazgo actual

---

## Interfaz de Usuario

La interfaz está organizada en tres áreas principales:

### Áreas Principales

| Área | Descripción |
|------|-------------|
| **1. Encabezado** | Toolbar DBMS, indicadores de estado, botones SIG y exportación |
| **2. Campos Identificativos** | Sitio, Área, UE, Número de inventario, RA, Tipo de hallazgo |
| **3. Campos Descriptivos** | Clase, Definición, Estado de conservación, Datación |
| **4. Pestañas de Detalle** | 6 pestañas para datos específicos |

### Pestañas Disponibles

| Pestaña | Contenido |
|---------|-----------|
| **Descripción** | Texto descriptivo, visor de medios, datación |
| **Diapositivas** | Gestión de diapositivas y negativos fotográficos |
| **Datos Cuantitativos** | Elementos del hallazgo, formas, medidas cerámicas |
| **Tecnologías** | Técnicas productivas y decorativas |
| **Ref Biblio** | Referencias bibliográficas |
| **Cuantificaciones** | Gráficos y estadísticas |

---

## Campos Principales

### Campos Identificativos

#### Sitio
- **Tipo**: ComboBox (solo lectura después de guardar)
- **Obligatorio**: Sí
- **Descripción**: Sitio arqueológico de procedencia
- **Notas**: Si está configurado en ajustes, se autocompleta

#### Número de Inventario
- **Tipo**: LineEdit numérico
- **Obligatorio**: Sí
- **Descripción**: Número progresivo único del hallazgo dentro del sitio
- **Restricción**: Único por sitio

#### Área
- **Tipo**: ComboBox editable
- **Obligatorio**: No
- **Descripción**: Área de excavación de procedencia

#### UE (Unidad Estratigráfica)
- **Tipo**: LineEdit
- **Obligatorio**: No (pero muy recomendado)
- **Descripción**: Número de la UE de hallazgo
- **Conexión**: Conecta el hallazgo a la ficha UE correspondiente

#### Estructura
- **Tipo**: ComboBox editable
- **Obligatorio**: No
- **Descripción**: Estructura de pertenencia (si aplica)
- **Notas**: Se completa automáticamente según la UE

#### RA (Reperto Archeologico)
- **Tipo**: LineEdit numérico
- **Obligatorio**: No
- **Descripción**: Número de hallazgo arqueológico (numeración alternativa)
- **Notas**: Usado para hallazgos particularmente significativos

### Campos de Clasificación

#### Tipo de Hallazgo
- **Tipo**: ComboBox editable
- **Obligatorio**: Sí
- **Valores típicos**: Cerámica, Metal, Vidrio, Hueso, Piedra, Moneda, etc.
- **Notas**: Determina los campos específicos a completar

#### Clase de Material (Criterio de Catalogación)
- **Tipo**: ComboBox editable
- **Obligatorio**: No
- **Descripción**: Clase de pertenencia del material
- **Ejemplos para cerámica**:
  - Cerámica común
  - Sigillata itálica
  - Sigillata africana
  - Cerámica de barniz negro
  - Cerámica de paredes finas
  - Ánforas
  - Lucernas

#### Definición
- **Tipo**: ComboBox editable
- **Obligatorio**: No
- **Descripción**: Definición tipológica específica
- **Ejemplos**: Plato, Copa, Olla, Jarra, Tapadera, etc.

#### Tipo
- **Tipo**: LineEdit
- **Obligatorio**: No
- **Descripción**: Tipología específica (ej. Dressel 1, Hayes 50)

### Campos de Estado y Conservación

#### Lavado
- **Tipo**: ComboBox
- **Valores**: Sí, No
- **Descripción**: Indica si el hallazgo ha sido lavado

#### Repertoriado
- **Tipo**: ComboBox
- **Valores**: Sí, No
- **Descripción**: Indica si el hallazgo ha sido seleccionado para estudio

#### Diagnóstico
- **Tipo**: ComboBox
- **Valores**: Sí, No
- **Descripción**: Indica si el hallazgo es diagnóstico (útil para clasificación)

#### Estado de Conservación
- **Tipo**: ComboBox editable
- **Obligatorio**: No
- **Valores típicos**: Íntegro, Fragmentario, Lacunar, Restaurado

### Campos de Depósito

#### Nr. Caja
- **Tipo**: LineEdit
- **Descripción**: Número de la caja de depósito

#### Tipo de Contenedor
- **Tipo**: ComboBox editable
- **Descripción**: Tipo de contenedor (caja, bolsa, estuche)

#### Lugar de Conservación
- **Tipo**: ComboBox editable
- **Descripción**: Almacén o depósito de conservación

#### Año
- **Tipo**: ComboBox editable
- **Descripción**: Año de hallazgo

### Campos de Catalogación

#### Compilador
- **Tipo**: ComboBox editable
- **Descripción**: Nombre del catalogador

#### Punto de Hallazgo
- **Tipo**: LineEdit
- **Descripción**: Coordenadas o referencia espacial del punto de hallazgo

---

## Pestañas de la Ficha

### Pestaña 1: Descripción

La pestaña principal contiene la descripción textual del hallazgo y la gestión de medios.

#### Campo Descripción
- **Tipo**: TextEdit multilínea
- **Contenido sugerido**:
  - Forma general
  - Partes conservadas
  - Características técnicas
  - Decoraciones
  - Comparaciones tipológicas

#### Datación del Hallazgo
- **Tipo**: ComboBox editable
- **Descripción**: Encuadramiento cronológico del hallazgo
- **Formato**: Textual (ej. "siglo I a.C.", "siglos II-III d.C.")

#### Visor de Medios
Área para visualizar las imágenes asociadas al hallazgo:
- **Visualizar todas las imágenes**: Carga todas las fotos conectadas
- **Buscar imágenes**: Búsqueda en las imágenes
- **Eliminar etiqueta**: Elimina la asociación imagen-hallazgo
- **SketchGPT**: Genera descripción IA desde imagen

### Pestaña 2: Diapositivas

Gestión de la documentación fotográfica tradicional.

#### Tabla Diapositivas
| Columna | Descripción |
|---------|-------------|
| Código | Código identificativo de la diapositiva |
| N. | Número progresivo |

#### Tabla Negativos
| Columna | Descripción |
|---------|-------------|
| Código | Código del rollo de negativos |
| N. | Número del fotograma |

#### Campos Adicionales
- **Photo ID**: Nombres de las fotos asociadas (autocompletado)
- **Drawing ID**: Nombres de los dibujos asociados (autocompletado)

### Pestaña 3: Datos Cuantitativos

Pestaña fundamental para el análisis cuantitativo, especialmente para la cerámica.

#### Tabla Elementos del Hallazgo
Permite registrar los elementos individuales que componen el hallazgo:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Elemento encontrado | Parte anatómica del vaso | Borde, Pared, Fondo, Asa |
| Tipo de cantidad | Estado del fragmento | Fragmento, Entero |
| Cantidad | Número de piezas | 5 |

#### Campos de Cuantificación Cerámica

| Campo | Descripción |
|-------|-------------|
| **Formas mínimas** | Número Mínimo de Individuos (NMI) |
| **Formas máximas** | Número Máximo de Individuos |
| **Total fragmentos** | Recuento automático desde tabla de elementos |
| **Peso** | Peso en gramos |
| **Diámetro del borde** | Diámetro del borde en cm |
| **EVE borde** | Estimated Vessel Equivalent (porcentaje de borde conservado) |

#### Botón Calcular Total de Fragmentos
Calcula automáticamente el total de fragmentos sumando las cantidades de la tabla de elementos.

#### Tabla de Mediciones
Permite registrar medidas múltiples:

| Columna | Descripción |
|---------|-------------|
| Tipo de medida | Altura, Anchura, Espesor, etc. |
| Unidad de medida | cm, mm, m |
| Valor | Valor numérico |

### Pestaña 4: Tecnologías

Registro de las técnicas productivas y decorativas.

#### Tabla de Tecnologías

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| Tipo de tecnología | Categoría técnica | Producción, Decoración |
| Posición | Dónde se encuentra | Interior, Exterior, Cuerpo |
| Cantidad | Si aplica | - |
| Unidad de medida | Si aplica | - |

#### Campos Específicos de Cerámica

| Campo | Descripción |
|-------|-------------|
| **Cuerpo cerámico** | Tipo de pasta (Depurada, Semidepurada, Tosca) |
| **Revestimiento** | Tipo de revestimiento (Barniz, Engobe, Vidriado) |

### Pestaña 5: Referencias Bibliográficas

Gestión de la bibliografía de comparación.

#### Tabla de Referencias

| Columna | Descripción |
|---------|-------------|
| Autor | Apellido del autor/es |
| Año | Año de publicación |
| Título | Título abreviado |
| Página | Referencia de página |
| Figura | Referencia de figura/lámina |

### Pestaña 6: Cuantificaciones

Pestaña para generar gráficos y estadísticas sobre los datos.

#### Tipos de Cuantificación Disponibles

| Tipo | Descripción |
|------|-------------|
| **Formas mínimas** | Gráfico para NMI |
| **Formas máximas** | Gráfico para número máximo |
| **Total fragmentos** | Gráfico para recuento de fragmentos |
| **Peso** | Gráfico para peso |
| **EVE borde** | Gráfico para EVE |

#### Parámetros de Agrupación

Los gráficos pueden agruparse por:
- Tipo de hallazgo
- Clase de material
- Definición
- Cuerpo cerámico
- Revestimiento
- Tipo
- Datación
- RA
- Año

---

## Toolbar DBMS

La barra de herramientas ofrece todas las herramientas para la gestión de registros.

### Botones Estándar

| Icono | Función | Descripción |
|-------|---------|-------------|
| Connection test | Test de conexión | Verifica la conexión a la base de datos |
| First/Prev/Next/Last | Navegación | Navegación entre registros |
| New record | Nuevo | Crear nuevo hallazgo |
| Save | Guardar | Guardar modificaciones |
| Delete | Eliminar | Eliminar hallazgo actual |
| View all | Todos | Visualizar todos los registros |
| New search | Búsqueda | Activar modo búsqueda |
| Search!!! | Ejecutar | Ejecutar la búsqueda |
| Order by | Ordenar | Ordenar los registros |

### Botones Específicos

| Icono | Función | Descripción |
|-------|---------|-------------|
| GIS | Visualizar SIG | Muestra el hallazgo en el mapa |
| PDF | Export PDF | Genera ficha PDF |
| Sheet | Export lista | Genera lista PDF |
| Excel | Export Excel | Exporta en formato Excel/CSV |
| A5 | Export A5 | Genera etiqueta formato A5 |
| Quant | Cuantificaciones | Abre panel de cuantificaciones |

---

## Gestión de Medios

### Asociación de Imágenes

#### Drag & Drop
Es posible arrastrar imágenes directamente en la lista para asociarlas al hallazgo.

#### Botones de Medios

| Botón | Función |
|-------|---------|
| **Todas las imágenes** | Carga todas las imágenes asociadas |
| **Buscar imágenes** | Abre búsqueda en las imágenes |
| **Eliminar etiqueta** | Elimina la asociación actual |

### Visualizador de Imágenes

Doble clic en una imagen de la lista abre el visualizador completo con:
- Zoom
- Pan
- Rotación
- Información EXIF

### Reproductor de Video

Para hallazgos con videos asociados, está disponible un reproductor integrado para:
- Reproducción de videos de artefactos
- Visualización de modelos 3D (si disponibles)

---

## Funcionalidades SIG

### Visualización en Mapa

#### Botón SIG (Toggle)
- **Activo**: El hallazgo se resalta en el mapa de QGIS
- **Inactivo**: Sin visualización
- **Atajo**: Ctrl+G

#### Requisitos
- El hallazgo debe tener la UE de procedencia especificada
- La UE debe tener una geometría en la capa SIG

### Conexión desde Mapa

Es posible seleccionar un hallazgo haciendo clic en el mapa:
1. Activar la herramienta de selección en QGIS
2. Hacer clic en la UE de interés
3. Los hallazgos de la UE se filtran en la ficha

---

## Cuantificaciones y Estadísticas

### Acceso a las Cuantificaciones

1. Hacer clic en el botón **Quant** en la barra de herramientas
2. Seleccionar el tipo de cuantificación
3. Seleccionar los parámetros de agrupación
4. Hacer clic en OK

### Tipos de Gráficos

#### Gráfico de Barras
Visualiza la distribución por categoría seleccionada.

### Exportación de Cuantificaciones

Los datos de las cuantificaciones se exportan automáticamente en:
- Archivo CSV en la carpeta `pyarchinit_Quantificazioni_folder`
- Gráfico visualizado en pantalla

---

## Exportación e Informes

### Export PDF Ficha Individual

Genera una ficha PDF completa del hallazgo actual con:
- Todos los datos identificativos
- Descripción
- Datos cuantitativos
- Referencias bibliográficas
- Imágenes asociadas (si disponibles)

### Export PDF Lista

Genera una lista PDF de todos los hallazgos visualizados (resultado de búsqueda actual):
- Tabla resumen
- Datos esenciales de cada hallazgo

### Export A5 (Etiquetas)

Genera etiquetas formato A5 para:
- Identificación de cajas
- Etiquetado de hallazgos
- Fichas móviles

Configuración de ruta PDF:
1. Hacer clic en el icono de carpeta junto al campo de ruta
2. Seleccionar la carpeta de destino
3. Hacer clic en "Exportar A5"

### Export Excel/CSV

Exporta los datos en formato tabular para:
- Elaboraciones estadísticas externas
- Importación en otros software
- Archivo

---

## Integración IA

### SketchGPT

Funcionalidad IA para generar automáticamente descripciones de los hallazgos a partir de imágenes.

#### Uso

1. Asociar una imagen al hallazgo
2. Hacer clic en el botón **SketchGPT**
3. Seleccionar la imagen a analizar
4. Seleccionar el modelo GPT (gpt-4-vision, gpt-4o)
5. El sistema genera una descripción arqueológica

#### Resultado

La descripción generada incluye:
- Identificación del tipo de hallazgo
- Descripción de las características visibles
- Posibles comparaciones tipológicas
- Sugerencias de datación

> **Nota**: Requiere API Key de OpenAI configurada.

---

## Workflow Operativo

### Creación de un Nuevo Hallazgo

#### Paso 1: Apertura de la Ficha
1. Abrir la Ficha de Inventario de Materiales
2. Verificar la conexión a la base de datos

#### Paso 2: Nuevo Registro
1. Hacer clic en **New record**
2. El Status cambia a "Nuevo Registro"

#### Paso 3: Datos Identificativos
1. Verificar/seleccionar el **Sitio**
2. Insertar el **Número de inventario** (progresivo)
3. Insertar **Área** y **UE** de procedencia

#### Paso 4: Clasificación
1. Seleccionar el **Tipo de hallazgo**
2. Seleccionar la **Clase de material**
3. Seleccionar/insertar la **Definición**

#### Paso 5: Descripción
1. Completar el campo **Descripción** en la pestaña Descripción
2. Seleccionar la **Datación**
3. Asociar eventuales imágenes

#### Paso 6: Datos Cuantitativos (si es cerámica)
1. Abrir la pestaña **Datos cuantitativos**
2. Insertar los elementos en la tabla
3. Completar formas mínimas/máximas
4. Insertar peso y medidas

#### Paso 7: Depósito
1. Insertar **Nr. caja**
2. Seleccionar **Lugar de conservación**
3. Indicar **Estado de conservación**

#### Paso 8: Guardado
1. Hacer clic en **Save**
2. Verificar el mensaje de confirmación
3. El registro está ahora guardado en la base de datos

### Búsqueda de Hallazgos

#### Búsqueda Simple
1. Hacer clic en **New search**
2. Completar los campos de búsqueda deseados
3. Hacer clic en **Search!!!**

#### Búsqueda por UE
1. Activar búsqueda
2. Insertar solo el número de UE en el campo UE
3. Ejecutar búsqueda

---

## Buenas Prácticas

### Numeración de Inventario

- Usar numeración progresiva sin interrupciones
- Un número = un hallazgo (o grupo homogéneo)
- Documentar el criterio de inventariado

### Clasificación

- Utilizar vocabularios controlados para las clases
- Mantener coherencia en la definición de los tipos
- Actualizar el tesauro cuando sea necesario

### Cuantificación Cerámica

Para una correcta cuantificación:
1. **Formas mínimas (NMI)**: Contar solo elementos diagnósticos (bordes, fondos distintivos)
2. **EVE**: Medir el porcentaje de circunferencia conservado
3. **Peso**: Pesar todos los fragmentos del grupo

### Documentación Fotográfica

- Fotografiar todos los hallazgos diagnósticos
- Usar escala métrica en las fotos
- Asociar las fotos mediante el gestor de medios

### Conexión con UE

- Verificar siempre que la UE exista antes de asociarla
- Para hallazgos de limpieza/superficie, usar UE apropiadas
- Documentar los casos de hallazgos fuera de contexto

---

## Resolución de Problemas

### Problemas Comunes

#### Número de inventario duplicado
- **Error**: "Ya existe un registro con este número de inventario"
- **Causa**: El número ya está utilizado para el sitio
- **Solución**: Verificar el siguiente número disponible con "View all"

#### Imágenes no visualizadas
- **Causa**: Ruta de las imágenes incorrecta
- **Solución**:
  1. Verificar configuración de ruta en Settings
  2. Verificar que las imágenes estén en la carpeta correcta
  3. Reasociar las imágenes

#### Cuantificaciones vacías
- **Causa**: Campos cuantitativos no completados
- **Solución**: Completar formas mínimas/máximas o total de fragmentos

#### Export PDF vacío
- **Causa**: Ningún registro seleccionado
- **Solución**: Verificar que haya al menos un registro visualizado

#### SIG no funciona
- **Causa**: UE no tiene geometría o capa no cargada
- **Solución**:
  1. Verificar que la capa UE esté cargada en QGIS
  2. Verificar que la UE tenga una geometría asociada

---

## Resumen de Campos de Base de Datos

| Campo | Tipo | Base de datos | Obligatorio |
|-------|------|---------------|-------------|
| Sitio | Text | sito | Sí |
| Número inventario | Integer | numero_inventario | Sí |
| Tipo hallazgo | Text | tipo_reperto | Sí |
| Clase material | Text | criterio_schedatura | No |
| Definición | Text | definizione | No |
| Descripción | Text | descrizione | No |
| Área | Text | area | No |
| UE | Text | us | No |
| Lavado | String(3) | lavato | No |
| Nr. caja | Text | nr_cassa | No |
| Lugar conservación | Text | luogo_conservazione | No |
| Estado conservación | String(200) | stato_conservazione | No |
| Datación | String(200) | datazione_reperto | No |
| Formas mínimas | Integer | forme_minime | No |
| Formas máximas | Integer | forme_massime | No |
| Total fragmentos | Integer | totale_frammenti | No |
| Cuerpo cerámico | String(200) | corpo_ceramico | No |
| Revestimiento | String(200) | rivestimento | No |
| Diámetro borde | Numeric | diametro_orlo | No |
| Peso | Numeric | peso | No |
| Tipo | String(200) | tipo | No |
| EVE borde | Numeric | eve_orlo | No |
| Repertoriado | String(3) | repertato | No |
| Diagnóstico | String(3) | diagnostico | No |
| RA | Integer | n_reperto | No |
| Tipo contenedor | String(200) | tipo_contenitore | No |
| Estructura | String(200) | struttura | No |
| Año | Integer | years | No |

---

*Última actualización: Enero 2026*
*PyArchInit - Gestión de Datos Arqueológicos*
