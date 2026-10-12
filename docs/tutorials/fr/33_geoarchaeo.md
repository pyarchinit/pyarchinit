# PyArchInit - GeoArchaeo - Analyse Géostatistique

## Table des matières
1. [Introduction](#introduction)
2. [Accès à l'outil](#accès-à-loutil)
3. [Interface utilisateur](#interface-utilisateur)
4. [Onglet Données](#onglet-données)
5. [Onglet Variogramme](#onglet-variogramme)
6. [Onglet Krigeage](#onglet-krigeage)
7. [Onglet Motifs (ML)](#onglet-motifs-ml)
8. [Onglet Échantillonnage](#onglet-échantillonnage)
9. [Onglet Rapport](#onglet-rapport)
10. [Flux de travail opérationnel](#flux-de-travail-opérationnel)
11. [Dépannage](#dépannage)
12. [Notes techniques](#notes-techniques)

---

## Introduction

**GeoArchaeo** est le module d'analyse géostatistique intégré à PyArchInit ; il correspond à la version **1.3.1** du plugin GeoArchaeo. Il travaille sur toute couche de points du projet QGIS possédant un champ numérique (nombre de tessons, mesures géophysiques, analyses de sol, dimensions des tombes…) et accompagne l'analyse depuis les statistiques descriptives jusqu'au variogramme, à l'interpolation par krigeage ordinaire avec son incertitude, à la recherche de groupes et d'anomalies par apprentissage automatique, à la proposition de nouveaux points d'échantillonnage et enfin à un rapport.

L'interface de GeoArchaeo n'existe qu'en italien et en anglais. Dans ce tutoriel les libellés sont traduits ; le libellé anglais affiché dans le panneau est indiqué entre parenthèses.

<!-- VIDEO: Introduction a GeoArchaeo -->
> **Tutoriel video**: [Inserer le lien video introduction GeoArchaeo]

### Pourquoi l'analyse géostatistique en archéologie ?

L'analyse géostatistique permet de :

- **Décrire** la distribution des valeurs mesurées (moyenne, dispersion, asymétrie, valeurs aberrantes)
- **Quantifier** la corrélation spatiale, c'est-à-dire jusqu'à quelle distance les valeurs se ressemblent (variogramme)
- **Interpoler** les valeurs entre les points connus pour obtenir une surface continue accompagnée de son incertitude (krigeage)
- **Reconnaître** des groupes de points semblables et des anomalies (apprentissage automatique)
- **Planifier** où échantillonner ou fouiller lors des prochaines campagnes
- **Documenter** les analyses dans un rapport

### Aperçu du flux de travail

```
Données d'entrée : couche de points + champ numérique (choisis en haut, une seule fois)
  │
  ├─ 1 Données ............ statistiques descriptives, histogramme
  ├─ 2 Variogramme ........ pépite, palier, portée, anisotropie
  ├─ 3 Krigeage ........... rasters de l'estimation et de l'incertitude, validation croisée
  ├─ 4 Motifs (ML) ........ groupes et anomalies (couche de points)
  ├─ 5 Échantillonnage .... nouveaux points proposés (couche de points)
  └─ 6 Rapport ............ document HTML avec graphiques interactifs, ou PDF
```

### Nouveautés de la version 1.3.1

- La couche et le champ se choisissent **une seule fois** en haut et valent pour tous les onglets ; chaque onglet conserve ses propres résultats
- Les graphiques s'affichent dans le panneau même sans QtWebEngine (aperçu statique et bouton pour les ouvrir dans le navigateur)
- Le krigeage produit aussi le **raster d'incertitude**, applique la rampe de couleurs et calcule une véritable **validation croisée leave-one-out**
- L'anisotropie est vérifiée avec de véritables **variogrammes directionnels** ; pépite, palier et portée peuvent être fixés à la main
- Variogramme et krigeage sont bien plus rapides (recherche des voisins par KD-tree) : grilles jusqu'à **500 × 500 cellules**
- Les valeurs NULL ne bloquent plus les statistiques ni le krigeage ; le rapport contient les graphiques ; les données d'exemple proviennent du dossier du module
- La langue du panneau est enregistrée dans les paramètres de QGIS

---

## Accès à l'outil

GeoArchaeo fait partie du groupe des outils d'analyse de PyArchInit.

### Depuis la barre d'outils

1. Dans la barre d'outils PyArchInit, repérer le bouton déroulant des **outils d'analyse** (le même groupe qui contient notamment SAM, Pottery Tools et MoveCost)
2. Cliquer sur la flèche à côté du bouton : l'icône visible peut être celle d'un autre outil du groupe
3. Choisir **GeoArchaeo - Geostatistical Analysis** (libellé de l'action dans PyArchInit lorsque QGIS est en français)

<!-- IMAGE: Bouton deroulant des outils d'analyse dans la barre d'outils -->
> **Fig. 1** : Le menu déroulant des outils d'analyse dans la barre d'outils PyArchInit

La même entrée se trouve dans le menu **pyArchInit** de la barre de menus de QGIS et dans le menu des extensions, sous **pyArchInit - Archaeological GIS Tools**.

Le panneau GeoArchaeo s'ouvre comme **panneau ancrable** sur le côté droit de la fenêtre QGIS : on peut le déplacer, le redimensionner ou le détacher comme n'importe quel panneau de QGIS. Si on le ferme, la même entrée le rouvre avec les résultats de la session encore présents.

<!-- IMAGE: Panneau GeoArchaeo ancre a droite dans QGIS -->
> **Fig. 2** : Le panneau GeoArchaeo ancré sur le côté droit de la fenêtre QGIS

### Sélecteur de langue

En haut à droite, la liste **«Langue :»** (*Language:*) propose **Italiano** et **English**, les deux seules langues de l'interface de GeoArchaeo. Le changement est immédiat, sans redémarrer QGIS, et le choix est enregistré dans les paramètres de QGIS. Tant qu'aucun choix n'est fait, le panneau suit la langue de QGIS : italien si QGIS est en italien, anglais dans tous les autres cas, donc aussi avec un QGIS en français.

---

## Interface utilisateur

De haut en bas, le panneau contient : l'en-tête avec ses boutons, le groupe **«Données d'entrée (utilisées par tous les onglets)»** (*Input data (used by all tabs)*), les **6 onglets** de l'analyse et, pendant les calculs, la barre de progression avec le bouton **«Annuler»** (*Cancel*).

### En-tête

| Élément | Fonction |
|---------|----------|
| **«Charger des données d'exemple»** (*Load example data*) | Ouvre la liste des jeux de données de test fournis avec le module (voir l'onglet Données) |
| **«Tutoriel»** (*Tutorial*) | Ouvre le guide intégré de GeoArchaeo, en italien ou en anglais, consultable aussi dans le navigateur |
| **«Langue :»** (*Language:*) | Liste Italiano / English |

### Données d'entrée

Dans le groupe **«Données d'entrée (utilisées par tous les onglets)»** (*Input data (used by all tabs)*), on choisit une seule fois :

- **«Couche de points :»** (*Point layer:*) : une couche vectorielle de points du projet
- **«Champ de valeur (numérique) :»** (*Value field (numeric):*) : le champ à analyser (la liste ne montre que les champs numériques)

En dessous, un résumé indique les points valides sur le total, le SCR et l'emprise de la couche, par exemple «500 points valides sur 500 · SCR EPSG:32633 · …» (*500 valid points of 500 · CRS EPSG:32633 · …*). Les points sans valeur (NULL ou texte non numérique) ne sont pas comptés comme valides. Le résumé avertit aussi lorsque le projet ne contient aucune couche de points, lorsque la couche n'a pas de champ numérique ou lorsque le SCR est géographique (degrés).

Lorsqu'on change de couche, le panneau propose aussi la distance maximale du variogramme et la taille de cellule du krigeage, et présélectionne la couche dans l'onglet Motifs (ML) si aucune n'y est encore sélectionnée.

### Les six onglets

| Onglet | Fonction | Résultat |
|--------|----------|----------|
| **Données** (*Data*) | Statistiques descriptives du champ | Tableau des statistiques, histogramme avec boîte à moustaches |
| **Variogramme** (*Variogram*) | Structure spatiale des valeurs | Pépite, palier, portée, anisotropie, graphique |
| **Krigeage** (*Kriging*) | Interpolation sur une grille régulière | Rasters de l'estimation et de l'incertitude, validation croisée |
| **Motifs (ML)** (*Patterns (ML)*) | Groupes et anomalies par apprentissage automatique | Couche de points avec l'étiquette du groupe |
| **Échantillonnage** (*Sampling*) | Proposition de nouveaux points à échantillonner | Couche de points et tableau des coordonnées |
| **Rapport** (*Report*) | Regroupement des analyses de la session | Fichier HTML avec graphiques interactifs, ou PDF |

<!-- IMAGE: En-tete, groupe Donnees d'entree et les six onglets de GeoArchaeo -->
> **Fig. 3** : L'en-tête, le groupe «Données d'entrée» et les six onglets du panneau GeoArchaeo

### Résultats et graphiques

Chaque onglet affiche ses résultats dans un **cadre** sous le bouton de calcul, qui reste visible tant qu'on ne relance pas l'analyse, ainsi que le **graphique** dans le panneau :

- si QGIS dispose de QtWebEngine, le graphique Plotly est interactif directement dans le panneau (zoom, valeurs au survol de la souris)
- sinon un **aperçu statique** apparaît avec la note «Aperçu statique (QtWebEngine non disponible dans cette installation de QGIS).» (*Static preview (QtWebEngine not available in this QGIS installation).*)
- dans les deux cas, le bouton **«Ouvrir le graphique interactif dans le navigateur»** (*Open interactive chart in browser*) ouvre la version interactive dans le navigateur web

Les onglets Données, Variogramme et Krigeage se terminent par un lien vers l'étape suivante, par exemple **«Étape suivante : Variogramme →»** (*Next step: Variogram →*).

### Analyses en cours

Variogramme, krigeage, reconnaissance de motifs et échantillonnage sont calculés dans un **thread séparé** : QGIS reste utilisable, et en bas du panneau apparaissent la **barre de progression** (en pourcentage pour le krigeage) et le bouton **«Annuler»** (*Cancel*). Une seule analyse s'exécute à la fois : en lancer une autre affiche «Une analyse est déjà en cours : attendez qu'elle se termine ou annulez-la.» (*An analysis is already running: wait for it to finish or cancel it.*)

---

## Onglet Données

L'onglet **Données** (*Data*, «1. Analyse exploratoire» / *1. Exploratory analysis*) décrit la distribution des valeurs avant de les interpoler.

### Calcul des statistiques

1. Dans le groupe «Données d'entrée», choisir la couche de points et le champ numérique
2. Ouvrir l'onglet **Données**
3. Cliquer sur **«Calculer les statistiques»** (*Calculate statistics*)

<!-- IMAGE: Onglet Donnees avec statistiques et histogramme -->
> **Fig. 4** : L'onglet Données avec le tableau des statistiques et l'histogramme du champ choisi

### Statistiques et interprétation

| Statistique | Description |
|-------------|-------------|
| **Nombre de valeurs** (*Number of values*), **Valeurs manquantes** (*Missing values*) | Points avec une valeur valide et points exclus (NULL ou texte non numérique) |
| **Minimum**, **Maximum**, **Moyenne** (*Mean*), **Médiane** (*Median*) | Étendue et position des valeurs |
| **Écart-type** (*Std. deviation*), **Coefficient de variation** (*Coeff. of variation*) | Dispersion absolue et relative |
| **Premier quartile (Q1)**, **Troisième quartile (Q3)** (*First/Third quartile*) | Limites des 50 % centraux des valeurs |
| **Asymétrie** (*Skewness*), **Kurtosis** (*Kurtosis*) | Forme de la distribution |

Sous le tableau, le panneau ajoute une lecture en mots :

- asymétrie supérieure à 1 : distribution asymétrique à droite (quelques valeurs très élevées) ; envisager une transformation logarithmique avant le krigeage, par exemple en créant un nouveau champ avec la calculatrice de champs
- asymétrie inférieure à -1 : distribution asymétrique à gauche (quelques valeurs très faibles)
- sinon : distribution à peu près symétrique, adaptée au krigeage
- le nombre de valeurs aberrantes possibles, c'est-à-dire au-delà de 3 écarts-types de la moyenne

Le graphique montre l'**histogramme** des valeurs avec une **boîte à moustaches** (seulement l'histogramme dans l'aperçu statique).

### Données d'exemple

Le bouton **«Charger des données d'exemple»** (*Load example data*) ouvre la fenêtre «Données d'exemple GeoArchaeo» (*GeoArchaeo example data*) avec les jeux de données du dossier `test_layers` du module ; le chemin est indiqué dans **«Dossier :»** (*Folder:*) et peut être changé avec **«Parcourir…»** (*Browse…*). Les GeoPackage et les GeoJSON sont déjà cochés. Les fichiers CSV n'apparaissent que s'il n'existe pas de GeoPackage ou de GeoJSON du même nom ; ils doivent être cochés à la main et sont chargés comme texte délimité (champs `x` et `y`, EPSG:32633). Avec **OK**, les couches sont ajoutées au projet et la première couche de points chargée devient la couche d'entrée du panneau.

| Jeu de données | Points | Principaux champs numériques | Usage conseillé |
|----------------|--------|------------------------------|-----------------|
| `villa_ceramica` (GeoPackage) | 500 | `ceramic_count`, `weight_g`, `depth_cm` | Statistiques, variogramme, krigeage |
| `geoarchaeo_test_complete` (GeoPackage) | 500 | Les mêmes que `villa_ceramica` | Essai de tous les onglets |
| `geofisica_survey` (GeoPackage) | 4800 | `gpr_amplitude`, `mag_nt` | Isolation Forest, essai sur un grand jeu de données |
| `necropoli` (GeoPackage) | 120 tombes | `length_cm`, `width_cm`, `depth_cm`, `n_grave_goods` | DBSCAN ou K-Means |
| `soil_samples` (GeoPackage) | 80 | `sand_pct`, `silt_pct`, `clay_pct`, `ph`, `p_ppm`, `organic_pct` | Krigeage des propriétés du sol |
| `ricognizione_survey` (GeoJSON) | 100 | `densita_mq`, `visibilita`, `pendenza`, `distanza_acqua` | Krigeage de la densité, échantillonnage |
| `unita_scavo_ceramica` (GeoJSON) | 50 | `ceramica_tot`, `ceramica_fine`, `ceramica_comune` | Variogramme et krigeage avec peu de points |
| `area_studio` (GeoJSON) | 1 polygone | — | Zone d'étude pour l'échantillonnage |

Parmi les CSV, `magnetometria_grid` (2500 points, champ `mag_nT`) contient des anomalies magnétiques simulées (deux murs, une fosse, un four). Toutes les données sont simulées et en EPSG:32633 (UTM 33N, mètres). Le polygone `area_studio` couvre la zone de `ricognizione_survey`, `unita_scavo_ceramica` et `magnetometria_grid`, pas celle des autres jeux de données.

### Exigences relatives aux données

- La couche doit être une couche vectorielle de **points** (pour les multipoints, le premier point est utilisé)
- Le champ doit être **numérique** : un champ texte contenant des nombres doit être converti avec la calculatrice de champs
- Les valeurs NULL ou non numériques sont exclues automatiquement et comptées comme manquantes
- Il faut au moins **5 points** avec une valeur valide pour le variogramme et le krigeage (1 pour les statistiques) ; un variogramme fiable demande en général quelques dizaines de points
- Un **SCR projeté** en mètres (par exemple UTM) est recommandé : avec un SCR géographique, le résumé avertit et le variogramme et le krigeage demandent une confirmation

---

## Onglet Variogramme

L'onglet **Variogramme** (*Variogram*, «2. Variogramme» / *2. Variogram*) mesure comment la différence entre les valeurs augmente avec la distance : il décrit la structure spatiale des données et guide le krigeage.

### Qu'est-ce qu'un variogramme ?

Le variogramme met en relation la **semi-variance** des paires de points avec la **distance** qui les sépare. Les paramètres du modèle sont :

| Paramètre | Description |
|-----------|-------------|
| **Pépite** (*nugget*) | Variabilité à distance quasi nulle : erreur de mesure et variabilité à petite échelle |
| **Palier** (*sill*) | Variance totale atteinte par le modèle (le "plateau") |
| **Portée** (*range*) | Distance au-delà de laquelle les valeurs ne sont plus corrélées ; dans GeoArchaeo, c'est la portée pratique (95 % du palier) |

### Calcul du variogramme

1. Ouvrir l'onglet **Variogramme**
2. Dans le groupe **«Paramètres»** (*Parameters*), vérifier **«Distance maximale :»** (*Maximum distance:*) : le bouton **«Auto»** propose environ 1/3 de la diagonale de la zone couverte par les points (la même valeur est proposée lorsqu'on change de couche)
3. Choisir le **«Modèle théorique :»** (*Theoretical model:*)
4. Si nécessaire, cocher **«Vérifier l'anisotropie (variogrammes directionnels)»** (*Check anisotropy (directional variograms)*)
5. Cliquer sur **«Calculer le variogramme»** (*Calculate variogram*)

Les paires de points sont regroupées en **15 classes de distance** (lags) entre zéro et la distance maximale ; le nombre de classes ne se modifie pas depuis le panneau. Au-delà de **3000 points**, le variogramme est calculé sur un sous-échantillon aléatoire de 3000 points, car le nombre de paires croît avec le carré du nombre de points. Le modèle est ajusté par moindres carrés pondérés par le nombre de paires de chaque classe.

<!-- IMAGE: Onglet Variogramme avec parametres et resultats -->
> **Fig. 5** : L'onglet Variogramme avec les paramètres, le modèle théorique et le cadre des résultats

### Modèles théoriques

| Modèle | Comportement | Quand l'utiliser |
|--------|--------------|------------------|
| **«Sphérique (recommandé)»** (*Spherical (recommended)*) | Croît jusqu'à la portée puis reste constant | Le plus courant : densités de mobilier, distributions à limites nettes |
| **«Exponentiel»** (*Exponential*) | Croît rapidement près de l'origine et atteint le palier progressivement | Phénomènes à décroissance continue, par exemple les éléments chimiques du sol |
| **«Gaussien»** (*Gaussian*) | Très régulier près de l'origine | Phénomènes très "lisses" (surfaces) ; à utiliser avec prudence |
| **«Matérn»** (*Matérn*) | Intermédiaire entre exponentiel et gaussien (ν = 1,5) | Alternative souple |

Règle pratique : commencer par le modèle sphérique et comparer le RMSE de son ajustement avec celui des autres modèles. Le krigeage utilise le **dernier** variogramme calculé : après les comparaisons, recalculer celui qui a été retenu.

### Paramètres manuels

Le groupe **«Paramètres manuels (facultatif)»** (*Manual parameters (optional)*), désactivé par défaut, permet de fixer **«Pépite :»** (*Nugget:*), **«Palier (variance totale) :»** (*Sill (total variance):*) et **«Portée (distance de corrélation) :»** (*Range (correlation distance):*). Groupe activé, les valeurs non nulles restent fixes et celles laissées sur «Auto» (zéro) sont estimées.

### Lecture des résultats

Le cadre des résultats indique :

- le modèle avec la **pépite**, le **palier**, la **portée** (en unités du SCR) et le **RMSE** de l'ajustement
- le nombre de paires de points et de classes de distance, avec le sous-échantillon éventuellement utilisé
- une lecture de la portée : jusqu'à cette distance les valeurs sont spatialement corrélées, au-delà elles ne s'influencent pas
- le rapport pépite/palier : moins de 25 % forte continuité à petite échelle, jusqu'à 60 % continuité modérée, plus de 60 % forte variabilité à petite échelle ou erreur de mesure (le krigeage sera peu informatif)

Le graphique montre les points du variogramme expérimental (plus gros là où les paires sont plus nombreuses), la courbe du modèle et les lignes de pépite, de palier et de portée.

<!-- IMAGE: Variogramme experimental avec le modele ajuste -->
> **Fig. 6** : Variogramme expérimental et modèle sphérique avec les lignes de pépite, de palier et de portée

### Variogrammes directionnels (anisotropie)

Avec **«Vérifier l'anisotropie (variogrammes directionnels)»** cochée, GeoArchaeo calcule aussi les variogrammes dans les directions **0°, 45°, 90° et 135°** (angles mesurés depuis l'est dans le sens antihoraire, tolérance ±22,5°). Pépite et palier restent ceux du variogramme global ; la portée est estimée pour chaque direction.

- Si le rapport entre la plus grande et la plus petite portée dépasse **2**, le cadre signale l'anisotropie et la direction principale (par exemple le long d'un mur, d'une route ou d'une pente)
- Sinon il indique «Aucune anisotropie significative» (*No relevant anisotropy*) avec le rapport calculé
- Avec trop peu de paires par direction apparaît «Pas assez de paires pour les variogrammes directionnels.» (*Not enough pairs for directional variograms.*)

Dans le graphique interactif, les variogrammes directionnels sont des entrées de légende masquées au départ : cliquer sur 0°, 45°, 90° ou 135° pour les afficher (dans l'aperçu statique ils sont toujours tracés). Le krigeage du panneau utilise le modèle omnidirectionnel : l'anisotropie sert à l'interprétation.

---

## Onglet Krigeage

L'onglet **Krigeage** (*Kriging*, «3. Krigeage ordinaire» / *3. Ordinary kriging*) interpole les valeurs sur une grille régulière à l'aide du variogramme, produit aussi la carte de l'incertitude et ajoute les rasters au projet.

### Le krigeage ordinaire

Le panneau exécute un **krigeage ordinaire** (moyenne locale constante mais inconnue), adapté à la plupart des données archéologiques. Pour chaque cellule il utilise les **20 points les plus proches**, trouvés avec un KD-tree ; ce nombre ne se modifie pas depuis le panneau. Le cokrigeage, le krigeage spatio-temporel et le krigeage par tuiles pour les très grands jeux de données n'existent que comme algorithmes Processing du plugin GeoArchaeo autonome et ne sont pas disponibles dans PyArchInit.

### Exécution du krigeage

1. Ouvrir l'onglet **Krigeage** et lire la ligne d'état du variogramme (voir ci-dessous) ; le bouton **«← Aller au variogramme»** (*← Go to Variogram*) ramène à l'onglet précédent
2. Régler **«Taille de cellule :»** (*Cell size:*), c'est-à-dire la taille d'une cellule en unités du SCR : le panneau propose environ 100 cellules sur le plus grand côté de la couche et affiche en dessous la grille obtenue («Grille : … × … = … cellules» / *Grid: … × … = … cells*)
3. Laisser cochée **«Utiliser le variogramme calculé»** (*Use the calculated variogram*) pour utiliser le variogramme de l'onglet précédent ; si elle est décochée, le variogramme est estimé automatiquement
4. Laisser cochée **«Créer aussi le raster d'incertitude (écart-type)»** (*Also create the uncertainty raster (std. deviation)*) si la carte d'incertitude est nécessaire
5. Cliquer sur **«Lancer le krigeage»** (*Run kriging*) : la barre de progression affiche le pourcentage et **«Annuler»** (*Cancel*) interrompt le calcul

La ligne d'état peut indiquer :

- «Variogramme disponible : …, portée … ✓» (*Variogram available: …, range … ✓*) : le variogramme calculé sur la même couche et le même champ est utilisé
- «Aucun variogramme calculé : il sera estimé automatiquement (modèle sphérique).» (*No variogram calculated: it will be estimated automatically (spherical model).*)
- «Le variogramme a été calculé sur une autre couche/un autre champ : il sera recalculé.» (*The variogram was calculated on another layer/field: it will be recalculated.*), là aussi avec une estimation automatique

> **Grille** : la grille couvre l'emprise de la couche de points et est limitée à **500 cellules par côté**. Si la taille de cellule choisie est trop fine, elle est augmentée automatiquement et la ligne de la grille le signale («taille de cellule minimale … (max. 500 cellules par côté)» / *minimum cell size … (max 500 cells per side)*). Au-delà de **40 000 cellules**, la ligne devient orange et, au lancement, le panneau demande une confirmation car le calcul peut prendre quelques minutes.

<!-- IMAGE: Rasters du krigeage et metriques de validation croisee -->
> **Fig. 7** : Les rasters de l'estimation et de l'incertitude sur la carte, avec le cadre des résultats et la validation croisée

### Résultats du krigeage

Le krigeage ajoute au projet deux rasters GeoTIFF dans le SCR de la couche de points :

| Couche | Contenu | Style |
|--------|---------|-------|
| `Kriging_<champ>` | Valeur estimée dans chaque cellule | Rampe de couleurs du bleu au rouge en passant par le jaune ; visible |
| `Kriging_<champ>_uncertainty` | Écart-type de l'estimation (incertitude) | Rampe du jaune clair au rouge ; ajoutée en haut de la liste des couches mais masquée |

Avec le panneau en italien, le second raster s'appelle `Kriging_<champ>_incertezza`. Les fichiers sont écrits dans un **dossier temporaire** : pour les conserver, les exporter depuis le menu contextuel de la couche (**Exporter**).

Le cadre des résultats résume les points utilisés, la taille de la grille, la taille de cellule, le modèle et la portée ; le graphique montre la carte des valeurs estimées et celle de l'incertitude, avec les points échantillons superposés.

### Validation croisée leave-one-out

Après le krigeage, GeoArchaeo effectue une **validation croisée leave-one-out** : chaque point est retiré puis réestimé à partir des autres (sur 200 points au maximum, tirés au hasard dans les grands jeux de données). Les métriques apparaissent dans le cadre des résultats :

| Métrique | Signification | Valeur souhaitable |
|----------|---------------|--------------------|
| **RMSE** (*root mean squared error*) | Erreur typique de l'estimation | La plus basse possible, comparée à l'écart-type des données |
| **MAE** (*mean absolute error*) | Erreur moyenne en valeur absolue | La plus basse possible |
| **ME** (*mean error, bias*) | Surestimation ou sous-estimation systématique | Proche de 0 |
| **R²** (*explained variance*) | Capacité prédictive | À partir de 0,5 bonne, sous 0,2 faible |
| **MSDR** (*standardized error*) | Réalisme de l'incertitude estimée | Environ 1 ; au-dessus de 1,5 incertitude sous-estimée, sous 0,5 surestimée |

Le panneau ajoute un jugement en mots sur la capacité prédictive (bonne, modérée ou faible) et, le cas échéant, sur le MSDR.

> **Note** : le krigeage s'exécute dans un **thread en arrière-plan**, ce qui permet à l'interface QGIS de rester utilisable pendant le calcul ; la barre de progression indique l'état du traitement.

---

## Onglet Motifs (ML)

L'onglet **Motifs (ML)** (*Patterns (ML)*, «4. Reconnaissance de motifs (apprentissage automatique)» / *4. Pattern recognition (machine learning)*) regroupe les points selon leur position et leurs attributs numériques, ou détecte les anomalies, et crée une couche avec l'étiquette de chaque point.

### Méthodes disponibles

| Méthode (entrée de la liste) | Ce qu'elle fait | Paramètres |
|------------------------------|-----------------|------------|
| **«K-Means – groupes par similarité»** (*K-Means – groups by similarity*) | Répartit les points en K groupes semblables par position et attributs | **«Nombre de groupes (0 = automatique) :»** (*Number of groups (0 = automatic):*) ; avec 0, le nombre est choisi d'après le nombre de points (de 2 à 5) |
| **«DBSCAN – groupes par densité (trouve aussi les points isolés)»** (*DBSCAN – groups by density (also finds isolated points)*) | Trouve des groupes de densité sans en fixer le nombre ; les points isolés forment le groupe «Isolés / bruit» (*Isolated / noise*) | Automatiques |
| **«Isolation Forest – détection d'anomalies»** (*Isolation Forest – anomaly detection*) | Signale comme «Anomalie» (*Anomaly*) environ 10 % des points les plus différents des autres ; les autres sont «Normal» (*Normal*) | Automatiques |

### Exécution

1. Ouvrir l'onglet **Motifs (ML)**
2. Dans la liste **«Couches de points à analyser (une ou plusieurs) :»** (*Point layers to analyse (one or more):*), sélectionner une ou plusieurs couches de points (si rien n'est sélectionné, la couche d'entrée est présélectionnée)
3. Choisir la **«Méthode :»** (*Method:*)
4. Pour K-Means seulement, régler **«Nombre de groupes (0 = automatique) :»**
5. Cliquer sur **«Lancer la reconnaissance de motifs»** (*Run pattern recognition*)

Les variables analysées sont les **coordonnées X et Y** et **tous les champs numériques** des couches sélectionnées, standardisés ; les valeurs manquantes sont remplacées par la moyenne du champ. Ce n'est donc pas seulement le champ de valeur choisi en haut qui est utilisé : tous les champs numériques entrent en jeu, y compris les identifiants et les numéros d'ordre, et s'ils faussent les groupes, mieux vaut analyser une copie de la couche ne contenant que les champs utiles. Pour analyser plusieurs couches ensemble, elles doivent avoir les mêmes champs numériques dans le même ordre et le même SCR (la couche créée utilise le SCR de la première couche sélectionnée).

<!-- IMAGE: Onglet Motifs (ML) avec la couche des groupes -->
> **Fig. 8** : L'onglet Motifs (ML) avec le graphique des groupes et la couche `ML_groups` sur la carte

### Résultats

- Le cadre des résultats indique la méthode, le nombre de groupes et le nombre de points de chacun (par exemple «Groupe A (n=42)» / *Group A (n=42)*)
- Le graphique montre les points dans le plan des deux premières composantes principales (PC1, PC2) des variables, colorés par groupe
- Une couche de points temporaire est créée, `ML_groups` (K-Means, DBSCAN) ou `ML_anomalies` (Isolation Forest), avec une légende par catégorie : gris pour les points isolés, rouge et plus gros pour les anomalies ; avec le panneau en italien les noms sont `Gruppi_ML` et `Anomalie_ML`

| Champ | Contenu |
|-------|---------|
| `cluster_id` | Numéro du groupe (-1 = isolés avec DBSCAN ; 1 = anomalie et 0 = normal avec Isolation Forest) |
| `cluster_name` | Nom lisible, par exemple «Group A (n=42)», «Isolated / noise (n=5)», «Anomaly (n=12)» |
| `cluster_size` | Nombre de points du groupe |
| `method` | Méthode utilisée |
| `x_coord`, `y_coord` | Coordonnées du point |

### Classification supervisée

Sous la méthode, le panneau rappelle que la classification supervisée (Random Forest avec un champ d'étiquettes) se trouve dans **Processing → GeoArchaeo**. Cet algorithme appartient au plugin GeoArchaeo autonome : dans PyArchInit, le fournisseur Processing de GeoArchaeo n'est pas enregistré, la Random Forest n'est donc pas disponible. Pour l'utiliser, il faut le plugin GeoArchaeo séparé.

---

## Onglet Échantillonnage

L'onglet **Échantillonnage** (*Sampling*, «5. Nouveaux points d'échantillonnage» / *5. New sampling locations*) suggère où échantillonner ou fouiller à l'avenir à partir des points existants et crée une couche avec les points proposés.

### Critères d'échantillonnage

| Critère (entrée de la liste) | Comment il choisit les points | Quand l'utiliser |
|------------------------------|-------------------------------|------------------|
| **«Couverture (maximin)»** (*Coverage (maximin)*) | Chaque nouveau point est le plus éloigné possible de tous les autres | Combler les vides de façon uniforme |
| **«Réduction de l'incertitude (variance de krigeage)»** (*Uncertainty reduction (kriging variance)*) | Chaque nouveau point va là où la variance de krigeage est maximale | Réduire l'erreur du krigeage là où elle est la plus forte |
| **«Grille stratifiée»** (*Stratified grid*) | Une position par cellule d'une grille régulière, avec une légère perturbation aléatoire | Couverture régulière d'une zone définie |
| **«Adaptatif (zones moins denses)»** (*Adaptive (sparser areas)*) | Tirage aléatoire avec une probabilité plus forte là où il y a peu de points | Favoriser les zones les moins échantillonnées en gardant une part d'aléatoire |

Le critère «Réduction de l'incertitude» utilise le variogramme calculé s'il porte sur la même couche et le même champ et si «Utiliser le variogramme calculé» est cochée dans l'onglet Krigeage ; sinon il utilise un modèle générique fondé sur la distance typique entre les points.

### Conception du plan d'échantillonnage

1. Vérifier **«Points existants :»** (*Existing points:*) : c'est la couche choisie en haut dans le groupe «Données d'entrée» (le champ numérique n'est pas nécessaire pour l'échantillonnage)
2. Facultatif : choisir dans **«Zone d'étude (polygone, facultatif) :»** (*Study area (polygon, optional):*) une couche de polygones ; tous ses polygones sont fusionnés et reprojetés dans le SCR des points, même si la couche est dans un autre SCR
3. Régler **«Nouveaux points à proposer :»** (*New points to propose:*) (de 1 à 500, 10 par défaut)
4. Choisir le **«Critère :»** (*Criterion:*) : sa description apparaît sous la liste
5. Cliquer sur **«Calculer les nouveaux points»** (*Calculate new points*)

Sans zone d'étude, les points sont cherchés dans le rectangle qui contient les points existants, élargi de 20 % de chaque côté.

<!-- IMAGE: Nouveaux points d'echantillonnage proposes -->
> **Fig. 9** : Les nouveaux points d'échantillonnage (étoiles jaunes) proposés à l'intérieur de la zone d'étude

### Résultats de l'échantillonnage

- Le cadre des résultats indique combien de points ont été proposés et avec quel critère ; en dessous, le tableau «Coordonnées des points proposés :» (*Coordinates of the proposed points:*) liste le numéro, X et Y
- La couche de points temporaire `New_sampling_points` est créée (`Nuovi_punti_campionamento` avec le panneau en italien), avec un symbole en étoile jaune et les champs `point_id`, `x_coord`, `y_coord` et `type` (valeur `suggested`)

---

## Onglet Rapport

L'onglet **Rapport** (*Report*, «6. Rapport» / *6. Report*) rassemble dans un seul document les analyses effectuées pendant la session : statistiques, graphiques interactifs, paramètres et validation.

### Contenu du rapport

Dans le groupe **«Sections à inclure»** (*Sections to include*), chaque section est marquée «disponible» (*available*) ou «pas encore calculé» (*not yet calculated*) ; les sections non calculées ne peuvent pas être choisies.

| Section | Contenu |
|---------|---------|
| **Statistiques descriptives** (*Descriptive statistics*) | Couche et champ, tableau des statistiques avec la lecture en mots, histogramme |
| **Variogramme** (*Variogram*) | Modèle, pépite, palier, portée, RMSE, distance maximale, interprétation, graphique |
| **Krigeage et validation croisée** (*Kriging and cross-validation*) | Méthode, taille de cellule, dimensions de la grille, métriques de validation croisée, graphique |
| **Reconnaissance de motifs** (*Pattern recognition*) | Couches analysées, groupes avec leur nombre de points, graphique |
| **Nouveaux points d'échantillonnage** (*New sampling locations*) | Critère, couche, tableau des coordonnées |

Chaque section contient la **dernière** analyse de son type effectuée pendant la session.

### Génération du rapport

1. Effectuer les analyses souhaitées dans les autres onglets
2. Ouvrir l'onglet **Rapport** et laisser cochées les sections à inclure (elles le sont par défaut)
3. Cliquer sur **«Enregistrer le rapport HTML»** (*Save HTML report*) ou sur **«Enregistrer le rapport PDF»** (*Save PDF report*) et choisir le nom du fichier

À l'enregistrement, le panneau affiche aussi un aperçu du rapport sans graphiques ; la note «Aperçu : les graphiques interactifs sont inclus dans le fichier HTML enregistré.» (*Preview: the interactive charts are included in the saved HTML file.*) rappelle où ils se trouvent.

<!-- IMAGE: Rapport HTML de GeoArchaeo ouvert dans le navigateur -->
> **Fig. 10** : Un rapport HTML de GeoArchaeo avec les graphiques interactifs, ouvert dans le navigateur

### Exportation

| Format | Contenu | Remarques |
|--------|---------|-----------|
| **HTML** (`geoarchaeo_report.html`) | Texte, tableaux et **graphiques interactifs** | Le fichier est autonome (la bibliothèque des graphiques est incluse, il fonctionne aussi hors ligne) et s'ouvre aussitôt dans le navigateur |
| **PDF** (`geoarchaeo_report.pdf`) | Texte et tableaux, **sans graphiques** | Si le PDF ne peut pas être créé, enregistrer le rapport HTML et l'imprimer en PDF depuis le navigateur |

Si aucune analyse n'a été effectuée, «Aucune analyse disponible : lancez d'abord au moins une analyse.» (*No analysis available: run at least one analysis first.*) apparaît ; si aucune section n'est cochée, «Sélectionnez au moins une section» (*Select at least one section*).

---

## Flux de travail opérationnel

Un exemple complet avec les données d'exemple fournies avec le module (panneau en anglais).

### Étape 1 : Préparation des données

1. Ouvrir GeoArchaeo depuis la barre d'outils PyArchInit
2. Cliquer sur **«Charger des données d'exemple»** (*Load example data*) et confirmer avec **OK** (les GeoPackage et les GeoJSON sont chargés)
3. Dans le groupe «Données d'entrée», choisir la couche `villa_ceramica` et le champ `ceramic_count`
4. Vérifier le résumé : 500 points valides sur 500, SCR EPSG:32633

### Étape 2 : Exploration des données

1. Onglet **Données** → **«Calculer les statistiques»** (*Calculate statistics*)
2. Lire l'asymétrie et les valeurs aberrantes ; en cas de forte asymétrie à droite, envisager une transformation logarithmique

### Étape 3 : Analyse du variogramme

1. Onglet **Variogramme** → **«Auto»** pour la distance maximale, modèle **«Sphérique (recommandé)»** (*Spherical (recommended)*) → **«Calculer le variogramme»** (*Calculate variogram*)
2. Recommencer avec **«Exponentiel»** (*Exponential*) et comparer le RMSE de l'ajustement
3. Facultatif : recalculer avec **«Vérifier l'anisotropie (variogrammes directionnels)»**
4. Recalculer en dernier le modèle retenu et noter pépite, palier et portée

### Étape 4 : Interpolation

1. Onglet **Krigeage** : vérifier la ligne «Variogramme disponible … ✓» (*Variogram available … ✓*)
2. Garder la taille de cellule proposée ou indiquer 1 (mètre)
3. **«Lancer le krigeage»** (*Run kriging*)
4. Examiner les rasters `Kriging_ceramic_count` et `Kriging_ceramic_count_uncertainty` ainsi que les valeurs de R² et de MSDR

### Étape 5 : Motifs et échantillonnage (facultatif)

1. Onglet **Motifs (ML)** : dans la liste, ne garder sélectionnée que `necropoli`, méthode DBSCAN → **«Lancer la reconnaissance de motifs»** (*Run pattern recognition*) ; la couche `ML_groups` montre les groupes de tombes et les points isolés
2. En haut, choisir la couche `ricognizione_survey` (champ `densita_mq`) ; onglet **Échantillonnage** : zone d'étude `area_studio`, 10 points, critère «Couverture (maximin)» (*Coverage (maximin)*) → **«Calculer les nouveaux points»** (*Calculate new points*)

### Étape 6 : Rapport

1. Onglet **Rapport** : laisser cochées les sections disponibles
2. **«Enregistrer le rapport HTML»** (*Save HTML report*) : le rapport s'ouvre dans le navigateur avec les graphiques interactifs
3. Exporter les rasters et les couches temporaires à conserver

---

## Dépannage

### Problèmes courants

| Problème | Cause | Solution |
|----------|-------|----------|
| «Aucune couche de points dans le projet…» (*No point layer in the project: load one or use the example data.*) | Le projet ne contient aucune couche de points | Ajouter une couche de points ou utiliser **«Charger des données d'exemple»** |
| «La couche n'a pas de champs numériques…» (*The layer has no numeric fields…*) | Le champ à analyser est de type texte | Le convertir en nombre avec la calculatrice de champs |
| «Au moins 5 points avec une valeur valide sont nécessaires…» (*At least 5 points with a valid value are required (found …)*) | Trop de valeurs NULL ou non numériques | Vérifier la table d'attributs ou choisir un autre champ |
| Avertissement «SCR géographique (degrés)» (*geographic CRS (degrees)*) | La couche n'est pas dans un SCR projeté | Reprojeter la couche, par exemple en UTM, et refaire l'analyse |
| Erreur «No point pairs within the maximum distance…» | Distance maximale du variogramme trop petite | Augmenter **«Distance maximale :»** ou utiliser **«Auto»** |
| «Pas assez de paires pour les variogrammes directionnels.» (*Not enough pairs for directional variograms.*) | Trop peu de paires par direction | Augmenter la distance maximale ou renoncer à la vérification de l'anisotropie |
| Krigeage lent, demande de confirmation ou «Mémoire insuffisante : augmentez la taille de cellule.» (*Out of memory: increase the cell size.*) | Grille comptant trop de cellules | Augmenter **«Taille de cellule :»** |
| R² faible dans la validation croisée | Faible corrélation spatiale ou trop de bruit | Considérer la carte comme indicative et consulter le raster d'incertitude |
| DBSCAN place presque tous les points dans «Isolés / bruit» (*Isolated / noise*) | Densité uniforme ou trop de variables | Essayer K-Means ou réduire les champs numériques |
| «Machine Learning features not available. Please install scikit-learn.» | scikit-learn est absent | Installer scikit-learn dans l'environnement Python de QGIS |
| «Plotly visualization not available. Please install plotly.» | Plotly est absent | Installer plotly dans l'environnement Python de QGIS |
| Graphique uniquement en image statique | QtWebEngine non disponible | Utiliser **«Ouvrir le graphique interactif dans le navigateur»** (*Open interactive chart in browser*) |
| «Impossible de créer le PDF…» (*Cannot create the PDF…*) | Erreur d'impression du PDF | Enregistrer le rapport HTML et l'imprimer depuis le navigateur |
| Panneau invisible | Panneau fermé | Le rouvrir depuis la barre d'outils ou le menu pyArchInit : les résultats de la session sont toujours là |

### Erreurs fréquentes

- **«Une analyse est déjà en cours…»** (*An analysis is already running: wait for it to finish or cancel it.*) : attendre la fin du calcul ou appuyer sur «Annuler»
- **«Analyse annulée»** (*Analysis cancelled*) : l'analyse a été interrompue avec «Annuler» et n'a produit aucun résultat
- **«Sélectionnez au moins une couche»** (*Select at least one layer*, onglet Motifs) : sélectionner au moins une couche dans la liste
- **«Sélectionnez la couche des points existants (en haut)»** (*Select the existing points layer (above)*, onglet Échantillonnage) : choisir la couche dans le groupe «Données d'entrée»
- **«Sélectionnez une couche de points et un champ numérique (en haut du panneau)»** (*Select a point layer and a numeric field (at the top of the panel)*) : compléter le choix dans le groupe «Données d'entrée»

### Performances

- Les analyses s'exécutent dans un **thread en arrière-plan** : QGIS reste utilisable et le calcul peut être annulé
- Le variogramme utilise au maximum 3000 points (sous-échantillon aléatoire), la validation croisée au maximum 200
- Le krigeage utilise les 20 points les plus proches de chaque cellule : le temps dépend surtout du nombre de cellules
- La grille est limitée à 500 × 500 cellules ; au-delà de 40 000 cellules, le panneau demande une confirmation
- Avec de grands jeux de données (par exemple les 4800 points de `geofisica_survey`), augmenter la taille de cellule

---

## Notes techniques

### Version et origine

- Le module `modules/geoarchaeo/` est aligné sur **GeoArchaeo 1.3.1**, le plugin autonome d'Enzo Cocca (github.com/enzococca/GeoArchaeo)
- Seul le panneau est intégré à PyArchInit : le fournisseur Processing de GeoArchaeo (cokrigeage, krigeage spatio-temporel, krigeage par tuiles, analyse compositionnelle, Random Forest) n'est **pas** enregistré
- Le module est compatible avec QGIS 3 (Qt5) et QGIS 4 (Qt6)

### Dépendances

| Bibliothèque | Utilisation |
|--------------|-------------|
| **NumPy** | Calculs numériques |
| **SciPy** | Ajustement des modèles de variogramme, recherche des voisins (KD-tree), statistiques |
| **scikit-learn** | K-Means, DBSCAN, Isolation Forest, composantes principales (nécessaire pour l'onglet Motifs) |
| **Plotly** | Graphiques interactifs dans le panneau et dans le rapport HTML |
| **Matplotlib** | Aperçus statiques des graphiques quand QtWebEngine est absent |
| **QtWebEngine** (facultatif) | Graphiques interactifs directement dans le panneau |
| **threadpoolctl** (facultatif) | Limite les threads de calcul pendant les analyses en arrière-plan |
| **GDAL** | Écriture des rasters GeoTIFF (inclus dans QGIS) |

### Systèmes de référence

- Les distances (distance maximale, portée, taille de cellule) sont exprimées dans les **unités du SCR de la couche de points**
- Utiliser un **SCR projeté** en mètres : avec un SCR géographique, le résumé avertit et le variogramme et le krigeage demandent une confirmation
- Les rasters du krigeage et les couches créées utilisent le SCR de la couche de points (dans l'onglet Motifs, celui de la première couche sélectionnée)
- La zone d'étude est reprojetée automatiquement dans le SCR des points

### Couches et fichiers produits

| Produit | Type | Emplacement |
|---------|------|-------------|
| `Kriging_<champ>`, `Kriging_<champ>_uncertainty` | Raster GeoTIFF (compression LZW) | Dossier temporaire du système |
| `ML_groups` / `ML_anomalies` | Couche de points temporaire (en mémoire) | Uniquement dans le projet ouvert |
| `New_sampling_points` | Couche de points temporaire (en mémoire) | Uniquement dans le projet ouvert |
| Rapport | HTML ou PDF | Chemin choisi à l'enregistrement |

Les rasters et les couches temporaires doivent être exportés (menu contextuel de la couche → **Exporter**) pour ne pas être perdus à la fermeture du projet. Les noms des couches suivent la langue du panneau au moment du calcul.

### Paramètres

- La langue du panneau est enregistrée dans les paramètres de QGIS (clé `GeoArchaeo/language`)
- Les résultats restent en mémoire tant que QGIS est ouvert : fermer le panneau ne les efface pas

---

> **Note** : GeoArchaeo est en développement constant. Pour signaler des bugs ou proposer des améliorations, utiliser le système de suivi des tickets (issues) du projet PyArchInit sur GitHub.
