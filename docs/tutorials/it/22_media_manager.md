# Tutorial 22: Media Manager

## Introduzione

Il **Media Manager** e lo strumento centrale di PyArchInit per la gestione delle immagini e dei contenuti multimediali associati ai record archeologici. Permette di collegare foto, disegni, video e altri media a US, reperti, tombe, strutture e altre entita.

### Funzionalita Principali

- Gestione centralizzata di tutti i media
- Collegamento a entita archeologiche (US, Reperti, Pottery, Tombe, Strutture, UT)
- Visualizzazione thumbnail e immagini a grandezza originale
- Tagging e categorizzazione
- Ricerca avanzata
- Integrazione con GPT per analisi immagini

## Accesso

### Dal Menu
**PyArchInit** → **Media Manager**

### Dalla Toolbar
Icona **Media Manager** nella toolbar PyArchInit

## Interfaccia

### Pannello Principale

```
+----------------------------------------------------------+
|                    Media Manager                          |
+----------------------------------------------------------+
| Sito: [ComboBox]  Area: [ComboBox]  US: [ComboBox]       |
+----------------------------------------------------------+
| [Griglia Thumbnail Immagini]                              |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Tags: [Lista tag associati]                               |
+----------------------------------------------------------+
| [Navigazione] << < Record X di Y > >>                     |
+----------------------------------------------------------+
```

### Filtri di Ricerca

| Campo | Descrizione |
|-------|-------------|
| Sito | Filtra per sito archeologico |
| Area | Filtra per area di scavo |
| US | Filtra per Unita Stratigrafica |
| Sigla Struttura | Filtra per sigla struttura |
| Nr. Struttura | Filtra per numero struttura |

### Controlli Thumbnail

| Controllo | Funzione |
|-----------|----------|
| Slider dimensione | Regola grandezza thumbnail |
| Double-click | Apre immagine a dimensione originale |
| Selezione multipla | Ctrl+click per selezionare piu immagini |

## Gestione Media

### Aggiungere Nuove Immagini

1. Aprire Media Manager
2. Selezionare il sito di destinazione
3. Cliccare **"Nuovo Record"** o usare il menu contestuale
4. Selezionare le immagini da aggiungere
5. Compilare i metadati

### Collegare Media a Entita

1. Selezionare l'immagine nella griglia
2. Nel pannello Tags, selezionare:
   - **Tipo entita**: US, Reperto, Pottery, Tomba, Struttura, UT
   - **Identificativo**: Numero/codice dell'entita
3. Cliccare **"Collega"**

### Tipi di Entita Supportate

| Tipo | Tabella DB | Descrizione |
|------|------------|-------------|
| US | us_table | Unita Stratigrafiche |
| REPERTO | inventario_materiali_table | Reperti/Materiali |
| CERAMICA | pottery_table | Ceramica |
| TOMBA | tomba_table | Sepolture |
| STRUTTURA | struttura_table | Strutture |
| UT | ut_table | Unita Topografiche |

### Visualizzare Immagine Originale

- **Double-click** su thumbnail
- Si apre viewer con:
  - Zoom (rotella mouse)
  - Pan (trascinamento)
  - Rotazione
  - Misurazione

## Funzionalita Avanzate

### Ricerca Avanzata

Il Media Manager supporta ricerca per:
- Nome file
- Data inserimento
- Entita collegata
- Tag/categorie

### Integrazione GPT

Pulsante **"GPT Sketch"** per:
- Analisi automatica dell'immagine
- Generazione descrizione
- Suggerimenti di classificazione

### Caricamento Remoto

Supporto per immagini su server remoti:
- URL diretti
- Server FTP
- Cloud storage

## Database

### Tabelle Coinvolte

| Tabella | Descrizione |
|---------|-------------|
| `media_table` | Metadati media |
| `media_thumb_table` | Thumbnail |
| `media_to_entity_table` | Collegamenti entita |

### Mapper Classes

- `MEDIA` - Entita media principale
- `MEDIA_THUMB` - Thumbnail
- `MEDIATOENTITY` - Relazione media-entita

## Best Practices

### 1. Organizzazione File

- Usare nomi file descrittivi
- Organizzare per sito/area/anno
- Mantenere backup originali

### 2. Metadati

- Compilare sempre sito e area
- Aggiungere descrizioni significative
- Usare tag consistenti

### 3. Qualita Immagini

- Risoluzione minima consigliata: 1920x1080
- Formato: JPG per foto, PNG per disegni
- Compressione moderata

### 4. Collegamenti

- Collegare ogni immagine alle entita pertinenti
- Verificare collegamenti dopo import massivo
- Usare la ricerca per immagini non collegate

## Risoluzione Problemi

### Thumbnail Non Visualizzate

**Cause**:
- Percorso immagine errato
- File mancante
- Problemi di permessi

**Soluzioni**:
- Verificare percorso in database
- Controllare esistenza file
- Verificare permessi cartella

### Immagine Non Collegabile

**Cause**:
- Entita non esistente
- Tipo entita errato

**Soluzioni**:
- Verificare esistenza record
- Controllare tipo entita selezionato

## Riferimenti

### File Sorgente
- `tabs/Image_viewer.py` - Interfaccia principale
- `modules/utility/pyarchinit_media_utility.py` - Utility media

### Database
- `media_table` - Dati media
- `media_to_entity_table` - Collegamenti

---

## Video Tutorial

### Media Manager Completo
`[Placeholder: video_media_manager.mp4]`

**Contenuti**:
- Aggiunta immagini
- Collegamento a entita
- Ricerca e filtri
- Funzionalita avanzate

**Durata prevista**: 15-18 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../pyarchinit_media_manager_animation.html)
