# Tutorial 12: Relatórios e Impressões PDF

## Introdução

O PyArchInit oferece um sistema completo de geração de **relatórios PDF** para todas as fichas arqueológicas. Esta funcionalidade permite exportar documentação em formato imprimível, conforme os padrões ministeriais e pronta para arquivamento.

### Tipos de Relatórios Disponíveis

| Tipo | Descrição | Ficha de Origem |
|------|-----------|-----------------|
| Fichas UE | Relatórios completos UE/UEM | Ficha UE |
| Índice UE | Lista sintética das UEs | Ficha UE |
| Fichas Periodização | Relatórios período/fase | Ficha Periodização |
| Fichas Estrutura | Relatórios de estruturas | Ficha Estrutura |
| Fichas Achados | Relatórios inventário de materiais | Ficha Inventário |
| Fichas Sepultura | Relatórios funerários | Ficha Sepultura |
| Fichas Amostras | Relatórios de amostras | Ficha Amostras |
| Fichas Indivíduo | Relatórios antropológicos | Ficha Indivíduo |

## Aceder à Função

### A partir do Menu Principal
1. **PyArchInit** na barra de menus
2. Selecione **Exportar PDF**

### A partir da Barra de Ferramentas
Clique no ícone **PDF** na barra de ferramentas do PyArchInit

## Interface de Exportação

### Vista Geral da Janela

A janela de exportação PDF apresenta:

```
+------------------------------------------+
|        PyArchInit - Exportar PDF          |
+------------------------------------------+
| Sítio: [ComboBox seleção sítio]   [v]   |
+------------------------------------------+
| Fichas a exportar:                        |
| [x] Fichas UE                            |
| [x] Fichas Periodização                  |
| [x] Fichas Estrutura                     |
| [x] Fichas Achados                       |
| [x] Fichas Sepultura                     |
| [x] Fichas Amostras                      |
| [x] Fichas Indivíduo                     |
+------------------------------------------+
| [Abrir Pasta]  [Exportar PDF]  [Cancelar]|
+------------------------------------------+
```

### Seleção do Sítio

| Campo | Descrição |
|-------|-----------|
| ComboBox Sítio | Lista de todos os sítios na base de dados |

**Nota**: A exportação é por sítio individual. Para exportar múltiplos sítios, repita a operação.

### Caixas de Seleção

Cada caixa de seleção ativa a exportação de um tipo específico:

| Caixa | Gera |
|-------|------|
| Fichas UE | Fichas completas + Índice UE |
| Fichas Periodização | Fichas de períodos + Índice |
| Fichas Estrutura | Fichas de estruturas + Índice |
| Fichas Achados | Fichas de materiais + Índice |
| Fichas Sepultura | Fichas funerárias + Índice |
| Fichas Amostras | Fichas de amostras + Índice |
| Fichas Indivíduo | Fichas antropológicas + Índice |

## Processo de Exportação

### Passo 1: Seleção de Dados

```python
# O sistema executa para cada tipo selecionado:
1. Consulta à base de dados para o sítio selecionado
2. Ordenação dos dados (por número, área, etc.)
3. Preparação da lista para geração
```

### Passo 2: Geração de PDF

Para cada tipo de ficha:
1. **Ficha individual**: PDF detalhado para cada registo
2. **Índice**: PDF resumido com todos os registos

### Passo 3: Gravação

Saída para a pasta:
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Conteúdo dos Relatórios

### Ficha UE

Informações incluídas:
- **Dados de identificação**: Sítio, Área, Número UE, Tipo de unidade
- **Definições**: Estratigráfica, Interpretativa
- **Descrição**: Texto descritivo completo
- **Interpretação**: Análise interpretativa
- **Periodização**: Período/Fase Inicial/Final
- **Características físicas**: Cor, consistência, formação
- **Medições**: Cotas min/max, dimensões
- **Relações**: Lista de relações estratigráficas
- **Documentação**: Referências gráficas e fotográficas
- **Dados UEM**: (se aplicável) Técnica construtiva, materiais

### Índice UE

Tabela resumida com colunas:
| Sítio | Área | UE | Def. Estratigráfica | Def. Interpretativa | Período |

### Ficha Periodização

- Sítio
- Número do período
- Número da fase
- Cronologia inicial/final
- Datação alargada
- Descrição do período

### Ficha Estrutura

- Dados de identificação (Sítio, Código, Número)
- Categoria, Tipo, Definição
- Descrição e Interpretação
- Periodização
- Materiais utilizados
- Elementos estruturais
- Relações de estruturas
- Medições e cotas

### Ficha Achados

- Sítio, Número de inventário
- Tipo de achado, Definição
- Descrição
- Proveniência (Área, UE)
- Estado de conservação
- Datação
- Elementos e medições
- Bibliografia

### Ficha Sepultura

- Dados de identificação
- Rito (inumação/cremação)
- Tipo de enterramento e deposição
- Descrição e interpretação
- Espólio (presença, tipo, descrição)
- Periodização
- Cotas da estrutura e do indivíduo
- UEs associadas

### Ficha Amostras

- Sítio, Número da amostra
- Tipo de amostra
- Descrição
- Proveniência (Área, UE)
- Local de conservação
- Número da caixa

### Ficha Indivíduo

- Dados de identificação
- Sexo, Idade (min/max), Classes etárias
- Posição do esqueleto
- Orientação (eixo, azimute)
- Estado de conservação
- Observações

## Idiomas Suportados

O sistema gera relatórios com base no idioma do sistema:

| Idioma | Código | Modelo |
|--------|--------|--------|
| Italiano | IT | `build_*_sheets()` |
| Alemão | DE | `build_*_sheets_de()` |
| Inglês | EN | `build_*_sheets_en()` |

O idioma é automaticamente detetado a partir das configurações do QGIS.

## Pasta de Saída

### Caminho Padrão
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Estrutura dos Ficheiros Gerados

```
pyarchinit_PDF_folder/
├── US_[sítio]_forms.pdf           # Fichas UE completas
├── US_[sítio]_index.pdf           # Índice UE
├── Periodization_[sítio].pdf      # Fichas periodização
├── Structure_[sítio]_forms.pdf    # Fichas estruturas
├── Structure_[sítio]_index.pdf    # Índice estruturas
├── Finds_[sítio]_forms.pdf        # Fichas achados
├── Finds_[sítio]_index.pdf        # Índice achados
├── Grave_[sítio]_forms.pdf        # Fichas sepulturas
├── Sample_[sítio]_forms.pdf       # Fichas amostras
├── Individual_[sítio]_forms.pdf   # Fichas indivíduo
└── ...
```

### Abrir Pasta

O botão **"Abrir Pasta"** abre diretamente o diretório de saída no gestor de ficheiros do sistema.

## Personalização dos Relatórios

### Modelos PDF

Os modelos são definidos nos módulos:
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Biblioteca Utilizada

Os PDFs são gerados com **ReportLab**, que permite:
- Layouts personalizáveis
- Inserção de imagens
- Tabelas formatadas
- Cabeçalhos/rodapés

### Fontes Necessárias

O sistema utiliza fontes específicas:
- **Cambria** (fonte principal)
- Instalação automática no primeiro arranque do plugin

## Fluxo de Trabalho Recomendado

### 1. Preparação dos Dados

```
1. Complete todas as fichas do sítio
2. Verifique a completude dos dados
3. Verifique a periodização
4. Verifique as relações estratigráficas
```

### 2. Exportação

```
1. Abra Exportar PDF
2. Selecione o sítio
3. Selecione os tipos de fichas
4. Clique em "Exportar PDF"
5. Aguarde a conclusão
```

### 3. Verificação

```
1. Abra a pasta de saída
2. Verifique os PDFs gerados
3. Verifique a formatação
4. Imprima ou archive
```

## Resolução de Problemas

### Erro: "Nenhuma ficha para imprimir"

**Causa**: Nenhum registo encontrado para o tipo selecionado

**Solução**:
- Verifique se existem dados para o sítio selecionado
- Verifique a base de dados

### PDFs Vazios ou Incompletos

**Causas possíveis**:
1. Campos obrigatórios não preenchidos
2. Problemas de codificação de caracteres
3. Fontes em falta

**Soluções**:
- Complete os campos obrigatórios
- Verifique a instalação da fonte Cambria

### Erro de Fonte

**Causa**: Fonte Cambria não instalada

**Solução**:
- O plugin tenta instalação automática
- Se houver problemas, instale manualmente

### Exportação Lenta

**Causa**: Muitos registos para exportar

**Solução**:
- Exporte por tipo separadamente
- Aguarde a conclusão

## Boas Práticas

### 1. Organização

- Exporte regularmente durante a escavação
- Crie cópias de segurança dos PDFs gerados
- Organize por campanha/ano

### 2. Completude dos Dados

- Preencha todos os campos antes da exportação
- Verifique as cotas a partir das medições GIS
- Verifique as relações estratigráficas

### 3. Arquivo

- Guarde os PDFs em suporte seguro
- Inclua na documentação final
- Anexe ao relatório de escavação

### 4. Impressão

- Utilize papel sem ácido para arquivo
- Imprima em formato A4
- Encaderne por campanha

## Integração com Outras Funções

### Cotas do GIS

O sistema recupera automaticamente:
- Cotas mínimas e máximas das geometrias
- Referências aos planos GIS

### Documentação Fotográfica

Os relatórios podem incluir referências a:
- Fotografias associadas
- Desenhos e levantamentos

### Periodização

Os relatórios UE incluem automaticamente:
- Datação alargada do período/fase atribuído
- Referências cronológicas

## Referências

### Ficheiros Fonte
- `tabs/Pdf_export.py` - Interface de exportação
- `modules/utility/pyarchinit_exp_*_pdf.py` - Geradores PDF

### Dependências
- ReportLab (geração PDF)
- Fonte Cambria

---

## Tutorial em Vídeo

### Exportação PDF Completa
`[Marcador de posição: video_export_pdf.mp4]`

**Conteúdos**:
- Seleção de sítio e fichas
- Processo de exportação
- Verificação da saída
- Organização do arquivo

**Duração estimada**: 10-12 minutos

---

*Última atualização: janeiro de 2026*
