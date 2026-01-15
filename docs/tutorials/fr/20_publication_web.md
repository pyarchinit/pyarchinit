# Tutorial 20 : Publication Web avec Lizmap

## Introduction

PyArchInit prend en charge la **publication web** des données archéologiques via **Lizmap**, une application qui permet de transformer les projets QGIS en applications web interactives.

### Qu'est-ce que Lizmap ?

Lizmap se compose de :
- **Plugin QGIS** : Pour configurer la publication
- **Lizmap Web Client** : Application web pour visualiser les cartes
- **QGIS Server** : Backend pour servir les cartes

### Avantages de la Publication Web

| Aspect | Description |
|--------|-------------|
| Accessibilité | Données consultables depuis un navigateur |
| Partage | Distribution facile aux parties prenantes |
| Interactivité | Zoom, pan, requêtes, popups |
| Mise à jour | Synchronisation avec la base de données |
| Mobile | Accès depuis smartphone/tablette |

## Prérequis

### Serveur

1. **QGIS Server** installé
2. **Lizmap Web Client** configuré
3. Serveur web (Apache/Nginx)
4. PHP 7.4+
5. PostgreSQL/PostGIS (conseillé)

### Client

1. **QGIS Desktop** avec plugin Lizmap
2. **PyArchInit** configuré
3. Projet QGIS enregistré

## Installation du Plugin Lizmap

### Depuis QGIS

1. **Extensions** → **Gestionnaire d'extensions**
2. Rechercher "Lizmap"
3. Installer **Lizmap**
4. Redémarrer QGIS

## Préparation du Projet

### 1. Organisation des Couches

Structure conseillée :
```
Projet QGIS
├── Groupe : Base
│   ├── Orthophoto
│   └── CTR/Cadastre
├── Groupe : Fouille
│   ├── pyunitastratigrafiche
│   ├── pyunitastratigrafiche_usm
│   └── pyarchinit_quote
├── Groupe : Documentation
│   ├── Photos géoréférencées
│   └── Relevés
└── Groupe : Analyse
    └── Matrice Harris (image)
```

### 2. Style des Couches

Pour chaque couche :
1. Appliquer le style approprié
2. Configurer les étiquettes
3. Définir l'échelle de visibilité

### 3. Popups et Attributs

Configurer les popups pour chaque couche :
1. Clic droit sur la couche → **Propriétés**
2. Onglet **Affichage**
3. Configurer **Info-bulle HTML**

Exemple de popup US :
```html
<h3>US [% "us_s" %]</h3>
<p><b>Zone :</b> [% "area_s" %]</p>
<p><b>Type :</b> [% "tipo_us_s" %]</p>
<p><b>Définition :</b> [% "definizione" %]</p>
```

### 4. Enregistrement du Projet

1. Enregistrer le projet (.qgz) dans le dossier Lizmap
2. Utiliser des chemins relatifs pour les données
3. Vérifier que toutes les couches sont accessibles

## Configuration Lizmap

### Ouverture du Plugin

1. **Web** → **Lizmap** → **Lizmap**

### Onglet Général

| Champ | Description | Valeur |
|-------|-------------|--------|
| Titre carte | Nom affiché | "Fouille Via Roma" |
| Résumé | Description | "Documentation archéologique..." |
| Image | Miniature projet | project_thumb.png |
| Repository | Dossier serveur | /var/www/lizmap/projects |

### Onglet Couches

Pour chaque couche configurer :

| Option | Description |
|--------|-------------|
| Activé | Couche visible dans Lizmap |
| Couche de base | Couche de fond (orthophoto, etc.) |
| Popup | Active le popup au clic |
| Édition | Permet la modification en ligne |
| Filtre | Filtres utilisateur |

### Onglet Fond de carte

Configurer les fonds :
- OpenStreetMap
- Google Maps (nécessite clé API)
- Bing Maps
- Orthophoto personnalisée

### Onglet Localisation

Recherche par localité :
- Configurer les couches pour la recherche
- Champs à rechercher
- Format d'affichage

### Onglet Édition (Optionnel)

Pour permettre l'édition en ligne :
1. Sélectionner les couches modifiables
2. Configurer les champs éditables
3. Définir les permissions

### Onglet Outils

Activer/désactiver :
- Impression
- Mesures
- Sélection
- Permalien
- etc.

### Sauvegarde de la Configuration

Cliquer sur **Enregistrer** pour générer le fichier `.qgs.cfg`

## Publication

### Upload sur Serveur

1. Copier les fichiers `.qgz` et `.qgz.cfg` sur le serveur
2. Vérifier les permissions des fichiers
3. Configurer QGIS Server

### Structure du Serveur

```
/var/www/lizmap/
├── lizmap/           # Application Lizmap
├── projects/         # Projets QGIS
│   ├── fouille_roma.qgz
│   └── fouille_roma.qgz.cfg
└── var/              # Données application
```

### Configuration QGIS Server

Fichier `/etc/apache2/sites-available/lizmap.conf` :
```apache
<VirtualHost *:80>
    ServerName lizmap.example.com
    DocumentRoot /var/www/lizmap/lizmap/www

    <Directory /var/www/lizmap/lizmap/www>
        AllowOverride All
        Require all granted
    </Directory>

    # QGIS Server
    ScriptAlias /cgi-bin/ /usr/lib/cgi-bin/
    <Directory "/usr/lib/cgi-bin">
        AllowOverride All
        Require all granted
    </Directory>

    FcgidInitialEnv QGIS_SERVER_LOG_FILE /var/log/qgis/qgis_server.log
    FcgidInitialEnv QGIS_SERVER_LOG_LEVEL 0
</VirtualHost>
```

## Accès Web

### URL de l'Application

```
http://lizmap.example.com/
```

### Navigation

1. Sélection du projet depuis la page d'accueil
2. Visualisation de la carte interactive
3. Outils dans la barre d'outils

### Fonctionnalités Utilisateur

| Fonction | Description |
|----------|-------------|
| Zoom | Molette souris, boutons +/- |
| Pan | Glisser-déposer sur la carte |
| Popup | Clic sur une entité |
| Recherche | Barre de recherche |
| Impression | Export en PDF |
| Permalien | URL partageable |

## Intégration PyArchInit

### Données en Temps Réel

Avec PostgreSQL :
- Les données sont toujours à jour
- Les modifications dans PyArchInit sont immédiatement visibles
- Pas de synchronisation manuelle

### Couches Conseillées

| Couche PyArchInit | Publication |
|-------------------|-------------|
| pyunitastratigrafiche | Oui, avec popup |
| pyunitastratigrafiche_usm | Oui, avec popup |
| pyarchinit_quote | Oui |
| pyarchinit_siti | Oui, comme vue d'ensemble |
| Matrice Harris | Comme image statique |

### Configuration Popup US

Template HTML avancé :
```html
<div class="us-popup">
    <h3 style="color:#2c3e50;">US [% "us_s" %]</h3>
    <table>
        <tr><td><b>Site :</b></td><td>[% "scavo_s" %]</td></tr>
        <tr><td><b>Zone :</b></td><td>[% "area_s" %]</td></tr>
        <tr><td><b>Type :</b></td><td>[% "tipo_us_s" %]</td></tr>
        <tr><td><b>Définition :</b></td><td>[% "definizione" %]</td></tr>
        <tr><td><b>Période :</b></td><td>[% "periodo" %]</td></tr>
    </table>
    [% if "foto_url" %]
    <img src="[% "foto_url" %]" style="max-width:200px;"/>
    [% end %]
</div>
```

## Sécurité

### Authentification

Lizmap prend en charge :
- Utilisateurs locaux
- LDAP
- OAuth2

### Configuration des Utilisateurs

Dans l'admin Lizmap :
1. Créer des groupes (admin, archéologue, public)
2. Créer des utilisateurs
3. Attribuer des permissions par projet

### Permissions par Couche

| Groupe | Visualiser | Éditer | Imprimer |
|--------|------------|--------|----------|
| Admin | Toutes | Toutes | Oui |
| Archéologue | Toutes | Certaines | Oui |
| Public | Base uniquement | Non | Non |

## Maintenance

### Mise à Jour des Projets

1. Modifier le projet dans QGIS Desktop
2. Régénérer la configuration Lizmap
3. Upload sur le serveur

### Cache

Gestion du cache des tuiles :
```bash
# Vider le cache
lizmap-cache-clearer.php -project fouille_roma

# Régénérer les tuiles
lizmap-tiles-seeder.php -project fouille_roma -bbox xmin,ymin,xmax,ymax
```

### Logs et Débogage

```bash
# Log QGIS Server
tail -f /var/log/qgis/qgis_server.log

# Log Lizmap
tail -f /var/www/lizmap/var/log/messages.log
```

## Bonnes Pratiques

### 1. Optimisation des Performances

- Utiliser des couches raster pré-tuilées
- Limiter le nombre d'entités par couche
- Configurer les échelles de visibilité
- Utiliser des index spatiaux

### 2. Expérience Utilisateur

- Popups informatifs mais concis
- Styles clairs et lisibles
- Organisation logique des couches
- Documentation pour les utilisateurs

### 3. Sécurité

- HTTPS obligatoire
- Mises à jour régulières
- Sauvegarde des configurations
- Surveillance des accès

### 4. Sauvegarde

- Sauvegarde des fichiers `.qgz` et `.cfg`
- Sauvegarde de la base de données PostgreSQL
- Versionnement des configurations

## Résolution des Problèmes

### Carte Non Affichée

**Causes** :
- QGIS Server non configuré
- Chemins de fichiers incorrects
- Permissions insuffisantes

**Solutions** :
- Vérifier les logs QGIS Server
- Contrôler les chemins dans le projet
- Vérifier les permissions des fichiers

### Popups Non Fonctionnels

**Causes** :
- Couche non configurée pour les popups
- HTML incorrect dans le template

**Solutions** :
- Activer les popups dans Lizmap
- Vérifier la syntaxe HTML

### Performances Lentes

**Causes** :
- Trop de données
- Cache non configuré
- Serveur sous-dimensionné

**Solutions** :
- Réduire les données visibles
- Configurer le cache des tuiles
- Augmenter les ressources du serveur

## Références

### Logiciels
- [Lizmap](https://www.lizmap.com/)
- [QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

### Documentation
- [Documentation Lizmap](https://docs.lizmap.com/)
- [Documentation QGIS Server](https://docs.qgis.org/latest/en/docs/server_manual/)

---

## Vidéo Tutorial

### Configuration Lizmap
`[Placeholder : video_lizmap_setup.mp4]`

**Contenus** :
- Installation du plugin
- Configuration du projet
- Publication

**Durée prévue** : 20-25 minutes

### Personnalisation Web
`[Placeholder : video_lizmap_custom.mp4]`

**Contenus** :
- Popups avancés
- Styles personnalisés
- Gestion des utilisateurs

**Durée prévue** : 15-18 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
