# Tutorial 36: Exportação Extended Matrix e Bridge s3dgraphy

## Introdução

A partir da versão **5.2.0-alpha** o PyArchInit integra um **bridge bidirecional** com a biblioteca **s3dgraphy** (modelo de dados Extended Matrix de Emanuel Demetrescu). O bridge permite:

- **Exportar** o diagrama estratigráfico como Extended Matrix em GraphML (com swimlanes temporais, redução transitiva, edge styling EM 1.5)
- **Reimportar** alterações feitas no yEd (movimentos de UE entre períodos/grupos) atualizando a base SQL
- **Anexar paradata** (Author / License / Embargo) a nível de sítio
- **Agrupar** UE por dimensão (struttura, area, attivita, settore, ambient, saggio, quad_par ou grupos ad-hoc)

Tag atual: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Requisitos

- Base de dados SQLite (PostgreSQL ainda não suportado)
- **Migração Phase 1 node_uuid** aplicada automaticamente ao abrir o DB
- **yEd Graph Editor** para visualizar a saída (https://www.yworks.com/products/yed)

> ⚠️ Para DB pre-5.2.0-alpha a migração pode requerer reiniciar o QGIS.

---

## 2. Exportar Extended Matrix (botão verde)

### 2.1 Abrir o diálogo

1. Abre a **Ficha UE** do sítio desejado
2. Clica no botão verde **"Esporta Extended Matrix"** (debaixo do tab Rapporti)

### 2.2 Aba "Export"

O diálogo mostra:

- **Output formats**: marca DOT / GraphML / JSON / phased JSON (recomendado: GraphML)
- **Group US by (optional)**: 7 checkboxes de dimensões + 1 "ad-hoc"
  - As dimensões com valores no DB são **autoselecionadas** ao abrir
- **Caixa de seleção dimensão primária** (predefinição `struttura`): quando uma UE tem pertença em 2+ dimensões, a primária ganha como folder yEd visível (parent hierárquico). As outras dimensões aparecem como etiquetas inline sob o nó UE. `toponym` nunca é primária, independentemente da seleção.
- **"Select Output Directory"**: pasta de destino

A partir de 5.6.0-alpha podes marcar **2+ dimensões**: a exportação funciona nativamente graças ao modelo m:n com `is_primary` (ver secção "Pertença multidimensional").

### 2.3 Clica em "Export"

São gerados 4 ficheiros com prefixo `Extended_Matrix_<sítio>[_<area>]`:
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix para yEd (alvo principal)
- `_s3dgraphy.json` — formato nativo s3dgraphy
- `_phased.json` — vista por época

---

## 3. Diálogo "Manage paradata" (4 abas)

### 3.1 Acesso
Clica no botão **"Manage paradata"** na ficha UE (ao lado do botão verde Export).

### 3.2 As 4 abas

| Aba | Conteúdo | Ficheiro gerado |
|---|---|---|
| **Authors** | Adicionar autores (nome + ORCID + papel) | `paradata_<sítio>.graphml` |
| **Licenses** | Licença do dataset (ex. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Datas de embargo + motivo | idem |
| **Groups** | Grupos ad-hoc (nome + seleção UE membros) | `groups_<sítio>.graphml` |

Os ficheiros são guardados ao lado do DB SQLite e são **versionáveis em Git**.

---

## 4. Estilo visual por dimensão (5.5.1-alpha + 5.6.0-alpha)

Cada dimensão de agrupamento tem uma cor distintiva em GraphML:

| Dimensão | Fill (50% transparência) | Border |
|---|---|---|
| `area` | rosa pastel `#FFE0E680` | `#C84A5F` |
| `struttura` | laranja pastel `#FFE6CC80` | `#C66B33` |
| `attivita` | amarelo pastel `#FFF5CC80` | `#A89A33` |
| `settore` | verde pastel `#E6FFCC80` | `#6BC633` |
| `ambient` | água pastel `#CCFFE680` | `#33A86B` |
| `saggio` | azul pastel `#CCF5FF80` | `#3389A8` |
| `quad_par` | violeta pastel `#E0CCFF80` | `#6633C6` |
| `adhoc` | cinza pastel `#F5F5F580` | `#666666` |

A partir de 5.6.0-alpha, os `LocationNodeGroup` são distinguidos por `kind`:

| `kind` | Fill (50% transparência) | Border |
|---|---|---|
| `toponym` | lavanda pastel `#E6E6FA80` | `#9370DB` |
| `study` | marfim pastel `#FFFFE080` | `#888888` |
| `functional` | ciano pastel `#E0FFFF80` | `#008B8B` |

O alpha 50% deixa visíveis as swimlanes das épocas atrás do retângulo do grupo.

### 4.1 Cadeia toponímica (5.6.0-alpha)

Os campos `site_table.{nazione, regione, provincia, comune}` são emitidos automaticamente como uma cadeia recursiva de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Os níveis administrativos vazios são saltados sem quebrar a cadeia. Uma desduplicação cross-sítio garante que a mesma `comune` presente em 2 sítios se torne **um único nó partilhado** no GraphML.

---

## 4.2 Pertença multidimensional (5.6.0-alpha)

A partir de 5.6.0-alpha uma UE pode pertencer a **múltiplas dimensões em simultâneo** graças ao modelo m:n com flag `is_primary`. Apenas a dimensão primária se torna o folder yEd visível; as outras aparecem como **etiquetas inline** sob o nó UE e como JSON em `<data key="s3d:other_locations">` para ferramentas downstream.

Exemplo: uma UE com `struttura=basilica` e `area=B` (primária `struttura`) produz:
- folder yEd "struttura: basilica" como parent visível;
- sob o nó UE, uma etiqueta inline `also: B (study), TestCity (toponym)`;
- no GraphML, o atributo `s3d:other_locations` com array JSON das pertenças secundárias.

A dimensão primária controla-se via caixa de seleção em §2.2.

---

## 5. Round-trip (aba Import)

Para modificar a base SQL movendo UE entre grupos em GraphML:

1. Abre o GraphML no **yEd**
2. Arrasta uma UE para outro grupo, guarda
3. Volta ao diálogo → aba **"Import"**
4. **Marca** a checkbox *"Update SQL on import (struttura/area/...)"*
5. Carrega o GraphML modificado

O sistema executa uma transação atómica: se algo falhar, **rollback completo** (o DB fica inalterado). Os grupos `adhoc` nunca escrevem SQL — apenas atualizam `groups_<sítio>.graphml`.

A partir de 5.6.0-alpha o walker de import é **recursivo** e suporta folders aninhados (p. ex. cadeia toponímica `nazione > regione > provincia > comune > UE`). Quando ciclos são detetados no grafo de folders, é levantada a exceção `CycleDetectedError` e o import é abortado com rollback.

---

## 6. CLI (alternativa ao diálogo)

Para scripts / batch:

```bash
# Exportar
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Listar grupos ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Adicionar autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = sucesso, 1 = erro de bridge, 2 = erro argparse.

---

## 7. Resolução de problemas

| Sintoma | Causa | Solução |
|---|---|---|
| "no such column: node_uuid" | Migração Phase 1 não executada | Reiniciar QGIS, reabrir o DB |
| GraphML vazio | DB sem rapporti / filtro de area demasiado restrito | Verificar us_table.rapporti |
| "rapporti devem ser TEXT" | Inseriste um número como integer | Os campos UE/Area são **TEXT**, não integer |
| Capitalização errada em rapporti | "copre" minúsculo no DB | Usa "Copre", "Coperto da" capitalizados |
| `DeprecationWarning` em ficheiro 5.5.x | Ficheiro legacy `ActivityNodeGroup + group_kind` | O projector promove-o em memória para `LocationNodeGroup`. Reexporta para migrar o ficheiro em disco. |

---

## 8. Documentação técnica

Para aprofundar arquitetura, decisões de design e roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over diferidos:
- **AI08-F3**: heurísticas de auto-layout (bin-packing de sub-grupos) — ainda diferido
- **AI09**: TimeBranchNodeGroup mapping — futuro
- **Phase 3**: SyncEngine + REST API — futuro
- **Phase 4**: GraphDBBackend + SPARQL — futuro

Entregues:
- **AI07** (5.6.0-alpha, 2026-05-10): migração `LocationNodeGroup` com enum `kind` + cadeia toponímica + pertenças multidimensionais
- **AI08-F1** (fundido em AI07): nesting hierárquico nativo via `is_primary`

---

## 5. yEd-aware Import — importar graphmls editados externamente (5.8.x)

A partir de **5.8.0-alpha** a bridge é **bidirecional também para graphmls criados diretamente em yEd** (isto é, sem passar antes por uma exportação pyarchinit). O pyarchinit reconhece automaticamente os graphmls «yEd-raw» — aqueles que não trazem data keys `pyarchinit.*` — e importa-os através de um dispatch dedicado que mapeia o prefixo do label do nó → tipo estratigráfico, reconhece linhas de TableNode como períodos, percorre os group folder como dimensões arqueológicas e deixa o utilizador escolher uma política para as edges que tocam folders.

### 5.1 Lançamento em 6 marcos

| Marco | Tag | O que adiciona |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` com 13 valores (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate a partir das linhas de TableNode) + `yed_group_walker.py` (FolderCandidate com auto-dimension a partir do prefixo do label: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orquestrador `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + sentinela `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` com 5 páginas (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistência sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Esta documentação + dev-log + CHANGELOG. |

### 5.2 Como funciona — fluxo do utilizador

1. **Abra um graphml no QGIS através do menu Import GraphML** (mesmo path do fluxo pyarchinit-projected existente).
2. O pyarchinit deteta automaticamente que é yEd-raw (sem keys `pyarchinit.*`) → faz dispatch para o novo branch em vez de cair no path legacy.
3. Abre-se o assistente `YedImportDialog` com **5 páginas**:
   - **1/5 Classifier** — tabela com uma linha por leaf node. Cada linha mostra `label` + `auto_kind` (por ex. `us_real` / `usv_virtual` / `property`) + uma combobox de override `user_kind`. O botão **Aceitar auto** repõe cada linha no seu `auto_kind` (limpa todos os overrides).
   - **2/5 Periods** — uma linha por TableNode-row parseada, colunas editáveis `periodo` + `fase`. As datas (`datazione_iniziale`/`finale`) ficam vazias: os graphmls yEd-raw não trazem datas.
   - **3/5 Folders** — uma linha por group folder. Combobox de `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` para excluir). `value` editável (default = `auto_value` derivado do prefixo do label).
   - **4/5 Rapporti policy** — 4 radio buttons para tratar as edges que tocam folders:
     - **SKIP** (default): descarta as edges folder-touching. As edges leaf-to-leaf passam intactas.
     - **FAN_OUT**: uma edge `folder_A → folder_B` expande-se para `N×M` pares de leaves (produto cartesiano dos membros).
     - **REPRESENTATIVE**: usa o primeiro membro de cada folder como proxy.
     - **SYNTHETIC**: cria uma linha us_table por folder (`unita_tipo='VA'` virtual activity) + reconecta as edges através destas âncoras.
   - **5/5 Preview** — dry-run de `import_yed_raw(overrides=..., dry_run=True)`. Mostra counts (us / inv / period / paradata) **sem commit**. Clicar **Finish** confirma, **Cancel** abandona.
4. Em **Finish** o assistente guarda os seus overrides num **sidecar JSON** `<graphml>.yed_overrides.json` ao lado do ficheiro. Reabrir o mesmo graphml pré-carrega o sidecar, pelo que os seus overrides anteriores voltam pré-aplicados.

### 5.3 Encaminhamento de destinos

O dispatch usa `_classify_destination` (em `yed_import_pipeline.py`) para classificar cada leaf:

| ClassificationKind | Destino | Nota |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | a partir do label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | a partir de `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | a partir de `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | a partir de `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derivado do prefixo do label: USVs/USVn/USVc) | a partir de `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | a partir de `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | a partir de `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | a partir de `^VSF\d+` |
| DOCUMENT | `paradata` | a partir de `^D\.\d+` |
| COMBINER | `paradata` | a partir de `^C\.\d+` |
| PROPERTY | `paradata` | keyword no label (`material`/`position`/`width`/...) |

**Decisão do utilizador 2026-05-13**: as USV* (virtuais) são «unità tipo» (continuam unidades estratigráficas) e vão para `us_table`, não para paradata. Apenas DOC/COMB/PROP/VIRTUAL_FIND permanecem em paradata.

### 5.4 Sidecar JSON — esquema

Versionado para forward-compat:

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Só os campos MODIFICADOS pelo utilizador são persistidos (diff). Valores `ClassificationKind` desconhecidos (por ex. de futuras releases de s3dgraphy) são silenciosamente ignorados ao carregar.

### 5.5 CLI para ingest scripted

Para CI / re-runs em batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` para backend SQLite vs PostgreSQL. `--overrides` é opcional (sem overrides = defaults yE-D). `--auto-defaults` é uma flag no-op forward-compat.

### 5.6 Limitações conhecidas

- **Sem edição de datas no assistente**: os graphmls yEd-raw não trazem `datazione_iniziale`/`datazione_finale`. A página Periods só edita `periodo` + `fase` (targets FK).
- **API ParadataStore parcial**: o upstream s3dgraphy ainda não fornece `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. O yE-D regista «skip — method missing» por cada leaf paradata mas contabiliza as tentativas no preview.
- **PropertyNode → Path B (sem ligação a US)**: os nós PROPERTY são escritos sem US alvo. O assistente emite um warning. Futuro: follow-up yE-Closure para adicionar «assign target» na UI.
- **Multi-DB**: o sidecar JSON é por graphml, não por DB. Importar o mesmo graphml em DBs diferentes reutiliza os mesmos overrides para todas.

### 5.7 Cobertura de testes final

| Suite | Test | Cobertura |
|---|---|---|
| yE-A | `test_yed_detector.py` | deteção de flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | políticas + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistência sidecar + CLI |

**Suite total pós-rollout**: 354 passed / 42 skipped (PG-L1 requerem psycopg2).

### 5.8 Atualização 5.8.5-alpha (yed-fastfix)

Pack de correções de comportamento sobre `5.8.3-alpha` que melhora a qualidade do re-export GraphML após um import yEd-aware. Alterações relevantes para o utilizador final:

- **Paradata multi-folder**: as labels DOC / Combinar / Extractor / property partilhadas entre vários folders yEd (p. ex. `material` referenciado a partir de VA01 + VA04 + VA05) geram agora UMA linha em `us_table` POR ocorrência — visibilidade multi-folder restaurada no GraphML re-exportado. Compromisso: o dedup por identidade (colapso de `D.01` / `D.01-2` / `D.01bis` numa única linha) já não se aplica à segunda/terceira ocorrência.
- **Rapporti recíprocos**: cada edge yEd `a → b` escreve o rapporto direto na linha de `a` E o inverso na linha de `b` (`<<` / «Coperto da» / etc.). Os DOC mostram agora todas as ligações extractor de entrada no formulário Scheda US.
- **Strip do prefixo `us` numérico**: `US100` → `us='100'` `unita_tipo='US'` (antes `us='US100'`). SF/VSF/RSF são escritos em modo dual em `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase**: a pertença de uma linha TableNode yEd a um período propaga-se para `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — preserva a distinção semântica EM 1.5.
- **Re-import idempotente**: voltar a executar o mesmo import salta as linhas já presentes; sem rollback por colisão UNIQUE na passagem repetida.
- **Paleta USV**: os nós USV renderizam-se agora com o paralelogramo azul canónico EM (antes retângulo com borda vermelha).

### 5.9 yE-F paradata multi-pasta (5.9.0-alpha)

Evolução estrutural de `yed-fastfix-5.8.5-alpha`: o compromisso do Bug R B1 (uma linha `us_table` por ocorrência, com `us='D.01_2'` / `us='D.01_3'`) foi superado. Uma folha paradata (DOC / Combinar / Extractor / property) partilhada entre várias pastas yEd produz agora **uma única linha** em `us_table` por label canónico, e a multi-pertença é preservada numa nova coluna `other_locations`.

Alterações visíveis para o utilizador final:

1. **Novo widget "Outras atividades" na ficha US/USM**: no separador *Periodizzazione* aparece um `QListWidget` etiquetado "Outras atividades" — visível **apenas** quando `unita_tipo` é uma tipologia paradata (`DOC`, `Combinar`, `Extractor`, `property`). O utilizador pode selecionar vários códigos de atividade; a seleção é serializada como lista JSON na nova coluna `other_locations`.
2. **Novo item de menu QGIS**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Tem de ser executado **uma vez** em cada DB preexistente para adicionar a nova coluna (as DB criadas pós-5.9 já têm a coluna).
3. **Import yEd-aware melhorado**: uma folha paradata que aparece em N pastas yEd gera agora **apenas 1** linha `us_table` (já não N linhas com sufixo `_2`/`_3` como em 5.8.5). A primeira pasta encontrada torna-se a `attivita` principal; as pastas secundárias são listadas em `other_locations`. No **export** são emitidas N cópias visuais yEd (uma por pasta), todas partilhando o mesmo `node_uuid` canónico para garantir a identidade round-trip.

**Retrocompatibilidade**: os dados produzidos pelo Bug R B1 em 5.8.5-alpha (linhas com sufixo `_2`/`_3`) permanecem legíveis sem qualquer conversão automática. A lógica nova aplica-se aos novos imports; as linhas legacy continuam a comportar-se como antes.

Predecessor: ver secção 5.8 (`yed-fastfix-5.8.5-alpha`) para o comportamento substituído.

---

## 6. Gerar continuidade (fichas CON)

No painel **«Verifica rapporti»** — disponível como separador dentro do diálogo de importação/exportação do s3dgraphy — encontra-se o botão **«Genera continuità»** (rótulo mantido em italiano como no plugin). Para o sítio atualmente selecionado, esta funcionalidade cria automaticamente as **fichas de continuidade** das US/USM cuja vida se estende por mais de um período.

### 6.1 O que faz

1. Percorre todas as US/USM do sítio em que **período inicial ≠ período final** (ou seja, cuja vida se estende por mais do que um período).
2. Para cada uma cria ou atualiza uma ficha de continuidade chamada **`CON_<us>`** (p. ex. `US5` → `CON_US5`).
3. A ficha CON **herda** da unidade-mãe: sítio, área (mais as áreas secundárias), estrutura e todo o intervalo de períodos (inicial → final). A sua descrição é gerada automaticamente.
4. Escreve uma **relação de continuidade recíproca** em ambos os lados: na CON e na sua unidade-mãe.

### 6.2 Idempotência

A operação é **idempotente**: voltar a executá-la não duplica as fichas existentes — atualiza as `CON_<us>` existentes se os dados da unidade-mãe tiverem mudado.

### 6.3 Pré-visualização (dry-run) e cópia de segurança

Antes de escrever é mostrada uma **pré-visualização dry-run** com as contagens: quantas fichas há a **criar**, a **atualizar**, **inalteradas** e quantas **órfãs**. As alterações são aplicadas **apenas após confirmação** (botão «Genera»). Ao aplicar é feita primeiro uma **cópia de segurança da base de dados** automática.

Uma ficha CON é **órfã** quando a sua unidade-mãe já não se estende por vários períodos (p. ex. o seu período inicial e final foram tornados iguais). Por predefinição as órfãs são apenas **assinaladas**; uma **caixa de seleção** («Rimuovi anche le CON orfane») permite optar por removê-las.

### 6.4 Na exportação Extended Matrix

As fichas `CON_<us>` geradas desta forma aparecem na exportação GraphML do Extended Matrix como **elementos de continuidade**.

---

## Referências

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositório pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
