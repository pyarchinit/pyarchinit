# Tutorial 15: Scheda Archeozoologia (Fauna)

## Introduzione

La **Scheda Archeozoologia/Fauna** (SCHEDA FR - Fauna Record) e il modulo di PyArchInit dedicato all'analisi e documentazione dei resti faunistici. Permette di registrare dati archeozoologici dettagliati per lo studio delle economie di sussistenza antiche.

### Concetti Base

**Archeozoologia:**
- Studio dei resti animali da contesti archeologici
- Analisi delle relazioni uomo-animale nel passato
- Ricostruzione di diete, allevamento, caccia

**Dati registrati:**
- Identificazione tassonomica (specie)
- Parti scheletriche presenti
- NMI (Numero Minimo Individui)
- Stato di conservazione
- Tracce tafonomiche
- Segni di macellazione

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Scheda Fauna** (o **Fauna form**)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Fauna** (osso stilizzato)

---

## Panoramica dell'Interfaccia

La scheda e organizzata in tab tematici:

### Tab Principali

| # | Tab | Contenuto |
|---|-----|-----------|
| 1 | Dati Identificativi | Sito, Area, US, Contesto |
| 2 | Dati Archeozoologici | Specie, NMI, Parti scheletriche |
| 3 | Dati Tafonomici | Conservazione, Frammentazione, Tracce |
| 4 | Dati Contestuali | Contesto deposizionale, Associazioni |
| 5 | Statistiche | Grafici e quantificazioni |

---

## Toolbar

La toolbar fornisce le funzioni standard:

| Icona | Funzione |
|-------|----------|
| First/Prev/Next/Last | Navigazione record |
| New | Nuovo record |
| Save | Salva |
| Delete | Elimina |
| Search | Ricerca |
| View All | Visualizza tutti |
| PDF | Export PDF |

---

## Tab Dati Identificativi

### Selezione US

**Campo**: `comboBox_us_select`

Seleziona la US di provenienza. Mostra le US disponibili nel formato "Sito - Area - US".

### Sito

**Campo**: `comboBox_sito`
**Database**: `sito`

Sito archeologico.

### Area

**Campo**: `comboBox_area`
**Database**: `area`

Area di scavo.

### Saggio

**Campo**: `comboBox_saggio`
**Database**: `saggio`

Saggio/trincea di provenienza.

### US

**Campo**: `comboBox_us`
**Database**: `us`

Unita Stratigrafica.

### Datazione US

**Campo**: `lineEdit_datazione`
**Database**: `datazione_us`

Inquadramento cronologico della US.

### Responsabile

**Campo**: `comboBox_responsabile`
**Database**: `responsabile_scheda`

Autore della schedatura.

### Data Compilazione

**Campo**: `dateEdit_data`
**Database**: `data_compilazione`

Data di compilazione della scheda.

---

## Tab Dati Archeozoologici

### Contesto

**Campo**: `comboBox_contesto`
**Database**: `contesto`

Tipo di contesto deposizionale.

**Valori:**
- Abitato
- Scarico/Discarica
- Riempimento
- Strato di vita
- Sepoltura
- Rituale

### Specie

**Campo**: `comboBox_specie`
**Database**: `specie`

Identificazione tassonomica.

**Specie comuni in archeozoologia:**
| Specie | Nome scientifico |
|--------|------------------|
| Bovino | Bos taurus |
| Ovino | Ovis aries |
| Caprino | Capra hircus |
| Suino | Sus domesticus |
| Equino | Equus caballus |
| Cervo | Cervus elaphus |
| Cinghiale | Sus scrofa |
| Lepre | Lepus europaeus |
| Cane | Canis familiaris |
| Gatto | Felis catus |
| Pollame | Gallus gallus |

### Numero Minimo Individui (NMI)

**Campo**: `spinBox_nmi`
**Database**: `numero_minimo_individui`

Stima del numero minimo di individui rappresentati.

### Parti Scheletriche

**Campo**: `tableWidget_parti`
**Database**: `parti_scheletriche`

Tabella per registrare le parti anatomiche presenti.

**Colonne:**
| Colonna | Descrizione |
|---------|-------------|
| Elemento | Osso/parte anatomica |
| Lato | Dx/Sx/Assiale |
| Quantita | Numero frammenti |
| NMI | Contributo al NMI |

### Misure Ossa

**Campo**: `tableWidget_misure`
**Database**: `misure_ossa`

Misurazioni osteometriche standard.

---

## Tab Dati Tafonomici

### Stato Frammentazione

**Campo**: `comboBox_frammentazione`
**Database**: `stato_frammentazione`

Grado di frammentazione dei resti.

**Valori:**
- Integro
- Poco frammentato
- Frammentato
- Molto frammentato

### Stato Conservazione

**Campo**: `comboBox_conservazione`
**Database**: `stato_conservazione`

Condizioni generali di conservazione.

**Valori:**
- Ottimo
- Buono
- Mediocre
- Cattivo
- Pessimo

### Tracce Combustione

**Campo**: `comboBox_combustione`
**Database**: `tracce_combustione`

Presenza di tracce di fuoco.

**Valori:**
- Assenti
- Annerimento
- Carbonizzazione
- Calcinazione

### Segni Tafonomici

**Campo**: `comboBox_segni_tafo`
**Database**: `segni_tafonomici_evidenti`

Tracce di alterazione post-deposizionale.

**Tipi:**
- Weathering (agenti atmosferici)
- Root marks (radici)
- Gnawing (rosicchiature)
- Trampling (calpestio)

### Alterazioni Morfologiche

**Campo**: `textEdit_alterazioni`
**Database**: `alterazioni_morfologiche`

Descrizione dettagliata delle alterazioni osservate.

---

## Tab Dati Contestuali

### Metodologia Recupero

**Campo**: `comboBox_metodologia`
**Database**: `metodologia_recupero`

Metodo di raccolta dei resti.

**Valori:**
- A vista
- Setacciatura a secco
- Flottazione
- Setacciatura umida

### Resti in Connessione Anatomica

**Campo**: `checkBox_connessione`
**Database**: `resti_connessione_anatomica`

Presenza di parti in connessione.

### Classi Reperti Associazione

**Campo**: `textEdit_associazioni`
**Database**: `classi_reperti_associazione`

Altri materiali associati ai resti faunistici.

### Osservazioni

**Campo**: `textEdit_osservazioni`
**Database**: `osservazioni`

Note generali.

### Interpretazione

**Campo**: `textEdit_interpretazione`
**Database**: `interpretazione`

Interpretazione del contesto faunistico.

---

## Tab Statistiche

Fornisce strumenti per:
- Grafici di distribuzione per specie
- Calcolo NMI totali
- Confronti tra US/fasi
- Export dati statistici

---

## Workflow Operativo

### Schedatura Resti Faunistici

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su "New Record"

3. **Dati identificativi**
   ```
   Sito: Villa Romana
   Area: 1000
   US: 150
   Responsabile: G. Verdi
   Data: 20/07/2024
   ```

4. **Dati archeozoologici** (Tab 2)
   ```
   Contesto: Scarico/Discarica
   Specie: Bos taurus
   NMI: 3

   Parti scheletriche:
   - Omero / Dx / 2 / 1
   - Tibia / Sx / 3 / 2
   - Metapodio / - / 5 / 1
   ```

5. **Dati tafonomici** (Tab 3)
   ```
   Frammentazione: Frammentato
   Conservazione: Buono
   Combustione: Assenti
   Segni tafonomici: Root marks
   ```

6. **Interpretazione**
   ```
   Scarico di rifiuti alimentari.
   Presenza di tracce di macellazione
   su alcune ossa lunghe.
   ```

7. **Salvataggio**
   - Click su "Save"

---

## Best Practices

### Identificazione

- Utilizzare collezioni di riferimento
- Indicare il grado di certezza dell'ID
- Registrare anche i resti non identificabili

### NMI

- Calcolare per ogni specie separatamente
- Considerare lato e eta dei reperti
- Documentare il metodo di calcolo

### Tafonomia

- Osservare sistematicamente ogni reperto
- Documentare le tracce prima del lavaggio
- Fotografare casi significativi

### Contesto

- Collegare sempre alla US di provenienza
- Registrare il metodo di recupero
- Annotare associazioni significative

---

## Export PDF

La scheda permette di generare:
- Schede singole dettagliate
- Elenchi per US o fase
- Report statistici

---

## Troubleshooting

### Problema: Specie non disponibile

**Causa**: Lista specie incompleta.

**Soluzione**:
1. Verificare il thesaurus fauna
2. Aggiungere le specie mancanti
3. Contattare l'amministratore

### Problema: NMI non calcolato

**Causa**: Parti scheletriche non registrate.

**Soluzione**:
1. Compilare la tabella parti scheletriche
2. Indicare lato e quantita
3. Il sistema calcolera automaticamente

---

## Riferimenti

### Database

- **Tabella**: `fauna_table`
- **Classe mapper**: `FAUNA`
- **ID**: `id_fauna`

### File Sorgente

- **Controller**: `tabs/Fauna.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Video Tutorial

### Schedatura Archeozoologica
**Durata**: 12-15 minuti
- Identificazione tassonomica
- Registrazione parti scheletriche
- Analisi tafonomica

[Placeholder video: video_archeozoologia.mp4]

### Statistiche Faunistiche
**Durata**: 8-10 minuti
- Calcolo NMI
- Grafici di distribuzione
- Export dati

[Placeholder video: video_fauna_statistiche.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
