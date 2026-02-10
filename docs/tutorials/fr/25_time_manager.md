# Tutorial 25 : Time Manager (Contrôleur Temporel SIG)

## Introduction

Le **Time Manager** (Contrôleur Temporel SIG) est un outil avancé pour visualiser la séquence stratigraphique dans le temps. Il permet de "naviguer" à travers les niveaux stratigraphiques en utilisant un contrôle temporel, visualisant progressivement les US de la plus récente à la plus ancienne.

### Fonctionnalités Principales

- Visualisation progressive des niveaux stratigraphiques
- Contrôle via molette/curseur
- Mode cumulatif ou niveau unique
- Génération automatique d'images/vidéo
- Intégration avec la Matrice de Harris

## Accès

### Depuis le Menu
**PyArchInit** → **Time Manager**

### Prérequis

- Couche avec champ `order_layer` (index stratigraphique)
- US avec order_layer rempli
- Couches chargées dans QGIS

## Interface

### Panneau Principal

```
+--------------------------------------------------+
|         GIS Time Management                       |
+--------------------------------------------------+
| Couches disponibles :                             |
| [ ] pyunitastratigrafiche                        |
| [ ] pyunitastratigrafiche_usm                    |
| [ ] autre_couche                                 |
+--------------------------------------------------+
|              [Molette Circulaire]                |
|                   /  \                           |
|                  /    \                          |
|                 /______\                         |
|                                                  |
|         Niveau : [SpinBox : 1-N]                |
+--------------------------------------------------+
| [x] Mode Cumulatif (affiche <= niveau)          |
+--------------------------------------------------+
| [ ] Afficher Matrice    [Stop] [Générer Vidéo]  |
+--------------------------------------------------+
| [Aperçu Matrice/Image]                           |
+--------------------------------------------------+
```

### Contrôles

| Contrôle | Fonction |
|----------|----------|
| Case à cocher Couche | Sélectionne les couches à contrôler |
| Molette | Navigation entre les niveaux (rotation) |
| SpinBox | Saisie directe du niveau |
| Mode Cumulatif | Affiche tous les niveaux jusqu'au sélectionné |
| Afficher Matrice | Visualise la Matrice de Harris synchronisée |

## Champ order_layer

### Qu'est-ce que order_layer ?

Le champ `order_layer` définit l'ordre stratigraphique de visualisation :
- **1** = Niveau le plus récent (superficiel)
- **N** = Niveau le plus ancien (profond)

### Remplissage de order_layer

Dans la Fiche US, champ **"Index Stratigraphique"** :
1. Attribuer des valeurs croissantes depuis la surface
2. Les US contemporaines peuvent avoir la même valeur
3. Suivre la séquence de la Matrice

### Exemple

| US | order_layer | Description |
|----|-------------|-------------|
| US001 | 1 | Humus superficiel |
| US002 | 2 | Couche de labour |
| US003 | 3 | Effondrement |
| US004 | 4 | Sol d'occupation |
| US005 | 5 | Fondation |

## Modes de Visualisation

### Mode Niveau Unique

Case à cocher **NON** active :
- Affiche UNIQUEMENT les US du niveau sélectionné
- Utile pour isoler des couches individuelles
- Visualisation "en tranches"

### Mode Cumulatif

Case à cocher **ACTIVE** :
- Affiche toutes les US jusqu'au niveau sélectionné
- Simule la fouille progressive
- Visualisation plus réaliste

## Intégration Matrice

### Visualisation Synchronisée

Avec la case **"Afficher Matrice"** active :
- La Matrice de Harris apparaît dans le panneau
- Elle se met à jour en synchronisation avec le niveau
- Elle met en évidence les US du niveau courant

### Génération d'Images

Le Time Manager peut générer :
- Captures d'écran pour chaque niveau
- Séquence d'images
- Vidéo time-lapse

## Génération Vidéo/Images

### Processus

1. Sélectionner les couches à inclure
2. Configurer la plage de niveaux (min-max)
3. Cliquer sur **"Générer Vidéo"**
4. Attendre le traitement
5. Sortie dans le dossier désigné

### Sortie

- Images PNG pour chaque niveau
- Optionnel : vidéo MP4 compilée

## Workflow Typique

### 1. Préparation

```
1. Ouvrir le projet QGIS avec les couches US
2. Vérifier que order_layer est rempli
3. Ouvrir le Time Manager
```

### 2. Sélection des Couches

```
1. Sélectionner les couches à contrôler
2. Généralement : pyunitastratigrafiche et/ou _usm
```

### 3. Navigation

```
1. Utiliser la molette ou le spinbox
2. Observer le changement de visualisation
3. Activer/désactiver le mode cumulatif
```

### 4. Documentation

```
1. Activer "Afficher Matrice"
2. Générer des captures d'écran significatives
3. Optionnel : générer une vidéo
```

## Templates de Mise en Page

### Chargement de Template

Le Time Manager prend en charge les templates QGIS pour :
- Mises en page d'impression personnalisées
- En-têtes et légendes
- Formats standards

### Templates Disponibles

Dans le dossier `resources/templates/` :
- Template de base
- Template avec Matrice
- Template pour vidéo

## Bonnes Pratiques

### 1. order_layer

- Remplir AVANT d'utiliser le Time Manager
- Utiliser des valeurs consécutives
- US contemporaines = même valeur

### 2. Visualisation

- Commencer par le niveau 1 (superficiel)
- Procéder par ordre croissant
- Utiliser le mode cumulatif pour les présentations

### 3. Documentation

- Capturer des écrans aux niveaux significatifs
- Documenter les passages de phase
- Générer des vidéos pour les rapports

## Résolution des Problèmes

### Couches Non Visibles dans la Liste

**Cause** : Couche sans champ order_layer

**Solution** :
- Ajouter le champ order_layer à la couche
- Le remplir avec des valeurs appropriées

### Aucun Changement Visuel

**Causes** :
- order_layer non rempli
- Filtre non appliqué

**Solutions** :
- Vérifier les valeurs order_layer dans les US
- Contrôler que la couche est sélectionnée

### Molette Ne Répond Pas

**Cause** : Aucune couche sélectionnée

**Solution** : Sélectionner au moins une couche dans la liste

## Références

### Fichiers Source
- `tabs/Gis_Time_controller.py` - Interface principale
- `gui/ui/Gis_Time_controller.ui` - Layout UI

### Champ Base de Données
- `us_table.order_layer` - Index stratigraphique

---

## Vidéo Tutorial

### Time Manager
`[Placeholder : video_time_manager.mp4]`

**Contenus** :
- Configuration de order_layer
- Navigation temporelle
- Génération de vidéo
- Intégration avec la Matrice

**Durée prévue** : 15-18 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../animations/pyarchinit_timemanager_animation.html)
