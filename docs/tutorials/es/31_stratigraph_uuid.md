# PyArchInit - StratiGraph: Identificadores UUID

## Índice
1. [Introducción](#introducción)
2. [Qué son los UUID](#qué-son-los-uuid)
3. [Por qué se necesitan los UUID en StratiGraph](#por-qué-se-necesitan-los-uuid-en-stratigraph)
4. [Cómo funcionan en PyArchInit](#cómo-funcionan-en-pyarchinit)
5. [Tablas con UUID](#tablas-con-uuid)
6. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

A partir de la versión **5.0.1-alpha**, PyArchInit integra un sistema de **identificadores universales únicos (UUID)** para todas las entidades arqueológicas. Esta funcionalidad forma parte del proyecto europeo **StratiGraph** (Horizon Europe) y garantiza que cada registro en la base de datos tenga un identificador estable y único a nivel global.

<!-- VIDEO: Introducción a los UUID en StratiGraph -->
> **Video Tutorial**: [Insertar enlace video introducción UUID]

---

## Qué son los UUID

Un **UUID** (Universally Unique Identifier) es un código alfanumérico de 128 bits que identifica de manera única una entidad. PyArchInit utiliza la versión 4 (UUID v4), generada de forma aleatoria.

### Ejemplo de UUID

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### Características de los UUID

| Característica | Descripción |
|---------------|-------------|
| **Formato** | 32 caracteres hexadecimales separados por guiones (8-4-4-4-12) |
| **Unicidad** | La probabilidad de colisión es estadísticamente insignificante (~1 en 2^122) |
| **Independencia** | No depende de la base de datos, del servidor o del momento de creación |
| **Persistencia** | Una vez asignado, no cambia nunca |
| **Versión** | UUID v4 (generado aleatoriamente) |

### Diferencia con los IDs tradicionales

| Tipo ID | Ejemplo | ¿Estable entre BDs? | ¿Único globalmente? |
|---------|---------|-----------------|---------------------|
| Auto-incremental (id_us) | `1`, `2`, `3`... | No | No |
| Restricción compuesta | `Sitio1-Area1-UE100` | Sí (semántico) | Depende |
| **UUID** | `a3f7b2c1-8d4e-...` | **Sí** | **Sí** |

Los IDs auto-incrementales (`id_us`, `id_invmat`, etc.) cambian cuando se copia una base de datos o se importan datos. Los UUID en cambio permanecen **siempre iguales**, independientemente de dónde se encuentren los datos.

---

## Por qué se necesitan los UUID en StratiGraph

El proyecto StratiGraph requiere que los datos arqueológicos puedan ser:

### 1. Exportados hacia el Knowledge Graph

Los datos de PyArchInit se exportan como **bundles** (paquetes estructurados) hacia un Knowledge Graph central. Cada entidad debe tener un identificador estable para ser reconocida en el grafo.

```
Entidad local (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     UE 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Sincronizados entre dispositivos

Cuando se trabaja en campo sin conexión a internet, los datos se guardan localmente. Al regresar la conexión, los datos se sincronizan. Los UUID garantizan que el mismo registro sea reconocido y actualizado (no duplicado).

### 3. Mapeados hacia CIDOC-CRM

La ontología CIDOC-CRM requiere **URIs persistentes** para cada entidad. Los UUID se utilizan para construir estas URIs:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Rastreados en el tiempo

Cada modificación, exportación o sincronización hace referencia al mismo UUID. Esto permite:
- Reconstruir la historia de un registro
- Verificar la procedencia de los datos
- Conectar datos entre proyectos diferentes

---

## Cómo funcionan en PyArchInit

### Generación automática

Los UUID se generan **automáticamente** en dos momentos:

| Momento | Descripción |
|---------|-------------|
| **Creación de nuevo registro** | Cuando se inserta un nuevo registro (ej. nueva UE), se genera automáticamente un UUID v4 |
| **Migración de base de datos existente** | Al primer inicio después de la actualización, todos los registros existentes sin UUID reciben un UUID generado |

El usuario **no debe hacer nada**: los UUID son gestionados completamente por el sistema.

### Dónde se encuentra el UUID

Cada tabla principal de la base de datos tiene una columna `entity_uuid` de tipo TEXT. El campo es visible en la base de datos pero no aparece en las fichas de compilación, ya que es gestionado internamente.

### Migración automática

Al actualizar PyArchInit a la versión 5.0.1-alpha (o posterior):

1. **Al primer inicio**, el sistema verifica si las tablas tienen la columna `entity_uuid`
2. Si falta, la columna se **añade automáticamente**
3. Los registros existentes que no tienen UUID reciben un **UUID generado**
4. Esta operación ocurre **una sola vez** por sesión de QGIS

El proceso es transparente y no requiere intervención manual. Funciona tanto con **PostgreSQL** como con **SQLite**.

---

## Tablas con UUID

La columna `entity_uuid` está presente en las siguientes 19 tablas:

| Tabla | Contenido |
|---------|-----------|
| `site_table` | Sitios arqueológicos |
| `us_table` | Unidades Estratigráficas (UE/UEM) |
| `inventario_materiali_table` | Inventario de hallazgos |
| `tomba_table` | Tumbas |
| `periodizzazione_table` | Periodización y fases |
| `struttura_table` | Estructuras |
| `campioni_table` | Muestras |
| `individui_table` | Individuos antropológicos |
| `pottery_table` | Cerámica |
| `media_table` | Archivos multimedia |
| `media_thumb_table` | Miniaturas multimedia |
| `media_to_entity_table` | Relaciones multimedia-entidad |
| `fauna_table` | Datos arqueozoológicos (Fauna) |
| `ut_table` | Unidades Topográficas |
| `tma_materiali_archeologici` | TMA Materiales Arqueológicos |
| `tma_materiali_ripetibili` | TMA Materiales Repetibles |
| `archeozoology_table` | Arqueozoología |
| `documentazione_table` | Documentación |
| `inventario_lapidei_table` | Inventario Lítico |

---

## Preguntas Frecuentes

### ¿Debo insertar manualmente los UUID?

**No.** Los UUID son generados automáticamente por el sistema. No es necesario (ni recomendable) modificarlos manualmente.

### ¿Qué sucede si copio la base de datos?

Los UUID se copian junto con la base de datos. Este es el comportamiento deseado: el mismo registro mantiene el mismo UUID incluso en copias diferentes de la base de datos.

### ¿Puedo ver los UUID en las fichas?

Actualmente los UUID no son visibles en las fichas de compilación. Son visibles directamente en la base de datos (ej. mediante DB Manager en QGIS) en la columna `entity_uuid` de cada tabla.

### ¿Los UUID ralentizan la base de datos?

No. El UUID es un simple campo TEXT y no tiene impacto significativo en el rendimiento de la base de datos.

### ¿Qué sucede con las bases de datos existentes?

Las bases de datos existentes se actualizan automáticamente al primer inicio: la columna `entity_uuid` se añade y todos los registros existentes reciben un UUID generado.

### ¿Los UUID funcionan tanto con PostgreSQL como con SQLite?

Sí. El sistema es compatible con ambos tipos de base de datos soportados por PyArchInit.

---

*Documentación PyArchInit - StratiGraph UUID*
*Versión: 5.0.1-alpha*
*Última actualización: Febrero 2026*
