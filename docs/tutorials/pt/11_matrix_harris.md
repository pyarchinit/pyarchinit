# Tutorial 11: Harris Matrix

## Introducao

O **Harris Matrix** (ou diagrama estratigrafico) e uma ferramenta fundamental em arqueologia para representar graficamente as relacoes estratigraficas entre as diferentes Unidades Estratigraficas (UE). O PyArchInit gera automaticamente o Harris Matrix a partir das relacoes estratigraficas introduzidas nas fichas de UE.

### O que e o Harris Matrix?

O Harris Matrix e um diagrama que representa:
- A **sequencia temporal** das UEs (da mais recente no topo a mais antiga na base)
- As **relacoes fisicas** entre UEs (cobre/coberta por, corta/cortada por, liga-se a)
- A **periodizacao** da escavacao (agrupamento por periodos e fases)

### Tipos de Relacoes Representadas

| Relacao | Significado | Representacao |
|---------|-------------|---------------|
| Cobre/Coberta por | Sobreposicao fisica | Linha continua descendente |
| Corta/Cortada por | Acao negativa (interface) | Linha tracejada |
| Liga-se a/Igual a | Contemporaneidade | Linha horizontal bidirecional |
| Preenche/Preenchida por | Enchimento de corte | Linha continua |
| Encosta-se a/Suporta | Suporte estrutural | Linha continua |

## Aceder a Funcao

### A Partir do Menu Principal
1. **PyArchInit** na barra de menus
2. Selecionar **Harris Matrix**

### A Partir da Ficha de UE
1. Abrir a Ficha de UE
2. Separador **Map**
3. Botao **"Export Matrix"** ou **"View Matrix"**

### Pre-requisitos
- Base de dados corretamente ligada
- UEs com relacoes estratigraficas preenchidas
- Periodizacao definida (opcional mas recomendado)
- Graphviz instalado no sistema

## Configuracao da Matrix

### Janela de Definicoes (Setting_Matrix)

Antes da geracao, aparece uma janela de configuracao:

#### Separador Geral

| Campo | Descricao | Valor Recomendado |
|-------|-----------|-------------------|
| DPI | Resolucao da imagem | 150-300 |
| Show Periods | Agrupar UEs por periodo/fase | Sim |
| Show Legend | Incluir legenda no grafico | Sim |

#### Separador Nos "Ante/Post" (Relacoes Normais)

| Parametro | Descricao | Opcoes |
|-----------|-----------|--------|
| Forma do no | Forma geometrica | box, ellipse, diamond |
| Cor de preenchimento | Cor interna | white, lightblue, etc. |
| Estilo | Aparencia do contorno | solid, dashed |
| Largura da linha | Largura do contorno | 0.5 - 2.0 |
| Tipo de seta | Cabeca da seta | normal, diamond, none |
| Tamanho da seta | Tamanho da cabeca | 0.5 - 1.5 |

#### Separador Nos "Negativos" (Cortes)

| Parametro | Descricao | Opcoes |
|-----------|-----------|--------|
| Forma do no | Forma geometrica | box, ellipse, diamond |
| Cor de preenchimento | Cor distintiva | gray, lightcoral |
| Estilo da linha | Aparencia da ligacao | dashed |

#### Separador Nos "Contemporaneos"

| Parametro | Descricao | Opcoes |
|-----------|-----------|--------|
| Forma do no | Forma geometrica | box, ellipse |
| Cor de preenchimento | Cor distintiva | lightyellow, white |
| Estilo da linha | Aparencia da ligacao | solid |
| Seta | Tipo de ligacao | none (bidirecional) |

## Tipos de Exportacao

### 1. Exportacao de Matrix Padrao

Gera a matrix basica com:
- Todas as relacoes estratigraficas
- Agrupamento por periodo/fase
- Disposicao vertical (TB - Topo para Base)

**Resultado**: `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Exportacao de Matrix Estendida (2ED)

Versao alargada com:
- Informacao adicional nos nos (UE + definicao + datacao)
- Ligacoes especiais (>, >>)
- Exportacao em formato GraphML

**Resultado**: `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. Visualizacao da Matrix (Visualizacao Rapida)

Para visualizacao rapida sem opcoes de configuracao:
- Utiliza definicoes predefinidas
- Geracao mais rapida
- Ideal para verificacoes rapidas

## Processo de Geracao

### Passo 1: Recolha de Dados

O sistema recolhe automaticamente:
```
Para cada UE no sitio/area selecionados:
  - Numero da UE
  - Tipo de unidade (UE/UEM)
  - Relacoes estratigraficas
  - Periodo e fase iniciais
  - Definicao interpretativa
```

### Passo 2: Construcao do Grafo

Criacao de relacoes:
```
Sequencia (Ante/Post):
  UE1 -> UE2 (UE1 cobre UE2)

Negativa (Cortes):
  UE3 -> UE4 (UE3 corta UE4)

Contemporanea:
  UE5 <-> UE6 (UE5 liga-se a UE6)
```

### Passo 3: Agrupamento por Periodo

Agrupamento hierarquico:
```
Sitio
  +-- Area
      +-- Periodo 1 : Fase 1 : "Epoca Romana"
          |-- UE101
          |-- UE102
          +-- UE103
      +-- Periodo 1 : Fase 2 : "Antiguidade Tardia"
          |-- UE201
          +-- UE202
```

### Passo 4: Reducao Transitiva (tred)

O comando `tred` do Graphviz remove relacoes redundantes:
- Se UE1 -> UE2 e UE2 -> UE3, remove UE1 -> UE3
- Simplifica o diagrama
- Mantem apenas as relacoes diretas

### Passo 5: Renderizacao Final

Geracao da imagem em multiplos formatos:
- DOT (fonte Graphviz)
- JPG (imagem comprimida)
- PNG (imagem sem perdas)

## Interpretacao da Matrix

### Leitura Vertical

```
     [UE mais recente]
           |
        UE 001
           |
        UE 002
           |
        UE 003
           |
     [UE mais antiga]
```

### Leitura de Agrupamentos

As caixas coloridas representam periodos/fases:
- **Azul claro**: Agrupamento de periodo
- **Amarelo**: Agrupamento de fase
- **Cinzento**: Fundo do sitio

### Tipos de Ligacao

```
----------->  Linha continua = Cobre/Preenche/Encosta-se
- - - - ->  Linha tracejada = Corta
<--------->  Bidirecional = Contemporanea/Igual a
```

### Cores dos Nos

| Cor | Significado Tipico |
|-----|---------------------|
| Branco | UE de deposito normal |
| Cinzento | UE negativa (corte) |
| Amarelo | UE contemporanea |
| Azul | UE com relacoes especiais |

## Resolucao de Problemas

### Erro: "Loop Detected"

**Causa**: Existem ciclos nas relacoes (A cobre B, B cobre A)

**Solucao**:
1. Abrir a Ficha de UE
2. Verificar as relacoes das UEs indicadas
3. Corrigir as relacoes circulares
4. Regenerar a matrix

### Erro: "tred command not found"

**Causa**: Graphviz nao instalado

**Solucao**:
- **Windows**: Instalar Graphviz a partir de graphviz.org
- **macOS**: `brew install graphviz`
- **Linux**: `sudo apt install graphviz`

### Matrix Nao Gerada

**Causas possiveis**:
1. Nenhuma relacao estratigrafica introduzida
2. UEs sem periodo/fase atribuidos
3. Problemas de permissoes na pasta de resultados

**Verificacao**:
1. Verificar se as UEs tem relacoes
2. Verificar a periodizacao
3. Verificar permissoes em `pyarchinit_Matrix_folder`

### Matrix Demasiado Grande

**Problema**: Imagem ilegivel com muitas UEs

**Solucoes**:
1. Reduzir DPI (100-150)
2. Filtrar por area especifica
3. Utilizar View Matrix para areas individuais
4. Exportar para formato vetorial (DOT) e abrir com yEd

## Resultados e Ficheiros Gerados

### Pasta de Resultados

```
~/pyarchinit/pyarchinit_Matrix_folder/
|-- Harris_matrix.dot           # Fonte Graphviz
|-- Harris_matrix_tred.dot      # Apos reducao transitiva
|-- Harris_matrix_tred.dot.jpg  # Imagem JPG final
|-- Harris_matrix_tred.dot.png  # Imagem PNG final
|-- Harris_matrix2ED.dot        # Versao estendida
|-- Harris_matrix2ED_graphml.dot # Para exportacao GraphML
+-- matrix_error.txt            # Registo de erros
```

### Utilizacao dos Ficheiros

| Ficheiro | Utilizacao |
|----------|------------|
| *.jpg/*.png | Inserir em relatorios |
| *.dot | Editar com editor Graphviz |
| _graphml.dot | Importar para yEd para edicao avancada |

## Boas Praticas

### 1. Antes da Geracao

- Verificar a completude das relacoes estratigraficas
- Verificar a ausencia de ciclos
- Atribuir periodo/fase a todas as UEs
- Preencher a definicao interpretativa

### 2. Durante a Compilacao das UEs

- Introduzir relacoes bidirecionais corretas
- Utilizar terminologia consistente
- Verificar a area correta nas relacoes

### 3. Otimizacao dos Resultados

- Para impressao: DPI 300
- Para ecra: DPI 150
- Para escavacoes complexas: dividir por areas

### 4. Controlo de Qualidade

- Comparar a matrix com a documentacao da escavacao
- Verificar as sequencias logicas
- Verificar os agrupamentos por periodo

## Integracao com Outras Ferramentas

### Exportacao para yEd

O ficheiro `_graphml.dot` pode ser aberto no yEd para:
- Edicao manual da disposicao
- Adicao de anotacoes
- Exportacao para diferentes formatos

### Exportacao para s3egraph

O PyArchInit suporta exportacao para o sistema s3egraph:
- Formato compativel
- Mantem relacoes estratigraficas
- Suporte para visualizacao 3D

## Referencias

### Ficheiros Fonte
- `tabs/Interactive_matrix.py` - Interface interativa
- `modules/utility/pyarchinit_matrix_exp.py` - Classes HarrisMatrix e ViewHarrisMatrix

### Base de Dados
- `us_table` - Dados e relacoes das UEs
- `periodizzazione_table` - Periodos e fases

### Dependencias
- Graphviz (dot, tred)
- Biblioteca Python graphviz

---

## Video Tutorial

### Harris Matrix - Geracao Completa
`[Marcador: video_matrix_harris.mp4]`

**Conteudos**:
- Configuracao de definicoes
- Geracao da matrix
- Interpretacao de resultados
- Resolucao de problemas comuns

**Duracao prevista**: 15-20 minutos

---

*Ultima atualizacao: janeiro de 2026*

---

## Animacao Interativa

Explore a animacao interativa para saber mais sobre este tema.

[Abrir Animacao Interativa](../../animations/harris_matrix_animation.html)
