# Tutorial 08 : Fiche Inventaire Matériaux

## Table des Matières
1. [Introduction](#introduction)
2. [Accès à la Fiche](#accès-à-la-fiche)
3. [Interface Utilisateur](#interface-utilisateur)
4. [Champs Principaux](#champs-principaux)
5. [Onglets de la Fiche](#onglets-de-la-fiche)
6. [Toolbar DBMS](#toolbar-dbms)
7. [Gestion des Médias](#gestion-des-médias)
8. [Fonctionnalités GIS](#fonctionnalités-gis)
9. [Quantifications et Statistiques](#quantifications-et-statistiques)
10. [Export et Rapports](#export-et-rapports)
11. [Intégration IA](#intégration-ia)
12. [Workflow Opérationnel](#workflow-opérationnel)
13. [Bonnes Pratiques](#bonnes-pratiques)
14. [Résolution des Problèmes](#résolution-des-problèmes)

---

## Introduction

La **Fiche Inventaire Matériaux** est l'outil principal pour la gestion du mobilier archéologique dans PyArchInit. Elle permet de cataloguer, décrire et quantifier tous les matériaux découverts lors de la fouille, des céramiques aux métaux, des verres aux ossements animaux.

### Objectif de la Fiche

- Inventorier tous les objets découverts
- Associer les objets aux US de provenance
- Gérer la classification typologique
- Documenter les caractéristiques physiques et technologiques
- Calculer les quantifications (formes minimales, EVE, poids)
- Relier photos et dessins aux objets
- Générer rapports et statistiques

### Types de Matériaux Gérés

La fiche supporte différents types de matériaux :
- **Céramique** : Vaisselle, terres cuites, matériaux de construction
- **Métaux** : Bronze, fer, plomb, or, argent
- **Verre** : Contenants, verre à vitre
- **Os/Ivoire** : Objets en matière dure animale
- **Pierre** : Outillage lithique, sculptures
- **Monnaies** : Numismatique
- **Organiques** : Bois, textiles, cuir

---

## Accès à la Fiche

### Depuis le Menu

1. Ouvrir QGIS avec le plugin PyArchInit actif
2. Menu **PyArchInit** → **Archaeological record management** → **Artefact** → **Artefact form**

### Depuis la Toolbar

1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Mobilier** (icône amphore/vase)

### Raccourci Clavier

- **Ctrl+G** : Active/désactive la visualisation GIS de l'objet actuel

---

## Interface Utilisateur

L'interface est organisée en trois zones principales :

### Zones Principales

| Zone | Description |
|------|-------------|
| **1. En-tête** | DBMS Toolbar, indicateurs état, boutons GIS et export |
| **2. Champs Identificatifs** | Site, Zone, US, Numéro inventaire, RA, Type objet |
| **3. Champs Descriptifs** | Classe, Définition, État conservation, Datation |
| **4. Tab Détail** | 6 onglets pour données spécifiques |

### Onglets Disponibles

| Tab | Contenu |
|-----|---------|
| **Description** | Texte descriptif, media viewer, datation |
| **Diapositives** | Gestion diapositives et négatifs photographiques |
| **Données quantitatives** | Éléments objet, formes, mesures céramiques |
| **Technologies** | Techniques productives et décoratives |
| **Réf Biblio** | Références bibliographiques |
| **Quantifications** | Graphiques et statistiques |

---

## Champs Principaux

### Champs Identificatifs

#### Site
- **Type** : ComboBox (lecture seule après sauvegarde)
- **Obligatoire** : Oui
- **Description** : Site archéologique de provenance
- **Note** : Si défini dans la configuration, pré-rempli automatiquement

#### Numéro Inventaire
- **Type** : LineEdit numérique
- **Obligatoire** : Oui
- **Description** : Numéro progressif unique de l'objet au sein du site
- **Contrainte** : Unique par site

#### Zone
- **Type** : ComboBox éditable
- **Obligatoire** : Non
- **Description** : Zone de fouille de provenance

#### US (Unité Stratigraphique)
- **Type** : LineEdit
- **Obligatoire** : Non (mais fortement conseillé)
- **Description** : Numéro de l'US de découverte
- **Lien** : Relie l'objet à la fiche US correspondante

#### Structure
- **Type** : ComboBox éditable
- **Obligatoire** : Non
- **Description** : Structure d'appartenance (si applicable)
- **Note** : Se remplit automatiquement en fonction de l'US

#### RA (Repère Archéologique)
- **Type** : LineEdit numérique
- **Obligatoire** : Non
- **Description** : Numéro de repère archéologique (numérotation alternative)
- **Note** : Utilisé pour les objets particulièrement significatifs

### Champs Classification

#### Type Objet
- **Type** : ComboBox éditable
- **Obligatoire** : Oui
- **Valeurs typiques** : Céramique, Métal, Verre, Os, Pierre, Monnaie, etc.
- **Note** : Détermine les champs spécifiques à remplir

#### Classe Matériau (Critère Documentation)
- **Type** : ComboBox éditable
- **Obligatoire** : Non
- **Description** : Classe d'appartenance du matériau
- **Exemples pour céramique** :
  - Céramique commune
  - Sigillée italique
  - Sigillée africaine
  - Céramique à vernis noir
  - Céramique à parois fines
  - Amphores
  - Lampes

#### Définition
- **Type** : ComboBox éditable
- **Obligatoire** : Non
- **Description** : Définition typologique spécifique
- **Exemples** : Assiette, Coupe, Marmite, Cruche, Couvercle, etc.

#### Type
- **Type** : LineEdit
- **Obligatoire** : Non
- **Description** : Typologie spécifique (ex. Dressel 1, Hayes 50)

### Champs État et Conservation

#### Lavé
- **Type** : ComboBox
- **Valeurs** : Oui, Non
- **Description** : Indique si l'objet a été lavé

#### Répertorié
- **Type** : ComboBox
- **Valeurs** : Oui, Non
- **Description** : Indique si l'objet a été sélectionné pour l'étude

#### Diagnostique
- **Type** : ComboBox
- **Valeurs** : Oui, Non
- **Description** : Indique si l'objet est diagnostique (utile pour classification)

#### État Conservation
- **Type** : ComboBox éditable
- **Obligatoire** : Non
- **Valeurs typiques** : Intact, Fragmentaire, Lacunaire, Restauré

### Champs Dépôt

#### N° Caisse
- **Type** : LineEdit
- **Description** : Numéro de la caisse de dépôt

#### Type Contenant
- **Type** : ComboBox éditable
- **Description** : Type de contenant (caisse, sachet, boîte)

#### Lieu de Conservation
- **Type** : ComboBox éditable
- **Description** : Magasin ou dépôt de conservation

#### Année
- **Type** : ComboBox éditable
- **Description** : Année de découverte

### Champs Documentation

#### Compilateur
- **Type** : ComboBox éditable
- **Description** : Nom du documenteur

#### Point de Découverte
- **Type** : LineEdit
- **Description** : Coordonnées ou référence spatiale du point de découverte

---

## Onglets de la Fiche

### Tab 1 : Description

L'onglet principal contient la description textuelle de l'objet et la gestion des médias.

#### Champ Description
- **Type** : TextEdit multiligne
- **Contenu suggéré** :
  - Forme générale
  - Parties conservées
  - Caractéristiques techniques
  - Décors
  - Comparaisons typologiques

#### Datation Objet
- **Type** : ComboBox éditable
- **Description** : Cadrage chronologique de l'objet
- **Format** : Textuel (ex. "Ier s. av. J.-C.", "IIe-IIIe s. apr. J.-C.")

#### Media Viewer
Zone pour visualiser les images associées à l'objet :
- **Afficher toutes les images** : Charge toutes les photos liées
- **Chercher images** : Recherche dans les images
- **Supprimer tag** : Supprime l'association image-objet
- **SketchGPT** : Génère une description IA depuis l'image

### Tab 2 : Diapositives

Gestion de la documentation photographique traditionnelle.

#### Tableau Diapositives
| Colonne | Description |
|---------|-------------|
| Code | Code identificatif de la diapositive |
| N° | Numéro progressif |

#### Tableau Négatifs
| Colonne | Description |
|---------|-------------|
| Code | Code du rouleau négatif |
| N° | Numéro du photogramme |

#### Champs Supplémentaires
- **Photo ID** : Noms des photos associées (auto-rempli)
- **Drawing ID** : Noms des dessins associés (auto-rempli)

### Tab 3 : Données Quantitatives

Onglet fondamental pour l'analyse quantitative, notamment pour la céramique.

#### Tableau Éléments Objet
Permet d'enregistrer les éléments individuels composant l'objet :

| Colonne | Description | Exemple |
|---------|-------------|---------|
| Élément découvert | Partie anatomique du vase | Bord, Paroi, Fond, Anse |
| Type de quantité | État du fragment | Fragment, Entier |
| Quantité | Nombre de pièces | 5 |

#### Champs Quantification Céramique

| Champ | Description |
|-------|-------------|
| **Formes minimales** | Nombre Minimum d'Individus (NMI) |
| **Formes maximales** | Nombre Maximum d'Individus |
| **Total fragments** | Comptage automatique depuis le tableau éléments |
| **Poids** | Poids en grammes |
| **Diamètre bord** | Diamètre du bord en cm |
| **EVE bord** | Estimated Vessel Equivalent (pourcentage bord conservé) |

#### Bouton Calcul Total Fragments
Calcule automatiquement le total des fragments en additionnant les quantités du tableau éléments.

#### Tableau Mesures
Permet d'enregistrer des mesures multiples :

| Colonne | Description |
|---------|-------------|
| Type mesure | Hauteur, Largeur, Épaisseur, etc. |
| Unité de mesure | cm, mm, m |
| Valeur | Valeur numérique |

### Tab 4 : Technologies

Enregistrement des techniques productives et décoratives.

#### Tableau Technologies

| Colonne | Description | Exemple |
|---------|-------------|---------|
| Type technologie | Catégorie technique | Production, Décoration |
| Position | Où elle se trouve | Intérieur, Extérieur, Corps |
| Quantité | Si applicable | - |
| Unité de mesure | Si applicable | - |

#### Champs Spécifiques Céramique

| Champ | Description |
|-------|-------------|
| **Corps céramique** | Type de pâte (Épuré, Semi-épuré, Grossier) |
| **Revêtement** | Type de revêtement (Vernis, Engobe, Glaçure) |

### Tab 5 : Références Bibliographiques

Gestion de la bibliographie de comparaison.

#### Tableau Références

| Colonne | Description |
|---------|-------------|
| Auteur | Nom auteur(s) |
| Année | Année publication |
| Titre | Titre abrégé |
| Page | Référence page |
| Figure | Référence figure/planche |

### Tab 6 : Quantifications

Onglet pour générer graphiques et statistiques sur les données.

#### Types de Quantification Disponibles

| Type | Description |
|------|-------------|
| **Formes minimales** | Graphique pour NMI |
| **Formes maximales** | Graphique pour nombre maximum |
| **Total fragments** | Graphique pour comptage fragments |
| **Poids** | Graphique pour poids |
| **EVE bord** | Graphique pour EVE |

#### Paramètres de Regroupement

Les graphiques peuvent être regroupés par :
- Type objet
- Classe matériau
- Définition
- Corps céramique
- Revêtement
- Type
- Datation
- RA
- Année

---

## Toolbar DBMS

La toolbar offre tous les outils pour la gestion des enregistrements.

### Boutons Standard

| Icône | Fonction | Description |
|-------|----------|-------------|
| Connection test | Test connexion | Vérifie la connexion à la base |
| First/Prev/Next/Last | Navigation | Navigation entre les enregistrements |
| New record | Nouveau | Crée un nouvel objet |
| Save | Sauvegarder | Sauvegarde les modifications |
| Delete | Supprimer | Supprime l'objet actuel |
| View all | Tous | Affiche tous les enregistrements |
| New search | Recherche | Active le mode recherche |
| Search!!! | Exécuter | Exécute la recherche |
| Order by | Trier | Trie les enregistrements |

### Boutons Spécifiques

| Icône | Fonction | Description |
|-------|----------|-------------|
| GIS | Visualiser GIS | Affiche l'objet sur la carte |
| PDF | Export PDF | Génère une fiche PDF |
| Sheet | Export liste | Génère une liste PDF |
| Excel | Export Excel | Exporte au format Excel/CSV |
| A5 | Export A5 | Génère une étiquette format A5 |
| Quant | Quantifications | Ouvre le panneau quantifications |

---

## Gestion des Médias

### Association d'Images

#### Drag & Drop
Il est possible de glisser des images directement dans la liste pour les associer à l'objet.

#### Boutons Médias

| Bouton | Fonction |
|--------|----------|
| **Toutes les images** | Charge toutes les images associées |
| **Chercher images** | Ouvre la recherche dans les images |
| **Supprimer tag** | Supprime l'association actuelle |

### Visualiseur d'Images

Double-clic sur une image dans la liste ouvre le visualiseur complet avec :
- Zoom
- Pan
- Rotation
- Informations EXIF

### Lecteur Vidéo

Pour les objets avec vidéos associées, un lecteur intégré est disponible pour :
- Lecture vidéo artefacts
- Visualisation modèles 3D (si disponibles)

---

## Fonctionnalités GIS

### Visualisation sur Carte

#### Bouton GIS (Toggle)
- **Actif** : L'objet est mis en évidence sur la carte QGIS
- **Inactif** : Aucune visualisation
- **Raccourci** : Ctrl+G

#### Prérequis
- L'objet doit avoir l'US de provenance spécifiée
- L'US doit avoir une géométrie dans la couche GIS

### Liaison depuis la Carte

Il est possible de sélectionner un objet en cliquant sur la carte :
1. Activer l'outil de sélection dans QGIS
2. Cliquer sur l'US d'intérêt
3. Les objets de l'US sont filtrés dans la fiche

---

## Quantifications et Statistiques

### Accès aux Quantifications

1. Cliquer sur le bouton **Quant** dans la toolbar
2. Sélectionner le type de quantification
3. Sélectionner les paramètres de regroupement
4. Cliquer OK

### Types de Graphiques

#### Graphique à Barres
Visualise la distribution par catégorie sélectionnée.

### Export Quantifications

Les données des quantifications sont exportées automatiquement en :
- Fichier CSV dans le dossier `pyarchinit_Quantificazioni_folder`
- Graphique affiché à l'écran

---

## Export et Rapports

### Export PDF Fiche Unique

Génère une fiche PDF complète de l'objet actuel avec :
- Toutes les données identificatives
- Description
- Données quantitatives
- Références bibliographiques
- Images associées (si disponibles)

### Export PDF Liste

Génère une liste PDF de tous les objets affichés (résultat de la recherche actuelle) :
- Tableau récapitulatif
- Données essentielles pour chaque objet

### Export A5 (Étiquettes)

Génère des étiquettes format A5 pour :
- Identification caisses
- Étiquetage objets
- Fiches mobiles

Configuration chemin PDF :
1. Cliquer sur l'icône dossier à côté du champ chemin
2. Sélectionner le dossier de destination
3. Cliquer "Exporter A5"

### Export Excel/CSV

Exporte les données en format tabulaire pour :
- Traitements statistiques externes
- Import dans d'autres logiciels
- Archivage

---

## Intégration IA

### SketchGPT

Fonctionnalité IA pour générer automatiquement des descriptions d'objets à partir d'images.

#### Utilisation

1. Associer une image à l'objet
2. Cliquer sur le bouton **SketchGPT**
3. Sélectionner l'image à analyser
4. Sélectionner le modèle GPT (gpt-4-vision, gpt-4o)
5. Le système génère une description archéologique

#### Résultat

La description générée inclut :
- Identification du type d'objet
- Description des caractéristiques visibles
- Comparaisons typologiques possibles
- Suggestions de datation

> **Note** : Nécessite une API Key OpenAI configurée.

---

## Workflow Opérationnel

### Création d'un Nouvel Objet

#### Étape 1 : Ouverture Fiche
1. Ouvrir la Fiche Inventaire Matériaux
2. Vérifier la connexion à la base de données

#### Étape 2 : Nouveau Record
1. Cliquer **New record**
2. Le Status passe à "Nouveau Record"

#### Étape 3 : Données Identificatives
1. Vérifier/sélectionner le **Site**
2. Saisir le **Numéro inventaire** (progressif)
3. Saisir **Zone** et **US** de provenance

#### Étape 4 : Classification
1. Sélectionner le **Type objet**
2. Sélectionner la **Classe matériau**
3. Sélectionner/saisir la **Définition**

#### Étape 5 : Description
1. Remplir le champ **Description** dans le tab Description
2. Sélectionner la **Datation**
3. Associer d'éventuelles images

#### Étape 6 : Données Quantitatives (si céramique)
1. Ouvrir le tab **Données quantitatives**
2. Saisir les éléments dans le tableau
3. Remplir formes minimales/maximales
4. Saisir poids et mesures

#### Étape 7 : Dépôt
1. Saisir **N° caisse**
2. Sélectionner **Lieu conservation**
3. Indiquer **État conservation**

#### Étape 8 : Sauvegarde
1. Cliquer **Save**
2. Vérifier le message de confirmation
3. L'enregistrement est maintenant sauvé dans la base

### Recherche d'Objets

#### Recherche Simple
1. Cliquer **New search**
2. Remplir les champs de recherche souhaités
3. Cliquer **Search!!!**

#### Recherche par US
1. Activer la recherche
2. Saisir uniquement le numéro US dans le champ US
3. Exécuter la recherche

---

## Bonnes Pratiques

### Numérotation Inventaire

- Utiliser une numérotation progressive sans interruption
- Un numéro = un objet (ou groupe homogène)
- Documenter le critère d'inventaire

### Classification

- Utiliser des vocabulaires contrôlés pour les classes
- Maintenir la cohérence dans la définition des types
- Mettre à jour le thésaurus si nécessaire

### Quantification Céramique

Pour une quantification correcte :
1. **Formes minimales (NMI)** : Compter uniquement les éléments diagnostiques (bords, fonds distinctifs)
2. **EVE** : Mesurer le pourcentage de circonférence conservée
3. **Poids** : Peser tous les fragments du groupe

### Documentation Photographique

- Photographier tous les objets diagnostiques
- Utiliser une échelle métrique dans les photos
- Associer les photos via le media manager

### Liaison US

- Vérifier toujours que l'US existe avant de l'associer
- Pour les objets hors contexte/nettoyage, utiliser des US appropriées
- Documenter les cas d'objets hors contexte

---

## Résolution des Problèmes

### Problèmes Courants

#### Numéro inventaire dupliqué
- **Erreur** : "Un enregistrement avec ce numéro inventaire existe déjà"
- **Cause** : Le numéro est déjà utilisé pour le site
- **Solution** : Vérifier le prochain numéro disponible avec "View all"

#### Images non affichées
- **Cause** : Chemin des images incorrect
- **Solution** :
  1. Vérifier la configuration du chemin dans Settings
  2. Vérifier que les images sont dans le bon dossier
  3. Réassocier les images

#### Quantifications vides
- **Cause** : Champs quantitatifs non remplis
- **Solution** : Remplir formes minimales/maximales ou total fragments

#### Export PDF vide
- **Cause** : Aucun enregistrement sélectionné
- **Solution** : Vérifier qu'au moins un enregistrement est affiché

#### GIS ne fonctionne pas
- **Cause** : L'US n'a pas de géométrie ou la couche n'est pas chargée
- **Solution** :
  1. Vérifier que la couche US est chargée dans QGIS
  2. Vérifier que l'US a une géométrie associée

---

## Vidéo Tutorial

### Vidéo 1 : Aperçu Fiche Inventaire
*Durée : 5-6 minutes*

`[Placeholder vidéo tutorial]`

**Contenus :**
- Interface générale
- Navigation entre les tabs
- Fonctionnalités principales

### Vidéo 2 : Documentation Céramique Complète
*Durée : 8-10 minutes*

`[Placeholder vidéo tutorial]`

**Contenus :**
- Remplissage de tous les champs
- Quantification céramique
- Éléments de l'objet
- Technologies

### Vidéo 3 : Gestion Médias et Photos
*Durée : 4-5 minutes*

`[Placeholder vidéo tutorial]`

**Contenus :**
- Association d'images
- Visualiseur
- SketchGPT

### Vidéo 4 : Export et Quantifications
*Durée : 5-6 minutes*

`[Placeholder vidéo tutorial]`

**Contenus :**
- Export PDF
- Export Excel
- Graphiques quantifications

---

## Récapitulatif Champs Base de Données

| Champ | Type | Base de données | Obligatoire |
|-------|------|-----------------|-------------|
| Site | Text | sito | Oui |
| Numéro inventaire | Integer | numero_inventario | Oui |
| Type objet | Text | tipo_reperto | Oui |
| Classe matériau | Text | criterio_schedatura | Non |
| Définition | Text | definizione | Non |
| Description | Text | descrizione | Non |
| Zone | Text | area | Non |
| US | Text | us | Non |
| Lavé | String(3) | lavato | Non |
| N° caisse | Text | nr_cassa | Non |
| Lieu conservation | Text | luogo_conservazione | Non |
| État conservation | String(200) | stato_conservazione | Non |
| Datation | String(200) | datazione_reperto | Non |
| Formes minimales | Integer | forme_minime | Non |
| Formes maximales | Integer | forme_massime | Non |
| Total fragments | Integer | totale_frammenti | Non |
| Corps céramique | String(200) | corpo_ceramico | Non |
| Revêtement | String(200) | rivestimento | Non |
| Diamètre bord | Numeric | diametro_orlo | Non |
| Poids | Numeric | peso | Non |
| Type | String(200) | tipo | Non |
| EVE bord | Numeric | eve_orlo | Non |
| Répertorié | String(3) | repertato | Non |
| Diagnostique | String(3) | diagnostico | Non |
| RA | Integer | n_reperto | Non |
| Type contenant | String(200) | tipo_contenitore | Non |
| Structure | String(200) | struttura | Non |
| Année | Integer | years | Non |

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
