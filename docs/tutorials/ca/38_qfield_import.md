# Tutorial 38: Importar des de QField (GPKG)

## Introducció

La funció **Importar des de QField (GPKG)** incorpora a pyArchInit les dades
recollides al camp amb **QField** mitjançant el complement associat
**pyarchinit-qfield**. L'ordre llegeix els GeoPackages (`.gpkg`) del projecte
QField i les fotografies preses al camp, i **afegeix** els registres a la base de
dades de pyArchInit sense duplicar les UE i els materials ja existents: dels
registres existents omple **només els camps buits**, sense sobreescriure mai els
valors ja presents.

El flux està pensat per ser **segur**: primer s'executa una **Previsualització
(simulació)** que ho simula tot sense escriure res, i després —només després de
confirmar— es llança la **Importació** real en una única transacció.

> Requisit: les dades s'han d'haver recollit al camp amb **QField** utilitzant el
> complement associat **pyarchinit-qfield**.

---

## 1. Requisits previs

- Dades recollides al camp amb **QField** mitjançant el complement
  **pyarchinit-qfield**.
- La carpeta del projecte QField conté els fitxers **`.gpkg`** i les fotos sota
  **`DCIM/pyarchinit`**.
- Una base de dades pyArchInit configurada (SQLite/Spatialite o
  PostgreSQL/PostGIS): la BD es **resol automàticament** des de la configuració
  del complement.

---

## 2. Obrir el diàleg

L'ordre es pot obrir de **dues maneres**:

1. **Menú**: **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Barra d'eines** (novetat): a la barra d'eines de pyArchInit, obre el
   **botó desplegable de les eines d'anàlisi** — el mateix que agrupa
   GeoArchaeo, MoveCost, Palimpsest i altres eines — i tria **Importa da
   QField (GPKG)**. L'entrada es reconeix per la **nova icona dedicada**: una
   rajola verda arrodonida d'estil QField amb un marcador blanc que baixa cap a
   una safata d'importació.

En tots dos casos s'obre el diàleg *Importar des de QField*: QGIS **no es
bloqueja** durant l'operació perquè la còpia de fotos i l'accés a WebDAV
s'executen en un fil separat.

---

## 3. Seleccionar la font: carpeta o arxiu ZIP

1. Prem **Navega…** i tria la **carpeta del projecte QField**, o prem
   **Arxiu ZIP…** i tria un arxiu **`.zip`** del projecte QField (el
   selector de fitxers filtra per `*.zip`). En ambdós casos, el camí triat
   apareix al mateix camp d'origen.
2. Si tries una carpeta, el diàleg **escaneja els GeoPackages** i omple
   automàticament el desplegable **Lloc** amb els llocs trobats.
3. Si tries un arxiu ZIP, s'**extreu automàticament** a una carpeta temporal
   i el desplegable **Lloc** torna a **Tots els llocs** (no es fa cap
   escaneig previ de llocs des d'un zip): la importació (Previsualització/
   simulació o Importa, fotos i miniatures incloses) s'executa sobre l'arbre
   extret, i la carpeta temporal s'**elimina automàticament** en acabar
   l'operació, fins i tot en cas d'error.
4. Tria un lloc concret o deixa **Tots els llocs** per importar-ho tot.

> Mentre una importació és en curs, tant **Navega…** com **Arxiu ZIP…**
> estan **desactivats**, com la resta de controls del diàleg.

> Si l'arxiu triat és **corrupte o no vàlid**, es mostra un error clar:
> **«Archivio ZIP non valido o corrotto: …»**. Si el zip no conté cap
> fitxer **`.gpkg`**, es mostra en el seu lloc l'error habitual de «no
> s'han trobat capes».

---

## 4. Opcions d'importació

| Opció | Significat |
|---|---|
| **SRID (buit = del GPKG)** | sistema de referència; deixa-ho buit per llegir-lo del GeoPackage |
| **Destinació de fotos** | precarregada amb la carpeta de mitjans configurada (local o WebDAV) |
| **Dedueix geometries** | evita reinserir geometries idèntiques ja presents |
| **Copia fotos** | copia les fotos al backend de mitjans |
| **Genera miniatures** | crea automàticament les miniatures de les fotos |

Les tres caselles estan **activades per defecte**.

---

## 5. Previsualització (simulació)

Prem **Previsualització (simulació)**: tota la importació s'executa en
**simulació**, **sense escriure res** a la base de dades. El registre mostra:

- quantes **UE**, **materials**, **geometries**, **punts de cota**, **fotos** i
  **enllaços** s'importarien;
- exactament **quins camps buits** dels registres existents s'omplirien.

És el pas que s'ha d'utilitzar sempre per comprovar el resultat abans d'escriure.

---

## 6. Importar

Prem **Importa** (es demana una **confirmació**). L'operació:

- **afegeix** els registres en **una única transacció**;
- **no duplica** les UE i els materials existents: omple **només els seus camps
  buits**, sense sobreescriure mai els valors ja presents;
- **copia les fotos** al backend de mitjans i **en genera les miniatures**
  automàticament;
- assigna als registres importats un **`node_uuid`** i els marca amb
  **`created_by = 'qfield_import'`**.

---

## 7. Després de la importació

Comprova les **relacions estratigràfiques** de les UE importades: **no es
dedueixen automàticament** i s'han de completar a mà a la fitxa UE.

---

## 8. Alternativa per línia d'ordres (CLI)

Per a usos avançats o sense interfície hi ha un script CLI disponible. La
**simulació és el comportament per defecte**; afegeix `--apply` per escriure
realment. El paràmetre `--qfield-dir` accepta tant la **carpeta del
projecte** com un arxiu **`.zip`**: si apunta a un zip, s'extreu
automàticament a una carpeta temporal, que s'elimina en acabar l'execució.
Un origen inexistent atura l'script amb l'error **«Sorgente non trovata
(cartella o archivio .zip): …»**.

```bash
# Previsualització (simulació, per defecte) des d'una carpeta
python3 scripts/import_qfield.py --qfield-dir <carpeta>

# Previsualització (simulació, per defecte) des d'un arxiu ZIP
python3 scripts/import_qfield.py --qfield-dir <arxiu.zip>

# Importació real
python3 scripts/import_qfield.py --qfield-dir <carpeta> --apply
```

---

*Documentació PyArchInit — Juliol 2026*
