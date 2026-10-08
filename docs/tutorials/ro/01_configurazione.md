# PyArchInit - Ghid de Configurare

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea Configurarii](#accesarea-configurarii)
3. [Fila Parametri de Conexiune](#fila-parametri-de-conexiune)
4. [Fila Instalare Baza de Date](#fila-instalare-baza-de-date)
5. [Fila Instrumente de Import](#fila-instrumente-de-import)
6. [Fila Graphviz](#fila-graphviz)
7. [Fila PostgreSQL](#fila-postgresql)
8. [Fila Ajutor](#fila-ajutor)
9. [Fila FTP catre Lizmap](#fila-ftp-catre-lizmap)
10. [Workspace Paradata (doar PostgreSQL)](#workspace-paradata-doar-postgresql)

---

## Introducere

Fereastra de configurare PyArchInit va permite sa setati toti parametrii necesari pentru functionarea corecta a plugin-ului. Inainte de a incepe documentarea unei sapaturi arheologice, trebuie sa configurati corect conexiunea la baza de date si caile catre resurse.

> **Tutorial Video**: [Inserati link video pentru introducerea in configurare]

---

## Accesarea Configurarii

Pentru a accesa configurarea:
1. Deschideti QGIS
2. Meniu **PyArchInit** → **Config**

Sau din bara de instrumente PyArchInit faceti clic pe pictograma **Setari**.

![Accesarea configurarii](images/01_configurazione/01_menu_config.png)
*Figura 1: Accesarea ferestrei de configurare din meniul PyArchInit*

![Bara de instrumente PyArchInit](images/01_configurazione/02_toolbar_config.png)
*Figura 2: Pictograma de configurare in bara de instrumente*

---

## Fila Parametri de Conexiune

Aceasta este fila principala pentru configurarea conexiunii la baza de date.

![Fila Parametri de Conexiune](images/01_configurazione/03_tab_parametri_connessione.png)
*Figura 3: Fila Parametri de Conexiune - Vedere completa*

### Sectiunea Setari BD

| Camp | Descriere |
|------|-----------|
| **Database** | Selectati tipul de baza de date: `sqlite` (local) sau `postgres` (server) |
| **Host** | Adresa serverului PostgreSQL (de ex., `localhost` sau IP-ul serverului) |
| **DBname** | Numele bazei de date (de ex., `pyarchinit`) |
| **Port** | Portul de conexiune (implicit: `5432` pentru PostgreSQL) |
| **User** | Numele de utilizator pentru conexiune |
| **Password** | Parola utilizatorului |
| **SSL Mode** | Modul SSL pentru PostgreSQL: `allow`, `prefer`, `require`, `disable` |

![Setari BD](images/01_configurazione/04_db_settings.png)
*Figura 4: Sectiunea Setari BD*

#### Alegerea Bazei de Date

**SQLite/Spatialite** (Recomandat pentru utilizator unic):
- Baza de date locala, nu necesita server
- Ideala pentru proiecte individuale sau mici
- Fisierul `.sqlite` este salvat in folderul `pyarchinit_DB_folder`

![Configurare SQLite](images/01_configurazione/05_config_sqlite.png)
*Figura 5: Exemplu de configurare SQLite*

**PostgreSQL/PostGIS** (Recomandat pentru echipe):
- Baza de date pe server, acces multi-utilizator
- Necesita PostgreSQL cu extensia PostGIS instalata
- Suporta gestionarea utilizatorilor si permisiuni
- Ideala pentru proiecte mari cu mai multi operatori

![Configurare PostgreSQL](images/01_configurazione/06_config_postgres.png)
*Figura 6: Exemplu de configurare PostgreSQL*

> **Tutorial Video**: [Inserati link video pentru configurarea bazei de date]

### Sectiunea Setari Cai

| Camp | Descriere | Buton |
|------|-----------|-------|
| **Thumbnail path** | Calea pentru salvarea miniaturilor imaginilor | `...` pentru navigare |
| **Image resize** | Calea pentru imaginile redimensionate | `...` pentru navigare |
| **Logo path** | Calea catre logo-ul personalizat pentru rapoarte | `...` pentru navigare |

![Setari Cai](images/01_configurazione/07_path_settings.png)
*Figura 7: Sectiunea Setari Cai*

#### Cai la Distanta Suportate

PyArchInit suporta si stocare la distanta:
- **Google Drive**: `gdrive://folder/path/`
- **Dropbox**: `dropbox://folder/path/`
- **Amazon S3**: `s3://bucket/path/`
- **Cloudinary**: `cloudinary://cloud_name/folder/`
- **WebDAV**: `webdav://server/path/`
- **HTTP/HTTPS**: `https://server/path/`

![Stocare la Distanta](images/01_configurazione/08_remote_storage.png)
*Figura 8: Exemplu de configurare stocare la distanta*

> **Configurarea media pe WebDAV.** Pentru a folosi un server WebDAV ca spatiu de stocare a imaginilor:
>
> 1. **Credentiale** — dialogul **Remote Storage Config**, fila **WebDAV**: introduceti *Username* si *Password*.
> 2. **Verify SSL** (aceeasi fila) — daca serverul foloseste un **certificat auto-semnat** (tipic pentru servere aflate pe o adresa IP simpla sau pe un port HTTPS non-standard), setati **"Verify SSL" → No (Self-signed certificates)**: cu verificarea activata fata de un server auto-semnat conexiunea esueaza in tacere. Pentru servere cu un certificat valid (de ex. Nextcloud/ownCloud) lasati-l pe **Yes (Verify certificates)**, care este valoarea implicita.
> 3. **Cai** — in campurile **Thumbnail path** si **Thumbnail resize** folositi formatul `webdav://server:port/folder/` (de ex. `webdav://192.0.2.10:5006/pyarchinit_media/thumb_resize/`).
> 4. **Reporniti QGIS** dupa salvare, pentru ca noile setari de stocare sa intre in vigoare.

### Folderul de date pyArchInit 5 (`~/pyarchinit_5`)

pyArchInit 5 stocheaza toate datele de lucru — `config.cfg`, baze de date, exporturi, copii de siguranta, paradata si folderul `bin/` cu instrumentele AI — intr-un folder dedicat din directorul personal: **`~/pyarchinit_5/`**.

Acesta este separat de pyArchInit classic, care continua sa foloseasca **`~/pyarchinit/`**. Cele doua versiuni prin urmare **nu** partajeaza date, astfel incat puteti rula pyArchInit 5 in timp ce instalarea anterioara si bazele sale de date raman neatinse.

**Prima lansare — copierea datelor existente.** Prima data cand pyArchInit 5 porneste, daca `~/pyarchinit_5` nu exista inca dar o instalare anterioara `~/pyarchinit` este gasita, apare un dialog care intreaba daca doriti sa copiati configuratia si bazele de date in noul folder:

- Alegeti **Da** pentru a copia `pyarchinit_DB_folder` (adica `config.cfg` si bazele de date SQLite) in `~/pyarchinit_5`, astfel incat sa puteti continua sa lucrati imediat cu datele existente.
- **Folderul `bin/` nu este copiat**, deoarece contine resurse AI de dimensiuni mari (medii virtuale SAM si ceramica, modele CLIP, indecsi FAISS, fisiere cu chei API). Recreati-le ruland din nou functiile AI relevante, sau copiati manual `~/pyarchinit/bin` in `~/pyarchinit_5/bin`.
- Daca alegeti **Nu**, pyArchInit 5 creeaza pur si simplu o noua structura de foldere goala, ca la o instalare noua.

> **Nou in 5.13.16-alpha — prima lansare mai clara.**
> - Intrebarea "copiati configuratia si bazele de date in noul folder `~/pyarchinit_5`?" apare acum intotdeauna in prim-plan, in fata oricarei ferestre. Inainte, mai ales pe Windows, putea ramane ascunsa in spatele QGIS sau al ecranului de pornire (splash), iar pornirea parea blocata. Raspundeti **Da** sau **Nu** pentru a continua.
> - Cat timp se instaleaza pachetele Python lipsa, ecranul de pornire pyArchInit ramane in prim-plan cu o bara de progres care arata pachetul n din N, procentul si timpul scurs. Instalarea poate dura cateva minute: nu inchideti QGIS. Pe Windows nu se deschid ferestre de consola in timpul instalarii.

> **Nou in 5.13.17-alpha — QGIS 4 si mai multe versiuni de QGIS pe acelasi computer.**
> - Pachetele Python ale pyArchInit sunt instalate cu Python-ul versiunii de QGIS pe care o folositi (de exemplu Python 3.12 in QGIS 4). Inainte, cu QGIS 3 si QGIS 4 instalate impreuna pe macOS, erau instalate pentru Python-ul din QGIS 3, iar QGIS 4 se oprea cu eroarea `No module named 'psycopg2._psycopg'`.
> - Daca folderul plugin-ului contine pachete instalate pentru alt Python (de exemplu un profil QGIS 3 copiat in QGIS 4), la pornire pyArchInit le muta in folderul `ext_libs_cp39` (numele indica versiunea de Python) si le reinstaleaza pe cele necesare: prima data poate dura cateva minute, cu progresul afisat pe ecranul de pornire (splash). Mesajul apare in panoul de jurnal (log) al QGIS, fila "PyArchInit".
> - Folderele `ext_libs_cp…` pot fi sterse. Daca folositi acelasi plugin din doua versiuni de QGIS, pyArchInit pune la loc folderul potrivit in loc sa reinstaleze.

**Locatie personalizata (avansat).** Pentru a utiliza un folder de date diferit, setati variabila de mediu `PYARCHINIT_HOME` inainte de a porni QGIS; cand este setata, suprascrie locatia implicita `~/pyarchinit_5`.

### Sectiunea Setari Santier

| Camp | Descriere |
|------|-----------|
| **Site** | Numele implicit al santierului pentru inregistrari noi |
| **Experimental features** | Activare functii experimentale (Da/Nu) |

---

## Fila Instalare Baza de Date

Aceasta fila va permite sa instalati sau sa actualizati baza de date PyArchInit.

![Fila Instalare BD](images/01_configurazione/08_tab_installazione_db.png)
*Figura 8: Fila Instalare Baza de Date*

### Instalare Noua

1. Selectati **sqlite** sau **postgres** ca tip de baza de date
2. Faceti clic pe **Conectare**
3. Daca baza de date nu exista, faceti clic pe **Instalare Baza de Date**
4. Sistemul va crea toate tabelele necesare

### Actualizare Baza de Date

Pentru instalari existente:
1. Faceti clic pe **Verificare/Actualizare Baza de Date**
2. Sistemul verifica structura si aplica eventualele actualizari

> **Atentie**: Faceti intotdeauna o copie de siguranta a bazei de date inainte de actualizare!

---

## Fila Instrumente de Import

Instrumente pentru importul datelor din surse externe.

### Import CSV

1. Selectati fisierul CSV
2. Mapati coloanele la campurile bazei de date
3. Faceti clic pe **Import**

### Import Shapefile

Pentru importul datelor GIS direct in straturile PyArchInit.

### Exportul unui sit in em.json (Extended Matrix)

Din meniul **pyArchInit → Extended Matrix → Esporta sito in em.json…** un sit intreg trece in formatul de lucru al Extended Matrix, cel pe care **EMStudio** il deschide nativ.

La ce sa va asteptati:

- pyArchInit listeaza siturile din baza de date: se alege **unul**;
- fisierul se naste in `pyarchinit_EM_folder` in dosarul de date al pluginului, cu numele sitului (orice alfabet: `Al-Khutm.em.json`, `Scavo_archeologico.em.json`);
- inainte de a-l preda, pyArchInit **reciteste fisierul**: un export care nu se reciteste identic nu este livrat;
- la final intreaba daca sa il **deschida imediat in EMStudio**; daca EMStudio nu este instalat, pyArchInit arata unde este fisierul si **ofera sa il instaleze acum** (vezi paragraful urmator).

In fisier se afla doar situl ales, iar fiecare unitate ajunge acolo ca ceea ce este:

- **doar randurile acelui sit**: intr-o baza de date cu mai multe situri, documentatia si perioadele celorlalte situri nu mai intra in export;
- **fiecare unitate cu tipul pe care il declara**: unitatile virtuale raman virtuale, special finds si continuitatile raman ele insele, astfel incat EMStudio deseneaza simbolul potrivit in loc sa faca din toate un strat;
- **paradatele calatoresc ca paradate**, nu ca unitati stratigrafice;
- o **coloana goala** a fisei nu mai devine o proprietate goala in graf.

Ceea ce deseneaza panoul **«Vedi la matrice»** este exact ceea ce se afla in fisier: o privire asupra lui este cel mai rapid mod de a verifica exportul inainte de a-l trimite in EMStudio sau intr-o camera.

> **Nota**: GraphML ramane doar ca **import unic din yEd**; formatul pentru vizualizarea si validarea matricei este em.json.

### Instalarea EMStudio din meniu

**EMStudio** este vizualizatorul Extended Matrix: un program separat al proiectului Extended Matrix (licenta GPL-3). pyArchInit nu il contine — il **descarca si il porneste**, cand i se cere.

Cu **pyArchInit → Extended Matrix → Installa EMStudio…** (Instaleaza EMStudio):

1. pyArchInit citeste release-urile oficiale ale EMStudio si **alege pachetul pentru acest computer** (macOS Apple Silicon, Windows, Linux);
2. inainte de descarcare arata o fereastra cu **versiunea, numele fisierului, dimensiunea, adresa de la care descarca si dosarul de destinatie** — `<dosarul de date pyArchInit>/tools/EMStudio` — si asteapta un da;
3. dupa descarcare **verifica amprenta sha256** declarata de release: un fisier care nu corespunde nu este instalat;
4. pe macOS **scoaterea carantinei** face parte din instalare: build-ul nu este semnat de Apple si fara acest pas sistemul ar spune ca aplicatia este "deteriorata";
5. la final arata unde a fost instalat. Daca EMStudio era deja acolo, intreaba daca sa descarce din nou ultima versiune.

Daca exportul in em.json nu gaseste EMStudio, **propune sa il instaleze pe loc** si apoi deschide fisierul.

> **Limita cunoscuta**: release-ul de astazi nu publica un pachet pentru **Mac-urile Intel**. In acest caz pyArchInit o spune si indica pagina release-urilor (github.com/ExtendedMatrix/EMStudio/releases), de unde se descarca manual.

### Vizualizarea matricei in QGIS

Din meniul **pyArchInit → Extended Matrix → Vedi la matrice…** (Vezi matricea) matricea unui sit este desenata intr-un **panou andocat in dreapta** ferestrei QGIS. Nu e nevoie de EMStudio, nici de un nod StratiGraph, nici de autentificare, nici de internet: pyArchInit exporta em.json al sitului intr-un dosar temporar si il deseneaza.

La ce sa ne asteptam:

- se alege **situl** dintr-o lista; panoul se deschide cu matricea deja potrivita in fereastra si, sus, un rand care spune **cate unitati, cate epoci si cate relatii** au fost desenate;
- desenul are **o banda orizontala pentru fiecare perioada/faza**, cea **mai recenta sus**, fiecare cu numele ei, cu anii ei si cu propria culoare;
- fiecare unitate sta in banda perioadei in care s-a nascut, iar in interiorul benzii stratigrafia decide nivelul: **ce acopera este desenat deasupra a ceea ce este acoperit**;
- fiecare unitate este desenata cu **simbologia Extended Matrix**, cea din regulile s3dgraphy (vezi tabelul);
- **rotita mouse-ului** mareste si micsoreaza, un **dublu clic** readuce toata matricea in fereastra (ca butonul **Adatta** / Potrivire), un **clic pe o unitate** ii arata fisa in cadrul din dreapta: definitie, interpretare, perioada si faza, datare, arie, structura;
- sub fisa apar **media legate de acea US**: miniaturile fotografiilor, cu numele lor. Daca imaginile stau pe o arhiva la distanta, miniaturile nu se descarca singure — un buton **Carica le anteprime** (incarca miniaturile) le cere, fiindca fiecare este o cerere in retea;
- butonul **Zoom sulla geometria** incadreaza pe harta planul unitatii. Se aprinde doar pentru unitatile care sunt randuri ale fisei US (un nod de continuitate sau un document nu are geometrie) si cauta printre **straturile deja incarcate**, in ordinea legendei, fara sa adauge vreunul. Daca niciun strat incarcat nu poarta campurile pentru a recunoaste unitatea, sau daca planul nu a fost desenat, panoul o spune in loc sa nu faca nimic.

| Unitate | Simbol |
|---|---|
| US — unitate stratigrafica | dreptunghi |
| USVs — unitate virtuala structurala | paralelogram albastru |
| USVn — unitate virtuala nestructurala | hexagon verde |
| SF — descoperire speciala (special find) | octogon oliv |
| BR / CON — continuitate | romb negru |
| Extractor | pentagon |
| Combinator | hexagon punctat |
| Document | elipsa |
| Proprietate | cerc punctat |

**Salva SVG…** (Salveaza SVG) si **Salva PNG…** (Salveaza PNG) salveaza desenul unde se doreste. **SVG-ul este vectorial**: se deschide intr-un navigator sau in Inkscape, se mareste cat e nevoie fara sa se incetoseze si se tipareste la orice dimensiune, inclusiv postere.

Aceeasi matrice se deschide si din fereastra **«Export Extended Matrix»** a fisei US: butonul **«Vedi la matrice»**, langa **«Apri in EMStudio»**, se aprinde dupa un export em.json reusit si deseneaza fisierul abia exportat.

> **Nota**: pe un sit foarte mare panoul o spune singur, cu un mesaj in bara de mesaje a QGIS, si recomanda **salvarea SVG-ului si privirea lui in afara QGIS**: parcurgerea pe ecran a unui desen cu mii de unitati este lenta.

> **Nota**: matricea se deseneaza si cand sapatura nu este in ordine. Relatiile care arata spre un element de paradata raman in desen, iar unitatile al caror nivel nu poate fi decis pentru ca relatiile contin o bucla sunt desenate oricum: panoul nu refuza o sapatura reala.

### Livrarea unui sit intr-o camera StratiGraph

Din meniul **pyArchInit → Extended Matrix → Consegna sito alla stanza…** unitatile unui sit calatoresc spre o **camera** a unui nod StratiGraph (REST, o livrare pe rand — nu e nevoie de o conexiune permanenta).

La ce sa va asteptati:

- se alege **situl**, apoi fereastra cere **nodul** (ex. `http://127.0.0.1:8020`; pentru un nod institutional `https://nod.org/em` — scrierea radacinii functioneaza si ea, `/em` este gasit singur), **camera** si, doar daca nodul o cere, un **token** (cel mai bine in variabila de mediu `STRATIGRAPH_TOKEN`: nu este salvat niciodata);
- rezultatul este o fraza: *«129 aplicate din 129»* la prima livrare; la a doua *«44 aplicate din 129, 85 deja prezente»* — **repetarile nu dubleaza nimic**: nodurile fuzioneaza, muchiile cunoscute revin ca «deja prezente»;
- randurile care nu pot deveni unitati ale camerei (documente, extractoare, proprietati) sunt listate la *Arata detalii*, niciodata inventate;
- **semnatura apartine celui care livreaza**: autorul este scris de nod din identitatea verificata, nu din payload.

Cu **Extended Matrix → Apri il nodo (stanze)…** camera se deschide **in pyArchInit** (panou lateral): se foloseste Qt WebEngine daca profilul QGIS il are, altfel Qt WebKit, pe care QGIS 3 il livreaza inca — astfel panoul ramane in QGIS si acolo unde lipseste WebEngine, iar browserul extern este doar ultima solutie. Cu o camera configurata se deschide direct pagina ei, fara una se deschide poarta nodului cu toate camerele.

### Migrarea intregii baze de date dintr-o singura data

Pentru a muta o baza de date intreaga in alta — din SQLite in PostgreSQL, din PostgreSQL in SQLite sau intre doua de acelasi fel — nu este nevoie sa repetati operatia tabel cu tabel: alegeti **ALL** in lista tabelelor si apasati **Import**.

Se copiaza **44 de tabele**: toate fisele (inclusiv buget, personal, prezente, echipamente, deviz, inventarul pieselor de piatra, arheozoologie, determinarea sexului si a varstei) **si toate geometriile** (US, USM, cote, situri, sectiuni, documentatie, materiale, indivizi, probe, morminte, structuri, linii de referinta, impartiri spatiale).

- **Inainte de a incepe**, daca baza de destinatie contine deja date, pyArchInit o spune si arata ce tabele si cate randuri: acolo unde nu exista o constrangere de unicitate inregistrarile s-ar adauga la cele existente. Puteti renunta.
- **In timpul copierii**, bara de progres arata tabelul in lucru.
- **La final**, o singura fereastra rezuma cate randuri au trecut pentru fiecare tabel; *Afiseaza detalii* arata si ce nu a trecut, si de ce.

Programul se ocupa singur de: inregistrarea coloanei geometrice cu SRID-ul datelor cand tabelul de destinatie este gol (o baza SQLite creata din sablon ar refuza toate geometriile); transformarea in nul a campurilor numerice goale, pe care PostgreSQL nu le accepta; **pastrarea identificatorilor inregistrarilor intr-o destinatie goala**, astfel incat legaturile (miniaturi, media, relatiile cu US) sa functioneze in continuare.

> **Nota**: utilizatorii, rolurile, permisiunile si jurnalele de acces **nu** sunt migrate: apartin instalarii si contin parolele.

---

## Fila Graphviz

Configurarea Graphviz pentru generarea diagramelor Harris Matrix.

| Camp | Descriere |
|------|-----------|
| **Graphviz Path** | Calea catre instalarea Graphviz (de ex., `/usr/bin/` pe Linux) |
| **Check Graphviz** | Verificati instalarea Graphviz |

### Instalarea Graphviz

**Windows**: Descarcati de pe [graphviz.org](https://graphviz.org/download/)

**macOS**: `brew install graphviz`

**Linux**: `sudo apt install graphviz`

---

## Fila PostgreSQL

Setari avansate ale serverului PostgreSQL.

| Camp | Descriere |
|------|-----------|
| **pg_dump path** | Calea catre pg_dump pentru copii de siguranta |
| **psql path** | Calea catre comanda psql |

---

## Fila Ajutor

Contine linkuri utile si resurse.

| Resursa | Descriere |
|---------|-----------|
| Tutorial Video | Link catre tutoriale video YouTube |
| Documentatie Online | https://pyarchinit.github.io/pyarchinit_doc/index.html |
| Facebook | Pagina UnaQuantum |

---

## Fila FTP catre Lizmap

Configurare pentru publicare web cu Lizmap.

| Camp | Descriere |
|------|-----------|
| **FTP Host** | Adresa serverului FTP |
| **FTP User** | Numele de utilizator FTP |
| **FTP Password** | Parola FTP |
| **Remote Path** | Calea de destinatie pe server |

---

## Workspace Paradata (doar PostgreSQL)

In **Fila DB Sync** a ferestrei de configurare se gaseste sectiunea **Paradata Workspace**, care permite personalizarea directorului in care sunt salvate fisierele `paradata_<sit>.graphml` si `groups_<sit>.graphml` cand se foloseste o baza de date PostgreSQL.

> **Doar PostgreSQL**: utilizatorii SQLite nu sunt afectati de aceasta setare. Cu SQLite, fisierele paradata sunt in continuare stocate langa fisierul `.sqlite` (comportament legacy, byte-identic).

### Cale implicita

Fara override, calea rezolvata este:

```
~/pyarchinit/pyarchinit_DB_folder/<host>_<port>_<dbname>/<sit>/
```

Exemplu: `~/pyarchinit/pyarchinit_DB_folder/localhost_5432_pyarchinit/Volterra/`

### Personalizarea caii

- **Browse...** deschide un dialog pentru a alege un director. Calea este salvata imediat in QSettings QGIS.
- Calea poate fi si **tastata** direct in campul text: valoarea este persistata la iesirea din camp (semnalul `editingFinished`). Lasarea campului gol elimina override-ul.
- **Reset** goleste campul, elimina cheia din QSettings si restaureaza calea implicita.

### Lantul de rezolutie (cine castiga)

Calea efectiva urmeaza un lant de fallback in 3 nivele:

1. **Variabila de mediu `PYARCHINIT_WORKSPACE_DIR`** (prioritate maxima — utila pentru scripturi CI/test).
2. **QSettings `pyarchinit/paradata_workspace`** (override UI — aceasta sectiune).
3. **Implicit** `~/pyarchinit/pyarchinit_DB_folder/`.

Valorile goale sunt sarite: daca `PYARCHINIT_WORKSPACE_DIR=""`, rezolutia trece la nivelul 2; daca si QSettings este gol, se foloseste calea implicita.

### Cand are efect

Modificarile sunt **imediate**: urmatorul acces la ParadataStore / GroupStore (de ex. salvarea de paradata pe o fisa US sau exportul unei Matrix) foloseste noua cale. **Nu este necesara repornirea QGIS.**

### Cazuri de utilizare

- **Drive de retea partajat**: directionarea workspace-ului catre o cale de retea (ex. `/Volumes/team/pyarchinit_workspace`) pentru a partaja paradata intre utilizatori pe un PostgreSQL centralizat.
- **Backup separat**: mentinerea fisierelor paradata in afara directorului home pentru a facilita backup-uri dedicate.
- **Teste izolate**: setarea `PYARCHINIT_WORKSPACE_DIR` in scripturi de test pentru a nu polua workspace-ul implicit.

---

## Depanare

### Conexiune Esuata

**Cauze**:
- Date de autentificare incorecte
- Serverul nu ruleaza
- Firewall-ul blocheaza conexiunea

**Solutii**:
- Verificati numele de utilizator si parola
- Verificati daca serviciul PostgreSQL ruleaza
- Verificati regulile firewall-ului

### Baza de Date Negasita

**Cauza**: Baza de date nu a fost inca instalata

**Solutie**: Mergeti la fila Instalare BD si faceti clic pe Instalare Baza de Date

---

## Bune Practici

1. **Faceti copii de siguranta regulat**: Folositi functia de Salvare si Restaurare
2. **Folositi PostgreSQL pentru echipe**: Suport mai bun pentru multi-utilizator
3. **Setati caile corecte**: Asigurati-va ca toate setarile de cai indica directoare valide
4. **Testati conexiunea**: Verificati intotdeauna conexiunea inainte de a incepe lucrul

---

*Ultima actualizare: Ianuarie 2026*

---

## Animatie Interactiva

Explorati animatia interactiva pentru a intelege mai bine procesul de instalare si configurare.

[Deschideti Animatia de Instalare](../../animations/pyarchinit_installation_animation.html)

Explorati animatia interactiva pentru gestionarea stocarii la distanta.

[Deschideti Animatia Stocare la Distanta](../../animations/pyarchinit_remote_storage_animation.html)
