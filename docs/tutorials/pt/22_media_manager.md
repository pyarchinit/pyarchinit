# Tutorial 22: Gestor de Media

## Introducao

O **Gestor de Media** e a ferramenta central do PyArchInit para gerir imagens e conteudos multimedia associados a registos arqueologicos. Permite associar fotografias, desenhos, videos e outros media a UE, achados, sepulturas, estruturas e outras entidades.

### Funcionalidades Principais

- Gestao centralizada de todos os media
- Associacao a entidades arqueologicas (UE, Achados, Ceramica, Sepulturas, Estruturas, UT)
- Visualizacao de miniaturas e imagens em tamanho original
- Etiquetagem e categorizacao
- Pesquisa avancada
- Integracao GPT para analise de imagens

## Acesso

### Pelo Menu
**PyArchInit** > **Gestor de Media**

### Pela Barra de Ferramentas
Icone do **Gestor de Media** na barra de ferramentas do PyArchInit

## Interface

### Painel Principal

```
+----------------------------------------------------------+
|                    Gestor de Media                         |
+----------------------------------------------------------+
| Sitio: [ComboBox]  Area: [ComboBox]  UE: [ComboBox]      |
+----------------------------------------------------------+
| [Grelha de Miniaturas de Imagens]                         |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Etiquetas: [Lista de etiquetas associadas]                |
+----------------------------------------------------------+
| [Navegacao] << < Registo X de Y > >>                      |
+----------------------------------------------------------+
```

### Filtros de Pesquisa

| Campo | Descricao |
|-------|-----------|
| Sitio | Filtrar por sitio arqueologico |
| Area | Filtrar por area de escavacao |
| UE | Filtrar por Unidade Estratigrafica |
| Codigo de Estrutura | Filtrar por codigo de estrutura |
| N.o de Estrutura | Filtrar por numero de estrutura |

### Controlos de Miniaturas

| Controlo | Funcao |
|----------|--------|
| Barra deslizante de tamanho | Ajustar tamanho das miniaturas |
| Duplo clique | Abrir imagem no tamanho original |
| Selecao multipla | Ctrl+clique para selecionar varias imagens |

## Gestao de Media

### Adicionar Novas Imagens

1. Abrir o Gestor de Media
2. Selecionar sitio de destino
3. Clicar em **"Novo Registo"** ou utilizar o menu de contexto
4. Selecionar imagens a adicionar
5. Preencher metadados

### Associar Media a Entidades

1. Selecionar imagem na grelha
2. No painel de Etiquetas, selecionar:
   - **Tipo de entidade**: UE, Achado, Ceramica, Sepultura, Estrutura, UT
   - **Identificador**: Numero/codigo da entidade
3. Clicar em **"Associar"**

### Tipos de Entidade Suportados

| Tipo | Tabela BD | Descricao |
|------|-----------|-----------|
| UE | us_table | Unidades Estratigraficas |
| ACHADO | inventario_materiali_table | Achados/Materiais |
| CERAMICA | pottery_table | Ceramica |
| SEPULTURA | tomba_table | Sepulturas |
| ESTRUTURA | struttura_table | Estruturas |
| UT | ut_table | Unidades Topograficas |

### Ver Imagem Original

- **Duplo clique** na miniatura
- Abre o visualizador com:
  - Zoom (roda do rato)
  - Panoramica (arrastar)
  - Rotacao
  - Medicao

## Funcionalidades Avancadas

### Pesquisa Avancada

O Gestor de Media suporta pesquisa por:
- Nome do ficheiro
- Data de entrada
- Entidade associada
- Etiquetas/categorias

### Integracao GPT

Botao **"GPT Sketch"** para:
- Analise automatica de imagens
- Geracao de descricoes
- Sugestoes de classificacao

### Carregamento Remoto

Suporte para imagens em servidores remotos:
- URLs diretos
- Servidores FTP
- Armazenamento na nuvem

## Base de Dados

### Tabelas Envolvidas

| Tabela | Descricao |
|--------|-----------|
| `media_table` | Metadados dos media |
| `media_thumb_table` | Miniaturas |
| `media_to_entity_table` | Associacoes a entidades |

### Classes Mapper

- `MEDIA` - Entidade media principal
- `MEDIA_THUMB` - Miniaturas
- `MEDIATOENTITY` - Relacao media-entidade

## Boas Praticas

### 1. Organizacao de Ficheiros

- Utilizar nomes de ficheiros descritivos
- Organizar por sitio/area/ano
- Manter copias de seguranca originais

### 2. Metadados

- Preencher sempre sitio e area
- Adicionar descricoes significativas
- Utilizar etiquetas consistentes

### 3. Qualidade de Imagem

- Resolucao minima recomendada: 1920x1080
- Formato: JPG para fotografias, PNG para desenhos
- Compressao moderada

### 4. Associacoes

- Associar cada imagem as entidades relevantes
- Verificar associacoes apos importacao em lote
- Utilizar pesquisa para imagens nao associadas

## Resolucao de Problemas

### Miniaturas Nao Apresentadas

**Causas**:
- Caminho da imagem incorreto
- Ficheiro em falta
- Problemas de permissoes

**Solucoes**:
- Verificar caminho na base de dados
- Confirmar existencia do ficheiro
- Verificar permissoes da pasta

### Impossivel Associar Imagem

**Causas**:
- Entidade nao existe
- Tipo de entidade errado

**Solucoes**:
- Verificar que o registo existe
- Verificar tipo de entidade selecionado

## Referencias

### Ficheiros Fonte
- `tabs/Image_viewer.py` - Interface principal
- `modules/utility/pyarchinit_media_utility.py` - Utilitarios de media

### Base de Dados
- `media_table` - Dados de media
- `media_to_entity_table` - Associacoes

---

## Tutorial em Video

### Gestor de Media Completo
`[Placeholder: video_media_manager.mp4]`

**Conteudos**:
- Adicionar imagens
- Associar a entidades
- Pesquisa e filtros
- Funcionalidades avancadas

**Duracao prevista**: 15-18 minutos

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este topico.

[Abrir Animacao Interativa](../../animations/pyarchinit_media_manager_animation.html)
