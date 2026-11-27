# PyArchInit - StratiGraph: Panoul de sincronizare

> Panoul si fereastra camerei urmeaza limba interfetei QGIS; aici butoanele sunt citate asa cum apar in romana.

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea panoului](#accesarea-panoului)
3. [Intelegerea interfetei](#intelegerea-interfetei)
4. [Exportul pachetelor](#exportul-pachetelor)
5. [Sincronizare](#sincronizare)
6. [Gestionarea cozii](#gestionarea-cozii)
7. [Trimiterea unui sit intr-o camera StratiGraph](#trimiterea-unui-sit-intr-o-camera-stratigraph)
8. [Configurare](#configurare)
9. [Depanare](#depanare)
10. [Intrebari frecvente](#intrebari-frecvente)

---

## Introducere

Incepand cu versiunea **5.0.2-alpha**, PyArchInit include un panou **StratiGraph Sync** care permite sincronizarea datelor offline-first cu Knowledge Graph-ul StratiGraph. Acest panou face parte din proiectul european **StratiGraph** (Horizon Europe) si implementeaza fluxul de lucru offline-first: lucrati local fara internet, exportati pachete cand sunteti pregatit, iar sistemul se sincronizeaza automat cand conectivitatea este restabilita.

<!-- VIDEO: Introducere in StratiGraph Sync -->
> **Tutorial video**: [Inserati linkul video introducere StratiGraph Sync]

### Prezentarea fluxului de lucru

```
1. Lucru offline         2. Export pachet        3. Sincronizare auto
   (OFFLINE_EDITING)        (LOCAL_EXPORT)         (QUEUED_FOR_SYNC)
        |                      |                      |
   Introducere normala   Export + Validare       Incarcare cand este online
   a datelor in          + Adaugare in coada     cu reincercare automata
   PyArchInit
```

---

## Accesarea panoului

Panoul StratiGraph Sync este ascuns implicit si poate fi comutat printr-un buton din bara de instrumente.

### Din bara de instrumente

1. Cautati butonul **StratiGraph Sync** in bara de instrumente PyArchInit -- are o pictograma verde cu sageti de sincronizare si litera "S"
2. Faceti clic pe buton pentru a **afisa** panoul (este un buton de comutare)
3. Faceti clic din nou pe buton pentru a **ascunde** panoul

Panoul apare ca un **widget dock in stanga** in interfata QGIS. Il puteti trage si repozitiona ca orice panou dock QGIS.

<!-- IMAGINE: Butonul din bara de instrumente pentru StratiGraph Sync -->
> **Fig. 1**: Butonul StratiGraph Sync din bara de instrumente (pictograma verde cu sageti de sincronizare si "S")

<!-- IMAGINE: Panoul docuit in partea stanga a QGIS -->
> **Fig. 2**: Panoul StratiGraph Sync docuit in partea stanga a ferestrei QGIS

---

## Intelegerea interfetei

Panoul StratiGraph Sync este impartit in mai multe sectiuni, de sus in jos.

### Indicatorul de stare

**Indicatorul de stare** din partea superioara a panoului arata starea curenta de sincronizare a datelor dumneavoastra. Starile posibile sunt:

| Stare | Pictograma | Descriere |
|-------|------------|-----------|
| **OFFLINE_EDITING** | Creion | Lucrati local, editand datele in mod normal |
| **LOCAL_EXPORT** | Pachet | Se exporta un pachet din datele locale |
| **LOCAL_VALIDATION** | Bifa | Pachetul exportat este validat |
| **QUEUED_FOR_SYNC** | Ceas | Pachetul a fost validat si asteapta sa fie incarcat |
| **SYNC_SUCCESS** | Cerc verde | Cea mai recenta sincronizare s-a finalizat cu succes |
| **SYNC_FAILED** | Cerc rosu | Cea mai recenta tentativa de sincronizare a esuat |

### Indicatorul de conexiune

Sub indicatorul de stare, **indicatorul de conexiune** arata daca sistemul poate ajunge la serverul StratiGraph:

| Status | Semnificatie |
|--------|-------------|
| **Online** | Punctul de verificare a sanatatii este accesibil; sincronizarea automata este activa |
| **Offline** | Punctul de verificare a sanatatii nu este accesibil; pachetele vor fi adaugate in coada |

Sistemul verifica automat conectivitatea la fiecare **30 de secunde** (configurabil).

### Contorul cozii

**Contorul cozii** afiseaza doua numere:

- **Pachete in asteptare**: Numarul de pachete care asteapta sa fie incarcate
- **Pachete esuate**: Numarul de pachete a caror incarcare a esuat (acestea vor fi reincercate automat)

### Ultima sincronizare

Afiseaza **marca temporala** si **rezultatul** (succes sau esec) al celei mai recente tentative de sincronizare.

### Butoane de actiune

| Buton | Actiune |
|-------|---------|
| **Export pachet** | Creeaza un pachet din datele locale, il valideaza si il adauga in coada de sincronizare |
| **Sincronizează acum** | Forteaza o tentativa imediata de sincronizare (disponibil doar cand este online) |
| **Coada...** | Deschide dialogul de gestionare a cozii care afiseaza toate intrarile |
| **Trimite situl într-o cameră...** | Se autentifica pe un nod StratiGraph si aduce un sit intr-o camera (vezi mai jos) |

### Jurnalul de activitate

In partea de jos a panoului, un **jurnal de activitate** derulabil afiseaza intrari cu marca temporala ale activitatii recente, inclusiv schimbarile de stare, exporturile, validarile si tentativele de sincronizare.

<!-- IMAGINE: Panoul complet cu toate sectiunile adnotate -->
> **Fig. 3**: Panoul complet StratiGraph Sync cu toate sectiunile etichetate

---

## Exportul pachetelor

Exportul unui pachet impacheteaza datele arheologice locale intr-un format structurat pregatit pentru incarcarea in Knowledge Graph-ul StratiGraph.

### Export pas cu pas

1. Asigurati-va ca ati salvat toata munca curenta in PyArchInit
2. Deschideti panoul StratiGraph Sync (daca nu este deja vizibil)
3. Faceti clic pe butonul **Export pachet**
4. Sistemul efectueaza trei operatiuni automat:
   - **Export**: Datele locale sunt impachetate intr-un fisier pachet
   - **Validare**: Pachetul este verificat pentru completitudine si integritate a datelor
   - **Adaugare in coada**: Pachetul validat este adaugat in coada de sincronizare
5. Urmariti **indicatorul de stare** care parcurge: `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. **Jurnalul de activitate** inregistreaza fiecare pas cu marca temporala

### Ce este inclus intr-un pachet

Un pachet contine toate entitatile arheologice care au UUID-uri (vezi Tutorial 31 pentru detalii despre UUID). Fiecare entitate este identificata prin `entity_uuid`, asigurand ca aceeasi inregistrare este intotdeauna recunoscuta pe server.

<!-- IMAGINE: Butonul Export pachet si tranzitia de stare -->
> **Fig. 4**: Facand clic pe "Export pachet" si observand schimbarile de stare in panou

---

## Sincronizare

### Sincronizare automata

Cand sistemul detecteaza ca sunteti **online** (verificarea sanatatii reuseste), incarca automat toate pachetele in asteptare din coada. Nu este necesara interventie manuala.

Procesul de sincronizare automata:

1. Verificarea conectivitatii trece (punctul de verificare a sanatatii raspunde)
2. Indicatorul de conexiune trece la **Online**
3. Pachetele in asteptare din coada sunt incarcate unul cate unul
4. Pachetele incarcate cu succes sunt marcate ca `SYNC_SUCCESS`
5. **Marca temporala a ultimei sincronizari** si rezultatul sunt actualizate

### Sincronizare manuala

Daca doriti sa fortati o tentativa imediata de sincronizare:

1. Asigurati-va ca indicatorul de conexiune arata **Online**
2. Faceti clic pe butonul **Sincronizează acum**
3. Sistemul incearca imediat sa incarce toate pachetele in asteptare

Butonul **Sincronizează acum** este eficient doar cand sistemul este online.

### Reincercare automata cu intarziere exponentiala

Daca o incarcare esueaza, sistemul **nu renunta**. In schimb, reincearca automat cu intarzieri crescatoare:

| Tentativa | Intarziere |
|-----------|-----------|
| Prima reincercare | 30 secunde |
| A doua reincercare | 60 secunde |
| A treia reincercare | 120 secunde |
| A patra reincercare | 5 minute |
| A cincea reincercare | 15 minute |

Aceasta previne supraincarcarea serverului cand este temporar indisponibil, asigurand in acelasi timp livrarea eventuala.

<!-- IMAGINE: Butonul Sincronizeaza acum si indicatorul de conexiune -->
> **Fig. 5**: Butonul "Sincronizează acum" si indicatorul starii conexiunii

---

## Gestionarea cozii

Butonul **Coada...** deschide un dialog detaliat unde puteti inspecta toate pachetele din coada de sincronizare.

### Coloanele dialogului cozii

| Coloana | Descriere |
|---------|-----------|
| **ID** | Identificator unic al intrarii din coada |
| **Status** | Starea curenta a intrarii (in asteptare, se sincronizeaza, succes, esuat) |
| **Tentative** | Numarul de tentative de incarcare efectuate pana acum |
| **Creat** | Marca temporala cand pachetul a fost adaugat prima data in coada |
| **Ultima eroare** | Mesajul de eroare de la cea mai recenta tentativa esuata (gol daca nu exista erori) |
| **Calea pachetului** | Calea in sistemul de fisiere catre fisierul pachet |

### Interpretarea intrarilor din coada

- Intrarile **In asteptare** asteapta sa fie incarcate
- Intrarile **Succes** au fost incarcate si confirmate de server
- Intrarile **Esuat** vor fi reincercate automat; verificati coloana **Ultima eroare** pentru detalii
- Numarul de **Tentative** va ajuta sa intelegeti de cate ori sistemul a incercat sa incarce un anumit pachet

### Stocarea cozii

Baza de date a cozii este stocata ca fisier SQLite la:

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Acest fisier persista intre sesiunile QGIS, deci pachetele in asteptare nu se pierd daca inchideti QGIS.

<!-- IMAGINE: Dialogul cozii care afiseaza mai multe intrari -->
> **Fig. 6**: Dialogul de gestionare a cozii cu intrarile pachetelor

---

## Trimiterea unui sit intr-o camera StratiGraph

Incepand cu versiunea **5.14.0-alpha**, butonul **Trimite situl într-o cameră...** aduce un sit intr-o *camera* a unui nod StratiGraph (StratiGraph Server). Graful sitului devine continutul camerei, unde EMStudio, EM Tools si celelalte instrumente ale proiectului il vad si lucreaza cu el.

![Panoul StratiGraph Sync](images/32_stratigraph_sync/06_sync_panel_send_button.png)

> **Fig. 7**: Panoul StratiGraph Sync cu butonul **Trimite situl într-o cameră...**

### Procedura pas cu pas

1. In panoul **StratiGraph Sync**, apasati **Trimite situl într-o cameră...**
2. **Nod**: adresa nodului, de exemplu `https://nod.example.org/em`. Este retinuta intre sesiuni.
3. **Sit**: alegeti situl. **Id-ul camerei** si **Titlul camerei** se completeaza din numele sitului si pot fi modificate; id-ul camerei este un singur cuvant, fara spatii.
4. Apasati **Autentificare...**: pagina de autentificare a nodului se deschide in browser. Autentificati-va cu contul propriu si reveniti in QGIS: randul **Identitate** arata numele si daca puteti crea camere. Dacă nodul are un client Keycloak dedicat pyArchInit, numele lui se pune în setarea QGIS `pyArchInit/stratigraph/client_id`; altfel se folosește clientul indicat de nod.
5. Optional: **Doar plan** arata ce s-ar trimite fara sa scrie nimic pe nod.
6. Apasati **Trimite situl**: jurnalul arata nodurile si muchiile exportate si rezultatul.

![Fereastra Trimite situl intr-o camera](images/32_stratigraph_sync/07_send_site_dialog.png)

> **Fig. 8**: Fereastra dupa autentificare si trimiterea sitului de exemplu catre un nod de dezvoltare: 745 de operatii aplicate, 0 refuzate, baza de date pastrata ca referinta

### Ce se trimite

- Graful intregului sit, ca un singur graf chiar daca situl are mai multe sondaje: astfel relatiile dintre unitati din sondaje diferite calatoresc impreuna cu restul.
- Fisierele citate de graf sunt incarcate o singura data. Retrimiterea aceluiasi sit nu dubleaza nimic.
- **Fisierele de baza de date nu sunt incarcate niciodata** (sqlite, spatialite, gpkg): in camera ramane doar o referinta. Celelalte situri din baza de date raman pe calculatorul dumneavoastra.
- Parola nu trece niciodata prin pyArchInit: se scrie doar pe pagina nodului. Tokenul de acces ramane in memorie si se pierde la inchiderea ferestrei.

### Din linia de comanda

Aceeasi trimitere fara QGIS (fara `--dry-run` scrie efectiv; fara `--token` deschide browserul pentru autentificare):

```bash
python scripts/stratigraph_send_site.py --db ~/pyarchinit_5/pyarchinit_DB_folder/pyarchinit_db.sqlite \
    --site "Scavo archeologico" --node https://nodo.example.org/em --room scavo-2026 --dry-run
```

### Lucrul cu o camera care contine deja date

Cand in camera lucreaza si altii (EMStudio, StratiField, EM Tools), dupa autentificare:

1. **Compară cu camera** compara situl cu camera in ambele sensuri, fara sa scrie nimic: ce are nou camera pentru pyArchInit (unitati noi, definitii schimbate, relatii) si ce adauga pyArchInit in camera.
2. **Trimite modificările** trimite camerei munca făcută aici: unități și relații noi, câmpuri schimbate aici, relații eliminate aici. Ce s-a schimbat doar în cameră nu este atins; un câmp schimbat de ambele părți este un conflict și doar se afișează (vezi «Sincronizare cu memorie»).
3. **Adu din cameră** aduce camera in fisele pyArchInit (US, definitii, periodizare, relatii), recunoscand fiecare fisa dupa identificatorul ei. Daca pull-ul ar elimina relatii locale pe care camera nu le cunoaste, fereastra le enumera si cere confirmare.

Cu **Adu din cameră** se poate si reconstrui un sit intr-o baza de date care nu il are: unitatile revin cu numar, tip, definitii si periodizare. Unitatile de continuitate (CON) nu calatoresc: pyArchInit le regenereaza cu **Genera continuita**.

Camera primeste fisa US intreaga, nu doar campurile grafului: descriere, interpretare, culoare, consistenta, cote, dimensiuni, sondaj, incapere, carou, sector, campurile de zidarie (USM). O fisa reconstruita dintr-o camera este identica cu originalul; relatiile se schimba doar in scriere (cu zona si situl). O camera trimisa cu o versiune anterioara de pyArchInit are doar campurile grafului: comparatia arata multe campuri diferite; un nou **Trimite situl** o completeaza.

Toate acestea functioneaza atat cu SQLite cat si cu PostgreSQL. Pentru a reconstrui un sit ajunge o baza de date pyArchInit creata si goala, deschisa in pyArchInit: **Adu din cameră** o populeaza (sit, fise, periodizare, relatii, media). Relatiile au mereu patru elemente: tip, US, zona, sit.

![Comparatia cu camera](images/32_stratigraph_sync/08_compare_with_room.png)

> **Fig. 9**: Comparatia cu o camera in care s-a lucrat si in EMStudio: o US noua si o definitie revizuita in camera, o US noua din pyArchInit de trimis

### Fotografii si media in camera

Fotografiile, videoclipurile, modelele 3D si documentele legate de fisele US calatoresc cu situl, in ambele sensuri. Ortofotografiile si celelalte rastere raman deoparte: sunt straturi QGIS, nu media pyArchInit.

- **Trimite situl** si **Trimite modificările** incarca fiecare fisier in depozitul camerei o singura data: un fisier pe care camera il are deja (acelasi continut) nu se retrimite. Daca originalul nu mai este pe disc, se foloseste copia din folderul Resize.
- **Adu din cameră** descarca media noi in folderul `stratigraph_media/<camera>` din home-ul pyArchInit, creeaza miniatura si copia ca la incarcarea unui fisier din fisa si le leaga de US-ul lor, cu descriere si etichete. Un media pe care baza de date il are deja (recunoscut dupa identificator) nu se descarca din nou: se verifica doar legatura.
- Media pentru artefacte, ceramica, morminte si structuri raman deocamdata locale: fereastra le numara.

![O fotografie noua trimisa in camera](images/32_stratigraph_sync/09_room_media.png)

> **Fig. 10**: O fotografie adaugata la US 3 dupa trimiterea sitului: comparatia o gaseste si Trimite modificările incarca fisierul si legatura

### Sincronizare cu memorie

După prima **Adu din cameră** (sau prima **Trimite situl**) pyArchInit își amintește camera așa cum era în acel moment: *baza* comună, salvată în folderul `stratigraph_rooms` din home-ul pyArchInit, câte una pentru fiecare bază de date, sit și cameră. De atunci:

- comparația citește din cameră **doar noutățile** de la ultima sincronizare, nu tot documentul;
- fiecare diferență are un autor: **schimbat aici** (se trimite), **schimbat în cameră** (o aduce aducerea), **schimbat de ambele părți** (conflict, afișat cu ambele valori), **eliminat în cameră** (se elimină și aici), **eliminat aici** (se trimite);
- **Adu din cameră** nu suprascrie niciodată în tăcere munca încă netrimisă: dacă există modificări locale, conflicte, relații eliminate aici, fereastra le enumeră și recomandă trimiterea lor mai întâi. Într-un conflict confirmat câștigă valoarea camerei.
- câmpurile pe care pyArchInit le **calculează** (ordinea stratigrafică, codul perioadei, datarea) nu sunt niciodată modificări sau conflicte: la sfârșitul aducerii pyArchInit le recalculează singur, ca butoanele fișei US;
- **relațiile sunt o mulțime**: cele adăugate aici și încă netrimise rămân după aducere, împreună cu cele adăugate de alții în cameră;
- dacă confirmați o aducere care înlocuiește valori locale, acele valori **nu se pierd**: **Restaurează valorile înlocuite** le pune la loc, și redevin modificări de trimis.

Unitățile pe care aducerea le lasă deoparte intenționat (continuitățile CON generate și media lor) rămân în cameră și nu contează ca eliminări. Funcționează la fel cu SQLite și PostgreSQL.

![Comparație în trei căi](images/32_stratigraph_sync/10_three_way_compare.png)

> **Fig. 11**: Comparația după o sincronizare: un câmp schimbat aici de trimis, unul schimbat în cameră de adus, un conflict pe același câmp

### Geometrii: sit, sondaje, zone și tăieturi

Odată cu situl călătoresc și desenele straturilor GIS din pyArchInit, ca amprente în propriul sistem de referință: poligonul **sitului** (`pyarchinit_siti_polygonal`), **sondajele** (`pyarchinit_sondaggi`), **zonele și sectoarele** (`pyarchinit_ripartizioni_spaziali`) și **tăieturile**, adică US negative (`pyunitastratigrafiche`). Pleacă din SQLite și din PostGIS.

**Adu din cameră** le scrie înapoi în straturi, SpatiaLite sau PostGIS, în sistemul de referință al stratului: un element care lipsește este adăugat, unul identic nu este atins, iar un element **desenat altfel aici rămâne cum este** și este semnalat: aducerea nu suprascrie niciodată un desen local.

Poligoanele US pozitive nu călătoresc: pentru Extended Matrix geometria lor este modelul 3D. Ortofotografiile și rasterele rămân în QGIS.

### Probleme frecvente

| Mesaj | Ce trebuie facut |
|-------|------------------|
| `401` sau autentificare expirata | Sesiunea se reinnoieste singura in timpul lucrului; daca a expirat complet (multe ore nefolosita) apasati din nou **Autentificare...** |
| ⚠ «Numărul … aparține mai multor unități» | În aceeași zonă două unități au același număr și tip diferit: relațiile indică unitatea doar prin număr, zonă și sit, deci în cameră ajung la ambele. Renumerotați una dintre ele înainte de trimitere |
| `403` / *may create rooms: False* | Contul nu are un rol in camera sau nu poate crea camere: intrebati administratorul nodului |
| `CERTIFICATE_VERIFY_FAILED` | Nodul foloseste un certificat local (nod de dezvoltare sau de teren): instalati-i autoritatea de certificare pe calculator, sau folositi `--ca-file` in linia de comanda |
| `409 ... already declared` | Camera exista si apartine altui utilizator: alegeti alt id |

---

## Configurare

### URL-ul de verificare a sanatatii

Sistemul utilizeaza un URL de verificare a sanatatii pentru a determina conectivitatea la serverul StratiGraph. Puteti configura acest lucru in setarile QGIS:

| Setare | Cheie | Implicit |
|--------|-------|---------|
| URL verificare sanatate | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Pentru a schimba URL-ul de verificare a sanatatii:

1. Deschideti **QGIS** -> **Setari** -> **Optiuni** (sau utilizati consola Python QGIS)
2. Navigati la setarile PyArchInit sau setati prin:

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://serverul-dvs.exemplu.com/health")
```

### Intervalul de verificare

Intervalul implicit de verificare a conectivitatii este de **30 de secunde**. Acesta poate fi configurat si prin QgsSettings.

---

## Depanare

### Panoul nu apare

- Asigurati-va ca utilizati PyArchInit versiunea **5.0.2-alpha** sau ulterioara
- Verificati ca butonul StratiGraph Sync din bara de instrumente este vizibil
- Incercati sa comutati butonul intre oprit si pornit
- Verificati **Vizualizare** -> **Panouri** in QGIS pentru a vedea daca widget-ul dock este listat

### Indicatorul de conexiune arata intotdeauna "Offline"

- Verificati ca serverul StratiGraph este pornit si accesibil
- Verificati URL-ul de verificare a sanatatii in setari (implicit: `http://localhost:8080/health`)
- Testati URL-ul manual intr-un browser sau cu `curl`:

```bash
curl http://localhost:8080/health
```

- Daca serverul este pe o alta masina, asigurati-va ca nu exista reguli de firewall care blocheaza conexiunea

### Exportul pachetului esueaza

- Asigurati-va ca baza de date este conectata si accesibila
- Verificati ca inregistrarile dumneavoastra au UUID-uri valide (Tutorial 31)
- Verificati jurnalul de activitate pentru mesaje de eroare specifice
- Asigurati-va ca exista suficient spatiu pe disc pentru fisierul pachet

### Sincronizarea esueaza repetat

- Verificati coloana **Ultima eroare** in dialogul Cozii pentru detalii
- Cauze comune:
  - Serverul este temporar indisponibil (sistemul va reincerca automat)
  - Probleme de conectivitate la retea
  - Serverul a respins pachetul (verificati jurnalele serverului)
- Daca un pachet esueaza constant dupa multe tentative, luati in considerare re-exportarea acestuia

### Probleme cu baza de date a cozii

- Baza de date a cozii se afla la `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Daca este corupta, o puteti sterge in siguranta -- pachetele in asteptare se vor pierde, dar le puteti re-exporta
- Faceti o copie de siguranta a acestui fisier daca trebuie sa pastrati starea cozii

---

## Intrebari frecvente

### Am nevoie de internet pentru a utiliza PyArchInit?

**Nu.** PyArchInit este complet functional offline. Panoul StratiGraph Sync gestioneaza doar sincronizarea cu serverul StratiGraph. Puteti lucra complet offline si exporta/sincroniza cand sunteti pregatit.

### Ce se intampla daca inchid QGIS cu pachete in asteptare?

Pachetele in asteptare sunt salvate in baza de date a cozii si vor fi disponibile cand reporniti QGIS. Sistemul va relua sincronizarea automat cand conectivitatea este restabilita.

### Pot exporta mai multe pachete?

Da. De fiecare data cand faceti clic pe "Export pachet", un nou pachet este creat si adaugat in coada. Mai multe pachete pot fi in coada si vor fi incarcate secvential.

### Cum stiu daca datele mele au fost sincronizate?

Verificati indicatorul **ultima sincronizare** din panou pentru cel mai recent rezultat. Puteti deschide si dialogul **Coada...** pentru a vedea starea fiecarui pachet individual.

### StratiGraph Sync functioneaza atat cu PostgreSQL cat si cu SQLite?

Da. Sistemul de sincronizare functioneaza cu ambele backend-uri de baze de date suportate de PyArchInit. Pachetele sunt exportate intr-un format independent de baza de date.

### Care este relatia dintre UUID-uri si sincronizare?

UUID-urile (Tutorial 31) furnizeaza identificatorii stabili care fac posibila sincronizarea. Fiecare entitate dintr-un pachet este identificata prin UUID-ul sau, permitand serverului sa potriveasca, creeze sau actualizeze corect inregistrarile.

---

*Documentatie PyArchInit - StratiGraph Sync*
*Versiune: 5.0.2-alpha*
*Ultima actualizare: februarie 2026*

---

## Animatie interactiva

Explorati animatia interactiva pentru a afla mai multe despre acest subiect.

[Deschideti animatia interactiva](../../animations/stratigraph_sync_animation.html)
