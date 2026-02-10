# Tutorial 13 : Gestion du Thésaurus

## Introduction

Le **Thésaurus** de PyArchInit est le système centralisé pour la gestion des vocabulaires contrôlés. Il permet de définir et maintenir les listes de valeurs utilisées dans toutes les fiches du plugin, garantissant la cohérence terminologique et facilitant la recherche.

### Fonctions Principales

- Gestion des vocabulaires pour chaque fiche
- Support multilingue
- Sigles et descriptions étendues
- Intégration avec GPT pour suggestions
- Import/export depuis fichiers CSV

---

## Accès au Thésaurus

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Thésaurus** (ou **Thesaurus form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Thésaurus** (livre/dictionnaire)

---

## Aperçu de l'Interface

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | Sélection Table | Choix de la fiche à configurer |
| 3 | Champs Sigle | Code, extension, typologie |
| 4 | Description | Description détaillée du terme |
| 5 | Langue | Sélection de la langue |
| 6 | Outils | Import CSV, suggestions GPT |

---

## Champs du Thésaurus

### Nom Table

**Champ** : `comboBox_nome_tabella`
**Base de données** : `nome_tabella`

Sélectionne la fiche pour laquelle définir les valeurs.

**Tables disponibles :**
| Table | Description |
|-------|-------------|
| `us_table` | Fiche US/USM |
| `site_table` | Fiche Site |
| `periodizzazione_table` | Périodisation |
| `inventario_materiali_table` | Inventaire Matériaux |
| `pottery_table` | Fiche Pottery |
| `campioni_table` | Fiche Échantillons |
| `documentazione_table` | Documentation |
| `tomba_table` | Fiche Tombe |
| `individui_table` | Fiche Individus |
| `fauna_table` | Archéozoologie |
| `ut_table` | Fiche UT |

### Sigle

**Champ** : `comboBox_sigla`
**Base de données** : `sigla`

Code court/abréviation du terme.

**Exemples :**
- `MR` pour Mur
- `US` pour Unité Stratigraphique
- `CR` pour Céramique

### Sigle Étendu

**Champ** : `comboBox_sigla_estesa`
**Base de données** : `sigla_estesa`

Forme complète du terme.

**Exemples :**
- `Mur périmétrique`
- `Unité Stratigraphique`
- `Céramique commune`

### Description

**Champ** : `textEdit_descrizione_sigla`
**Base de données** : `descrizione`

Description détaillée du terme, définition, notes d'utilisation.

### Typologie Sigle

**Champ** : `comboBox_tipologia_sigla`
**Base de données** : `tipologia_sigla`

Code numérique qui identifie le champ de destination.

**Structure des codes :**
```
X.Y où :
X = numéro de table
Y = numéro de champ
```

**Exemples pour us_table :**
| Code | Champ |
|------|-------|
| 1.1 | Définition stratigraphique |
| 1.2 | Mode de formation |
| 1.3 | Type US |

### Langue

**Champ** : `comboBox_lingua`
**Base de données** : `lingua`

Langue du terme.

**Langues supportées :**
- IT (Italien)
- EN_US (Anglais)
- DE (Allemand)
- FR (Français)
- ES (Espagnol)
- AR (Arabe)
- CA (Catalan)

---

## Champs Hiérarchie

### ID Parent

**Champ** : `comboBox_id_parent`
**Base de données** : `id_parent`

ID du terme parent (pour structures hiérarchiques).

### Parent Sigle

**Champ** : `comboBox_parent_sigla`
**Base de données** : `parent_sigla`

Sigle du terme parent.

### Niveau Hiérarchie

**Champ** : `spinBox_hierarchy`
**Base de données** : `hierarchy_level`

Niveau dans la hiérarchie (0=racine, 1=premier niveau, etc.).

---

## Fonctionnalités Spéciales

### Suggestions GPT

Le bouton "Suggestions" utilise OpenAI GPT pour :
- Générer des descriptions automatiques
- Fournir des liens Wikipedia de référence
- Suggérer des définitions en contexte archéologique

**Utilisation :**
1. Sélectionner ou insérer un terme dans "Sigle étendu"
2. Cliquer sur "Suggestions"
3. Sélectionner le modèle GPT
4. Attendre la génération
5. Révision et sauvegarde

**Note :** Nécessite une clé API OpenAI configurée.

### Import CSV

Pour les bases de données SQLite, il est possible d'importer des vocabulaires depuis des fichiers CSV.

**Format CSV requis :**
```csv
nome_tabella,sigla,sigla_estesa,descrizione,tipologia_sigla,lingua
us_table,MR,Mur,Structure murale,1.3,FR
us_table,PV,Sol,Surface de circulation,1.3,FR
```

**Procédure :**
1. Cliquer sur "Import CSV"
2. Sélectionner le fichier
3. Confirmer l'importation
4. Vérifier les données importées

---

## Workflow Opérationnel

### Ajout d'un Nouveau Terme

1. **Ouverture Thésaurus**
   - Via menu ou toolbar

2. **Nouveau record**
   - Cliquer sur "New Record"

3. **Sélection table**
   ```
   Nom table : us_table
   ```

4. **Définition terme**
   ```
   Sigle : PZ
   Sigle étendu : Puits
   Typologie sigle : 1.3
   Langue : FR
   ```

5. **Description**
   ```
   Structure creusée dans le sol pour
   l'approvisionnement en eau.
   Généralement de forme circulaire
   avec revêtement en pierre ou briques.
   ```

6. **Sauvegarde**
   - Cliquer sur "Save"

### Recherche de Termes

1. Cliquer sur "New Search"
2. Remplir les critères :
   - Nom table
   - Sigle ou sigle étendu
   - Langue
3. Cliquer sur "Search"
4. Naviguer parmi les résultats

### Modification d'un Terme Existant

1. Rechercher le terme à modifier
2. Modifier les champs nécessaires
3. Cliquer sur "Save"

---

## Organisation des Codes Typologie

### Structure Conseillée

Pour chaque table, organiser les codes de manière systématique :

**us_table (1.x) :**
| Code | Champ |
|------|-------|
| 1.1 | Définition stratigraphique |
| 1.2 | Mode de formation |
| 1.3 | Type US |
| 1.4 | Consistance |
| 1.5 | Couleur |

**inventario_materiali_table (2.x) :**
| Code | Champ |
|------|-------|
| 2.1 | Type objet |
| 2.2 | Classe matériau |
| 2.3 | Définition |
| 2.4 | État de conservation |

**pottery_table (3.x) :**
| Code | Champ |
|------|-------|
| 3.1 | Forme |
| 3.2 | Ware |
| 3.3 | Fabric |
| 3.4 | Traitement de surface |

---

## Bonnes Pratiques

### Cohérence Terminologique

- Utiliser toujours les mêmes termes pour les mêmes concepts
- Éviter les synonymes non documentés
- Documenter les conventions adoptées

### Multilingue

- Créer les termes dans toutes les langues nécessaires
- Maintenir les correspondances entre langues
- Utiliser les traductions officielles quand disponibles

### Hiérarchie

- Utiliser la structure hiérarchique pour les termes corrélés
- Définir clairement les niveaux
- Documenter les relations

### Maintenance

- Réviser périodiquement les vocabulaires
- Éliminer les termes obsolètes
- Mettre à jour les descriptions

---

## Résolution des Problèmes

### Problème : Terme non visible dans les ComboBox

**Cause :** Code typologie erroné ou langue non correspondante.

**Solution :**
1. Vérifier le code tipologia_sigla
2. Contrôler la langue configurée
3. Vérifier que le record est sauvegardé

### Problème : Import CSV échoué

**Cause :** Format de fichier incorrect.

**Solution :**
1. Vérifier la structure du CSV
2. Contrôler les délimiteurs (virgule)
3. Vérifier l'encodage (UTF-8)

### Problème : Suggestions GPT ne fonctionnent pas

**Cause :** Clé API manquante ou non valide.

**Solution :**
1. Vérifier la configuration de la clé API
2. Contrôler la connexion internet
3. Vérifier le crédit OpenAI

---

## Références

### Base de données

- **Table** : `pyarchinit_thesaurus_sigle`
- **Classe mapper** : `PYARCHINIT_THESAURUS_SIGLE`
- **ID** : `id_thesaurus_sigle`

### Fichiers Source

- **UI** : `gui/ui/Thesaurus.ui`
- **Contrôleur** : `tabs/Thesaurus.py`

---

## Vidéo Tutorial

### Gestion des Vocabulaires
**Durée** : 10-12 minutes
- Structure du thésaurus
- Ajout de termes
- Organisation des codes

`[Placeholder vidéo : video_thesaurus_gestion.mp4]`

### Multilingue et Import
**Durée** : 8-10 minutes
- Configuration des langues
- Import depuis CSV
- Suggestions GPT

`[Placeholder vidéo : video_thesaurus_avance.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../pyarchinit_thesaurus_animation.html)
