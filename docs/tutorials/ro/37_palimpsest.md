# Tutorial 37: Analiza palimpsestelor (palimpsestr / SEF)

## Introducere

PyArchInit integrează **palimpsestr**, o bibliotecă R care aplică modelul
**SEF — Stratigraphic Entanglement Field** pentru *descompunerea probabilistică
a palimpsestelor*: separă, pe baze statistice, materialele unui depozit complex
în **faze** latente, estimând pentru fiecare unitate stratigrafică (US) faza de
apartenență, rezidualitatea și eventualele **intruziuni**.

Fereastra **palimpsestr** (pictograma cu straturi colorate din bara de
instrumente pyArchInit) permite:

- **Fit SEF**: estimarea fazelor și producerea de straturi vectoriale (faze,
  legături) și a unui tabel de diagnosticare;
- **Intruziuni**: identificarea materialelor/US deplasate cronologic;
- **Raport narativ (PDF/DOCX)**: un raport interpretativ cu text, grafice de
  diagnosticare și tabele;
- **Raport AI**: un raport descriptiv generat de agenți AI specializați, în orice
  limbă a pyArchInit;
- lucrul atât pe **SQLite/Spatialite**, cât și pe **PostgreSQL/PostGIS**;
- folosirea unei **cronologii absolute** (date calibrate OxCal) în locul datării
  textuale.

> Necesită palimpsestr **≥ 0.22.0** instalat în biblioteca R folosită de
> *Processing R Provider* din QGIS.

---

## 1. Cerințe prealabile

- **R** instalat și pluginul **Processing R Provider** activ în QGIS.
- Pachetul R **palimpsestr ≥ 0.22.0** (și dependențele: `sf`, `DBI`, `RSQLite`;
  `RPostgres` pentru PostgreSQL).
- Pentru **raportul PDF/DOCX**: **pandoc** și un motor **LaTeX** (de ex. TinyTeX).
  Dacă lipsesc, sunt produse oricum narațiunea Markdown `.md` + figurile PNG.
- Pentru **cronologia OxCal**: pachetul R **oxcAAR** și **Java** (motorul OxCal
  este descărcat automat la prima utilizare prin `oxcAAR::quickSetupOxcal()`).
- Pentru **raportul AI**: un furnizor LLM configurat (OpenAI, Anthropic, Ollama
  sau LM Studio) prin selectorul Furnizor AI.

Scripturile R (`.rsx`) sunt **incluse în plugin** și instalate automat la
deschiderea ferestrei; butonul *Install/update R scripts* le reinstalează manual.

---

## 2. Deschiderea ferestrei

1. Bara de instrumente pyArchInit → meniul de analiză → **palimpsestr - Analisi
   palinsesti** (Analiza palimpsestelor).
2. Fereastra afișează baza de date activă (SQLite sau PostgreSQL) și parametrii.

---

## 3. Parametrii analizei

| Parametru | Semnificație |
|---|---|
| **Numărul de faze (K)** | câte faze latente să fie estimate (2–12) |
| **Modelul de clasă** | `multinomial` (recomandat) sau `gaussian` (legacy) |
| **Componenta de zgomot/outlier** | activează estimarea intruziunilor/rezidualității |
| **Pragul intruziunilor** | posterior minim pentru a marca un material ca intruziune |
| **Materiale (source)** | **Ambele** / **Materiale** / **Ceramică** |
| **Sit (filtru)** | limitează analiza la un sit (gol = toate) |

Selectorul **Materiale** este partajat de Fit, Intruziuni și Raport: toate
respectă aceeași selecție de materiale.

---

## 4. Fit SEF și Intruziuni

- **Fit SEF model**: execută descompunerea și încarcă în proiect straturile
  *SEF phases* (puncte colorate pe faze) și *SEF links*, alături de tabelul de
  diagnosticare.
- **Detect intrusions**: încarcă un strat de puncte cu `intrusion_prob`,
  `direction` și `intrusion_type`.

---

## 5. Raport narativ (PDF/DOCX)

1. Setează **Limba raportului** (Italiană/Engleză) și **Formatul** (PDF+DOCX /
   PDF / DOCX).
2. Apasă **Genera report (PDF/DOCX)** (Generează raport).
3. **Panoul de rezultate** afișează narațiunea citind fișierul `.md` care este
   **întotdeauna** scris alături de output.
4. Butoanele **Apri PDF / Apri DOCX / Apri cartella** (Deschide PDF / Deschide
   DOCX / Deschide folderul) se activează în funcție de fișierele efectiv produse.

> Dacă apar doar narațiunea `.md` și figurile (fără PDF/DOCX), lipsesc
> pandoc/LaTeX: fereastra încearcă să le adauge automat în `PATH`; în caz contrar
> instalează-le (în R: `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

Analizele funcționează și pe conexiunea **PostgreSQL** activă a pyArchInit, nu
doar pe SQLite. Fereastra convertește automat URL-ul de conexiune într-un DSN
libpq și îl transmite algoritmilor (parametrul `PG_connection`); cu PostgreSQL
activ nu este cerut niciun fișier SQLite.

---

## 7. Cronologia absolută (OxCal)

Tabelul opțional **`palimpsest_chronology`** furnizează date **calibrate per US**
(ani calendaristici, î.Hr. negativi) pe care palimpsestr le folosește **în locul**
`datazione` textuale.

1. Apasă **Cronologia assoluta (OxCal)…** (Cronologie absolută).
2. **Crea/aggiorna tabella** (Creează/actualizează tabelul): creează
   `palimpsest_chronology` pe backendul activ (SQLite sau PostgreSQL), în mod
   idempotent.
3. **Calibrare live**: introdu pentru fiecare US datele radiocarbon
   (BP ± eroare, cod lab) și apasă **Calibra e salva (OxCal)** (Calibrează și
   salvează): un driver R (`oxcAAR::oxcalCalibrate` +
   `palimpsestr::chronology_from_oxcal`) calculează intervalele calendaristice și
   le salvează ca `start`/`end`.
4. **Import CSV**: ca alternativă, importă un CSV deja calibrat cu coloanele
   `sito, area, us, start, end, lab_code, source`.

Datele de exemplu sunt în `docs/examples/`:
`palimpsest_oxcal_samples_villa_romana.csv` (eșantioane C14 pentru calibrare) și
`palimpsest_chronology_villa_romana.csv` (intervale deja calibrate).

> Odată populat, tabelul este detectat **automat**: nu trebuie modificat nimic în
> algoritmi.

---

## 8. Raport AI (analiză descriptivă)

Butonul **Report AI (analisi descrittiva)…** (Raport AI — analiză descriptivă)
generează un raport **descriptiv și didactic** cu un flux de **agenți AI
specializați**:

1. **Metodolog** — explică alegerile: modelul (multinomial vs gaussian), valoarea
   lui **K** și dovezile de diagnosticare care o justifică, componenta de zgomot
   și **pragul**, selecția materialelor și utilizarea cronologiei OxCal; indică
   limitele și precauțiile.
2. **Analist** — interpretează fazele, cronologia (cu datele absolute dacă sunt
   prezente), rezidualitatea/intruziunile și tiparul spațial.
3. **Redactor** — compune un singur raport coerent, făcând referire la figuri.

Procedură:

1. Alege **Furnizorul AI** și modelul în selector.
2. Alege **Limba raportului** (toate limbile pyArchInit:
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Apasă **Genera report AI** (Generează raport AI): textul apare în timp real.
4. Salvează ca **DOCX** (cu figurile încorporate) sau **Markdown**.

Raportul explică în mod explicit **de ce** au fost alese modelul, K-ul și pragul,
și interpretează rezultatele într-un mod inteligibil — ideal pentru raportul de
săpătură.

---

## 9. Modificarea datelor, graficul OxCal, PDF și o notă despre taf

- **Editor per US (Cronologie și tafonomie)**: fereastra de dialog preîncarcă **toate US-urile sitului** cu două coloane informative **Perioadă** și **Nr. reperelor**, astfel încât poți atribui valoarea **taf** fiecărui US (nu doar celor datate). taf este respectată de Fit, Intrusions, Report și de raportul AI: reduce ponderea US-urilor redepuse sau deranjate. Se salvează doar US-urile completate (cu taf și/sau o dată).
- **Datele salvate sunt editabile**: fereastra *Cronologia assoluta* **încarcă la
  deschidere** datele deja prezente în `palimpsest_chronology` (butonul *Ricarica
  dal DB*). Poți modifica manual coloanele **start/end** și apăsa **Salva
  modifiche (start/end)**, sau introduce date C14 noi și apăsa *Calibra e salva*.
  Datele **persistă** în baza de date — nu trebuie reintroduse de fiecare dată.
- **Graficul de calibrare**: după *Calibra e salva*, butoanele **Mostra grafico
  OxCal** / **Esporta grafico (PNG)** afișează un panou per US cu curba de
  probabilitate, banda 95% HPD și intervalul calendaristic.
- **Raportul AI în PDF**: pe lângă DOCX și Markdown, raportul AI poate fi salvat
  în **PDF** (butonul *Salva PDF…*), cu tabele și figuri încorporate.
- **Scorul tafonomic (taf)**: este o valoare **interpretativă** în `[0,1]`
  (0 = material complet deranjat/redepus, 1 = integru în poziție) care ponderează
  materialele în estimare. **Nu este calculat automat**: îl atribuie arheologul în
  funcție de contextul depozițional (de ex. 1.0 depozite in situ; 0.5–0.7 straturi
  de acumulare/nivelare; 0.3 umpluturi clar redepuse).
- **Limite de reținut** (raportul AI le declară automat): modelul presupune
  **stratigrafie orizontală** (z ca proxy cronologic; prudență cu umpluturi de
  tăieturi, prăbușiri, terasări); **rezoluția este limitată de dată**: cu
  coordonate ale centroidului US și date legate de US, un PDI≈1 și entropie≈0
  reflectă **înregistrarea**, nu o secvență perfect rezolvată.

---

*Documentație PyArchInit — Iunie 2026*
