# Tutorial 29 : Créer Votre Carte

## Introduction

**Créer Votre Carte** (Make Your Map) est la fonction de PyArchInit pour générer des cartes et des mises en page d'impression professionnelles directement depuis la visualisation actuelle de QGIS. Elle utilise des modèles de mise en page prédéfinis pour créer des sorties cartographiques standardisées.

### Fonctionnalités

- Génération rapide de cartes depuis la vue actuelle
- Modèles prédéfinis pour différents formats
- Personnalisation des en-têtes et légendes
- Export en PDF, PNG, SVG

## Accès

### Depuis la Barre d'Outils
Icône **"Make your Map"** (imprimante) dans la barre d'outils PyArchInit

### Depuis le Menu
**PyArchInit** → **Make your Map**

## Utilisation de Base

### Génération Rapide

1. Configurer la vue de la carte souhaitée dans QGIS
2. Définir le zoom et l'emprise corrects
3. Cliquer sur **"Make your Map"**
4. Sélectionner le modèle désiré
5. Saisir le titre et les informations
6. Générer la carte

## Modèles Disponibles

### Formats Standards

| Modèle | Format | Orientation | Utilisation |
|--------|--------|-------------|-------------|
| A4 Portrait | A4 | Vertical | Documentation standard |
| A4 Paysage | A4 | Horizontal | Vues étendues |
| A3 Portrait | A3 | Vertical | Planches détaillées |
| A3 Paysage | A3 | Horizontal | Planimétries |

### Éléments du Modèle

Chaque modèle comprend :
- **Zone de la carte** - Vue principale
- **En-tête** - Titre et informations du projet
- **Échelle** - Barre d'échelle graphique
- **Nord** - Flèche du nord
- **Légende** - Symboles des couches
- **Cartouche** - Informations techniques

## Personnalisation

### Informations à Saisir

| Champ | Description |
|-------|-------------|
| Titre | Nom de la carte |
| Sous-titre | Description supplémentaire |
| Site | Nom du site archéologique |
| Zone | Numéro de zone |
| Date | Date de création |
| Auteur | Nom de l'auteur |
| Échelle | Échelle de représentation |

### Style de la Carte

Avant de générer :
1. Configurer les styles des couches dans QGIS
2. Activer/désactiver les couches désirées
3. Définir les étiquettes
4. Vérifier la légende

## Export

### Formats Disponibles

| Format | Utilisation | Qualité |
|--------|-------------|---------|
| PDF | Impression, archive | Vectorielle |
| PNG | Web, présentations | Raster |
| SVG | Édition, publication | Vectorielle |
| JPG | Web, aperçu | Raster compressé |

### Résolution

| DPI | Utilisation |
|-----|-------------|
| 96 | Écran/aperçu |
| 150 | Publication web |
| 300 | Impression standard |
| 600 | Impression haute qualité |

## Intégration Time Manager

### Génération de Séquence

En combinaison avec le Time Manager :
1. Configurer le Time Manager
2. Pour chaque niveau stratigraphique :
   - Définir le niveau
   - Générer la carte
   - Enregistrer avec un nom progressif

### Sortie Animation

Série de cartes pour :
- Présentations
- Vidéos time-lapse
- Documentation progressive

## Workflow Typique

### 1. Préparation

```
1. Charger les couches nécessaires
2. Configurer les styles appropriés
3. Définir le système de référence
4. Définir l'emprise de la carte
```

### 2. Configuration de la Vue

```
1. Zoomer sur la zone d'intérêt
2. Activer/désactiver les couches
3. Vérifier les étiquettes
4. Contrôler la légende
```

### 3. Génération

```
1. Cliquer sur Make your Map
2. Sélectionner le modèle
3. Remplir les informations
4. Choisir le format d'export
5. Enregistrer
```

## Bonnes Pratiques

### 1. Avant la Génération

- Vérifier la complétude des données
- Contrôler les styles des couches
- Définir une échelle appropriée

### 2. Modèles

- Utiliser des modèles cohérents dans le projet
- Personnaliser les en-têtes pour l'institution
- Maintenir les standards cartographiques

### 3. Sortie

- Enregistrer en haute résolution pour l'impression
- Conserver une copie PDF pour l'archivage
- Utiliser un nommage descriptif

## Personnalisation des Modèles

### Modification d'un Modèle

Les modèles QGIS peuvent être modifiés :
1. Ouvrir le Gestionnaire de Mise en Page dans QGIS
2. Modifier le modèle existant
3. Enregistrer comme nouveau modèle
4. Disponible dans Make your Map

### Création d'un Modèle

1. Créer une nouvelle mise en page dans QGIS
2. Ajouter les éléments nécessaires
3. Configurer les variables pour les champs dynamiques
4. Enregistrer dans le dossier templates

## Résolution des Problèmes

### Carte Vide

**Causes** :
- Aucune couche active
- Emprise erronée

**Solutions** :
- Activer les couches visibles
- Zoomer sur la zone avec des données

### Légende Incomplète

**Cause** : Couches non configurées correctement

**Solution** : Vérifier les propriétés des couches dans QGIS

### Export Échoué

**Causes** :
- Chemin non accessible en écriture
- Format non supporté

**Solutions** :
- Vérifier les permissions du dossier
- Choisir un format différent

## Références

### Fichiers Source
- `pyarchinitPlugin.py` - Fonction runPrint
- Modèles dans le dossier `resources/templates/`

### QGIS
- Gestionnaire de Mise en Page
- Composeur d'Impression

---

## Vidéo Tutorial

### Créer Votre Carte
`[Placeholder : video_make_map.mp4]`

**Contenus** :
- Préparation de la vue
- Utilisation des modèles
- Personnalisation
- Export des formats

**Durée prévue** : 10-12 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../pyarchinit_create_map_animation.html)
