# PyArchInit Text2SQL - Guida all'uso

## ⚠️ Importante: Migrazione da text2sql.ai a OpenAI GPT-4

**Il sistema ora utilizza automaticamente OpenAI GPT-4 invece di text2sql.ai**, anche quando viene chiamato il vecchio metodo. Questo significa:
- Non è più necessaria l'API key di text2sql.ai
- Le query utilizzano la stessa API key OpenAI già configurata per PyArchInit
- Migliore qualità delle query SQL generate
- Supporto nativo per query geometriche complesse

## Panoramica

Il nuovo sistema Text2SQL di PyArchInit permette di generare query SQL complesse usando il linguaggio naturale. Supporta tre modalità:

1. **OpenAI GPT-4** - Utilizza l'API key già configurata per PyArchInit
2. **Ollama** - Modello locale gratuito, nessun costo per query
3. **API Gratuita** - In sviluppo

## Caratteristiche principali

- ✅ Supporto per query geometriche complesse (PostGIS/Spatialite)
- ✅ Spiegazione dettagliata delle query prima dell'esecuzione
- ✅ Integrazione con lo schema del database PyArchInit
- ✅ Supporto per PostgreSQL, SQLite, MySQL e SQL Server

## Configurazione

### OpenAI GPT-4
L'API key viene automaticamente letta dal file:
```
~/.pyarchinit/bin/gpt_api_key.txt
```
Questa è la stessa chiave usata per altre funzionalità AI di PyArchInit.

### Ollama (Locale)
1. Installa Ollama: https://ollama.ai
2. Avvia Ollama: `ollama serve`
3. Scarica un modello: `ollama pull llama3.2` o `ollama pull codellama`
4. Seleziona "Ollama" nell'interfaccia e verifica la connessione

## Esempi di query

### Query archeologiche standard
- "Trova tutti i reperti ceramici dal sito con ID 1 che hanno datazione tra 100 e 200 d.C."
- "Mostra tutte le US del periodo romano con interpretazione 'strato di crollo'"
- "Elenca le tombe con corredo funerario contenente oggetti in bronzo"

### Query geometriche
- "Trova tutte le strutture entro 50 metri dalla US con numero 100"
- "Mostra le US che si sovrappongono spazialmente alla struttura STR001"
- "Trova i reperti localizzati nell'area delimitata dalle coordinate X1,Y1,X2,Y2"

### Query complesse con JOIN
- "Mostra tutti i reperti ceramici trovati in US datate al II secolo d.C. raggruppati per tipo"
- "Elenca le strutture con le relative US e i materiali associati, ordinate per periodo"

## Funzionalità

1. **Genera SQL**: Converte la descrizione in linguaggio naturale in SQL
2. **Spiega Query**: Fornisce una spiegazione dettagliata di cosa fa la query
3. **Copia Query**: Copia la query negli appunti
4. **Usa Query**: Inserisce la query direttamente nel campo SQL dell'interfaccia

## Note tecniche

- Le query geometriche utilizzano le funzioni standard PostGIS/Spatialite
- Il sistema conosce automaticamente lo schema completo del database PyArchInit
- Le spiegazioni sono fornite in italiano con esempi archeologici concreti
- Per query molto complesse, OpenAI GPT-4 fornisce risultati migliori

## Costi

- **OpenAI GPT-4**: ~$0.01-0.03 per query (dipende dalla complessità)
- **Ollama**: Gratuito (esecuzione locale)
- **API Gratuita**: In sviluppo

## Risoluzione problemi

### Ollama non si connette
- Verifica che Ollama sia in esecuzione: `ollama list`
- Controlla che la porta 11434 sia disponibile
- Riavvia Ollama: `ollama serve`

### Errore API OpenAI
- Verifica che l'API key sia valida
- Controlla il credito disponibile su OpenAI
- L'API key deve avere accesso a GPT-4

### Query non corrette
- Sii più specifico nella descrizione
- Usa i nomi esatti delle tabelle quando li conosci
- Per query geometriche, specifica sempre l'unità di misura (metri)