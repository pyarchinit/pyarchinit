# Tutorial 16: Ficha de Cerâmica (Cerâmica Especializada)

## Índice
1. [Introdução](#introdução)
2. [Aceder à Ficha](#aceder-à-ficha)
3. [Interface do Utilizador](#interface-do-utilizador)
4. [Campos Principais](#campos-principais)
5. [Separadores da Ficha](#separadores-da-ficha)
6. [Ferramentas de Cerâmica](#ferramentas-de-cerâmica)
7. [Pesquisa Visual de Semelhança](#pesquisa-visual-de-semelhança)
8. [Quantificações](#quantificações)
9. [Gestão de Media](#gestão-de-media)
10. [Exportação e Relatórios](#exportação-e-relatórios)
11. [Fluxo de Trabalho Operacional](#fluxo-de-trabalho-operacional)
12. [Boas Práticas](#boas-práticas)
13. [Resolução de Problemas](#resolução-de-problemas)

---

## Introdução

A **Ficha de Cerâmica** é uma ferramenta especializada para a catalogação detalhada de cerâmicas arqueológicas. Ao contrário do formulário de Inventário de Materiais (mais generalista), esta ficha é especificamente concebida para a análise cerâmica aprofundada, com campos dedicados para pasta, classe cerâmica, decorações e medições específicas de vasos.

### Diferenças em relação à Ficha de Inventário de Materiais

| Aspeto | Inventário de Materiais | Cerâmica |
|--------|-------------------------|----------|
| **Finalidade** | Todos os tipos de achados | Apenas cerâmica |
| **Detalhe** | Geral | Especializado |
| **Campos de pasta** | Corpo cerâmico (genérico) | Pasta detalhada |
| **Decorações** | Campo único | Interior/Exterior separados |
| **Medições** | Genéricas | Específicas de vasos |
| **Ferramentas IA** | SketchGPT | PotteryInk, YOLO, Pesquisa de Semelhança |

### Funcionalidades Avançadas

A ficha de Cerâmica inclui funcionalidades de IA de última geração:
- **PotteryInk**: Geração automática de desenhos arqueológicos a partir de fotografias
- **Deteção YOLO**: Reconhecimento automático de formas cerâmicas
- **Pesquisa Visual de Semelhança**: Pesquisa de cerâmicas semelhantes via embeddings visuais
- **Gerador de Layout**: Geração automática de estampas cerâmicas

---

## Aceder à Ficha

### A partir do Menu

1. Abra o QGIS com o plugin PyArchInit ativo
2. Menu **PyArchInit** → **Gestão de registos arqueológicos** → **Artefacto** → **Cerâmica**

### A partir da Barra de Ferramentas

1. Localize a barra de ferramentas do PyArchInit
2. Clique no ícone **Cerâmica** (ícone de vaso/ânfora)

---

## Interface do Utilizador

A interface está organizada eficientemente para a catalogação cerâmica:

### Áreas Principais

| Área | Descrição |
|------|-----------|
| **1. Cabeçalho** | Barra SGBD, indicadores de estado, filtros |
| **2. Identificação** | Sítio, Área, UE, Número ID, Caixa, Saco |
| **3. Classificação** | Forma, Classe, Pasta, Material |
| **4. Separadores de Detalhe** | Descrição, Dados Técnicos, Suplementos |
| **5. Painel de Media** | Visualizador de imagens, pré-visualização |

### Separadores Disponíveis

| Separador | Conteúdo |
|-----------|----------|
| **Dados descritivos** | Descrição, decorações, notas |
| **Dados Técnicos** | Medições, tratamento de superfície, Munsell |
| **Suplementos** | Bibliografia, Estatísticas |

---

## Campos Principais

### Campos de Identificação

#### Número ID
- **Tipo**: Integer
- **Obrigatório**: Sim
- **Descrição**: Número único de identificação do fragmento cerâmico
- **Restrição**: Único por sítio

#### Sítio
- **Tipo**: ComboBox
- **Obrigatório**: Sim
- **Descrição**: Sítio arqueológico de origem

#### Área
- **Tipo**: ComboBox editável
- **Descrição**: Área de escavação

#### UE (Unidade Estratigráfica)
- **Tipo**: Integer
- **Descrição**: Número da UE de descoberta

#### Setor
- **Tipo**: Texto
- **Descrição**: Setor específico de descoberta

### Campos de Armazenamento

#### Caixa
- **Tipo**: Integer
- **Descrição**: Número da caixa de armazenamento

#### Saco
- **Tipo**: Integer
- **Descrição**: Número do saco

#### Ano
- **Tipo**: Integer
- **Descrição**: Ano de descoberta/catalogação

### Campos de Classificação Cerâmica

#### Forma
- **Tipo**: ComboBox editável
- **Recomendado**: Sim
- **Valores típicos**: Tigela, Pote, Jarro, Prato, Taça, Ânfora, Tampa, etc.
- **Descrição**: Forma geral do vaso

#### Forma Específica
- **Tipo**: ComboBox editável
- **Descrição**: Tipologia específica (ex.: Hayes 50, Dressel 1)

#### Forma Detalhada
- **Tipo**: Texto
- **Descrição**: Variante morfológica detalhada

#### Classe Cerâmica
- **Tipo**: ComboBox editável
- **Descrição**: Classe cerâmica
- **Exemplos**:
  - Sigillata africana
  - Sigillata itálica
  - Cerâmica de paredes finas
  - Cerâmica comum
  - Ânfora
  - Cerâmica de cozinha

#### Material
- **Tipo**: ComboBox editável
- **Descrição**: Material de base
- **Valores**: Cerâmica, Terracota, Porcelana, etc.

#### Pasta
- **Tipo**: ComboBox editável
- **Descrição**: Tipo de pasta cerâmica
- **Características a considerar**:
  - Cor da pasta
  - Granulometria das inclusões
  - Dureza
  - Porosidade

### Campos de Conservação

#### Percentagem
- **Tipo**: ComboBox editável
- **Descrição**: Percentagem preservada do vaso
- **Valores típicos**: <10%, 10-25%, 25-50%, 50-75%, >75%, Completo

#### QTD (Quantidade)
- **Tipo**: Integer
- **Descrição**: Número de fragmentos

### Campos de Documentação

#### Foto
- **Tipo**: Texto
- **Descrição**: Referência fotográfica

#### Desenho
- **Tipo**: Texto
- **Descrição**: Referência de desenho

---

## Separadores da Ficha

### Separador 1: Dados Descritivos

Separador principal para a descrição do fragmento.

#### Decorações

| Campo | Descrição |
|-------|-----------|
| **Decoração Exterior** | Tipo de decoração exterior |
| **Decoração Interior** | Tipo de decoração interior |
| **Descrição Decor. Exterior** | Descrição detalhada da decoração exterior |
| **Descrição Decor. Interior** | Descrição detalhada da decoração interior |
| **Tipo de Decoração** | Tipologia decorativa (Pintada, Incisa, Aplicada, etc.) |
| **Motivo Decorativo** | Motivo decorativo (Geométrico, Vegetal, Figurativo) |
| **Posição da Decoração** | Posição da decoração (Bordo, Bojo, Base, Asa) |

#### Feito ao Torno
- **Tipo**: ComboBox
- **Valores**: Sim, Não, Desconhecido
- **Descrição**: Indica se o vaso foi feito ao torno

#### Notas
- **Tipo**: TextEdit multilinha
- **Descrição**: Notas e observações adicionais

#### Visualizador de Media
Área para visualização de imagens associadas:
- Arrastar e largar para associar imagens
- Duplo clique para abrir o visualizador completo
- Botões para gestão de etiquetas

### Separador 2: Dados Técnicos

Dados técnicos e medições.

#### Cor Munsell
- **Tipo**: ComboBox editável
- **Descrição**: Código de cor Munsell da pasta
- **Formato**: ex.: "10YR 7/4", "5YR 6/6"
- **Nota**: Consulte o Munsell Soil Color Chart

#### Tratamento de Superfície
- **Tipo**: ComboBox editável
- **Descrição**: Tratamento da superfície
- **Valores típicos**:
  - Engobe
  - Brunido
  - Vidrado
  - Pintado
  - Simples

#### Medições (em cm)

| Campo | Descrição |
|-------|-----------|
| **Diâmetro Máx.** | Diâmetro máximo do vaso |
| **Diâmetro Bordo** | Diâmetro do bordo |
| **Diâmetro Base** | Diâmetro da base |
| **Altura Total** | Altura total (se reconstituível) |
| **Altura Preservada** | Altura preservada |

#### Datação
- **Tipo**: ComboBox editável
- **Descrição**: Enquadramento cronológico
- **Formato**: Texto (ex.: "séc. I-II d.C.")

### Separador 3: Suplementos

Separador com subsecções para dados suplementares.

#### Subseparador: Bibliografia
Gestão de referências bibliográficas para comparações tipológicas.

| Coluna | Descrição |
|--------|-----------|
| Autor | Autor(es) |
| Ano | Ano de publicação |
| Título | Título abreviado |
| Página | Referência de página |
| Figura | Figura/Estampa |

#### Subseparador: Estatísticas
Acesso a funcionalidades de quantificação e gráficos estatísticos.

---

## Ferramentas de Cerâmica

A Ficha de Cerâmica inclui um poderoso conjunto de ferramentas de IA para o processamento de imagens cerâmicas.

### Aceder às Ferramentas de Cerâmica

1. Menu **PyArchInit** → **Gestão de registos arqueológicos** → **Artefacto** → **Ferramentas de Cerâmica**

Ou a partir do botão dedicado na Ficha de Cerâmica.

### PotteryInk - Geração de Desenhos

Transforma automaticamente fotografias cerâmicas em desenhos arqueológicos estilizados.

#### Utilização

1. Selecione uma imagem cerâmica
2. Clique em "Gerar Desenho"
3. O sistema processa a imagem com IA
4. O desenho é gerado em estilo arqueológico

#### Requisitos
- Ambiente virtual dedicado (criado automaticamente)
- Modelos de IA pré-treinados
- GPU recomendada para desempenho ótimo

### Deteção YOLO de Cerâmica

Reconhecimento automático de formas cerâmicas em imagens.

#### Funcionalidades

- Identifica automaticamente a forma do vaso
- Sugere classificação
- Deteta partes anatómicas (bordo, parede, base, asa)

### Gerador de Layout

Gera automaticamente estampas cerâmicas para publicação.

#### Resultado

- Estampas em formato arqueológico padrão
- Escala métrica automática
- Layout otimizado
- Exportação para PDF ou imagem

### Extrator de PDF

Extrai imagens cerâmicas de publicações PDF para comparações.

---

## Pesquisa Visual de Semelhança

Funcionalidade avançada para encontrar cerâmicas visualmente semelhantes na base de dados.

### Como Funciona

O sistema utiliza **embeddings visuais** gerados por modelos de deep learning para representar cada imagem cerâmica como um vetor numérico. A pesquisa encontra as cerâmicas com os vetores mais semelhantes.

### Utilização

1. Selecione uma imagem de referência
2. Clique em "Encontrar Semelhante"
3. O sistema pesquisa a base de dados
4. As cerâmicas mais semelhantes são mostradas ordenadas por semelhança

### Modelos Disponíveis

- **ResNet50**: Bom equilíbrio velocidade/precisão
- **EfficientNet**: Desempenho ótimo
- **CLIP**: Pesquisa multimodal (texto + imagem)

### Atualização de Embeddings

Os embeddings são gerados automaticamente quando novas imagens são adicionadas. É possível forçar a atualização a partir do menu Ferramentas de Cerâmica.

---

## Quantificações

### Acesso

1. Clique no botão **Quant** na barra de ferramentas
2. Selecione o parâmetro de quantificação
3. Visualize o gráfico

### Parâmetros Disponíveis

| Parâmetro | Descrição |
|-----------|-----------|
| **Pasta** | Distribuição por tipo de pasta |
| **UE** | Distribuição por unidade estratigráfica |
| **Área** | Distribuição por área de escavação |
| **Material** | Distribuição por material |
| **Percentagem** | Distribuição por percentagem preservada |
| **Forma** | Distribuição por forma |
| **Forma específica** | Distribuição por forma específica |
| **Classe cerâmica** | Distribuição por classe cerâmica |
| **Cor Munsell** | Distribuição por cor |
| **Tratamento de superfície** | Distribuição por tratamento |
| **Decoração exterior** | Distribuição por decoração exterior |
| **Decoração interior** | Distribuição por decoração interior |
| **Feito ao torno** | Distribuição torno sim/não |

### Exportação de Quantificações

Os dados são exportados para:
- Ficheiro CSV em `pyarchinit_Quantificazioni_folder`
- Gráfico exibido no ecrã

---

## Gestão de Media

### Associação de Imagens

#### Métodos

1. **Arrastar e Largar**: Arraste imagens para a lista
2. **Botão Todas as Imagens**: Carregue todas as imagens associadas
3. **Pesquisar Imagens**: Pesquise imagens específicas

### Leitor de Vídeo

Para cerâmicas com documentação em vídeo, está disponível um leitor integrado.

### Integração Cloudinary

Suporte para imagens remotas no Cloudinary:
- Carregamento automático de miniaturas
- Cache local para desempenho
- Sincronização na nuvem

---

## Exportação e Relatórios

### Exportação de Ficha PDF

Gera uma ficha PDF completa com:
- Dados de identificação
- Classificação
- Medições
- Imagens associadas
- Notas

### Exportação de Lista

Gera lista PDF de todos os registos exibidos.

### Exportação de Dados

Botão para exportação em formato tabular (CSV/Excel).

---

## Fluxo de Trabalho Operacional

### Registo de um Novo Fragmento Cerâmico

#### Passo 1: Abrir e Novo Registo
1. Abra a Ficha de Cerâmica
2. Clique em **Novo registo**

#### Passo 2: Dados de Identificação
1. Verifique/selecione **Sítio**
2. Introduza **Número ID** (progressivo)
3. Introduza **Área**, **UE**, **Setor**
4. Introduza **Caixa** e **Saco**

#### Passo 3: Classificação
1. Selecione **Forma** (Tigela, Pote, etc.)
2. Selecione **Classe cerâmica** (classe cerâmica)
3. Selecione **Pasta** (tipo de pasta)
4. Indique **Material** e **Percentagem**

#### Passo 4: Dados Técnicos
1. Abra o separador **Dados Técnicos**
2. Introduza a **cor Munsell**
3. Selecione **Tratamento de superfície**
4. Introduza as **medições** (diâmetros, alturas)
5. Indique **Feito ao torno**

#### Passo 5: Decorações (se presentes)
1. Volte ao separador **Dados descritivos**
2. Selecione o tipo de **Decoração Exterior/Interior**
3. Preencha as descrições detalhadas
4. Indique **Tipo de decoração**, **motivo**, **posição**

#### Passo 6: Documentação
1. Associe fotografias (arrastar e largar)
2. Introduza referências de **Foto** e **Desenho**
3. Preencha **Notas** com observações

#### Passo 7: Datação e Comparações
1. Introduza a **Datação**
2. Abra o separador **Suplementos** → **Bibliografia**
3. Adicione referências bibliográficas

#### Passo 8: Gravar
1. Clique em **Gravar**
2. Verifique a confirmação

---

## Boas Práticas

### Classificação Consistente

- Utilize vocabulários normalizados para Forma, Classe, Pasta
- Mantenha a consistência na nomenclatura
- Atualize o tesauro quando necessário

### Documentação Fotográfica

- Fotografe cada fragmento com escala
- Inclua vista interior e exterior
- Documente os detalhes decorativos

### Medições

- Utilize paquímetro para medições precisas
- Indique sempre a unidade de medida (cm)
- Para fragmentos, meça apenas as partes preservadas

### Cor Munsell

- Utilize sempre o Munsell Soil Color Chart
- Meça em fratura fresca
- Indique as condições de iluminação

### Utilização de Ferramentas IA

- Verifique sempre os resultados automáticos
- O PotteryInk funciona melhor com fotografias de boa qualidade
- A pesquisa de semelhança é útil para comparações, não substitui a análise

---

## Resolução de Problemas

### Problemas Comuns

#### Número ID Duplicado
- **Erro**: "Já existe um registo com este ID"
- **Solução**: Verifique o próximo número disponível

#### Ferramentas de Cerâmica não arrancam
- **Causa**: Ambiente virtual não configurado
- **Solução**:
  1. Verifique a ligação à internet
  2. Aguarde a configuração automática
  3. Verifique o registo em `pyarchinit/bin/pottery_venv`

#### PotteryInk lento
- **Causa**: Processamento em CPU em vez de GPU
- **Solução**:
  1. Instale os drivers CUDA (NVIDIA)
  2. Verifique se o PyTorch está a utilizar GPU

#### Pesquisa de Semelhança Vazia
- **Causa**: Embeddings não gerados
- **Solução**:
  1. Abra Ferramentas de Cerâmica
  2. Clique em "Atualizar Embeddings"
  3. Aguarde a conclusão

#### Imagens não carregam
- **Causa**: Caminho incorreto ou Cloudinary não configurado
- **Solução**:
  1. Verifique a configuração do caminho nas Definições
  2. Para Cloudinary: verifique as credenciais

---

## Tutorial em Vídeo

### Vídeo 1: Vista Geral da Ficha de Cerâmica
*Duração: 5-6 minutos*

[Marcador de posição de vídeo]

### Vídeo 2: Registo Completo de Cerâmica
*Duração: 8-10 minutos*

[Marcador de posição de vídeo]

### Vídeo 3: Ferramentas de Cerâmica e IA
*Duração: 10-12 minutos*

[Marcador de posição de vídeo]

### Vídeo 4: Pesquisa de Semelhança
*Duração: 5-6 minutos*

[Marcador de posição de vídeo]

---

## Resumo dos Campos da Base de Dados

| Campo | Tipo | Base de dados | Obrigatório |
|-------|------|---------------|-------------|
| Número ID | Integer | id_number | Sim |
| Sítio | Texto | sito | Sim |
| Área | Texto | area | Não |
| UE | Integer | us | Não |
| Caixa | Integer | box | Não |
| Saco | Integer | bag | Não |
| Setor | Texto | sector | Não |
| Foto | Texto | photo | Não |
| Desenho | Texto | drawing | Não |
| Ano | Integer | anno | Não |
| Pasta | Texto | fabric | Não |
| Percentagem | Texto | percent | Não |
| Material | Texto | material | Não |
| Forma | Texto | form | Não |
| Forma Específica | Texto | specific_form | Não |
| Forma Detalhada | Texto | specific_shape | Não |
| Classe Cerâmica | Texto | ware | Não |
| Cor Munsell | Texto | munsell | Não |
| Tratamento Superfície | Texto | surf_trat | Não |
| Decor. Exterior | Texto | exdeco | Não |
| Decor. Interior | Texto | intdeco | Não |
| Feito ao Torno | Texto | wheel_made | Não |
| Desc. Decor. Ext. | Texto | descrip_ex_deco | Não |
| Desc. Decor. Int. | Texto | descrip_in_deco | Não |
| Notas | Texto | note | Não |
| Diâmetro Máx. | Numeric | diametro_max | Não |
| QTD | Integer | qty | Não |
| Diâmetro Bordo | Numeric | diametro_rim | Não |
| Diâmetro Base | Numeric | diametro_bottom | Não |
| Altura Total | Numeric | diametro_height | Não |
| Altura Preservada | Numeric | diametro_preserved | Não |
| Tipo Decoração | Texto | decoration_type | Não |
| Motivo Decorativo | Texto | decoration_motif | Não |
| Posição Decoração | Texto | decoration_position | Não |
| Datação | Texto | datazione | Não |

---

*Última atualização: janeiro de 2026*
*PyArchInit - Análise de Cerâmica Arqueológica*

---

## Animação Interativa

Explore a animação interativa para saber mais sobre este tema.

[Abrir Animação Interativa](../../animations/pyarchinit_pottery_tools_animation.html)
