# Tutorial 14 : SIG et Cartographie

## Introduction

PyArchInit est profondément intégré avec **QGIS**, exploitant toutes ses fonctionnalités SIG pour la gestion spatiale des données archéologiques. Ce tutoriel couvre l'intégration cartographique, les couches prédéfinies et les fonctionnalités avancées comme la **segmentation automatique SAM**.

### Fonctionnalités SIG Principales

- Visualisation des US sur carte
- Couches vectorielles prédéfinies
- Styling QML personnalisé
- Cotes et mesures SIG
- Segmentation automatique (SAM)
- Export cartographique

## Couches Prédéfinies PyArchInit

### Couches Vectorielles Principales

| Couche | Géométrie | Description |
|--------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | US dépôt |
| `pyunitastratigrafiche_usm` | MultiPolygon | US muraires |
| `pyarchinit_quote` | Point | Points de cote |
| `pyarchinit_siti` | Point | Localisation des sites |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Zones de fouille |
| `pyarchinit_strutture_ipotesi` | Polygon | Structures hypothétiques |
| `pyarchinit_documentazione` | Point | Références documentation |

### Attributs Couche US

| Champ | Type | Description |
|-------|------|-------------|
| `gid` | Integer | ID unique |
| `scavo_s` | Text | Nom du site |
| `area_s` | Text | Numéro de zone |
| `us_s` | Text | Numéro US |
| `stratigraph_index_us` | Integer | Index stratigraphique |
| `tipo_us_s` | Text | Type US |
| `rilievo_originale` | Text | Relevé d'origine |
| `disegnatore` | Text | Auteur du relevé |
| `data` | Date | Date du relevé |

## Visualisation des US sur Carte

### Depuis le Tab "Map" de la Fiche US

1. Ouvrir une fiche US
2. Sélectionner le tab **Map**
3. Fonctions disponibles :

| Bouton | Fonction |
|--------|----------|
| View US | Visualiser l'US courante sur la carte |
| View All | Visualiser toutes les US de la zone |
| New Record | Créer une nouvelle géométrie |
| Pan to | Centrer la carte sur l'US |

### Visualisation depuis Recherche

1. Exécuter une recherche US
2. Bouton **"View Record"** → visualise unique
3. Bouton **"View All"** → visualise tous les résultats

## Styling des Couches

### Fichiers QML

PyArchInit inclut des styles prédéfinis au format QML :
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Application du Style

1. Sélectionner la couche dans la légende
2. Clic droit → **Propriétés**
3. Tab **Style**
4. **Charger style** → sélectionner le QML

### Personnalisation

Les styles peuvent être personnalisés pour :
- Couleurs selon le type d'US
- Étiquettes avec numéro US
- Transparence
- Bordures et remplissages

## Cotes et Mesures

### Couche Cotes

La couche `pyarchinit_quote` mémorise :
- Coordonnées X, Y
- Cote Z (absolue)
- Type de point de cote
- US de référence
- Zone de référence

### Calcul Automatique des Cotes

Depuis la Fiche US, les cotes min/max sont calculées :
1. Requête aux points de cote associés à l'US
2. Extraction des valeurs minimum et maximum
3. Affichage dans le rapport

### Insertion des Cotes

1. Couche cotes en édition
2. Dessiner un point sur la carte
3. Remplir les attributs :
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentation Automatique SAM

### Qu'est-ce que SAM ?

**SAM (Segment Anything Model)** est un modèle d'intelligence artificielle développé par Meta pour la segmentation automatique d'images. PyArchInit l'intègre pour :
- Digitalisation automatique de pierres/éléments
- Segmentation d'orthophotos
- Accélération du relevé

### Accès à la Fonction

1. **PyArchInit** → **SAM Segmentation**
2. Ou depuis la toolbar : icône **SAM**

### Interface SAM

```
+--------------------------------------------------+
|        SAM Stone Segmentation                     |
+--------------------------------------------------+
| Input:                                            |
|   Raster Layer: [ComboBox orthophoto]            |
+--------------------------------------------------+
| Target Layer:                                     |
|   [o] pyunitastratigrafiche                      |
|   [ ] pyunitastratigrafiche_usm                  |
+--------------------------------------------------+
| Default Attributes:                               |
|   Site (sito): [champ automatique]               |
|   Area: [input zone]                             |
|   Stratigraphic Index: [1-10]                    |
|   Type US: [pierre|couche|accumulation|coupe]    |
+--------------------------------------------------+
| Segmentation Mode:                                |
|   [o] Automatic (détecter toutes les pierres)    |
|   [ ] Click mode (cliquer sur chaque pierre)     |
|   [ ] Box mode (dessiner un rectangle)           |
|   [ ] Polygon mode (dessiner à main levée)       |
|   [ ] From layer (utiliser polygone existant)    |
+--------------------------------------------------+
| Model:                                            |
|   [ComboBox modèle]                              |
|   API Key: [******]                              |
+--------------------------------------------------+
|        [Start Segmentation]  [Cancel]             |
+--------------------------------------------------+
```

### Modes de Segmentation

#### 1. Mode Automatique
- Segmente automatiquement tous les objets visibles
- Idéal pour les zones avec beaucoup de pierres
- Nécessite une orthophoto de bonne qualité

#### 2. Mode Clic
- Cliquer sur chaque objet à segmenter
- Clic droit ou Entrée pour terminer
- Échap pour annuler
- Plus précis pour des objets spécifiques

#### 3. Mode Rectangle
- Dessiner un rectangle sur la zone
- Segmente uniquement la zone sélectionnée
- Utile pour des zones délimitées

#### 4. Mode Polygone
- Dessiner un polygone libre
- Cliquer pour ajouter des sommets
- Clic droit pour compléter
- Pour des zones irrégulières

#### 5. Mode depuis Couche
- Utilise un polygone existant comme masque
- Sélectionner une couche polygonale
- Segmente uniquement à l'intérieur du polygone

### Modèles Disponibles

| Modèle | Type | Prérequis | Qualité |
|--------|------|-----------|---------|
| Replicate SAM-2 | API Cloud | Clé API | Excellente |
| Roboflow SAM-3 | API Cloud | Clé API | Excellente + Text Prompt |
| SAM vit_b | Local | 375MB VRAM | Bonne |
| SAM vit_l | Local | 1.2GB VRAM | Très bonne |
| SAM vit_h | Local | 2.5GB VRAM | Excellente |
| OpenCV | Local | Aucun | Basique |

### SAM-3 avec Text Prompt

La version SAM-3 (Roboflow) supporte les **prompts textuels** :
- "stones" - pierres
- "pottery fragments" - fragments céramiques
- "bones" - os
- Toute description textuelle

### Configuration API

#### Replicate API (SAM-2)
1. S'inscrire sur [replicate.com](https://replicate.com)
2. Obtenir la clé API
3. Insérer dans la configuration

#### Roboflow API (SAM-3)
1. S'inscrire sur [roboflow.com](https://roboflow.com)
2. Obtenir la clé API
3. Insérer dans la configuration

### Installation Locale SAM

Pour utilisation locale sans API :
```bash
# Créer un environnement virtuel
cd ~/pyarchinit/bin
python -m venv sam_venv

# Activer l'environnement
source sam_venv/bin/activate

# Installer les dépendances
pip install segment-anything torch torchvision

# Télécharger les modèles (optionnel)
# vit_b: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
# vit_l: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
# vit_h: https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
```

### Workflow SAM

1. **Préparation**
   - Charger l'orthophoto comme couche raster
   - Vérifier le système de référence
   - Préparer la couche cible

2. **Configuration**
   - Sélectionner le raster d'entrée
   - Configurer les attributs par défaut
   - Choisir le mode et le modèle

3. **Exécution**
   - Cliquer sur "Start Segmentation"
   - Attendre le traitement
   - Vérifier les résultats

4. **Post-traitement**
   - Contrôler les polygones générés
   - Attribuer les numéros US
   - Corriger les éventuelles erreurs

## Intégration Cartographique

### Export des Données SIG

Depuis la Fiche US, tab Map :
- **Export GeoPackage** : Couche en GPKG
- **Export Shapefile** : Couche en SHP
- **Export GeoJSON** : Couche en JSON

### Import des Données SIG

Importer des géométries existantes :
1. Charger la couche dans QGIS
2. Sélectionner les entités
3. Utiliser la fonction import

### Géotraitement

Opérations spatiales disponibles :
- Buffer
- Intersection
- Union
- Différence
- Centroïdes

## Bonnes Pratiques

### 1. Orthophotos

- Résolution minimale : 1-2 cm/pixel
- Format : GeoTIFF géoréférencé
- Système de référence : cohérent avec le projet

### 2. Digitalisation

- Utiliser l'accrochage pour la précision
- Vérifier la topologie
- Maintenir la cohérence des attributs

### 3. Segmentation SAM

- Orthophotos de haute qualité
- Éclairage uniforme
- Contraste adéquat objets/fond
- Post-vérification toujours nécessaire

### 4. Organisation des Couches

- Grouper par typologie
- Utiliser des styles cohérents
- Maintenir l'ordre dans la légende

## Résolution des Problèmes

### Couches Non Affichées

**Causes possibles** :
- Étendue incorrecte
- Système de référence différent
- Filtre actif

**Solutions** :
- Zoom sur la couche
- Vérifier le CRS
- Supprimer les filtres

### SAM Ne Fonctionne Pas

**Causes possibles** :
- Clé API non valide
- Raster non géoréférencé
- Modèle local non installé

**Solutions** :
- Vérifier la clé API
- Contrôler le géoréférencement
- Installer le modèle

### Géométries Corrompues

**Causes possibles** :
- Erreurs de digitalisation
- Import problématique

**Solutions** :
- Utiliser "Réparer les géométries"
- Redessiner l'élément

## Références

### Fichiers Source
- `modules/gis/pyarchinit_pyqgis.py` - Intégration SIG
- `tabs/Sam_Segmentation_Dialog.py` - Dialogue SAM
- `modules/gis/sam_map_tools.py` - Outils carte SAM

### Couches
- `pyunitastratigrafiche` - US dépôt
- `pyunitastratigrafiche_usm` - US muraires
- `pyarchinit_quote` - Cotes

---

## Vidéo Tutorial

### Intégration SIG
`[Placeholder : video_integration_sig.mp4]`

**Contenus** :
- Couches prédéfinies
- Visualisation des US
- Styling et étiquettes
- Export cartographique

**Durée prévue** : 15-18 minutes

### Segmentation SAM
`[Placeholder : video_sam_segmentation.mp4]`

**Contenus** :
- Configuration SAM
- Modes de segmentation
- Post-traitement
- Bonnes pratiques

**Durée prévue** : 12-15 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../pyarchinit_image_classification_animation.html)
