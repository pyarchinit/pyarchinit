# Tutorial 36: Exportação Extended Matrix e Bridge s3dgraphy

## Introdução

A partir da versão **5.2.0-alpha** o PyArchInit integra um **bridge bidirecional** com a biblioteca **s3dgraphy** (modelo de dados Extended Matrix de Emanuel Demetrescu). O bridge permite:

- **Exportar** o diagrama estratigráfico como Extended Matrix em **em.json**, o formato que o EMStudio abre (a antiga exportação GraphML está retirada)
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

A janela diz em cima para que serve cada formato. Contém:

- **Formati** (Formatos): **DOT (Graphviz) — matrice di Harris** e **em.json (Extended Matrix, per EMStudio)**, marcados de início, mais **Matrice per fasi** (matriz por fases, análise cronológica), opcional. O GraphML já não se exporta: o JSON desta janela **é o em.json**, o mesmo ficheiro que o menu **Extended Matrix → Esporta sito in em.json…** produz — mesmo projetor, mesma simbologia.
- **Opzioni** (Opções): **Controlla la sequenza stratigrafica e segnala i problemi** (verificar a sequência estratigráfica e assinalar os problemas). É a única opção que resta, e agora é realmente lida: sem a marca, a verificação não se faz. As duas caixas antigas que falavam ao yEd (sugestões de auto-layout, cores por período) foram-se com a exportação GraphML.
- **Extended Matrix**: quatro botões ao lado da exportação — **Apri in EMStudio** e **Vedi la matrice** (ambos acendem depois de uma exportação em.json bem sucedida; o segundo desenha a matriz dentro do QGIS, sem EMStudio), **Consegna alla stanza…** e **Apri la stanza**. São as mesmas entradas do menu pyArchInit, à mão.

Ao premir **Esporta** é pedida a **pasta de destino**.

Autores, licenças, embargos e grupos gerem-se na janela **"Manage paradata"** (§3).

### 2.2.1 Sondagens: um unico grafo ou um por sondagem

Um grupo de tres escolhas, na mesma janela, decide **como dividir o
em.json** quando a escavacao tem varias sondagens:

- **Automatico**: um unico grafo se o sitio tem uma sondagem, um grafo
  por sondagem se tem varias. E a escolha de partida.
- **Um unico grafo para todo o sitio**: toda a escavacao num grafo, como
  sempre.
- **Um grafo por sondagem**: **um unico ficheiro**, que leva dentro um
  grafo para cada sondagem, mais um para as unidades que o tem vazio. As
  relacoes que **saem** da sondagem nao se perdem: ficam no ficheiro
  como ligacoes entre grafos (`graph.links`).

> **O EMStudio 1.6.0 mostra um de cada vez.** O ficheiro esta correto —
> o leitor da biblioteca volta a ler todos os grafos, sem avisos — mas o
> EMStudio abre o grafo declarado em `active_graph_id`, a primeira
> sondagem, e nao tem um seletor para os outros. A matriz dentro do
> QGIS, **Mostrar matriz**, une-os todos e desenha a escavacao inteira.
> Medido em 2026-10-12 no sitio de exemplo: 4 grafos (52/49/56/51 nos),
> 32 ligacoes entre sondagens, 51 unidades na matriz unida.

A sondagem e o campo **Saggio** da ficha UE: as unidades que o tem vazio
acabam num grafo separado, dentro do mesmo ficheiro.

### 2.3 Clica em "Esporta"

Os ficheiros que nascem, conforme os formatos marcados:
- `<sítio>.em.json` — Extended Matrix, para abrir no EMStudio ou entregar a uma sala
- `Extended_Matrix_<sítio>[_<area>].dot` — Graphviz DOT, para a matriz de Harris clássica
- `Extended_Matrix_<sítio>[_<area>]_phased.json` — vista por época

> **Os lugares nao entram no em.json.** Sitio, area e setor permanecem na ficha de cada unidade, mas ja nao viajam como nos de grupo com as suas arestas: enquanto o ficheiro contiver nem que seja uma aresta `is_in_location`, a vista **Matrix** do EMStudio amontoa todas as unidades na primeira faixa em vez de as distribuir por epoca (medido a 2026-10-08 contra o EMStudio 1.6.0-dev.26, por bisseccao sobre cinco ficheiros). Nenhuma informacao se perde — apenas uma forma de a representar.

O resumo final lista os ficheiros e, para o em.json, **quantos nós e quantas arestas** saíram, com os avisos que houver.

> **O GraphML já não se exporta**: a matriz vê-se e valida-se no EMStudio, que lê em.json. As linhas temporais (swimlanes) do antigo GraphML foram-se com ele. O GraphML sobrevive apenas à **entrada**, para os ficheiros desenhados no yEd (§5).

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

A dimensão primária segue uma ordem predefinida, com `struttura` em primeiro lugar; `toponym` nunca é primária.

---

## 5. Round-trip (aba Import)

> **O que se pode importar**: a aba Import lê agora também **em.json** — o do EMStudio ou o do nó StratiGraph — e escolhe o leitor pela extensão do ficheiro; um `.graphml` do yEd continua a ser aceite para os ficheiros de antes. O procedimento abaixo, mover UE entre grupos, diz respeito à via yEd/GraphML.

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
| As linhas da swimlane mostram um texto longuíssimo | As versões anteriores usavam a Descrizione da periodização como etiqueta | Atualiza o plugin e reexporta, e/ou preenche **Datazione estesa** com um nome curto |
| As épocas da swimlane estão na ordem errada (ex. Bronze acima do Tardo-antigo) | As linhas são ordenadas por **Cronologia Inicial**; datas a.C. inseridas como números positivos (1650 em vez de -1650) são ordenadas como d.C. | Na Ficha de Periodização insere os anos a.C. como números negativos e reexporta. O resumo da exportação mostra agora um aviso "⚠️ Periodizzazione: ..." com a lista dos períodos a corrigir |

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

> **A fase, por si so, nao conta.** A regra olha o **periodo**: uma USM que vai de **2/3 a 2/4** — mesmo periodo, muda so a fase — nao gera nada. Se as tuas unidades sobrevivem de fase em fase dentro do mesmo periodo, marca **«anche i salti di fase»** («tambem os saltos de fase») ao lado do botao: entao esses saltos tambem contam, desde que **ambas** as fases estejam preenchidas. Uma unidade que nao se move — mesmo periodo e mesma fase — nunca e uma continuidade. A caixa comeca **sem marca**, e vale para a pre-visualizacao e para a escrita ao mesmo tempo.

### 6.2 Idempotência

A operação é **idempotente**: voltar a executá-la não duplica as fichas existentes — atualiza as `CON_<us>` existentes se os dados da unidade-mãe tiverem mudado.

### 6.3 Pré-visualização (dry-run) e cópia de segurança

Antes de escrever é mostrada uma **pré-visualização dry-run** com as contagens: quantas fichas há a **criar**, a **atualizar**, **inalteradas** e quantas **órfãs**. As alterações são aplicadas **apenas após confirmação** (botão «Genera»). Ao aplicar é feita primeiro uma **cópia de segurança da base de dados** automática.

Uma ficha CON é **órfã** quando a sua unidade-mãe já não se estende por vários períodos (p. ex. o seu período inicial e final foram tornados iguais). Por predefinição as órfãs são apenas **assinaladas**; uma **caixa de seleção** («Rimuovi anche le CON orfane») permite optar por removê-las.

**Uma continuidade escrita a mao e reconhecida.** Uma ficha CON cujas relacoes nomeiam uma unica unidade — `> 12`, ou «Continuidade posterior a 12» — e a continuidade dessa unidade, chame-se como se chamar: o gerador **atualiza-a** (arco de periodos, rotulo canonico) e o nome continua a ser o seu. Nao nasce uma segunda: a continuidade e **uma por unidade**. Se tambem existir uma `CON_<us>` canonica, ganha essa e a outra fica orfa, a decidir a mao.

### 6.4 Na exportação Extended Matrix

As fichas `CON_<us>` geradas desta forma aparecem no **em.json** do Extended Matrix como **elementos de continuidade** (a exportação GraphML está retirada, §2.3).

---

## 7. Verificação de paradoxos temporais (estratigráficos)

No painel **"Verifica rapporti"** (Verificar relações — uma aba do diálogo de import/export do s3dgraphy), a verificação agora também assinala os **paradoxos temporais**: quando o período/fase atribuído a uma unidade contradiz a estratigrafia observada. A estratigrafia é o dado de referência, por isso as correções automáticas deslocam os **períodos**, não as relações.

### 7.1 O que deteta
- **Inversão temporal**: duas unidades datadas ligadas por uma relação de ordem (p. ex. US5 «cobre» US7) em que a unidade mais recente na estratigrafia se revela inteiramente mais **antiga** por período.
- **Contemporaneidade incoerente**: unidades declaradas contemporâneas (igualdade física / vínculo) mas com intervalos cronológicos **disjuntos**.
- **Não avaliável**: relação de ordem em que pelo menos uma das duas unidades não tem um período datável (apenas assinalado, sem correção).

Nota sobre o limite: dois períodos **adjacentes que se tocam** num único ponto cronológico são considerados sobrepostos → **não** constituem um paradoxo (benefício da dúvida).

### 7.2 Correção automática e sugestões
- Quando um único deslocamento resolve o conflito, a verificação propõe deslocar a unidade **mono-período** em conflito com a maioria dos seus vizinhos, escolhendo o período de deslocamento mínimo; para as contemporaneidades com uma unidade não datável copia o período do vizinho datado.
- Nos casos ambíguos — empate, unidades **multi-período** (p. ex. fichas CON), nenhum período válido — não corrige automaticamente: fornece uma **sugestão «o quê + como»** (p. ex. «Desloca US5 para um período ≥ 3, ou US7 para um período ≤ 1, ou verifica a relação»).

### 7.3 Pré-visualização e backup
- A **pré-visualização** mostra as alterações de período propostas antes de as aplicar.
- Antes de escrever os períodos é efetuado um **backup automático da base de dados** (SQLite e PostgreSQL).
- Após a aplicação, relança a verificação para controlar eventuais paradoxos residuais.

---

## 8. Verificação da cronologia (periodização e fichas)

No mesmo painel **"Verifica rapporti"** (Verificar relações — uma aba do diálogo de import/export do s3dgraphy), desde a versão 5.13.64-alpha a verificação encontra e corrige também problemas de **cronologia** do sítio selecionado. A verificação de paradoxos temporais (secção 7) compara o período de uma unidade com a estratigrafia; esta compara a periodização consigo própria e com as fichas US que a copiam.

### 8.1 O que deteta

O painel agrupa os problemas por tipo. Ao lado dos grupos das relações aparecem quatro grupos novos:

| Grupo | O que assinala | Como é tratado |
|-------|----------------|----------------|
| **Fases com intervalos sobrepostos** | Duas linhas da periodização cujos intervalos de anos se cruzam | Manual: o painel propõe reduzir os intervalos apenas se, depois da redução, restar um intervalo utilizável |
| **Datação da ficha desalinhada** | O campo `datazione` da ficha US diz algo diferente da `datazione_estesa` do seu período/fase | Automático: a periodização é a fonte e a ficha é a cópia, por isso a cópia é reescrita a partir da fonte. Um campo vazio é preenchido da mesma maneira. Uma US sem período é ignorada, porque não há nada para copiar |
| **Periodização com início depois do fim** | `cron_iniziale` maior que `cron_finale` | Manual: são provavelmente datas a.C. sem o sinal menos — o painel propõe reescrever os dois anos como negativos (`-1650` em vez de `1650`); se for um erro de digitação, troque os dois valores à mão |
| **Fase sem anos** | Uma fase cujos anos faltam ou não são legíveis | Só assinalada: não há nada de onde os herdar |

Um exemplo para as sobreposições. A base de dados de exemplo tem duas, e nenhuma traz proposta: as duas fases têm intervalos **idênticos**, e qualquer redução faria uma fase terminar antes de começar. O painel limita-se a dizê-lo; a decisão (juntar as fases, corrigir os anos, deixar como está) cabe ao arqueólogo.

### 8.2 Correção automática e sugestões

**Correções automáticas e propostas.** As correções automáticas estão **já assinaladas**; as propostas **não**, e só são aplicadas se se assinalar a caixa. Antes a regra era diferente: um problema cuja correção exigia uma decisão humana só podia ser lido. Agora tem uma caixa, deixada em branco. Isto vale também para as duas categorias de relações mais antigas que oferecem uma sugestão, isto é, a contradição direta e o ciclo estratigráfico.

Para usar o painel:

1. Selecione no painel o **sítio** a verificar. A verificação é **por sítio**: olha apenas para o sítio escolhido e corrige apenas esse. Numa base de dados com dez sítios isto conta, porque os mesmos números de US existem em todos.
2. Leia a **linha de resumo** acima da árvore: indica quantos problemas há, quantos são corrigíveis automaticamente e **quantas são as propostas a assinalar à mão**.
3. Abra os grupos e selecione um problema para ler o detalhe no painel de pré-visualização.
4. Verifique as caixas. As correções automáticas já estão assinaladas: retire a marca das que não quiser aplicar. Assinale as propostas com que concorda.
5. Aplique as correções. Antes de escrever o que quer que seja é criada uma **cópia de segurança automática** (cópia do ficheiro SQLite ou `pg_dump` para PostgreSQL em `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); a cópia, que já existia para as correções dos campos de período, cobre agora também as cronológicas.
6. Se o resultado não convencer, prima **Annulla ultimo fix** (anular a última correção): a anulação reverte também as correções escritas na tabela da periodização.

### 8.3 Pré-visualização e backup

**A pré-visualização mostra a data calculada.** Para cada unidade citada por um problema, o painel de pré-visualização mostra a sua data calculada numa linha como esta:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

A linha indica, por ordem, o intervalo de anos, a regra que o produziu e a relação ao longo da qual a restrição viajou, com o nó de onde veio. Quando os dois extremos do intervalo chegam por caminhos diferentes, cada extremo leva a sua etiqueta (`inizio …` e `fine …`), de modo que uma data nunca é atribuída à relação errada. Hoje, numa base de dados normal, cada unidade toma as suas datas do seu próprio período, por isso a maioria das linhas dirá `epoca`. O objetivo da linha não é surpreender, é permitir ver **de onde vem** uma data.

---

## 9. Como ler os arcos da matrix

Algumas escolhas do desenho da matrix podem parecer estranhas, mas não são erros:

- **Uma seta nunca passa por baixo de um nó.** Quando a coluna de chegada está ocupada, a seta entra na caixa **pelo lado**: é normal.
- **A igualdade não é uma sobreposição.** Uma relação «Uguale a» (Igual a) ou «Si lega a» (Liga-se a) coloca as duas unidades na **mesma linha**, lado a lado, ligadas por **duas linhas horizontais** (o sinal de igual) **sem ponta de seta**.
- **Os arcos redundantes não são desenhados.** Se a UE 1 cobre a 2 e a 2 cobre a 3, a seta de 1 para 3 não aparece, porque não acrescenta nada. Dentro de um **ciclo**, pelo contrário, todos os arcos ficam, porque um ciclo é um erro que é preciso ver.
- **As linhas dizem que relacao sao.** Cinzenta e continua: a sequencia (cobre, enche, apoia-se). **Pontilhada verde**: um corte (`Taglia` / `Tagliato da`), seja qual for a definicao estratigrafica e em qualquer lingua. **Grossa e preta**: a continuidade — um losango pequeno e preto sem nome (o nome aparece ao passar o rato), na coluna da sua unidade, por isso a linha e reta. **Vermelha**: uma seta que sobe pelas faixas, isto e, uma contradicao entre estratigrafia e cronologia; um corte que sobe e vermelho **e** continua pontilhado.
- **Os paradados nunca sao uma linha continua.** Tomam cor e traco das regras do Extended Matrix (`em_visual_rules.json`): castanho-vermelho pontilhado «extraido de», laranja tracejado «proveniencia do dado», ouro tracejado «propriedade», cinzento tracejado «ligacao generica», vermelho-tomate tracejado «combina» (no ficheiro seria continuo: e a unica excecao, porque um arco para um documento nao deve parecer uma sobreposicao).
- **O bordo castanho e uma alvenaria.** As USM — WSU, MSE, UEM, USZ, ΤΣΜ nas outras linguas — tem a mesma caixa das US, com o bordo castanho em vez de vermelho.

---

## 10. Narrativa com IA

A partir da versão **5.13.106-alpha**, o painel da matriz dentro do QGIS (§2.2, «Vedi la matrice») tem dois separadores na coluna da direita: **Units** (*Unità*) — a ficha da unidade escolhida, o zoom sobre a geometria e os media, como antes — e **Narrative** (*Narrativa*), que é novo. O separador Narrative pede a uma IA que escreva a **história do sítio**, um capítulo por época, e depois permite lê-la, fazê-la validar por uma pessoa e exportá-la para HTML ou DOCX. Lê e escreve **o mesmo em.json** que o EMStudio abre, no formato da biblioteca s3dgraphy: a narrativa que vê aqui é a que o EMStudio mostra no seu separador *Narrative*.

> **Sem definições novas.** O separador não tem uma janela de configuração própria: usa a IA que já configurou noutro ponto do pyArchInit (§10.2).

> **A IA escreve rascunhos, não textos definitivos.** Cada parágrafo escrito pelo modelo continua a ser um «AI draft» (rascunho da IA) até uma pessoa o validar (§10.6), e nos documentos exportados leva a marca ⚠.

Os nomes dos separadores e dos botões do separador Narrative existem em italiano e em inglês: **estão em italiano se o QGIS estiver em italiano, em inglês com qualquer outra língua**. Aqui indicam-se sempre os dois. As entradas de menu e as janelas de diálogo do plugin (como «Vedi la matrice…» ou os três botões da §10.9) estão, pelo contrário, só em italiano; a tradução para português vem entre parênteses.

### 10.1 Abrir o separador Narrative

1. Abra o menu **Plugins → pyArchInit - Archaeological GIS Tools** e escolha a entrada **Extended Matrix → Vedi la matrice…** (Ver a matriz).
2. Escolha o **sítio**.
3. Se o sítio tiver **sondagens** (*saggi*), o pyArchInit pergunta «Il sito ha N saggi. Come divido il file?» (O sítio tem N sondagens. Como divido o ficheiro?) com duas respostas: «Un grafo per ogni saggio (…)» (um grafo por sondagem), a predefinida, ou «Un grafo solo per tutto il sito» (um único grafo para todo o sítio). É a mesma escolha da §2.2.1 e da entrada «Esporta sito in em.json…»: as duas entradas escrevem o **mesmo ficheiro**, com a mesma forma.
4. O pyArchInit exporta o sítio da base de dados para `<home>/pyarchinit_EM_folder/<sítio>.em.json` — `<home>` é `~/pyarchinit_5`, ou a pasta indicada pela variável de ambiente `PYARCHINIT_HOME` — e abre o painel **«Matrice — `<site>`»**, acoplado à direita da janela do QGIS. O nome do ficheiro é o do sítio, com os caracteres especiais substituídos por «_» (por exemplo, «Scavo 1» dá `Scavo_1.em.json`).
5. Na coluna da direita do painel, clique no separador **Narrative**.

<!-- IMMAGINE: Captura de ecrã do menu Plugins → pyArchInit - Archaeological GIS Tools com a entrada «Extended Matrix → Vedi la matrice…» -->
![Menu Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: A entrada «Extended Matrix → Vedi la matrice…» no menu do plugin*

<!-- IMMAGINE: Captura de ecrã da pergunta sobre as sondagens com as duas respostas -->
![Pergunta sobre as sondagens](images/36_extended_matrix_s3dgraphy/02_domanda_saggi.png)
*Figura 2: A pergunta sobre as sondagens: um grafo por sondagem ou um único grafo*

<!-- IMMAGINE: Captura de ecrã do painel da matriz acoplado à direita, com os separadores Units e Narrative -->
![Painel com dois separadores](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 3: O painel da matriz com os separadores Units e Narrative*

O ficheiro é **um por sítio e fica no disco**: já não está numa pasta temporária. É o ficheiro que o EMStudio abre e é nele que a narrativa é escrita. Sempre que escolhe «Vedi la matrice…», o sítio é **exportado de novo da base de dados** e o ficheiro é reescrito; a narrativa que já lá estiver é mantida (§10.8).

Também pode chegar ao separador por outros dois caminhos:

- a partir da entrada **Extended Matrix → Esporta sito in em.json…** (Exportar sítio para em.json), que no fim oferece o botão «Narrativa con l'AI» (§10.9);
- a partir do botão **Vedi la matrice** da janela «Esporta Extended Matrix» da ficha UE (§2.2): abre o mesmo painel sobre o ficheiro que acabou de exportar, na pasta que escolheu.

### 10.2 Que IA é utilizada

Em cima, no separador Narrative, uma linha diz que IA vai usar: **«Model: `<model>` (`<where it comes from>`)»**, seguida do lembrete sobre o EMStudio. Se o separador não encontrar nenhuma, escreve **«No AI configured: set it in the US form → AI report (or in the AI database query).»** (ou seja, nenhuma IA configurada: configure-a na ficha UE → relatório de IA, ou na consulta à base de dados com IA) e os botões **Generate with AI** (Gerar com IA) e **Regenerate chapter** (Regenerar capítulo) ficam desativados.

O separador lê as definições de IA **já guardadas** pelas outras janelas do pyArchInit, por esta ordem, e usa a **primeira** que tiver um modelo e — para os fornecedores remotos — a chave API:

| # | Onde se define | Como o separador lhe chama (en / it) |
|---|----------------|---------------------------------------|
| 1 | Ficha UE, botão «Report» → janela «Generatore di Report» (Gerador de relatórios), grupo «Provider AI» | AI report of the US form / Relazione AI della scheda US |
| 2 | Ficha UE, botão «Query AI Database» | AI database query / Interrogazione AI del database |
| 3 | Janela palimpsestr, botão «Report AI (analisi descrittiva)…», seletor «Provider AI» | Palimpsest report / Relazione Palimpsest |
| 4 | Janela «Generazione SQL con AI» (texto para SQL: ver o tutorial 30) | Text to SQL / Testo in SQL |

Os fornecedores são os dos seletores «Provider AI»: **OpenAI** e **Anthropic (Claude)**, remotos, com a chave API escrita no campo «API key»; **Ollama** e **LM Studio** no seu computador, sem chave. O seletor guarda a escolha assim que a altera. Se quiser outro modelo, altere-o na janela que o separador indica entre parênteses (ou numa que venha antes na lista). O separador volta a ler as definições **quando o painel se abre**: depois de as alterar, abra de novo a matriz.

### 10.3 O separador Narrative

```
┌─ Units ─┬─ Narrative ────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the     │
│ file open, close it first: the last writer wins.                 │
├──────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                     │
│ Early 15th century — AI draft                                    │
│ 15th century — endorsed                                          │
│ Modern age — AI draft, truncated                                 │
├──────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.            │
├──────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                 │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]             │
│ [Prepare the chapters]  [Export…]  [Open in EMStudio]  [Cancel]* │
└──────────────────────────────────────────────────────────────────┘
```

\* A linha de progresso e o botão «Cancel» (Cancelar) só se veem enquanto a IA está a escrever. Neste diagrama, as linhas da lista são as do sítio de exemplo.

<!-- IMMAGINE: Captura de ecrã do separador Narrative com a lista de capítulos, o texto do capítulo escolhido e os seis botões -->
![Separador Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 4: O separador Narrative*

De cima para baixo:

- **a linha de estado**: o modelo em uso (§10.2) e o lembrete *«If EMStudio has the file open, close it first: the last writer wins.»* (se o EMStudio tiver o ficheiro aberto, feche-o primeiro: prevalece quem escrever por último);
- **a lista de capítulos**, uma linha por capítulo: *Título — estado*. Com a exportação por sondagens (§2.2.1), cada sondagem tem a sua narrativa e cada linha é precedida do nome da sondagem entre parênteses retos, por exemplo `[Saggio A] 15th century — AI draft`;
- **o texto do capítulo escolhido**: a prosa, com as unidades citadas pelo nome. Se o capítulo ainda não tiver prosa, vê o respetivo marcador de posição «[to be written: …]»;
- **a linha de progresso**, só durante a geração: «Chapter 3 of 9 · 15th century» (capítulo 3 de 9 · século XV);
- **os botões**, em duas linhas.

O resultado de cada operação aparece na barra de mensagens do QGIS, com o título «Narrative».

Quando o ficheiro **ainda não tem narrativa**, a lista fica vazia e um texto diz: *«No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it.»* (nenhuma narrativa no ficheiro: «Prepare the chapters» cria o esquema, com N capítulos repartidos por épocas e atividades; «Generate with AI» escreve-o).

#### Os estados de um capítulo

| Estado (en / it) | O que significa |
|------------------|-----------------|
| **to be written** / da scrivere | O capítulo só tem o marcador de posição «[to be written: …]». |
| **AI draft** / bozza AI | Há prosa escrita pelo modelo que nenhuma pessoa validou. Basta um parágrafo: se o capítulo tiver pelo menos um parágrafo não validado, o seu estado é este, mesmo que haja outra prosa. |
| **endorsed** / convalidato | Toda a prosa da IA foi validada por uma pessoa. |
| **written** / scritto | Prosa escrita por uma pessoa (no EMStudio). |
| **truncated** / troncato | Acrescenta-se ao estado (por exemplo «AI draft, truncated»): o modelo interrompeu-se porque atingiu o limite de comprimento, e o texto acaba a meio. |

#### Os botões

| Botão (en) | Em italiano | O que faz |
|------------|-------------|-----------|
| **Generate with AI** | Genera con l'AI | Escreve, **um de cada vez**, todos os capítulos de época (e de atividade) ainda «to be written»; os que já estão escritos não são alterados. Se ainda não houver narrativa, cria primeiro o esquema. Mostra o progresso e o botão **Cancel**. Ativo apenas com um ficheiro aberto e uma IA configurada. |
| **Regenerate chapter** | Rigenera capitolo | Reescreve **o capítulo escolhido** na lista (com várias sondagens, só o da sondagem escolhida): o rascunho da IA não validado é substituído — mas só depois de o modelo ter respondido: se a chamada falhar, o rascunho anterior permanece — e os blocos já validados mantêm-se. Ativa-se quando se escolhe um capítulo de época ou de atividade e há uma IA configurada; para «Presentation» (Apresentação) e «Where it is» (Onde se encontra) fica desativado. |
| **Endorse…** | Convalida… | Abre um menu com «This chapter» e «All chapters» e depois pergunta quem valida (§10.6). Ativo quando há uma narrativa. |
| **Prepare the chapters** | Prepara i capitoli | Cria **apenas o esquema** dos capítulos, sem IA: serve mesmo que não haja nenhuma IA configurada, para escrever à mão no EMStudio. Não toca na prosa já escrita e acrescenta os capítulos das épocas novas. Resultado: «Chapters prepared: N.» (capítulos preparados: N). |
| **Export…** | Esporta… | Guarda a narrativa em HTML ou DOCX (§10.7). Ativo quando há uma narrativa. |
| **Open in EMStudio** | Apri in EMStudio | Abre o em.json no EMStudio. Se o EMStudio não for encontrado, a barra de mensagens remete para a entrada de menu **Extended Matrix → Installa EMStudio…** (Instalar o EMStudio). |
| **Cancel** | Annulla | Aparece apenas durante a geração: a IA interrompe-se **depois do capítulo em curso** e o que foi escrito é guardado. |

Durante a geração, todos os botões ficam desativados, exceto **Cancel**.

### 10.4 O que a IA escreve

**Que capítulos.** O esquema é o da biblioteca s3dgraphy (o modelo «site_story»):

- **Presentation** e **Where it is** são capítulos canónicos: ficam como marcadores de posição «[to be written: …]», a escrever à mão no EMStudio, porque no grafo não há nada a partir do qual possam ser escritos sem inventar. «Where it is» só existe se o grafo tiver uma posição geográfica. A IA não os gera.
- **Um capítulo por época** (período/fase) que tenha unidades, da mais antiga à mais recente. O título é o nome da época, isto é, a «Datazione estesa» (datação alargada) da periodização; se faltar, resulta um nome genérico como «Period 8 Phase 1»: preencha-a na ficha de Periodização para obter títulos legíveis. Uma unidade aparece no capítulo da época em que nasce e nos das épocas em que sobrevive.
- **Um capítulo por atividade**, se o grafo contiver grupos de atividades. Um sítio exportado da base de dados normalmente não os tem — o campo Atividade da ficha UE viaja como propriedade da unidade — e então os capítulos são os de época.

**O que o modelo recebe.** Para cada capítulo, um *briefing* com, para cada unidade: nome, tipo e descrição; os campos preenchidos da ficha UE (definição estratigráfica e interpretativa, interpretação, período e fase, datação, atividade, estrutura, sondagem, divisão, setor, área); as épocas; **as relações estratigráficas** com as outras unidades (cobre, corta, preenche, encosta-se a, igual a…) com os respetivos nomes; e, se existirem, as fontes documentais ligadas. As unidades são listadas **da mais antiga à mais recente**, seguindo as relações. Acima de **80 unidades** por capítulo, o briefing é reduzido às primeiras 80. Tem também um limite de comprimento (cerca de 25 000 caracteres): acima dele, os textos longos das fichas são encurtados, as relações repetidas e as cadeias de provas são eliminadas e, se ainda não bastar, as unidades mais recentes ficam de fora. Nos dois casos, o modelo é informado de quantas unidades faltam.

**As regras.** O modelo recebe as cinco regras da biblioteca: escrever só o que o contexto sustenta (nada de datas, materiais, funções ou acontecimentos inventados); manter a incerteza (uma unidade virtual é uma hipótese, não um facto); não citar nenhuma fonte que não exista; escrever prosa contínua, sem listas nem títulos; dizer abertamente quando o contexto é demasiado pobre. São pedidos de um a três parágrafos.

**A língua.** A prosa está na **língua da narrativa**, que fica fixada quando o esquema é criado pela primeira vez: **italiano se nesse momento o QGIS estiver em italiano, inglês com qualquer outra língua** (o modelo recebe as instruções só nestas duas línguas). Uma narrativa já existente mantém a sua língua, mesmo que mais tarde mude a língua do QGIS. O mesmo vale para os títulos dos capítulos canónicos e para os marcadores de posição.

**Como é guardada.** No formato da biblioteca, o mesmo que o EMStudio lê: um nó de narrativa (`NarrativeNode`) que contém os capítulos; cada parágrafo escrito pelo modelo é um bloco «AI draft» atribuído ao **autor de IA** desse modelo; o **prompt** usado fica registado como um extrator ligado às fontes, para se poder saber o que foi pedido. As unidades citadas no texto são **menções** (`[[name]]`): no ficheiro continuam ligadas ao nó da unidade e, no separador e nas exportações, aparecem com o seu nome. Uma menção que não corresponda a nenhuma unidade do grafo é reduzida a palavras simples, sem parênteses retos.

**Custos e tempos.** O modelo é chamado **uma vez por capítulo**. Com um fornecedor remoto cada chamada tem um custo e um tempo de espera (nos testes com um modelo remoto, algumas dezenas de segundos por capítulo: um sítio com cerca de dez épocas demora alguns minutos); com o Ollama ou o LM Studio não se paga nada, mas os tempos dependem do computador.

### 10.5 Passo a passo

1. Abra a matriz do sítio (§10.1) e clique no separador **Narrative**. Verifique em cima **que modelo** vai usar.
2. **Feche o EMStudio** se tiver o ficheiro aberto: o pyArchInit e o EMStudio escrevem o mesmo ficheiro, e prevalece quem escrever por último.
3. Opcional: clique em **Prepare the chapters** para ver o esquema, sem IA.
4. Clique em **Generate with AI**. Acompanhe o progresso («Chapter 3 of 9 · …»); pode continuar a usar o QGIS. No fim, a barra de mensagens diz, por exemplo, *«7 chapters generated, 1 failed: Modern age — …»* (7 capítulos gerados, 1 falhou) — com *«(cancelled)»* se cancelou — e a lista volta a carregar-se: os capítulos escritos ficam «AI draft».
5. **Leia**: escolha um capítulo após o outro e leia o texto por baixo da lista. Confronte-o com a estratigrafia: é um rascunho construído a partir dos dados da ficha UE.
6. Se um capítulo não convencer, escolha a sua linha e clique em **Regenerate chapter**. O novo rascunho **substitui** o anterior não validado: se quiser conservar a versão anterior, exporte-a primeiro. Se um capítulo estiver «truncated», regenere-o **antes** de validar.
7. Quando um capítulo estiver certo, clique em **Endorse…** (§10.6).
8. Clique em **Export…** para exportar para HTML ou DOCX (§10.7), ou em **Open in EMStudio** para escrever à mão «Presentation» e «Where it is» e refinar o resto.
9. Mais tarde pode abrir a matriz de novo: a narrativa mantém-se (§10.8).

<!-- IMMAGINE: Captura de ecrã da geração em curso: a linha de progresso «Chapter 3 of 9 · …» e o botão Cancel -->
![Geração em curso](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 5: Geração em curso, com a linha de progresso e o botão Cancel*

Um capítulo que falha não impede os outros: o resumo diz quais. Para tentar de novo, basta clicar outra vez em **Generate with AI**, que escreve apenas os capítulos ainda «to be written».

### 10.6 Validar: quem assina

Validar quer dizer que uma **pessoa** assume a responsabilidade pelo texto que o modelo escreveu. Nunca acontece sozinho: nem ao gerar, nem ao guardar.

1. Clique em **Endorse…**. Abre-se um pequeno menu: **«This chapter»** (este capítulo) — ativo só se o capítulo escolhido estiver em «AI draft» — ou **«All chapters»** (todos os capítulos), isto é, todos os rascunhos da IA ainda não validados, em todos os grafos do ficheiro.
2. Uma janela pergunta **«Who endorses? Pick an author or type a new name.»** (Quem valida? Escolha um autor ou escreva um nome novo.) A lista contém os **autores humanos já presentes no grafo** — as pessoas nomeadas na ficha UE como compilador (*schedatore*), diretor da UE e responsável pela UE — e pode escrever um nome novo, que passa a ser um novo autor do grafo (com várias sondagens, em cada grafo que tenha rascunhos por assinar).
3. A barra de mensagens diz **«N blocks endorsed by `<name>`.»** (N blocos validados pelo autor indicado), ou «Nothing to endorse.» (nada para validar). O ficheiro é guardado.

<!-- IMMAGINE: Captura de ecrã do menu Endorse… («This chapter» / «All chapters») e da janela para escolher o autor -->
![Validar](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 6: Validar: o menu e a escolha do autor*

Os blocos passam de «AI draft» a «endorsed». No documento exportado, a pessoa aparece entre os responsáveis («a cura di», editado por) e o modelo como assistente («con l'assistenza di», com a assistência de), e os parágrafos validados deixam de levar a marca ⚠. Regenerar não apaga os blocos validados: uma assinatura é um ato e não se perde ao reescrever.

### 10.7 Exportar para HTML ou DOCX

Clique em **Export…**: abre-se a janela para guardar o ficheiro, com dois formatos, «HTML page (\*.html)» e «Word document (\*.docx)» (página HTML e documento Word). O nome sugerido é `<sítio>_narrativa.html`, na pasta do em.json; se escrever a extensão (`.html` ou `.docx`), esta prevalece; caso contrário, decide o formato escolhido. Com a exportação por sondagens é escrito **um ficheiro por sondagem**, acrescentando o nome da sondagem ao nome escolhido. A barra de mensagens confirma: «Narrative exported to `<path>`» (narrativa exportada para o caminho do ficheiro).

O documento contém:

- o título da narrativa (por exemplo «Scavo archeologico — the story of the site», em português «Escavação arqueológica — a história do sítio»), os responsáveis («a cura di») e o modelo como assistente («con l'assistenza di»);
- para cada capítulo, a prosa, com as unidades citadas pelo seu nome, e a lista das unidades do capítulo;
- no fim, a secção **Fonti** (fontes): os documentos em que a história assenta e a entrada «Prompt», que remete para o prompt registado no ficheiro.

Algumas coisas que convém saber:

- **os rascunhos não validados entram**, cada um precedido de «⚠︎ non validato da una persona» (não validado por uma pessoa), e o cabeçalho diz quantos blocos estão neste estado. Para um documento sem marcas, valide primeiro (§10.6);
- **entram todos os capítulos**, mesmo os que ainda estão «to be written»: o respetivo marcador de posição «[to be written: …]» fica no texto;
- as figuras que um autor previu no EMStudio (por exemplo a matriz de uma época) não são desenhadas pela exportação do pyArchInit: no documento fica um marcador de posição;
- o HTML é um único ficheiro, que não depende de outros; o DOCX abre-se com o Word ou o LibreOffice e requer o pacote `python-docx`, um dos requisitos do plugin.

<!-- IMMAGINE: Captura de ecrã do documento HTML exportado: um capítulo com um rascunho precedido de «⚠︎ non validato da una persona» -->
![Documento HTML exportado](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 7: O documento HTML exportado, com um rascunho não validado assinalado*

### 10.8 Exportar de novo o sítio: a narrativa mantém-se

Exportar de novo o sítio a partir da base de dados — com **Vedi la matrice…**, com **Esporta sito in em.json…** ou com a janela «Esporta Extended Matrix» da ficha UE — **mantém a narrativa** que já estiver no ficheiro de destino: prosa, validações, autor de IA e prompts. As épocas que entretanto surgiram recebem um capítulo «to be written». Um aviso di-lo: **«Narrative kept from the previous file (N chapters).»** (narrativa mantida do ficheiro anterior, N capítulos). Vê-o na barra de mensagens com «Vedi la matrice…», no resumo da janela «Esporta Extended Matrix» e, com «Esporta sito in em.json…», nos detalhes da janela final.

As **outras alterações** feitas ao ficheiro no EMStudio — posições dos nós, descrições reescritas — **não sobrevivem**, como antes: o ficheiro é regenerado a partir da base de dados. Só a narrativa é mantida.

Antes de reescrever um ficheiro que contém uma narrativa, o pyArchInit faz uma **cópia de segurança** ao lado: `<sítio>.em.json.bak` (cada nova exportação substitui a cópia anterior).

Se mudar a forma do ficheiro (de «Un grafo per ogni saggio» para «Un grafo solo per tutto il sito», ou ao contrário), os grafos mudam de nome e a narrativa **não pode passar** para o ficheiro novo. Um aviso di-lo: *«The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …»* (a narrativa do ficheiro anterior, com a lista de grafos, não passou para o ficheiro novo: a forma do ficheiro mudou; cópia de segurança em …). O texto não se perde: está na cópia `.bak`, que, no entanto, é substituída pela próxima exportação de um ficheiro que contenha uma narrativa — ponha-a num lugar seguro. Para a recuperar, renomeie a cópia para `.em.json` e exporte de novo com a escolha anterior.

Se o ficheiro anterior não puder ser lido (por exemplo, um ficheiro cuja escrita ficou a meio), a exportação continua na mesma: o ficheiro ilegível é **renomeado** para `<sítio>.em.json.broken` e um aviso diz *«The previous file cannot be read (…): its narrative, if any, was not kept.»* (o ficheiro anterior não se consegue ler e a sua narrativa, se existia, não foi mantida).

> **A narrativa não está na base de dados do pyArchInit: vive apenas no em.json.** Uma cópia de segurança da base de dados não a copia. Copie de vez em quando a pasta `pyarchinit_EM_folder`.

### 10.9 A partir da entrada «Esporta sito in em.json…»

A entrada **Extended Matrix → Esporta sito in em.json…** faz a mesma pergunta sobre as sondagens e escreve o mesmo ficheiro `<sítio>.em.json` em `pyarchinit_EM_folder`. No fim mostra «Esportato `<path>`» (Exportado), com os totais de nós, arestas e avisos (o texto dos avisos está nos detalhes da janela), e **três botões**:

| Botão | O que faz |
|-------|-----------|
| **Apri in EMStudio** (Abrir no EMStudio) | Abre o ficheiro no EMStudio; se não estiver instalado, propõe instalá-lo. |
| **Narrativa con l'AI** (Narrativa com IA) | Aparece **só se houver uma IA configurada** (§10.2): abre o painel da matriz já no separador Narrative. |
| **Chiudi** (Fechar) | Fecha a janela. |

<!-- IMMAGINE: Captura de ecrã da janela final de «Esporta sito in em.json…» com os três botões -->
![Exportar sítio para em.json: três botões](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 8: A janela final de «Esporta sito in em.json…»*

### 10.10 Avisos

- **Feche o EMStudio antes de gerar ou validar.** Se o EMStudio tiver o ficheiro aberto, prevalece quem escrever por último. Com várias sondagens, o EMStudio mostra um grafo de cada vez (nota na §2.2.1): o separador Narrative mostra-os todos.
- **Uma IA escreve apenas a partir do que encontra no grafo, e pode enganar-se.** As regras mantêm-na sob controlo, mas não a tornam infalível: leia cada capítulo antes de o validar.
- **Com um fornecedor remoto, os dados saem do seu computador.** O briefing de cada capítulo (nomes, definições, descrições e relações das unidades) é enviado para o serviço escolhido; com o Ollama ou o LM Studio fica local.
- **O ficheiro é escrito no fim.** A geração guarda quando termina, mesmo que a tenha cancelado: não feche o QGIS enquanto a IA está a escrever. A gravação é segura: o ficheiro é escrito ao lado, relido, e só então substitui o verdadeiro; se algo correr mal, **o ficheiro anterior fica como estava**.
- **Não volte a abrir a matriz enquanto a IA está a escrever.** O separador continua no ficheiro anterior e avisa: *«Generation in progress: wait for it to finish, or press Cancel, before changing file.»* (geração em curso: espere que termine, ou clique em Cancel, antes de mudar de ficheiro).
- **O texto edita-se no EMStudio**, não no pyArchInit.
- A narrativa e os nós que a sustentam (autor de IA, prompts) **não aparecem no desenho da matriz**.

### 10.11 Resolução de problemas

| Mensagem (en / it) | Causa | Solução |
|--------------------|-------|---------|
| "No AI configured…" / «Nessuna AI impostata…» | Nenhuma das quatro janelas da §10.2 tem um modelo (e, para a OpenAI e a Anthropic, a chave API). | Defina o fornecedor e o modelo — e a chave — numa dessas janelas e depois **abra de novo a matriz**: o separador só volta a ler as definições quando se abre. Mesmo sem IA pode preparar os capítulos, validar, exportar e abrir o EMStudio. |
| "No narrative in the file…" / «Nessuna narrativa nel file…» | O ficheiro ainda não tem narrativa (é normal da primeira vez). | Clique em **Prepare the chapters** (esquema) ou em **Generate with AI** (esquema e prosa). O número N conta os capítulos de época e de atividade que o esquema terá (uma época sem unidades não tem nenhum); a mensagem «Chapters prepared» conta também «Presentation» e, se existir, «Where it is». |
| "EMStudio is not installed…" / «EMStudio non risulta installato…» | O programa não foi encontrado no computador. | Use a entrada de menu **Extended Matrix → Installa EMStudio…** (tem este nome com qualquer língua do QGIS). |
| "truncated" / «troncato» junto ao estado | O modelo interrompeu-se no limite de comprimento e o texto acaba a meio. | Antes de validar, use **Regenerate chapter**; se voltar a acontecer, termine o capítulo no EMStudio. |
| "N chapters generated, M failed: `<title>` — `<reason>`" / «N capitoli generati, M falliti: …» | O fornecedor recusou o pedido (chave inválida, quota, modelo não disponível) ou o servidor local não responde. «the model wrote nothing» (o modelo não escreveu nada) quer dizer que a resposta veio vazia. | Elimine a causa e clique de novo em **Generate with AI**: só escreve os capítulos que ficaram «to be written». |
| "The previous file cannot be read (…)" / «Il file precedente non si legge (…)» | Na reexportação, o ficheiro existente não era um em.json legível. | A exportação continuou: o ficheiro ilegível foi conservado ao lado do novo como `….broken`, e a narrativa que continha, se existia, não passou para o ficheiro novo. Se precisar dela, recupere-a desse ficheiro ou de uma cópia de segurança. |
| "The previous file's narrative (graphs: …) did not travel into the new file…" / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | Mudou a forma do ficheiro (um grafo por sondagem ↔ um único grafo): os grafos têm nomes diferentes e a narrativa não pode passar. | O ficheiro anterior está na cópia `.bak`: renomeie-a para `.em.json` e exporte de novo com a escolha anterior. |
| "Could not write … The previous file is intact." / «Non sono riuscito a scrivere … Il file precedente è intatto.» | A gravação falhou (disco cheio, ficheiro bloqueado, permissões). | Corrija e repita: os capítulos gerados nessa sessão não tinham sido guardados. |
| "DocX export needs python-docx — install the extra: …" (sempre em inglês) | O pacote `python-docx` não está instalado no Python do QGIS: só é necessário para o DOCX. | Instale `python-docx` (é um dos requisitos do plugin) ou exporte para HTML, que não precisa de nada. |

---

## Referências

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repositório pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
