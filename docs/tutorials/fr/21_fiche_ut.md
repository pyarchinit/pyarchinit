# Tutorial 21 : Fiche UT - Unités Topographiques

## Introduction

La **Fiche UT** (Unités Topographiques) est le module de PyArchInit dédié à la documentation des prospections archéologiques de surface (survey). Elle permet d'enregistrer les données relatives aux concentrations de matériaux, anomalies du terrain et sites identifiés lors des prospections.

### Concepts de Base

**Unité Topographique (UT) :**
- Zone délimitée avec des caractéristiques archéologiques homogènes
- Identifiée lors d'une prospection de surface
- Définie par une concentration de matériaux ou des anomalies visibles

**Prospection (Survey) :**
- Exploration systématique du territoire
- Collecte de données sur la présence anthropique ancienne
- Documentation sans fouille

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche UT** (ou **TU form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **UT**

---

## Aperçu de l'Interface

La fiche est riche en champs pour documenter tous les aspects de la prospection.

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | Champs Identificatifs | Projet, N° UT |
| 3 | Localisation | Données géographiques et administratives |
| 4 | Description | Définition, description, interprétation |
| 5 | Données Survey | Conditions, méthodologie |
| 6 | Chronologie | Périodes et datations |

---

## Champs Identificatifs

### Projet

**Champ** : `lineEdit_progetto`
**Base de données** : `progetto`

Nom du projet de prospection.

### Numéro UT

**Champ** : `lineEdit_nr_ut`
**Base de données** : `nr_ut`

Numéro progressif de l'Unité Topographique.

### UT Littéral

**Champ** : `lineEdit_ut_letterale`
**Base de données** : `ut_letterale`

Éventuel suffixe alphabétique (ex. UT 15a, 15b).

---

## Champs Localisation

### Données Administratives

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Pays | `nazione` | État |
| Région | `regione` | Région administrative |
| Province | `provincia` | Province |
| Commune | `comune` | Commune |
| Fraction | `frazione` | Fraction/localité |
| Localité | `localita` | Toponyme local |
| Adresse | `indirizzo` | Voie/route |
| N° civique | `nr_civico` | Numéro civique |

### Données Cartographiques

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Carte IGN | `carta_topo_igm` | Feuille IGN |
| Carte cadastrale | `carta_ctr` | Élément cadastral |
| Folio cadastral | `foglio_catastale` | Référence cadastre |

### Coordonnées

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Coord. géographiques | `coord_geografiche` | Lat/Long |
| Coord. planes | `coord_piane` | UTM/Lambert |
| Altitude | `quota` | Altitude NGF |
| Précision coord. | `coordinate_precision` | Précision GPS |
| Méthode GPS | `gps_method` | Type de relevé |

---

## Champs Descriptifs

### Définition UT

**Champ** : `comboBox_def_ut`
**Base de données** : `def_ut`

Classification typologique de l'UT.

**Valeurs :**
- Concentration de matériaux
- Zone de fragments
- Anomalie du terrain
- Structure affleurante
- Site archéologique

### Description UT

**Champ** : `textEdit_descrizione`
**Base de données** : `descrizione_ut`

Description détaillée de l'Unité Topographique.

**Contenus :**
- Étendue et forme de la zone
- Densité des matériaux
- Caractéristiques du terrain
- Visibilité et conditions

### Interprétation UT

**Champ** : `textEdit_interpretazione`
**Base de données** : `interpretazione_ut`

Interprétation fonctionnelle/historique.

---

## Données Environnementales

### Relief du Terrain

**Champ** : `comboBox_terreno`
**Base de données** : `andamento_terreno_pendenza`

Morphologie et pente.

**Valeurs :**
- Plat
- Légère pente
- Pente moyenne
- Forte pente
- En terrasses

### Utilisation du Sol

**Champ** : `comboBox_suolo`
**Base de données** : `utilizzo_suolo_vegetazione`

Usage du sol au moment de la prospection.

**Valeurs :**
- Labour
- Prairie/pâturage
- Vignoble
- Oliveraie
- Friche
- Forêt
- Urbain

### Description du Sol

**Champ** : `textEdit_suolo`
**Base de données** : `descrizione_empirica_suolo`

Caractéristiques pédologiques observées.

### Description du Lieu

**Champ** : `textEdit_luogo`
**Base de données** : `descrizione_luogo`

Contexte paysager.

---

## Données Survey

### Méthode de Prospection

**Champ** : `comboBox_metodo`
**Base de données** : `metodo_rilievo_e_ricognizione`

Méthodologie adoptée.

**Valeurs :**
- Prospection systématique
- Prospection extensive
- Prospection ciblée
- Vérification de signalement

### Type de Survey

**Champ** : `comboBox_survey_type`
**Base de données** : `survey_type`

Typologie de prospection.

### Visibilité

**Champ** : `spinBox_visibility`
**Base de données** : `visibility_percent`

Pourcentage de visibilité du sol (0-100%).

### Couverture Végétale

**Champ** : `comboBox_vegetation`
**Base de données** : `vegetation_coverage`

Degré de couverture végétale.

### Condition de Surface

**Champ** : `comboBox_surface`
**Base de données** : `surface_condition`

État de la surface.

**Valeurs :**
- Labouré fraîchement
- Labouré non hersé
- Herbe basse
- Herbe haute
- Chaumes

### Accessibilité

**Champ** : `comboBox_accessibility`
**Base de données** : `accessibility`

Facilité d'accès à la zone.

### Date

**Champ** : `dateEdit_data`
**Base de données** : `data`

Date de la prospection.

### Heure/Météo

**Champ** : `lineEdit_meteo`
**Base de données** : `ora_meteo`

Conditions météo et heure.

### Responsable

**Champ** : `comboBox_responsabile`
**Base de données** : `responsabile`

Responsable de la prospection.

### Équipe

**Champ** : `textEdit_team`
**Base de données** : `team_members`

Membres du groupe.

---

## Données Matériaux

### Dimensions UT

**Champ** : `lineEdit_dimensioni`
**Base de données** : `dimensioni_ut`

Étendue en m².

### Objets par m²

**Champ** : `lineEdit_rep_mq`
**Base de données** : `rep_per_mq`

Densité des matériaux.

### Objets Datants

**Champ** : `textEdit_rep_datanti`
**Base de données** : `rep_datanti`

Description des matériaux diagnostiques.

---

## Chronologie

### Période I

| Champ | Base de données |
|-------|-----------------|
| Période I | `periodo_I` |
| Datation I | `datazione_I` |
| Interprétation I | `interpretazione_I` |

### Période II

| Champ | Base de données |
|-------|-----------------|
| Période II | `periodo_II` |
| Datation II | `datazione_II` |
| Interprétation II | `interpretazione_II` |

---

## Autres Champs

### Géométrie

**Champ** : `comboBox_geometria`
**Base de données** : `geometria`

Forme de l'UT.

### Bibliographie

**Champ** : `textEdit_bibliografia`
**Base de données** : `bibliografia`

Références bibliographiques.

### Documentation

**Champ** : `textEdit_documentazione`
**Base de données** : `documentazione`

Documentation produite (photos, dessins).

### Documentation Photo

**Champ** : `textEdit_photo_doc`
**Base de données** : `photo_documentation`

Liste de la documentation photographique.

### Organismes de Protection/Classements

**Champ** : `textEdit_vincoli`
**Base de données** : `enti_tutela_vincoli`

Classements et organismes de tutelle.

### Enquêtes Préliminaires

**Champ** : `textEdit_indagini`
**Base de données** : `indagini_preliminari`

Éventuelles enquêtes déjà réalisées.

---

## Workflow Opérationnel

### Enregistrement d'une Nouvelle UT

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouvel enregistrement**
   - Cliquer sur "New Record"

3. **Données identificatives**
   ```
   Projet : Survey Vallée du Rhône 2024
   N° UT : 25
   ```

4. **Localisation**
   ```
   Région : Provence-Alpes-Côte d'Azur
   Département : Vaucluse
   Commune : Orange
   Localité : Colline Haute
   Coord. : 44.1234 N, 4.5678 E
   Altitude : 125 m
   ```

5. **Description**
   ```
   Définition : Concentration de matériaux
   Description : Zone elliptique d'environ 50x30 m
   avec concentration de fragments céramiques
   et briques sur versant collinaire exposé
   au sud...
   ```

6. **Données survey**
   ```
   Méthode : Prospection systématique
   Visibilité : 80%
   Condition : Labouré fraîchement
   Date : 15/04/2024
   Responsable : Équipe A
   ```

7. **Matériaux et chronologie**
   ```
   Dimensions : 1500 m²
   Obj./m² : 5-8
   Objets datants : Céramique commune,
   sigillée italique, briques

   Période I : Romain
   Datation I : Ier-IIe s. ap. J.-C.
   Interprétation I : Villa rustica
   ```

8. **Sauvegarde**
   - Cliquer sur "Save"

---

## Intégration SIG

La fiche UT est étroitement intégrée avec QGIS :

- **Couche UT** : visualisation des géométries
- **Attributs liés** : données de la fiche
- **Sélection depuis la carte** : clic sur la géométrie ouvre la fiche

---

## Export PDF

La fiche prend en charge l'export en PDF pour :
- Fiches UT individuelles
- Listes par projet
- Rapports de survey

---

## Bonnes Pratiques

### Nomenclature

- Numérotation progressive par projet
- Utiliser des suffixes pour les subdivisions
- Documenter les conventions

### Géolocalisation

- Utiliser le GPS différentiel quand possible
- Indiquer toujours la méthode et la précision
- Vérifier les coordonnées sur carte

### Documentation

- Photographier chaque UT
- Produire des croquis planimétriques
- Enregistrer les conditions de visibilité

### Matériaux

- Collecter des échantillons diagnostiques
- Estimer la densité par zone
- Documenter la distribution spatiale

---

## Résolution des Problèmes

### Problème : Coordonnées non valides

**Cause** : Format incorrect ou système de référence erroné.

**Solution** :
1. Vérifier le format (DD ou DMS)
2. Contrôler le système de référence
3. Utiliser l'outil de conversion QGIS

### Problème : UT non visible sur la carte

**Cause** : Géométrie non associée.

**Solution** :
1. Vérifier que la couche UT existe
2. Contrôler que l'enregistrement a une géométrie
3. Vérifier la projection de la couche

---

## Références

### Base de données

- **Table** : `ut_table`
- **Classe mapper** : `UT`
- **ID** : `id_ut`

### Fichiers Source

- **UI** : `gui/ui/UT_ui.ui`
- **Contrôleur** : `tabs/UT.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_UTsheet_pdf.py`

---

## Vidéo Tutorial

### Documentation des Prospections
**Durée** : 15-18 minutes
- Enregistrement UT
- Données survey
- Géolocalisation

`[Placeholder vidéo : video_ut_survey.mp4]`

### Intégration SIG Survey
**Durée** : 10-12 minutes
- Couches et attributs
- Visualisation des résultats
- Analyse spatiale

`[Placeholder vidéo : video_ut_sig.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
