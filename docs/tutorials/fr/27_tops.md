# Tutorial 27 : TOPS - Total Open Station

## Introduction

**TOPS** (Total Open Station) est l'intégration de PyArchInit avec le logiciel open source pour le téléchargement et la conversion de données depuis les stations totales. Il permet d'importer directement les relevés topographiques dans le système PyArchInit.

### Qu'est-ce que Total Open Station ?

Total Open Station est un logiciel libre pour :
- Téléchargement de données depuis les stations totales
- Conversion entre formats
- Export vers des formats compatibles SIG

PyArchInit intègre TOPS pour simplifier l'importation des données de fouille.

## Accès

### Depuis le Menu
**PyArchInit** → **TOPS (Total Open Station)**

## Interface

### Panneau Principal

```
+--------------------------------------------------+
|         Total Open Station to PyArchInit          |
+--------------------------------------------------+
| Entrée :                                          |
|   Fichier : [___________________] [Parcourir]    |
|   Format d'entrée : [ComboBox formats]           |
+--------------------------------------------------+
| Sortie :                                          |
|   Fichier : [___________________] [Parcourir]    |
|   Format de sortie : [csv | dxf | ...]           |
+--------------------------------------------------+
| [ ] Convertir les coordonnées                    |
+--------------------------------------------------+
| [Aperçu des Données - TableView]                 |
+--------------------------------------------------+
|              [Exporter]                           |
+--------------------------------------------------+
```

## Formats Supportés

### Formats d'Entrée (Stations Totales)

| Format | Fabricant | Extension |
|--------|-----------|-----------|
| Leica GSI | Leica | .gsi |
| Topcon GTS | Topcon | .raw |
| Sokkia SDR | Sokkia | .sdr |
| Trimble DC | Trimble | .dc |
| Nikon RAW | Nikon | .raw |
| Zeiss R5 | Zeiss | .r5 |
| CSV générique | - | .csv |

### Formats de Sortie

| Format | Utilisation |
|--------|-------------|
| CSV | Import dans PyArchInit Quote |
| DXF | Import dans CAO/SIG |
| GeoJSON | Import direct SIG |
| Shapefile | Standard SIG |

## Workflow

### 1. Import des Données depuis la Station Totale

```
1. Connecter la station totale au PC
2. Télécharger le fichier de données (format natif)
3. Enregistrer dans le dossier de travail
```

### 2. Conversion avec TOPS

```
1. Ouvrir TOPS dans PyArchInit
2. Sélectionner le fichier d'entrée (Parcourir)
3. Choisir le format d'entrée correct
4. Définir le fichier de sortie
5. Choisir le format de sortie (CSV recommandé)
6. Cliquer sur Exporter
```

### 3. Import dans PyArchInit

Après l'export en CSV :
1. Le système demande automatiquement :
   - **Nom du site** archéologique
   - **Unité de mesure** (mètres)
   - **Nom du dessinateur**
2. Les points sont chargés comme couche QGIS
3. Optionnel : copie vers la couche Quote US

### 4. Conversion des Coordonnées (Optionnel)

Si la case **"Convertir les coordonnées"** est activée :
- Saisir les décalages X, Y, Z
- Appliquer la translation des coordonnées
- Utile pour les systèmes de référence locaux

## Aperçu des Données

### TableView

Affiche un aperçu des données importées :
| point_name | area_q | x | y | z |
|------------|--------|---|---|---|
| P001 | 1000 | 100.234 | 200.456 | 10.50 |
| P002 | 1000 | 100.567 | 200.789 | 10.45 |

### Modification des Données

- Sélectionner les lignes à supprimer
- Le bouton **Delete** supprime les lignes sélectionnées
- Utile pour filtrer les points non nécessaires

## Intégration Quote US

### Copie Automatique

Après l'import, TOPS peut copier les points dans la couche **"Quote US dessin"** :
1. Le nom du site est demandé
2. L'unité de mesure est demandée
3. Le dessinateur est demandé
4. Les points sont copiés avec les attributs corrects

### Attributs Remplis

| Attribut | Valeur |
|----------|--------|
| sito_q | Nom du site saisi |
| area_q | Extrait de point_name |
| unita_misu_q | Unité saisie (mètres) |
| disegnatore | Nom saisi |
| data | Date actuelle |

## Conventions de Nommage

### Format point_name

Pour l'extraction automatique de l'area :
```
[AREA]-[NOM_POINT]
Exemple : 1000-P001
```

Le système sépare automatiquement :
- `area_q` = 1000
- `point_name` = P001

## Bonnes Pratiques

### 1. Sur le Terrain

- Utiliser un nommage cohérent pour les points
- Inclure le code de l'area dans le nom du point
- Noter le système de référence utilisé

### 2. Import

- Vérifier le format d'entrée correct
- Contrôler l'aperçu avant l'export
- Supprimer les points erronés/dupliqués

### 3. Post-Import

- Vérifier les coordonnées dans QGIS
- Contrôler la couche Quote US
- Lier les points aux US correctes

## Résolution des Problèmes

### Format Non Reconnu

**Cause** : Format de la station non supporté

**Solution** :
- Exporter depuis la station en format générique (CSV)
- Vérifier la documentation de la station

### Coordonnées Erronées

**Causes** :
- Système de référence différent
- Décalage non appliqué

**Solutions** :
- Vérifier le système de référence du projet
- Appliquer la conversion des coordonnées

### Couche Non Créée

**Cause** : Erreur pendant l'import

**Solution** :
- Contrôler le log des erreurs
- Vérifier le format du fichier de sortie
- Répéter la conversion

## Références

### Fichiers Source
- `tabs/tops_pyarchinit.py` - Interface principale
- `gui/ui/Tops2pyarchinit.ui` - Layout UI

### Logiciel Externe
- [Total Open Station](https://tops.iosa.it/) - Logiciel principal
- Documentation des formats de stations

---

## Vidéo Tutorial

### Import TOPS
`[Placeholder : video_tops.mp4]`

**Contenus** :
- Téléchargement depuis la station totale
- Conversion des formats
- Import dans PyArchInit
- Intégration Quote US

**Durée prévue** : 12-15 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
