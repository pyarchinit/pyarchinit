# Tutorial 24 : Export d'Images

## Introduction

La fonction **Export d'Images** permet d'exporter en masse les images associées aux enregistrements archéologiques, en les organisant automatiquement dans des dossiers par période, phase, type d'entité.

## Accès

### Depuis le Menu
**PyArchInit** → **Export Images**

## Interface

### Panneau Export

```
+--------------------------------------------------+
|           Export d'Images                         |
+--------------------------------------------------+
| Site : [ComboBox sélection site]                 |
| Année : [ComboBox année fouille]                 |
+--------------------------------------------------+
| Type d'Export :                                   |
|   [o] Toutes les images                          |
|   [ ] US uniquement                              |
|   [ ] Objets uniquement                          |
|   [ ] Pottery uniquement                         |
+--------------------------------------------------+
| [Ouvrir Dossier]           [Exporter]            |
+--------------------------------------------------+
```

### Options d'Export

| Option | Description |
|--------|-------------|
| Toutes les images | Exporte tout le matériel photographique |
| US uniquement | Exporte uniquement les images liées aux US |
| Objets uniquement | Exporte uniquement les images des objets |
| Pottery uniquement | Exporte uniquement les images de céramique |

## Structure de Sortie

### Organisation des Dossiers

L'export crée une structure hiérarchique :

```
pyarchinit_image_export/
└── [Nom Site] - Toutes les images/
    ├── Période - 1/
    │   ├── Phase - 1/
    │   │   ├── US_001/
    │   │   │   ├── photo_001.jpg
    │   │   │   └── photo_002.jpg
    │   │   └── US_002/
    │   │       └── photo_003.jpg
    │   └── Phase - 2/
    │       └── US_003/
    │           └── photo_004.jpg
    └── Période - 2/
        └── ...
```

### Convention de Nommage

Les fichiers conservent leur nom original, organisés par :
1. **Période** - Période chronologique initiale
2. **Phase** - Phase chronologique initiale
3. **Entité** - US, Objet, etc.

## Processus d'Export

### Étape 1 : Sélection des Paramètres

1. Sélectionner le **Site** dans le ComboBox
2. Sélectionner l'**Année** (optionnel)
3. Choisir le **Type d'export**

### Étape 2 : Exécution

1. Cliquer sur **"Exporter"**
2. Attendre la fin du processus
3. Message de confirmation

### Étape 3 : Vérification

1. Cliquer sur **"Ouvrir Dossier"**
2. Vérifier la structure créée
3. Contrôler la complétude

## Dossier de Sortie

### Chemin Standard

```
~/pyarchinit/pyarchinit_image_export/
```

### Contenu

- Dossiers organisés par site
- Sous-dossiers par période/phase
- Images originales (non redimensionnées)

## Filtre par Année

Le ComboBox **Année** permet de :
- Exporter uniquement les images d'une campagne spécifique
- Organiser l'export par année de fouille
- Réduire la taille de l'export

## Bonnes Pratiques

### 1. Avant l'Export

- Vérifier les liaisons images-entités
- Contrôler la périodisation des US
- S'assurer d'avoir suffisamment d'espace disque

### 2. Pendant l'Export

- Ne pas interrompre le processus
- Attendre le message de fin

### 3. Après l'Export

- Vérifier la structure des dossiers
- Contrôler la complétude des images
- Créer une sauvegarde si nécessaire

## Utilisations Typiques

### Préparation de Rapport

```
1. Sélectionner le site
2. Exporter toutes les images
3. Utiliser la structure pour les chapitres du rapport
```

### Remise à l'Administration

```
1. Sélectionner le site et l'année
2. Exporter par typologie demandée
3. Organiser selon les standards administratifs
```

### Sauvegarde de Campagne

```
1. En fin de campagne, tout exporter
2. Archiver sur stockage externe
3. Vérifier l'intégrité
```

## Résolution des Problèmes

### Export Incomplet

**Causes** :
- Images non liées
- Chemins de fichiers incorrects

**Solutions** :
- Vérifier les liaisons dans le Gestionnaire de Médias
- Contrôler l'existence des fichiers source

### Structure Incorrecte

**Causes** :
- Périodisation manquante
- US sans période/phase

**Solutions** :
- Remplir la périodisation des US
- Attribuer période/phase à toutes les US

## Références

### Fichiers Source
- `tabs/Images_directory_export.py` - Interface d'export
- `gui/ui/Images_directory_export.ui` - Layout UI

### Dossiers
- `~/pyarchinit/pyarchinit_image_export/` - Sortie de l'export

---

## Vidéo Tutorial

### Export d'Images
`[Placeholder : video_export_images.mp4]`

**Contenus** :
- Configuration de l'export
- Structure de sortie
- Organisation des archives

**Durée prévue** : 10-12 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
