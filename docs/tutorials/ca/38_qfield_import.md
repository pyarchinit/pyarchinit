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

Barra de menú **pyArchInit → Importar des de QField (GPKG)**.

S'obre el diàleg *Importar des de QField*: QGIS **no es bloqueja** durant
l'operació perquè la còpia de fotos i l'accés a WebDAV s'executen en un fil
separat.

---

## 3. Seleccionar la carpeta del projecte QField

1. Prem **Navega…** i tria la **carpeta del projecte QField**.
2. El diàleg **escaneja els GeoPackages** i omple automàticament el desplegable
   **Lloc** amb els llocs trobats.
3. Tria un lloc concret o deixa **Tots els llocs** per importar-ho tot.

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
realment:

```bash
# Previsualització (simulació, per defecte)
python3 scripts/import_qfield.py --qfield-dir <carpeta>

# Importació real
python3 scripts/import_qfield.py --qfield-dir <carpeta> --apply
```

---

*Documentació PyArchInit — Juliol 2026*
