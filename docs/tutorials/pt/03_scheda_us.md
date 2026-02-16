# PyArchInit - Ficha de UE/UEM (Unidade Estratigrafica)

## Indice
1. [Introducao](#introducao)
2. [Conceitos Fundamentais](#conceitos-fundamentais)
3. [Aceder a Ficha](#aceder-a-ficha)
4. [Interface Geral](#interface-geral)
5. [Campos de Identificacao](#campos-de-identificacao)
6. [Separador Localizacao](#separador-localizacao)
7. [Separador Dados Descritivos](#separador-dados-descritivos)
8. [Separador Periodizacao](#separador-periodizacao)
9. [Separador Relacoes Estratigraficas](#separador-relacoes-estratigraficas)
10. [Separador Dados Fisicos](#separador-dados-fisicos)
11. [Separador Dados de Registo](#separador-dados-de-registo)
12. [Separador Medicoes da UE](#separador-medicoes-da-ue)
13. [Separador Documentacao](#separador-documentacao)
14. [Separador Tecnica Construtiva UEM](#separador-tecnica-construtiva-uem)
15. [Separador Ligantes UEM](#separador-ligantes-uem)
16. [Separador Media](#separador-media)
17. [Separador Ajuda - Caixa de Ferramentas](#separador-ajuda---caixa-de-ferramentas)
18. [Harris Matrix](#harris-matrix)
19. [Funcionalidades GIS](#funcionalidades-gis)
20. [Exportacoes](#exportacoes)
21. [Fluxo de Trabalho Operacional](#fluxo-de-trabalho-operacional)
22. [Resolucao de Problemas](#resolucao-de-problemas)

---

## Introducao

A **Ficha de UE/UEM** (Unidade Estratigrafica / Unidade Estratigrafica Muraria) e o nucleo da documentacao arqueologica no PyArchInit. Representa a ferramenta principal para registar toda a informacao relativa as unidades estratigraficas identificadas durante a escavacao.

Esta ficha implementa os principios do **metodo estratigrafico** desenvolvido por Edward C. Harris, permitindo documentar:
- Caracteristicas fisicas de cada camada
- Relacoes estratigraficas entre unidades
- Cronologia relativa e absoluta
- Documentacao grafica e fotografica associada

<!-- VIDEO: Introducao a Ficha de UE -->
> **Video Tutorial**: [Inserir ligacao de video de introducao a ficha de UE]

---

## Conceitos Fundamentais

### O que e uma Unidade Estratigrafica (UE)

Uma **Unidade Estratigrafica** e a menor unidade de escavacao que pode ser identificada e distinguida das demais. Pode ser:
- **Camada**: deposito de terra com caracteristicas homogeneas
- **Interface**: superficie de contacto entre camadas (ex.: corte de fossa)
- **Elemento estrutural**: parte de uma construcao

### Tipos de Unidade

| Tipo | Codigo | Descricao |
|------|--------|-----------|
| UE | Unidade Estratigrafica | Camada generica |
| UEM | Unidade Estratigrafica Mural | Elemento construtivo de parede |
| USVA | Unita Stratigrafica Verticale A | Alzato verticale tipo A |
| USVB | Unita Stratigrafica Verticale B | Alzato verticale tipo B |
| USVC | Unita Stratigrafica Verticale C | Alzato verticale tipo C |
| USD | Unita Stratigrafica di Demolizione | Strato di crollo/demolizione |
| CON | Conci | Blocchi architettonici |
| VSF | Virtual Stratigraphic Feature | Elemento virtuale |
| SF | Stratigraphic Feature | Feature stratigrafica |
| SUS | Sub-Unita Stratigrafica | Suddivisione di US |
| DOC | Documentazione | Elemento documentario |

### Relacoes Estratigraficas

As relacoes estratigraficas definem as relacoes temporais entre UEs:

| Relacao | Inversa | Significado |
|---------|---------|-------------|
| **Cobre** | Coberta por | A UE sobrepoe-se fisicamente |
| **Corta** | Cortada por | A UE interrompe/cruza |
| **Preenche** | Preenchida por | A UE preenche uma cavidade |
| **Encosta-se a** | Suporta | Relacao de apoio |

<!-- IMAGE: Diagrama de relacoes estratigraficas -->
![Relacoes Estratigraficas](images/03_scheda_us/01_schema_rapporti.png)
*Figura 1: Diagrama de relacoes estratigraficas*

---

## Aceder a Ficha

Para aceder a Ficha de UE:

1. Menu **PyArchInit** -> **Archaeological record management** -> **SU/WSU**
2. Ou, na barra de ferramentas do PyArchInit, clicar no icone **SU/WSU**

<!-- IMAGE: Captura de ecra do menu de acesso -->
![Acesso a Ficha de UE](images/03_scheda_us/02_menu_scheda_us.png)
*Figura 2: Aceder a Ficha de UE a partir do menu*

<!-- IMAGE: Captura de ecra da barra de ferramentas -->
![Barra de Ferramentas UE](images/03_scheda_us/03_toolbar_us.png)
*Figura 3: Icone da Ficha de UE na barra de ferramentas*

---

## Interface Geral

A Ficha de UE esta organizada em varias areas funcionais:

<!-- IMAGE: Captura de ecra da interface completa com areas numeradas -->
![Interface UE](images/03_scheda_us/04_interfaccia_completa.png)
*Figura 4: Interface completa da Ficha de UE*

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | **Campos de Identificacao** | Sitio, Area, UE, Tipo, Definicoes |
| 2 | **Barra de Ferramentas DBMS** | Navegacao, gravacao, pesquisa |
| 3 | **Separadores de Dados** | Separadores tematicos para dados |
| 4 | **Barra de Ferramentas GIS** | Ferramentas de visualizacao no mapa |
| 5 | **Separador Caixa de Ferramentas** | Ferramentas avancadas e Matrix |

### Barra de Ferramentas DBMS

A barra de ferramentas DBMS e identica a da Ficha de Sitio com algumas funcionalidades adicionais:

<!-- IMAGE: Captura de ecra da barra de ferramentas DBMS da UE -->
![Barra de Ferramentas DBMS](images/03_scheda_us/05_toolbar_dbms.png)
*Figura 5: Barra de Ferramentas DBMS da Ficha de UE*

| Botao | Funcao | Descricao |
|-------|--------|-----------|
| **New record** | Novo | Cria uma nova ficha de UE |
| **Save** | Guardar | Guarda as alteracoes |
| **Delete** | Eliminar | Elimina a ficha atual |
| **View all** | Ver todos | Mostra todos os registos |
| **First/Prev/Next/Last** | Navegacao | Navegar entre registos |
| **new search** | Pesquisa | Inicia o modo de pesquisa |
| **search !!!** | Executar | Executa a pesquisa |
| **Order by** | Ordenar | Ordena os registos |
| **Report** | Imprimir | Gera relatorio PDF |
| **SU/Photo list** | Lista | Gera listas |

---

## Campos de Identificacao

Os campos de identificacao estao sempre visiveis no topo da ficha.

<!-- IMAGE: Captura de ecra dos campos de identificacao -->
![Campos de Identificacao](images/03_scheda_us/06_campi_identificativi.png)
*Figura 6: Campos de identificacao*

### Campos Obrigatorios

| Campo | Descricao | Formato |
|-------|-----------|---------|
| **Site** | Nome do sitio arqueologico | Texto (da combobox) |
| **Area** | Numero da area de escavacao | Inteiro (1-20) |
| **SU/WSU** | Numero da unidade estratigrafica | Inteiro |
| **Unit type** | Tipo de unidade (SU, WSU, etc.) | Selecao |

### Campos Descritivos

| Campo | Descricao |
|-------|-----------|
| **Stratigraphic definition** | Classificacao estratigrafica (do thesaurus) |
| **Interpretive definition** | Interpretacao funcional (do thesaurus) |

### Definicoes Estratigraficas (Exemplos)

| Definicao | Descricao |
|-----------|-----------|
| Layer | Deposito generico |
| Fill | Material de enchimento |
| Cut | Interface negativa |
| Floor surface | Superficie de circulacao |
| Collapse | Material de derrube |
| Beaten earth | Pavimento de terra batida |

### Definicoes Interpretativas (Exemplos)

| Definicao | Descricao |
|-----------|-----------|
| Construction activity | Fase construtiva |
| Abandonment | Fase de abandono |
| Flooring | Superficie de pavimento |
| Wall | Estrutura de parede |
| Pit | Escavacao intencional |
| Leveling | Camada de preparacao |

---

## Separador Localizacao

Contem dados de posicionamento dentro da escavacao.

<!-- IMAGE: Captura de ecra do separador de localizacao -->
![Separador Localizacao](images/03_scheda_us/07_tab_localizzazione.png)
*Figura 7: Separador Localizacao*

### Campos de Localizacao

| Campo | Descricao | Notas |
|-------|-----------|-------|
| **Sector** | Setor de escavacao | Letras A-H ou numeros 1-20 |
| **Square/Wall** | Referencia espacial | Para escavacoes em quadricula |
| **Room** | Numero da divisao | Para edificios/estruturas |
| **Trench** | Numero da sondagem | Para sondagens de teste |

### Numeros de Catalogo

| Campo | Descricao |
|-------|-----------|
| **General Cat. Nr.** | Numero de catalogo geral |
| **Internal Cat. Nr.** | Numero de catalogo interno |
| **International Cat. Nr.** | Codigo internacional |

---

## Separador Dados Descritivos

Contem a descricao textual da unidade estratigrafica.

<!-- IMAGE: Captura de ecra do separador de dados descritivos -->
![Separador Dados Descritivos](images/03_scheda_us/08_tab_dati_descrittivi.png)
*Figura 8: Separador Dados Descritivos*

### Campos Descritivos

| Campo | Descricao | Sugestoes |
|-------|-----------|-----------|
| **Description** | Descricao fisica da UE | Cor, consistencia, composicao, limites |
| **Interpretation** | Interpretacao funcional | Funcao, formacao, significado |
| **Dating elements** | Materiais para datacao | Ceramica, moedas, objetos datantes |
| **Observations** | Notas adicionais | Duvidas, hipoteses, comparacoes |

### Como Descrever uma UE

**Descricao fisica:**
```
Camada de solo argiloso, cor castanha escura (10YR 3/3),
consistencia compacta, com inclusoes de fragmentos de tijolo (2-5 cm),
seixos de calcario (1-3 cm) e carvao. Limites nitidos superiormente,
difusos inferiormente. Espessura variavel 15-25 cm.
```

**Interpretacao:**
```
Camada de abandono formada apos a cessacao das atividades
na divisao. A presenca de material de construcao fragmentado
sugere colapso parcial das estruturas.
```

---

## Separador Periodizacao

Gere a cronologia da unidade estratigrafica.

<!-- IMAGE: Captura de ecra do separador de periodizacao -->
![Separador Periodizacao](images/03_scheda_us/09_tab_periodizzazione.png)
*Figura 9: Separador Periodizacao*

### Periodizacao Relativa

| Campo | Descricao |
|-------|-----------|
| **Initial Period** | Periodo de formacao |
| **Initial Phase** | Fase de formacao |
| **Final Period** | Periodo de obliteracao |
| **Final Phase** | Fase de obliteracao |

**Nota**: Os periodos e fases devem ser primeiro criados na **Ficha de Periodizacao**.

### Cronologia Absoluta

| Campo | Descricao |
|-------|-----------|
| **Dating** | Data absoluta ou intervalo |
| **Year** | Ano da escavacao |

### Outros Campos

| Campo | Descricao | Valores |
|-------|-----------|---------|
| **Activity** | Tipo de atividade | Texto livre |
| **Structure** | Codigo de estrutura associada | Da Ficha de Estrutura |
| **Excavated** | Estado da escavacao | Sim / Nao |
| **Excavation method** | Modo de escavacao | Mecanico / Estratigrafico |

### Campo Estrutura - Ligacao com a Ficha de Estrutura

O campo **Structure** permite associar uma ou mais estruturas a unidade estratigrafica atual. E um campo de selecao multipla (caixas de verificacao).

#### Como funciona a sincronizacao

1. **Primeiro** criar estruturas na **Ficha de Estrutura**
2. Na Ficha de Estrutura preencher: **Site** (igual ao da UE), **Code** (ex.: "MUR"), **Number** (ex.: 1)
3. Na Ficha de UE, o campo Estrutura mostrara as estruturas disponiveis no formato `CODIGO-NUMERO`

#### Selecionar estruturas

1. Clicar no campo **Structure** para abrir o menu pendente
2. Assinalar as caixas das estruturas a associar
3. Pode selecionar **multiplas estruturas** de uma vez
4. Guardar o registo

#### Remover uma unica estrutura

1. Clicar no campo **Structure** para abrir o menu pendente
2. **Desmarcar** a caixa da estrutura a remover
3. Guardar o registo

#### Remover todas as estruturas (Limpar campo)

1. **Clicar com o botao direito** no campo Estrutura
2. Selecionar "**Clear Structure field**" no menu de contexto
3. Guardar o registo para confirmar a alteracao

> **Nota**: A funcao "Limpar campo" remove TODAS as estruturas associadas. Para remover apenas uma, utilize as caixas de verificacao.

---

## Separador Relacoes Estratigraficas

**Este e o separador mais importante da ficha de UE.** Define as relacoes estratigraficas com outras unidades.

<!-- IMAGE: Captura de ecra do separador de relacoes estratigraficas -->
![Separador Relacoes](images/03_scheda_us/10_tab_rapporti.png)
*Figura 10: Separador Relacoes Estratigraficas*

<!-- VIDEO: Como introduzir relacoes estratigraficas -->
> **Video Tutorial**: [Inserir ligacao de video de relacoes estratigraficas]

### Estrutura da Tabela de Relacoes

| Coluna | Descricao |
|--------|-----------|
| **Site** | Sitio da UE relacionada |
| **Area** | Area da UE relacionada |
| **SU** | Numero da UE relacionada |
| **Relationship type** | Tipo de relacao |

### Tipos de Relacao Disponiveis

| Italiano | Ingles | Alemao |
|----------|--------|--------|
| Copre | Covers | Liegt uber |
| Coperto da | Covered by | Liegt unter |
| Taglia | Cuts | Schneidet |
| Tagliato da | Cut by | Geschnitten von |
| Riempie | Fills | Verfullt |
| Riempito da | Filled by | Verfullt von |
| Si appoggia a | Abuts | Stutzt sich auf |
| Gli si appoggia | Supports | Wird gestutzt von |
| Uguale a (=) | Same as | Gleich |
| Anteriore (>>) | Earlier | Fruher |
| Posteriore (<<) | Later | Spater |

### Introduzir Relacoes

1. Clicar em **+** para adicionar uma linha
2. Introduzir Sitio, Area, UE da UE relacionada
3. Selecionar o tipo de relacao
4. Guardar

<!-- IMAGE: Captura de ecra de introducao de relacao -->
![Introducao de Relacao](images/03_scheda_us/11_inserimento_rapporto.png)
*Figura 11: Introduzir uma relacao estratigrafica*

### Botoes de Relacoes

| Botao | Funcao |
|-------|--------|
| **+** | Adicionar linha |
| **-** | Remover linha |
| **Insert or update inverse relat.** | Criar automaticamente a relacao inversa |
| **Go to SU** | Navegar para a UE selecionada |
| **Display matrix** | Mostrar o Harris Matrix |
| **Fix** | Corrigir erros de relacao |

### Relacoes Inversas Automaticas

Ao introduzir uma relacao, pode criar automaticamente a inversa:

| Se introduzir | Sera criado |
|---------------|-------------|
| UE 1 **cobre** UE 2 | UE 2 **coberta por** UE 1 |
| UE 1 **corta** UE 2 | UE 2 **cortada por** UE 1 |
| UE 1 **preenche** UE 2 | UE 2 **preenchida por** UE 1 |

### Verificacao de Relacoes

O botao **Check relationships** verifica a consistencia das relacoes:
- Deteta relacoes em falta
- Encontra inconsistencias
- Assinala erros logicos

<!-- IMAGE: Captura de ecra de verificacao de relacoes -->
![Verificacao de Relacoes](images/03_scheda_us/12_controllo_rapporti.png)
*Figura 12: Resultado da verificacao de relacoes*

---

## Separador Relacoes da Matrix Estendida

Separador dedicado a gestao avancada de relacoes para a Matrix Estendida.

<!-- IMAGE: Captura de ecra do separador EM -->
![Separador EM](images/03_scheda_us/13_tab_em.png)
*Figura 13: Separador Relacoes da Matrix Estendida*

Este separador permite adicionar informacao suplementar para cada relacao:
- Tipo de unidade
- Definicao interpretativa
- Periodizacao

---

## Separador Dados Fisicos

Descreve as caracteristicas fisicas da unidade estratigrafica.

<!-- IMAGE: Captura de ecra do separador de dados fisicos -->
![Separador Dados Fisicos](images/03_scheda_us/14_tab_dati_fisici.png)
*Figura 14: Separador Dados Fisicos*

### Caracteristicas Gerais

| Campo | Valores |
|-------|---------|
| **Color** | Castanho, Amarelo, Cinzento, Preto, etc. |
| **Consistency** | Argilosa, Compacta, Friavel, Arenosa |
| **Formation** | Artificial, Natural |
| **Position** | - |
| **Formation mode** | Aporte, Subtracao, Acumulacao, Deslizamento |
| **Distinction criteria** | Texto livre |

### Tabelas de Componentes

| Tabela | Conteudo |
|--------|----------|
| **Organic comp.** | Ossos, madeira, carvao, sementes, etc. |
| **Inorganic comp.** | Pedras, tijolos, ceramica, etc. |
| **Artificial Inclusions** | Materiais antropicos incluidos |

Para cada tabela:
- **+** Adicionar linha
- **-** Remover linha

### Amostragem

| Campo | Valores |
|-------|---------|
| **Flotation** | Sim / Nao |
| **Sieving** | Sim / Nao |
| **Reliability** | Fraca, Boa, Razoavel, Excelente |
| **Conservation status** | Insuficiente, Fraco, Bom, Razoavel, Excelente |

---

## Separador Dados de Registo

Informacoes sobre a compilacao da ficha.

<!-- IMAGE: Captura de ecra do separador de dados de registo -->
![Separador Dados de Registo](images/03_scheda_us/15_tab_schedatura.png)
*Figura 15: Separador Dados de Registo*

### Entidade e Responsaveis

| Campo | Descricao |
|-------|-----------|
| **Responsible Entity** | Entidade responsavel pela escavacao |
| **Superintendence** | SABAP competente |
| **Scientific Director** | Diretor da escavacao |
| **Compilation Manager** | Quem compilou a ficha de campo |
| **Reworking Manager** | Quem reelaborou os dados |

### Referencias

| Campo | Descricao |
|-------|-----------|
| **TM Ref.** | Referencia de ficha TM (Tabela de Materiais) |
| **RA Ref.** | Referencia de ficha RA (Achados Arqueologicos) |
| **Pottery Ref.** | Referencia de ficha de ceramica |

### Datas

| Campo | Formato |
|-------|---------|
| **Survey date** | DD/MM/AAAA |
| **Filing date** | DD/MM/AAAA |
| **Reworking date** | DD/MM/AAAA |

---

## Separador Medicoes da UE

Contem todas as medicoes da unidade estratigrafica.

<!-- IMAGE: Captura de ecra do separador de medicoes -->
![Separador Medicoes](images/03_scheda_us/16_tab_misure.png)
*Figura 16: Separador Medicoes da UE*

### Cotas

| Campo | Descricao | Unidade |
|-------|-----------|---------|
| **Absolute elevation** | Cota acima do nivel do mar | metros |
| **Relative elevation** | Cota relativa ao ponto de referencia | metros |
| **Max absolute elevation** | Cota absoluta maxima | metros |
| **Max relative elevation** | Cota relativa maxima | metros |
| **Min absolute elevation** | Cota absoluta minima | metros |
| **Min relative elevation** | Cota relativa minima | metros |

### Dimensoes

| Campo | Descricao | Unidade |
|-------|-----------|---------|
| **Max length** | Comprimento maximo | metros |
| **Average width** | Largura media | metros |
| **Max height** | Altura maxima | metros |
| **Min height** | Altura minima | metros |
| **Thickness** | Espessura da camada | metros |
| **Max depth** | Profundidade maxima | metros |
| **Min depth** | Profundidade minima | metros |

---

## Separador Documentacao

Gere as referencias a documentacao grafica e fotografica.

<!-- IMAGE: Captura de ecra do separador de documentacao -->
![Separador Documentacao](images/03_scheda_us/17_tab_documentazione.png)
*Figura 17: Separador Documentacao*

### Tabela de Documentacao

| Coluna | Descricao |
|--------|-----------|
| **Documentation type** | Foto, Planta, Corte, Alcado, etc. |
| **References** | Numero/codigo do documento |

### Tipos de Documentacao

| Tipo | Descricao |
|------|-----------|
| Photo | Documentacao fotografica |
| Plan | Planta de escavacao |
| Section | Corte estratigrafico |
| Elevation | Alcado de parede |
| Survey | Levantamento grafico |
| 3D | Modelo tridimensional |

### Botoes

| Botao | Funcao |
|-------|--------|
| **insert row** | Adiciona referencia |
| **remove row** | Remove referencia |
| **Update doc** | Atualiza a partir da tabela de documentacao |
| **View documentation** | Mostra documentos associados |

---

## Separador Tecnica Construtiva UEM

Separador especifico para Unidades Estratigraficas Murarias (UEM).

<!-- IMAGE: Captura de ecra do separador de tecnica construtiva -->
![Separador Tecnica Construtiva](images/03_scheda_us/18_tab_tecnica_usm.png)
*Figura 18: Separador Tecnica Construtiva UEM*

### Dados Especificos da UEM

| Campo | Descricao |
|-------|-----------|
| **WSU Length** | Comprimento da parede (metros) |
| **WSU Height** | Altura da parede (metros) |
| **Analyzed surface** | Percentagem analisada |
| **Wall section** | Tipo de seccao |
| **Module** | Modulo construtivo |
| **Work typology** | Tipo de paramento |
| **Orientation** | Orientacao da estrutura |
| **Reuse** | Sim / Nao |

### Materiais e Tecnicas

| Seccao | Campos |
|--------|--------|
| **Bricks** | Materiais, Tratamento, Consistencia, Forma, Cor, Mistura, Assentamento |
| **Stone Elements** | Materiais, Tratamento, Consistencia, Forma, Cor, Talhe, Assentamento |

### Amostras

| Campo | Descricao |
|-------|-----------|
| **Mortar samples** | Referencias de amostras de argamassa |
| **Brick samples** | Referencias de amostras de tijolo |
| **Stone samples** | Referencias de amostras de pedra |

---

## Separador Ligantes UEM

Descreve as caracteristicas dos ligantes (argamassa) nas estruturas murarias.

<!-- IMAGE: Captura de ecra do separador de ligantes -->
![Separador Ligantes](images/03_scheda_us/19_tab_leganti.png)
*Figura 19: Separador Ligantes UEM*

### Caracteristicas do Ligante

| Campo | Descricao |
|-------|-----------|
| **Binder type** | Argamassa, Barro, Ausente, etc. |
| **Consistency** | Tenaz, Friavel, etc. |
| **Color** | Cor do ligante |
| **Finish** | Tipo de acabamento |
| **Binder thickness** | Espessura em cm |

### Composicao

| Seccao | Descricao |
|--------|-----------|
| **Aggregates** | Componentes grosseiros |
| **Inerts** | Componentes finos |
| **Inclusions** | Materiais incluidos |

---

## Separador Media

Apresenta as imagens associadas a unidade estratigrafica.

<!-- IMAGE: Captura de ecra do separador de media -->
![Separador Media](images/03_scheda_us/20_tab_media.png)
*Figura 20: Separador Media*

### Lista de UEs

A tabela mostra todas as UEs com imagens associadas:
- Ir para a ficha
- Caixa de verificacao para selecao multipla
- Pre-visualizacao em miniatura

### Botoes

| Botao | Funcao |
|-------|--------|
| **Search images** | Pesquisar imagens associadas |
| **Save** | Guardar associacoes |
| **Revert** | Desfazer alteracoes |

---

## Separador Ajuda - Caixa de Ferramentas

Contem ferramentas avancadas para verificacao e exportacao.

<!-- IMAGE: Captura de ecra do separador caixa de ferramentas -->
![Separador Caixa de Ferramentas](images/03_scheda_us/21_tab_toolbox.png)
*Figura 21: Separador Caixa de Ferramentas*

### Sistemas de Verificacao

| Ferramenta | Descricao |
|------------|-----------|
| **Check stratigraphic relationships** | Verificar a consistencia das relacoes |
| **Check, go!!!!** | Executar a verificacao |

### Exportacao de Matrix

| Botao | Resultado |
|-------|-----------|
| **Export Matrix** | Ficheiro DOT para Graphviz |
| **Export Graphml** | Ficheiro GraphML para yEd |
| **Export to Extended Matrix** | Formato S3DGraphy |
| **Interactive Matrix** | Visualizacao interativa |

### Ferramentas Adicionais

| Ferramenta | Descricao |
|------------|-----------|
| **Stratigraphic order** | Calcular a sequencia estratigrafica |
| **Create Period Code** | Gerar codigos de periodo |
| **csv2us** | Importar UEs a partir de CSV |
| **Graphml2csv** | Exportar GraphML para CSV |

---

## Ordenacao Estratigrafica (Order Layer)

O sistema de **Ordenacao Estratigrafica** calcula automaticamente a sequencia de UEs com base nas relacoes estratigraficas introduzidas. E um calculo automatico que atribui um valor numerico progressivo a cada UE de acordo com a sua posicao na sequencia estratigrafica.

### Como funciona

O sistema analisa as relacoes estratigraficas (cobre/coberta por, corta/cortada por, etc.) e constroi um grafo dirigido. Depois calcula a ordem topologica, atribuindo:
- **Nivel 0**: UEs mais antigas (na base da estratigrafia)
- **Nivel 1, 2, 3...**: UEs progressivamente mais recentes
- **Nivel N**: UEs mais recentes (no topo da estratigrafia)

### Requisitos para a ordenacao

1. **Relacoes completas**: Todas as UEs devem ter relacoes estratigraficas introduzidas
2. **Sem paradoxos**: Nao podem existir ciclos nas relacoes (ex.: UE1 cobre UE2 e UE2 cobre UE1)
3. **Relacoes inversas**: Todas as relacoes devem ter a sua inversa

### Como executar a ordenacao

1. Efetuar uma **pesquisa** por Sitio e Area (o sistema funciona por sitio/area individual)
2. Ir ao **Separador Ajuda** -> **Caixa de Ferramentas**
3. Clicar em **Stratigraphic order**
4. Confirmar a operacao
5. Aguardar a conclusao

### Formato da ordenacao

A ordenacao e **sempre numerica sequencial**:
```
0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13...
```

**Regras:**
- Os numeros sao **sempre consecutivos** (nunca 1, 2, 5, 8 - sempre 1, 2, 3, 4)
- Sem lacunas na sequencia
- UEs ao mesmo nivel estratigrafico tem o mesmo numero
- A ordem pode ser **invertida** (caixa de verificacao "Order: Ancient -> Recent"):
  - **Ativa**: 0 = mais antiga, N = mais recente
  - **Inativa**: 0 = mais recente, N = mais antiga

### Campo Order Layer

O resultado e guardado no campo **Order Layer** (lineEditOrderLayer) de cada UE. Este campo:
- E **calculado automaticamente** pelo sistema
- Pode ser **modificado manualmente** se necessario
- E utilizado para ordenar as UEs na visualizacao

### Erros comuns

| Erro | Causa | Solucao |
|------|-------|---------|
| "Stratigraphic paradox" | Ciclo nas relacoes | Verificar e corrigir as relacoes |
| "Missing SUs" | UEs referenciadas nao existem | Criar as UEs em falta |
| "Missing relationship" | Relacao sem tipo ou numero | Completar as relacoes |

### Visualizacao

Uma vez calculada a ordem, pode:
- **Ordenar** registos por Order Layer
- **Filtrar** por niveis especificos
- **Exportar** Matrix com niveis

---

### Funcoes GIS

| Botao | Funcao |
|-------|--------|
| **Draw SU** | Carregar camada para desenho |
| **Preview SU plan** | Pre-visualizar no mapa |
| **Open SU forms** | Abre as fichas selecionadas |
| **Pan** | Ferramenta de panoramica |
| **Show images** | Mostrar fotografias |

### Exportacoes de Estampas

| Botao | Resultado |
|-------|-----------|
| **Plate Export** | Estampas de escavacao |
| **symbology** | Gestao de simbologia |
| **Open folder** | Abre a pasta de resultados |

---

## Harris Matrix

O Harris Matrix e uma representacao grafica das relacoes estratigraficas.

<!-- IMAGE: Captura de ecra do harris matrix -->
![Harris Matrix](images/03_scheda_us/22_matrix_harris.png)
*Figura 22: Exemplo de Harris Matrix*

<!-- VIDEO: Geracao do Harris Matrix -->
> **Video Tutorial**: [Inserir ligacao de video do Harris Matrix]

### Geracao da Matrix

1. Selecionar o sitio e a area
2. Verificar se as relacoes estao corretas
3. Ir ao **Separador Ajuda** -> **Caixa de Ferramentas**
4. Clicar em **Export Matrix**

### Formatos de Exportacao

| Formato | Software | Utilizacao |
|---------|----------|------------|
| DOT | Graphviz | Visualizacao basica |
| GraphML | yEd, Gephi | Edicao avancada |
| Extended Matrix | S3DGraphy | Visualizacao 3D |
| CSV | Excel | Analise de dados |

### Matrix Estendida

A Matrix Estendida adiciona informacao suplementar:
- Periodizacao
- Definicoes interpretativas
- Dados cronologicos
- Compatibilidade CIDOC-CRM

<!-- IMAGE: Captura de ecra da matrix estendida -->
![Matrix Estendida](images/03_scheda_us/23_extended_matrix.png)
*Figura 23: Dialogo da Matrix Estendida*

### Matrix Interativa

Visualizacao interativa da Matrix:
- Zoom e panoramica
- Selecao de nos
- Navegacao para fichas

---

## Funcionalidades GIS

A Ficha de UE esta intimamente integrada com o QGIS.

<!-- IMAGE: Captura de ecra da integracao GIS -->
![Integracao GIS](images/03_scheda_us/24_gis_integration.png)
*Figura 24: Integracao GIS*

### Barra de Ferramentas GIS

| Botao | Funcao | Atalho |
|-------|--------|--------|
| **GIS Viewer** | Carregar camadas de UE | Ctrl+G |
| **Preview SU plan** | Pre-visualizar geometria | Ctrl+G |
| **Draw SU** | Ativar desenho | - |

### Camadas GIS Associadas

| Camada | Geometria | Descricao |
|--------|-----------|-----------|
| PYUS | Poligono | Unidades estratigraficas |
| PYUSM | Poligono | Unidades murarias |
| PYQUOTE | Ponto | Cotas |
| PYQUOTEUSM | Ponto | Cotas UEM |
| PYUS_NEGATIVE | Poligono | UE negativas |

### Visualizacao de Resultados de Pesquisa

Quando o modo GIS esta ativo:
- As pesquisas sao apresentadas no mapa
- Os resultados sao realcados
- Pode navegar entre resultados

---

## Exportacoes

### Fichas de UE em PDF

1. Clicar em **Report** na barra de ferramentas
2. Escolher o formato (PDF, Word)
3. Selecionar as fichas a exportar

<!-- IMAGE: Captura de ecra da exportacao PDF -->
![Exportacao PDF](images/03_scheda_us/25_esportazione_pdf.png)
*Figura 25: Opcoes de exportacao PDF*

### Listas

| Tipo | Conteudo |
|------|----------|
| **SU List** | Lista de todas as UEs |
| **Photo List with Thumbnail** | Lista com pre-visualizacoes |
| **Photo List without Thumbnail** | Lista simples |
| **SU Forms** | Fichas completas |

### Conversao para Word

O botao **Convert to Word** permite:
1. Selecionar um PDF
2. Converter para formato DOCX
3. Editar no Word

---

## Fluxo de Trabalho Operacional

### Criar uma Nova UE

<!-- VIDEO: Fluxo de trabalho de criacao de UE -->
> **Video Tutorial**: [Inserir ligacao de video de criacao de UE]

#### Passo 1: Abrir a Ficha
<!-- IMAGE: Passo 1 -->
![Passo 1](images/03_scheda_us/26_workflow_step1.png)

#### Passo 2: Clicar em New Record
<!-- IMAGE: Passo 2 -->
![Passo 2](images/03_scheda_us/27_workflow_step2.png)

#### Passo 3: Introduzir Identificacao
- Selecionar o Sitio
- Introduzir a Area
- Introduzir o numero da UE
- Selecionar o Tipo

<!-- IMAGE: Passo 3 -->
![Passo 3](images/03_scheda_us/28_workflow_step3.png)

#### Passo 4: Definicoes
- Selecionar a definicao estratigrafica
- Selecionar a definicao interpretativa

<!-- IMAGE: Passo 4 -->
![Passo 4](images/03_scheda_us/29_workflow_step4.png)

#### Passo 5: Descricao
- Preencher a descricao fisica
- Preencher a interpretacao

<!-- IMAGE: Passo 5 -->
![Passo 5](images/03_scheda_us/30_workflow_step5.png)

#### Passo 6: Relacoes Estratigraficas
- Introduzir relacoes com outras UEs
- Criar relacoes inversas

<!-- IMAGE: Passo 6 -->
![Passo 6](images/03_scheda_us/31_workflow_step6.png)

#### Passo 7: Dados Fisicos e Medicoes
- Preencher as caracteristicas fisicas
- Introduzir as medicoes

<!-- IMAGE: Passo 7 -->
![Passo 7](images/03_scheda_us/32_workflow_step7.png)

#### Passo 8: Guardar
- Clicar em Save
- Verificar a gravacao

<!-- IMAGE: Passo 8 -->
![Passo 8](images/03_scheda_us/33_workflow_step8.png)

### Gerar o Harris Matrix

1. Verificar que todas as relacoes estao introduzidas
2. Executar a verificacao de relacoes
3. Corrigir eventuais erros
4. Exportar a Matrix

### Associar Documentacao

1. Primeiro criar fichas na tabela de Documentacao
2. Na ficha de UE, separador Documentacao
3. Adicionar referencias
4. Verificar com "View documentation"

---

## Resolucao de Problemas

### Erro ao guardar
- Verificar se Sitio, Area e UE estao preenchidos
- Verificar se a combinacao e unica

### Relacoes inconsistentes
- Utilizar a verificacao de relacoes
- Verificar relacoes inversas
- Corrigir com o botao Fix

### Matrix nao e gerada
- Verificar se o Graphviz esta instalado
- Verificar o caminho na configuracao
- Verificar se existem relacoes

### Camadas GIS nao carregam
- Verificar a ligacao a base de dados
- Verificar se existem geometrias
- Verificar o sistema de coordenadas de referencia

### Imagens nao apresentadas
- Verificar os caminhos das miniaturas
- Verificar as associacoes de media
- Verificar as permissoes da pasta

---

## Notas Tecnicas

### Base de Dados

- **Tabela principal**: `us_table`
- **Campos principais**: mais de 80 campos
- **Chave primaria**: `id_us`
- **Chave composta**: sitio + area + ue

### Thesaurus

Os campos com thesaurus (definicoes) utilizam a tabela `pyarchinit_thesaurus_sigle`:
- tipologia_sigla = '1.1' para definicao estratigrafica
- tipologia_sigla = '1.2' para definicao interpretativa

### Camadas GIS

| Camada | Tabela | Tipo |
|--------|--------|------|
| PYUS | pyarchinit_us_view | Poligono |
| PYUSM | pyarchinit_usm_view | Poligono |
| PYQUOTE | pyarchinit_quote_view | Ponto |

---

*Documentacao PyArchInit - Ficha de UE/UEM*
*Versao: 4.9.x*
*Ultima atualizacao: janeiro de 2026*
