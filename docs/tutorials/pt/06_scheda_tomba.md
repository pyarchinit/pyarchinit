# Tutorial 06: Ficha de Sepultura

## Introducao

A **Ficha de Sepultura** e o modulo do PyArchInit dedicado a documentacao de enterramentos arqueologicos. Esta ferramenta permite registar todos os aspetos de uma sepultura: desde a estrutura funeraria ao rito, do espolio funerario aos individuos sepultados.

### Conceitos Basicos

**Sepultura no PyArchInit:**
- Uma sepultura e uma estrutura funeraria que contem um ou mais individuos
- Esta ligada a Ficha de Estrutura (a estrutura fisica do enterramento)
- Esta ligada a Ficha de Individuo (para dados antropologicos)
- Documenta o rito, espolio funerario e caracteristicas da deposicao

**Relacoes:**
```
Sepultura -> Estrutura (contentor fisico)
          -> Individuo(s) (restos humanos)
          -> Espolio funerario (objetos acompanhantes)
          -> Inventario de Materiais (achados associados)
```

---

## Aceder a Ficha

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Grave Form**

![Acesso pelo menu](images/06_scheda_tomba/02_menu_accesso.png)

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone **Grave** (simbolo de sepultura)

![Acesso pela barra de ferramentas](images/06_scheda_tomba/03_toolbar_accesso.png)

---

## Panoramica da Interface

A ficha apresenta uma disposicao organizada em seccoes funcionais:

![Interface completa](images/06_scheda_tomba/04_interfaccia_completa.png)

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | Barra de Ferramentas DBMS | Navegacao, pesquisa, gravacao |
| 2 | Info BD | Estado do registo, ordenacao, contador |
| 3 | Campos de Identificacao | Sitio, Area, N.o da ficha, Estrutura |
| 4 | Campos do Individuo | Ligacao ao individuo |
| 5 | Area de Separadores | Separadores tematicos para dados especificos |

---

## Barra de Ferramentas DBMS

A barra de ferramentas principal fornece ferramentas para a gestao de registos.

![Barra de Ferramentas DBMS](images/06_scheda_tomba/05_toolbar_dbms.png)

### Botoes de Navegacao

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Primeiro](../../resources/icons/5_leftArrows.png) | Primeiro reg | Ir para o primeiro registo |
| ![Anterior](../../resources/icons/4_leftArrow.png) | Reg anterior | Ir para o registo anterior |
| ![Seguinte](../../resources/icons/6_rightArrow.png) | Reg seguinte | Ir para o registo seguinte |
| ![Ultimo](../../resources/icons/7_rightArrows.png) | Ultimo reg | Ir para o ultimo registo |

### Botoes CRUD

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Novo](../../resources/icons/newrec.png) | Novo registo | Criar um novo registo de sepultura |
| ![Guardar](../../resources/icons/b_save.png) | Guardar | Guardar alteracoes |
| ![Eliminar](../../resources/icons/delete.png) | Eliminar | Eliminar o registo atual |

### Botoes de Pesquisa

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![Nova Pesquisa](../../resources/icons/new_search.png) | Nova pesquisa | Iniciar nova pesquisa |
| ![Pesquisar](../../resources/icons/search.png) | Pesquisar!!! | Executar pesquisa |
| ![Ordenar](../../resources/icons/sort.png) | Ordenar por | Ordenar resultados |
| ![Ver Todos](../../resources/icons/view_all.png) | Ver todos | Ver todos os registos |

### Botoes Especiais

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| ![GIS](../../resources/icons/GIS.png) | GIS | Carregar sepultura no mapa |
| ![PDF](../../resources/icons/pdf-icon.png) | Exportacao PDF | Exportar para PDF |
| ![Diretorio](../../resources/icons/directoryExp.png) | Abrir diretorio | Abrir pasta de exportacao |

---

## Campos de Identificacao

Os campos de identificacao definem univocamente a sepultura na base de dados.

![Campos de identificacao](images/06_scheda_tomba/06_campi_identificativi.png)

### Sitio

**Campo**: `comboBox_sito`
**Base de dados**: `sito`

Selecionar o sitio arqueologico de pertenca.

### Area

**Campo**: `comboBox_area`
**Base de dados**: `area`

Area de escavacao dentro do sitio.

### Numero da Ficha

**Campo**: `lineEdit_nr_scheda`
**Base de dados**: `nr_scheda_taf`

Numero progressivo da ficha de sepultura. O proximo numero disponivel e proposto automaticamente.

### Codigo e Numero da Estrutura

| Campo | Base de dados | Descricao |
|-------|---------------|-----------|
| Codigo da estrutura | `sigla_struttura` | Codigo da estrutura (ex.: TM, TB) |
| N.o da estrutura | `nr_struttura` | Numero da estrutura |

Estes campos ligam a sepultura a Ficha de Estrutura correspondente.

### Numero do Individuo

**Campo**: `comboBox_nr_individuo`
**Base de dados**: `nr_individuo`

Numero do individuo sepultado. Liga a sepultura a Ficha de Individuo.

**Notas:**
- Uma sepultura pode conter multiplos individuos (enterramento multiplo)
- O menu mostra os individuos disponiveis para a estrutura selecionada

---

## Separador Dados Descritivos

O primeiro separador contem campos fundamentais para a descricao do enterramento.

![Separador Dados Descritivos](images/06_scheda_tomba/07_tab_descrittivi.png)

### Rito

**Campo**: `comboBox_rito`
**Base de dados**: `rito`

Tipo de ritual funerario praticado.

**Valores tipicos:**
| Rito | Descricao |
|------|-----------|
| Inumacao | Deposicao do corpo inteiro |
| Cremacao | Incineracao dos restos |
| Cremacao primaria | Cremacao no local |
| Cremacao secundaria | Cremacao noutro local e deposicao |
| Misto | Combinacao de ritos |
| Indeterminado | Nao determinavel |

### Tipo de Enterramento

**Campo**: `comboBox_tipo_sepoltura`
**Base de dados**: `tipo_sepoltura`

Classificacao tipologica do enterramento.

**Exemplos:**
- Sepultura em fossa simples
- Sepultura em cista
- Sepultura em camara
- Sepultura alla cappuccina
- Sepultura em enchytrismos
- Sarcofago
- Ossuario

### Tipo de Deposicao

**Campo**: `comboBox_tipo_deposizione`
**Base de dados**: `tipo_deposizione`

Metodo de deposicao do corpo.

**Valores:**
- Primaria (deposicao direta)
- Secundaria (reducao/deslocamento)
- Multipla simultanea
- Multipla sucessiva

### Estado de Conservacao

**Campo**: `comboBox_stato_conservazione`
**Base de dados**: `stato_di_conservazione`

Avaliacao do estado de conservacao.

**Escala:**
- Excelente
- Bom
- Razoavel
- Mau
- Muito mau

### Descricao

**Campo**: `textEdit_descrizione`
**Base de dados**: `descrizione_taf`

Descricao detalhada da sepultura.

**Conteudo recomendado:**
- Forma e dimensoes da fossa
- Orientacao
- Profundidade
- Caracteristicas do enchimento
- Condicao no momento da escavacao

### Interpretacao

**Campo**: `textEdit_interpretazione`
**Base de dados**: `interpretazione_taf`

Interpretacao historico-arqueologica do enterramento.

---

## Caracteristicas da Sepultura

### Sinalizadores

**Campo**: `comboBox_segnacoli`
**Base de dados**: `segnacoli`

Presenca e tipo de sinalizadores da sepultura.

**Valores:**
- Ausente
- Estela
- Cipo
- Tumulo
- Recinto
- Outro

### Canal Libatorio

**Campo**: `comboBox_canale_libatorio`
**Base de dados**: `canale_libatorio_si_no`

Presenca de canal para libacoes rituais.

**Valores:** Sim / Nao

### Cobertura

**Campo**: `comboBox_copertura_tipo`
**Base de dados**: `copertura_tipo`

Tipo de cobertura da sepultura.

**Exemplos:**
- Telhas
- Lajes de pedra
- Tabuas de madeira
- Terra
- Ausente

### Contentor dos Restos

**Campo**: `comboBox_tipo_contenitore`
**Base de dados**: `tipo_contenitore_resti`

Tipo de contentor para os restos.

**Exemplos:**
- Fossa em terra
- Caixa de madeira
- Caixa de pedra
- Anfora
- Urna
- Sarcofago

### Objetos Exteriores

**Campo**: `comboBox_oggetti_esterno`
**Base de dados**: `oggetti_rinvenuti_esterno`

Objetos encontrados fora da sepultura mas associados a ela.

---

## Separador Espolio Funerario

Este separador gere a documentacao do espolio funerario.

![Separador Espolio Funerario](images/06_scheda_tomba/08_tab_corredo.png)

### Presenca de Espolio

**Campo**: `comboBox_corredo_presenza`
**Base de dados**: `corredo_presenza`

Indica se a sepultura continha espolio funerario.

**Valores:**
- Sim
- Nao
- Provavel
- Removido

### Tipo de Espolio

**Campo**: `comboBox_corredo_tipo`
**Base de dados**: `corredo_tipo`

Classificacao geral do espolio funerario.

**Categorias:**
- Pessoal (joias, fibulas)
- Ritual (vasos, lucernas)
- Simbolico (moedas, amuletos)
- Instrumental (ferramentas)
- Misto

### Descricao do Espolio

**Campo**: `textEdit_corredo_descrizione`
**Base de dados**: `corredo_descrizione`

Descricao detalhada dos objetos do espolio.

### Tabela do Espolio

**Widget**: `tableWidget_corredo_tipo`

Tabela para registo dos elementos individuais do espolio.

**Colunas:**
| Coluna | Descricao |
|--------|-----------|
| ID do achado | Numero de inventario do achado |
| ID do individuo | Individuo associado |
| Material | Tipo de material |
| Posicao na sepultura | Onde foi localizado na sepultura |
| Posicao relativa ao corpo | Posicao relativa ao corpo |

**Notas:**
- Os elementos estao ligados a Ficha de Inventario de Materiais
- A tabela e preenchida automaticamente com achados da estrutura

---

## Separador Outras Caracteristicas

Este separador contem informacao adicional sobre o enterramento.

![Separador Outras Caracteristicas](images/06_scheda_tomba/09_tab_altre.png)

### Periodizacao

| Campo | Base de dados | Descricao |
|-------|---------------|-----------|
| Periodo inicial | `periodo_iniziale` | Periodo de inicio de utilizacao |
| Fase inicial | `fase_iniziale` | Fase no periodo |
| Periodo final | `periodo_finale` | Periodo de fim de utilizacao |
| Fase final | `fase_finale` | Fase no periodo |
| Datacao alargada | `datazione_estesa` | Datacao literal |

Os valores sao preenchidos com base na Ficha de Periodizacao do sitio.

---

## Separador Ferramentas

O separador Ferramentas contem funcionalidades adicionais.

![Separador Ferramentas](images/06_scheda_tomba/10_tab_tools.png)

### Gestao de Media

Permite:
- Visualizar imagens associadas
- Adicionar novas fotografias por arrastar e largar
- Pesquisar media na base de dados

### Exportacao

Opcoes de exportacao:
- Lista de Sepulturas (lista sintetica)
- Fichas de Sepultura (fichas completas)
- Conversao PDF para Word

---

## Integracao GIS

### Visualizacao no Mapa

| Botao | Funcao |
|-------|--------|
| Comutador GIS | Ativar/desativar carregamento automatico |
| Carregar no GIS | Carregar sepultura no mapa |

### Camadas GIS

A ficha utiliza camadas especificas para sepulturas:
- **pyarchinit_tomba**: geometria da sepultura
- Ligacao com camadas de estrutura e UE

---

## Exportacao e Impressao

### Exportacao PDF

O botao PDF abre um painel com opcoes:

| Opcao | Descricao |
|-------|-----------|
| Lista de Sepulturas | Lista sintetica de sepulturas |
| Fichas de Sepultura | Fichas detalhadas completas |
| Imprimir | Gerar PDF |

### Conteudo da Ficha PDF

A ficha PDF inclui:
- Dados de identificacao
- Rito e tipo de enterramento
- Descricao e interpretacao
- Dados do espolio
- Periodizacao
- Imagens associadas

---

## Fluxo de Trabalho Operacional

### Criar uma Nova Sepultura

1. **Abrir ficha**
   - Pelo menu ou barra de ferramentas

2. **Novo registo**
   - Clicar em "New Record"
   - O numero da ficha e proposto automaticamente

3. **Dados de identificacao**
   ```
   Site: Necropole de Isola Sacra
   Area: 1
   N.o da ficha: 45
   Codigo da estrutura: TM
   N.o da estrutura: 45
   ```

4. **Ligacao ao individuo**
   ```
   N.o do Individuo: 1
   ```

5. **Dados descritivos** (Separador 1)
   ```
   Rito: Inumacao
   Tipo de enterramento: Sepultura em fossa simples
   Tipo de deposicao: Primaria
   Estado de conservacao: Bom

   Descricao: Fossa retangular com
   cantos arredondados, orientada E-O...

   Sinalizadores: Cipo
   Cobertura: Telhas alla cappuccina
   ```

6. **Espolio funerario** (Separador 2)
   ```
   Presenca: Sim
   Tipo: Pessoal
   Descricao: Fibula em bronze junto ao ombro direito,
   moeda junto a boca...
   ```

7. **Periodizacao**
   ```
   Periodo inicial: II - Fase A
   Periodo final: II - Fase A
   Datacao: Seculo II d.C.
   ```

8. **Guardar**
   - Clicar em "Save"

### Pesquisar Sepulturas

1. Clicar em "New Search"
2. Preencher criterios:
   - Sitio
   - Rito
   - Tipo de enterramento
   - Periodo
3. Clicar em "Search"
4. Navegar pelos resultados

---

## Relacoes com Outras Fichas

| Ficha | Relacao |
|-------|---------|
| **Ficha de Sitio** | O sitio contem sepulturas |
| **Ficha de Estrutura** | Estrutura fisica da sepultura |
| **Ficha de Individuo** | Restos humanos na sepultura |
| **Ficha de Inventario de Materiais** | Achados do espolio |
| **Ficha de Periodizacao** | Cronologia |

### Fluxo de Trabalho Recomendado

1. Criar **Ficha de Sitio** (se nao existir)
2. Criar **Ficha de Estrutura** para a sepultura
3. Criar **Ficha de Sepultura** ligando a estrutura
4. Criar **Ficha de Individuo** para cada individuo
5. Registar o espolio na **Ficha de Inventario de Materiais**

---

## Boas Praticas

### Nomenclatura

- Utilizar codigos consistentes (TM, TB, SEP)
- Numeracao progressiva dentro do sitio
- Documentar as convencoes adotadas

### Descricao

- Descrever sistematicamente forma, dimensoes, orientacao
- Documentar a condicao no momento da escavacao
- Separar observacoes objetivas das interpretacoes

### Espolio

- Registar a posicao exata de cada objeto
- Ligar cada elemento ao Inventario de Materiais
- Documentar associacoes significativas

### Periodizacao

- Basear a datacao em elementos diagnosticos
- Indicar o nivel de fiabilidade
- Comparar com enterramentos semelhantes

---

## Resolucao de Problemas

### Problema: Individuo nao disponivel no menu

**Causa**: Individuo ainda nao criado ou nao associado a estrutura.

**Solucao**:
1. Verificar se a Ficha de Individuo existe
2. Verificar se o individuo esta associado a mesma estrutura

### Problema: Espolio nao apresentado na tabela

**Causa**: Achados nao ligados a estrutura.

**Solucao**:
1. Abrir a Ficha de Inventario de Materiais
2. Verificar se os achados tem a estrutura correta
3. Atualizar a Ficha de Sepultura

### Problema: Sepultura nao visivel no mapa

**Causa**: Geometria nao associada.

**Solucao**:
1. Verificar se a camada de sepulturas existe
2. Verificar se a estrutura tem geometria
3. Verificar o sistema de coordenadas de referencia

---

## Referencias

### Base de Dados

- **Tabela**: `tomba_table`
- **Classe mapper**: `TOMBA`
- **ID**: `id_tomba`

### Ficheiros Fonte

- **UI**: `gui/ui/Tomba.ui`
- **Controlador**: `tabs/Tomba.py`
- **Exportacao PDF**: `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Video Tutorial

### Panoramica da Ficha de Sepultura
**Duracao**: 5-6 minutos
- Apresentacao da interface
- Campos principais
- Navegacao entre separadores

[Marcador de video: video_panoramica_tomba.mp4]

### Documentacao Completa de Sepultura
**Duracao**: 10-12 minutos
- Criacao de novo registo
- Preenchimento de todos os campos
- Ligacao do individuo e espolio

[Marcador de video: video_schedatura_tomba.mp4]

### Gestao do Espolio Funerario
**Duracao**: 6-8 minutos
- Registo dos elementos do espolio
- Ligacao com o Inventario de Materiais
- Documentacao de posicoes

[Marcador de video: video_corredo_tomba.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
