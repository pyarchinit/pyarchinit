# Tutorial 16: Scheda Pottery (Ceramica Specialistica)

## Indice
1. [Introduzione](#introduzione)
2. [Accesso alla Scheda](#accesso-alla-scheda)
3. [Interfaccia Utente](#interfaccia-utente)
4. [Campi Principali](#campi-principali)
5. [Tab della Scheda](#tab-della-scheda)
6. [Pottery Tools](#pottery-tools)
7. [Ricerca per Similarita Visiva](#ricerca-per-similarita-visiva)
8. [Quantificazioni](#quantificazioni)
9. [Gestione Media](#gestione-media)
10. [Export e Report](#export-e-report)
11. [Workflow Operativo](#workflow-operativo)
12. [Best Practices](#best-practices)
13. [Troubleshooting](#troubleshooting)

---

## Introduzione

La **Scheda Pottery** e uno strumento specializzato per la catalogazione dettagliata della ceramica archeologica. A differenza della scheda Inventario Materiali (piu generalista), questa scheda e progettata specificamente per l'analisi ceramologica approfondita, con campi dedicati a fabric, ware, decorazioni, e misure specifiche dei vasi.

### Differenze con Scheda Inventario Materiali

| Aspetto | Inventario Materiali | Pottery |
|---------|---------------------|---------|
| **Scopo** | Tutti i tipi di reperti | Solo ceramica |
| **Dettaglio** | Generale | Specialistico |
| **Campi fabric** | Corpo ceramico (generico) | Fabric dettagliato |
| **Decorazioni** | Campo singolo | Interna/Esterna separate |
| **Misure** | Generiche | Specifiche per vasi |
| **AI Tools** | SketchGPT | PotteryInk, YOLO, Similarity Search |

### Funzionalita Avanzate

La scheda Pottery include funzionalita AI all'avanguardia:
- **PotteryInk**: Generazione automatica di disegni archeologici da foto
- **YOLO Detection**: Riconoscimento automatico forme ceramiche
- **Visual Similarity Search**: Ricerca ceramiche simili tramite embedding visivi
- **Layout Generator**: Generazione automatica tavole ceramiche

![Panoramica Scheda Pottery](images/16_scheda_pottery/01_panoramica.png)
*Figura 1: Vista generale della Scheda Pottery*

---

## Accesso alla Scheda

### Da Menu

1. Aprire QGIS con il plugin PyArchInit attivo
2. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery**

![Menu Pottery](images/16_scheda_pottery/02_menu_accesso.png)
*Figura 2: Accesso alla scheda dal menu*

### Da Toolbar

1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Pottery** (icona vaso/anfora ceramica)

![Toolbar Pottery](images/16_scheda_pottery/03_toolbar_accesso.png)
*Figura 3: Icona nella toolbar*

---

## Interfaccia Utente

L'interfaccia e organizzata in modo efficiente per la schedatura ceramologica:

![Interfaccia Completa](images/16_scheda_pottery/04_interfaccia_completa.png)
*Figura 4: Layout completo dell'interfaccia*

### Aree Principali

| Area | Descrizione |
|------|-------------|
| **1. Header** | DBMS Toolbar, indicatori stato, filtri |
| **2. Identificazione** | Sito, Area, US, ID Number, Box, Bag |
| **3. Classificazione** | Form, Ware, Fabric, Material |
| **4. Tab Dettaglio** | Description, Technical Data, Supplements |
| **5. Media Panel** | Viewer immagini, anteprima |

### Tab Disponibili

| Tab | Contenuto |
|-----|-----------|
| **Description data** | Descrizione, decorazioni, note |
| **Technical Data** | Misure, trattamento superficie, Munsell |
| **Supplements** | Bibliografia, Statistiche |

---

## Campi Principali

### Campi Identificativi

#### ID Number
- **Tipo**: Integer
- **Obbligatorio**: Si
- **Descrizione**: Numero identificativo univoco del frammento ceramico
- **Vincolo**: Univoco per sito

#### Sito
- **Tipo**: ComboBox
- **Obbligatorio**: Si
- **Descrizione**: Sito archeologico di provenienza

#### Area
- **Tipo**: ComboBox editabile
- **Descrizione**: Area di scavo

#### US (Unita Stratigrafica)
- **Tipo**: Integer
- **Descrizione**: Numero della US di rinvenimento

#### Sector
- **Tipo**: Text
- **Descrizione**: Settore specifico di rinvenimento

![Campi Identificativi](images/16_scheda_pottery/05_campi_identificativi.png)
*Figura 5: Campi identificativi*

### Campi Deposito

#### Box
- **Tipo**: Integer
- **Descrizione**: Numero della cassa di deposito

#### Bag
- **Tipo**: Integer
- **Descrizione**: Numero del sacchetto

#### Year (Anno)
- **Tipo**: Integer
- **Descrizione**: Anno di rinvenimento/schedatura

### Campi Classificazione Ceramica

#### Form (Forma)
- **Tipo**: ComboBox editabile
- **Obbligatorio**: Consigliato
- **Valori tipici**: Bowl, Jar, Jug, Plate, Cup, Amphora, Lid, ecc.
- **Descrizione**: Forma generale del vaso

![Campo Form](images/16_scheda_pottery/06_campo_form.png)
*Figura 6: Selezione forma*

#### Specific Form (Forma Specifica)
- **Tipo**: ComboBox editabile
- **Descrizione**: Tipologia specifica (es. Hayes 50, Dressel 1)

#### Specific Shape
- **Tipo**: Text
- **Descrizione**: Variante morfologica dettagliata

#### Ware
- **Tipo**: ComboBox editabile
- **Descrizione**: Classe ceramica
- **Esempi**:
  - African Red Slip
  - Italian Sigillata
  - Thin Walled Ware
  - Coarse Ware
  - Amphora
  - Cooking Ware

![Campo Ware](images/16_scheda_pottery/07_campo_ware.png)
*Figura 7: Selezione ware*

#### Material
- **Tipo**: ComboBox editabile
- **Descrizione**: Materiale base
- **Valori**: Ceramic, Terracotta, Porcelain, ecc.

#### Fabric
- **Tipo**: ComboBox editabile
- **Descrizione**: Tipo di impasto ceramico
- **Caratteristiche da considerare**:
  - Colore dell'impasto
  - Granulometria inclusi
  - Durezza
  - Porosita

![Campo Fabric](images/16_scheda_pottery/08_campo_fabric.png)
*Figura 8: Selezione fabric*

### Campi Conservazione

#### Percent
- **Tipo**: ComboBox editabile
- **Descrizione**: Percentuale conservata del vaso
- **Valori tipici**: <10%, 10-25%, 25-50%, 50-75%, >75%, Complete

#### QTY (Quantity)
- **Tipo**: Integer
- **Descrizione**: Numero di frammenti

### Campi Documentazione

#### Photo
- **Tipo**: Text
- **Descrizione**: Riferimento fotografico

#### Drawing
- **Tipo**: Text
- **Descrizione**: Riferimento disegno

---

## Tab della Scheda

### Tab 1: Description Data

Tab principale per la descrizione del frammento.

![Tab Description](images/16_scheda_pottery/09_tab_description.png)
*Figura 9: Tab Description Data*

#### Decorazioni

| Campo | Descrizione |
|-------|-------------|
| **External Decoration** | Tipo decorazione esterna |
| **Internal Decoration** | Tipo decorazione interna |
| **Description External Deco** | Descrizione dettagliata decorazione esterna |
| **Description Internal Deco** | Descrizione dettagliata decorazione interna |
| **Decoration Type** | Tipologia decorativa (Painted, Incised, Applique, ecc.) |
| **Decoration Motif** | Motivo decorativo (Geometric, Vegetal, Figurative) |
| **Decoration Position** | Posizione decorazione (Rim, Body, Base, Handle) |

#### Wheel Made
- **Tipo**: ComboBox
- **Valori**: Yes, No, Unknown
- **Descrizione**: Indica se il vaso e stato prodotto al tornio

#### Note
- **Tipo**: TextEdit multilinea
- **Descrizione**: Note aggiuntive e osservazioni

#### Media Viewer
Area per visualizzare le immagini associate:
- Drag & drop per associare immagini
- Doppio click per aprire viewer completo
- Pulsanti per gestione tag

### Tab 2: Technical Data

Dati tecnici e misurazioni.

![Tab Technical](images/16_scheda_pottery/10_tab_technical.png)
*Figura 10: Tab Technical Data*

#### Munsell Color
- **Tipo**: ComboBox editabile
- **Descrizione**: Codice colore Munsell dell'impasto
- **Formato**: es. "10YR 7/4", "5YR 6/6"
- **Note**: Riferirsi alla Munsell Soil Color Chart

![Campo Munsell](images/16_scheda_pottery/11_campo_munsell.png)
*Figura 11: Selezione colore Munsell*

#### Surface Treatment
- **Tipo**: ComboBox editabile
- **Descrizione**: Trattamento superficiale
- **Valori tipici**:
  - Slip (ingobbio)
  - Burnished (brunito)
  - Glazed (vetrinato)
  - Painted (dipinto)
  - Plain (semplice)

#### Misure (in cm)

| Campo | Descrizione |
|-------|-------------|
| **Diameter Max** | Diametro massimo del vaso |
| **Diameter Rim** | Diametro dell'orlo |
| **Diameter Bottom** | Diametro del fondo |
| **Total Height** | Altezza totale (se ricostruibile) |
| **Preserved Height** | Altezza conservata |

![Campi Misure](images/16_scheda_pottery/12_campi_misure.png)
*Figura 12: Campi misure*

#### Datazione
- **Tipo**: ComboBox editabile
- **Descrizione**: Inquadramento cronologico
- **Formato**: Testuale (es. "I-II sec. d.C.")

### Tab 3: Supplements

Tab con sottosezioni per dati supplementari.

![Tab Supplements](images/16_scheda_pottery/13_tab_supplements.png)
*Figura 13: Tab Supplements*

#### Sub-Tab: Bibliography
Gestione riferimenti bibliografici per confronti tipologici.

| Colonna | Descrizione |
|---------|-------------|
| Author | Autore/i |
| Year | Anno pubblicazione |
| Title | Titolo abbreviato |
| Page | Pagina di riferimento |
| Figure | Figura/Tavola |

#### Sub-Tab: Statistic
Accesso alle funzionalita di quantificazione e grafici statistici.

---

## Pottery Tools

La scheda Pottery include un potente set di strumenti AI per l'elaborazione delle immagini ceramiche.

### Accesso a Pottery Tools

1. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery Tools**

Oppure dal pulsante dedicato nella scheda Pottery.

![Pottery Tools](images/16_scheda_pottery/14_pottery_tools.png)
*Figura 14: Interfaccia Pottery Tools*

### PotteryInk - Generazione Disegni

Trasforma automaticamente le foto di ceramica in disegni archeologici stilizzati.

![PotteryInk](images/16_scheda_pottery/15_potteryink.png)
*Figura 15: PotteryInk in azione*

#### Utilizzo

1. Selezionare un'immagine di ceramica
2. Cliccare su "Generate Drawing"
3. Il sistema elabora l'immagine con AI
4. Il disegno viene generato in stile archeologico

#### Requisiti
- Virtual environment dedicato (creato automaticamente)
- Modelli AI pre-addestrati
- GPU consigliata per prestazioni ottimali

### YOLO Pottery Detection

Riconoscimento automatico delle forme ceramiche nelle immagini.

![YOLO Detection](images/16_scheda_pottery/16_yolo_detection.png)
*Figura 16: YOLO Detection*

#### Funzionalita

- Identifica automaticamente la forma del vaso
- Suggerisce classificazione
- Rileva parti anatomiche (orlo, parete, fondo, ansa)

### Layout Generator

Genera automaticamente tavole ceramiche per pubblicazione.

![Layout Generator](images/16_scheda_pottery/17_layout_generator.png)
*Figura 17: Layout Generator*

#### Output

- Tavole in formato standard archeologico
- Scala metrica automatica
- Disposizione ottimizzata
- Export in PDF o immagine

### PDF Extractor

Estrae immagini di ceramica da pubblicazioni PDF per confronti.

---

## Ricerca per Similarita Visiva

Funzionalita avanzata per trovare ceramiche visivamente simili nel database.

### Come Funziona

Il sistema utilizza **embedding visivi** generati da modelli di deep learning per rappresentare ogni immagine ceramica come un vettore numerico. La ricerca trova le ceramiche con vettori piu simili.

![Similarity Search](images/16_scheda_pottery/18_similarity_search.png)
*Figura 18: Ricerca per similarita visiva*

### Utilizzo

1. Selezionare un'immagine di riferimento
2. Cliccare su "Find Similar"
3. Il sistema cerca nel database
4. Vengono mostrate le ceramiche piu simili ordinate per similarita

### Modelli Disponibili

- **ResNet50**: Buon bilanciamento velocita/precisione
- **EfficientNet**: Prestazioni ottimali
- **CLIP**: Ricerca multimodale (testo + immagine)

### Aggiornamento Embedding

Gli embedding vengono generati automaticamente quando si aggiungono nuove immagini. E possibile forzare l'aggiornamento dal menu Pottery Tools.

---

## Quantificazioni

### Accesso

1. Cliccare sul pulsante **Quant** nella toolbar
2. Selezionare il parametro di quantificazione
3. Visualizzare il grafico

![Pannello Quantificazioni](images/16_scheda_pottery/19_pannello_quant.png)
*Figura 19: Pannello quantificazioni*

### Parametri Disponibili

| Parametro | Descrizione |
|-----------|-------------|
| **Fabric** | Distribuzione per tipo di impasto |
| **US** | Distribuzione per unita stratigrafica |
| **Area** | Distribuzione per area di scavo |
| **Material** | Distribuzione per materiale |
| **Percent** | Distribuzione per percentuale conservata |
| **Shape/Form** | Distribuzione per forma |
| **Specific form** | Distribuzione per forma specifica |
| **Ware** | Distribuzione per classe ceramica |
| **Munsell color** | Distribuzione per colore |
| **Surface treatment** | Distribuzione per trattamento superficiale |
| **External decoration** | Distribuzione per decorazione esterna |
| **Internal decoration** | Distribuzione per decorazione interna |
| **Wheel made** | Distribuzione tornio si/no |

### Export Quantificazioni

I dati vengono esportati in:
- File CSV in `pyarchinit_Quantificazioni_folder`
- Grafico visualizzato a schermo

---

## Gestione Media

### Associazione Immagini

![Gestione Media](images/16_scheda_pottery/20_gestione_media.png)
*Figura 20: Gestione media*

#### Metodi

1. **Drag & Drop**: Trascinare immagini nella lista
2. **Pulsante All Images**: Carica tutte le immagini associate
3. **Search Images**: Cerca immagini specifiche

### Video Player

Per ceramiche con documentazione video, e disponibile un player integrato.

### Cloudinary Integration

Supporto per immagini remote su Cloudinary:
- Caricamento automatico thumbnail
- Cache locale per prestazioni
- Sincronizzazione con cloud

---

## Export e Report

### Export PDF Scheda

![Export PDF](images/16_scheda_pottery/21_export_pdf.png)
*Figura 21: Export PDF*

Genera una scheda PDF completa con:
- Dati identificativi
- Classificazione
- Misure
- Immagini associate
- Note

### Export Lista

Genera elenco PDF di tutti i record visualizzati.

### Export Dati

Pulsante per export in formato tabellare (CSV/Excel).

---

## Workflow Operativo

### Schedatura Nuovo Frammento Ceramico

#### Passo 1: Apertura e Nuovo Record
1. Aprire la Scheda Pottery
2. Cliccare **New record**

![Workflow Step 1](images/16_scheda_pottery/22_workflow_step1.png)
*Figura 22: Nuovo record*

#### Passo 2: Dati Identificativi
1. Verificare/selezionare **Sito**
2. Inserire **ID Number** (progressivo)
3. Inserire **Area**, **US**, **Sector**
4. Inserire **Box** e **Bag**

![Workflow Step 2](images/16_scheda_pottery/23_workflow_step2.png)
*Figura 23: Dati identificativi*

#### Passo 3: Classificazione
1. Selezionare **Form** (Bowl, Jar, ecc.)
2. Selezionare **Ware** (classe ceramica)
3. Selezionare **Fabric** (tipo impasto)
4. Indicare **Material** e **Percent**

![Workflow Step 3](images/16_scheda_pottery/24_workflow_step3.png)
*Figura 24: Classificazione*

#### Passo 4: Dati Tecnici
1. Aprire tab **Technical Data**
2. Inserire **Munsell color**
3. Selezionare **Surface treatment**
4. Inserire le **misure** (diametri, altezze)
5. Indicare **Wheel made**

![Workflow Step 4](images/16_scheda_pottery/25_workflow_step4.png)
*Figura 25: Dati tecnici*

#### Passo 5: Decorazioni (se presenti)
1. Tornare a tab **Description data**
2. Selezionare tipo **External/Internal decoration**
3. Compilare descrizioni dettagliate
4. Indicare **Decoration type**, **motif**, **position**

![Workflow Step 5](images/16_scheda_pottery/26_workflow_step5.png)
*Figura 26: Decorazioni*

#### Passo 6: Documentazione
1. Associare foto (drag & drop)
2. Inserire riferimento **Photo** e **Drawing**
3. Compilare **Note** con osservazioni

#### Passo 7: Datazione e Confronti
1. Inserire **Datazione**
2. Aprire tab **Supplements** → **Bibliography**
3. Aggiungere riferimenti bibliografici

#### Passo 8: Salvataggio
1. Cliccare **Save**
2. Verificare conferma

![Workflow Step 8](images/16_scheda_pottery/27_workflow_step8.png)
*Figura 27: Salvataggio*

---

## Best Practices

### Classificazione Coerente

- Utilizzare vocabolari standardizzati per Form, Ware, Fabric
- Mantenere coerenza nella nomenclatura
- Aggiornare il thesaurus quando necessario

### Documentazione Fotografica

- Fotografare ogni frammento con scala
- Includere vista interna ed esterna
- Documentare dettagli decorativi

### Misurazioni

- Usare calibro per misure accurate
- Indicare sempre l'unita di misura (cm)
- Per frammenti, misurare solo parti conservate

### Colore Munsell

- Usare sempre la Munsell Soil Color Chart
- Misurare su frattura fresca
- Indicare condizioni di luce

### Utilizzo AI Tools

- Verificare sempre i risultati automatici
- PotteryInk funziona meglio con foto di buona qualita
- La similarity search e utile per confronti, non sostitutiva dell'analisi

---

## Troubleshooting

### Problemi Comuni

#### ID Number duplicato
- **Errore**: "Esiste gia un record con questo ID"
- **Soluzione**: Verificare il prossimo numero disponibile

#### Pottery Tools non si avvia
- **Causa**: Virtual environment non configurato
- **Soluzione**:
  1. Verificare connessione internet
  2. Attendere configurazione automatica
  3. Controllare log in `pyarchinit/bin/pottery_venv`

#### PotteryInk lento
- **Causa**: Elaborazione CPU invece di GPU
- **Soluzione**:
  1. Installare driver CUDA (NVIDIA)
  2. Verificare che PyTorch usi GPU

#### Similarity Search vuoto
- **Causa**: Embedding non generati
- **Soluzione**:
  1. Aprire Pottery Tools
  2. Cliccare "Update Embeddings"
  3. Attendere completamento

#### Immagini non caricate
- **Causa**: Path non corretto o Cloudinary non configurato
- **Soluzione**:
  1. Verificare configurazione path in Settings
  2. Per Cloudinary: verificare credenziali

---

## Video Tutorial

### Video 1: Panoramica Scheda Pottery
*Durata: 5-6 minuti*

[Placeholder per video]

### Video 2: Schedatura Ceramica Completa
*Durata: 8-10 minuti*

[Placeholder per video]

### Video 3: Pottery Tools e AI
*Durata: 10-12 minuti*

[Placeholder per video]

### Video 4: Ricerca per Similarita
*Durata: 5-6 minuti*

[Placeholder per video]

---

## Riepilogo Campi Database

| Campo | Tipo | Database | Obbligatorio |
|-------|------|----------|--------------|
| ID Number | Integer | id_number | Si |
| Sito | Text | sito | Si |
| Area | Text | area | No |
| US | Integer | us | No |
| Box | Integer | box | No |
| Bag | Integer | bag | No |
| Sector | Text | sector | No |
| Photo | Text | photo | No |
| Drawing | Text | drawing | No |
| Year | Integer | anno | No |
| Fabric | Text | fabric | No |
| Percent | Text | percent | No |
| Material | Text | material | No |
| Form | Text | form | No |
| Specific Form | Text | specific_form | No |
| Specific Shape | Text | specific_shape | No |
| Ware | Text | ware | No |
| Munsell Color | Text | munsell | No |
| Surface Treatment | Text | surf_trat | No |
| External Decoration | Text | exdeco | No |
| Internal Decoration | Text | intdeco | No |
| Wheel Made | Text | wheel_made | No |
| Descrip. External Deco | Text | descrip_ex_deco | No |
| Descrip. Internal Deco | Text | descrip_in_deco | No |
| Note | Text | note | No |
| Diameter Max | Numeric | diametro_max | No |
| QTY | Integer | qty | No |
| Diameter Rim | Numeric | diametro_rim | No |
| Diameter Bottom | Numeric | diametro_bottom | No |
| Total Height | Numeric | diametro_height | No |
| Preserved Height | Numeric | diametro_preserved | No |
| Decoration Type | Text | decoration_type | No |
| Decoration Motif | Text | decoration_motif | No |
| Decoration Position | Text | decoration_position | No |
| Datazione | Text | datazione | No |

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Archaeological Pottery Analysis*

---

## Animazione Interattiva

Esplora l'animazione interattiva per approfondire questo argomento.

[Apri Animazione Interattiva](../animations/pyarchinit_pottery_tools_animation.html)
