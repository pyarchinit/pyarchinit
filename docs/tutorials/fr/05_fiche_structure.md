# Tutorial 05 : Fiche Structure

## Introduction

La **Fiche Structure** est le module de PyArchInit dédié à la documentation des structures archéologiques. Une structure est un ensemble organisé d'Unités Stratigraphiques (US/USM) formant une entité constructive ou fonctionnelle reconnaissable, comme un mur, un dallage, une tombe, un four, ou tout autre élément construit.

### Concepts de Base

**Structure vs Unité Stratigraphique :**
- Une **US** est l'unité individuelle (couche, creusement, remplissage)
- Une **Structure** regroupe plusieurs US corrélées fonctionnellement
- Exemple : un mur (structure) est composé de fondation, élévation, mortier (différentes US)

**Hiérarchies :**
- Les structures peuvent avoir des rapports entre elles
- Chaque structure appartient à une ou plusieurs périodes/phases chronologiques
- Les structures sont liées aux US qui les composent

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Gestion Structures** (ou **Structure form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Structure** (bâtiment stylisé)

---

## Aperçu de l'Interface

La fiche présente une disposition organisée en sections fonctionnelles :

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | DB Info | État record, tri, compteur |
| 3 | Champs Identificatifs | Site, Sigle, Numéro structure |
| 4 | Champs Classification | Catégorie, Typologie, Définition |
| 5 | Zone Tab | Onglets thématiques pour données spécifiques |

---

## Toolbar DBMS

La toolbar principale fournit tous les outils pour la gestion des enregistrements.

### Boutons de Navigation

| Icône | Fonction | Description |
|-------|----------|-------------|
| First rec | Premier | Aller au premier enregistrement |
| Prev rec | Précédent | Aller à l'enregistrement précédent |
| Next rec | Suivant | Aller à l'enregistrement suivant |
| Last rec | Dernier | Aller au dernier enregistrement |

### Boutons CRUD

| Icône | Fonction | Description |
|-------|----------|-------------|
| New record | Nouveau | Créer un nouvel enregistrement structure |
| Save | Sauvegarder | Sauvegarder les modifications |
| Delete | Supprimer | Supprimer l'enregistrement actuel |

### Boutons de Recherche

| Icône | Fonction | Description |
|-------|----------|-------------|
| New search | Nouvelle recherche | Démarrer une nouvelle recherche |
| Search!!! | Exécuter recherche | Exécuter la recherche |
| Order by | Trier par | Trier les résultats |
| View all | Voir tout | Afficher tous les enregistrements |

### Boutons Spéciaux

| Icône | Fonction | Description |
|-------|----------|-------------|
| Map preview | Aperçu carte | Activer/désactiver l'aperçu carte |
| Media preview | Aperçu média | Activer/désactiver l'aperçu média |
| Draw Structure | Dessiner structure | Dessiner la structure sur la carte |
| Load to GIS | Charger GIS | Charger la structure sur la carte |
| Load all | Charger tout | Charger toutes les structures |
| PDF export | Export PDF | Exporter en PDF |
| Open directory | Ouvrir dossier | Ouvrir le dossier d'export |

---

## Champs Identificatifs

Les champs identificatifs définissent de manière unique la structure dans la base de données.

### Site

**Champ** : `comboBox_sito`
**Base de données** : `sito`

Sélectionne le site archéologique d'appartenance. Le menu déroulant affiche tous les sites enregistrés dans la base de données.

**Notes :**
- Champ obligatoire
- La combinaison Site + Sigle + Numéro doit être unique
- Bloqué après la création de l'enregistrement

### Sigle Structure

**Champ** : `comboBox_sigla_struttura`
**Base de données** : `sigla_struttura`

Code alphanumérique identifiant le type de structure. Conventions courantes :

| Sigle | Signification | Exemple |
|-------|---------------|---------|
| MR | Mur | MR 1 |
| ST | Structure | ST 5 |
| PV | Dallage | PV 2 |
| FO | Four | FO 1 |
| VA | Bassin | VA 3 |
| TM | Tombe | TM 10 |
| PT | Puits | PT 2 |
| CN | Canal | CN 1 |

**Notes :**
- Éditable avec saisie libre
- Bloqué après la création

### Numéro Structure

**Champ** : `numero_struttura`
**Base de données** : `numero_struttura`

Numéro progressif de la structure dans le sigle.

**Notes :**
- Champ numérique
- Doit être unique pour la combinaison Site + Sigle
- Bloqué après la création

---

## Champs de Classification

Les champs de classification définissent la nature de la structure.

### Catégorie Structure

**Champ** : `comboBox_categoria_struttura`
**Base de données** : `categoria_struttura`

Macro-catégorie fonctionnelle de la structure.

**Valeurs typiques :**
- Résidentielle
- Productive
- Funéraire
- Religieuse
- Défensive
- Hydraulique
- Viaire
- Artisanale

### Typologie Structure

**Champ** : `comboBox_tipologia_struttura`
**Base de données** : `tipologia_struttura`

Typologie spécifique au sein de la catégorie.

**Exemples par catégorie :**
| Catégorie | Typologies |
|-----------|------------|
| Résidentielle | Maison, Villa, Palais, Cabane |
| Productive | Four, Moulin, Pressoir |
| Funéraire | Tombe à fosse, Tombe à chambre, Sarcophage |
| Hydraulique | Puits, Citerne, Aqueduc, Canal |

### Définition Structure

**Champ** : `comboBox_definizione_struttura`
**Base de données** : `definizione_struttura`

Définition synthétique et spécifique de l'élément structurel.

**Exemples :**
- Mur périmétral
- Dallage en opus signinum
- Seuil en pierre
- Escalier
- Base de colonne

---

## Tab Données Descriptives

Le premier tab contient les champs textuels pour la description détaillée.

### Description

**Champ** : `textEdit_descrizione_struttura`
**Base de données** : `descrizione`

Champ textuel libre pour la description physique de la structure.

**Contenus conseillés :**
- Technique constructive
- Matériaux utilisés
- État de conservation
- Dimensions générales
- Orientation
- Caractéristiques particulières

**Exemple :**
```
Mur en opus incertum réalisé avec des blocs de calcaire local
de dimensions variables (15-30 cm). Liant en mortier de chaux
de couleur blanchâtre. Conservé sur une hauteur maximale de 1,20 m.
Largeur moyenne 50 cm. Orientation NE-SW. Présente des traces
d'enduit sur le côté intérieur.
```

### Interprétation

**Champ** : `textEdit_interpretazione_struttura`
**Base de données** : `interpretazione`

Interprétation fonctionnelle et historique de la structure.

**Contenus conseillés :**
- Fonction originale supposée
- Phases d'utilisation/réutilisation
- Comparaisons typologiques
- Cadrage chronologique
- Rapports avec d'autres structures

**Exemple :**
```
Mur périmétral nord d'un bâtiment résidentiel d'époque romaine
impériale. La technique constructive et les matériaux suggèrent
une datation au IIe siècle apr. J.-C. Dans une phase ultérieure (IIIe-IVe s.)
le mur a été partiellement spolié et intégré dans une
structure productive.
```

---

## Tab Périodisation

Ce tab gère le cadrage chronologique de la structure.

### Période et Phase Initiale

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Période Initiale | `periodo_iniziale` | Période de construction/début d'utilisation |
| Phase Initiale | `fase_iniziale` | Phase au sein de la période |

Les valeurs sont remplies automatiquement en fonction des périodes définies dans la Fiche Périodisation pour le site sélectionné.

### Période et Phase Finale

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Période Finale | `periodo_finale` | Période d'abandon/désaffection |
| Phase Finale | `fase_finale` | Phase au sein de la période |

### Datation Étendue

**Champ** : `comboBox_datazione_estesa`
**Base de données** : `datazione_estesa`

Datation littérale calculée automatiquement ou saisie manuellement.

**Formats :**
- "Ier s. av. J.-C. - IIe s. apr. J.-C."
- "100 av. J.-C. - 200 apr. J.-C."
- "Époque romaine impériale"

---

## Tab Rapports

Ce tab gère les relations entre structures.

### Tableau Rapports Structure

**Widget** : `tableWidget_rapporti`
**Base de données** : `rapporti_struttura`

Enregistre les rapports entre la structure actuelle et d'autres structures.

**Colonnes :**
| Colonne | Description |
|---------|-------------|
| Type de rapport | Relation stratigraphique/fonctionnelle |
| Site | Site de la structure corrélée |
| Sigle | Sigle de la structure corrélée |
| Numéro | Numéro de la structure corrélée |

**Types de rapport :**

| Rapport | Inverse | Description |
|---------|---------|-------------|
| Se lie à | Se lie à | Connexion physique contemporaine |
| Couvre | Couvert par | Relation de superposition |
| Coupe | Coupé par | Relation de coupe |
| Remplit | Rempli par | Relation de remplissage |
| S'appuie sur | Lui s'appuie | Relation d'appui |
| Égal à | Égal à | Même structure avec nom différent |

### Gestion des Lignes

| Bouton | Fonction |
|--------|----------|
| + | Ajouter nouvelle ligne |
| - | Supprimer ligne sélectionnée |

---

## Tab Éléments Constructifs

Ce tab documente les matériaux et éléments composant la structure.

### Matériaux Utilisés

**Widget** : `tableWidget_materiali_impiegati`
**Base de données** : `materiali_impiegati`

Liste des matériaux utilisés dans la construction.

**Colonne :**
- Matériaux : description du matériau

**Exemples de matériaux :**
- Blocs de calcaire
- Briques
- Mortier de chaux
- Galets de rivière
- Tuiles
- Marbre
- Tuf

### Éléments Structurels

**Widget** : `tableWidget_elementi_strutturali`
**Base de données** : `elementi_strutturali`

Liste des éléments constructifs avec quantité.

**Colonnes :**
| Colonne | Description |
|---------|-------------|
| Typologie élément | Type d'élément |
| Quantité | Nombre d'éléments |

**Exemples d'éléments :**
| Élément | Quantité |
|---------|----------|
| Base de colonne | 4 |
| Chapiteau | 2 |
| Seuil | 1 |
| Bloc équarri | 45 |

---

## Tab Mesures

Ce tab enregistre les dimensions de la structure.

### Tableau Mesures

**Widget** : `tableWidget_misurazioni`
**Base de données** : `misure_struttura`

**Colonnes :**
| Colonne | Description |
|---------|-------------|
| Type mesure | Type de dimension |
| Unité de mesure | m, cm, m², etc. |
| Valeur | Valeur numérique |

### Types de Mesure Courants

| Type | Description |
|------|-------------|
| Longueur | Dimension majeure |
| Largeur | Dimension mineure |
| Hauteur conservée | Élévation conservée |
| Hauteur originale | Élévation estimée originale |
| Profondeur | Pour structures enterrées |
| Diamètre | Pour structures circulaires |
| Épaisseur | Pour murs, dallages |
| Surface | Aire en m² |

### Exemple de Remplissage

| Type mesure | Unité de mesure | Valeur |
|-------------|-----------------|--------|
| Longueur | m | 8,50 |
| Largeur | cm | 55 |
| Hauteur conservée | m | 1,20 |
| Surface | m² | 4,68 |

---

## Tab Média

Gestion des images, vidéos et modèles 3D associés à la structure.

### Fonctionnalités

**Widget** : `iconListWidget`

Affiche les miniatures des médias associés.

### Boutons

| Icône | Fonction | Description |
|-------|----------|-------------|
| All images | Toutes images | Afficher toutes les images |
| Remove tags | Supprimer tags | Supprimer l'association média |
| Search images | Chercher images | Rechercher des images dans la base |

### Drag & Drop

Il est possible de glisser des fichiers directement sur la fiche :

**Formats supportés :**
- Images : JPG, JPEG, PNG, TIFF, TIF, BMP
- Vidéos : MP4, AVI, MOV, MKV, FLV
- 3D : OBJ, STL, PLY, FBX, 3DS

### Visualisation

- **Double-clic** sur miniature : ouvre le visualiseur
- Pour les vidéos : ouvre le lecteur vidéo intégré
- Pour la 3D : ouvre le visualiseur 3D PyVista

---

## Tab Map

Aperçu de la position de la structure sur la carte.

### Fonctionnalités

- Affiche la géométrie de la structure
- Zoom automatique sur l'élément
- Intégration avec les couches GIS du projet

---

## Intégration GIS

### Visualisation sur Carte

| Bouton | Fonction |
|--------|----------|
| Map Preview | Toggle aperçu dans le tab Map |
| Draw Structure | Mettre en évidence la structure sur la carte QGIS |
| Load to GIS | Charger la couche structures |
| Load All | Charger toutes les structures du site |

### Couches GIS

La fiche utilise la couche **pyarchinit_strutture** pour la visualisation :
- Géométrie : polygone ou multipolygone
- Attributs liés aux champs de la fiche

---

## Export et Impression

### Export PDF

Le bouton PDF ouvre un panneau avec des options d'export :

| Option | Description |
|--------|-------------|
| Liste Structures | Liste synthétique des structures |
| Fiches Structures | Fiches complètes détaillées |
| Imprimer | Générer le PDF |
| Convertir en Word | Convertir le PDF au format Word |

### Conversion PDF vers Word

Fonctionnalité avancée pour convertir les PDF générés en documents Word éditables :

1. Sélectionner le fichier PDF à convertir
2. Spécifier l'intervalle de pages (optionnel)
3. Cliquer sur "Convertir"
4. Le fichier Word est sauvegardé dans le même dossier

---

## Workflow Opérationnel

### Création d'une Nouvelle Structure

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouveau record**
   - Clic sur "New Record"
   - Les champs identificatifs deviennent éditables

3. **Données identificatives**
   ```
   Site : Villa Romaine de Settefinestre
   Sigle : MR
   Numéro : 15
   ```

4. **Classification**
   ```
   Catégorie : Résidentielle
   Typologie : Mur périmétral
   Définition : Mur en opus incertum
   ```

5. **Données descriptives** (Tab 1)
   ```
   Description : Mur réalisé en opus incertum avec
   blocs de calcaire local...

   Interprétation : Limite nord de la domus, phase I
   de l'implantation résidentielle...
   ```

6. **Périodisation** (Tab 2)
   ```
   Période initiale : I - Phase : A
   Période finale : II - Phase : B
   Datation : Ier s. av. J.-C. - IIe s. apr. J.-C.
   ```

7. **Rapports** (Tab 3)
   ```
   Se lie à : MR 16, MR 17
   Coupé par : ST 5
   ```

8. **Éléments constructifs** (Tab 4)
   ```
   Matériaux : Blocs de calcaire, Mortier de chaux
   Éléments : Blocs équarris (52), Seuil (1)
   ```

9. **Mesures** (Tab 5)
   ```
   Longueur : 12,50 m
   Largeur : 0,55 m
   Hauteur conservée : 1,80 m
   ```

10. **Sauvegarde**
    - Clic sur "Save"
    - Vérifier la confirmation de sauvegarde

### Recherche de Structures

1. Clic sur "New Search"
2. Remplir un ou plusieurs champs filtre :
   - Site
   - Sigle structure
   - Catégorie
   - Période
3. Clic sur "Search"
4. Naviguer parmi les résultats

### Modification d'une Structure Existante

1. Naviguer vers l'enregistrement souhaité
2. Modifier les champs nécessaires
3. Clic sur "Save"

---

## Bonnes Pratiques

### Nomenclature

- Utiliser des sigles cohérents dans tout le projet
- Documenter les conventions utilisées
- Éviter les duplications de numérotation

### Description

- Être systématique dans la description
- Suivre un schéma : technique > matériaux > dimensions > état
- Séparer description objective et interprétation

### Périodisation

- Toujours relier aux périodes définies dans la Fiche Périodisation
- Indiquer phase initiale et finale
- Utiliser la datation étendue pour la synthèse

### Rapports

- Enregistrer tous les rapports significatifs
- Vérifier la réciprocité des rapports
- Relier aux US qui composent la structure

### Médias

- Associer des photos représentatives
- Inclure des photos de détails constructifs
- Documenter les phases de fouille

---

## Résolution des Problèmes

### Problème : Structure non visible sur la carte

**Cause** : Géométrie non associée ou couche non chargée.

**Solution** :
1. Vérifier que la couche `pyarchinit_strutture` existe
2. Contrôler que la structure a une géométrie associée
3. Vérifier le système de référence

### Problème : Périodes non disponibles

**Cause** : Périodes non définies pour le site.

**Solution** :
1. Ouvrir la Fiche Périodisation
2. Définir les périodes pour le site actuel
3. Retourner à la Fiche Structure

### Problème : Erreur sauvegarde "enregistrement existant"

**Cause** : Combinaison Site + Sigle + Numéro déjà existante.

**Solution** :
1. Vérifier la numérotation existante
2. Utiliser un numéro progressif libre
3. Contrôler qu'il n'y a pas de doublons

### Problème : Médias non affichés

**Cause** : Chemin des images incorrect.

**Solution** :
1. Vérifier le chemin dans la configuration
2. Contrôler que les fichiers existent
3. Régénérer les miniatures si nécessaire

---

## Relations avec d'Autres Fiches

| Fiche | Relation |
|-------|----------|
| **Fiche Site** | Le site contient les structures |
| **Fiche US** | Les US composent les structures |
| **Fiche Périodisation** | Fournit la chronologie |
| **Fiche Inventaire Matériaux** | Mobilier associé aux structures |
| **Fiche Tombe** | Tombes comme type spécial de structure |

---

## Références

### Base de données

- **Table** : `struttura_table`
- **Classe mapper** : `STRUTTURA`
- **ID** : `id_struttura`

### Fichiers Source

- **UI** : `gui/ui/Struttura.ui`
- **Contrôleur** : `tabs/Struttura.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`

---

## Vidéo Tutorial

### Aperçu Fiche Structure
**Durée** : 5-6 minutes
- Présentation générale de l'interface
- Navigation entre les tabs
- Fonctionnalités principales

`[Placeholder vidéo : video_apercu_structure.mp4]`

### Documentation Complète d'une Structure
**Durée** : 10-12 minutes
- Création d'un nouveau record
- Remplissage de tous les champs
- Gestion des rapports et mesures

`[Placeholder vidéo : video_documentation_structure.mp4]`

### Intégration GIS et Export
**Durée** : 6-8 minutes
- Visualisation sur carte
- Chargement des couches
- Export PDF et Word

`[Placeholder vidéo : video_gis_export_structure.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
