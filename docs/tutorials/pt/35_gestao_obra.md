# PyArchInit - Gestao de Obra

## Indice

1. [Introducao](#introducao)
2. [Acesso ao modulo](#acesso-ao-modulo)
3. [Painel de Obra (Dashboard)](#painel-de-obra-dashboard)
4. [Ficha de Pessoal](#ficha-de-pessoal)
5. [Ficha de Presencas](#ficha-de-presencas)
6. [Ficha de Equipamentos](#ficha-de-equipamentos)
7. [Ficha de Orcamento](#ficha-de-orcamento)
8. [Fluxo de trabalho operacional](#fluxo-de-trabalho-operacional)
9. [Perguntas frequentes](#perguntas-frequentes)

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
