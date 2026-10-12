# PyArchInit - GeoArchaeo - Análise Geoestatística

## Índice
1. [Introdução](#introdução)
2. [Acesso à ferramenta](#acesso-à-ferramenta)
3. [Interface do utilizador](#interface-do-utilizador)
4. [Separador Dados](#separador-dados)
5. [Separador Variograma](#separador-variograma)
6. [Separador Kriging](#separador-kriging)
7. [Separador Padrões (ML)](#separador-padrões-ml)
8. [Separador Amostragem](#separador-amostragem)
9. [Separador Relatório](#separador-relatório)
10. [Fluxo de trabalho operacional](#fluxo-de-trabalho-operacional)
11. [Resolução de problemas](#resolução-de-problemas)
12. [Notas técnicas](#notas-técnicas)

---

## Introdução

O **GeoArchaeo** é o módulo de análise geoestatística integrado no PyArchInit e corresponde à versão **1.3.1** do plugin GeoArchaeo. Trabalha com qualquer camada de pontos do projeto QGIS que tenha um campo numérico (número de fragmentos, medições geofísicas, análises de solo, medidas das sepulturas…) e acompanha a análise desde as estatísticas descritivas até ao variograma, à interpolação por kriging ordinário com a respetiva incerteza, à procura de grupos e anomalias com aprendizagem automática, à proposta de novos pontos de amostragem e, por fim, a um relatório.

A interface do GeoArchaeo existe apenas em italiano e em inglês. Neste tutorial as etiquetas são traduzidas e, entre parênteses, indica-se a etiqueta inglesa que aparece no painel.

<!-- VIDEO: Introducao ao GeoArchaeo -->
> **Tutorial em video**: [Inserir ligacao do video de introducao ao GeoArchaeo]

### Porquê a análise geoestatística em arqueologia?

A análise geoestatística permite:

- **Descrever** a distribuição dos valores medidos (média, dispersão, assimetria, valores atípicos)
- **Quantificar** a correlação espacial, ou seja, até que distância os valores se assemelham (variograma)
- **Interpolar** os valores entre os pontos conhecidos, obtendo uma superfície contínua acompanhada da sua incerteza (kriging)
- **Reconhecer** grupos de pontos semelhantes e anomalias (aprendizagem automática)
- **Planear** onde amostrar ou escavar nas próximas campanhas
- **Documentar** as análises num relatório

### Visão geral do fluxo de trabalho

```
Dados de entrada: camada de pontos + campo numérico (escolhidos em cima, uma só vez)
  │
  ├─ 1 Dados ............ estatísticas descritivas, histograma
  ├─ 2 Variograma ....... efeito pepita, patamar, alcance, anisotropia
  ├─ 3 Kriging .......... rasters da estimativa e da incerteza, validação cruzada
  ├─ 4 Padrões (ML) ..... grupos e anomalias (camada de pontos)
  ├─ 5 Amostragem ....... novos pontos propostos (camada de pontos)
  └─ 6 Relatório ........ documento HTML com gráficos interativos, ou PDF
```

### Novidades da versão 1.3.1

- A camada e o campo escolhem-se **uma só vez** em cima e valem para todos os separadores; cada separador conserva os seus resultados
- Os gráficos aparecem no painel mesmo sem QtWebEngine (pré-visualização estática e botão para os abrir no navegador)
- O kriging produz também o **raster de incerteza**, aplica a rampa de cores e calcula uma verdadeira **validação cruzada leave-one-out**
- A anisotropia é verificada com verdadeiros **variogramas direcionais**; efeito pepita, patamar e alcance podem ser fixados à mão
- O variograma e o kriging são muito mais rápidos (procura de vizinhos com KD-tree): grelhas até **500 × 500 células**
- Os valores NULL já não bloqueiam as estatísticas nem o kriging; o relatório contém os gráficos; os dados de exemplo vêm da pasta do módulo
- O idioma do painel fica guardado nas definições do QGIS

---

## Acesso à ferramenta

O GeoArchaeo faz parte do grupo de ferramentas de análise do PyArchInit.

### A partir da barra de ferramentas

1. Na barra de ferramentas do PyArchInit, localizar o botão de lista pendente das **ferramentas de análise** (o mesmo grupo que contém, entre outros, SAM, Pottery Tools e MoveCost)
2. Clicar na seta junto ao botão: o ícone visível pode ser o de outra ferramenta do grupo
3. Escolher **GeoArchaeo - Geostatistical Analysis** (etiqueta da ação no PyArchInit quando o QGIS está em português)

<!-- IMAGE: Botao de lista pendente das ferramentas de analise na barra de ferramentas -->
> **Fig. 1**: O menu pendente das ferramentas de análise na barra de ferramentas do PyArchInit

A mesma entrada encontra-se no menu **pyArchInit** da barra de menus do QGIS e no menu de plugins, em **pyArchInit - Archaeological GIS Tools**.

O painel GeoArchaeo abre-se como **painel acoplável** no lado direito da janela do QGIS: pode ser movido, redimensionado ou desacoplado como qualquer painel do QGIS. Se for fechado, a mesma entrada volta a abri-lo com os resultados da sessão ainda presentes.

<!-- IMAGE: Painel GeoArchaeo acoplado a direita no QGIS -->
> **Fig. 2**: O painel GeoArchaeo acoplado no lado direito da janela do QGIS

### Seletor de idioma

Em cima à direita, a lista **«Idioma:»** (*Language:*) oferece **Italiano** e **English**, os dois únicos idiomas da interface do GeoArchaeo. A mudança é imediata, sem reiniciar o QGIS, e a escolha fica guardada nas definições do QGIS. Enquanto não houver escolha, o painel segue o idioma do QGIS: italiano se o QGIS estiver em italiano, inglês em todos os outros casos, portanto também com o QGIS em português.

---

## Interface do utilizador

De cima para baixo, o painel contém: o cabeçalho com os botões, o grupo **«Dados de entrada (usados por todos os separadores)»** (*Input data (used by all tabs)*), os **6 separadores** da análise e, durante os cálculos, a barra de progresso com o botão **«Cancelar»** (*Cancel*).

### Cabeçalho

| Elemento | Função |
|----------|--------|
| **«Carregar dados de exemplo»** (*Load example data*) | Abre a lista dos conjuntos de dados de teste incluídos no módulo (ver o separador Dados) |
| **«Tutorial»** (*Tutorial*) | Abre o guia integrado do GeoArchaeo, em italiano ou em inglês, que também pode ser aberto no navegador |
| **«Idioma:»** (*Language:*) | Lista Italiano / English |

### Dados de entrada

No grupo **«Dados de entrada (usados por todos os separadores)»** (*Input data (used by all tabs)*) escolhe-se uma só vez:

- **«Camada de pontos:»** (*Point layer:*): uma camada vetorial de pontos do projeto
- **«Campo de valor (numérico):»** (*Value field (numeric):*): o campo a analisar (a lista mostra apenas campos numéricos)

Por baixo aparece um resumo com os pontos válidos sobre o total, o SRC e a extensão da camada, por exemplo «500 pontos válidos de 500 · SRC EPSG:32633 · …» (*500 valid points of 500 · CRS EPSG:32633 · …*). Os pontos sem valor (NULL ou texto não numérico) não são contados como válidos. O resumo também avisa quando o projeto não tem camadas de pontos, quando a camada não tem campos numéricos ou quando o SRC é geográfico (graus).

Ao mudar de camada, o painel propõe também a distância máxima do variograma e o tamanho da célula do kriging, e pré-seleciona a camada no separador Padrões (ML) se ainda não houver nada selecionado.

### Os seis separadores

| Separador | Função | Resultado |
|-----------|--------|-----------|
| **Dados** (*Data*) | Estatísticas descritivas do campo | Tabela de estatísticas, histograma com diagrama de caixa |
| **Variograma** (*Variogram*) | Estrutura espacial dos valores | Efeito pepita, patamar, alcance, anisotropia, gráfico |
| **Kriging** (*Kriging*) | Interpolação sobre uma grelha regular | Rasters da estimativa e da incerteza, validação cruzada |
| **Padrões (ML)** (*Patterns (ML)*) | Grupos e anomalias com aprendizagem automática | Camada de pontos com a etiqueta do grupo |
| **Amostragem** (*Sampling*) | Proposta de novos pontos de amostragem | Camada de pontos e tabela de coordenadas |
| **Relatório** (*Report*) | Reunião das análises da sessão | Ficheiro HTML com gráficos interativos, ou PDF |

<!-- IMAGE: Cabecalho, grupo Dados de entrada e os seis separadores do GeoArchaeo -->
> **Fig. 3**: O cabeçalho, o grupo «Dados de entrada» e os seis separadores do painel GeoArchaeo

### Resultados e gráficos

Cada separador mostra os resultados num **quadro** por baixo do botão de cálculo, que se mantém visível até a análise ser repetida, e o **gráfico** no painel:

- se o QGIS dispuser de QtWebEngine, o gráfico Plotly é interativo diretamente no painel (zoom, valores ao passar o rato)
- caso contrário, aparece uma **pré-visualização estática** com a nota «Pré-visualização estática (QtWebEngine não disponível nesta instalação do QGIS).» (*Static preview (QtWebEngine not available in this QGIS installation).*)
- em ambos os casos, o botão **«Abrir gráfico interativo no navegador»** (*Open interactive chart in browser*) abre a versão interativa no navegador web

Os separadores Dados, Variograma e Kriging terminam com uma ligação para o passo seguinte, por exemplo **«Próximo passo: Variograma →»** (*Next step: Variogram →*).

### Análises em curso

O variograma, o kriging, o reconhecimento de padrões e a amostragem são calculados numa **thread separada**: o QGIS continua utilizável e, no fundo do painel, aparecem a **barra de progresso** (em percentagem para o kriging) e o botão **«Cancelar»** (*Cancel*). Executa-se uma análise de cada vez: ao iniciar outra aparece «Já está uma análise em curso: aguarde que termine ou cancele-a.» (*An analysis is already running: wait for it to finish or cancel it.*)

---

## Separador Dados

O separador **Dados** (*Data*, «1. Análise exploratória» / *1. Exploratory analysis*) descreve a distribuição dos valores antes de os interpolar.

### Cálculo das estatísticas

1. No grupo «Dados de entrada», escolher a camada de pontos e o campo numérico
2. Abrir o separador **Dados**
3. Clicar em **«Calcular estatísticas»** (*Calculate statistics*)

<!-- IMAGE: Separador Dados com estatisticas e histograma -->
> **Fig. 4**: O separador Dados com a tabela de estatísticas e o histograma do campo escolhido

### Estatísticas e interpretação

| Estatística | Descrição |
|-------------|-----------|
| **Número de valores** (*Number of values*), **Valores em falta** (*Missing values*) | Pontos com valor válido e pontos excluídos (NULL ou texto não numérico) |
| **Mínimo**, **Máximo**, **Média** (*Mean*), **Mediana** (*Median*) | Amplitude e posição dos valores |
| **Desvio-padrão** (*Std. deviation*), **Coeficiente de variação** (*Coeff. of variation*) | Dispersão absoluta e relativa |
| **Primeiro quartil (Q1)**, **Terceiro quartil (Q3)** (*First/Third quartile*) | Limites dos 50 % centrais dos valores |
| **Assimetria** (*Skewness*), **Curtose** (*Kurtosis*) | Forma da distribuição |

Por baixo da tabela, o painel acrescenta uma leitura em palavras:

- assimetria superior a 1: distribuição assimétrica à direita (poucos valores muito altos); convém ponderar uma transformação logarítmica antes do kriging, por exemplo criando um novo campo com a calculadora de campos
- assimetria inferior a -1: distribuição assimétrica à esquerda (poucos valores muito baixos)
- nos restantes casos: distribuição aproximadamente simétrica, adequada ao kriging
- o número de possíveis valores atípicos, isto é, para além de 3 desvios-padrão da média

O gráfico mostra o **histograma** dos valores com um **diagrama de caixa** (na pré-visualização estática, apenas o histograma).

### Dados de exemplo

O botão **«Carregar dados de exemplo»** (*Load example data*) abre a janela «Dados de exemplo do GeoArchaeo» (*GeoArchaeo example data*) com os conjuntos de dados da pasta `test_layers` do módulo; o caminho é indicado em **«Pasta:»** (*Folder:*) e pode ser mudado com **«Procurar…»** (*Browse…*). Os GeoPackage e os GeoJSON já estão assinalados. Os CSV só aparecem se não existir um GeoPackage ou um GeoJSON com o mesmo nome; têm de ser assinalados à mão e são carregados como texto delimitado (campos `x` e `y`, EPSG:32633). Com **OK**, as camadas são adicionadas ao projeto e a primeira camada de pontos carregada passa a ser a camada de entrada do painel.

| Conjunto de dados | Pontos | Principais campos numéricos | Utilização recomendada |
|-------------------|--------|-----------------------------|------------------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Estatísticas, variograma, kriging |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Os mesmos de `villa_ceramica` | Experimentar todos os separadores |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, teste com um conjunto grande |
| `necropoli` (GeoPackage) | 120 sepulturas | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN ou K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Kriging de propriedades do solo |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Kriging da densidade, amostragem |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variograma e kriging com poucos pontos |
| `area_studio` (GeoJSON) | 1 polígono | — | Área de estudo para a amostragem |

Entre os CSV, `magnetometria_grid` (2500 pontos, campo `mag_nT`) contém anomalias magnéticas simuladas (dois muros, uma fossa, um forno). Todos os dados são simulados e estão em EPSG:32633 (UTM 33N, metros). O polígono `area_studio` cobre a zona de `ricognizione_survey`, `unita_scavo_ceramica` e `magnetometria_grid`, não a dos restantes conjuntos de dados.

### Requisitos dos dados

- A camada tem de ser uma camada vetorial de **pontos** (nos multipontos usa-se o primeiro ponto)
- O campo tem de ser **numérico**: um campo de texto que contenha números tem de ser convertido com a calculadora de campos
- Os valores NULL ou não numéricos são excluídos automaticamente e contados como em falta
- São necessários pelo menos **5 pontos** com valor válido para o variograma e o kriging (1 para as estatísticas); um variograma fiável requer normalmente algumas dezenas de pontos
- Recomenda-se um **SRC projetado** em metros (por exemplo UTM): com um SRC geográfico o resumo avisa e o variograma e o kriging pedem confirmação

---

## Separador Variograma

O separador **Variograma** (*Variogram*, «2. Variograma» / *2. Variogram*) mede como a diferença entre os valores cresce com a distância: descreve a estrutura espacial dos dados e orienta o kriging.

### O que é um variograma?

O variograma relaciona a **semivariância** dos pares de pontos com a **distância** que os separa. Os parâmetros do modelo são:

| Parâmetro | Descrição |
|-----------|-----------|
| **Efeito pepita** (*nugget*) | Variabilidade a distância quase nula: erro de medição e variabilidade a pequena escala |
| **Patamar** (*sill*) | Variância total atingida pelo modelo (o "patamar") |
| **Alcance** (*range*) | Distância a partir da qual os valores deixam de estar correlacionados; no GeoArchaeo é o alcance prático (95 % do patamar) |

### Cálculo do variograma

1. Abrir o separador **Variograma**
2. No grupo **«Parâmetros»** (*Parameters*), verificar **«Distância máxima:»** (*Maximum distance:*): o botão **«Auto»** propõe cerca de 1/3 da diagonal da área ocupada pelos pontos (o mesmo valor é proposto ao mudar de camada)
3. Escolher o **«Modelo teórico:»** (*Theoretical model:*)
4. Se necessário, assinalar **«Verificar anisotropia (variogramas direcionais)»** (*Check anisotropy (directional variograms)*)
5. Clicar em **«Calcular variograma»** (*Calculate variogram*)

Os pares de pontos são agrupados em **15 classes de distância** (lags) entre zero e a distância máxima; o número de classes não pode ser alterado no painel. Acima de **3000 pontos**, o variograma é calculado sobre uma subamostra aleatória de 3000 pontos, porque o número de pares cresce com o quadrado do número de pontos. O modelo é ajustado por mínimos quadrados ponderados pelo número de pares de cada classe.

<!-- IMAGE: Separador Variograma com parametros e resultados -->
> **Fig. 5**: O separador Variograma com os parâmetros, o modelo teórico e o quadro de resultados

### Modelos teóricos

| Modelo | Comportamento | Quando usar |
|--------|---------------|-------------|
| **«Esférico (recomendado)»** (*Spherical (recommended)*) | Cresce até ao alcance e depois mantém-se constante | O mais usado: densidades de materiais, distribuições com limites nítidos |
| **«Exponencial»** (*Exponential*) | Cresce depressa junto à origem e atinge o patamar gradualmente | Fenómenos de decaimento contínuo, por exemplo elementos químicos no solo |
| **«Gaussiano»** (*Gaussian*) | Muito regular junto à origem | Fenómenos muito "suaves" (superfícies); usar com prudência |
| **«Matérn»** (*Matérn*) | Intermédio entre o exponencial e o gaussiano (ν = 1,5) | Alternativa flexível |

Regra prática: começar pelo modelo esférico e comparar o RMSE do seu ajuste com o dos outros modelos. O kriging usa o **último** variograma calculado: depois das comparações, voltar a calcular o modelo escolhido.

### Parâmetros manuais

O grupo **«Parâmetros manuais (opcional)»** (*Manual parameters (optional)*), desativado por omissão, permite fixar **«Efeito pepita:»** (*Nugget:*), **«Patamar (variância total):»** (*Sill (total variance):*) e **«Alcance (distância de correlação):»** (*Range (correlation distance):*). Com o grupo ativo, os valores diferentes de zero ficam fixos e os que ficarem em «Auto» (zero) são estimados.

### Leitura dos resultados

O quadro de resultados indica:

- o modelo com **efeito pepita**, **patamar**, **alcance** (nas unidades do SRC) e o **RMSE** do ajuste
- o número de pares de pontos e de classes de distância, com a subamostra usada, se houver
- uma leitura do alcance: até essa distância os valores estão espacialmente correlacionados, para além dela não se influenciam
- a razão efeito pepita/patamar: abaixo de 25 % forte continuidade a pequena escala, até 60 % continuidade moderada, acima de 60 % grande variabilidade a pequena escala ou erro de medição (o kriging será pouco informativo)

O gráfico mostra os pontos do variograma experimental (maiores onde há mais pares), a curva do modelo e as linhas do efeito pepita, do patamar e do alcance.

<!-- IMAGE: Variograma experimental com o modelo ajustado -->
> **Fig. 6**: Variograma experimental e modelo esférico com as linhas do efeito pepita, do patamar e do alcance

### Variogramas direcionais (anisotropia)

Com **«Verificar anisotropia (variogramas direcionais)»** assinalada, o GeoArchaeo calcula também os variogramas nas direções **0°, 45°, 90° e 135°** (ângulos medidos a partir de leste, no sentido anti-horário, tolerância ±22,5°). O efeito pepita e o patamar são os do variograma global; para cada direção estima-se o alcance.

- Se a razão entre o maior e o menor alcance ultrapassar **2**, o quadro assinala a anisotropia e a direção principal (por exemplo ao longo de um muro, de um caminho ou de uma vertente)
- Caso contrário, indica «Nenhuma anisotropia relevante» (*No relevant anisotropy*) com a razão calculada
- Com poucos pares por direção aparece «Pares insuficientes para os variogramas direcionais.» (*Not enough pairs for directional variograms.*)

No gráfico interativo, os variogramas direcionais são entradas da legenda inicialmente ocultas: clicar em 0°, 45°, 90° ou 135° para os mostrar (na pré-visualização estática são sempre desenhados). O kriging do painel usa o modelo omnidirecional: a anisotropia serve para a interpretação.

---

## Separador Kriging

O separador **Kriging** (*Kriging*, «3. Kriging ordinário» / *3. Ordinary kriging*) interpola os valores sobre uma grelha regular usando o variograma, produz também o mapa de incerteza e adiciona os rasters ao projeto.

### O kriging ordinário

O painel executa **kriging ordinário** (média local constante mas desconhecida), adequado à maior parte dos dados arqueológicos. Para cada célula usa os **20 pontos mais próximos**, encontrados com uma KD-tree; este número não pode ser alterado no painel. O co-kriging, o kriging espácio-temporal e o kriging por blocos para conjuntos de dados muito grandes existem apenas como algoritmos de Processing do plugin GeoArchaeo autónomo e não estão disponíveis no PyArchInit.

### Execução do kriging

1. Abrir o separador **Kriging** e ler a linha de estado do variograma (ver abaixo); o botão **«← Ir para o variograma»** (*← Go to Variogram*) volta ao separador anterior
2. Definir **«Tamanho da célula:»** (*Cell size:*), isto é, o lado de uma célula nas unidades do SRC: o painel propõe cerca de 100 células no lado maior da camada e mostra por baixo a grelha resultante («Grelha: … × … = … células» / *Grid: … × … = … cells*)
3. Deixar assinalada **«Usar o variograma calculado»** (*Use the calculated variogram*) para usar o variograma do separador anterior; se não estiver assinalada, o variograma é estimado automaticamente
4. Deixar assinalada **«Criar também o raster de incerteza (desvio-padrão)»** (*Also create the uncertainty raster (std. deviation)*) se for necessário o mapa de incerteza
5. Clicar em **«Executar kriging»** (*Run kriging*): a barra de progresso mostra a percentagem e **«Cancelar»** (*Cancel*) interrompe o cálculo

A linha de estado pode indicar:

- «Variograma disponível: …, alcance … ✓» (*Variogram available: …, range … ✓*): é usado o variograma calculado na mesma camada e no mesmo campo
- «Nenhum variograma calculado: será estimado automaticamente (modelo esférico).» (*No variogram calculated: it will be estimated automatically (spherical model).*)
- «O variograma foi calculado noutra camada/noutro campo: será recalculado.» (*The variogram was calculated on another layer/field: it will be recalculated.*), também neste caso com uma estimativa automática

> **Grelha**: a grelha cobre a extensão da camada de pontos e está limitada a **500 células por lado**. Se o tamanho de célula escolhido for demasiado fino, é aumentado automaticamente e a linha da grelha assinala-o («tamanho mínimo da célula … (máx. 500 células por lado)» / *minimum cell size … (max 500 cells per side)*). Acima de **40 000 células**, a linha fica cor de laranja e, ao iniciar, o painel pede confirmação, porque o cálculo pode demorar alguns minutos.

<!-- IMAGE: Rasters do kriging e metricas da validacao cruzada -->
> **Fig. 7**: Os rasters da estimativa e da incerteza no mapa, com o quadro de resultados e a validação cruzada

### Resultados do kriging

O kriging adiciona ao projeto dois rasters GeoTIFF no SRC da camada de pontos:

| Camada | Conteúdo | Estilo |
|--------|----------|--------|
| `Kriging_<campo>` | Valor estimado em cada célula | Rampa de cores do azul ao vermelho, passando pelo amarelo; visível |
| `Kriging_<campo>_uncertainty` | Desvio-padrão da estimativa (incerteza) | Rampa do amarelo-claro ao vermelho; adicionada no topo da lista de camadas, mas oculta |

Com o painel em italiano, o segundo raster chama-se `Kriging_<campo>_incertezza`. Os ficheiros são escritos numa **pasta temporária**: para os conservar, exportá-los a partir do menu de contexto da camada (**Exportar**).

O quadro de resultados resume os pontos usados, as dimensões da grelha, o tamanho da célula, o modelo e o alcance; o gráfico mostra o mapa dos valores estimados e o da incerteza, com os pontos amostrais sobrepostos.

### Validação cruzada leave-one-out

Depois do kriging, o GeoArchaeo efetua uma **validação cruzada leave-one-out**: cada ponto é retirado e reestimado a partir dos outros (num máximo de 200 pontos escolhidos ao acaso nos conjuntos grandes). As métricas aparecem no quadro de resultados:

| Métrica | Significado | Valor desejável |
|---------|-------------|-----------------|
| **RMSE** (*root mean squared error*) | Erro típico da estimativa | O mais baixo possível, comparado com o desvio-padrão dos dados |
| **MAE** (*mean absolute error*) | Erro médio em valor absoluto | O mais baixo possível |
| **ME** (*mean error, bias*) | Sobrestimação ou subestimação sistemática | Próximo de 0 |
| **R²** (*explained variance*) | Capacidade preditiva | A partir de 0,5 boa, abaixo de 0,2 fraca |
| **MSDR** (*standardized error*) | Realismo da incerteza estimada | Cerca de 1; acima de 1,5 incerteza subestimada, abaixo de 0,5 sobrestimada |

O painel acrescenta um juízo em palavras sobre a capacidade preditiva (boa, moderada ou fraca) e, quando for caso disso, sobre o MSDR.

> **Nota**: o kriging é executado numa **thread em segundo plano**, pelo que a interface do QGIS continua utilizável durante o cálculo; a barra de progresso indica o estado do processamento.

---

## Separador Padrões (ML)

O separador **Padrões (ML)** (*Patterns (ML)*, «4. Reconhecimento de padrões (aprendizagem automática)» / *4. Pattern recognition (machine learning)*) agrupa os pontos por posição e atributos numéricos, ou deteta anomalias, e cria uma camada com a etiqueta de cada ponto.

### Métodos disponíveis

| Método (entrada da lista) | O que faz | Parâmetros |
|---------------------------|-----------|------------|
| **«K-Means – grupos por semelhança»** (*K-Means – groups by similarity*) | Divide os pontos em K grupos semelhantes em posição e atributos | **«Número de grupos (0 = automático):»** (*Number of groups (0 = automatic):*); com 0, o número é escolhido de acordo com a quantidade de pontos (de 2 a 5) |
| **«DBSCAN – grupos por densidade (encontra também pontos isolados)»** (*DBSCAN – groups by density (also finds isolated points)*) | Encontra grupos por densidade sem fixar o seu número; os pontos isolados formam o grupo «Isolados / ruído» (*Isolated / noise*) | Automáticos |
| **«Isolation Forest – deteção de anomalias»** (*Isolation Forest – anomaly detection*) | Assinala como «Anomalia» (*Anomaly*) cerca de 10 % dos pontos mais diferentes dos outros; os restantes são «Normal» (*Normal*) | Automáticos |

### Execução

1. Abrir o separador **Padrões (ML)**
2. Na lista **«Camadas de pontos a analisar (uma ou mais):»** (*Point layers to analyse (one or more):*), selecionar uma ou mais camadas de pontos (se nada estiver selecionado, é pré-selecionada a camada de entrada)
3. Escolher o **«Método:»** (*Method:*)
4. Apenas para K-Means, definir **«Número de grupos (0 = automático):»**
5. Clicar em **«Iniciar reconhecimento de padrões»** (*Run pattern recognition*)

As variáveis analisadas são as **coordenadas X e Y** e **todos os campos numéricos** das camadas selecionadas, estandardizados; os valores em falta são substituídos pela média do campo. Não se usa, portanto, apenas o campo de valor escolhido em cima: entram todos os campos numéricos, incluindo identificadores e números sequenciais, e se estes distorcerem os grupos é preferível analisar uma cópia da camada só com os campos úteis. Ao analisar várias camadas em conjunto, convém que tenham os mesmos campos numéricos, pela mesma ordem, e o mesmo SRC (a camada criada usa o SRC da primeira camada selecionada).

<!-- IMAGE: Separador Padroes (ML) com a camada dos grupos -->
> **Fig. 8**: O separador Padrões (ML) com o gráfico dos grupos e a camada `ML_groups` no mapa

### Resultados

- O quadro de resultados indica o método, o número de grupos e quantos pontos caem em cada um (por exemplo «Grupo A (n=42)» / *Group A (n=42)*)
- O gráfico mostra os pontos no plano das duas primeiras componentes principais (PC1, PC2) das variáveis, coloridos por grupo
- É criada uma camada de pontos temporária, `ML_groups` (K-Means, DBSCAN) ou `ML_anomalies` (Isolation Forest), com uma legenda por categorias: cinzento para os pontos isolados, vermelho e maior para as anomalias; com o painel em italiano os nomes são `Gruppi_ML` e `Anomalie_ML`

| Campo | Conteúdo |
|-------|----------|
| `cluster_id` | Número do grupo (-1 = isolados com DBSCAN; 1 = anomalia e 0 = normal com Isolation Forest) |
| `cluster_name` | Nome legível, por exemplo «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Número de pontos do grupo |
| `method` | Método usado |
| `x_coord`, `y_coord` | Coordenadas do ponto |

### Classificação supervisionada

Por baixo do método, o painel lembra que a classificação supervisionada (Random Forest com um campo de etiquetas) se encontra em **Processing → GeoArchaeo**. Esse algoritmo pertence ao plugin GeoArchaeo autónomo: no PyArchInit o fornecedor de Processing do GeoArchaeo não é registado, pelo que o Random Forest não está disponível. Para o usar é necessário o plugin GeoArchaeo separado.

---

## Separador Amostragem

O separador **Amostragem** (*Sampling*, «5. Novos pontos de amostragem» / *5. New sampling locations*) sugere onde amostrar ou escavar no futuro a partir dos pontos existentes e cria uma camada com os pontos propostos.

### Critérios de amostragem

| Critério (entrada da lista) | Como escolhe os pontos | Quando usar |
|-----------------------------|------------------------|-------------|
| **«Cobertura (maximin)»** (*Coverage (maximin)*) | Cada novo ponto fica o mais longe possível de todos os outros | Preencher os vazios de forma uniforme |
| **«Redução da incerteza (variância de kriging)»** (*Uncertainty reduction (kriging variance)*) | Cada novo ponto vai para onde a variância de kriging é máxima | Reduzir o erro do kriging onde é maior |
| **«Grelha estratificada»** (*Stratified grid*) | Uma posição por célula de uma grelha regular, com uma ligeira perturbação aleatória | Cobertura regular de uma área definida |
| **«Adaptativo (zonas menos densas)»** (*Adaptive (sparser areas)*) | Extração aleatória com maior probabilidade onde há poucos pontos | Privilegiar as zonas menos amostradas mantendo uma componente aleatória |

O critério «Redução da incerteza» usa o variograma calculado se este disser respeito à mesma camada e ao mesmo campo e se, no separador Kriging, estiver assinalada «Usar o variograma calculado»; caso contrário, usa um modelo genérico baseado na distância típica entre os pontos.

### Planeamento da amostragem

1. Verificar **«Pontos existentes:»** (*Existing points:*): é a camada escolhida em cima no grupo «Dados de entrada» (para a amostragem o campo numérico não é necessário)
2. Opcional: escolher em **«Área de estudo (polígono, opcional):»** (*Study area (polygon, optional):*) uma camada de polígonos; todos os seus polígonos são unidos e reprojetados para o SRC dos pontos, mesmo que a camada esteja noutro SRC
3. Definir **«Novos pontos a propor:»** (*New points to propose:*) (de 1 a 500, 10 por omissão)
4. Escolher o **«Critério:»** (*Criterion:*): por baixo da lista aparece a sua descrição
5. Clicar em **«Calcular novos pontos»** (*Calculate new points*)

Sem área de estudo, os pontos são procurados no retângulo que contém os pontos existentes, alargado 20 % em cada lado.

<!-- IMAGE: Novos pontos de amostragem propostos -->
> **Fig. 9**: Os novos pontos de amostragem (estrelas amarelas) propostos dentro da área de estudo

### Resultados da amostragem

- O quadro de resultados indica quantos pontos foram propostos e com que critério; por baixo, a tabela «Coordenadas dos pontos propostos:» (*Coordinates of the proposed points:*) lista o número, X e Y
- É criada a camada de pontos temporária `New_sampling_points` (`Nuovi_punti_campionamento` com o painel em italiano), com símbolo de estrela amarela e os campos `point_id`, `x_coord`, `y_coord` e `type` (valor `suggested`)

---

## Separador Relatório

O separador **Relatório** (*Report*, «6. Relatório» / *6. Report*) reúne num único documento as análises efetuadas na sessão: estatísticas, gráficos interativos, parâmetros e validação.

### Conteúdo do relatório

No grupo **«Secções a incluir»** (*Sections to include*), cada secção é marcada como «disponível» (*available*) ou «ainda não calculado» (*not yet calculated*); as secções não calculadas não podem ser escolhidas.

| Secção | Conteúdo |
|--------|----------|
| **Estatísticas descritivas** (*Descriptive statistics*) | Camada e campo, tabela de estatísticas com a leitura em palavras, histograma |
| **Variograma** (*Variogram*) | Modelo, efeito pepita, patamar, alcance, RMSE, distância máxima, interpretação, gráfico |
| **Kriging e validação cruzada** (*Kriging and cross-validation*) | Método, tamanho da célula, dimensões da grelha, métricas da validação cruzada, gráfico |
| **Reconhecimento de padrões** (*Pattern recognition*) | Camadas analisadas, grupos com o respetivo número de pontos, gráfico |
| **Novos pontos de amostragem** (*New sampling locations*) | Critério, camada, tabela de coordenadas |

Cada secção contém a **última** análise do seu tipo efetuada na sessão.

### Geração do relatório

1. Efetuar as análises pretendidas nos outros separadores
2. Abrir o separador **Relatório** e deixar assinaladas as secções a incluir (estão assinaladas por omissão)
3. Clicar em **«Guardar relatório HTML»** (*Save HTML report*) ou em **«Guardar relatório PDF»** (*Save PDF report*) e escolher o nome do ficheiro

Ao guardar, o painel mostra também uma pré-visualização do relatório sem gráficos; a nota «Pré-visualização: os gráficos interativos estão incluídos no ficheiro HTML guardado.» (*Preview: the interactive charts are included in the saved HTML file.*) lembra onde se encontram.

<!-- IMAGE: Relatorio HTML do GeoArchaeo aberto no navegador -->
> **Fig. 10**: Um relatório HTML do GeoArchaeo com gráficos interativos, aberto no navegador

### Exportação

| Formato | Conteúdo | Notas |
|---------|----------|-------|
| **HTML** (`geoarchaeo_report.html`) | Texto, tabelas e **gráficos interativos** | O ficheiro é autónomo (a biblioteca de gráficos está incluída e funciona também sem ligação à rede) e abre-se de imediato no navegador |
| **PDF** (`geoarchaeo_report.pdf`) | Texto e tabelas, **sem gráficos** | Se não for possível criar o PDF, guardar o relatório HTML e imprimi-lo em PDF a partir do navegador |

Se não tiver sido efetuada nenhuma análise, aparece «Nenhuma análise disponível: execute primeiro pelo menos uma análise.» (*No analysis available: run at least one analysis first.*); se nenhuma secção estiver assinalada, «Selecione pelo menos uma secção» (*Select at least one section*).

---

## Fluxo de trabalho operacional

Um exemplo completo com os dados de exemplo incluídos no módulo (painel em inglês).

### Passo 1: Preparação dos dados

1. Abrir o GeoArchaeo a partir da barra de ferramentas do PyArchInit
2. Clicar em **«Carregar dados de exemplo»** (*Load example data*) e confirmar com **OK** (são carregados os GeoPackage e os GeoJSON)
3. No grupo «Dados de entrada», escolher a camada `villa_ceramica` e o campo `ceramic_count`
4. Verificar o resumo: 500 pontos válidos de 500, SRC EPSG:32633

### Passo 2: Exploração dos dados

1. Separador **Dados** → **«Calcular estatísticas»** (*Calculate statistics*)
2. Ler a assimetria e os valores atípicos; com uma forte assimetria à direita, ponderar uma transformação logarítmica

### Passo 3: Análise do variograma

1. Separador **Variograma** → **«Auto»** para a distância máxima, modelo **«Esférico (recomendado)»** (*Spherical (recommended)*) → **«Calcular variograma»** (*Calculate variogram*)
2. Repetir com **«Exponencial»** (*Exponential*) e comparar o RMSE do ajuste
3. Opcional: recalcular com **«Verificar anisotropia (variogramas direcionais)»**
4. Recalcular no fim o modelo escolhido e anotar efeito pepita, patamar e alcance

### Passo 4: Interpolação

1. Separador **Kriging**: verificar a linha «Variograma disponível … ✓» (*Variogram available … ✓*)
2. Manter o tamanho de célula proposto ou indicar 1 (metro)
3. **«Executar kriging»** (*Run kriging*)
4. Examinar os rasters `Kriging_ceramic_count` e `Kriging_ceramic_count_uncertainty` e os valores de R² e MSDR

### Passo 5: Padrões e amostragem (opcionais)

1. Separador **Padrões (ML)**: deixar selecionada na lista apenas `necropoli`, método DBSCAN → **«Iniciar reconhecimento de padrões»** (*Run pattern recognition*); a camada `ML_groups` mostra os grupos de sepulturas e os pontos isolados
2. Em cima, escolher a camada `ricognizione_survey` (campo `densita_mq`); separador **Amostragem**: área de estudo `area_studio`, 10 pontos, critério «Cobertura (maximin)» (*Coverage (maximin)*) → **«Calcular novos pontos»** (*Calculate new points*)

### Passo 6: Relatório

1. Separador **Relatório**: deixar assinaladas as secções disponíveis
2. **«Guardar relatório HTML»** (*Save HTML report*): o relatório abre-se no navegador com os gráficos interativos
3. Exportar os rasters e as camadas temporárias que se pretendam conservar

---

## Resolução de problemas

### Problemas comuns

| Problema | Causa | Solução |
|----------|-------|---------|
| «Nenhuma camada de pontos no projeto…» (*No point layer in the project: load one or use the example data.*) | O projeto não tem camadas de pontos | Adicionar uma camada de pontos ou usar **«Carregar dados de exemplo»** |
| «A camada não tem campos numéricos…» (*The layer has no numeric fields…*) | O campo a analisar é de texto | Convertê-lo em número com a calculadora de campos |
| «São necessários pelo menos 5 pontos com valor válido…» (*At least 5 points with a valid value are required (found …)*) | Demasiados valores NULL ou não numéricos | Verificar a tabela de atributos ou escolher outro campo |
| Aviso «SRC geográfico (graus)» (*geographic CRS (degrees)*) | A camada não está num SRC projetado | Reprojetar a camada, por exemplo para UTM, e repetir a análise |
| Erro «No point pairs within the maximum distance…» | Distância máxima do variograma demasiado pequena | Aumentar **«Distância máxima:»** ou usar **«Auto»** |
| «Pares insuficientes para os variogramas direcionais.» (*Not enough pairs for directional variograms.*) | Poucos pares por direção | Aumentar a distância máxima ou prescindir da verificação da anisotropia |
| Kriging lento, pedido de confirmação ou «Memória insuficiente: aumente o tamanho da célula.» (*Out of memory: increase the cell size.*) | Grelha com demasiadas células | Aumentar **«Tamanho da célula:»** |
| R² baixo na validação cruzada | Pouca correlação espacial ou demasiado ruído | Considerar o mapa apenas indicativo e consultar o raster de incerteza |
| O DBSCAN coloca quase todos os pontos em «Isolados / ruído» (*Isolated / noise*) | Densidade uniforme ou demasiadas variáveis | Experimentar K-Means ou reduzir os campos numéricos |
| «Machine Learning features not available. Please install scikit-learn.» | Falta o scikit-learn | Instalar o scikit-learn no ambiente Python do QGIS |
| «Plotly visualization not available. Please install plotly.» | Falta o Plotly | Instalar o plotly no ambiente Python do QGIS |
| Gráfico apenas como imagem estática | QtWebEngine não disponível | Usar **«Abrir gráfico interativo no navegador»** (*Open interactive chart in browser*) |
| «Não é possível criar o PDF…» (*Cannot create the PDF…*) | Erro na impressão do PDF | Guardar o relatório HTML e imprimi-lo a partir do navegador |
| Painel não visível | Painel fechado | Voltar a abri-lo a partir da barra de ferramentas ou do menu pyArchInit: os resultados da sessão continuam lá |

### Erros frequentes

- **«Já está uma análise em curso…»** (*An analysis is already running: wait for it to finish or cancel it.*): aguardar o fim do cálculo ou carregar em «Cancelar»
- **«Análise cancelada»** (*Analysis cancelled*): a análise foi interrompida com «Cancelar» e não produziu resultados
- **«Selecione pelo menos uma camada»** (*Select at least one layer*, separador Padrões): selecionar pelo menos uma camada na lista
- **«Selecione a camada dos pontos existentes (acima)»** (*Select the existing points layer (above)*, separador Amostragem): escolher a camada no grupo «Dados de entrada»
- **«Selecione uma camada de pontos e um campo numérico (no topo do painel)»** (*Select a point layer and a numeric field (at the top of the panel)*): completar a escolha no grupo «Dados de entrada»

### Desempenho

- As análises são executadas numa **thread em segundo plano**: o QGIS continua utilizável e o cálculo pode ser cancelado
- O variograma usa no máximo 3000 pontos (subamostra aleatória) e a validação cruzada no máximo 200
- O kriging usa os 20 pontos mais próximos de cada célula: o tempo depende sobretudo do número de células
- A grelha está limitada a 500 × 500 células; acima de 40 000 células o painel pede confirmação
- Com conjuntos de dados grandes (por exemplo os 4800 pontos de `geofisica_survey`), aumentar o tamanho da célula

---

## Notas técnicas

### Versão e origem

- O módulo `modules/geoarchaeo/` está alinhado com o **GeoArchaeo 1.3.1**, o plugin autónomo de Enzo Cocca (github.com/enzococca/GeoArchaeo)
- No PyArchInit está integrado apenas o painel: o fornecedor de Processing do GeoArchaeo (co-kriging, kriging espácio-temporal, kriging por blocos, análise composicional, Random Forest) **não** é registado
- O módulo é compatível com o QGIS 3 (Qt5) e o QGIS 4 (Qt6)

### Dependências

| Biblioteca | Utilização |
|------------|------------|
| **NumPy** | Cálculos numéricos |
| **SciPy** | Ajuste dos modelos de variograma, procura de vizinhos (KD-tree), estatísticas |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, componentes principais (necessária para o separador Padrões) |
| **Plotly** | Gráficos interativos no painel e no relatório HTML |
| **Matplotlib** | Pré-visualizações estáticas dos gráficos quando falta o QtWebEngine |
| **QtWebEngine** (opcional) | Gráficos interativos diretamente no painel |
| **threadpoolctl** (opcional) | Limita as threads de cálculo durante as análises em segundo plano |
| **GDAL** | Escrita dos rasters GeoTIFF (incluído no QGIS) |

### Sistemas de referência

- As distâncias (distância máxima, alcance, tamanho da célula) são expressas nas **unidades do SRC da camada de pontos**
- Usar um **SRC projetado** em metros: com um SRC geográfico o resumo avisa e o variograma e o kriging pedem confirmação
- Os rasters do kriging e as camadas criadas usam o SRC da camada de pontos (no separador Padrões, o da primeira camada selecionada)
- A área de estudo é reprojetada automaticamente para o SRC dos pontos

### Camadas e ficheiros produzidos

| Produto | Tipo | Localização |
|---------|------|-------------|
| `Kriging_<campo>`, `Kriging_<campo>_uncertainty` | Raster GeoTIFF (compressão LZW) | Pasta temporária do sistema |
| `ML_groups` / `ML_anomalies` | Camada de pontos temporária (em memória) | Apenas no projeto aberto |
| `New_sampling_points` | Camada de pontos temporária (em memória) | Apenas no projeto aberto |
| Relatório | HTML ou PDF | Caminho escolhido ao guardar |

Os rasters e as camadas temporárias têm de ser exportados (menu de contexto da camada → **Exportar**) para não se perderem ao fechar o projeto. Os nomes das camadas seguem o idioma do painel no momento do cálculo.

### Definições

- O idioma do painel fica guardado nas definições do QGIS (chave `GeoArchaeo/language`)
- Os resultados permanecem em memória enquanto o QGIS estiver aberto: fechar o painel não os apaga

---

> **Nota**: O GeoArchaeo está em desenvolvimento contínuo. Para comunicar erros ou sugerir melhorias, utilize o sistema de registo de problemas (issues) do projeto PyArchInit no GitHub.
