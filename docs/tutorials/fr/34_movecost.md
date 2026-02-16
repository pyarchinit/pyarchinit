# PyArchInit - MoveCost - Analyse des Chemins de Moindre Cout

## Sommaire

1. [Introduction](#introduction)
2. [Acces a l'outil](#acces-a-loutil)
3. [Prerequis](#prerequis)
4. [Interface utilisateur](#interface-utilisateur)
5. [Onglet Algorithmes](#onglet-algorithmes)
6. [Onglet Resultats](#onglet-resultats)
7. [Onglet Exportation](#onglet-exportation)
8. [Onglet Parametres](#onglet-parametres)
9. [Flux de travail operationnel](#flux-de-travail-operationnel)
10. [Resolution des problemes](#resolution-des-problemes)
11. [Notes techniques](#notes-techniques)

---

## Introduction

**MoveCost** est un outil autonome de PyArchInit pour l'analyse des chemins de moindre cout (Least-Cost Path Analysis, LCPA) base sur des scripts R. L'analyse des chemins de moindre cout est une methodologie fondamentale en archeologie du paysage qui permet de modeliser les itineraires les plus probables entre des lieux, en tenant compte de la topographie du terrain et du cout energetique du deplacement.

### Historique

Auparavant, la fonctionnalite MoveCost etait integree directement dans le formulaire Site de PyArchInit. A partir de la version actuelle, MoveCost a ete extrait comme **outil d'analyse independant**, accessible via un QDialog dedie. Cette separation offre plusieurs avantages :

- **Interface dediee** : Un dialogue avec 4 onglets organises par fonction
- **Meilleure organisation** : Algorithmes, resultats, exportation et parametres clairement separes
- **Acces rapide** : Disponible depuis la barre d'outils sans ouvrir le formulaire Site
- **Extensibilite** : Structure modulaire facilitant l'ajout de nouveaux algorithmes

### Qu'est-ce que l'analyse des chemins de moindre cout ?

L'analyse des chemins de moindre cout calcule le chemin optimal entre deux ou plusieurs points sur une surface de cout derivee d'un modele numerique de terrain (MNT). Le cout du deplacement depend de la pente du terrain et est calcule a l'aide de fonctions de cout anisotropiques qui tiennent compte de la direction du mouvement (montee vs descente).

<!-- IMAGE: Exemple de chemin de moindre cout sur MNT -->
> **Fig. 1** : Exemple de chemin de moindre cout calcule sur un modele numerique de terrain

---

## Acces a l'outil

### Depuis la barre d'outils

1. Reperer le bouton deroulant **Outils d'analyse** (Analysis Tools) dans la barre d'outils PyArchInit -- il a une icone de graphique/analyse
2. Cliquer sur la fleche du menu deroulant
3. Selectionner **MoveCost** dans le menu

<!-- IMAGE: Bouton Outils d'analyse dans la barre d'outils -->
> **Fig. 2** : Le bouton Outils d'analyse dans la barre d'outils PyArchInit avec le menu deroulant ouvert

### Fenetre de dialogue

Au clic, un **QDialog modal** s'ouvre avec quatre onglets :

```
+-----------------------------------------------------------+
|  MoveCost - Analyse des Chemins de Moindre Cout            |
+-----------------------------------------------------------+
| [Algorithmes] | [Resultats] | [Exportation] | [Parametres]|
+-----------------------------------------------------------+
|                                                           |
|              (Contenu de l'onglet actif)                   |
|                                                           |
+-----------------------------------------------------------+
|                              [Fermer]                      |
+-----------------------------------------------------------+
```

---

## Prerequis

Avant d'utiliser MoveCost, verifier que les composants suivants sont installes et configures :

### 1. R (Langage statistique)

| Prerequis | Detail |
|-----------|--------|
| **Logiciel** | R (version >= 4.0 recommandee) |
| **Telechargement** | [https://cran.r-project.org/](https://cran.r-project.org/) |
| **Verification** | Ouvrir un terminal et taper `R --version` |

### 2. Paquet R `movecost`

Installer le paquet depuis R :

```r
install.packages("movecost")
```

Dependances principales installees automatiquement : `terra`, `gdistance`, `sp`.

### 3. QGIS Processing R Provider

| Prerequis | Detail |
|-----------|--------|
| **Extension** | Processing R Provider |
| **Installation** | QGIS > Extensions > Gerer et installer les extensions > Chercher "Processing R Provider" |
| **Configuration** | Parametres de traitement > Sketcher > R > Chemin du dossier R |

### 4. Donnees d'entree

- **MNT/MNE** : Un raster du modele numerique de terrain pour la zone d'etude
- **Couche de points** : Points d'origine et de destination pour l'analyse
- **Couche de polygones** : (Optionnel) Pour les variantes "by polygon" des algorithmes

### Liste de verification rapide

```
+-------------------------------------------+
| Liste de verification des prerequis        |
+-------------------------------------------+
| [x] R installe et dans le PATH            |
| [x] Paquet movecost installe dans R       |
| [x] Processing R Provider actif dans QGIS |
| [x] MNT charge dans le projet QGIS        |
| [x] Couche de points avec origines/dest.  |
+-------------------------------------------+
```

---

## Interface utilisateur

Le dialogue MoveCost est organise en **4 onglets**, chacun avec une fonction specifique.

### Apercu des onglets

| Onglet | Icone | Fonction |
|--------|-------|----------|
| **Algorithmes** | Engrenage | Selectionner et lancer les 14 algorithmes d'analyse |
| **Resultats** | Graphique | Visualiser les statistiques de cout et les plots R |
| **Exportation** | Disque | Exporter les resultats en CSV, PDF ou HTML |
| **Parametres** | Cle a molette | Configurer les scripts R, la langue, l'organisation des couches |

<!-- IMAGE: Apercu du dialogue MoveCost avec 4 onglets -->
> **Fig. 3** : Le dialogue MoveCost avec les quatre onglets visibles

---

## Onglet Algorithmes

L'onglet **Algorithmes** est le coeur de l'outil MoveCost. Il contient **14 algorithmes** bases sur des scripts R, organises en **3 groupes fonctionnels**.

### Groupe 1 : Surface de cout et chemins

Algorithmes pour le calcul de surfaces de cout accumulees et de chemins de moindre cout.

| Algorithme | Description |
|------------|-------------|
| **movecost** | Calcule la surface de cout accumulee anisotrope dependante de la pente et les chemins de moindre cout depuis un point d'origine |
| **movecost by polygon** | Idem, mais en utilisant une zone polygonale pour definir l'etendue du MNT |
| **movebound** | Calcule les limites de cout de deplacement dependantes de la pente autour de localisations ponctuelles |
| **movebound by polygon** | Idem, mais en utilisant un polygone |

### Groupe 2 : Analyse de corridors et reseaux

Algorithmes pour l'analyse de corridors de cout et de reseaux de chemins optimaux.

| Algorithme | Description |
|------------|-------------|
| **movecorr** | Calcule le corridor de moindre cout entre des localisations ponctuelles |
| **movecorr by polygon** | Idem, mais en utilisant un polygone |
| **movealloc** | Calcule l'allocation de cout de deplacement dependante de la pente aux origines |
| **movealloc by polygon** | Idem, mais en utilisant un polygone |
| **movenetw** | Calcule le reseau de chemins de moindre cout entre plusieurs points |
| **movenetw by polygon** | Idem, mais en utilisant un polygone |

### Groupe 3 : Comparaison et classement

Algorithmes pour comparer les fonctions de cout et classer les destinations.

| Algorithme | Description |
|------------|-------------|
| **movecomp** | Compare les chemins de moindre cout generes avec differentes fonctions de cout |
| **movecomp by polygon** | Idem, mais en utilisant un polygone |
| **moverank** | Classe les destinations par cout de deplacement depuis une origine |
| **moverank by polygon** | Idem, mais en utilisant un polygone |

### Comment lancer un algorithme

1. Selectionner l'algorithme souhaite dans la liste
2. L'interface de traitement (Processing) de QGIS s'ouvre avec les parametres specifiques a l'algorithme
3. Configurer les parametres d'entree :
   - **MNT/MNE** : Selectionner le raster de terrain
   - **Point(s) d'origine** : Selectionner la couche de points
   - **Polygone** (si variante "by polygon") : Selectionner la zone d'etude
   - **Fonction de cout** : Choisir parmi les fonctions disponibles (Tobler, Minetti, etc.)
4. Cliquer sur **Executer**
5. Les resultats sont automatiquement ajoutes au projet QGIS

<!-- IMAGE: Onglet Algorithmes avec 3 groupes -->
> **Fig. 4** : L'onglet Algorithmes avec les trois groupes d'algorithmes mis en evidence

<!-- IMAGE: Interface Processing pour un algorithme movecost -->
> **Fig. 5** : L'interface de traitement QGIS pour l'algorithme movecost avec les parametres configures

### Variantes "by polygon"

Les variantes "by polygon" de chaque algorithme permettent de :
- **Limiter la zone d'analyse** a une region specifique
- **Reduire le temps de calcul** en travaillant sur un MNT decoupe
- **Focaliser l'analyse** sur une zone d'interet archeologique

---

## Onglet Resultats

L'onglet **Resultats** permet de visualiser les resultats des analyses executees.

### Resume des couts (Cost Summary)

Une zone de texte (QTextEdit) affiche les statistiques resumees des couches de cout generees :

| Statistique | Description |
|-------------|-------------|
| **Minimum** | Valeur minimale de cout dans la surface |
| **Maximum** | Valeur maximale de cout dans la surface |
| **Moyenne** | Valeur moyenne de cout |
| **Ecart-type** | Ecart-type des valeurs de cout |

```
+---------------------------------------------------+
| Resume des couts                                   |
+---------------------------------------------------+
| Couche : movecost_accumulated_cost                 |
| Minimum : 0.00                                     |
| Maximum : 15234.56                                 |
| Moyenne : 4521.89                                  |
| Ecart-type : 2103.45                               |
|                                                    |
| Couche : movecost_back_link                        |
| Minimum : 0.00                                     |
| Maximum : 8.00                                     |
| Moyenne : 4.12                                     |
+---------------------------------------------------+
```

### Visualiseur de plots R (R Plot Viewer)

Le visualiseur de plots R affiche le dernier graphique genere par les scripts R :

| Fonction | Description |
|----------|-------------|
| **Affichage automatique** | Affiche le dernier plot R depuis le repertoire temporaire |
| **Actualiser** | Recharge le dernier plot disponible |
| **Enregistrer** | Enregistre le plot actuel dans un fichier image (PNG, JPG) |
| **Selection manuelle** | Permet d'ouvrir un plot R specifique depuis n'importe quel emplacement |

<!-- IMAGE: Onglet Resultats avec resume des couts et plot R -->
> **Fig. 6** : L'onglet Resultats affichant les statistiques de cout et un plot R

### Emplacements des plots R

Les plots R sont sauvegardes dans les repertoires temporaires de QGIS/R. Le visualiseur recherche automatiquement dans les emplacements suivants :

- Repertoire temporaire de QGIS Processing
- Repertoire temporaire de R (`tempdir()`)
- Dossier de sortie specifie par l'utilisateur

---

## Onglet Exportation

L'onglet **Exportation** offre trois options pour exporter les resultats de l'analyse.

### Exporter la table des couts (CSV)

Exporte les statistiques des couches de cout dans un fichier CSV :

1. Cliquer sur **Exporter la table des couts**
2. Selectionner l'emplacement et le nom du fichier
3. Le fichier CSV contient : nom de couche, minimum, maximum, moyenne, ecart-type

| Colonne | Description |
|---------|-------------|
| `layer_name` | Nom de la couche de cout |
| `min_value` | Valeur minimale |
| `max_value` | Valeur maximale |
| `mean_value` | Valeur moyenne |
| `std_dev` | Ecart-type |

### Exporter le rapport (PDF)

> **Note** : Cette fonctionnalite est actuellement en cours de developpement (stub). Elle sera disponible dans une version future.

### Exporter le rapport (HTML)

Genere un rapport HTML complet et stylise qui inclut :

- **En-tete** avec titre du projet et date
- **Parametres d'analyse** utilises
- **Statistiques des couches** au format tabulaire
- **Plots R** integres sous forme d'images
- **Style CSS integre** pour une presentation professionnelle

1. Cliquer sur **Exporter le rapport (HTML)**
2. Selectionner l'emplacement et le nom du fichier
3. Le rapport s'ouvre automatiquement dans le navigateur par defaut

<!-- IMAGE: Exemple de rapport HTML exporte -->
> **Fig. 7** : Un exemple de rapport HTML genere par MoveCost avec statistiques et graphiques

---

## Onglet Parametres

L'onglet **Parametres** permet de configurer l'outil MoveCost.

### Installer les scripts R

| Fonction | Description |
|----------|-------------|
| **Installer les scripts R** | Copie les scripts R de movecost dans le repertoire de traitement de QGIS |

Cette operation est necessaire lors de la **premiere configuration** ou apres une mise a jour de l'extension. Les scripts sont copies dans le dossier des scripts R du Processing :

```
{QGIS_HOME}/processing/rscripts/
```

### Selection de la langue

MoveCost prend en charge **5 langues** pour l'interface :

| Langue | Code |
|--------|------|
| English | en |
| Italiano | it |
| Francais | fr |
| Espanol | es |
| Deutsch | de |

La langue selectionnee s'applique a :
- Libelles de l'interface du dialogue
- Messages d'etat et d'erreur
- En-tetes des tableaux de resultats

### Organisation des couches

| Fonction | Description |
|----------|-------------|
| **Organiser les couches** | Organisation et stylisation automatiques des couches de sortie movecost |

Cette fonction :
1. Regroupe les couches de sortie en groupes logiques dans le panneau Couches de QGIS
2. Applique des styles de couleur predefinis (rampes de couleur pour les surfaces de cout)
3. Renomme les couches avec des noms descriptifs

### Documentation

| Fonction | Description |
|----------|-------------|
| **Aide** | Ouvre la documentation en ligne de l'outil |

<!-- IMAGE: Onglet Parametres avec toutes les options -->
> **Fig. 8** : L'onglet Parametres de MoveCost avec les options de configuration

---

## Flux de travail operationnel

### Exemple pas a pas : Calcul d'un chemin de moindre cout

Cet exemple montre comment calculer un chemin de moindre cout entre un habitat et une source d'eau.

### Etape 1 : Preparation des donnees

```
1. Charger le MNT de la zone d'etude dans le projet QGIS
2. Creer une couche de points avec :
   - Point d'origine (habitat)
   - Point(s) de destination (source d'eau)
3. Verifier que le systeme de reference de coordonnees est coherent
```

### Etape 2 : Verification des prerequis

```
1. Ouvrir MoveCost depuis la barre d'outils
2. Aller dans l'onglet Parametres
3. Cliquer sur "Installer les scripts R" (si premiere fois)
4. Verifier qu'aucune erreur n'est signalee
```

### Etape 3 : Execution de l'analyse

```
1. Passer a l'onglet Algorithmes
2. Selectionner "movecost" dans le Groupe 1
3. Dans la fenetre de traitement :
   - MNT : selectionner le raster de terrain
   - Origine : selectionner le point de l'habitat
   - Destination : selectionner le point de la source d'eau
   - Fonction de cout : Tobler (recommandee par defaut)
4. Cliquer sur Executer
5. Attendre la fin du traitement
```

### Etape 4 : Analyse des resultats

```
1. Passer a l'onglet Resultats
2. Consulter le Resume des couts pour les statistiques
3. Examiner le plot R pour la visualisation
4. Dans le canevas QGIS, observer :
   - La surface de cout accumulee (raster colore)
   - Le chemin de moindre cout (ligne vectorielle)
```

### Etape 5 : Exportation

```
1. Passer a l'onglet Exportation
2. Exporter la table des couts en CSV pour des analyses complementaires
3. Generer le rapport HTML pour la documentation
4. Enregistrer le plot R depuis l'onglet Resultats
```

### Etape 6 : Organisation

```
1. Retourner a l'onglet Parametres
2. Cliquer sur "Organiser les couches" pour trier les resultats
3. Les couches sont regroupees et stylisees automatiquement
```

<!-- IMAGE: Flux de travail complet avec captures d'ecran annotees -->
> **Fig. 9** : Le flux de travail complet de la preparation des donnees aux resultats finaux

---

## Resolution des problemes

### R non trouve

**Symptome** : Message d'erreur "R non trouve" ou "R is not installed"

**Solutions** :
1. Verifier que R est installe : ouvrir un terminal et taper `R --version`
2. Verifier le chemin de R dans les parametres de Processing :
   - **QGIS** > **Parametres** > **Options** > **Sketcher** > **Sketcher** > **R**
   - Definir le **chemin du dossier R** correctement
3. Sur macOS, R peut se trouver dans `/Library/Frameworks/R.framework/Resources/`
4. Sur Windows, generalement dans `C:\Program Files\R\R-4.x.x\`
5. Sur Linux, verifier avec `which R`

### Scripts R manquants

**Symptome** : Les algorithmes n'apparaissent pas dans la boite a outils de traitement

**Solutions** :
1. Ouvrir MoveCost > Parametres > cliquer sur **Installer les scripts R**
2. Redemarrer QGIS apres l'installation des scripts
3. Verifier que le Processing R Provider est actif :
   - **QGIS** > **Extensions** > **Gerer et installer les extensions** > Verifier "Processing R Provider"
4. Verifier le dossier des scripts R : `{QGIS_HOME}/processing/rscripts/`

### Plots R non affiches

**Symptome** : L'onglet Resultats n'affiche aucun graphique

**Solutions** :
1. Cliquer sur **Actualiser** dans l'onglet Resultats
2. Utiliser la **Selection manuelle** pour naviguer vers le dossier des plots
3. Verifier que l'analyse s'est terminee avec succes
4. Verifier les repertoires temporaires :
   - macOS/Linux : `/tmp/` ou `$TMPDIR`
   - Windows : `%TEMP%`
5. Certains algorithmes peuvent ne pas generer de graphiques

### Paquet movecost non installe dans R

**Symptome** : Erreur "there is no package called 'movecost'"

**Solutions** :
1. Ouvrir R ou RStudio
2. Executer : `install.packages("movecost")`
3. Verifier : `library(movecost)` -- ne doit produire aucune erreur
4. En cas de problemes de dependances : `install.packages("movecost", dependencies = TRUE)`

### Analyse tres lente

**Symptome** : Le traitement prend beaucoup de temps

**Solutions** :
1. Utiliser les variantes **"by polygon"** pour limiter la zone de calcul
2. Reduire la resolution du MNT (reechantillonnage)
3. Verifier les dimensions du MNT :
   - Les MNT tres grands (>10000x10000 pixels) necessitent un temps considerable
   - Decouper le MNT a la zone d'interet avant l'analyse
4. Fermer les autres applications pour liberer de la RAM

### Erreur de projection / SCR

**Symptome** : Resultats incoherents ou erreur de systeme de reference de coordonnees

**Solutions** :
1. Verifier que le MNT et les couches de points ont le **meme SCR**
2. Utiliser un **SCR projete** (metrique), pas geographique
3. SCR recommandes : UTM (p.ex. EPSG:32632 pour l'Italie centrale)
4. Reprojeter les couches si necessaire avant l'analyse

---

## Notes techniques

### Architecture de l'outil

MoveCost est implemente comme un **QDialog** autonome (`MoveCostDialog`) qui :
- S'interface avec le QGIS Processing Framework pour l'execution des algorithmes R
- Lit les resultats depuis les couches chargees dans le projet
- Gere la visualisation des plots R via QLabel/QPixmap
- Genere des rapports HTML utilisant des modeles predefinis

### Fichiers source

| Fichier | Description |
|---------|-------------|
| `tabs/MoveCost.py` | Dialogue principal et logique de l'interface |
| `gui/ui/MoveCost.ui` | Disposition de l'interface Qt Designer |
| `resources/r_scripts/` | Scripts R pour les algorithmes movecost |

### Fonctions de cout supportees

Le paquet R `movecost` supporte plusieurs fonctions de cout anisotropiques :

| Fonction | Auteur | Description |
|----------|--------|-------------|
| **Tobler** | Tobler (1993) | Fonction de cout de marche classique |
| **Minetti** | Minetti et al. (2002) | Basee sur le cout metabolique |
| **Herzog** | Herzog (2010) | Variante modifiee |
| **Llobera-Sluckin** | Llobera & Sluckin (2007) | Modele energetique |
| **Autres** | Divers | Voir la documentation du paquet R |

### References bibliographiques

- Alberti, G. (2019). `movecost` : An R package for calculating accumulated slope-dependent anisotropic cost-surfaces and least-cost paths. *SoftwareX*, 10, 100601.
- Tobler, W. (1993). Three presentations on geographical analysis and modeling. *NCGIA Technical Report*, 93-1.
- Minetti, A.E. et al. (2002). Energy cost of walking and running at extreme uphill and downhill slopes. *Journal of Applied Physiology*, 93(3), 1039-1046.

### Compatibilite

| Composant | Version minimale |
|-----------|-----------------|
| PyArchInit | 5.0.x |
| QGIS | 3.22+ |
| R | 4.0+ |
| Paquet movecost (R) | 1.0+ |
| Processing R Provider | 2.0+ |

---

## Tutoriel video

### MoveCost - Analyse des Chemins de Moindre Cout
`[Espace reserve : video_movecost.mp4]`

**Contenu** :
- Configuration de R et du paquet movecost
- Installation des scripts R dans QGIS
- Execution de l'algorithme movecost de base
- Visualisation des resultats et des plots R
- Exportation des rapports

**Duree prevue** : 20-25 minutes

---

*Documentation PyArchInit - MoveCost*
*Version : 5.0.x*
*Derniere mise a jour : Fevrier 2026*
