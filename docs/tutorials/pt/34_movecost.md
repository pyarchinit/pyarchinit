# PyArchInit - MoveCost - Analise de Caminhos de Menor Custo

## Indice

1. [Introducao](#introducao)
2. [Acesso a ferramenta](#acesso-a-ferramenta)
3. [Pre-requisitos](#pre-requisitos)
4. [Interface do utilizador](#interface-do-utilizador)
5. [Separador Algoritmos](#separador-algoritmos)
6. [Separador Resultados](#separador-resultados)
7. [Separador Exportacao](#separador-exportacao)
8. [Separador Definicoes](#separador-definicoes)
9. [Fluxo de trabalho operacional](#fluxo-de-trabalho-operacional)
10. [Resolucao de problemas](#resolucao-de-problemas)
11. [Notas tecnicas](#notas-tecnicas)

---

## Introducao

**MoveCost** e uma ferramenta autonoma do PyArchInit para analise de caminhos de menor custo (Least-Cost Path Analysis, LCPA) baseada em scripts R. A analise de caminhos de menor custo e uma metodologia fundamental em arqueologia da paisagem que permite modelar os percursos mais provaveis entre localizacoes, tendo em conta a topografia do terreno e o custo energetico do movimento.

### Historia

Anteriormente, a funcionalidade MoveCost estava integrada diretamente no formulario de Sitio (Site form) do PyArchInit. A partir da versao atual, o MoveCost foi extraido como **ferramenta de analise independente**, acessivel atraves de um QDialog dedicado. Esta separacao oferece varias vantagens:

- **Interface dedicada**: Um dialogo com 4 separadores organizados por funcao
- **Melhor organizacao**: Algoritmos, resultados, exportacao e definicoes claramente separados
- **Acesso rapido**: Disponivel na barra de ferramentas sem abrir o formulario de Sitio
- **Extensibilidade**: Estrutura modular que facilita a adicao de novos algoritmos

### O que e a analise de caminhos de menor custo?

A analise de caminhos de menor custo calcula o percurso otimo entre dois ou mais pontos numa superficie de custo derivada de um modelo digital do terreno (MDT). O custo do movimento depende do declive do terreno e e calculado utilizando funcoes de custo anisotropicas que tem em conta a direcao do movimento (subida vs descida).

<!-- IMAGE: Exemplo de caminho de menor custo sobre MDT -->
> **Fig. 1**: Exemplo de caminho de menor custo calculado sobre um modelo digital do terreno

---

## Acesso a ferramenta

### A partir da barra de ferramentas

1. Localizar o botao suspenso **Ferramentas de Analise** (Analysis Tools) na barra de ferramentas do PyArchInit -- tem um icone de grafico/analise
2. Clicar na seta do menu suspenso
3. Selecionar **MoveCost** no menu

<!-- IMAGE: Botao Ferramentas de Analise na barra de ferramentas -->
> **Fig. 2**: O botao Ferramentas de Analise na barra de ferramentas do PyArchInit com o menu suspenso aberto

### Janela de dialogo

Ao clicar, abre-se um **QDialog modal** com quatro separadores:

```
+-----------------------------------------------------------+
|  MoveCost - Analise de Caminhos de Menor Custo             |
+-----------------------------------------------------------+
| [Algoritmos] | [Resultados] | [Exportacao] | [Definicoes] |
+-----------------------------------------------------------+
|                                                           |
|              (Conteudo do separador ativo)                  |
|                                                           |
+-----------------------------------------------------------+
|                              [Fechar]                      |
+-----------------------------------------------------------+
```

---

## Pre-requisitos

Antes de utilizar o MoveCost, verificar que os seguintes componentes estao instalados e configurados:

### 1. R (Linguagem estatistica)

| Requisito | Detalhe |
|-----------|---------|
| **Software** | R (versao >= 4.0 recomendada) |
| **Transferencia** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verificacao** | Abrir um terminal e digitar `R --version` |

### 2. Pacote R `movecost`

Instalar o pacote a partir do R:

```r
install.packages("movecost")
```

Dependencias principais instaladas automaticamente: `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Requisito | Detalhe |
|-----------|---------|
| **Extensao** | Processing R Provider |
| **Instalacao** | QGIS > Extensoes > Gerir e instalar extensoes > Procurar "Processing R Provider" |
| **Configuracao** | Definicoes de processamento > Fornecedores > R > Caminho da pasta R |

### 4. Dados de entrada

- **MDT/MDE**: Um raster do modelo digital do terreno para a area de estudo
- **Camada de pontos**: Pontos de origem e destino para a analise
- **Camada de poligonos**: (Opcional) Para as variantes "by polygon" dos algoritmos

### Lista de verificacao rapida

```
+-------------------------------------------+
| Lista de verificacao de pre-requisitos     |
+-------------------------------------------+
| [x] R instalado e no PATH                |
| [x] Pacote movecost instalado no R       |
| [x] Processing R Provider ativo no QGIS  |
| [x] MDT carregado no projeto QGIS         |
| [x] Camada de pontos com origens/destinos |
+-------------------------------------------+
```

---

## Interface do utilizador

O dialogo MoveCost esta organizado em **4 separadores**, cada um com uma funcao especifica.

### Vista geral dos separadores

| Separador | Icone | Funcao |
|-----------|-------|--------|
| **Algoritmos** | Engrenagem | Selecionar e executar os 14 algoritmos de analise |
| **Resultados** | Grafico | Visualizar estatisticas de custo e graficos R |
| **Exportacao** | Disco | Exportar resultados para CSV, PDF ou HTML |
| **Definicoes** | Chave inglesa | Configurar scripts R, idioma, organizacao de camadas |

<!-- IMAGE: Vista geral do dialogo MoveCost com 4 separadores -->
> **Fig. 3**: O dialogo MoveCost com os quatro separadores visiveis

---

## Separador Algoritmos

O separador **Algoritmos** e o nucleo da ferramenta MoveCost. Contem **14 algoritmos** baseados em scripts R, organizados em **3 grupos funcionais**.

### Grupo 1: Superficie de custo e caminhos

Algoritmos para o calculo de superficies de custo acumuladas e caminhos de menor custo.

| Algoritmo | Descricao |
|-----------|-----------|
| **movecost** | Calcula a superficie de custo acumulada anisotropica dependente do declive e os caminhos de menor custo a partir de um ponto de origem |
| **movecost by polygon** | O mesmo, mas utilizando uma area poligonal para definir a extensao do MDT |
| **movebound** | Calcula os limites de custo de deslocamento dependentes do declive em torno de localizacoes pontuais |
| **movebound by polygon** | O mesmo, mas utilizando um poligono |

### Grupo 2: Analise de corredores e redes

Algoritmos para analise de corredores de custo e redes de caminhos otimos.

| Algoritmo | Descricao |
|-----------|-----------|
| **movecorr** | Calcula o corredor de menor custo entre localizacoes pontuais |
| **movecorr by polygon** | O mesmo, mas utilizando um poligono |
| **movealloc** | Calcula a alocacao de custo de deslocamento dependente do declive para as origens |
| **movealloc by polygon** | O mesmo, mas utilizando um poligono |
| **movenetw** | Calcula a rede de caminhos de menor custo entre multiplos pontos |
| **movenetw by polygon** | O mesmo, mas utilizando um poligono |

### Grupo 3: Comparacao e classificacao

Algoritmos para comparar funcoes de custo e classificar destinos.

| Algoritmo | Descricao |
|-----------|-----------|
| **movecomp** | Compara caminhos de menor custo gerados utilizando diferentes funcoes de custo |
| **movecomp by polygon** | O mesmo, mas utilizando um poligono |
| **moverank** | Classifica os destinos por custo de deslocamento a partir de uma origem |
| **moverank by polygon** | O mesmo, mas utilizando um poligono |

### Como executar um algoritmo

1. Selecionar o algoritmo desejado da lista
2. A interface de processamento do QGIS abre-se com os parametros especificos do algoritmo
3. Configurar os parametros de entrada:
   - **MDT/MDE**: Selecionar o raster do terreno
   - **Ponto(s) de origem**: Selecionar a camada de pontos
   - **Poligono** (se variante "by polygon"): Selecionar a area de estudo
   - **Funcao de custo**: Escolher entre as funcoes disponiveis (Tobler, Minetti, etc.)
4. Clicar em **Executar**
5. Os resultados sao adicionados automaticamente ao projeto QGIS

<!-- IMAGE: Separador Algoritmos com 3 grupos -->
> **Fig. 4**: O separador Algoritmos com os tres grupos de algoritmos destacados

<!-- IMAGE: Interface de processamento para um algoritmo movecost -->
> **Fig. 5**: A interface de processamento do QGIS para o algoritmo movecost com os parametros configurados

### Variantes "by polygon"

As variantes "by polygon" de cada algoritmo permitem:
- **Limitar a area de analise** a uma regiao especifica
- **Reduzir o tempo de calculo** ao trabalhar com um MDT recortado
- **Focalizar a analise** numa area de interesse arqueologico

---

## Separador Resultados

O separador **Resultados** permite visualizar os resultados das analises executadas.

### Resumo de custos (Cost Summary)

Uma area de texto (QTextEdit) apresenta as estatisticas resumidas das camadas de custo geradas:

| Estatistica | Descricao |
|-------------|-----------|
| **Minimo** | Valor minimo de custo na superficie |
| **Maximo** | Valor maximo de custo na superficie |
| **Media** | Valor medio de custo |
| **Desv. Padrao** | Desvio padrao dos valores de custo |

```
+---------------------------------------------------+
| Resumo de custos                                   |
+---------------------------------------------------+
| Camada: movecost_accumulated_cost                  |
| Minimo: 0.00                                       |
| Maximo: 15234.56                                   |
| Media: 4521.89                                     |
| Desv. Padrao: 2103.45                              |
|                                                    |
| Camada: movecost_back_link                         |
| Minimo: 0.00                                       |
| Maximo: 8.00                                       |
| Media: 4.12                                        |
+---------------------------------------------------+
```

### Visualizador de graficos R (R Plot Viewer)

O visualizador de graficos R apresenta o ultimo grafico gerado pelos scripts R:

| Funcao | Descricao |
|--------|-----------|
| **Visualizacao automatica** | Apresenta o ultimo grafico R do diretorio temporario |
| **Atualizar** | Recarrega o ultimo grafico disponivel |
| **Guardar** | Guarda o grafico atual num ficheiro de imagem (PNG, JPG) |
| **Selecao manual** | Permite abrir um grafico R especifico de qualquer localizacao |

<!-- IMAGE: Separador Resultados com resumo de custos e grafico R -->
> **Fig. 6**: O separador Resultados apresentando as estatisticas de custo e um grafico R

### Localizacoes dos graficos R

Os graficos R sao guardados nos diretorios temporarios do QGIS/R. O visualizador procura automaticamente nas seguintes localizacoes:

- Diretorio temporario do QGIS Processing
- Diretorio temporario do R (`tempdir()`)
- Pasta de saida especificada pelo utilizador

---

## Separador Exportacao

O separador **Exportacao** oferece tres opcoes para exportar os resultados da analise.

### Exportar tabela de custos (CSV)

Exporta as estatisticas das camadas de custo para um ficheiro CSV:

1. Clicar em **Exportar tabela de custos**
2. Selecionar a localizacao e o nome do ficheiro
3. O ficheiro CSV contem: nome da camada, minimo, maximo, media, desvio padrao

| Coluna | Descricao |
|--------|-----------|
| `layer_name` | Nome da camada de custo |
| `min_value` | Valor minimo |
| `max_value` | Valor maximo |
| `mean_value` | Valor medio |
| `std_dev` | Desvio padrao |

### Exportar relatorio (PDF)

> **Nota**: Esta funcionalidade esta atualmente em desenvolvimento (stub). Estara disponivel numa versao futura.

### Exportar relatorio (HTML)

Gera um relatorio HTML completo e estilizado que inclui:

- **Cabecalho** com titulo do projeto e data
- **Parametros da analise** utilizados
- **Estatisticas das camadas** em formato tabular
- **Graficos R** incorporados como imagens
- **Estilo CSS integrado** para uma apresentacao profissional

1. Clicar em **Exportar relatorio (HTML)**
2. Selecionar a localizacao e o nome do ficheiro
3. O relatorio abre-se automaticamente no navegador predefinido

<!-- IMAGE: Exemplo de relatorio HTML exportado -->
> **Fig. 7**: Um exemplo de relatorio HTML gerado pelo MoveCost com estatisticas e graficos

---

## Separador Definicoes

O separador **Definicoes** permite configurar a ferramenta MoveCost.

### Instalar scripts R

| Funcao | Descricao |
|--------|-----------|
| **Instalar scripts R** | Copia os scripts R do movecost para o diretorio de processamento do QGIS |

Esta operacao e necessaria na **primeira configuracao** ou apos uma atualizacao da extensao. Os scripts sao copiados para a pasta de scripts R do Processing:

```
{QGIS_HOME}/processing/rscripts/
```

### Selecao de idioma

O MoveCost suporta **5 idiomas** para a interface:

| Idioma | Codigo |
|--------|--------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

O idioma selecionado aplica-se a:
- Etiquetas da interface do dialogo
- Mensagens de estado e erro
- Cabecalhos das tabelas de resultados

### Organizacao de camadas

| Funcao | Descricao |
|--------|-----------|
| **Organizar camadas** | Organizacao e estilizacao automatica das camadas de saida do movecost |

Esta funcao:
1. Agrupa as camadas de saida em grupos logicos no painel de Camadas do QGIS
2. Aplica estilos de cor predefinidos (rampas de cor para superficies de custo)
3. Renomeia as camadas com nomes descritivos

### Documentacao

| Funcao | Descricao |
|--------|-----------|
| **Ajuda** | Abre a documentacao integrada da ferramenta |

<!-- IMAGE: Separador Definicoes com todas as opcoes -->
> **Fig. 8**: O separador Definicoes do MoveCost com as opcoes de configuracao

---

## Fluxo de trabalho operacional

### Exemplo passo a passo: Calculo de um caminho de menor custo

Este exemplo mostra como calcular um caminho de menor custo entre um povoado e uma fonte de agua.

### Passo 1: Preparacao dos dados

```
1. Carregar o MDT da area de estudo no projeto QGIS
2. Criar uma camada de pontos com:
   - Ponto de origem (povoado)
   - Ponto(s) de destino (fonte de agua)
3. Verificar que o sistema de referencia de coordenadas e consistente
```

### Passo 2: Verificacao dos pre-requisitos

```
1. Abrir o MoveCost a partir da barra de ferramentas
2. Ir ao separador Definicoes
3. Clicar em "Instalar scripts R" (se for a primeira vez)
4. Verificar que nao sao reportados erros
```

### Passo 3: Execucao da analise

```
1. Mudar para o separador Algoritmos
2. Selecionar "movecost" do Grupo 1
3. Na janela de processamento:
   - MDT: selecionar o raster do terreno
   - Origem: selecionar o ponto do povoado
   - Destino: selecionar o ponto da fonte de agua
   - Funcao de custo: Tobler (recomendada por predefinicao)
4. Clicar em Executar
5. Aguardar a conclusao do processamento
```

### Passo 4: Analise dos resultados

```
1. Mudar para o separador Resultados
2. Rever o Resumo de custos para as estatisticas
3. Examinar o grafico R para a visualizacao
4. No canvas do QGIS, observar:
   - A superficie de custo acumulada (raster colorido)
   - O caminho de menor custo (linha vetorial)
```

### Passo 5: Exportacao

```
1. Mudar para o separador Exportacao
2. Exportar a tabela de custos para CSV para analises adicionais
3. Gerar o relatorio HTML para documentacao
4. Guardar o grafico R a partir do separador Resultados
```

### Passo 6: Organizacao

```
1. Voltar ao separador Definicoes
2. Clicar em "Organizar camadas" para ordenar os resultados
3. As camadas sao agrupadas e estilizadas automaticamente
```

<!-- IMAGE: Fluxo de trabalho completo com capturas de ecra anotadas -->
> **Fig. 9**: O fluxo de trabalho completo desde a preparacao dos dados ate aos resultados finais

---

## Resolucao de problemas

### R nao encontrado

**Sintoma**: Mensagem de erro "R nao encontrado" ou "R is not installed"

**Solucoes**:
1. Verificar que R esta instalado: abrir um terminal e digitar `R --version`
2. Verificar o caminho do R nas definicoes de Processing:
   - **QGIS** > **Definicoes** > **Opcoes** > **Processamento** > **Fornecedores** > **R**
   - Definir o **caminho da pasta R** corretamente
3. No macOS, R pode estar em `/Library/Frameworks/R.framework/Resources/`
4. No Windows, normalmente em `C:\Program Files\R\R-4.x.x\`
5. No Linux, verificar com `which R`

### Scripts R em falta

**Sintoma**: Os algoritmos nao aparecem na caixa de ferramentas de processamento

**Solucoes**:
1. Abrir MoveCost > Definicoes > clicar em **Instalar scripts R**
2. Reiniciar o QGIS apos instalar os scripts
3. Verificar que o Processing R Provider esta ativo:
   - **QGIS** > **Extensoes** > **Gerir e instalar extensoes** > Verificar "Processing R Provider"
4. Verificar a pasta de scripts R: `{QGIS_HOME}/processing/rscripts/`

### Graficos R nao aparecem

**Sintoma**: O separador Resultados nao apresenta nenhum grafico

**Solucoes**:
1. Clicar em **Atualizar** no separador Resultados
2. Utilizar **Selecao manual** para navegar ate a pasta de graficos
3. Verificar que a analise foi concluida com sucesso
4. Verificar os diretorios temporarios:
   - macOS/Linux: `/tmp/` ou `$TMPDIR`
   - Windows: `%TEMP%`
5. Alguns algoritmos podem nao gerar graficos

### Pacote movecost nao instalado no R

**Sintoma**: Erro "there is no package called 'movecost'"

**Solucoes**:
1. Abrir R ou RStudio
2. Executar: `install.packages("movecost")`
3. Verificar: `library(movecost)` -- nao deve produzir erros
4. Se existirem problemas de dependencias: `install.packages("movecost", dependencies = TRUE)`

### Analise muito lenta

**Sintoma**: O processamento demora muito tempo

**Solucoes**:
1. Utilizar as variantes **"by polygon"** para limitar a area de calculo
2. Reduzir a resolucao do MDT (reamostragem)
3. Verificar as dimensoes do MDT:
   - MDTs muito grandes (>10000x10000 pixeis) requerem tempo consideravel
   - Recortar o MDT para a area de interesse antes da analise
4. Fechar outras aplicacoes para libertar RAM

### Erro de projecao / SRC

**Sintoma**: Resultados inconsistentes ou erro de sistema de referencia de coordenadas

**Solucoes**:
1. Verificar que o MDT e as camadas de pontos tem o **mesmo SRC**
2. Utilizar um **SRC projetado** (metrico), nao geografico
3. SRC recomendados: UTM (p.ex. EPSG:32632 para Italia central)
4. Reprojetar as camadas se necessario antes da analise

---

## Notas tecnicas

### Arquitetura da ferramenta

O MoveCost e implementado como um **QDialog** autonomo (`MoveCostDialog`) que:
- Interage com o QGIS Processing Framework para a execucao de algoritmos R
- Le os resultados das camadas carregadas no projeto
- Gere a visualizacao de graficos R atraves de QLabel/QPixmap
- Gera relatorios HTML utilizando modelos predefinidos

### Ficheiros fonte

| Ficheiro | Descricao |
|----------|-----------|
| `tabs/MoveCost.py` | Dialogo principal e logica da interface |
| `gui/ui/MoveCost.ui` | Layout da interface Qt Designer |
| `resources/r_scripts/` | Scripts R para os algoritmos movecost |

### Funcoes de custo suportadas

O pacote R `movecost` suporta varias funcoes de custo anisotropicas:

| Funcao | Autor | Descricao |
|--------|-------|-----------|
| **Tobler** | Tobler (1993) | Funcao classica de custo de marcha |
| **Minetti** | Minetti et al. (2002) | Baseada no custo metabolico |
| **Herzog** | Herzog (2010) | Variante modificada |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Modelo energetico |
| **Outras** | Varios | Consultar a documentacao do pacote R |

### Referencias bibliograficas

- Alberti, G. (2019). `movecost`: An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibilidade

| Componente | Versao minima |
|------------|--------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| Pacote movecost (R) | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Tutorial em video

### MoveCost - Analise de Caminhos de Menor Custo
`[Marcador: video_movecost.mp4]`

**Conteudo**:
- Configuracao do R e do pacote movecost
- Instalacao dos scripts R no QGIS
- Execucao do algoritmo movecost basico
- Visualizacao dos resultados e graficos R
- Exportacao de relatorios

**Duracao estimada**: 20-25 minutos

---

*Documentacao PyArchInit - MoveCost*
*Versao: 5.0.x*
*Ultima atualizacao: Fevereiro 2026*
