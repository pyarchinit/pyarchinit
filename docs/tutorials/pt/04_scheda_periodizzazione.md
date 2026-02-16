# Tutorial 04: Ficha de Periodizacao

## Indice
1. [Introducao](#introducao)
2. [Aceder a Ficha](#aceder-a-ficha)
3. [Interface do Utilizador](#interface-do-utilizador)
4. [Conceitos Fundamentais](#conceitos-fundamentais)
5. [Campos da Ficha](#campos-da-ficha)
6. [Barra de Ferramentas DBMS](#barra-de-ferramentas-dbms)
7. [Funcionalidades GIS](#funcionalidades-gis)
8. [Exportacao PDF](#exportacao-pdf)
9. [Integracao AI](#integracao-ai)
10. [Fluxo de Trabalho Operacional](#fluxo-de-trabalho-operacional)
11. [Boas Praticas](#boas-praticas)
12. [Resolucao de Problemas](#resolucao-de-problemas)

---

## Introducao

A **Ficha de Periodizacao** e uma ferramenta fundamental para gerir as fases cronologicas de uma escavacao arqueologica. Permite definir os periodos e fases que caracterizam a sequencia estratigrafica do sitio, associando uma datacao cronologica e descricao a cada par periodo/fase.

### Finalidade da Ficha

- Definir a sequencia cronologica da escavacao
- Associar periodos e fases a unidades estratigraficas
- Gerir cronologia absoluta (anos) e relativa (periodos historicos)
- Visualizar UEs por periodo/fase no mapa GIS
- Gerar relatorios PDF de periodizacao

### Relacao com Outras Fichas

A Ficha de Periodizacao esta intimamente ligada a:
- **Ficha de UE/UEM**: Cada UE e atribuida a um periodo e fase
- **Ficha de Sitio**: Os periodos sao especificos de cada sitio
- **Harris Matrix**: Os periodos colorem a Matrix por fase cronologica

![Panoramica da Ficha de Periodizacao](images/04_scheda_periodizzazione/01_panoramica.png)
*Figura 1: Vista geral da Ficha de Periodizacao*

---

## Aceder a Ficha

### A Partir do Menu

1. Abrir o QGIS com o plugin PyArchInit ativo
2. Menu **PyArchInit** -> **Archaeological record management** -> **Excavation - Loss of use calculation** -> **Period and Phase**

![Menu Periodizacao](images/04_scheda_periodizzazione/02_menu_accesso.png)
*Figura 2: Aceder a ficha a partir do menu*

### A Partir da Barra de Ferramentas

1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone de **Periodizacao** (icone de sitio com relogio)

![Barra de Ferramentas Periodizacao](images/04_scheda_periodizzazione/03_toolbar_accesso.png)
*Figura 3: Icone na barra de ferramentas*

---

## Interface do Utilizador

A interface da Ficha de Periodizacao esta organizada de forma simples e linear:

![Interface Completa](images/04_scheda_periodizzazione/04_interfaccia_completa.png)
*Figura 4: Disposicao completa da interface*

### Areas Principais

| Area | Descricao |
|------|-----------|
| **1. Barra de Ferramentas DBMS** | Barra de ferramentas para navegacao e gestao de registos |
| **2. Indicadores de Estado** | DB Info, Estado, Ordenacao |
| **3. Dados de Identificacao** | Sitio, Periodo, Fase, Codigo de periodo |
| **4. Dados Descritivos** | Descricao textual do periodo |
| **5. Cronologia** | Anos inicial e final |
| **6. Datacao Alargada** | Selecao a partir do vocabulario de epocas historicas |

---

## Conceitos Fundamentais

### Periodo e Fase

O sistema de periodizacao no PyArchInit baseia-se numa estrutura hierarquica de dois niveis:

#### Periodo
O **Periodo** representa uma macrofase cronologica da escavacao. E identificado por um numero inteiro (1, 2, 3, ...) e representa as grandes subdivisoes da sequencia estratigrafica.

Exemplos de periodos:
- Periodo 1: Epoca contemporanea
- Periodo 2: Epoca medieval
- Periodo 3: Epoca romana imperial
- Periodo 4: Epoca romana republicana

#### Fase
A **Fase** representa uma subdivisao interna do periodo. E tambem identificada por um numero inteiro e permite detalhar ainda mais a sequencia.

Exemplos de fases no Periodo 3 (Epoca romana imperial):
- Fase 1: Seculos III-IV d.C.
- Fase 2: Seculo II d.C.
- Fase 3: Seculo I d.C.

### Codigo de Periodo

O **Codigo de Periodo** e um identificador numerico unico que liga o par periodo/fase as UEs. Quando se atribui um periodo/fase a uma UE na Ficha de UE, e utilizado este codigo.

> **Importante**: O codigo de periodo deve ser unico para cada combinacao sitio/periodo/fase.

### Esquema Conceptual

```
Sitio
|-- Periodo 1 (Epoca contemporanea)
|   |-- Fase 1 -> Codigo 101
|   +-- Fase 2 -> Codigo 102
|-- Periodo 2 (Epoca medieval)
|   |-- Fase 1 -> Codigo 201
|   |-- Fase 2 -> Codigo 202
|   +-- Fase 3 -> Codigo 203
+-- Periodo 3 (Epoca romana)
    |-- Fase 1 -> Codigo 301
    +-- Fase 2 -> Codigo 302
```

---

## Campos da Ficha

### Campos de Identificacao

#### Sitio
- **Tipo**: ComboBox (apenas leitura em modo de navegacao)
- **Obrigatorio**: Sim
- **Descricao**: Selecionar o sitio arqueologico a que pertence a periodizacao
- **Notas**: Se um sitio predefinido estiver configurado, este campo sera pre-preenchido e nao editavel

![Campo Sitio](images/04_scheda_periodizzazione/05_campo_sito.png)
*Figura 5: Campo de selecao de sitio*

#### Periodo
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Sim
- **Valores**: Inteiros de 1 a 15 (predefinidos) ou valores personalizados
- **Descricao**: Numero cronologico do periodo
- **Notas**: Numeros mais baixos indicam periodos mais recentes, numeros mais altos indicam periodos mais antigos

#### Fase
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Sim
- **Valores**: Inteiros de 1 a 15 (predefinidos) ou valores personalizados
- **Descricao**: Numero da fase dentro do periodo

![Campos Periodo e Fase](images/04_scheda_periodizzazione/06_campi_periodo_fase.png)
*Figura 6: Campos Periodo e Fase*

#### Codigo de Periodo
- **Tipo**: LineEdit (texto)
- **Obrigatorio**: Nao (mas fortemente recomendado)
- **Descricao**: Codigo numerico unico para identificar o par periodo/fase
- **Sugestao**: Utilizar uma convencao como `[periodo][fase]` (ex.: 101, 102, 201, 301)

![Campo Codigo de Periodo](images/04_scheda_periodizzazione/07_codice_periodo.png)
*Figura 7: Campo Codigo de Periodo*

### Campos Descritivos

#### Descricao
- **Tipo**: TextEdit (multilinhas)
- **Obrigatorio**: Nao
- **Descricao**: Descricao textual do periodo/fase
- **Conteudo sugerido**:
  - Caracteristicas gerais do periodo
  - Eventos historicos relacionados
  - Tipos de estrutura/material esperados
  - Referencias bibliograficas

![Campo Descricao](images/04_scheda_periodizzazione/08_campo_descrizione.png)
*Figura 8: Campo de descricao*

### Campos Cronologicos

#### Cronologia Inicial
- **Tipo**: LineEdit (numerico)
- **Obrigatorio**: Nao
- **Formato**: Ano numerico
- **Notas**:
  - Valores positivos = d.C.
  - Valores negativos = a.C.
  - Exemplo: `-100` para 100 a.C., `200` para 200 d.C.

#### Cronologia Final
- **Tipo**: LineEdit (numerico)
- **Obrigatorio**: Nao
- **Formato**: Ano numerico (mesmas convencoes da Cronologia Inicial)

![Campos de Cronologia](images/04_scheda_periodizzazione/09_campi_cronologia.png)
*Figura 9: Campos de Cronologia Inicial e Final*

#### Datacao Alargada (Epocas Historicas)
- **Tipo**: ComboBox editavel com vocabulario pre-carregado
- **Obrigatorio**: Nao
- **Descricao**: Selecao a partir de um vocabulario de epocas historicas predefinidas
- **Funcionalidade automatica**: Ao selecionar uma epoca, os campos de Cronologia Inicial e Final sao preenchidos automaticamente

![Datacao Alargada](images/04_scheda_periodizzazione/10_datazione_estesa.png)
*Figura 10: ComboBox de Datacao Alargada com epocas pre-carregadas*

### Vocabulario de Epocas Historicas

O vocabulario inclui uma vasta gama de periodos historicos:

| Categoria | Exemplos |
|-----------|----------|
| **Epoca Contemporanea** | Seculo XXI, Seculo XX |
| **Epoca Moderna** | Seculos XIX-XVI |
| **Epoca Medieval** | Seculos XV-VIII |
| **Epoca Antiga** | Seculos VII-I |
| **Imperio Romano** | Periodos especificos (Julio-Claudiano, Flaviano, etc.) |
| **Imperio Bizantino** | Periodos especificos |
| **Pre-historia** | Paleolitico, Mesolitico, Neolitico, Idade do Bronze, Idade do Ferro |

---

## Barra de Ferramentas DBMS

A barra de ferramentas DBMS permite a gestao completa de registos:

![Barra de Ferramentas DBMS](images/04_scheda_periodizzazione/11_toolbar_dbms.png)
*Figura 11: Barra de ferramentas DBMS completa*

### Botoes de Navegacao

| Icone | Nome | Funcao | Atalho |
|-------|------|--------|--------|
| ![Primeiro](images/icons/first.png) | Primeiro | Ir para o primeiro registo | - |
| ![Anterior](images/icons/prev.png) | Anterior | Ir para o registo anterior | - |
| ![Seguinte](images/icons/next.png) | Seguinte | Ir para o registo seguinte | - |
| ![Ultimo](images/icons/last.png) | Ultimo | Ir para o ultimo registo | - |

### Botoes de Gestao de Registos

| Icone | Nome | Funcao |
|-------|------|--------|
| ![Novo](images/icons/new.png) | Novo registo | Criar um novo registo |
| ![Guardar](images/icons/save.png) | Guardar | Guardar alteracoes |
| ![Eliminar](images/icons/delete.png) | Eliminar | Eliminar o registo atual |
| ![Ver Todos](images/icons/view_all.png) | Ver todos | Ver todos os registos |

### Botoes de Pesquisa

| Icone | Nome | Funcao |
|-------|------|--------|
| ![Nova Pesquisa](images/icons/new_search.png) | Nova pesquisa | Ativar modo de pesquisa |
| ![Pesquisar](images/icons/search.png) | Pesquisar!!! | Executar pesquisa |
| ![Ordenar](images/icons/sort.png) | Ordenar por | Ordenar registos |

### Indicadores de Estado

![Indicadores de Estado](images/04_scheda_periodizzazione/12_indicatori_stato.png)
*Figura 12: Indicadores de estado*

| Indicador | Descricao |
|-----------|-----------|
| **Status** | Modo atual: "Use" (navegacao), "Find" (pesquisa), "New Record" |
| **Sorting** | "Unsorted" ou "Sorted" |
| **record n.** | Numero do registo atual |
| **record tot.** | Numero total de registos |

---

## Funcionalidades GIS

A Ficha de Periodizacao oferece funcionalidades poderosas de visualizacao GIS para ver as UEs associadas a cada periodo/fase.

### Botoes GIS

![Botoes GIS](images/04_scheda_periodizzazione/13_pulsanti_gis.png)
*Figura 13: Botoes para visualizacao GIS*

#### Ver Periodo Individual (Icone GIS)
- **Funcao**: Carrega todas as UEs associadas ao periodo/fase atual no mapa QGIS
- **Requisito**: O campo Codigo de Periodo deve estar preenchido
- **Camadas carregadas**: UE e UEM filtradas por codigo de periodo

#### Ver Todos os Periodos - UE (Icone Multiplas Camadas)
- **Funcao**: Carrega todos os periodos como camadas separadas no mapa (apenas UE)
- **Resultado**: Uma camada para cada combinacao periodo/fase

#### Ver Todos os Periodos - UEM (Icone GIS3)
- **Funcao**: Carrega todos os periodos como camadas separadas no mapa (apenas UEM)
- **Resultado**: Uma camada para cada combinacao periodo/fase para unidades murarias

### Visualizacao no Mapa

![Mapa com Periodos](images/04_scheda_periodizzazione/14_mappa_periodi.png)
*Figura 14: UEs apresentadas por periodo no mapa QGIS*

Ao carregar camadas por periodo:
- Cada periodo/fase tem uma cor distintiva
- As UEs sao filtradas com base no codigo de periodo atribuido
- As camadas individuais podem ser ativadas/desativadas

---

## Exportacao PDF

A ficha oferece dois modos de exportacao PDF:

### Exportacao de Ficha Individual

![Botao PDF Ficha](images/04_scheda_periodizzazione/15_pulsante_pdf_scheda.png)
*Figura 15: Botao de exportacao de ficha PDF*

- **Icone**: PDF
- **Funcao**: Gera um PDF com os dados do periodo/fase atual
- **Conteudo**:
  - Informacoes de identificacao (Sitio, Periodo, Fase)
  - Cronologia (inicial, final, datacao alargada)
  - Descricao completa

### Exportacao de Lista de Periodizacao

![Botao PDF Lista](images/04_scheda_periodizzazione/16_pulsante_pdf_lista.png)
*Figura 16: Botao de exportacao de lista PDF*

- **Icone**: Folha
- **Funcao**: Gera um PDF com a lista de todos os periodos/fases do sitio
- **Conteudo**: Tabela resumo com todos os periodos

### Exemplo de PDF Gerado

![Exemplo PDF](images/04_scheda_periodizzazione/17_esempio_pdf.png)
*Figura 17: Exemplo de PDF gerado*

---

## Integracao AI

A Ficha de Periodizacao inclui integracao GPT para obter sugestoes automaticas de descricoes de periodos historicos.

### Botao de Sugestoes

![Botao de Sugestoes](images/04_scheda_periodizzazione/18_pulsante_suggerimenti.png)
*Figura 18: Botao de Sugestoes AI*

### Como Funciona

1. Selecionar uma epoca historica no campo **Datacao Alargada**
2. Clicar no botao **Sugestoes**
3. Selecionar o modelo GPT a utilizar (gpt-4o ou gpt-4)
4. O sistema gera automaticamente:
   - Uma descricao do periodo historico
   - 3 ligacoes relevantes da Wikipedia
5. O texto gerado pode ser inserido no campo Descricao

### Configuracao da Chave API

Para utilizar esta funcionalidade:
1. Obter uma Chave API da OpenAI
2. Na primeira utilizacao, o sistema solicita a chave
3. A chave e guardada em `PYARCHINIT_HOME/bin/gpt_api_key.txt`

> **Nota**: Esta funcionalidade requer ligacao a Internet e uma conta OpenAI com creditos disponiveis.

---

## Fluxo de Trabalho Operacional

### Criar uma Nova Periodizacao

#### Passo 1: Aceder a Ficha
1. Abrir a Ficha de Periodizacao a partir do menu ou barra de ferramentas
2. Verificar a ligacao a base de dados (indicador de Estado)

![Passo 1 do Fluxo](images/04_scheda_periodizzazione/19_workflow_step1.png)
*Figura 19: Abrir a ficha*

#### Passo 2: Novo Registo
1. Clicar no botao **New record**
2. O estado muda para "New Record"
3. Os campos tornam-se editaveis

![Passo 2 do Fluxo](images/04_scheda_periodizzazione/20_workflow_step2.png)
*Figura 20: Clicar em New record*

#### Passo 3: Selecao do Sitio
1. Se nao estiver predefinido, selecionar o **Sitio** no menu pendente
2. O sitio deve ja existir na Ficha de Sitio

![Passo 3 do Fluxo](images/04_scheda_periodizzazione/21_workflow_step3.png)
*Figura 21: Selecao do sitio*

#### Passo 4: Definicao de Periodo e Fase
1. Selecionar ou digitar o numero do **Periodo**
2. Selecionar ou digitar o numero da **Fase**
3. Introduzir o **Codigo de Periodo** unico

![Passo 4 do Fluxo](images/04_scheda_periodizzazione/22_workflow_step4.png)
*Figura 22: Definicao de periodo e fase*

#### Passo 5: Cronologia
1. Selecionar a **Datacao Alargada** a partir do vocabulario de epocas
2. Os campos de Cronologia Inicial e Final sao preenchidos automaticamente
3. Ou introduzir os anos manualmente

![Passo 5 do Fluxo](images/04_scheda_periodizzazione/23_workflow_step5.png)
*Figura 23: Definir a cronologia*

#### Passo 6: Descricao
1. Preencher o campo **Descricao** com informacao sobre o periodo
2. Opcional: utilizar o botao **Sugestoes** para obter texto gerado por AI

![Passo 6 do Fluxo](images/04_scheda_periodizzazione/24_workflow_step6.png)
*Figura 24: Preencher a descricao*

#### Passo 7: Guardar
1. Clicar no botao **Save**
2. O registo e guardado na base de dados
3. O estado regressa a "Use"

![Passo 7 do Fluxo](images/04_scheda_periodizzazione/25_workflow_step7.png)
*Figura 25: Guardar*

### Esquema de Periodizacao Recomendado

Para uma escavacao tipica, recomenda-se criar a periodizacao seguindo este esquema:

| Periodo | Fase | Codigo | Descricao |
|---------|------|--------|-----------|
| 1 | 1 | 101 | Epoca contemporanea - Lavragem |
| 1 | 2 | 102 | Epoca contemporanea - Abandono |
| 2 | 1 | 201 | Epoca medieval - Fase tardia |
| 2 | 2 | 202 | Epoca medieval - Fase central |
| 2 | 3 | 203 | Epoca medieval - Fase inicial |
| 3 | 1 | 301 | Epoca romana - Fase imperial |
| 3 | 2 | 302 | Epoca romana - Fase republicana |
| 4 | 1 | 401 | Epoca pre-romana |

---

## Boas Praticas

### Convencoes de Numeracao

1. **Periodos**: Numerar do mais recente (1) ao mais antigo
2. **Fases**: Numerar da mais recente (1) a mais antiga dentro do periodo
3. **Codigos**: Utilizar a formula `[periodo * 100 + fase]` para codigos unicos

### Descricoes Eficazes

Uma boa descricao de periodo deve incluir:
- Enquadramento cronologico
- Principais caracteristicas do periodo
- Tipos de estrutura/material esperados
- Comparacoes com sitios contemporaneos
- Referencias bibliograficas

### Gestao da Cronologia

- Utilizar sempre anos numericos para as cronologias
- Para datas a.C., utilizar numeros negativos
- Verificar a consistencia: a cronologia final deve ser >= a inicial (em valor absoluto para a.C.)

### Ligacao com UEs

Apos criar a periodizacao:
1. Abrir a Ficha de UE
2. No separador **Periodizacao**, atribuir Periodo e Fase Inicial/Final
3. O sistema associara automaticamente a UE a periodizacao

---

## Resolucao de Problemas

### Problemas Comuns

#### "Period code not add"
- **Causa**: Campo Codigo de Periodo vazio
- **Solucao**: Preencher o campo Codigo de Periodo antes de utilizar funcoes GIS

#### Cronologia nao e preenchida automaticamente
- **Causa**: A epoca selecionada nao tem dados associados
- **Solucao**: Verificar se a epoca esta presente no ficheiro CSV de epocas historicas

#### Erro ao guardar: registo duplicado
- **Causa**: Ja existe um registo com a mesma combinacao Sitio/Periodo/Fase
- **Solucao**: Verificar os valores e utilizar uma combinacao unica

#### UEs nao aparecem na visualizacao GIS
- **Causa**: As UEs nao tem codigo de periodo atribuido
- **Solucao**:
  1. Verificar na Ficha de UE se os campos Periodo/Fase estao preenchidos
  2. Verificar se o Codigo de Periodo corresponde

#### Sugestoes AI nao funcionam
- **Causa**: Chave API em falta ou invalida
- **Solucao**:
  1. Verificar a ligacao a Internet
  2. Verificar a validade da Chave API
  3. Reinstalar bibliotecas: `pip install --upgrade openai pydantic`

---

## Video Tutorial

### Video 1: Panoramica da Ficha de Periodizacao
*Duracao: 3-4 minutos*

[Marcador de video tutorial]

**Conteudos:**
- Abrir a ficha
- Descricao da interface
- Navegar entre registos

### Video 2: Criar Periodizacao Completa
*Duracao: 5-6 minutos*

[Marcador de video tutorial]

**Conteudos:**
- Criar uma nova periodizacao
- Preencher todos os campos
- Utilizar o vocabulario de epocas
- Guardar

### Video 3: Visualizacao GIS por Periodo
*Duracao: 3-4 minutos*

[Marcador de video tutorial]

**Conteudos:**
- Utilizar os botoes GIS
- Ver UEs por periodo
- Gerir camadas carregadas

---

## Resumo dos Campos

| Campo | Tipo | Obrigatorio | Base de Dados |
|-------|------|-------------|---------------|
| Sitio | ComboBox | Sim | sito |
| Periodo | ComboBox | Sim | periodo |
| Fase | ComboBox | Sim | fase |
| Codigo de Periodo | LineEdit | Nao | cont_per |
| Descricao | TextEdit | Nao | descrizione |
| Cronologia Inicial | LineEdit | Nao | cron_iniziale |
| Cronologia Final | LineEdit | Nao | cron_finale |
| Datacao Alargada | ComboBox | Nao | datazione_estesa |

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sketches of Sketches*
