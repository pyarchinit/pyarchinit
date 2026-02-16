# Tutorial 15: Ficha de Arqueozoologia (Fauna)

## Introdução

A **Ficha de Arqueozoologia/Fauna** (FICHA FAUNA - FF) é o módulo do PyArchInit dedicado à análise e documentação de restos faunísticos. Permite registar dados arqueozoológicos detalhados para o estudo das economias de subsistência antigas.

### Conceitos Básicos

**Arqueozoologia:**
- Estudo dos restos animais de contextos arqueológicos
- Análise das relações humano-animal no passado
- Reconstrução de dietas, criação de gado, caça

**Dados registados:**
- Identificação taxonómica (espécie)
- Partes esqueléticas presentes
- NMI (Número Mínimo de Indivíduos)
- Estado de conservação
- Vestígios tafonómicos
- Marcas de corte

---

## Aceder à Ficha

### Via Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecione **Ficha Fauna** (ou **Ficha Fauna**)

### Via Barra de Ferramentas
1. Localize a barra de ferramentas do PyArchInit
2. Clique no ícone **Fauna** (osso estilizado)

---

## Vista Geral da Interface

A ficha está organizada em separadores temáticos:

### Separadores Principais

| # | Separador | Conteúdo |
|---|-----------|----------|
| 1 | Dados de Identificação | Sítio, Área, UE, Contexto |
| 2 | Dados Arqueozoológicos | Espécie, NMI, Partes esqueléticas |
| 3 | Dados Tafonómicos | Conservação, Fragmentação, Vestígios |
| 4 | Dados Contextuais | Contexto deposicional, Associações |
| 5 | Estatísticas | Gráficos e quantificações |

---

## Barra de Ferramentas

A barra de ferramentas fornece funções padrão:

| Ícone | Função |
|-------|--------|
| Primeiro/Anterior/Seguinte/Último | Navegação entre registos |
| Novo | Novo registo |
| Gravar | Gravar |
| Eliminar | Eliminar |
| Pesquisar | Pesquisar |
| Ver Todos | Ver todos |
| PDF | Exportação PDF |

---

## Separador Dados de Identificação

### Seleção de UE

**Campo**: `comboBox_us_select`

Seleciona a UE de origem. Mostra as UEs disponíveis no formato "Sítio - Área - UE".

### Sítio

**Campo**: `comboBox_sito`
**Base de dados**: `sito`

Sítio arqueológico.

### Área

**Campo**: `comboBox_area`
**Base de dados**: `area`

Área de escavação.

### Sondagem

**Campo**: `comboBox_saggio`
**Base de dados**: `saggio`

Sondagem de origem.

### UE

**Campo**: `comboBox_us`
**Base de dados**: `us`

Unidade Estratigráfica.

### Datação da UE

**Campo**: `lineEdit_datazione`
**Base de dados**: `datazione_us`

Enquadramento cronológico da UE.

### Responsável

**Campo**: `comboBox_responsabile`
**Base de dados**: `responsabile_scheda`

Autor da ficha.

### Data de Compilação

**Campo**: `dateEdit_data`
**Base de dados**: `data_compilazione`

Data de compilação da ficha.

---

## Separador Dados Arqueozoológicos

### Contexto

**Campo**: `comboBox_contesto`
**Base de dados**: `contesto`

Tipo de contexto deposicional.

**Valores:**
- Povoado
- Lixeira/Despejo
- Enchimento
- Piso de ocupação
- Enterramento
- Ritual

### Espécie

**Campo**: `comboBox_specie`
**Base de dados**: `specie`

Identificação taxonómica.

**Espécies arqueozoológicas comuns:**
| Espécie | Nome científico |
|---------|----------------|
| Bovino | Bos taurus |
| Ovelha | Ovis aries |
| Cabra | Capra hircus |
| Porco | Sus domesticus |
| Cavalo | Equus caballus |
| Veado | Cervus elaphus |
| Javali | Sus scrofa |
| Lebre | Lepus europaeus |
| Cão | Canis familiaris |
| Gato | Felis catus |
| Galinha | Gallus gallus |

### Número Mínimo de Indivíduos (NMI)

**Campo**: `spinBox_nmi`
**Base de dados**: `numero_minimo_individui`

Estimativa do número mínimo de indivíduos representados.

### Partes Esqueléticas

**Campo**: `tableWidget_parti`
**Base de dados**: `parti_scheletriche`

Tabela para registo das partes anatómicas presentes.

**Colunas:**
| Coluna | Descrição |
|--------|-----------|
| Elemento | Osso/parte anatómica |
| Lateralidade | Direito/Esquerdo/Axial |
| Quantidade | Número de fragmentos |
| NMI | Contribuição para o NMI |

### Medições Ósseas

**Campo**: `tableWidget_misure`
**Base de dados**: `misure_ossa`

Medições osteométricas padrão.

---

## Separador Dados Tafonómicos

### Estado de Fragmentação

**Campo**: `comboBox_frammentazione`
**Base de dados**: `stato_frammentazione`

Grau de fragmentação dos restos.

**Valores:**
- Completo
- Ligeiramente fragmentado
- Fragmentado
- Muito fragmentado

### Estado de Conservação

**Campo**: `comboBox_conservazione`
**Base de dados**: `stato_conservazione`

Condições gerais de conservação.

**Valores:**
- Excelente
- Bom
- Razoável
- Mau
- Muito mau

### Vestígios de Combustão

**Campo**: `comboBox_combustione`
**Base de dados**: `tracce_combustione`

Presença de vestígios de fogo.

**Valores:**
- Ausente
- Enegrecimento
- Carbonização
- Calcinação

### Sinais Tafonómicos

**Campo**: `comboBox_segni_tafo`
**Base de dados**: `segni_tafonomici_evidenti`

Vestígios de alteração pós-deposicional.

**Tipos:**
- Meteorização (agentes atmosféricos)
- Marcas de raízes
- Roeduras
- Pisoteio

### Alterações Morfológicas

**Campo**: `textEdit_alterazioni`
**Base de dados**: `alterazioni_morfologiche`

Descrição detalhada das alterações observadas.

---

## Separador Dados Contextuais

### Metodologia de Recuperação

**Campo**: `comboBox_metodologia`
**Base de dados**: `metodologia_recupero`

Método de recolha dos restos.

**Valores:**
- Recolha manual
- Crivagem a seco
- Flutuação
- Crivagem húmida

### Restos em Conexão Anatómica

**Campo**: `checkBox_connessione`
**Base de dados**: `resti_connessione_anatomica`

Presença de partes conectadas.

### Classes de Achados Associados

**Campo**: `textEdit_associazioni`
**Base de dados**: `classi_reperti_associazione`

Outros materiais associados aos restos faunísticos.

### Observações

**Campo**: `textEdit_osservazioni`
**Base de dados**: `osservazioni`

Notas gerais.

### Interpretação

**Campo**: `textEdit_interpretazione`
**Base de dados**: `interpretazione`

Interpretação do contexto faunístico.

---

## Separador Estatísticas

Fornece ferramentas para:
- Gráficos de distribuição por espécie
- Cálculo do NMI total
- Comparações entre UEs/fases
- Exportação de dados estatísticos

---

## Fluxo de Trabalho Operacional

### Registo de Restos Faunísticos

1. **Abra a ficha**
   - Via menu ou barra de ferramentas

2. **Novo registo**
   - Clique em "Novo Registo"

3. **Dados de identificação**
   ```
   Sítio: Vila Romana
   Área: 1000
   UE: 150
   Responsável: G. Verdi
   Data: 20/07/2024
   ```

4. **Dados arqueozoológicos** (Separador 2)
   ```
   Contexto: Lixeira/Despejo
   Espécie: Bos taurus
   NMI: 3

   Partes esqueléticas:
   - Húmero / Direito / 2 / 1
   - Tíbia / Esquerdo / 3 / 2
   - Metápodo / - / 5 / 1
   ```

5. **Dados tafonómicos** (Separador 3)
   ```
   Fragmentação: Fragmentado
   Conservação: Bom
   Combustão: Ausente
   Sinais tafonómicos: Marcas de raízes
   ```

6. **Interpretação**
   ```
   Despejo de resíduos alimentares.
   Presença de marcas de corte
   em alguns ossos longos.
   ```

7. **Gravar**
   - Clique em "Gravar"

---

## Boas Práticas

### Identificação

- Utilize coleções de referência
- Indique o nível de certeza da identificação
- Registe também os restos não identificáveis

### NMI

- Calcule para cada espécie separadamente
- Considere a lateralidade e a idade dos achados
- Documente o método de cálculo

### Tafonomia

- Observe sistematicamente cada espécime
- Documente os vestígios antes da lavagem
- Fotografe os casos significativos

### Contexto

- Ligue sempre à UE de origem
- Registe o método de recuperação
- Anote as associações significativas

---

## Exportação PDF

A ficha permite gerar:
- Fichas individuais detalhadas
- Listas por UE ou fase
- Relatórios estatísticos

---

## Resolução de Problemas

### Problema: Espécie não disponível

**Causa**: Lista de espécies incompleta.

**Solução**:
1. Verifique o tesauro de fauna
2. Adicione as espécies em falta
3. Contacte o administrador

### Problema: NMI não calculado

**Causa**: Partes esqueléticas não registadas.

**Solução**:
1. Preencha a tabela de partes esqueléticas
2. Indique a lateralidade e quantidade
3. O sistema calculará automaticamente

---

## Referências

### Base de Dados

- **Tabela**: `fauna_table`
- **Classe mapper**: `FAUNA`
- **ID**: `id_fauna`

### Ficheiros Fonte

- **Controlador**: `tabs/Fauna.py`
- **Exportação PDF**: `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Tutorial em Vídeo

### Registo Arqueozoológico
**Duração**: 12-15 minutos
- Identificação taxonómica
- Registo de partes esqueléticas
- Análise tafonómica

[Marcador de posição de vídeo: video_archeozoologia.mp4]

### Estatísticas Faunísticas
**Duração**: 8-10 minutos
- Cálculo do NMI
- Gráficos de distribuição
- Exportação de dados

[Marcador de posição de vídeo: video_fauna_statistiche.mp4]

---

*Última atualização: janeiro de 2026*
*PyArchInit - Sistema de Gestão de Dados Arqueológicos*
