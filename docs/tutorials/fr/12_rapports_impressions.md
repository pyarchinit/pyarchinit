# Tutorial 12 : Rapports et Impressions PDF

## Introduction

PyArchInit offre un système complet de génération de **rapports PDF** pour toutes les fiches archéologiques. Cette fonctionnalité permet d'exporter la documentation en format imprimable, conforme aux standards ministériels et prête pour l'archivage.

### Types de Rapports Disponibles

| Type | Description | Fiche Origine |
|------|-------------|---------------|
| Fiches US | Rapports complets US/USM | Fiche US |
| Index US | Liste synthétique US | Fiche US |
| Fiches Périodisation | Rapports périodes/phases | Fiche Périodisation |
| Fiches Structure | Rapports structures | Fiche Structure |
| Fiches Mobilier | Rapports inventaire matériaux | Fiche Inventaire |
| Fiches Tombe | Rapports sépultures | Fiche Tombe |
| Fiches Échantillons | Rapports prélèvements | Fiche Échantillons |
| Fiches Individus | Rapports anthropologiques | Fiche Individus |

## Accès à la Fonction

### Depuis le Menu Principal
1. **PyArchInit** dans la barre de menu
2. Sélectionner **Export PDF**

### Depuis la Toolbar
Cliquer sur l'icône **PDF** dans la toolbar de PyArchInit

## Interface d'Exportation

### Aperçu de la Fenêtre

La fenêtre d'exportation PDF présente :

```
+------------------------------------------+
|        PyArchInit - Export PDF            |
+------------------------------------------+
| Site : [ComboBox sélection site]    [v]   |
+------------------------------------------+
| Fiches à exporter :                       |
| [x] Fiches US                             |
| [x] Fiches Périodisation                  |
| [x] Fiches Structure                      |
| [x] Fiches Mobilier                       |
| [x] Fiches Tombe                          |
| [x] Fiches Échantillons                   |
| [x] Fiches Individus                      |
+------------------------------------------+
| [Ouvrir Dossier]  [Exporter PDF]  [Annuler] |
+------------------------------------------+
```

### Sélection du Site

| Champ | Description |
|-------|-------------|
| ComboBox Site | Liste de tous les sites dans la base de données |

**Note** : L'exportation se fait par site individuel. Pour exporter plusieurs sites, répéter l'opération.

### Cases à Cocher Fiches

Chaque case à cocher active l'exportation d'un type spécifique :

| Case à cocher | Génère |
|---------------|--------|
| Fiches US | Fiches complètes + Index US |
| Fiches Périodisation | Fiches périodes + Index |
| Fiches Structure | Fiches structures + Index |
| Fiches Mobilier | Fiches matériaux + Index |
| Fiches Tombe | Fiches sépultures + Index |
| Fiches Échantillons | Fiches prélèvements + Index |
| Fiches Individus | Fiches anthropologiques + Index |

## Processus d'Exportation

### Étape 1 : Sélection des Données

```python
# Le système exécute pour chaque type sélectionné :
1. Requête base de données pour le site sélectionné
2. Tri des données (par numéro, zone, etc.)
3. Préparation de la liste pour génération
```

### Étape 2 : Génération PDF

Pour chaque type de fiche :
1. **Fiche individuelle** : PDF détaillé pour chaque enregistrement
2. **Index** : PDF récapitulatif avec tous les enregistrements

### Étape 3 : Sauvegarde

Sortie dans le dossier :
```
~/pyarchinit/pyarchinit_PDF_folder/
```

## Contenu des Rapports

### Fiche US

Informations incluses :
- **Données identificatives** : Site, Zone, Numéro US, Type unité
- **Définitions** : Stratigraphique, Interprétative
- **Description** : Texte descriptif complet
- **Interprétation** : Analyse interprétative
- **Périodisation** : Période/Phase initiale et finale
- **Caractéristiques physiques** : Couleur, consistance, formation
- **Mesures** : Cotes min/max, dimensions
- **Rapports** : Liste des relations stratigraphiques
- **Documentation** : Références graphiques et photographiques
- **Données USM** : (si applicable) Technique murale, matériaux

### Index US

Tableau récapitulatif avec colonnes :
| Site | Zone | US | Déf. Stratigraphique | Déf. Interprétative | Période |

### Fiche Périodisation

- Site
- Numéro Période
- Numéro Phase
- Chronologie initiale/finale
- Datation étendue
- Description période

### Fiche Structure

- Données identificatives (Site, Sigle, Numéro)
- Catégorie, Typologie, Définition
- Description et Interprétation
- Périodisation
- Matériaux utilisés
- Éléments structurels
- Rapports structure
- Mesures et cotes

### Fiche Mobilier

- Site, Numéro inventaire
- Type objet, Définition
- Description
- Provenance (Zone, US)
- État de conservation
- Datation
- Éléments et mesures
- Bibliographie

### Fiche Tombe

- Données identificatives
- Rite (inhumation/crémation)
- Type sépulture et déposition
- Description et interprétation
- Mobilier (présence, type, description)
- Périodisation
- Cotes structure et individu
- US associées

### Fiche Échantillons

- Site, Numéro échantillon
- Type échantillon
- Description
- Provenance (Zone, US)
- Lieu de conservation
- Numéro caisse

### Fiche Individus

- Données identificatives
- Sexe, Âge (min/max), Classes d'âge
- Position squelette
- Orientation (axe, azimut)
- État de conservation
- Observations

## Langues Supportées

Le système génère les rapports selon la langue du système :

| Langue | Code | Template |
|--------|------|----------|
| Italien | IT | `build_*_sheets()` |
| Allemand | DE | `build_*_sheets_de()` |
| Anglais | EN | `build_*_sheets_en()` |

La langue est détectée automatiquement depuis les paramètres QGIS.

## Dossier de Sortie

### Chemin Standard
```
~/pyarchinit/pyarchinit_PDF_folder/
```

### Structure des Fichiers Générés

```
pyarchinit_PDF_folder/
├── US_[site]_fiches.pdf           # Fiches US complètes
├── US_[site]_index.pdf            # Index US
├── Periodisation_[site].pdf       # Fiches Périodisation
├── Structure_[site]_fiches.pdf    # Fiches Structure
├── Structure_[site]_index.pdf     # Index Structure
├── Mobilier_[site]_fiches.pdf     # Fiches Mobilier
├── Mobilier_[site]_index.pdf      # Index Mobilier
├── Tombe_[site]_fiches.pdf        # Fiches Tombe
├── Echantillons_[site]_fiches.pdf # Fiches Échantillons
├── Individus_[site]_fiches.pdf    # Fiches Individus
└── ...
```

### Ouverture du Dossier

Le bouton **"Ouvrir Dossier"** ouvre directement le répertoire de sortie dans le gestionnaire de fichiers du système.

## Personnalisation des Rapports

### Templates PDF

Les templates sont définis dans les modules :
- `modules/utility/pyarchinit_exp_USsheet_pdf.py`
- `modules/utility/pyarchinit_exp_Findssheet_pdf.py`
- `modules/utility/pyarchinit_exp_Periodizzazionesheet_pdf.py`
- `modules/utility/pyarchinit_exp_Individui_pdf.py`
- `modules/utility/pyarchinit_exp_Strutturasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`
- `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

### Bibliothèque Utilisée

Les PDF sont générés avec **ReportLab**, qui permet :
- Mises en page personnalisables
- Insertion d'images
- Tableaux formatés
- En-têtes/pieds de page

### Polices Requises

Le système utilise des polices spécifiques :
- **Cambria** (police principale)
- Installation automatique au premier démarrage du plugin

## Workflow Conseillé

### 1. Préparation des Données

```
1. Compléter toutes les fiches du site
2. Vérifier la complétude des données
3. Contrôler la périodisation
4. Vérifier les rapports stratigraphiques
```

### 2. Exportation

```
1. Ouvrir Export PDF
2. Sélectionner le site
3. Sélectionner les types de fiches
4. Cliquer "Exporter PDF"
5. Attendre la fin du processus
```

### 3. Vérification

```
1. Ouvrir le dossier de sortie
2. Contrôler les PDF générés
3. Vérifier le formatage
4. Imprimer ou archiver
```

## Résolution des Problèmes

### Erreur : "No form to print"

**Cause** : Aucun enregistrement trouvé pour le type sélectionné

**Solution** :
- Vérifier que des données existent pour le site sélectionné
- Contrôler la base de données

### PDF Vides ou Incomplets

**Causes possibles** :
1. Champs obligatoires non remplis
2. Problèmes d'encodage de caractères
3. Polices manquantes

**Solutions** :
- Compléter les champs obligatoires
- Vérifier l'installation de la police Cambria

### Erreur de Police

**Cause** : Police Cambria non installée

**Solution** :
- Le plugin tente l'installation automatique
- En cas de problème, installer manuellement

### Export Lent

**Cause** : Nombreux enregistrements à exporter

**Solution** :
- Exporter par typologie séparément
- Attendre la fin du processus

## Bonnes Pratiques

### 1. Organisation

- Exporter régulièrement pendant la fouille
- Créer des sauvegardes des PDF générés
- Organiser par campagne/année

### 2. Complétude des Données

- Remplir tous les champs avant l'export
- Vérifier les cotes depuis les mesures GIS
- Contrôler les rapports stratigraphiques

### 3. Archivage

- Sauvegarder les PDF sur un stockage sécurisé
- Inclure dans la documentation finale
- Joindre au rapport de fouille

### 4. Impression

- Utiliser du papier sans acide pour l'archivage
- Imprimer en format A4
- Relier par campagne

## Intégration avec d'Autres Fonctions

### Cotes depuis GIS

Le système récupère automatiquement :
- Cotes minimales et maximales depuis les géométries
- Références aux plans GIS

### Documentation Photographique

Les rapports peuvent inclure des références à :
- Photographies liées
- Dessins et relevés

### Périodisation

Les rapports US incluent automatiquement :
- Datation étendue depuis la période/phase assignée
- Références chronologiques

## Références

### Fichiers Source
- `tabs/Pdf_export.py` - Interface d'exportation
- `modules/utility/pyarchinit_exp_*_pdf.py` - Générateurs PDF

### Dépendances
- ReportLab (génération PDF)
- Police Cambria

---

## Vidéo Tutorial

### Export PDF Complet
`[Placeholder : video_export_pdf.mp4]`

**Contenus** :
- Sélection du site et des fiches
- Processus d'exportation
- Vérification de la sortie
- Organisation de l'archive

**Durée prévue** : 10-12 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
