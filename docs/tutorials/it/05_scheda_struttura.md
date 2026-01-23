# Tutorial 05: Scheda Struttura

## Introduzione

La **Scheda Struttura** e il modulo di PyArchInit dedicato alla documentazione delle strutture archeologiche. Una struttura e un insieme organizzato di Unita Stratigrafiche (US/USM) che formano un'entita costruttiva o funzionale riconoscibile, come un muro, una pavimentazione, una tomba, un forno, o qualsiasi altro elemento costruito.

### Concetti Base

**Struttura vs Unita Stratigrafica:**
- Una **US** e la singola unita (strato, taglio, riempimento)
- Una **Struttura** raggruppa piu US correlate funzionalmente
- Esempio: un muro (struttura) e composto da fondazione, alzato, malta (diverse US)

**Gerarchie:**
- Strutture possono avere rapporti tra loro
- Ogni struttura appartiene a uno o piu periodi/fasi cronologiche
- Le strutture sono collegate alle US che le compongono

---

## Accesso alla Scheda

### Via Menu
1. Menu **PyArchInit** nella barra dei menu di QGIS
2. Selezionare **Gestione Strutture** (o **Structure form**)

![Menu accesso](images/05_scheda_struttura/02_menu_accesso.png)

### Via Toolbar
1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Struttura** (edificio stilizzato)

![Toolbar accesso](images/05_scheda_struttura/03_toolbar_accesso.png)

---

## Panoramica dell'Interfaccia

La scheda presenta un layout organizzato in sezioni funzionali:

![Interfaccia completa](images/05_scheda_struttura/04_interfaccia_completa.png)

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigazione, ricerca, salvataggio |
| 2 | DB Info | Stato record, ordinamento, contatore |
| 3 | Campi Identificativi | Sito, Sigla, Numero struttura |
| 4 | Campi Classificazione | Categoria, Tipologia, Definizione |
| 5 | Area Tab | Tab tematici per dati specifici |

---

## Toolbar DBMS

La toolbar principale fornisce tutti gli strumenti per la gestione dei record.

![Toolbar DBMS](images/05_scheda_struttura/05_toolbar_dbms.png)

### Pulsanti di Navigazione

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![First](../../resources/icons/5_leftArrows.png) | First rec | Vai al primo record |
| ![Prev](../../resources/icons/4_leftArrow.png) | Prev rec | Vai al record precedente |
| ![Next](../../resources/icons/6_rightArrow.png) | Next rec | Vai al record successivo |
| ![Last](../../resources/icons/7_rightArrows.png) | Last rec | Vai all'ultimo record |

### Pulsanti CRUD

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![New](../../resources/icons/newrec.png) | New record | Crea un nuovo record struttura |
| ![Save](../../resources/icons/b_save.png) | Save | Salva le modifiche |
| ![Delete](../../resources/icons/delete.png) | Delete | Elimina il record corrente |

### Pulsanti di Ricerca

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![New Search](../../resources/icons/new_search.png) | New search | Avvia nuova ricerca |
| ![Search](../../resources/icons/search.png) | Search!!! | Esegui ricerca |
| ![Sort](../../resources/icons/sort.png) | Order by | Ordina risultati |
| ![View All](../../resources/icons/view_all.png) | View all | Visualizza tutti i record |

### Pulsanti Speciali

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![Map Preview](map_preview.png) | Map preview | Attiva/disattiva anteprima mappa |
| ![Media Preview](../../resources/icons/photo.png) | Media preview | Attiva/disattiva anteprima media |
| ![Draw Structure](../../resources/icons/iconStrutt.png) | Draw structure | Disegna struttura su mappa |
| ![GIS](../../resources/icons/GIS.png) | Load to GIS | Carica struttura su mappa |
| ![Layers](../../resources/icons/layers-icon.png) | Load all | Carica tutte le strutture |
| ![PDF](../../resources/icons/pdf-icon.png) | PDF export | Esporta in PDF |
| ![Directory](../../resources/icons/directoryExp.png) | Open directory | Apri cartella export |

---

## Campi Identificativi

I campi identificativi definiscono univocamente la struttura nel database.

![Campi identificativi](images/05_scheda_struttura/06_campi_identificativi.png)

### Sito

**Campo**: `comboBox_sito`
**Database**: `sito`

Seleziona il sito archeologico di appartenenza. Il menu a tendina mostra tutti i siti registrati nel database.

**Note:**
- Campo obbligatorio
- La combinazione Sito + Sigla + Numero deve essere univoca
- Bloccato dopo la creazione del record

### Sigla Struttura

**Campo**: `comboBox_sigla_struttura`
**Database**: `sigla_struttura`

Codice alfanumerico che identifica il tipo di struttura. Convenzioni comuni:

| Sigla | Significato | Esempio |
|-------|-------------|---------|
| MR | Muro | MR 1 |
| ST | Struttura | ST 5 |
| PV | Pavimentazione | PV 2 |
| FO | Forno | FO 1 |
| VA | Vasca | VA 3 |
| TM | Tomba | TM 10 |
| PT | Pozzo | PT 2 |
| CN | Canale | CN 1 |

**Note:**
- Editabile con inserimento libero
- Bloccato dopo la creazione

### Numero Struttura

**Campo**: `numero_struttura`
**Database**: `numero_struttura`

Numero progressivo della struttura all'interno della sigla.

**Note:**
- Campo numerico
- Deve essere univoco per combinazione Sito + Sigla
- Bloccato dopo la creazione

---

## Sincronizzazione con la Scheda US

Le strutture create in questa scheda appaiono automaticamente nel campo **Struttura** della **Scheda US** per lo stesso sito.

### Come funziona il collegamento

1. **Creare la struttura** compilando almeno:
   - **Sito**: il sito archeologico (es. "Roma_Foro")
   - **Sigla**: il codice della struttura (es. "MUR")
   - **Numero**: il numero progressivo (es. 1)
   - Salvare il record

2. **Nella Scheda US** dello stesso sito:
   - Il campo **Struttura** mostrera la struttura nel formato `SIGLA-NUMERO`
   - Esempio: "MUR-1", "PV-2", "ST-3"

### Formato di visualizzazione

Le strutture appaiono nella Scheda US nel formato:
```
SIGLA_STRUTTURA - NUMERO_STRUTTURA
```

**Esempi:**
| Scheda Struttura | Visualizzato in Scheda US |
|------------------|---------------------------|
| Sito=Roma, Sigla=MUR, Numero=1 | MUR-1 |
| Sito=Roma, Sigla=PV, Numero=2 | PV-2 |
| Sito=Roma, Sigla=ST, Numero=10 | ST-10 |

### Note importanti

- La struttura deve essere **salvata** prima di apparire nella Scheda US
- Solo le strutture dello **stesso sito** sono visibili
- Nella Scheda US e possibile **selezionare piu strutture** (selezione multipla con checkbox)
- Per **rimuovere** una struttura dall'US: aprire il menu a tendina e togliere la spunta
- Per **svuotare** tutte le strutture: click destro → "Svuota campo Struttura"

---

## Campi di Classificazione

I campi di classificazione definiscono la natura della struttura.

![Campi classificazione](images/05_scheda_struttura/07_campi_classificazione.png)

### Categoria Struttura

**Campo**: `comboBox_categoria_struttura`
**Database**: `categoria_struttura`

Macro-categoria funzionale della struttura.

**Valori tipici:**
- Residenziale
- Produttiva
- Funeraria
- Religiosa
- Difensiva
- Idraulica
- Viaria
- Artigianale

### Tipologia Struttura

**Campo**: `comboBox_tipologia_struttura`
**Database**: `tipologia_struttura`

Tipologia specifica all'interno della categoria.

**Esempi per categoria:**
| Categoria | Tipologie |
|-----------|-----------|
| Residenziale | Casa, Villa, Palazzo, Capanna |
| Produttiva | Fornace, Mulino, Frantoio |
| Funeraria | Tomba a fossa, Tomba a camera, Sarcofago |
| Idraulica | Pozzo, Cisterna, Acquedotto, Canale |

### Definizione Struttura

**Campo**: `comboBox_definizione_struttura`
**Database**: `definizione_struttura`

Definizione sintetica e specifica dell'elemento strutturale.

**Esempi:**
- Muro perimetrale
- Pavimentazione in cocciopesto
- Soglia in pietra
- Scalinata
- Base di colonna

---

## Tab Dati Descrittivi

Il primo tab contiene i campi testuali per la descrizione dettagliata.

![Tab Dati Descrittivi](images/05_scheda_struttura/08_tab_descrittivi.png)

### Descrizione

**Campo**: `textEdit_descrizione_struttura`
**Database**: `descrizione`

Campo testuale libero per la descrizione fisica della struttura.

**Contenuti consigliati:**
- Tecnica costruttiva
- Materiali utilizzati
- Stato di conservazione
- Dimensioni generali
- Orientamento
- Caratteristiche peculiari

**Esempio:**
```
Muro in opera incerta realizzato con blocchi di calcare locale
di dimensioni variabili (cm 15-30). Legante in malta di calce
di colore biancastro. Conservato per un'altezza massima di m 1.20.
Larghezza media cm 50. Orientamento NE-SW. Presenta tracce
di intonaco sul lato interno.
```

### Interpretazione

**Campo**: `textEdit_interpretazione_struttura`
**Database**: `interpretazione`

Interpretazione funzionale e storica della struttura.

**Contenuti consigliati:**
- Funzione originaria ipotizzata
- Fasi di utilizzo/riutilizzo
- Confronti tipologici
- Inquadramento cronologico
- Rapporti con altre strutture

**Esempio:**
```
Muro perimetrale nord di un edificio residenziale di eta romana
imperiale. La tecnica costruttiva e i materiali suggeriscono
una datazione al II sec. d.C. In una fase successiva (III-IV sec.)
il muro venne parzialmente spoliato e inglobato in una
struttura produttiva.
```

---

## Tab Periodizzazione

Questo tab gestisce l'inquadramento cronologico della struttura.

![Tab Periodizzazione](images/05_scheda_struttura/09_tab_periodizzazione.png)

### Periodo e Fase Iniziale

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Periodo Iniziale | `periodo_iniziale` | Periodo di costruzione/inizio uso |
| Fase Iniziale | `fase_iniziale` | Fase all'interno del periodo |

I valori sono popolati automaticamente in base ai periodi definiti nella Scheda Periodizzazione per il sito selezionato.

### Periodo e Fase Finale

| Campo | Database | Descrizione |
|-------|----------|-------------|
| Periodo Finale | `periodo_finale` | Periodo di abbandono/dismissione |
| Fase Finale | `fase_finale` | Fase all'interno del periodo |

### Datazione Estesa

**Campo**: `comboBox_datazione_estesa`
**Database**: `datazione_estesa`

Datazione letterale calcolata automaticamente o inserita manualmente.

**Formati:**
- "I sec. a.C. - II sec. d.C."
- "100 a.C. - 200 d.C."
- "Eta romana imperiale"

**Note:**
- Viene proposta automaticamente in base a periodo/fase
- Modificabile manualmente per casi particolari

---

## Tab Rapporti

Questo tab gestisce le relazioni tra strutture.

![Tab Rapporti](images/05_scheda_struttura/10_tab_rapporti.png)

### Tabella Rapporti Struttura

**Widget**: `tableWidget_rapporti`
**Database**: `rapporti_struttura`

Registra i rapporti tra la struttura corrente e altre strutture.

**Colonne:**
| Colonna | Descrizione |
|---------|-------------|
| Tipo di rapporto | Relazione stratigrafica/funzionale |
| Sito | Sito della struttura correlata |
| Sigla | Sigla della struttura correlata |
| Numero | Numero della struttura correlata |

**Tipi di rapporto:**

| Rapporto | Inverso | Descrizione |
|----------|---------|-------------|
| Si lega a | Si lega a | Connessione fisica contemporanea |
| Copre | Coperto da | Relazione di sovrapposizione |
| Taglia | Tagliato da | Relazione di taglio |
| Riempie | Riempito da | Relazione di riempimento |
| Si appoggia a | Gli si appoggia | Relazione di appoggio |
| Uguale a | Uguale a | Stessa struttura con nome diverso |

### Gestione Righe

| Pulsante | Funzione |
|----------|----------|
| + | Aggiungi nuova riga |
| - | Rimuovi riga selezionata |

---

## Tab Elementi Costruttivi

Questo tab documenta i materiali e gli elementi che compongono la struttura.

![Tab Elementi Costruttivi](images/05_scheda_struttura/11_tab_elementi.png)

### Materiali Impiegati

**Widget**: `tableWidget_materiali_impiegati`
**Database**: `materiali_impiegati`

Elenco dei materiali utilizzati nella costruzione.

**Colonna:**
- Materiali: descrizione del materiale

**Esempi di materiali:**
- Blocchi di calcare
- Laterizi
- Malta di calce
- Ciottoli di fiume
- Tegole
- Marmo
- Tufo

### Elementi Strutturali

**Widget**: `tableWidget_elementi_strutturali`
**Database**: `elementi_strutturali`

Elenco degli elementi costruttivi con quantita.

**Colonne:**
| Colonna | Descrizione |
|---------|-------------|
| Tipologia elemento | Tipo di elemento |
| Quantita | Numero di elementi |

**Esempi di elementi:**
| Elemento | Quantita |
|----------|----------|
| Base di colonna | 4 |
| Capitello | 2 |
| Soglia | 1 |
| Blocco squadrato | 45 |

### Gestione Righe

Per entrambe le tabelle:
| Pulsante | Funzione |
|----------|----------|
| + | Aggiungi nuova riga |
| - | Rimuovi riga selezionata |

---

## Tab Misure

Questo tab registra le dimensioni della struttura.

![Tab Misure](images/05_scheda_struttura/12_tab_misure.png)

### Tabella Misurazioni

**Widget**: `tableWidget_misurazioni`
**Database**: `misure_struttura`

**Colonne:**
| Colonna | Descrizione |
|---------|-------------|
| Tipo misura | Tipo di dimensione |
| Unita di misura | m, cm, mq, etc. |
| Valore | Valore numerico |

### Tipi di Misura Comuni

| Tipo | Descrizione |
|------|-------------|
| Lunghezza | Dimensione maggiore |
| Larghezza | Dimensione minore |
| Altezza conservata | Alzato conservato |
| Altezza originaria | Alzato stimato originale |
| Profondita | Per strutture infossate |
| Diametro | Per strutture circolari |
| Spessore | Per muri, pavimenti |
| Superficie | Area in mq |

### Esempio di Compilazione

| Tipo misura | Unita di misura | Valore |
|-------------|-----------------|--------|
| Lunghezza | m | 8.50 |
| Larghezza | cm | 55 |
| Altezza conservata | m | 1.20 |
| Superficie | mq | 4.68 |

---

## Tab Media

Gestione di immagini, video e modelli 3D associati alla struttura.

![Tab Media](images/05_scheda_struttura/13_tab_media.png)

### Funzionalita

**Widget**: `iconListWidget`

Visualizza le miniature dei media associati.

### Pulsanti

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| ![All Images](../../resources/icons/photo2.png) | All images | Mostra tutte le immagini |
| ![Remove Tags](../../resources/icons/remove_tag.png) | Remove tags | Rimuovi associazione media |
| ![Search](../../resources/icons/search.png) | Search images | Cerca immagini nel database |

### Drag & Drop

E possibile trascinare file direttamente sulla scheda:

**Formati supportati:**
- Immagini: JPG, JPEG, PNG, TIFF, TIF, BMP
- Video: MP4, AVI, MOV, MKV, FLV
- 3D: OBJ, STL, PLY, FBX, 3DS

### Visualizzazione

- **Doppio click** su miniatura: apre il visualizzatore
- Per i video: apre il player video integrato
- Per i 3D: apre il visualizzatore 3D PyVista

---

## Tab Map

Anteprima della posizione della struttura sulla mappa.

![Tab Map](images/05_scheda_struttura/14_tab_map.png)

### Funzionalita

- Visualizza la geometria della struttura
- Zoom automatico sull'elemento
- Integrazione con i layer GIS del progetto

---

## Integrazione GIS

### Visualizzazione su Mappa

| Pulsante | Funzione |
|----------|----------|
| Map Preview | Toggle anteprima nel tab Map |
| Draw Structure | Evidenzia struttura sulla mappa QGIS |
| Load to GIS | Carica layer strutture |
| Load All | Carica tutte le strutture del sito |

### Layer GIS

La scheda utilizza il layer **pyarchinit_strutture** per la visualizzazione:
- Geometria: poligono o multipoligono
- Attributi collegati ai campi della scheda

---

## Export e Stampa

### Export PDF

![Export Panel](images/05_scheda_struttura/15_export_panel.png)

Il pulsante PDF apre un pannello con opzioni di export:

| Opzione | Descrizione |
|---------|-------------|
| Elenco Strutture | Lista sintetica delle strutture |
| Schede Strutture | Schede complete dettagliate |
| Stampa | Genera il PDF |
| Converti in Word | Converte PDF in formato Word |

### Conversione PDF to Word

Funzionalita avanzata per convertire i PDF generati in documenti Word editabili:

1. Selezionare il file PDF da convertire
2. Specificare intervallo pagine (opzionale)
3. Cliccare "Convert"
4. Il file Word viene salvato nella stessa cartella

---

## Workflow Operativo

### Creazione Nuova Struttura

1. **Apertura scheda**
   - Via menu o toolbar

2. **Nuovo record**
   - Click su pulsante "New Record"
   - I campi identificativi diventano editabili

3. **Dati identificativi**
   ```
   Sito: Villa Romana di Settefinestre
   Sigla: MR
   Numero: 15
   ```

4. **Classificazione**
   ```
   Categoria: Residenziale
   Tipologia: Muro perimetrale
   Definizione: Muro in opera incerta
   ```

5. **Dati descrittivi** (Tab 1)
   ```
   Descrizione: Muro realizzato in opera incerta con
   blocchi di calcare locale...

   Interpretazione: Limite nord della domus, fase I
   dell'impianto residenziale...
   ```

6. **Periodizzazione** (Tab 2)
   ```
   Periodo iniziale: I - Fase: A
   Periodo finale: II - Fase: B
   Datazione: I sec. a.C. - II sec. d.C.
   ```

7. **Rapporti** (Tab 3)
   ```
   Si lega a: MR 16, MR 17
   Tagliato da: ST 5
   ```

8. **Elementi costruttivi** (Tab 4)
   ```
   Materiali: Blocchi di calcare, Malta di calce
   Elementi: Blocchi squadrati (52), Soglia (1)
   ```

9. **Misure** (Tab 5)
   ```
   Lunghezza: 12.50 m
   Larghezza: 0.55 m
   Altezza conservata: 1.80 m
   ```

10. **Salvataggio**
    - Click su "Save"
    - Verifica conferma salvataggio

### Ricerca Strutture

1. Click su "New Search"
2. Compilare uno o piu campi filtro:
   - Sito
   - Sigla struttura
   - Categoria
   - Periodo
3. Click su "Search"
4. Navigare tra i risultati

### Modifica Struttura Esistente

1. Navigare al record desiderato
2. Modificare i campi necessari
3. Click su "Save"

---

## Best Practices

### Nomenclatura

- Usare sigle coerenti in tutto il progetto
- Documentare le convenzioni usate
- Evitare duplicazioni di numerazione

### Descrizione

- Essere sistematici nella descrizione
- Seguire uno schema: tecnica > materiali > dimensioni > stato
- Separare descrizione oggettiva da interpretazione

### Periodizzazione

- Collegare sempre a periodi definiti nella Scheda Periodizzazione
- Indicare sia fase iniziale che finale
- Usare la datazione estesa per sintesi

### Rapporti

- Registrare tutti i rapporti significativi
- Verificare la reciprocita dei rapporti
- Collegare alle US che compongono la struttura

### Media

- Associare foto rappresentative
- Includere foto di dettaglio costruttivi
- Documentare le fasi di scavo

---

## Troubleshooting

### Problema: Struttura non visibile su mappa

**Causa**: Geometria non associata o layer non caricato.

**Soluzione**:
1. Verificare che esista il layer `pyarchinit_strutture`
2. Controllare che la struttura abbia una geometria associata
3. Verificare il sistema di riferimento

### Problema: Periodi non disponibili

**Causa**: Periodi non definiti per il sito.

**Soluzione**:
1. Aprire la Scheda Periodizzazione
2. Definire i periodi per il sito corrente
3. Tornare alla Scheda Struttura

### Problema: Errore salvataggio "record esistente"

**Causa**: Combinazione Sito + Sigla + Numero gia esistente.

**Soluzione**:
1. Verificare la numerazione esistente
2. Usare un numero progressivo libero
3. Controllare che non ci siano duplicati

### Problema: Media non visualizzati

**Causa**: Path delle immagini non corretto.

**Soluzione**:
1. Verificare il path nella configurazione
2. Controllare che i file esistano
3. Rigenerare le miniature se necessario

---

## Relazioni con Altre Schede

| Scheda | Relazione |
|--------|-----------|
| **Scheda Sito** | Il sito contiene le strutture |
| **Scheda US** | Le US compongono le strutture |
| **Scheda Periodizzazione** | Fornisce la cronologia |
| **Scheda Inventario Materiali** | Reperti associati alle strutture |
| **Scheda Tomba** | Tombe come tipo speciale di struttura |

---

## Riferimenti

### Database

- **Tabella**: `struttura_table`
- **Classe mapper**: `STRUTTURA`
- **ID**: `id_struttura`

### File Sorgente

- **UI**: `gui/ui/Struttura.ui`
- **Controller**: `tabs/Struttura.py`
- **PDF Export**: `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Video Tutorial

### Panoramica Scheda Struttura
**Durata**: 5-6 minuti
- Presentazione generale dell'interfaccia
- Navigazione tra i tab
- Funzionalita principali

[Placeholder video: video_panoramica_struttura.mp4]

### Schedatura Completa di una Struttura
**Durata**: 10-12 minuti
- Creazione nuovo record
- Compilazione di tutti i campi
- Gestione rapporti e misure

[Placeholder video: video_schedatura_struttura.mp4]

### Integrazione GIS e Export
**Durata**: 6-8 minuti
- Visualizzazione su mappa
- Caricamento layer
- Export PDF e Word

[Placeholder video: video_gis_export_struttura.mp4]

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Sistema di Gestione Dati Archeologici*
