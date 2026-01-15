# Tutorial 09: Scheda Campioni

## Introduzione

La **Scheda Campioni** e il modulo di PyArchInit dedicato alla gestione delle campionature archeologiche. Permette di registrare e tracciare tutti i tipi di campioni prelevati durante lo scavo: terre, carbone, semi, ossa, malte, metalli e altro materiale destinato ad analisi specialistiche.

### Tipologie di Campioni

I campioni archeologici comprendono:
- **Sedimenti**: per analisi sedimentologiche, granulometriche
- **Carboni**: per datazioni radiometriche (C14)
- **Semi/Pollini**: per analisi archeobotaniche
- **Ossa**: per analisi archeozoologiche, isotopiche, DNA
- **Malte/Intonaci**: per analisi archeometriche
- **Metalli/Scorie**: per analisi metallurgiche
- **Ceramiche**: per analisi di impasto, provenienza

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda Campioni** (o **Samples form**)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Campioni**

---

## Panoramica dell'Interfaccia

La scheda presenta un layout semplificato per la gestione rapida dei campioni.

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | DB Info | Stato record, ordinamento, contatore |
| 3 | Campi Identificativi | Sito, Nr. Campione, Tipo |
| 4 | Campi Descrittivi | Descrizione, note |
| 5 | Campi di Conservazione | Cassa, Luogo |

---

## Toolbar DBMS

### Pulsanti di Navigazione

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| First rec | Vai al primo record |
| Prev rec | Vai al record precedente |
| Next rec | Vai al record successivo |
| Last rec | Vai all'ultimo record |

### Pulsanti CRUD

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| New record | Crea un nuovo record campione |
| Save | Salva le modifiche |
| Delete | Elimina il record corrente |

### Pulsanti di Ricerca

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| New search | Avvia nuova ricerca |
| Search!!! | Esegui ricerca |
| Order by | Ordina risultati |
| View all | Visualizza tutti i record |

---

## Campi della Scheda

### Sito

**Campo**: `comboBox_sito`
**Database**: `sito`

Seleziona il sito archeologico di appartenenza.

### Numero Campione

**Campo**: `lineEdit_nr_campione`
**Database**: `nr_campione`

Numero identificativo progressivo del campione.

### Tipo Campione

**Campo**: `comboBox_tipo_campione`
**Database**: `tipo_campione`

Classificazione tipologica del campione. I valori provengono dal thesaurus.

**Tipologie comuni:**
| Tipo | Descrizione |
|------|-------------|
| Sedimento | Campione di terra |
| Carbone | Per datazioni C14 |
| Semi | Resti carpologici |
| Ossa | Resti faunistici |
| Malta | Leganti edilizi |
| Ceramica | Per analisi impasto |
| Metallo | Per analisi metallurgiche |
| Polline | Per analisi palinologiche |

### Descrizione

**Campo**: `textEdit_descrizione`
**Database**: `descrizione`

Descrizione dettagliata del campione.

**Contenuti consigliati:**
- Caratteristiche fisiche del campione
- Quantita prelevata
- Modalita di prelievo
- Motivo del campionamento
- Analisi previste

### Area

**Campo**: `comboBox_area`
**Database**: `area`

Area di scavo di provenienza.

### US

**Campo**: `comboBox_us`
**Database**: `us`

Unita Stratigrafica di provenienza.

### Numero Inventario Materiale

**Campo**: `lineEdit_nr_inv_mat`
**Database**: `numero_inventario_materiale`

Se il campione e collegato a un reperto inventariato, indicare il numero di inventario.

### Numero Cassa

**Campo**: `lineEdit_nr_cassa`
**Database**: `nr_cassa`

Cassa o contenitore di conservazione.

### Luogo di Conservazione

**Campo**: `comboBox_luogo_conservazione`
**Database**: `luogo_conservazione`

Dove e conservato il campione.

**Esempi:**
- Laboratorio scavo
- Deposito museo
- Laboratorio analisi esterno
- Universita

---

## Workflow Operativo

### Creazione Nuovo Campione

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"

3. **Dati identificativi**
   ```
   Sito: Villa Romana di Settefinestre
   Nr. Campione: C-2024-001
   Tipo campione: Carbone
   ```

4. **Provenienza**
   ```
   Area: 1000
   US: 150
   ```

5. **Descrizione**
   ```
   Campione di carbone prelevato dalla
   superficie di concotto US 150.
   Quantita: 50 gr circa.
   Prelevato per datazione C14.
   ```

6. **Conservazione**
   ```
   Nr. Cassa: Camp-1
   Luogo: Laboratorio scavo
   ```

7. **Salvataggio**
   - Click su "Save"

### Ricerca Campioni

1. Click su "New Search"
2. Compilare criteri:
   - Sito
   - Tipo campione
   - US
3. Click su "Search"
4. Navigare tra i risultati

---

## Export PDF

La scheda supporta l'esportazione in PDF per:
- Elenco campioni
- Schede dettagliate singole

---

## Best Practices

### Nomenclatura

- Usare codici univoci e parlanti
- Formato consigliato: `SITO-ANNO-PROGRESSIVO`
- Esempio: `VRS-2024-C001`

### Prelievo

- Documentare sempre le coordinate di prelievo
- Fotografare il punto di prelievo
- Annotare profondita e contesto

### Conservazione

- Usare contenitori appropriati al tipo
- Etichettare chiaramente ogni campione
- Mantenere condizioni idonee

### Documentazione

- Collegare sempre alla US di provenienza
- Indicare le analisi previste
- Registrare l'invio a laboratori esterni

---

## Troubleshooting

### Problema: Tipo campione non disponibile

**Causa**: Thesaurus non configurato.

**Soluzione**:
1. Aprire la Scheda Thesaurus
2. Aggiungere il tipo mancante per `campioni_table`
3. Salvare e riaprire la Scheda Campioni

### Problema: US non visualizzata

**Causa**: US non registrata per il sito selezionato.

**Soluzione**:
1. Verificare che la US esista nella Scheda US
2. Controllare che appartenga allo stesso sito

---

## Riferimenti

### Database

- **Tabella**: `campioni_table`
- **Classe mapper**: `CAMPIONI`
- **ID**: `id_campione`

### File Sorgente

- **UI**: `gui/ui/Campioni.ui`
- **Controller**: `tabs/Campioni.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Video Tutorial

### Gestione Campioni
**Durata**: 5-6 minuti
- Creazione nuovo campione
- Compilazione campi
- Ricerca e export

[Placeholder video: video_campioni.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
