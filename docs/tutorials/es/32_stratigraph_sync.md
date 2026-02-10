# PyArchInit - StratiGraph: Panel de Sincronizacion

## Indice
1. [Introduccion](#introduccion)
2. [Acceso al panel](#acceso-al-panel)
3. [Comprension de la interfaz](#comprension-de-la-interfaz)
4. [Exportacion de bundles](#exportacion-de-bundles)
5. [Sincronizacion](#sincronizacion)
6. [Gestion de la cola](#gestion-de-la-cola)
7. [Configuracion](#configuracion)
8. [Resolucion de problemas](#resolucion-de-problemas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introduccion

A partir de la version **5.0.2-alpha**, PyArchInit incluye un panel **StratiGraph Sync** que permite la sincronizacion offline-first de datos con el Knowledge Graph de StratiGraph. Este panel forma parte del proyecto europeo **StratiGraph** (Horizon Europe) e implementa el flujo de trabajo offline-first: se trabaja localmente sin internet, se exportan los bundles cuando se esta listo y el sistema se sincroniza automaticamente cuando se restablece la conectividad.

<!-- VIDEO: Introduccion a StratiGraph Sync -->
> **Video Tutorial**: [Insertar enlace de video introduccion StratiGraph Sync]

### Vision general del flujo de trabajo

```
1. Trabajo offline      2. Exportar Bundle     3. Sincronizacion
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Entrada de datos      Exportar + Validar     Subir cuando online
   normal en             + Encolar              con reintento
   PyArchInit                                   automatico
```

---

## Acceso al panel

El panel StratiGraph Sync esta oculto por defecto y se puede activar mediante un boton en la barra de herramientas.

### Desde la barra de herramientas

1. Buscar el boton **StratiGraph Sync** en la barra de herramientas de PyArchInit -- tiene un icono verde con flechas de sincronizacion y la letra "S"
2. Hacer clic en el boton para **mostrar** el panel (es un boton de alternancia)
3. Hacer clic nuevamente para **ocultar** el panel

El panel aparece como un **dock widget a la izquierda** en la interfaz de QGIS. Se puede arrastrar y reposicionar como cualquier otro panel de QGIS.

<!-- IMAGE: Boton de la barra de herramientas para StratiGraph Sync -->
> **Fig. 1**: El boton StratiGraph Sync en la barra de herramientas (icono verde con flechas de sincronizacion y "S")

<!-- IMAGE: Panel acoplado en el lado izquierdo de QGIS -->
> **Fig. 2**: El panel StratiGraph Sync acoplado en el lado izquierdo de la ventana QGIS

---

## Comprension de la interfaz

El panel StratiGraph Sync se divide en varias secciones, de arriba a abajo.

### Indicador de estado

El **indicador de estado** en la parte superior del panel muestra el estado actual de sincronizacion de los datos. Los estados posibles son:

| Estado | Icono | Descripcion |
|--------|-------|-------------|
| **OFFLINE_EDITING** | Lapiz | Se esta trabajando localmente, editando datos normalmente |
| **LOCAL_EXPORT** | Paquete | Se esta exportando un bundle desde los datos locales |
| **LOCAL_VALIDATION** | Marca de verificacion | El bundle exportado esta siendo validado |
| **QUEUED_FOR_SYNC** | Reloj | El bundle ha sido validado y esta esperando para ser subido |
| **SYNC_SUCCESS** | Circulo verde | La ultima sincronizacion se completo con exito |
| **SYNC_FAILED** | Circulo rojo | El ultimo intento de sincronizacion fallo |

### Indicador de conexion

Debajo del indicador de estado, el **indicador de conexion** muestra si el sistema puede alcanzar el servidor StratiGraph:

| Estado | Significado |
|--------|-------------|
| **Online** | El endpoint de health check es accesible; la sincronizacion automatica esta activa |
| **Offline** | El endpoint de health check no es accesible; los bundles seran encolados |

El sistema comprueba automaticamente la conectividad cada **30 segundos** (configurable).

### Contador de cola

El **contador de cola** muestra dos numeros:

- **Bundles pendientes**: Numero de bundles esperando a ser subidos
- **Bundles fallidos**: Numero de bundles cuya subida ha fallado (se reintentaran automaticamente)

### Ultima sincronizacion

Muestra la **marca de tiempo** y el **resultado** (exito o fallo) del ultimo intento de sincronizacion.

### Botones de accion

| Boton | Accion |
|-------|--------|
| **Export Bundle** | Crea un bundle desde los datos locales, lo valida y lo agrega a la cola de sincronizacion |
| **Sync Now** | Fuerza un intento inmediato de sincronizacion (solo disponible cuando esta online) |
| **Queue...** | Abre el dialogo de gestion de cola mostrando todas las entradas |

### Registro de actividad

En la parte inferior del panel, un **registro de actividad** desplazable muestra entradas con marca de tiempo de la actividad reciente, incluyendo cambios de estado, exportaciones, validaciones e intentos de sincronizacion.

<!-- IMAGE: Panel completo con todas las secciones anotadas -->
> **Fig. 3**: El panel StratiGraph Sync completo con todas las secciones etiquetadas

---

## Exportacion de bundles

La exportacion de un bundle empaqueta los datos arqueologicos locales en un formato estructurado listo para subir al Knowledge Graph de StratiGraph.

### Procedimiento paso a paso

1. Asegurarse de haber guardado todo el trabajo actual en PyArchInit
2. Abrir el panel StratiGraph Sync (si no esta ya visible)
3. Hacer clic en el boton **Export Bundle**
4. El sistema realiza automaticamente tres operaciones:
   - **Exportacion**: Los datos locales se empaquetan en un archivo bundle
   - **Validacion**: El bundle se comprueba en cuanto a completitud e integridad de datos
   - **Encolamiento**: El bundle validado se agrega a la cola de sincronizacion
5. Observar el **indicador de estado** que pasa por: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. El **registro de actividad** registra cada paso con una marca de tiempo

### Que contiene un bundle

Un bundle contiene todas las entidades arqueologicas que tienen UUID (ver Tutorial 31 para detalles sobre UUID). Cada entidad se identifica por su `entity_uuid`, asegurando que el mismo registro siempre sea reconocido en el servidor.

<!-- IMAGE: Boton Export Bundle y transicion de estado -->
> **Fig. 4**: Clic en "Export Bundle" y observacion de los cambios de estado en el panel

---

## Sincronizacion

### Sincronizacion automatica

Cuando el sistema detecta que esta **online** (el health check tiene exito), sube automaticamente todos los bundles pendientes de la cola. No se requiere intervencion manual.

El proceso de sincronizacion automatica:

1. La comprobacion de conectividad tiene exito (el endpoint de health check responde)
2. El indicador de conexion cambia a **Online**
3. Los bundles pendientes en la cola se suben uno por uno
4. Los bundles subidos con exito se marcan como `SYNC_SUCCESS`
5. La marca de tiempo y el resultado de la **ultima sincronizacion** se actualizan

### Sincronizacion manual

Si se desea forzar un intento inmediato de sincronizacion:

1. Asegurarse de que el indicador de conexion muestre **Online**
2. Hacer clic en el boton **Sync Now**
3. El sistema intenta inmediatamente subir todos los bundles pendientes

El boton **Sync Now** solo es efectivo cuando el sistema esta online.

### Reintento automatico con backoff exponencial

Si una subida falla, el sistema **no** se rinde. En su lugar, reintenta automaticamente con retrasos crecientes:

| Intento | Retraso |
|---------|---------|
| 1er reintento | 30 segundos |
| 2o reintento | 60 segundos |
| 3er reintento | 120 segundos |
| 4o reintento | 5 minutos |
| 5o reintento | 15 minutos |

Esto evita sobrecargar el servidor cuando no esta disponible temporalmente, asegurando al mismo tiempo la entrega eventual.

<!-- IMAGE: Boton Sync Now e indicador de conexion -->
> **Fig. 5**: El boton "Sync Now" y el indicador de estado de conexion

---

## Gestion de la cola

El boton **Queue...** abre un dialogo detallado donde se pueden inspeccionar todos los bundles en la cola de sincronizacion.

### Columnas del dialogo de cola

| Columna | Descripcion |
|---------|-------------|
| **ID** | Identificador unico de la entrada en la cola |
| **Status** | Estado actual de la entrada (pending, syncing, success, failed) |
| **Attempts** | Numero de intentos de subida realizados hasta ahora |
| **Created** | Marca de tiempo de cuando el bundle fue agregado a la cola |
| **Last Error** | Mensaje de error del ultimo intento fallido (vacio si no hay error) |
| **Bundle path** | Ruta del archivo bundle en el sistema de archivos |

### Interpretar las entradas de la cola

- Las entradas **Pending** estan esperando para ser subidas
- Las entradas **Success** han sido subidas y confirmadas por el servidor
- Las entradas **Failed** se reintentaran automaticamente; consultar la columna **Last Error** para detalles
- El conteo de **Attempts** ayuda a entender cuantas veces el sistema ha intentado subir un bundle particular

### Almacenamiento de la cola

La base de datos de la cola se almacena como un archivo SQLite en:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Este archivo persiste entre sesiones de QGIS, por lo que los bundles pendientes no se pierden al cerrar QGIS.

<!-- IMAGE: Dialogo de cola mostrando varias entradas -->
> **Fig. 6**: El dialogo de gestion de cola con entradas de bundles

---

## Configuracion

### URL de Health Check

El sistema usa una URL de health check para determinar la conectividad con el servidor StratiGraph. Se puede configurar en las opciones de QGIS:

| Configuracion | Clave | Predeterminado |
|--------------|-------|----------------|
| URL de Health check | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Para cambiar la URL de health check:

1. Abrir **QGIS** -> **Configuracion** -> **Opciones** (o usar la consola Python de QGIS)
2. Navegar a la configuracion de PyArchInit o establecer mediante:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://su-servidor.ejemplo.com/health")
```

### Intervalo de comprobacion

El intervalo predeterminado de comprobacion de conectividad es de **30 segundos**. Esto tambien se puede configurar a traves de QgsSettings.

---

## Resolucion de problemas

### El panel no aparece

- Asegurarse de estar usando PyArchInit version **5.0.2-alpha** o posterior
- Verificar que el boton StratiGraph Sync sea visible en la barra de herramientas
- Intentar desactivar y reactivar el boton
- Comprobar **Ver** -> **Paneles** en QGIS para ver si el dock widget esta listado

### El indicador de conexion siempre muestra "Offline"

- Verificar que el servidor StratiGraph este ejecutandose y sea accesible
- Comprobar la URL de health check en la configuracion (predeterminado: `http://localhost:8080/health`)
- Probar la URL manualmente en un navegador o con `curl`:

```bash
curl http://localhost:8080/health
```

- Si el servidor esta en otra maquina, asegurarse de que no haya reglas de firewall bloqueando la conexion

### La exportacion del bundle falla

- Asegurarse de que la base de datos este conectada y accesible
- Verificar que los registros tengan UUID validos (Tutorial 31)
- Consultar el registro de actividad para mensajes de error especificos
- Asegurarse de que haya suficiente espacio en disco para el archivo bundle

### La sincronizacion falla repetidamente

- Comprobar la columna **Last Error** en el dialogo de cola para detalles
- Causas comunes:
  - El servidor no esta disponible temporalmente (el sistema reintentara automaticamente)
  - Problemas de conectividad de red
  - El servidor rechazo el bundle (comprobar los logs del servidor)
- Si un bundle falla consistentemente despues de muchos intentos, considerar reexportarlo

### Problemas con la base de datos de la cola

- La base de datos de la cola esta en `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Si esta corrupta, se puede eliminar de forma segura -- los bundles pendientes se perderan, pero pueden reexportarse
- Hacer una copia de seguridad de este archivo si es necesario preservar el estado de la cola

---

## Preguntas Frecuentes

### Necesito internet para usar PyArchInit?

**No.** PyArchInit funciona completamente sin conexion. El panel StratiGraph Sync solo gestiona la sincronizacion con el servidor StratiGraph. Se puede trabajar completamente offline y exportar/sincronizar cuando se este listo.

### Que pasa si cierro QGIS con bundles pendientes?

Los bundles pendientes se guardan en la base de datos de la cola y estaran disponibles al reiniciar QGIS. El sistema reanuda la sincronizacion automaticamente cuando se restablece la conectividad.

### Puedo exportar multiples bundles?

Si. Cada vez que se hace clic en "Export Bundle", se crea un nuevo bundle y se agrega a la cola. Se pueden encolar multiples bundles y se subiran secuencialmente.

### Como se si mis datos se han sincronizado?

Comprobar el indicador de **ultima sincronizacion** en el panel para el resultado mas reciente. Tambien se puede abrir el dialogo **Queue...** para ver el estado de cada bundle individual.

### StratiGraph Sync funciona tanto con PostgreSQL como con SQLite?

Si. El sistema de sincronizacion funciona con ambos backends de base de datos soportados por PyArchInit. Los bundles se exportan en un formato independiente de la base de datos.

### Cual es la relacion entre UUID y sincronizacion?

Los UUID (Tutorial 31) proporcionan los identificadores estables que hacen posible la sincronizacion. Cada entidad en un bundle se identifica por su UUID, permitiendo al servidor asociar, crear o actualizar registros correctamente.

---

*Documentacion PyArchInit - StratiGraph Sync*
*Version: 5.0.2-alpha*
*Ultima actualizacion: Febrero 2026*

---

## Animación Interactiva

Explora la animación interactiva para aprender más sobre este tema.

[Abrir Animación Interactiva](../../animations/stratigraph_sync_animation.html)
