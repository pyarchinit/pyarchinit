# Tutorial 09 : Fiche Échantillons

## Introduction

La **Fiche Échantillons** est le module de PyArchInit dédié à la gestion des prélèvements archéologiques. Elle permet d'enregistrer et de suivre tous les types d'échantillons prélevés lors de la fouille : terres, charbons, graines, os, mortiers, métaux et tout autre matériau destiné à des analyses spécialisées.

### Types d'Échantillons

Les échantillons archéologiques comprennent :
- **Sédiments** : pour analyses sédimentologiques, granulométriques
- **Charbons** : pour datations radiométriques (C14)
- **Graines/Pollens** : pour analyses archéobotaniques
- **Os** : pour analyses archéozoologiques, isotopiques, ADN
- **Mortiers/Enduits** : pour analyses archéométriques
- **Métaux/Scories** : pour analyses métallurgiques
- **Céramiques** : pour analyses de pâte, provenance

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche Échantillons** (ou **Samples form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Échantillons**

---

## Aperçu de l'Interface

La fiche présente une disposition simplifiée pour la gestion rapide des échantillons.

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | DB Info | État record, tri, compteur |
| 3 | Champs Identificatifs | Site, N° Échantillon, Type |
| 4 | Champs Descriptifs | Description, notes |
| 5 | Champs de Conservation | Caisse, Lieu |

---

## Toolbar DBMS

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
| New record | Nouveau | Créer un nouvel enregistrement échantillon |
| Save | Sauvegarder | Sauvegarder les modifications |
| Delete | Supprimer | Supprimer l'enregistrement actuel |

### Boutons de Recherche

| Icône | Fonction | Description |
|-------|----------|-------------|
| New search | Nouvelle recherche | Démarrer une nouvelle recherche |
| Search!!! | Exécuter recherche | Exécuter la recherche |
| Order by | Trier par | Trier les résultats |
| View all | Voir tout | Afficher tous les enregistrements |

---

## Champs de la Fiche

### Site

**Champ** : `comboBox_sito`
**Base de données** : `sito`

Sélectionne le site archéologique d'appartenance.

### Numéro Échantillon

**Champ** : `lineEdit_nr_campione`
**Base de données** : `nr_campione`

Numéro identificatif progressif de l'échantillon.

### Type Échantillon

**Champ** : `comboBox_tipo_campione`
**Base de données** : `tipo_campione`

Classification typologique de l'échantillon. Les valeurs proviennent du thésaurus.

**Types courants :**
| Type | Description |
|------|-------------|
| Sédiment | Échantillon de terre |
| Charbon | Pour datations C14 |
| Graines | Restes carpologiques |
| Os | Restes faunistiques |
| Mortier | Liants de construction |
| Céramique | Pour analyse de pâte |
| Métal | Pour analyses métallurgiques |
| Pollen | Pour analyses palynologiques |

### Description

**Champ** : `textEdit_descrizione`
**Base de données** : `descrizione`

Description détaillée de l'échantillon.

**Contenus conseillés :**
- Caractéristiques physiques de l'échantillon
- Quantité prélevée
- Modalités de prélèvement
- Motif de l'échantillonnage
- Analyses prévues

### Zone

**Champ** : `comboBox_area`
**Base de données** : `area`

Zone de fouille de provenance.

### US

**Champ** : `comboBox_us`
**Base de données** : `us`

Unité Stratigraphique de provenance.

### Numéro Inventaire Matériau

**Champ** : `lineEdit_nr_inv_mat`
**Base de données** : `numero_inventario_materiale`

Si l'échantillon est lié à un objet inventorié, indiquer le numéro d'inventaire.

### Numéro Caisse

**Champ** : `lineEdit_nr_cassa`
**Base de données** : `nr_cassa`

Caisse ou contenant de conservation.

### Lieu de Conservation

**Champ** : `comboBox_luogo_conservazione`
**Base de données** : `luogo_conservazione`

Où est conservé l'échantillon.

**Exemples :**
- Laboratoire de fouille
- Dépôt musée
- Laboratoire d'analyses externe
- Université

---

## Workflow Opérationnel

### Création d'un Nouvel Échantillon

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouveau record**
   - Clic sur "New Record"

3. **Données identificatives**
   ```
   Site : Villa Romaine de Settefinestre
   N° Échantillon : C-2024-001
   Type échantillon : Charbon
   ```

4. **Provenance**
   ```
   Zone : 1000
   US : 150
   ```

5. **Description**
   ```
   Échantillon de charbon prélevé sur la
   surface de sol brûlé US 150.
   Quantité : environ 50 gr.
   Prélevé pour datation C14.
   ```

6. **Conservation**
   ```
   N° Caisse : Ech-1
   Lieu : Laboratoire de fouille
   ```

7. **Sauvegarde**
   - Clic sur "Save"

### Recherche d'Échantillons

1. Clic sur "New Search"
2. Remplir les critères :
   - Site
   - Type échantillon
   - US
3. Clic sur "Search"
4. Naviguer parmi les résultats

---

## Export PDF

La fiche supporte l'exportation en PDF pour :
- Liste des échantillons
- Fiches détaillées individuelles

---

## Bonnes Pratiques

### Nomenclature

- Utiliser des codes uniques et parlants
- Format conseillé : `SITE-ANNÉE-PROGRESSIF`
- Exemple : `VRS-2024-C001`

### Prélèvement

- Documenter toujours les coordonnées de prélèvement
- Photographier le point de prélèvement
- Noter la profondeur et le contexte

### Conservation

- Utiliser des contenants appropriés au type
- Étiqueter clairement chaque échantillon
- Maintenir des conditions appropriées

### Documentation

- Toujours relier à l'US de provenance
- Indiquer les analyses prévues
- Enregistrer l'envoi à des laboratoires externes

---

## Résolution des Problèmes

### Problème : Type échantillon non disponible

**Cause** : Thésaurus non configuré.

**Solution** :
1. Ouvrir la Fiche Thésaurus
2. Ajouter le type manquant pour `campioni_table`
3. Sauvegarder et rouvrir la Fiche Échantillons

### Problème : US non affichée

**Cause** : US non enregistrée pour le site sélectionné.

**Solution** :
1. Vérifier que l'US existe dans la Fiche US
2. Contrôler qu'elle appartient au même site

---

## Références

### Base de données

- **Table** : `campioni_table`
- **Classe mapper** : `CAMPIONI`
- **ID** : `id_campione`

### Fichiers Source

- **UI** : `gui/ui/Campioni.ui`
- **Contrôleur** : `tabs/Campioni.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Campsheet_pdf.py`

---

## Vidéo Tutorial

### Gestion des Échantillons
**Durée** : 5-6 minutes
- Création d'un nouvel échantillon
- Remplissage des champs
- Recherche et export

`[Placeholder vidéo : video_echantillons.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
