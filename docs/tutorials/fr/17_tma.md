# Tutorial 17 : TMA - Tableau des Matériaux Archéologiques

## Introduction

La **Fiche TMA** (Tableau des Matériaux Archéologiques) est le module avancé de PyArchInit pour la gestion des matériaux de fouille selon les standards ministériels italiens. Elle permet un catalogage détaillé conforme aux normes ICCD (Istituto Centrale per il Catalogo e la Documentazione).

### Caractéristiques Principales

- Catalogage conforme au standard ICCD
- Gestion des matériaux par caisse/contenant
- Champs chronologiques détaillés
- Tableau des matériaux associés
- Gestion des médias intégrée
- Export d'étiquettes et fiches PDF

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche TMA**

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **TMA**

---

## Aperçu de l'Interface

La fiche présente une interface complexe avec de nombreux champs.

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | Champs Identificatifs | Site, Zone, US, Caisse |
| 3 | Champs Localisation | Emplacement, Local, Sondage |
| 4 | Champs Chronologiques | Période, Fraction, Chronologies |
| 5 | Tableau Matériaux | Détail des matériaux associés |
| 6 | Tab Médias | Images et documents |

---

## Champs Identificatifs

### Site

**Champ** : `comboBox_sito`
**Base de données** : `sito`

Site archéologique (SCAN - Dénomination fouille ICCD).

### Zone

**Champ** : `comboBox_area`
**Base de données** : `area`

Zone de fouille.

### US (DSCU)

**Champ** : `comboBox_us`
**Base de données** : `dscu`

Unité Stratigraphique de provenance (DSCU = Description Fouille Unité).

### Secteur

**Champ** : `comboBox_settore`
**Base de données** : `settore`

Secteur de fouille.

### Inventaire

**Champ** : `lineEdit_inventario`
**Base de données** : `inventario`

Numéro d'inventaire.

### Caisse

**Champ** : `lineEdit_cassetta`
**Base de données** : `cassetta`

Numéro de la caisse/contenant.

---

## Champs Localisation ICCD

### LDCT - Typologie Emplacement

**Champ** : `comboBox_ldct`
**Base de données** : `ldct`

Type de lieu de conservation.

**Valeurs ICCD :**
- musée
- surintendance
- dépôt
- laboratoire
- autre

### LDCN - Dénomination Emplacement

**Champ** : `lineEdit_ldcn`
**Base de données** : `ldcn`

Nom spécifique du lieu de conservation.

### Ancien Emplacement

**Champ** : `lineEdit_vecchia_coll`
**Base de données** : `vecchia_collocazione`

Éventuel emplacement précédent.

### SCAN - Dénomination Fouille

**Champ** : `lineEdit_scan`
**Base de données** : `scan`

Nom officiel de la fouille/recherche.

### Sondage

**Champ** : `comboBox_saggio`
**Base de données** : `saggio`

Sondage/tranchée de référence.

### Local/Locus

**Champ** : `lineEdit_vano`
**Base de données** : `vano_locus`

Pièce ou locus de provenance.

---

## Champs Chronologiques

### DTZG - Période Chronologique

**Champ** : `comboBox_dtzg`
**Base de données** : `dtzg`

Période chronologique générale.

**Exemples ICCD :**
- âge du bronze
- âge du fer
- époque romaine
- époque médiévale

### DTZS - Fraction Chronologique

**Champ** : `comboBox_dtzs`
**Base de données** : `dtzs`

Subdivision de la période.

**Exemples :**
- ancien/ne
- moyen/ne
- tardif/ve
- final/e

### Chronologies

**Champ** : `tableWidget_cronologie`
**Base de données** : `cronologie`

Tableau pour chronologies multiples ou détaillées.

---

## Champs Acquisition

### AINT - Type Acquisition

**Champ** : `comboBox_aint`
**Base de données** : `aint`

Modalité d'acquisition des matériaux.

**Valeurs ICCD :**
- fouille
- prospection
- achat
- donation
- saisie

### AIND - Date Acquisition

**Champ** : `dateEdit_aind`
**Base de données** : `aind`

Date de l'acquisition.

### RCGD - Date Prospection

**Champ** : `dateEdit_rcgd`
**Base de données** : `rcgd`

Date de la prospection (si applicable).

### RCGZ - Spécifications Prospection

**Champ** : `textEdit_rcgz`
**Base de données** : `rcgz`

Notes sur la prospection.

---

## Champs Matériaux

### OGTM - Matériau

**Champ** : `comboBox_ogtm`
**Base de données** : `ogtm`

Matériau principal (Objet Type Matériau).

**Valeurs ICCD :**
- céramique
- verre
- métal
- os
- pierre
- brique

### N. Objets

**Champ** : `spinBox_n_reperti`
**Base de données** : `n_reperti`

Nombre total d'objets.

### Poids

**Champ** : `doubleSpinBox_peso`
**Base de données** : `peso`

Poids total en grammes.

### DESO - Indication Objets

**Champ** : `textEdit_deso`
**Base de données** : `deso`

Description synthétique des objets.

---

## Tableau Détail Matériaux

**Widget** : `tableWidget_materiali`
**Table associée** : `tma_materiali`

Permet d'enregistrer les matériaux individuels contenus dans la caisse.

### Colonnes

| Champ ICCD | Description |
|------------|-------------|
| MADI | Inventaire matériau |
| MACC | Catégorie |
| MACL | Classe |
| MACP | Précision typologique |
| MACD | Définition |
| Chronologie | Datation spécifique |
| MACQ | Quantité |

### Gestion des Lignes

| Bouton | Fonction |
|--------|----------|
| + | Ajouter un matériau |
| - | Supprimer un matériau |

---

## Champs Documentation

### FTAP - Type Photographie

**Champ** : `comboBox_ftap`
**Base de données** : `ftap`

Type de documentation photographique.

### FTAN - Code Photo

**Champ** : `lineEdit_ftan`
**Base de données** : `ftan`

Code identificatif de la photo.

### DRAT - Type Dessin

**Champ** : `comboBox_drat`
**Base de données** : `drat`

Type de documentation graphique.

### DRAN - Code Dessin

**Champ** : `lineEdit_dran`
**Base de données** : `dran`

Code identificatif du dessin.

### DRAA - Auteur Dessin

**Champ** : `lineEdit_draa`
**Base de données** : `draa`

Auteur du dessin.

---

## Tab Médias

Gestion des images associées à la caisse/TMA.

### Fonctionnalités

- Visualisation des miniatures
- Drag & drop pour ajouter des images
- Double-clic pour visualiser
- Liaison à la base de données médias

---

## Tab Table View

Vue tabulaire de tous les enregistrements TMA pour consultation rapide.

### Fonctionnalités

- Affichage en grille
- Tri par colonne
- Filtres rapides
- Sélection multiple

---

## Export et Impression

### Export PDF

| Option | Description |
|--------|-------------|
| Fiche TMA | Fiche complète |
| Étiquettes | Étiquettes pour caisses |

### Étiquettes Caisses

Génération automatique d'étiquettes pour :
- Identification des caisses
- Contenu synthétique
- Données de provenance
- Code-barres (optionnel)

---

## Workflow Opérationnel

### Enregistrement d'une Nouvelle TMA

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouvel enregistrement**
   - Cliquer sur "New Record"

3. **Données identificatives**
   ```
   Site : Villa Romaine
   Zone : 1000
   US : 150
   Caisse : C-001
   ```

4. **Localisation**
   ```
   LDCT : dépôt
   LDCN : Dépôt Surintendance Rome
   SCAN : Fouilles Villa Romaine 2024
   ```

5. **Chronologie**
   ```
   DTZG : époque romaine
   DTZS : impériale
   ```

6. **Matériaux** (tableau)
   ```
   | Inv | Cat | Classe | Déf | Q.té |
   |-----|-----|--------|-----|------|
   | 001 | céramique | commune | pot | 5 |
   | 002 | céramique | sigillée | plat | 3 |
   | 003 | verre | - | unguentarium | 1 |
   ```

7. **Sauvegarde**
   - Cliquer sur "Save"

---

## Bonnes Pratiques

### Standard ICCD

- Utiliser les vocabulaires contrôlés ICCD
- Respecter les sigles officiels
- Maintenir la cohérence terminologique

### Organisation des Caisses

- Numérotation progressive unique
- Une TMA par caisse physique
- Séparer par US quand possible

### Documentation

- Toujours lier photos et dessins
- Utiliser des codes uniques pour les médias
- Enregistrer auteur et date

---

## Résolution des Problèmes

### Problème : Vocabulaires ICCD non disponibles

**Cause** : Thésaurus non configuré.

**Solution** :
1. Importer les vocabulaires ICCD standard
2. Vérifier la configuration du thésaurus

### Problème : Matériaux non sauvegardés

**Cause** : Tableau des matériaux non synchronisé.

**Solution** :
1. Vérifier que tous les champs obligatoires sont remplis
2. Sauvegarder la fiche principale avant d'ajouter des matériaux

---

## Références

### Base de données

- **Table principale** : `tma_materiali_archeologici`
- **Table détail** : `tma_materiali`
- **Classe mapper** : `TMA`, `TMA_MATERIALI`
- **ID** : `id`

### Fichiers Source

- **UI** : `gui/ui/Tma.ui`
- **Contrôleur** : `tabs/Tma.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Tmasheet_pdf.py`
- **Étiquettes** : `modules/utility/pyarchinit_tma_label_pdf.py`

---

## Vidéo Tutorial

### Catalogage TMA
**Durée** : 15-18 minutes
- Standard ICCD
- Remplissage complet
- Gestion des matériaux

`[Placeholder vidéo : video_tma_catalogage.mp4]`

### Génération d'Étiquettes
**Durée** : 5-6 minutes
- Configuration des étiquettes
- Impression en lot
- Personnalisation

`[Placeholder vidéo : video_tma_etiquettes.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
