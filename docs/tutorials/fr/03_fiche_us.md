# Tutorial 03 : Fiche US/USM (Unité Stratigraphique)

## Introduction

La **Fiche US/USM** (Unité Stratigraphique / Unité Stratigraphique Murale) est le cœur de la documentation archéologique dans PyArchInit. Elle représente l'outil principal pour enregistrer toutes les informations relatives aux unités stratigraphiques identifiées lors de la fouille.

Cette fiche implémente les principes de la **méthode stratigraphique** développée par Edward C. Harris, permettant de documenter :
- Les caractéristiques physiques de chaque couche
- Les relations stratigraphiques entre les unités
- La chronologie relative et absolue
- La documentation graphique et photographique associée

---

## Concepts Fondamentaux

### Qu'est-ce qu'une Unité Stratigraphique (US)

Une **Unité Stratigraphique** est la plus petite unité de fouille identifiable et distinguable des autres. Elle peut être :
- **Couche** : dépôt de terre avec caractéristiques homogènes
- **Interface** : surface de contact entre couches (ex. creusement de fosse)
- **Élément structural** : partie d'une construction

### Types d'Unités

| Type | Code | Description |
|------|------|-------------|
| US | Unité Stratigraphique | Couche générique |
| USM | Unité Stratigraphique Murale | Élément construit mural |
| USD | Unité Stratigraphique de Démolition | Couche d'effondrement |
| SF | Stratigraphic Feature | Feature stratigraphique |
| SUS | Sub-Unité Stratigraphique | Subdivision d'US |

### Relations Stratigraphiques

| Relation | Inverse | Signification |
|----------|---------|---------------|
| **Couvre** | Couvert par | L'US se superpose physiquement |
| **Coupe** | Coupé par | L'US interrompt/traverse |
| **Remplit** | Rempli par | L'US comble une cavité |
| **S'appuie sur** | Lui s'appuie | Relation d'appui |

---

## Accès à la Fiche

1. Menu **PyArchInit** → **Archaeological record management** → **SU/WSU**
2. Ou depuis la barre d'outils PyArchInit, cliquer sur l'icône **US/USM**

---

## Interface Générale

La Fiche US est organisée en plusieurs zones fonctionnelles :

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | **Champs Identificatifs** | Site, Zone, US, Type, Définitions |
| 2 | **Toolbar DBMS** | Navigation, sauvegarde, recherche |
| 3 | **Onglets Données** | Fiches thématiques pour les données |
| 4 | **Toolbar GIS** | Outils de visualisation carte |
| 5 | **Onglet Tool Box** | Outils avancés et Matrice |

---

## Champs Identificatifs

### Champs Obligatoires

| Champ | Description | Format |
|-------|-------------|--------|
| **Site** | Nom du site archéologique | Texte (depuis combobox) |
| **Zone** | Numéro de la zone de fouille | Entier (1-20) |
| **US/USM** | Numéro de l'unité stratigraphique | Entier |
| **Type unité** | Type d'unité (US, USM, etc.) | Sélection |

### Champs Descriptifs

| Champ | Description |
|-------|-------------|
| **Définition stratigraphique** | Classification stratigraphique (depuis thésaurus) |
| **Définition interprétative** | Interprétation fonctionnelle (depuis thésaurus) |

---

## Onglet Localisation

| Champ | Description |
|-------|-------------|
| **Secteur** | Secteur de fouille |
| **Carré/Paroi** | Référence spatiale |
| **Pièce** | Numéro de la pièce |
| **Sondage** | Numéro du sondage |

---

## Onglet Données Descriptives

### Champs Descriptifs

| Champ | Description | Suggestions |
|-------|-------------|-------------|
| **Description** | Description physique de l'US | Couleur, consistance, composition, limites |
| **Interprétation** | Interprétation fonctionnelle | Fonction, formation, signification |
| **Éléments datants** | Matériaux pour datation | Céramique, monnaies, objets datés |
| **Observations** | Notes supplémentaires | Doutes, hypothèses, comparaisons |

### Comment Décrire une US

**Description physique :**
```
Couche de terre argileuse, de couleur brun foncé (10YR 3/3),
consistance compacte, avec inclusions de fragments de tuiles (2-5 cm),
galets calcaires (1-3 cm) et charbon. Limites nettes en haut,
diffuses en bas. Épaisseur variable 15-25 cm.
```

**Interprétation :**
```
Couche d'abandon formée suite à la cessation des activités
dans la pièce. La présence de matériaux de construction
fragmentés suggère un effondrement partiel des structures.
```

---

## Onglet Périodisation

### Périodisation Relative

| Champ | Description |
|-------|-------------|
| **Période Initiale** | Période de formation |
| **Phase Initiale** | Phase de formation |
| **Période Finale** | Période d'oblitération |
| **Phase Finale** | Phase d'oblitération |

### Chronologie Absolue

| Champ | Description |
|-------|-------------|
| **Datation** | Date absolue ou intervalle |
| **Année** | Année de fouille |

---

## Onglet Relations Stratigraphiques

**C'est l'onglet le plus important de la fiche US.** Il définit les relations stratigraphiques avec les autres unités.

### Structure du Tableau Relations

| Colonne | Description |
|---------|-------------|
| **Site** | Site de l'US corrélée |
| **Zone** | Zone de l'US corrélée |
| **US** | Numéro US corrélée |
| **Type de relation** | Type de relation |

### Types de Relations Disponibles

| Français | Anglais | Allemand |
|----------|---------|----------|
| Couvre | Covers | Liegt über |
| Couvert par | Covered by | Liegt unter |
| Coupe | Cuts | Schneidet |
| Coupé par | Cut by | Geschnitten von |
| Remplit | Fills | Verfüllt |
| Rempli par | Filled by | Verfüllt von |
| S'appuie sur | Abuts | Stützt sich auf |
| Lui s'appuie | Supports | Wird gestützt von |
| Égal à (=) | Same as | Gleich |

### Insertion des Relations

1. Cliquer **+** pour ajouter une ligne
2. Entrer Site, Zone, US de l'US corrélée
3. Sélectionner le type de relation
4. Sauvegarder

### Relations Inverses Automatiques

Lorsque vous insérez une relation, vous pouvez créer automatiquement l'inverse :

| Si vous insérez | Est créé |
|-----------------|----------|
| US 1 **couvre** US 2 | US 2 **couverte par** US 1 |
| US 1 **coupe** US 2 | US 2 **coupée par** US 1 |
| US 1 **remplit** US 2 | US 2 **remplie par** US 1 |

---

## Onglet Données Physiques

### Caractéristiques Générales

| Champ | Valeurs |
|-------|---------|
| **Couleur** | Brun, Jaune, Gris, Noir, etc. |
| **Consistance** | Argileuse, Compacte, Friable, Sableuse |
| **Formation** | Artificielle, Naturelle |
| **Mode de formation** | Apport, Soustraction, Accumulation |

### Tableaux des Composants

| Tableau | Contenu |
|---------|---------|
| **Comp. organiques** | Os, bois, charbons, graines, etc. |
| **Comp. inorganiques** | Pierres, tuiles, céramique, etc. |
| **Inclusions Artificielles** | Matériaux anthropiques inclus |

---

## Onglet Mesures US

### Cotes

| Champ | Description | Unité |
|-------|-------------|-------|
| **Cote absolue** | Cote par rapport au niveau de la mer | mètres |
| **Cote relative** | Cote par rapport à un point de référence | mètres |
| **Cote max absolue** | Cote maximale absolue | mètres |
| **Cote min absolue** | Cote minimale absolue | mètres |

### Dimensions

| Champ | Description | Unité |
|-------|-------------|-------|
| **Longueur max** | Longueur maximale | mètres |
| **Largeur moyenne** | Largeur moyenne | mètres |
| **Épaisseur** | Épaisseur de la couche | mètres |
| **Profondeur max** | Profondeur maximale | mètres |

---

## Onglet Documentation

### Tableau Documentation

| Colonne | Description |
|---------|-------------|
| **Type documentation** | Photo, Plan, Coupe, Élévation, etc. |
| **Références** | Numéro/code du document |

### Types de Documentation

| Type | Description |
|------|-------------|
| Photo | Documentation photographique |
| Plan | Plan de fouille |
| Coupe | Coupe stratigraphique |
| Élévation | Élévation murale |
| Relevé | Relevé graphique |
| 3D | Modèle tridimensionnel |

---

## Onglet Technique Constructive USM

Onglet spécifique pour les Unités Stratigraphiques Murales (USM).

### Données Spécifiques USM

| Champ | Description |
|-------|-------------|
| **Longueur USM** | Longueur de la maçonnerie (mètres) |
| **Hauteur USM** | Hauteur de la maçonnerie (mètres) |
| **Surface analysée** | Pourcentage analysé |
| **Section murale** | Type de section |
| **Typologie de l'ouvrage** | Type de maçonnerie |
| **Orientation** | Orientation de la structure |
| **Remploi** | Oui / Non |

---

## Matrice de Harris

La Matrice de Harris est une représentation graphique des relations stratigraphiques.

### Génération de la Matrice

1. Sélectionner le site et la zone
2. Vérifier que les relations sont correctes
3. Aller dans **Onglet Help** → **Tool Box**
4. Cliquer **Export Matrix**

### Formats d'Exportation

| Format | Logiciel | Usage |
|--------|----------|-------|
| DOT | Graphviz | Visualisation de base |
| GraphML | yEd, Gephi | Édition avancée |
| Extended Matrix | S3DGraphy | Visualisation 3D |
| CSV | Excel | Analyse de données |

---

## Fonctionnalités GIS

La Fiche US est étroitement intégrée avec QGIS.

### Couches GIS Associées

| Couche | Géométrie | Description |
|--------|-----------|-------------|
| PYUS | Polygone | Unités stratigraphiques |
| PYUSM | Polygone | Unités murales |
| PYQUOTE | Point | Cotes |
| PYQUOTEUSM | Point | Cotes USM |

---

## Exportations

### Fiches US PDF

1. Cliquer **Report** dans la toolbar
2. Choisir le format (PDF, Word)
3. Sélectionner les fiches à exporter

### Listes

| Type | Contenu |
|------|---------|
| **Liste US** | Liste de toutes les US |
| **Liste Photos avec Miniatures** | Liste avec aperçus |
| **Fiches US** | Fiches complètes |

---

## Workflow Opérationnel

### Créer une Nouvelle US

1. **Ouvrir la Fiche**
2. **Cliquer New Record**
3. **Insérer les Identificatifs** - Site, Zone, numéro US, Type
4. **Définitions** - stratigraphique et interprétative
5. **Description** - physique et interprétation
6. **Relations Stratigraphiques** - insérer les relations
7. **Données Physiques et Mesures**
8. **Sauvegarder**

---

## Résolution des Problèmes

### Erreur lors de la sauvegarde
- Vérifier que Site, Zone et US sont remplis
- Vérifier que la combinaison est unique

### Relations non cohérentes
- Utiliser le contrôle des relations
- Vérifier les relations inverses

### La Matrice ne se génère pas
- Vérifier que Graphviz est installé
- Contrôler le chemin dans la configuration

---

## Notes Techniques

- **Table principale** : `us_table`
- **Clé primaire** : `id_us`
- **Clé composée** : sito + area + us

---

## Vidéo Tutorial

### Fiche US Complète
`[Placeholder : video_fiche_us.mp4]`

**Contenus** :
- Création d'une US
- Relations stratigraphiques
- Génération de la Matrice de Harris
- Export PDF

**Durée prévue** : 20-25 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
