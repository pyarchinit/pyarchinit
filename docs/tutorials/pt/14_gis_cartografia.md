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

**SAM (Segment Anything Model)** é um modelo de inteligência artificial desenvolvido pela Meta para segmentação automática de imagens. O PyArchInit integra-o para:
- Digitalização automática de pedras/elementos
- Segmentação de ortofotografias
- Aceleração de levantamentos

### Aceder à Função

1. **PyArchInit** → **Segmentação SAM**
2. Ou a partir da barra de ferramentas: ícone **SAM**

### Interface SAM

```
+--------------------------------------------------+
|        Segmentação de Pedras SAM                  |
+--------------------------------------------------+
| Entrada:                                          |
|   Camada Raster: [ComboBox ortofoto]             |
+--------------------------------------------------+
| Camada Alvo:                                      |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Atributos Predefinidos:                           |
|   Sítio (sito): [campo automático]               |
|   Área: [entrada área]                           |
|   Índice Estratigráfico: [1-10]                  |
|   Tipo UE: [pedra|camada|acumulação|corte]       |
+--------------------------------------------------+
| Modo de Segmentação:                              |
|   [o] Automático (detetar todas as pedras)       |
|   [ ] Modo clique (clicar em cada pedra)         |
|   [ ] Modo caixa (desenhar retângulo)            |
|   [ ] Modo polígono (desenhar à mão livre)       |
|   [ ] A partir de camada (usar polígono existente)|
+--------------------------------------------------+
| Modelo:                                           |
|   [ComboBox modelo]                              |
|   Chave API: [******]                            |
+--------------------------------------------------+
|        [Iniciar Segmentação]  [Cancelar]          |
+--------------------------------------------------+
```

### Modos de Segmentação

#### 1. Modo Automático
- Segmenta automaticamente todos os objetos visíveis
- Ideal para áreas com muitas pedras
- Requer ortofotografia de boa qualidade

#### 2. Modo Clique
- Clique em cada objeto a segmentar
- Clique direito ou Enter para terminar
- Escape para cancelar
- Mais preciso para objetos específicos

#### 3. Modo Caixa
- Desenhe um retângulo na área
- Segmenta apenas a área selecionada
- Útil para zonas delimitadas

#### 4. Modo Polígono
- Desenhe um polígono à mão livre
- Clique para adicionar vértices
- Clique direito para completar
- Para áreas irregulares

#### 5. Modo A Partir de Camada
- Use um polígono existente como máscara
- Selecione a camada de polígonos
- Segmenta apenas dentro do polígono

### Modelos Disponíveis

| Modelo | Tipo | Requisitos | Qualidade |
|--------|------|------------|-----------|
| Replicate SAM-2 | Cloud API | Chave API | Excelente |
| Roboflow SAM-3 | Cloud API | Chave API | Excelente + Prompt Texto |
| SAM vit_b | Local | 375MB VRAM | Boa |
| SAM vit_l | Local | 1.2GB VRAM | Muito boa |
| SAM vit_h | Local | 2.5GB VRAM | Excelente |
| OpenCV | Local | Nenhum | Básica |

### SAM-3 com Prompt de Texto

A versão SAM-3 (Roboflow) suporta **prompts de texto**:
- "stones" - pedras
- "pottery fragments" - fragmentos de cerâmica
- "bones" - ossos
- Qualquer descrição textual

### Configuração da API

#### API Replicate (SAM-2)
1. Registe-se em [replicate.com](https://replicate.com)
2. Obtenha a chave API
3. Introduza na configuração

#### API Roboflow (SAM-3)
1. Registe-se em [roboflow.com](https://roboflow.com)
2. Obtenha a chave API
3. Introduza na configuração

### Instalação Local do SAM

Para utilização local sem API:
```bash
# Criar ambiente virtual
cd ~/pyarchinit/bin
python -m venv sam_venv

# Ativar ambiente
source sam_venv/bin/activate

# Instalar dependências
pip install segment-anything torch torchvision

# Descarregar modelos (opcional)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### Fluxo de Trabalho SAM

1. **Preparação**
   - Carregue a ortofotografia como camada raster
   - Verifique o sistema de referência de coordenadas
   - Prepare a camada alvo

2. **Configuração**
   - Selecione o raster de entrada
   - Defina os atributos predefinidos
   - Escolha o modo e o modelo

3. **Execução**
   - Clique em "Iniciar Segmentação"
   - Aguarde o processamento
   - Verifique os resultados

4. **Pós-processamento**
   - Verifique os polígonos gerados
   - Atribua números de UE
   - Corrija eventuais erros

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

- Ortofotografia de alta qualidade
- Iluminação uniforme
- Contraste adequado objeto/fundo
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

**Causas possíveis**:
- Chave API inválida
- Raster não georreferenciado
- Modelo local não instalado

**Soluções**:
- Verifique a chave API
- Verifique a georreferenciação
- Instale o modelo

### Geometrias Corrompidas

**Causas possíveis**:
- Erros de digitalização
- Importação problemática

**Soluções**:
- Use "Reparar Geometrias"
- Redesenhe o elemento

## Referências

### Ficheiros Fonte
- `modules/gis/pyarchinit_pyqgis.py` - Integração GIS
- `tabs/Sam_Segmentation_Dialog.py` - Diálogo SAM
- `modules/gis/sam_map_tools.py` - Ferramentas de Mapa SAM

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

*Última atualização: janeiro de 2026*

---

## Animação Interativa

Explore a animação interativa para saber mais sobre este tema.

[Abrir Animação Interativa](../../animations/pyarchinit_image_classification_animation.html)
