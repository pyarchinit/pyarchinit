# Tutorial 25: Time Manager (GIS Time Controller)

## Introducción

El **Time Manager** (GIS Time Controller) es una herramienta avanzada para visualizar la secuencia estratigráfica en el tiempo. Permite "navegar" a través de los niveles estratigráficos usando un control temporal, visualizando progresivamente las UE desde la más antigua a la más reciente (la formación del sitio).

### Funcionalidades Principales

- Visualización progresiva de los niveles estratigráficos
- Control mediante dial/slider
- Modo acumulativo o nivel individual
- Generación automática de imágenes/video
- Integración con Matrix de Harris

## Acceso

### Desde el Menú
**PyArchInit** → **Time Manager**

### Prerrequisitos

- Capa con campo `order_layer` (índice estratigráfico)
- UE con order_layer completado
- Capas cargadas en QGIS

## Interfaz

### Panel Principal

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Capas disponibles:                                |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] otra_capa                                    |
+--------------------------------------------------+
|              [Dial Circular]                     |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Nivel: [SpinBox: 0-N]                   |
+--------------------------------------------------+
| [x] Modo Acumulativo (muestra <= nivel)         |
+--------------------------------------------------+
| [ ] Mostrar Matrix          [Stop] [Generar Video] |
+--------------------------------------------------+
| [Preview Matrix/Imagen]                          |
+--------------------------------------------------+
```

### Controles

| Control | Función |
|---------|---------|
| Checkbox Capa | Selecciona capa a controlar |
| Dial | Navega entre los niveles (rotación) |
| SpinBox | Introducción directa del nivel |
| Modo Acumulativo | Muestra todos los niveles hasta el seleccionado |
| Mostrar Matrix | Visualiza Matrix de Harris sincronizado |

## Campo order_layer

### ¿Qué es order_layer?

El campo `order_layer` define el orden estratigráfico de visualización:
- **0** = Nivel más antiguo (profundo)
- **N** = Nivel más reciente (superficial)

Es la convención del botón **Orden estratigráfico** con la casilla "Orden: Antiguo → Reciente" activa (configuración predeterminada, ver Tutorial 03): si la ordenación se calculó al revés, el Time Manager y el mapa muestran la secuencia invertida.

### Completar order_layer

En la Ficha de UE, pestaña **Ayuda** → **Tool Box**, el botón **Orden estratigráfico** calcula `order_layer` a partir de las relaciones estratigráficas (ver Tutorial 03); el valor de la UE actual aparece en el campo bajo el botón. Reglas:
1. 0 a las UE más antiguas, valores crecientes hacia las más recientes (en superficie)
2. UE contemporáneas pueden tener el mismo valor
3. Seguir la secuencia del Matrix

### Ejemplo

| UE | order_layer | Descripción |
|----|-------------|-------------|
| US001 | 4 | Humus superficial |
| US002 | 3 | Estrato de arado |
| US003 | 2 | Derrumbe |
| US004 | 1 | Plano de uso |
| US005 | 0 | Cimentación |

Desde la 5.13.19-alpha las capas de UE y USM que pyArchInit carga en el mapa (ver Tutorial 14, *Elección del Estilo*) se dibujan en el mismo orden que usa el Time Manager: por cronología del período y después por `order_layer` (0 = más antiguo), de modo que las unidades más recientes quedan encima.

## Modos de Visualización

### Modo Nivel Individual

Checkbox **NO** activo:
- Muestra SOLO las UE del nivel seleccionado
- Útil para aislar estratos individuales
- Visualización "por capas"

### Modo Acumulativo

Checkbox **ACTIVO**:
- Muestra todas las UE desde el nivel 0 (más antiguo) hasta el seleccionado
- Muestra la formación del sitio, de las UE más antiguas a las más recientes
- Visualización más realista

## Integración con Matrix

### Visualización Sincronizada

Con checkbox **"Mostrar Matrix"** activo:
- El Matrix de Harris aparece en el panel
- Se actualiza en sincronía con el nivel
- Resalta las UE del nivel actual

### Generación de Imágenes

El Time Manager puede generar:
- Capturas de pantalla para cada nivel
- Secuencia de imágenes
- Video time-lapse

## Generación de Video/Imágenes

### Proceso

1. Seleccionar capas a incluir
2. Configurar rango de niveles (mín-máx)
3. Hacer clic en **"Generar Video"**
4. Esperar el procesamiento
5. Output en carpeta designada

### Output

- Imágenes PNG para cada nivel
- Opcional: video MP4 compilado

## Workflow Típico

### 1. Preparación

```
1. Abrir proyecto QGIS con capas de UE
2. Verificar que order_layer esté completado
3. Abrir Time Manager
```

### 2. Selección de Capas

```
1. Seleccionar las capas a controlar
2. Normalmente: pyunitastratigrafiche y/o _usm
```

### 3. Navegación

```
1. Usar el dial o spinbox
2. Observar el cambio de visualización
3. Activar/desactivar modo acumulativo
```

### 4. Documentación

```
1. Activar "Mostrar Matrix"
2. Generar capturas significativas
3. Opcional: generar video
```

## Plantillas de Layout

### Carga de Plantilla

El Time Manager soporta plantillas QGIS para:
- Layouts de impresión personalizados
- Encabezados y leyendas
- Formatos estándar

### Plantillas Disponibles

En la carpeta `resources/templates/`:
- Plantilla base
- Plantilla con Matrix
- Plantilla para video

## Buenas Prácticas

### 1. order_layer

- Completar ANTES de usar Time Manager
- Usar valores consecutivos
- UE contemporáneas = mismo valor

### 2. Visualización

- Comenzar desde el nivel 0 (más antiguo)
- Proceder en orden creciente
- Usar modo acumulativo para presentaciones

### 3. Documentación

- Capturar pantalla en niveles significativos
- Documentar cambios de fase
- Generar video para memorias

## Resolución de Problemas

### Capas No Visibles en la Lista

**Causa**: Capa sin campo order_layer

**Solución**:
- Añadir campo order_layer a la capa
- Rellenarlo con valores apropiados

### Sin Cambio Visual

**Causas**:
- order_layer no completado
- Filtro no aplicado

**Soluciones**:
- Verificar valores order_layer en las UE
- Controlar que la capa esté seleccionada

### El Dial No Responde

**Causa**: Ninguna capa seleccionada

**Solución**: Seleccionar al menos una capa de la lista

## Referencias

### Archivos Fuente
- `tabs/Gis_Time_controller.py` - Interfaz principal
- `gui/ui/Gis_Time_controller.ui` - Layout UI

### Campo de Base de Datos
- `us_table.order_layer` - Índice estratigráfico

---

## Video Tutorial

### Time Manager
`[Placeholder: video_time_manager.mp4]`

**Contenidos**:
- Configuración de order_layer
- Navegación temporal
- Generación de video
- Integración con Matrix

**Duración prevista**: 15-18 minutos

---

*Última actualización: Enero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/pyarchinit_timemanager_animation.html)
