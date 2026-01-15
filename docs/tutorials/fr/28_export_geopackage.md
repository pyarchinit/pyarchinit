# Tutorial 28 : Export GeoPackage

## Introduction

La fonction **Export GeoPackage** permet d'empaqueter les couches vectorielles et raster de PyArchInit dans un seul fichier GeoPackage (.gpkg). Ce format est idéal pour le partage, l'archivage et la portabilité des données SIG.

### Avantages du GeoPackage

| Aspect | Avantage |
|--------|----------|
| Fichier unique | Toutes les données dans un seul fichier |
| Portabilité | Partage facile |
| Standard OGC | Compatibilité universelle |
| Multi-couches | Vectoriels et rasters ensemble |
| Basé sur SQLite | Léger et rapide |

## Accès

### Depuis le Menu
**PyArchInit** → **Empaqueter pour GeoPackage**

## Interface

### Panneau Export

```
+--------------------------------------------------+
|        Import dans GeoPackage                     |
+--------------------------------------------------+
| Destination :                                     |
|   [____________________________] [Parcourir]     |
+--------------------------------------------------+
| [Exporter les Couches Vectorielles]              |
| [Exporter les Couches Raster]                    |
+--------------------------------------------------+
```

## Procédure

### Export des Couches Vectorielles

1. Sélectionner les couches à exporter dans le panneau Couches QGIS
2. Ouvrir l'outil GeoPackage Export
3. Spécifier le chemin et le nom du fichier de destination
4. Cliquer sur **"Exporter les Couches Vectorielles"**

### Export des Couches Raster

1. Sélectionner les couches raster dans le panneau Couches
2. Spécifier la destination (même fichier ou nouveau)
3. Cliquer sur **"Exporter les Couches Raster"**

### Export Combiné

Pour inclure les vectoriels et les rasters dans le même GeoPackage :
1. D'abord exporter les vectoriels
2. Puis exporter les rasters dans le même fichier
3. Le système ajoute les couches au GeoPackage existant

## Sélection des Couches

### Méthode

1. Dans le panneau Couches de QGIS, sélectionner les couches désirées
   - Ctrl+clic pour une sélection multiple
   - Shift+clic pour une plage
2. Ouvrir Export GeoPackage
3. Les couches sélectionnées seront exportées

### Couches Recommandées

| Couche | Type | Notes |
|--------|------|-------|
| pyunitastratigrafiche | Vectorielle | US dépôt |
| pyunitastratigrafiche_usm | Vectorielle | US maçonnées |
| pyarchinit_quote | Vectorielle | Points de cote |
| pyarchinit_siti | Vectorielle | Sites |
| Orthophoto | Raster | Orthophoto de fouille |

## Sortie

### Structure du GeoPackage

```
output.gpkg
├── pyunitastratigrafiche (vector)
├── pyunitastratigrafiche_usm (vector)
├── pyarchinit_quote (vector)
└── ortofoto (raster)
```

### Chemin par Défaut

```
~/pyarchinit/pyarchinit_DB_folder/
```

## Options d'Export

### Couches Vectorielles

- Conserve les géométries originales
- Préserve tous les attributs
- Convertit automatiquement les noms avec des espaces (utilise des underscores)

### Couches Raster

- Supporte les formats courants (GeoTIFF, etc.)
- Conserve la géoréférence
- Préserve le système de référence

## Utilisations Typiques

### Partage de Projet

```
1. Sélectionner toutes les couches du projet
2. Exporter en GeoPackage
3. Partager le fichier .gpkg
4. Le destinataire l'ouvre directement dans QGIS
```

### Archivage de Campagne

```
1. En fin de campagne, sélectionner les couches finales
2. Exporter en GeoPackage daté
3. Archiver avec la documentation
```

### Sauvegarde SIG

```
1. Périodiquement exporter l'état actuel
2. Maintenir des versions datées
3. Utiliser pour la reprise après sinistre
```

## Bonnes Pratiques

### 1. Avant l'Export

- Vérifier la complétude des couches
- Contrôler le système de référence
- Enregistrer le projet QGIS

### 2. Nommage

- Utiliser des noms descriptifs pour le fichier
- Inclure la date dans le nom
- Éviter les caractères spéciaux

### 3. Vérification

- Ouvrir le GeoPackage créé
- Vérifier que toutes les couches sont présentes
- Contrôler les attributs

## Résolution des Problèmes

### Export Échoué

**Causes** :
- Couche non valide
- Chemin non accessible en écriture
- Espace disque insuffisant

**Solutions** :
- Vérifier la validité de la couche
- Contrôler les permissions du dossier
- Libérer de l'espace disque

### Couches Manquantes

**Cause** : Couche non sélectionnée

**Solution** : Vérifier la sélection dans le panneau Couches

### Raster Non Exporté

**Causes** :
- Format non supporté
- Fichier source non accessible

**Solutions** :
- Convertir le raster en GeoTIFF
- Vérifier le chemin du fichier source

## Références

### Fichiers Source
- `tabs/gpkg_export.py` - Interface d'export
- `gui/ui/gpkg_export.ui` - Layout UI

### Documentation
- [Standard GeoPackage](https://www.geopackage.org/)
- [Support GeoPackage QGIS](https://docs.qgis.org/)

---

## Vidéo Tutorial

### Export GeoPackage
`[Placeholder : video_geopackage.mp4]`

**Contenus** :
- Sélection des couches
- Export vectoriels et rasters
- Vérification de la sortie
- Bonnes pratiques

**Durée prévue** : 8-10 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
