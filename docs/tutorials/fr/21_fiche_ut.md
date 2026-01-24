# Tutorial 21 : Fiche UT - Unites Topographiques

## Introduction

La **Fiche UT** (Unites Topographiques) est le module de PyArchInit dedie a la documentation des prospections archeologiques de surface (survey). Elle permet d'enregistrer les donnees relatives aux concentrations de materiaux, anomalies du terrain et sites identifies lors des prospections.

### Concepts de Base

**Unite Topographique (UT) :**
- Zone delimitee avec des caracteristiques archeologiques homogenes
- Identifiee lors d'une prospection de surface
- Definie par une concentration de materiaux ou des anomalies visibles

**Prospection (Survey) :**
- Exploration systematique du territoire
- Collecte de donnees sur la presence anthropique ancienne
- Documentation sans fouille

---

## Acces a la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Selectionner **Fiche UT** (ou **TU form**)

### Via Barre d'Outils
1. Reperer la barre d'outils PyArchInit
2. Cliquer sur l'icone **UT**

---

## Apercu de l'Interface

La fiche est organisee en plusieurs onglets pour documenter tous les aspects de la prospection.

### Onglets Principaux

| # | Onglet | Description |
|---|--------|-------------|
| 1 | Identification | Projet, N. UT, Localisation |
| 2 | Description | Definition, description, interpretation |
| 3 | Donnees UT | Conditions, methodologie, dates |
| 4 | Analyse | Potentiel et risque archeologique |

### Barre d'Outils Principale

| Bouton | Fonction |
|--------|----------|
| Premier | Aller au premier enregistrement |
| Precedent | Enregistrement precedent |
| Suivant | Enregistrement suivant |
| Dernier | Aller au dernier enregistrement |
| Recherche | Recherche avancee |
| Sauvegarder | Enregistrer l'enregistrement |
| Supprimer | Supprimer l'enregistrement |
| PDF | Exporter fiche PDF |
| **PDF Liste** | Exporter liste des UT en PDF |
| **Export GNA** | Exporter au format GNA |
| Afficher Couche | Visualiser couche sur la carte |

---

## Champs Identificatifs

### Projet

**Champ** : `comboBox_progetto`
**Base de donnees** : `progetto`

Nom du projet de prospection.

### Numero UT

**Champ** : `comboBox_nr_ut`
**Base de donnees** : `nr_ut`

Numero progressif de l'Unite Topographique.

### UT Litteral

**Champ** : `lineEdit_ut_letterale`
**Base de donnees** : `ut_letterale`

Suffixe alphabetique optionnel (ex. UT 15a, 15b).

---

## Champs Localisation

### Donnees Administratives

| Champ | Base de donnees | Description |
|-------|-----------------|-------------|
| Pays | `nazione` | Etat |
| Region | `regione` | Region administrative |
| Province | `provincia` | Province/Departement |
| Commune | `comune` | Commune |
| Fraction | `frazione` | Fraction/localite |
| Localite | `localita` | Toponyme local |
| Adresse | `indirizzo` | Voie/route |
| N. civique | `nr_civico` | Numero civique |

### Donnees Cartographiques

| Champ | Base de donnees | Description |
|-------|-----------------|-------------|
| Carte IGN | `carta_topo_igm` | Feuille IGN |
| Carte CTR | `carta_ctr` | Element CTR |
| Folio cadastral | `foglio_catastale` | Reference cadastre |

### Coordonnees

| Champ | Base de donnees | Description |
|-------|-----------------|-------------|
| Coord. geographiques | `coord_geografiche` | Lat/Long (format : lat, lon) |
| Coord. planes | `coord_piane` | UTM/Lambert (format : x, y) |
| Altitude | `quota` | Altitude NGF |
| Precision coord. | `coordinate_precision` | Precision GPS en metres |

**IMPORTANT** : Les coordonnees sont utilisees pour la generation des cartes de chaleur. Au moins un des champs `coord_geografiche` ou `coord_piane` doit etre rempli pour chaque UT.

---

## Champs Descriptifs

### Definition UT

**Champ** : `comboBox_def_ut`
**Base de donnees** : `def_ut`
**Thesaurus** : Code 12.7

Classification typologique de l'UT. Les valeurs sont chargees depuis le thesaurus et automatiquement traduites dans la langue courante.

**Valeurs standard :**
| Code | Francais | Italien |
|------|----------|---------|
| scatter | Dispersion de materiaux | Area di dispersione materiali |
| site | Site archeologique | Sito archeologico |
| anomaly | Anomalie du terrain | Anomalia del terreno |
| structure | Structure affleurante | Struttura affiorante |
| concentration | Concentration de mobilier | Concentrazione reperti |
| traces | Traces anthropiques | Tracce antropiche |
| findspot | Decouverte isolee | Rinvenimento sporadico |
| negative | Resultat negatif | Esito negativo |

### Description UT

**Champ** : `textEdit_descrizione`
**Base de donnees** : `descrizione_ut`

Description detaillee de l'Unite Topographique.

**Contenus :**
- Etendue et forme de la zone
- Densite des materiaux
- Caracteristiques du terrain
- Visibilite et conditions

### Interpretation UT

**Champ** : `textEdit_interpretazione`
**Base de donnees** : `interpretazione_ut`

Interpretation fonctionnelle/historique.

---

## Champs Survey avec Thesaurus

Les champs suivants utilisent le systeme de thesaurus pour garantir une terminologie standardisee traduite en 7 langues (IT, EN, DE, ES, FR, AR, CA).

### Type de Survey (12.1)

**Champ** : `comboBox_survey_type`
**Base de donnees** : `survey_type`

| Code | Francais | Description |
|------|----------|-------------|
| intensive | Prospection intensive | Prospection systematique intensive |
| extensive | Prospection extensive | Prospection par echantillonnage |
| targeted | Prospection ciblee | Investigation de zones specifiques |
| random | Echantillonnage aleatoire | Methodologie aleatoire |

### Couverture Vegetale (12.2)

**Champ** : `comboBox_vegetation_coverage`
**Base de donnees** : `vegetation_coverage`

| Code | Francais | Description |
|------|----------|-------------|
| none | Absente | Sol nu |
| sparse | Clairsemee | Couverture < 25% |
| moderate | Moderee | Couverture 25-50% |
| dense | Dense | Couverture 50-75% |
| very_dense | Tres dense | Couverture > 75% |

### Methode GPS (12.3)

**Champ** : `comboBox_gps_method`
**Base de donnees** : `gps_method`

| Code | Francais | Description |
|------|----------|-------------|
| handheld | GPS portable | Appareil GPS de poche |
| dgps | GPS differentiel | DGPS avec station de base |
| rtk | GPS RTK | Cinematique en temps reel |
| total_station | Station totale | Leve a la station totale |

### Condition de Surface (12.4)

**Champ** : `comboBox_surface_condition`
**Base de donnees** : `surface_condition`

| Code | Francais | Description |
|------|----------|-------------|
| ploughed | Laboure | Champ fraichement laboure |
| stubble | Chaumes | Presence de chaumes |
| pasture | Paturage | Prairie/paturage |
| woodland | Boise | Zone boisee |
| urban | Urbain | Zone urbaine/batie |

### Accessibilite (12.5)

**Champ** : `comboBox_accessibility`
**Base de donnees** : `accessibility`

| Code | Francais | Description |
|------|----------|-------------|
| easy | Acces facile | Aucune restriction |
| moderate_access | Acces modere | Quelques difficultes |
| difficult | Acces difficile | Problemes significatifs |
| restricted | Acces restreint | Sur autorisation uniquement |

### Conditions Meteorologiques (12.6)

**Champ** : `comboBox_weather_conditions`
**Base de donnees** : `weather_conditions`

| Code | Francais | Description |
|------|----------|-------------|
| sunny | Ensoleille | Temps clair |
| cloudy | Nuageux | Conditions nuageuses |
| rainy | Pluvieux | Pluie pendant la prospection |
| windy | Venteux | Vent fort |

---

## Donnees Environnementales

### Pourcentage de Visibilite

**Champ** : `spinBox_visibility_percent`
**Base de donnees** : `visibility_percent`

Pourcentage de visibilite du sol (0-100%). Valeur numerique importante pour le calcul du potentiel archeologique.

### Pente du Terrain

**Champ** : `lineEdit_andamento_terreno_pendenza`
**Base de donnees** : `andamento_terreno_pendenza`

Morphologie et pente du terrain.

### Utilisation du Sol

**Champ** : `lineEdit_utilizzo_suolo_vegetazione`
**Base de donnees** : `utilizzo_suolo_vegetazione`

Usage du sol au moment de la prospection.

---

## Donnees Materiaux

### Dimensions UT

**Champ** : `lineEdit_dimensioni_ut`
**Base de donnees** : `dimensioni_ut`

Etendue en m2.

### Objets par m2

**Champ** : `lineEdit_rep_per_mq`
**Base de donnees** : `rep_per_mq`

Densite des materiaux par metre carre. Valeur critique pour le calcul du potentiel.

### Objets Datants

**Champ** : `lineEdit_rep_datanti`
**Base de donnees** : `rep_datanti`

Description des materiaux diagnostiques.

---

## Chronologie

### Periode I

| Champ | Base de donnees |
|-------|-----------------|
| Periode I | `periodo_I` |
| Datation I | `datazione_I` |
| Interpretation I | `interpretazione_I` |

### Periode II

| Champ | Base de donnees |
|-------|-----------------|
| Periode II | `periodo_II` |
| Datation II | `datazione_II` |
| Interpretation II | `interpretazione_II` |

---

## Onglet Analyse - Potentiel et Risque Archeologique

L'onglet **Analyse** fournit des outils avances pour le calcul automatique du potentiel et du risque archeologique.

### Potentiel Archeologique

Le systeme calcule un score de 0 a 100 base sur differents facteurs ponderes :

| Facteur | Poids | Description | Comment il est calcule |
|---------|-------|-------------|------------------------|
| Definition UT | 30% | Type d'evidence archeologique | "site" = 100, "structure" = 90, "concentration" = 80, "scatter" = 60, etc. |
| Periode historique | 25% | Chronologie des materiaux | Les periodes anciennes pesent plus (Prehistorique = 90, Romain = 85, Medieval = 70, etc.) |
| Densite de mobilier | 20% | Materiaux par m2 | >10/m2 = 100, 5-10 = 80, 2-5 = 60, <2 = 40 |
| Condition de surface | 15% | Visibilite et accessibilite | "ploughed" = 90, "stubble" = 70, "pasture" = 50, "woodland" = 30 |
| Documentation | 10% | Qualite de la documentation | Presence photo = +20, bibliographie = +30, investigations = +50 |

**Classification du score :**

| Score | Niveau | Couleur | Signification |
|-------|--------|---------|---------------|
| 80-100 | Eleve | Vert | Haute probabilite de depots significatifs |
| 60-79 | Moyen-Eleve | Jaune-Vert | Bonne probabilite, verification recommandee |
| 40-59 | Moyen | Orange | Probabilite moderee |
| 20-39 | Faible | Rouge | Faible probabilite |
| 0-19 | Non evaluable | Gris | Donnees insuffisantes |

### Risque Archeologique

Evalue le risque d'impact/perte du patrimoine :

| Facteur | Poids | Description | Comment il est calcule |
|---------|-------|-------------|------------------------|
| Accessibilite | 25% | Facilite d'acces a la zone | "easy" = 80, "moderate" = 50, "difficult" = 30, "restricted" = 10 |
| Usage du sol | 25% | Activites agricoles/constructives | "urban" = 90, "ploughed" = 70, "pasture" = 40, "woodland" = 20 |
| Classements existants | 20% | Protections juridiques | Absence de classement = 80, classement paysager = 40, classement archeologique = 10 |
| Investigations anterieures | 15% | Etat des connaissances | Aucune investigation = 60, prospection = 40, fouille = 20 |
| Potentiel | 15% | Inversement proportionnel au potentiel | Potentiel eleve = risque eleve de perte |

**Classification du risque :**

| Score | Niveau | Couleur | Action recommandee |
|-------|--------|---------|-------------------|
| 75-100 | Eleve | Rouge | Intervention urgente, mesures de protection immediates |
| 50-74 | Moyen | Orange | Surveillance active, evaluer la protection |
| 25-49 | Faible | Jaune | Surveillance periodique |
| 0-24 | Nul | Vert | Aucune intervention immediate necessaire |

### Champs Base de Donnees pour l'Analyse

| Champ | Base de donnees | Description |
|-------|-----------------|-------------|
| Score Potentiel | `potential_score` | Valeur 0-100 calculee |
| Score Risque | `risk_score` | Valeur 0-100 calculee |
| Facteurs Potentiel | `potential_factors` | JSON avec detail des facteurs |
| Facteurs Risque | `risk_factors` | JSON avec detail des facteurs |
| Date Analyse | `analysis_date` | Horodatage du calcul |
| Methode Analyse | `analysis_method` | Algorithme utilise |

---

## Couches Geometriques UT

PyArchInit gere trois types de geometries pour les Unites Topographiques :

### Tables Geometriques

| Couche | Table | Type Geometrie | Usage |
|--------|-------|----------------|-------|
| UT Points | `pyarchinit_ut_point` | Point | Localisation ponctuelle |
| UT Lignes | `pyarchinit_ut_line` | LineString | Traces, parcours |
| UT Polygones | `pyarchinit_ut_polygon` | Polygon | Zones de dispersion |

### Creation des Couches UT

1. **Via Navigateur QGIS :**
   - Ouvrir la base de donnees dans le Navigateur
   - Localiser la table `pyarchinit_ut_point/line/polygon`
   - Glisser sur la carte

2. **Via Menu PyArchInit :**
   - Menu **PyArchInit** > **Outils SIG** > **Charger Couches UT**
   - Selectionner le type de geometrie

### Liaison UT-Geometrie

Chaque enregistrement geometrique est lie a la fiche UT par :

| Champ | Description |
|-------|-------------|
| `progetto` | Nom du projet (doit correspondre) |
| `nr_ut` | Numero UT (doit correspondre) |

### Workflow Creation Geometries

1. **Activer l'edition** sur la couche UT souhaitee
2. **Dessiner** la geometrie sur la carte
3. **Remplir** les attributs `progetto` et `nr_ut`
4. **Enregistrer** la couche
5. **Verifier** la liaison depuis la fiche UT

---

## Generation de Cartes de Chaleur (Heatmap)

Le module de generation de cartes de chaleur permet de visualiser la distribution spatiale du potentiel et du risque archeologique.

### Exigences Minimales

- **Au moins 2 UT** avec coordonnees valides (`coord_geografiche` OU `coord_piane`)
- **Scores calcules** pour le potentiel et/ou le risque
- **SCR defini** dans le projet QGIS

### Methodes d'Interpolation

| Methode | Description | Quand l'utiliser |
|---------|-------------|------------------|
| **KDE** (Kernel Density) | Estimation de densite par noyau gaussien | Distribution continue, nombreux points |
| **IDW** (Inverse Distance) | Poids inverse de la distance | Donnees eparses, valeurs ponctuelles importantes |
| **Grid** | Interpolation sur grille reguliere | Analyses systematiques |

### Parametres Heatmap

| Parametre | Valeur par Defaut | Description |
|-----------|-------------------|-------------|
| Taille cellule | 50 m | Resolution de la grille |
| Bande passante (KDE) | Auto | Rayon d'influence |
| Puissance (IDW) | 2 | Exposant de ponderation |

### Procedure de Generation

1. **Depuis la fiche UT :**
   - Aller a l'onglet **Analyse**
   - Verifier que les scores sont calcules
   - Cliquer **Generer Heatmap**

2. **Selection des parametres :**
   - Type : Potentiel ou Risque
   - Methode : KDE, IDW, ou Grid
   - Taille cellule : typiquement 25-100 m

3. **Sortie :**
   - Couche raster ajoutee a QGIS
   - Enregistree dans `pyarchinit_Raster_folder`
   - Symbologie appliquee automatiquement

### Heatmap avec Masque Polygonal (GNA)

Pour generer des cartes de chaleur **a l'interieur d'une zone de projet** (ex. perimetre d'etude) :

1. **Preparer le polygone** de la zone de projet
2. **Utiliser l'Export GNA** (voir section suivante)
3. Le systeme **masque** automatiquement la heatmap au polygone

---

## Export GNA - Geoportail National pour l'Archeologie

### Qu'est-ce que le GNA ?

Le **Geoportail National pour l'Archeologie** (GNA) est le systeme d'information du Ministere de la Culture italien pour la gestion des donnees archeologiques territoriales. PyArchInit supporte l'export au format GeoPackage standard GNA.

### Structure GeoPackage GNA

| Couche | Type | Description |
|--------|------|-------------|
| **MOPR** | Polygon | Zone/Perimetre de projet |
| **MOSI** | Point/Polygon | Sites archeologiques (UT) |
| **VRP** | MultiPolygon | Carte du Potentiel Archeologique |
| **VRD** | MultiPolygon | Carte du Risque Archeologique |

### Correspondance Champs UT vers MOSI GNA

| Champ GNA | Champ UT PyArchInit | Notes |
|-----------|---------------------|-------|
| ID | `{progetto}_{nr_ut}` | Identifiant compose |
| AMA | `def_ut` | Vocabulaire controle GNA |
| OGD | `interpretazione_ut` | Definition de l'objet |
| OGT | `geometria` | Type de geometrie |
| DES | `descrizione_ut` | Description (max 10000 car.) |
| OGM | `metodo_rilievo_e_ricognizione` | Modalite d'identification |
| DTSI | `periodo_I` -> date | Date debut (negatif pour av. J.-C.) |
| DTSF | `periodo_II` -> date | Date fin |
| PRVN | `nazione` | Pays |
| PVCR | `regione` | Region |
| PVCP | `provincia` | Province |
| PVCC | `comune` | Commune |
| LCDQ | `quota` | Altitude NGF |

### Classification VRP (Potentiel)

| Plage | Code GNA | Etiquette | Couleur |
|-------|----------|-----------|---------|
| 0-20 | NV | Non evaluable | Gris |
| 20-40 | NU | Nul | Vert |
| 40-60 | BA | Faible | Jaune |
| 60-80 | ME | Moyen | Orange |
| 80-100 | AL | Eleve | Rouge |

### Classification VRD (Risque)

| Plage | Code GNA | Etiquette | Couleur |
|-------|----------|-----------|---------|
| 0-25 | NU | Nul | Vert |
| 25-50 | BA | Faible | Jaune |
| 50-75 | ME | Moyen | Orange |
| 75-100 | AL | Eleve | Rouge |

### Procedure d'Export GNA

1. **Preparation des donnees :**
   - Verifier que toutes les UT ont des coordonnees
   - Calculer les scores potentiel/risque
   - Preparer le polygone de la zone de projet (MOPR)

2. **Demarrage de l'export :**
   - Depuis la fiche UT, cliquer **Export GNA**
   - Ou menu **PyArchInit** > **GNA** > **Export**

3. **Configuration :**
   ```
   Projet : [selectionner projet]
   Zone de projet : [selectionner couche polygone MOPR]
   Sortie : [chemin fichier .gpkg]

   [x] Exporter MOSI (sites)
   [x] Generer VRP (potentiel)
   [x] Generer VRD (risque)

   Methode heatmap : KDE
   Taille cellule : 50 m
   ```

4. **Execution :**
   - Cliquer **Exporter**
   - Attendre la generation (peut prendre quelques minutes)
   - Le GeoPackage est enregistre au chemin specifie

5. **Verification de la sortie :**
   - Ouvrir le GeoPackage dans QGIS
   - Verifier les couches MOPR, MOSI, VRP, VRD
   - Controler que les geometries VRP/VRD sont decoupees au MOPR

### Validation GNA

Pour valider la sortie contre les specifications GNA :

1. Charger le GeoPackage dans le **modele GNA officiel**
2. Verifier que les couches sont reconnues
3. Controler les vocabulaires controles
4. Verifier les relations geometriques (MOSI dans MOPR)

---

## Export PDF

### Fiche UT Individuelle

Exporte la fiche UT complete en format PDF professionnel.

**Contenu :**
- En-tete avec projet et numero UT
- Section Identification
- Section Localisation
- Section Terrain
- Section Donnees Survey
- Section Chronologie
- Section Analyse (potentiel/risque avec barres colorees)
- Section Documentation

**Procedure :**
1. Selectionner l'enregistrement UT
2. Cliquer le bouton **PDF** dans la barre d'outils
3. Le PDF est enregistre dans `pyarchinit_PDF_folder`

### Liste des UT (PDF Liste)

Exporte une liste tabulaire de toutes les UT en format paysage.

**Colonnes :**
- UT, Projet, Definition, Interpretation
- Commune, Coordonnees, Periode I, Periode II
- Obj/m2, Visibilite, Potentiel, Risque

**Procedure :**
1. Charger les UT a exporter (recherche ou afficher tout)
2. Cliquer le bouton **PDF Liste** dans la barre d'outils
3. Le PDF est enregistre sous `Elenco_UT.pdf`

### Rapport d'Analyse UT

Genere un rapport detaille de l'analyse potentiel/risque.

**Contenu :**
1. Donnees d'identification de l'UT
2. Section Potentiel Archeologique
   - Score avec indicateur graphique
   - Texte narratif descriptif
   - Tableau des facteurs avec contributions
3. Section Risque Archeologique
   - Score avec indicateur graphique
   - Texte narratif avec recommandations
   - Tableau des facteurs avec contributions
4. Section Methodologie

---

## Workflow Operationnel Complet

### Phase 1 : Configuration du Projet

1. **Creer un nouveau projet** dans PyArchInit ou en utiliser un existant
2. **Definir la zone d'etude** (polygone MOPR)
3. **Configurer le SCR** du projet QGIS

### Phase 2 : Enregistrement des UT sur le Terrain

1. **Ouverture de la fiche UT**
2. **Nouvel enregistrement** (cliquer "New Record")
3. **Remplir les donnees d'identification :**
   ```
   Projet : Survey Vallee du Rhone 2024
   N. UT : 25
   ```

4. **Remplir la localisation :**
   ```
   Region : Provence-Alpes-Cote d'Azur
   Province : Vaucluse
   Commune : Orange
   Localite : Colline Haute
   Coord. geographiques : 44.1234, 4.5678
   Altitude : 125 m
   Precision GPS : 3 m
   ```

5. **Remplir la description** (utilisant le thesaurus) :
   ```
   Definition : Concentration de mobilier
   Description : Zone elliptique d'env. 50x30 m
   avec concentration de fragments ceramiques
   et briques sur versant collinaire...
   ```

6. **Remplir les donnees survey** (utilisant le thesaurus) :
   ```
   Type Survey : Prospection intensive
   Couverture Vegetale : Clairsemee
   Methode GPS : GPS differentiel
   Condition Surface : Laboure
   Accessibilite : Acces facile
   Conditions Meteo : Ensoleille
   Visibilite : 80%
   Date : 15/04/2024
   Responsable : Equipe A
   ```

7. **Remplir materiaux et chronologie :**
   ```
   Dimensions : 1500 m2
   Obj/m2 : 5-8
   Objets datants : Ceramique commune,
   sigillee italique, briques

   Periode I : Romain
   Datation I : Ier-IIe s. ap. J.-C.
   Interpretation I : Villa rustica
   ```

8. **Enregistrer** (cliquer "Save")

### Phase 3 : Creation des Geometries

1. **Charger la couche** `pyarchinit_ut_polygon`
2. **Activer l'edition**
3. **Dessiner** le perimetre de l'UT sur la carte
4. **Remplir les attributs** : progetto, nr_ut
5. **Enregistrer** la couche

### Phase 4 : Analyse

1. **Ouvrir l'onglet Analyse** dans la fiche UT
2. **Verifier** les scores calcules automatiquement
3. **Generer une heatmap** si necessaire
4. **Exporter le rapport PDF** de l'analyse

### Phase 5 : Export GNA (si requis)

1. **Verifier la completude des donnees** pour toutes les UT
2. **Preparer le polygone MOPR** de la zone de projet
3. **Executer l'Export GNA**
4. **Valider la sortie** contre les specifications GNA

---

## Conseils et Astuces

### Optimisation du Workflow

1. **Pre-remplir les thesaurus** avant de commencer les prospections
2. **Utiliser des modeles de projet** avec donnees communes pre-remplies
3. **Synchroniser les coordonnees** du GPS au champ `coord_geografiche`
4. **Enregistrer frequemment** pendant la saisie

### Ameliorer la Qualite des Donnees

1. **Remplir TOUS les champs** pertinents pour chaque UT
2. **Toujours utiliser les thesaurus** au lieu du texte libre
3. **Verifier les coordonnees** sur la carte avant d'enregistrer
4. **Documenter photographiquement** chaque UT

### Optimisation des Heatmaps

1. **Taille de cellule appropriee** : utiliser 25-50m pour les petites zones, 100-200m pour les zones etendues
2. **Methode KDE** pour distributions continues et homogenes
3. **Methode IDW** quand les valeurs ponctuelles sont critiques
4. **Toujours verifier** que les coordonnees sont correctes avant de generer

### Export GNA Efficace

1. **Preparer le polygone MOPR** a l'avance comme couche separee
2. **Verifier que toutes les UT** ont des coordonnees valides
3. **Calculer les scores** avant l'export
4. **Utiliser des noms de fichiers** descriptifs pour les GeoPackages

### Gestion Multi-Utilisateurs

1. **Definir des conventions** de numerotation UT partagees
2. **Utiliser une base PostgreSQL** pour l'acces concurrent
3. **Synchroniser periodiquement** les donnees
4. **Documenter les modifications** dans les champs notes

---

## Depannage

### Probleme : Listes Deroulantes Thesaurus Vides

**Symptomes :** Les menus deroulants pour survey_type, vegetation, etc. sont vides.

**Causes :**
- Entrees thesaurus non presentes dans la base de donnees
- Code langue incorrect
- Table thesaurus non mise a jour

**Solutions :**
1. Menu **PyArchInit** > **Base de donnees** > **Mettre a jour la base de donnees**
2. Verifier la table `pyarchinit_thesaurus_sigle` pour les entrees `ut_table`
3. Controler les parametres de langue
4. Si necessaire, reimporter les thesaurus depuis le modele

### Probleme : Coordonnees Non Valides

**Symptomes :** Erreur lors de l'enregistrement ou coordonnees affichees a une position incorrecte.

**Causes :**
- Format incorrect (virgule vs point decimal)
- Systeme de reference non correspondant
- Ordre lat/lon inverse

**Solutions :**
1. Format correct `coord_geografiche` : `42.1234, 12.5678` (lat, lon)
2. Format correct `coord_piane` : `1234567.89, 4567890.12` (x, y)
3. Toujours utiliser le point comme separateur decimal
4. Verifier le SCR du projet QGIS

### Probleme : UT Non Visible sur la Carte

**Symptomes :** Apres l'enregistrement, l'UT n'apparait pas sur la carte.

**Causes :**
- Geometrie non creee dans la couche
- Attributs `progetto`/`nr_ut` non correspondants
- Couche non chargee ou masquee
- SCR different entre couche et projet

**Solutions :**
1. Verifier que la couche `pyarchinit_ut_point/polygon` existe
2. Controler que les attributs sont correctement remplis
3. Activer la visibilite de la couche dans le panneau Couches
4. Utiliser "Zoomer sur la couche" pour verifier l'emprise

### Probleme : Heatmap Non Generee

**Symptomes :** Erreur "Il faut au moins 2 points avec coordonnees valides".

**Causes :**
- Moins de 2 UT avec coordonnees
- Coordonnees en format incorrect
- Champs coordonnees vides

**Solutions :**
1. Verifier qu'au moins 2 UT ont `coord_geografiche` OU `coord_piane` remplis
2. Controler le format des coordonnees (point decimal, ordre correct)
3. Recalculer les scores avant de generer la heatmap
4. Verifier que les champs ne contiennent pas de caracteres speciaux

### Probleme : Score Potentiel/Risque Non Calcule

**Symptomes :** Les champs potentiel_score et risk_score sont vides ou a zero.

**Causes :**
- Champs obligatoires non remplis
- Valeurs thesaurus non reconnues
- Erreur dans le calcul

**Solutions :**
1. Remplir au minimum : `def_ut`, `periodo_I`, `visibility_percent`
2. Utiliser des valeurs du thesaurus (pas de texte libre)
3. Enregistrer l'enregistrement et le rouvrir
4. Verifier dans les logs QGIS les eventuelles erreurs

### Probleme : Export GNA Echoue

**Symptomes :** Le GeoPackage n'est pas cree ou est incomplet.

**Causes :**
- Module GNA non disponible
- Donnees UT incompletes
- Polygone MOPR non valide
- Permissions d'ecriture insuffisantes

**Solutions :**
1. Verifier que le module `modules/gna` est installe
2. Controler que toutes les UT ont des coordonnees valides
3. Verifier que le polygone MOPR est valide (pas d'auto-intersections)
4. Controler les permissions sur le dossier de sortie
5. Verifier l'espace disque suffisant

### Probleme : Export PDF avec Champs Manquants

**Symptomes :** Le PDF genere n'affiche pas certains champs ou affiche des valeurs incorrectes.

**Causes :**
- Champs de base de donnees non mis a jour
- Version du schema de base de donnees obsolete
- Donnees non enregistrees avant l'export

**Solutions :**
1. Enregistrer l'enregistrement avant d'exporter
2. Mettre a jour la base de donnees si necessaire
3. Verifier que les nouveaux champs (v4.9.67+) existent dans la table

### Probleme : Erreur Qt6/QGIS 4.x

**Symptomes :** Le plugin ne se charge pas sur QGIS 4.x avec erreur `AllDockWidgetFeatures`.

**Causes :**
- Incompatibilite Qt5/Qt6
- Fichier UI non mis a jour

**Solutions :**
1. Mettre a jour PyArchInit a la derniere version
2. Le fichier `UT_ui.ui` doit utiliser des drapeaux explicites au lieu de `AllDockWidgetFeatures`

---

## References

### Base de Donnees

- **Table** : `ut_table`
- **Classe mapper** : `UT`
- **ID** : `id_ut`

### Tables Geometriques

- **Points** : `pyarchinit_ut_point`
- **Lignes** : `pyarchinit_ut_line`
- **Polygones** : `pyarchinit_ut_polygon`

### Fichiers Source

| Fichier | Description |
|---------|-------------|
| `gui/ui/UT_ui.ui` | Interface utilisateur Qt |
| `tabs/UT.py` | Controleur principal |
| `modules/utility/pyarchinit_exp_UTsheet_pdf.py` | Export PDF fiches |
| `modules/utility/pyarchinit_exp_UT_analysis_pdf.py` | Export PDF analyse |
| `modules/analysis/ut_potential.py` | Calcul du potentiel |
| `modules/analysis/ut_risk.py` | Calcul du risque |
| `modules/analysis/ut_heatmap_generator.py` | Generation heatmap |
| `modules/gna/gna_exporter.py` | Export GNA |
| `modules/gna/gna_vocabulary_mapper.py` | Correspondance vocabulaires GNA |

### Codes Thesaurus UT

| Code | Champ | Description |
|------|-------|-------------|
| 12.1 | survey_type | Type de prospection |
| 12.2 | vegetation_coverage | Couverture vegetale |
| 12.3 | gps_method | Methode GPS |
| 12.4 | surface_condition | Condition de surface |
| 12.5 | accessibility | Accessibilite |
| 12.6 | weather_conditions | Conditions meteorologiques |
| 12.7 | def_ut | Definition UT |

---

## Video Tutorial

### Documentation des Prospections
**Duree** : 15-18 minutes
- Enregistrement UT
- Donnees survey avec thesaurus
- Geolocalisation

### Analyse Potentiel et Risque
**Duree** : 10-12 minutes
- Calcul automatique des scores
- Interpretation des resultats
- Generation de heatmap

### Export GNA
**Duree** : 12-15 minutes
- Preparation des donnees
- Configuration de l'export
- Validation de la sortie

### Export Rapport PDF
**Duree** : 8-10 minutes
- Fiche UT standard
- Liste des UT
- Rapport d'analyse avec cartes

---

*Derniere mise a jour : Janvier 2026*
*PyArchInit v4.9.68 - Systeme de Gestion des Donnees Archeologiques*
