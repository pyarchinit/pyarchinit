# Tutorial 23 : Recherche d'Images

## Introduction

La fonction **Recherche d'Images** permet de rechercher rapidement des images dans la base de données PyArchInit en filtrant par site, type d'entité et autres critères. C'est un outil complémentaire au Gestionnaire de Médias pour la recherche globale.

## Accès

### Depuis le Menu
**PyArchInit** → **Recherche Images**

## Interface

### Panneau de Recherche

```
+--------------------------------------------------+
|           Recherche d'Images                      |
+--------------------------------------------------+
| Filtres :                                         |
|   Site : [ComboBox]                              |
|   Type Entité : [-- Tous -- | US | Pottery | ...]|
|   [ ] Uniquement images non taguées              |
+--------------------------------------------------+
| [Rechercher]  [Effacer]                          |
+--------------------------------------------------+
| Résultats :                                       |
|  +------+  +------+  +------+                    |
|  | img  |  | img  |  | img  |                    |
|  | info |  | info |  | info |                    |
|  +------+  +------+  +------+                    |
+--------------------------------------------------+
| [Ouvrir Image] [Exporter] [Aller à l'Enregistrement]|
+--------------------------------------------------+
```

### Filtres Disponibles

| Filtre | Description |
|--------|-------------|
| Site | Sélectionner un site spécifique ou tous |
| Type Entité | US, Pottery, Matériaux, Tombe, Structure, UT |
| Uniquement non taguées | Afficher uniquement les images sans liaisons |

### Types d'Entités

| Type | Description |
|------|-------------|
| -- Tous -- | Toutes les entités |
| US | Unités Stratigraphiques |
| Pottery | Céramique |
| Matériaux | Objets/Inventaire |
| Tombe | Sépultures |
| Structure | Structures |
| UT | Unités Topographiques |

## Fonctionnalités

### Recherche de Base

1. Sélectionner les filtres souhaités
2. Cliquer sur **"Rechercher"**
3. Visualiser les résultats dans la grille

### Actions sur les Résultats

| Bouton | Fonction |
|--------|----------|
| Ouvrir Image | Visualise l'image en taille originale |
| Exporter | Exporte l'image sélectionnée |
| Aller à l'Enregistrement | Ouvre la fiche de l'entité liée |
| Ouvrir Gestionnaire Médias | Ouvre le Gestionnaire de Médias avec l'image sélectionnée |

### Menu Contextuel (Clic droit)

- **Ouvrir image**
- **Exporter image...**
- **Aller à l'enregistrement**

### Recherche d'Images Non Taguées

Case à cocher **"Uniquement images non taguées"** :
- Trouve les images dans la base de données sans liaisons
- Utile pour le nettoyage et l'organisation
- Permet d'identifier les images à cataloguer

## Workflow Typique

### 1. Trouver les Images d'un Site

```
1. Sélectionner le site dans le ComboBox
2. Laisser "-- Tous --" pour le type d'entité
3. Cliquer sur Rechercher
4. Parcourir les résultats
```

### 2. Trouver des Images US Spécifiques

```
1. Sélectionner le site
2. Sélectionner "US" comme type d'entité
3. Cliquer sur Rechercher
4. Double-clic pour ouvrir l'image
```

### 3. Identifier les Images Non Cataloguées

```
1. Sélectionner le site (ou tous)
2. Activer "Uniquement images non taguées"
3. Cliquer sur Rechercher
4. Pour chaque résultat :
   - Ouvrir l'image
   - Identifier le contenu
   - Lier via le Gestionnaire de Médias
```

## Export

### Export d'une Image Unique

1. Sélectionner l'image dans les résultats
2. Cliquer sur **"Exporter"** ou menu contextuel
3. Sélectionner la destination
4. Enregistrer

### Export Multiple

Pour l'export de plusieurs images, utiliser la fonction **Export d'Images** dédiée (Tutorial 24).

## Bonnes Pratiques

### 1. Recherche Efficace

- Utiliser des filtres spécifiques pour des résultats ciblés
- Commencer avec des filtres larges, puis restreindre
- Utiliser la recherche non taguées périodiquement

### 2. Organisation

- Cataloguer régulièrement les images non taguées
- Vérifier les liaisons après import
- Maintenir une nomenclature cohérente

## Résolution des Problèmes

### Aucun Résultat

**Causes** :
- Filtres trop restrictifs
- Aucune image pour les critères

**Solutions** :
- Élargir les filtres
- Vérifier l'existence des données

### Image Non Visualisable

**Causes** :
- Fichier non trouvé
- Format non supporté

**Solutions** :
- Vérifier le chemin du fichier
- Contrôler le format de l'image

## Références

### Fichiers Source
- `tabs/Image_search.py` - Interface de recherche
- `gui/ui/pyarchinit_image_search_dialog.ui` - Layout UI

### Base de Données
- `media_table` - Données médias
- `media_to_entity_table` - Liaisons

---

## Vidéo Tutorial

### Recherche d'Images
`[Placeholder : video_recherche_images.mp4]`

**Contenus** :
- Utilisation des filtres
- Recherche avancée
- Export des résultats

**Durée prévue** : 8-10 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
