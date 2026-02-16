# Tutorial 21: Formulario UT - Unidades Topograficas

## Introducao

O **Formulario UT** (Unidades Topograficas) e o modulo do PyArchInit dedicado a documentacao de prospeccoes arqueologicas de superficie. Permite registar dados relacionados com concentracoes de materiais, anomalias do terreno e sitios identificados durante prospeccoes de campo.

### Conceitos Basicos

**Unidade Topografica (UT):**
- Area delimitada com caracteristicas arqueologicas homogeneas
- Identificada durante prospeccao de superficie
- Definida por concentracao de materiais ou anomalias visiveis

**Prospeccao:**
- Prospeccao sistematica do territorio
- Recolha de dados sobre presenca humana antiga
- Documentacao sem escavacao

---

## Aceder ao Formulario

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Formulario UT**

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas do PyArchInit
2. Clicar no icone **UT**

---

## Visao Geral da Interface

O formulario esta organizado em varios separadores para documentar todos os aspetos da prospeccao.

### Separadores Principais

| # | Separador | Descricao |
|---|-----------|-----------|
| 1 | Identificacao | Projeto, N.o UT, Localizacao |
| 2 | Descricao | Definicao, descricao, interpretacao |
| 3 | Dados UT | Condicoes, metodologia, datas |
| 4 | Analise | Potencial e risco arqueologico |

### Barra de Ferramentas Principal

| Botao | Funcao |
|-------|--------|
| Primeiro | Ir para o primeiro registo |
| Anterior | Registo anterior |
| Seguinte | Registo seguinte |
| Ultimo | Ir para o ultimo registo |
| Pesquisar | Pesquisa avancada |
| Guardar | Guardar registo |
| Eliminar | Eliminar registo |
| PDF | Exportar ficha PDF |
| **Lista PDF** | Exportar lista de UT para PDF |
| **Exportacao GNA** | Exportar para formato GNA |
| Mostrar Camada | Apresentar camada no mapa |

---

## Campos de Identificacao

### Projeto

**Campo**: `comboBox_progetto`
**Base de dados**: `progetto`

Nome do projeto de prospeccao.

### Numero UT

**Campo**: `comboBox_nr_ut`
**Base de dados**: `nr_ut`

Numero progressivo da Unidade Topografica.

### Letra UT

**Campo**: `lineEdit_ut_letterale`
**Base de dados**: `ut_letterale`

Sufixo alfabetico opcional (p. ex., UT 15a, 15b).

---

## Campos de Localizacao

### Dados Administrativos

| Campo | Base de dados | Descricao |
|-------|--------------|-----------|
| Nacao | `nazione` | Pais |
| Regiao | `regione` | Regiao administrativa |
| Provincia | `provincia` | Provincia |
| Municipio | `comune` | Municipio |
| Freguesia | `frazione` | Freguesia/localidade |
| Localidade | `localita` | Toponimo local |
| Morada | `indirizzo` | Rua/estrada |
| N.o | `nr_civico` | Numero de policia |

### Dados Cartograficos

| Campo | Base de dados | Descricao |
|-------|--------------|-----------|
| Carta IGM | `carta_topo_igm` | Folha IGM |
| Carta CTR | `carta_ctr` | Elemento CTR |
| Folha cadastral | `foglio_catastale` | Referencia cadastral |

### Coordenadas

| Campo | Base de dados | Descricao |
|-------|--------------|-----------|
| Coord. geograficas | `coord_geografiche` | Lat/Long (formato: lat, lon) |
| Coord. planas | `coord_piane` | UTM/projecao local (formato: x, y) |
| Altitude | `quota` | Elevacao acima do nivel do mar |
| Precisao das coord. | `coordinate_precision` | Precisao GPS em metros |

**IMPORTANTE**: As coordenadas sao utilizadas para geracao de mapas de calor. Pelo menos um dos campos `coord_geografiche` ou `coord_piane` deve ser preenchido para cada UT.

---

## Campos Descritivos

### Definicao da UT

**Campo**: `comboBox_def_ut`
**Base de dados**: `def_ut`
**Thesaurus**: Codigo 12.7

Classificacao tipologica da UT. Os valores sao carregados do thesaurus e traduzidos automaticamente para o idioma atual.

**Valores padrao:**
| Codigo | Ingles | Italiano |
|--------|--------|----------|
| scatter | Material scatter | Area di dispersione materiali |
| site | Archaeological site | Sito archeologico |
| anomaly | Terrain anomaly | Anomalia del terreno |
| structure | Outcropping structure | Struttura affiorante |
| concentration | Finds concentration | Concentrazione reperti |
| traces | Anthropic traces | Tracce antropiche |
| findspot | Sporadic find | Rinvenimento sporadico |
| negative | Negative result | Esito negativo |

### Descricao da UT

**Campo**: `textEdit_descrizione`
**Base de dados**: `descrizione_ut`

Descricao detalhada da Unidade Topografica.

**Conteudos:**
- Extensao e forma da area
- Densidade de materiais
- Caracteristicas do terreno
- Visibilidade e condicoes

### Interpretacao da UT

**Campo**: `textEdit_interpretazione`
**Base de dados**: `interpretazione_ut`

Interpretacao funcional/historica.

---

## Campos de Prospeccao com Thesaurus

Os seguintes campos utilizam o sistema de thesaurus para garantir terminologia padronizada traduzida em 7 idiomas (IT, EN, DE, ES, FR, AR, CA).

### Tipo de Prospeccao (12.1)

**Campo**: `comboBox_survey_type`
**Base de dados**: `survey_type`

| Codigo | Ingles | Descricao |
|--------|--------|-----------|
| intensive | Intensive survey | Prospeccao intensiva sistematica |
| extensive | Extensive survey | Prospeccao por amostragem |
| targeted | Targeted survey | Investigacao de areas especificas |
| random | Random sampling | Metodologia aleatoria |

### Cobertura Vegetal (12.2)

**Campo**: `comboBox_vegetation_coverage`
**Base de dados**: `vegetation_coverage`

| Codigo | Ingles | Descricao |
|--------|--------|-----------|
| none | Absent | Solo nu |
| sparse | Sparse | Cobertura < 25% |
| moderate | Moderate | Cobertura 25-50% |
| dense | Dense | Cobertura 50-75% |
| very_dense | Very dense | Cobertura > 75% |

### Metodo GPS (12.3)

**Campo**: `comboBox_gps_method`
**Base de dados**: `gps_method`

| Codigo | Ingles | Descricao |
|--------|--------|-----------|
| handheld | Handheld GPS | Dispositivo GPS portatil |
| dgps | Differential GPS | DGPS com estacao base |
| rtk | RTK GPS | Cinematico em tempo real |
| total_station | Total station | Levantamento com estacao total |

### Condicao da Superficie (12.4)

**Campo**: `comboBox_surface_condition`
**Base de dados**: `surface_condition`

| Codigo | Ingles | Descricao |
|--------|--------|-----------|
| ploughed | Ploughed | Campo recentemente lavrado |
| stubble | Stubble | Presenca de restolho |
| pasture | Pasture | Terreno de pastagem/prado |
| woodland | Woodland | Area arborizada |
| urban | Urban | Area urbana/edificada |

### Acessibilidade (12.5)

**Campo**: `comboBox_accessibility`
**Base de dados**: `accessibility`

| Codigo | Ingles | Descricao |
|--------|--------|-----------|
| easy | Easy access | Sem restricoes |
| moderate_access | Moderate access | Algumas dificuldades |
| difficult | Difficult access | Problemas significativos |
| restricted | Restricted access | Apenas com autorizacao |

### Condicoes Meteorologicas (12.6)

**Campo**: `comboBox_weather_conditions`
**Base de dados**: `weather_conditions`

| Codigo | Ingles | Descricao |
|--------|--------|-----------|
| sunny | Sunny | Tempo limpo |
| cloudy | Cloudy | Condicoes nubladas |
| rainy | Rainy | Chuva durante a prospeccao |
| windy | Windy | Vento forte |

---

## Dados Ambientais

### Percentagem de Visibilidade

**Campo**: `spinBox_visibility_percent`
**Base de dados**: `visibility_percent`

Percentagem de visibilidade do solo (0-100%). Valor numerico importante para o calculo do potencial arqueologico.

### Declive do Terreno

**Campo**: `lineEdit_andamento_terreno_pendenza`
**Base de dados**: `andamento_terreno_pendenza`

Morfologia e declive do terreno.

### Uso do Solo

**Campo**: `lineEdit_utilizzo_suolo_vegetazione`
**Base de dados**: `utilizzo_suolo_vegetazione`

Uso do solo no momento da prospeccao.

---

## Dados de Materiais

### Dimensoes da UT

**Campo**: `lineEdit_dimensioni_ut`
**Base de dados**: `dimensioni_ut`

Extensao em metros quadrados.

### Achados por m2

**Campo**: `lineEdit_rep_per_mq`
**Base de dados**: `rep_per_mq`

Densidade de materiais por metro quadrado. Valor critico para o calculo do potencial.

### Achados Datantes

**Campo**: `lineEdit_rep_datanti`
**Base de dados**: `rep_datanti`

Descricao dos materiais diagnosticos.

---

## Cronologia

### Periodo I

| Campo | Base de dados |
|-------|--------------|
| Periodo I | `periodo_I` |
| Datacao I | `datazione_I` |
| Interpretacao I | `interpretazione_I` |

### Periodo II

| Campo | Base de dados |
|-------|--------------|
| Periodo II | `periodo_II` |
| Datacao II | `datazione_II` |
| Interpretacao II | `interpretazione_II` |

---

## Separador de Analise - Potencial e Risco Arqueologico

O separador **Analise** fornece ferramentas avancadas para calculo automatico do potencial e risco arqueologico.

### Potencial Arqueologico

O sistema calcula uma pontuacao de 0 a 100 com base em fatores ponderados:

| Fator | Peso | Descricao | Como e calculado |
|-------|------|-----------|------------------|
| Definicao UT | 30% | Tipo de evidencia arqueologica | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, etc. |
| Periodo historico | 25% | Cronologia dos materiais | Periodos mais antigos pesam mais (Pre-historico = 90, Romano = 85, Medieval = 70, etc.) |
| Densidade de achados | 20% | Materiais por m2 | >10/m2 = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Condicao da superficie | 15% | Visibilidade e acessibilidade | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentacao | 10% | Qualidade da documentacao | Presenca de fotos = +20, bibliografia = +30, investigacoes = +50 |

**Classificacao da Pontuacao:**

| Pontuacao | Nivel | Cor | Significado |
|-----------|-------|-----|-------------|
| 80-100 | Elevado | Verde | Elevada probabilidade de depositos significativos |
| 60-79 | Medio-Elevado | Amarelo-Verde | Boa probabilidade, verificacao recomendada |
| 40-59 | Medio | Laranja | Probabilidade moderada |
| 20-39 | Baixo | Vermelho | Baixa probabilidade |
| 0-19 | Nao avaliavel | Cinzento | Dados insuficientes |

### Risco Arqueologico

Avalia o risco de impacto/perda patrimonial:

| Fator | Peso | Descricao | Como e calculado |
|-------|------|-----------|------------------|
| Acessibilidade | 25% | Facilidade de acesso a area | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Uso do solo | 25% | Atividades agricolas/construtivas | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Condicionantes existentes | 20% | Protecoes legais | Sem condicionantes = 80, protecao paisagistica = 40, protecao arqueologica = 10 |
| Investigacoes previas | 15% | Estado do conhecimento | Sem investigacao = 60, prospeccao = 40, escavacao = 20 |
| Potencial | 15% | Inversamente proporcional ao potencial | Potencial elevado = risco elevado de perda |

**Classificacao do Risco:**

| Pontuacao | Nivel | Cor | Acao Recomendada |
|-----------|-------|-----|------------------|
| 75-100 | Elevado | Vermelho | Intervencao urgente, medidas de protecao imediatas |
| 50-74 | Medio | Laranja | Monitorizacao ativa, avaliar protecao |
| 25-49 | Baixo | Amarelo | Monitorizacao periodica |
| 0-24 | Nenhum | Verde | Nao e necessaria intervencao imediata |

### Campos da Base de Dados para Analise

| Campo | Base de dados | Descricao |
|-------|--------------|-----------|
| Pontuacao de Potencial | `potential_score` | Valor calculado 0-100 |
| Pontuacao de Risco | `risk_score` | Valor calculado 0-100 |
| Fatores de Potencial | `potential_factors` | JSON com detalhes dos fatores |
| Fatores de Risco | `risk_factors` | JSON com detalhes dos fatores |
| Data da Analise | `analysis_date` | Marca temporal do calculo |
| Metodo de Analise | `analysis_method` | Algoritmo utilizado |

---

## Camadas de Geometria UT

O PyArchInit gere tres tipos de geometrias para Unidades Topograficas:

### Tabelas de Geometria

| Camada | Tabela | Tipo de Geometria | Utilizacao |
|--------|--------|-------------------|------------|
| Pontos UT | `pyarchinit_ut_point` | Ponto | Localizacao pontual |
| Linhas UT | `pyarchinit_ut_line` | LineString | Tracos, percursos |
| Poligonos UT | `pyarchinit_ut_polygon` | Poligono | Areas de dispersao |

### Criar Camadas UT

1. **Pelo Explorador QGIS:**
   - Abrir a base de dados no Explorador
   - Localizar a tabela `pyarchinit_ut_point/line/polygon`
   - Arrastar para o mapa

2. **Pelo Menu PyArchInit:**
   - Menu **PyArchInit** > **Ferramentas SIG** > **Carregar Camadas UT**
   - Selecionar tipo de geometria

### Ligacao UT-Geometria

Cada registo de geometria esta ligado ao formulario UT atraves de:

| Campo | Descricao |
|-------|-----------|
| `progetto` | Nome do projeto (deve coincidir) |
| `nr_ut` | Numero da UT (deve coincidir) |

### Fluxo de Trabalho para Criacao de Geometria

1. **Ativar edicao** na camada UT pretendida
2. **Desenhar** a geometria no mapa
3. **Preencher** os atributos `progetto` e `nr_ut`
4. **Guardar** a camada
5. **Verificar** a ligacao a partir do formulario UT

---

## Geracao de Mapas de Calor

O modulo de geracao de mapas de calor permite visualizar a distribuicao espacial do potencial e risco arqueologico.

### Requisitos Minimos

- **Pelo menos 2 UT** com coordenadas validas (`coord_geografiche` OU `coord_piane`)
- **Pontuacoes calculadas** para potencial e/ou risco
- **SRC definido** no projeto QGIS

### Metodos de Interpolacao

| Metodo | Descricao | Quando utilizar |
|--------|-----------|-----------------|
| **KDE** (Kernel Density) | Estimativa de densidade de kernel gaussiano | Distribuicao continua, muitos pontos |
| **IDW** (Inverse Distance) | Ponderacao pelo inverso da distancia | Dados esparsos, valores pontuais importantes |
| **Grid** | Interpolacao em grelha regular | Analise sistematica |

### Parametros do Mapa de Calor

| Parametro | Valor Predefinido | Descricao |
|-----------|-------------------|-----------|
| Tamanho da celula | 50 m | Resolucao da grelha |
| Largura de banda (KDE) | Auto | Raio de influencia |
| Potencia (IDW) | 2 | Expoente de ponderacao |

### Procedimento de Geracao

1. **A partir do formulario UT:**
   - Ir ao separador **Analise**
   - Verificar que as pontuacoes estao calculadas
   - Clicar em **Gerar Mapa de Calor**

2. **Selecionar parametros:**
   - Tipo: Potencial ou Risco
   - Metodo: KDE, IDW ou Grid
   - Tamanho da celula: tipicamente 25-100 m

3. **Resultado:**
   - Camada raster adicionada ao QGIS
   - Guardada em `pyarchinit_Raster_folder`
   - Simbologia aplicada automaticamente

### Mapa de Calor com Mascara Poligonal (GNA)

Para gerar mapas de calor **dentro de uma area de projeto** (p. ex., perimetro de estudo):

1. **Preparar o poligono** da area do projeto
2. **Utilizar Exportacao GNA** (ver seccao seguinte)
3. O sistema **aplica automaticamente a mascara** ao mapa de calor sobre o poligono

---

## Exportacao GNA - Geoportal Nacional de Arqueologia

### O Que e o GNA?

O **Geoportal Nacional de Arqueologia** (GNA) e o sistema de informacao do Ministerio da Cultura italiano para gestao de dados arqueologicos territoriais. O PyArchInit suporta exportacao para o formato padrao GeoPackage do GNA.

### Estrutura GeoPackage do GNA

| Camada | Tipo | Descricao |
|--------|------|-----------|
| **MOPR** | Poligono | Area/perimetro do projeto |
| **MOSI** | Ponto/Poligono | Sitios arqueologicos (UT) |
| **VRP** | MultiPoligono | Mapa de Potencial Arqueologico |
| **VRD** | MultiPoligono | Mapa de Risco Arqueologico |

### Mapeamento de Campos UT para MOSI GNA

| Campo GNA | Campo UT PyArchInit | Notas |
|-----------|---------------------|-------|
| ID | `{progetto}_{nr_ut}` | Identificador composto |
| AMA | `def_ut` | Vocabulario controlado GNA |
| OGD | `interpretazione_ut` | Definicao do objeto |
| OGT | `geometria` | Tipo de geometria |
| DES | `descrizione_ut` | Descricao (max 10000 car.) |
| OGM | `metodo_rilievo_e_ricognizione` | Metodo de identificacao |
| DTSI | `periodo_I` -> data | Data de inicio (negativo para a.C.) |
| DTSF | `periodo_II` -> data | Data de fim |
| PRVN | `nazione` | Nacao |
| PVCR | `regione` | Regiao |
| PVCP | `provincia` | Provincia |
| PVCC | `comune` | Municipio |
| LCDQ | `quota` | Elevacao |

### Classificacao VRP (Potencial)

| Intervalo | Codigo GNA | Etiqueta | Cor |
|-----------|-----------|----------|-----|
| 0-20 | NV | Nao avaliavel | Cinzento |
| 20-40 | NU | Nenhum | Verde |
| 40-60 | BA | Baixo | Amarelo |
| 60-80 | ME | Medio | Laranja |
| 80-100 | AL | Elevado | Vermelho |

### Classificacao VRD (Risco)

| Intervalo | Codigo GNA | Etiqueta | Cor |
|-----------|-----------|----------|-----|
| 0-25 | NU | Nenhum | Verde |
| 25-50 | BA | Baixo | Amarelo |
| 50-75 | ME | Medio | Laranja |
| 75-100 | AL | Elevado | Vermelho |

### Procedimento de Exportacao GNA

1. **Preparacao dos dados:**
   - Verificar que todas as UT tem coordenadas
   - Calcular pontuacoes de potencial/risco
   - Preparar poligono da area do projeto (MOPR)

2. **Iniciar exportacao:**
   - A partir do formulario UT, clicar em **Exportacao GNA**
   - Ou menu **PyArchInit** > **GNA** > **Exportar**

3. **Configuracao:**
   ```
   Projeto: [selecionar projeto]
   Area do projeto: [selecionar camada de poligono MOPR]
   Saida: [caminho do ficheiro .gpkg]

   [x] Exportar MOSI (sitios)
   [x] Gerar VRP (potencial)
   [x] Gerar VRD (risco)

   Metodo de mapa de calor: KDE
   Tamanho da celula: 50 m
   ```

4. **Execucao:**
   - Clicar em **Exportar**
   - Aguardar a geracao (pode demorar varios minutos)
   - O GeoPackage e guardado no caminho especificado

5. **Verificar resultado:**
   - Abrir o GeoPackage no QGIS
   - Verificar camadas MOPR, MOSI, VRP, VRD
   - Confirmar que as geometrias VRP/VRD estao cortadas pelo MOPR

### Validacao GNA

Para validar o resultado face as especificacoes GNA:

1. Carregar o GeoPackage no **modelo oficial GNA**
2. Verificar que as camadas sao reconhecidas
3. Verificar vocabularios controlados
4. Verificar relacoes geometricas (MOSI dentro de MOPR)

---

## Exportacao PDF

### Ficha UT Individual

Exporta a ficha completa da UT em formato PDF profissional.

**Conteudo:**
- Cabecalho com projeto e numero da UT
- Seccao de Identificacao
- Seccao de Localizacao
- Seccao de Terreno
- Seccao de Dados da Prospeccao
- Seccao de Cronologia
- Seccao de Analise (potencial/risco com barras coloridas)
- Seccao de Documentacao

**Procedimento:**
1. Selecionar o registo UT
2. Clicar no botao **PDF** na barra de ferramentas
3. O PDF e guardado em `pyarchinit_PDF_folder`

### Lista de UT (Lista PDF)

Exporta uma lista tabular de todas as UT em formato paisagem.

**Colunas:**
- UT, Projeto, Definicao, Interpretacao
- Municipio, Coordenadas, Periodo I, Periodo II
- Achados/m2, Visibilidade, Potencial, Risco

**Procedimento:**
1. Carregar as UT a exportar (pesquisar ou ver todas)
2. Clicar no botao **Lista PDF** na barra de ferramentas
3. O PDF e guardado como `UT_List.pdf`

### Relatorio de Analise UT

Gera um relatorio detalhado de analise de potencial/risco.

**Conteudo:**
1. Dados de identificacao da UT
2. Seccao de Potencial Arqueologico
   - Pontuacao com indicador grafico
   - Texto narrativo descritivo
   - Tabela de fatores com contribuicoes
3. Seccao de Risco Arqueologico
   - Pontuacao com indicador grafico
   - Texto narrativo com recomendacoes
   - Tabela de fatores com contribuicoes
4. Seccao de Metodologia

---

## Fluxo de Trabalho Operacional Completo

### Fase 1: Configuracao do Projeto

1. **Criar novo projeto** no PyArchInit ou utilizar um existente
2. **Definir area de estudo** (poligono MOPR)
3. **Configurar SRC** do projeto QGIS

### Fase 2: Registo de UT no Campo

1. **Abrir formulario UT**
2. **Novo registo** (clicar em "Novo Registo")
3. **Preencher dados de identificacao:**
   ```
   Projeto: Prospeccao Vale do Tejo 2024
   N.o UT: 25
   ```

4. **Preencher localizacao:**
   ```
   Regiao: Lisboa
   Provincia: Lisboa
   Municipio: Vila Franca de Xira
   Localidade: Monte Alto
   Coord. geograficas: 38.9234, -8.9678
   Altitude: 125 m
   Precisao GPS: 3 m
   ```

5. **Preencher descricao** (utilizando thesaurus):
   ```
   Definicao: Concentracao de achados
   Descricao: Area eliptica de aprox. 50x30 m
   com concentracao de fragmentos ceramicos
   e telhas em encosta virada a sul...
   ```

6. **Preencher dados da prospeccao** (utilizando thesaurus):
   ```
   Tipo de Prospeccao: Prospeccao intensiva
   Cobertura Vegetal: Esparsa
   Metodo GPS: GPS diferencial
   Condicao da Superficie: Lavrado
   Acessibilidade: Acesso facil
   Condicoes Meteorologicas: Sol
   Visibilidade: 80%
   Data: 15/04/2024
   Responsavel: Equipa A
   ```

7. **Preencher materiais e cronologia:**
   ```
   Dimensoes: 1500 m2
   Achados/m2: 5-8
   Achados datantes: Ceramica comum,
   sigillata italica, telhas

   Periodo I: Romano
   Datacao I: sec. I-II d.C.
   Interpretacao I: Villa rustica
   ```

8. **Guardar** (clicar em "Guardar")

### Fase 3: Criacao de Geometria

1. **Carregar camada** `pyarchinit_ut_polygon`
2. **Ativar edicao**
3. **Desenhar** o perimetro da UT no mapa
4. **Preencher atributos**: progetto, nr_ut
5. **Guardar** a camada

### Fase 4: Analise

1. **Abrir separador Analise** no formulario UT
2. **Verificar** pontuacoes calculadas automaticamente
3. **Gerar mapa de calor** se necessario
4. **Exportar relatorio PDF** da analise

### Fase 5: Exportacao GNA (se necessario)

1. **Verificar completude dos dados** de todas as UT
2. **Preparar poligono MOPR** da area do projeto
3. **Executar Exportacao GNA**
4. **Validar resultado** face as especificacoes GNA

---

## Dicas e Sugestoes

### Otimizacao do Fluxo de Trabalho

1. **Pre-preencher thesauri** antes de iniciar prospeccoes
2. **Utilizar modelos de projeto** com dados comuns predefinidos
3. **Sincronizar coordenadas** do GPS para o campo `coord_geografiche`
4. **Guardar frequentemente** durante a entrada de dados

### Melhorar a Qualidade dos Dados

1. **Preencher TODOS os campos relevantes** para cada UT
2. **Utilizar sempre thesauri** em vez de texto livre
3. **Verificar coordenadas** no mapa antes de guardar
4. **Documentar fotograficamente** cada UT

### Otimizacao de Mapas de Calor

1. **Tamanho de celula adequado**: utilizar 25-50m para areas pequenas, 100-200m para areas extensas
2. **Metodo KDE** para distribuicoes continuas e homogeneas
3. **Metodo IDW** quando os valores pontuais sao criticos
4. **Verificar sempre** que as coordenadas estao corretas antes de gerar

### Exportacao GNA Eficiente

1. **Preparar poligono MOPR** antecipadamente como camada separada
2. **Verificar que todas as UT** tem coordenadas validas
3. **Calcular pontuacoes** antes da exportacao
4. **Utilizar nomes descritivos** para os GeoPackages

### Gestao Multiutilizador

1. **Definir convencoes de nomenclatura partilhadas** para numeracao de UT
2. **Utilizar base de dados PostgreSQL** para acesso concorrente
3. **Sincronizar dados periodicamente**
4. **Documentar alteracoes** nos campos de notas

---

## Resolucao de Problemas

### Problema: Caixas combinadas do Thesaurus Vazias

**Sintomas:** As listas pendentes para survey_type, vegetacao, etc. estao vazias.

**Causas:**
- Entradas do thesaurus nao presentes na base de dados
- Codigo de idioma errado
- Tabela do thesaurus nao atualizada

**Solucoes:**
1. Menu **PyArchInit** > **Base de Dados** > **Atualizar base de dados**
2. Verificar tabela `pyarchinit_thesaurus_sigle` para entradas de `ut_table`
3. Verificar definicoes de idioma
4. Se necessario, reimportar thesauri a partir do modelo

### Problema: Coordenadas Invalidas

**Sintomas:** Erro ao guardar ou coordenadas apresentadas em posicao errada.

**Causas:**
- Formato errado (virgula vs ponto decimal)
- Sistema de coordenadas nao coincidente
- Ordem lat/lon invertida

**Solucoes:**
1. Formato correto para `coord_geografiche`: `42.1234, 12.5678` (lat, lon)
2. Formato correto para `coord_piane`: `1234567.89, 4567890.12` (x, y)
3. Utilizar sempre ponto como separador decimal
4. Verificar SRC do projeto QGIS

### Problema: UT Nao Visivel no Mapa

**Sintomas:** Apos guardar, a UT nao aparece no mapa.

**Causas:**
- Geometria nao criada na camada
- Atributos `progetto`/`nr_ut` nao coincidem
- Camada nao carregada ou oculta
- SRC diferente entre camada e projeto

**Solucoes:**
1. Verificar que a camada `pyarchinit_ut_point/polygon` existe
2. Confirmar que os atributos estao corretamente preenchidos
3. Ativar visibilidade da camada no painel de Camadas
4. Utilizar "Ampliar para Camada" para verificar a extensao

### Problema: Mapa de Calor Nao Gerado

**Sintomas:** Erro "Sao necessarios pelo menos 2 pontos com coordenadas validas".

**Causas:**
- Menos de 2 UT com coordenadas
- Coordenadas em formato errado
- Campos de coordenadas vazios

**Solucoes:**
1. Verificar que pelo menos 2 UT tem `coord_geografiche` OU `coord_piane` preenchidos
2. Verificar formato das coordenadas (ponto decimal, ordem correta)
3. Recalcular pontuacoes antes de gerar o mapa de calor
4. Verificar que os campos nao contem caracteres especiais

### Problema: Pontuacao de Potencial/Risco Nao Calculada

**Sintomas:** Os campos potential_score e risk_score estao vazios ou a zero.

**Causas:**
- Campos obrigatorios nao preenchidos
- Valores do thesaurus nao reconhecidos
- Erro de calculo

**Solucoes:**
1. Preencher pelo menos: `def_ut`, `periodo_I`, `visibility_percent`
2. Utilizar valores do thesaurus (nao texto livre)
3. Guardar o registo e reabrir
4. Verificar registos do QGIS para erros

### Problema: Exportacao GNA Falhou

**Sintomas:** GeoPackage nao criado ou incompleto.

**Causas:**
- Modulo GNA nao disponivel
- Dados UT incompletos
- Poligono MOPR invalido
- Permissoes de escrita insuficientes

**Solucoes:**
1. Verificar que o modulo `modules/gna` esta instalado
2. Confirmar que todas as UT tem coordenadas validas
3. Verificar que o poligono MOPR e valido (sem auto-intersecoes)
4. Verificar permissoes na pasta de saida
5. Verificar espaco em disco suficiente

### Problema: Exportacao PDF com Campos em Falta

**Sintomas:** O PDF gerado nao mostra alguns campos ou mostra valores errados.

**Causas:**
- Campos da base de dados nao atualizados
- Versao do esquema da base de dados obsoleta
- Dados nao guardados antes da exportacao

**Solucoes:**
1. Guardar o registo antes de exportar
2. Atualizar a base de dados se necessario
3. Verificar que os novos campos (v4.9.67+) existem na tabela

### Problema: Erro Qt6/QGIS 4.x

**Sintomas:** O plugin nao carrega no QGIS 4.x com erro `AllDockWidgetFeatures`.

**Causas:**
- Incompatibilidade Qt5/Qt6
- Ficheiro UI nao atualizado

**Solucoes:**
1. Atualizar o PyArchInit para a versao mais recente
2. O ficheiro `UT_ui.ui` deve utilizar flags explicitas em vez de `AllDockWidgetFeatures`

---

## Referencias

### Base de Dados

- **Tabela**: `ut_table`
- **Classe mapper**: `UT`
- **ID**: `id_ut`

### Tabelas de Geometria

- **Pontos**: `pyarchinit_ut_point`
- **Linhas**: `pyarchinit_ut_line`
- **Poligonos**: `pyarchinit_ut_polygon`

### Ficheiros Fonte

| Ficheiro | Descricao |
|----------|-----------|
| `gui/ui/UT_ui.ui` | Interface de utilizador Qt |
| `tabs/UT.py` | Controlador principal |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | Exportacao de ficha PDF |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | Exportacao de analise PDF |
| `modules/analysis/ut_potential.py` | Calculo de potencial |
| `modules/analysis/ut_risk.py` | Calculo de risco |
| `modules/analysis/ut_heatmap_generator.py` | Geracao de mapa de calor |
| `modules/gna/gna_exporter.py` | Exportacao GNA |
| `modules/gna/gna_vocabulary_mapper.py` | Mapeamento de vocabulario GNA |

### Codigos do Thesaurus UT

| Codigo | Campo | Descricao |
|--------|-------|-----------|
| 12.1 | survey_type | Tipo de prospeccao |
| 12.2 | vegetation_coverage | Cobertura vegetal |
| 12.3 | gps_method | Metodo GPS |
| 12.4 | surface_condition | Condicao da superficie |
| 12.5 | accessibility | Acessibilidade |
| 12.6 | weather_conditions | Condicoes meteorologicas |
| 12.7 | def_ut | Definicao da UT |

---

## Tutoriais em Video

### Documentacao de Prospeccao
**Duracao**: 15-18 minutos
- Registo de UT
- Dados de prospeccao com thesaurus
- Geolocalizacao

### Analise de Potencial e Risco
**Duracao**: 10-12 minutos
- Calculo automatico de pontuacoes
- Interpretacao de resultados
- Geracao de mapas de calor

### Exportacao GNA
**Duracao**: 12-15 minutos
- Preparacao de dados
- Configuracao da exportacao
- Validacao do resultado

### Exportacao de Relatorio PDF
**Duracao**: 8-10 minutos
- Ficha UT padrao
- Lista de UT
- Relatorio de analise com mapas

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit v4.9.68 - Sistema de Gestao de Dados Arqueologicos*
