# Tutorial 08: Scheda Inventario Materiali

## Indice
1. [Introduzione](#introduzione)
2. [Accesso alla Scheda](#accesso-alla-scheda)
3. [Interfaccia Utente](#interfaccia-utente)
4. [Campi Principali](#campi-principali)
5. [Tab della Scheda](#tab-della-scheda)
6. [Toolbar DBMS](#toolbar-dbms)
7. [Gestione Media](#gestione-media)
8. [Funzionalita GIS](#funzionalita-gis)
9. [Quantificazioni e Statistiche](#quantificazioni-e-statistiche)
10. [Export e Report](#export-e-report)
11. [Integrazione AI](#integrazione-ai)
12. [Workflow Operativo](#workflow-operativo)
13. [Best Practices](#best-practices)
14. [Troubleshooting](#troubleshooting)

---

## Introduzione

La **Scheda Inventario Materiali** e lo strumento principale per la gestione dei reperti archeologici in PyArchInit. Permette di catalogare, descrivere e quantificare tutti i materiali rinvenuti durante lo scavo, dalle ceramiche ai metalli, dai vetri alle ossa animali.

### Scopo della Scheda

- Inventariare tutti i reperti rinvenuti
- Associare i reperti alle US di provenienza
- Gestire la classificazione tipologica
- Documentare le caratteristiche fisiche e tecnologiche
- Calcolare quantificazioni (forme minime, EVE, peso)
- Collegare foto e disegni ai reperti
- Generare report e statistiche

### Tipi di Materiali Gestibili

La scheda supporta diversi tipi di materiali:
- **Ceramica**: Vasellame, terrecotte, laterizi
- **Metalli**: Bronzo, ferro, piombo, oro, argento
- **Vetro**: Contenitori, vetro da finestra
- **Osso/Avorio**: Manufatti in materia dura animale
- **Pietra**: Strumenti litici, sculture
- **Monete**: Numismatica
- **Organici**: Legno, tessuti, cuoio

![Panoramica Scheda Inventario](images/08_scheda_inventario_materiali/01_panoramica.png)
*Figura 1: Vista generale della Scheda Inventario Materiali*

---

## Accesso alla Scheda

### Da Menu

1. Aprire QGIS con il plugin PyArchInit attivo
2. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Artefact form**

![Menu Inventario](images/08_scheda_inventario_materiali/02_menu_accesso.png)
*Figura 2: Accesso alla scheda dal menu*

### Da Toolbar

1. Individuare la toolbar PyArchInit
2. Cliccare sull'icona **Reperti** (icona anfora/vaso)

![Toolbar Inventario](images/08_scheda_inventario_materiali/03_toolbar_accesso.png)
*Figura 3: Icona nella toolbar*

### Scorciatoia da Tastiera

- **Ctrl+G**: Attiva/disattiva visualizzazione GIS del reperto corrente

---

## Interfaccia Utente

L'interfaccia e organizzata in tre aree principali:

![Interfaccia Completa](images/08_scheda_inventario_materiali/04_interfaccia_completa.png)
*Figura 4: Layout completo dell'interfaccia*

### Aree Principali

| Area | Descrizione |
|------|-------------|
| **1. Header** | DBMS Toolbar, indicatori stato, pulsanti GIS e export |
| **2. Campi Identificativi** | Sito, Area, US, Numero inventario, RA, Tipo reperto |
| **3. Campi Descrittivi** | Classe, Definizione, Stato conservazione, Datazione |
| **4. Tab Dettaglio** | 6 tab per dati specifici |

### Tab Disponibili

| Tab | Contenuto |
|-----|-----------|
| **Descrizione** | Testo descrittivo, media viewer, datazione |
| **Diapositive** | Gestione diapositive e negativi fotografici |
| **Dati quantitativi** | Elementi reperto, forme, misure ceramiche |
| **Tecnologie** | Tecniche produttive e decorative |
| **Rif Biblio** | Riferimenti bibliografici |
| **Quantificazioni** | Grafici e statistiche |

---

## Campi Principali

### Campi Identificativi

#### Sito
- **Tipo**: ComboBox (sola lettura dopo salvataggio)
- **Obbligatorio**: Si
- **Descrizione**: Sito archeologico di provenienza
- **Note**: Se impostato nella configurazione, precompilato automaticamente

#### Numero Inventario
- **Tipo**: LineEdit numerico
- **Obbligatorio**: Si
- **Descrizione**: Numero progressivo univoco del reperto all'interno del sito
- **Vincolo**: Univoco per sito

![Campi Identificativi](images/08_scheda_inventario_materiali/05_campi_identificativi.png)
*Figura 5: Campi identificativi principali*

#### Area
- **Tipo**: ComboBox editabile
- **Obbligatorio**: No
- **Descrizione**: Area di scavo di provenienza

#### US (Unita Stratigrafica)
- **Tipo**: LineEdit
- **Obbligatorio**: No (ma fortemente consigliato)
- **Descrizione**: Numero della US di rinvenimento
- **Collegamento**: Collega il reperto alla scheda US corrispondente

#### Struttura
- **Tipo**: ComboBox editabile
- **Obbligatorio**: No
- **Descrizione**: Struttura di appartenenza (se applicabile)
- **Note**: Si popola automaticamente in base alla US

#### RA (Reperto Archeologico)
- **Tipo**: LineEdit numerico
- **Obbligatorio**: No
- **Descrizione**: Numero di reperto archeologico (numerazione alternativa)
- **Note**: Usato per reperti particolarmente significativi

### Campi Classificazione

#### Tipo Reperto
- **Tipo**: ComboBox editabile
- **Obbligatorio**: Si
- **Valori tipici**: Ceramica, Metallo, Vetro, Osso, Pietra, Moneta, ecc.
- **Note**: Determina i campi specifici da compilare

![Tipo Reperto](images/08_scheda_inventario_materiali/06_tipo_reperto.png)
*Figura 6: Selezione tipo reperto*

#### Classe Materiale (Criterio Schedatura)
- **Tipo**: ComboBox editabile
- **Obbligatorio**: No
- **Descrizione**: Classe di appartenenza del materiale
- **Esempi per ceramica**:
  - Ceramica comune
  - Sigillata italica
  - Sigillata africana
  - Ceramica a vernice nera
  - Ceramica a pareti sottili
  - Anfore
  - Lucerne

#### Definizione
- **Tipo**: ComboBox editabile
- **Obbligatorio**: No
- **Descrizione**: Definizione tipologica specifica
- **Esempi**: Piatto, Coppa, Olla, Brocca, Coperchio, ecc.

#### Tipo
- **Tipo**: LineEdit
- **Obbligatorio**: No
- **Descrizione**: Tipologia specifica (es. Dressel 1, Hayes 50)

### Campi Stato e Conservazione

#### Lavato
- **Tipo**: ComboBox
- **Valori**: Si, No
- **Descrizione**: Indica se il reperto e stato lavato

#### Repertato
- **Tipo**: ComboBox
- **Valori**: Si, No
- **Descrizione**: Indica se il reperto e stato selezionato per lo studio

#### Diagnostico
- **Tipo**: ComboBox
- **Valori**: Si, No
- **Descrizione**: Indica se il reperto e diagnostico (utile per classificazione)

![Stato Reperto](images/08_scheda_inventario_materiali/07_stato_reperto.png)
*Figura 7: Campi stato del reperto*

#### Stato Conservazione
- **Tipo**: ComboBox editabile
- **Obbligatorio**: No
- **Valori tipici**: Integro, Frammentario, Lacunoso, Restaurato

### Campi Deposito

#### Nr. Cassa
- **Tipo**: LineEdit
- **Descrizione**: Numero della cassa di deposito

#### Tipo Contenitore
- **Tipo**: ComboBox editabile
- **Descrizione**: Tipo di contenitore (cassa, sacchetto, scatola)

#### Luogo di Conservazione
- **Tipo**: ComboBox editabile
- **Descrizione**: Magazzino o deposito di conservazione

#### Anno
- **Tipo**: ComboBox editabile
- **Descrizione**: Anno di rinvenimento

### Campi Schedatura

#### Compilatore
- **Tipo**: ComboBox editabile
- **Descrizione**: Nome dello schedatore

#### Punto Rinvenimento
- **Tipo**: LineEdit
- **Descrizione**: Coordinate o riferimento spaziale del punto di rinvenimento

---

## Tab della Scheda

### Tab 1: Descrizione

Il tab principale contiene la descrizione testuale del reperto e la gestione dei media.

![Tab Descrizione](images/08_scheda_inventario_materiali/08_tab_descrizione.png)
*Figura 8: Tab Descrizione*

#### Campo Descrizione
- **Tipo**: TextEdit multilinea
- **Contenuto suggerito**:
  - Forma generale
  - Parti conservate
  - Caratteristiche tecniche
  - Decorazioni
  - Confronti tipologici

#### Datazione Reperto
- **Tipo**: ComboBox editabile
- **Descrizione**: Inquadramento cronologico del reperto
- **Formato**: Testuale (es. "I sec. a.C.", "II-III sec. d.C.")

#### Media Viewer
Area per visualizzare le immagini associate al reperto:
- **Visualizza tutte le immagini**: Carica tutte le foto collegate
- **Cerca immagini**: Ricerca nelle immagini
- **Rimuovi tag**: Rimuove associazione immagine-reperto
- **SketchGPT**: Genera descrizione AI da immagine

### Tab 2: Diapositive

Gestione della documentazione fotografica tradizionale.

![Tab Diapositive](images/08_scheda_inventario_materiali/09_tab_diapositive.png)
*Figura 9: Tab Diapositive*

#### Tabella Diapositive
| Colonna | Descrizione |
|---------|-------------|
| Codice | Codice identificativo della diapositiva |
| N. | Numero progressivo |

#### Tabella Negativi
| Colonna | Descrizione |
|---------|-------------|
| Codice | Codice del rullino negativo |
| N. | Numero del fotogramma |

#### Campi Aggiuntivi
- **Photo ID**: Nomi delle foto associate (auto-popolato)
- **Drawing ID**: Nomi dei disegni associati (auto-popolato)

### Tab 3: Dati Quantitativi

Tab fondamentale per l'analisi quantitativa, specialmente per la ceramica.

![Tab Dati Quantitativi](images/08_scheda_inventario_materiali/10_tab_dati_quantitativi.png)
*Figura 10: Tab Dati Quantitativi*

#### Tabella Elementi Reperto
Permette di registrare i singoli elementi che compongono il reperto:

| Colonna | Descrizione | Esempio |
|---------|-------------|---------|
| Elemento rinvenuto | Parte anatomica del vaso | Orlo, Parete, Fondo, Ansa |
| Tipo di quantita | Stato del frammento | Frammento, Intero |
| Quantita | Numero di pezzi | 5 |

#### Campi Quantificazione Ceramica

| Campo | Descrizione |
|-------|-------------|
| **Forme minime** | Numero Minimo di Individui (NMI) |
| **Forme massime** | Numero Massimo di Individui |
| **Totale frammenti** | Conteggio automatico dalla tabella elementi |
| **Peso** | Peso in grammi |
| **Diametro orlo** | Diametro dell'orlo in cm |
| **EVE orlo** | Estimated Vessel Equivalent (percentuale orlo conservato) |

![Campi Ceramica](images/08_scheda_inventario_materiali/11_campi_ceramica.png)
*Figura 11: Campi specifici per ceramica*

#### Pulsante Calcolo Totale Frammenti
Calcola automaticamente il totale dei frammenti sommando le quantita dalla tabella elementi.

#### Tabella Misurazioni
Permette di registrare misure multiple:

| Colonna | Descrizione |
|---------|-------------|
| Tipo misura | Altezza, Larghezza, Spessore, ecc. |
| Unita di misura | cm, mm, m |
| Valore | Valore numerico |

### Tab 4: Tecnologie

Registrazione delle tecniche produttive e decorative.

![Tab Tecnologie](images/08_scheda_inventario_materiali/12_tab_tecnologie.png)
*Figura 12: Tab Tecnologie*

#### Tabella Tecnologie

| Colonna | Descrizione | Esempio |
|---------|-------------|---------|
| Tipo tecnologia | Categoria tecnica | Produzione, Decorazione |
| Posizione | Dove si trova | Interno, Esterno, Corpo |
| Quantita | Se applicabile | - |
| Unita di misura | Se applicabile | - |

#### Campi Specifici Ceramica

| Campo | Descrizione |
|-------|-------------|
| **Corpo ceramico** | Tipo di impasto (Depurato, Semidepurato, Grezzo) |
| **Rivestimento** | Tipo di rivestimento (Vernice, Ingobbio, Vetrina) |

### Tab 5: Riferimenti Bibliografici

Gestione della bibliografia di confronto.

![Tab Rif Biblio](images/08_scheda_inventario_materiali/13_tab_rif_biblio.png)
*Figura 13: Tab Riferimenti Bibliografici*

#### Tabella Riferimenti

| Colonna | Descrizione |
|---------|-------------|
| Autore | Cognome autore/i |
| Anno | Anno pubblicazione |
| Titolo | Titolo abbreviato |
| Pagina | Riferimento pagina |
| Figura | Riferimento figura/tavola |

### Tab 6: Quantificazioni

Tab per generare grafici e statistiche sui dati.

![Tab Quantificazioni](images/08_scheda_inventario_materiali/14_tab_quantificazioni.png)
*Figura 14: Tab Quantificazioni*

#### Tipi di Quantificazione Disponibili

| Tipo | Descrizione |
|------|-------------|
| **Forme minime** | Grafico per NMI |
| **Forme massime** | Grafico per numero massimo |
| **Totale frammenti** | Grafico per conteggio frammenti |
| **Peso** | Grafico per peso |
| **EVE orlo** | Grafico per EVE |

#### Parametri di Raggruppamento

I grafici possono essere raggruppati per:
- Tipo reperto
- Classe materiale
- Definizione
- Corpo ceramico
- Rivestimento
- Tipo
- Datazione
- RA
- Anno

---

## Toolbar DBMS

La toolbar offre tutti gli strumenti per la gestione dei record.

![Toolbar DBMS](images/08_scheda_inventario_materiali/15_toolbar_dbms.png)
*Figura 15: Toolbar DBMS completa*

### Pulsanti Standard

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| Connection test | Test connessione | Verifica connessione al database |
| First/Prev/Next/Last | Navigazione | Navigazione tra i record |
| New record | Nuovo | Crea nuovo reperto |
| Save | Salva | Salva modifiche |
| Delete | Elimina | Elimina reperto corrente |
| View all | Tutti | Visualizza tutti i record |
| New search | Ricerca | Attiva modalita ricerca |
| Search!!! | Esegui | Esegue la ricerca |
| Order by | Ordina | Ordina i record |

### Pulsanti Specifici

| Icona | Funzione | Descrizione |
|-------|----------|-------------|
| GIS | Visualizza GIS | Mostra reperto sulla mappa |
| PDF | Export PDF | Genera scheda PDF |
| Sheet | Export lista | Genera elenco PDF |
| Excel | Export Excel | Esporta in formato Excel/CSV |
| A5 | Export A5 | Genera etichetta formato A5 |
| Quant | Quantificazioni | Apre pannello quantificazioni |

---

## Gestione Media

### Associazione Immagini

![Gestione Media](images/08_scheda_inventario_materiali/16_gestione_media.png)
*Figura 16: Gestione media e immagini*

#### Drag & Drop
E possibile trascinare immagini direttamente nella lista per associarle al reperto.

#### Pulsanti Media

| Pulsante | Funzione |
|----------|----------|
| **Tutte le immagini** | Carica tutte le immagini associate |
| **Cerca immagini** | Apre ricerca nelle immagini |
| **Rimuovi tag** | Rimuove associazione corrente |

### Visualizzatore Immagini

Doppio click su un'immagine nella lista apre il visualizzatore completo con:
- Zoom
- Pan
- Rotazione
- Informazioni EXIF

### Video Player

Per reperti con video associati, e disponibile un player integrato per:
- Riproduzione video artefatti
- Visualizzazione modelli 3D (se disponibili)

---

## Funzionalita GIS

### Visualizzazione su Mappa

![GIS Integration](images/08_scheda_inventario_materiali/17_gis_integration.png)
*Figura 17: Reperto visualizzato su mappa*

#### Pulsante GIS (Toggle)
- **Attivo**: Il reperto viene evidenziato sulla mappa QGIS
- **Disattivo**: Nessuna visualizzazione
- **Scorciatoia**: Ctrl+G

#### Requisiti
- Il reperto deve avere la US di provenienza specificata
- La US deve avere una geometria nel layer GIS

### Collegamento da Mappa

E possibile selezionare un reperto cliccando sulla mappa:
1. Attivare lo strumento di selezione in QGIS
2. Cliccare sulla US di interesse
3. I reperti della US vengono filtrati nella scheda

---

## Quantificazioni e Statistiche

### Accesso alle Quantificazioni

1. Cliccare sul pulsante **Quant** nella toolbar
2. Selezionare il tipo di quantificazione
3. Selezionare i parametri di raggruppamento
4. Cliccare OK

![Pannello Quantificazioni](images/08_scheda_inventario_materiali/18_pannello_quant.png)
*Figura 18: Pannello selezione quantificazioni*

### Tipi di Grafici

#### Grafico a Barre
Visualizza la distribuzione per categoria selezionata.

![Grafico Barre](images/08_scheda_inventario_materiali/19_grafico_barre.png)
*Figura 19: Esempio grafico a barre*

### Export Quantificazioni

I dati delle quantificazioni vengono esportati automaticamente in:
- File CSV nella cartella `pyarchinit_Quantificazioni_folder`
- Grafico visualizzato a schermo

---

## Export e Report

### Export PDF Scheda Singola

![Export PDF](images/08_scheda_inventario_materiali/20_export_pdf.png)
*Figura 20: Pulsante export PDF*

Genera una scheda PDF completa del reperto corrente con:
- Tutti i dati identificativi
- Descrizione
- Dati quantitativi
- Riferimenti bibliografici
- Immagini associate (se disponibili)

### Export PDF Lista

Genera un elenco PDF di tutti i reperti visualizzati (risultato ricerca corrente):
- Tabella riepilogativa
- Dati essenziali per ogni reperto

### Export A5 (Etichette)

![Export A5](images/08_scheda_inventario_materiali/21_export_a5.png)
*Figura 21: Esempio etichetta A5*

Genera etichette formato A5 per:
- Identificazione casse
- Etichettatura reperti
- Schede mobili

Configurazione percorso PDF:
1. Cliccare sull'icona cartella accanto al campo percorso
2. Selezionare la cartella di destinazione
3. Cliccare "Esporta A5"

### Export Excel/CSV

Esporta i dati in formato tabellare per:
- Elaborazioni statistiche esterne
- Import in altri software
- Archiviazione

---

## Integrazione AI

### SketchGPT

![SketchGPT](images/08_scheda_inventario_materiali/22_sketchgpt.png)
*Figura 22: Pulsante SketchGPT*

Funzionalita AI per generare automaticamente descrizioni dei reperti a partire da immagini.

#### Utilizzo

1. Associare un'immagine al reperto
2. Cliccare sul pulsante **SketchGPT**
3. Selezionare l'immagine da analizzare
4. Selezionare il modello GPT (gpt-4-vision, gpt-4o)
5. Il sistema genera una descrizione archeologica

#### Output

La descrizione generata include:
- Identificazione del tipo di reperto
- Descrizione delle caratteristiche visibili
- Possibili confronti tipologici
- Suggerimenti di datazione

> **Nota**: Richiede API Key OpenAI configurata.

---

## Workflow Operativo

### Creazione di un Nuovo Reperto

#### Passo 1: Apertura Scheda
1. Aprire la Scheda Inventario Materiali
2. Verificare la connessione al database

![Workflow Step 1](images/08_scheda_inventario_materiali/23_workflow_step1.png)
*Figura 23: Apertura scheda*

#### Passo 2: Nuovo Record
1. Cliccare **New record**
2. Lo Status cambia in "Nuovo Record"

![Workflow Step 2](images/08_scheda_inventario_materiali/24_workflow_step2.png)
*Figura 24: Nuovo record*

#### Passo 3: Dati Identificativi
1. Verificare/selezionare il **Sito**
2. Inserire il **Numero inventario** (progressivo)
3. Inserire **Area** e **US** di provenienza

![Workflow Step 3](images/08_scheda_inventario_materiali/25_workflow_step3.png)
*Figura 25: Dati identificativi*

#### Passo 4: Classificazione
1. Selezionare il **Tipo reperto**
2. Selezionare la **Classe materiale**
3. Selezionare/inserire la **Definizione**

![Workflow Step 4](images/08_scheda_inventario_materiali/26_workflow_step4.png)
*Figura 26: Classificazione*

#### Passo 5: Descrizione
1. Compilare il campo **Descrizione** nel tab Descrizione
2. Selezionare la **Datazione**
3. Associare eventuali immagini

![Workflow Step 5](images/08_scheda_inventario_materiali/27_workflow_step5.png)
*Figura 27: Descrizione*

#### Passo 6: Dati Quantitativi (se ceramica)
1. Aprire il tab **Dati quantitativi**
2. Inserire gli elementi nella tabella
3. Compilare forme minime/massime
4. Inserire peso e misure

![Workflow Step 6](images/08_scheda_inventario_materiali/28_workflow_step6.png)
*Figura 28: Dati quantitativi*

#### Passo 7: Deposito
1. Inserire **Nr. cassa**
2. Selezionare **Luogo conservazione**
3. Indicare **Stato conservazione**

![Workflow Step 7](images/08_scheda_inventario_materiali/29_workflow_step7.png)
*Figura 29: Dati deposito*

#### Passo 8: Salvataggio
1. Cliccare **Save**
2. Verificare il messaggio di conferma
3. Il record e ora salvato nel database

![Workflow Step 8](images/08_scheda_inventario_materiali/30_workflow_step8.png)
*Figura 30: Salvataggio*

### Ricerca Reperti

#### Ricerca Semplice
1. Cliccare **New search**
2. Compilare i campi di ricerca desiderati
3. Cliccare **Search!!!**

#### Ricerca per US
1. Attivare ricerca
2. Inserire solo il numero US nel campo US
3. Eseguire ricerca

---

## Best Practices

### Numerazione Inventario

- Usare numerazione progressiva senza interruzioni
- Un numero = un reperto (o gruppo omogeneo)
- Documentare il criterio di inventariazione

### Classificazione

- Utilizzare vocabolari controllati per le classi
- Mantenere coerenza nella definizione dei tipi
- Aggiornare il thesaurus quando necessario

### Quantificazione Ceramica

Per una corretta quantificazione:
1. **Forme minime (NMI)**: Contare solo elementi diagnostici (orli, fondi distintivi)
2. **EVE**: Misurare la percentuale di circonferenza conservata
3. **Peso**: Pesare tutti i frammenti del gruppo

### Documentazione Fotografica

- Fotografare tutti i reperti diagnostici
- Usare scala metrica nelle foto
- Associare le foto tramite il media manager

### Collegamento US

- Verificare sempre che la US esista prima di associarla
- Per reperti da pulizia/superficie, usare US appropriate
- Documentare i casi di reperti fuori contesto

---

## Troubleshooting

### Problemi Comuni

#### Numero inventario duplicato
- **Errore**: "Esiste gia un record con questo numero inventario"
- **Causa**: Il numero e gia utilizzato per il sito
- **Soluzione**: Verificare il prossimo numero disponibile con "View all"

#### Immagini non visualizzate
- **Causa**: Path delle immagini non corretto
- **Soluzione**:
  1. Verificare configurazione path in Settings
  2. Verificare che le immagini siano nella cartella corretta
  3. Riassociare le immagini

#### Quantificazioni vuote
- **Causa**: Campi quantitativi non compilati
- **Soluzione**: Compilare forme minime/massime o totale frammenti

#### Export PDF vuoto
- **Causa**: Nessun record selezionato
- **Soluzione**: Verificare di avere almeno un record visualizzato

#### GIS non funziona
- **Causa**: US non ha geometria o layer non caricato
- **Soluzione**:
  1. Verificare che il layer US sia caricato in QGIS
  2. Verificare che la US abbia una geometria associata

---

## Video Tutorial

### Video 1: Panoramica Scheda Inventario
*Durata: 5-6 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Interfaccia generale
- Navigazione tra i tab
- Funzionalita principali

### Video 2: Schedatura Ceramica Completa
*Durata: 8-10 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Compilazione tutti i campi
- Quantificazione ceramica
- Elementi del reperto
- Tecnologie

### Video 3: Gestione Media e Foto
*Durata: 4-5 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Associazione immagini
- Visualizzatore
- SketchGPT

### Video 4: Export e Quantificazioni
*Durata: 5-6 minuti*

[Placeholder per video tutorial]

**Contenuti:**
- Export PDF
- Export Excel
- Grafici quantificazioni

---

## Riepilogo Campi Database

| Campo | Tipo | Database | Obbligatorio |
|-------|------|----------|--------------|
| Sito | Text | sito | Si |
| Numero inventario | Integer | numero_inventario | Si |
| Tipo reperto | Text | tipo_reperto | Si |
| Classe materiale | Text | criterio_schedatura | No |
| Definizione | Text | definizione | No |
| Descrizione | Text | descrizione | No |
| Area | Text | area | No |
| US | Text | us | No |
| Lavato | String(3) | lavato | No |
| Nr. cassa | Text | nr_cassa | No |
| Luogo conservazione | Text | luogo_conservazione | No |
| Stato conservazione | String(200) | stato_conservazione | No |
| Datazione | String(200) | datazione_reperto | No |
| Forme minime | Integer | forme_minime | No |
| Forme massime | Integer | forme_massime | No |
| Totale frammenti | Integer | totale_frammenti | No |
| Corpo ceramico | String(200) | corpo_ceramico | No |
| Rivestimento | String(200) | rivestimento | No |
| Diametro orlo | Numeric | diametro_orlo | No |
| Peso | Numeric | peso | No |
| Tipo | String(200) | tipo | No |
| EVE orlo | Numeric | eve_orlo | No |
| Repertato | String(3) | repertato | No |
| Diagnostico | String(3) | diagnostico | No |
| RA | Integer | n_reperto | No |
| Tipo contenitore | String(200) | tipo_contenitore | No |
| Struttura | String(200) | struttura | No |
| Anno | Integer | years | No |

---

*Ultimo aggiornamento: Gennaio 2026*
*PyArchInit - Archaeological Data Management*
