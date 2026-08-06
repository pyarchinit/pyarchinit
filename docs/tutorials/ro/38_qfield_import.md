# Tutorial 38: Import din QField (GPKG)

## Introducere

Funcția **Import din QField (GPKG)** aduce în pyArchInit datele culese pe teren
cu **QField** prin intermediul pluginului asociat **pyarchinit-qfield**. Comanda
citește GeoPackage-urile (`.gpkg`) ale proiectului QField și fotografiile făcute
pe teren și **adaugă** înregistrările în baza de date pyArchInit fără a duplica
US-urile și materialele deja existente: pentru înregistrările existente completează
**doar câmpurile goale**, fără a suprascrie niciodată valorile deja introduse.

Fluxul este conceput să fie **sigur**: mai întâi se rulează o **Previzualizare
(simulare)** care simulează totul fără a scrie nimic, iar apoi — numai după
confirmare — se lansează **Importul** real într-o singură tranzacție.

> Cerință prealabilă: datele trebuie să fi fost culese pe teren cu **QField**
> folosind pluginul asociat **pyarchinit-qfield**.

---

## 1. Cerințe prealabile

- Date culese pe teren cu **QField** prin pluginul **pyarchinit-qfield**.
- Folderul proiectului QField conține fișierele **`.gpkg`** și fotografiile în
  **`DCIM/pyarchinit`**.
- O bază de date pyArchInit configurată (SQLite/Spatialite sau
  PostgreSQL/PostGIS): baza de date este **rezolvată automat** din configurația
  pluginului.

---

## 2. Deschiderea dialogului

Comanda poate fi deschisă în **două moduri**:

1. **Meniu**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Bară de instrumente** (noutate): în bara de instrumente pyArchInit,
   deschide **butonul derulant al instrumentelor de analiză** — același care
   găzduiește GeoArchaeo, MoveCost, Palimpsest și alte instrumente — și alege
   **Importa da QField (GPKG)**. Intrarea se recunoaște după **noua pictogramă
   dedicată**: o plăcuță verde rotunjită în stil QField, cu un marcator alb
   care coboară într-o tavă de import.

În ambele cazuri se deschide dialogul *Import din QField*: QGIS **nu se
blochează** în timpul operației, deoarece copierea fotografiilor și accesul
WebDAV rulează într-un fir separat.

---

## 3. Selectarea sursei: folder sau arhivă ZIP

1. Apasă **Răsfoiește…** și alege **folderul proiectului QField**, sau apasă
   **Arhivă ZIP…** și alege o arhivă **`.zip`** a proiectului QField
   (selectorul de fișiere filtrează după `*.zip`). În ambele cazuri, calea
   aleasă apare în același câmp de sursă.
2. Dacă alegi un folder, dialogul **scanează GeoPackage-urile** și
   completează automat lista derulantă **Sit** cu siturile găsite.
3. Dacă alegi o arhivă ZIP, aceasta este **extrasă automat** într-un folder
   temporar, iar lista derulantă **Sit** revine la **Toate siturile** (nu se
   face nicio prescanare a siturilor dintr-o arhivă zip): importul
   (Previzualizare/simulare sau Import, inclusiv fotografii și miniaturi)
   rulează pe arborele extras, iar folderul temporar este **eliminat
   automat** la finalul operațiunii, chiar și în caz de eroare.
4. Alege un sit anume sau lasă **Toate siturile** pentru a importa tot.

> Cât timp un import este în curs, atât **Răsfoiește…**, cât și
> **Arhivă ZIP…** sunt **dezactivate**, la fel ca toate celelalte controale
> din dialog.

> Dacă arhiva aleasă este **coruptă sau nevalidă**, se afișează o eroare
> clară: **„Archivio ZIP non valido o corrotto: …”**. Dacă arhiva zip nu
> conține niciun fișier **`.gpkg`**, se afișează în schimb eroarea obișnuită
> „nu s-au găsit straturi”.

---

## 4. Opțiuni de import

| Opțiune | Semnificație |
|---|---|
| **SRID (gol = din GPKG)** | sistemul de referință; lasă gol pentru a-l citi din GeoPackage |
| **Destinație foto** | precompletată cu folderul media configurat (local sau WebDAV) |
| **Deduplică geometriile** | evită reintroducerea geometriilor identice deja prezente |
| **Copiază fotografiile** | copiază fotografiile în backendul media |
| **Generează miniaturi** | creează automat miniaturile fotografiilor |

Cele trei casete sunt **activate implicit**.

---

## 5. Previzualizare (simulare)

Apasă **Previzualizare (simulare)**: întregul import rulează în **simulare**,
**fără a scrie nimic** în baza de date. Jurnalul arată:

- câte **US**, **materiale**, **geometrii**, **puncte de cotă**, **fotografii** și
  **legături** ar fi importate;
- exact **ce câmpuri goale** ale înregistrărilor existente ar fi completate.

Este pasul care trebuie folosit întotdeauna pentru a verifica rezultatul înainte
de a scrie.

---

## 6. Import

Apasă **Importă** (se solicită o **confirmare**). Operația:

- **adaugă** înregistrările într-o **singură tranzacție**;
- **nu duplică** US-urile și materialele existente: completează **doar câmpurile
  lor goale**, fără a suprascrie niciodată valorile deja prezente;
- **copiază fotografiile** în backendul media și **le generează miniaturile**
  automat;
- atribuie înregistrărilor importate un **`node_uuid`** și le marchează cu
  **`created_by = 'qfield_import'`**.

---

## 7. După import

Verifică **relațiile stratigrafice** ale US-urilor importate: **nu sunt deduse
automat** și trebuie completate manual în fișa US.

---

## 8. Alternativă din linia de comandă (CLI)

Pentru utilizări avansate sau fără interfață este disponibil un script CLI.
**Simularea este comportamentul implicit**; adaugă `--apply` pentru a scrie
efectiv. Parametrul `--qfield-dir` acceptă atât **folderul proiectului**, cât
și o arhivă **`.zip`**: dacă indică o arhivă zip, aceasta este extrasă automat
într-un folder temporar, care este eliminat la finalul rulării. O sursă
inexistentă oprește scriptul cu eroarea **„Sorgente non trovata (cartella o
archivio .zip): …”**.

```bash
# Previzualizare (simulare, implicit) dintr-un folder
python3 scripts/import_qfield.py --qfield-dir <folder>

# Previzualizare (simulare, implicit) dintr-o arhivă ZIP
python3 scripts/import_qfield.py --qfield-dir <arhiva.zip>

# Import real
python3 scripts/import_qfield.py --qfield-dir <folder> --apply
```

---

*Documentație PyArchInit — Iulie 2026*
