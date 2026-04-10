# PyArchInit - Gestao de Obra

## Indice

1. [Introducao](#introducao)
2. [Acesso ao modulo](#acesso-ao-modulo)
3. [Painel de Obra (Dashboard)](#painel-de-obra-dashboard)
4. [Ficha de Pessoal](#ficha-de-pessoal)
5. [Ficha de Presencas](#ficha-de-presencas)
6. [Ficha de Equipamentos](#ficha-de-equipamentos)
7. [Ficha de Orcamento](#ficha-de-orcamento)
8. [Visualizacao 2D e 3D do Computo Metrico](#visualizacao-2d-e-3d-do-computo-metrico)
9. [Exportacao PDF e CSV do Painel](#exportacao-pdf-e-csv-do-painel)
10. [Fluxo de trabalho operacional](#fluxo-de-trabalho-operacional)
11. [Perguntas frequentes](#perguntas-frequentes)

---

## Introducao

O modulo **Gestao de Obra** do PyArchInit fornece um conjunto integrado de ferramentas para a administracao operacional de um estaleiro arqueologico. Atraves de cinco formularios interligados, o responsavel de escavacao pode controlar orcamentos, gerir pessoal e presencas, inventariar equipamentos e calcular volumes de terra movimentada.

O modulo e composto por:

| Componente | Funcao |
|------------|--------|
| **Painel de Obra** | Dashboard central com resumos e indicadores |
| **Pessoal** | Registo CRUD de colaboradores do estaleiro |
| **Presencas** | Registo CRUD de presencas diarias e horas de trabalho |
| **Equipamentos** | Registo CRUD de maquinas e ferramentas |
| **Orcamento** | Registo CRUD de rubricas orcamentais por ano |

Todos os formularios partilham a mesma barra de ferramentas DBMS padrao do PyArchInit, permitindo navegacao, pesquisa, ordenacao e operacoes CRUD de forma consistente.

<!-- IMAGE: Vista geral dos 5 icones na barra de ferramentas Gestao de Obra -->
> **Fig. 1**: Os cinco icones do modulo Gestao de Obra na barra de ferramentas do PyArchInit

---

## Acesso ao modulo

### Barra de ferramentas dedicada

Ao ativar a extensao PyArchInit, uma barra de ferramentas intitulada **"pyArchInit - Gestao de Obra"** e adicionada automaticamente a interface do QGIS. Esta barra contem cinco icones:

| Icone | Nome | Formulario aberto |
|-------|------|-------------------|
| Painel | **Painel de Obra** | Dashboard central (`Cantiere.ui`) |
| Pessoa | **Pessoal** | Ficha de pessoal (`Personale.ui`) |
| Relogio | **Presencas** | Ficha de presencas (`Presenze.ui`) |
| Ferramenta | **Equipamentos** | Ficha de equipamentos (`Attrezzature.ui`) |
| Moeda | **Orcamento** | Ficha de orcamento (`Budget.ui`) |

### Menu da extensao

Em alternativa, aceder atraves de: **Extensoes** > **pyArchInit - Archaeological GIS Tools** e selecionar o formulario pretendido (Painel de Obra, Pessoal, Presencas, Equipamentos ou Orcamento).

<!-- IMAGE: Menu da extensao com as opcoes de Gestao de Obra destacadas -->
> **Fig. 2**: Acesso ao modulo Gestao de Obra a partir do menu de extensoes

---

## Painel de Obra (Dashboard)

O **Painel de Obra** e o ponto de entrada central do modulo. Apresenta uma visao sintetica de todos os dados operacionais do estaleiro selecionado.

<!-- IMAGE: Vista geral do Painel de Obra com todas as seccoes visiveis -->
> **Fig. 3**: Interface completa do Painel de Obra

### Seletores de contexto

No topo do dialogo encontram-se dois seletores que determinam o contexto de todos os dados apresentados:

| Seletor | Descricao |
|---------|-----------|
| **Sitio** | Selecionar o sitio arqueologico (preenche-se automaticamente com o sitio configurado) |
| **Ano** | Selecionar o ano de referencia (ultimos 10 anos) |

O botao **Atualizar** recarrega manualmente todos os paineis. Os dados sao tambem atualizados automaticamente ao alterar o sitio ou o ano.

### Resumo do orcamento

Esta seccao apresenta o estado financeiro do estaleiro para o ano selecionado.

| Indicador | Descricao |
|-----------|-----------|
| **Montante previsto** | Soma de todos os `importo_previsto` das rubricas orcamentais |
| **Montante efetivo** | Soma de todos os `importo_effettivo` registados |
| **Barra de progresso** | Percentagem do orcamento consumido (efetivo / previsto x 100) |
| **Grafico circular** | Distribuicao do orcamento efetivo por categoria |

<!-- IMAGE: Seccao de resumo do orcamento com barra de progresso e grafico circular -->
> **Fig. 4**: Resumo orcamental com barra de progresso a 67% e grafico circular por categoria

### Resumo do pessoal

Apresenta dados de presenca do dia atual e totais mensais.

| Indicador | Descricao |
|-----------|-----------|
| **Presentes** | Numero de colaboradores com tipo de jornada "trabalho" no dia de hoje |
| **Ferias** | Numero de colaboradores em ferias |
| **Baixa** | Numero de colaboradores em baixa medica |
| **Horas/mes** | Total de horas (ordinarias + extraordinarias) no mes corrente |
| **Custo/mes** | Soma dos custos diarios no mes corrente |

<!-- IMAGE: Seccao de resumo do pessoal com contadores e totais mensais -->
> **Fig. 5**: Resumo do pessoal mostrando 12 presentes, 2 em ferias, 1 em baixa

### Resumo dos equipamentos

Apresenta o estado do parque de equipamentos do estaleiro.

| Indicador | Descricao |
|-----------|-----------|
| **Total** | Numero total de equipamentos registados para o sitio |
| **Em uso** | Equipamentos com estado `em_uso` |
| **Manutencao** | Equipamentos com estado `manutencao` |
| **Alertas** | Numero de equipamentos com manutencao atrasada (data de proxima manutencao anterior a hoje) |

Quando existem equipamentos com manutencao atrasada, o alerta e apresentado a vermelho e em negrito.

<!-- IMAGE: Seccao de resumo dos equipamentos com alerta de manutencao a vermelho -->
> **Fig. 6**: Resumo dos equipamentos com alerta de 2 manutencoes atrasadas

### Computo metrico

A seccao de computo metrico permite calcular areas e volumes a partir de modelos digitais de elevacao (DEM) e apresenta o historico de calculos anteriores.

#### Tipos de calculo

| Tipo | Descricao |
|------|-----------|
| **Diferenca DEM** | Calcula o volume a partir da diferenca entre dois DEM (pre e pos-escavacao) |
| **DEM + Poligono** | Calcula a area/volume de uma zona delimitada por um poligono sobre um DEM |

#### Seletores de camadas

| Campo | Descricao |
|-------|-----------|
| **DEM pre** | Camada raster do terreno antes da intervencao |
| **DEM pos** | Camada raster do terreno apos a intervencao |
| **Camada de poligono** | Camada vetorial com os poligonos de delimitacao |

#### Como calcular

Para **Diferenca DEM**: selecionar os DEM pre e pos-escavacao e clicar em **Calcular**. O resultado apresenta o volume em metros cubicos. Para **DEM + Poligono**: selecionar o DEM e a camada de poligono de delimitacao e clicar em **Calcular**. O resultado apresenta area (m2) e volume (m3).

Apos o calculo, clicar em **Guardar computo** para registar o resultado na base de dados.

#### Tabela de historico

A tabela apresenta todos os calculos anteriores com as seguintes colunas:

| Coluna | Descricao |
|--------|-----------|
| **Data** | Data do calculo |
| **Tipo** | Diferenca DEM ou DEM+Poligono |
| **Area (m2)** | Area calculada em metros quadrados |
| **Volume (m3)** | Volume calculado em metros cubicos |
| **Notas** | Observacoes livres |

<!-- IMAGE: Seccao de computo metrico com seletores de DEM e tabela de historico -->
> **Fig. 7**: Computo metrico com dois calculos registados na tabela de historico

A partir da versao 5.1, ao lado do botao **Calcular** estao tambem disponiveis os botoes **Mostrar 2D**, **Mostrar 3D** e **Criar malha 3D**, para visualizar o resultado do calculo diretamente no mapa e numa vista tridimensional interativa. Ver a seccao [Visualizacao 2D e 3D do Computo Metrico](#visualizacao-2d-e-3d-do-computo-metrico).

### Novo esquema por separadores do Painel de Obra

A partir da versao atual, a janela **Painel de Obra** foi reorganizada em **tres separadores** para dar espaco ao novo painel de **Analise de Custos** sem sobrecarregar a vista. A linha de cabecalho com **Sitio**, **Ano** e o botao **Atualizar** mantem-se visivel por cima dos separadores, de modo que se pode trocar de sitio ou de ano a qualquer momento: todos os separadores sao atualizados automaticamente.

| Separador | Conteudo |
|-----------|----------|
| **Resumo** | E a vista que aparece ao abrir o painel. Em cima, em toda a largura, o **Resumo de Orcamento** (barra de progresso e grafico circular); por baixo, lado a lado, os resumos de **Pessoal** e **Equipamento** |
| **Computo Metrico** | Reune todo o fluxo de calculo DEM: combos **DEM Pre**, **DEM Post** e **Poligono**, botoes de opcao **Diferenca DEM** / **DEM sobre Poligono**, botao **Calcular**, etiquetas de **area** e **volume**, o novo grupo **Analise de Custos** (EUR/m3, m3/dia -> custo total, dias estimados, custo diario), botao **Guardar Registo**, botoes **Mostrar 2D** / **Mostrar 3D** / **Exportar 2DM + 3D** e a **tabela de historico** em baixo |
| **Exportacao** | Os botoes de **exportacao PDF** e **CSV** com uma breve descricao |

<!-- IMAGE: Novo esquema por separadores do Painel de Obra (Resumo / Computo Metrico / Exportacao) -->
> **Fig. 7a**: O novo esquema por separadores do Painel de Obra com o cabecalho Sitio / Ano / Atualizar sempre visivel

**Fix**: os DEM ja nao desaparecem ao premir **Calcular** (regressao da 5.0.13-alpha em que a atualizacao automatica dos combos reiniciava a selecao atual).

---

## Visualizacao 2D e 3D do Computo Metrico

A partir da versao 5.1, apos premir o botao **Calcular** no painel de Computo Metrico, o Painel de Obra deixa de se limitar a mostrar os valores numericos (area e volume): cria automaticamente um conjunto de camadas cartograficas e disponibiliza uma vista 3D interativa.

### O que acontece ao premir "Calcular"

No final de um calculo de diferenca de DEM, o Painel de Obra executa automaticamente os seguintes passos:

1. **Gravacao permanente do raster de diferenca**: o raster resultante (DEM pos - DEM pre) e gravado como GeoTIFF permanente em `<PYARCHINIT_HOME>/site_dashboard/<nome do sitio>/`. Assim o raster deixa de se perder ao fechar o QGIS e pode ser reutilizado a qualquer momento.
2. **Adicionado ao projeto QGIS**: o raster e adicionado ao painel de camadas dentro de um grupo dedicado chamado **"Site Dashboard - Computi"**, para manter todos os calculos organizados.
3. **Simbologia automatica**: o raster recebe uma **rampa de cores divergente**:
   - **Vermelho** para as zonas de escavacao (valores negativos, terra retirada)
   - **Azul** para as zonas de aterro (valores positivos, terra adicionada)
   - **Transparente / neutro** para as celulas com variacao insignificante (|diff| <= 1 cm)
4. **Poligonizacao da area de intervencao**: as celulas raster com |diff| > 1 cm sao convertidas numa camada vetorial de poligonos, igualmente adicionada ao grupo "Site Dashboard - Computi" com um estilo destacado, para mostrar num relance a extensao total da intervencao.
5. **Zoom automatico**: o canvas principal do QGIS e automaticamente centrado na extensao do calculo.

### Pre-requisitos

Para utilizar as novas visualizacoes 2D / 3D e necessario:

- Ter **duas camadas raster DEM** carregadas no projeto QGIS (tipicamente um DEM **pre** e um DEM **pos**-escavacao)
- Selecciona-las nos combos **DEM Pre** e **DEM Pos** do painel de Computo Metrico
- O sistema de coordenadas (CRS) dos dois rasters deve ser coerente

### Novos botoes

Ao lado do botao **Calcular** estao agora disponiveis tres novos botoes:

| Botao | Descricao |
|-------|-----------|
| **Mostrar 2D** | Recentra o mapa do QGIS na extensao do ultimo calculo. Util para voltar rapidamente ao Computo Metrico ativo depois de trabalhar noutras areas. |
| **Mostrar 3D** | Abre uma caixa de dialogo 3D interativa que utiliza o DEM **pre** como terreno, com o raster de diferenca sobreposto. Inclui: controlo de **exagero vertical**, caixas para ativar / desativar camadas individuais e um botao **Repor vista**. |
| **Criar malha 3D** | Cria malhas TIN a partir dos DEMs pre e pos (atraves dos algoritmos do QGIS Processing). As malhas podem ser mostradas dentro do visualizador 3D, permitindo comparar visualmente as duas superficies e o volume entre elas. |

<!-- IMAGE: Os novos botoes Mostrar 2D, Mostrar 3D e Criar malha 3D ao lado do botao Calcular -->
> **Fig. 7a**: Os novos botoes **Mostrar 2D**, **Mostrar 3D** e **Criar malha 3D** ao lado do botao **Calcular**

<!-- IMAGE: Caixa de dialogo 3D com DEM pre como terreno e raster de diferenca sobreposto -->
> **Fig. 7b**: A caixa de dialogo 3D interativa do Computo Metrico com exagero vertical e controlo de camadas

### Fluxo de trabalho tipico

1. Carregar no projeto QGIS os dois rasters DEM (pre e pos)
2. Abrir o **Painel de Obra**
3. No painel **Computo Metrico** seleccionar os dois DEMs em **DEM Pre** e **DEM Pos**
4. Clicar em **Calcular**: o raster de diferenca e o poligono de intervencao sao criados automaticamente e o mapa e centrado na extensao
5. Ler os valores numericos (area, volume, escavacao, aterro) diretamente no painel
6. Clicar em **Mostrar 3D** para abrir a vista tridimensional
7. (Opcional) Clicar em **Criar malha 3D** para gerar e visualizar as malhas TIN dos dois DEMs
8. Clicar em **Guardar computo** para arquivar o resultado no historico

### Organizacao em disco

Todos os rasters e camadas gerados pelo Computo Metrico sao guardados em:

```
<PYARCHINIT_HOME>/site_dashboard/<nome do sitio>/
```

onde `<PYARCHINIT_HOME>` e a pasta de trabalho configurada nas definicoes do PyArchInit e `<nome do sitio>` e o sitio atualmente selecionado no painel. Isto mantem um historico fisico de todos os calculos e permite reutilizar as camadas noutros projetos QGIS.

### Atualizacao: "Mostrar 2D" -- Caixa de dialogo de corte analitico

A partir da proxima versao, o botao **Mostrar 2D** do painel de Computo Metrico ja nao se limita a recentrar o mapa no ultimo calculo: abre agora uma **caixa de dialogo analitica baseada em matplotlib** que apresenta os resultados da escavacao como uma seccao arqueologica classica.

A caixa de dialogo esta disponivel **apenas quando o calculo foi efetuado no modo "Diferenca DEM"** (com DEM pre e DEM pos). Se utilizou o modo **DEM + Poligono**, o botao mantem o comportamento anterior e limita-se a fazer zoom no mapa do QGIS sobre a extensao do calculo.

Quando esta disponivel, a caixa de dialogo contem os seguintes paineis:

| Painel | Descricao |
|--------|-----------|
| **Mapa de calor da diferenca DEM** | Mapa de calor 2D do raster de escavacao/aterro com uma rampa de cores divergente (vermelho para escavacao, azul para aterro) |
| **Histograma** | Distribuicao das profundidades de **escavacao** e das alturas de **aterro**, para obter de imediato um resumo estatistico do volume movimentado |
| **Seccao longitudinal (E-O)** | A seccao arqueologica classica: o **DEM pre** e desenhado a **azul**, o **DEM pos** a **vermelho** e o volume escavado e **preenchido** entre as duas linhas |
| **Seccao transversal (N-S)** | Mesma logica da seccao E-O mas ao longo da direcao Norte-Sul |
| **Spinbox linha / coluna** | Permitem deslocar interativamente a posicao das duas seccoes sobre o raster para explorar toda a escavacao |
| **Botao "Guardar PNG"** | Exporta a figura completa (mapa de calor, histograma e ambas as seccoes) como imagem PNG, pronta para ser incluida no relatorio de escavacao |

<!-- IMAGE: Caixa de dialogo analitica Mostrar 2D com mapa de calor, histograma e seccoes E-O / N-S -->
> **Fig. 7d**: A nova caixa de dialogo analitica **Mostrar 2D** com mapa de calor da diferenca DEM, histograma de escavacao / aterro e ambas as seccoes longitudinal e transversal (DEM pre a azul, DEM pos a vermelho, volume escavado preenchido entre as duas linhas)

### Atualizacao: "Mostrar 3D" -- Alternativa matplotlib

O botao **Mostrar 3D** gere agora automaticamente dois cenarios consoante a versao do QGIS instalada:

1. **QGIS com o modulo 3D nativo (Qt3D disponivel)**: como antes, abre-se a caixa de dialogo `Qgs3DMapCanvas` incorporada, com terreno construido a partir do DEM pre, exagero vertical e controlo de camadas.
2. **QGIS sem o modulo 3D (erro "QGIS 3D module not available")**: o Painel de Obra passa automaticamente a utilizar um **visualizador 3D baseado em matplotlib**. Como o matplotlib faz parte das dependencias ja instaladas pelo plugin, este visualizador **funciona sempre**, mesmo em compilacoes minimais do QGIS sem suporte 3D.

O visualizador alternativo oferece:

| Controlo | Descricao |
|----------|-----------|
| **Modo de visualizacao** | Tres modos selecionaveis: **Pre + Pos** (ambas as superficies sobrepostas), **So diferenca** (apenas a superficie de escavacao/aterro), **So Pre** (o DEM pre como superficie de referencia) |
| **Exagero vertical** | Um cursor para acentuar a diferenca de cota entre as duas superficies -- util quando a escavacao e pouco profunda |
| **Rotacao interativa** | Arrastando com o rato e possivel rodar a cena 3D em tempo real para explorar a escavacao de qualquer angulo |

<!-- IMAGE: Visualizador 3D matplotlib alternativo em modo Pre + Pos -->
> **Fig. 7e**: O visualizador 3D matplotlib alternativo, utilizado quando o modulo Qt3D nativo do QGIS nao esta disponivel: mostra as superficies pre e pos com exagero vertical ajustavel

### Atualizacao: "Criar malha 3D" -- Simbologia terreno automatica

O botao **Criar malha 3D** aplica agora automaticamente uma **rampa de cores tipo terreno** ao grupo de datasets de elevacao da malha (**Bed Elevation**). Anteriormente a malha parecia uma superficie plana e dificil de ler; passa agora a ser imediatamente um mapa de cotas expressivo:

- **Verde** para as cotas mais baixas
- **Laranja** para as cotas intermedias
- **Castanho** para as cotas mais altas

Desta forma a malha fica imediatamente visivel e significativa no canvas do QGIS, mesmo antes de abrir a vista 3D. Apos construi-la, basta clicar em **Mostrar 3D** para a ver renderizada como superficie tridimensional, seja atraves do modulo 3D nativo do QGIS, seja atraves do visualizador matplotlib alternativo descrito acima.

<!-- IMAGE: Malha 3D com a nova rampa verde / laranja / castanho tipo terreno -->
> **Fig. 7f**: A malha 3D com a nova rampa de cores tipo terreno aplicada automaticamente ao seu dataset de elevacao

### Atualizacao: poligono como mascara de recorte

Se no painel Computo Metrico, alem dos dois DEMs, selecionar tambem uma camada vetorial no combo **Camada Poligono** mantendo ativo o modo **Diferenca DEM**, o poligono passa a ser utilizado como **mascara de recorte**: ambos os DEMs sao recortados pelo poligono antes do calculo da diferenca, de modo que a seccao analitica 2D, o fallback 3D em matplotlib e a malha TIN trabalham exclusivamente na area de intervencao. O fluxo tipico e: desenhar um poligono em torno da escavacao, selecionar os DEMs pre e pos, escolher o poligono no combo **Camada Poligono** e clicar em **Calcular**. Os dois rasters recortados sao adicionados automaticamente ao grupo **"Cruscotto Cantiere - Computi"** na arvore de camadas, prontos a serem reutilizados.

### Atualizacao: "Criar malha 3D" -- fim dos crashes

As versoes anteriores podiam provocar crashes do QGIS em algumas compilacoes devido a um segfault C++ no interior dos algoritmos de Processing usados para construir a malha. A geracao foi reescrita em **Python puro**: o Painel le o DEM com GDAL e escreve diretamente um ficheiro 2DM com uma **malha de quadrangulos em grelha regular**, sem depender dos algoritmos nativos. O resultado e seguro em qualquer versao do QGIS. As malhas com mais de cerca de **15 000 celulas** sao automaticamente subamostradas para manter a construcao rapida e o ficheiro leve, enquanto as celulas com valor nodata sao ignoradas: quando existe uma mascara poligonal ativa, a malha segue portanto a forma exata da area de intervencao recortada. Nos raros casos em que a geracao falha por outros motivos (disco cheio, permissoes), a caixa de dialogo sugere agora abrir diretamente **Mostrar 3D**, que utiliza o visualizador matplotlib de fallback e nao precisa de qualquer camada de malha.

### Atualizacao: auto-atualizacao dos combos ao clicar em "Calcular"

O painel Computo Metrico **atualiza agora automaticamente as listas de DEM e poligono sempre que se clica em "Calcular"**: deixa de ser necessario fechar e reabrir o Painel de Obra depois de carregar um novo raster ou desenhar um novo poligono no projeto. Basta adicionar a camada no QGIS, regressar ao painel e premir **Calcular** -- os combos **DEM Pre**, **DEM Pos** e **Camada Poligono** sao repopulados em tempo real com o estado atual do projeto. O eventual diagnostico do recorte (sucesso, SRC incompativel, intersecao vazia) aparece na **barra de mensagens do QGIS**, de modo a ser sempre claro quais camadas foram realmente utilizadas no calculo.

### Atualizacao: botao renomeado "Exportar 2DM + 3D"

O botao anteriormente designado **Criar malha 3D** foi renomeado para **Exportar 2DM + 3D** para refletir o seu novo comportamento: **deixou** de carregar a malha como camada no projeto QGIS (a API de malha nativa pode provocar crashes em algumas compilacoes do QGIS) e passa a executar duas acoes seguras e complementares. Escreve os ficheiros **2DM** em disco a partir dos DEMs pre e pos (uteis para importar em software externo de pos-processamento) e abre diretamente a **vista 3D matplotlib** sobre os DEMs recortados, permitindo avaliar visualmente o resultado de imediato. Deste modo, o risco de crash fica completamente eliminado, porque a API de malha do QGIS nunca chega a ser invocada.

### Atualizacao: recorte do poligono com diagnostico visivel

Quando se seleciona uma camada no combo **Camada Poligono** em conjunto com os dois DEMs, o recorte dos rasters pelo poligono passa a ser **registado na barra de mensagens do QGIS**: em caso de sucesso, e apresentada a lista dos ficheiros recortados escritos em disco; em caso de falha, e indicado o motivo concreto (por exemplo poligono num SRC diferente do dos DEMs, nenhuma intersecao geometrica entre poligono e raster, ficheiro de origem inexistente ou ilegivel). E assim imediato perceber por que razao um recorte nao foi aplicado e o que corrigir (reprojetar o poligono, move-lo sobre a area dos DEMs, verificar o caminho do ficheiro), sem ter de abrir logs ou a consola Python.

### Atualizacao: recorte do poligono tambem no modo "DEM sobre Poligono"

O recorte do poligono funciona agora tambem quando se seleciona o radio button **DEM sobre Poligono** (modo zonal-stats com um unico DEM): o raster passa a ser recortado pela extensao do poligono **antes** de ser passado aos visualizadores **Mostrar 2D**, **Mostrar 3D** e **Exportar 2DM + 3D**, de modo que o corte e a vista 3D apresentem apenas a area de intervencao em vez do DEM inteiro como acontecia anteriormente. A mensagem de diagnostico do recorte aparece na **barra de mensagens do QGIS** exatamente como no modo Diferenca DEM. Neste cenario com apenas um DEM, o visualizador **Mostrar 2D** adapta-se automaticamente: o heat-map mostra as cotas com uma rampa de cores **terrain**, o histograma representa a distribuicao das cotas com a linha da media, e as duas seccoes longitudinal/transversal desenham apenas uma linha de cota (sem preenchimento entre pre e pos, porque nao existe DEM pos).

### Atualizacao: Analise de Custos do Computo Metrico

No painel Computo Metrico do Painel de Obra foi adicionado um novo bloco **Analise de Custos** com dois parametros de entrada: **Custo unitario** (em euros/m3) e **Produtividade** (em m3/dia). A cada pressao do botao **Calcular**, o painel atualiza automaticamente tres valores derivados visiveis num relance: **Custo total** (volume x custo unitario), **Dias estimados** (volume / produtividade) e **Custo diario** (custo unitario x produtividade). Ambas as entradas sao guardadas automaticamente **por obra** nas definicoes do QGIS (chaves `pyArchInit/site_dashboard/costs/<obra>/...`), bastando introduzi-las uma unica vez por cada obra: ao mudar de obra os valores guardados sao recarregados automaticamente, e os tres totais sao recalculados em tempo real em cada novo calculo.

### Atualizacao: recorte pre/pos alinhado

O calculo da diferenca DEM exige que os dois DEM (pre e pos) estejam exatamente alinhados sobre a mesma grelha de pixeis. Nas versoes anteriores, ao usar um poligono de recorte, os dois DEM recortados podiam acabar em grelhas ligeiramente diferentes e o calculo `pre - pos` resultava incorreto ou vazio. Agora ambos os recortes utilizam a **resolucao nativa do DEM pre** como referencia (mesmos `xRes` / `yRes` e mesmo alinhamento de grelha), de modo que os dois rasters recortados coincidem sempre ao nivel do pixel e a diferenca produz um resultado valido. Ate mesmo as trincheiras minimas das quais apenas foram retirados "10 baldes de terra" (cerca de 1 m3) sao agora capturadas corretamente pelo computo.

### Atualizacao: novo combo "Muros / Estruturas"

No painel Computo Metrico foi adicionado um segundo combo **Muros / Estruturas** que permite selecionar uma camada de poligonos que representam muros, estruturas em alcado, pilares ou outras partes construidas que **nao devem ser contabilizadas** no calculo dos metros cubicos de escavacao. Quando se carrega em **Calcular**, os poligonos dos muros sao rasterizados como NODATA sobre o raster de diferenca recortado e as suas celulas sao excluidas do total de volume; a mensagem de diagnostico aparece na barra de mensagens do QGIS (por exemplo `walls masked: muri_trincea_42`). Fluxo de trabalho arqueologico tipico: carregar DEM pre + DEM pos + poligono da area de escavacao + poligono dos muros encontrados, selecionar ambos nos dois combos e premir **Calcular** -- o volume escavado exclui automaticamente o volume das estruturas.

---

## Exportacao PDF e CSV do Painel

O Painel de Obra permite exportar um resumo completo dos dados de gestao em dois formatos: **PDF** (documento paginado, ideal para entrega ao cliente ou arquivo) e **CSV** (ideal para analises posteriores em Excel ou outras folhas de calculo).

### Exportacao PDF

O botao **Exportar PDF** gera um relatorio completo da obra. A partir da versao 5.1, o PDF inclui:

- **Capa renovada** com nome do sitio, ano de referencia e data de geracao
- **Resumo de orcamento** com tabelas detalhadas por categoria e totais (previsto vs efetivo)
- **Resumo de pessoal** com estatisticas de presencas, horas trabalhadas e custos
- **Resumo de equipamentos** com estado do inventario e manutencoes em atraso
- **Nova seccao "Computo Metrico"** com:
  - Tabela detalhada de todos os calculos guardados
  - **Totais**: area total (m2) e volume total (m3)
  - **Estatisticas**: volume de escavacao, volume de aterro, area afetada
- **Nova seccao "Analise de Custos"** (inserida entre **Computo Metrico** e **Estatisticas**) com um parameter card dos valores configurados (custo unitario em euros/m3 e produtividade em m3/dia), tabela detalhada por registo (data, tipo, volume, custo, dias estimados, custo diario) e linha de **totais** ao fundo da tabela; o bloco **Estatisticas** foi estendido com **custo total** e **dias totais** de obra
- **Suporte completo a caracteres especiais**: a renderizacao do PDF foi corrigida para todas as linguas suportadas, incluindo as letras acentuadas do romeno (**a**, **a**, **i**, **s**, **t**), os caracteres **gregos**, **arabes**, **portugueses** e **catalaes**.

### Exportacao CSV

O botao **Exportar CSV** gera um ficheiro CSV compativel com as principais folhas de calculo. A partir da versao 5.1:

- **Codificacao UTF-8 com BOM**: garante que o Excel (especialmente a versao europeia) abra o ficheiro corretamente sem corromper as letras acentuadas e os caracteres especiais
- **Separador `;`** (ponto e virgula): compativel com a localizacao europeia do Excel
- **Seccao COMPUTO METRICO**: inclui todos os dados de computo metrico, com tipo, area, volume e notas de cada calculo
- **Nova seccao `=== ANALISE DE CUSTOS ===`**: comeca com os dois parametros (custo unitario em euros/m3 e produtividade em m3/dia) e segue-se a tabela detalhada por registo (data, tipo, volume, custo, dias estimados, custo diario), pronta a ser filtrada ou agregada em Excel
- **Bloco SUMMARY final estendido**: um resumo agregado com totais e estatisticas, util para analises rapidas sem ter de escrever formulas; agora inclui tambem **Custo total** e **Dias totais** calculados a partir da nova Analise de Custos

<!-- IMAGE: PDF exportado com a nova seccao Computo Metrico -->
> **Fig. 7c**: Exemplo de PDF exportado com a nova seccao **Computo Metrico** (tabela, totais e estatisticas)

<!-- IMAGE: CSV exportado aberto em Excel com a seccao COMPUTO METRICO e o bloco SUMMARY -->
> **Fig. 7d**: Exemplo de CSV exportado aberto em Excel com a seccao **COMPUTO METRICO** e o bloco **SUMMARY** final

---

## Ficha de Pessoal

A **Ficha de Pessoal** permite gerir o registo dos colaboradores afetos ao estaleiro arqueologico.

<!-- IMAGE: Interface completa da Ficha de Pessoal -->
> **Fig. 8**: Interface da Ficha de Pessoal

### Campos do formulario

| Campo | Tipo | Descricao |
|-------|------|-----------|
| **Sitio** | ComboBox | Sitio arqueologico ao qual o colaborador esta afeto |
| **Nome** | Texto | Nome proprio do colaborador |
| **Apelido** | Texto | Apelido do colaborador |
| **Qualificacao** | Texto | Formacao ou habilitacao profissional |
| **Funcao** | Texto | Funcao desempenhada no estaleiro (p.ex. arqueologo, topografo, operario) |
| **Data de contratacao** | Data | Data de inicio da colaboracao |
| **Data de fim** | Data | Data prevista de fim de contrato (pode ficar vazio) |
| **Custo diario** | Numerico | Custo diario do colaborador (em euros) |
| **Notas** | Texto | Observacoes adicionais |

### Barra de ferramentas DBMS

A ficha utiliza a barra de ferramentas DBMS padrao do PyArchInit:

| Botao | Funcao |
|-------|--------|
| **Novo registo** | Limpa o formulario para introduzir um novo colaborador |
| **Guardar** | Guarda o registo atual (novo ou editado) |
| **Eliminar registo** | Remove o colaborador atual (com confirmacao) |
| **Ver todos** | Mostra todos os registos |
| **Nova pesquisa** | Ativa o modo de pesquisa |
| **Pesquisar** | Executa a pesquisa com os criterios preenchidos |
| **Ordenar por** | Abre o painel de ordenacao |
| **Navegacao** | Primeiro, anterior, seguinte, ultimo registo |

<!-- IMAGE: Barra de ferramentas DBMS da Ficha de Pessoal -->
> **Fig. 9**: Barra de ferramentas DBMS com indicadores de estado

---

## Ficha de Presencas

A **Ficha de Presencas** regista a assiduidade diaria de cada colaborador, incluindo o tipo de jornada, horas trabalhadas e custo associado.

<!-- IMAGE: Interface completa da Ficha de Presencas -->
> **Fig. 10**: Interface da Ficha de Presencas

### Campos do formulario

| Campo | Tipo | Descricao |
|-------|------|-----------|
| **Sitio** | ComboBox | Sitio arqueologico |
| **ID Pessoal** | ComboBox/Texto | Identificador do colaborador (ligacao a ficha de pessoal) |
| **Data** | Data | Data da presenca |
| **Tipo de jornada** | ComboBox | `trabalho`, `ferias`, `baixa` ou `licenca` |
| **Horas ordinarias** | Numerico | Numero de horas de trabalho normal |
| **Horas extraordinarias** | Numerico | Numero de horas de trabalho extra |
| **Custo do dia** | Numerico | Custo total da jornada (em euros) |
| **Notas** | Texto | Observacoes adicionais |

### Tipos de jornada

| Tipo | Descricao |
|------|-----------|
| **Trabalho** (`lavorativa`) | Dia de trabalho normal no estaleiro |
| **Ferias** (`ferie`) | Dia de ferias |
| **Baixa** (`malattia`) | Dia de baixa medica |
| **Licenca** (`permesso`) | Dia de licenca/ausencia justificada |

<!-- IMAGE: Exemplo de registo de presenca preenchido -->
> **Fig. 11**: Exemplo de registo de presenca com 8 horas ordinarias e 2 extraordinarias

---

## Ficha de Equipamentos

A **Ficha de Equipamentos** permite inventariar todas as maquinas, ferramentas e equipamentos utilizados no estaleiro arqueologico.

<!-- IMAGE: Interface completa da Ficha de Equipamentos -->
> **Fig. 12**: Interface da Ficha de Equipamentos

### Campos do formulario

| Campo | Tipo | Descricao |
|-------|------|-----------|
| **Sitio** | ComboBox | Sitio arqueologico |
| **Nome** | Texto | Designacao do equipamento |
| **Tipo** | Texto | Categoria do equipamento (p.ex. maquinaria, ferramenta manual, topografia) |
| **Marca** | Texto | Fabricante/marca |
| **Modelo** | Texto | Modelo especifico |
| **Estado** | ComboBox | `em_uso`, `manutencao` ou `fora_servico` |
| **Data de compra** | Data | Data de aquisicao |
| **Custo** | Numerico | Valor de aquisicao (em euros) |
| **Data ultima manutencao** | Data | Data da ultima manutencao realizada |
| **Data proxima manutencao** | Data | Data prevista para a proxima manutencao |
| **Notas** | Texto | Observacoes adicionais |

### Estados do equipamento

| Estado | Descricao | Cor no Painel |
|--------|-----------|---------------|
| **em_uso** | Operacional e em utilizacao no estaleiro | Verde |
| **manutencao** | Em manutencao ou reparacao | Amarelo |
| **fora_servico** | Inoperacional ou abatido | Vermelho |

Quando a **data de proxima manutencao** de um equipamento e anterior a data atual e o estado nao e `fora_servico`, o Painel de Obra apresenta um alerta de manutencao atrasada.

<!-- IMAGE: Exemplo de registo de equipamento com datas de manutencao -->
> **Fig. 13**: Registo de equipamento com proxima manutencao prevista para 2026-03-15

---

## Ficha de Orcamento

A **Ficha de Orcamento** permite definir e acompanhar as rubricas orcamentais do estaleiro, comparando montantes previstos com montantes efetivamente gastos.

<!-- IMAGE: Interface completa da Ficha de Orcamento -->
> **Fig. 14**: Interface da Ficha de Orcamento

### Campos do formulario

| Campo | Tipo | Descricao |
|-------|------|-----------|
| **Sitio** | ComboBox | Sitio arqueologico |
| **Ano** | Numerico | Ano de referencia da rubrica |
| **Categoria** | Texto | Categoria orcamental (p.ex. pessoal, equipamento, logistica, laboratorio) |
| **Rubrica** | Texto | Descricao especifica da despesa |
| **Montante previsto** | Numerico | Valor orcamentado (em euros) |
| **Montante efetivo** | Numerico | Valor efetivamente gasto (em euros) |
| **Notas** | Texto | Observacoes e justificacoes |

### Categorias orcamentais sugeridas

| Categoria | Exemplos de rubricas |
|-----------|---------------------|
| **Pessoal** | Salarios, seguros, formacao |
| **Equipamento** | Aquisicao, aluguer, manutencao |
| **Logistica** | Transporte, alojamento, alimentacao |
| **Laboratorio** | Analises, conservacao, restauro |
| **Documentacao** | Fotografia, topografia, desenho |
| **Diversos** | Consumiveis, comunicacoes, licencas |

<!-- IMAGE: Exemplo de rubrica orcamental com montante previsto e efetivo -->
> **Fig. 15**: Rubrica orcamental de pessoal com 85% do montante previsto consumido

---

## Fluxo de trabalho operacional

### Configuracao inicial de um estaleiro

```
1. Abrir a Ficha de Orcamento
2. Criar as rubricas orcamentais para o ano corrente:
   - Pessoal, Equipamento, Logistica, etc.
   - Preencher os montantes previstos
3. Abrir a Ficha de Pessoal
4. Registar todos os colaboradores do estaleiro
5. Abrir a Ficha de Equipamentos
6. Inventariar todos os equipamentos disponiveis
7. Abrir o Painel de Obra para verificar os resumos
```

### Rotina diaria

```
1. Abrir a Ficha de Presencas
2. Para cada colaborador, registar:
   - Tipo de jornada (trabalho/ferias/baixa/licenca)
   - Horas ordinarias e extraordinarias
   - Custo do dia
3. Abrir o Painel de Obra
4. Verificar os indicadores:
   - Presentes vs ausentes
   - Alertas de manutencao de equipamentos
   - Estado do orcamento
```

### Atualizacao de orcamento

```
1. Abrir a Ficha de Orcamento
2. Pesquisar pela rubrica a atualizar
3. Atualizar o campo "Montante efetivo"
4. Guardar o registo
5. Verificar no Painel de Obra que a barra de
   progresso e o grafico circular refletem a alteracao
```

### Computo de volumes apos intervencao

```
1. Carregar os DEM (pre e pos-escavacao) no projeto QGIS
2. Abrir o Painel de Obra
3. Selecionar o tipo de calculo (Diferenca DEM ou DEM+Poligono)
4. Selecionar as camadas de entrada
5. Clicar em Calcular
6. Analisar o resultado
7. Clicar em Guardar computo para registar no historico
```

<!-- IMAGE: Diagrama do fluxo de trabalho completo -->
> **Fig. 16**: Fluxo de trabalho operacional do modulo Gestao de Obra

---

## Perguntas frequentes

### O Painel de Obra nao apresenta dados

**Causa**: O sitio nao esta selecionado ou nao existem dados registados.

**Solucoes**:
1. Verificar que o seletor de sitio tem um sitio valido selecionado
2. Verificar que o ano selecionado corresponde ao periodo com dados
3. Clicar no botao **Atualizar** para forcar o recarregamento
4. Verificar a ligacao a base de dados

### A barra de progresso do orcamento ultrapassa 100%

Isto indica que o montante efetivo total excede o montante previsto. A barra de progresso e limitada visualmente a 100%, mas os valores numericos exatos sao sempre apresentados nos campos de montante.

### Os alertas de manutencao aparecem para equipamentos fora de servico

Os alertas de manutencao sao calculados apenas para equipamentos cujo estado **nao** e `fora_servico`. Se um equipamento esta fora de servico, os alertas nao sao apresentados independentemente da data de proxima manutencao.

### Como associar uma presenca a um colaborador

O campo **ID Pessoal** na Ficha de Presencas deve corresponder ao identificador de um colaborador registado na Ficha de Pessoal. Recomenda-se primeiro registar todos os colaboradores na Ficha de Pessoal antes de iniciar o registo de presencas.

### Os DEM nao aparecem nos seletores do computo metrico

As caixas de selecao de DEM apresentam apenas as **camadas raster** carregadas no projeto QGIS. Para que um DEM apareca:
1. Carregar o ficheiro raster no projeto QGIS (arrastar e largar ou usar o menu Camada)
2. Verificar que a camada aparece no painel de Camadas
3. Reabrir o Painel de Obra (os seletores sao preenchidos na abertura do dialogo)

### Posso utilizar o modulo com SQLite e PostgreSQL

Sim. O modulo Gestao de Obra suporta ambos os sistemas de base de dados. A ligacao e determinada automaticamente pelas definicoes de configuracao do PyArchInit. Nao e necessaria qualquer configuracao adicional.

### Como exportar os dados de presencas para um relatorio

Atualmente, os dados de presencas podem ser consultados e navegados diretamente na Ficha de Presencas. A funcionalidade de exportacao para PDF/CSV esta prevista para uma versao futura. Entretanto, pode utilizar as funcionalidades nativas de exportacao do QGIS ou consultar diretamente a base de dados.

---

## Notas tecnicas

### Tabelas da base de dados

| Tabela | Formulario | Descricao |
|--------|-----------|-----------|
| `personale_table` | Pessoal | Registo de colaboradores |
| `presenze_table` | Presencas | Registo de presencas diarias |
| `attrezzature_table` | Equipamentos | Inventario de equipamentos |
| `budget_table` | Orcamento | Rubricas orcamentais |
| `computo_metrico_table` | Painel de Obra | Historico de calculos volumetricos |

### Ficheiros fonte

| Ficheiro | Descricao |
|----------|-----------|
| `tabs/Cantiere.py` | Controlador do Painel de Obra (Dashboard) |
| `tabs/Personale.py` | Controlador da Ficha de Pessoal |
| `tabs/Presenze.py` | Controlador da Ficha de Presencas |
| `tabs/Attrezzature.py` | Controlador da Ficha de Equipamentos |
| `tabs/Budget.py` | Controlador da Ficha de Orcamento |
| `gui/ui/Cantiere.ui` | Layout Qt do Painel de Obra |
| `gui/ui/Personale.ui` | Layout Qt da Ficha de Pessoal |
| `gui/ui/Presenze.ui` | Layout Qt da Ficha de Presencas |
| `gui/ui/Attrezzature.ui` | Layout Qt da Ficha de Equipamentos |
| `gui/ui/Budget.ui` | Layout Qt da Ficha de Orcamento |

### Compatibilidade

| Componente | Versao minima |
|------------|--------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| PostgreSQL | 12+ (com PostGIS) |
| SQLite | 3.x (com Spatialite) |

---

*Documentacao PyArchInit - Gestao de Obra*
*Versao: 5.0.x*
*Ultima atualizacao: Fevereiro 2026*
