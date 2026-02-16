# Tutorial 30: AI Query Database (Text2SQL)

## Introducao

**AI Query Database** e uma funcionalidade avancada do PyArchInit que permite consultar a base de dados arqueologica utilizando **linguagem natural**. O sistema converte automaticamente perguntas em consultas SQL utilizando inteligencia artificial.

### Como Funciona

1. O utilizador escreve uma pergunta em ingles/italiano
2. A AI analisa o pedido
3. Gera a consulta SQL correspondente
4. Executa a consulta na base de dados
5. Devolve os resultados

### Exemplos de Perguntas

- *"Find all ceramic finds from the Roman Villa site"*
- *"Show Roman period SUs in area 1000"*
- *"How many individuals were found in the graves?"*
- *"List structures with medieval dating"*

## Acesso

### A Partir do Formulario UE/Achados
Separador dedicado **"AI Query"** ou **"Text2SQL"**

### Pelo Menu
**PyArchInit** > **AI Query Database**

## Interface

### Painel de Consulta

```
+--------------------------------------------------+
|         Geracao SQL com AI                        |
+--------------------------------------------------+
| Modo de Geracao:                                  |
|   (o) OpenAI GPT-4 (API ja configurada)          |
|   ( ) Ollama (modelo local)                      |
|   ( ) API Gratuita (se disponivel)               |
+--------------------------------------------------+
| Modelo Ollama: [llama3.2 v] [Verificar Ollama]   |
+--------------------------------------------------+
| Entrada:                                          |
|   Tipo de Base de Dados: [sqlite | postgresql]   |
|                                                  |
|   Descreva a consulta:                           |
|   +--------------------------------------------+ |
|   | Find all ceramic finds from the Roman      | |
|   | Villa site with dating between 1st-2nd c.  | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Gerar SQL]  [Limpar]                            |
+--------------------------------------------------+
| Consulta SQL Gerada:                              |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Roman Villa'                 | |
|   | AND tipo_reperto LIKE '%ceramic%'          | |
|   +--------------------------------------------+ |
| [Explicar Consulta] [Copiar Consulta] [Usar Consulta] |
+--------------------------------------------------+
| Explicacao:                                       |
|   A consulta seleciona todos os campos da...     |
+--------------------------------------------------+
```

## Modos de Geracao

### 1. OpenAI GPT-4

- **Requisitos**: Chave API OpenAI configurada
- **Qualidade**: Excelente
- **Custo**: Pagamento por utilizacao (API)
- **Velocidade**: Rapida

### 2. Ollama (Local)

- **Requisitos**: Ollama instalado e em execucao
- **Qualidade**: Boa-Excelente (depende do modelo)
- **Custo**: Gratuito
- **Velocidade**: Depende do hardware

### 3. API Gratuita

- **Requisitos**: Ligacao a Internet
- **Qualidade**: Variavel
- **Custo**: Gratuito
- **Limitacoes**: Possivel limitacao de taxa

## Configuracao

### OpenAI

1. Obter chave API de [OpenAI](https://platform.openai.com/)
2. Configurar em **PyArchInit** > **Configuracao** > **Chaves API**
3. Selecionar "OpenAI GPT-4" no modo

### Ollama

1. Instalar Ollama de [ollama.ai](https://ollama.ai/)
2. Iniciar Ollama: `ollama serve`
3. Descarregar modelo: `ollama pull llama3.2`
4. Selecionar "Ollama" e verificar ligacao

### Modelos Ollama Recomendados

| Modelo | Tamanho | Qualidade SQL |
|--------|---------|--------------|
| llama3.2 | 2GB | Boa |
| mistral | 4GB | Excelente |
| codellama | 7GB | Excelente para SQL |
| qwen2.5-coder | 4GB | Excelente para codigo |

## Utilizacao

### 1. Escrever a Pergunta

Na caixa de entrada, descrever o que pretende pesquisar:
- Utilizar linguagem natural
- Ser especifico quando possivel
- Mencionar tabelas/campos se conhecidos

### 2. Gerar SQL

1. Clicar em **"Gerar SQL"**
2. Aguardar processamento
3. Ver consulta gerada

### 3. Verificar Consulta

- Ler a consulta SQL gerada
- Clicar em **"Explicar Consulta"** para compreender
- Verificar correcao logica

### 4. Executar Consulta

- **"Copiar Consulta"**: Copiar para a area de transferencia
- **"Usar Consulta"**: Executar diretamente no sistema

## Esquema da Base de Dados

### Tabelas Principais

O sistema conhece o esquema do PyArchInit:

| Tabela | Descricao |
|--------|-----------|
| site_table | Sitios arqueologicos |
| us_table | Unidades Estratigraficas |
| inventario_materiali_table | Achados |
| pottery_table | Ceramica |
| tomba_table | Sepulturas |
| individui_table | Individuos |
| struttura_table | Estruturas |
| periodizzazione_table | Periodizacao |
| campioni_table | Amostras |
| documentazione_table | Documentacao |

### Campos Comuns

A AI conhece os campos principais:
- `sito` - Nome do sitio
- `area` - Numero da area
- `us` - Numero da UE
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Exemplos de Consultas

### Pesquisa de Achados

**Pergunta**: *"Find all bronze finds from the Ancient Rome site"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Ancient Rome'
AND (tipo_reperto LIKE '%bronze%' OR definizione LIKE '%bronze%')
```

### Contagem de UE

**Pergunta**: *"How many SUs are there per period at Villa Adriana site?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_su
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Pesquisa Espacial

**Pergunta**: *"Show SUs in area 1000 with elevations below 10 meters"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Boas Praticas

### 1. Perguntas Eficazes

- Ser especifico: nomes de sitios, numeros, datas
- Indicar o que pretende: lista, contagem, detalhes
- Mencionar filtros pretendidos

### 2. Verificacao de Resultados

- Verificar sempre a consulta gerada
- Utilizar "Explicar Consulta" se nao for claro
- Testar num subconjunto antes de consultas complexas

### 3. Iteracao

- Se o resultado estiver incorreto, reformular a pergunta
- Adicionar detalhes se a consulta for demasiado ampla
- Simplificar se a consulta for demasiado complexa

## Resolucao de Problemas

### Consulta Nao Gerada

**Causas**:
- API nao configurada
- Ligacao em falta
- Pergunta nao compreensivel

**Solucoes**:
- Verificar configuracao da API
- Verificar ligacao
- Reformular a pergunta

### Resultados Errados

**Causas**:
- Pergunta ambigua
- Campo/tabela inexistente

**Solucoes**:
- Ser mais especifico
- Verificar nomes de tabelas/campos

### Ollama Nao Responde

**Causas**:
- Ollama nao esta em execucao
- Modelo nao descarregado

**Solucoes**:
- Iniciar `ollama serve`
- Descarregar modelo necessario

## Referencias

### Ficheiros Fonte
- `modules/utility/textTosql.py` - Classe MakeSQL
- `modules/utility/database_schema.py` - Esquema da base de dados

### APIs Externas
- [API OpenAI](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Tutorial em Video

### AI Query Database
`[Placeholder: video_ai_query.mp4]`

**Conteudos**:
- Configuracao da API
- Escrever perguntas eficazes
- Interpretar resultados
- Boas praticas

**Duracao prevista**: 15-18 minutos

---

*Ultima atualizacao: janeiro de 2026*
