# Tutorial 06 : Fiche Tombe

## Introduction

La **Fiche Tombe** est le module de PyArchInit dédié à la documentation des sépultures archéologiques. Cet outil permet d'enregistrer tous les aspects d'une tombe : de la structure funéraire au rite, du mobilier aux individus inhumés.

### Concepts de Base

**Tombe dans PyArchInit :**
- Une tombe est une structure funéraire contenant un ou plusieurs individus
- Elle est liée à la Fiche Structure (la structure physique de la sépulture)
- Elle est liée à la Fiche Individus (pour les données anthropologiques)
- Elle documente le rite, le mobilier et les caractéristiques de la déposition

**Relations :**
```
Tombe → Structure (contenant physique)
     → Individu(s) (restes humains)
     → Mobilier (objets d'accompagnement)
     → Inventaire Matériaux (mobilier associé)
```

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche Tombe** (ou **Grave form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Tombe** (symbole sépulture)

---

## Aperçu de l'Interface

La fiche présente une disposition organisée en sections fonctionnelles :

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | DB Info | État record, tri, compteur |
| 3 | Champs Identificatifs | Site, Zone, N. Fiche, Structure |
| 4 | Champs Individu | Liaison à l'individu |
| 5 | Zone Tab | Onglets thématiques pour données spécifiques |

---

## Toolbar DBMS

La toolbar principale fournit les outils pour la gestion des enregistrements.

### Boutons de Navigation

| Icône | Fonction | Description |
|-------|----------|-------------|
| First rec | Premier | Aller au premier enregistrement |
| Prev rec | Précédent | Aller à l'enregistrement précédent |
| Next rec | Suivant | Aller à l'enregistrement suivant |
| Last rec | Dernier | Aller au dernier enregistrement |

### Boutons CRUD

| Icône | Fonction | Description |
|-------|----------|-------------|
| New record | Nouveau | Créer un nouvel enregistrement tombe |
| Save | Sauvegarder | Sauvegarder les modifications |
| Delete | Supprimer | Supprimer l'enregistrement actuel |

### Boutons de Recherche

| Icône | Fonction | Description |
|-------|----------|-------------|
| New search | Nouvelle recherche | Démarrer une nouvelle recherche |
| Search!!! | Exécuter recherche | Exécuter la recherche |
| Order by | Trier par | Trier les résultats |
| View all | Voir tout | Afficher tous les enregistrements |

### Boutons Spéciaux

| Icône | Fonction | Description |
|-------|----------|-------------|
| GIS | Charger GIS | Charger la tombe sur la carte |
| PDF export | Export PDF | Exporter en PDF |
| Open directory | Ouvrir dossier | Ouvrir le dossier d'export |

---

## Champs Identificatifs

Les champs identificatifs définissent de manière unique la tombe dans la base de données.

### Site

**Champ** : `comboBox_sito`
**Base de données** : `sito`

Sélectionne le site archéologique d'appartenance.

### Zone

**Champ** : `comboBox_area`
**Base de données** : `area`

Zone de fouille au sein du site.

### Numéro Fiche

**Champ** : `lineEdit_nr_scheda`
**Base de données** : `nr_scheda_taf`

Numéro progressif de la fiche tombe. Le prochain numéro disponible est proposé automatiquement.

### Sigle et Numéro Structure

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Sigle structure | `sigla_struttura` | Sigle de la structure (ex. TM, TB) |
| N° structure | `nr_struttura` | Numéro de la structure |

Ces champs relient la tombe à la Fiche Structure correspondante.

### Numéro Individu

**Champ** : `comboBox_nr_individuo`
**Base de données** : `nr_individuo`

Numéro de l'individu inhumé. Relie la tombe à la Fiche Individus.

**Notes :**
- Une tombe peut contenir plusieurs individus (sépulture multiple)
- Le menu affiche les individus disponibles pour la structure sélectionnée

---

## Tab Données Descriptives

Le premier tab contient les champs fondamentaux pour décrire la sépulture.

### Rite

**Champ** : `comboBox_rito`
**Base de données** : `rito`

Type de rituel funéraire pratiqué.

**Valeurs typiques :**
| Rite | Description |
|------|-------------|
| Inhumation | Déposition du corps entier |
| Crémation | Incinération des restes |
| Incinération primaire | Crémation sur place |
| Incinération secondaire | Crémation ailleurs et déposition |
| Mixte | Combinaison de rites |
| Indéterminé | Non déterminable |

### Type de Sépulture

**Champ** : `comboBox_tipo_sepoltura`
**Base de données** : `tipo_sepoltura`

Classification typologique de la sépulture.

**Exemples :**
- Tombe à fosse simple
- Tombe en coffre
- Tombe à chambre
- Tombe sous tuiles (cappuccina)
- Tombe à enchytrismos
- Sarcophage
- Ossuaire

### Type de Déposition

**Champ** : `comboBox_tipo_deposizione`
**Base de données** : `tipo_deposizione`

Modalité de déposition du corps.

**Valeurs :**
- Primaire (déposition directe)
- Secondaire (réduction/déplacement)
- Multiple simultanée
- Multiple successive

### État de Conservation

**Champ** : `comboBox_stato_conservazione`
**Base de données** : `stato_di_conservazione`

Évaluation de l'état de conservation.

**Échelle :**
- Excellent
- Bon
- Moyen
- Mauvais
- Très mauvais

### Description

**Champ** : `textEdit_descrizione`
**Base de données** : `descrizione_taf`

Description détaillée de la tombe.

**Contenus conseillés :**
- Forme et dimensions de la fosse
- Orientation
- Profondeur
- Caractéristiques du remplissage
- État au moment de la fouille

### Interprétation

**Champ** : `textEdit_interpretazione`
**Base de données** : `interpretazione_taf`

Interprétation historico-archéologique de la sépulture.

---

## Caractéristiques de la Tombe

### Signalisation

**Champ** : `comboBox_segnacoli`
**Base de données** : `segnacoli`

Présence et type de signalisation funéraire.

**Valeurs :**
- Absent
- Stèle
- Cippe
- Tumulus
- Enclos
- Autre

### Canal Libatoire

**Champ** : `comboBox_canale_libatorio`
**Base de données** : `canale_libatorio_si_no`

Présence d'un canal pour libations rituelles.

**Valeurs :** Oui / Non

### Couverture

**Champ** : `comboBox_copertura_tipo`
**Base de données** : `copertura_tipo`

Type de couverture de la tombe.

**Exemples :**
- Tuiles
- Dalles de pierre
- Planches de bois
- Terre
- Absent

### Contenant des Restes

**Champ** : `comboBox_tipo_contenitore`
**Base de données** : `tipo_contenitore_resti`

Type de contenant pour les restes.

**Exemples :**
- Fosse en pleine terre
- Coffre en bois
- Coffre en pierre
- Amphore
- Urne
- Sarcophage

### Objets Extérieurs

**Champ** : `comboBox_oggetti_esterno`
**Base de données** : `oggetti_rinvenuti_esterno`

Objets trouvés à l'extérieur de la tombe mais associés à celle-ci.

---

## Tab Mobilier

Ce tab gère la documentation du mobilier funéraire.

### Présence Mobilier

**Champ** : `comboBox_corredo_presenza`
**Base de données** : `corredo_presenza`

Indique si la tombe contenait du mobilier.

**Valeurs :**
- Oui
- Non
- Probable
- Enlevé

### Type Mobilier

**Champ** : `comboBox_corredo_tipo`
**Base de données** : `corredo_tipo`

Classification générale du mobilier.

**Catégories :**
- Personnel (bijoux, fibules)
- Rituel (vases, lampes)
- Symbolique (monnaies, amulettes)
- Instrumental (outils)
- Mixte

### Description Mobilier

**Champ** : `textEdit_corredo_descrizione`
**Base de données** : `corredo_descrizione`

Description détaillée des objets du mobilier.

### Tableau Mobilier

**Widget** : `tableWidget_corredo_tipo`

Tableau pour enregistrer les éléments individuels du mobilier.

**Colonnes :**
| Colonne | Description |
|---------|-------------|
| ID Objet | Numéro d'inventaire de l'objet |
| ID Indiv. | Individu associé |
| Matériau | Type de matériau |
| Position du mobilier | Où il était placé dans la tombe |
| Position dans le mobilier | Position par rapport au corps |

**Notes :**
- Les éléments sont liés à la Fiche Inventaire Matériaux
- Le tableau se remplit automatiquement avec les objets de la structure

---

## Tab Autres Caractéristiques

Ce tab contient des informations supplémentaires sur la sépulture.

### Périodisation

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Période initiale | `periodo_iniziale` | Période de début d'utilisation |
| Phase initiale | `fase_iniziale` | Phase dans la période |
| Période finale | `periodo_finale` | Période de fin d'utilisation |
| Phase finale | `fase_finale` | Phase dans la période |
| Datation étendue | `datazione_estesa` | Datation littérale |

Les valeurs sont remplies en fonction de la Fiche Périodisation du site.

---

## Tab Outils

Le tab Outils contient des fonctionnalités supplémentaires.

### Gestion Médias

Permet de :
- Visualiser les images associées
- Ajouter de nouvelles photos par drag & drop
- Rechercher des médias dans la base de données

### Export

Options d'exportation :
- Liste Tombes (liste synthétique)
- Fiches Tombes (fiches complètes)
- Conversion PDF vers Word

---

## Intégration GIS

### Visualisation sur Carte

| Bouton | Fonction |
|--------|----------|
| GIS Toggle | Activer/désactiver le chargement automatique |
| Load to GIS | Charger la tombe sur la carte |

### Couches GIS

La fiche utilise des couches spécifiques pour les tombes :
- **pyarchinit_tomba** : géométrie des tombes
- Liaison avec les couches structures et US

---

## Export et Impression

### Export PDF

Le bouton PDF ouvre un panneau avec des options :

| Option | Description |
|--------|-------------|
| Liste Tombes | Liste synthétique des tombes |
| Fiches Tombes | Fiches complètes détaillées |
| Imprimer | Générer le PDF |

### Contenu Fiche PDF

La fiche PDF inclut :
- Données identificatives
- Rite et type de sépulture
- Description et interprétation
- Données du mobilier
- Périodisation
- Images associées

---

## Workflow Opérationnel

### Création d'une Nouvelle Tombe

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouveau record**
   - Clic sur "New Record"
   - Le numéro de fiche est proposé automatiquement

3. **Données identificatives**
   ```
   Site : Nécropole d'Isola Sacra
   Zone : 1
   N. Fiche : 45
   Sigle structure : TM
   N° structure : 45
   ```

4. **Liaison individu**
   ```
   N° Individu : 1
   ```

5. **Données descriptives** (Tab 1)
   ```
   Rite : Inhumation
   Type sépulture : Tombe à fosse simple
   Type déposition : Primaire
   État conservation : Bon

   Description : Fosse rectangulaire aux angles
   arrondis, orientée E-W...

   Signalisation : Cippe
   Couverture : Tuiles à la cappuccina
   ```

6. **Mobilier** (Tab 2)
   ```
   Présence : Oui
   Type : Personnel
   Description : Fibule en bronze près de
   l'épaule droite, monnaie près de la bouche...
   ```

7. **Périodisation**
   ```
   Période initiale : II - Phase A
   Période finale : II - Phase A
   Datation : IIe s. apr. J.-C.
   ```

8. **Sauvegarde**
   - Clic sur "Save"

### Recherche de Tombes

1. Clic sur "New Search"
2. Remplir les critères :
   - Site
   - Rite
   - Type sépulture
   - Période
3. Clic sur "Search"
4. Naviguer parmi les résultats

---

## Relations avec d'Autres Fiches

| Fiche | Relation |
|-------|----------|
| **Fiche Site** | Le site contient les tombes |
| **Fiche Structure** | La structure physique de la tombe |
| **Fiche Individus** | Les restes humains dans la tombe |
| **Fiche Inventaire Matériaux** | Les objets du mobilier |
| **Fiche Périodisation** | La chronologie |

### Flux de Travail Conseillé

1. Créer la **Fiche Site** (si elle n'existe pas)
2. Créer la **Fiche Structure** pour la tombe
3. Créer la **Fiche Tombe** en la reliant à la structure
4. Créer la **Fiche Individus** pour chaque individu
5. Enregistrer le mobilier dans la **Fiche Inventaire Matériaux**

---

## Bonnes Pratiques

### Nomenclature

- Utiliser des sigles cohérents (TM, TB, SEP)
- Numérotation progressive au sein du site
- Documenter les conventions adoptées

### Description

- Décrire systématiquement forme, dimensions, orientation
- Documenter l'état au moment de la fouille
- Séparer observations objectives et interprétations

### Mobilier

- Enregistrer la position exacte de chaque objet
- Relier chaque élément à l'Inventaire Matériaux
- Documenter les associations significatives

### Périodisation

- Baser la datation sur des éléments diagnostiques
- Indiquer le degré de fiabilité
- Comparer avec des sépultures similaires

---

## Résolution des Problèmes

### Problème : Individu non disponible dans le menu

**Cause** : L'individu n'a pas encore été créé ou n'est pas associé à la structure.

**Solution** :
1. Vérifier que la Fiche Individus existe
2. Contrôler que l'individu est associé à la même structure

### Problème : Mobilier non affiché dans le tableau

**Cause** : Les objets ne sont pas liés à la structure.

**Solution** :
1. Ouvrir la Fiche Inventaire Matériaux
2. Vérifier que les objets ont la structure correcte
3. Actualiser la fiche Tombe

### Problème : Tombe non visible sur la carte

**Cause** : Géométrie non associée.

**Solution** :
1. Vérifier que la couche tombe existe
2. Contrôler que la structure a une géométrie
3. Vérifier le système de référence

---

## Références

### Base de données

- **Table** : `tomba_table`
- **Classe mapper** : `TOMBA`
- **ID** : `id_tomba`

### Fichiers Source

- **UI** : `gui/ui/Tomba.ui`
- **Contrôleur** : `tabs/Tomba.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Tombasheet_pdf.py`

---

## Vidéo Tutorial

### Aperçu Fiche Tombe
**Durée** : 5-6 minutes
- Présentation de l'interface
- Champs principaux
- Navigation entre les tabs

`[Placeholder vidéo : video_apercu_tombe.mp4]`

### Documentation Complète d'une Tombe
**Durée** : 10-12 minutes
- Création d'un nouveau record
- Remplissage de tous les champs
- Liaison individus et mobilier

`[Placeholder vidéo : video_documentation_tombe.mp4]`

### Gestion Mobilier Funéraire
**Durée** : 6-8 minutes
- Enregistrement des éléments du mobilier
- Liaison avec l'Inventaire Matériaux
- Documentation des positions

`[Placeholder vidéo : video_mobilier_tombe.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
