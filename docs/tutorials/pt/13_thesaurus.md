# Tutorial 13: Gestão do Tesauro

## Introdução

O **Tesauro** no PyArchInit é o sistema centralizado para a gestão de vocabulários controlados. Permite definir e manter as listas de valores utilizadas em todos os formulários do plugin, assegurando a consistência terminológica e facilitando a pesquisa.

### Funções Principais

- Gestão de vocabulários para cada formulário
- Suporte multilingue
- Códigos e descrições alargadas
- Integração GPT para sugestões
- Importação/exportação de ficheiros CSV

---

## Aceder ao Tesauro

### Via Menu
1. Menu **PyArchInit** na barra de menus do QGIS
2. Selecione **Tesauro** (ou **Ficha Tesauro**)

### Via Barra de Ferramentas
1. Localize a barra de ferramentas do PyArchInit
2. Clique no ícone **Tesauro** (livro/dicionário)

---

## Vista Geral da Interface

### Áreas Principais

| # | Área | Descrição |
|---|------|-----------|
| 1 | Barra SGBD | Navegação, pesquisa, gravar |
| 2 | Seleção de Tabela | Escolha do formulário a configurar |
| 3 | Campos de Código | Código, extensão, tipo |
| 4 | Descrição | Descrição detalhada do termo |
| 5 | Idioma | Seleção do idioma |
| 6 | Ferramentas | Importação CSV, sugestões GPT |

---

## Campos do Tesauro

### Nome da Tabela

**Campo**: `comboBox_nome_tabella`
**Base de dados**: `nome_tabella`

Selecione o formulário para o qual deseja definir valores.

**Tabelas disponíveis:**
| Tabela | Descrição |
|--------|-----------|
| `us_table` | Ficha UE/UEM |
| `site_table` | Ficha Sítio |
| `periodizzazione_table` | Periodização |
| `inventario_materiali_table` | Inventário de Materiais |
| `pottery_table` | Ficha Cerâmica |
| `campioni_table` | Ficha Amostras |
| `documentazione_table` | Documentação |
| `tomba_table` | Ficha Sepultura |
| `individui_table` | Ficha Indivíduo |
| `fauna_table` | Arqueozoologia |
| `ut_table` | Ficha UT |

### Código

**Campo**: `comboBox_sigla`
**Base de dados**: `sigla`

Código curto/abreviatura do termo.

**Exemplos:**
- `MR` para Muro
- `UE` para Unidade Estratigráfica
- `CR` para Cerâmica

### Código Alargado

**Campo**: `comboBox_sigla_estesa`
**Base de dados**: `sigla_estesa`

Forma completa do termo.

**Exemplos:**
- `Muro perimetral`
- `Unidade Estratigráfica`
- `Cerâmica comum`

### Descrição

**Campo**: `textEdit_descrizione_sigla`
**Base de dados**: `descrizione`

Descrição detalhada do termo, definição, notas de utilização.

### Tipo de Código

**Campo**: `comboBox_tipologia_sigla`
**Base de dados**: `tipologia_sigla`

Código numérico que identifica o campo de destino.

**Estrutura do código:**
```
X.Y onde:
X = número da tabela
Y = número do campo
```

**Exemplos para us_table:**
| Código | Campo |
|--------|-------|
| 1.1 | Definição estratigráfica |
| 1.2 | Modo de formação |
| 1.3 | Tipo de UE |

### Idioma

**Campo**: `comboBox_lingua`
**Base de dados**: `lingua`

Idioma do termo.

**Idiomas suportados:**
- IT (Italiano)
- EN_US (Inglês)
- DE (Alemão)
- FR (Francês)
- ES (Espanhol)
- AR (Árabe)
- CA (Catalão)

---

## Campos de Hierarquia

### ID Pai

**Campo**: `comboBox_id_parent`
**Base de dados**: `id_parent`

ID do termo pai (para estruturas hierárquicas).

### Código Pai

**Campo**: `comboBox_parent_sigla`
**Base de dados**: `parent_sigla`

Código do termo pai.

### Nível Hierárquico

**Campo**: `spinBox_hierarchy`
**Base de dados**: `hierarchy_level`

Nível na hierarquia (0=raiz, 1=primeiro nível, etc.).

---

## Funcionalidades Especiais

### Sugestões GPT

O botão "Sugestões" utiliza o OpenAI GPT para:
- Gerar descrições automáticas
- Fornecer ligações de referência da Wikipédia
- Sugerir definições em contexto arqueológico

**Utilização:**
1. Selecione ou introduza um termo em "Código alargado"
2. Clique em "Sugestões"
3. Selecione o modelo GPT
4. Aguarde a geração
5. Reveja e grave

**Nota:** Requer chave API OpenAI configurada.

### Importação CSV

Para bases de dados SQLite, os vocabulários podem ser importados de ficheiros CSV.

**Formato CSV necessário:**
```csv
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,MR,Muro,Estrutura de muro,1.3,EN_US
us_table,PV,Pavimento,Superfície de circulação,1.3,EN_US
```

**Procedimento:**
1. Clique em "Importar CSV"
2. Selecione o ficheiro
3. Confirme a importação
4. Verifique os dados importados

---

## Fluxo de Trabalho Operacional

### Adicionar um Novo Termo

1. **Abra o Tesauro**
   - Via menu ou barra de ferramentas

2. **Novo registo**
   - Clique em "Novo Registo"

3. **Seleção da tabela**
   ```
   Nome da tabela: us_table
   ```

4. **Definição do termo**
   ```
   Código: PC
   Código alargado: Poço
   Tipo de código: 1.3
   Idioma: EN_US
   ```

5. **Descrição**
   ```
   Estrutura escavada no solo para
   abastecimento de água. Geralmente de
   forma circular com revestimento de
   pedra ou tijolo.
   ```

6. **Gravar**
   - Clique em "Gravar"

### Pesquisar Termos

1. Clique em "Nova Pesquisa"
2. Preencha os critérios:
   - Nome da tabela
   - Código ou código alargado
   - Idioma
3. Clique em "Pesquisar"
4. Navegue pelos resultados

### Modificar um Termo Existente

1. Pesquise o termo a modificar
2. Modifique os campos necessários
3. Clique em "Gravar"

---

## Organização dos Tipos de Código

### Estrutura Recomendada

Para cada tabela, organize os códigos sistematicamente:

**us_table (1.x):**
| Código | Campo |
|--------|-------|
| 1.1 | Definição estratigráfica |
| 1.2 | Modo de formação |
| 1.3 | Tipo de UE |
| 1.4 | Consistência |
| 1.5 | Cor |

**inventario_materiali_table (2.x):**
| Código | Campo |
|--------|-------|
| 2.1 | Tipo de achado |
| 2.2 | Classe de material |
| 2.3 | Definição |
| 2.4 | Estado de conservação |

**pottery_table (3.x):**
| Código | Campo |
|--------|-------|
| 3.1 | Forma |
| 3.2 | Classe cerâmica |
| 3.3 | Pasta |
| 3.4 | Tratamento de superfície |

---

## Boas Práticas

### Consistência Terminológica

- Utilize sempre os mesmos termos para os mesmos conceitos
- Evite sinónimos não documentados
- Documente as convenções adotadas

### Multilingue

- Crie termos em todos os idiomas necessários
- Mantenha as correspondências entre idiomas
- Utilize traduções oficiais quando disponíveis

### Hierarquia

- Utilize a estrutura hierárquica para termos relacionados
- Defina claramente os níveis
- Documente as relações

### Manutenção

- Reveja periodicamente os vocabulários
- Remova termos obsoletos
- Atualize as descrições

---

## Resolução de Problemas

### Problema: Termo não visível nas ComboBoxes

**Causa:** Código de tipo incorreto ou idioma não correspondente.

**Solução:**
1. Verifique o código tipologia_sigla
2. Verifique o idioma definido
3. Verifique se o registo está gravado

### Problema: Importação CSV falhou

**Causa:** Formato de ficheiro incorreto.

**Solução:**
1. Verifique a estrutura CSV
2. Verifique os delimitadores (vírgula)
3. Verifique a codificação (UTF-8)

### Problema: Sugestões GPT não funcionam

**Causa:** Chave API em falta ou inválida.

**Solução:**
1. Verifique a configuração da chave API
2. Verifique a ligação à internet
3. Verifique o crédito OpenAI

---

## Referências

### Base de Dados

- **Tabela**: `pyarchinit_thesaurus_sigle`
- **Classe mapper**: `PYARCHINIT_THESAURUS_SIGLE`
- **ID**: `id_thesaurus_sigle`

### Ficheiros Fonte

- **UI**: `gui/ui/Thesaurus.ui`
- **Controlador**: `tabs/Thesaurus.py`

---

## Tutorial em Vídeo

### Gestão de Vocabulários
**Duração**: 10-12 minutos
- Estrutura do tesauro
- Adição de termos
- Organização de códigos

[Marcador de posição de vídeo: video_thesaurus_gestione.mp4]

### Multilingue e Importação
**Duração**: 8-10 minutos
- Configuração de idiomas
- Importação CSV
- Sugestões GPT

[Marcador de posição de vídeo: video_thesaurus_avanzato.mp4]

---

*Última atualização: janeiro de 2026*
*PyArchInit - Sistema de Gestão de Dados Arqueológicos*

---

## Animação Interativa

Explore a animação interativa para saber mais sobre este tema.

[Abrir Animação Interativa](../../animations/pyarchinit_thesaurus_animation.html)
