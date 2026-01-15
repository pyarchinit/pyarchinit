# Tutorial 30: AI Query Database (Text2SQL)

## Introduzione

**AI Query Database** e una funzionalita avanzata di PyArchInit che permette di interrogare il database archeologico usando il **linguaggio naturale**. Il sistema converte automaticamente le domande in query SQL grazie all'intelligenza artificiale.

### Come Funziona

1. L'utente scrive una domanda in italiano/inglese
2. L'AI analizza la richiesta
3. Genera la query SQL corrispondente
4. Esegue la query sul database
5. Restituisce i risultati

### Esempi di Domande

- *"Trova tutti i reperti ceramici del sito Villa Romana"*
- *"Mostra le US del periodo romano nell'area 1000"*
- *"Quanti individui sono stati trovati nelle tombe?"*
- *"Elenca le strutture con datazione medievale"*

## Accesso

### Dalla Scheda US/Reperti
Tab dedicato **"AI Query"** o **"Text2SQL"**

### Dal Menu
**PyArchInit** → **AI Query Database**

## Interfaccia

### Pannello Query

```
+--------------------------------------------------+
|         Generazione SQL con AI                    |
+--------------------------------------------------+
| Modalita di Generazione:                          |
|   (o) OpenAI GPT-4 (API gia configurata)         |
|   ( ) Ollama (modello locale)                    |
|   ( ) API gratuita (se disponibile)              |
+--------------------------------------------------+
| Modello Ollama: [llama3.2 v] [Verifica Ollama]   |
+--------------------------------------------------+
| Input:                                            |
|   Tipo Database: [sqlite | postgresql]           |
|                                                  |
|   Descrivi la query:                             |
|   +--------------------------------------------+ |
|   | Trova tutti i reperti ceramici dal sito    | |
|   | Villa Romana con datazione tra I e II sec  | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Genera SQL]  [Pulisci]                          |
+--------------------------------------------------+
| Query SQL Generata:                               |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Villa Romana'                | |
|   | AND tipo_reperto LIKE '%ceramic%'          | |
|   +--------------------------------------------+ |
| [Spiega Query] [Copia Query] [Usa Query]        |
+--------------------------------------------------+
| Spiegazione:                                      |
|   La query seleziona tutti i campi dalla...      |
+--------------------------------------------------+
```

## Modalita di Generazione

### 1. OpenAI GPT-4

- **Requisiti**: API key OpenAI configurata
- **Qualita**: Eccellente
- **Costo**: A consumo (API)
- **Velocita**: Veloce

### 2. Ollama (Locale)

- **Requisiti**: Ollama installato e in esecuzione
- **Qualita**: Buona-Ottima (dipende dal modello)
- **Costo**: Gratuito
- **Velocita**: Dipende da hardware

### 3. API Gratuita

- **Requisiti**: Connessione internet
- **Qualita**: Variabile
- **Costo**: Gratuito
- **Limitazioni**: Rate limiting possibile

## Configurazione

### OpenAI

1. Ottenere API key da [OpenAI](https://platform.openai.com/)
2. Configurare in **PyArchInit** → **Configurazione** → **API Keys**
3. Selezionare "OpenAI GPT-4" nella modalita

### Ollama

1. Installare Ollama da [ollama.ai](https://ollama.ai/)
2. Avviare Ollama: `ollama serve`
3. Scaricare modello: `ollama pull llama3.2`
4. Selezionare "Ollama" e verificare connessione

### Modelli Ollama Consigliati

| Modello | Dimensione | Qualita SQL |
|---------|------------|-------------|
| llama3.2 | 2GB | Buona |
| mistral | 4GB | Ottima |
| codellama | 7GB | Eccellente per SQL |
| qwen2.5-coder | 4GB | Ottima per codice |

## Utilizzo

### 1. Scrivere la Domanda

Nella casella di input, descrivere cosa si vuole cercare:
- Usare linguaggio naturale
- Essere specifici quando possibile
- Menzionare tabelle/campi se noti

### 2. Generare SQL

1. Cliccare **"Genera SQL"**
2. Attendere elaborazione
3. Visualizzare query generata

### 3. Verificare Query

- Leggere la query SQL generata
- Cliccare **"Spiega Query"** per comprendere
- Verificare correttezza logica

### 4. Eseguire Query

- **"Copia Query"**: Copia negli appunti
- **"Usa Query"**: Esegue direttamente nel sistema

## Schema Database

### Tabelle Principali

Il sistema conosce lo schema PyArchInit:

| Tabella | Descrizione |
|---------|-------------|
| site_table | Siti archeologici |
| us_table | Unita Stratigrafiche |
| inventario_materiali_table | Reperti |
| pottery_table | Ceramica |
| tomba_table | Tombe |
| individui_table | Individui |
| struttura_table | Strutture |
| periodizzazione_table | Periodizzazione |
| campioni_table | Campioni |
| documentazione_table | Documentazione |

### Campi Comuni

L'AI conosce i campi principali:
- `sito` - Nome sito
- `area` - Numero area
- `us` - Numero US
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Esempi di Query

### Ricerca Reperti

**Domanda**: *"Trova tutti i reperti in bronzo del sito Roma Antica"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Roma Antica'
AND (tipo_reperto LIKE '%bronzo%' OR definizione LIKE '%bronzo%')
```

### Conteggio US

**Domanda**: *"Quante US ci sono per ogni periodo nel sito Villa Adriana?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_us
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Ricerca Spaziale

**Domanda**: *"Mostra le US dell'area 1000 con quote inferiori a 10 metri"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Best Practices

### 1. Domande Efficaci

- Essere specifici: nomi siti, numeri, date
- Indicare cosa si vuole: lista, conteggio, dettagli
- Menzionare filtri desiderati

### 2. Verifica Risultati

- Sempre controllare la query generata
- Usare "Spiega Query" se non chiaro
- Testare su subset prima di query complesse

### 3. Iterazione

- Se risultato non corretto, riformulare domanda
- Aggiungere dettagli se query troppo ampia
- Semplificare se query troppo complessa

## Risoluzione Problemi

### Query Non Generata

**Cause**:
- API non configurata
- Connessione mancante
- Domanda non comprensibile

**Soluzioni**:
- Verificare configurazione API
- Controllare connessione
- Riformulare domanda

### Risultati Errati

**Cause**:
- Domanda ambigua
- Campo/tabella non esistente

**Soluzioni**:
- Essere piu specifici
- Verificare nomi tabelle/campi

### Ollama Non Risponde

**Cause**:
- Ollama non in esecuzione
- Modello non scaricato

**Soluzioni**:
- Avviare `ollama serve`
- Scaricare modello richiesto

## Riferimenti

### File Sorgente
- `modules/utility/textTosql.py` - Classe MakeSQL
- `modules/utility/database_schema.py` - Schema database

### API Esterne
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Video Tutorial

### AI Query Database
`[Placeholder: video_ai_query.mp4]`

**Contenuti**:
- Configurazione API
- Scrittura domande efficaci
- Interpretazione risultati
- Best practices

**Durata prevista**: 15-18 minuti

---

*Ultimo aggiornamento: Gennaio 2026*
