# Tutorial 21 : Fiche UT - Unités Topographiques

## Introduction

La **Fiche UT** (Unités Topographiques) est le module de PyArchInit dédié à la documentation des prospections archéologiques de surface. Elle permet d'enregistrer les données relatives aux concentrations de matériaux, anomalies du terrain et sites identifiés lors des prospections.

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
2. Sélectionner **Fiche UT**

### Via Barre d'Outils
1. Repérer la barre d'outils PyArchInit
2. Cliquer sur l'icône **UT**

---

## Aperçu de l'Interface

La fiche est organisée en plusieurs onglets pour documenter tous les aspects de la prospection.

### Onglets Principaux

| # | Onglet | Description |
|---|--------|-------------|
| 1 | Identification | Projet, N° UT, Localisation |
| 2 | Description | Définition, description, interprétation |
| 3 | Données UT | Conditions, méthodologie, dates |
| 4 | Analyse | Potentiel et risque archéologique |

---

## Champs Identificatifs

### Projet

**Champ** : `comboBox_progetto`
**Base de données** : `progetto`

Nom du projet de prospection.

### Numéro UT

**Champ** : `comboBox_nr_ut`
**Base de données** : `nr_ut`

Numéro progressif de l'Unité Topographique.

### UT Littéral

**Champ** : `lineEdit_ut_letterale`
**Base de données** : `ut_letterale`

Suffixe alphabétique optionnel (ex. UT 15a, 15b).

---

## Champs Localisation

### Données Administratives

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Pays | `nazione` | État |
| Région | `regione` | Région administrative |
| Province | `provincia` | Province/Département |
| Commune | `comune` | Commune |
| Fraction | `frazione` | Fraction/localité |
| Localité | `localita` | Toponyme local |
| Adresse | `indirizzo` | Voie/route |
| N° | `nr_civico` | Numéro |

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

---

## Champs Descriptifs

### Définition UT ⭐ NOUVEAU

**Champ** : `comboBox_def_ut`
**Base de données** : `def_ut`
**Thésaurus** : Code 12.7

Classification typologique de l'UT. Les valeurs sont chargées depuis le thésaurus et automatiquement traduites dans la langue courante.

**Valeurs standard :**
| Code | Français | Italien |
|------|----------|---------|
| scatter | Dispersion de matériaux | Area di dispersione materiali |
| site | Site archéologique | Sito archeologico |
| anomaly | Anomalie du terrain | Anomalia del terreno |
| structure | Structure affleurante | Struttura affiorante |
| concentration | Concentration de mobilier | Concentrazione reperti |
| traces | Traces anthropiques | Tracce antropiche |
| findspot | Découverte isolée | Rinvenimento sporadico |
| negative | Résultat négatif | Esito negativo |

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

## Champs Thésaurus Survey ⭐ NOUVEAU

Les champs suivants utilisent le système de thésaurus pour garantir une terminologie standardisée traduite en 7 langues (IT, EN, DE, ES, FR, AR, CA).

### Type de Survey (12.1)

**Champ** : `comboBox_survey_type`
**Base de données** : `survey_type`

| Code | Français | Description |
|------|----------|-------------|
| intensive | Prospection intensive | Prospection pédestre systématique |
| extensive | Prospection extensive | Reconnaissance extensive |
| targeted | Prospection ciblée | Investigation de zones spécifiques |
| random | Échantillonnage aléatoire | Méthodologie d'échantillonnage aléatoire |

### Couverture Végétale (12.2)

**Champ** : `comboBox_vegetation_coverage`
**Base de données** : `vegetation_coverage`

| Code | Français | Description |
|------|----------|-------------|
| none | Pas de végétation | Sol nu |
| sparse | Végétation clairsemée | Couverture < 25% |
| moderate | Végétation modérée | Couverture 25-50% |
| dense | Végétation dense | Couverture 50-75% |
| very_dense | Végétation très dense | Couverture > 75% |

### Méthode GPS (12.3)

**Champ** : `comboBox_gps_method`
**Base de données** : `gps_method`

| Code | Français | Description |
|------|----------|-------------|
| handheld | GPS portable | Appareil GPS de poche |
| dgps | GPS différentiel | DGPS avec station de base |
| rtk | GPS RTK | Cinématique temps réel |
| total_station | Station totale | Levé à la station totale |

### Condition de Surface (12.4)

**Champ** : `comboBox_surface_condition`
**Base de données** : `surface_condition`

| Code | Français | Description |
|------|----------|-------------|
| ploughed | Labouré | Champ fraîchement labouré |
| stubble | Chaumes | Présence de chaumes |
| pasture | Pâturage | Prairie/pâturage |
| woodland | Boisé | Zone boisée |
| urban | Urbain | Zone urbaine/bâtie |

### Accessibilité (12.5)

**Champ** : `comboBox_accessibility`
**Base de données** : `accessibility`

| Code | Français | Description |
|------|----------|-------------|
| easy | Accès facile | Aucune restriction |
| moderate_access | Accès modéré | Quelques difficultés |
| difficult | Accès difficile | Problèmes significatifs |
| restricted | Accès restreint | Sur autorisation uniquement |

### Conditions Météorologiques (12.6)

**Champ** : `comboBox_weather_conditions`
**Base de données** : `weather_conditions`

| Code | Français | Description |
|------|----------|-------------|
| sunny | Ensoleillé | Clair et ensoleillé |
| cloudy | Nuageux | Conditions nuageuses |
| rainy | Pluvieux | Pluie pendant prospection |
| windy | Venteux | Vents forts |

---

## Données Environnementales

### Pourcentage de Visibilité

**Champ** : `spinBox_visibility_percent`
**Base de données** : `visibility_percent`

Pourcentage de visibilité du sol (0-100%). Valeur numérique.

### Pente du Terrain

**Champ** : `lineEdit_andamento_terreno_pendenza`
**Base de données** : `andamento_terreno_pendenza`

Morphologie et pente du terrain.

### Utilisation du Sol

**Champ** : `lineEdit_utilizzo_suolo_vegetazione`
**Base de données** : `utilizzo_suolo_vegetazione`

Usage du sol au moment de la prospection.

---

## Données Matériaux

### Dimensions UT

**Champ** : `lineEdit_dimensioni_ut`
**Base de données** : `dimensioni_ut`

Étendue de la zone en m².

### Objets par m²

**Champ** : `lineEdit_rep_per_mq`
**Base de données** : `rep_per_mq`

Densité des matériaux par mètre carré.

### Objets Datants

**Champ** : `lineEdit_rep_datanti`
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

## Onglet Analyse ⭐ NOUVEAU

L'onglet **Analyse** fournit des outils avancés pour le calcul automatique du potentiel et du risque archéologique.

### Potentiel Archéologique

Le système calcule un score de 0 à 100 basé sur :

| Facteur | Poids | Description |
|---------|-------|-------------|
| Définition UT | 30% | Type d'évidence archéologique |
| Période historique | 25% | Chronologie du mobilier |
| Densité de mobilier | 20% | Matériaux par m² |
| Condition de surface | 15% | Visibilité et accessibilité |
| Documentation | 10% | Qualité de la documentation |

**Affichage :**
- Barre de progression colorée (vert = élevé, jaune = moyen, rouge = faible)
- Tableau détaillé des facteurs avec scores individuels
- Texte narratif automatique avec interprétation

### Risque Archéologique

Évalue le risque d'impact/perte du patrimoine :

| Facteur | Poids | Description |
|---------|-------|-------------|
| Accessibilité | 25% | Facilité d'accès à la zone |
| Usage du sol | 25% | Activités agricoles/constructives |
| Classements existants | 20% | Protections juridiques |
| Enquêtes antérieures | 15% | État des connaissances |
| Visibilité | 15% | Exposition du site |

### Génération de Carte de Chaleur

Le bouton **Générer Carte de Chaleur** crée des couches raster affichant :
- **Carte de Potentiel** : distribution spatiale du potentiel archéologique
- **Carte de Risque** : carte du risque d'impact

**Méthodes disponibles :**
- Estimation de Densité de Noyau (KDE)
- Pondération par Distance Inverse (IDW)
- Voisin Naturel

---

## Export PDF ⭐ AMÉLIORÉ

### Fiche UT Standard

Exporte la fiche UT complète avec tous les champs remplis.

### Rapport d'Analyse UT

Génère un rapport PDF incluant :

1. **Données d'identification UT**
2. **Section Potentiel Archéologique**
   - Score avec indicateur graphique
   - Texte narratif descriptif
   - Tableau des facteurs avec contributions
   - Image de la carte de potentiel (si générée)
3. **Section Risque Archéologique**
   - Score avec indicateur graphique
   - Texte narratif avec recommandations
   - Tableau des facteurs avec contributions
   - Image de la carte de risque (si générée)
4. **Section Méthodologie**
   - Description des algorithmes utilisés
   - Notes sur les pondérations des facteurs

Le rapport est disponible dans les 7 langues supportées.

---

## Workflow Opérationnel

### Enregistrement d'une Nouvelle UT

1. **Ouverture fiche**
   - Via menu ou barre d'outils

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

5. **Description** (utilisant thésaurus)
   ```
   Définition : Concentration de mobilier (du thésaurus)
   Description : Zone elliptique d'environ 50x30 m
   avec concentration de fragments céramiques
   et briques sur versant collinaire exposé
   au sud...
   ```

6. **Données survey** (utilisant thésaurus)
   ```
   Type Survey : Prospection intensive
   Couverture Végétale : Clairsemée
   Méthode GPS : GPS différentiel
   Condition Surface : Labouré
   Accessibilité : Accès facile
   Conditions Météo : Ensoleillé
   Visibilité : 80%
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

8. **Analyse** (onglet Analyse)
   - Vérifier score Potentiel
   - Vérifier score Risque
   - Générer Carte de Chaleur si nécessaire

9. **Sauvegarde**
   - Cliquer sur "Save"

---

## Intégration SIG

La fiche UT est étroitement intégrée avec QGIS :

- **Couche UT** : visualisation des géométries
- **Attributs liés** : données de la fiche
- **Sélection depuis la carte** : clic sur la géométrie ouvre la fiche
- **Carte de chaleur comme couche** : les cartes générées sont enregistrées comme couches raster

---

## Bonnes Pratiques

### Utilisation du Thésaurus

- Toujours préférer les valeurs du thésaurus pour la cohérence
- Les valeurs sont automatiquement traduites dans la langue de l'utilisateur
- Pour les nouvelles valeurs, les ajouter d'abord au thésaurus

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

### Analyse

- Toujours vérifier les scores calculés
- Générer des cartes de chaleur pour les projets complets
- Exporter les rapports pour documentation

---

## Codes Thésaurus UT

| Code | Champ | Description |
|------|-------|-------------|
| 12.1 | survey_type | Type de survey |
| 12.2 | vegetation_coverage | Couverture végétale |
| 12.3 | gps_method | Méthode GPS |
| 12.4 | surface_condition | Condition de surface |
| 12.5 | accessibility | Accessibilité |
| 12.6 | weather_conditions | Conditions météorologiques |
| 12.7 | def_ut | Définition UT |

---

## Résolution des Problèmes

### Problème : Comboboxes vides

**Cause** : Entrées du thésaurus non présentes dans la base de données.

**Solution** :
1. Mettre à jour la base de données via "Update database"
2. Vérifier que la table `pyarchinit_thesaurus_sigle` contient des entrées pour `ut_table`
3. Vérifier le code de langue dans les paramètres

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

### Problème : Carte de chaleur non générée

**Cause** : Données insuffisantes ou erreur de calcul.

**Solution** :
1. Vérifier qu'il existe au moins 3 UTs avec données complètes
2. Vérifier que les géométries sont valides
3. Vérifier l'espace disque disponible

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
- **PDF Analyse** : `modules/utility/pyarchinit_exp_UT_analysis_pdf.py`
- **Calculateur Potentiel** : `modules/analysis/ut_potential.py`
- **Calculateur Risque** : `modules/analysis/ut_risk.py`
- **Générateur Carte Chaleur** : `modules/analysis/ut_heatmap_generator.py`

---

## Vidéo Tutorial

### Documentation des Prospections
**Durée** : 15-18 minutes
- Enregistrement UT
- Données survey avec thésaurus
- Géolocalisation

[Placeholder vidéo : video_ut_survey.mp4]

### Analyse de Potentiel et Risque
**Durée** : 10-12 minutes
- Calcul automatique des scores
- Interprétation des résultats
- Génération de carte de chaleur

[Placeholder vidéo : video_ut_analysis.mp4]

### Export de Rapports PDF
**Durée** : 8-10 minutes
- Fiche UT standard
- Rapport d'analyse avec cartes
- Personnalisation de la sortie

[Placeholder vidéo : video_ut_pdf.mp4]

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit v4.9.68 - Système de Gestion des Données Archéologiques*
