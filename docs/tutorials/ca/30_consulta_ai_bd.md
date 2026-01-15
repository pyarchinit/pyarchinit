# Tutorial 30: Consulta AI Base de Dades (Text2SQL)

## Introducció

**Consulta AI Base de Dades** és una funcionalitat avançada de PyArchInit que permet interrogar la base de dades arqueològica usant el **llenguatge natural**. El sistema converteix automàticament les preguntes en consultes SQL gràcies a la intel·ligència artificial.

### Com Funciona

1. L'usuari escriu una pregunta en català/anglès
2. La IA analitza la sol·licitud
3. Genera la consulta SQL corresponent
4. Executa la consulta a la base de dades
5. Retorna els resultats

### Exemples de Preguntes

- *"Troba totes les troballes ceràmiques del lloc Vil·la Romana"*
- *"Mostra les US del període romà a l'àrea 1000"*
- *"Quants individus s'han trobat a les tombes?"*
- *"Llista les estructures amb datació medieval"*

## Accés

### Des de la Fitxa US/Troballes
Tab dedicat **"AI Query"** o **"Text2SQL"**

### Des del Menú
**PyArchInit** → **AI Query Database**

## Interfície

### Panell Consulta

```
+--------------------------------------------------+
|         Generació SQL amb AI                      |
+--------------------------------------------------+
| Modalitat de Generació:                           |
|   (o) OpenAI GPT-4 (API ja configurada)          |
|   ( ) Ollama (model local)                       |
|   ( ) API gratuïta (si disponible)               |
+--------------------------------------------------+
| Model Ollama: [llama3.2 v] [Verifica Ollama]     |
+--------------------------------------------------+
| Entrada:                                          |
|   Tipus Base de Dades: [sqlite | postgresql]     |
|                                                  |
|   Descriu la consulta:                           |
|   +--------------------------------------------+ |
|   | Troba totes les troballes ceràmiques del   | |
|   | lloc Vil·la Romana amb datació I-II s.     | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Genera SQL]  [Neteja]                           |
+--------------------------------------------------+
| Consulta SQL Generada:                            |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Vil·la Romana'               | |
|   | AND tipo_reperto LIKE '%ceramic%'          | |
|   +--------------------------------------------+ |
| [Explica Consulta] [Copia Consulta] [Usa Consulta]|
+--------------------------------------------------+
| Explicació:                                       |
|   La consulta selecciona tots els camps de la... |
+--------------------------------------------------+
```

## Modalitats de Generació

### 1. OpenAI GPT-4

- **Requisits**: API key OpenAI configurada
- **Qualitat**: Excel·lent
- **Cost**: A consum (API)
- **Velocitat**: Ràpida

### 2. Ollama (Local)

- **Requisits**: Ollama instal·lat i en execució
- **Qualitat**: Bona-Òptima (depèn del model)
- **Cost**: Gratuït
- **Velocitat**: Depèn del maquinari

### 3. API Gratuïta

- **Requisits**: Connexió internet
- **Qualitat**: Variable
- **Cost**: Gratuït
- **Limitacions**: Rate limiting possible

## Configuració

### OpenAI

1. Obtenir API key de [OpenAI](https://platform.openai.com/)
2. Configurar a **PyArchInit** → **Configuració** → **API Keys**
3. Seleccionar "OpenAI GPT-4" a la modalitat

### Ollama

1. Instal·lar Ollama des de [ollama.ai](https://ollama.ai/)
2. Iniciar Ollama: `ollama serve`
3. Descarregar model: `ollama pull llama3.2`
4. Seleccionar "Ollama" i verificar connexió

### Models Ollama Recomanats

| Model | Mida | Qualitat SQL |
|-------|------|--------------|
| llama3.2 | 2GB | Bona |
| mistral | 4GB | Òptima |
| codellama | 7GB | Excel·lent per SQL |
| qwen2.5-coder | 4GB | Òptima per codi |

## Ús

### 1. Escriure la Pregunta

A la casella d'entrada, descriure què es vol cercar:
- Usar llenguatge natural
- Ser específic quan sigui possible
- Esmentar taules/camps si es coneixen

### 2. Generar SQL

1. Fer clic **"Genera SQL"**
2. Esperar elaboració
3. Visualitzar consulta generada

### 3. Verificar Consulta

- Llegir la consulta SQL generada
- Fer clic **"Explica Consulta"** per comprendre
- Verificar correcció lògica

### 4. Executar Consulta

- **"Copia Consulta"**: Copia al portapapers
- **"Usa Consulta"**: Executa directament al sistema

## Esquema Base de Dades

### Taules Principals

El sistema coneix l'esquema PyArchInit:

| Taula | Descripció |
|-------|------------|
| site_table | Llocs arqueològics |
| us_table | Unitats Estratigràfiques |
| inventario_materiali_table | Troballes |
| pottery_table | Ceràmica |
| tomba_table | Tombes |
| individui_table | Individus |
| struttura_table | Estructures |
| periodizzazione_table | Periodització |
| campioni_table | Mostres |
| documentazione_table | Documentació |

### Camps Comuns

La IA coneix els camps principals:
- `sito` - Nom lloc
- `area` - Número àrea
- `us` - Número US
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Exemples de Consultes

### Cerca Troballes

**Pregunta**: *"Troba totes les troballes en bronze del lloc Roma Antiga"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Roma Antiga'
AND (tipo_reperto LIKE '%bronze%' OR definizione LIKE '%bronze%')
```

### Recompte US

**Pregunta**: *"Quantes US hi ha per a cada període al lloc Vil·la Adriana?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_us
FROM us_table
WHERE sito = 'Vil·la Adriana'
GROUP BY periodo_iniziale
```

### Cerca Espacial

**Pregunta**: *"Mostra les US de l'àrea 1000 amb cotes inferiors a 10 metres"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Bones Pràctiques

### 1. Preguntes Eficaces

- Ser específic: noms llocs, números, dates
- Indicar què es vol: llista, recompte, detalls
- Esmentar filtres desitjats

### 2. Verificació Resultats

- Sempre controlar la consulta generada
- Usar "Explica Consulta" si no és clar
- Testejar en subconjunt abans de consultes complexes

### 3. Iteració

- Si el resultat no és correcte, reformular pregunta
- Afegir detalls si consulta massa àmplia
- Simplificar si consulta massa complexa

## Resolució de Problemes

### Consulta No Generada

**Causes**:
- API no configurada
- Connexió absent
- Pregunta no comprensible

**Solucions**:
- Verificar configuració API
- Controlar connexió
- Reformular pregunta

### Resultats Erronis

**Causes**:
- Pregunta ambigua
- Camp/taula no existent

**Solucions**:
- Ser més específic
- Verificar noms taules/camps

### Ollama No Respon

**Causes**:
- Ollama no en execució
- Model no descarregat

**Solucions**:
- Iniciar `ollama serve`
- Descarregar model requerit

## Referències

### Fitxers Font
- `modules/utility/textTosql.py` - Classe MakeSQL
- `modules/utility/database_schema.py` - Esquema base de dades

### APIs Externes
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Vídeo Tutorial

### Consulta AI Base de Dades
`[Placeholder: video_consulta_ai.mp4]`

**Continguts**:
- Configuració API
- Escriptura preguntes eficaces
- Interpretació resultats
- Bones pràctiques

**Durada prevista**: 15-18 minuts

---

*Última actualització: Gener 2026*
