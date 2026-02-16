# Tutorial 23: Pesquisa de Imagens

## Introducao

A funcao de **Pesquisa de Imagens** permite pesquisar rapidamente imagens na base de dados do PyArchInit, filtrando por sitio, tipo de entidade e outros criterios. E uma ferramenta complementar ao Gestor de Media para pesquisa global.

## Acesso

### Pelo Menu
**PyArchInit** > **Pesquisa de Imagens**

## Interface

### Painel de Pesquisa

```
+--------------------------------------------------+
|           Pesquisa de Imagens                     |
+--------------------------------------------------+
| Filtros:                                          |
|   Sitio: [ComboBox]                              |
|   Tipo de Entidade: [-- Todos -- | UE | Ceramica | ...]  |
|   [ ] Apenas imagens sem etiqueta                |
+--------------------------------------------------+
| [Pesquisar]  [Limpar]                            |
+--------------------------------------------------+
| Resultados:                                       |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Abrir Imagem] [Exportar] [Ir para Registo]      |
+--------------------------------------------------+
```

### Filtros Disponiveis

| Filtro | Descricao |
|--------|-----------|
| Sitio | Selecionar sitio especifico ou todos |
| Tipo de Entidade | UE, Ceramica, Materiais, Sepultura, Estrutura, UT |
| Apenas sem etiqueta | Mostrar apenas imagens sem associacoes |

### Tipos de Entidade

| Tipo | Descricao |
|------|-----------|
| -- Todos -- | Todas as entidades |
| UE | Unidades Estratigraficas |
| Ceramica | Ceramica |
| Materiais | Achados/Inventario |
| Sepultura | Sepulturas |
| Estrutura | Estruturas |
| UT | Unidades Topograficas |

## Funcionalidades

### Pesquisa Basica

1. Selecionar filtros pretendidos
2. Clicar em **"Pesquisar"**
3. Ver resultados na grelha

### Acoes sobre os Resultados

| Botao | Funcao |
|-------|--------|
| Abrir Imagem | Ver imagem no tamanho original |
| Exportar | Exportar imagem selecionada |
| Ir para Registo | Abrir formulario da entidade associada |
| Abrir Gestor de Media | Abrir Gestor de Media com a imagem selecionada |

### Menu de Contexto (Clique direito)

- **Abrir imagem**
- **Exportar imagem...**
- **Ir para registo**

### Pesquisa de Imagens Sem Etiqueta

Caixa de selecao **"Apenas imagens sem etiqueta"**:
- Encontra imagens na base de dados sem associacoes
- Util para limpeza e organizacao
- Permite identificar imagens a catalogar

## Fluxo de Trabalho Tipico

### 1. Encontrar Imagens de um Sitio

```
1. Selecionar sitio no ComboBox
2. Deixar "-- Todos --" para tipo de entidade
3. Clicar em Pesquisar
4. Navegar pelos resultados
```

### 2. Encontrar Imagens de uma UE Especifica

```
1. Selecionar sitio
2. Selecionar "UE" como tipo de entidade
3. Clicar em Pesquisar
4. Duplo clique para abrir imagem
```

### 3. Identificar Imagens Nao Catalogadas

```
1. Selecionar sitio (ou todos)
2. Ativar "Apenas imagens sem etiqueta"
3. Clicar em Pesquisar
4. Para cada resultado:
   - Abrir imagem
   - Identificar conteudo
   - Associar pelo Gestor de Media
```

## Exportacao

### Exportacao de Imagem Individual

1. Selecionar imagem nos resultados
2. Clicar em **"Exportar"** ou menu de contexto
3. Selecionar destino
4. Guardar

### Exportacao Multipla

Para exportar varias imagens, utilizar a funcao dedicada **Exportar Imagens** (Tutorial 24).

## Boas Praticas

### 1. Pesquisa Eficiente

- Utilizar filtros especificos para resultados direcionados
- Comecar com filtros amplos, depois restringir
- Utilizar pesquisa sem etiqueta periodicamente

### 2. Organizacao

- Catalogar imagens sem etiqueta regularmente
- Verificar associacoes apos importacao
- Manter nomenclatura consistente

## Resolucao de Problemas

### Sem Resultados

**Causas**:
- Filtros demasiado restritivos
- Sem imagens para os criterios

**Solucoes**:
- Alargar filtros
- Verificar que os dados existem

### Imagem Nao Visualizavel

**Causas**:
- Ficheiro nao encontrado
- Formato nao suportado

**Solucoes**:
- Verificar caminho do ficheiro
- Verificar formato da imagem

## Referencias

### Ficheiros Fonte
- `tabs/Image_search.py` - Interface de pesquisa
- `gui/ui/pyarchinit_image_search_dialog.ui` - Disposicao da UI

### Base de Dados
- `media_table` - Dados de media
- `media_to_entity_table` - Associacoes

---

## Tutorial em Video

### Pesquisa de Imagens
`[Placeholder: video_ricerca_immagini.mp4]`

**Conteudos**:
- Utilizacao de filtros
- Pesquisa avancada
- Exportacao de resultados

**Duracao prevista**: 8-10 minutos

---

*Ultima atualizacao: janeiro de 2026*
