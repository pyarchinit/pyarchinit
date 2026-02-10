# Tutorial 22 : Gestionnaire de Médias

## Introduction

Le **Gestionnaire de Médias** est l'outil central de PyArchInit pour la gestion des images et des contenus multimédias associés aux enregistrements archéologiques. Il permet de lier photos, dessins, vidéos et autres médias aux US, objets, tombes, structures et autres entités.

### Fonctionnalités Principales

- Gestion centralisée de tous les médias
- Liaison aux entités archéologiques (US, Objets, Pottery, Tombes, Structures, UT)
- Visualisation des miniatures et images en taille originale
- Tagging et catégorisation
- Recherche avancée
- Intégration avec GPT pour analyse d'images

## Accès

### Depuis le Menu
**PyArchInit** → **Media Manager**

### Depuis la Toolbar
Icône **Media Manager** dans la toolbar PyArchInit

## Interface

### Panneau Principal

```
+----------------------------------------------------------+
|                    Media Manager                          |
+----------------------------------------------------------+
| Site : [ComboBox]  Zone : [ComboBox]  US : [ComboBox]    |
+----------------------------------------------------------+
| [Grille Miniatures Images]                                |
|  +------+  +------+  +------+  +------+                  |
|  | img1 |  | img2 |  | img3 |  | img4 |                  |
|  +------+  +------+  +------+  +------+                  |
|  +------+  +------+  +------+  +------+                  |
|  | img5 |  | img6 |  | img7 |  | img8 |                  |
|  +------+  +------+  +------+  +------+                  |
+----------------------------------------------------------+
| Tags : [Liste tags associés]                              |
+----------------------------------------------------------+
| [Navigation] << < Enregistrement X de Y > >>              |
+----------------------------------------------------------+
```

### Filtres de Recherche

| Champ | Description |
|-------|-------------|
| Site | Filtrer par site archéologique |
| Zone | Filtrer par zone de fouille |
| US | Filtrer par Unité Stratigraphique |
| Sigle Structure | Filtrer par sigle de structure |
| N° Structure | Filtrer par numéro de structure |

### Contrôles Miniatures

| Contrôle | Fonction |
|----------|----------|
| Curseur taille | Ajuster la taille des miniatures |
| Double-clic | Ouvre l'image en taille originale |
| Sélection multiple | Ctrl+clic pour sélectionner plusieurs images |

## Gestion des Médias

### Ajouter de Nouvelles Images

1. Ouvrir le Gestionnaire de Médias
2. Sélectionner le site de destination
3. Cliquer sur **"Nouvel enregistrement"** ou utiliser le menu contextuel
4. Sélectionner les images à ajouter
5. Remplir les métadonnées

### Lier des Médias aux Entités

1. Sélectionner l'image dans la grille
2. Dans le panneau Tags, sélectionner :
   - **Type d'entité** : US, Objet, Pottery, Tombe, Structure, UT
   - **Identifiant** : Numéro/code de l'entité
3. Cliquer sur **"Lier"**

### Types d'Entités Supportées

| Type | Table BD | Description |
|------|----------|-------------|
| US | us_table | Unités Stratigraphiques |
| OBJET | inventario_materiali_table | Objets/Matériaux |
| CERAMIQUE | pottery_table | Céramique |
| TOMBE | tomba_table | Sépultures |
| STRUCTURE | struttura_table | Structures |
| UT | ut_table | Unités Topographiques |

### Visualiser l'Image Originale

- **Double-clic** sur la miniature
- Ouverture de la visionneuse avec :
  - Zoom (molette souris)
  - Déplacement (glissement)
  - Rotation
  - Mesure

## Fonctionnalités Avancées

### Recherche Avancée

Le Gestionnaire de Médias prend en charge la recherche par :
- Nom de fichier
- Date d'insertion
- Entité liée
- Tag/catégories

### Intégration GPT

Bouton **"GPT Sketch"** pour :
- Analyse automatique de l'image
- Génération de description
- Suggestions de classification

### Chargement Distant

Support pour images sur serveurs distants :
- URL directs
- Serveur FTP
- Stockage cloud

## Base de Données

### Tables Concernées

| Table | Description |
|-------|-------------|
| `media_table` | Métadonnées médias |
| `media_thumb_table` | Miniatures |
| `media_to_entity_table` | Liaisons entités |

### Classes Mapper

- `MEDIA` - Entité média principale
- `MEDIA_THUMB` - Miniature
- `MEDIATOENTITY` - Relation média-entité

## Bonnes Pratiques

### 1. Organisation des Fichiers

- Utiliser des noms de fichiers descriptifs
- Organiser par site/zone/année
- Maintenir des sauvegardes des originaux

### 2. Métadonnées

- Remplir toujours le site et la zone
- Ajouter des descriptions significatives
- Utiliser des tags cohérents

### 3. Qualité des Images

- Résolution minimale conseillée : 1920x1080
- Format : JPG pour les photos, PNG pour les dessins
- Compression modérée

### 4. Liaisons

- Lier chaque image aux entités pertinentes
- Vérifier les liaisons après import massif
- Utiliser la recherche pour les images non liées

## Résolution des Problèmes

### Miniatures Non Affichées

**Causes** :
- Chemin de l'image incorrect
- Fichier manquant
- Problèmes de permissions

**Solutions** :
- Vérifier le chemin dans la base de données
- Contrôler l'existence du fichier
- Vérifier les permissions du dossier

### Image Non Liable

**Causes** :
- Entité inexistante
- Type d'entité incorrect

**Solutions** :
- Vérifier l'existence de l'enregistrement
- Contrôler le type d'entité sélectionné

## Références

### Fichiers Source
- `tabs/Image_viewer.py` - Interface principale
- `modules/utility/pyarchinit_media_utility.py` - Utilitaires médias

### Base de Données
- `media_table` - Données médias
- `media_to_entity_table` - Liaisons

---

## Vidéo Tutorial

### Gestionnaire de Médias Complet
`[Placeholder : video_gestionnaire_medias.mp4]`

**Contenus** :
- Ajout d'images
- Liaison aux entités
- Recherche et filtres
- Fonctionnalités avancées

**Durée prévue** : 15-18 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../pyarchinit_media_manager_animation.html)
