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

## 3. Sélectionner la source : dossier ou archive ZIP

1. Cliquez sur **Parcourir…** et choisissez le **dossier du projet QField**,
   ou cliquez sur **Archive ZIP…** et choisissez une archive **`.zip`** du
   projet QField (le sélecteur de fichiers filtre sur `*.zip`). Dans les deux
   cas, le chemin choisi apparaît dans le même champ source.
2. Si vous choisissez un dossier, la boîte de dialogue **analyse les
   GeoPackages** et remplit automatiquement la liste déroulante **Site** avec
   les sites trouvés.
3. Si vous choisissez une archive ZIP, celle-ci est **extraite
   automatiquement** dans un dossier temporaire et la liste déroulante
   **Site** revient à **Tous les sites** (aucune pré-analyse des sites n'est
   effectuée depuis une archive zip) : l'import (Aperçu/simulation ou Import,
   photos et vignettes incluses) s'exécute sur l'arborescence extraite, et le
   dossier temporaire est **automatiquement supprimé** à la fin de
   l'opération, même en cas d'erreur.
4. Choisissez un site précis ou laissez **Tous les sites** pour tout importer.

> Pendant qu'un import est en cours, **Parcourir…** et **Archive ZIP…** sont
> tous deux **désactivés**, comme tous les autres contrôles de la boîte de
> dialogue.

> Si l'archive choisie est **corrompue ou invalide**, un message d'erreur
> clair s'affiche : **« Archivio ZIP non valido o corrotto : … »**. Si
> l'archive ne contient aucun fichier **`.gpkg`**, l'erreur habituelle
> « aucune couche trouvée » s'affiche à la place.

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
réellement. Le paramètre `--qfield-dir` accepte aussi bien le **dossier du
projet** qu'une archive **`.zip`** : s'il pointe vers une archive zip, celle-ci
est extraite automatiquement dans un dossier temporaire, supprimé à la fin de
l'exécution. Une source inexistante interrompt le script avec l'erreur
**« Sorgente non trovata (cartella o archivio .zip) : … »**.

```bash
# Aperçu (simulation, par défaut) depuis un dossier
python3 scripts/import_qfield.py --qfield-dir <dossier>

# Aperçu (simulation, par défaut) depuis une archive ZIP
python3 scripts/import_qfield.py --qfield-dir <archive.zip>

# Import réel
python3 scripts/import_qfield.py --qfield-dir <dossier> --apply
```

---

*Documentation PyArchInit — Juillet 2026*
