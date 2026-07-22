# Tutorial 38 : Importer depuis QField (GPKG)

## Introduction

La fonction **Importer depuis QField (GPKG)** intègre dans pyArchInit les
données relevées sur le terrain avec **QField** au moyen de l'extension associée
**pyarchinit-qfield**. La commande lit les GeoPackages (`.gpkg`) du projet QField
et les photos prises sur le terrain, puis **ajoute** les enregistrements à la
base de données de pyArchInit sans dupliquer les US et le mobilier déjà présents :
pour les enregistrements existants, elle remplit **uniquement les champs vides**,
sans jamais écraser les valeurs déjà saisies.

Le déroulement est conçu pour être **sûr** : on exécute d'abord un **Aperçu
(simulation)** qui simule tout sans rien écrire, puis — seulement après
confirmation — on lance l'**Import** réel en une seule transaction.

> Prérequis : les données doivent avoir été relevées sur le terrain avec
> **QField** à l'aide de l'extension associée **pyarchinit-qfield**.

---

## 1. Prérequis

- Données relevées sur le terrain avec **QField** au moyen de l'extension
  **pyarchinit-qfield**.
- Le dossier du projet QField contient les fichiers **`.gpkg`** et les photos
  sous **`DCIM/pyarchinit`**.
- Une base de données pyArchInit configurée (SQLite/Spatialite ou
  PostgreSQL/PostGIS) : la BD est **résolue automatiquement** à partir de la
  configuration de l'extension.

---

## 2. Ouvrir la boîte de dialogue

La commande est accessible de **deux façons** :

1. **Menu** : **Plugin → pyArchInit - Archaeological GIS Tools → Importa da
   QField (GPKG)**.
2. **Barre d'outils** (nouveau) : dans la barre d'outils de pyArchInit, ouvrez
   le **bouton déroulant des outils d'analyse** — le même qui regroupe
   GeoArchaeo, MoveCost, Palimpsest et d'autres outils — puis choisissez
   **Importa da QField (GPKG)**. L'entrée se repère grâce à sa **nouvelle icône
   dédiée** : une tuile verte arrondie de style QField avec un repère blanc qui
   descend dans un bac d'importation.

Dans les deux cas, la boîte de dialogue *Importer depuis QField* s'ouvre : QGIS
**ne se bloque pas** pendant l'opération car la copie des photos et l'accès
WebDAV s'exécutent dans un fil d'exécution séparé.

---

## 3. Sélectionner le dossier du projet QField

1. Cliquez sur **Parcourir…** et choisissez le **dossier du projet QField**.
2. La boîte de dialogue **analyse les GeoPackages** et remplit automatiquement la
   liste déroulante **Site** avec les sites trouvés.
3. Choisissez un site précis ou laissez **Tous les sites** pour tout importer.

---

## 4. Options d'importation

| Option | Signification |
|---|---|
| **SRID (vide = du GPKG)** | système de référence ; laissez vide pour le lire depuis le GeoPackage |
| **Destination des photos** | pré-remplie avec le dossier média configuré (local ou WebDAV) |
| **Dédupliquer les géométries** | évite de réinsérer des géométries identiques déjà présentes |
| **Copier les photos** | copie les photos vers le backend média |
| **Générer les miniatures** | crée automatiquement les vignettes des photos |

Les trois cases sont **cochées par défaut**.

---

## 5. Aperçu (simulation)

Cliquez sur **Aperçu (simulation)** : la totalité de l'import est exécutée en
**simulation**, **sans rien écrire** dans la base de données. Le journal indique :

- combien d'**US**, de **mobiliers**, de **géométries**, de **points de cote**,
  de **photos** et de **liens** seraient importés ;
- exactement **quels champs vides** des enregistrements existants seraient
  remplis.

C'est l'étape à toujours utiliser pour vérifier le résultat avant d'écrire.

---

## 6. Importer

Cliquez sur **Importer** (une **confirmation** est demandée). L'opération :

- **ajoute** les enregistrements en **une seule transaction** ;
- **ne duplique pas** les US et le mobilier existants : elle remplit
  **uniquement leurs champs vides**, sans jamais écraser les valeurs déjà
  présentes ;
- **copie les photos** vers le backend média et **génère automatiquement leurs
  vignettes** ;
- attribue aux enregistrements importés un **`node_uuid`** et les marque avec
  **`created_by = 'qfield_import'`**.

---

## 7. Après l'importation

Vérifiez les **relations stratigraphiques** des US importées : elles ne sont
**pas déduites automatiquement** et doivent être complétées à la main dans la
fiche US.

---

## 8. Alternative en ligne de commande (CLI)

Pour un usage avancé ou sans interface, un script CLI est disponible. La
**simulation est le comportement par défaut** ; ajoutez `--apply` pour écrire
réellement :

```bash
# Aperçu (simulation, par défaut)
python3 scripts/import_qfield.py --qfield-dir <dossier>

# Import réel
python3 scripts/import_qfield.py --qfield-dir <dossier> --apply
```

---

*Documentation PyArchInit — Juillet 2026*
