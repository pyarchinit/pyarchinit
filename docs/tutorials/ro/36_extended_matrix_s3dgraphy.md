# Tutorial 36: Export Extended Matrix și Bridge s3dgraphy

## Introducere

Începând cu versiunea **5.2.0-alpha** PyArchInit integrează un **bridge bidirecțional** cu biblioteca **s3dgraphy** (modelul de date Extended Matrix al lui Emanuel Demetrescu). Bridge-ul permite:

- **Exportarea** diagramei stratigrafice ca Extended Matrix în **em.json**, formatul pe care îl deschide EMStudio (vechiul export GraphML este retras)
- **Re-importul** modificărilor făcute în yEd (mutarea UE între perioade/grupuri) actualizând baza de date SQL
- **Atașarea paradatelor** (Author / License / Embargo) la nivelul sitului
- **Gruparea** UE după dimensiune (struttura, area, attivita, settore, ambient, saggio, quad_par sau grupuri ad-hoc)

Tag curent: `narrativa-del-file-5.13.128-alpha` (2026-10-17).

---

## 1. Cerințe

- Bază de date SQLite/Spatialite **sau PostgreSQL/PostGIS**: exportul în em.json este același pe ambele motoare (conexiunea este cea a proiectului; `export_site` acceptă `sqlite://` și `postgresql://`)
- **Migrarea Phase 1 node_uuid** aplicată automat la deschiderea bazei
- **EMStudio** pentru a deschide em.json (se instalează din **Extended Matrix → Installa EMStudio…**), sau panoul **Vedi la matrice…** din QGIS, care nu are nevoie de nimic altceva. **yEd** (https://www.yworks.com/products/yed) este necesar doar dacă imporți fișiere GraphML desenate acolo (§5)

> ⚠️ Pentru baze pre-5.2.0-alpha migrarea poate necesita repornirea QGIS.

---

## 2. Export Extended Matrix (butonul verde)

### 2.1 Deschiderea dialogului

1. Deschide **Fișa UE** a sitului dorit
2. Click pe butonul verde **"Esporta Extended Matrix"** (sub tab-ul Rapporti)

### 2.2 Tab "Export"

Fereastra spune în partea de sus la ce servește fiecare format. Conține:

- **Formati** (Formate): **DOT (Graphviz) — matrice di Harris** și **em.json (Extended Matrix, per EMStudio)**, bifate din start, plus **Matrice per fasi** (matrice pe faze, analiză cronologică), opțională. GraphML nu se mai exportă: JSON-ul acestei ferestre **este em.json**, exact fișierul pe care îl produce meniul **Extended Matrix → Esporta sito in em.json…** — același proiector, aceeași simbologie.
- **Opzioni** (Opțiuni): **Controlla la sequenza stratigrafica e segnala i problemi** (verifică secvența stratigrafică și semnalează problemele). Este singura opțiune rămasă, și acum este citită cu adevărat: fără bifă, verificarea nu se face. Cele două casete vechi care vorbeau cu yEd (sugestii de auto-layout, culori pe perioadă) au plecat împreună cu exportul GraphML.
- **Extended Matrix**: patru butoane lângă export — **Apri in EMStudio** și **Vedi la matrice** (ambele se aprind după un export em.json reușit; al doilea desenează matricea în QGIS, fără EMStudio), **Consegna alla stanza…** și **Apri la stanza**. Sunt aceleași intrări din meniul pyArchInit, la îndemână.

La apăsarea pe **Esporta** se cere **dosarul de destinație**.

Autorii, licențele, embargourile și grupurile se gestionează în fereastra **"Manage paradata"** (§3).

### 2.2.1 Sondaje: un singur graf pentru tot situl

Începând cu versiunea **5.13.109-alpha**, em.json conține **un singur graf**, cu unitățile tuturor sondajelor: nu e nimic de ales. Fereastra „Esporta Extended Matrix” nu mai are grupul „Saggi” (sondaje), iar intrările de meniu **Esporta sito in em.json…** și **Vedi la matrice…** cer doar situl.

Sondajul este câmpul **Saggio** din fișa US: rămâne un câmp ca celelalte, care poate fi folosit ca dimensiune pentru gruparea unităților (`saggio`, §4) și care ajunge în *briefing*-ul narațiunii (§10.4), dar nu mai împarte fișierul. Un fișier exportat cu versiunile anterioare (până la 5.13.108-alpha), cu un graf pe sondaj, se deschide în continuare în panoul matricei (§10.8).

### 2.3 Click pe "Esporta"

Fișierele care se nasc, în funcție de formatele bifate:
- `<sit>.em.json` — Extended Matrix, de deschis în EMStudio sau de livrat într-o cameră
- `Extended_Matrix_<sit>[_<area>].dot` — Graphviz DOT, pentru matricea Harris clasică
- `Extended_Matrix_<sit>[_<area>]_phased.json` — vizualizare per epocă

> **Locurile sunt incluse în em.json.** Locul sitului, lanțul toponim și grupurile de arii, sectoare, sondaje și încăperi ies împreună cu unitățile, legate prin muchii `is_in_location` (§4).

Rezumatul final listează fișierele și, pentru em.json, **câte noduri și câte muchii** au ieșit, cu eventualele avertismente.

> **Din 5.13.122-alpha em.json iese mai curat.** Fiecare unitate are **o singură** muchie către epoca în care se naște (înainte avea două identice: biblioteca o adăuga pe a ei după ce o reatașase deja pe cea a importatorului); **descrierea** nodului este definiția stratigrafică sau, dacă aceasta este goală, descrierea fișei (înainte ieșea cuvântul «None»); graful are un **nume**, cel al sitului (înainte EMStudio îl deschidea ca «Untitled»); o unitate care supraviețuiește până într-o epocă mai recentă are muchia `survive_in_epoch` către **fiecare** epocă intermediară, nu doar către ultima. Pentru un sit care provine dintr-un em.json de la EMStudio vezi și §5.0, «Fișierul em.json rămâne memorat».

> **GraphML nu se mai exportă**: matricea se privește și se validează în EMStudio, care citește em.json. Rândurile temporale (swimlane) ale vechiului GraphML au plecat cu el. GraphML supraviețuiește doar la **intrare**, pentru fișierele desenate în yEd (§5).

---

## 3. Dialog "Manage paradata" (4 tab-uri)

### 3.1 Acces
Click pe butonul **"Manage paradata"** în fișa UE (lângă butonul verde Export).

### 3.2 Cele 4 tab-uri

| Tab | Conținut | Fișier generat |
|---|---|---|
| **Authors** | Adaugă autori (nume + ORCID + rol) | `paradata_<sit>.graphml` |
| **Licenses** | Licență dataset (ex. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Date embargo + motiv | idem |
| **Groups** | Grupuri ad-hoc (nume + selecție UE membre) | `groups_<sit>.graphml` |

Fișierele se salvează lângă DB SQLite și sunt **versionabile în Git**.

---

## 4. Dimensiuni și tipuri de grup în em.json

Fișierul em.json exportat de pyArchInit poartă **grupurile de loc** (`LocationNodeGroup`) ale fișei UE, deosebite prin tipul `kind`: `toponym`, lanțul nazione → regione → provincia → comune și locul sitului (§4.1); `study`, **ariile**, **sectoarele** și **sondajele**; `functional`, **încăperile**. Fiecare unitate este legată de grupurile în care se află prin muchii `is_in_location`; identificatorul grupului spune câmpul din care provine (de exemplu `loc::area::study::1`). Fișierul nu poartă culori: le hotărăște cel care îl citește, EMStudio cu stilul lui propriu și panoul matricei din QGIS cu regulile vizuale ale bibliotecii s3dgraphy. Vechiul export GraphML colora grupurile după dimensiune: paleta aceea a fost retrasă odată cu el. Biblioteca știe și să grupeze după **structură**, **activitate**, **careu** și după grupuri ad-hoc, cu o apartenență primară și celelalte secundare (`is_primary`): pyArchInit nu i-o cere astăzi, iar în fișier atributul apare doar pe muchiile lanțului toponim, mereu fals.

### 4.1 Lanț toponim (5.6.0-alpha)

Câmpurile `site_table.{nazione, regione, provincia, comune}` sunt emise automat ca un lanț recursiv de `LocationNodeGroup(kind="toponym")` (parent: nazione → regione → provincia → comune). Nivelurile administrative goale sunt sărite fără a întrerupe lanțul. O deduplicare cross-sit garantează că aceeași `comune` prezentă în 2 situri devine **un singur nod partajat** în em.json.

---

## 4.2 Apartenență multidimensională (5.6.0-alpha)

O unitate poate fi în mai multe grupuri deodată — o arie, un sector, un sondaj, o încăpere, pe lângă locul sitului — și în fișier are câte o muchie `is_in_location` pentru fiecare, toate pe picior de egalitate. Exemplu: o UE cu `area=1`, `settore=1` și `ambient=Ambiente 3` are trei muchii, spre „1” (arie, `study`), „1” (sector, `study`) și „Ambiente 3” (`functional`), plus cea spre locul sitului, de unde urcă lanțul toponim. Distincția dintre apartenența primară și cea secundară (`is_primary`, cu `struttura` pe primul loc și `toponym` niciodată primar) ține de modelul bibliotecii, pentru cine îi cere grupurile după dimensiune: în fișierul em.json al pyArchInit nu există.

---

## 5. Round-trip (tab Import)

> **Ce se poate importa**: tab-ul Import citește acum și **em.json** — cel de la EMStudio sau de la nodul StratiGraph — și alege cititorul după extensia fișierului; un `.graphml` de yEd rămâne acceptat pentru fișierele de dinainte. Procedura de mai jos, mutarea UE între grupuri, se referă la calea yEd/GraphML.

### 5.0 Importul unui em.json din EMStudio (chiar și cu baza de date goală)

Un em.json scris de **EMStudio** (nu de pyArchInit) se importă în baza de date pyArchInit **chiar și atunci când baza de date este goală** (din 5.13.121-alpha): situl, perioadele, fișele, relațiile și fișierele media se nasc din fișier, fără a fi nevoie să creezi mai întâi vreun sit.

1. Deschide meniul **Plugins → pyArchInit - Archaeological GIS Tools** și alege intrarea **Extended Matrix → Importa em.json…** (Importă em.json): fereastra Extended Matrix se deschide direct pe tab-ul **Import**, chiar dacă baza de date nu are niciun sit. Din fișa US se ajunge în același loc: butonul verde **Esporta Extended Matrix**, fără un sit ales, deschide aceeași fereastră pe tab-ul Import în loc să se oprească (**exportul**, în schimb, continuă să ceară un sit).
2. Apasă **Browse…** și alege em.json.
3. Verifică **Sito target:** (situl-țintă). Dacă este gol — cazul unei baze de date fără situri —, se propune numele grafului scris în em.json (de exemplu «Temple») sau, dacă lipsește, numele fișierului fără «.em.json»; poate fi modificat. Dacă în câmp apare deja un sit (cu o bază de date care are situri: cel al fișei US din care ai pornit sau, din meniu, primul în ordine alfabetică), nu se propune niciun nume: scrie numele sitului nou sau alege-l pe cel în care vrei să imporți. Dedesubt sunt două căsuțe, bifate implicit: **Crea periodi mancanti se assenti** (Creează perioadele lipsă — dacă o debifezi și situl nu are deja perioadele din fișier, importul se oprește cu eroarea «MissingEpochError») și **Importa anche i media citati (immagini, video, 3D, documenti)** (Importă și fișierele media citate — imagini, videoclipuri, 3D, documente). Dedesubt este câmpul **Cartella dei file** (Folderul fișierelor), opțional, cu butonul **Sfoglia…** (Răsfoiește…): servește atunci când em.json a fost copiat singur, departe de fișierele pe care le citează — indică folderul proiectului EMStudio (cel care conține `EM/`, `DosCo`, `proxies`, `RB`…).
4. Apasă **Anteprima** (Previzualizare): nu scrie nimic și spune câte fișe sunt noi, actualizate și neschimbate, câte perioade sunt noi și, într-o listă, câte fișe de ce tip, câte noduri ale fișierului nu devin fișe și câte unități au **proxy-ul 3D** (din 5.13.124-alpha; pentru TempluMare «65 unità su 112 hanno il loro proxy 3D.»: aceleași 65 pe care le arată EMStudio, care numără 114 unități pentru că include și cele 2 noduri de continuitate).
5. Apasă **Applica** (Aplică; se activează după previzualizare): importă și arată același rezumat, plus pe cel al fișierelor media.

Ce se întâmplă, pe scurt:

- **Ce devine fișă.** Doar unitățile al căror tip îl cunoaște pyArchInit (US, USM, USD, USVs, USVn, serUSVn, SF, VSF, RSF, USN, USNt…) și paradatele: proprietățile (`property`), extractorii (`Extractor`), combinatorii (`Combinar`) și documentele (`DOC`). Resursele, fișierele, modelele 3D, formele semantice, procesele geamănului digital, grupurile, epocile și narațiunea **nu** devin fișe: înainte de 5.13.121-alpha deveneau toate «US».
- **Numele (câmpul US).** Numele nodului fără prefixul tipului: USV105 → 105, D.05 → 05, D.05.02 → 05.02. Proprietățile care au același nume (de exemplu «height», care apare la multe unități) primesc între paranteze numele unității de care aparțin: «height (105)». Dacă două tipuri diferite ar da același număr — combinatorul «C.10» și documentul «D.10», US «SU002» și USD «USD002» —, tipul mai puternic (US, apoi celelalte unități, apoi documentele, extractorii, combinatorii) păstrează numărul, iar celălalt păstrează numele complet din EMStudio («C.10», «USD002»), ca relațiile să nu se încurce.
- **Relațiile.** Între două US/USM sunt cele obișnuite din pyArchInit («Copre» (acoperă), «Taglia» (taie)…), iar relația «vine după» (`is_after`: unitatea este mai recentă decât cealaltă) între două US se scrie «Copre». Între unități de tipuri diferite relațiile fizice se scriu pe larg («Taglia», «Si appoggia a» (se sprijină pe)), relația «vine după» cu `>` (`A > B`: A este mai recentă decât B), iar lanțul paradatelor — unitate → proprietate → extractor sau combinator → document, și descoperirea «parte din» o descoperire virtuală — cu `>>`. Perioadele, activitățile, grupurile și resursele nu sunt relații. La export, aceste semne redevin muchiile Extended Matrix (`is_after`, `has_property`, `has_data_provenance`, `extracted_from`, `combines`, `is_part_of`). Fiecare relație este scrisă pe **ambele** fișe, inversată pe a doua — «Copre»/«Coperto da» (acoperă/acoperit de), «Taglia»/«Tagliato da» (taie/tăiat de), `>`/`<`, `>>`/`<<` —, așa cum cere verificarea relațiilor din fișa US; o fișă fără relații are lista goală, nu câmpul gol. Înainte de 5.13.125-alpha verificarea dădea «malformed node or string: None» și «Rapporto reciproco non trovato» (relație reciprocă negăsită).
- **Activitate și descriere.** Activitatea nodului (grupul ActivityNodeGroup) merge în câmpul **Activitate** al fișei; descrierea nodului, în câmpul **Descriere**.
- **Periodizare.** Epocile din EMStudio, care au doar nume și date, se regăsesc după nume în periodizarea sitului; cele care nu există devin perioade noi, de la cea mai veche, numerotate după ultima perioadă a sitului, în faza 1, cu datele de început și de sfârșit și numele ca datare extinsă. Fiecare unitate preia perioada și faza inițiale de la epoca în care se naște, iar pe cele finale de la ultima epocă în care supraviețuiește (sau aceleași cu cele inițiale). Perioadele fără **codul perioadei** îl primesc în succesiune, 1, 2, 3…, în ordinea perioadei și a fazei; fiecare unitate preia **datarea** perioadei sale inițiale și **codul perioadei** așa cum îl scrie «Crea codice periodo» (Creați codul perioadei) — de exemplu 1/2/3 pentru o unitate care trăiește de la perioada 1 la 3 —, dacă nu le are deja (din 5.13.125-alpha).
- **Fișa sitului.** Dacă situl nu există, este creat. **Definiția** este bunul cultural despre care vorbește studiul, dacă em.json îl declară, altfel numele grafului (pentru TempluMare «Temple»); **națiunea, regiunea, provincia și comuna** provin din lanțul de locuri din em.json, atunci când există. Toate cele cinci ajung și în **tezaur** (fișa sitului, codurile 1.1–1.5), de unde fișa sitului le citește. Descrierea este luată din graf: nume, cod, autori și poziție (EPSG și origine). Dacă situl există deja, se completează doar ce este gol, iar definiția «Extended Matrix», scrisă de versiunile dinainte de 5.13.125-alpha, este înlocuită.
- **Fișiere media.** Urmând legăturile din em.json — fișă → resursă → fișier, fișă → model 3D → resursă → fișier, și url-ul documentului sau al extractorului —, fișierele citate devin fișiere media ale fișei. Ele se caută așa cum le caută EMStudio: în folderul em.json și în arborele proiectului său EM (`EM/`, `EM/DosCo`, `EM/proxies`, `RB`, `RM`, `SB`), plus folderul din câmpul **Cartella dei file**, dacă l-ai indicat. Contează imaginile, videoclipurile, modelele 3D (inclusiv **GLB** și **GLTF**) și documentele (**PDF, Word, Excel, ODT, ODS, RTF, CSV, TXT**). Fișierul media indică **fișierul original**, ca cele adăugate din fișă; miniatura și copia merg în folderele **Thumbnail path** și **Image resize** din configurare (tutorialul 01): modelele 3D au propria vizualizare, PDF-urile prima pagină, celelalte documente o pictogramă cu tipul. **Proxy-ul 3D** al unei unități — în graf se află pe proprietatea ei «geometry» — merge pe fișa unității. Dacă proprietatea este partajată de mai multe unități — o USV care moștenește geometria US pe care o completează — proxy-ul merge la unitatea care a creat-o, ca în EMStudio (înainte de 5.13.124-alpha mergea la prima unitate găsită în fișier). Rezumatul spune câte fișiere media sunt noi și de ce tip, câte erau deja prezente, câte miniaturi, câte fișiere citate nu au fost găsite (cu sfatul de a indica folderul proiectului), câte copii sunt goale (substituenți din cloud, de descărcat din nou), câte referințe externe (web, rețea, cloud) rămân adrese și care fișiere nu sunt media (`.blend`, `.mtl`, `.zip`…). Un fișier arhivat într-un bucket care are și o copie pe disc (în em.json, mai multe adrese pentru aceeași resursă) se importă din copia de pe disc; înainte de 5.13.124-alpha rămânea o referință externă. O a doua importare nu duplică nimic. Înainte de 5.13.122-alpha fișierele erau copiate în folderul principal al pyArchInit, GLB-urile nu aveau miniatură (iar fișa nu le arăta), proxy-urile se aflau pe proprietate în loc de unitate, iar PDF-urile rămâneau pe dinafară. Din 5.13.127-alpha vederile modelelor 3D se desenează toate împreună într-un proces Python separat, în afara QGIS: înainte, pe macOS, QGIS se închidea singur la închiderea rezumatului importului.
- **Reimportarea.** Importul aceluiași fișier încă o dată nu dublează nici perioadele, nici fișele: cele deja prezente apar ca «invariate» (neschimbate) sau «aggiornate» (actualizate), iar acolo unde baza de date și fișierul diferă, câștigă fișierul (rezumatul le numără drept «conflitti», conflicte). Previzualizarea numără ca «aggiornate» și fișele cărora importul le adaugă relații, datare sau codul perioadei (înainte apăreau ca «invariate»). Reimportarea em.json într-o bază de date importată înainte de 5.13.125-alpha o repară: definiția sitului, relațiile pe ambele fișe, datarea și codurile perioadei.
- **Fișierul em.json rămâne memorat.** pyArchInit păstrează în tabelele sale unitățile, paradatele, relațiile și epocile; tot restul grafului — resurse, fișiere, modele, forme semantice, procesele geamănului digital, grupuri de paradate și de activități, autori, licențe, narațiunea —, împreună cu titlul, **codul studiului** (de exemplu GT16: este prefixul cu care Blender reatașează proxy-urile), georeferențierea (EPSG și deplasări) și numele din EMStudio, este memorat la import (tabela `pyarchinit_em_sources`, un rând pe sit; ultimul import câștigă). La **exportul** em.json al sitului, toate acestea revin: numele originale (SU006, D.07.08, height…) pentru fișele care au încă numărul dat la import — o fișă redenumită în pyArchInit păstrează numele nou —, datele nodurilor (de exemplu proprietatea «geometry» cu forma ei, din care EMStudio numără proxy-urile) și nodurile care nu sunt fișe, cu muchiile lor, atașate la fișele care mai există: o ramură rămasă fără fișă (de exemplu forma unei proprietăți șterse) nu revine. Relațiile, perioadele și descrierile provin întotdeauna din baza de date. Mesajul de la sfârșitul exportului spune cât a revenit, de exemplu «Dall'em.json importato tornano 851 nomi, 1090 nodi e 1969 archi, codice dello studio GT16.» (Din em.json importat revin 851 de nume, 1090 de noduri și 1969 de muchii, codul studiului GT16). Testat pe TempluMare_v3.2 (1946 de noduri): niciun nume și nicio descriere diferite de original, iar în EMStudio 65 de unități din 114 cu proxy și 2 epoci din 3 cu un model, ca în original. Rămân diferite cele 9 «vine după» dintre două US, pe care pyArchInit le scrie «Copre», și grupurile de loc ale sitului și ale ariei cu studiul, pe care pyArchInit le adaugă.

Calea yEd/GraphML, pentru mutarea unităților între grupuri, este cea care urmează.

Pentru a modifica baza SQL mutând UE între grupuri în GraphML:

1. Deschide GraphML în **yEd**
2. Trage o UE într-un alt grup, salvează
3. Înapoi la dialog → tab **"Import"**
4. **Bifează** checkbox-ul *"Update SQL on import (struttura/area/...)"*
5. Încarcă GraphML modificat

Sistemul rulează o tranzacție atomică: la eșec, **rollback complet** (DB rămâne nealterată). Grupurile `adhoc` nu scriu niciodată SQL — actualizează doar `groups_<sit>.graphml`.

Începând cu 5.6.0-alpha walker-ul de import este **recursiv** și suportă foldere imbricate (de ex. lanț toponim `nazione > regione > provincia > comune > UE`). La detectarea ciclurilor în graful folderelor, este ridicată excepția `CycleDetectedError` și importul este abandonat cu rollback.

---

## 6. CLI (alternativă la dialog)

Pentru scripts / batch:

```bash
# Export
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Listează grupuri ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Adaugă autor
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes: 0 = succes, 1 = eroare bridge, 2 = eroare argparse.

---

## 7. Rezolvarea problemelor

| Simptom | Cauză | Soluție |
|---|---|---|
| "no such column: node_uuid" | Migrarea Phase 1 neexecutată | Repornește QGIS, redeschide DB |
| GraphML gol | DB fără rapporti / filtru area prea strict | Verifică us_table.rapporti |
| "rapporti trebuie să fie TEXT" | Ai introdus un număr ca integer | Câmpurile UE/Area sunt **TEXT**, nu integer |
| Capitalizare greșită în rapporti | "copre" cu litere mici în DB | Folosește "Copre", "Coperto da" capitalizate |
| `DeprecationWarning` pe fișier 5.5.x | Fișier legacy `ActivityNodeGroup + group_kind` | Projector-ul îl promovează în memorie la `LocationNodeGroup`. Reexportă pentru a migra fișierul pe disc. |
| Rândurile swimlane-ului afișează un text foarte lung | Versiunile anterioare foloseau Descrizione din periodizare ca etichetă | Actualizează plugin-ul și reexportă, și/sau completează **Datazione estesa** cu un nume scurt |
| Epocile din swimlane sunt în ordine greșită (ex. Bronz deasupra Antichității târzii) | Rândurile sunt ordonate după **Cronologia Inițială**; datele î.Hr. introduse ca numere pozitive (1650 în loc de -1650) sunt ordonate ca d.Hr. | În Fișa de Periodizare introdu anii î.Hr. ca numere negative și reexportă. Rezumatul exportului afișează acum un avertisment „⚠️ Periodizzazione: ..." cu lista perioadelor de corectat |

---

## 8. Documentație tehnică

Pentru aprofundare arhitectură, decizii de design și roadmap:

- Specs: `docs/superpowers/specs/2026-05-*-design.md`
- Plans: `docs/superpowers/plans/2026-05-*.md`
- Dev log: `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over amânate:
- **AI08-F3**: euristici auto-layout (bin-packing sub-grupuri) — încă amânat
- **AI09**: TimeBranchNodeGroup mapping — viitor
- **Phase 3**: SyncEngine + REST API — viitor
- **Phase 4**: GraphDBBackend + SPARQL — viitor

Livrate:
- **AI07** (5.6.0-alpha, 2026-05-10): migrare `LocationNodeGroup` cu enum `kind` + lanț toponim + apartenențe multidimensionale
- **AI08-F1** (fuzionat în AI07): nesting ierarhic nativ via `is_primary`

---

## 5. yEd-aware Import — importul de graphml editate extern (5.8.x)

Începând cu **5.8.0-alpha** bridge-ul este **bidirecțional și pentru graphml-uri create direct în yEd** (adică fără să treci mai întâi printr-un export pyarchinit). Pyarchinit recunoaște automat graphml-urile „yEd-raw" — cele care nu au data keys `pyarchinit.*` — și le importă printr-un dispatch dedicat care mapează prefixul label-ului nodului → tip stratigrafic, recunoaște rândurile de TableNode ca perioade, parcurge group folders ca dimensiuni arheologice și lasă utilizatorul să aleagă o politică pentru edges care ating folders.

### 5.1 Rollout în 6 etape

| Etapă | Tag | Ce adaugă |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` cu 13 valori (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate din rândurile de TableNode) + `yed_group_walker.py` (FolderCandidate cu auto-dimension din prefixul label-ului: VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orchestrator `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + sentinel `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` cu 5 pagini (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistență sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Această documentație + dev-log + CHANGELOG. |

### 5.2 Cum funcționează — flux utilizator

1. **Deschide un graphml în QGIS prin meniul Import GraphML** (același path ca fluxul pyarchinit-projected existent).
2. Pyarchinit detectează automat că este yEd-raw (fără keys `pyarchinit.*`) → face dispatch pe noul branch în loc să cadă pe path-ul legacy.
3. Se deschide wizard-ul `YedImportDialog` cu **5 pagini**:
   - **1/5 Classifier** — tabel cu un rând per leaf node. Fiecare rând arată `label` + `auto_kind` (de ex. `us_real` / `usv_virtual` / `property`) + un combobox de override `user_kind`. Butonul **Acceptă auto** resetează fiecare rând la `auto_kind` (șterge toate override-urile).
   - **2/5 Periods** — un rând per TableNode-row parsat, coloane editabile `periodo` + `fase`. Datele (`datazione_iniziale`/`finale`) rămân goale: graphml-urile yEd-raw nu poartă date.
   - **3/5 Folders** — un rând per group folder. Combobox de `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` pentru excludere). `value` editabil (default = `auto_value` derivat din prefixul label-ului).
   - **4/5 Rapporti policy** — 4 radio buttons pentru tratarea edges care ating folders:
     - **SKIP** (default): aruncă edges folder-touching. Edges leaf-to-leaf trec intacte.
     - **FAN_OUT**: o edge `folder_A → folder_B` se expandează la `N×M` perechi de leaves (produs cartezian al membrilor).
     - **REPRESENTATIVE**: folosește primul membru al fiecărui folder ca proxy.
     - **SYNTHETIC**: creează un rând us_table per folder (`unita_tipo='VA'` virtual activity) + reconectează edges prin aceste ancore.
   - **5/5 Preview** — dry-run al `import_yed_raw(overrides=..., dry_run=True)`. Afișează counts (us / inv / period / paradata) **fără commit**. Click pe **Finish** confirmă, **Cancel** abandonează.
4. La **Finish** wizard-ul salvează override-urile tale într-un **sidecar JSON** `<graphml>.yed_overrides.json` lângă fișier. Redeschiderea aceluiași graphml preîncarcă sidecar-ul, deci override-urile anterioare revin preaplicate.

### 5.3 Rutarea destinațiilor

Dispatch-ul folosește `_classify_destination` (în `yed_import_pipeline.py`) pentru a clasifica fiecare leaf:

| ClassificationKind | Destinație | Notă |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | din label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | din `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | din `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | din `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` derivat din prefixul label-ului: USVs/USVn/USVc) | din `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | din `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | din `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | din `^VSF\d+` |
| DOCUMENT | `paradata` | din `^D\.\d+` |
| COMBINER | `paradata` | din `^C\.\d+` |
| PROPERTY | `paradata` | cuvânt-cheie în label (`material`/`position`/`width`/...) |

**Decizie utilizator 2026-05-13**: USV* (virtuale) sunt „unità tipo" (rămân unități stratigrafice) și aparțin în `us_table`, nu în paradata. Doar DOC/COMB/PROP/VIRTUAL_FIND rămân în paradata.

### 5.4 Sidecar JSON — schemă

Versionat pentru forward-compat:

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

Se persistă doar câmpurile MODIFICATE de utilizator (diff). Valorile `ClassificationKind` necunoscute (de ex. din release-uri viitoare s3dgraphy) sunt skip-uite tăcut la încărcare.

### 5.5 CLI pentru ingest scripted

Pentru CI / re-runs în batch:

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` pentru backend SQLite vs PostgreSQL. `--overrides` este opțional (fără overrides = defaults yE-D). `--auto-defaults` este un flag no-op forward-compat.

### 5.6 Limite cunoscute

- **Fără editare de date în wizard**: graphml-urile yEd-raw nu poartă `datazione_iniziale`/`datazione_finale`. Pagina Periods editează doar `periodo` + `fase` (targets FK).
- **API ParadataStore parțial**: upstream s3dgraphy încă nu furnizează `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D loghează „skip — method missing" pentru fiecare leaf paradata dar numără încercările în preview.
- **PropertyNode → Path B (fără legătură US)**: nodurile PROPERTY se scriu fără US target. Wizard-ul emite un warning. Viitor: follow-up yE-Closure pentru a adăuga „assign target" în UI.
- **Multi-DB**: sidecar-ul JSON este per graphml, nu per DB. Dacă imporți același graphml în DB-uri diferite, se reutilizează aceleași overrides pentru toate.

### 5.7 Acoperire teste finală

| Suite | Test | Acoperire |
|---|---|---|
| yE-A | `test_yed_detector.py` | detectare flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | politici + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistență sidecar + CLI |

**Suite totală post-rollout**: 354 passed / 42 skipped (PG-L1 necesită psycopg2).

### 5.8 Actualizare 5.8.5-alpha (yed-fastfix)

Pachet de corecții comportamentale peste `5.8.3-alpha` care îmbunătățește calitatea re-exportului GraphML după un import yEd-aware. Modificări relevante pentru utilizatorul final:

- **Paradata multi-folder**: label-urile DOC / Combinar / Extractor / property partajate între mai multe foldere yEd (de ex. `material` referențiat din VA01 + VA04 + VA05) generează acum UN rând în `us_table` PER apariție — vizibilitate multi-folder restabilită în GraphML-ul re-exportat. Compromis: dedup-ul după identitate (colapsarea `D.01` / `D.01-2` / `D.01bis` într-un singur rând) nu se mai aplică pentru a doua/a treia apariție.
- **Rapporti reciproce**: fiecare edge yEd `a → b` scrie rapporto-ul direct pe rândul lui `a` ȘI inversul pe rândul lui `b` (`<<` / „Coperto da" / etc.). DOC-urile arată acum toate conexiunile extractor de intrare în formularul Scheda US.
- **Strip al prefixului `us` numeric**: `US100` → `us='100'` `unita_tipo='US'` (înainte `us='US100'`). SF/VSF/RSF se scriu dual în `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fază**: apartenența unui rând TableNode yEd la o perioadă se propagă către `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware**: `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — păstrează distincția semantică EM 1.5.
- **Re-import idempotent**: re-rularea aceluiași import sare peste rândurile deja prezente; fără rollback pentru coliziune UNIQUE la pasul repetat.
- **Paletă USV**: nodurile USV se randează acum cu paralelogramul albastru canonic EM (înainte dreptunghi cu bordură roșie).

### 5.9 yE-F paradata multi-folder (5.9.0-alpha)

Evoluție structurală a `yed-fastfix-5.8.5-alpha`: compromisul Bug R B1 (un rând `us_table` per apariție, cu `us='D.01_2'` / `us='D.01_3'`) a fost depășit. O frunză paradata (DOC / Combinar / Extractor / property) partajată între mai multe foldere yEd produce acum **un singur rând** în `us_table` per label canonic, iar apartenența multiplă este păstrată într-o nouă coloană `other_locations`.

Modificări vizibile pentru utilizatorul final:

1. **Widget nou „Alte activități" în fișa US/USM**: în tab-ul *Periodizzazione* apare un `QListWidget` etichetat „Alte activități" — vizibil **doar** când `unita_tipo` este o tipologie paradata (`DOC`, `Combinar`, `Extractor`, `property`). Utilizatorul poate selecta mai multe coduri de activitate; selecția este serializată ca listă JSON în noua coloană `other_locations`.
2. **Element de meniu QGIS nou**: `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Trebuie executat **o singură dată** pe fiecare DB preexistentă pentru a adăuga noua coloană (DB-urile create post-5.9 au deja coloana).
3. **Import yEd-aware îmbunătățit**: o frunză paradata care apare în N foldere yEd generează acum **doar 1** rând `us_table` (nu N rânduri cu sufix `_2`/`_3` ca în 5.8.5). Primul folder întâlnit devine `attivita` principală; folderele secundare sunt listate în `other_locations`. La **export** se emit N copii vizuale yEd (una per folder), toate împărtășind același `node_uuid` canonic pentru a garanta identitatea round-trip.

**Compatibilitate înapoi**: datele produse de Bug R B1 în 5.8.5-alpha (rânduri cu sufix `_2`/`_3`) rămân lizibile fără nicio conversie automată. Logica nouă se aplică noilor importuri; rândurile legacy continuă să se comporte ca înainte.

Predecesor: vezi secțiunea 5.8 (`yed-fastfix-5.8.5-alpha`) pentru comportamentul înlocuit.

---

## 6. Generare continuitate (fișe CON)

În panoul **„Verifica rapporti"** — disponibil ca tab în interiorul dialogului de import/export s3dgraphy — există butonul **„Genera continuità"** (etichetă păstrată în italiană ca în plugin). Pentru situl selectat curent, această funcție creează automat **fișele de continuitate** ale US/USM a căror viață se întinde pe mai mult de o perioadă.

### 6.1 Ce face

1. Scanează toate US/USM din sit la care **perioada inițială ≠ perioada finală** (adică a căror viață se întinde pe mai multe perioade).
2. Pentru fiecare creează sau actualizează o fișă de continuitate denumită **`CON_<us>`** (de ex. `US5` → `CON_US5`).
3. Fișa CON **moștenește** de la unitatea-mamă: situl, aria (plus ariile secundare), structura și întregul interval de perioade (inițială → finală). Descrierea ei este generată automat.
4. Scrie o **relație de continuitate reciprocă** pe ambele părți: pe CON și pe unitatea-mamă.

> **Faza, de la sine, nu conteaza.** Regula se uita la **perioada**: o USM care merge de la **2/3 la 2/4** — aceeasi perioada, se schimba doar faza — nu genereaza nimic. Daca unitatile tale supravietuiesc din faza in faza in interiorul aceleiasi perioade, bifeaza **„anche i salti di fase"** („si salturile de faza") langa buton: atunci conteaza si acele salturi, cu conditia ca **ambele** faze sa fie completate. O unitate care nu se misca — aceeasi perioada si aceeasi faza — nu este niciodata o continuitate. Caseta porneste **nebifata** si este valabila pentru previzualizare si pentru scriere deopotriva.

### 6.2 Idempotență

Operația este **idempotentă**: rularea repetată nu duplică fișele existente — actualizează `CON_<us>` existente dacă datele unității-mamă s-au schimbat.

### 6.3 Previzualizare (dry-run) și backup

Înainte de scriere se afișează o **previzualizare dry-run** cu numărătorile: câte fișe trebuie **create**, **actualizate**, **neschimbate** și câte **orfane**. Modificările se aplică **doar după confirmare** (butonul „Genera"). La aplicare se face mai întâi un **backup al bazei de date** automat.

O fișă CON este **orfană** atunci când unitatea ei mamă nu se mai întinde pe mai multe perioade (de ex. perioada inițială și cea finală au fost făcute egale). În mod implicit orfanele sunt doar **semnalate**; o **casetă de bifare** („Rimuovi anche le CON orfane") permite optarea pentru eliminarea lor.

**O continuitate scrisa de mana este recunoscuta.** O fisa CON ale carei relatii numesc o singura unitate — `> 12`, sau „Continuitate dupa 12” — este continuitatea acelei unitati, oricum s-ar numi: generatorul o **actualizeaza** (intervalul de perioade, eticheta canonica) iar numele ramane al ei. Nu se naste o a doua: continuitatea este **una pe unitate**. Daca exista si o `CON_<us>` canonica, castiga aceea, iar cealalta ramane orfana, de decis de mana.

### 6.4 În exportul Extended Matrix

Fișele `CON_<us>` generate astfel apar în **em.json** al Extended Matrix ca **elemente de continuitate** (exportul GraphML este pensionat, §2.3).

---

## 7. Verificarea paradoxurilor temporale (stratigrafice)

În panoul **"Verifica rapporti"** (Verificarea relațiilor — o filă din dialogul de import/export s3dgraphy), verificarea semnalează acum și **paradoxurile temporale**: când perioada/faza atribuită unei unități contrazice stratigrafia observată. Stratigrafia este data de referință, prin urmare corecțiile automate mută **perioadele**, nu relațiile.

### 7.1 Ce detectează
- **Inversiune temporală**: două unități datate legate printr-o relație de ordine (de ex. US5 «acoperă» US7) în care unitatea mai recentă din stratigrafie se dovedește a fi în întregime mai **veche** ca perioadă.
- **Contemporaneitate incoerentă**: unități declarate contemporane (egalitate fizică / legătură) dar cu intervale cronologice **disjuncte**.
- **Neevaluabil**: relație de ordine în care cel puțin una dintre cele două unități nu are o perioadă databilă (doar semnalat, fără corecție).

Notă privind limita: două perioade **adiacente care se ating** într-un singur punct cronologic sunt considerate suprapuse → **nu** constituie un paradox (prezumția de bună-credință).

### 7.2 Corecție automată și sugestii
- Când o singură mutare rezolvă conflictul, verificarea propune mutarea unității **mono-perioadă** aflate în conflict cu majoritatea vecinilor săi, alegând perioada cu mutarea minimă; pentru contemporaneitățile cu o unitate nedatabilă copiază perioada vecinului datat.
- În cazurile ambigue — egalitate, unități **multi-perioadă** (de ex. fișe CON), nicio perioadă validă — nu corectează automat: oferă o **sugestie «ce + cum»** (de ex. «Mută US5 la o perioadă ≥ 3, sau US7 la o perioadă ≤ 1, sau verifică relația»).

### 7.3 Previzualizare și backup
- **Previzualizarea** arată modificările de perioadă propuse înainte de a le aplica.
- Înainte de scrierea perioadelor se efectuează un **backup automat al bazei de date** (SQLite și PostgreSQL).
- După aplicare, relansează verificarea pentru a controla eventualele paradoxuri reziduale.

---

## 8. Verificarea cronologiei (periodizare și fișe)

În același panou **"Verifica rapporti"** (Verificarea relațiilor — o filă din dialogul de import/export s3dgraphy), începând cu versiunea 5.13.64-alpha verificarea găsește și corectează și probleme de **cronologie** ale sitului selectat. Verificarea paradoxurilor temporale (secțiunea 7) compară perioada unei unități cu stratigrafia; aceasta compară periodizarea cu ea însăși și cu fișele US care o copiază.

### 8.1 Ce detectează

Panoul grupează problemele pe tipuri. Alături de grupurile relațiilor apar patru grupuri noi:

| Grup | Ce semnalează | Cum este tratat |
|------|---------------|-----------------|
| **Faze cu intervale suprapuse** | Două rânduri ale periodizării ale căror intervale de ani se intersectează | Manual: panoul propune îngustarea intervalelor doar dacă, după îngustare, rămâne un interval utilizabil |
| **Datare a fișei dezaliniată** | Câmpul `datazione` al fișei US spune altceva decât `datazione_estesa` a perioadei/fazei sale | Automat: periodizarea este sursa, iar fișa este copia, deci copia este rescrisă din sursă. Un câmp gol se completează la fel. O US fără perioadă este sărită, pentru că nu există nimic de copiat |
| **Periodizare cu începutul după sfârșit** | `cron_iniziale` mai mare decât `cron_finale` | Manual: sunt probabil date î.Hr. fără semnul minus — panoul propune rescrierea celor doi ani ca numere negative (`-1650` în loc de `1650`); dacă este însă o greșeală de tastare, inversează manual cele două valori |
| **Fază fără ani** | O fază ai cărei ani lipsesc sau nu pot fi citiți | Doar semnalată: nu există nimic de la care să îi moștenească |

Un exemplu pentru suprapuneri. Baza de date de exemplu are două și niciuna nu are propunere: cele două faze au intervale **identice**, iar orice îngustare ar face ca o fază să se termine înainte de a începe. Panoul doar o spune; decizia (unirea fazelor, corectarea anilor, lăsarea așa cum este) aparține arheologului.

### 8.2 Corecție automată și sugestii

**Corecții automate și propuneri.** Corecțiile automate sunt **deja bifate**; propunerile **nu**, și sunt aplicate doar dacă se bifează caseta. Înainte regula era alta: o problemă a cărei corecție cerea o decizie umană putea fi doar citită. Acum are o casetă, lăsată nebifată. Acest lucru este valabil și pentru cele două categorii mai vechi de relații care oferă o sugestie, adică contradicția directă și ciclul stratigrafic.

Pentru a folosi panoul:

1. Selectați în panou **situl** de verificat. Verificarea este **pe sit**: se uită doar la situl ales și corectează doar acel sit. Într-o bază de date cu zece situri acest lucru contează, pentru că aceleași numere de US există în toate.
2. Citiți **linia de rezumat** de deasupra arborelui: spune câte probleme sunt, câte pot fi corectate automat și **câte sunt propunerile de bifat manual**.
3. Deschideți grupurile și selectați o problemă pentru a-i citi detaliul în panoul de previzualizare.
4. Verificați casetele. Corecțiile automate sunt deja bifate: debifați-le pe cele pe care nu doriți să le aplicați. Bifați propunerile cu care sunteți de acord.
5. Aplicați corecțiile. Înainte de a scrie orice se creează o **copie de siguranță automată** (copie a fișierului SQLite sau `pg_dump` pentru PostgreSQL în `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`); copia, care exista deja pentru corecțiile câmpurilor de perioadă, acoperă acum și corecțiile cronologice.
6. Dacă rezultatul nu convinge, apăsați **Annulla ultimo fix** (anulează ultima corecție): anularea readuce și corecțiile scrise în tabela periodizării.

### 8.3 Previzualizare și backup

**Previzualizarea arată data calculată.** Pentru fiecare unitate citată de o problemă, panoul de previzualizare arată data ei calculată într-o linie ca aceasta:

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

Linia indică, în ordine, intervalul de ani, regula care l-a produs și relația de-a lungul căreia a călătorit constrângerea, împreună cu nodul de la care provine. Când cele două capete ale intervalului vin pe drumuri diferite, fiecare capăt are eticheta lui (`inizio …` și `fine …`), astfel încât o dată nu este niciodată atribuită relației greșite. Astăzi, într-o bază de date normală, fiecare unitate își ia datele din propria perioadă, deci majoritatea liniilor vor spune `epoca`. Rostul liniei nu este să surprindă, ci să lase să se vadă **de unde vine** o dată.

---

## 9. Cum se citesc arcele matricei

Unele alegeri din desenul matricei pot parea ciudate, dar nu sunt erori:

- **O sageata nu trece niciodata pe sub un nod.** Cand coloana de sosire este ocupata, sageata intra in casuta **din lateral**: este normal.
- **Egalitatea nu este o suprapunere.** O relatie «Uguale a» (Egal cu) sau «Si lega a» (Se leaga de) pune cele doua unitati pe **acelasi rand**, alaturate, unite prin **doua linii orizontale** (semnul egal) **fara varf de sageata**.
- **Arcele redundante nu se deseneaza.** Daca US 1 acopera US 2 si US 2 acopera US 3, sageata de la 1 la 3 nu apare, pentru ca nu adauga nimic. In interiorul unui **ciclu**, in schimb, toate arcele raman, pentru ca un ciclu este o eroare care trebuie vazuta.
- **Liniile spun ce relatie sunt.** Gri si continua: secventa (acopera, umple, se sprijina). **Punctata verde**: o taietura (`Taglia` / `Tagliato da`), oricare ar fi definitia stratigrafica si in orice limba. **Groasa si neagra**: continuitatea — un romb mic si negru fara nume (numele apare la trecerea mouse-ului), in coloana unitatii sale, asa ca linia e dreapta. **Rosie**: o sageata care urca prin benzi, adica o contradictie intre stratigrafie si cronologie; o taietura care urca e rosie **si** ramane punctata.
- **Paradatele nu sunt niciodata o linie continua.** Iau culoarea si trasatura din regulile Extended Matrix (`em_visual_rules.json`): brun-rosu punctat „extras din", portocaliu intrerupt „provenienta datei", auriu intrerupt „proprietate", gri intrerupt „conexiune generica", rosu-tomata intrerupt „combina" (in fisier ar fi continua: e singura abatere, pentru ca un arc catre un document nu trebuie sa para o suprapunere).
- **Paradatele stau sub unitatea lor.** Proprietatile, extractorii, combinatorii si documentele unei unitati sunt in **grupul** ei, cadrul punctat de sub caseta ei, ca grupurile de paradate din EMStudio: un rand pentru fiecare pas al lantului (proprietatile, apoi extractorii si combinatorii, apoi documentele), si nu conteaza in nivelurile stratigrafice. Un document folosit de mai multe unitati apare in grupul fiecareia, ca in EMStudio, iar liniile paradatelor raman in interiorul grupului. Paradatele pe care nicio unitate nu le atinge au o banda proprie in partea de jos („Paradati senza unità”). Antetul panoului le numara separat: „114 unità · 739 paradati · 3 epoche · 90 rapporti” pentru TempluMare (din 5.13.126-alpha; inainte paradatele intrau in niveluri ca unitati, iar matricea unui sit ca TempluMare devenea un ghem).
- **Marginea bruna este o zidarie.** USM — WSU, MSE, UEM, USZ, ΤΣΜ in celelalte limbi — au aceeasi caseta ca US, cu margine bruna in loc de rosie.

---

## 10. Narațiune cu AI

Începând cu versiunea **5.13.106-alpha**, panoul matricei din QGIS (§2.2, „Vedi la matrice”) are două file în coloana din dreapta: **Units** (*Unità*) — detaliile unității alese, zoomul pe geometrie și fișierele media, ca până acum — și **Narrative** (*Narrativa*), cea nouă. Fila Narrative pune un AI să scrie **povestea sitului**, câte un capitol pentru fiecare epocă, apoi o poți citi, o poate valida o persoană și o poți exporta în HTML, DOCX sau PDF. Citește și scrie **același em.json** pe care îl deschide EMStudio, în formatul bibliotecii s3dgraphy: narațiunea pe care o vezi aici este cea pe care EMStudio o arată în fila sa *Narrative*.

> **Nicio setare nouă.** Fila nu are o fereastră de configurare proprie: folosește AI-ul pe care l-ai configurat deja în altă parte din pyArchInit (§10.2).

> **AI-ul scrie ciorne, nu texte definitive.** Fiecare paragraf scris de model rămâne „AI draft” (ciornă AI) până când o persoană îl validează (§10.6), iar în documentele exportate poartă semnul ⚠.

Numele filelor și ale butoanelor din fila Narrative există în italiană și în engleză: **sunt în italiană dacă QGIS este în italiană, în engleză cu orice altă limbă**. Aici le găsești întotdeauna pe amândouă. Intrările de meniu și ferestrele de dialog ale pluginului (precum „Vedi la matrice…” sau cele trei butoane din §10.9) sunt, în schimb, doar în italiană; traducerea în română este dată între paranteze.

### 10.1 Deschiderea filei Narrative

1. Deschide meniul **Plugins → pyArchInit - Archaeological GIS Tools** și alege intrarea **Extended Matrix → Vedi la matrice…** (Vezi matricea).
2. Alege **situl**.
3. pyArchInit exportă situl din baza de date în `<home>/pyarchinit_EM_folder/<sit>.em.json` — `<home>` este `~/pyarchinit_5`, sau folderul indicat de variabila de mediu `PYARCHINIT_HOME` — și deschide panoul **„Matrice — `<sit>`”**, ancorat în dreapta ferestrei QGIS. Numele fișierului este numele sitului, cu caracterele speciale înlocuite cu „_” (de exemplu „Scavo 1” devine `Scavo_1.em.json`).
4. În coloana din dreapta a panoului, apasă fila **Narrative**.

<!-- IMMAGINE: Captură de ecran a meniului Plugins → pyArchInit - Archaeological GIS Tools cu intrarea „Extended Matrix → Vedi la matrice…” -->
![Meniul Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figura 1: Intrarea „Extended Matrix → Vedi la matrice…” în meniul pluginului*

<!-- IMMAGINE: Captură de ecran a panoului matricei ancorat în dreapta, cu filele Units și Narrative -->
![Panou cu două file](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figura 2: Panoul matricei cu filele Units și Narrative*

Fișierul este **unul pentru fiecare sit și rămâne pe disc**: nu se mai află într-un folder temporar. Este fișierul pe care îl deschide EMStudio și în el se scrie narațiunea. De fiecare dată când alegi „Vedi la matrice…”, situl este **exportat din nou din baza de date** și fișierul este rescris; narațiunea deja prezentă în el se păstrează (§10.8).

La filă se ajunge și din alte două locuri:

- din intrarea **Extended Matrix → Esporta sito in em.json…** (Exportă situl în em.json), care la final oferă butonul „Narrativa con l'AI” (§10.9);
- din butonul **Vedi la matrice** al ferestrei „Esporta Extended Matrix” din fișa US (§2.2): deschide același panou pe fișierul pe care tocmai l-ai exportat, în folderul pe care l-ai ales.

### 10.2 Ce AI este folosit

În partea de sus a filei Narrative, o linie spune ce AI va folosi: **„Model: `<model>` (`<where it comes from>`)”**, urmată de reamintirea despre EMStudio. Dacă nu găsește niciunul, scrie **„No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”.”** (niciun AI configurat: configurează-l în fișa US cu butonul „Report” (Provider AI) sau cu „Query AI Database”), iar butoanele **Generate with AI** și **Regenerate chapter** rămân dezactivate.

Fila citește setările AI **deja salvate** de celelalte ferestre ale pyArchInit, în această ordine, și o folosește pe **prima** care are un model și — pentru furnizorii online — cheia API:

| # | Unde se setează | Cum o numește fila (en / it) |
|---|-----------------|------------------------------|
| 1 | Fișa US, butonul „Report” → fereastra „Generatore di Report” (Generator de rapoarte), grupul „Provider AI” | Report generator of the US form / Generatore di Report della scheda US |
| 2 | Fișa US, butonul „Query AI Database” | Query AI Database / Query AI Database |
| 3 | Fereastra palimpsestr, butonul „Report AI (analisi descrittiva)…”, selectorul „Provider AI” | Palimpsest report / Relazione Palimpsest |
| 4 | Fereastra „Generazione SQL con AI” (text în SQL: vezi tutorialul 30) | Text to SQL / Testo in SQL |

Furnizorii sunt cei din selectoarele „Provider AI”: **OpenAI** și **Anthropic (Claude)** online, cu cheia API scrisă în câmpul „API key”; **Ollama** și **LM Studio** pe computerul tău, fără cheie. Selectorul salvează alegerea de îndată ce o schimbi. Dacă vrei alt model, schimbă-l în fereastra pe care fila o indică între paranteze (sau într-una care vine mai devreme în listă). Fila recitește setările **când se deschide panoul**: după ce le-ai schimbat, deschide din nou matricea.

### 10.3 Fila Narrative

```
┌─ Units ─┬─ Narrative ───────────────────────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the                        │
│ file open, close it first: the last writer wins.                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                                        │
│ Early 15th century — AI draft                                                       │
│ 15th century — endorsed                                                             │
│ Modern age — AI draft, truncated                                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                                    │
│ Language of the prose: [English ▾]                                                  │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]                                │
│ [Prepare the chapters]  [Show on the map]  [Export…]  [Open in EMStudio]  [Cancel]* │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

\* Linia de progres și butonul „Cancel” se văd doar cât timp AI-ul scrie. În această schemă, rândurile listei sunt cele ale sitului de exemplu.

<!-- IMMAGINE: Captură de ecran a filei Narrative, cu lista capitolelor, textul capitolului ales și cele șapte butoane -->
![Fila Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figura 3: Fila Narrative*

De sus în jos:

- **linia de stare**: modelul folosit (§10.2) și reamintirea *„If EMStudio has the file open, close it first: the last writer wins.”* (dacă EMStudio are fișierul deschis, închide-l mai întâi: cine scrie ultimul câștigă);
- **lista capitolelor**, un rând pentru fiecare capitol: *Titlu — stare*. Un fișier dintr-o versiune anterioară, împărțit pe sondaje, arată toate grafurile: fiecare rând este precedat de numele grafului între paranteze drepte, de exemplu `[Saggio A] 15th century — AI draft`;
- **textul capitolului ales**: textul narativ, cu unitățile citate pe nume — numele sunt **linkuri**: un clic arată unitatea pe hartă (§10.10); sub paragraful în care o unitate este numită prima dată apar până la două fotografii ale ei (§10.11). Dacă capitolul nu are încă text, vezi substituentul său „[to be written: …]”;
- **linia de progres**, doar în timpul generării: „Chapter 3 of 9 · 15th century”;
- **limba textului** (începând cu 5.13.128-alpha): limba în care AI-ul scrie capitolele și în care se nasc titlurile capitolelor noi (§10.4, „Limba”);
- **butoanele**, pe două rânduri.

Rezultatul fiecărei operații apare în bara de mesaje a QGIS, cu titlul „Narrative”.

Când fișierul **nu are încă o narațiune**, lista este goală și un text spune: *„No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it.”* (nicio narațiune în fișier: „Prepare the chapters” creează scheletul, cu N capitole între epoci și activități, iar „Generate with AI” îl scrie).

#### Stările unui capitol

| Stare (en / it) | Ce înseamnă |
|-----------------|-------------|
| **to be written** / da scrivere | Capitolul conține doar substituentul „[to be written: …]”. |
| **AI draft** / bozza AI | Există text scris de model pe care nicio persoană nu l-a validat. Este suficient un paragraf: dacă un capitol are chiar și un singur paragraf nevalidat, aceasta este starea lui, chiar dacă există și alt text. |
| **endorsed** / convalidato | Tot textul scris de AI a fost validat de o persoană. |
| **written** / scritto | Text scris de o persoană (în EMStudio). |
| **truncated** / troncato | Se adaugă la stare (de exemplu „AI draft, truncated”): modelul s-a oprit pentru că a atins limita de lungime, iar textul se termină la jumătate. |

#### Butoanele

| Buton (en) | În italiană | Ce face |
|------------|-------------|---------|
| **Generate with AI** | Genera con l'AI | Scrie, **pe rând**, toate capitolele încă „to be written” — mai întâi **Presentation**, apoi cele de epocă (și de activitate); cele deja scrise nu sunt atinse. Dacă narațiunea nu există încă, creează mai întâi scheletul. Arată progresul și butonul **Cancel**. Activ doar cu un fișier deschis și un AI configurat. Dacă fișierul aduce o narațiune proprie — de exemplu cea din TempluMare, scrisă în EMStudio — nu adaugă capitole: scrie doar capitolele lui pyArchInit care sunt încă „to be written”, dacă le-ai adăugat cu „Prepare the chapters” (până la 5.13.127-alpha le adăuga singur). |
| **Regenerate chapter** | Rigenera capitolo | Rescrie **capitolul ales** în listă: ciorna AI nevalidată este înlocuită — dar numai după ce modelul a răspuns: dacă apelul eșuează, ciorna de dinainte rămâne — iar blocurile deja validate rămân. Se activează când alegi Presentation sau un capitol de epocă sau de activitate și un AI este configurat; pentru „Where it is” rămâne dezactivat. Presentation este capitolul lui pyArchInit: primul capitol al narațiunii unui fișier (introducerea din TempluMare) nu este acesta și nu se regenerează. |
| **Endorse…** | Convalida… | Deschide un meniu cu „This chapter” și „All chapters”, apoi întreabă cine validează (§10.6). Activ când există o narațiune. |
| **Prepare the chapters** | Prepara i capitoli | Creează **doar scheletul** capitolelor, fără AI: funcționează chiar dacă nu este configurat niciun AI, ca să poți scrie manual în EMStudio. Nu atinge textul deja scris și adaugă capitolele epocilor noi. Rezultat: „Chapters prepared: N.” (Capitole pregătite: N.) Dacă fișierul aduce o narațiune proprie, întreabă mai întâi: **Only the file's chapters** (nu se adaugă nimic: „The file's N chapters stay as they are: no chapter added.”), **Add pyArchInit's** (Presentation, „Where it is”, câte un capitol pentru fiecare epocă și fiecare activitate care nu are unul, după capitolele fișierului, care rămân neatinse) sau **Cancel**. Întreabă de fiecare dată, până când le adaugi. Titlurile capitolelor noi sunt în **limba textului**. |
| **Show on the map** | Mostra sulla mappa | Selectează și încadrează pe hartă, **toate împreună**, unitățile despre care vorbește capitolul ales (§10.10): cele citate în text sau, dacă capitolul nu este încă scris, toate cele din banda lui. Activ doar dacă cel puțin una dintre unitățile despre care vorbește capitolul ales este un rând al fișei US. |
| **Export…** | Esporta… | Salvează narațiunea în HTML (cu harta interactivă a sitului, §10.7), DOCX sau PDF de tipărit (§10.7), cu fotografiile unităților citate, când există (§10.11). Activ când există o narațiune. |
| **Open in EMStudio** | Apri in EMStudio | Deschide em.json în EMStudio. Dacă EMStudio nu este instalat, bara de mesaje trimite la intrarea de meniu **Extended Matrix → Installa EMStudio…** (Instalează EMStudio). |
| **Cancel** | Annulla | Apare doar în timpul generării: AI-ul se oprește **după capitolul în curs**, iar ce s-a scris este salvat. |

În timpul generării, toate butoanele sunt dezactivate, în afară de **Cancel**.

### 10.4 Ce scrie AI-ul

**Ce capitole.** Scheletul este cel al bibliotecii s3dgraphy (șablonul „site_story”):

- Începând cu **5.13.110-alpha**, **Presentation** (Prezentare) este un capitol canonic pe care AI-ul îl scrie ca pe celelalte, dintr-un briefing al sitului întreg (vezi „Briefingul pentru Presentation” mai jos); înainte rămânea un substituent. **Where it is** (Unde se află) este celălalt capitol canonic și rămâne un substituent „[to be written: …]”, de scris manual în EMStudio: se naște din poziția sitului, iar harta o pune biblioteca. Există doar dacă graful poartă o poziție geografică. AI-ul nu îl generează.
- **Un capitol pentru fiecare epocă** (perioadă/fază) care are unități, de la cea mai veche la cea mai recentă. Titlul este numele epocii, adică „Datazione estesa” (datare extinsă) din periodizare; dacă lipsește, rezultă un nume generic, de exemplu „Period 8 Phase 1”: completeaz-o în Fișa de Periodizare pentru a avea titluri ușor de citit. O unitate apare în capitolul epocii în care se naște și în cele ale epocilor în care supraviețuiește.
- **Un capitol pentru fiecare activitate**, dacă graful conține grupuri de activități. Un sit exportat din baza de date, în mod normal, nu are niciunul — câmpul Activity (activitate) din fișa US călătorește ca proprietate a unității — și atunci capitolele sunt cele de epocă.

**Narațiunea fișierului.** Un fișier em.json din EMStudio poate sosi cu o narațiune proprie: TempluMare aduce 13 capitole de Emanuel Demetrescu, în engleză, scrise de el însuși. pyArchInit o păstrează așa cum este: capitolele ei nu sunt atinse, iar cele din șablonul „site_story” se adaugă doar cu **Prepare the chapters** → **Add pyArchInit's** (până la 5.13.127-alpha le adăugau și „Generate with AI”, și fiecare export al sitului). Un capitol al fișierului ancorat la o activitate contează drept capitolul acelei activități: în TempluMare, „Virtual Activity 2: colonnade” este ancorat la activitatea VAct.03, iar „Virtual Activity 4: Temple” la VAct.01, astfel că VAct.02 și VAct.04 rămân fără capitol și pyArchInit adaugă câte unul pentru fiecare („VAct.02 Columnade”, „VAct.04 Temple”): ancorele fișierului sunt cele care trebuie corectate.

**Ce primește modelul.** Pentru fiecare capitol de epocă sau de activitate, un *briefing* cu, pentru fiecare unitate: nume, tip și descriere; câmpurile completate ale fișei US (definiția stratigrafică și interpretativă, interpretarea, perioada și faza, datarea, activitatea, structura, sondajul, încăperea, sectorul, aria); epocile; **relațiile stratigrafice** cu celelalte unități (acoperă, taie, umple, se sprijină pe, egal cu…), cu numele lor; și, dacă există, sursele documentare legate. Unitățile sunt listate **de la cea mai veche la cea mai recentă**, urmând relațiile. Peste **80 de unități** pe capitol, briefingul este limitat la primele 80. Are și o limită de lungime (aproximativ 25.000 de caractere): peste aceasta, textele lungi ale fișelor sunt scurtate, relațiile repetate și lanțurile de dovezi sunt eliminate și, dacă nici asta nu ajunge, unitățile cele mai recente sunt omise. În ambele cazuri modelul este informat câte unități lipsesc.

**Regulile.** Modelul primește cele cinci reguli ale bibliotecii: să scrie doar ceea ce susține contextul (fără date, materiale, funcții sau evenimente inventate); să păstreze incertitudinea (o unitate virtuală este o ipoteză, nu un fapt); să nu citeze surse care nu sunt prezente; să scrie text continuu, fără liste sau titluri; să spună deschis când contextul este prea sărac. I se cer de la unul la trei paragrafe.

**Briefingul pentru Presentation.** Presentation nu are unități proprii: modelul primește un briefing al **sitului întreg**, luat din graf și nu din baza de date, cu numele sitului; lanțul toponimelor (țară → regiune → provincie → comună); locurile din fișa US (arii, sectoare, sondaje, încăperi); epocile de la cea mai veche la cea mai recentă, fiecare cu câte unități sunt prezente în ea (aceeași unitate poate fi în mai multe epoci, deci suma poate depăși totalul); câte unități sunt și de ce tip, și câte relații stratigrafice; documentele; persoanele numite în fișele US; și titlurile capitolelor poveștii. Instrucțiunile sunt cele pentru Presentation, nu cele cinci reguli de mai sus: cer de la două la patru paragrafe care să spună ce este situl și unde se află, ce epoci acoperă istoria, cum se citește această poveste (un capitol pe epocă și pe activitate, cu unitățile citate pe nume și cu ciornele marcate ca atare până când o persoană le validează) și pe ce surse se sprijină; să folosească doar briefingul, fără a inventa date sau fapte, și să lase deoparte o informație care pare ciudată, în loc să o comenteze. Textul stă **la începutul** capitolului; fișele surselor (documentele) rămân după el, iar substituenții „[to be written: a presentation of …]” și „[to be written: how this account is to be read…]” dispar.

**Limba.** Începând cu 5.13.128-alpha o alege cine scrie, în lista derulantă **Language of the prose** a filei: pornește de la limba narațiunii fișierului, dacă are una (TempluMare: engleză), altfel de la cea a QGIS. Se aplică textului pe care AI-ul îl scrie cu „Generate with AI” și „Regenerate chapter” și titlurilor capitolelor noi pe care „Prepare the chapters” le adaugă („Presentation”, „Where it is”); capitolele deja scrise nu se traduc, iar același capitol canonic într-o altă limbă nu se adaugă a doua oară. Instrucțiunile modelului există în italiană și în engleză: pentru celelalte limbi (germană, franceză, spaniolă, catalană, portugheză, română, greacă, arabă) modelul primește instrucțiunile în engleză, cu cererea de a scrie în acea limbă. Până la 5.13.127-alpha textul se năștea mereu în limba narațiunii: cu TempluMare, în engleză chiar și cu QGIS în italiană.

**Cum se salvează.** În formatul bibliotecii, același pe care îl citește EMStudio: un nod de narațiune (`NarrativeNode`) care conține capitolele; fiecare paragraf scris de model este un bloc „AI draft” atribuit **autorului AI** al acelui model; **promptul** folosit este înregistrat ca extractor legat de surse, astfel încât se poate afla ce s-a cerut. Unitățile citate în text sunt **mențiuni** (`[[name]]`): în fișier rămân legate de nodul unității, iar în filă și în exporturi apar cu numele ei. O mențiune care nu corespunde niciunei unități din graf este redusă la simple cuvinte, fără paranteze.

**Costuri și durate.** Modelul este apelat **o dată pentru fiecare capitol**, inclusiv Presentation. Cu un furnizor online, fiecare apel are un cost și un timp de așteptare (în încercări cu un model online, câteva zeci de secunde pe capitol: un sit cu aproximativ zece epoci durează câteva minute); cu Ollama sau LM Studio nu se plătește nimic, dar duratele depind de computerul tău.

### 10.5 Pas cu pas

1. Deschide matricea sitului (§10.1) și apasă fila **Narrative**. Verifică sus **ce model** va folosi.
2. **Închide EMStudio** dacă are fișierul deschis: pyArchInit și EMStudio scriu același fișier, iar cine scrie ultimul câștigă.
3. Opțional: **Prepare the chapters**, ca să vezi scheletul, fără AI.
4. Apasă **Generate with AI**. Urmărește progresul: Presentation, dacă este încă „to be written”, merge prima („Chapter 1 of 9 · Presentation”), apoi capitolele de epocă („Chapter 3 of 9 · …”); poți continua să folosești QGIS. La final, bara de mesaje spune, de exemplu, *„7 chapters generated, 1 failed: Modern age — …”* (7 capitole generate, 1 eșuat: Modern age — …), cu *„(cancelled)”* (anulat) dacă ai anulat, iar lista se reîncarcă: capitolele scrise sunt „AI draft”.
5. **Citește**: alege pe rând câte un capitol și citește textul de sub listă. Confruntă-l cu stratigrafia: este o ciornă construită din datele fișei US. Ca să vezi unde se află unitățile despre care vorbește, apasă pe numele lor sau folosește **Show on the map** (Arată pe hartă; §10.10).
6. Dacă un capitol nu te convinge, alege rândul lui și apasă **Regenerate chapter**. Noua ciornă **înlocuiește** ciorna anterioară nevalidată: dacă vrei să păstrezi versiunea de dinainte, exportă-o mai întâi. Dacă un capitol este „truncated”, regenerează-l **înainte** de a-l valida.
7. Când un capitol este în regulă, apasă **Endorse…** (§10.6).
8. Apasă **Export…** pentru a salva în HTML, DOCX sau PDF (§10.7), sau **Open in EMStudio** pentru a scrie manual „Where it is” și a finisa restul.
9. Mai târziu poți deschide din nou matricea: narațiunea rămâne (§10.8).

<!-- IMMAGINE: Captură de ecran a generării în curs: linia de progres „Chapter 3 of 9 · …” și butonul Cancel -->
![Generare în curs](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figura 4: Generare în curs, cu linia de progres și butonul Cancel*

Un capitol care eșuează nu le oprește pe celelalte: rezumatul spune care. Pentru a reîncerca, este suficient să apeși din nou **Generate with AI**, care scrie doar capitolele încă „to be written”.

### 10.6 Validarea: cine semnează

A valida înseamnă că o **persoană** își asumă răspunderea pentru textul scris de model. Nu se întâmplă niciodată de la sine: nici prin generare, nici prin salvare.

1. Apasă **Endorse…**. Se deschide un meniu mic: **„This chapter”** (Acest capitol) — activ doar dacă capitolul ales este „AI draft” — sau **„All chapters”** (Toate capitolele), adică toate ciornele AI încă nevalidate, în toate grafurile fișierului. Presentation se validează ca orice alt capitol: alege-o în listă, iar „This chapter” o validează de una singură.
2. O fereastră întreabă **„Who endorses? Pick an author or type a new name.”** (Cine validează? Alege un autor sau scrie un nume nou.) Lista conține **autorii umani deja existenți în graf** — persoanele numite în fișa US drept compilator (*schedatore*), director US și responsabil US — și poți scrie un nume nou, care devine un nou autor al grafului.
3. Bara de mesaje spune **„N blocks endorsed by `<name>`.”** (N blocuri validate de autorul ales.) sau „Nothing to endorse.” (Nimic de validat.) Fișierul este salvat.

<!-- IMMAGINE: Captură de ecran a meniului Endorse… („This chapter” / „All chapters”) și a ferestrei de alegere a autorului -->
![Validare](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figura 5: Validarea: meniul și alegerea autorului*

Blocurile trec de la „AI draft” la „endorsed”. În documentul exportat, persoana apare printre responsabili („a cura di”, îngrijit de), modelul apare ca asistent („con l'assistenza di”, cu asistența), iar paragrafele validate nu mai poartă semnul ⚠. Regenerarea nu șterge blocurile validate: o semnătură este un act și nu se pierde prin rescriere.

### 10.7 Exportul în HTML, DOCX sau PDF

Apasă **Export…**: se deschide fereastra de salvare, cu trei formate: „HTML page” (pagină HTML; `.html`), „Word document” (document Word; `.docx`) și „Printable PDF” (PDF de tipărit; `.pdf`). Numele propus este `<sit>_narrativa`, fără extensie, în folderul fișierului em.json: extensia o pune formatul ales în filtrul ferestrei; o extensie scrisă de mână (`.html`, `.docx` sau `.pdf`) are prioritate față de filtru. Bara de mesaje confirmă: „Narrative exported to `<path>`” (Narațiune exportată în fișierul ales).

Documentul conține:

- titlul narațiunii (de exemplu „Scavo archeologico — the story of the site”, adică „Săpătură arheologică — povestea sitului”), responsabilii („a cura di”) și modelul ca asistent („con l'assistenza di”);
- pentru fiecare capitol, întâi textul, cu unitățile citate prin numele lor, apoi lista unităților capitolului; pentru unitățile citate care au fotografii, o bandă de fotografii ia locul rândului lor (§10.11);
- **harta sitului** (începând cu 5.13.115-alpha, doar în HTML), într-un chenar fix: în dreapta pe ecranele late, sus pe telefon. Cu harta, pagina se lărgește (începând cu 5.13.116-alpha), iar textul păstrează o coloană lizibilă. În repaus arată toate unitățile grafului în gri deschis; un clic pe numele unei unități din text arată **doar unitățile din perioada acelui capitol** ca contururi cu numărul deasupra, unitatea apăsată **colorată**, și încadrează grupul; un clic pe titlul unui capitol face la fel, fără unitatea colorată. Rândul de sub hartă indică perioada și câte unități; „whole site” (tot situl) revine la vederea de ansamblu. Geometriile provin din vederile US și USM ale bazei de date a proiectului, în momentul exportului (situl grafului, unități asociate după arie și număr): o unitate citată, dar fără desen, are linkul și nimic pe hartă; fără o bază de date conectată, documentul nu are hartă;
- la sfârșit, secțiunea **Fonti** (surse): documentele pe care se sprijină povestea și intrarea „Prompt”, care trimite la promptul înregistrat în fișier.

Câteva lucruri de știut:

- **ciornele nevalidate intră în document**, fiecare precedată de „⚠︎ non validato da una persona” (nevalidat de o persoană), iar antetul spune câte blocuri se află în această stare. Pentru un document fără semne, validează mai întâi (§10.6). În HTML ciorna se citește ca restul textului, cu același font și același fundal: deasupra paragrafului rămâne rândul de avertizare, iar în stânga apare un filet chihlimbariu. În Word și în PDF avertizarea stă înaintea paragrafului (în PDF, pe un rând separat, fără semnul ⚠, §10.11);
- **intră toate capitolele**, chiar și cele încă „to be written”: substituentul lor „[to be written: …]” rămâne în text;
- textul stă **la începutul** capitolului, înaintea listei unităților; într-o narațiune scrisă cu o versiune anterioară poate fi încă la sfârșit și se pune la loc reexportând situl (§10.8) sau cu **Prepare the chapters** (Pregătește capitolele);
- figurile pe care un autor le-a prevăzut în EMStudio (de exemplu matricea unei epoci) nu sunt desenate de exportul pyArchInit: în document rămâne un substituent;
- HTML-ul este un singur fișier, autonom (și fotografiile sunt încorporate, iar harta este un SVG în interiorul fișierului, fără biblioteci externe: se deschide și pe telefon, fără rețea); DOCX-ul se deschide cu Word sau LibreOffice și are nevoie de pachetul `python-docx`, iar PDF-ul de biblioteca ReportLab (§10.11): ambele fac parte din cerințele pluginului.

<!-- IMMAGINE: Captură de ecran a documentului HTML exportat: un capitol cu o ciornă precedată de „⚠︎ non validato da una persona” -->
![Document HTML exportat](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figura 6: Documentul HTML exportat, cu o ciornă nevalidată marcată*

### 10.8 Reexportarea sitului: narațiunea rămâne

Reexportarea sitului din baza de date — cu **Vedi la matrice…**, cu **Esporta sito in em.json…** sau cu fereastra „Esporta Extended Matrix” din fișa US — **păstrează narațiunea** deja prezentă în fișierul de destinație: textul, validările, autorul AI și prompturile. Epocile apărute între timp primesc un capitol „to be written”. O notificare o spune: **„Narrative kept from the previous file (N chapters).”** (Narațiune păstrată din fișierul anterior, N capitole.) O vezi în bara de mesaje cu „Vedi la matrice…”, în rezumatul ferestrei „Esporta Extended Matrix” și, cu „Esporta sito in em.json…”, în detaliile ferestrei finale.

**Un sit importat dintr-un fișier em.json** (§5) are și narațiunea fișierului importat, pe care importul o memorează și o readuce în export. Începând cu 5.13.128-alpha câștigă cea mai recentă: dacă fișierul de lucru a fost salvat după import — cu „Prepare the chapters”, „Generate with AI”, „Endorse…” sau cu EMStudio pe același fișier —, trece narațiunea lui, cu notificarea obișnuită; dacă fișierul em.json a fost importat mai târziu, rămâne cea importată, iar o notificare o spune: *„The previous file's narrative was not kept: the em.json imported on … is newer, and its narrative wins. Backup copy of the previous file in ….”* (Narațiunea fișierului anterior nu a fost păstrată: fișierul em.json importat la … este mai recent, iar narațiunea lui câștigă. Copie de siguranță a fișierului anterior în ….) Până la 5.13.127-alpha câștiga întotdeauna cea importată: capitolele pregătite și scrise în panou dispăreau la exportul următor, cu o notificare care dădea vina, pe nedrept, pe forma fișierului.

**Celelalte modificări** făcute în fișier în EMStudio — pozițiile nodurilor, descrierile rescrise — **nu supraviețuiesc**, ca până acum: fișierul este regenerat din baza de date. Se păstrează doar narațiunea.

Înainte de a rescrie un fișier care conține o narațiune, pyArchInit face o **copie de siguranță** alături de el: `<sit>.em.json.bak` (fiecare reexportare nouă înlocuiește copia precedentă).

Dacă fișierul de dinainte era împărțit pe sondaje (versiunile până la 5.13.108-alpha puteau exporta un graf pentru fiecare sondaj), la prima reexportare fișierul nou are **un singur graf** pentru tot situl: grafurile au nume diferite, iar narațiunea **nu poate trece** în fișierul nou. O notificare o spune: *„The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in …”* (Narațiunea fișierului anterior (grafuri: …) nu a trecut în fișierul nou (grafuri: …): forma fișierului s-a schimbat. Copie de siguranță în …). Textul nu este pierdut: se află în copia `.bak`, care însă este înlocuită la următoarea reexportare a unui fișier care conține o narațiune — pune-o într-un loc sigur. Dacă ai nevoie de narațiunea veche, deschide acea copie (redenumind-o într-un fișier `.em.json` cu alt nume); altfel, regenerează capitolele în fișierul nou (§10.5). Din versiunea 5.13.109-alpha fișierul are mereu un singur graf, iar narațiunea trece de la o reexportare la alta.

Dacă fișierul anterior nu poate fi citit (de exemplu un fișier rămas scris pe jumătate), exportul merge înainte oricum: fișierul necitibil este **redenumit** `<sit>.em.json.broken`, iar o notificare spune *„The previous file cannot be read (…): its narrative, if any, was not kept.”* (Fișierul anterior nu poate fi citit (…): narațiunea lui, dacă exista, nu a fost păstrată.)

> **Narațiunea nu se află în baza de date pyArchInit: există doar în em.json.** Backup-ul bazei de date nu o copiază. Copiază din când în când folderul `pyarchinit_EM_folder`.

### 10.9 Din intrarea „Esporta sito in em.json…”

Intrarea **Extended Matrix → Esporta sito in em.json…** scrie același fișier `<sit>.em.json` în `pyarchinit_EM_folder`. La final afișează „Esportato `<cale>`” (Exportat), cu numărul de noduri, muchii și notificări (textul notificărilor se află în detaliile ferestrei), și **trei butoane**:

| Buton | Ce face |
|-------|---------|
| **Apri in EMStudio** (Deschide în EMStudio) | Deschide fișierul în EMStudio; dacă nu este instalat, oferă să îl instaleze. |
| **Narrativa con l'AI** (Narațiune cu AI) | Apare **doar dacă un AI este configurat** (§10.2): deschide panoul matricei direct pe fila Narrative. |
| **Chiudi** (Închide) | Închide fereastra. |

<!-- IMMAGINE: Captură de ecran a ferestrei finale „Esporta sito in em.json…” cu cele trei butoane -->
![Esporta sito in em.json: trei butoane](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figura 7: Fereastra finală a intrării „Esporta sito in em.json…”*

### 10.10 Unitățile pe hartă

Începând cu versiunea **5.13.108-alpha**, fila Narrative aduce pe **harta din QGIS** unitățile despre care vorbește un capitol, în două moduri:

- **O singură unitate: apasă pe numele ei.** În textul capitolului ales, numele unităților citate sunt **linkuri**: un clic selectează acea unitate pe stratul US încărcat și încadrează harta pe ea, cu o clipire. Nu deschide nimic.
- **Toate împreună: „Show on the map”** (*Mostra sulla mappa*; Arată pe hartă), pe al doilea rând de butoane, între „Prepare the chapters” (Pregătește capitolele) și „Export…” (Exportă…). Selectează și încadrează împreună toate unitățile despre care vorbește capitolul ales: cele citate în text sau, dacă textul nu citează niciuna (de exemplu pentru că capitolul nu este încă scris), toate unitățile din banda lui (epoca). Selecția este una singură pe strat — o înlocuiește pe cea existentă — iar încadrarea cuprinde toate geometriile găsite, care clipesc.

<!-- IMMAGINE: Captură de ecran din QGIS cu unitățile capitolului selectate pe hartă și, sus, bara de mesaje „Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.” -->
![Unitățile capitolului pe hartă](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Figura 8: Unitățile despre care vorbește un capitol, selectate pe hartă, și bara de mesaje*

Este nevoie ca un strat cu geometriile US să fie deja încărcat în proiect, de exemplu **vederea US** din pyArchInit: fila îl caută printre straturile încărcate, ca butonul „Zoom sulla geometria” (Zoom pe geometrie) din fila Units (tutorialul 01), recunoscând unitățile după câmpurile `sito`, `area` și `us`. **Proiectul nu este modificat**: nu se adaugă niciun strat, se schimbă doar selecția și încadrarea hărții. Începând cu **5.13.110-alpha**, dacă mai multe straturi poartă aceleași câmpuri — ca vederea US (poligoane) și vederea cotelor (puncte) —, fila încearcă mai întâi geometria cea mai plină: poligoane, apoi linii, apoi puncte; ordinea straturilor în legendă contează doar dacă tot restul este egal. Valabil și pentru butonul „Zoom sulla geometria”: nu mai este nevoie să pui vederea US în capul legendei.

Bara de mesaje („Narrative”) spune ce s-a găsit, de exemplu „Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9.” (5 din 6 unități evidențiate în „US view”, 7 geometrii; nedesenate: 1.US9). Numele dintre ghilimele este cel al stratului în care au fost găsite unitățile, așa cum apare în panoul de straturi din QGIS; o unitate poate avea mai multe geometrii, deci geometriile pot fi mai multe decât unitățile. Se caută doar unitățile care sunt rânduri ale fișei US: un document sau un nod de continuitate nu are geometrie și nu intră în numărătoare. Dacă unitățile nedesenate sunt mai mult de cinci, numele se opresc la primele cinci, urmate de „…” și de total.

Un clic pe un nume care nu este un rând al fișei US nu găsește nimic, iar bara de mesaje o spune. Dacă niciun strat încărcat nu poartă câmpurile pentru a recunoaște unitățile, mesajul o spune: încarcă vederea US (§10.13).

### 10.11 Fotografiile unităților și PDF-ul

Începând cu versiunea **5.13.108-alpha**, narațiunea arată și **fotografiile** unităților despre care vorbește — în textul filei și în exporturi — și poate fi salvată în plus ca **PDF de tipărit**.

**În textul capitolului.** Sub paragraful în care o unitate este numită prima dată apar **până la două miniaturi** ale fișierelor ei media: sunt aceleași ca în fila Units, citite din folderul de miniaturi al proiectului, iar dedesubt, cu litere mici, se află numele unității și numele fișierelor media. Dacă unitatea este numită din nou în același capitol, fotografiile nu se repetă.

**În exporturi.** În toate cele trei formate, pentru fiecare unitate citată în text care are imagini pe disc, o **bandă cu una sau două fotografii alăturate** ia locul rândului de text al unității, cu numele unității drept legendă: se folosește copia redusă, dacă există, altfel miniatura. Unitățile necitate în text rămân un rând de text. Fotografiile sunt încorporate în fișier: HTML-ul și DOCX-ul sunt scrise de biblioteca s3dgraphy, PDF-ul de pyArchInit.

**PDF-ul de tipărit.** Este un document A4 pe care pyArchInit îl scrie cu ReportLab, cu fontul Cambria ca celelalte PDF-uri ale pluginului (dacă fișierul fontului nu se află în folderul `bin` al pyArchInit, folosește Helvetica). Conține titlul, responsabilii („edited by”) și modelul ca asistent („with the assistance of”); în partea de sus, dacă există ciorne nevalidate, apare și un aviz cu numărul lor; apoi toate capitolele, ca în celelalte formate, fiecare cu textul său — unitățile citate scrise cu numele, iar înaintea fiecărui paragraf nevalidat un rând „non validato da una persona” (nevalidat de o persoană), fără semnul ⚠ — urmat de fotografii cu legenda lor și de celelalte unități cu litere mici; la sfârșit, sursele. În subsol se află „Generated by pyArchInit on …” (generat de pyArchInit la …) cu data și numărul paginii.

<!-- IMMAGINE: Capturi de ecran alăturate: textul unui capitol cu miniaturile sub prima mențiune a unei unități și o pagină a PDF-ului de tipărit cu banda de fotografii și legenda -->
![Fotografiile unităților în text și în PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Figura 9: Fotografiile unităților în textul capitolului și într-o pagină a PDF-ului*

**Ce este necesar.** Fotografiile nu se află în em.json: se citesc din baza de date și din folderele proiectului. Sunt deci necesare baza de date conectată (matricea deschisă din proiect), căile **Thumbnail path** și **Image resize** setate în configurare (tutorialul 01) și fișierele pe disc; pentru text este suficient folderul de miniaturi. Imaginile de pe o arhivă la distanță nu se folosesc. Dacă lipsește ceva, nu apare niciun mesaj: fotografiile pur și simplu nu apar, iar exportul reușește oricum (§10.13).

### 10.12 Avertismente

- **Închide EMStudio înainte de a genera sau a valida.** Dacă EMStudio are fișierul deschis, cine scrie ultimul câștigă.
- **Un AI scrie doar din ceea ce găsește în graf și poate greși.** Regulile îl țin în frâu, dar nu îl fac infailibil: citește fiecare capitol înainte de a-l valida.
- **Cu un furnizor online, datele ies din computerul tău.** Briefingul fiecărui capitol (numele, definițiile, descrierile și relațiile unităților) și cel pentru Presentation (numele sitului, toponimele, locurile, epocile, documentele și numele persoanelor numite în fișele US) sunt trimise serviciului ales; cu Ollama sau LM Studio rămân locale.
- **Fișierul se scrie la final.** Generarea salvează când se termină, chiar dacă ai anulat-o: nu închide QGIS cât timp AI-ul scrie. Salvarea este sigură: fișierul este scris alături, recitit și abia apoi înlocuiește fișierul real; dacă ceva merge prost, **fișierul anterior rămâne așa cum era**.
- **Nu redeschide matricea cât timp AI-ul scrie.** Fila rămâne pe fișierul de dinainte și avertizează: *„Generation in progress: wait for it to finish, or press Cancel, before changing file.”* (Generare în curs: așteaptă să se termine sau apasă Cancel înainte de a schimba fișierul.)
- **Textul se modifică în EMStudio**, nu în pyArchInit.
- Narațiunea și nodurile care o susțin (autorul AI, prompturile) **nu apar în desenul matricei**.

### 10.13 Rezolvarea problemelor

| Mesaj (en / it) | Cauză | Soluție |
|-----------------|-------|---------|
| „No AI configured…” / «Nessuna AI impostata…» | Niciuna dintre cele patru ferestre din §10.2 nu are un model (și, pentru OpenAI și Anthropic, cheia API). | Setează furnizorul și modelul — și cheia — într-una dintre acele ferestre, apoi **deschide din nou matricea**: fila recitește setările doar când se deschide. Chiar și fără AI poți pregăti capitolele, valida, exporta și deschide EMStudio. |
| „No narrative in the file…” / «Nessuna narrativa nel file…» | Fișierul nu are încă o narațiune (este normal prima dată). | Apasă **Prepare the chapters** (schelet) sau **Generate with AI** (schelet și text). N este numărul capitolelor de epocă și de activitate pe care le va avea scheletul (o epocă fără unități nu primește niciunul); mesajul „Chapters prepared” include în număr și „Presentation” și, dacă există, „Where it is”. „Generate with AI” scrie în plus „Presentation”, pe care N nu o numără: progresul numără un capitol în plus. |
| „EMStudio is not installed…” / «EMStudio non risulta installato…» | Programul nu a fost găsit pe computer. | Folosește intrarea de meniu **Extended Matrix → Installa EMStudio…** (are acest nume cu orice limbă a QGIS). |
| „truncated” / «troncato» lângă stare | Modelul s-a oprit la limita de lungime, iar textul se termină la jumătate. | Înainte de a valida, folosește **Regenerate chapter**; dacă se repetă, termină capitolul în EMStudio. |
| „N chapters generated, M failed: `<title>` — `<reason>`” / «N capitoli generati, M falliti: …» | Furnizorul a refuzat cererea (cheie nevalidă, cotă depășită, model indisponibil) sau serverul local nu răspunde. „the model wrote nothing” (modelul nu a scris nimic) înseamnă că răspunsul era gol. | Elimină cauza și apasă din nou **Generate with AI**: scrie doar capitolele rămase „to be written”. |
| „The previous file cannot be read (…)” / «Il file precedente non si legge (…)» | La reexportare, fișierul existent nu era un em.json care să poată fi citit. | Exportul a mers înainte: fișierul necitibil a fost păstrat lângă cel nou ca `….broken`, iar narațiunea pe care o conținea, dacă exista, nu a trecut în fișierul nou. Dacă ai nevoie de ea, recuperează-o din acel fișier sau dintr-un backup. |
| „The previous file's narrative (graphs: …) did not travel into the new file…” / «La narrativa del file precedente (grafi: …) non è passata nel file nuovo…» | Fișierul de dinainte era împărțit pe sondaje (versiuni până la 5.13.108-alpha): grafurile au nume diferite și narațiunea nu poate trece. | Fișierul de dinainte se află în copia `.bak`: deschide-o dacă ai nevoie de narațiunea veche, sau regenerează capitolele în fișierul nou. |
| „Could not write … The previous file is intact.” / «Non sono riuscito a scrivere … Il file precedente è intatto.» | Salvarea a eșuat (disc plin, fișier blocat, permisiuni). | Rezolvă problema și repetă: capitolele generate în acea sesiune nu fuseseră salvate. |
| „DocX export needs python-docx — install the extra: …” (întotdeauna în engleză) | Pachetul `python-docx` nu este instalat în Python-ul QGIS: este necesar doar pentru DOCX. | Instalează `python-docx` (face parte din cerințele pluginului) sau exportă în HTML, care nu necesită nimic. |
| „None of the loaded layers has the fields to recognise the units…” / «Nessuno dei layer caricati porta i campi per riconoscere le unità…» | Proiectul deschis nu are niciun strat cu câmpurile `sito`, `area` și `us` ale unităților (de exemplu vederea US din pyArchInit): fila caută doar printre straturile deja încărcate. | **Încarcă vederea US** din pyArchInit (sau un strat cu aceleași câmpuri) în proiect, apoi apasă din nou pe nume sau pe **Show on the map** (Arată pe hartă). Fila nu adaugă straturi de la sine. Începând cu 5.13.110-alpha nu e nevoie să o pui în capul legendei: la aceleași câmpuri, fila încearcă mai întâi poligoanele (§10.10). Încărcată din fișa US cu un stil ales (fereastra „Style Choice”, tutorialul 14), vederea US poartă și numărul unității într-un cerc. Începând cu 5.13.111-alpha, vederea cotelor (puncte), încărcată din fișa US, poartă și cota (două zecimale) deasupra simbolului. Stilul și etichetele vederii se stabilesc în fereastra „View styles” (intrarea de meniu „View styles…”, tutorialul 14); începând cu 5.13.112-alpha, un stil implicit salvat acolo comandă la încărcare. |
| Niciun mesaj: fotografiile nu apar în textul capitolului și nici în exporturi | Fotografiile se citesc din baza de date a proiectului și din folderele lui, și lipsește ceva: baza de date nu este conectată (matricea a fost deschisă fără ea), calea **Thumbnail path** nu există pe acest computer sau este o arhivă la distanță, fișierele nu sunt pe disc, sau unitatea nu este un rând al fișei US ori nu are fișiere media. | Verifică fila **Units**: dacă acolo unitatea își arată miniaturile, le vei găsi și aici. Altfel, deschide matricea din proiect, verifică **Thumbnail path** și **Image resize** în configurare (tutorialul 01) și dacă fișierele se află pe computer: imaginile de pe o arhivă la distanță nu intră. Exportul reușește oricum, fără fotografii. |

---

## Referințe

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Repository pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
