# PyArchInit - Gestion de Obra (Site Management)

## Indice

1. [Introduccion](#introduccion)
2. [Acceso al modulo](#acceso-al-modulo)
3. [Panel de Obra (Dashboard)](#panel-de-obra-dashboard)
4. [Formulario de Personal](#formulario-de-personal)
5. [Formulario de Asistencia](#formulario-de-asistencia)
6. [Formulario de Equipamiento](#formulario-de-equipamiento)
7. [Formulario de Presupuesto](#formulario-de-presupuesto)
8. [Flujo de trabajo operativo](#flujo-de-trabajo-operativo)
9. [Preguntas frecuentes (FAQ)](#preguntas-frecuentes-faq)
10. [Notas tecnicas](#notas-tecnicas)

---

## Introduccion

El modulo **Gestion de Obra** (*Gestione Cantiere*) es el componente de PyArchInit dedicado a la gestion administrativa y logistica de una excavacion arqueologica. Aborda los aspectos operativos del trabajo de campo: personal, asistencia, equipamiento y presupuesto.

El modulo esta compuesto por **cinco herramientas** independientes pero interconectadas:

| # | Herramienta | Funcion |
|---|-------------|---------|
| 1 | **Panel de Obra** | Dashboard central con resumen de presupuesto, personal, equipamiento y topografia |
| 2 | **Personal** | Registro CRUD de los trabajadores del proyecto |
| 3 | **Asistencia** | Registro CRUD de jornadas laborales, ausencias y costes diarios |
| 4 | **Equipamiento** | Registro CRUD de maquinaria, instrumentos y herramientas |
| 5 | **Presupuesto** | Registro CRUD de partidas presupuestarias (previstos vs. efectivos) |

<!-- IMAGE: Vista general del modulo Gestion de Obra con los 5 iconos de la barra de herramientas -->
> **Fig. 1**: Los cinco iconos del modulo Gestion de Obra en la barra de herramientas de PyArchInit

---

## Acceso al modulo

El modulo se accede desde la barra de herramientas **Gestion de Obra**, que contiene **5 iconos**: Panel de Obra, Personal, Asistencia, Equipamiento y Presupuesto. Al abrir cualquier formulario por primera vez, las tablas necesarias se crean automaticamente en la base de datos.

<!-- IMAGE: Barra de herramientas Gestion de Obra con los 5 botones resaltados -->
> **Fig. 2**: La barra de herramientas Gestion de Obra con los cinco botones de acceso

---

## Panel de Obra (Dashboard)

El **Panel de Obra** es el dashboard central del modulo. En la parte superior se encuentran los selectores de **Sitio** y **Ano** que filtran todos los indicadores.

### Seccion Presupuesto

| Indicador | Descripcion |
|-----------|-------------|
| **Importe previsto** | Suma total de las partidas planificadas |
| **Importe efectivo** | Suma total del gasto ejecutado |
| **Barra de progreso** | Porcentaje de ejecucion (verde <75%, amarillo 75-90%, rojo >90%) |
| **Grafico de sectores** | Distribucion del gasto por categorias |

<!-- IMAGE: Seccion Presupuesto del dashboard con barra de progreso y grafico de sectores -->
> **Fig. 3**: El resumen presupuestario con la barra de progreso y el grafico de sectores

### Seccion Personal

| Indicador | Descripcion |
|-----------|-------------|
| **Presentes / Vacaciones / Baja** | Contadores de estado del personal en el dia actual |
| **Horas mensuales** | Total de horas trabajadas en el mes en curso |
| **Coste mensual** | Coste total del personal en el mes en curso |

<!-- IMAGE: Seccion Personal del dashboard con los indicadores de presencia -->
> **Fig. 4**: El resumen de personal con los contadores de presencia y los totales mensuales

### Seccion Equipamiento

| Indicador | Descripcion |
|-----------|-------------|
| **Total / En uso / En mantenimiento** | Contadores de estado del inventario |
| **Alertas de mantenimiento** | Equipos con mantenimiento vencido (resaltados en rojo) |

<!-- IMAGE: Seccion Equipamiento del dashboard con indicadores y alertas -->
> **Fig. 5**: El resumen de equipamiento con los indicadores de estado y las alertas

### Seccion Topografia (Computo Metrico)

| Metodo | Descripcion |
|--------|-------------|
| **Diferencia de DEM** | Volumen comparando dos DEM (antes y despues de la excavacion) |
| **DEM + Poligono** | Volumen dentro de un area poligonal definida sobre un DEM |

Procedimiento: seleccionar los rasters (y poligono si aplica), hacer clic en **Calcular** y el resultado se muestra en metros cubicos.

<!-- IMAGE: Seccion Topografia con los dos metodos de calculo de volumenes -->
> **Fig. 6**: Los dos metodos de computo metrico: diferencia de DEM y DEM+poligono

### Tabla de historial

En la parte inferior del panel, una tabla muestra los eventos recientes del proyecto con columnas: **Fecha**, **Tipo**, **Descripcion** y **Usuario**.

<!-- IMAGE: Tabla de historial en la parte inferior del Panel de Obra -->
> **Fig. 7**: La tabla de historial del Panel de Obra

---

## Formulario de Personal

Permite registrar los datos de trabajadores y colaboradores del proyecto.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **Nombre** | Texto | Si |
| **Apellidos** | Texto | Si |
| **Cualificacion** | ComboBox (arqueologo, tecnico, operario...) | No |
| **Rol** | ComboBox (director, responsable de area, excavador...) | No |
| **Fecha de contratacion** | Fecha | No |
| **Fecha de fin** | Fecha (vacia si activo) | No |
| **Coste diario** | Numerico (euros) | No |
| **Notas** | Texto | No |

**Crear registro**: New record > completar campos > Save. **Buscar**: new search > criterios > search !!!

<!-- IMAGE: Formulario de Personal con todos los campos visibles -->
> **Fig. 8**: El formulario de Personal con los campos de registro

---

## Formulario de Asistencia

Registra las jornadas laborales de cada trabajador.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **ID Personal** | ComboBox (vinculado a Personal) | Si |
| **Fecha** | Fecha | Si |
| **Tipo de jornada** | ComboBox: Laboral / Vacaciones / Baja / Permiso | Si |
| **Horas ordinarias** | Numerico | No |
| **Horas extra** | Numerico | No |
| **Coste jornada** | Numerico (calculo automatico o manual) | No |
| **Notas** | Texto | No |

**Registrar jornada**: New record > seleccionar trabajador, fecha y tipo > insertar horas > Save. El coste puede calcularse automaticamente a partir del coste diario del trabajador.

<!-- IMAGE: Formulario de Asistencia con un registro de jornada laboral -->
> **Fig. 9**: El formulario de Asistencia con un registro completado

---

## Formulario de Equipamiento

Gestiona el inventario de maquinaria e instrumentos.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **Nombre** | Texto | Si |
| **Tipo** | ComboBox (maquinaria, instrumento topografico, herramienta...) | No |
| **Marca** / **Modelo** | Texto | No |
| **Estado** | ComboBox: `en_uso` / `mantenimiento` / `fuera_servicio` | Si |
| **Fecha de compra** | Fecha | No |
| **Coste** | Numerico (euros) | No |
| **Fecha ultimo mantenimiento** | Fecha | No |
| **Fecha proximo mantenimiento** | Fecha | No |
| **Notas** | Texto | No |

Cuando la fecha de proximo mantenimiento se supera, el **Panel de Obra** muestra una alerta en rojo.

<!-- IMAGE: Formulario de Equipamiento con un registro de instrumento topografico -->
> **Fig. 10**: El formulario de Equipamiento con un registro de estacion total

---

## Formulario de Presupuesto

Planifica y controla los costes del proyecto por ano y categoria.

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| **Sitio** | ComboBox | Si |
| **Ano** | Numerico | Si |
| **Categoria** | ComboBox (Personal, Materiales, Equipamiento, Logistica, Documentacion, Laboratorio, Otros) | Si |
| **Partida** | Texto (descripcion de la linea de gasto) | Si |
| **Importe previsto** | Numerico (euros) | No |
| **Importe efectivo** | Numerico (euros) | No |
| **Notas** | Texto | No |

**Crear partida**: New record > seleccionar sitio, ano y categoria > insertar partida e importe previsto > Save. Actualizar el importe efectivo cuando se conozca el gasto real.

<!-- IMAGE: Formulario de Presupuesto con una partida registrada -->
> **Fig. 11**: El formulario de Presupuesto con una partida presupuestaria registrada

---

## Flujo de trabajo operativo

### Configuracion inicial

1. **Crear el sitio** en la Ficha de Sitio (ver [Tutorial Ficha de Sitio](02_ficha_sitio.md))
2. **Registrar el personal**: abrir Personal, crear un registro por trabajador con cualificacion, rol y coste diario
3. **Crear el presupuesto**: abrir Presupuesto, insertar las partidas con importes previstos
4. **Registrar el equipamiento**: abrir Equipamiento, registrar cada equipo con estado y fechas de mantenimiento
5. **Verificar en el Panel de Obra**: seleccionar sitio y ano, comprobar que los indicadores reflejan los datos

### Gestion diaria

- **Asistencia**: registrar la jornada de cada trabajador (tipo, horas, coste)
- **Presupuesto**: actualizar el importe efectivo cuando se produce un gasto
- **Equipamiento**: actualizar el estado cuando un equipo entra o sale de mantenimiento
- **Panel de Obra**: consultar los indicadores para verificar el estado general del proyecto

<!-- IMAGE: Diagrama del flujo de trabajo diario con los formularios interconectados -->
> **Fig. 12**: El flujo de trabajo diario: asistencia, presupuesto y equipamiento

---

## Preguntas frecuentes (FAQ)

**P: Es necesario crear el sitio antes de usar el modulo?**
R: Si. Todos los formularios requieren un sitio previamente registrado en la Ficha de Sitio.

**P: Funciona con SQLite y PostgreSQL?**
R: Si. Todas las funcionalidades estan disponibles en ambos motores de base de datos.

**P: Como se vincula un registro de asistencia a un trabajador?**
R: El campo **ID Personal** del formulario de Asistencia se vincula al identificador unico del registro en el formulario de Personal.

**P: El coste de la jornada se calcula automaticamente?**
R: Si, a partir del coste diario del trabajador y las horas registradas. Tambien se puede insertar manualmente.

**P: Que sucede cuando un equipo tiene el mantenimiento vencido?**
R: El Panel de Obra muestra una alerta en rojo en la seccion de Equipamiento.

**P: Que ocurre si el importe efectivo supera el previsto?**
R: La barra de progreso del Panel de Obra cambia a rojo, indicando sobrecosto.

**P: Se puede tener presupuesto para varios anos?**
R: Si. Cada partida tiene un campo de ano. Se filtran desde el selector del Panel de Obra.

---

## Notas tecnicas

### Tablas de base de datos

| Formulario | Tabla |
|------------|-------|
| Personal | `cantiere_personale_table` |
| Asistencia | `cantiere_presenze_table` |
| Equipamiento | `cantiere_attrezzature_table` |
| Presupuesto | `cantiere_budget_table` |

### Archivos fuente

| Archivo | Descripcion |
|---------|-------------|
| `tabs/Cantiere_Dashboard.py` | Controlador del Panel de Obra |
| `tabs/Cantiere_Personale.py` | Controlador del formulario de Personal |
| `tabs/Cantiere_Presenze.py` | Controlador del formulario de Asistencia |
| `tabs/Cantiere_Attrezzature.py` | Controlador del formulario de Equipamiento |
| `tabs/Cantiere_Budget.py` | Controlador del formulario de Presupuesto |
| `gui/ui/Cantiere_*.ui` | Disenos de interfaz Qt Designer |

### Compatibilidad

| Componente | Version minima |
|------------|---------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| SQLite | 3.x |
| PostgreSQL | 12+ |

---

*Documentacion PyArchInit - Gestion de Obra*
*Version: 5.0.x*
*Ultima actualizacion: Febrero 2026*
