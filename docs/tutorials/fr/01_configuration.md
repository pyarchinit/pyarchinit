# Tutorial 01 : Guide de Configuration PyArchInit

## Introduction

La fenêtre de configuration de PyArchInit permet de paramétrer tous les éléments nécessaires au bon fonctionnement du plugin. Avant de documenter une fouille archéologique, il est essentiel de configurer correctement la connexion à la base de données et les chemins des ressources.

---

## Accès à la Configuration

Pour accéder à la configuration :
1. Ouvrir QGIS
2. Menu **PyArchInit** → **Config**

Ou depuis la barre d'outils PyArchInit, cliquer sur l'icône **Paramètres**.

---

## Onglet Paramètres de Connexion

C'est l'onglet principal pour configurer la connexion à la base de données.

### Section DB Settings

| Champ | Description |
|-------|-------------|
| **Database** | Type de base de données : `sqlite` (local) ou `postgres` (serveur) |
| **Host** | Adresse du serveur PostgreSQL (ex. `localhost` ou IP) |
| **DBname** | Nom de la base de données (ex. `pyarchinit`) |
| **Port** | Port de connexion (défaut : `5432` pour PostgreSQL) |
| **User** | Nom d'utilisateur |
| **Password** | Mot de passe |
| **SSL Mode** | Mode SSL pour PostgreSQL : `allow`, `prefer`, `require`, `disable` |

### Choix de la Base de Données

**SQLite/Spatialite** (Recommandé pour utilisateur unique) :
- Base de données locale, aucun serveur requis
- Idéal pour projets individuels ou de petite taille
- Le fichier `.sqlite` est enregistré dans `pyarchinit_DB_folder`

**PostgreSQL/PostGIS** (Recommandé pour équipe) :
- Base de données sur serveur, accès multi-utilisateurs
- Nécessite PostgreSQL avec extension PostGIS
- Supporte la gestion des utilisateurs et permissions
- Idéal pour grands projets avec plusieurs opérateurs

### Section Path Settings

| Champ | Description |
|-------|-------------|
| **Thumbnail path** | Chemin pour les miniatures d'images |
| **Image resize** | Chemin pour les images redimensionnées |
| **Logo path** | Chemin du logo personnalisé pour les rapports |

#### Chemins Distants Supportés

PyArchInit supporte également le stockage distant :
- **Google Drive** : `gdrive://folder/path/`
- **Dropbox** : `dropbox://folder/path/`
- **Amazon S3** : `s3://bucket/path/`
- **Cloudinary** : `cloudinary://cloud_name/folder/`
- **WebDAV** : `webdav://server/path/`
- **HTTP/HTTPS** : `https://server/path/`

### Boutons d'Action

| Bouton | Fonction |
|--------|----------|
| **Sauvegarder les paramètres** | Enregistre toutes les configurations |
| **Mettre à jour DB** | Met à jour le schéma sans perdre les données |
| **Aligner Postgres** | Aligne la structure PostgreSQL |
| **Aligner Spatialite** | Aligne la structure SQLite |

---

## Onglet Installation DB

Permet de créer une nouvelle base de données.

### Installation PostgreSQL/PostGIS

| Champ | Description |
|-------|-------------|
| **host** | Adresse du serveur (défaut : `localhost`) |
| **port** | Port PostgreSQL (5432) |
| **user** | Utilisateur avec droits de création |
| **password** | Mot de passe |
| **db name** | Nom de la nouvelle base |
| **Sélectionner SRID** | Système de référence spatiale |

### Installation SpatiaLite

| Champ | Description |
|-------|-------------|
| **db name** | Nom du fichier base de données |
| **Sélectionner SRID** | Système de référence spatiale |

### SRID Courants

| SRID | Description |
|------|-------------|
| 4326 | WGS 84 (coordonnées géographiques) |
| 32631 | WGS 84 / UTM zone 31N (France Nord) |
| 32632 | WGS 84 / UTM zone 32N (France Est) |
| 2154 | RGF93 / Lambert-93 (France métropolitaine) |

---

## Onglet Outils d'Importation

Permet d'importer des données depuis d'autres bases ou fichiers CSV.

### Base Source et Destination

Configurez séparément :
- **Base source** : D'où proviennent les données
- **Base destination** : Où importer les données

### Tables Disponibles pour Import

| Table | Description |
|-------|-------------|
| SITE | Sites archéologiques |
| US | Unités Stratigraphiques |
| PERIODISATION | Périodisation et phases |
| INVENTARIO_MATERIALI | Inventaire du mobilier |
| POTTERY | Céramique |
| STRUTTURA | Structures |
| TOMBA | Tombes |
| ALL | Toutes les tables |

### Options d'Import

| Option | Description |
|--------|-------------|
| **Replace** | Remplace les enregistrements existants |
| **Ignore** | Ignore les doublons |
| **Abort** | Interrompt en cas d'erreur |

---

## Onglet Graphviz

Graphviz est nécessaire pour générer les diagrammes de la Matrice de Harris.

### Configuration

| Champ | Description |
|-------|-------------|
| **Chemin bin** | Chemin vers le dossier `/bin` de Graphviz |
| **Sauvegarder** | Enregistre le chemin dans PATH |

### Installation Graphviz

**Windows** : Télécharger depuis https://graphviz.org/download/

**macOS** :
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian)** :
```bash
sudo apt-get install graphviz
```

---

## Onglet FTP vers Lizmap

Permet de publier les données sur un serveur Lizmap pour la visualisation web.

### Paramètres de Connexion FTP

| Champ | Description |
|-------|-------------|
| **Adresse IP** | Adresse du serveur FTP |
| **Port** | Port FTP (défaut : 21) |
| **User** | Nom d'utilisateur FTP |
| **Password** | Mot de passe FTP |

### Opérations Disponibles

- Connecter/Déconnecter
- Changer de répertoire
- Créer un répertoire
- Télécharger/Uploader des fichiers

---

## Workflow Recommandé pour Nouveau Projet

1. **Ouvrir la Configuration** depuis le menu PyArchInit
2. **Choisir le type de base de données** (SQLite ou PostgreSQL)
3. **Onglet Installation DB** : Créer une nouvelle base avec le SRID approprié
4. **Onglet Paramètres** : Configurer la connexion
5. **Définir les chemins** pour miniatures, images et logo
6. **Sauvegarder les paramètres**
7. **Tester la connexion** en ouvrant une fiche (ex. Site)

---

## Résolution des Problèmes

### Erreur de connexion PostgreSQL
- Vérifier que le serveur PostgreSQL est démarré
- Contrôler host, port et identifiants
- Vérifier que l'extension PostGIS est installée

### Base SQLite non trouvée
- Vérifier que le fichier existe dans `pyarchinit_DB_folder`
- Contrôler les permissions de lecture/écriture

### Graphviz ne fonctionne pas
- Vérifier l'installation de Graphviz
- Configurer manuellement le chemin
- Redémarrer QGIS après configuration

---

## Video Tutorial

### Configuration Complète
`[Placeholder : video_configuration.mp4]`

**Contenus** :
- Choix du type de base de données
- Configuration des connexions
- Installation Graphviz
- Test de connexion

**Durée prévue** : 15-20 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour mieux comprendre le processus d'installation et de configuration.

[Ouvrir l'Animation Installation](../../pyarchinit_installation_animation.html)

Explorez l'animation interactive pour la gestion du stockage distant.

[Ouvrir l'Animation Stockage Distant](../../pyarchinit_remote_storage_animation.html)
