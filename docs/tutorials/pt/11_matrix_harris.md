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
| PDF poster | Gera tambem um PDF poster multipagina para imprimir matrix mais largas do que uma folha: as folhas sobrepoem-se 2 cm e cada folha tem a etiqueta "foglio n/N - riga r/R, colonna c/C - A0 scala 1:x" (folha n/N - linha r/R, coluna c/C - A0 escala 1:x). Para matrix muito grandes (quando o DPI do JPG tem de ser reduzido) o poster e produzido de qualquer forma, mesmo se a caixa nao estiver marcada | Sim (para impressao) |
| Formato | Formato das folhas do poster: A0, A1, A2, A3 | A0 |
| Scala (Escala) | Escala do poster: "Adatta all'altezza" (ajustar a altura: uma fila de folhas, a altura da matrix preenche a folha), "Adatta alla pagina" (ajustar a pagina: uma unica folha com toda a matrix), 1:1, 1:2, 1:3 (escala fixa, mais folhas). O desenho nunca e ampliado; a orientacao (vertical/horizontal) e escolhida automaticamente para usar menos folhas | Adatta all'altezza |

Os controlos **PDF poster**, **Formato** e **Scala** estao na segunda linha da janela (as etiquetas estao em italiano em todos os idiomas da interface).

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

### Matrix de Grandes Dimensoes

Com matrix muito grandes (p. ex. 1300 UEs e cerca de 2000 relacoes) a exportacao com ligacoes ortogonais podia demorar mais de 25 minutos e produzir um JPG vazio (0 bytes). A partir desta versao **Export Matrix** e **View Matrix** adaptam-se automaticamente:

| Situacao | O que acontece |
|----------|----------------|
| Mais de **600** relacoes | As ligacoes passam automaticamente de ortogonais (`ortho`) para polilinhas retas com espacamento mais compacto: a mesma matrix e paginada em cerca de um segundo. Abaixo do limiar o estilo ortogonal mantem-se inalterado |
| Imagem que excede o limite do renderizador bitmap (32 767 px por lado) | O DPI de JPG/PNG e reduzido automaticamente (o valor definido em Setting_Matrix e um maximo) e junto a imagem, em `pyarchinit_Matrix_folder`, sao guardadas as copias vetoriais `.svg` e `.pdf` (`Harris_matrix_tred.dot.svg/.pdf`; para View Matrix `Harris_matrix_viewtred.dot.svg/.pdf`) |
| Aviso "Matrix molto grande" (matrix muito grande: o JPG foi gerado a N dpi, use os ficheiros .svg / .pdf) | Abrir o ficheiro `.svg` ou `.pdf` (browser, Inkscape, visualizador PDF) para uma versao legivel e ampliavel sem perda de qualidade |

Os ficheiros `.dot` continuam a ser produzidos como antes.

**Exportacao com periodizacao** (checkbox de periodos em Setting_Matrix):

- A exportacao ja nao e interrompida com o erro `Errore durante il rendering del file DOT: 'NoneType' object has no attribute 'write'`, que aparecia quando o Graphviz emitia um aviso e o QGIS nao tinha a consola Python aberta (tipico no Windows). Os avisos do Graphviz sao agora escritos na consola Python / no registo do QGIS em vez de abortar a exportacao.
- Em DB grandes a exportacao com periodos e muito mais rapida (a mesma base de dados de 1311 UEs passou de cerca de 25–45 s e um DOT de 51 MB para cerca de 3 s) e cada fase recebe o seu proprio cluster invisivel, de modo que nenhuma fase e ignorada silenciosamente pelo Graphviz.
- Para matrix com periodos muito largas o JPG pode agora ser gerado mesmo abaixo de 12 dpi se necessario (como referencia, a matrix de 1311 UEs com periodos sai a 49 dpi): e apenas uma visao geral; para a versao legivel use as copias `.svg` / `.pdf` guardadas ao lado.

**Copias vetoriais e impressao do poster**:

- As copias `.pdf` / `.svg` ficam agora sempre dentro de 200 polegadas (14 400 pt) por lado, o limite a partir do qual o Acrobat e a Pre-visualizacao mostram apenas uma parte da pagina: toda a matrix fica assim visivel e ampliavel (vetorial, sem perda de qualidade). Na base de dados de 1311 UEs com periodos o PDF mede 14 400 × 2 591 pt.
- Para a imprimir use o PDF poster (checkbox **PDF poster** em Setting_Matrix): para a mesma base de dados, A0 com "Adatta all'altezza" (ajustar a altura) da 5 folhas A0 horizontais a escala 1:3,4 (texto ≈ 4 pt: legivel num plotter; use A0 "1:2" ou "1:1" para texto maior e mais folhas). Uma unica folha A0 ("Adatta alla pagina", ajustar a pagina) e apenas uma visao geral.

### Aviso "Periodizacao: cronologia inicial maior do que a final"

**Quando aparece**: ao exportar com **Print Periodizzazione** ativo, se em pelo menos um periodo/fase a Cronologia Inicial e maior do que a Cronologia Final (ex. `Periodo 6 Fase 1: 1650 → 1450`). A exportacao continua na mesma.

**Causa**: quase sempre datas a.C. inseridas sem o sinal de menos (a convencao do pyArchInit e a.C. = anos negativos). O periodo e ordenado como d.C.: a Idade do Bronze fica acima das fases romanas e as etiquetas dos clusters mostram "1650 d.C." em vez de "1650 a.C.".

**Solucao**:
1. Abrir a Ficha de Periodizacao e corrigir os periodos listados no aviso inserindo os anos a.C. como numeros negativos (ex. `-1650` → `-1450`)
2. Regenerar a Matrix

## Resultados e Ficheiros Gerados

### Pasta de Resultados

```
~/pyarchinit/pyarchinit_Matrix_folder/
|-- Harris_matrix.dot           # Fonte Graphviz
|-- Harris_matrix_tred.dot      # Apos reducao transitiva
|-- Harris_matrix_tred.dot.jpg  # Imagem JPG final
|-- Harris_matrix_tred.dot.png  # Imagem PNG final
|-- Harris_matrix_tred.dot.svg  # Vetorial (so matrix grandes)
|-- Harris_matrix_tred.dot.pdf  # Vetorial (so matrix grandes)
|-- Harris_matrix_poster_A0.pdf # PDF poster multipagina para impressao
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
| *.svg/*.pdf | Versao vetorial ampliavel (matrix grandes) |
| _poster_A0.pdf | PDF poster multipagina para impressao; o nome segue o formato escolhido (p. ex. `_poster_A3.pdf`), para Export Matrix 2ED o prefixo e `Harris_matrix2ED` |

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
