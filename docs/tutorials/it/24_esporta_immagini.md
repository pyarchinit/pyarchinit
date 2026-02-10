# Tutorial 24: Esporta Immagini

## Introduzione

La funzione **Esporta Immagini** permette di esportare in massa le immagini associate ai record archeologici, organizzandole automaticamente in cartelle per periodo, fase, tipo di entita.

## Accesso

### Dal Menu
**PyArchInit** → **Esporta Immagini**

## Interfaccia

### Pannello Export

```
+--------------------------------------------------+
|           Esporta Immagini                        |
+--------------------------------------------------+
| Sito: [ComboBox selezione sito]                  |
| Anno: [ComboBox anno scavo]                      |
+--------------------------------------------------+
| Tipo Export:                                      |
|   [o] Tutte le immagini                          |
|   [ ] Solo US                                    |
|   [ ] Solo Reperti                               |
|   [ ] Solo Pottery                               |
+--------------------------------------------------+
| [Apri Cartella]           [Esporta]              |
+--------------------------------------------------+
```

### Opzioni Export

| Opzione | Descrizione |
|---------|-------------|
| Tutte le immagini | Esporta tutto il materiale fotografico |
| Solo US | Esporta solo immagini collegate a US |
| Solo Reperti | Esporta solo immagini dei reperti |
| Solo Pottery | Esporta solo immagini ceramica |

## Struttura Output

### Organizzazione Cartelle

L'export crea una struttura gerarchica:

```
pyarchinit_image_export/
└── [Nome Sito] - Tutte le immagini/
    ├── Periodo - 1/
    │   ├── Fase - 1/
    │   │   ├── US_001/
    │   │   │   ├── foto_001.jpg
    │   │   │   └── foto_002.jpg
    │   │   └── US_002/
    │   │       └── foto_003.jpg
    │   └── Fase - 2/
    │       └── US_003/
    │           └── foto_004.jpg
    └── Periodo - 2/
        └── ...
```

### Naming Convention

I file mantengono il nome originale, organizzati per:
1. **Periodo** - Periodo cronologico iniziale
2. **Fase** - Fase cronologica iniziale
3. **Entita** - US, Reperto, etc.

## Processo di Export

### Step 1: Selezione Parametri

1. Selezionare il **Sito** dal ComboBox
2. Selezionare l'**Anno** (opzionale)
3. Scegliere il **Tipo di export**

### Step 2: Esecuzione

1. Cliccare **"Esporta"**
2. Attendere completamento
3. Messaggio di conferma

### Step 3: Verifica

1. Cliccare **"Apri Cartella"**
2. Verificare struttura creata
3. Controllare completezza

## Cartella di Output

### Percorso Standard

```
~/pyarchinit/pyarchinit_image_export/
```

### Contenuto

- Cartelle organizzate per sito
- Sottocartelle per periodo/fase
- Immagini originali (non ridimensionate)

## Filtro per Anno

Il ComboBox **Anno** permette di:
- Esportare solo immagini di una campagna specifica
- Organizzare export per anno di scavo
- Ridurre dimensione export

## Best Practices

### 1. Prima dell'Export

- Verificare collegamenti immagini-entita
- Controllare periodizzazione US
- Assicurarsi spazio disco sufficiente

### 2. Durante l'Export

- Non interrompere il processo
- Attendere messaggio completamento

### 3. Dopo l'Export

- Verificare struttura cartelle
- Controllare completezza immagini
- Creare backup se necessario

## Utilizzi Tipici

### Preparazione Relazione

```
1. Selezionare sito
2. Esportare tutte le immagini
3. Utilizzare struttura per capitoli relazione
```

### Consegna Soprintendenza

```
1. Selezionare sito e anno
2. Esportare per tipologia richiesta
3. Organizzare secondo standard ministeriali
```

### Backup Campagna

```
1. A fine campagna, esportare tutto
2. Archiviare su storage esterno
3. Verificare integrita
```

## Risoluzione Problemi

### Export Incompleto

**Cause**:
- Immagini non collegate
- Percorsi file errati

**Soluzioni**:
- Verificare collegamenti in Media Manager
- Controllare esistenza file sorgente

### Struttura Non Corretta

**Cause**:
- Periodizzazione mancante
- US senza periodo/fase

**Soluzioni**:
- Compilare periodizzazione US
- Assegnare periodo/fase a tutte le US

## Riferimenti

### File Sorgente
- `tabs/Images_directory_export.py` - Interfaccia export
- `gui/ui/Images_directory_export.ui` - Layout UI

### Cartelle
- `~/pyarchinit/pyarchinit_image_export/` - Output export

---

## Video Tutorial

### Export Immagini
`[Placeholder: video_export_immagini.mp4]`

**Contenuti**:
- Configurazione export
- Struttura output
- Organizzazione archivio

**Durata prevista**: 10-12 minuti

---

*Ultimo aggiornamento: Gennaio 2026*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../../pyarchinit_image_export_animation.html)
