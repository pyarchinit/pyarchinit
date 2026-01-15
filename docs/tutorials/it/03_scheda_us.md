# PyArchInit - Scheda US/USM (Unita Stratigrafica)

## Indice
1. [Introduzione](#introduzione)
2. [Concetti Fondamentali](#concetti-fondamentali)
3. [Accesso alla Scheda](#accesso-alla-scheda)
4. [Interfaccia Generale](#interfaccia-generale)
5. [Campi Identificativi](#campi-identificativi)
6. [Tab Localizzazione](#tab-localizzazione)
7. [Tab Dati Descrittivi](#tab-dati-descrittivi)
8. [Tab Periodizzazione](#tab-periodizzazione)
9. [Tab Rapporti Stratigrafici](#tab-rapporti-stratigrafici)
10. [Tab Dati Fisici](#tab-dati-fisici)
11. [Tab Dati Schedatura](#tab-dati-schedatura)
12. [Tab Misure US](#tab-misure-us)
13. [Tab Documentazione](#tab-documentazione)
14. [Tab Tecnica Edilizia USM](#tab-tecnica-edilizia-usm)
15. [Tab Leganti USM](#tab-leganti-usm)
16. [Tab Media](#tab-media)
17. [Tab Help - Tool Box](#tab-help---tool-box)
18. [Matrix di Harris](#matrix-di-harris)
19. [Funzionalita GIS](#funzionalita-gis)
20. [Esportazioni](#esportazioni)
21. [Workflow Operativo](#workflow-operativo)
22. [Risoluzione Problemi](#risoluzione-problemi)

---

## Introduzione

La **Scheda US/USM** (Unita Stratigrafica / Unita Stratigrafica Muraria) e il cuore della documentazione archeologica in PyArchInit. Rappresenta lo strumento principale per registrare tutte le informazioni relative alle unita stratigrafiche individuate durante lo scavo.

Questa scheda implementa i principi del **metodo stratigrafico** sviluppato da Edward C. Harris, permettendo di documentare:
- Le caratteristiche fisiche di ogni strato
- I rapporti stratigrafici tra le unita
- La cronologia relativa e assoluta
- La documentazione grafica e fotografica associata

<!-- VIDEO: Introduzione alla Scheda US -->
> **Video Tutorial**: [Inserire link video introduzione scheda US]

---

## Concetti Fondamentali

### Cos'e un'Unita Stratigrafica (US)

Un'**Unita Stratigrafica** e la piu piccola unita di scavo individuabile e distinguibile dalle altre. Puo essere:
- **Strato**: deposito di terra con caratteristiche omogenee
- **Interfaccia**: superficie di contatto tra strati (es. taglio di fossa)
- **Elemento strutturale**: parte di una costruzione

### Tipi di Unita

| Tipo | Codice | Descrizione |
|------|--------|-------------|
| US | Unita Stratigrafica | Strato generico |
| USM | Unita Stratigrafica Muraria | Elemento costruttivo murario |
| USVA | Unita Stratigrafica Verticale A | Alzato verticale tipo A |
| USVB | Unita Stratigrafica Verticale B | Alzato verticale tipo B |
| USVC | Unita Stratigrafica Verticale C | Alzato verticale tipo C |
| USD | Unita Stratigrafica di Demolizione | Strato di crollo/demolizione |
| CON | Conci | Blocchi architettonici |
| VSF | Virtual Stratigraphic Feature | Elemento virtuale |
| SF | Stratigraphic Feature | Feature stratigrafica |
| SUS | Sub-Unita Stratigrafica | Suddivisione di US |
| DOC | Documentazione | Elemento documentario |

### Rapporti Stratigrafici

I rapporti stratigrafici definiscono le relazioni temporali tra le US:

| Rapporto | Inverso | Significato |
|----------|---------|-------------|
| **Copre** | Coperto da | L'US si sovrappone fisicamente |
| **Taglia** | Tagliato da | L'US interrompe/attraversa |
| **Riempie** | Riempito da | L'US colma una cavita |
| **Si appoggia a** | Gli si appoggia | Relazione di appoggio |

<!-- IMMAGINE: Schema rapporti stratigrafici -->
![Rapporti Stratigrafici](images/03_scheda_us/01_schema_rapporti.png)
*Figura 1: Schema dei rapporti stratigrafici*

---

## Accesso alla Scheda

Per accedere alla Scheda US:

1. Menu **PyArchInit** → **Archaeological record management** → **SU/WSU**
2. Oppure dalla toolbar PyArchInit, cliccare sull'icona **US/USM**

<!-- IMMAGINE: Screenshot menu accesso -->
![Accesso Scheda US](images/03_scheda_us/02_menu_scheda_us.png)
*Figura 2: Accesso alla Scheda US dal menu*

<!-- IMMAGINE: Screenshot toolbar -->
![Toolbar US](images/03_scheda_us/03_toolbar_us.png)
*Figura 3: Icona Scheda US nella toolbar*

---

## Interfaccia Generale

La Scheda US e organizzata in diverse aree funzionali:

<!-- IMMAGINE: Screenshot interfaccia completa con aree numerate -->
![Interfaccia US](images/03_scheda_us/04_interfaccia_completa.png)
*Figura 4: Interfaccia completa della Scheda US*

### Aree Principali

| # | Area | Descrizione |
|---|------|-------------|
| 1 | **Campi Identificativi** | Sito, Area, US, Tipo, Definizioni |
| 2 | **Toolbar DBMS** | Navigazione, salvataggio, ricerca |
| 3 | **Tab Dati** | Schede tematiche per i dati |
| 4 | **Toolbar GIS** | Strumenti di visualizzazione mappa |
| 5 | **Tab Tool Box** | Strumenti avanzati e Matrix |

### Toolbar DBMS

La toolbar DBMS e identica a quella della Scheda Sito con alcune funzionalita aggiuntive:

<!-- IMMAGINE: Screenshot toolbar DBMS US -->
![Toolbar DBMS](images/03_scheda_us/05_toolbar_dbms.png)
*Figura 5: Toolbar DBMS della Scheda US*

| Bottone | Funzione | Descrizione |
|---------|----------|-------------|
| **New record** | Nuovo | Crea una nuova scheda US |
| **Save** | Salva | Salva le modifiche |
| **Delete** | Elimina | Elimina la scheda corrente |
| **View all** | Vedi tutti | Mostra tutti i record |
| **First/Prev/Next/Last** | Navigazione | Naviga tra i record |
| **new search** | Ricerca | Avvia modalita ricerca |
| **search !!!** | Esegui | Esegue la ricerca |
| **Order by** | Ordina | Ordina i record |
| **Report** | Stampa | Genera report PDF |
| **Elenco US/Foto** | Lista | Genera elenchi |

---

## Campi Identificativi

I campi identificativi sono sempre visibili nella parte superiore della scheda.

<!-- IMMAGINE: Screenshot campi identificativi -->
![Campi Identificativi](images/03_scheda_us/06_campi_identificativi.png)
*Figura 6: Campi identificativi*

### Campi Obbligatori

| Campo | Descrizione | Formato |
|-------|-------------|---------|
| **Sito** | Nome del sito archeologico | Testo (da combobox) |
| **Area** | Numero dell'area di scavo | Numero intero (1-20) |
| **US/USM** | Numero dell'unita stratigrafica | Numero intero |
| **Unita tipo** | Tipo di unita (US, USM, ecc.) | Selezione |

### Campi Descrittivi

| Campo | Descrizione |
|-------|-------------|
| **Definizione stratigrafica** | Classificazione stratigrafica (da thesaurus) |
| **Definizione interpretativa** | Interpretazione funzionale (da thesaurus) |

### Definizioni Stratigrafiche (Esempi)

| Definizione | Descrizione |
|-------------|-------------|
| Strato | Deposito generico |
| Riempimento | Materiale di colmatura |
| Taglio | Interfaccia negativa |
| Piano d'uso | Superficie di calpestio |
| Crollo | Materiale di crollo |
| Battuto | Pavimentazione in terra battuta |

### Definizioni Interpretative (Esempi)

| Definizione | Descrizione |
|-------------|-------------|
| Attivita' di cantiere | Fase costruttiva |
| Abbandono | Fase di abbandono |
| Pavimentazione | Piano pavimentale |
| Muro | Struttura muraria |
| Fossa | Escavazione intenzionale |
| Livellamento | Strato di preparazione |

---

## Tab Localizzazione

Contiene i dati di posizionamento all'interno dello scavo.

<!-- IMMAGINE: Screenshot tab localizzazione -->
![Tab Localizzazione](images/03_scheda_us/07_tab_localizzazione.png)
*Figura 7: Tab Localizzazione*

### Campi di Localizzazione

| Campo | Descrizione | Note |
|-------|-------------|------|
| **Settore** | Settore di scavo | Lettere A-H o numeri 1-20 |
| **Quadrato/Parete** | Riferimento spaziale | Per scavi a griglia |
| **Ambiente** | Numero dell'ambiente | Per edifici/strutture |
| **Saggio** | Numero del saggio | Per saggi di verifica |

### Numeri di Catalogo

| Campo | Descrizione |
|-------|-------------|
| **Nr. Cat. Generale** | Numero catalogo generale |
| **Nr. Cat. Interno** | Numero catalogo interno |
| **Nr. Cat. Internazionale** | Codice internazionale |

---

## Tab Dati Descrittivi

Contiene la descrizione testuale dell'unita stratigrafica.

<!-- IMMAGINE: Screenshot tab dati descrittivi -->
![Tab Dati Descrittivi](images/03_scheda_us/08_tab_dati_descrittivi.png)
*Figura 8: Tab Dati Descrittivi*

### Campi Descrittivi

| Campo | Descrizione | Suggerimenti |
|-------|-------------|--------------|
| **Descrizione** | Descrizione fisica dell'US | Colore, consistenza, composizione, limiti |
| **Interpretazione** | Interpretazione funzionale | Funzione, formazione, significato |
| **Elementi datanti** | Materiali per datazione | Ceramica, monete, oggetti datanti |
| **Osservazioni** | Note aggiuntive | Dubbi, ipotesi, confronti |

### Come Descrivere un'US

**Descrizione fisica:**
```
Strato di terra argillosa, di colore marrone scuro (10YR 3/3),
consistenza compatta, con inclusi di frammenti laterizi (2-5 cm),
ciottoli calcarei (1-3 cm) e carbone. Limiti netti in alto,
sfumati in basso. Spessore variabile 15-25 cm.
```

**Interpretazione:**
```
Strato di abbandono formatosi in seguito alla cessazione delle
attivita nell'ambiente. La presenza di materiale edilizio
frammentato suggerisce un crollo parziale delle strutture.
```

---

## Tab Periodizzazione

Gestisce la cronologia dell'unita stratigrafica.

<!-- IMMAGINE: Screenshot tab periodizzazione -->
![Tab Periodizzazione](images/03_scheda_us/09_tab_periodizzazione.png)
*Figura 9: Tab Periodizzazione*

### Periodizzazione Relativa

| Campo | Descrizione |
|-------|-------------|
| **Periodo Iniziale** | Periodo di formazione |
| **Fase Iniziale** | Fase di formazione |
| **Periodo Finale** | Periodo di obliterazione |
| **Fase Finale** | Fase di obliterazione |

**Nota**: I periodi e le fasi devono essere prima creati nella **Scheda Periodizzazione**.

### Cronologia Assoluta

| Campo | Descrizione |
|-------|-------------|
| **Datazione** | Data assoluta o intervallo |
| **Anno** | Anno di scavo |

### Altri Campi

| Campo | Descrizione | Valori |
|-------|-------------|--------|
| **Attivita** | Tipo di attivita | Testo libero |
| **Struttura** | Codice struttura associata | Da Scheda Struttura |
| **Scavato** | Stato di scavo | Si / No |
| **Metodo di scavo** | Modalita di scavo | Meccanico / Stratigrafico |

---

## Tab Rapporti Stratigrafici

**Questo e il tab piu importante della scheda US.** Definisce le relazioni stratigrafiche con le altre unita.

<!-- IMMAGINE: Screenshot tab rapporti stratigrafici -->
![Tab Rapporti](images/03_scheda_us/10_tab_rapporti.png)
*Figura 10: Tab Rapporti Stratigrafici*

<!-- VIDEO: Come inserire rapporti stratigrafici -->
> **Video Tutorial**: [Inserire link video rapporti stratigrafici]

### Struttura della Tabella Rapporti

| Colonna | Descrizione |
|---------|-------------|
| **Sito** | Sito dell'US correlata |
| **Area** | Area dell'US correlata |
| **US** | Numero US correlata |
| **Tipo di rapporto** | Tipo di relazione |

### Tipi di Rapporto Disponibili

| Italiano | English | Deutsch |
|----------|---------|---------|
| Copre | Covers | Liegt über |
| Coperto da | Covered by | Liegt unter |
| Taglia | Cuts | Schneidet |
| Tagliato da | Cut by | Geschnitten von |
| Riempie | Fills | Verfüllt |
| Riempito da | Filled by | Verfüllt von |
| Si appoggia a | Abuts | Stützt sich auf |
| Gli si appoggia | Supports | Wird gestützt von |
| Uguale a (=) | Same as | Gleich |
| Anteriore (>>) | Earlier | Früher |
| Posteriore (<<) | Later | Später |

### Inserimento Rapporti

1. Cliccare **+** per aggiungere una riga
2. Inserire Sito, Area, US della US correlata
3. Selezionare il tipo di rapporto
4. Salvare

<!-- IMMAGINE: Screenshot inserimento rapporto -->
![Inserimento Rapporto](images/03_scheda_us/11_inserimento_rapporto.png)
*Figura 11: Inserimento di un rapporto stratigrafico*

### Bottoni Rapporti

| Bottone | Funzione |
|---------|----------|
| **+** | Aggiungi riga |
| **-** | Rimuovi riga |
| **Insert or update inverse relat.** | Crea automaticamente il rapporto inverso |
| **Vai all'US** | Naviga alla US selezionata |
| **visualizza matrix** | Mostra il Matrix di Harris |
| **Fix** | Correggi errori nei rapporti |

### Rapporti Inversi Automatici

Quando inserisci un rapporto, puoi creare automaticamente l'inverso:

| Se inserisci | Viene creato |
|--------------|--------------|
| US 1 **copre** US 2 | US 2 **coperta da** US 1 |
| US 1 **taglia** US 2 | US 2 **tagliata da** US 1 |
| US 1 **riempie** US 2 | US 2 **riempita da** US 1 |

### Controllo Rapporti

Il bottone **Check rapporti** verifica la coerenza dei rapporti:
- Rileva rapporti mancanti
- Trova inconsistenze
- Segnala errori logici

<!-- IMMAGINE: Screenshot controllo rapporti -->
![Controllo Rapporti](images/03_scheda_us/12_controllo_rapporti.png)
*Figura 12: Risultato controllo rapporti*

---

## Tab Rapporti per Extended Matrix

Tab dedicato alla gestione avanzata dei rapporti per l'Extended Matrix.

<!-- IMMAGINE: Screenshot tab EM -->
![Tab EM](images/03_scheda_us/13_tab_em.png)
*Figura 13: Tab Rapporti per Extended Matrix*

Questo tab permette di aggiungere informazioni supplementari per ogni rapporto:
- Tipo di unita
- Definizione interpretativa
- Periodizzazione

---

## Tab Dati Fisici

Descrive le caratteristiche fisiche dell'unita stratigrafica.

<!-- IMMAGINE: Screenshot tab dati fisici -->
![Tab Dati Fisici](images/03_scheda_us/14_tab_dati_fisici.png)
*Figura 14: Tab Dati Fisici*

### Caratteristiche Generali

| Campo | Valori |
|-------|--------|
| **Colore** | Marrone, Giallo, Grigio, Nero, ecc. |
| **Consistenza** | Argillosa, Compatta, Friabile, Sabbiosa |
| **Formazione** | Artificiale, Naturale |
| **Posizione** | - |
| **Modo formazione** | Apporto, Sottrazione, Accumulo, Frana |
| **Criteri distinzione** | Testo libero |

### Tabelle Componenti

| Tabella | Contenuto |
|---------|-----------|
| **Comp. organici** | Ossa, legno, carboni, semi, ecc. |
| **Comp. inorganici** | Pietre, laterizi, ceramica, ecc. |
| **Inclusi Artificiali** | Materiali antropici inclusi |

Per ogni tabella:
- **+** Aggiungi riga
- **-** Rimuovi riga

### Campionature

| Campo | Valori |
|-------|--------|
| **Flottazione** | Si / No |
| **Setacciatura** | Si / No |
| **Affidabilita'** | Scarso, Buona, Discreta, Ottima |
| **Stato conservazione** | Insufficiente, Scarso, Buono, Discreto, Ottimo |

---

## Tab Dati Schedatura

Informazioni sulla compilazione della scheda.

<!-- IMMAGINE: Screenshot tab dati schedatura -->
![Tab Dati Schedatura](images/03_scheda_us/15_tab_schedatura.png)
*Figura 15: Tab Dati Schedatura*

### Ente e Responsabili

| Campo | Descrizione |
|-------|-------------|
| **Ente Responsabile** | Ente che gestisce lo scavo |
| **Soprintendenza** | SABAP di competenza |
| **Responsabile scientifico** | Direttore dello scavo |
| **Responsabile compilazione** | Chi ha compilato la scheda sul campo |
| **Responsabile rielaborazione** | Chi ha rielaborato i dati |

### Riferimenti

| Campo | Descrizione |
|-------|-------------|
| **Ref. TM** | Riferimento scheda TM (Tabella Materiali) |
| **Ref. RA** | Riferimento scheda RA (Reperti Archeologici) |
| **Ref. Pottery** | Riferimento scheda Ceramica |

### Date

| Campo | Formato |
|-------|---------|
| **Data rilevazione** | GG/MM/AAAA |
| **Data schedatura** | GG/MM/AAAA |
| **Data rielaborazione** | GG/MM/AAAA |

---

## Tab Misure US

Contiene tutte le misurazioni dell'unita stratigrafica.

<!-- IMMAGINE: Screenshot tab misure -->
![Tab Misure](images/03_scheda_us/16_tab_misure.png)
*Figura 16: Tab Misure US*

### Quote

| Campo | Descrizione | Unita |
|-------|-------------|-------|
| **Quota assoluta** | Quota sul livello del mare | metri |
| **Quota relativa** | Quota rispetto a punto di riferimento | metri |
| **Quota max assoluta** | Quota massima assoluta | metri |
| **Quota max relativa** | Quota massima relativa | metri |
| **Quota min assoluta** | Quota minima assoluta | metri |
| **Quota min relativa** | Quota minima relativa | metri |

### Dimensioni

| Campo | Descrizione | Unita |
|-------|-------------|-------|
| **Lunghezza max** | Lunghezza massima | metri |
| **Larghezza media** | Larghezza media | metri |
| **Altezza max** | Altezza massima | metri |
| **Altezza min** | Altezza minima | metri |
| **Spessore** | Spessore dello strato | metri |
| **Profondita max** | Profondita massima | metri |
| **Profondita min** | Profondita minima | metri |

---

## Tab Documentazione

Gestisce i riferimenti alla documentazione grafica e fotografica.

<!-- IMMAGINE: Screenshot tab documentazione -->
![Tab Documentazione](images/03_scheda_us/17_tab_documentazione.png)
*Figura 17: Tab Documentazione*

### Tabella Documentazione

| Colonna | Descrizione |
|---------|-------------|
| **Tipo documentazione** | Foto, Pianta, Sezione, Prospetto, ecc. |
| **Riferimenti** | Numero/codice del documento |

### Tipi di Documentazione

| Tipo | Descrizione |
|------|-------------|
| Foto | Documentazione fotografica |
| Pianta | Pianta di scavo |
| Sezione | Sezione stratigrafica |
| Prospetto | Prospetto murario |
| Rilievo | Rilievo grafico |
| 3D | Modello tridimensionale |

### Bottoni

| Bottone | Funzione |
|---------|----------|
| **inserisci riga** | Aggiunge riferimento |
| **rimuovi riga** | Rimuove riferimento |
| **Aggiorna doc** | Aggiorna dalla tabella documentazione |
| **Visualizza documentazione** | Mostra i documenti associati |

---

## Tab Tecnica Edilizia USM

Tab specifico per le Unita Stratigrafiche Murarie (USM).

<!-- IMMAGINE: Screenshot tab tecnica edilizia -->
![Tab Tecnica Edilizia](images/03_scheda_us/18_tab_tecnica_usm.png)
*Figura 18: Tab Tecnica Edilizia USM*

### Dati Specifici USM

| Campo | Descrizione |
|-------|-------------|
| **Lunghezza USM** | Lunghezza della muratura (metri) |
| **Altezza USM** | Altezza della muratura (metri) |
| **Superficie analizzata** | Percentuale analizzata |
| **Sezione muraria** | Tipo di sezione |
| **Modulo** | Modulo costruttivo |
| **Tipologia dell'opera** | Tipo di muratura |
| **Orientamento** | Orientamento della struttura |
| **Reimpiego** | Si / No |

### Materiali e Tecniche

| Sezione | Campi |
|---------|-------|
| **Laterizi** | Materiali, Lavorazione, Consistenza, Forma, Colore, Impasto, Posa in opera |
| **Elementi Litici** | Materiali, Lavorazione, Consistenza, Forma, Colore, Taglio, Posa in opera |

### Campioni

| Campo | Descrizione |
|-------|-------------|
| **Campioni malta** | Riferimenti campioni di malta |
| **Campioni mattone** | Riferimenti campioni di laterizi |
| **Campioni pietra** | Riferimenti campioni litici |

---

## Tab Leganti USM

Descrive le caratteristiche dei leganti (malta) nelle strutture murarie.

<!-- IMMAGINE: Screenshot tab leganti -->
![Tab Leganti](images/03_scheda_us/19_tab_leganti.png)
*Figura 19: Tab Leganti USM*

### Caratteristiche del Legante

| Campo | Descrizione |
|-------|-------------|
| **Tipo legante** | Malta, Fango, Assente, ecc. |
| **Consistenza** | Tenace, Friabile, ecc. |
| **Colore** | Colore del legante |
| **Rifinitura** | Tipo di rifinitura |
| **Spessore legante** | Spessore in cm |

### Composizione

| Sezione | Descrizione |
|---------|-------------|
| **Aggregati** | Componenti grossolani |
| **Inerti** | Componenti fini |
| **Inclusi** | Materiali inclusi |

---

## Tab Media

Visualizza le immagini associate all'unita stratigrafica.

<!-- IMMAGINE: Screenshot tab media -->
![Tab Media](images/03_scheda_us/20_tab_media.png)
*Figura 20: Tab Media*

### Lista US

La tabella mostra tutte le US con le immagini associate:
- Vai alla scheda
- Checkbox per selezione multipla
- Anteprima thumbnail

### Bottoni

| Bottone | Funzione |
|---------|----------|
| **Cerca immagini** | Ricerca immagini associate |
| **Save** | Salva associazioni |
| **Revert** | Annulla modifiche |

---

## Tab Help - Tool Box

Contiene strumenti avanzati per il controllo e l'esportazione.

<!-- IMMAGINE: Screenshot tab toolbox -->
![Tab Tool Box](images/03_scheda_us/21_tab_toolbox.png)
*Figura 21: Tab Tool Box*

### Sistemi di Controllo

| Strumento | Descrizione |
|-----------|-------------|
| **Check rapporti stratigrafici** | Verifica coerenza rapporti |
| **Check, go!!!!** | Esegue il controllo |

### Esportazione Matrix

| Bottone | Output |
|---------|--------|
| **Esporta Matrix** | File DOT per Graphviz |
| **Export Graphml** | File GraphML per yEd |
| **Export to Extended Matrix** | Formato S3DGraphy |
| **Interactive Matrix** | Visualizzazione interattiva |

### Strumenti Aggiuntivi

| Strumento | Descrizione |
|-----------|-------------|
| **Ordine stratigrafico** | Calcola sequenza stratigrafica |
| **Crea Codice Periodo** | Genera codici periodo |
| **csv2us** | Importa US da CSV |
| **Graphml2csv** | Esporta GraphML in CSV |

### Funzioni GIS

| Bottone | Funzione |
|---------|----------|
| **Disegna US** | Carica layer per disegno |
| **Preview pianta US** | Anteprima sulla mappa |
| **Apri schede US** | Apre schede selezionate |
| **Pan** | Strumento panoramica |
| **Mostra immagini** | Visualizza foto |

### Esportazioni Tavole

| Bottone | Output |
|---------|--------|
| **Esportazione Tavole** | Tavole di scavo |
| **symbology** | Gestione simbologia |
| **Open folder** | Apre cartella output |

---

## Matrix di Harris

Il Matrix di Harris e una rappresentazione grafica delle relazioni stratigrafiche.

<!-- IMMAGINE: Screenshot matrix harris -->
![Matrix Harris](images/03_scheda_us/22_matrix_harris.png)
*Figura 22: Esempio di Matrix di Harris*

<!-- VIDEO: Generazione Matrix di Harris -->
> **Video Tutorial**: [Inserire link video Matrix Harris]

### Generazione Matrix

1. Selezionare il sito e l'area
2. Verificare che i rapporti siano corretti
3. Andare su **Tab Help** → **Tool Box**
4. Cliccare **Export Matrix**

### Formati di Esportazione

| Formato | Software | Uso |
|---------|----------|-----|
| DOT | Graphviz | Visualizzazione base |
| GraphML | yEd, Gephi | Editing avanzato |
| Extended Matrix | S3DGraphy | Visualizzazione 3D |
| CSV | Excel | Analisi dati |

### Extended Matrix

L'Extended Matrix aggiunge informazioni supplementari:
- Periodizzazione
- Definizioni interpretative
- Dati cronologici
- Compatibilita con CIDOC-CRM

<!-- IMMAGINE: Screenshot extended matrix -->
![Extended Matrix](images/03_scheda_us/23_extended_matrix.png)
*Figura 23: Dialog Extended Matrix*

### Interactive Matrix

Visualizzazione interattiva del Matrix:
- Zoom e pan
- Selezione nodi
- Navigazione alle schede

---

## Funzionalita GIS

La Scheda US e strettamente integrata con QGIS.

<!-- IMMAGINE: Screenshot GIS integration -->
![GIS Integration](images/03_scheda_us/24_gis_integration.png)
*Figura 24: Integrazione GIS*

### Toolbar GIS

| Bottone | Funzione | Shortcut |
|---------|----------|----------|
| **GIS Viewer** | Carica layer US | Ctrl+G |
| **Preview pianta US** | Anteprima geometria | Ctrl+G |
| **Disegna US** | Attiva disegno | - |

### Layer GIS Associati

| Layer | Geometria | Descrizione |
|-------|-----------|-------------|
| PYUS | Poligono | Unita stratigrafiche |
| PYUSM | Poligono | Unita murarie |
| PYQUOTE | Punto | Quote |
| PYQUOTEUSM | Punto | Quote USM |
| PYUS_NEGATIVE | Poligono | US negative |

### Visualizzazione Risultati Ricerca

Quando la modalita GIS e attiva:
- Le ricerche vengono visualizzate sulla mappa
- I risultati sono evidenziati
- Si puo navigare tra i risultati

---

## Esportazioni

### Schede US PDF

1. Cliccare **Report** nella toolbar
2. Scegliere formato (PDF, Word)
3. Selezionare le schede da esportare

<!-- IMMAGINE: Screenshot esportazione PDF -->
![Esportazione PDF](images/03_scheda_us/25_esportazione_pdf.png)
*Figura 25: Opzioni esportazione PDF*

### Elenchi

| Tipo | Contenuto |
|------|-----------|
| **Elenco US** | Lista di tutte le US |
| **Elenco Foto con Thumbnail** | Lista con anteprime |
| **Elenco Foto senza Thumbnail** | Lista semplice |
| **Schede US** | Schede complete |

### Conversione Word

Il bottone **Converti in Word** permette di:
1. Selezionare un PDF
2. Convertirlo in formato DOCX
3. Editarlo in Word

---

## Workflow Operativo

### Creare una Nuova US

<!-- VIDEO: Workflow creazione US -->
> **Video Tutorial**: [Inserire link video creazione US]

#### Step 1: Aprire la Scheda
<!-- IMMAGINE: Step 1 -->
![Step 1](images/03_scheda_us/26_workflow_step1.png)

#### Step 2: Cliccare New Record
<!-- IMMAGINE: Step 2 -->
![Step 2](images/03_scheda_us/27_workflow_step2.png)

#### Step 3: Inserire Identificativi
- Selezionare Sito
- Inserire Area
- Inserire numero US
- Selezionare Tipo

<!-- IMMAGINE: Step 3 -->
![Step 3](images/03_scheda_us/28_workflow_step3.png)

#### Step 4: Definizioni
- Selezionare definizione stratigrafica
- Selezionare definizione interpretativa

<!-- IMMAGINE: Step 4 -->
![Step 4](images/03_scheda_us/29_workflow_step4.png)

#### Step 5: Descrizione
- Compilare la descrizione fisica
- Compilare l'interpretazione

<!-- IMMAGINE: Step 5 -->
![Step 5](images/03_scheda_us/30_workflow_step5.png)

#### Step 6: Rapporti Stratigrafici
- Inserire i rapporti con le altre US
- Creare i rapporti inversi

<!-- IMMAGINE: Step 6 -->
![Step 6](images/03_scheda_us/31_workflow_step6.png)

#### Step 7: Dati Fisici e Misure
- Compilare caratteristiche fisiche
- Inserire le misure

<!-- IMMAGINE: Step 7 -->
![Step 7](images/03_scheda_us/32_workflow_step7.png)

#### Step 8: Salvare
- Cliccare Save
- Verificare il salvataggio

<!-- IMMAGINE: Step 8 -->
![Step 8](images/03_scheda_us/33_workflow_step8.png)

### Generare il Matrix di Harris

1. Verificare tutti i rapporti siano inseriti
2. Eseguire il controllo rapporti
3. Correggere eventuali errori
4. Esportare il Matrix

### Collegare Documentazione

1. Creare prima le schede nella tabella Documentazione
2. Nella scheda US, tab Documentazione
3. Aggiungere i riferimenti
4. Verificare con "Visualizza documentazione"

---

## Risoluzione Problemi

### Errore nel salvataggio
- Verificare che Sito, Area e US siano compilati
- Verificare che la combinazione sia univoca

### Rapporti non coerenti
- Usare il controllo rapporti
- Verificare i rapporti inversi
- Correggere con il bottone Fix

### Matrix non si genera
- Verificare che Graphviz sia installato
- Controllare il percorso nella configurazione
- Verificare che ci siano rapporti

### Layer GIS non si caricano
- Verificare la connessione al database
- Controllare che esistano geometrie
- Verificare il sistema di riferimento

### Immagini non visualizzate
- Verificare i percorsi thumbnail
- Controllare le associazioni media
- Verificare permessi cartelle

---

## Note Tecniche

### Database

- **Tabella principale**: `us_table`
- **Campi principali**: oltre 80 campi
- **Chiave primaria**: `id_us`
- **Chiave composita**: sito + area + us

### Thesaurus

I campi con thesaurus (definizioni) usano la tabella `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' per definizione stratigrafica
- tipologia_sigla = '1.2' per definizione interpretativa

### Layer GIS

| Layer | Tabella | Tipo |
|-------|---------|------|
| PYUS | pyarchinit_us_view | Poligono |
| PYUSM | pyarchinit_usm_view | Poligono |
| PYQUOTE | pyarchinit_quote_view | Punto |

---

## Lista Immagini da Inserire

Per completare questa documentazione, inserire le seguenti immagini nella cartella `images/03_scheda_us/`:

| # | Nome File | Descrizione |
|---|-----------|-------------|
| 01 | `01_schema_rapporti.png` | Schema rapporti stratigrafici |
| 02 | `02_menu_scheda_us.png` | Menu accesso |
| 03 | `03_toolbar_us.png` | Toolbar |
| 04 | `04_interfaccia_completa.png` | Interfaccia con aree numerate |
| 05 | `05_toolbar_dbms.png` | Toolbar DBMS |
| 06 | `06_campi_identificativi.png` | Campi identificativi |
| 07 | `07_tab_localizzazione.png` | Tab Localizzazione |
| 08 | `08_tab_dati_descrittivi.png` | Tab Dati Descrittivi |
| 09 | `09_tab_periodizzazione.png` | Tab Periodizzazione |
| 10 | `10_tab_rapporti.png` | Tab Rapporti |
| 11 | `11_inserimento_rapporto.png` | Inserimento rapporto |
| 12 | `12_controllo_rapporti.png` | Controllo rapporti |
| 13 | `13_tab_em.png` | Tab Extended Matrix |
| 14 | `14_tab_dati_fisici.png` | Tab Dati Fisici |
| 15 | `15_tab_schedatura.png` | Tab Schedatura |
| 16 | `16_tab_misure.png` | Tab Misure |
| 17 | `17_tab_documentazione.png` | Tab Documentazione |
| 18 | `18_tab_tecnica_usm.png` | Tab Tecnica USM |
| 19 | `19_tab_leganti.png` | Tab Leganti |
| 20 | `20_tab_media.png` | Tab Media |
| 21 | `21_tab_toolbox.png` | Tab Tool Box |
| 22 | `22_matrix_harris.png` | Esempio Matrix |
| 23 | `23_extended_matrix.png` | Dialog Extended Matrix |
| 24 | `24_gis_integration.png` | Integrazione GIS |
| 25 | `25_esportazione_pdf.png` | Esportazione PDF |
| 26-33 | `26_workflow_step*.png` | Steps workflow |

## Lista Video da Inserire

| Placeholder | Descrizione |
|-------------|-------------|
| Video introduzione scheda US | Panoramica completa |
| Video rapporti stratigrafici | Come inserire rapporti |
| Video Matrix Harris | Generazione e export |
| Video creazione US | Workflow passo-passo |

---

*Documentazione PyArchInit - Scheda US/USM*
*Versione: 4.9.x*
*Ultimo aggiornamento: Gennaio 2026*
