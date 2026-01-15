# Tutorial 30: AI Query Database (Text2SQL)

## Introduction

**AI Query Database** is an advanced PyArchInit feature that allows querying the archaeological database using **natural language**. The system automatically converts questions into SQL queries using artificial intelligence.

### How It Works

1. User writes a question in English/Italian
2. AI analyzes the request
3. Generates corresponding SQL query
4. Executes query on database
5. Returns results

### Example Questions

- *"Find all ceramic finds from the Roman Villa site"*
- *"Show Roman period SUs in area 1000"*
- *"How many individuals were found in the graves?"*
- *"List structures with medieval dating"*

## Access

### From SU/Finds Form
Dedicated **"AI Query"** or **"Text2SQL"** tab

### From Menu
**PyArchInit** → **AI Query Database**

## Interface

### Query Panel

```
+--------------------------------------------------+
|         SQL Generation with AI                    |
+--------------------------------------------------+
| Generation Mode:                                  |
|   (o) OpenAI GPT-4 (API already configured)      |
|   ( ) Ollama (local model)                       |
|   ( ) Free API (if available)                    |
+--------------------------------------------------+
| Ollama Model: [llama3.2 v] [Verify Ollama]       |
+--------------------------------------------------+
| Input:                                            |
|   Database Type: [sqlite | postgresql]           |
|                                                  |
|   Describe the query:                            |
|   +--------------------------------------------+ |
|   | Find all ceramic finds from the Roman      | |
|   | Villa site with dating between 1st-2nd c.  | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Generate SQL]  [Clear]                          |
+--------------------------------------------------+
| Generated SQL Query:                              |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Roman Villa'                 | |
|   | AND tipo_reperto LIKE '%ceramic%'          | |
|   +--------------------------------------------+ |
| [Explain Query] [Copy Query] [Use Query]         |
+--------------------------------------------------+
| Explanation:                                      |
|   The query selects all fields from the...       |
+--------------------------------------------------+
```

## Generation Modes

### 1. OpenAI GPT-4

- **Requirements**: OpenAI API key configured
- **Quality**: Excellent
- **Cost**: Pay per use (API)
- **Speed**: Fast

### 2. Ollama (Local)

- **Requirements**: Ollama installed and running
- **Quality**: Good-Excellent (depends on model)
- **Cost**: Free
- **Speed**: Depends on hardware

### 3. Free API

- **Requirements**: Internet connection
- **Quality**: Variable
- **Cost**: Free
- **Limitations**: Rate limiting possible

## Configuration

### OpenAI

1. Get API key from [OpenAI](https://platform.openai.com/)
2. Configure in **PyArchInit** → **Configuration** → **API Keys**
3. Select "OpenAI GPT-4" in mode

### Ollama

1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Start Ollama: `ollama serve`
3. Download model: `ollama pull llama3.2`
4. Select "Ollama" and verify connection

### Recommended Ollama Models

| Model | Size | SQL Quality |
|-------|------|-------------|
| llama3.2 | 2GB | Good |
| mistral | 4GB | Excellent |
| codellama | 7GB | Excellent for SQL |
| qwen2.5-coder | 4GB | Excellent for code |

## Usage

### 1. Write the Question

In the input box, describe what you want to search:
- Use natural language
- Be specific when possible
- Mention tables/fields if known

### 2. Generate SQL

1. Click **"Generate SQL"**
2. Wait for processing
3. View generated query

### 3. Verify Query

- Read the generated SQL query
- Click **"Explain Query"** to understand
- Verify logical correctness

### 4. Execute Query

- **"Copy Query"**: Copy to clipboard
- **"Use Query"**: Execute directly in system

## Database Schema

### Main Tables

The system knows the PyArchInit schema:

| Table | Description |
|-------|-------------|
| site_table | Archaeological sites |
| us_table | Stratigraphic Units |
| inventario_materiali_table | Finds |
| pottery_table | Pottery |
| tomba_table | Graves |
| individui_table | Individuals |
| struttura_table | Structures |
| periodizzazione_table | Periodization |
| campioni_table | Samples |
| documentazione_table | Documentation |

### Common Fields

The AI knows main fields:
- `sito` - Site name
- `area` - Area number
- `us` - SU number
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Query Examples

### Find Search

**Question**: *"Find all bronze finds from the Ancient Rome site"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Ancient Rome'
AND (tipo_reperto LIKE '%bronze%' OR definizione LIKE '%bronze%')
```

### SU Count

**Question**: *"How many SUs are there per period at Villa Adriana site?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_su
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Spatial Search

**Question**: *"Show SUs in area 1000 with elevations below 10 meters"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Best Practices

### 1. Effective Questions

- Be specific: site names, numbers, dates
- Indicate what you want: list, count, details
- Mention desired filters

### 2. Result Verification

- Always check the generated query
- Use "Explain Query" if unclear
- Test on subset before complex queries

### 3. Iteration

- If result incorrect, reformulate question
- Add details if query too broad
- Simplify if query too complex

## Troubleshooting

### Query Not Generated

**Causes**:
- API not configured
- Missing connection
- Question not understandable

**Solutions**:
- Verify API configuration
- Check connection
- Reformulate question

### Wrong Results

**Causes**:
- Ambiguous question
- Non-existent field/table

**Solutions**:
- Be more specific
- Verify table/field names

### Ollama Not Responding

**Causes**:
- Ollama not running
- Model not downloaded

**Solutions**:
- Start `ollama serve`
- Download required model

## References

### Source Files
- `modules/utility/textTosql.py` - MakeSQL class
- `modules/utility/database_schema.py` - Database schema

### External APIs
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Video Tutorial

### AI Query Database
`[Placeholder: video_ai_query.mp4]`

**Contents**:
- API configuration
- Writing effective questions
- Interpreting results
- Best practices

**Expected duration**: 15-18 minutes

---

*Last updated: January 2026*
