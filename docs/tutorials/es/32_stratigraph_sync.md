# PyArchInit - StratiGraph: Panel de Sincronizacion

> El panel y la ventana de la sala siguen el idioma de la interfaz de QGIS; aqui los botones se citan como aparecen en espanol.

## Indice
1. [Introduccion](#introduccion)
2. [Acceso al panel](#acceso-al-panel)
3. [Comprension de la interfaz](#comprension-de-la-interfaz)
4. [Exportacion de bundles](#exportacion-de-bundles)
5. [Sincronizacion](#sincronizacion)
6. [Gestion de la cola](#gestion-de-la-cola)
7. [Enviar un sitio a una sala StratiGraph](#enviar-un-sitio-a-una-sala-stratigraph)
8. [Configuracion](#configuracion)
9. [Resolucion de problemas](#resolucion-de-problemas)
10. [Preguntas Frecuentes](#preguntas-frecuentes)

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
| **Exportar paquete** | Crea un bundle desde los datos locales, lo valida y lo agrega a la cola de sincronizacion |
| **Sincronizar ahora** | Fuerza un intento inmediato de sincronizacion (solo disponible cuando esta online) |
| **Cola...** | Abre el dialogo de gestion de cola mostrando todas las entradas |
| **Enviar el sitio a una sala...** | Inicia sesion en un nodo StratiGraph y lleva un sitio a una sala (ver abajo) |

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
3. Hacer clic en el boton **Exportar paquete**
4. El sistema realiza automaticamente tres operaciones:
   - **Exportacion**: Los datos locales se empaquetan en un archivo bundle
   - **Validacion**: El bundle se comprueba en cuanto a completitud e integridad de datos
   - **Encolamiento**: El bundle validado se agrega a la cola de sincronizacion
5. Observar el **indicador de estado** que pasa por: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. El **registro de actividad** registra cada paso con una marca de tiempo

### Que contiene un bundle

Un bundle contiene todas las entidades arqueologicas que tienen UUID (ver Tutorial 31 para detalles sobre UUID). Cada entidad se identifica por su `entity_uuid`, asegurando que el mismo registro siempre sea reconocido en el servidor.

<!-- IMAGE: Boton Exportar paquete y transicion de estado -->
> **Fig. 4**: Clic en "Exportar paquete" y observacion de los cambios de estado en el panel

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
2. Hacer clic en el boton **Sincronizar ahora**
3. El sistema intenta inmediatamente subir todos los bundles pendientes

El boton **Sincronizar ahora** solo es efectivo cuando el sistema esta online.

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

<!-- IMAGE: Boton Sincronizar ahora e indicador de conexion -->
> **Fig. 5**: El boton "Sincronizar ahora" y el indicador de estado de conexion

---

## Gestion de la cola

El boton **Cola...** abre un dialogo detallado donde se pueden inspeccionar todos los bundles en la cola de sincronizacion.

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

## Enviar un sitio a una sala StratiGraph

Desde la version **5.14.0-alpha** el boton **Enviar el sitio a una sala...** lleva un sitio a una *sala* de un nodo StratiGraph (StratiGraph Server). El grafo del sitio se convierte en el contenido de la sala, donde EMStudio, EM Tools y las demas herramientas del proyecto lo ven y trabajan con el.

![Panel StratiGraph Sync](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: El panel StratiGraph Sync con el boton **Enviar el sitio a una sala...**

### Procedimiento paso a paso

1. En el panel **StratiGraph Sync**, pulse **Enviar el sitio a una sala...**
2. **Nodo**: la direccion del nodo, por ejemplo `https://nodo.example.org/em`. Se recuerda entre sesiones.
3. **Sitio**: elija el sitio. **Id de la sala** y **Título de la sala** se rellenan con el nombre del sitio y se pueden cambiar; el id de la sala es una sola palabra, sin espacios.
4. Pulse **Iniciar sesión...**: la pagina de acceso del nodo se abre en el navegador. Acceda con su cuenta y vuelva a QGIS: la linea **Identidad** muestra su nombre y si puede crear salas. Si el nodo tiene un cliente Keycloak dedicado a pyArchInit, su nombre va en el ajuste de QGIS `pyArchInit/stratigraph/client_id`; si no, se usa el cliente que indica el nodo.
5. Opcional: **Solo plan** muestra lo que se enviaria sin escribir nada en el nodo.
6. Pulse **Enviar el sitio**: el registro indica los nodos y aristas exportados y el resultado.

![Ventana Enviar el sitio a una sala](images/32_stratigraph_sync/07_send_site_dialog.png)

> **Fig. 8**: La ventana tras el acceso y el envio del sitio de ejemplo a un nodo de desarrollo: 745 operaciones aplicadas, 0 rechazadas, la base de datos conservada como referencia

### Que se envia

- El grafo del sitio entero, como un solo grafo aunque el sitio tenga varios sondeos: asi las relaciones entre unidades de sondeos distintos viajan con el resto.
- Los archivos citados por el grafo se suben una sola vez. Volver a enviar el mismo sitio no duplica nada.
- **Los archivos de base de datos nunca se suben** (sqlite, spatialite, gpkg): en la sala queda solo una referencia. Los demas sitios de su base de datos se quedan en su ordenador.
- La contrasena nunca pasa por pyArchInit: se escribe solo en la pagina del nodo. El token de acceso queda en memoria y se pierde al cerrar la ventana.

### Desde la linea de comandos

El mismo envio sin QGIS (sin `--dry-run` escribe de verdad; sin `--token` abre el navegador para acceder):

```bash
python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \
    --site "Scavo archeologico" --node https://nodo.example.org/em --room scavo-2026 --dry-run
```

### Trabajar con una sala que ya tiene datos

Cuando en la sala trabajan tambien otros (EMStudio, StratiField, EM Tools), despues de acceder:

1. **Comparar con la sala** compara el sitio con la sala en los dos sentidos, sin escribir nada: que tiene de nuevo la sala para pyArchInit (unidades nuevas, definiciones cambiadas, relaciones) y que anade pyArchInit a la sala.
2. **Enviar los cambios** envía a la sala el trabajo hecho aquí: unidades y relaciones nuevas, campos cambiados aquí, relaciones quitadas aquí. Lo que cambió solo en la sala no se toca; un campo cambiado en ambos lados es un conflicto y solo se muestra (véase «Sincronización con memoria»).
3. **Traer de la sala** lleva la sala a las fichas de pyArchInit (UE, definiciones, periodizacion, relaciones), reconociendo cada ficha por su identificador. Si el pull quitara relaciones locales que la sala no conoce, la ventana las enumera y pide confirmacion.

Con **Traer de la sala** tambien se puede reconstruir un sitio en una base de datos que no lo tiene: las unidades vuelven con numero, tipo, definiciones y periodizacion. Las unidades de continuidad (CON) no viajan: pyArchInit las regenera con **Genera continuita**.

La sala recibe la ficha UE entera, no solo los campos del grafo: descripcion, interpretacion, color, consistencia, cotas, medidas, sondeo, ambiente, cuadro, sector, los campos de mamposteria (USM). Una ficha reconstruida desde una sala es igual a la original; las relaciones cambian solo en la escritura (con area y sitio). Una sala enviada con una version anterior de pyArchInit tiene solo los campos del grafo: la comparacion muestra muchos campos distintos; basta un nuevo **Enviar el sitio** para completarla.

Todo esto vale tanto para SQLite como para PostgreSQL. Para reconstruir un sitio basta una base de datos de pyArchInit creada y vacia, abierta en pyArchInit: **Traer de la sala** la rellena (sitio, fichas, periodizacion, relaciones, medios). Las relaciones tienen siempre cuatro elementos: tipo, UE, area, sitio.

![Comparacion con la sala](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: La comparacion con una sala en la que se ha trabajado tambien en EMStudio: una UE nueva y una definicion revisada en la sala, una UE nueva de pyArchInit para enviar

### Fotos y medios en la sala

Las fotos, los videos, los modelos 3D y los documentos vinculados a las fichas UE viajan con el sitio, en ambos sentidos. Las ortofotos y los demas raster quedan fuera: son capas de QGIS, no medios de pyArchInit.

- **Enviar el sitio** y **Enviar los cambios** suben cada archivo al deposito de la sala una sola vez: un archivo que la sala ya tiene (mismo contenido) no se reenvia. Si el original ya no esta en el disco se usa la copia de la carpeta Resize.
- **Traer de la sala** descarga los medios nuevos en la carpeta `stratigraph_media/<sala>` del home de pyArchInit, crea miniatura y copia como al cargar un archivo desde la ficha y los vincula a su UE, con descripcion y etiquetas. Un medio que la base de datos ya tiene (reconocido por su identificador) no se vuelve a descargar: solo se comprueba el vinculo.
- Los medios de hallazgos, ceramica, tumbas y estructuras por ahora quedan en local: la ventana los cuenta.

![Una foto nueva enviada a la sala](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: Una foto anadida a la UE 3 despues de enviar el sitio: la comparacion la encuentra y Enviar los cambios sube el archivo y su vinculo

### Sincronización con memoria

Después del primer **Traer de la sala** (o del primer **Enviar el sitio**) pyArchInit recuerda la sala tal como era en ese momento: la *base* común, guardada en la carpeta `stratigraph_rooms` del home de pyArchInit, una por base de datos, sitio y sala. Desde entonces:

- la comparación lee de la sala **solo lo nuevo** desde la última sincronización, no todo el documento;
- cada diferencia tiene un autor: **cambiado aquí** (se envía), **cambiado en la sala** (lo trae «Traer»), **cambiado en ambos lados** (conflicto, mostrado con los dos valores), **quitado en la sala** (se quita también aquí), **quitado aquí** (se envía);
- **Traer de la sala** nunca sobrescribe en silencio trabajo aún no enviado: si hay cambios locales, conflictos, relaciones añadidas o quitadas aquí, la ventana los lista y aconseja enviarlos antes. En un conflicto confirmado gana el valor de la sala.

Las unidades que el traer deja fuera a propósito (las continuidades CON generadas y sus medios) quedan en la sala y no cuentan como eliminaciones. Funciona igual con SQLite y PostgreSQL.

![Comparación a tres vías](images/32_stratigraph_sync/10_three_way_compare.png)

> **Fig. 11**: La comparación tras una sincronización: un campo cambiado aquí por enviar, uno cambiado en la sala por traer, un conflicto en el mismo campo

### Geometrías: sitio, sondeos, áreas y cortes

Con el sitio viajan también los dibujos de las capas SIG de pyArchInit, como huellas en su propio sistema de referencia: el polígono del **sitio** (`pyarchinit_siti_polygonal`), los **sondeos** (`pyarchinit_sondaggi`), **áreas y sectores** (`pyarchinit_ripartizioni_spaziali`) y los **cortes**, es decir las UE negativas (`pyunitastratigrafiche`). Salen de SQLite y de PostGIS.

**Traer de la sala** los vuelve a escribir en las capas, SpatiaLite o PostGIS, en el sistema de referencia de la capa: un elemento que falta se añade, uno igual no se toca, y un elemento **dibujado aquí de otro modo se queda como está** y se señala: el traer nunca sobrescribe un dibujo local.

Los polígonos de las UE positivas no viajan: para el Extended Matrix su geometría es el modelo 3D. Ortofotos y ráster se quedan en QGIS.

### Problemas frecuentes

| Mensaje | Que hacer |
|---------|-----------|
| `401` o acceso caducado | La sesion se renueva sola mientras se trabaja; si ha caducado del todo (muchas horas sin usarla) pulse de nuevo **Iniciar sesión...** |
| ⚠ «El número … es de varias unidades» | En la misma área dos unidades tienen el mismo número y distinto tipo: las relaciones indican la unidad solo con número, área y sitio, así que en la sala alcanzan ambas. Renumerar una de ellas antes de enviar |
| `403` / *may create rooms: False* | La cuenta no tiene un rol en la sala o no puede crear salas: pregunte al administrador del nodo |
| `CERTIFICATE_VERIFY_FAILED` | El nodo usa un certificado local (nodo de desarrollo o de campo): instale su CA en el ordenador, o use `--ca-file` en la linea de comandos |
| `409 ... already declared` | La sala existe y pertenece a otro usuario: elija otro id |

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

Si. Cada vez que se hace clic en "Exportar paquete", se crea un nuevo bundle y se agrega a la cola. Se pueden encolar multiples bundles y se subiran secuencialmente.

### Como se si mis datos se han sincronizado?

Comprobar el indicador de **ultima sincronizacion** en el panel para el resultado mas reciente. Tambien se puede abrir el dialogo **Cola...** para ver el estado de cada bundle individual.

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
