# Tutorial 16 : Fiche Pottery (Céramique Spécialisée)

## Index
1. [Introduction](#introduction)
2. [Accès à la Fiche](#accès-à-la-fiche)
3. [Interface Utilisateur](#interface-utilisateur)
4. [Champs Principaux](#champs-principaux)
5. [Onglets de la Fiche](#onglets-de-la-fiche)
6. [Pottery Tools](#pottery-tools)
7. [Recherche par Similarité Visuelle](#recherche-par-similarité-visuelle)
8. [Quantifications](#quantifications)
9. [Gestion des Médias](#gestion-des-médias)
10. [Export et Rapports](#export-et-rapports)
11. [Workflow Opérationnel](#workflow-opérationnel)
12. [Bonnes Pratiques](#bonnes-pratiques)
13. [Résolution des Problèmes](#résolution-des-problèmes)

---

## Introduction

La **Fiche Pottery** est un outil spécialisé pour le catalogage détaillé de la céramique archéologique. À la différence de la fiche Inventaire Matériaux (plus généraliste), cette fiche est conçue spécifiquement pour l'analyse céramologique approfondie, avec des champs dédiés au fabric, au ware, aux décors et aux mesures spécifiques des vases.

### Différences avec la Fiche Inventaire Matériaux

| Aspect | Inventaire Matériaux | Pottery |
|--------|---------------------|---------|
| **Objectif** | Tous les types d'objets | Céramique uniquement |
| **Détail** | Général | Spécialisé |
| **Champs fabric** | Corps céramique (générique) | Fabric détaillé |
| **Décors** | Champ unique | Interne/Externe séparés |
| **Mesures** | Génériques | Spécifiques aux vases |
| **Outils IA** | SketchGPT | PotteryInk, YOLO, Similarity Search |

### Fonctionnalités Avancées

La fiche Pottery inclut des fonctionnalités IA de pointe :
- **PotteryInk** : Génération automatique de dessins archéologiques à partir de photos
- **YOLO Detection** : Reconnaissance automatique des formes céramiques
- **Visual Similarity Search** : Recherche de céramiques similaires via embeddings visuels
- **Layout Generator** : Génération automatique de planches céramiques

---

## Accès à la Fiche

### Depuis le Menu

1. Ouvrir QGIS avec le plugin PyArchInit actif
2. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery**

### Depuis la Toolbar

1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Pottery** (icône vase/amphore céramique)

---

## Interface Utilisateur

L'interface est organisée de manière efficace pour l'enregistrement céramologique :

### Zones Principales

| Zone | Description |
|------|-------------|
| **1. En-tête** | Toolbar DBMS, indicateurs d'état, filtres |
| **2. Identification** | Site, Zone, US, ID Number, Box, Bag |
| **3. Classification** | Form, Ware, Fabric, Material |
| **4. Tab Détail** | Description, Technical Data, Supplements |
| **5. Panneau Médias** | Visionneuse images, aperçu |

### Onglets Disponibles

| Onglet | Contenu |
|--------|---------|
| **Description data** | Description, décors, notes |
| **Technical Data** | Mesures, traitement de surface, Munsell |
| **Supplements** | Bibliographie, Statistiques |

---

## Champs Principaux

### Champs Identificatifs

#### ID Number
- **Type** : Integer
- **Obligatoire** : Oui
- **Description** : Numéro identificatif unique du fragment céramique
- **Contrainte** : Unique par site

#### Site
- **Type** : ComboBox
- **Obligatoire** : Oui
- **Description** : Site archéologique de provenance

#### Zone
- **Type** : ComboBox éditable
- **Description** : Zone de fouille

#### US (Unité Stratigraphique)
- **Type** : Integer
- **Description** : Numéro de l'US de découverte

#### Secteur
- **Type** : Text
- **Description** : Secteur spécifique de découverte

### Champs Dépôt

#### Box
- **Type** : Integer
- **Description** : Numéro de la caisse de dépôt

#### Bag
- **Type** : Integer
- **Description** : Numéro du sachet

#### Year (Année)
- **Type** : Integer
- **Description** : Année de découverte/enregistrement

### Champs Classification Céramique

#### Form (Forme)
- **Type** : ComboBox éditable
- **Obligatoire** : Conseillé
- **Valeurs typiques** : Bowl, Jar, Jug, Plate, Cup, Amphora, Lid, etc.
- **Description** : Forme générale du vase

#### Specific Form (Forme Spécifique)
- **Type** : ComboBox éditable
- **Description** : Typologie spécifique (ex. Hayes 50, Dressel 1)

#### Specific Shape
- **Type** : Text
- **Description** : Variante morphologique détaillée

#### Ware
- **Type** : ComboBox éditable
- **Description** : Classe céramique
- **Exemples** :
  - African Red Slip
  - Italian Sigillata
  - Thin Walled Ware
  - Coarse Ware
  - Amphora
  - Cooking Ware

#### Material
- **Type** : ComboBox éditable
- **Description** : Matériau de base
- **Valeurs** : Ceramic, Terracotta, Porcelain, etc.

#### Fabric
- **Type** : ComboBox éditable
- **Description** : Type de pâte céramique
- **Caractéristiques à considérer** :
  - Couleur de la pâte
  - Granulométrie des inclusions
  - Dureté
  - Porosité

### Champs Conservation

#### Percent
- **Type** : ComboBox éditable
- **Description** : Pourcentage conservé du vase
- **Valeurs typiques** : <10%, 10-25%, 25-50%, 50-75%, >75%, Complete

#### QTY (Quantity)
- **Type** : Integer
- **Description** : Nombre de fragments

### Champs Documentation

#### Photo
- **Type** : Text
- **Description** : Référence photographique

#### Drawing
- **Type** : Text
- **Description** : Référence dessin

---

## Onglets de la Fiche

### Onglet 1 : Description Data

Onglet principal pour la description du fragment.

#### Décors

| Champ | Description |
|-------|-------------|
| **External Decoration** | Type de décor externe |
| **Internal Decoration** | Type de décor interne |
| **Description External Deco** | Description détaillée du décor externe |
| **Description Internal Deco** | Description détaillée du décor interne |
| **Decoration Type** | Typologie décorative (Painted, Incised, Applique, etc.) |
| **Decoration Motif** | Motif décoratif (Geometric, Vegetal, Figurative) |
| **Decoration Position** | Position du décor (Rim, Body, Base, Handle) |

#### Wheel Made
- **Type** : ComboBox
- **Valeurs** : Yes, No, Unknown
- **Description** : Indique si le vase a été produit au tour

#### Note
- **Type** : TextEdit multiligne
- **Description** : Notes supplémentaires et observations

#### Visionneuse Médias
Zone pour visualiser les images associées :
- Drag & drop pour associer des images
- Double-clic pour ouvrir la visionneuse complète
- Boutons pour gestion des tags

### Onglet 2 : Technical Data

Données techniques et mesures.

#### Couleur Munsell
- **Type** : ComboBox éditable
- **Description** : Code couleur Munsell de la pâte
- **Format** : ex. "10YR 7/4", "5YR 6/6"
- **Note** : Se référer au Munsell Soil Color Chart

#### Surface Treatment
- **Type** : ComboBox éditable
- **Description** : Traitement de surface
- **Valeurs typiques** :
  - Slip (engobe)
  - Burnished (bruni)
  - Glazed (glaçuré)
  - Painted (peint)
  - Plain (simple)

#### Mesures (en cm)

| Champ | Description |
|-------|-------------|
| **Diameter Max** | Diamètre maximum du vase |
| **Diameter Rim** | Diamètre du bord |
| **Diameter Bottom** | Diamètre du fond |
| **Total Height** | Hauteur totale (si reconstituable) |
| **Preserved Height** | Hauteur conservée |

#### Datation
- **Type** : ComboBox éditable
- **Description** : Cadre chronologique
- **Format** : Textuel (ex. "Ier-IIe s. ap. J.-C.")

### Onglet 3 : Supplements

Onglet avec sous-sections pour données supplémentaires.

#### Sous-Onglet : Bibliography
Gestion des références bibliographiques pour comparaisons typologiques.

| Colonne | Description |
|---------|-------------|
| Author | Auteur(s) |
| Year | Année de publication |
| Title | Titre abrégé |
| Page | Page de référence |
| Figure | Figure/Planche |

#### Sous-Onglet : Statistic
Accès aux fonctionnalités de quantification et graphiques statistiques.

---

## Pottery Tools

La fiche Pottery inclut un puissant ensemble d'outils IA pour le traitement des images céramiques.

### Accès à Pottery Tools

1. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Pottery Tools**

Ou depuis le bouton dédié dans la fiche Pottery.

### PotteryInk - Génération de Dessins

Transforme automatiquement les photos de céramique en dessins archéologiques stylisés.

#### Utilisation

1. Sélectionner une image de céramique
2. Cliquer sur "Generate Drawing"
3. Le système traite l'image avec l'IA
4. Le dessin est généré en style archéologique

#### Prérequis
- Environnement virtuel dédié (créé automatiquement)
- Modèles IA pré-entraînés
- GPU conseillé pour performances optimales

### YOLO Pottery Detection

Reconnaissance automatique des formes céramiques dans les images.

#### Fonctionnalités

- Identifie automatiquement la forme du vase
- Suggère une classification
- Détecte les parties anatomiques (bord, paroi, fond, anse)

### Layout Generator

Génère automatiquement des planches céramiques pour publication.

#### Sortie

- Planches au format standard archéologique
- Échelle métrique automatique
- Disposition optimisée
- Export en PDF ou image

### PDF Extractor

Extrait les images de céramique depuis des publications PDF pour comparaisons.

---

## Recherche par Similarité Visuelle

Fonctionnalité avancée pour trouver des céramiques visuellement similaires dans la base de données.

### Comment ça Fonctionne

Le système utilise des **embeddings visuels** générés par des modèles de deep learning pour représenter chaque image céramique comme un vecteur numérique. La recherche trouve les céramiques avec les vecteurs les plus similaires.

### Utilisation

1. Sélectionner une image de référence
2. Cliquer sur "Find Similar"
3. Le système recherche dans la base de données
4. Les céramiques les plus similaires sont affichées triées par similarité

### Modèles Disponibles

- **ResNet50** : Bon équilibre vitesse/précision
- **EfficientNet** : Performances optimales
- **CLIP** : Recherche multimodale (texte + image)

### Mise à Jour des Embeddings

Les embeddings sont générés automatiquement lors de l'ajout de nouvelles images. Il est possible de forcer la mise à jour depuis le menu Pottery Tools.

---

## Quantifications

### Accès

1. Cliquer sur le bouton **Quant** dans la toolbar
2. Sélectionner le paramètre de quantification
3. Visualiser le graphique

### Paramètres Disponibles

| Paramètre | Description |
|-----------|-------------|
| **Fabric** | Distribution par type de pâte |
| **US** | Distribution par unité stratigraphique |
| **Area** | Distribution par zone de fouille |
| **Material** | Distribution par matériau |
| **Percent** | Distribution par pourcentage conservé |
| **Shape/Form** | Distribution par forme |
| **Specific form** | Distribution par forme spécifique |
| **Ware** | Distribution par classe céramique |
| **Munsell color** | Distribution par couleur |
| **Surface treatment** | Distribution par traitement de surface |
| **External decoration** | Distribution par décor externe |
| **Internal decoration** | Distribution par décor interne |
| **Wheel made** | Distribution tour oui/non |

### Export des Quantifications

Les données sont exportées en :
- Fichier CSV dans `pyarchinit_Quantificazioni_folder`
- Graphique affiché à l'écran

---

## Gestion des Médias

### Association d'Images

#### Méthodes

1. **Drag & Drop** : Glisser les images dans la liste
2. **Bouton All Images** : Charger toutes les images associées
3. **Search Images** : Rechercher des images spécifiques

### Lecteur Vidéo

Pour les céramiques avec documentation vidéo, un lecteur intégré est disponible.

### Intégration Cloudinary

Support pour images distantes sur Cloudinary :
- Chargement automatique des miniatures
- Cache local pour performances
- Synchronisation avec le cloud

---

## Export et Rapports

### Export PDF Fiche

Génère une fiche PDF complète avec :
- Données identificatives
- Classification
- Mesures
- Images associées
- Notes

### Export Liste

Génère une liste PDF de tous les enregistrements affichés.

### Export Données

Bouton pour export en format tabulaire (CSV/Excel).

---

## Workflow Opérationnel

### Enregistrement d'un Nouveau Fragment Céramique

#### Étape 1 : Ouverture et Nouveau Record
1. Ouvrir la Fiche Pottery
2. Cliquer sur **New record**

#### Étape 2 : Données Identificatives
1. Vérifier/sélectionner le **Site**
2. Insérer l'**ID Number** (progressif)
3. Insérer **Zone**, **US**, **Secteur**
4. Insérer **Box** et **Bag**

#### Étape 3 : Classification
1. Sélectionner **Form** (Bowl, Jar, etc.)
2. Sélectionner **Ware** (classe céramique)
3. Sélectionner **Fabric** (type de pâte)
4. Indiquer **Material** et **Percent**

#### Étape 4 : Données Techniques
1. Ouvrir l'onglet **Technical Data**
2. Insérer la **couleur Munsell**
3. Sélectionner le **Surface treatment**
4. Insérer les **mesures** (diamètres, hauteurs)
5. Indiquer **Wheel made**

#### Étape 5 : Décors (si présents)
1. Revenir à l'onglet **Description data**
2. Sélectionner le type **External/Internal decoration**
3. Remplir les descriptions détaillées
4. Indiquer **Decoration type**, **motif**, **position**

#### Étape 6 : Documentation
1. Associer les photos (drag & drop)
2. Insérer la référence **Photo** et **Drawing**
3. Remplir les **Notes** avec observations

#### Étape 7 : Datation et Comparaisons
1. Insérer la **Datation**
2. Ouvrir l'onglet **Supplements** → **Bibliography**
3. Ajouter les références bibliographiques

#### Étape 8 : Sauvegarde
1. Cliquer sur **Save**
2. Vérifier la confirmation

---

## Bonnes Pratiques

### Classification Cohérente

- Utiliser des vocabulaires standardisés pour Form, Ware, Fabric
- Maintenir la cohérence dans la nomenclature
- Mettre à jour le thésaurus quand nécessaire

### Documentation Photographique

- Photographier chaque fragment avec échelle
- Inclure vue interne et externe
- Documenter les détails décoratifs

### Mesures

- Utiliser un pied à coulisse pour mesures précises
- Indiquer toujours l'unité de mesure (cm)
- Pour les fragments, mesurer uniquement les parties conservées

### Couleur Munsell

- Utiliser toujours le Munsell Soil Color Chart
- Mesurer sur cassure fraîche
- Indiquer les conditions de lumière

### Utilisation des Outils IA

- Vérifier toujours les résultats automatiques
- PotteryInk fonctionne mieux avec des photos de bonne qualité
- La similarity search est utile pour les comparaisons, pas un substitut de l'analyse

---

## Résolution des Problèmes

### Problèmes Courants

#### ID Number dupliqué
- **Erreur** : "Un enregistrement avec cet ID existe déjà"
- **Solution** : Vérifier le prochain numéro disponible

#### Pottery Tools ne démarre pas
- **Cause** : Environnement virtuel non configuré
- **Solution** :
  1. Vérifier la connexion internet
  2. Attendre la configuration automatique
  3. Contrôler le log dans `pyarchinit/bin/pottery_venv`

#### PotteryInk lent
- **Cause** : Traitement CPU au lieu de GPU
- **Solution** :
  1. Installer les drivers CUDA (NVIDIA)
  2. Vérifier que PyTorch utilise le GPU

#### Similarity Search vide
- **Cause** : Embeddings non générés
- **Solution** :
  1. Ouvrir Pottery Tools
  2. Cliquer sur "Update Embeddings"
  3. Attendre la fin du processus

#### Images non chargées
- **Cause** : Chemin incorrect ou Cloudinary non configuré
- **Solution** :
  1. Vérifier la configuration des chemins dans Settings
  2. Pour Cloudinary : vérifier les identifiants

---

## Vidéo Tutorial

### Vidéo 1 : Aperçu Fiche Pottery
*Durée : 5-6 minutes*

`[Placeholder vidéo : video_pottery_apercu.mp4]`

### Vidéo 2 : Enregistrement Céramique Complet
*Durée : 8-10 minutes*

`[Placeholder vidéo : video_pottery_enregistrement.mp4]`

### Vidéo 3 : Pottery Tools et IA
*Durée : 10-12 minutes*

`[Placeholder vidéo : video_pottery_tools_ia.mp4]`

### Vidéo 4 : Recherche par Similarité
*Durée : 5-6 minutes*

`[Placeholder vidéo : video_pottery_similarite.mp4]`

---

## Récapitulatif des Champs Base de Données

| Champ | Type | Base de données | Obligatoire |
|-------|------|-----------------|-------------|
| ID Number | Integer | id_number | Oui |
| Site | Text | sito | Oui |
| Zone | Text | area | Non |
| US | Integer | us | Non |
| Box | Integer | box | Non |
| Bag | Integer | bag | Non |
| Sector | Text | sector | Non |
| Photo | Text | photo | Non |
| Drawing | Text | drawing | Non |
| Year | Integer | anno | Non |
| Fabric | Text | fabric | Non |
| Percent | Text | percent | Non |
| Material | Text | material | Non |
| Form | Text | form | Non |
| Specific Form | Text | specific_form | Non |
| Specific Shape | Text | specific_shape | Non |
| Ware | Text | ware | Non |
| Munsell Color | Text | munsell | Non |
| Surface Treatment | Text | surf_trat | Non |
| External Decoration | Text | exdeco | Non |
| Internal Decoration | Text | intdeco | Non |
| Wheel Made | Text | wheel_made | Non |
| Descrip. External Deco | Text | descrip_ex_deco | Non |
| Descrip. Internal Deco | Text | descrip_in_deco | Non |
| Note | Text | note | Non |
| Diameter Max | Numeric | diametro_max | Non |
| QTY | Integer | qty | Non |
| Diameter Rim | Numeric | diametro_rim | Non |
| Diameter Bottom | Numeric | diametro_bottom | Non |
| Total Height | Numeric | diametro_height | Non |
| Preserved Height | Numeric | diametro_preserved | Non |
| Decoration Type | Text | decoration_type | Non |
| Decoration Motif | Text | decoration_motif | Non |
| Decoration Position | Text | decoration_position | Non |
| Datation | Text | datazione | Non |

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Analyse Céramologique Archéologique*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../animations/pyarchinit_pottery_tools_animation.html)
