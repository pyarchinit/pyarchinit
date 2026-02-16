# PyArchInit - GeoArchaeo - Analyse Geostatistique

## Table des matieres
1. [Introduction](#introduction)
2. [Acces a l'outil](#acces-a-loutil)
3. [Interface utilisateur](#interface-utilisateur)
4. [Onglet Donnees](#onglet-donnees)
5. [Onglet Variogramme](#onglet-variogramme)
6. [Onglet Krigeage](#onglet-krigeage)
7. [Onglet Machine Learning](#onglet-machine-learning)
8. [Onglet Echantillonnage](#onglet-echantillonnage)
9. [Onglet Rapport](#onglet-rapport)
10. [Flux de travail operationnel](#flux-de-travail-operationnel)
11. [Depannage](#depannage)
12. [Notes techniques](#notes-techniques)

---

## Introduction

**GeoArchaeo** est le module d'analyse geostatistique integre a PyArchInit. Il fournit un ensemble complet d'outils pour l'analyse spatiale des donnees archeologiques, de la modelisation des variogrammes a l'interpolation par krigeage, en passant par les predictions par apprentissage automatique et la conception de strategies d'echantillonnage.

<!-- VIDEO: Introduction a GeoArchaeo -->
> **Tutoriel video**: [Inserer le lien video introduction GeoArchaeo]

### Pourquoi l'analyse geostatistique en archeologie?

L'analyse geostatistique permet de:

- **Interpoler** des valeurs entre des points d'echantillonnage connus, creant des surfaces continues a partir de donnees discretes
- **Quantifier** la correlation spatiale dans les donnees archeologiques (ex. densite de vestiges, epaisseur des couches)
- **Predire** les distributions spatiales dans les zones non encore fouillees
- **Optimiser** les strategies d'echantillonnage pour les prospections futures
- **Generer** des rapports analytiques complets pour la documentation scientifique

### Apercu du flux de travail

```
1. Charger les donnees   2. Variogramme         3. Krigeage/ML
   (Onglet Donnees)         (Onglet Variogramme)   (Onglet Krigeage/ML)
        |                      |                      |
   Selectionner           Calculer et            Interpolation ou
   couche et champs       modeliser le           prediction spatiale
                          variogramme
                               |                      |
                          4. Echantillonnage     5. Rapport
                             (Onglet Echant.)       (Onglet Rapport)
                                  |                      |
                             Concevoir            Generer le rapport
                             la strategie         d'analyse
```

---

## Acces a l'outil

GeoArchaeo est accessible depuis la barre d'outils PyArchInit via le menu deroulant des Outils d'analyse.

### Depuis la barre d'outils

1. Reperer le bouton **Outils d'analyse** (icone deroulante) dans la barre d'outils PyArchInit
2. Cliquer sur la fleche du menu deroulant
3. Selectionner **GeoArchaeo** dans la liste

<!-- IMAGE: Bouton Outils d'analyse dans la barre d'outils -->
> **Fig. 1**: Le menu deroulant Outils d'analyse dans la barre d'outils PyArchInit

Le panneau GeoArchaeo apparait comme un **widget ancrable** dans l'interface QGIS. Il peut etre deplace, redimensionne ou detache comme tout autre panneau QGIS.

<!-- IMAGE: Panneau GeoArchaeo ancre dans QGIS -->
> **Fig. 2**: Le panneau GeoArchaeo ancre dans la fenetre QGIS

### Selecteur de langue

Le panneau GeoArchaeo inclut un **selecteur de langue** en haut, permettant de changer la langue de l'interface sans redemarrer QGIS. Les langues prises en charge incluent l'italien, l'anglais, l'allemand, le francais, l'espagnol, l'arabe, le catalan, le roumain, le portugais et le grec.

---

## Interface utilisateur

Le panneau GeoArchaeo est organise en **6 onglets principaux**, chacun dedie a une phase du flux de travail d'analyse geostatistique.

| Onglet | Icone | Fonction |
|--------|-------|----------|
| **Donnees** | Tableau | Charger et explorer les donnees spatiales depuis les couches QGIS |
| **Variogramme** | Graphique | Calculer et modeliser des variogrammes experimentaux |
| **Krigeage** | Grille | Effectuer une interpolation par krigeage (ordinaire, universel) |
| **ML** | Cerveau | Predictions spatiales par apprentissage automatique |
| **Echantillonnage** | Cible | Concevoir des strategies d'echantillonnage pour les prospections archeologiques |
| **Rapport** | Document | Generer des rapports d'analyse |

<!-- IMAGE: Apercu des 6 onglets GeoArchaeo -->
> **Fig. 3**: Les six onglets du panneau GeoArchaeo

### Barre d'outils du panneau

En haut du panneau, vous trouverez:

- **Selecteur de langue**: Menu deroulant pour changer la langue de l'interface
- **Charger les donnees d'exemple**: Bouton pour charger un jeu de donnees de test
- **Aide**: Bouton pour acceder a la documentation

---

## Onglet Donnees

L'onglet **Donnees** est le point de depart de toute analyse geostatistique. Il permet de charger et de visualiser les donnees spatiales disponibles dans les couches QGIS.

### Chargement des donnees

1. Ouvrir l'onglet **Donnees**
2. Selectionner une **couche vectorielle** dans le menu deroulant (toutes les couches ponctuelles du projet QGIS sont listees)
3. Selectionner le **champ d'analyse** (le champ numerique a analyser)
4. Cliquer sur **Charger les donnees**

<!-- IMAGE: Onglet Donnees avec couche et champ selectionnes -->
> **Fig. 4**: L'onglet Donnees avec une couche et un champ d'analyse selectionnes

### Donnees d'exemple

Pour vous familiariser avec l'outil, vous pouvez charger un **jeu de donnees d'exemple** en cliquant sur le bouton dedie. Le jeu de donnees d'exemple contient des donnees archeologiques simulees avec des coordonnees et des valeurs numeriques adaptees a l'analyse geostatistique.

### Exploration des donnees

Apres le chargement, l'onglet affiche:

| Information | Description |
|-------------|-------------|
| **Nombre de points** | Total des points charges |
| **Etendue** | Emprise du jeu de donnees (xmin, ymin, xmax, ymax) |
| **Statistiques** | Moyenne, mediane, ecart-type, min, max |
| **Apercu** | Tableau avec les premieres lignes du jeu de donnees |

### Exigences relatives aux donnees

- La couche doit etre une **couche vectorielle ponctuelle**
- Le champ d'analyse doit contenir des **valeurs numeriques**
- Les points doivent avoir des **coordonnees valides** dans le systeme de reference du projet
- Au moins **30 points** sont recommandes pour une analyse geostatistique significative

---

## Onglet Variogramme

L'onglet **Variogramme** permet de calculer et de modeliser des variogrammes experimentaux, qui decrivent la structure de la correlation spatiale dans les donnees.

### Qu'est-ce qu'un variogramme?

Un variogramme est un graphique qui montre comment la **variance** entre paires de points change en fonction de la **distance** qui les separe. Les parametres cles sont:

| Parametre | Description |
|-----------|-------------|
| **Nugget** | Variance a distance nulle (erreur de mesure + variabilite a micro-echelle) |
| **Sill** | Variance maximale atteinte (plateau du variogramme) |
| **Portee (Range)** | Distance au-dela de laquelle il n'y a plus de correlation spatiale |

### Calcul du variogramme experimental

1. S'assurer que les donnees sont chargees dans l'onglet Donnees
2. Ouvrir l'onglet **Variogramme**
3. Definir les parametres:
   - **Nombre de lags**: Nombre d'intervalles de distance (defaut: 15)
   - **Distance maximale**: Distance maximale a considerer (defaut: auto)
   - **Tolerance angulaire**: Pour les variogrammes directionnels (defaut: omnidirectionnel)
4. Cliquer sur **Calculer le variogramme**

<!-- IMAGE: Variogramme experimental calcule -->
> **Fig. 5**: Un variogramme experimental calcule a partir de donnees archeologiques

### Modelisation du variogramme

Apres le calcul du variogramme experimental, il est possible d'ajuster un **modele theorique**:

1. Selectionner le **type de modele**:
   - **Spherique**: Le modele le plus courant, atteint le sill a une distance finie
   - **Exponentiel**: Atteint le sill de maniere asymptotique
   - **Gaussien**: Transition graduelle, adapte aux phenomenes tres reguliers
   - **Lineaire**: Variogramme sans sill defini
2. Cliquer sur **Ajuster le modele**
3. Verifier les parametres estimes (nugget, sill, portee) et la qualite de l'ajustement

<!-- IMAGE: Modele de variogramme ajuste -->
> **Fig. 6**: Modele spherique ajuste au variogramme experimental

### Variogrammes directionnels

Pour verifier l'**anisotropie** (variation de la structure spatiale dans differentes directions):

1. Definir une **tolerance angulaire** (ex. 22,5 degres)
2. Selectionner les **directions** a analyser (0, 45, 90, 135 degres)
3. Comparer les variogrammes dans les differentes directions

---

## Onglet Krigeage

L'onglet **Krigeage** permet d'effectuer une interpolation par krigeage, la methode geostatistique de reference pour la prediction spatiale optimale.

### Types de krigeage disponibles

| Type | Description | Quand l'utiliser |
|------|-------------|-----------------|
| **Krigeage ordinaire** | Suppose une moyenne locale constante mais inconnue | Cas le plus courant, donnees stationnaires |
| **Krigeage universel** | Tient compte d'une tendance spatiale (derive) | Lorsque les donnees montrent une tendance directionnelle |

### Execution du krigeage

1. S'assurer qu'un variogramme a ete modelise dans l'onglet Variogramme
2. Ouvrir l'onglet **Krigeage**
3. Selectionner le **type de krigeage** (ordinaire ou universel)
4. Definir les parametres de la grille de sortie:
   - **Resolution**: Taille des cellules de la grille (en unites du CRS)
   - **Etendue**: Automatique depuis le jeu de donnees ou personnalisee
5. Definir les parametres de krigeage:
   - **Points minimum**: Nombre minimum de points voisins a utiliser
   - **Points maximum**: Nombre maximum de points voisins a utiliser
   - **Rayon de recherche**: Distance maximale pour les points voisins
6. Cliquer sur **Executer le krigeage**

<!-- IMAGE: Resultat de l'interpolation par krigeage -->
> **Fig. 7**: Carte d'interpolation par krigeage avec la grille de prediction

### Resultats du krigeage

L'analyse produit deux couches raster:

- **Prediction**: Les valeurs interpolees sur la grille
- **Variance de krigeage**: L'incertitude de la prediction pour chaque cellule

Les couches sont automatiquement ajoutees au projet QGIS et affichees sur la carte.

> **Note**: L'analyse est executee dans un **thread en arriere-plan**, ce qui permet a l'interface QGIS de rester utilisable pendant le calcul. Une barre de progression indique l'etat du traitement.

---

## Onglet Machine Learning

L'onglet **ML** propose des methodes d'apprentissage automatique pour les predictions spatiales, en alternative ou en complement du krigeage.

### Algorithmes disponibles

| Algorithme | Description | Avantages |
|------------|-------------|-----------|
| **Random Forest** | Ensemble d'arbres de decision | Robuste, gere les relations non lineaires |
| **Gradient Boosting** | Arbres de decision sequentiels | Haute precision, adapte aux motifs complexes |
| **SVR** | Regression par vecteurs de support | Bon avec peu de donnees, noyaux flexibles |

### Flux de travail ML

1. Ouvrir l'onglet **ML**
2. Selectionner l'**algorithme** souhaite
3. Configurer les **variables predictives**:
   - Coordonnees (X, Y)
   - Champs supplementaires de la couche (ex. altitude, pente, distance a une riviere)
4. Definir les **parametres** de l'algorithme (ou utiliser les valeurs par defaut)
5. Selectionner la methode de **validation**:
   - Validation croisee k-fold (defaut: 5 folds)
   - Hold-out (pourcentage de test)
6. Cliquer sur **Entrainer le modele**

<!-- IMAGE: Configuration du modele ML -->
> **Fig. 8**: Configuration d'un modele Random Forest dans l'onglet ML

### Resultats ML

| Resultat | Description |
|----------|-------------|
| **Carte de prediction** | Couche raster avec les valeurs predites |
| **Importance des variables** | Graphique de l'importance relative des variables predictives |
| **Metriques de validation** | R-carre, RMSE, MAE de la validation croisee |
| **Graphique des residus** | Nuage de points des valeurs observees vs predites |

### Comparaison Krigeage vs ML

Pour comparer les resultats:

1. Executer le krigeage et le ML sur les memes donnees
2. Comparer les metriques de validation dans l'onglet Rapport
3. Visualiser les cartes de differences

---

## Onglet Echantillonnage

L'onglet **Echantillonnage** permet de concevoir des strategies d'echantillonnage optimales pour les prospections archeologiques futures.

### Strategies d'echantillonnage

| Strategie | Description | Quand l'utiliser |
|-----------|-------------|-----------------|
| **Aleatoire simple** | Points distribues aleatoirement dans la zone | En l'absence d'informations prealables |
| **Aleatoire stratifie** | Points aleatoires dans des strates definies | Lorsque la zone a des secteurs aux caracteristiques differentes |
| **Grille reguliere** | Points sur une grille reguliere | Pour une couverture uniforme de la zone |
| **Optimise** | Points positionnes pour minimiser la variance de krigeage | Lorsqu'on dispose d'un variogramme |

### Conception du plan d'echantillonnage

1. Ouvrir l'onglet **Echantillonnage**
2. Selectionner la **strategie** d'echantillonnage
3. Definir le **nombre de points** souhaite
4. Definir la **zone d'etude**:
   - A partir de l'etendue de la couche actuelle
   - A partir d'une couche polygonale
   - En dessinant manuellement sur la carte
5. Definir d'eventuelles **contraintes**:
   - Distance minimale entre les points
   - Zones d'exclusion
6. Cliquer sur **Generer l'echantillonnage**

<!-- IMAGE: Points d'echantillonnage generes -->
> **Fig. 9**: Points d'echantillonnage optimise superposes a la carte de la zone d'etude

### Resultats de l'echantillonnage

- Une **couche vectorielle ponctuelle** avec les points d'echantillonnage est ajoutee au projet QGIS
- Une **table attributaire** avec les coordonnees et les identifiants des points
- Un **rapport** avec les statistiques de la strategie (couverture, distances, etc.)

---

## Onglet Rapport

L'onglet **Rapport** permet de generer des rapports complets de l'analyse geostatistique.

### Contenu du rapport

Le rapport inclut automatiquement toutes les analyses effectuees durant la session:

| Section | Contenu |
|---------|---------|
| **Resume** | Vue d'ensemble du jeu de donnees et des analyses effectuees |
| **Donnees** | Statistiques descriptives, distribution, carte des points |
| **Variogramme** | Variogramme experimental, modele, parametres |
| **Interpolation** | Carte de krigeage/ML, metriques de validation |
| **Echantillonnage** | Strategie, carte des points, statistiques |
| **Conclusions** | Interpretation synthetique des resultats |

### Generation du rapport

1. Ouvrir l'onglet **Rapport**
2. Selectionner les **sections** a inclure (toutes par defaut)
3. Definir le **format de sortie**:
   - PDF (recommande pour la documentation)
   - HTML (pour la consultation interactive)
   - Markdown (pour la modification ulterieure)
4. Saisir d'eventuelles **notes supplementaires** ou commentaires
5. Cliquer sur **Generer le rapport**

<!-- IMAGE: Apercu du rapport genere -->
> **Fig. 10**: Apercu d'un rapport d'analyse geostatistique genere par GeoArchaeo

### Exportation

Le rapport peut etre sauvegarde localement ou exporte dans les formats disponibles. Les images (graphiques, cartes) sont incorporees directement dans le rapport.

---

## Flux de travail operationnel

Voici un flux de travail typique pour une analyse geostatistique complete dans GeoArchaeo:

### Etape 1: Preparation des donnees

1. Charger la couche vectorielle ponctuelle dans QGIS
2. Verifier que le champ numerique a analyser est present et correct
3. Controler le systeme de reference des coordonnees

### Etape 2: Exploration des donnees

1. Ouvrir GeoArchaeo depuis la barre d'outils
2. Dans l'onglet **Donnees**, selectionner la couche et le champ
3. Examiner les statistiques descriptives
4. Verifier la distribution des donnees (rechercher les valeurs aberrantes)

### Etape 3: Analyse du variogramme

1. Dans l'onglet **Variogramme**, calculer le variogramme experimental
2. Essayer differents modeles (spherique, exponentiel, gaussien)
3. Choisir le modele avec le meilleur ajustement
4. Noter les parametres (nugget, sill, portee)

### Etape 4: Interpolation

1. Dans l'onglet **Krigeage**, definir les parametres de la grille
2. Executer le krigeage ordinaire
3. Examiner la carte de prediction et la variance
4. Optionnellement, comparer avec un modele ML dans l'onglet ML

### Etape 5: Echantillonnage (optionnel)

1. Dans l'onglet **Echantillonnage**, concevoir une strategie pour les prospections futures
2. Utiliser le variogramme pour l'echantillonnage optimise

### Etape 6: Rapport

1. Dans l'onglet **Rapport**, generer le rapport final
2. Exporter en PDF pour la documentation

---

## Depannage

### Problemes courants

| Probleme | Cause | Solution |
|----------|-------|----------|
| Aucune couche disponible | Pas de couches ponctuelles dans le projet | Ajouter une couche vectorielle ponctuelle au projet QGIS |
| Pas de champs numeriques | La couche n'a pas de champs numeriques | Verifier la table attributaire de la couche |
| Variogramme plat | Donnees sans correlation spatiale | Verifier les donnees, augmenter la distance maximale |
| Le krigeage echoue | Modele de variogramme non ajuste | Ajuster d'abord un modele dans l'onglet Variogramme |
| Mauvais resultats ML | Donnees insuffisantes ou variables non informatives | Ajouter des variables predictives ou augmenter les donnees |
| Panneau non visible | Widget ferme accidentellement | Rouvrir depuis le menu Outils d'analyse |

### Erreurs frequentes

- **"Donnees insuffisantes"**: Au moins 30 points sont necessaires pour une analyse fiable
- **"Modele de variogramme non defini"**: Ajuster un modele avant d'executer le krigeage
- **"CRS incompatible"**: Toutes les couches doivent utiliser le meme systeme de reference

### Performances

- L'analyse est executee dans un **thread en arriere-plan**: l'interface QGIS reste utilisable
- Pour les tres grands jeux de donnees (>10 000 points), le traitement peut prendre plus de temps
- Il est possible de surveiller la progression via la barre en bas du panneau

---

## Notes techniques

### Dependances

GeoArchaeo utilise les bibliotheques Python suivantes:

| Bibliotheque | Utilisation |
|-------------|-------------|
| **NumPy** | Calculs numeriques et matriciels |
| **SciPy** | Optimisation et ajustement de modeles |
| **scikit-learn** | Algorithmes d'apprentissage automatique |
| **Matplotlib** | Generation de graphiques |

### Systemes de reference

- GeoArchaeo travaille dans le systeme de reference du projet QGIS courant
- Un **CRS projete** (en metres) est recommande pour l'analyse geostatistique
- Les systemes geographiques (en degres) peuvent produire des resultats imprecis

### Exportation des resultats

Les resultats peuvent etre exportes dans divers formats:

- **Couches raster** (GeoTIFF) pour les surfaces interpolees
- **Couches vectorielles** (GeoPackage, Shapefile) pour les points d'echantillonnage
- **Graphiques** (PNG, SVG) pour les variogrammes et diagnostics
- **Rapports** (PDF, HTML, Markdown) pour la documentation

### Integration QGIS

- Les couches de sortie sont automatiquement ajoutees au panneau **Couches** de QGIS
- Le style des couches raster peut etre personnalise via les proprietes de couche QGIS
- Les resultats sont compatibles avec tous les outils d'analyse spatiale de QGIS

---

> **Note**: GeoArchaeo est en developpement actif. Pour signaler des bugs ou suggerer des ameliorations, veuillez utiliser le systeme de suivi des problemes du projet PyArchInit sur GitHub.
