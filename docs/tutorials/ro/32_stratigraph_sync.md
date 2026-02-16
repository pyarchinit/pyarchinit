# PyArchInit - StratiGraph: Panoul de sincronizare

## Cuprins
1. [Introducere](#introducere)
2. [Accesarea panoului](#accesarea-panoului)
3. [Intelegerea interfetei](#intelegerea-interfetei)
4. [Exportul pachetelor](#exportul-pachetelor)
5. [Sincronizare](#sincronizare)
6. [Gestionarea cozii](#gestionarea-cozii)
7. [Configurare](#configurare)
8. [Depanare](#depanare)
9. [Intrebari frecvente](#intrebari-frecvente)

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
| **Sincronizeaza acum** | Forteaza o tentativa imediata de sincronizare (disponibil doar cand este online) |
| **Coada...** | Deschide dialogul de gestionare a cozii care afiseaza toate intrarile |

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
2. Faceti clic pe butonul **Sincronizeaza acum**
3. Sistemul incearca imediat sa incarce toate pachetele in asteptare

Butonul **Sincronizeaza acum** este eficient doar cand sistemul este online.

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
> **Fig. 5**: Butonul "Sincronizeaza acum" si indicatorul starii conexiunii

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
