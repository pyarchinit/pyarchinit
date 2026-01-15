# Tutorial 10: Scheda Documentazione

## Introduzione

La **Scheda Documentazione** e il modulo di PyArchInit per la gestione della documentazione grafica di scavo: piante, sezioni, prospetti, rilievi e qualsiasi altro elaborato grafico prodotto durante le attivita archeologiche.

### Tipologie di Documentazione

- **Piante**: piante di strato, di fase, generali
- **Sezioni**: sezioni stratigrafiche
- **Prospetti**: alzati murari, fronti di scavo
- **Rilievi**: rilievi topografici, fotogrammetrici
- **Ortofoto**: elaborazioni da drone/fotogrammetria
- **Disegni di reperti**: ceramica, metalli, ecc.

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda Documentazione** (o **Documentation form**)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Documentazione**

---

## Panoramica dell'Interfaccia

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | DB Info | Stato record, ordinamento, contatore |
| 3 | Campi Identificativi | Sito, Nome, Data |
| 4 | Campi Tipologici | Tipo, Sorgente, Scala |
| 5 | Campi Descrittivi | Disegnatore, Note |

---

## Toolbar DBMS

### Pulsanti Standard

| Funzione | Descrizione |
|----------|-------------|
| First/Prev/Next/Last rec | Navigazione tra i record |
| New record | Crea nuovo record |
| Save | Salva le modifiche |
| Delete | Elimina il record |
| New search / Search | Funzioni di ricerca |
| Order by | Ordina risultati |
| View all | Visualizza tutti i record |

---

## Campi della Scheda

### Sito

**Campo**: `comboBox_sito_doc`
**Database**: `sito`

Sito archeologico di riferimento.

### Nome Documentazione

**Campo**: `lineEdit_nome_doc`
**Database**: `nome_doc`

Nome identificativo del documento.

**Convenzioni di nomenclatura:**
- `P` = Pianta (es. P001)
- `S` = Sezione (es. S001)
- `PR` = Prospetto (es. PR001)
- `R` = Rilievo (es. R001)

### Data

**Campo**: `dateEdit_data`
**Database**: `data`

Data di esecuzione del disegno/rilievo.

### Tipo Documentazione

**Campo**: `comboBox_tipo_doc`
**Database**: `tipo_documentazione`

Tipologia del documento.

**Valori tipici:**
| Tipo | Descrizione |
|------|-------------|
| Pianta di strato | Singola US |
| Pianta di fase | Piu US coeve |
| Pianta generale | Vista d'insieme |
| Sezione stratigrafica | Profilo verticale |
| Prospetto | Alzato murario |
| Rilievo topografico | Planimetria generale |
| Ortofoto | Da fotogrammetria |
| Disegno reperto | Ceramica, metallo, ecc. |

### Sorgente

**Campo**: `comboBox_sorgente`
**Database**: `sorgente`

Fonte/metodo di produzione.

**Valori:**
- Rilievo diretto
- Fotogrammetria
- Laser scanner
- GPS/Stazione totale
- Digitalizzazione CAD
- Ortofoto drone

### Scala

**Campo**: `comboBox_scala`
**Database**: `scala`

Scala di rappresentazione.

**Scale comuni:**
| Scala | Uso tipico |
|-------|-----------|
| 1:1 | Disegni reperti |
| 1:5 | Dettagli |
| 1:10 | Sezioni, dettagli |
| 1:20 | Piante di strato |
| 1:50 | Piante generali |
| 1:100 | Planimetrie |
| 1:200+ | Carte topografiche |

### Disegnatore

**Campo**: `comboBox_disegnatore`
**Database**: `disegnatore`

Autore del disegno/rilievo.

### Note

**Campo**: `textEdit_note`
**Database**: `note`

Note aggiuntive sul documento.

---

## Workflow Operativo

### Registrazione Nuova Documentazione

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"

3. **Dati identificativi**
   ```
   Sito: Villa Romana di Settefinestre
   Nome: P025
   Data: 15/06/2024
   ```

4. **Classificazione**
   ```
   Tipo: Pianta di strato
   Sorgente: Rilievo diretto
   Scala: 1:20
   ```

5. **Autore e note**
   ```
   Disegnatore: M. Rossi
   Note: Pianta US 150. Evidenzia
   limiti del battuto pavimentale.
   ```

6. **Salvataggio**
   - Click su "Save"

### Ricerca Documentazione

1. Click su "New Search"
2. Compilare criteri:
   - Sito
   - Tipo documentazione
   - Scala
   - Disegnatore
3. Click su "Search"
4. Navigare tra i risultati

---

## Export PDF

La scheda supporta l'esportazione in PDF per:
- Elenco documentazione
- Schede dettagliate

---

## Best Practices

### Nomenclatura

- Usare codici coerenti in tutto il progetto
- Numerazione progressiva per tipo
- Documentare le convenzioni adottate

### Organizzazione

- Collegare sempre al sito di riferimento
- Indicare la scala effettiva
- Registrare data e autore

### Archiviazione

- Collegare i file digitali tramite la gestione media
- Mantenere copie di backup
- Usare formati standard (PDF, TIFF)

---

## Troubleshooting

### Problema: Tipo documentazione non disponibile

**Causa**: Thesaurus non configurato.

**Soluzione**:
1. Aprire la Scheda Thesaurus
2. Aggiungere i tipi mancanti per `documentazione_table`

### Problema: File non visualizzato

**Causa**: Percorso non corretto o file mancante.

**Soluzione**:
1. Verificare che il file esista
2. Controllare il percorso nella configurazione media

---

## Riferimenti

### Database

- **Tabella**: `documentazione_table`
- **Classe mapper**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### File Sorgente

- **UI**: `gui/ui/Documentazione.ui`
- **Controller**: `tabs/Documentazione.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Video Tutorial

### Gestione Documentazione Grafica
**Durata**: 6-8 minuti
- Registrazione nuova documentazione
- Classificazione e metadati
- Ricerca e consultazione

[Placeholder video: video_documentazione.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
