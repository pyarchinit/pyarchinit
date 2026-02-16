# Tutorial 10: Ficha de Documentacao

## Introducao

A **Ficha de Documentacao** e o modulo do PyArchInit para gestao da documentacao grafica de escavacao: plantas, cortes, alcados, levantamentos e qualquer outro resultado grafico produzido durante as atividades arqueologicas.

### Tipos de Documentacao

- **Plantas**: plantas de camada, plantas de fase, plantas gerais
- **Cortes**: cortes estratigraficos
- **Alcados**: alcados de parede, frentes de escavacao
- **Levantamentos**: levantamentos topograficos, fotogrametricos
- **Ortofotografias**: resultados de drone/fotogrametria
- **Desenhos de achados**: ceramica, metais, etc.

---

## Aceder a Ficha

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Documentation Form**

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone **Documentacao**

---

## Panoramica da Interface

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | Barra de Ferramentas DBMS | Navegacao, pesquisa, gravacao |
| 2 | Info BD | Estado do registo, ordenacao, contador |
| 3 | Campos de Identificacao | Sitio, Nome, Data |
| 4 | Campos Tipologicos | Tipo, Fonte, Escala |
| 5 | Campos Descritivos | Desenhador, Notas |

---

## Barra de Ferramentas DBMS

### Botoes Padrao

| Funcao | Descricao |
|--------|-----------|
| Primeiro/Anterior/Seguinte/Ultimo reg | Navegacao entre registos |
| Novo registo | Criar novo registo |
| Guardar | Guardar alteracoes |
| Eliminar | Eliminar registo |
| Nova pesquisa / Pesquisar | Funcoes de pesquisa |
| Ordenar por | Ordenar resultados |
| Ver todos | Ver todos os registos |

---

## Campos da Ficha

### Sitio

**Campo**: `comboBox_sito_doc`
**Base de dados**: `sito`

Sitio arqueologico de referencia.

### Nome da Documentacao

**Campo**: `lineEdit_nome_doc`
**Base de dados**: `nome_doc`

Nome de identificacao do documento.

**Convencoes de nomenclatura:**
- `P` = Planta (ex.: P001)
- `S` = Corte (ex.: S001)
- `E` = Alcado (ex.: E001)
- `R` = Levantamento (ex.: R001)

### Data

**Campo**: `dateEdit_data`
**Base de dados**: `data`

Data de execucao do desenho/levantamento.

### Tipo de Documentacao

**Campo**: `comboBox_tipo_doc`
**Base de dados**: `tipo_documentazione`

Tipo de documento.

**Valores tipicos:**
| Tipo | Descricao |
|------|-----------|
| Layer plan | UE individual |
| Phase plan | Varias UEs coetaneas |
| General plan | Vista geral |
| Stratigraphic section | Perfil vertical |
| Elevation | Alcado de parede |
| Topographic survey | Planimetria geral |
| Orthophoto | A partir de fotogrametria |
| Find drawing | Ceramica, metal, etc. |

### Fonte

**Campo**: `comboBox_sorgente`
**Base de dados**: `sorgente`

Fonte/metodo de producao.

**Valores:**
- Levantamento direto
- Fotogrametria
- Scanner laser
- GPS/Estacao total
- Digitalizacao CAD
- Ortofotografia por drone

### Escala

**Campo**: `comboBox_scala`
**Base de dados**: `scala`

Escala de representacao.

**Escalas comuns:**
| Escala | Utilizacao tipica |
|--------|-------------------|
| 1:1 | Desenhos de achados |
| 1:5 | Pormenores |
| 1:10 | Cortes, pormenores |
| 1:20 | Plantas de camada |
| 1:50 | Plantas gerais |
| 1:100 | Planimetrias |
| 1:200+ | Mapas topograficos |

### Desenhador

**Campo**: `comboBox_disegnatore`
**Base de dados**: `disegnatore`

Autor do desenho/levantamento.

### Notas

**Campo**: `textEdit_note`
**Base de dados**: `note`

Notas adicionais sobre o documento.

---

## Fluxo de Trabalho Operacional

### Registar Nova Documentacao

1. **Abrir ficha**
   - Pelo menu ou barra de ferramentas

2. **Novo registo**
   - Clicar em "New Record"

3. **Dados de identificacao**
   ```
   Site: Villa Romana de Settefinestre
   Nome: P025
   Data: 15/06/2024
   ```

4. **Classificacao**
   ```
   Tipo: Layer plan
   Fonte: Levantamento direto
   Escala: 1:20
   ```

5. **Autor e notas**
   ```
   Desenhador: M. Rossi
   Notas: Planta da UE 150. Evidencia
   os limites da superficie de pavimento.
   ```

6. **Guardar**
   - Clicar em "Save"

### Pesquisar Documentacao

1. Clicar em "New Search"
2. Preencher criterios:
   - Sitio
   - Tipo de documentacao
   - Escala
   - Desenhador
3. Clicar em "Search"
4. Navegar pelos resultados

---

## Exportacao PDF

A ficha suporta exportacao PDF para:
- Lista de documentacao
- Fichas detalhadas

---

## Boas Praticas

### Nomenclatura

- Utilizar codigos consistentes ao longo de todo o projeto
- Numeracao progressiva por tipo
- Documentar as convencoes adotadas

### Organizacao

- Ligar sempre ao sitio de referencia
- Indicar a escala real
- Registar a data e o autor

### Arquivo

- Ligar ficheiros digitais atraves da gestao de media
- Manter copias de seguranca
- Utilizar formatos padrao (PDF, TIFF)

---

## Resolucao de Problemas

### Problema: Tipo de documentacao nao disponivel

**Causa**: Thesaurus nao configurado.

**Solucao**:
1. Abrir a Ficha de Thesaurus
2. Adicionar os tipos em falta para `documentazione_table`

### Problema: Ficheiro nao apresentado

**Causa**: Caminho incorreto ou ficheiro em falta.

**Solucao**:
1. Verificar se o ficheiro existe
2. Verificar o caminho na configuracao de media

---

## Referencias

### Base de Dados

- **Tabela**: `documentazione_table`
- **Classe mapper**: `DOCUMENTAZIONE`
- **ID**: `id_documentazione`

### Ficheiros Fonte

- **UI**: `gui/ui/Documentazione.ui`
- **Controlador**: `tabs/Documentazione.py`
- **Exportacao PDF**: `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Video Tutorial

### Gestao de Documentacao Grafica
**Duracao**: 6-8 minutos
- Registo de nova documentacao
- Classificacao e metadados
- Pesquisa e consulta

[Marcador de video: video_documentazione.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
