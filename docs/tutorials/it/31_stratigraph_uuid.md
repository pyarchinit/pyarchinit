# PyArchInit - StratiGraph: Identificatori UUID

## Indice
1. [Introduzione](#introduzione)
2. [Cosa sono gli UUID](#cosa-sono-gli-uuid)
3. [Perche servono gli UUID in StratiGraph](#perche-servono-gli-uuid-in-stratigraph)
4. [Come funzionano in PyArchInit](#come-funzionano-in-pyarchinit)
5. [Tabelle con UUID](#tabelle-con-uuid)
6. [Domande Frequenti](#domande-frequenti)

---

## Introduzione

A partire dalla versione **5.0.1-alpha**, PyArchInit integra un sistema di **identificatori universali (UUID)** per tutte le entita archeologiche. Questa funzionalita fa parte del progetto europeo **StratiGraph** (Horizon Europe) e garantisce che ogni record nel database abbia un identificatore stabile e unico a livello globale.

<!-- VIDEO: Introduzione agli UUID in StratiGraph -->
> **Video Tutorial**: [Inserire link video introduzione UUID]

---

## Cosa sono gli UUID

Un **UUID** (Universally Unique Identifier) e un codice alfanumerico di 128 bit che identifica in modo univoco un'entita. PyArchInit utilizza la versione 4 (UUID v4), generata in modo casuale.

### Esempio di UUID

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### Caratteristiche degli UUID

| Caratteristica | Descrizione |
|---------------|-------------|
| **Formato** | 32 caratteri esadecimali separati da trattini (8-4-4-4-12) |
| **Unicita** | La probabilita di collisione e statisticamente trascurabile (~1 su 2^122) |
| **Indipendenza** | Non dipende dal database, dal server o dal momento di creazione |
| **Persistenza** | Una volta assegnato, non cambia mai |
| **Versione** | UUID v4 (generato casualmente) |

### Differenza con gli ID tradizionali

| Tipo ID | Esempio | Stabile tra DB? | Unico globalmente? |
|---------|---------|-----------------|---------------------|
| Auto-increment (id_us) | `1`, `2`, `3`... | No | No |
| Vincolo composito | `Sito1-Area1-US100` | Si (semantico) | Dipende |
| **UUID** | `a3f7b2c1-8d4e-...` | **Si** | **Si** |

Gli ID auto-incrementali (`id_us`, `id_invmat`, ecc.) cambiano quando si copia un database o si importano dati. Gli UUID invece restano **sempre gli stessi**, indipendentemente da dove si trovano i dati.

---

## Perche servono gli UUID in StratiGraph

Il progetto StratiGraph richiede che i dati archeologici possano essere:

### 1. Esportati verso il Knowledge Graph

I dati di PyArchInit vengono esportati come **bundle** (pacchetti strutturati) verso un Knowledge Graph centrale. Ogni entita deve avere un identificatore stabile per essere riconosciuta nel grafo.

```
Entita locale (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     US 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Sincronizzati tra dispositivi

Quando si lavora sul campo senza connessione internet, i dati vengono salvati localmente. Al ritorno della connessione, i dati vengono sincronizzati. Gli UUID garantiscono che lo stesso record venga riconosciuto e aggiornato (non duplicato).

### 3. Mappati verso CIDOC-CRM

L'ontologia CIDOC-CRM richiede **URI persistenti** per ogni entita. Gli UUID vengono usati per costruire queste URI:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Tracciati nel tempo

Ogni modifica, export o sincronizzazione fa riferimento allo stesso UUID. Questo permette di:
- Ricostruire la storia di un record
- Verificare la provenienza dei dati
- Collegare dati tra progetti diversi

---

## Come funzionano in PyArchInit

### Generazione automatica

Gli UUID vengono generati **automaticamente** in due momenti:

| Momento | Descrizione |
|---------|-------------|
| **Creazione nuovo record** | Quando si inserisce un nuovo record (es. nuova US), viene generato automaticamente un UUID v4 |
| **Migrazione database esistente** | Al primo avvio dopo l'aggiornamento, tutti i record esistenti senza UUID ricevono un UUID generato |

L'utente **non deve fare nulla**: gli UUID vengono gestiti interamente dal sistema.

### Dove si trova l'UUID

Ogni tabella principale del database ha una colonna `entity_uuid` di tipo TEXT. Il campo e visibile nel database ma non appare nelle schede di compilazione, poiche e gestito internamente.

### Migrazione automatica

Quando si aggiorna PyArchInit alla versione 5.0.1-alpha (o successiva):

1. **Al primo avvio**, il sistema verifica se le tabelle hanno la colonna `entity_uuid`
2. Se manca, la colonna viene **aggiunta automaticamente**
3. I record esistenti che non hanno UUID ricevono un **UUID generato**
4. Questa operazione avviene **una sola volta** per sessione QGIS

Il processo e trasparente e non richiede intervento manuale. Funziona sia con **PostgreSQL** che con **SQLite**.

---

## Tabelle con UUID

La colonna `entity_uuid` e presente nelle seguenti 19 tabelle:

| Tabella | Contenuto |
|---------|-----------|
| `site_table` | Siti archeologici |
| `us_table` | Unita Stratigrafiche (US/USM) |
| `inventario_materiali_table` | Inventario reperti |
| `tomba_table` | Tombe |
| `periodizzazione_table` | Periodizzazione e fasi |
| `struttura_table` | Strutture |
| `campioni_table` | Campioni |
| `individui_table` | Individui antropologici |
| `pottery_table` | Ceramica |
| `media_table` | File media |
| `media_thumb_table` | Miniature media |
| `media_to_entity_table` | Relazioni media-entita |
| `fauna_table` | Dati archeozoologici (Fauna) |
| `ut_table` | Unita Topografiche |
| `tma_materiali_archeologici` | TMA Materiali Archeologici |
| `tma_materiali_ripetibili` | TMA Materiali Ripetibili |
| `archeozoology_table` | Archeozoologia |
| `documentazione_table` | Documentazione |
| `inventario_lapidei_table` | Inventario Lapidei |

---

## Domande Frequenti

### Devo inserire manualmente gli UUID?

**No.** Gli UUID vengono generati automaticamente dal sistema. Non e necessario (ne consigliato) modificarli manualmente.

### Cosa succede se copio il database?

Gli UUID vengono copiati insieme al database. Questo e il comportamento desiderato: lo stesso record mantiene lo stesso UUID anche su copie diverse del database.

### Posso vedere gli UUID nelle schede?

Al momento gli UUID non sono visibili nelle schede di compilazione. Sono visibili direttamente nel database (es. tramite DB Manager in QGIS) nella colonna `entity_uuid` di ogni tabella.

### Gli UUID rallentano il database?

No. L'UUID e un semplice campo TEXT e non ha impatto significativo sulle performance del database.

### Cosa succede ai database esistenti?

I database esistenti vengono aggiornati automaticamente al primo avvio: la colonna `entity_uuid` viene aggiunta e tutti i record esistenti ricevono un UUID generato.

### Gli UUID funzionano sia con PostgreSQL che con SQLite?

Si. Il sistema e compatibile con entrambi i tipi di database supportati da PyArchInit.

---

*Documentazione PyArchInit - StratiGraph UUID*
*Versione: 5.0.1-alpha*
*Ultimo aggiornamento: Febbraio 2026*
