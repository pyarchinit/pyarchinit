# Tutorial 14: GIS și Cartografie

## Introducere

PyArchInit este integrat profund cu **QGIS**, valorificând toate funcționalitățile GIS pentru gestionarea spațială a datelor arheologice. Acest tutorial acoperă integrarea cartografică, straturile predefinite și funcții avansate precum **segmentarea automată SAM**.

### Funcții GIS Principale

- Vizualizarea US pe hartă
- Straturi vectoriale predefinite
- Stilizare QML personalizată
- Cote și măsurători GIS
- Segmentare automată (SAM)
- Export cartografic

## Straturi Predefinite PyArchInit

### Straturi Vectoriale Principale

| Strat | Geometrie | Descriere |
|-------|-----------|-----------|
| `pyunitastratigrafiche` | MultiPolygon | US depozit |
| `pyunitastratigrafiche_usm` | MultiPolygon | US zidărie |
| `pyarchinit_quote` | Point | Puncte de cotă |
| `pyarchinit_siti` | Point | Locații situri |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Zone de săpătură |
| `pyarchinit_strutture_ipotesi` | Polygon | Structuri ipotetice |
| `pyarchinit_documentazione` | Point | Referințe documentație |

### Atributele Stratului US

| Câmp | Tip | Descriere |
|------|-----|-----------|
| `gid` | Integer | ID unic |
| `scavo_s` | Text | Numele sitului |
| `area_s` | Text | Numărul zonei |
| `us_s` | Text | Numărul US |
| `stratigraph_index_us` | Integer | Index stratigrafic |
| `tipo_us_s` | Text | Tipul US |
| `rilievo_originale` | Text | Releveu original |
| `disegnatore` | Text | Autorul releveului |
| `data` | Date | Data releveului |

## Vizualizarea US pe Hartă

### Din Tab-ul „Hartă" în Fișa US

1. Deschideți o fișă US
2. Selectați tab-ul **Hartă**
3. Funcții disponibile:

| Buton | Funcție |
|-------|---------|
| Vizualizare US | Afișează US curentă pe hartă |
| Vizualizare Toate | Afișează toate US-urile din zonă |
| Înregistrare Nouă | Creează o geometrie nouă |
| Centrare pe | Centrează harta pe US |

### Vizualizare din Căutare

1. Executați o căutare US
2. Butonul **„Vizualizare Înregistrare"** → afișare individuală
3. Butonul **„Vizualizare Toate"** → afișare toate rezultatele

### Alegerea Stilului (US și USM)

Când US sau US de zidărie (USM) din rezultatele căutării sunt încărcate pe hartă, apare fereastra **Style Choice** („How do you want to manage the layer style?"). Butoanele sunt afișate în engleză:

| Buton | Efect |
|-------|-------|
| **Save new style** | Creează stilul pe baza câmpului ales și îl salvează în baza de date cu un nume |
| **Load existing style** | Folosește ca model un stil gata făcut, ales dintr-o listă (vezi mai jos), și creează stilul pe baza câmpului ales fără a-l salva în baza de date |
| **Use temporary style** | Creează stilul pe baza câmpului ales fără a-l salva în baza de date |
| **Single symbol (outline only)** | Desenează doar conturul geometriilor, fără umplere |

Începând cu 5.13.19-alpha, **Load existing style** deschide fereastra **Existing style** („Choose the style to use as a template:", în engleză) cu lista stilurilor disponibile: stilurile salvate în baza de date (*Database: nume*), stilurile QML livrate cu pyArchInit (`us_*.qml`, afișate ca *pyArchInit: …*) și **Other QML file…**, pentru a alege orice fișier `.qml`. Stilul ales este încărcat pe strat (transparența și modul de amestecare vin odată cu el, etichetele nu: pe vederile US și USM de poligoane sunt, începând cu 5.13.110-alpha, cele din paragraful **Etichete** de mai jos, numărul unității încercuit, orice ar spune stilul-model) și servește drept **model**: după alegerea câmpului de categorizare, valorile pe care stilul le are deja își păstrează culoarea și simbolul, iar celelalte primesc o copie a simbolului său cu o culoare proprie. Dacă alegerea este anulată, funcționează ca **Use temporary style**. Înainte căuta doar printre stilurile din baza de date și, dacă nu găsea niciunul, trecea direct la fereastra de categorizare.

Cu **Save new style**, **Load existing style** și **Use temporary style** se alege apoi câmpul de categorizare (fereastra **Select Categorization Field**, în engleză): **Stratigraphic Definition** (definiție stratigrafică), **SU Type** (tip US), **Interpretive Definition** (definiție interpretativă) sau **Period/Phase (cont_per)** (perioadă/fază, începând cu 5.13.19-alpha); fiecare valoare a câmpului primește o culoare proprie, care începând cu 5.13.19-alpha rămâne aceeași la fiecare încărcare a stratului. Cu **Period/Phase (cont_per)**, intrarea din legendă a fiecărui cod arată și datarea perioadei/fazei preluată din periodizare. Apar doar câmpurile prezente în strat.

**Ordinea de desenare.** Începând cu 5.13.19-alpha, unitățile sunt desenate în ordinea folosită de Manager Temporal (Time Manager): mai întâi cele fără perioadă, apoi după cronologia perioadei (din periodizarea perioadei/fazei inițiale a US sau din `cont_per`), apoi după `order_layer` (0 = cea mai veche) și, la final, tăierea deasupra umpluturii sale, astfel încât unitățile cele mai recente sunt deasupra. Se aplică tuturor opțiunilor de stil, inclusiv **Single symbol (outline only)**. Când straturile sunt încărcate perioadă cu perioadă, stilul este cerut o singură dată și folosit pentru toate perioadele.

**Etichete.** Începând cu 5.13.110-alpha, odată cu stilul ales, vederea US (și USM) primește și **etichetele** ei: numărul unității **îngroșat, într-un cerc alb cu bordură roșu închis**, **câte una pentru fiecare unitate**, pe desenul ei cel mai mare dacă se vede (neacoperit în întregime de unul de nivel superior), cu aceeași rețetă ca la planșele atlasului din Time Manager (tutorialul 25). Când două numere s-ar acoperi, unul este mutat, iar o linie de legătură îl unește cu desenul său. Se aplică la US și USM, cu SQLite și cu PostgreSQL, și la toate opțiunile de stil, inclusiv **Single symbol (outline only)**; dacă stilul încărcat cu **Load existing style** avea deja etichete, numărul încercuit le ia locul. Straturile de puncte nu primesc numărul încercuit. Începând cu 5.13.111-alpha, însă, **vederea cotelor** (punctele de cotă, stratul „Elevation view”), imediat ce este încărcată din fișa US, poartă **eticheta cu valoarea cotei** (două zecimale, de exemplu „12,35”), plasată **deasupra liniei orizontale a simbolului**, cu aceeași rețetă ca la planșele atlasului din Time Manager. Se aplică la toate comenzile care o încarcă, cu SQLite și cu PostgreSQL, și nu depinde de stilul ales; straturile care nu sunt de puncte sau care nu au câmpul cotei nu primesc această etichetă.

Începând cu 5.13.18-alpha, stilul ales (și câmpul de categorizare) este respectat și cu bazele de date SQLite, atât pentru US, cât și pentru USM; înainte harta apărea întotdeauna cu o culoare pentru fiecare US.

## Stilizarea Straturilor

### Fișiere QML

PyArchInit include stiluri predefinite în format QML:
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Aplicarea Stilului

1. Selectați stratul în legendă
2. Clic dreapta → **Proprietăți**
3. Tab-ul **Stil**
4. **Încarcă stil** → selectați QML

### Personalizare

Stilurile pot fi personalizate pentru:
- Culori bazate pe tipul US
- Etichete cu numărul US
- Transparență
- Margini și umpleri

## Cote și Măsurători

### Stratul de Cote

Stratul `pyarchinit_quote` stochează:
- Coordonate X, Y
- Cota Z (absolută)
- Tipul punctului de cotă
- US de referință
- Zona de referință

### Calculul Automat al Cotelor

Din Fișa US, cotele min/max sunt calculate:
1. Interogare puncte de cotă asociate US-ului
2. Extragerea valorii minime și maxime
3. Afișare în raport

### Introducerea Cotelor

1. Stratul de cote în mod editare
2. Desenați un punct pe hartă
3. Completați atributele:
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentarea Automată SAM

### Ce este SAM?

**SAM (Segment Anything Model)** este modelul de inteligență artificială al Meta care împarte o imagine în obiectele sale. În pyArchInit, fereastra SAM transformă o imagine în **poligoane**, pornind de la:

- o **ortofotografie** (un fișier raster: GeoTIFF, JPEG georeferențiat…);
- sau un **strat de tile-uri (dale) ori un serviciu** încărcat în QGIS: XYZ precum ESRI World Imagery sau Google, WMS, ArcGIS REST.

Nu doar pietre: și **clădiri, drumuri, câmpuri, râuri, ziduri**. Modelele sunt din două familii:

- **SAM 2.1** (Meta) găsește contururile obiectelor — ale tuturor sau ale celor indicate prin puncte, o casetă sau un poligon —, dar nu spune ce sunt;
- **clasele text** (YOLOE-26 local, SAM 3 în cloud) caută ceea ce scrieți («building, road, river, field») și fiecare poligon își poartă eticheta.

Poligoanele ajung în stratul ales: straturile US ale pyArchInit, orice strat poligonal al proiectului sau un strat temporar nou.

### Accesarea Funcției

1. Din bara de instrumente pyArchInit: butonul derulant **Instrumente de analiză** (Analysis Tools) → «SAM - Segmentation (stones, buildings, roads, fields…)». Este acțiunea implicită a butonului: un clic pe pictogramă deschide direct fereastra.
2. Sau din meniul **pyArchInit** → «SAM - Segmentation (stones, buildings, roads, fields…)».

Fereastra se numește «SAM — Segmentation (stones, buildings, roads, fields, rivers…)». Etichetele ei există doar în italiană și engleză: cu QGIS în română apare în engleză, ca în schemă. În continuare, fiecare etichetă tradusă este urmată de cea engleză între paranteze.

### Interfața SAM

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Cinci grupuri, de completat de sus în jos: «Mediu local» (*Local environment*), «Imagine» (*Image*), «Ce se segmentează» (*What to segment*), «Model» (*Model*), «Destinație» (*Target*). Dedesubt se află linia de stare («Gata», *Ready*), unde apar și mesajele lucrului în curs, și butoanele «Pornește» (*Start*), «Anulează» (*Cancel*, vizibil doar în timpul lucrului) și «Închide» (*Close*). Unele rânduri apar doar când e nevoie: «Cheie API:» (*API key:*) în locul stării ponderilor pentru modelele cloud; «Sit:» (*Site:*), «Zonă:» (*Area:*), «Index stratigrafic:» (*Stratigraphic index:*) și «Tip US:» (*US type:*) pentru straturile US; «Câmp pentru etichetă:» (*Field for the label:*) pentru celelalte straturi. Fereastra reține ultima zonă US, clasele, latura maximă, modelul ales și cheile API.

Intrările din lista de modele sunt scrise mereu în italiană («Locale» = local), la fel ca unele mesaje de serviciu citate mai jos.

#### Mediu local

Modelele locale (SAM 2.1 și YOLOE) nu rulează în Python-ul QGIS, ci într-un **Python separat**, pe care fereastra îl creează și îl verifică singură. La deschidere grupul afișează «verificare…» (*checking…*), apoi:

- cu verde «gata — ultralytics …, torch …, mps» (*ready — …*): mediul există; ultimul cuvânt este dispozitivul de calcul (`mps`, `cuda` sau `cpu`);
- cu portocaliu «neinstalat: necesar pentru modelele locale (SAM 2.1, YOLOE). Un Python de sistem 3.10–3.13, ~1,5 GB de pachete.» (*not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.*).

«Instalează / actualizează» (*Install / update*) creează mediul sau îi actualizează pachetele (vedeți mai jos «Instalarea SAM Local»); «Arată jurnalul» (*Show log*) deschide și închide jurnalul instalării, cu ieșirea lui pip rând cu rând. Modelele cloud nu au nevoie de mediu.

#### Imagine

- «Strat raster:» (*Raster layer:*): imaginea de segmentat, aleasă dintre rasterele proiectului: o ortofotografie (fișier) sau un strat de tile-uri/serviciu. Dedesubt, cu gri, scrie despre care dintre ele e vorba: numele fișierului și dimensiunile în pixeli (`orthophoto.tif — 12000 × 9000 px`) sau tipul de serviciu, randat din vizualizare (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)`; acest rând este în italiană, *reso dalla vista* = randat din vizualizare).
- «Extindere:» (*Area:*): «vizualizarea curentă» (*current view*, ceea ce se vede pe hartă) sau «tot rasterul» (*whole raster*). «tot rasterul» se poate alege doar pentru fișiere: un serviciu de tile-uri nu are margine, așa că se lucrează mereu pe vizualizare (sau pe o casetă ori un poligon).
- «Rezoluție (unități de hartă/px):» (*Resolution (map units/px):*): doar pentru tile-uri: câte unități de hartă (metri, sau grade dacă harta este în coordonate geografice) pentru fiecare pixel al imaginii randate. Valoarea propusă este cea a vizualizării la deschiderea ferestrei sau la alegerea stratului: dacă schimbați apoi zoomul, corectați-o manual. Cu cât e mai mică, cu atât mai multe detalii.
- «Latura maximă (px):» (*Max side (px):*): latura cea mai lungă a imaginii transmise modelului: implicit 2048, de la 512 la 8192. Peste această latură imaginea este micșorată; SAM lucrează oricum intern la 1024 px.

### Moduri de Segmentare

Grupul «Ce se segmentează» (*What to segment*) oferă șase moduri. La alegerea unui mod se schimbă lista modelelor (vedeți «Modele Disponibile») și dedesubt apare, cu albastru, instrucțiunea pentru acel mod.

#### 1. Totul automat

«Tot (automat)» (*Everything (automatic)*): SAM 2.1 segmentează fiecare obiect pe care îl găsește în extinderea aleasă la «Extindere:» («vizualizarea curentă» sau «tot rasterul»). Poligoanele nu au clasă: în stratul temporar primesc eticheta «segment». Se pornește cu «Pornește» (*Start*).

#### 2. Puncte

«Puncte: faceți clic pe obiectele de pe hartă» (*Points: click the objects on the map*): apăsați «Pornește selecția» (*Start selection*); fereastra se ascunde, iar bara de mesaje a QGIS amintește comenzile. Faceți clic pe obiecte unul câte unul: fiecare clic este un obiect. Clic dreapta sau Enter pentru a termina, Backspace elimină ultimul punct, Esc anulează. Fereastra reapare și segmentarea rulează pe extinderea aleasă la «Extindere:», câte un obiect pentru fiecare punct; punctele din afara imaginii sunt ignorate.

#### 3. Casetă

«Casetă: desenați un dreptunghi» (*Box: draw a rectangle*): apăsați «Pornește selecția» și trageți un dreptunghi pe hartă (Esc sau clic dreapta anulează). Imaginea este decupată pe dreptunghi și tot ce se află înăuntru este segmentat.

#### 4. Poligon

«Poligon: desenați zona» (*Polygon: draw the area*): apăsați «Pornește selecția» și faceți clic pe vârfuri; clic dreapta, Enter sau dublu clic închid poligonul (sunt necesare cel puțin trei vârfuri), Backspace elimină ultimul vârf, Esc anulează. Se segmentează doar interiorul poligonului.

#### 5. Poligon din strat

«Poligon din strat:» (*Polygon from layer:*): alegeți un strat poligonal din lista derulantă alăturată. Se folosește entitatea selectată din strat, sau toate dacă nu e selectată niciuna (mai multe entități sunt unite într-una). Ca la poligonul desenat, se segmentează doar interiorul: util pentru a lucra în interiorul unui sondaj, al unei zone de săpătură sau al unei limite deja desenate. Se pornește cu «Pornește».

#### 6. Clase text

«Clase text:» (*Text classes:*): scrieți în câmpul alăturat ce trebuie căutat: cuvinte în **engleză** separate prin virgulă (implicit «building, road, river, field»; alte exemple: stone, wall). Fiecare clasă devine o etichetă a poligoanelor. Funcționează cu YOLOE-26 local sau cu SAM 3 de la Roboflow în cloud, pe extinderea aleasă la «Extindere:». Se pornește cu «Pornește».

**«Prag:»** (*Threshold:*; implicit 0,30, de la 0,05 la 0,95) este încrederea minimă pentru ca un rezultat să fie păstrat: mai jos dă mai multe poligoane, inclusiv nesigure; mai sus dă mai puține, dar mai sigure. Modelul cloud Replicate nu îl folosește.

### Modele Disponibile

Grupul «Model» (*Model*) are o listă derulantă «Model:» (*Model:*) al cărei conținut depinde de modul ales:

| Model | Tip | Cerințe | Moduri |
|-------|-----|---------|--------|
| SAM 2.1 Tiny | Local | mediu local + ponderi ~78 MB | toate, în afară de clasele text; cel mai ușor și mai rapid |
| SAM 2.1 Small | Local | mediu local + ponderi ~92 MB | toate, în afară de clasele text |
| SAM 2.1 Base+ | Local | mediu local + ponderi ~162 MB | toate, în afară de clasele text |
| SAM 2.1 Large | Local | mediu local + ponderi ~449 MB | toate, în afară de clasele text; cel mai precis și cel mai lent |
| Cloud: Replicate SAM-2 | Cloud | cheie API Replicate | doar segmentare automată (în modul «Puncte» clicurile sunt ignorate, cu un avertisment) |
| YOLOE-26 S | Local | mediu local + ponderi ~31 MB + MobileCLIP2 254 MB (o dată) | clase text |
| YOLOE-26 M | Local | mediu local + ponderi ~70 MB + MobileCLIP2 254 MB (o dată) | clase text |
| YOLOE-26 L | Local | mediu local + ponderi ~79 MB + MobileCLIP2 254 MB (o dată) | clase text |
| Cloud: Roboflow SAM 3 | Cloud | cheie API Roboflow | clase text |

În lista derulantă intrările arată așa: «Locale: SAM 2.1 Tiny — ~78 MB», «Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB», «Cloud: Replicate SAM-2 (solo automatico, chiave API)», «Cloud: Roboflow SAM 3 (classi a testo, chiave API)» (*locale* = local, *classi a testo* = clase text, *solo automatico* = doar automat, *chiave* = cheie).

**Ponderi.** Pentru un model local, sub lista derulantă apare starea ponderilor (fișierele modelului): «ponderi prezente ✓» (*weights present ✓*, verde) sau «ponderi lipsă (~N MB)» (*weights missing (~N MB)*, portocaliu), cu butonul «Descarcă ponderile» (*Download weights*). Descărcarea, cu bară de progres, ia fișierele din resursele publice ale ultralytics de pe GitHub (nu e nevoie de cont). Pentru YOLOE se descarcă și codificatorul de text MobileCLIP2 (254 MB), o singură dată pentru S, M și L. Ponderile se află în `~/pyarchinit_5/bin/models/sam/`.

**Cheie API.** Pentru un model cloud, câmpul «Cheie API:» (*API key:*) și linkul pentru a o obține înlocuiesc starea ponderilor (vedeți «Configurarea API»).

### SAM-3 cu Prompt Text

Cu modul «Clase text» nu se cere „împarte totul”, ci „găsește aceste lucruri”:

- se scriu una sau mai multe clase în engleză, separate prin virgulă: `building, road, river, field` sau `stone, wall`…;
- **YOLOE-26** (local, S/M/L) înțelege cuvintele prin codificatorul de text MobileCLIP2; **SAM 3** de la Roboflow (cloud) primește aceleași clase ca prompturi text (cel mult 16);
- fiecare poligon poartă clasa care l-a găsit: în stratul temporar, în câmpul `label`; într-un strat propriu, în «Câmp pentru etichetă:» (*Field for the label:*). În straturile US ale pyArchInit clasa nu se scrie.

SAM 2.1 în «Tot (automat)», în schimb, nu atribuie clase: găsește contururi, nu nume.

### Configurarea API

Cheile sunt necesare doar pentru modelele cloud. Alegeți modelul cloud din listă, lipiți cheia în câmpul «Cheie API:» (*API key:*; textul rămâne ascuns) și apăsați «Pornește»: cheia este salvată în setările QGIS și propusă din nou data viitoare. Cu modelele cloud, imaginea pregătită este trimisă serviciului.

#### API Replicate (SAM-2)
1. Creați un cont pe [replicate.com](https://replicate.com)
2. Creați un token la [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) (linkul «Cheie Replicate» (*Replicate key*) de lângă câmp deschide aceeași pagină)
3. Lipiți-l în «Cheie API:» cu modelul «Cloud: Replicate SAM-2»

#### API Roboflow (SAM-3)
1. Creați un cont pe [roboflow.com](https://roboflow.com)
2. Copiați cheia de la [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) (linkul «Cheie Roboflow» (*Roboflow key*) de lângă câmp)
3. Lipiți-o în «Cheie API:» cu modelul «Cloud: Roboflow SAM 3»

### Instalarea SAM Local

Nu este nevoie de nicio comandă în terminal: mediul pentru modelele locale se instalează din fereastră.

1. Este necesar un **Python de sistem 3.10–3.13**: pachetele nu se instalează în Python-ul QGIS, ca să nu riscați să-l stricați. Fereastra îl caută singură: pe **macOS** Python de pe [python.org](https://www.python.org/downloads/) sau din Homebrew, pe **Windows** lansatorul `py` al Python-ului de pe python.org, pe **Linux** `python3.10`…`python3.13` sau `python3` al sistemului.
2. Apăsați «Instalează / actualizează» (*Install / update*) în grupul «Mediu local»: se creează mediul virtual `~/pyarchinit_5/bin/sam_venv` și în el se instalează `ultralytics` (care aduce torch, torchvision, OpenCV, numpy) și `requests`: aproximativ **1,5 GB** de pachete, o singură dată. Pe Linux fără placă NVIDIA se instalează torch pentru CPU, mult mai ușor.
3. «Arată jurnalul» (*Show log*) arată pip la lucru. La sfârșit starea devine verde: «gata — ultralytics …, torch …, mps».
4. Descărcați ponderile modelului pe care vreți să-l folosiți cu «Descarcă ponderile» (*Download weights*, grupul «Model»).

O nouă apăsare pe «Instalează / actualizează» actualizează pachetele. Dispozitivul de calcul se alege singur: **MPS** pe Mac-urile cu Apple Silicon, **CUDA** cu o placă NVIDIA, altfel **CPU** (funcționează, dar mai lent). Dacă MPS sau CUDA eșuează, lucrul repornește singur pe CPU.

| Ce | Unde |
|----|------|
| Mediul Python | `~/pyarchinit_5/bin/sam_venv` |
| Ponderile modelelor | `~/pyarchinit_5/bin/models/sam/` |
| Chei API | setările QGIS |

`~/pyarchinit_5` este dosarul de date al pyArchInit (sau cel indicat de variabila `PYARCHINIT_HOME`).

### Destinație și Atribute

Grupul «Destinație» (*Target*) decide unde ajung poligoanele. Lista «Strat:» (*Layer:*) conține straturile poligonale ale proiectului și «— strat temporar nou —» (*— new temporary layer —*); dacă `pyunitastratigrafiche` este încărcat, este propus acesta.

| Destinație | Ce se scrie |
|------------|-------------|
| «— strat temporar nou —» | un strat în memorie `SAM_<raster>_<data_ora>`, în SRC-ul imaginii, cu câmpurile `label` (clasa sau «segment»), `score` (încredere), `area`, `source` (modelul) și `created` (data și ora) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = «Sit:» (*Site:*; din configurație, nemodificabil), `area_s` = «Zonă:» (*Area:*; obligatorie), `stratigraph_index_us` = «Index stratigrafic:» (*Stratigraphic index:*; 1 = pietre/obiecte, 2 = strat/suprafață), `tipo_us_s` = «Tip US:» (*US type:*; pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <model>` (de ex. `SAM sam2.1_t.pt`), `data` = azi; `us_s` rămâne gol |
| alt strat poligonal | clasa în «Câmp pentru etichetă:» (*Field for the label:*), un câmp text (se propune `label`, `etichetta`, `classe`, `class`, `tipo` sau `nome`, dacă există; gol = nu se scrie); dacă stratul are câmpuri `score`, `area`, `source` sau `created`, se completează și acestea |

- În straturile US numărul US se atribuie ulterior, în tabelul de atribute; mesajul final amintește acest lucru: «Atribuiți apoi numerele US în tabelul de atribute.» (*Then assign the US numbers in the attribute table.*).
- Poligoanele sunt reproiectate în SRC-ul stratului de destinație și salvate imediat în el (dacă stratul era deja în editare, se salvează și modificările lui în așteptare).
- Stratul temporar trăiește doar până la închiderea QGIS: pentru a-l păstra, exportați-l într-un fișier (clic dreapta pe strat → Export).

### Cum Funcționează

1. **Imaginea.** Pentru un fișier, extinderea este decupată și, la nevoie, micșorată cu GDAL: pixelii sunt cei reali ai fișierului, nu cei desenați pe hartă (stilul stratului nu contează; rasterele care nu sunt pe 8 biți sunt întinse la 0–255). Tile-urile și serviciile nu au fișier: QGIS randează vizualizarea cu propriul motor de desenare, la rezoluția aleasă — doar acel strat, fără celelalte straturi ale hărții —, și se segmentează randarea.
2. **Zona.** Cu un poligon (desenat sau din strat) se ia dreptunghiul care îl conține, se albește tot ce e în afară, iar la final rezultatele sunt decupate pe poligon.
3. **Modelul.** Lucrul îl face `scripts/sam_worker.py`, care rulează în afara QGIS cu Python-ul din `sam_venv` (sau apelează serviciul cloud): QGIS nu se blochează. Mesajele lui de progres (rândurile `[sam] …` ale workerului, în italiană) apar în linia de stare: modelul și dispozitivul, apoi câte poligoane în câte secunde. Poligoanele sub 20 de pixeli sunt eliminate, iar contururile simplificate.
4. **Întoarcerea pe hartă.** Workerul returnează poligoanele în pixeli; pyArchInit le readuce în coordonate cu georeferențierea imaginii, repară geometriile invalide și le reproiectează în SRC-ul stratului de destinație.

### Flux de Lucru SAM

**1. Pregătire**
- Încărcați ortofotografia sau un strat de tile-uri (de ex. ESRI World Imagery ca XYZ Tiles)
- Verificați sistemul de referință al proiectului
- Pentru a scrie în US: încărcați `pyunitastratigrafiche` (sau `pyunitastratigrafiche_usm`) și verificați situl în configurație
- Prima dată, pentru modelele locale: «Instalează / actualizează», apoi «Descarcă ponderile»

**2. Configurare**
- «Imagine»: strat raster, extindere, rezoluție (pentru tile-uri) și latura maximă
- «Ce se segmentează»: modul, pragul și, pentru clasele text, clasele
- «Model»: un model local cu ponderile prezente sau un model cloud cu cheia lui
- «Destinație»: stratul și atributele lui

**3. Execuție**
- «Pornește» sau «Pornește selecția», apoi puncte, casetă sau poligon pe hartă
- Urmăriți linia de stare; «Anulează» întrerupe lucrul
- La final apare «Gata: N poligoane adăugate la „strat” (model).» (*Done: N polygons added to “layer” (model).*)

**4. Post-procesare**
- Verificați poligoanele; eventualele avertismente apar în bara de mesaje a QGIS
- Straturi US: atribuiți numerele US (`us_s`) în tabelul de atribute
- Corectați, uniți sau ștergeți poligoanele greșite cu instrumentele de editare ale QGIS
- Strat temporar: exportați-l dacă trebuie păstrat

## Integrare Cartografică

### Export Date GIS

Din Fișa US, tab-ul Hartă:
- **Export GeoPackage**: Strat ca GPKG
- **Export Shapefile**: Strat ca SHP
- **Export GeoJSON**: Strat ca JSON

### Import Date GIS

Import geometrii existente:
1. Încărcați stratul în QGIS
2. Selectați entitățile
3. Folosiți funcția de import

### Geoprocesare

Operații spațiale disponibile:
- Buffer
- Intersecție
- Uniune
- Diferență
- Centroizi

## Bune Practici

### 1. Ortofotografii

- Rezoluție minimă: 1-2 cm/pixel
- Format: GeoTIFF georeferențiat
- Sistem de referință: consistent cu proiectul

### 2. Digitizare

- Folosiți snap pentru precizie
- Verificați topologia
- Mențineți consistența atributelor

### 3. Segmentare SAM

- Ortofotografie de bună calitate, iluminare uniformă, contrast bun între obiecte și fundal
- **Ortofotografii mari**: lucrați pe vizualizare sau pe casetă, nu pe «tot rasterul». SAM lucrează intern la 1024 px, iar peste valoarea «Latura maximă (px):» imaginea este micșorată: pe o zonă prea mare obiectele mici se pierd
- **Tile-uri**: alegeți un nivel de zoom la care obiectele se recunosc cu ochiul liber (de ex. 0,3–0,6 m/px pentru clădiri și drumuri). «Rezoluție (unități de hartă/px):» o propune pe cea a vizualizării; dacă extinderea e mare, imaginea este micșorată la latura maximă, iar rezoluția reală se înrăutățește
- **Clase text**: substantive englezești simple (building, road, river, field, stone, wall)
- Clasele vin doar de la YOLOE sau SAM 3: SAM 2.1 în «Tot (automat)» găsește contururi, dar nu atribuie clase
- **Hardware**: Mac-urile cu Apple Silicon folosesc MPS, o placă NVIDIA folosește CUDA, altfel CPU-ul, mai lent (atunci sunt preferabile SAM 2.1 Tiny sau Small, YOLOE-26 S și zone mici)
- Post-verificarea este întotdeauna necesară

### 4. Organizarea Straturilor

- Grupare pe tip
- Folosiți stiluri consistente
- Mențineți ordinea în legendă

## Depanare

### Straturile Nu Sunt Afișate

**Cauze posibile**:
- Extindere greșită
- Sistem de referință diferit
- Filtru activ

**Soluții**:
- Zoom la Strat
- Verificați CRS
- Eliminați filtrele

### SAM Nu Funcționează

| Mesaj sau simptom | Ce trebuie făcut |
|-------------------|------------------|
| «Mediu local» cu portocaliu: «neinstalat…» (*not installed…*), sau «Mediul local nu este instalat: apăsați „Instalează / actualizează” (sau alegeți un model cloud).» (*The local environment is not installed: press “Install / update” (or choose a cloud model).*) | Apăsați «Instalează / actualizează». Este necesar un Python de sistem 3.10–3.13; dacă lipsește, apare `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` (nu s-a găsit niciun Python 3.10–3.13: instalați Python de pe python.org sau din Homebrew). Dacă pip eșuează, eroarea este în «Arată jurnalul». Pe Linux fără placă NVIDIA se instalează torch pentru CPU |
| «ponderi lipsă (~N MB)» (*weights missing (~N MB)*), sau «Lipsesc ponderile modelului: apăsați „Descarcă ponderile”.» (*The model weights are missing: press “Download weights”.*) | Apăsați «Descarcă ponderile» (este necesară conexiunea la internet) |
| «Este necesară cheia API a serviciului.» (*The service API key is needed.*) | Cu un model cloud, lipiți cheia în «Cheie API:» (vedeți «Configurarea API») |
| «Nu s-a găsit niciun poligon: încercați o zonă mai mică, un prag mai mic sau alt model.» (*No polygon found: try a smaller area, a lower threshold or another model.*) | Extindere mai mică, «Prag:» mai mic, alt model (un SAM 2.1 mai mare sau clasele text); pentru tile-uri, o rezoluție mai fină |
| «Zona aleasă nu acoperă rasterul» (mesaj în italiană: `l'area scelta non copre il raster`) | Vizualizarea, caseta sau poligonul sunt în afara rasterului: încadrați rasterul și încercați din nou |
| «Completați zona pentru stratul US.» (*Fill in the area for the US layer.*) | Completați câmpul «Zonă:» din grupul «Destinație» |
| «Raster rotit: nesuportat (reproiectați-l mai întâi)» (mesaj în italiană: `raster ruotato: non supportato (riproiettalo prima)`) | Reproiectați rasterul cu gdalwarp (meniul Raster din QGIS) și folosiți fișierul nou |
| «Segmentarea a eșuat» (*Segmentation failed*) cu ultimele rânduri ale workerului | Citiți rândurile din mesaj; încercați din nou cu o extindere mai mică sau o latură maximă mai mică («Latura maximă (px):»), ori cu un model mai mic |

### Geometrii Corupte

**Cauze posibile**:
- Erori de digitizare
- Import problematic

**Soluții**:
- Folosiți „Reparare Geometrii"
- Redesenați elementul

### Strat încărcat, dar geometrii invizibile (SQLite)

**Simptom**:
- Un strat pyArchInit dintr-o bază de date SQLite/SpatiaLite (ex. US `pyunitastratigrafiche`, USM, materiale, US negative) se încarcă și tabelul de atribute afișează înregistrările, dar pe hartă nu se desenează nimic, iar „Zoom la Strat" nu funcționează

**Cauză**:
- Indexul spațial (R*Tree) al stratului nu a fost întreținut: triggerele sale s-au pierdut când un tabel a fost recreat (ex. de scripturi vechi de actualizare a schemei) sau datele au fost importate ocolindu-le
- QGIS alege entitățile de desenat prin acest index, deci ele rămân invizibile
- Au fost afectate și bazele de date create din șablonul SQLite între octombrie 2025 și septembrie 2026

**Soluție (automată)**:
- La conectarea la o bază de date SQLite, pyArchInit verifică toți indecșii spațiali (câteva clipe; nu se scrie nimic dacă baza de date este intactă) și îi reconstruiește automat pe cei deteriorați
- Începând cu versiunea 5.13.16-alpha, aceeași verificare repară și **vederile spațiale** (`pyarchinit_us_view`, `pyarchinit_quote_view`, structuri, materiale, vederile UT etc.):
  - fiecare vedere este legată de ROWID-ul tabelului său de geometrie
  - înregistrările vederilor care nu mai există sunt eliminate
  - vederile standard lipsă sunt recreate
  - vederile UT sunt înregistrate ca vederi spațiale
  - tabelele de geometrie fără index spațial primesc unul: necesar când GDAL-ul inclus în QGIS nu are funcțiile SpatiaLite (ex. QGIS pe macOS), unde fără index acele straturi nu desenau nimic
- Înainte de a modifica ceva, salvează O SINGURĂ copie de siguranță lângă baza de date: `<baza_de_date>.sqlite.pre_spatial_index_repair_<data-ora UTC>`
- Rezultatul este scris în panoul de mesaje jurnal al QGIS (View → Panels → Log Messages), fila „PyArchInit"

**Ce trebuie făcut**:
- Nimic de pornit manual: verificarea rulează automat la PRIMA conectare la fiecare bază de date în fiecare sesiune QGIS (deci după actualizarea pluginului sau după repornirea QGIS)
- Dacă straturile erau deja încărcate, eliminați-le și adăugați-le din nou (sau redeschideți proiectul) după reparare
- Dacă jurnalul „PyArchInit" raportează că un index NU a putut fi reparat (ex. SpatiaLite nu poate fi încărcat), remediați cauza și reporniți QGIS: verificarea se repetă doar într-o sesiune nouă
- Fișierul de siguranță poate fi șters după verificarea straturilor
- Pentru a repeta verificarea (ex. după restaurarea unei copii de siguranță), reporniți QGIS
- Notă: în `inventario_materiali_view` punctul șantierului este repetat pentru fiecare material, deci „Identify" pe acel punct afișează unul dintre materiale

## Referințe

### Fișiere Sursă
- `modules/gis/pyarchinit_pyqgis.py` - Integrare GIS
- `tabs/Sam_Segmentation_Dialog.py` - Fereastra SAM: grupuri, moduri, destinație
- `modules/utility/sam_environment.py` - Mediu Python separat, pachete și ponderi
- `modules/gis/sam_raster_source.py` - Imaginea de segmentat (decupare GDAL sau randarea vizualizării) și georeferențiere
- `modules/gis/sam_map_tools.py` - Instrumente de hartă pentru puncte, casetă și poligon
- `scripts/sam_worker.py` - Worker în afara QGIS: SAM 2.1, YOLOE, Replicate, Roboflow

### Straturi
- `pyunitastratigrafiche` - US depozit
- `pyunitastratigrafiche_usm` - US zidărie
- `pyarchinit_quote` - Cote

---

## Tutorial Video

### Integrare GIS
`[Substituent: video_gis_integration.mp4]`

**Conținut**:
- Straturi predefinite
- Vizualizarea US
- Stilizare și etichete
- Export cartografic

**Durată estimată**: 15-18 minute

### Segmentare SAM
`[Substituent: video_sam_segmentation.mp4]`

**Conținut**:
- Configurarea SAM
- Moduri de segmentare
- Post-procesare
- Bune practici

**Durată estimată**: 12-15 minute

---

*Ultima actualizare: ianuarie 2026*

---

## Animație Interactivă

Explorați animația interactivă pentru a afla mai multe despre acest subiect.

[Deschideți Animația Interactivă](../../animations/pyarchinit_image_classification_animation.html)
