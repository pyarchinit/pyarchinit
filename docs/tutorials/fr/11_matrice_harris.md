# Tutorial 11 : Matrice de Harris

## Introduction

La **Matrice de Harris** (ou diagramme stratigraphique) est un outil fondamental en archéologie pour représenter graphiquement les relations stratigraphiques entre les différentes Unités Stratigraphiques (US). PyArchInit génère automatiquement la Matrice de Harris à partir des rapports stratigraphiques saisis dans les fiches US.

### Qu'est-ce que la Matrice de Harris ?

La Matrice de Harris est un diagramme qui représente :
- La **séquence temporelle** des US (du plus récent en haut au plus ancien en bas)
- Les **relations physiques** entre les US (couvre/couvert par, coupe/coupé par, se lie à)
- La **périodisation** de la fouille (regroupement par périodes et phases)

### Types de Relations Représentées

| Relation | Signification | Représentation |
|----------|---------------|----------------|
| Couvre/Couvert par | Superposition physique | Ligne continue vers le bas |
| Coupe/Coupé par | Action négative (interface) | Ligne pointillée |
| Se lie à/Égal à | Contemporanéité | Ligne horizontale bidirectionnelle |
| Remplit/Rempli par | Remplissage de creusement | Ligne continue |
| S'appuie sur/Lui s'appuie | Appui structurel | Ligne continue |

## Accès à la Fonction

### Depuis le Menu Principal
1. **PyArchInit** dans la barre de menu
2. Sélectionner **Matrice de Harris**

### Depuis la Fiche US
1. Ouvrir la Fiche US
2. Tab **Map**
3. Bouton **"Exporter Matrix"** ou **"View Matrix"**

### Prérequis
- Base de données correctement connectée
- US avec rapports stratigraphiques remplis
- Périodisation définie (optionnel mais conseillé)
- Graphviz installé sur le système

## Configuration de la Matrice

### Fenêtre de Paramètres (Setting_Matrix)

Avant la génération, une fenêtre de configuration apparaît :

#### Tab Général

| Champ | Description | Valeur Conseillée |
|-------|-------------|-------------------|
| DPI | Résolution de l'image | 150-300 |
| Afficher Périodes | Regrouper les US par période/phase | Oui |
| Afficher Légende | Inclure la légende dans le graphique | Oui |

#### Tab Nœuds "Ante/Post" (Relations Normales)

| Paramètre | Description | Options |
|-----------|-------------|---------|
| Forme nœud | Forme géométrique | box, ellipse, diamond |
| Couleur remplissage | Couleur interne | white, lightblue, etc. |
| Style | Aspect bordure | solid, dashed |
| Épaisseur ligne | Largeur bordure | 0.5 - 2.0 |
| Type flèche | Pointe de la flèche | normal, diamond, none |
| Taille flèche | Grandeur pointe | 0.5 - 1.5 |

#### Tab Nœuds "Négatif" (Creusements)

| Paramètre | Description | Options |
|-----------|-------------|---------|
| Forme nœud | Forme géométrique | box, ellipse, diamond |
| Couleur remplissage | Couleur distinctive | gray, lightcoral |
| Style ligne | Aspect connexion | dashed (pointillé) |

#### Tab Nœuds "Contemporain"

| Paramètre | Description | Options |
|-----------|-------------|---------|
| Forme nœud | Forme géométrique | box, ellipse |
| Couleur remplissage | Couleur distinctive | lightyellow, white |
| Style ligne | Aspect connexion | solid |
| Flèche | Type connexion | none (bidirectionnel) |

#### Tab Connexions Spéciales (">", ">>")

Pour les relations stratigraphiques spéciales ou connexions documentaires :

| Paramètre | Description |
|-----------|-------------|
| Forme | box, ellipse |
| Couleur | lightgreen, etc. |
| Style | solid, dashed |

## Types d'Export

### 1. Export Matrix Standard

Génère la matrice de base avec :
- Tous les rapports stratigraphiques
- Regroupement par période/phase
- Disposition verticale (TB - Top to Bottom)

**Sortie** : `pyarchinit_Matrix_folder/Harris_matrix.jpg`

### 2. Export Matrix 2ED (Étendu)

Version étendue avec :
- Informations supplémentaires dans les nœuds (US + définition + datation)
- Connexions spéciales (>, >>)
- Export également au format GraphML

**Sortie** : `pyarchinit_Matrix_folder/Harris_matrix2ED.jpg`

### 3. View Matrix (Visualisation Rapide)

Pour visualisation rapide sans options de configuration :
- Utilise les paramètres par défaut
- Génération plus rapide
- Idéal pour contrôles rapides

## Processus de Génération

### Étape 1 : Collecte des Données

Le système collecte automatiquement :
```
Pour chaque US dans le site/zone sélectionné :
  - Numéro US
  - Type unité (US/USM)
  - Rapports stratigraphiques
  - Période et phase initiale
  - Définition interprétative
```

### Étape 2 : Construction du Graphe

Création des relations :
```
Séquence (Ante/Post) :
  US1 -> US2 (US1 couvre US2)

Négatif (Creusements) :
  US3 -> US4 (US3 coupe US4)

Contemporain :
  US5 <-> US6 (US5 se lie à US6)
```

### Étape 3 : Clustering par Périodes

Regroupement hiérarchique :
```
Site
  └── Zone
      └── Période 1 : Phase 1 : "Époque Romaine"
          ├── US101
          ├── US102
          └── US103
      └── Période 1 : Phase 2 : "Antiquité Tardive"
          ├── US201
          └── US202
```

### Étape 4 : Réduction Transitive (tred)

La commande `tred` de Graphviz supprime les relations redondantes :
- Si US1 -> US2 et US2 -> US3, supprime US1 -> US3
- Simplifie le diagramme
- Conserve uniquement les relations directes

### Étape 5 : Rendu Final

Génération d'image avec formats multiples :
- DOT (source Graphviz)
- JPG (image compressée)
- PNG (image sans perte)

## Interprétation de la Matrice

### Lecture Verticale

```
     [US les plus récentes]
           ↓
        US 001
           ↓
        US 002
           ↓
        US 003
           ↓
     [US les plus anciennes]
```

### Lecture des Clusters

Les cadres colorés représentent les périodes/phases :
- **Bleu clair** : Cluster de période
- **Jaune** : Cluster de phase
- **Gris** : Fond du site

### Types de Connexions

```
─────────→  Ligne continue = Couvre/Remplit/S'appuie sur
- - - - →  Ligne pointillée = Coupe
←────────→  Bidirectionnel = Contemporain/Égal à
```

### Couleurs des Nœuds

| Couleur | Signification Typique |
|---------|----------------------|
| Blanc | US dépôt normal |
| Gris | US négative (creusement) |
| Jaune | US contemporaines |
| Bleu | US avec relations spéciales |

## Résolution des Problèmes

### Erreur : "Loop Detected"

**Cause** : Il existe des cycles dans les relations (A couvre B, B couvre A)

**Solution** :
1. Ouvrir la Fiche US
2. Vérifier les rapports des US indiquées
3. Corriger les relations circulaires
4. Régénérer la matrice

### Erreur : "tred command not found"

**Cause** : Graphviz non installé

**Solution** :
- **Windows** : Installer Graphviz depuis graphviz.org
- **macOS** : `brew install graphviz`
- **Linux** : `sudo apt install graphviz`

### Matrice Non Générée

**Causes possibles** :
1. Aucun rapport stratigraphique saisi
2. US sans période/phase assignée
3. Problèmes de permissions dans le dossier de sortie

**Vérification** :
1. Contrôler que les US ont des rapports
2. Vérifier la périodisation
3. Contrôler les permissions de `pyarchinit_Matrix_folder`

### Matrice Trop Grande

**Problème** : Image illisible avec de nombreuses US

**Solutions** :
1. Réduire le DPI (100-150)
2. Filtrer par zone spécifique
3. Utiliser le View Matrix pour zones individuelles
4. Exporter en format vectoriel (DOT) et ouvrir avec yEd

### US Non Regroupées par Période

**Cause** : Périodisation manquante ou non activée

**Solution** :
1. Remplir la Fiche Périodisation
2. Assigner période/phase initiale aux US
3. Activer "Afficher Périodes" dans les paramètres

## Sortie et Fichiers Générés

### Dossier de Sortie

```
~/pyarchinit/pyarchinit_Matrix_folder/
```

### Structure des Fichiers Générés

```
pyarchinit_Matrix_folder/
├── Harris_matrix.dot           # Source Graphviz
├── Harris_matrix_tred.dot      # Après réduction transitive
├── Harris_matrix_tred.dot.jpg  # Image finale JPG
├── Harris_matrix_tred.dot.png  # Image finale PNG
├── Harris_matrix2ED.dot        # Version étendue
├── Harris_matrix2ED_graphml.dot # Pour export GraphML
└── matrix_error.txt            # Log erreurs
```

### Utilisation des Fichiers

| Fichier | Utilisation |
|---------|-------------|
| *.jpg/*.png | Insertion dans rapports |
| *.dot | Modification avec éditeur Graphviz |
| _graphml.dot | Import dans yEd pour édition avancée |

## Bonnes Pratiques

### 1. Avant la Génération

- Vérifier la complétude des rapports stratigraphiques
- Contrôler l'absence de cycles
- Assigner période/phase à toutes les US
- Remplir la définition interprétative

### 2. Pendant la Saisie des US

- Insérer des rapports bidirectionnels corrects
- Utiliser une terminologie cohérente
- Vérifier la zone correcte dans les rapports

### 3. Optimisation de la Sortie

- Pour impression : DPI 300
- Pour écran : DPI 150
- Pour fouilles complexes : subdiviser par zones

### 4. Contrôle Qualité

- Comparer la matrice avec la documentation de fouille
- Vérifier les séquences logiques
- Contrôler les regroupements par période

## Workflow Complet

### 1. Préparation des Données

```
1. Compléter les fiches US avec tous les rapports
2. Remplir la fiche Périodisation
3. Assigner période/phase aux US
4. Vérifier la cohérence des données
```

### 2. Génération de la Matrice

```
1. Menu PyArchInit → Matrice de Harris
2. Configurer les paramètres (DPI, couleurs)
3. Activer le clustering par périodes
4. Générer la matrice
```

### 3. Vérification et Correction

```
1. Contrôler la matrice générée
2. Identifier les éventuelles erreurs
3. Corriger les rapports dans les fiches US
4. Régénérer si nécessaire
```

### 4. Utilisation Finale

```
1. Insérer dans le rapport de fouille
2. Exporter pour publication
3. Archiver avec la documentation
```

## Intégration avec d'Autres Outils

### Export pour yEd

Le fichier `_graphml.dot` peut être ouvert dans yEd pour :
- Édition manuelle de la disposition
- Ajout d'annotations
- Export dans différents formats

### Export pour s3egraph

PyArchInit supporte l'export pour le système s3egraph :
- Format compatible
- Conserve les relations stratigraphiques
- Support pour visualisation 3D

## Références

### Fichiers Source
- `tabs/Interactive_matrix.py` - Interface interactive
- `modules/utility/pyarchinit_matrix_exp.py` - Classes HarrisMatrix et ViewHarrisMatrix

### Base de données
- `us_table` - Données US et rapports
- `periodizzazione_table` - Périodes et phases

### Dépendances
- Graphviz (dot, tred)
- Python graphviz library

---

## Vidéo Tutorial

### Matrice de Harris - Génération Complète
`[Placeholder : video_matrice_harris.mp4]`

**Contenus** :
- Configuration des paramètres
- Génération de la matrice
- Interprétation des résultats
- Résolution des problèmes courants

**Durée prévue** : 15-20 minutes

### Matrice de Harris - Édition Avancée avec yEd
`[Placeholder : video_matrice_yed.mp4]`

**Contenus** :
- Export pour yEd
- Modification de la disposition
- Ajout d'annotations
- Ré-export

**Durée prévue** : 10-12 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../animations/harris_matrix_animation.html)
