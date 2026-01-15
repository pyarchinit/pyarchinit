# Tutorial 26 : Pottery Tools

## Introduction

**Pottery Tools** est un module avancé pour le traitement d'images céramiques. Il offre des outils pour extraire des images de PDF, générer des mises en page de planches, traiter des dessins avec l'IA (PotteryInk) et d'autres fonctionnalités spécialisées pour la documentation céramique.

### Fonctionnalités Principales

- Extraction d'images depuis PDF
- Génération de mises en page de planches céramiques
- Traitement d'images avec l'IA
- Conversion de format de dessins
- Intégration avec la Fiche Pottery

## Accès

### Depuis le Menu
**PyArchInit** → **Pottery Tools**

## Interface

### Panneau Principal

```
+--------------------------------------------------+
|              Pottery Tools                        |
+--------------------------------------------------+
| [Onglet : Extraction PDF]                        |
| [Onglet : Générateur de Layout]                  |
| [Onglet : Traitement d'Images]                   |
| [Onglet : PotteryInk IA]                         |
+--------------------------------------------------+
| [Barre de Progression]                           |
| [Messages Log]                                   |
+--------------------------------------------------+
```

## Onglet Extraction PDF

### Fonction

Extrait automatiquement les images de documents PDF contenant des planches céramiques.

### Utilisation

1. Sélectionner le fichier PDF source
2. Spécifier le dossier de destination
3. Cliquer sur **"Extraire"**
4. Les images sont enregistrées comme fichiers séparés

### Options

| Option | Description |
|--------|-------------|
| DPI | Résolution d'extraction (150-600) |
| Format | PNG, JPG, TIFF |
| Pages | Toutes ou plage spécifique |

## Onglet Générateur de Layout

### Fonction

Génère automatiquement des planches de céramique avec une mise en page standardisée.

### Types de Layout

| Layout | Description |
|--------|-------------|
| Grille | Images en grille régulière |
| Séquence | Images en séquence numérotée |
| Comparaison | Layout pour comparaison |
| Catalogue | Format catalogue avec légendes |

### Utilisation

1. Sélectionner les images à inclure
2. Choisir le type de layout
3. Configurer les paramètres (dimensions, marges)
4. Générer la planche

### Paramètres Layout

| Paramètre | Description |
|-----------|-------------|
| Taille de page | A4, A3, Personnalisée |
| Orientation | Portrait, Paysage |
| Marges | Espace des bords |
| Espacement | Distance entre images |
| Légendes | Texte sous les images |

## Onglet Traitement d'Images

### Fonction

Traitement par lots d'images céramiques.

### Opérations Disponibles

| Opération | Description |
|-----------|-------------|
| Redimensionner | Mise à l'échelle des images |
| Recadrer | Rognage automatique/manuel |
| Rotation | Rotation en degrés |
| Convertir | Changement de format |
| Optimiser | Compression qualité |

### Traitement par Lots

1. Sélectionner le dossier source
2. Choisir les opérations à appliquer
3. Spécifier la destination
4. Exécuter le traitement

## Onglet PotteryInk IA

### Fonction

Utilise l'intelligence artificielle pour :
- Conversion photo → dessin technique
- Reconnaissance des formes céramiques
- Suggestions de classification
- Mesure automatique

### Prérequis

- Environnement virtuel Python configuré
- Modèles IA téléchargés (YOLO, etc.)
- GPU recommandé (mais pas obligatoire)

### Utilisation

1. Charger l'image céramique
2. Sélectionner le type de traitement
3. Attendre le traitement IA
4. Vérifier et enregistrer le résultat

### Types de Traitement IA

| Type | Description |
|------|-------------|
| Ink Conversion | Convertit la photo en dessin technique |
| Shape Detection | Reconnaît la forme du vase |
| Profile Extraction | Extrait le profil céramique |
| Decoration Analysis | Analyse les décors |

## Environnement Virtuel

### Configuration Automatique

Au premier lancement, Pottery Tools :
1. Crée l'environnement virtuel dans `~/pyarchinit/bin/pottery_venv/`
2. Installe les dépendances nécessaires
3. Télécharge les modèles IA (si requis)

### Dépendances

- PyTorch
- Ultralytics (YOLO)
- OpenCV
- Pillow

### Vérification de l'Installation

Le log affiche l'état :
```
✓ Virtual environment created
✓ Dependencies installed
✓ Models downloaded
✓ Pottery Tools initialized successfully!
```

## Intégration Base de Données

### Liaison avec la Fiche Pottery

Les images traitées peuvent être :
- Liées automatiquement aux enregistrements Pottery
- Enregistrées avec les métadonnées appropriées
- Organisées par site/inventaire

## Bonnes Pratiques

### 1. Qualité des Images en Entrée

- Résolution minimale : 300 DPI
- Éclairage uniforme
- Fond neutre (blanc/gris)
- Échelle métrique visible

### 2. Traitement IA

- Toujours vérifier les résultats de l'IA
- Corriger manuellement si nécessaire
- Conserver les originaux et les fichiers traités

### 3. Organisation des Sorties

- Utiliser un nommage cohérent
- Organiser par site/campagne
- Maintenir la traçabilité

## Résolution des Problèmes

### Environnement Virtuel Non Créé

**Causes** :
- Python non trouvé
- Permissions insuffisantes

**Solutions** :
- Vérifier l'installation de Python
- Contrôler les permissions du dossier

### Traitement IA Lent

**Causes** :
- Aucun GPU disponible
- Images trop grandes

**Solutions** :
- Réduire la taille des images
- Utiliser le CPU (plus lent mais fonctionne)

### Extraction PDF Échouée

**Causes** :
- PDF protégé
- Format non supporté

**Solutions** :
- Vérifier la protection du PDF
- Essayer avec un autre logiciel PDF

## Références

### Fichiers Source
- `tabs/Pottery_tools.py` - Interface principale
- `modules/utility/pottery_utilities.py` - Utilitaires de traitement
- `gui/ui/Pottery_tools.ui` - Layout UI

### Dossiers
- `~/pyarchinit/bin/pottery_venv/` - Environnement virtuel
- `~/pyarchinit/models/` - Modèles IA

---

## Vidéo Tutorial

### Pottery Tools Complet
`[Placeholder : video_pottery_tools.mp4]`

**Contenus** :
- Extraction depuis PDF
- Génération de layout
- Traitement IA
- Intégration base de données

**Durée prévue** : 20-25 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
