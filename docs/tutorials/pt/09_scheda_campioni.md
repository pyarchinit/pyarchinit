# Tutorial 09: Ficha de Amostras

## Introducao

A **Ficha de Amostras** e o modulo do PyArchInit dedicado a gestao de amostras arqueologicas. Permite registar e acompanhar todos os tipos de amostras recolhidas durante a escavacao: terra, carvao, sementes, ossos, argamassas, metais e outros materiais destinados a analises especializadas.

### Tipos de Amostras

As amostras arqueologicas incluem:
- **Sedimentos**: para analises sedimentologicas, granulometricas
- **Carvao**: para datacao por radiocarbono (C14)
- **Sementes/Polen**: para analises arqueobotanicas
- **Ossos**: para analises arqueozoologicas, isotopicas, de ADN
- **Argamassas/Rebocos**: para analises arqueometricas
- **Metais/Escorias**: para analises metalurgicas
- **Ceramica**: para analises de pasta e proveniencia

---

## Aceder a Ficha

### Pelo Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecionar **Samples Form**

### Pela Barra de Ferramentas
1. Localizar a barra de ferramentas PyArchInit
2. Clicar no icone **Amostras**

---

## Panoramica da Interface

A ficha apresenta uma disposicao simplificada para gestao rapida de amostras.

### Areas Principais

| # | Area | Descricao |
|---|------|-----------|
| 1 | Barra de Ferramentas DBMS | Navegacao, pesquisa, gravacao |
| 2 | Info BD | Estado do registo, ordenacao, contador |
| 3 | Campos de Identificacao | Sitio, N.o da amostra, Tipo |
| 4 | Campos Descritivos | Descricao, notas |
| 5 | Campos de Armazenamento | Caixa, Localizacao |

---

## Barra de Ferramentas DBMS

### Botoes de Navegacao

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| Primeiro reg | Ir para o primeiro registo |
| Reg anterior | Ir para o registo anterior |
| Reg seguinte | Ir para o registo seguinte |
| Ultimo reg | Ir para o ultimo registo |

### Botoes CRUD

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| Novo registo | Criar um novo registo de amostra |
| Guardar | Guardar alteracoes |
| Eliminar | Eliminar o registo atual |

### Botoes de Pesquisa

| Icone | Funcao | Descricao |
|-------|--------|-----------|
| Nova pesquisa | Iniciar nova pesquisa |
| Pesquisar!!! | Executar pesquisa |
| Ordenar por | Ordenar resultados |
| Ver todos | Ver todos os registos |

---

## Campos da Ficha

### Sitio

**Campo**: `comboBox_sito`
**Base de dados**: `sito`

Selecionar o sitio arqueologico de pertenca.

### Numero da Amostra

**Campo**: `lineEdit_nr_campione`
**Base de dados**: `nr_campione`

Numero de identificacao progressivo da amostra.

### Tipo de Amostra

**Campo**: `comboBox_tipo_campione`
**Base de dados**: `tipo_campione`

Classificacao tipologica da amostra. Os valores provem do thesaurus.

**Tipos comuns:**
| Tipo | Descricao |
|------|-----------|
| Sedimento | Amostra de solo |
| Carvao | Para datacao C14 |
| Sementes | Restos carpologicos |
| Ossos | Restos faunisticos |
| Argamassa | Ligantes de construcao |
| Ceramica | Para analise de pasta |
| Metal | Para analise metalurgica |
| Polen | Para analise palinologica |

### Descricao

**Campo**: `textEdit_descrizione`
**Base de dados**: `descrizione`

Descricao detalhada da amostra.

**Conteudo recomendado:**
- Caracteristicas fisicas da amostra
- Quantidade recolhida
- Metodo de recolha
- Razao da amostragem
- Analises previstas

### Area

**Campo**: `comboBox_area`
**Base de dados**: `area`

Area de escavacao de origem.

### UE

**Campo**: `comboBox_us`
**Base de dados**: `us`

Unidade Estratigrafica de origem.

### Numero de Inventario de Material

**Campo**: `lineEdit_nr_inv_mat`
**Base de dados**: `numero_inventario_materiale`

Se a amostra estiver ligada a um achado inventariado, indicar o numero de inventario.

### Numero da Caixa

**Campo**: `lineEdit_nr_cassa`
**Base de dados**: `nr_cassa`

Caixa ou contentor de armazenamento.

### Local de Armazenamento

**Campo**: `comboBox_luogo_conservazione`
**Base de dados**: `luogo_conservazione`

Onde a amostra esta armazenada.

**Exemplos:**
- Laboratorio de escavacao
- Deposito do museu
- Laboratorio de analise externo
- Universidade

---

## Fluxo de Trabalho Operacional

### Criar uma Nova Amostra

1. **Abrir ficha**
   - Pelo menu ou barra de ferramentas

2. **Novo registo**
   - Clicar em "New Record"

3. **Dados de identificacao**
   ```
   Site: Villa Romana de Settefinestre
   N.o da amostra: C-2024-001
   Tipo de amostra: Carvao
   ```

4. **Proveniencia**
   ```
   Area: 1000
   UE: 150
   ```

5. **Descricao**
   ```
   Amostra de carvao recolhida da
   superficie queimada da UE 150.
   Quantidade: aprox. 50 gr.
   Recolhida para datacao C14.
   ```

6. **Armazenamento**
   ```
   N.o da caixa: Samp-1
   Local: Laboratorio de escavacao
   ```

7. **Guardar**
   - Clicar em "Save"

### Pesquisar Amostras

1. Clicar em "New Search"
2. Preencher criterios:
   - Sitio
   - Tipo de amostra
   - UE
3. Clicar em "Search"
4. Navegar pelos resultados

---

## Exportacao PDF

A ficha suporta exportacao PDF para:
- Lista de amostras
- Fichas detalhadas individuais

---

## Boas Praticas

### Nomenclatura

- Utilizar codigos unicos e significativos
- Formato recomendado: `SITIO-ANO-PROGRESSIVO`
- Exemplo: `VRS-2024-C001`

### Recolha

- Documentar sempre as coordenadas de recolha
- Fotografar o ponto de recolha
- Anotar a profundidade e o contexto

### Armazenamento

- Utilizar contentores adequados ao tipo
- Etiquetar claramente cada amostra
- Manter condicoes adequadas

### Documentacao

- Ligar sempre a UE de origem
- Indicar as analises previstas
- Registar o envio para laboratorios externos

---

## Resolucao de Problemas

### Problema: Tipo de amostra nao disponivel

**Causa**: Thesaurus nao configurado.

**Solucao**:
1. Abrir a Ficha de Thesaurus
2. Adicionar o tipo em falta para `campioni_table`
3. Guardar e reabrir a Ficha de Amostras

### Problema: UE nao apresentada

**Causa**: UE nao registada para o sitio selecionado.

**Solucao**:
1. Verificar se a UE existe na Ficha de UE
2. Verificar se pertence ao mesmo sitio

---

## Referencias

### Base de Dados

- **Tabela**: `campioni_table`
- **Classe mapper**: `CAMPIONI`
- **ID**: `id_campione`

### Ficheiros Fonte

- **UI**: `gui/ui/Campioni.ui`
- **Controlador**: `tabs/Campioni.py`
- **Exportacao PDF**: `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Video Tutorial

### Gestao de Amostras
**Duracao**: 5-6 minutos
- Criacao de nova amostra
- Preenchimento de campos
- Pesquisa e exportacao

[Marcador de video: video_campioni.mp4]

---

*Ultima atualizacao: janeiro de 2026*
*PyArchInit - Sistema de Gestao de Dados Arqueologicos*
