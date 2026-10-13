# Tutorial 25 : Time Manager (Contrôleur Temporel SIG)

## Introduction

Le **Time Manager** (Contrôleur Temporel SIG) est un outil avancé pour visualiser la séquence stratigraphique dans le temps. Il permet de "naviguer" à travers les niveaux stratigraphiques en utilisant un contrôle temporel, visualisant progressivement les US de la plus ancienne à la plus récente (la formation du site).

### Fonctionnalités Principales

- Visualisation progressive des niveaux stratigraphiques
- Contrôle via molette/curseur
- Mode cumulatif ou niveau unique
- Impression automatique des planches de l'atlas, une par niveau
- Intégration avec la Matrice de Harris

## Accès

### Depuis le Menu
**PyArchInit** → **Time Manager**

### Prérequis

- Couche avec champ `order_layer` (index stratigraphique)
- US avec order_layer rempli
- Couches chargées dans QGIS

## Interface

### Panneau Principal

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Couches disponibles :                             |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] autre_couche                                 |
+--------------------------------------------------+
|              [Molette Circulaire]                |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Niveau : [SpinBox : 0-N]                |
+--------------------------------------------------+
| [ ] Mode Cumulatif (affiche <= niveau)          |
+--------------------------------------------------+
| [ ] Afficher la matrice                          |
| [Atlas Impression Tableaux par Période]          |
| [Arrêter le processus d'impression]              |
+--------------------------------------------------+
| [Aperçu Matrice/Image]                           |
+--------------------------------------------------+
```

### Contrôles

| Contrôle | Fonction |
|----------|----------|
| Onglets (en haut) | **Système de chronologie relative** (liste des couches, molette et niveau) et **Système de chronologie absolue** (recherche par années, voir « Chronologie absolue ») |
| Case à cocher Couche | Sélectionne les couches à contrôler |
| Molette | Navigation entre les niveaux (rotation) |
| SpinBox | Saisie directe du niveau |
| Mode Cumulatif | Affiche tous les niveaux jusqu'au sélectionné |
| Afficher la matrice | Visualise la Matrice de Harris synchronisée |

## Champ order_layer

### Qu'est-ce que order_layer ?

Le champ `order_layer` définit l'ordre stratigraphique de visualisation :
- **0** = Niveau le plus ancien (profond)
- **N** = Niveau le plus récent (superficiel)

C'est la convention du bouton **Ordre stratigraphique** avec la case "Ordre : Ancien → Récent" cochée (réglage par défaut, voir Tutorial 03) : si l'ordre a été calculé à l'envers, le Time Manager et la carte affichent la séquence inversée.

### Remplissage de order_layer

Dans la Fiche US, onglet **Help** → **Tool Box**, le bouton **Ordre stratigraphique** calcule `order_layer` à partir des relations stratigraphiques (voir Tutorial 03) ; la valeur de l'US courante apparaît dans le champ sous le bouton. Règles :
1. 0 aux US les plus anciennes, valeurs croissantes vers les plus récentes (en surface)
2. Les US contemporaines peuvent avoir la même valeur
3. Suivre la séquence de la Matrice

### Exemple

| US | order_layer | Description |
|----|-------------|-------------|
| US001 | 4 | Humus superficiel |
| US002 | 3 | Couche de labour |
| US003 | 2 | Effondrement |
| US004 | 1 | Sol d'occupation |
| US005 | 0 | Fondation |

Depuis la 5.13.19-alpha, les couches US et USM que pyArchInit charge sur la carte (voir Tutorial 14, *Choix du Style*) sont dessinées dans le même ordre que celui du Time Manager : selon la chronologie de la période, puis selon `order_layer` (0 = la plus ancienne), de sorte que les unités les plus récentes sont au-dessus.

## Modes de Visualisation

### Mode Niveau Unique

Case à cocher **NON** active :
- Affiche UNIQUEMENT les US du niveau sélectionné
- Utile pour isoler des couches individuelles
- Visualisation "en tranches"

### Mode Cumulatif

Case à cocher **ACTIVE** :
- Affiche toutes les US du niveau 0 (le plus ancien) au niveau sélectionné
- Montre la formation du site, des US les plus anciennes aux plus récentes
- Visualisation plus réaliste

### Chronologie absolue

Le second onglet de la fenêtre, **Système de chronologie absolue**, travaille sur des années plutôt que sur les niveaux de `order_layer` : on choisit un intervalle de temps et on charge sur la carte les US des périodes qui chevauchent cet intervalle. Il faut que la Périodisation soit remplie (voir Tutorial 04), avec la **Chronologie initiale** et la **Chronologie finale** de chaque période et phase : une période sans années n'est pas trouvée.

**Contrôles.**

- **Histoire initiale** (l'année de début) et **Chronologie finale** (l'année de fin) : deux champs numériques, qui se lisent « Affiche l'intervalle de temps entre l'année : … et l'année … ». Les années vont de `-4 000 000` à `2100` : les valeurs négatives sont av. J.-C. (268 av. J.-C. = `-268`), les positives apr. J.-C. sans signe (1400 apr. J.-C. = `1400`). L'année la plus ancienne va dans le premier champ.
- Bouton **Voir** : lance la recherche.

**Ce que fait le bouton Voir.**

1. Il cherche dans la Périodisation (de tous les sites de la base de données) les périodes et les phases dont la datation **chevauche** l'intervalle, c'est-à-dire qui ne finissent pas avant l'année initiale et ne commencent pas après l'année finale. S'il n'en trouve aucune, il avertit « There are no Periods in this time interval » (le message s'affiche en anglais) et s'arrête.
2. Il prend les US dont la période initiale et la phase initiale correspondent à celles trouvées. S'il n'y en a aucune, il avertit « There are no geometries to display » (en anglais aussi).
3. Il charge les couches de ces US sur la carte, avec le même mécanisme de chargement que la fiche US (voir Tutorial 03).
4. Il met à jour l'aperçu de la Matrice, si **Afficher la matrice** est active : l'aperçu suit les couches cochées et le niveau de l'onglet relatif, pas l'intervalle d'années.

**Différence avec l'onglet relatif.** La molette et le mode cumulatif **filtrent** les couches déjà chargées ; le bouton **Voir**, lui, **ajoute** au projet un nouveau groupe de couches à chaque clic (les précédents restent dans le projet). Comme dans la fiche US, avec une base de données PostgreSQL le mécanisme de chargement filtre par site et non par US individuelle : les couches montrent tout le site.

## Intégration Matrice

### Visualisation Synchronisée

Avec la case **"Afficher la matrice"** active :
- La Matrice de Harris apparaît dans le panneau
- Elle se met à jour en synchronisation avec le niveau
- Elle met en évidence les US du niveau courant

### Génération d'Images

Le Time Manager peut générer :
- Une planche par niveau, composée avec le modèle de mise en page choisi (image JPG)
- La Matrice de Harris de ce niveau dans la planche, si **Afficher la matrice** est active

## Impression des Planches

### Processus

1. Sélectionner les couches à inclure
2. Activer **Afficher la matrice** si la Matrice doit apparaître sur les planches (sinon l'image de la Matrice du modèle est masquée)
3. Cliquer sur **Atlas Impression Tableaux par Période**
4. Dans la fenêtre qui s'ouvre, choisir le modèle de mise en page (voir la note « Quel modèle choisir » en bas) et confirmer
5. Choisir le dossier où enregistrer les planches
6. Répondre à la question : ouvrir ou non le Layout Designer pour retoucher le modèle avant de commencer
7. Patienter : une barre de progression indique la planche en cours et, à la fin, un message dit où elles ont été enregistrées
8. Pour arrêter la génération, cliquer sur **Arrêter le processus d'impression** : les planches déjà écrites restent dans le dossier

### Sortie

- Un `Tavola_N.jpg` pour chaque niveau (N est la valeur de `order_layer`), dans le dossier choisi : la carte à ce niveau, dans le mode actif (cumulatif ou niveau unique)
- Le titre « Tavola N » et l'image de la Matrice apparaissent si le modèle les prévoit (la Matrice seulement avec **Afficher la matrice** active)
- Les niveaux où aucune US n'a de datation renseignée sont ignorés : ces numéros manquent dans la suite des fichiers
- Avec un modèle à deux pages, chaque niveau produit deux images, la seconde étant `Tavola_N_2.jpg` (voir la note « Rendre apte n'importe quel modèle » en bas)

**Étiquettes de la planche.** Pendant qu'il génère les planches de l'atlas, le Time Manager met sur les couches choisies les étiquettes de la planche — le numéro de l'unité dans un cercle sur les US, la cote sur les points — et les retire à la fin de la génération, en remettant celles qui y étaient avant. Depuis la 5.13.110-alpha, il les retire dans tous les cas, même si une planche échoue : auparavant, dans ce cas, elles restaient sur les couches du projet et finissaient dans le fichier du projet à l'enregistrement.

## Workflow Typique

### 1. Préparation

```
1. Ouvrir le projet QGIS avec les couches US
2. Vérifier que order_layer est rempli
3. Ouvrir le Time Manager
```

### 2. Sélection des Couches

```
1. Sélectionner les couches à contrôler
2. Généralement : pyunitastratigrafiche et/ou _usm
```

### 3. Navigation

```
1. Utiliser la molette ou le spinbox
2. Observer le changement de visualisation
3. Activer/désactiver le mode cumulatif
```

### 4. Documentation

```
1. Activer "Afficher la matrice"
2. Imprimer les planches avec "Atlas Impression Tableaux par Période"
3. Vérifier les fichiers Tavola_N.jpg dans le dossier choisi
```

## Templates de Mise en Page

### Chargement de Template

Le Time Manager prend en charge les templates QGIS pour :
- Mises en page d'impression personnalisées
- En-têtes et légendes
- Formats standards

### Templates Disponibles

La fenêtre de choix liste les fichiers `.qpt` trouvés dans le dossier du plugin, dans `resources/dbfiles/` et dans `~/pyarchinit_5/bin/profile/template/` :
- `layout_TimeManager` : le modèle du Time Manager, avec le titre « Tavola N » et l'image de la Matrice
- les modèles d'impression du profil pyArchInit (par exemple les « Modello adArte… »)
- tout autre `.qpt`, choisi avec le bouton **Sfoglia...** (Parcourir)

## Bonnes Pratiques

### 1. order_layer

- Remplir AVANT d'utiliser le Time Manager
- Utiliser des valeurs consécutives
- US contemporaines = même valeur

### 2. Visualisation

- Commencer par le niveau 0 (le plus ancien)
- Procéder par ordre croissant
- Utiliser le mode cumulatif pour les présentations

### 3. Documentation

- Capturer des écrans aux niveaux significatifs
- Documenter les passages de phase
- Imprimer les planches pour les rapports (une par niveau)

## Résolution des Problèmes

### Couches Non Visibles dans la Liste

**Cause** : Couche sans champ order_layer

**Solution** :
- Ajouter le champ order_layer à la couche
- Le remplir avec des valeurs appropriées

### Aucun Changement Visuel

**Causes** :
- order_layer non rempli
- Filtre non appliqué

**Solutions** :
- Vérifier les valeurs order_layer dans les US
- Contrôler que la couche est sélectionnée

### Molette Ne Répond Pas

**Cause** : Aucune couche sélectionnée

**Solution** : Sélectionner au moins une couche dans la liste

## Références

### Fichiers Source
- `tabs/Gis_Time_controller.py` - Interface principale
- `gui/ui/Gis_Time_controller.ui` - Layout UI

### Champ Base de Données
- `us_table.order_layer` - Index stratigraphique

---

## Vidéo Tutorial

### Time Manager
`[Placeholder : video_time_manager.mp4]`

**Contenus** :
- Configuration de order_layer
- Navigation temporelle
- Impression des planches
- Intégration avec la Matrice

**Durée prévue** : 15-18 minutes

---

*Dernière mise à jour : Octobre 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../animations/pyarchinit_timemanager_animation.html)

---

## La matrice, depuis la 5.13.44

La matrice du Time Manager ne passe plus par Graphviz. Elle est dessinée par le même moteur de mise en page que le panneau **Voir la matrice**, dans QGIS et sans sous-processus.

- **Elle est immédiate.** Sur le site d'exemple (51 US, 81 relations) le dessin coûte quelques millisecondes au lieu d'environ trois dixièmes de seconde, et les processus `dot` et `tred` qui restaient parfois bloqués ont disparu. Les périodes du site sont lues **une seule fois** : auparavant elles étaient relues avec une requête par aire et par période, à chaque cran de la molette.
- **Dans l'atlas la matrice est vectorielle.** L'image placée dans la planche est un SVG de quelques dizaines de Ko au lieu d'un JPEG de méga-octets.
- **C'est la même matrice** que le panneau Extended Matrix : mêmes bandes de période, même symbologie, même réduction des redondances. Les flèches qui **remontent** les bandes — là où la stratigraphie contredit la chronologie — sont dessinées en **rouge**.
- La matrice ne contient toujours que les US visibles à la position courante de la molette.

- Les US **non visibles** à la position courante mais citées par une relation entrent tout de même dans le dessin, **estompées** : sans elles la séquence semblerait brisée, et dessinées comme les autres elles sembleraient sur la carte.

> **Quel modèle choisir.** Dans le sélecteur chaque modèle est marqué : **✓** possède le titre et l'image de la matrice (celui du Time Manager), **•** seulement la carte — les planches sortent, plus dépouillées — **✗** n'a pas de carte. Auparavant, en choisir un sans ces éléments faisait revenir le générateur sans un mot.

> **Rendre apte n'importe quel modèle.** `scripts/prepare_atlas_templates.py`, exécuté avec le Python de QGIS, écrit à côté de chaque modèle une copie suffixée « + Time Manager » portant le titre et l'image de la matrice sur une **nouvelle page**. Les originaux ne sont pas touchés. Chaque niveau produit alors deux images.
