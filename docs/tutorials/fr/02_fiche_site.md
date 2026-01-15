# Tutorial 02 : Fiche Site

## Introduction

La **Fiche Site** est le point de départ pour la documentation d'une fouille archéologique dans PyArchInit. Chaque projet archéologique commence par la création d'un site, qui sert de conteneur principal pour toutes les autres informations (Unités Stratigraphiques, Structures, Mobilier, etc.).

Un **site archéologique** dans PyArchInit représente une zone géographique définie où se déroulent les activités de recherche archéologique.

---

## Accès à la Fiche

Pour accéder à la Fiche Site :

1. Menu **PyArchInit** → **Archaeological record management** → **Site**
2. Ou depuis la barre d'outils PyArchInit, cliquer sur l'icône **Site**

---

## Interface Utilisateur

La Fiche Site est divisée en plusieurs zones fonctionnelles :

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | **DBMS Toolbar** | Barre d'outils pour navigation et gestion des enregistrements |
| 2 | **Données Descriptives** | Champs pour les informations du site |
| 3 | **Générateur US** | Outil pour créer des fiches US en lot |
| 4 | **GIS Viewer** | Contrôles pour visualisation cartographique |
| 5 | **MoveCost** | Outils d'analyse spatiale avancée |
| 6 | **Aide** | Documentation et tutoriels vidéo |

---

## Données Descriptives du Site

### Champs Obligatoires

| Champ | Description | Note |
|-------|-------------|------|
| **Site** | Nom identifiant du site | Obligatoire, doit être unique |

### Champs Géographiques

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Nation** | Pays où se trouve le site | France |
| **Région** | Région administrative | Occitanie |
| **Province** | Département | Hérault |
| **Commune** | Commune | Montpellier |

### Champs Descriptifs

| Champ | Description |
|-------|-------------|
| **Nom** | Nom étendu/descriptif du site |
| **Définition** | Typologie du site (depuis thésaurus) |
| **Description** | Champ texte libre pour description détaillée |
| **Dossier** | Chemin vers le dossier local du projet |

### Définition Site (Thésaurus)

Le champ **Définition** utilise un vocabulaire contrôlé :

| Définition | Description |
|------------|-------------|
| Zone de fouille | Zone soumise à investigation stratigraphique |
| Zone de prospection | Zone de reconnaissance de surface |
| Site archéologique | Localité avec témoins archéologiques |
| Monument | Structure monumentale |
| Nécropole | Zone sépulcrale |
| Habitat | Zone d'habitation |
| Sanctuaire | Zone cultuelle |

---

## Toolbar DBMS

La toolbar DBMS fournit tous les contrôles pour la gestion des enregistrements.

### Indicateurs d'État

| Indicateur | Description |
|------------|-------------|
| **DB Info** | Type de base de données connectée |
| **Status** | État actuel : `Usa` (parcourir), `Trova` (recherche), `Nuovo Record` |
| **Tri** | Indique si les enregistrements sont triés |
| **record n.** | Numéro de l'enregistrement actuel |
| **record tot.** | Total des enregistrements |

### Navigation des Enregistrements

| Bouton | Fonction |
|--------|----------|
| **First rec** | Aller au premier enregistrement |
| **Prev rec** | Aller à l'enregistrement précédent |
| **Next rec** | Aller à l'enregistrement suivant |
| **Last rec** | Aller au dernier enregistrement |

### Gestion des Enregistrements

| Bouton | Fonction | Description |
|--------|----------|-------------|
| **New record** | Créer nouveau | Prépare le formulaire pour un nouveau site |
| **Save** | Sauvegarder | Enregistre les modifications |
| **Delete record** | Supprimer | Supprime l'enregistrement actuel |
| **View all records** | Afficher tout | Montre tous les enregistrements |

### Recherche et Tri

| Bouton | Fonction |
|--------|----------|
| **new search** | Nouvelle recherche - active le mode recherche |
| **search !!!** | Exécuter la recherche |
| **Order by** | Trier - ouvre le panneau de tri |

---

## Fonctionnalités GIS

### Chargement des Couches

| Bouton | Fonction |
|--------|----------|
| **GIS viewer** | Charge toutes les couches pour insérer des géométries |
| **Charger couche site** | Charge uniquement les couches du site actuel |
| **Charger tous les sites** | Charge les couches de tous les sites |

### Géocodage - Recherche d'Adresse

1. Entrer l'adresse dans le champ texte
2. Cliquer **Zoom on**
3. La carte se centre sur la position trouvée

### WMS Contraintes Archéologiques

Le bouton WMS charge la couche des contraintes archéologiques (zonages de protection).

### Fonds de Carte

Le bouton Base Maps permet de charger des fonds de carte (Google Maps, OpenStreetMap, etc.).

---

## Génération de Fiches US

Cette fonctionnalité permet de créer automatiquement un nombre défini de fiches US pour le site actuel.

### Paramètres

| Champ | Description | Exemple |
|-------|-------------|---------|
| **Numéro Zone** | Numéro de la zone de fouille | 1 |
| **Numéro US de départ** | Numéro initial US | 1 |
| **Nombre de fiches à créer** | Quantité d'US à générer | 100 |
| **Type** | US ou USM | US |

### Procédure

1. S'assurer d'être sur le bon site
2. Entrer le numéro de zone
3. Entrer le numéro US de départ
4. Entrer le nombre de fiches à créer
5. Sélectionner le type (US ou USM)
6. Cliquer **Générer US**

---

## MoveCost - Analyse de Parcours

La section **MovecostToPyarchinit** intègre des fonctions R pour l'analyse des chemins de moindre coût (Least Cost Path Analysis).

### Prérequis

- **R** installé sur le système
- Package R **movecost** installé
- Plugin **Processing R Provider** actif dans QGIS

### Fonctions Disponibles

| Fonction | Description |
|----------|-------------|
| **movecost** | Calcule le coût de déplacement et chemins optimaux |
| **movebound** | Calcule les limites de coût de marche |
| **movcorr** | Calcule les corridors de moindre coût |
| **movalloc** | Allocation territoriale basée sur les coûts |

---

## Exportation Rapport

### Exporter Rapport de Fouille

Le bouton **Exporter** génère un PDF avec le rapport de fouille pour le site actuel.

Le rapport inclut :
- Données d'identification du site
- Liste des US
- Séquence stratigraphique
- Matrice de Harris (si disponible)

---

## Workflow Opérationnel

### Créer un Nouveau Site

1. **Ouvrir la Fiche Site**
2. **Cliquer "New record"** - le statut change en "Nouveau Record"
3. **Remplir les Données Obligatoires** - au minimum le nom du site
4. **Remplir les Données Géographiques** - nation, région, département, commune
5. **Sélectionner la Définition** - choisir la typologie depuis le thésaurus
6. **Ajouter la Description** - informations détaillées
7. **Sauvegarder** - cliquer sur Save
8. **Vérifier** - le site est créé, le statut revient à "Usa"

### Modifier un Site Existant

1. Naviguer vers le site à modifier
2. Modifier les champs souhaités
3. Cliquer **Save**
4. Confirmer la sauvegarde

### Supprimer un Site

**Attention** : La suppression d'un site NE supprime PAS automatiquement les US, structures et mobilier associés.

1. Naviguer vers le site à supprimer
2. Cliquer **Delete record**
3. Confirmer la suppression

---

## Gestion de la Concurrence (PostgreSQL)

Avec PostgreSQL en environnement multi-utilisateurs, le système gère automatiquement les conflits de modification :

- **Indicateur de verrouillage** : Montre si l'enregistrement est en cours de modification par un autre utilisateur
- **Contrôle de version** : Détecte les modifications concurrentes
- **Résolution de conflits** : Permet de choisir quelle version conserver

---

## Résolution des Problèmes

### Le site n'est pas sauvegardé
- Vérifier que le champ "Site" est rempli
- Vérifier que le nom n'existe pas déjà

### Les couches GIS ne se chargent pas
- Vérifier la connexion à la base de données
- Vérifier qu'il existe des géométries associées

### Erreur de géocodage
- Vérifier la connexion internet
- Contrôler que l'adresse est correctement écrite

---

## Notes Techniques

- **Table base de données** : `site_table`
- **Champs** : sito, nazione, regione, comune, descrizione, provincia, definizione_sito, sito_path
- **Couches GIS associées** : PYSITO_POLYGON, PYSITO_POINT
- **Thésaurus** : tipologia_sigla = '1.1'

---

## Vidéo Tutorial

### Création d'un Site
`[Placeholder : video_fiche_site.mp4]`

**Contenus** :
- Création d'un nouveau site
- Configuration des données
- Génération des US
- Fonctionnalités GIS

**Durée prévue** : 12-15 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
