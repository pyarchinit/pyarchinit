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

Bara de meniu **pyArchInit → Import din QField (GPKG)**.

Se deschide dialogul *Import din QField*: QGIS **nu se blochează** în timpul
operației, deoarece copierea fotografiilor și accesul WebDAV rulează într-un fir
separat.

---

## 3. Selectarea folderului proiectului QField

1. Apasă **Răsfoiește…** și alege **folderul proiectului QField**.
2. Dialogul **scanează GeoPackage-urile** și completează automat lista derulantă
   **Sit** cu siturile găsite.
3. Alege un sit anume sau lasă **Toate siturile** pentru a importa tot.

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
efectiv:

```bash
# Previzualizare (simulare, implicit)
python3 scripts/import_qfield.py --qfield-dir <folder>

# Import real
python3 scripts/import_qfield.py --qfield-dir <folder> --apply
```

---

*Documentație PyArchInit — Iulie 2026*
