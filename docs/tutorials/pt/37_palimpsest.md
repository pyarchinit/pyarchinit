# Tutorial 37: Análise dos palimpsestos (palimpsestr / SEF)

## Introdução

O PyArchInit integra o **palimpsestr**, uma biblioteca R que aplica o modelo
**SEF — Stratigraphic Entanglement Field** para a *decomposição probabilística
dos palimpsestos*: separa, em base estatística, os achados de um depósito complexo
em **fases** latentes, estimando para cada unidade estratigráfica (US) a fase de
pertença, a residualidade e as eventuais **intrusões**.

A janela **palimpsestr** (ícone de estratos coloridos na barra de ferramentas do
pyArchInit) permite:

- **Fit SEF**: estimar as fases e produzir camadas vetoriais (fases, ligações) e
  uma tabela de diagnóstico;
- **Intrusões**: identificar achados/US fora de posição cronologicamente;
- **Relatório narrado (PDF/DOCX)**: um relatório interpretativo com texto, gráficos
  de diagnóstico e tabelas;
- **Relatório AI**: um relatório descritivo gerado por agentes AI especializados,
  em qualquer idioma do pyArchInit;
- trabalhar tanto em **SQLite/Spatialite** como em **PostgreSQL/PostGIS**;
- usar uma **cronologia absoluta** (datas calibradas OxCal) em vez da
  datação textual.

> Requer palimpsestr **≥ 0.22.0** instalado na biblioteca R usada pelo
> *Processing R Provider* do QGIS.

---

## 1. Pré-requisitos

- **R** instalado e o plugin **Processing R Provider** ativo no QGIS.
- Pacote R **palimpsestr ≥ 0.22.0** (**≥ 0.22.1** para a pontuação taf; **≥ 0.23.0**
  para as coordenadas pontuais dos achados) (e dependências: `sf`, `DBI`, `RSQLite`;
  `RPostgres` para PostgreSQL).
- Para o **relatório PDF/DOCX**: **pandoc** e um motor **LaTeX** (ex.: TinyTeX). Se
  faltarem, é mesmo assim produzida a narrativa Markdown `.md` + as figuras PNG.
- Para a **cronologia OxCal**: pacote R **oxcAAR** e **Java** (o motor OxCal
  é descarregado automaticamente na primeira utilização por `oxcAAR::quickSetupOxcal()`).
- Para o **relatório AI**: um provedor LLM configurado (OpenAI, Anthropic, Ollama ou
  LM Studio) através do seletor Provider AI.

Os scripts R (`.rsx`) estão **incluídos no plugin** e instalados automaticamente
ao abrir a janela; o botão *Install/update R scripts* reinstala-os
manualmente.

---

## 2. Abrir a janela

1. Barra de ferramentas pyArchInit → menu de análise → **palimpsestr - Analisi
   palinsesti**.
2. A janela mostra a base de dados ativa (SQLite ou PostgreSQL) e os parâmetros.

---

## 3. Parâmetros da análise

| Parâmetro | Significado |
|---|---|
| **Número de fases (K)** | quantas fases latentes estimar (2–12) |
| **Modelo de classe** | `multinomial` (recomendado) ou `gaussiano` (legado) |
| **Componente de ruído/outlier** | ativa a estimativa de intrusões/residualidade |
| **Limiar de intrusões** | posterior mínima para assinalar um achado como intrusão |
| **Achados (source)** | **Ambos** / **Materiais** / **Cerâmica** |
| **Sítio (filtro)** | limita a análise a um sítio (vazio = todos) |

O seletor **Achados** é partilhado por Fit, Intrusões e Relatório: todos respeitam
a mesma seleção de achados.

---

## 4. Fit SEF e Intrusões

- **Fit SEF model**: executa a decomposição e carrega no projeto as camadas
  *SEF phases* (pontos coloridos por fase) e *SEF links*, além da tabela
  de diagnóstico.
- **Detect intrusions**: carrega uma camada de pontos com `intrusion_prob`,
  `direction` e `intrusion_type`.

---

## 5. Relatório narrado (PDF/DOCX)

1. Defina **Idioma do relatório** (Italiano/English) e **Formato** (PDF+DOCX / PDF /
   DOCX).
2. Prima **Genera report (PDF/DOCX)**.
3. O **painel de resultados** mostra a narrativa lendo o ficheiro `.md` que
   é **sempre** escrito junto ao output.
4. Os botões **Apri PDF / Apri DOCX / Apri cartella** ficam ativos consoante os
   ficheiros efetivamente produzidos.

> Se aparecerem apenas a narrativa `.md` e as figuras (sem PDF/DOCX), faltam
> pandoc/LaTeX: a janela tenta adicioná-los automaticamente ao `PATH`; caso
> contrário, instale-os (em R: `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

As análises funcionam também sobre a conexão **PostgreSQL** ativa do
pyArchInit, não apenas em SQLite. A janela converte automaticamente a URL de
conexão numa DSN libpq e passa-a aos algoritmos (parâmetro
`PG_connection`); com PostgreSQL ativo não é solicitado qualquer ficheiro SQLite.

---

## 7. Cronologia absoluta (OxCal)

A tabela opcional **`palimpsest_chronology`** fornece datas **calibradas por
US** (anos calendários, a.C. negativos) que o palimpsestr usa **em vez** da
`datazione` textual.

1. Prima **Cronologia assoluta (OxCal)…**.
2. **Crea/aggiorna tabella**: cria `palimpsest_chronology` no backend ativo
   (SQLite ou PostgreSQL), de modo idempotente.
3. **Calibração ao vivo**: insira para cada US as datas radiocarbónicas
   (BP ± erro, código lab) e prima **Calibra e salva (OxCal)**: um driver R
   (`oxcAAR::oxcalCalibrate` + `palimpsestr::chronology_from_oxcal`) calcula os
   intervalos calendários e guarda-os como `start`/`end`.
4. **Importação CSV**: em alternativa, importe um CSV já calibrado com colunas
   `sito, area, us, start, end, lab_code, source`.

Os dados de exemplo estão em `docs/examples/`:
`palimpsest_oxcal_samples_villa_romana.csv` (amostras C14 para a calibração) e
`palimpsest_chronology_villa_romana.csv` (intervalos já calibrados).

> Uma vez preenchida, a tabela é detetada **automaticamente**: não é preciso
> alterar nada nos algoritmos.

---

## 8. Relatório AI (análise descritiva)

O botão **Report AI (analisi descrittiva)…** gera um relatório
**descritivo e didático** com uma pipeline de **agentes AI especializados**:

1. **Metodólogo** — explica as escolhas: o modelo (multinomial vs gaussiano), o
   valor de **K** e as evidências de diagnóstico que o justificam, a
   componente de ruído e o **limiar**, a seleção dos achados e o uso da
   cronologia OxCal; indica limites e cautelas.
2. **Analista** — interpreta as fases, a cronologia (com as datas absolutas se
   presentes), a residualidade/intrusões e o padrão espacial.
3. **Redator** — compõe um único relatório coeso, referenciando as figuras.

Procedimento:

1. Escolha o **Provider AI** e o modelo no seletor.
2. Escolha o **Idioma do relatório** (todos os idiomas do pyArchInit:
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Prima **Genera report AI**: o texto aparece em tempo real.
4. Guarde como **DOCX** (com as figuras incorporadas) ou **Markdown**.

O relatório explica explicitamente **porquê** foram escolhidos o modelo, o K e
o limiar, e interpreta os resultados de modo compreensível — o ideal para o
relatório de escavação.

> **Provedor de IA e compatibilidade.** O relatório de IA do palimpsest usa o provedor LLM configurado (OpenAI, Anthropic, Ollama ou LM Studio) através de `LLMProviderManager`; os erros de provedor/SDK são agora apresentados com uma **mensagem clara** em vez de uma exceção críptica. O relatório de IA funciona tanto em **QGIS 3.x** (Python 3.9) como em **QGIS 4.x** (Python ≥ 3.10), com instalação automática das dependências.
>
> A **Consulta à base de dados com IA (RAG / Text2SQL)** é uma funcionalidade **separada** do palimpsest (ver *Tutorial 30 — AI Query Database*): no QGIS 4.x usa langchain 1.x e foi tornada compatível na versão **5.13.5-alpha**. Se uma funcionalidade de IA parar com um erro de importação do langchain (por exemplo `No module named 'langchain.text_splitter'` ou `cannot import name 'Tool' from 'langchain.agents'`), atualize o plugin e reinstale as dependências.

---

## 9. Editar as datas, gráfico OxCal, PDF e nota sobre o taf

- **Editor por US (Cronologia e tafonomia)**: o diálogo pré-carrega **todas as US do sítio** com duas colunas informativas **Período** e **N.º de achados**, para que possa atribuir o **taf** a cada US (não apenas às datadas). O taf é tido em conta pelo Fit, pelas Intrusions, pelo Report e pelo relatório da IA: reduz o peso das US redepositadas ou perturbadas. Apenas as US preenchidas (com taf e/ou uma data) são guardadas.
- **As datas guardadas podem ser editadas**: o diálogo *Cronologia assoluta*
  **carrega ao abrir** as datas já presentes em `palimpsest_chronology` (botão
  *Ricarica dal DB*). Pode editar manualmente as colunas **start/end** e premir
  **Salva modifiche (start/end)**; ou inserir novas datas C14 e premir
  *Calibra e salva*. As datas **persistem** na base de dados: não é preciso
  reinseri-las de cada vez.
- **Gráfico de calibração**: após *Calibra e salva*, os botões **Mostra grafico
  OxCal** / **Esporta grafico (PNG)** mostram um painel por US com a curva de
  probabilidade, a banda 95% HPD e o intervalo calendário.
- **Relatório AI em PDF**: além de DOCX e Markdown, o relatório AI pode ser
  guardado em **PDF** (botão *Salva PDF…*), com tabelas e figuras incorporadas.
- **Pontuação tafonómica (taf)**: é um valor **interpretativo** em `[0,1]`
  (0 = achado totalmente perturbado/redepositado, 1 = íntegro in situ) que pondera
  os achados na estimativa. **Não é calculado automaticamente**: é o arqueólogo
  que o atribui com base no contexto deposicional (ex.: 1.0 depósitos in situ;
  0.5–0.7 acumulações/nivelamentos; 0.3 enchimentos claramente redepositados).
- **Coordenadas pontuais dos achados** (palimpsestr ≥ 0.23.0): quando um achado
  é desenhado como ponto em `pyarchinit_reperti` (ligado a
  `inventario_materiali_table` pela junção `pyarchinit_reperti_view`, ou seja
  sítio + número de inventário = `id_rep`), a análise usa as suas próprias x, y
  (e z a partir da `quota` do ponto) em vez do centroide da US. Os achados sem
  ponto mantêm o centroide da US. Onde o desenho pontual está disponível, isto
  confere uma resolução espacial ao nível do achado e atenua a limitação do
  centroide indicada a seguir. Não há nada a configurar — o diálogo deteta e usa
  os pontos automaticamente.
- **Limites a recordar** (o relatório AI declara-os automaticamente): o modelo
  pressupõe **estratigrafia horizontal** (z como proxy cronológico; cautela com
  enchimentos de cortes, colapsos, terraçamentos); a **resolução está vinculada
  ao dado**: com coordenadas do centroide da US e datas ligadas à US, um PDI≈1 e
  entropia≈0 refletem o **registo**, não uma sequência perfeitamente resolvida
  (os achados pontuais, quando presentes, melhoram a resolução espacial).

---

*Documentação PyArchInit — Junho 2026*
