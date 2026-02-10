# Tutorial 29: Make Your Map

## Introduzione

**Make Your Map** e la funzione di PyArchInit per generare mappe e layout di stampa professionali direttamente dalla visualizzazione corrente di QGIS. Utilizza i template di layout predefiniti per creare output cartografici standardizzati.

### Funzionalita

- Generazione rapida di mappe da vista corrente
- Template predefiniti per diversi formati
- Personalizzazione intestazioni e legende
- Export in PDF, PNG, SVG

## Accesso

### Dalla Toolbar
Icona **"Make your Map"** (stampante) nella toolbar PyArchInit

### Dal Menu
**PyArchInit** → **Make your Map**

## Utilizzo Base

### Generazione Rapida

1. Configurare la vista mappa desiderata in QGIS
2. Impostare zoom e estensione corretti
3. Cliccare **"Make your Map"**
4. Selezionare template desiderato
5. Inserire titolo e informazioni
6. Generare mappa

## Template Disponibili

### Formati Standard

| Template | Formato | Orientamento | Utilizzo |
|----------|---------|--------------|----------|
| A4 Portrait | A4 | Verticale | Documentazione standard |
| A4 Landscape | A4 | Orizzontale | Viste estese |
| A3 Portrait | A3 | Verticale | Tavole dettagliate |
| A3 Landscape | A3 | Orizzontale | Planimetrie |

### Elementi Template

Ogni template include:
- **Area mappa** - Vista principale
- **Intestazione** - Titolo e informazioni progetto
- **Scala** - Barra di scala grafica
- **Nord** - Freccia del nord
- **Legenda** - Simboli layer
- **Cartiglio** - Informazioni tecniche

## Personalizzazione

### Informazioni Inseribili

| Campo | Descrizione |
|-------|-------------|
| Titolo | Nome della mappa |
| Sottotitolo | Descrizione aggiuntiva |
| Sito | Nome sito archeologico |
| Area | Numero area |
| Data | Data creazione |
| Autore | Nome autore |
| Scala | Scala di rappresentazione |

### Stile Mappa

Prima di generare:
1. Configurare stili layer in QGIS
2. Attivare/disattivare layer desiderati
3. Impostare etichette
4. Verificare legenda

## Export

### Formati Disponibili

| Formato | Utilizzo | Qualita |
|---------|----------|---------|
| PDF | Stampa, archivio | Vettoriale |
| PNG | Web, presentazioni | Raster |
| SVG | Editing, pubblicazione | Vettoriale |
| JPG | Web, preview | Raster compresso |

### Risoluzione

| DPI | Utilizzo |
|-----|----------|
| 96 | Screen/preview |
| 150 | Web publishing |
| 300 | Stampa standard |
| 600 | Stampa alta qualita |

## Integrazione Time Manager

### Generazione Sequenza

In combinazione con Time Manager:
1. Configurare Time Manager
2. Per ogni livello stratigrafico:
   - Impostare livello
   - Generare mappa
   - Salvare con nome progressivo

### Output Animazione

Serie di mappe per:
- Presentazioni
- Video time-lapse
- Documentazione progressiva

## Workflow Tipico

### 1. Preparazione

```
1. Caricare layer necessari
2. Configurare stili appropriati
3. Impostare sistema riferimento
4. Definire estensione mappa
```

### 2. Configurazione Vista

```
1. Zoomare sull'area di interesse
2. Attivare/disattivare layer
3. Verificare etichette
4. Controllare legenda
```

### 3. Generazione

```
1. Cliccare Make your Map
2. Selezionare template
3. Compilare informazioni
4. Scegliere formato export
5. Salvare
```

## Best Practices

### 1. Prima della Generazione

- Verificare completezza dati
- Controllare stili layer
- Impostare scala appropriata

### 2. Template

- Usare template consistenti nel progetto
- Personalizzare intestazioni per istituzione
- Mantenere standard cartografici

### 3. Output

- Salvare in alta risoluzione per stampa
- Mantenere copia PDF per archivio
- Usare naming descrittivo

## Personalizzazione Template

### Modifica Template

I template QGIS possono essere modificati:
1. Aprire Layout Manager in QGIS
2. Modificare template esistente
3. Salvare come nuovo template
4. Disponibile in Make your Map

### Creazione Template

1. Creare nuovo layout in QGIS
2. Aggiungere elementi necessari
3. Configurare variabili per campi dinamici
4. Salvare nella cartella templates

## Risoluzione Problemi

### Mappa Vuota

**Cause**:
- Nessun layer attivo
- Estensione errata

**Soluzioni**:
- Attivare layer visibili
- Zoomare sull'area con dati

### Legenda Incompleta

**Causa**: Layer non configurati correttamente

**Soluzione**: Verificare proprieta layer in QGIS

### Export Fallito

**Cause**:
- Percorso non scrivibile
- Formato non supportato

**Soluzioni**:
- Verificare permessi cartella
- Scegliere formato diverso

## Riferimenti

### File Sorgente
- `pyarchinitPlugin.py` - Funzione runPrint
- Template nella cartella `resources/templates/`

### QGIS
- Layout Manager
- Print Composer

---

## Video Tutorial

### Make Your Map
`[Placeholder: video_make_map.mp4]`

**Contenuti**:
- Preparazione vista
- Utilizzo template
- Personalizzazione
- Export formati

**Durata prevista**: 10-12 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../animations/pyarchinit_create_map_animation.html)
