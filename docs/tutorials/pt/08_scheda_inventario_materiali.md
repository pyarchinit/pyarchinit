# Tutorial 08: Ficha de Inventario de Materiais

## Indice
1. [Introducao](#introducao)
2. [Aceder a Ficha](#aceder-a-ficha)
3. [Interface do Utilizador](#interface-do-utilizador)
4. [Campos Principais](#campos-principais)
5. [Separadores da Ficha](#separadores-da-ficha)
6. [Barra de Ferramentas DBMS](#barra-de-ferramentas-dbms)
7. [Gestao de Media](#gestao-de-media)
8. [Funcionalidades GIS](#funcionalidades-gis)
9. [Quantificacoes e Estatisticas](#quantificacoes-e-estatisticas)
10. [Exportacao e Relatorios](#exportacao-e-relatorios)
11. [Integracao AI](#integracao-ai)
12. [Fluxo de Trabalho Operacional](#fluxo-de-trabalho-operacional)
13. [Boas Praticas](#boas-praticas)
14. [Resolucao de Problemas](#resolucao-de-problemas)

---

## Introducao

A **Ficha de Inventario de Materiais** e a ferramenta principal para gerir achados arqueologicos no PyArchInit. Permite catalogar, descrever e quantificar todos os materiais encontrados durante a escavacao, desde ceramica a metais, de vidro a ossos animais.

### Finalidade da Ficha

- Inventariar todos os achados recuperados
- Associar achados as UEs de origem
- Gerir a classificacao tipologica
- Documentar caracteristicas fisicas e tecnologicas
- Calcular quantificacoes (vasos minimos, EVE, peso)
- Ligar fotografias e desenhos aos achados
- Gerar relatorios e estatisticas

### Tipos de Material Geridos

A ficha suporta varios tipos de material:
- **Ceramica**: Olaria, terracotas, materiais de construcao
- **Metais**: Bronze, ferro, chumbo, ouro, prata
- **Vidro**: Recipientes, vidro de janela
- **Osso/Marfim**: Objetos em materia animal dura
- **Pedra**: Utensilios liticos, esculturas
- **Moedas**: Numismatica
- **Organicos**: Madeira, texteis, couro

---

## Aceder a Ficha

### A Partir do Menu

1. Abrir o QGIS com o plugin PyArchInit ativo
2. Menu **PyArchInit** -> **Archaeological record management** -> **Artefact** -> **Artefact form**

### A Partir da Barra de Ferramentas

1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone **Achados** (icone de anfora/vaso)

### Atalho de Teclado

- **Ctrl+G**: Ativar/desativar visualizacao GIS do achado atual

---

## Interface do Utilizador

A interface esta organizada em tres areas principais:

### Areas Principais

| Area | Descricao |
|------|-----------|
| **1. Cabecalho** | Barra de ferramentas DBMS, indicadores de estado, botoes GIS e exportacao |
| **2. Campos de Identificacao** | Sitio, Area, UE, Numero de inventario, RA, Tipo de achado |
| **3. Campos Descritivos** | Classe, Definicao, Estado de conservacao, Datacao |
| **4. Separadores de Detalhe** | 6 separadores para dados especificos |

### Separadores Disponiveis

| Separador | Conteudo |
|-----------|----------|
| **Descricao** | Texto descritivo, visualizador de media, datacao |
| **Diapositivos** | Gestao de diapositivos e negativos |
| **Dados Quantitativos** | Elementos do achado, formas, medicoes ceramicas |
| **Tecnologias** | Tecnicas de producao e decoracao |
| **Ref. Bibliografica** | Referencias bibliograficas |
| **Quantificacoes** | Graficos e estatisticas |

---

## Campos Principais

### Campos de Identificacao

#### Sitio
- **Tipo**: ComboBox (apenas leitura apos gravacao)
- **Obrigatorio**: Sim
- **Descricao**: Sitio arqueologico de origem

#### Numero de Inventario
- **Tipo**: LineEdit numerico
- **Obrigatorio**: Sim
- **Descricao**: Numero progressivo unico do achado dentro do sitio
- **Restricao**: Unico por sitio

#### Area
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Nao
- **Descricao**: Area de escavacao de origem

#### UE (Unidade Estratigrafica)
- **Tipo**: LineEdit
- **Obrigatorio**: Nao (mas fortemente recomendado)
- **Descricao**: Numero da UE de origem
- **Ligacao**: Liga o achado a ficha de UE correspondente

#### Estrutura
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Nao
- **Descricao**: Estrutura de pertenca (se aplicavel)

#### RA (Achado Arqueologico)
- **Tipo**: LineEdit numerico
- **Obrigatorio**: Nao
- **Descricao**: Numero de achado alternativo

### Campos de Classificacao

#### Tipo de Achado
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Sim
- **Valores tipicos**: Ceramica, Metal, Vidro, Osso, Pedra, Moeda, etc.

#### Classe do Material (Criterio de Registo)
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Nao
- **Exemplos para ceramica**:
  - Ceramica comum
  - Sigillata italica
  - Sigillata africana
  - Ceramica de verniz negro
  - Ceramica de paredes finas
  - Anforas
  - Lucernas

#### Definicao
- **Tipo**: ComboBox editavel
- **Obrigatorio**: Nao
- **Exemplos**: Prato, Taca, Panela, Jarro, Tampa, etc.

### Campos de Estado e Conservacao

#### Lavado
- **Tipo**: ComboBox
- **Valores**: Sim, Nao

#### Catalogado
- **Tipo**: ComboBox
- **Valores**: Sim, Nao

#### Diagnostico
- **Tipo**: ComboBox
- **Valores**: Sim, Nao

#### Estado de Conservacao
- **Tipo**: ComboBox editavel
- **Valores tipicos**: Completo, Fragmentario, Lacunoso, Restaurado

---

## Separadores da Ficha

### Separador 1: Descricao

O separador principal contem a descricao textual e a gestao de media.

#### Campo de Descricao
- **Tipo**: TextEdit multilinhas
- **Conteudo sugerido**:
  - Forma geral
  - Partes conservadas
  - Caracteristicas tecnicas
  - Decoracoes
  - Comparacoes tipologicas

#### Datacao do Achado
- **Tipo**: ComboBox editavel
- **Formato**: Texto (ex.: "Seculo I a.C.", "Seculos II-III d.C.")

#### Visualizador de Media
Area para visualizacao de imagens associadas ao achado:
- **Ver todas as imagens**: Carregar todas as fotografias ligadas
- **Pesquisar imagens**: Pesquisar imagens
- **Remover tag**: Remover associacao imagem-achado
- **SketchGPT**: Gerar descricao AI a partir de imagem

### Separador 2: Diapositivos

Gestao de documentacao fotografica tradicional.

#### Tabela de Diapositivos
| Coluna | Descricao |
|--------|-----------|
| Codigo | Codigo de identificacao do diapositivo |
| N.o | Numero progressivo |

#### Tabela de Negativos
| Coluna | Descricao |
|--------|-----------|
| Codigo | Codigo do rolo do negativo |
| N.o | Numero do fotograma |

### Separador 3: Dados Quantitativos

Separador fundamental para analise quantitativa, especialmente para ceramica.

#### Tabela de Elementos do Achado
Regista os elementos individuais que compoem o achado:

| Coluna | Descricao | Exemplo |
|--------|-----------|---------|
| Elemento encontrado | Parte anatomica do vaso | Bordo, Parede, Fundo, Asa |
| Tipo de quantidade | Estado do fragmento | Fragmento, Completo |
| Quantidade | Numero de pecas | 5 |

#### Campos de Quantificacao Ceramica

| Campo | Descricao |
|-------|-----------|
| **Vasos minimos** | Numero Minimo de Individuos (NMI) |
| **Vasos maximos** | Numero Maximo de Individuos |
| **Total de fragmentos** | Calculado automaticamente a partir da tabela de elementos |
| **Peso** | Peso em gramas |
| **Diametro do bordo** | Diametro do bordo em cm |
| **EVE do bordo** | Equivalente Estimado de Vaso (percentagem do bordo conservada) |

### Separador 4: Tecnologias

Registo de tecnicas de producao e decoracao.

#### Tabela de Tecnologias

| Coluna | Descricao | Exemplo |
|--------|-----------|---------|
| Tipo de tecnologia | Categoria tecnica | Producao, Decoracao |
| Posicao | Onde se localiza | Interior, Exterior, Corpo |
| Quantidade | Se aplicavel | - |
| Unidade | Se aplicavel | - |

#### Campos Especificos de Ceramica

| Campo | Descricao |
|-------|-----------|
| **Pasta ceramica** | Tipo de pasta (Fina, Semi-fina, Grosseira) |
| **Revestimento** | Tipo de revestimento (Engobe, Vidrado) |

### Separador 5: Referencias Bibliograficas

Gestao de bibliografia comparativa.

#### Tabela de Referencias

| Coluna | Descricao |
|--------|-----------|
| Autor | Apelido(s) do(s) autor(es) |
| Ano | Ano de publicacao |
| Titulo | Titulo abreviado |
| Pagina | Referencia de pagina |
| Figura | Referencia de figura/estampa |

### Separador 6: Quantificacoes

Separador para geracao de graficos e estatisticas.

#### Tipos de Quantificacao Disponiveis

| Tipo | Descricao |
|------|-----------|
| **Vasos minimos** | Grafico de NMI |
| **Vasos maximos** | Grafico de numero maximo |
| **Total de fragmentos** | Grafico de contagem de fragmentos |
| **Peso** | Grafico de peso |
| **EVE do bordo** | Grafico de EVE |

#### Parametros de Agrupamento

Os graficos podem ser agrupados por:
- Tipo de achado
- Classe do material
- Definicao
- Pasta ceramica
- Revestimento
- Tipo
- Datacao
- RA
- Ano

---

## Barra de Ferramentas DBMS

### Botoes Padrao

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| Teste de ligacao | Testar ligacao | Verificar a ligacao a base de dados |
| Primeiro/Anterior/Seguinte/Ultimo | Navegacao | Navegar entre registos |
| Novo registo | Novo | Criar novo achado |
| Guardar | Guardar | Guardar alteracoes |
| Eliminar | Eliminar | Eliminar achado atual |
| Ver todos | Todos | Ver todos os registos |
| Nova pesquisa | Pesquisa | Ativar modo de pesquisa |
| Pesquisar!!! | Executar | Executar pesquisa |
| Ordenar por | Ordenar | Ordenar registos |

### Botoes Especificos

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| GIS | Ver GIS | Mostrar achado no mapa |
| PDF | Exportar PDF | Gerar ficha PDF |
| Folha | Exportar lista | Gerar lista PDF |
| Excel | Exportar Excel | Exportar para formato Excel/CSV |
| A5 | Exportar A5 | Gerar etiqueta formato A5 |
| Quant | Quantificacoes | Abrir painel de quantificacoes |

---

## Gestao de Media

### Associacao de Imagens

#### Arrastar e Largar
Pode arrastar imagens diretamente para a lista para as associar ao achado.

#### Botoes de Media

| Botao | Funcao |
|-------|--------|
| **Todas as imagens** | Carregar todas as imagens associadas |
| **Pesquisar imagens** | Abrir pesquisa de imagens |
| **Remover tag** | Remover associacao atual |

### Visualizador de Imagens

O duplo clique numa imagem da lista abre o visualizador completo com:
- Zoom
- Panoramica
- Rotacao
- Informacao EXIF

---

## Funcionalidades GIS

### Visualizacao no Mapa

#### Botao GIS (Comutador)
- **Ativo**: O achado e realcado no mapa QGIS
- **Inativo**: Sem visualizacao
- **Atalho**: Ctrl+G

#### Requisitos
- O achado deve ter a UE de origem especificada
- A UE deve ter geometria na camada GIS

---

## Quantificacoes e Estatisticas

### Aceder as Quantificacoes

1. Clicar no botao **Quant** na barra de ferramentas
2. Selecionar o tipo de quantificacao
3. Selecionar os parametros de agrupamento
4. Clicar em OK

### Tipos de Grafico

#### Grafico de Barras
Apresenta a distribuicao por categoria selecionada.

### Exportar Quantificacoes

Os dados de quantificacao sao automaticamente exportados para:
- Ficheiro CSV em `pyarchinit_Quantificazioni_folder`
- Grafico apresentado no ecra

---

## Exportacao e Relatorios

### Exportacao PDF de Ficha Individual

Gera uma ficha PDF completa do achado atual com:
- Todos os dados de identificacao
- Descricao
- Dados quantitativos
- Referencias bibliograficas
- Imagens associadas (se disponiveis)

### Exportacao PDF de Lista

Gera uma lista PDF de todos os achados apresentados (resultado da pesquisa atual):
- Tabela resumo
- Dados essenciais de cada achado

### Exportacao A5 (Etiquetas)

Gera etiquetas em formato A5 para:
- Identificacao de caixas
- Etiquetagem de achados
- Fichas moveis

### Exportacao Excel/CSV

Exporta dados em formato tabular para:
- Tratamento estatistico externo
- Importacao para outro software
- Arquivo

---

## Integracao AI

### SketchGPT

Funcionalidade AI para gerar automaticamente descricoes de achados a partir de imagens.

#### Utilizacao

1. Associar uma imagem ao achado
2. Clicar no botao **SketchGPT**
3. Selecionar a imagem a analisar
4. Selecionar o modelo GPT (gpt-4-vision, gpt-4o)
5. O sistema gera uma descricao arqueologica

#### Resultado

A descricao gerada inclui:
- Identificacao do tipo de achado
- Descricao das caracteristicas visiveis
- Possiveis comparacoes tipologicas
- Sugestoes de datacao

> **Nota**: Requer Chave API OpenAI configurada.

---

## Fluxo de Trabalho Operacional

### Criar um Novo Achado

#### Passo 1: Abrir a Ficha
1. Abrir a Ficha de Inventario de Materiais
2. Verificar a ligacao a base de dados

#### Passo 2: Novo Registo
1. Clicar em **New record**
2. O estado muda para "New Record"

#### Passo 3: Dados de Identificacao
1. Verificar/selecionar o **Sitio**
2. Introduzir o **Numero de inventario** (progressivo)
3. Introduzir a **Area** e a **UE** de origem

#### Passo 4: Classificacao
1. Selecionar o **Tipo de achado**
2. Selecionar a **Classe do material**
3. Selecionar/introduzir a **Definicao**

#### Passo 5: Descricao
1. Preencher o campo **Descricao** no separador Descricao
2. Selecionar a **Datacao**
3. Associar eventuais imagens

#### Passo 6: Dados Quantitativos (se ceramica)
1. Abrir o separador **Dados Quantitativos**
2. Introduzir elementos na tabela
3. Preencher vasos minimos/maximos
4. Introduzir peso e medicoes

#### Passo 7: Armazenamento
1. Introduzir **N.o da caixa**
2. Selecionar **Local de armazenamento**
3. Indicar o **Estado de conservacao**

#### Passo 8: Guardar
1. Clicar em **Save**
2. Verificar a mensagem de confirmacao
3. O registo esta agora guardado na base de dados

### Pesquisar Achados

#### Pesquisa Simples
1. Clicar em **New search**
2. Preencher os campos de pesquisa desejados
3. Clicar em **Search!!!**

#### Pesquisa por UE
1. Ativar a pesquisa
2. Introduzir apenas o numero da UE no campo UE
3. Executar a pesquisa

---

## Boas Praticas

### Numeracao de Inventario

- Utilizar numeracao progressiva sem lacunas
- Um numero = um achado (ou grupo homogeneo)
- Documentar os criterios de inventariacao

### Classificacao

- Utilizar vocabularios controlados para as classes
- Manter consistencia nas definicoes de tipo
- Atualizar o thesaurus quando necessario

### Quantificacao Ceramica

Para uma quantificacao correta:
1. **Vasos minimos (NMI)**: Contar apenas elementos diagnosticos (bordos, fundos distintivos)
2. **EVE**: Medir a percentagem de circunferencia conservada
3. **Peso**: Pesar todos os fragmentos do grupo

### Documentacao Fotografica

- Fotografar todos os achados diagnosticos
- Utilizar escala metrica nas fotografias
- Associar fotografias atraves do gestor de media

### Ligacao a UE

- Verificar sempre que a UE existe antes de associar
- Para achados de limpeza/superficie, utilizar UE apropriada
- Documentar achados fora de contexto

---

## Resolucao de Problemas

### Problemas Comuns

#### Numero de inventario duplicado
- **Erro**: "Ja existe um registo com este numero de inventario"
- **Causa**: Numero ja utilizado para o sitio
- **Solucao**: Verificar o proximo numero disponivel com "Ver todos"

#### Imagens nao apresentadas
- **Causa**: Caminho de imagens incorreto
- **Solucao**:
  1. Verificar a configuracao do caminho nas Definicoes
  2. Verificar se as imagens estao na pasta correta
  3. Reassociar as imagens

#### Quantificacoes vazias
- **Causa**: Campos quantitativos nao preenchidos
- **Solucao**: Preencher vasos minimos/maximos ou total de fragmentos

#### GIS nao funciona
- **Causa**: A UE nao tem geometria ou a camada nao esta carregada
- **Solucao**:
  1. Verificar se a camada da UE esta carregada no QGIS
  2. Verificar se a UE tem geometria associada

---

## Video Tutorial

### Video 1: Panoramica da Ficha de Inventario
*Duracao: 5-6 minutos*

**Conteudos:**
- Interface geral
- Navegacao entre separadores
- Funcionalidades principais

### Video 2: Documentacao Ceramica Completa
*Duracao: 8-10 minutos*

**Conteudos:**
- Preenchimento de todos os campos
- Quantificacao ceramica
- Elementos do achado
- Tecnologias

### Video 3: Media e Gestao de Fotografias
*Duracao: 4-5 minutos*

**Conteudos:**
- Associacao de imagens
- Visualizador
- SketchGPT

### Video 4: Exportacao e Quantificacoes
*Duracao: 5-6 minutos*

**Conteudos:**
- Exportacao PDF
- Exportacao Excel
- Graficos de quantificacao

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Gestao de Dados Arqueologicos*
