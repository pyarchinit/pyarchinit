# PyArchInit - GeoArchaeo - Analise Geoestatistica

## Indice
1. [Introducao](#introducao)
2. [Acesso a ferramenta](#acesso-a-ferramenta)
3. [Interface do utilizador](#interface-do-utilizador)
4. [Separador Dados](#separador-dados)
5. [Separador Variograma](#separador-variograma)
6. [Separador Kriging](#separador-kriging)
7. [Separador Machine Learning](#separador-machine-learning)
8. [Separador Amostragem](#separador-amostragem)
9. [Separador Relatorio](#separador-relatorio)
10. [Fluxo de trabalho operacional](#fluxo-de-trabalho-operacional)
11. [Resolucao de problemas](#resolucao-de-problemas)
12. [Notas tecnicas](#notas-tecnicas)

---

## Introducao

**GeoArchaeo** e o modulo de analise geoestatistica integrado no PyArchInit. Fornece um conjunto completo de ferramentas para a analise espacial de dados arqueologicos, desde a modelacao de variogramas ate a interpolacao kriging, passando por predicoes com aprendizagem automatica e o desenho de estrategias de amostragem.

<!-- VIDEO: Introducao ao GeoArchaeo -->
> **Tutorial em video**: [Inserir ligacao do video de introducao ao GeoArchaeo]

### Porque a analise geoestatistica em arqueologia?

A analise geoestatistica permite:

- **Interpolar** valores entre pontos de amostragem conhecidos, criando superficies continuas a partir de dados discretos
- **Quantificar** a correlacao espacial nos dados arqueologicos (ex. densidade de achados, espessura de camadas)
- **Prever** distribuicoes espaciais em areas ainda nao escavadas
- **Otimizar** estrategias de amostragem para prospeccoes futuras
- **Gerar** relatorios analiticos completos para documentacao cientifica

### Visao geral do fluxo de trabalho

```
1. Carregar dados       2. Variograma          3. Kriging/ML
   (Separador Dados)       (Separador Variogr.)   (Separador Kriging/ML)
        |                      |                      |
   Selecionar camada      Calcular e modelar     Interpolacao ou
   e campos               variograma             predicao espacial
                               |                      |
                          4. Amostragem          5. Relatorio
                             (Separador Amostr.)    (Separador Relat.)
                                  |                      |
                             Desenhar             Gerar relatorio
                             estrategia           de analise
```

---

## Acesso a ferramenta

O GeoArchaeo esta acessivel a partir da barra de ferramentas do PyArchInit atraves do botao pendente de Ferramentas de Analise.

### A partir da barra de ferramentas

1. Localizar o botao **Ferramentas de Analise** (icone pendente) na barra de ferramentas do PyArchInit
2. Clicar na seta do menu pendente
3. Selecionar **GeoArchaeo** da lista

<!-- IMAGE: Botao Ferramentas de Analise na barra de ferramentas -->
> **Fig. 1**: O menu pendente Ferramentas de Analise na barra de ferramentas do PyArchInit

O painel GeoArchaeo aparece como um **widget acoplavel** na interface do QGIS. Pode ser arrastado, redimensionado ou desacoplado como qualquer outro painel do QGIS.

<!-- IMAGE: Painel GeoArchaeo acoplado no QGIS -->
> **Fig. 2**: O painel GeoArchaeo acoplado na janela do QGIS

### Seletor de idioma

O painel GeoArchaeo inclui um **seletor de idioma** no topo, que permite alterar o idioma da interface sem reiniciar o QGIS. Os idiomas suportados incluem italiano, ingles, alemao, frances, espanhol, arabe, catalao, romeno, portugues e grego.

---

## Interface do utilizador

O painel GeoArchaeo esta organizado em **6 separadores principais**, cada um dedicado a uma fase do fluxo de trabalho de analise geoestatistica.

| Separador | Icone | Funcao |
|-----------|-------|--------|
| **Dados** | Tabela | Carregar e explorar dados espaciais a partir de camadas QGIS |
| **Variograma** | Grafico | Calcular e modelar variogramas experimentais |
| **Kriging** | Grelha | Realizar interpolacao kriging (ordinario, universal) |
| **ML** | Cerebro | Predicoes espaciais com aprendizagem automatica |
| **Amostragem** | Alvo | Desenhar estrategias de amostragem para prospeccoes arqueologicas |
| **Relatorio** | Documento | Gerar relatorios de analise |

<!-- IMAGE: Visao geral dos 6 separadores do GeoArchaeo -->
> **Fig. 3**: Os seis separadores do painel GeoArchaeo

### Barra de ferramentas do painel

No topo do painel encontrara:

- **Seletor de idioma**: Menu pendente para alterar o idioma da interface
- **Carregar dados de exemplo**: Botao para carregar um conjunto de dados de teste
- **Ajuda**: Botao para aceder a documentacao

---

## Separador Dados

O separador **Dados** e o ponto de partida para qualquer analise geoestatistica. Permite carregar e visualizar os dados espaciais disponiveis nas camadas QGIS.

### Carregamento de dados

1. Abrir o separador **Dados**
2. Selecionar uma **camada vetorial** do menu pendente (sao listadas todas as camadas de pontos do projeto QGIS)
3. Selecionar o **campo de analise** (o campo numerico a analisar)
4. Clicar em **Carregar dados**

<!-- IMAGE: Separador Dados com camada e campo selecionados -->
> **Fig. 4**: O separador Dados com uma camada e um campo de analise selecionados

### Dados de exemplo

Para se familiarizar com a ferramenta, e possivel carregar um **conjunto de dados de exemplo** clicando no botao dedicado. O conjunto de dados de exemplo contem dados arqueologicos simulados com coordenadas e valores numericos adequados para analise geoestatistica.

### Exploracao de dados

Apos o carregamento, o separador apresenta:

| Informacao | Descricao |
|------------|-----------|
| **Numero de pontos** | Total de pontos carregados |
| **Extensao** | Caixa envolvente do conjunto de dados (xmin, ymin, xmax, ymax) |
| **Estatisticas** | Media, mediana, desvio padrao, min, max |
| **Pre-visualizacao** | Tabela com as primeiras linhas do conjunto de dados |

### Requisitos dos dados

- A camada deve ser uma **camada vetorial de pontos**
- O campo de analise deve conter **valores numericos**
- Os pontos devem ter **coordenadas validas** no sistema de referencia do projeto
- Recomendam-se pelo menos **30 pontos** para uma analise geoestatistica significativa

---

## Separador Variograma

O separador **Variograma** permite calcular e modelar variogramas experimentais, que descrevem a estrutura da correlacao espacial nos dados.

### O que e um variograma?

Um variograma e um grafico que mostra como a **variancia** entre pares de pontos muda em funcao da **distancia** que os separa. Os parametros chave sao:

| Parametro | Descricao |
|-----------|-----------|
| **Nugget** | Variancia a distancia zero (erro de medicao + variabilidade a microescala) |
| **Sill** | Variancia maxima atingida (patamar do variograma) |
| **Range** | Distancia alem da qual nao ha mais correlacao espacial |

### Calculo do variograma experimental

1. Certificar-se de que os dados foram carregados no separador Dados
2. Abrir o separador **Variograma**
3. Definir os parametros:
   - **Numero de lags**: Numero de intervalos de distancia (predefinido: 15)
   - **Distancia maxima**: Distancia maxima a considerar (predefinido: auto)
   - **Tolerancia angular**: Para variogramas direcionais (predefinido: omnidirecional)
4. Clicar em **Calcular variograma**

<!-- IMAGE: Variograma experimental calculado -->
> **Fig. 5**: Um variograma experimental calculado a partir de dados arqueologicos

### Modelacao do variograma

Apos o calculo do variograma experimental, e possivel ajustar um **modelo teorico**:

1. Selecionar o **tipo de modelo**:
   - **Esferico**: O modelo mais comum, atinge o sill a uma distancia finita
   - **Exponencial**: Atinge o sill assintoticamente
   - **Gaussiano**: Transicao gradual, adequado a fenomenos muito regulares
   - **Linear**: Variograma sem sill definido
2. Clicar em **Ajustar modelo**
3. Verificar os parametros estimados (nugget, sill, range) e a qualidade do ajuste

<!-- IMAGE: Modelo de variograma ajustado -->
> **Fig. 6**: Modelo esferico ajustado ao variograma experimental

### Variogramas direcionais

Para verificar a **anisotropia** (variacao da estrutura espacial em diferentes direcoes):

1. Definir uma **tolerancia angular** (ex. 22,5 graus)
2. Selecionar as **direcoes** a analisar (0, 45, 90, 135 graus)
3. Comparar os variogramas nas diferentes direcoes

---

## Separador Kriging

O separador **Kriging** permite realizar a interpolacao kriging, o metodo geoestatistico de referencia para a predicao espacial otima.

### Tipos de kriging disponiveis

| Tipo | Descricao | Quando usar |
|------|-----------|-------------|
| **Kriging ordinario** | Assume uma media local constante mas desconhecida | Caso mais comum, dados estacionarios |
| **Kriging universal** | Tem em conta uma tendencia espacial (deriva) | Quando os dados mostram uma tendencia direcional |

### Execucao do kriging

1. Certificar-se de que o variograma foi modelado no separador Variograma
2. Abrir o separador **Kriging**
3. Selecionar o **tipo de kriging** (ordinario ou universal)
4. Definir os parametros da grelha de saida:
   - **Resolucao**: Dimensao das celulas da grelha (em unidades do CRS)
   - **Extensao**: Automatica a partir do conjunto de dados ou personalizada
5. Definir os parametros do kriging:
   - **Pontos minimos**: Numero minimo de pontos vizinhos a usar
   - **Pontos maximos**: Numero maximo de pontos vizinhos a usar
   - **Raio de pesquisa**: Distancia maxima para pontos vizinhos
6. Clicar em **Executar kriging**

<!-- IMAGE: Resultado da interpolacao kriging -->
> **Fig. 7**: Mapa de interpolacao kriging com a grelha de predicao

### Resultados do kriging

A analise produz duas camadas raster:

- **Predicao**: Os valores interpolados na grelha
- **Variancia de kriging**: A incerteza da predicao em cada celula

As camadas sao adicionadas automaticamente ao projeto QGIS e apresentadas no mapa.

> **Nota**: A analise e executada num **thread em segundo plano**, pelo que a interface do QGIS permanece utilizavel durante o calculo. Uma barra de progresso indica o estado do processamento.

---

## Separador Machine Learning

O separador **ML** oferece metodos de aprendizagem automatica para predicoes espaciais, como alternativa ou complemento ao kriging.

### Algoritmos disponiveis

| Algoritmo | Descricao | Vantagens |
|-----------|-----------|-----------|
| **Random Forest** | Conjunto de arvores de decisao | Robusto, lida com relacoes nao lineares |
| **Gradient Boosting** | Arvores de decisao sequenciais | Alta precisao, adequado para padroes complexos |
| **SVR** | Regressao por vetores de suporte | Bom com poucos dados, kernels flexiveis |

### Fluxo de trabalho ML

1. Abrir o separador **ML**
2. Selecionar o **algoritmo** desejado
3. Configurar as **variaveis preditoras**:
   - Coordenadas (X, Y)
   - Campos adicionais da camada (ex. altitude, declive, distancia a um rio)
4. Definir os **parametros** do algoritmo (ou usar os valores predefinidos)
5. Selecionar o metodo de **validacao**:
   - Validacao cruzada k-fold (predefinido: 5 folds)
   - Hold-out (percentagem de teste)
6. Clicar em **Treinar modelo**

<!-- IMAGE: Configuracao do modelo ML -->
> **Fig. 8**: Configuracao de um modelo Random Forest no separador ML

### Resultados ML

| Resultado | Descricao |
|-----------|-----------|
| **Mapa de predicao** | Camada raster com os valores previstos |
| **Importancia das variaveis** | Grafico da importancia relativa das variaveis preditoras |
| **Metricas de validacao** | R-quadrado, RMSE, MAE da validacao cruzada |
| **Grafico de residuos** | Diagrama de dispersao dos valores observados vs previstos |

### Comparacao Kriging vs ML

Para comparar resultados:

1. Executar tanto o kriging como o ML nos mesmos dados
2. Comparar as metricas de validacao no separador Relatorio
3. Visualizar mapas de diferencas

---

## Separador Amostragem

O separador **Amostragem** permite desenhar estrategias de amostragem otimas para prospeccoes arqueologicas futuras.

### Estrategias de amostragem

| Estrategia | Descricao | Quando usar |
|------------|-----------|-------------|
| **Aleatoria simples** | Pontos distribuidos aleatoriamente na area | Quando nao ha informacao previa |
| **Aleatoria estratificada** | Pontos aleatorios dentro de estratos definidos | Quando a area tem zonas com caracteristicas diferentes |
| **Grelha regular** | Pontos numa grelha regular | Para cobertura uniforme da area |
| **Otimizada** | Pontos posicionados para minimizar a variancia de kriging | Quando se dispoe de um variograma |

### Desenho do plano de amostragem

1. Abrir o separador **Amostragem**
2. Selecionar a **estrategia** de amostragem
3. Definir o **numero de pontos** desejado
4. Definir a **area de estudo**:
   - A partir da extensao da camada atual
   - A partir de uma camada poligonal
   - Desenhando manualmente no mapa
5. Definir eventuais **restricoes**:
   - Distancia minima entre pontos
   - Areas de exclusao
6. Clicar em **Gerar amostragem**

<!-- IMAGE: Pontos de amostragem gerados -->
> **Fig. 9**: Pontos de amostragem otimizada sobrepostos ao mapa da area de estudo

### Resultados da amostragem

- Uma **camada vetorial de pontos** com os pontos de amostragem e adicionada ao projeto QGIS
- Uma **tabela de atributos** com as coordenadas e identificadores dos pontos
- Um **relatorio** com as estatisticas da estrategia (cobertura, distancias, etc.)

---

## Separador Relatorio

O separador **Relatorio** permite gerar relatorios completos da analise geoestatistica.

### Conteudo do relatorio

O relatorio inclui automaticamente todas as analises realizadas durante a sessao:

| Seccao | Conteudo |
|--------|---------|
| **Resumo** | Visao geral do conjunto de dados e analises realizadas |
| **Dados** | Estatisticas descritivas, distribuicao, mapa de pontos |
| **Variograma** | Variograma experimental, modelo, parametros |
| **Interpolacao** | Mapa de kriging/ML, metricas de validacao |
| **Amostragem** | Estrategia, mapa de pontos, estatisticas |
| **Conclusoes** | Interpretacao sintetica dos resultados |

### Geracao do relatorio

1. Abrir o separador **Relatorio**
2. Selecionar as **seccoes** a incluir (todas por predefinicao)
3. Definir o **formato de saida**:
   - PDF (recomendado para documentacao)
   - HTML (para consulta interativa)
   - Markdown (para edicao posterior)
4. Introduzir eventuais **notas adicionais** ou comentarios
5. Clicar em **Gerar relatorio**

<!-- IMAGE: Pre-visualizacao do relatorio gerado -->
> **Fig. 10**: Pre-visualizacao de um relatorio de analise geoestatistica gerado pelo GeoArchaeo

### Exportacao

O relatorio pode ser guardado localmente ou exportado nos formatos disponiveis. As imagens (graficos, mapas) sao incorporadas diretamente no relatorio.

---

## Fluxo de trabalho operacional

Apresenta-se de seguida um fluxo de trabalho tipico para uma analise geoestatistica completa no GeoArchaeo:

### Passo 1: Preparacao dos dados

1. Carregar a camada vetorial de pontos no QGIS
2. Verificar que o campo numerico a analisar esta presente e correto
3. Verificar o sistema de referencia de coordenadas

### Passo 2: Exploracao dos dados

1. Abrir o GeoArchaeo a partir da barra de ferramentas
2. No separador **Dados**, selecionar a camada e o campo
3. Examinar as estatisticas descritivas
4. Verificar a distribuicao dos dados (procurar valores atipicos ou anomalos)

### Passo 3: Analise do variograma

1. No separador **Variograma**, calcular o variograma experimental
2. Experimentar diferentes modelos (esferico, exponencial, gaussiano)
3. Escolher o modelo com o melhor ajuste
4. Registar os parametros (nugget, sill, range)

### Passo 4: Interpolacao

1. No separador **Kriging**, definir os parametros da grelha
2. Executar o kriging ordinario
3. Examinar o mapa de predicao e a variancia
4. Opcionalmente, comparar com um modelo ML no separador ML

### Passo 5: Amostragem (opcional)

1. No separador **Amostragem**, desenhar uma estrategia para prospeccoes futuras
2. Utilizar o variograma para a amostragem otimizada

### Passo 6: Relatorio

1. No separador **Relatorio**, gerar o relatorio final
2. Exportar em PDF para documentacao

---

## Resolucao de problemas

### Problemas comuns

| Problema | Causa | Solucao |
|----------|-------|---------|
| Nenhuma camada disponivel | Nao ha camadas de pontos no projeto | Adicionar uma camada vetorial de pontos ao projeto QGIS |
| Sem campos numericos | A camada nao tem campos numericos | Verificar a tabela de atributos da camada |
| Variograma plano | Dados sem correlacao espacial | Verificar os dados, aumentar a distancia maxima |
| O kriging falha | Modelo de variograma nao ajustado | Ajustar primeiro um modelo no separador Variograma |
| Maus resultados ML | Dados insuficientes ou variaveis nao informativas | Adicionar variaveis preditoras ou aumentar os dados |
| Painel nao visivel | Widget fechado acidentalmente | Reabrir a partir do menu Ferramentas de Analise |

### Erros frequentes

- **"Dados insuficientes"**: Sao necessarios pelo menos 30 pontos para uma analise fiavel
- **"Modelo de variograma nao definido"**: Ajustar um modelo antes de executar o kriging
- **"CRS incompativel"**: Todas as camadas devem usar o mesmo sistema de referencia

### Desempenho

- A analise e executada num **thread em segundo plano**: a interface do QGIS permanece utilizavel
- Para conjuntos de dados muito grandes (>10.000 pontos), o processamento pode demorar mais
- E possivel monitorizar o progresso atraves da barra na parte inferior do painel

---

## Notas tecnicas

### Dependencias

O GeoArchaeo utiliza as seguintes bibliotecas Python:

| Biblioteca | Utilizacao |
|-----------|-----------|
| **NumPy** | Calculos numericos e matriciais |
| **SciPy** | Otimizacao e ajuste de modelos |
| **scikit-learn** | Algoritmos de aprendizagem automatica |
| **Matplotlib** | Geracao de graficos |

### Sistemas de referencia

- O GeoArchaeo trabalha no sistema de referencia do projeto QGIS atual
- Recomenda-se um **CRS projetado** (em metros) para a analise geoestatistica
- Sistemas geograficos (em graus) podem produzir resultados imprecisos

### Exportacao de resultados

Os resultados podem ser exportados em varios formatos:

- **Camadas raster** (GeoTIFF) para superficies interpoladas
- **Camadas vetoriais** (GeoPackage, Shapefile) para pontos de amostragem
- **Graficos** (PNG, SVG) para variogramas e diagnosticos
- **Relatorios** (PDF, HTML, Markdown) para documentacao

### Integracao com QGIS

- As camadas de saida sao adicionadas automaticamente ao painel de **Camadas** do QGIS
- O estilo das camadas raster pode ser personalizado com as propriedades de camada do QGIS
- Os resultados sao compativeis com todas as ferramentas de analise espacial do QGIS

---

> **Nota**: O GeoArchaeo esta em desenvolvimento ativo. Para reportar erros ou sugerir melhorias, utilize o sistema de seguimento de problemas do projeto PyArchInit no GitHub.
