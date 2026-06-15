# Tutorial 37: Analisi dei palinsesti (palimpsestr / SEF)

## Introduzione

PyArchInit integra **palimpsestr**, una libreria R che applica il modello
**SEF — Stratigraphic Entanglement Field** per la *decomposizione probabilistica
dei palinsesti*: separa, su base statistica, i reperti di un deposito complesso
in **fasi** latenti, stimando per ogni unità stratigrafica (US) la fase di
appartenenza, la residualità e le eventuali **intrusioni**.

La scheda **palimpsestr** (icona a strati colorati nella barra strumenti
pyArchInit) consente di:

- **Fit SEF**: stimare le fasi e produrre layer vettoriali (fasi, link) e una
  tabella diagnostica;
- **Intrusioni**: individuare reperti/US fuori posto cronologicamente;
- **Report narrato (PDF/DOCX)**: una relazione interpretativa con testo, grafici
  diagnostici e tabelle;
- **Report AI**: una relazione descrittiva generata da agenti AI specializzati,
  in qualsiasi lingua di pyArchInit;
- lavorare sia su **SQLite/Spatialite** sia su **PostgreSQL/PostGIS**;
- usare una **cronologia assoluta** (date calibrate OxCal) al posto della
  datazione testuale.

> Richiede palimpsestr **≥ 0.22.0** installato nella libreria R usata dal
> *Processing R Provider* di QGIS.

---

## 1. Prerequisiti

- **R** installato e il plugin **Processing R Provider** attivo in QGIS.
- Pacchetto R **palimpsestr ≥ 0.22.0** (e dipendenze: `sf`, `DBI`, `RSQLite`;
  `RPostgres` per PostgreSQL).
- Per il **report PDF/DOCX**: **pandoc** e un motore **LaTeX** (es. TinyTeX). Se
  mancano, viene comunque prodotta la narrativa Markdown `.md` + le figure PNG.
- Per la **cronologia OxCal**: pacchetto R **oxcAAR** e **Java** (il motore OxCal
  viene scaricato automaticamente al primo uso da `oxcAAR::quickSetupOxcal()`).
- Per il **report AI**: un provider LLM configurato (OpenAI, Anthropic, Ollama o
  LM Studio) tramite il selettore Provider AI.

Gli script R (`.rsx`) sono **inclusi nel plugin** e installati automaticamente
all'apertura della scheda; il pulsante *Install/update R scripts* li
reinstalla manualmente.

---

## 2. Aprire la scheda

1. Barra strumenti pyArchInit → menu di analisi → **palimpsestr - Analisi
   palinsesti**.
2. La scheda mostra il database attivo (SQLite o PostgreSQL) e i parametri.

---

## 3. Parametri dell'analisi

| Parametro | Significato |
|---|---|
| **Numero di fasi (K)** | quante fasi latenti stimare (2–12) |
| **Modello di classe** | `multinomiale` (consigliato) o `gaussiano` (legacy) |
| **Componente di rumore/outlier** | attiva la stima di intrusioni/residualità |
| **Soglia intrusioni** | posterior minima per segnalare un reperto come intrusione |
| **Reperti (source)** | **Entrambi** / **Materiali** / **Ceramica** |
| **Sito (filtro)** | limita l'analisi a un sito (vuoto = tutti) |

Il selettore **Reperti** è condiviso da Fit, Intrusioni e Report: tutti onorano
la stessa selezione di reperti.

---

## 4. Fit SEF e Intrusioni

- **Fit SEF model**: esegue la decomposizione e carica nel progetto i layer
  *SEF phases* (punti colorati per fase) e *SEF links*, oltre alla tabella
  diagnostica.
- **Detect intrusions**: carica un layer di punti con `intrusion_prob`,
  `direction` e `intrusion_type`.

---

## 5. Report narrato (PDF/DOCX)

1. Imposta **Lingua report** (Italiano/English) e **Formato** (PDF+DOCX / PDF /
   DOCX).
2. Premi **Genera report (PDF/DOCX)**.
3. Il **pannello risultati** mostra la narrativa leggendo il file `.md` che
   viene **sempre** scritto accanto all'output.
4. I pulsanti **Apri PDF / Apri DOCX / Apri cartella** si abilitano in base ai
   file effettivamente prodotti.

> Se compaiono solo la narrativa `.md` e le figure (niente PDF/DOCX), mancano
> pandoc/LaTeX: la scheda prova ad aggiungerli automaticamente al `PATH`; in
> caso contrario installali (in R: `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

Le analisi funzionano anche sulla connessione **PostgreSQL** attiva di
pyArchInit, non solo su SQLite. La scheda converte automaticamente la URL di
connessione in una DSN libpq e la passa agli algoritmi (parametro
`PG_connection`); con PostgreSQL attivo non viene richiesto alcun file SQLite.

---

## 7. Cronologia assoluta (OxCal)

La tabella opzionale **`palimpsest_chronology`** fornisce date **calibrate per
US** (anni calendariali, a.C. negativi) che palimpsestr usa **al posto** della
`datazione` testuale.

1. Premi **Cronologia assoluta (OxCal)…**.
2. **Crea/aggiorna tabella**: crea `palimpsest_chronology` sul backend attivo
   (SQLite o PostgreSQL), in modo idempotente.
3. **Calibrazione live**: inserisci per ogni US le date radiocarboniche
   (BP ± errore, codice lab) e premi **Calibra e salva (OxCal)**: un driver R
   (`oxcAAR::oxcalCalibrate` + `palimpsestr::chronology_from_oxcal`) calcola gli
   intervalli calendariali e li salva come `start`/`end`.
4. **Import CSV**: in alternativa importa un CSV già calibrato con colonne
   `sito, area, us, start, end, lab_code, source`.

I dati di esempio sono in `docs/examples/`:
`palimpsest_oxcal_samples_villa_romana.csv` (campioni C14 per la calibrazione) e
`palimpsest_chronology_villa_romana.csv` (intervalli già calibrati).

> Una volta popolata, la tabella viene rilevata **automaticamente**: non serve
> modificare nulla negli algoritmi.

---

## 8. Report AI (analisi descrittiva)

Il pulsante **Report AI (analisi descrittiva)…** genera una relazione
**descrittiva e didattica** con una pipeline di **agenti AI specializzati**:

1. **Metodologo** — spiega le scelte: modello (multinomiale vs gaussiano), il
   valore di **K** e le evidenze diagnostiche che lo giustificano, la
   componente di rumore e la **soglia**, la selezione dei reperti e l'uso della
   cronologia OxCal; indica limiti e cautele.
2. **Analista** — interpreta fasi, cronologia (con le date assolute se
   presenti), residualità/intrusioni e pattern spaziale.
3. **Redattore** — compone un unico report coeso, richiamando le figure.

Procedura:

1. Scegli il **Provider AI** e il modello nel selettore.
2. Scegli la **Lingua del report** (tutte le lingue di pyArchInit:
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Premi **Genera report AI**: il testo appare in tempo reale.
4. Salva come **DOCX** (con le figure incorporate) o **Markdown**.

Il report spiega esplicitamente **perché** sono stati scelti il modello, il K e
la soglia, e interpreta i risultati in modo comprensibile — l'ideale per la
relazione di scavo.

---

## 9. Modificare le date, grafico OxCal, PDF e nota sul taf

- **Le date salvate si modificano**: il dialog *Cronologia assoluta* **carica
  all'apertura** le date già presenti in `palimpsest_chronology` (pulsante
  *Ricarica dal DB*). Puoi modificare a mano le colonne **start/end** e premere
  **Salva modifiche (start/end)**; oppure inserire nuove date C14 e premere
  *Calibra e salva*. Le date **persistono** nel database: non vanno reinserite
  ogni volta.
- **Grafico di calibrazione**: dopo *Calibra e salva* i pulsanti **Mostra
  grafico OxCal** / **Esporta grafico (PNG)** mostrano un pannello per US con la
  curva di probabilità, la banda 95% HPD e l'intervallo calendariale.
- **Report AI in PDF**: oltre a DOCX e Markdown, il report AI può essere salvato
  in **PDF** (pulsante *Salva PDF…*), con tabelle e figure incorporate.
- **Punteggio tafonomico (taf)**: è un valore **interpretativo** in `[0,1]`
  (0 = reperto del tutto disturbato/redeposto, 1 = integro in posto) che pesa i
  reperti nella stima. **Non è calcolato automaticamente**: lo assegna
  l'archeologo in base al contesto deposizionale (es. 1.0 depositi in situ;
  0.5–0.7 accumuli/livellamenti; 0.3 riempimenti chiaramente redeposti).
- **Limiti da ricordare** (il report AI li dichiara automaticamente): il modello
  assume **stratigrafia orizzontale** (z come proxy cronologico; cautela con
  riempimenti di tagli, crolli, terrazzamenti); la **risoluzione è vincolata dal
  dato**: con coordinate del centroide US e date legate all'US, un PDI≈1 ed
  entropia≈0 riflettono la **registrazione**, non una sequenza perfettamente
  risolta.

---

*Documentazione PyArchInit — Giugno 2026*
