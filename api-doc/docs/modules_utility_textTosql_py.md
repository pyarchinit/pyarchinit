# modules/utility/textTosql.py

## Overview

This file contains 26 documented elements.

## Classes

### Text2SQLWidget

Widget per l'interfaccia Text2SQL con modalità dual (API e locale)

**Inherits from**: QWidget

#### Methods

##### __init__(self, parent)

Initializes a `Text2SQLWidget` instance by calling the parent `QWidget` constructor with the optional `parent` argument. Stores the `parent` reference as an instance attribute and invokes `setup_ui()` to configure the user interface.

##### setup_ui(self)

Configura l'interfaccia utente

##### on_generate_clicked(self)

Gestisce il click sul pulsante di generazione

##### on_explain_clicked(self)

Gestisce il click sul pulsante di spiegazione

##### on_clear_clicked(self)

Pulisce l'interfaccia

##### on_copy_clicked(self)

Copia la query negli appunti

##### on_use_clicked(self)

Usa la query generata

### MakeSQL

Classe per generare SQL da linguaggio naturale usando diversi LLM

#### Methods

##### schema_to_text(metadata)

Converte lo schema del database in formato testuale

##### get_api_key(parent)

Ottiene l'API key di OpenAI dal file di configurazione

##### make_openai_request(prompt, db_type, parent)

Genera SQL usando OpenAI GPT-4

##### explain_openai_request(sql_query, parent)

Spiega una query SQL usando OpenAI

##### get_anthropic_api_key(parent)

Ottiene l'API key di Anthropic dal file di configurazione

##### make_anthropic_request(prompt, db_type, parent)

Genera SQL usando Anthropic Claude 4.6 Sonnet

##### check_ollama_status()

Verifica se Ollama è disponibile

##### get_ollama_models()

Ottiene la lista dei modelli Ollama disponibili

##### make_ollama_request(prompt, db_type, model, parent)

Genera SQL usando Ollama

##### explain_ollama_request(sql_query, model, parent)

Spiega una query SQL usando Ollama

##### clean_sql_query(sql_query)

Pulisce la query SQL rimuovendo elementi non necessari

##### make_query(prompt, db_type, config, parent)

Genera SQL usando qualunque provider (OpenAI/Anthropic/Ollama/LM Studio).

Ritorna (sql_query, explanation). Il prompt di sistema è uguale per
tutti i provider — l'unica differenza è il client che lo serve.

##### explain_query(sql_query, config, parent)

Spiega una query SQL usando il provider configurato.

##### make_api_request(prompt, db, apikey)

Metodo legacy per compatibilità - ora usa OpenAI GPT-4 invece di text2sql.ai

##### explain_request(prompt, apikey)

Metodo legacy per compatibilità - ora usa OpenAI GPT-4 invece di text2sql.ai

## Functions

### make_api_request(prompt, db, apikey)

Funzione legacy per compatibilità

**Parameters:**
- `prompt`
- `db`
- `apikey`

### explain_request(prompt, apikey)

Funzione legacy per compatibilità

**Parameters:**
- `prompt`
- `apikey`

