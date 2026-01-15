# Tutorial 27: TOPS - Total Open Station

## Introduzione

**TOPS** (Total Open Station) e l'integrazione di PyArchInit con il software open source per il download e la conversione di dati da stazioni totali. Permette di importare direttamente i rilievi topografici nel sistema PyArchInit.

### Cos'e Total Open Station?

Total Open Station e un software libero per:
- Download dati da stazioni totali
- Conversione tra formati
- Export in formati GIS-compatibili

PyArchInit integra TOPS per semplificare l'importazione dei dati di scavo.

## Accesso

### Dal Menu
**PyArchInit** → **TOPS (Total Open Station)**

## Interfaccia

### Pannello Principale

```
+--------------------------------------------------+
|         Total Open Station to PyArchInit          |
+--------------------------------------------------+
| Input:                                            |
|   File: [___________________] [Sfoglia]          |
|   Formato input: [ComboBox formati]              |
+--------------------------------------------------+
| Output:                                           |
|   File: [___________________] [Sfoglia]          |
|   Formato output: [csv | dxf | ...]              |
+--------------------------------------------------+
| [ ] Converti coordinate                          |
+--------------------------------------------------+
| [Anteprima Dati - TableView]                     |
+--------------------------------------------------+
|              [Esporta]                            |
+--------------------------------------------------+
```

## Formati Supportati

### Formati Input (Stazioni Totali)

| Formato | Produttore | Estensione |
|---------|------------|------------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| CSV generico | - | .csv |

### Formati Output

| Formato | Utilizzo |
|---------|----------|
| CSV | Import in PyArchInit Quote |
| DXF | Import in CAD/GIS |
| GeoJSON | Import diretto GIS |
| Shapefile | Standard GIS |

## Workflow

### 1. Import Dati da Stazione Totale

```
1. Collegare stazione totale al PC
2. Scaricare file dati (formato nativo)
3. Salvare in cartella di lavoro
```

### 2. Conversione con TOPS

```
1. Aprire TOPS in PyArchInit
2. Selezionare file input (Sfoglia)
3. Scegliere formato input corretto
4. Impostare file output
5. Scegliere formato output (CSV consigliato)
6. Cliccare Esporta
```

### 3. Import in PyArchInit

Dopo l'export in CSV:
1. Il sistema chiede automaticamente:
   - **Nome sito** archeologico
   - **Unita di misura** (metri)
   - **Nome disegnatore**
2. I punti vengono caricati come layer QGIS
3. Opzionale: copia in layer Quote US

### 4. Conversione Coordinate (Opzionale)

Se checkbox **"Converti coordinate"** attivo:
- Inserire offset X, Y, Z
- Applicare traslazione coordinate
- Utile per sistemi di riferimento locali

## Anteprima Dati

### TableView

Mostra anteprima dei dati importati:
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Modifica Dati

- Selezionare righe da eliminare
- Pulsante **Delete** rimuove righe selezionate
- Utile per filtrare punti non necessari

## Integrazione Quote US

### Copia Automatica

Dopo l'import, TOPS puo copiare i punti nel layer **"Quote US disegno"**:
1. Viene chiesto il nome del sito
2. Viene chiesta l'unita di misura
3. Viene chiesto il disegnatore
4. I punti vengono copiati con attributi corretti

### Attributi Compilati

| Attributo | Valore |
|-----------|--------|
| sito_q | Nome sito inserito |
| area_q | Estratto da point_name |
| unita_misu_q | Unita inserita (metri) |
| disegnatore | Nome inserito |
| data | Data corrente |

## Convenzioni Naming

### Formato point_name

Per l'estrazione automatica dell'area:
```
[AREA]-[NOME_PUNTO]
Esempio: 1000-P001
```

Il sistema separa automaticamente:
- `area_q` = 1000
- `point_name` = P001

## Best Practices

### 1. Sul Campo

- Usare naming consistente per punti
- Includere codice area nel nome punto
- Annotare sistema di riferimento usato

### 2. Import

- Verificare formato input corretto
- Controllare anteprima prima di export
- Eliminare punti errati/duplicati

### 3. Post-Import

- Verificare coordinate in QGIS
- Controllare layer Quote US
- Collegare punti a US corrette

## Risoluzione Problemi

### Formato Non Riconosciuto

**Causa**: Formato stazione non supportato

**Soluzione**:
- Esportare da stazione in formato generico (CSV)
- Verificare documentazione stazione

### Coordinate Errate

**Cause**:
- Sistema riferimento diverso
- Offset non applicato

**Soluzioni**:
- Verificare sistema riferimento progetto
- Applicare conversione coordinate

### Layer Non Creato

**Causa**: Errore durante import

**Soluzione**:
- Controllare log errori
- Verificare formato file output
- Ripetere conversione

## Riferimenti

### File Sorgente
- `tabs/tops_pyarchinit.py` - Interfaccia principale
- `gui/ui/Tops2pyarchinit.ui` - Layout UI

### Software Esterno
- [Total Open Station](https://tops.iosa.it/) - Software principale
- Documentazione formati stazioni

---

## Video Tutorial

### TOPS Import
`[Placeholder: video_tops.mp4]`

**Contenuti**:
- Download da stazione totale
- Conversione formati
- Import in PyArchInit
- Integrazione Quote US

**Durata prevista**: 12-15 minuti

---

*Ultimo aggiornamento: Gennaio 2026*
