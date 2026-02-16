# PyArchInit - Ficha de Sitio

## Indice
1. [Introducao](#introducao)
2. [Aceder a Ficha](#aceder-a-ficha)
3. [Interface do Utilizador](#interface-do-utilizador)
4. [Dados Descritivos do Sitio](#dados-descritivos-do-sitio)
5. [Barra de Ferramentas DBMS](#barra-de-ferramentas-dbms)
6. [Funcionalidades GIS](#funcionalidades-gis)
7. [Geracao de Fichas de UE](#geracao-de-fichas-de-ue)
8. [Ferramentas de Análise](#ferramentas-de-análise)
9. [Exportacao de Relatorios](#exportacao-de-relatorios)
10. [Fluxo de Trabalho Operacional](#fluxo-de-trabalho-operacional)

---

## Introducao

A **Ficha de Sitio** e o ponto de partida para documentar uma escavacao arqueologica no PyArchInit. Todo o projeto arqueologico comeca com a criacao de um sitio, que serve como contentor principal para todas as outras informacoes (Unidades Estratigraficas, Estruturas, Achados, etc.).

Um **sitio arqueologico** no PyArchInit representa uma area geografica definida onde decorrem atividades de investigacao arqueologica. Pode ser uma escavacao, uma area de prospeccao, um monumento, etc.

<!-- VIDEO: Introducao a Ficha de Sitio -->
> **Video Tutorial**: [Inserir ligacao de video para introducao a ficha de sitio]

---

## Aceder a Ficha

Para aceder a Ficha de Sitio:

1. Menu **PyArchInit** -> **Archaeological record management** -> **Site**
2. Ou, na barra de ferramentas do PyArchInit, clicar no icone **Site**

<!-- IMAGE: Captura de ecra do menu de acesso a ficha de sitio -->
![Acesso a Ficha de Sitio](images/02_scheda_sito/01_menu_scheda_sito.png)
*Figura 1: Aceder a Ficha de Sitio a partir do menu PyArchInit*

<!-- IMAGE: Captura de ecra da barra de ferramentas com icone de sitio -->
![Barra de Ferramentas do Sitio](images/02_scheda_sito/02_toolbar_sito.png)
*Figura 2: Icone da Ficha de Sitio na barra de ferramentas*

---

## Interface do Utilizador

A Ficha de Sitio esta dividida em varias areas funcionais:

<!-- IMAGE: Captura de ecra da ficha de sitio completa com areas numeradas -->
![Interface da Ficha de Sitio](images/02_scheda_sito/03_interfaccia_completa.png)
*Figura 3: Interface completa da Ficha de Sitio*

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | **Barra de Ferramentas DBMS** | Barra de ferramentas para navegacao e gestao de registos |
| 2 | **Dados Descritivos** | Campos para introducao de informacoes do sitio |
| 3 | **Gerador de UE** | Ferramenta para criacao em lote de fichas de UE |
| 4 | **Visualizador GIS** | Controlos para a visualizacao cartografica |
| 5 | **Ferramentas de Análise** | Acessíveis pela barra de ferramentas (MoveCost, GeoArchaeo, SAM, etc.) |
| 6 | **Ajuda** | Documentacao e video tutoriais |

---

## Dados Descritivos do Sitio

### Separador Dados Descritivos

<!-- IMAGE: Captura de ecra do separador de dados descritivos -->
![Separador Dados Descritivos](images/02_scheda_sito/04_tab_dati_descrittivi.png)
*Figura 4: Separador Dados Descritivos*

#### Campos Obrigatorios

| Campo | Descricao | Notas |
|-------|-----------|-------|
| **Site** | Nome de identificacao do sitio | Campo obrigatorio, deve ser unico |

#### Campos Geograficos

| Campo | Descricao | Exemplo |
|-------|-----------|---------|
| **Nation** | Pais onde se localiza o sitio | Portugal |
| **Region** | Regiao administrativa | Alentejo |
| **Province** | Distrito | Evora |
| **Municipality** | Municipio | Evora |

<!-- IMAGE: Captura de ecra dos campos geograficos preenchidos -->
![Campos Geograficos](images/02_scheda_sito/05_campi_geografici.png)
*Figura 5: Exemplo de preenchimento dos campos geograficos*

#### Campos Descritivos

| Campo | Descricao |
|-------|-----------|
| **Name** | Nome extenso/descritivo do sitio |
| **Definition** | Tipo de sitio (a partir do thesaurus) |
| **Description** | Campo de texto livre para descricao detalhada |
| **Folder** | Caminho para a pasta local do projeto |

<!-- IMAGE: Captura de ecra do campo de descricao -->
![Campo de Descricao](images/02_scheda_sito/06_campo_descrizione.png)
*Figura 6: Campo de descricao textual*

### Definicao do Sitio (Thesaurus)

O campo **Definition** utiliza um vocabulario controlado (thesaurus). As opcoes disponiveis incluem:

| Definicao | Descricao |
|-----------|-----------|
| Excavation area | Zona sujeita a investigacao estratigrafica |
| Survey area | Area de prospeccao de superficie |
| Archaeological site | Local com vestigios arqueologicos |
| Monument | Estrutura monumental individual |
| Necropolis | Area funeraria |
| Settlement | Area residencial |
| Sanctuary | Area sagrada/de culto |
| ... | Outras definicoes do thesaurus |

<!-- IMAGE: Captura de ecra do menu pendente de definicao do sitio -->
![Definicao do Sitio](images/02_scheda_sito/07_definizione_sito.png)
*Figura 7: Selecao da definicao do sitio a partir do thesaurus*

### Pasta do Projeto

O campo **Folder** permite associar um diretorio local ao sitio para organizar os ficheiros do projeto.

<!-- IMAGE: Captura de ecra da selecao de pasta -->
![Selecao de Pasta](images/02_scheda_sito/08_selezione_cartella.png)
*Figura 8: Selecao da pasta do projeto*

| Botao | Funcao |
|-------|--------|
| **...** | Navegar para selecionar a pasta |
| **Open** | Abre a pasta no gestor de ficheiros |

---

## Barra de Ferramentas DBMS

A barra de ferramentas DBMS fornece todos os controlos para a gestao de registos.

<!-- IMAGE: Captura de ecra da barra de ferramentas DBMS -->
![Barra de Ferramentas DBMS](images/02_scheda_sito/09_toolbar_dbms.png)
*Figura 9: Barra de Ferramentas DBMS*

### Indicadores de Estado

| Indicador | Descricao |
|-----------|-----------|
| **DB Info** | Mostra o tipo de base de dados ligada (SQLite/PostgreSQL) |
| **Status** | Estado atual: `Use` (navegacao), `Find` (pesquisa), `New Record` |
| **Sorting** | Indica se os registos estao ordenados |
| **record n.** | Numero do registo atual |
| **record tot.** | Total de registos |

<!-- IMAGE: Captura de ecra dos indicadores de estado -->
![Indicadores de Estado](images/02_scheda_sito/10_indicatori_stato.png)
*Figura 10: Indicadores de estado*

### Navegacao de Registos

| Botao | Icone | Funcao | Atalho |
|-------|-------|--------|--------|
| **First rec** | |< | Ir para o primeiro registo | - |
| **Prev rec** | < | Ir para o registo anterior | - |
| **Next rec** | > | Ir para o registo seguinte | - |
| **Last rec** | >| | Ir para o ultimo registo | - |

<!-- IMAGE: Captura de ecra dos botoes de navegacao -->
![Navegacao](images/02_scheda_sito/11_navigazione_record.png)
*Figura 11: Botoes de navegacao*

### Gestao de Registos

| Botao | Funcao | Descricao |
|-------|--------|-----------|
| **New record** | Criar novo | Prepara a ficha para introduzir um novo sitio |
| **Save** | Guardar | Guarda as alteracoes ou o novo registo |
| **Delete record** | Eliminar | Elimina o registo atual (com confirmacao) |
| **View all records** | Ver todos | Mostra todos os registos na base de dados |

<!-- IMAGE: Captura de ecra dos botoes de gestao -->
![Gestao de Registos](images/02_scheda_sito/12_gestione_record.png)
*Figura 12: Botoes de gestao de registos*

### Pesquisa e Ordenacao

| Botao | Funcao | Descricao |
|-------|--------|-----------|
| **new search** | Nova pesquisa | Inicia o modo de pesquisa |
| **search !!!** | Executar pesquisa | Executa a pesquisa com os criterios introduzidos |
| **Order by** | Ordenar | Abre o painel de ordenacao |

<!-- IMAGE: Captura de ecra da pesquisa -->
![Pesquisa](images/02_scheda_sito/13_ricerca.png)
*Figura 13: Funcoes de pesquisa*

#### Como Efetuar uma Pesquisa

1. Clicar em **new search** - o estado muda para "Find"
2. Preencher os campos com os criterios de pesquisa
3. Clicar em **search !!!** para executar
4. Os resultados sao apresentados e pode navegar entre eles

<!-- IMAGE: Captura de ecra de exemplo de pesquisa -->
![Exemplo de Pesquisa](images/02_scheda_sito/14_esempio_ricerca.png)
*Figura 14: Exemplo de pesquisa por regiao*

<!-- VIDEO: Como efetuar pesquisas -->
> **Video Tutorial**: [Inserir ligacao de video de pesquisa]

#### Painel de Ordenacao

Ao clicar em **Order by** abre-se um painel para ordenar os registos:

<!-- IMAGE: Captura de ecra do painel de ordenacao -->
![Painel de Ordenacao](images/02_scheda_sito/15_pannello_ordinamento.png)
*Figura 15: Painel de ordenacao*

| Opcao | Descricao |
|-------|-----------|
| **Field** | Selecionar o campo para ordenacao |
| **Ascending** | Ordem A-Z, 0-9 |
| **Descending** | Ordem Z-A, 9-0 |

---

## Funcionalidades GIS

A Ficha de Sitio oferece varias funcionalidades de integracao GIS.

<!-- IMAGE: Captura de ecra da seccao GIS -->
![Seccao GIS](images/02_scheda_sito/16_sezione_gis.png)
*Figura 16: Seccao de funcionalidades GIS*

### Carregamento de Camadas

| Botao | Funcao |
|-------|--------|
| **GIS viewer** | Carregar todas as camadas para introducao de geometrias |
| **Load site layer** (icone globo) | Carregar apenas as camadas do sitio atual |
| **Load all sites** (icone multiplos globos) | Carregar camadas de todos os sitios |

<!-- IMAGE: Captura de ecra dos botoes GIS -->
![Botoes GIS](images/02_scheda_sito/17_bottoni_gis.png)
*Figura 17: Botoes de carregamento de camadas GIS*

### Geocodificacao - Pesquisa de Morada

A funcao de geocodificacao permite localizar uma morada no mapa.

<!-- IMAGE: Captura de ecra da geocodificacao -->
![Geocodificacao](images/02_scheda_sito/18_geocoding.png)
*Figura 18: Campo de pesquisa de morada*

1. Introduzir a morada no campo de texto
2. Clicar em **Zoom on**
3. O mapa centra-se na localizacao encontrada

| Campo | Descricao |
|-------|-----------|
| **Address** | Introduzir rua, cidade, pais |
| **Zoom on** | Centra o mapa na morada |

### Modo GIS Ativo

O comutador **Enable search loading** ativa/desativa a visualizacao automatica dos resultados de pesquisa no mapa.

<!-- IMAGE: Captura de ecra do comutador GIS -->
![Comutador GIS](images/02_scheda_sito/19_toggle_gis.png)
*Figura 19: Comutador do modo GIS*

- **Ativo**: As pesquisas sao automaticamente apresentadas no mapa
- **Inativo**: As pesquisas nao alteram a visualizacao do mapa

### WMS Servidoes Arqueologicas

O botao WMS carrega a camada de servidoes arqueologicas do Ministerio da Cultura italiano.

<!-- IMAGE: Captura de ecra das servidoes WMS -->
![Servidoes WMS](images/02_scheda_sito/20_wms_vincoli.png)
*Figura 20: Camada WMS de servidoes arqueologicas*

### Mapas Base

O botao Mapas Base permite carregar mapas base (Google Maps, OpenStreetMap, etc.).

<!-- IMAGE: Captura de ecra dos mapas base -->
![Mapas Base](images/02_scheda_sito/21_base_maps.png)
*Figura 21: Selecao de mapas base*

---

## Geracao de Fichas de UE

Esta funcionalidade permite criar automaticamente um numero arbitrario de fichas de UE para o sitio atual.

<!-- IMAGE: Captura de ecra do gerador de UE -->
![Gerador de UE](images/02_scheda_sito/22_generatore_us.png)
*Figura 22: Seccao de geracao de fichas de UE*

### Parametros

| Campo | Descricao | Exemplo |
|-------|-----------|---------|
| **Area Number** | Numero da area de escavacao | 1 |
| **Starting SU form number** | Numero inicial da UE | 1 |
| **Number of forms to create** | Quantas fichas de UE gerar | 100 |
| **Type** | UE ou UEM | UE |

### Procedimento

1. Certificar-se de que esta no sitio correto
2. Introduzir o numero da area
3. Introduzir o numero inicial da UE
4. Introduzir quantas fichas criar
5. Selecionar o tipo (UE ou UEM)
6. Clicar em **Generate SU**

<!-- IMAGE: Captura de ecra de exemplo de geracao -->
![Exemplo de Geracao](images/02_scheda_sito/23_esempio_generazione.png)
*Figura 23: Exemplo de geracao de 50 UE a partir da UE 101*

<!-- VIDEO: Como gerar fichas de UE em lote -->
> **Video Tutorial**: [Inserir ligacao de video de geracao de UE]

---

## Ferramentas de Análise

As ferramentas de análise avançada estão agora disponíveis como diálogos independentes, acessíveis pelo botão **Ferramentas de Análise** na barra de ferramentas do PyArchInit:

- **MoveCost** - Análise de caminhos de menor custo (ver [Tutorial MoveCost](34_movecost.md))
- **GeoArchaeo** - Análise geoestatística para pesquisa arqueológica (ver [Tutorial GeoArchaeo](33_geoarchaeo.md))
- **SAM Segmentation** - Segmentação de imagens com IA
- **Pottery Tools** - Ferramentas de análise cerâmica
- **TOPS** - Importação de dados de estação total
- **Image Search** - Pesquisa de imagens

---

## Exportacao de Relatorios

### Exportar Relatorio de Escavacao

O botao **Export** gera um PDF com o relatorio de escavacao do sitio atual.

<!-- IMAGE: Captura de ecra da exportacao -->
![Exportacao](images/02_scheda_sito/26_esportazione.png)
*Figura 26: Botao de exportacao de relatorio*

**Nota**: Esta funcionalidade esta em versao de desenvolvimento e pode conter erros.

O relatorio inclui:
- Dados de identificacao do sitio
- Lista de UE
- Sequencia estratigrafica
- Harris Matrix (se disponivel)

<!-- IMAGE: Captura de ecra de exemplo de PDF -->
![Exemplo de PDF](images/02_scheda_sito/27_esempio_pdf.png)
*Figura 27: Exemplo de relatorio PDF gerado*

---

## Fluxo de Trabalho Operacional

### Criar um Novo Sitio

<!-- VIDEO: Fluxo de trabalho de criacao de novo sitio -->
> **Video Tutorial**: [Inserir ligacao de video do fluxo de trabalho de novo sitio]

#### Passo 1: Abrir a Ficha de Sitio
<!-- IMAGE: Passo 1 -->
![Passo 1 do Fluxo](images/02_scheda_sito/28_workflow_step1.png)
*Figura 28: Passo 1 - Abrir a ficha*

#### Passo 2: Clicar em "New record"
O estado muda para "New Record" e os campos sao limpos.

<!-- IMAGE: Passo 2 -->
![Passo 2 do Fluxo](images/02_scheda_sito/29_workflow_step2.png)
*Figura 29: Passo 2 - Novo registo*

#### Passo 3: Preencher os Dados Obrigatorios
Introduzir pelo menos o nome do sitio (campo obrigatorio).

<!-- IMAGE: Passo 3 -->
![Passo 3 do Fluxo](images/02_scheda_sito/30_workflow_step3.png)
*Figura 30: Passo 3 - Introducao de dados*

#### Passo 4: Preencher os Dados Geograficos
Introduzir pais, regiao, distrito, municipio.

<!-- IMAGE: Passo 4 -->
![Passo 4 do Fluxo](images/02_scheda_sito/31_workflow_step4.png)
*Figura 31: Passo 4 - Dados geograficos*

#### Passo 5: Selecionar a Definicao
Escolher o tipo de sitio a partir do thesaurus.

<!-- IMAGE: Passo 5 -->
![Passo 5 do Fluxo](images/02_scheda_sito/32_workflow_step5.png)
*Figura 32: Passo 5 - Definicao do sitio*

#### Passo 6: Adicionar Descricao
Preencher o campo de descricao com informacao detalhada.

<!-- IMAGE: Passo 6 -->
![Passo 6 do Fluxo](images/02_scheda_sito/33_workflow_step6.png)
*Figura 33: Passo 6 - Descricao*

#### Passo 7: Guardar
Clicar em **Save** para guardar o novo sitio.

<!-- IMAGE: Passo 7 -->
![Passo 7 do Fluxo](images/02_scheda_sito/34_workflow_step7.png)
*Figura 34: Passo 7 - Guardar*

#### Passo 8: Verificar
O sitio foi criado, o estado regressa a "Use".

<!-- IMAGE: Passo 8 -->
![Passo 8 do Fluxo](images/02_scheda_sito/35_workflow_step8.png)
*Figura 35: Passo 8 - Verificacao da criacao*

### Modificar um Sitio Existente

1. Navegar ate ao sitio a modificar
2. Modificar os campos desejados
3. Clicar em **Save**
4. Confirmar a gravacao das alteracoes

### Eliminar um Sitio

**Aviso**: Eliminar um sitio NAO elimina automaticamente as UE, estruturas e achados associados.

1. Navegar ate ao sitio a eliminar
2. Clicar em **Delete record**
3. Confirmar a eliminacao

<!-- IMAGE: Captura de ecra de confirmacao de eliminacao -->
![Confirmacao de Eliminacao](images/02_scheda_sito/36_conferma_eliminazione.png)
*Figura 36: Dialogo de confirmacao de eliminacao*

---

## Separador Ajuda

O separador Ajuda proporciona acesso rapido a documentacao.

<!-- IMAGE: Captura de ecra do separador de ajuda -->
![Separador Ajuda](images/02_scheda_sito/37_tab_help.png)
*Figura 37: Separador Ajuda*

| Recurso | Ligacao |
|---------|--------|
| Video Tutorial | YouTube |
| Documentacao | pyarchinit.github.io |
| Comunidade | Facebook UnaQuantum |

---

## Gestao de Concorrencia (PostgreSQL)

Quando se utiliza PostgreSQL num ambiente multiutilizador, o sistema gere automaticamente conflitos de modificacao:

- **Indicador de bloqueio**: Mostra se o registo esta a ser editado por outro utilizador
- **Controlo de versao**: Deteta modificacoes concorrentes
- **Resolucao de conflitos**: Permite escolher qual versao manter

<!-- IMAGE: Captura de ecra do indicador de concorrencia -->
![Concorrencia](images/02_scheda_sito/38_concorrenza.png)
*Figura 38: Indicador de registo bloqueado*

---

## Resolucao de Problemas

### Sitio nao guardado
- Verificar se o campo "Site" esta preenchido
- Verificar se o nome ja nao existe na base de dados

### Camadas GIS nao carregam
- Verificar a ligacao a base de dados
- Verificar se existem geometrias associadas ao sitio

### Erro de geocodificacao
- Verificar a ligacao a Internet
- Verificar se a morada esta escrita corretamente

### Ferramentas de análise
- Para problemas com MoveCost, GeoArchaeo e outras ferramentas de análise, consulte os tutoriais dedicados respetivos.

---

## Notas Tecnicas

- **Tabela da base de dados**: `site_table`
- **Campos da base de dados**: sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Camadas GIS associadas**: PYSITO_POLYGON, PYSITO_POINT
- **Thesaurus**: tipologia_sigla = '1.1'

---

*Documentacao PyArchInit - Ficha de Sitio*
*Versao: 4.9.x*
*Ultima atualizacao: janeiro de 2026*
