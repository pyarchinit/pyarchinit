# Tutorial 07: Ficha de Individuos

## Introducción

La **Ficha de Individuos** es el módulo de PyArchInit dedicado a la documentación antropológica de los restos humanos encontrados durante la excavación. Esta ficha registra información sobre el sexo, la edad, la posición del cuerpo y el estado de conservación del esqueleto.

### Conceptos Básicos

**Individuo en PyArchInit:**
- Un individuo es un conjunto de restos óseos atribuibles a una sola persona
- Está conectado a la Ficha de Tumba (contexto sepulcral)
- Está conectado a la Ficha de Estructura (estructura física)
- Puede estar conectado a la Arqueozoología para análisis específicos

**Datos Antropológicos:**
- Estimación del sexo biológico
- Estimación de la edad de muerte
- Posición y orientación del cuerpo
- Estado de conservación y completitud

---

## Acceso a la Ficha

### Vía Menú
1. Menú **PyArchInit** en la barra de menús de QGIS
2. Seleccionar **Ficha de Individuos** (o **Individual form**)

### Vía Toolbar
1. Localizar la barra de herramientas PyArchInit
2. Hacer clic en el icono **Individuos** (figura humana)

---

## Vista General de la Interfaz

La ficha presenta un diseño organizado en secciones funcionales:

### Áreas Principales

| # | Área | Descripción |
|---|------|-------------|
| 1 | Toolbar DBMS | Navegación, búsqueda, guardado |
| 2 | DB Info | Estado del registro, ordenamiento, contador |
| 3 | Campos Identificativos | Sitio, Área, UE, Nr. Individuo |
| 4 | Conexión Estructura | Sigla y número de estructura |
| 5 | Área de Pestañas | Pestañas temáticas para datos específicos |

---

## Toolbar DBMS

La barra de herramientas principal proporciona las herramientas para la gestión de registros.

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
| New record | Crear un nuevo registro de individuo |
| Save | Guardar las modificaciones |
| Delete | Eliminar el registro actual |

### Botones de Búsqueda

| Icono | Función | Descripción |
|-------|---------|-------------|
| New search | Iniciar nueva búsqueda |
| Search!!! | Ejecutar búsqueda |
| Order by | Ordenar resultados |
| View all | Ver todos los registros |

### Botones Especiales

| Icono | Función | Descripción |
|-------|---------|-------------|
| PDF export | Exportar a PDF |
| Open directory | Abrir carpeta de exportación |

---

## Campos Identificativos

Los campos identificativos definen de forma única el individuo en la base de datos.

### Sitio

**Campo**: `comboBox_sito`
**Base de datos**: `sito`

Selecciona el sitio arqueológico de pertenencia.

### Área

**Campo**: `comboBox_area`
**Base de datos**: `area`

Área de excavación dentro del sitio. Los valores provienen del tesauro.

### UE

**Campo**: `comboBox_us`
**Base de datos**: `us`

Unidad Estratigráfica de referencia.

### Número de Individuo

**Campo**: `lineEdit_individuo`
**Base de datos**: `nr_individuo`

Número progresivo del individuo. Se propone automáticamente el siguiente número disponible.

**Notas:**
- La combinación Sitio + Área + UE + Nr. Individuo debe ser única
- El número se asigna automáticamente en la creación

### Conexión con Estructura

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Sigla estructura | `sigla_struttura` | Sigla de la estructura (ej. TM) |
| Nr estructura | `nr_struttura` | Número de la estructura |

Estos campos conectan el individuo con la estructura funeraria.

---

## Datos de Catalogación

### Fecha de Catalogación

**Campo**: `dateEdit_schedatura`
**Base de datos**: `data_schedatura`

Fecha de compilación de la ficha.

### Catalogador

**Campo**: `comboBox_schedatore`
**Base de datos**: `schedatore`

Nombre del operador que compila la ficha.

---

## Pestaña Datos Descriptivos

La primera pestaña contiene los datos antropológicos fundamentales.

### Estimación del Sexo

**Campo**: `comboBox_sesso`
**Base de datos**: `sesso`

Estimación del sexo biológico basada en caracteres morfológicos.

**Valores:**
| Valor | Descripción |
|-------|-------------|
| Masculino | Caracteres masculinos evidentes |
| Femenino | Caracteres femeninos evidentes |
| Masculino probable | Predominio de caracteres masculinos |
| Femenino probable | Predominio de caracteres femeninos |
| Indeterminado | No determinable |

**Criterios de determinación:**
- Morfología de la pelvis
- Morfología del cráneo
- Robustez general del esqueleto
- Dimensiones de los huesos

### Estimación de la Edad de Muerte

| Campo | Base de datos | Descripción |
|-------|---------------|-------------|
| Edad mínima | `eta_min` | Límite inferior de la estimación |
| Edad máxima | `eta_max` | Límite superior de la estimación |

**Métodos de estimación:**
- Sínfisis púbica
- Superficie auricular
- Suturas craneales
- Desarrollo dentario (para subadultos)
- Epífisis óseas (para subadultos)

### Clases de Edad

**Campo**: `comboBox_classi_eta`
**Base de datos**: `classi_eta`

Clasificación por franjas de edad.

**Valores típicos:**
| Clase | Edad aproximada |
|-------|-----------------|
| Infans I | 0-6 años |
| Infans II | 7-12 años |
| Juvenis | 13-20 años |
| Adultus | 21-40 años |
| Maturus | 41-60 años |
| Senilis | >60 años |

### Observaciones

**Campo**: `textEdit_osservazioni`
**Base de datos**: `osservazioni`

Campo de texto para notas antropológicas específicas.

**Contenidos recomendados:**
- Patologías observadas
- Traumatismos
- Marcadores ocupacionales
- Anomalías esqueléticas
- Notas sobre la determinación del sexo y la edad

---

## Pestaña Orientación y Posición

Esta pestaña documenta la posición y orientación del cuerpo.

### Estado de Conservación

| Campo | Base de datos | Valores |
|-------|---------------|---------|
| Completo | `completo_si_no` | Sí / No |
| Alterado | `disturbato_si_no` | Sí / No |
| En conexión | `in_connessione_si_no` | Sí / No |

**Definiciones:**
- **Completo**: todos los distritos anatómicos están representados
- **Alterado**: evidencias de remoción post-deposicional
- **En conexión**: las articulaciones están preservadas

### Longitud del Esqueleto

**Campo**: `lineEdit_lunghezza`
**Base de datos**: `lunghezza_scheletro`

Longitud medida del esqueleto in situ (en cm o m).

### Posición del Esqueleto

**Campo**: `comboBox_posizione_scheletro`
**Base de datos**: `posizione_scheletro`

Posición general del cuerpo.

**Valores:**
- Supino (boca arriba)
- Prono (boca abajo)
- Lateral derecho
- Lateral izquierdo
- Encogido
- Irregular

### Posición del Cráneo

**Campo**: `comboBox_posizione_cranio`
**Base de datos**: `posizione_cranio`

Orientación de la cabeza.

**Valores:**
- Hacia la derecha
- Hacia la izquierda
- Hacia arriba
- Hacia abajo
- No determinable

### Posición de Extremidades Superiores

**Campo**: `comboBox_arti_superiori`
**Base de datos**: `posizione_arti_superiori`

Posición de los brazos.

**Valores:**
- Extendidos a los lados
- Sobre la pelvis
- Sobre el tórax
- Cruzados sobre el tórax
- Mixtos
- No determinable

### Posición de Extremidades Inferiores

**Campo**: `comboBox_arti_inferiori`
**Base de datos**: `posizione_arti_inferiori`

Posición de las piernas.

**Valores:**
- Extendidas
- Flexionadas
- Cruzadas
- Separadas
- No determinable

### Orientación del Eje

**Campo**: `comboBox_orientamento_asse`
**Base de datos**: `orientamento_asse`

Orientación del eje longitudinal del cuerpo.

**Valores:**
- N-S (cabeza al Norte)
- S-N (cabeza al Sur)
- E-W (cabeza al Este)
- W-E (cabeza al Oeste)
- NE-SW, NW-SE, etc.

### Orientación Acimut

**Campo**: `lineEdit_azimut`
**Base de datos**: `orientamento_azimut`

Valor numérico del acimut en grados (0-360).

---

## Pestaña Restos Osteológicos

Esta pestaña está dedicada a la documentación de los distritos anatómicos.

### Documentación de los Distritos

Permite registrar:
- Presencia/ausencia de los elementos óseos individuales
- Estado de conservación por distrito
- Lado (derecho/izquierdo) para elementos pares

**Distritos principales:**
| Distrito | Elementos |
|----------|-----------|
| Cráneo | Calvaria, mandíbula, dientes |
| Columna | Vértebras cervicales, torácicas, lumbares, sacro |
| Tórax | Costillas, esternón |
| Extremidades superiores | Clavículas, escápulas, húmeros, radio, cúbito, manos |
| Pelvis | Coxales |
| Extremidades inferiores | Fémures, tibia, peroné, pies |

---

## Pestaña Otras Características

Esta pestaña contiene información adicional.

### Contenidos

- Características métricas específicas
- Índices antropométricos
- Patologías detalladas
- Relaciones con otros individuos

---

## Exportación e Impresión

### Export PDF

El botón PDF abre un panel con opciones:

| Opción | Descripción |
|--------|-------------|
| Lista de Individuos | Lista sintética |
| Fichas de Individuos | Fichas completas detalladas |
| Imprimir | Genera el PDF |

### Contenido de la Ficha PDF

La ficha PDF incluye:
- Datos identificativos
- Datos antropológicos (sexo, edad)
- Posición y orientación
- Estado de conservación
- Observaciones

---

## Workflow Operativo

### Creación de Nuevo Individuo

1. **Apertura de la ficha**
   - Vía menú o barra de herramientas

2. **Nuevo registro**
   - Clic en "New Record"
   - El número de individuo se propone automáticamente

3. **Datos identificativos**
   ```
   Sitio: Necrópolis de Isola Sacra
   Área: 1
   UE: 150
   Nr. Individuo: 1
   Sigla estructura: TM
   Nr estructura: 45
   ```

4. **Datos de catalogación**
   ```
   Fecha: 15/03/2024
   Catalogador: M. Rossi
   ```

5. **Datos antropológicos** (Pestaña 1)
   ```
   Sexo: Masculino
   Edad mín: 35
   Edad máx: 45
   Clase edad: Adultus

   Observaciones: Estatura estimada 170 cm.
   Artrosis lumbar. Caries múltiples.
   ```

6. **Orientación y Posición** (Pestaña 2)
   ```
   Completo: Sí
   Alterado: No
   En conexión: Sí
   Longitud: 165 cm
   Posición: Supino
   Cráneo: Hacia la derecha
   Extremidades superiores: Extendidas a los lados
   Extremidades inferiores: Extendidas
   Orientación: E-W
   Acimut: 90
   ```

7. **Restos osteológicos** (Pestaña 3)
   - Documentar los distritos presentes

8. **Guardado**
   - Clic en "Save"

### Búsqueda de Individuos

1. Clic en "New Search"
2. Completar criterios:
   - Sitio
   - Sexo
   - Clase de edad
   - Posición
3. Clic en "Search"
4. Navegar entre los resultados

---

## Relaciones con Otras Fichas

| Ficha | Relación |
|-------|----------|
| **Ficha de Sitio** | El sitio contiene los individuos |
| **Ficha de Estructura** | La estructura contiene el individuo |
| **Ficha de Tumba** | La tumba documenta el contexto |
| **Arqueozoología** | Para análisis osteológicos específicos |

### Flujo de Trabajo Recomendado

1. Crear la **Ficha de Estructura** para la tumba
2. Crear la **Ficha de Tumba**
3. Crear la **Ficha de Individuos** para cada esqueleto
4. Conectar el individuo a la tumba y estructura

---

## Buenas Prácticas

### Determinación del Sexo

- Utilizar múltiples indicadores morfológicos
- Indicar el grado de fiabilidad
- Especificar los criterios utilizados en las observaciones

### Estimación de la Edad

- Proporcionar siempre un rango (mín-máx)
- Indicar los métodos utilizados
- Para subadultos, especificar desarrollo dentario y epifisario

### Posición y Orientación

- Documentar con fotos antes de la extracción
- Usar referencias cardinales
- Medir el acimut con brújula

### Conservación

- Distinguir pérdidas tafonómicas de extracciones antiguas
- Documentar las perturbaciones post-deposicionales
- Registrar condiciones de recuperación

---

## Resolución de Problemas

### Problema: Número de individuo duplicado

**Causa**: Ya existe un individuo con el mismo número.

**Solución**:
1. Verificar la numeración existente
2. Usar el número propuesto automáticamente
3. Comprobar área y UE

### Problema: Estructura no encontrada

**Causa**: La estructura no existe o tiene sigla diferente.

**Solución**:
1. Verificar la existencia de la Ficha de Estructura
2. Comprobar sigla y número
3. Crear primero la estructura si es necesario

### Problema: Clases de edad no disponibles

**Causa**: Tesauro no configurado.

**Solución**:
1. Verificar la configuración del tesauro
2. Comprobar el idioma configurado
3. Contactar al administrador

---

## Referencias

### Base de Datos

- **Tabla**: `individui_table`
- **Clase mapper**: `SCHEDAIND`
- **ID**: `id_scheda_ind`

### Archivos Fuente

- **UI**: `gui/ui/Schedaind.ui`
- **Controlador**: `tabs/Schedaind.py`
- **Export PDF**: `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

*Última actualización: Enero 2026*
*PyArchInit - Sistema de Gestión de Datos Arqueológicos*
