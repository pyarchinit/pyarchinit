# Tutorial 14: GIS e Cartografia

## Introdução

O PyArchInit está profundamente integrado com o **QGIS**, aproveitando todas as suas funcionalidades GIS para a gestão espacial de dados arqueológicos. Este tutorial abrange a integração cartográfica, as camadas predefinidas e funcionalidades avançadas como a **segmentação automática SAM**.

### Funcionalidades GIS Principais

- Visualização de UEs no mapa
- Camadas vetoriais predefinidas
- Estilização QML personalizada
- Cotas e medições GIS
- Segmentação automática (SAM)
- Exportação cartográfica

## Camadas Predefinidas do PyArchInit

### Camadas Vetoriais Principais

| Camada | Geometria | Descrição |
|--------|-----------|-----------|
| `pyunitastratigrafiche` | MultiPolygon | UE depósito |
| `pyunitastratigrafiche_usm` | MultiPolygon | UE muro |
| `pyarchinit_quote` | Point | Pontos de cota |
| `pyarchinit_siti` | Point | Localização de sítios |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Áreas de escavação |
| `pyarchinit_strutture_ipotesi` | Polygon | Estruturas hipotéticas |
| `pyarchinit_documentazione` | Point | Referências de documentação |

### Atributos da Camada UE

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `gid` | Integer | ID único |
| `scavo_s` | Text | Nome do sítio |
| `area_s` | Text | Número da área |
| `us_s` | Text | Número da UE |
| `stratigraph_index_us` | Integer | Índice estratigráfico |
| `tipo_us_s` | Text | Tipo de UE |
| `rilievo_originale` | Text | Levantamento original |
| `disegnatore` | Text | Autor do levantamento |
| `data` | Date | Data do levantamento |

## Visualização de UEs no Mapa

### A partir do Separador "Mapa" na Ficha UE

1. Abra uma ficha UE
2. Selecione o separador **Mapa**
3. Funções disponíveis:

| Botão | Função |
|-------|--------|
| Ver UE | Exibir a UE atual no mapa |
| Ver Todas | Exibir todas as UEs da área |
| Novo Registo | Criar nova geometria |
| Centrar em | Centrar o mapa na UE |

### Visualização a partir da Pesquisa

1. Execute uma pesquisa de UE
2. Botão **"Ver Registo"** → exibição individual
3. Botão **"Ver Todas"** → exibição de todos os resultados

### Escolha do Estilo (UE e USM)

Quando as UEs ou as UEs de muro (USM) dos resultados da pesquisa são carregadas no mapa, aparece a janela **Style Choice** ("How do you want to manage the layer style?"). Os botões são apresentados em inglês:

| Botão | Efeito |
|-------|--------|
| **Save new style** | Cria o estilo com base no campo escolhido e guarda-o na base de dados com um nome |
| **Load existing style** | Usa como modelo um estilo já pronto, escolhido de uma lista (ver abaixo), e cria o estilo com base no campo escolhido sem o guardar na base de dados |
| **Use temporary style** | Cria o estilo com base no campo escolhido sem o guardar na base de dados |
| **Single symbol (outline only)** | Desenha apenas o contorno das geometrias, sem preenchimento |

Desde a 5.13.19-alpha, **Load existing style** abre a janela **Existing style** ("Choose the style to use as a template:", em inglês) com a lista dos estilos disponíveis: os estilos guardados na base de dados (*Database: nome*), os estilos QML fornecidos com o pyArchInit (`us_*.qml`, listados como *pyArchInit: …*) e **Other QML file…**, para escolher qualquer ficheiro `.qml`. O estilo escolhido é carregado na camada (a transparência e o modo de mistura vêm com ele, as etiquetas não: nas vistas US e USM de polígonos são, desde a 5.13.110-alpha, as do parágrafo **Etiquetas** mais abaixo, o número da unidade em círculo, diga o que disser o estilo modelo) e serve de **modelo**: depois de escolher o campo de categorização, os valores que o estilo já tem mantêm a sua cor e o seu símbolo, os outros recebem uma cópia do seu símbolo com uma cor própria. Se a escolha for cancelada, funciona como **Use temporary style**. Antes procurava apenas entre os estilos da base de dados e, não encontrando nenhum, passava diretamente à janela de categorização.

Com **Save new style**, **Load existing style** e **Use temporary style** escolhe-se depois o campo de categorização (janela **Select Categorization Field**, em inglês): **Stratigraphic Definition** (definição estratigráfica), **SU Type** (tipo de UE), **Interpretive Definition** (definição interpretativa) ou **Period/Phase (cont_per)** (período/fase, desde a 5.13.19-alpha); cada valor do campo recebe uma cor própria, que desde a 5.13.19-alpha é a mesma sempre que a camada é carregada. Com **Period/Phase (cont_per)** a entrada da legenda de cada código mostra também a datação do período/fase retirada da periodização. Só aparecem os campos presentes na camada.

**Ordem de desenho.** Desde a 5.13.19-alpha as unidades são desenhadas pela ordem usada pelo Time Manager: primeiro as que não têm período, depois pela cronologia do período (a partir da periodização do período/fase inicial da UE, ou do `cont_per`), depois pelo `order_layer` (0 = mais antiga) e, por fim, o corte por cima do seu enchimento, de modo que as unidades mais recentes ficam por cima. Aplica-se a todas as opções de estilo, incluindo **Single symbol (outline only)**. Quando as camadas são carregadas período a período, o estilo é pedido uma única vez e usado para todos os períodos.

**Etiquetas.** Desde a 5.13.110-alpha, com o estilo escolhido a vista US (e USM) recebe também as suas **etiquetas**: o número da unidade em **negrito dentro de um círculo branco com contorno vermelho escuro**, **uma por unidade**, no seu desenho maior se se vir (não coberto por inteiro por um de nível superior), com a mesma receita das pranchas do atlas do Time Manager (tutorial 25). Quando dois números se tapariam, um é deslocado e uma linha de chamada liga-o ao seu desenho. Aplica-se às UE e às USM, com SQLite e com PostgreSQL, e a todas as opções de estilo, incluindo **Single symbol (outline only)**; se o estilo carregado com **Load existing style** já tinha etiquetas, o número em círculo toma o lugar delas. As camadas de pontos não recebem o número em círculo. Desde a 5.13.111-alpha, porém, a **vista das cotas** (os pontos de cota, camada «Elevation view»), logo que é carregada a partir da ficha UE, traz a **etiqueta com o valor da cota** (duas casas decimais, por exemplo «12,35»), colocada **acima da linha horizontal do símbolo**, com a mesma receita das pranchas do atlas do Time Manager. Aplica-se a todas as opções que a carregam, com SQLite e com PostgreSQL, e não depende do estilo escolhido; as camadas que não são de pontos, ou que não têm o campo da cota, não recebem esta etiqueta.

Desde a 5.13.18-alpha o estilo escolhido (e o campo de categorização) é respeitado também com as bases de dados SQLite, tanto para as UEs como para as USM; antes o mapa saía sempre com uma cor para cada UE.

## Estilização de Camadas

### Ficheiros QML

O PyArchInit inclui estilos predefinidos em formato QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicação do Estilo

1. Selecione a camada na legenda
2. Clique direito → **Propriedades**
3. Separador **Estilo**
4. **Carregar estilo** → selecione QML

### Personalização

Os estilos podem ser personalizados para:
- Cores baseadas no tipo de UE
- Rótulos com número da UE
- Transparência
- Bordas e preenchimentos

## Cotas e Medições

### Camada de Cotas

A camada `pyarchinit_quote` armazena:
- Coordenadas X, Y
- Cota Z (absoluta)
- Tipo de ponto de cota
- UE de referência
- Área de referência

### Cálculo Automático de Cotas

A partir da Ficha UE, as cotas min/max são calculadas:
1. Consulta dos pontos de cota associados à UE
2. Extração do valor mínimo e máximo
3. Exibição no relatório

### Introdução de Cotas

1. Camada de cotas em modo de edição
2. Desenhe um ponto no mapa
3. Preencha os atributos:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentação Automática SAM

### O que é o SAM?

O **SAM (Segment Anything Model)** é o modelo de inteligência artificial da Meta que divide uma imagem nos seus objetos. No pyArchInit, a janela SAM transforma uma imagem em **polígonos**, a partir de:

- uma **ortofotografia** (um ficheiro raster: GeoTIFF, JPEG georreferenciado…);
- ou uma **camada de tiles (mosaicos) ou um serviço** carregado no QGIS: XYZ como ESRI World Imagery ou Google, WMS, ArcGIS REST.

Não só pedras: também **edifícios, estradas, campos, rios, muros**. Os modelos são de duas famílias:

- o **SAM 2.1** (Meta) encontra os contornos dos objetos — todos, ou os que se indicam com pontos, uma caixa ou um polígono —, mas não diz o que são;
- as **classes de texto** (YOLOE-26 em local, SAM 3 na nuvem) procuram aquilo que se escreve («building, road, river, field») e cada polígono leva a sua etiqueta.

Os polígonos vão para a camada escolhida: as camadas de UE do pyArchInit, qualquer camada de polígonos do projeto ou uma camada temporária nova.

### Aceder à Função

1. Na barra de ferramentas do pyArchInit: botão suspenso **Ferramentas de análise** (Analysis Tools) → «SAM - Segmentation (stones, buildings, roads, fields…)». É a ação predefinida do botão: um clique no ícone abre logo a janela.
2. Ou no menu **pyArchInit** → «SAM - Segmentation (stones, buildings, roads, fields…)».

A janela intitula-se «SAM — Segmentation (stones, buildings, roads, fields, rivers…)». As suas etiquetas só existem em italiano e em inglês: com o QGIS em português aparece em inglês, como no esquema. A seguir, cada etiqueta traduzida é seguida da inglesa entre parênteses.

### Interface SAM

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Cinco grupos, a preencher de cima para baixo: «Ambiente local» (*Local environment*), «Imagem» (*Image*), «O que segmentar» (*What to segment*), «Modelo» (*Model*), «Destino» (*Target*). Por baixo ficam a linha de estado («Pronto», *Ready*), onde aparecem também as mensagens do trabalho em curso, e os botões «Iniciar» (*Start*), «Cancelar» (*Cancel*, visível só durante o trabalho) e «Fechar» (*Close*). Algumas linhas só aparecem quando são precisas: «Chave API:» (*API key:*) em vez do estado dos pesos para os modelos na nuvem; «Sítio:» (*Site:*), «Área:» (*Area:*), «Índice estratigráfico:» (*Stratigraphic index:*) e «Tipo de UE:» (*US type:*) para as camadas de UE; «Campo para a etiqueta:» (*Field for the label:*) para as outras camadas. A janela memoriza a última área de UE, as classes, o lado máximo, o modelo escolhido e as chaves API.

As entradas da lista de modelos estão sempre escritas em italiano («Locale» = local), tal como algumas mensagens de serviço citadas mais abaixo.

#### Ambiente local

Os modelos locais (SAM 2.1 e YOLOE) não correm no Python do QGIS, mas num **Python separado**, que a janela cria e verifica sozinha. Ao abrir, o grupo mostra «a verificar…» (*checking…*) e depois:

- a verde «pronto — ultralytics …, torch …, mps» (*ready — …*): o ambiente existe; a última palavra é o dispositivo de cálculo (`mps`, `cuda` ou `cpu`);
- a laranja «não instalado: necessário para os modelos locais (SAM 2.1, YOLOE). Um Python do sistema 3.10–3.13, ~1,5 GB de pacotes.» (*not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.*).

«Instalar / atualizar» (*Install / update*) cria o ambiente ou atualiza os seus pacotes (ver mais abaixo «Instalação Local do SAM»); «Mostrar registo» (*Show log*) abre e fecha o registo da instalação, com a saída do pip linha a linha. Os modelos na nuvem não precisam do ambiente.

#### Imagem

- «Camada raster:» (*Raster layer:*): a imagem a segmentar, escolhida entre os rasters do projeto: uma ortofotografia (ficheiro) ou uma camada de tiles/serviço. Por baixo, a cinzento, indica-se qual das duas é: nome do ficheiro e dimensões em píxeis (`orthophoto.tif — 12000 × 9000 px`) ou o tipo de serviço, renderizado a partir da vista (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)`; esta linha está em italiano, *reso dalla vista* = renderizado a partir da vista).
- «Extensão:» (*Area:*): «vista atual» (*current view*, o que se vê no mapa) ou «raster inteiro» (*whole raster*). «raster inteiro» só pode ser escolhido para ficheiros: um serviço de tiles não tem limite, por isso trabalha-se sempre sobre a vista (ou sobre uma caixa ou um polígono).
- «Resolução (unidades de mapa/px):» (*Resolution (map units/px):*): só para tiles: quantas unidades de mapa (metros, ou graus se o mapa estiver em coordenadas geográficas) por cada píxel da imagem renderizada. O valor proposto é o da vista ao abrir a janela ou ao escolher a camada: se depois mudar o zoom, corrija-o à mão. Quanto mais pequeno, mais pormenor.
- «Lado máximo (px):» (*Max side (px):*): o lado mais comprido da imagem passada ao modelo: 2048 por omissão, de 512 a 8192. Acima desse lado a imagem é reduzida; o SAM trabalha de qualquer forma a 1024 px internos.

### Modos de Segmentação

O grupo «O que segmentar» (*What to segment*) oferece seis modos. Ao escolher um modo, muda a lista de modelos (ver «Modelos Disponíveis») e aparece por baixo, a azul, a instrução desse modo.

#### 1. Tudo automático

«Tudo (automático)» (*Everything (automatic)*): o SAM 2.1 segmenta cada objeto que encontra na «Extensão:» escolhida («vista atual» ou «raster inteiro»). Os polígonos não têm classe: na camada temporária recebem a etiqueta «segment». Arranca-se com «Iniciar» (*Start*).

#### 2. Pontos

«Pontos: clique nos objetos do mapa» (*Points: click the objects on the map*): clicar em «Iniciar seleção» (*Start selection*); a janela esconde-se e a barra de mensagens do QGIS lembra os comandos. Clicar nos objetos um a um: cada clique é um objeto. Clique direito ou Enter para terminar, Retrocesso (Backspace) retira o último ponto, Esc cancela. A janela volta a aparecer e a segmentação corre sobre a «Extensão:» escolhida, um objeto por ponto; os pontos fora da imagem são ignorados.

#### 3. Caixa

«Caixa: desenhe um retângulo» (*Box: draw a rectangle*): clicar em «Iniciar seleção» e arrastar um retângulo no mapa (Esc ou clique direito cancela). A imagem é recortada pelo retângulo e tudo o que está lá dentro é segmentado.

#### 4. Polígono

«Polígono: desenhe a área» (*Polygon: draw the area*): clicar em «Iniciar seleção» e clicar nos vértices; clique direito, Enter ou duplo clique fecham o polígono (são precisos pelo menos três vértices), Retrocesso retira o último vértice, Esc cancela. Só o interior do polígono é segmentado.

#### 5. Polígono a partir de camada

«Polígono a partir de camada:» (*Polygon from layer:*): escolher uma camada de polígonos na lista suspensa ao lado. Usa-se o elemento selecionado da camada, ou todos se nenhum estiver selecionado (vários elementos são unidos num só). Tal como no polígono desenhado, só o interior é segmentado: útil para trabalhar dentro de uma sondagem, de uma área de escavação ou de um limite já desenhado. Arranca-se com «Iniciar».

#### 6. Classes de texto

«Classes de texto:» (*Text classes:*): escrever no campo ao lado o que procurar: palavras em **inglês** separadas por vírgulas (por omissão «building, road, river, field»; outros exemplos: stone, wall). Cada classe torna-se uma etiqueta dos polígonos. Funciona com o YOLOE-26 em local ou com o SAM 3 da Roboflow na nuvem, sobre a «Extensão:» escolhida. Arranca-se com «Iniciar».

**«Limiar:»** (*Threshold:*; 0,30 por omissão, de 0,05 a 0,95) é a confiança mínima para que um resultado seja mantido: mais baixo dá mais polígonos, incluindo incertos; mais alto dá menos, mas mais seguros. O modelo na nuvem da Replicate não o usa.

### Modelos Disponíveis

O grupo «Modelo» (*Model*) tem uma lista suspensa «Modelo:» (*Model:*) cujo conteúdo depende do modo escolhido:

| Modelo | Tipo | Requisitos | Modos |
|--------|------|------------|-------|
| SAM 2.1 Tiny | Local | ambiente local + pesos ~78 MB | todos exceto as classes de texto; o mais leve e rápido |
| SAM 2.1 Small | Local | ambiente local + pesos ~92 MB | todos exceto as classes de texto |
| SAM 2.1 Base+ | Local | ambiente local + pesos ~162 MB | todos exceto as classes de texto |
| SAM 2.1 Large | Local | ambiente local + pesos ~449 MB | todos exceto as classes de texto; o mais preciso e o mais lento |
| Cloud: Replicate SAM-2 | Nuvem | chave API da Replicate | só segmentação automática (no modo «Pontos» os cliques são ignorados, com um aviso) |
| YOLOE-26 S | Local | ambiente local + pesos ~31 MB + MobileCLIP2 254 MB (uma vez) | classes de texto |
| YOLOE-26 M | Local | ambiente local + pesos ~70 MB + MobileCLIP2 254 MB (uma vez) | classes de texto |
| YOLOE-26 L | Local | ambiente local + pesos ~79 MB + MobileCLIP2 254 MB (uma vez) | classes de texto |
| Cloud: Roboflow SAM 3 | Nuvem | chave API da Roboflow | classes de texto |

Na lista suspensa, as entradas leem-se assim: «Locale: SAM 2.1 Tiny — ~78 MB», «Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB», «Cloud: Replicate SAM-2 (solo automatico, chiave API)», «Cloud: Roboflow SAM 3 (classi a testo, chiave API)» (*locale* = local, *classi a testo* = classes de texto, *solo automatico* = só automático, *chiave* = chave).

**Pesos.** Para um modelo local, por baixo da lista aparece o estado dos pesos: «pesos presentes ✓» (*weights present ✓*, verde) ou «pesos em falta (~N MB)» (*weights missing (~N MB)*, laranja), com o botão «Descarregar pesos» (*Download weights*). A transferência, com barra de progresso, vai buscar os ficheiros aos recursos públicos da ultralytics no GitHub (não é precisa conta). Para o YOLOE descarrega-se também o codificador de texto MobileCLIP2 (254 MB), uma só vez para S, M e L. Os pesos ficam em `~/pyarchinit_5/bin/models/sam/`.

**Chave API.** Para um modelo na nuvem, o campo «Chave API:» (*API key:*) e a ligação para a obter substituem o estado dos pesos (ver «Configuração da API»).

### SAM-3 com Prompt de Texto

Com o modo «Classes de texto» não se pede «divide tudo», mas «encontra estas coisas»:

- escrevem-se uma ou mais classes em inglês, separadas por vírgulas: `building, road, river, field`, ou `stone, wall`…;
- o **YOLOE-26** (local, S/M/L) entende as palavras graças ao codificador de texto MobileCLIP2; o **SAM 3** da Roboflow (nuvem) recebe as mesmas classes como prompts de texto (no máximo 16);
- cada polígono leva a classe que o encontrou: na camada temporária, no campo `label`; numa camada própria, no «Campo para a etiqueta:» (*Field for the label:*). Nas camadas de UE do pyArchInit a classe não é escrita.

O SAM 2.1 em «Tudo (automático)», pelo contrário, não atribui classes: encontra contornos, não nomes.

### Configuração da API

As chaves só são precisas para os modelos na nuvem. Escolher o modelo na nuvem na lista, colar a chave no campo «Chave API:» (*API key:*; o texto fica oculto) e clicar em «Iniciar»: a chave é guardada nas definições do QGIS e proposta de novo da vez seguinte. Com os modelos na nuvem, a imagem preparada é enviada ao serviço.

#### API Replicate (SAM-2)
1. Criar uma conta em [replicate.com](https://replicate.com)
2. Criar um token em [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) (a ligação «Chave Replicate» (*Replicate key*) ao lado do campo abre a mesma página)
3. Colá-lo em «Chave API:» com o modelo «Cloud: Replicate SAM-2»

#### API Roboflow (SAM-3)
1. Criar uma conta em [roboflow.com](https://roboflow.com)
2. Copiar a chave em [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) (ligação «Chave Roboflow» (*Roboflow key*) ao lado do campo)
3. Colá-la em «Chave API:» com o modelo «Cloud: Roboflow SAM 3»

### Instalação Local do SAM

Não é preciso nenhum comando no terminal: o ambiente dos modelos locais instala-se a partir da janela.

1. É preciso um **Python do sistema 3.10–3.13**: os pacotes não são instalados no Python do QGIS, para não correr o risco de o estragar. A janela procura-o sozinha: no **macOS** o Python de [python.org](https://www.python.org/downloads/) ou do Homebrew, no **Windows** o lançador `py` do Python de python.org, no **Linux** `python3.10`…`python3.13` ou o `python3` do sistema.
2. Clicar em «Instalar / atualizar» (*Install / update*) no grupo «Ambiente local»: é criado o ambiente virtual `~/pyarchinit_5/bin/sam_venv` e nele são instalados o `ultralytics` (que traz torch, torchvision, OpenCV, numpy) e o `requests`: cerca de **1,5 GB** de pacotes, uma só vez. Em Linux sem placa NVIDIA é instalado o torch para CPU, muito mais leve.
3. «Mostrar registo» (*Show log*) mostra o pip a trabalhar. No fim, o estado fica verde: «pronto — ultralytics …, torch …, mps».
4. Descarregar os pesos do modelo que se quer usar com «Descarregar pesos» (*Download weights*, grupo «Modelo»).

Clicando de novo em «Instalar / atualizar», os pacotes são atualizados. O dispositivo de cálculo é escolhido sozinho: **MPS** nos Mac com Apple Silicon, **CUDA** com uma placa NVIDIA e, caso contrário, **CPU** (funciona, mas é mais lento). Se o MPS ou o CUDA falharem, o trabalho recomeça sozinho no CPU.

| O quê | Onde |
|-------|------|
| Ambiente Python | `~/pyarchinit_5/bin/sam_venv` |
| Pesos dos modelos | `~/pyarchinit_5/bin/models/sam/` |
| Chaves API | definições do QGIS |

`~/pyarchinit_5` é a pasta de dados do pyArchInit (ou a indicada pela variável `PYARCHINIT_HOME`).

### Destino e Atributos

O grupo «Destino» (*Target*) decide para onde vão os polígonos. A lista «Camada:» (*Layer:*) contém as camadas de polígonos do projeto e «— nova camada temporária —» (*— new temporary layer —*); se `pyunitastratigrafiche` estiver carregada, é essa a proposta.

| Destino | O que é escrito |
|---------|-----------------|
| «— nova camada temporária —» | uma camada em memória `SAM_<raster>_<data_hora>`, no SRC da imagem, com os campos `label` (a classe, ou «segment»), `score` (confiança), `area`, `source` (o modelo) e `created` (data e hora) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = «Sítio:» (*Site:*; da configuração, não editável), `area_s` = «Área:» (*Area:*; obrigatória), `stratigraph_index_us` = «Índice estratigráfico:» (*Stratigraphic index:*; 1 = pedras/objetos, 2 = estrato/superfície), `tipo_us_s` = «Tipo de UE:» (*US type:*; pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <modelo>` (p. ex. `SAM sam2.1_t.pt`), `data` = hoje; `us_s` fica vazio |
| outra camada de polígonos | a classe no «Campo para a etiqueta:» (*Field for the label:*), um campo de texto (é proposto `label`, `etichetta`, `classe`, `class`, `tipo` ou `nome`, se existir; vazio = não escrever); se a camada tiver campos `score`, `area`, `source` ou `created`, também são preenchidos |

- Nas camadas de UE, o número de UE atribui-se depois, na tabela de atributos; a mensagem final lembra-o: «Atribua depois os números de UE na tabela de atributos.» (*Then assign the US numbers in the attribute table.*).
- Os polígonos são reprojetados para o SRC da camada de destino e gravados nela de imediato (se a camada já estava em edição, as suas alterações pendentes também são gravadas).
- A camada temporária só dura até ao fecho do QGIS: para a manter, exportá-la para um ficheiro (clique direito na camada → Exportar).

### Como Funciona

1. **A imagem.** Num ficheiro, a extensão é recortada e, se necessário, reduzida com GDAL: os píxeis são os reais do ficheiro, não os desenhados no mapa (o estilo da camada não conta; os rasters que não são de 8 bits são reescalados para 0–255). Os tiles e os serviços não têm ficheiro: o QGIS renderiza a vista com o seu próprio motor de desenho, à resolução escolhida — só essa camada, sem as outras camadas do mapa —, e é essa renderização que é segmentada.
2. **A área.** Com um polígono (desenhado ou a partir de camada) toma-se o retângulo que o contém, pinta-se de branco tudo o que fica fora e, no fim, os resultados são recortados pelo polígono.
3. **O modelo.** O trabalho é feito por `scripts/sam_worker.py`, que corre fora do QGIS com o Python de `sam_venv` (ou chama o serviço na nuvem): o QGIS não bloqueia. As suas mensagens de progresso (as linhas `[sam] …` do worker, em italiano) aparecem na linha de estado: modelo e dispositivo, depois quantos polígonos em quantos segundos. Os polígonos com menos de 20 píxeis são descartados e os contornos simplificados.
4. **O regresso ao mapa.** O worker devolve os polígonos em píxeis; o pyArchInit volta a passá-los para coordenadas com a georreferenciação da imagem, repara as geometrias inválidas e reprojeta-as para o SRC da camada de destino.

### Fluxo de Trabalho SAM

**1. Preparação**
- Carregar a ortofotografia, ou uma camada de tiles (p. ex. ESRI World Imagery como XYZ Tiles)
- Verificar o sistema de referência do projeto
- Para escrever nas UE: carregar `pyunitastratigrafiche` (ou `pyunitastratigrafiche_usm`) e verificar o sítio na configuração
- Da primeira vez, para os modelos locais: «Instalar / atualizar» e depois «Descarregar pesos»

**2. Configuração**
- «Imagem»: camada raster, extensão, resolução (para os tiles) e lado máximo
- «O que segmentar»: o modo, o limiar e, para as classes de texto, as classes
- «Modelo»: um modelo local com os pesos presentes, ou um modelo na nuvem com a sua chave
- «Destino»: a camada e os seus atributos

**3. Execução**
- «Iniciar», ou «Iniciar seleção» e depois pontos, caixa ou polígono no mapa
- Acompanhar a linha de estado; «Cancelar» interrompe o trabalho
- No fim aparece «Concluído: N polígonos adicionados a “camada” (modelo).» (*Done: N polygons added to “layer” (model).*)

**4. Pós-processamento**
- Verificar os polígonos; os eventuais avisos aparecem na barra de mensagens do QGIS
- Camadas de UE: atribuir os números de UE (`us_s`) na tabela de atributos
- Corrigir, unir ou apagar os polígonos errados com as ferramentas de edição do QGIS
- Camada temporária: exportá-la se tiver de ser mantida

## Integração Cartográfica

### Exportação de Dados GIS

A partir da Ficha UE, separador Mapa:
- **Exportar GeoPackage**: Camada como GPKG
- **Exportar Shapefile**: Camada como SHP
- **Exportar GeoJSON**: Camada como JSON

### Importação de Dados GIS

Importar geometrias existentes:
1. Carregue a camada no QGIS
2. Selecione as entidades
3. Use a função de importação

### Geoprocessamento

Operações espaciais disponíveis:
- Buffer
- Interseção
- União
- Diferença
- Centroides

## Boas Práticas

### 1. Ortofotografias

- Resolução mínima: 1-2 cm/pixel
- Formato: GeoTIFF georreferenciado
- Sistema de referência: consistente com o projeto

### 2. Digitalização

- Use snap para precisão
- Verifique a topologia
- Mantenha a consistência dos atributos

### 3. Segmentação SAM

- Ortofotografia de boa qualidade, iluminação uniforme, bom contraste entre objetos e fundo
- **Ortofotografias grandes**: trabalhar por vista ou por caixa, não sobre «raster inteiro». O SAM trabalha a 1024 px internos e, acima do «Lado máximo (px):», a imagem é reduzida: numa área demasiado grande os objetos pequenos perdem-se
- **Tiles**: escolher um nível de zoom em que os objetos se reconheçam à vista (p. ex. 0,3–0,6 m/px para edifícios e estradas). A «Resolução (unidades de mapa/px):» propõe a da vista; se a extensão for grande, a imagem é reduzida ao lado máximo e a resolução real piora
- **Classes de texto**: substantivos ingleses simples (building, road, river, field, stone, wall)
- As classes só vêm do YOLOE ou do SAM 3: o SAM 2.1 em «Tudo (automático)» encontra contornos mas não atribui classes
- **Hardware**: os Mac com Apple Silicon usam MPS, uma placa NVIDIA usa CUDA e, caso contrário, o CPU, mais lento (é então melhor usar SAM 2.1 Tiny ou Small, YOLOE-26 S e áreas pequenas)
- Pós-verificação sempre necessária

### 4. Organização de Camadas

- Agrupe por tipo
- Use estilos consistentes
- Mantenha a ordem na legenda

## Resolução de Problemas

### Camadas Não Exibidas

**Causas possíveis**:
- Extensão errada
- Sistema de referência diferente
- Filtro ativo

**Soluções**:
- Zoom para Camada
- Verifique o SRC
- Remova filtros

### SAM Não Funciona

| Mensagem ou sintoma | O que fazer |
|---------------------|-------------|
| «Ambiente local» a laranja: «não instalado…» (*not installed…*), ou «O ambiente local não está instalado: clique em “Instalar / atualizar” (ou escolha um modelo na nuvem).» (*The local environment is not installed: press “Install / update” (or choose a cloud model).*) | Clicar em «Instalar / atualizar». É preciso um Python do sistema 3.10–3.13; se não existir, aparece `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` (não foi encontrado nenhum Python 3.10–3.13: instale o Python a partir de python.org ou do Homebrew). Se o pip falhar, o erro está em «Mostrar registo». Em Linux sem placa NVIDIA é instalado o torch para CPU |
| «pesos em falta (~N MB)» (*weights missing (~N MB)*), ou «Faltam os pesos do modelo: clique em “Descarregar pesos”.» (*The model weights are missing: press “Download weights”.*) | Clicar em «Descarregar pesos» (é precisa ligação à internet) |
| «É precisa a chave API do serviço.» (*The service API key is needed.*) | Com um modelo na nuvem, colar a chave em «Chave API:» (ver «Configuração da API») |
| «Nenhum polígono encontrado: experimente uma área mais pequena, um limiar mais baixo ou outro modelo.» (*No polygon found: try a smaller area, a lower threshold or another model.*) | Extensão mais pequena, «Limiar:» mais baixo, outro modelo (um SAM 2.1 maior, ou as classes de texto); para os tiles, uma resolução mais fina |
| «A área escolhida não cobre o raster» (mensagem em italiano: `l'area scelta non copre il raster`) | A vista, a caixa ou o polígono ficam fora do raster: enquadrar o raster e tentar de novo |
| «Preencha a área para a camada de UE.» (*Fill in the area for the US layer.*) | Escrever a «Área:» no grupo «Destino» |
| «Raster rodado: não suportado (reprojete-o primeiro)» (mensagem em italiano: `raster ruotato: non supportato (riproiettalo prima)`) | Reprojetar o raster com gdalwarp (menu Raster do QGIS) e usar o ficheiro novo |
| «A segmentação falhou» (*Segmentation failed*) com as últimas linhas do worker | Ler as linhas da mensagem; tentar de novo com uma extensão ou um «Lado máximo (px):» mais pequenos, ou com um modelo mais pequeno |

### Geometrias Corrompidas

**Causas possíveis**:
- Erros de digitalização
- Importação problemática

**Soluções**:
- Use "Reparar Geometrias"
- Redesenhe o elemento

### Camada carregada mas geometrias não visíveis (SQLite)

**Sintoma**:
- Uma camada pyArchInit de uma base de dados SQLite/SpatiaLite (ex. UE `pyunitastratigrafiche`, UEM, materiais, UE negativas) é carregada e a tabela de atributos mostra os registos, mas nada é desenhado no mapa e "Zoom para Camada" não funciona

**Causa**:
- O índice espacial (R*Tree) da camada não foi mantido: os seus triggers perderam-se quando uma tabela foi recriada (ex. por scripts antigos de atualização do esquema) ou os dados foram importados contornando-os
- O QGIS escolhe as entidades a desenhar através desse índice, por isso permanecem invisíveis
- Também foram afetadas as bases de dados criadas a partir do modelo SQLite entre outubro de 2025 e setembro de 2026

**Solução (automática)**:
- Ao ligar-se a uma base de dados SQLite, o pyArchInit verifica todos os índices espaciais (alguns instantes; nada é escrito se a base de dados estiver íntegra) e reconstrói automaticamente os danificados
- Desde a versão 5.13.16-alpha a mesma verificação repara também as **vistas espaciais** (`pyarchinit_us_view`, `pyarchinit_quote_view`, estruturas, materiais, as vistas UT, etc.):
  - cada vista é associada ao ROWID da respetiva tabela geométrica
  - os registos de vistas que já não existem são removidos
  - as vistas padrão em falta são recriadas
  - as vistas UT são registadas como vistas espaciais
  - as tabelas geométricas sem índice espacial recebem um: necessário quando o GDAL incluído no QGIS não tem as funções SpatiaLite (ex. QGIS em macOS), onde sem índice essas camadas não desenhavam nada
- Antes de alterar o que quer que seja guarda UMA única cópia de segurança junto à base de dados: `<base_de_dados>.sqlite.pre_spatial_index_repair_<data-hora UTC>`
- O resultado é escrito no painel de mensagens de registo do QGIS (View → Panels → Log Messages), separador "PyArchInit"

**O que fazer**:
- Nada a iniciar manualmente: a verificação é executada automaticamente na PRIMEIRA ligação a cada base de dados em cada sessão do QGIS (ou seja, após atualizar o plugin ou após reiniciar o QGIS)
- Se as camadas já estavam carregadas, remova-as e adicione-as novamente (ou reabra o projeto) após a reparação
- Se o registo "PyArchInit" indicar que um índice NÃO pôde ser reparado (ex. o SpatiaLite não pôde ser carregado), corrija a causa e reinicie o QGIS: a verificação só é repetida numa nova sessão
- O ficheiro de cópia de segurança pode ser eliminado depois de verificadas as camadas
- Para repetir a verificação (ex. após restaurar uma cópia de segurança), reinicie o QGIS
- Nota: em `inventario_materiali_view` o ponto do sítio é repetido para cada material, por isso "Identify" nesse ponto mostra um dos materiais

## Referências

### Ficheiros Fonte
- `modules/gis/pyarchinit_pyqgis.py` - Integração GIS
- `tabs/Sam_Segmentation_Dialog.py` - Janela SAM: grupos, modos, destino
- `modules/utility/sam_environment.py` - Ambiente Python separado, pacotes e pesos
- `modules/gis/sam_raster_source.py` - Imagem a segmentar (recorte GDAL ou renderização da vista) e georreferenciação
- `modules/gis/sam_map_tools.py` - Ferramentas de mapa para pontos, caixa e polígono
- `scripts/sam_worker.py` - Worker fora do QGIS: SAM 2.1, YOLOE, Replicate, Roboflow

### Camadas
- `pyunitastratigrafiche` - UE depósito
- `pyunitastratigrafiche_usm` - UE muro
- `pyarchinit_quote` - Cotas

---

## Tutorial em Vídeo

### Integração GIS
`[Marcador de posição: video_gis_integration.mp4]`

**Conteúdos**:
- Camadas predefinidas
- Visualização de UEs
- Estilização e rótulos
- Exportação cartográfica

**Duração estimada**: 15-18 minutos

### Segmentação SAM
`[Marcador de posição: video_sam_segmentation.mp4]`

**Conteúdos**:
- Configuração do SAM
- Modos de segmentação
- Pós-processamento
- Boas práticas

**Duração estimada**: 12-15 minutos

---

*Última atualização: outubro de 2026*

---

## Animação Interativa

Explore a animação interativa para saber mais sobre este tema.

[Abrir Animação Interativa](../../animations/pyarchinit_image_classification_animation.html)
