# Tutorial 17: TMA - Tabela de Materiais Arqueologicos

## Introducao

O **Formulario TMA** (Tabela de Materiais Arqueologicos) e o modulo avancado do PyArchInit para gestao de materiais de escavacao segundo as normas ministeriais italianas. Permite a catalogacao detalhada em conformidade com os regulamentos do ICCD (Instituto Central de Catalogo e Documentacao).

### Funcionalidades Principais

- Catalogacao conforme ICCD
- Gestao de materiais por caixa/contentor
- Campos cronologicos detalhados
- Tabela de materiais associados
- Gestao integrada de media
- Exportacao de etiquetas e formularios PDF

---

## Aceder ao Formulario

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Formulario TMA**

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas do PyArchInit
2. Clicar no icone **TMA**

---

## Visao Geral da Interface

O formulario apresenta uma interface complexa com muitos campos.

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | Barra SGBD | Navegacao, pesquisa, guardar |
| 2 | Campos de Identificacao | Sitio, Area, UE, Caixa |
| 3 | Campos de Localizacao | Localizacao, Sala, Sondagem |
| 4 | Campos Cronologicos | Periodo, Fracao, Cronologias |
| 5 | Tabela de Materiais | Detalhe dos materiais associados |
| 6 | Separador Media | Imagens e documentos |

---

## Campos de Identificacao

### Sitio

**Campo**: `comboBox_sito`
**Base de dados**: `sito`

Sitio arqueologico (SCAN - Denominacao de Escavacao ICCD).

### Area

**Campo**: `comboBox_area`
**Base de dados**: `area`

Area de escavacao.

### UE (DSCU)

**Campo**: `comboBox_us`
**Base de dados**: `dscu`

Unidade Estratigrafica de origem (DSCU = Descricao Unidade de Escavacao).

### Sector

**Campo**: `comboBox_settore`
**Base de dados**: `settore`

Sector de escavacao.

### Inventario

**Campo**: `lineEdit_inventario`
**Base de dados**: `inventario`

Numero de inventario.

### Caixa

**Campo**: `lineEdit_cassetta`
**Base de dados**: `cassetta`

Numero da caixa/contentor.

---

## Campos de Localizacao ICCD

### LDCT - Tipo de Localizacao

**Campo**: `comboBox_ldct`
**Base de dados**: `ldct`

Tipo de local de armazenamento.

**Valores ICCD:**
- museu
- superintendencia
- deposito
- laboratorio
- outro

### LDCN - Nome da Localizacao

**Campo**: `lineEdit_ldcn`
**Base de dados**: `ldcn`

Nome especifico do local de armazenamento.

### Localizacao Anterior

**Campo**: `lineEdit_vecchia_coll`
**Base de dados**: `vecchia_collocazione`

Localizacao anterior, se aplicavel.

### SCAN - Nome da Escavacao

**Campo**: `lineEdit_scan`
**Base de dados**: `scan`

Nome oficial da escavacao/investigacao.

### Sondagem

**Campo**: `comboBox_saggio`
**Base de dados**: `saggio`

Sondagem de referencia.

### Sala/Locus

**Campo**: `lineEdit_vano`
**Base de dados**: `vano_locus`

Sala ou locus de origem.

---

## Campos Cronologicos

### DTZG - Periodo Cronologico

**Campo**: `comboBox_dtzg`
**Base de dados**: `dtzg`

Periodo cronologico geral.

**Exemplos ICCD:**
- Idade do Bronze
- Idade do Ferro
- Epoca Romana
- Epoca Medieval

### DTZS - Fracao Cronologica

**Campo**: `comboBox_dtzs`
**Base de dados**: `dtzs`

Subdivisao do periodo.

**Exemplos:**
- inicial
- medio
- tardio
- final

### Cronologias

**Campo**: `tableWidget_cronologie`
**Base de dados**: `cronologie`

Tabela para cronologias multiplas ou detalhadas.

---

## Campos de Aquisicao

### AINT - Tipo de Aquisicao

**Campo**: `comboBox_aint`
**Base de dados**: `aint`

Metodo de aquisicao dos materiais.

**Valores ICCD:**
- escavacao
- prospeccao
- compra
- doacao
- apreensao

### AIND - Data de Aquisicao

**Campo**: `dateEdit_aind`
**Base de dados**: `aind`

Data de aquisicao.

### RCGD - Data de Prospeccao

**Campo**: `dateEdit_rcgd`
**Base de dados**: `rcgd`

Data da prospeccao (se aplicavel).

### RCGZ - Detalhes da Prospeccao

**Campo**: `textEdit_rcgz`
**Base de dados**: `rcgz`

Notas da prospeccao.

---

## Campos de Materiais

### OGTM - Material

**Campo**: `comboBox_ogtm`
**Base de dados**: `ogtm`

Material principal (Tipo de Objeto Material).

**Valores ICCD:**
- ceramica
- vidro
- metal
- osso
- pedra
- tijolo/telha

### N.o de Achados

**Campo**: `spinBox_n_reperti`
**Base de dados**: `n_reperti`

Numero total de achados.

### Peso

**Campo**: `doubleSpinBox_peso`
**Base de dados**: `peso`

Peso total em gramas.

### DESO - Descricao do Objeto

**Campo**: `textEdit_deso`
**Base de dados**: `deso`

Descricao breve dos objetos.

---

## Tabela de Detalhe dos Materiais

**Widget**: `tableWidget_materiali`
**Tabela associada**: `tma_materiali`

Permite registar materiais individuais contidos na caixa.

### Colunas

| Campo ICCD | Descricao |
|------------|-----------|
| MADI | Inventario do material |
| MACC | Categoria |
| MACL | Classe |
| MACP | Especificacao tipologica |
| MACD | Definicao |
| Cronologia | Datacao especifica |
| MACQ | Quantidade |

### Gestao de Linhas

| Botao | Funcao |
|-------|--------|
| + | Adicionar material |
| - | Remover material |

---

## Campos de Documentacao

### FTAP - Tipo de Fotografia

**Campo**: `comboBox_ftap`
**Base de dados**: `ftap`

Tipo de documentacao fotografica.

### FTAN - Codigo da Fotografia

**Campo**: `lineEdit_ftan`
**Base de dados**: `ftan`

Codigo de identificacao da fotografia.

### DRAT - Tipo de Desenho

**Campo**: `comboBox_drat`
**Base de dados**: `drat`

Tipo de documentacao grafica.

### DRAN - Codigo do Desenho

**Campo**: `lineEdit_dran`
**Base de dados**: `dran`

Codigo de identificacao do desenho.

### DRAA - Autor do Desenho

**Campo**: `lineEdit_draa`
**Base de dados**: `draa`

Autor do desenho.

---

## Separador Media

Gestao de imagens associadas a caixa/TMA.

### Funcionalidades

- Visualizacao de miniaturas
- Arrastar e largar para adicionar imagens
- Duplo clique para visualizar
- Ligacao a base de dados de media

---

## Separador de Vista em Tabela

Vista em tabela de todos os registos TMA para consulta rapida.

### Funcionalidades

- Vista em grelha
- Ordenacao por colunas
- Filtros rapidos
- Selecao multipla

---

## Exportacao e Impressao

### Exportacao PDF

| Opcao | Descricao |
|-------|-----------|
| Formulario TMA | Formulario completo |
| Etiquetas | Etiquetas de caixa |

### Etiquetas de Caixa

Geracao automatica de etiquetas para:
- Identificacao da caixa
- Conteudo resumido
- Dados de proveniencia
- Codigo de barras (opcional)

---

## Fluxo de Trabalho Operacional

### Registar Nova TMA

1. **Abrir formulario**
   - Pelo menu ou barra de ferramentas

2. **Novo registo**
   - Clicar em "Novo Registo"

3. **Dados de identificacao**
   ```
   Sitio: Vila Romana
   Area: 1000
   UE: 150
   Caixa: C-001
   ```

4. **Localizacao**
   ```
   LDCT: deposito
   LDCN: Deposito da Superintendencia de Roma
   SCAN: Escavacoes da Vila Romana 2024
   ```

5. **Cronologia**
   ```
   DTZG: Epoca Romana
   DTZS: Imperial
   ```

6. **Materiais** (tabela)
   ```
   | Inv | Cat | Classe | Def | Qtd |
   |-----|-----|--------|-----|-----|
   | 001 | ceramica | comum | pote | 5 |
   | 002 | ceramica | sigillata | prato | 3 |
   | 003 | vidro | - | unguentario | 1 |
   ```

7. **Guardar**
   - Clicar em "Guardar"

---

## Boas Praticas

### Normas ICCD

- Utilizar vocabularios controlados ICCD
- Seguir abreviaturas oficiais
- Manter consistencia terminologica

### Organizacao de Caixas

- Numeracao progressiva unica
- Uma TMA por caixa fisica
- Separar por UE quando possivel

### Documentacao

- Ligar sempre fotografias e desenhos
- Utilizar codigos unicos para media
- Registar autor e data

---

## Resolucao de Problemas

### Problema: Vocabularios ICCD indisponiveis

**Causa**: Thesaurus nao configurado.

**Solucao**:
1. Importar vocabularios padrao ICCD
2. Verificar configuracao do thesaurus

### Problema: Materiais nao guardados

**Causa**: Tabela de materiais nao sincronizada.

**Solucao**:
1. Verificar que todos os campos obrigatorios estao preenchidos
2. Guardar o formulario principal antes de adicionar materiais

---

## Referencias

### Base de Dados

- **Tabela principal**: `tma_materiali_archeologici`
- **Tabela de detalhe**: `tma_materiali`
- **Classe mapper**: `TMA`, `TMA_MATERIALI`
- **ID**: `id`

### Ficheiros Fonte

- **UI**: `gui/ui/Tma.ui`
- **Controlador**: `tabs/Tma.py`
- **Exportacao PDF**: `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Etiquetas**: `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Tutorial em Video

### Catalogacao TMA
**Duracao**: 15-18 minutos
- Normas ICCD
- Preenchimento completo
- Gestao de materiais

[Video placeholder: video_tma_catalogazione.mp4]

### Geracao de Etiquetas
**Duracao**: 5-6 minutos
- Configuracao de etiquetas
- Impressao em lote
- Personalizacao

[Video placeholder: video_tma_etichette.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
