# Tutorial 37: Anàlisi de palimpsests (palimpsestr / SEF)

## Introducció

PyArchInit integra **palimpsestr**, una biblioteca R que aplica el model
**SEF — Stratigraphic Entanglement Field** per a la *descomposició probabilística
dels palimpsests*: separa, sobre una base estadística, les troballes d'un dipòsit
complex en **fases** latents, estimant per a cada unitat estratigràfica (US) la
fase de pertinença, la residualitat i les eventuals **intrusions**.

El quadre **palimpsestr** (icona d'estrats acolorits a la barra d'eines
pyArchInit) permet:

- **Fit SEF**: estimar les fases i produir capes vectorials (fases, enllaços) i
  una taula de diagnòstic;
- **Intrusions**: detectar troballes/US fora de lloc cronològicament;
- **Informe narrat (PDF/DOCX)**: un informe interpretatiu amb text, gràfics de
  diagnòstic i taules;
- **Informe AI**: un informe descriptiu generat per agents AI especialitzats, en
  qualsevol llengua de pyArchInit;
- treballar tant amb **SQLite/Spatialite** com amb **PostgreSQL/PostGIS**;
- utilitzar una **cronologia absoluta** (dates calibrades OxCal) en lloc de la
  datació textual.

> Requereix palimpsestr **≥ 0.22.0** instal·lat a la biblioteca R utilitzada pel
> *Processing R Provider* de QGIS.

---

## 1. Requisits previs

- **R** instal·lat i el connector **Processing R Provider** actiu a QGIS.
- Paquet R **palimpsestr ≥ 0.22.0** (**≥ 0.22.1** per a la puntuació taf; **≥ 0.23.0**
  per a les coordenades de troballes registrades puntualment) (i dependències: `sf`,
  `DBI`, `RSQLite`; `RPostgres` per a PostgreSQL).
- Per a l'**informe PDF/DOCX**: **pandoc** i un motor **LaTeX** (p. ex. TinyTeX).
  Si manquen, igualment es produeix la narrativa Markdown `.md` + les figures PNG.
- Per a la **cronologia OxCal**: paquet R **oxcAAR** i **Java** (el motor OxCal es
  descarrega automàticament al primer ús mitjançant
  `oxcAAR::quickSetupOxcal()`).
- Per a l'**informe AI**: un proveïdor LLM configurat (OpenAI, Anthropic, Ollama o
  LM Studio) mitjançant el selector Proveïdor AI.

Els scripts R (`.rsx`) estan **inclosos al connector** i s'instal·len
automàticament en obrir el quadre; el botó *Install/update R scripts* els
reinstal·la manualment.

---

## 2. Obrir el quadre

1. Barra d'eines pyArchInit → menú d'anàlisi → **palimpsestr - Analisi
   palinsesti** (Anàlisi de palimpsests).
2. El quadre mostra la base de dades activa (SQLite o PostgreSQL) i els
   paràmetres.

---

## 3. Paràmetres de l'anàlisi

| Paràmetre | Significat |
|---|---|
| **Nombre de fases (K)** | quantes fases latents estimar (2–12) |
| **Model de classe** | `multinomial` (recomanat) o `gaussià` (legacy) |
| **Component de soroll/outlier** | activa l'estimació d'intrusions/residualitat |
| **Llindar d'intrusions** | posterior mínima per a marcar una troballa com a intrusió |
| **Troballes (source)** | **Ambdós** / **Materials** / **Ceràmica** |
| **Lloc (filtre)** | limita l'anàlisi a un lloc (buit = tots) |

El selector **Troballes** és compartit per Fit, Intrusions i Informe: tots
respecten la mateixa selecció de troballes.

---

## 4. Fit SEF i Intrusions

- **Fit SEF model**: executa la descomposició i carrega al projecte les capes
  *SEF phases* (punts acolorits per fase) i *SEF links*, a més de la taula de
  diagnòstic.
- **Detect intrusions**: carrega una capa de punts amb `intrusion_prob`,
  `direction` i `intrusion_type`.

---

## 5. Informe narrat (PDF/DOCX)

1. Estableix la **Llengua de l'informe** (Italià/Anglès) i el **Format**
   (PDF+DOCX / PDF / DOCX).
2. Prem **Genera report (PDF/DOCX)** (Genera informe).
3. El **panell de resultats** mostra la narrativa llegint el fitxer `.md` que
   s'escriu **sempre** al costat de la sortida.
4. Els botons **Apri PDF / Apri DOCX / Apri cartella** (Obre PDF / Obre DOCX /
   Obre carpeta) s'activen segons els fitxers efectivament produïts.

> Si només apareixen la narrativa `.md` i les figures (cap PDF/DOCX), manquen
> pandoc/LaTeX: el quadre intenta afegir-los automàticament al `PATH`; en cas
> contrari, instal·la'ls (a R: `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

Les anàlisis també funcionen sobre la connexió **PostgreSQL** activa de
pyArchInit, no només sobre SQLite. El quadre converteix automàticament la URL de
connexió en una DSN libpq i la passa als algorismes (paràmetre `PG_connection`);
amb PostgreSQL actiu no es demana cap fitxer SQLite.

---

## 7. Cronologia absoluta (OxCal)

La taula opcional **`palimpsest_chronology`** proporciona dates **calibrades per
US** (anys calendaris, a.C. negatius) que palimpsestr utilitza **en lloc de** la
`datazione` textual.

1. Prem **Cronologia assoluta (OxCal)…** (Cronologia absoluta).
2. **Crea/aggiorna tabella** (Crea/actualitza taula): crea `palimpsest_chronology`
   al backend actiu (SQLite o PostgreSQL), de manera idempotent.
3. **Calibratge en directe**: introdueix per a cada US les dates radiocarbòniques
   (BP ± error, codi de laboratori) i prem **Calibra e salva (OxCal)** (Calibra i
   desa): un controlador R (`oxcAAR::oxcalCalibrate` +
   `palimpsestr::chronology_from_oxcal`) calcula els intervals calendaris i els
   desa com a `start`/`end`.
4. **Importació CSV**: alternativament, importa un CSV ja calibrat amb columnes
   `sito, area, us, start, end, lab_code, source`.

Les dades d'exemple són a `docs/examples/`:
`palimpsest_oxcal_samples_villa_romana.csv` (mostres C14 per al calibratge) i
`palimpsest_chronology_villa_romana.csv` (intervals ja calibrats).

> Un cop poblada, la taula es detecta **automàticament**: no cal modificar res als
> algorismes.

---

## 8. Informe AI (anàlisi descriptiva)

El botó **Report AI (analisi descrittiva)…** (Informe AI - anàlisi descriptiva)
genera un informe **descriptiu i didàctic** amb una canalització d'**agents AI
especialitzats**:

1. **Metodòleg** — explica les decisions: el model (multinomial vs gaussià), el
   valor de **K** i les evidències de diagnòstic que el justifiquen, la component
   de soroll i el **llindar**, la selecció de troballes i l'ús de la cronologia
   OxCal; indica límits i cauteles.
2. **Analista** — interpreta fases, cronologia (amb les dates absolutes si hi
   són), residualitat/intrusions i patró espacial.
3. **Redactor** — compon un únic informe cohesionat, fent referència a les
   figures.

Procediment:

1. Tria el **Proveïdor AI** i el model al selector.
2. Tria la **Llengua de l'informe** (totes les llengües de pyArchInit:
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Prem **Genera report AI** (Genera informe AI): el text apareix en temps real.
4. Desa com a **DOCX** (amb les figures incorporades) o **Markdown**.

L'informe explica explícitament **per què** s'han triat el model, la K i el
llindar, i interpreta els resultats de manera comprensible — l'ideal per a
l'informe d'excavació.

> **Proveïdor AI i compatibilitat.** L'informe AI del palimpsest utilitza el
> proveïdor LLM configurat (OpenAI, Anthropic, Ollama o LM Studio) mitjançant
> `LLMProviderManager`; els errors del proveïdor/SDK ara es mostren amb un
> **missatge clar** en lloc d'una excepció críptica. L'informe AI funciona tant
> a **QGIS 3.x** (Python 3.9) com a **QGIS 4.x** (Python ≥ 3.10), amb instal·lació
> automàtica de les dependències.
>
> La **Consulta AI de la base de dades (RAG / Text2SQL)** és una funcionalitat
> **independent** del palimpsest (vegeu *Tutorial 30 — AI Query Database*): a
> QGIS 4.x utilitza langchain 1.x i es va fer compatible a la **5.13.5-alpha**.
> Si una funcionalitat AI s'atura amb un error d'importació de langchain (p. ex.
> `No module named 'langchain.text_splitter'` o
> `cannot import name 'Tool' from 'langchain.agents'`), actualitza el connector i
> reinstal·la les dependències.

---

## 9. Modificar les dates, gràfic OxCal, PDF i nota sobre el taf

- **Editor per US (Cronologia i tafonomia)**: el diàleg precarrega **totes les US del jaciment** amb dues columnes informatives **Període** i **N. troballes**, de manera que pots assignar el **taf** a cada US (no només a les datades). El taf és tingut en compte per Fit, Intrusions, Report i l'informe d'IA: redueix el pes de les US redipositades o alterades. Només es desen les US emplenades (amb taf i/o una data).
- **Les dates desades es poden modificar**: el diàleg *Cronologia absoluta*
  **carrega en obrir-se** les dates ja presents a `palimpsest_chronology` (botó
  "Ricarica dal DB"). Pots modificar a mà les columnes **start/end** i prémer
  "Salva modifiche (start/end)"; o bé introduir noves dates C14 i prémer
  "Calibra e salva". Les dates **persisteixen** a la base de dades: no cal
  reintroduir-les cada vegada.
- **Gràfic de calibratge**: després de "Calibra e salva" els botons "Mostra
  grafico OxCal" / "Esporta grafico (PNG)" mostren un panell per US amb la corba
  de probabilitat, la banda 95% HPD i l'interval calendari.
- **Informe AI en PDF**: a més de DOCX i Markdown, l'informe AI es pot desar en
  **PDF** (botó "Salva PDF…"), amb taules i figures incorporades.
- **Puntuació tafonòmica (taf)**: és un valor **interpretatiu** dins de `[0,1]`
  (0 = troballa del tot pertorbada/redipositada, 1 = íntegra in situ) que pondera
  les troballes en l'estimació. **No es calcula automàticament**: l'assigna
  l'arqueòleg en funció del context deposicional (p. ex. 1.0 dipòsits in situ;
  0.5–0.7 acumulacions/anivellaments; 0.3 farciments clarament redipositats).
- **Coordenades de troballes registrades puntualment** (palimpsestr ≥ 0.23.0): quan
  una troballa es dibuixa com a punt a `pyarchinit_reperti` (vinculada a
  `inventario_materiali_table` mitjançant la unió `pyarchinit_reperti_view`, és a dir
  lloc + número d'inventari = `id_rep`), l'anàlisi utilitza les seves pròpies x, y (i
  la z a partir de la `quota` del punt) en lloc del centroide de l'US. Les troballes
  sense punt conserven el centroide de l'US. Allà on hi ha registre puntual, això
  proporciona una resolució espacial a nivell de troballa i mitiga la limitació del
  centroide indicada a continuació. No cal configurar res — el diàleg detecta i
  utilitza els punts automàticament.
- **Límits a recordar** (l'informe AI els declara automàticament): el model
  assumeix **estratigrafia horitzontal** (z com a indicador cronològic; cautela
  amb farciments de talls, esfondraments, terrasses); la **resolució està
  limitada per la dada**: amb coordenades del centroide US i dates lligades a
  l'US, un PDI≈1 i entropia≈0 reflecteixen el **registre**, no una seqüència
  perfectament resolta (les troballes registrades puntualment, quan hi són,
  milloren la resolució espacial).

---

*Documentació PyArchInit — Juny 2026*
