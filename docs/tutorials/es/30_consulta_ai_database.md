# Tutorial 30: AI Query Database (Text2SQL)

## Introducción

**AI Query Database** es una funcionalidad avanzada de PyArchInit que permite consultar la base de datos arqueológica usando **lenguaje natural**. El sistema convierte automáticamente las preguntas en consultas SQL gracias a la inteligencia artificial.

### Cómo Funciona

1. El usuario escribe una pregunta en español/inglés
2. La AI analiza la petición
3. Genera la consulta SQL correspondiente
4. Ejecuta la consulta en la base de datos
5. Devuelve los resultados

### Ejemplos de Preguntas

- *"Encuentra todos los hallazgos cerámicos del sitio Villa Romana"*
- *"Muestra las UE del período romano en el área 1000"*
- *"¿Cuántos individuos se han encontrado en las tumbas?"*
- *"Lista las estructuras con datación medieval"*

## Acceso

### Desde la Ficha UE/Hallazgos
Tab dedicado **"AI Query"** o **"Text2SQL"**

### Desde el Menú
**PyArchInit** → **AI Query Database**

## Interfaz

### Panel de Consulta

```
+--------------------------------------------------+
|         Generación SQL con AI                     |
+--------------------------------------------------+
| Modo de Generación:                               |
|   (o) OpenAI GPT-4 (API ya configurada)          |
|   ( ) Ollama (modelo local)                      |
|   ( ) API gratuita (si está disponible)          |
+--------------------------------------------------+
| Modelo Ollama: [llama3.2 v] [Verificar Ollama]   |
+--------------------------------------------------+
| Input:                                            |
|   Tipo de Base de Datos: [sqlite | postgresql]   |
|                                                  |
|   Describe la consulta:                          |
|   +--------------------------------------------+ |
|   | Encuentra todos los hallazgos cerámicos    | |
|   | del sitio Villa Romana con datación entre  | |
|   | los siglos I y II                          | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Generar SQL]  [Limpiar]                         |
+--------------------------------------------------+
| Consulta SQL Generada:                            |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Villa Romana'                | |
|   | AND tipo_reperto LIKE '%ceramic%'          | |
|   +--------------------------------------------+ |
| [Explicar Query] [Copiar Query] [Usar Query]    |
+--------------------------------------------------+
| Explicación:                                      |
|   La consulta selecciona todos los campos de...  |
+--------------------------------------------------+
```

## Modos de Generación

### 1. OpenAI GPT-4

- **Requisitos**: API key de OpenAI configurada
- **Calidad**: Excelente
- **Coste**: Por consumo (API)
- **Velocidad**: Rápida

### 2. Ollama (Local)

- **Requisitos**: Ollama instalado y en ejecución
- **Calidad**: Buena-Óptima (depende del modelo)
- **Coste**: Gratuito
- **Velocidad**: Depende del hardware

### 3. API Gratuita

- **Requisitos**: Conexión a internet
- **Calidad**: Variable
- **Coste**: Gratuito
- **Limitaciones**: Rate limiting posible

## Configuración

### OpenAI

1. Obtener API key de [OpenAI](https://platform.openai.com/)
2. Configurar en **PyArchInit** → **Configuración** → **API Keys**
3. Seleccionar "OpenAI GPT-4" en el modo

### Ollama

1. Instalar Ollama de [ollama.ai](https://ollama.ai/)
2. Iniciar Ollama: `ollama serve`
3. Descargar modelo: `ollama pull llama3.2`
4. Seleccionar "Ollama" y verificar conexión

### Modelos Ollama Recomendados

| Modelo | Tamaño | Calidad SQL |
|--------|--------|-------------|
| llama3.2 | 2GB | Buena |
| mistral | 4GB | Óptima |
| codellama | 7GB | Excelente para SQL |
| qwen2.5-coder | 4GB | Óptima para código |

## Uso

### 1. Escribir la Pregunta

En el cuadro de entrada, describir lo que se quiere buscar:
- Usar lenguaje natural
- Ser específico cuando sea posible
- Mencionar tablas/campos si se conocen

### 2. Generar SQL

1. Hacer clic en **"Generar SQL"**
2. Esperar el procesamiento
3. Visualizar la consulta generada

### 3. Verificar Consulta

- Leer la consulta SQL generada
- Hacer clic en **"Explicar Query"** para comprender
- Verificar la corrección lógica

### 4. Ejecutar Consulta

- **"Copiar Query"**: Copia al portapapeles
- **"Usar Query"**: Ejecuta directamente en el sistema

## Esquema de Base de Datos

### Tablas Principales

El sistema conoce el esquema PyArchInit:

| Tabla | Descripción |
|-------|-------------|
| site_table | Sitios arqueológicos |
| us_table | Unidades Estratigráficas |
| inventario_materiali_table | Hallazgos |
| pottery_table | Cerámica |
| tomba_table | Tumbas |
| individui_table | Individuos |
| struttura_table | Estructuras |
| periodizzazione_table | Periodización |
| campioni_table | Muestras |
| documentazione_table | Documentación |

### Campos Comunes

La AI conoce los campos principales:
- `sito` - Nombre del sitio
- `area` - Número de área
- `us` - Número de UE
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Ejemplos de Consultas

### Búsqueda de Hallazgos

**Pregunta**: *"Encuentra todos los hallazgos en bronce del sitio Roma Antigua"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Roma Antigua'
AND (tipo_reperto LIKE '%bronce%' OR definizione LIKE '%bronce%')
```

### Conteo de UE

**Pregunta**: *"¿Cuántas UE hay para cada período en el sitio Villa Adriana?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_us
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Búsqueda Espacial

**Pregunta**: *"Muestra las UE del área 1000 con cotas inferiores a 10 metros"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Buenas Prácticas

### 1. Preguntas Efectivas

- Ser específico: nombres de sitios, números, fechas
- Indicar lo que se quiere: lista, conteo, detalles
- Mencionar filtros deseados

### 2. Verificación de Resultados

- Siempre controlar la consulta generada
- Usar "Explicar Query" si no está claro
- Probar en un subconjunto antes de consultas complejas

### 3. Iteración

- Si el resultado no es correcto, reformular la pregunta
- Añadir detalles si la consulta es demasiado amplia
- Simplificar si la consulta es demasiado compleja

## Resolución de Problemas

### Consulta No Generada

**Causas**:
- API no configurada
- Conexión faltante
- Pregunta no comprensible

**Soluciones**:
- Verificar configuración de API
- Controlar conexión
- Reformular la pregunta

### Resultados Incorrectos

**Causas**:
- Pregunta ambigua
- Campo/tabla no existente

**Soluciones**:
- Ser más específico
- Verificar nombres de tablas/campos

### Ollama No Responde

**Causas**:
- Ollama no en ejecución
- Modelo no descargado

**Soluciones**:
- Iniciar `ollama serve`
- Descargar el modelo requerido

## Referencias

### Archivos Fuente
- `modules/utility/textTosql.py` - Clase MakeSQL
- `modules/utility/database_schema.py` - Esquema de base de datos

### APIs Externas
- [OpenAI API](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Video Tutorial

### AI Query Database
`[Placeholder: video_ai_query.mp4]`

**Contenidos**:
- Configuración de API
- Escritura de preguntas efectivas
- Interpretación de resultados
- Buenas prácticas

**Duración prevista**: 15-18 minutos

---

*Última actualización: Enero 2026*
