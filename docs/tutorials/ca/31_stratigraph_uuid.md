# PyArchInit - StratiGraph: Identificadors UUID

## Index
1. [Introduccio](#introduccio)
2. [Que son els UUID](#que-son-els-uuid)
3. [Per que serveixen els UUID a StratiGraph](#per-que-serveixen-els-uuid-a-stratigraph)
4. [Com funcionen a PyArchInit](#com-funcionen-a-pyarchinit)
5. [Taules amb UUID](#taules-amb-uuid)
6. [Preguntes Frequents](#preguntes-frequents)

---

## Introduccio

A partir de la versio **5.0.1-alpha**, PyArchInit integra un sistema **d'identificadors universals (UUID)** per a totes les entitats arqueologiques. Aquesta funcionalitat forma part del projecte europeu **StratiGraph** (Horizon Europe) i garanteix que cada registre a la base de dades tingui un identificador estable i unic a nivell global.

<!-- VIDEO: Introduccio als UUID a StratiGraph -->
> **Video Tutorial**: [Inserir enllaç video introduccio UUID]

---

## Que son els UUID

Un **UUID** (Universally Unique Identifier) es un codi alfanumeric de 128 bits que identifica de manera unica una entitat. PyArchInit utilitza la versio 4 (UUID v4), generada de manera aleatoria.

### Exemple d'UUID

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### Caracteristiques dels UUID

| Caracteristica | Descripcio |
|---------------|------------|
| **Format** | 32 caracters hexadecimals separats per guions (8-4-4-4-12) |
| **Unicitat** | La probabilitat de col·lisio es estadisticament negligible (~1 sobre 2^122) |
| **Independencia** | No depen de la base de dades, del servidor o del moment de creacio |
| **Persistencia** | Un cop assignat, no canvia mai |
| **Versio** | UUID v4 (generat aleatoriament) |

### Diferencia amb els ID tradicionals

| Tipus ID | Exemple | Estable entre BD? | Unic globalment? |
|----------|---------|-------------------|------------------|
| Auto-increment (id_us) | `1`, `2`, `3`... | No | No |
| Restriccio composta | `Lloc1-Area1-UE100` | Si (semantic) | Depen |
| **UUID** | `a3f7b2c1-8d4e-...` | **Si** | **Si** |

Els ID auto-incrementals (`id_us`, `id_invmat`, etc.) canvien quan es copia una base de dades o s'importen dades. Els UUID, en canvi, resten **sempre els mateixos**, independentment d'on es trobin les dades.

---

## Per que serveixen els UUID a StratiGraph

El projecte StratiGraph requereix que les dades arqueologiques puguin ser:

### 1. Exportades cap al Knowledge Graph

Les dades de PyArchInit s'exporten com a **bundles** (paquets estructurats) cap a un Knowledge Graph central. Cada entitat ha de tenir un identificador estable per ser reconeguda al graf.

```
Entitat local (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     UE 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Sincronitzades entre dispositius

Quan es treballa al camp sense connexio a internet, les dades es guarden localment. En tornar la connexio, les dades es sincronitzen. Els UUID garanteixen que el mateix registre sigui reconegut i actualitzat (no duplicat).

### 3. Mapejades cap a CIDOC-CRM

L'ontologia CIDOC-CRM requereix **URI persistents** per a cada entitat. Els UUID s'utilitzen per construir aquests URI:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Traçades en el temps

Cada modificacio, exportacio o sincronitzacio fa referencia al mateix UUID. Aixo permet:
- Reconstruir la historia d'un registre
- Verificar la proveniencia de les dades
- Vincular dades entre projectes diferents

---

## Com funcionen a PyArchInit

### Generacio automatica

Els UUID es generen **automaticament** en dos moments:

| Moment | Descripcio |
|--------|------------|
| **Creacio nou registre** | Quan s'insereix un nou registre (ex. nova UE), es genera automaticament un UUID v4 |
| **Migracio base de dades existent** | Al primer inici despres de l'actualitzacio, tots els registres existents sense UUID reben un UUID generat |

L'usuari **no ha de fer res**: els UUID es gestionen enterament pel sistema.

### On es troba l'UUID

Cada taula principal de la base de dades te una columna `entity_uuid` de tipus TEXT. El camp es visible a la base de dades pero no apareix a les fitxes de compilacio, ja que es gestionat internament.

### Migracio automatica

Quan s'actualitza PyArchInit a la versio 5.0.1-alpha (o posterior):

1. **Al primer inici**, el sistema verifica si les taules tenen la columna `entity_uuid`
2. Si falta, la columna s'**afegeix automaticament**
3. Els registres existents sense UUID reben un **UUID generat**
4. Aquesta operacio succeeix **nomes un cop** per sessio QGIS

El proces es transparent i no requereix intervencio manual. Funciona tant amb **PostgreSQL** com amb **SQLite**.

---

## Taules amb UUID

La columna `entity_uuid` es present a les seguents 19 taules:

| Taula | Contingut |
|-------|-----------|
| `site_table` | Jaciments arqueologics |
| `us_table` | Unitats Estratigrafiques (UE/UEM) |
| `inventario_materiali_table` | Inventari de materials |
| `tomba_table` | Sepultures |
| `periodizzazione_table` | Perioditzacio i fases |
| `struttura_table` | Estructures |
| `campioni_table` | Mostres |
| `individui_table` | Individus antropologics |
| `pottery_table` | Ceramica |
| `media_table` | Fitxers multimedia |
| `media_thumb_table` | Miniatures multimedia |
| `media_to_entity_table` | Relacions multimedia-entitat |
| `fauna_table` | Dades arqueozoologiques (Fauna) |
| `ut_table` | Unitats Topografiques |
| `tma_materiali_archeologici` | TMA Materials Arqueologics |
| `tma_materiali_ripetibili` | TMA Materials Repetibles |
| `archeozoology_table` | Arqueozoologia |
| `documentazione_table` | Documentacio |
| `inventario_lapidei_table` | Inventari Lapidari |

---

## Preguntes Frequents

### He d'introduir manualment els UUID?

**No.** Els UUID es generen automaticament pel sistema. No es necessari (ni recomanat) modificar-los manualment.

### Que passa si copio la base de dades?

Els UUID es copien juntament amb la base de dades. Aquest es el comportament desitjat: el mateix registre mante el mateix UUID fins i tot en copies diferents de la base de dades.

### Puc veure els UUID a les fitxes?

Actualment els UUID no son visibles a les fitxes de compilacio. Son visibles directament a la base de dades (ex. mitjanҫant DB Manager a QGIS) a la columna `entity_uuid` de cada taula.

### Els UUID alenteixen la base de dades?

No. L'UUID es un simple camp TEXT i no te impacte significatiu en el rendiment de la base de dades.

### Que passa amb les bases de dades existents?

Les bases de dades existents s'actualitzen automaticament al primer inici: la columna `entity_uuid` s'afegeix i tots els registres existents reben un UUID generat.

### Els UUID funcionen tant amb PostgreSQL com amb SQLite?

Si. El sistema es compatible amb els dos tipus de bases de dades suportats per PyArchInit.

---

*Documentacio PyArchInit - StratiGraph UUID*
*Versio: 5.0.1-alpha*
*Ultima actualitzacio: Febrer 2026*
