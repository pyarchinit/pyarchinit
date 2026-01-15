# Tutorial 23: Ricerca Immagini

## Introduzione

La funzione **Ricerca Immagini** permette di cercare rapidamente immagini nel database PyArchInit filtrando per sito, tipo di entita e altri criteri. E uno strumento complementare al Media Manager per la ricerca globale.

## Accesso

### Dal Menu
**PyArchInit** → **Ricerca Immagini**

## Interfaccia

### Pannello di Ricerca

```
+--------------------------------------------------+
|           Ricerca Immagini                        |
+--------------------------------------------------+
| Filtri:                                           |
|   Sito: [ComboBox]                               |
|   Tipo Entita: [-- Tutti -- | US | Pottery | ...]|
|   [ ] Solo immagini non taggate                  |
+--------------------------------------------------+
| [Cerca]  [Pulisci]                               |
+--------------------------------------------------+
| Risultati:                                        |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Apri Immagine] [Esporta] [Vai al Record]        |
+--------------------------------------------------+
```

### Filtri Disponibili

| Filtro | Descrizione |
|--------|-------------|
| Sito | Seleziona sito specifico o tutti |
| Tipo Entita | US, Pottery, Materiali, Tomba, Struttura, UT |
| Solo non taggate | Mostra solo immagini senza collegamenti |

### Tipi di Entita

| Tipo | Descrizione |
|------|-------------|
| -- Tutti -- | Tutte le entita |
| US | Unita Stratigrafiche |
| Pottery | Ceramica |
| Materiali | Reperti/Inventario |
| Tomba | Sepolture |
| Struttura | Strutture |
| UT | Unita Topografiche |

## Funzionalita

### Ricerca Base

1. Selezionare i filtri desiderati
2. Cliccare **"Cerca"**
3. Visualizzare i risultati nella griglia

### Azioni sui Risultati

| Pulsante | Funzione |
|----------|----------|
| Apri Immagine | Visualizza immagine a dimensione originale |
| Esporta | Esporta immagine selezionata |
| Vai al Record | Apre la scheda dell'entita collegata |
| Apri Media Manager | Apre il Media Manager con l'immagine selezionata |

### Menu Contestuale (Right-click)

- **Apri immagine**
- **Esporta immagine...**
- **Vai al record**

### Ricerca Immagini Non Taggate

Checkbox **"Solo immagini non taggate"**:
- Trova immagini nel database senza collegamenti
- Utile per pulizia e organizzazione
- Permette di identificare immagini da catalogare

## Workflow Tipico

### 1. Trovare Immagini di un Sito

```
1. Selezionare sito dal ComboBox
2. Lasciare "-- Tutti --" per tipo entita
3. Cliccare Cerca
4. Sfogliare risultati
```

### 2. Trovare Immagini US Specifiche

```
1. Selezionare sito
2. Selezionare "US" come tipo entita
3. Cliccare Cerca
4. Double-click per aprire immagine
```

### 3. Identificare Immagini Non Catalogate

```
1. Selezionare sito (o tutti)
2. Attivare "Solo immagini non taggate"
3. Cliccare Cerca
4. Per ogni risultato:
   - Aprire immagine
   - Identificare contenuto
   - Collegare tramite Media Manager
```

## Esportazione

### Export Singola Immagine

1. Selezionare immagine nei risultati
2. Cliccare **"Esporta"** o menu contestuale
3. Selezionare destinazione
4. Salvare

### Export Multiplo

Per export di piu immagini, usare la funzione **Esporta Immagini** dedicata (Tutorial 24).

## Best Practices

### 1. Ricerca Efficiente

- Usare filtri specifici per risultati mirati
- Iniziare con filtri ampi, poi restringere
- Usare la ricerca non taggate periodicamente

### 2. Organizzazione

- Catalogare immagini non taggate regolarmente
- Verificare collegamenti dopo import
- Mantenere naming consistente

## Risoluzione Problemi

### Nessun Risultato

**Cause**:
- Filtri troppo restrittivi
- Nessuna immagine per i criteri

**Soluzioni**:
- Ampliare i filtri
- Verificare esistenza dati

### Immagine Non Visualizzabile

**Cause**:
- File non trovato
- Formato non supportato

**Soluzioni**:
- Verificare percorso file
- Controllare formato immagine

## Riferimenti

### File Sorgente
- `tabs/Image_search.py` - Interfaccia ricerca
- `gui/ui/pyarchinit_image_search_dialog.ui` - Layout UI

### Database
- `media_table` - Dati media
- `media_to_entity_table` - Collegamenti

---

## Video Tutorial

### Ricerca Immagini
`[Placeholder: video_ricerca_immagini.mp4]`

**Contenuti**:
- Utilizzo filtri
- Ricerca avanzata
- Export risultati

**Durata prevista**: 8-10 minuti

---

*Ultimo aggiornamento: Gennaio 2026*
