# Tutorial 10 : Fiche Documentation

## Introduction

La **Fiche Documentation** est le module de PyArchInit pour la gestion de la documentation graphique de fouille : plans, coupes, élévations, relevés et tout autre document graphique produit durant les activités archéologiques.

### Types de Documentation

- **Plans** : plans de couche, de phase, généraux
- **Coupes** : coupes stratigraphiques
- **Élévations** : élévations murales, fronts de fouille
- **Relevés** : relevés topographiques, photogrammétriques
- **Orthophotos** : traitements de drone/photogrammétrie
- **Dessins d'objets** : céramique, métaux, etc.

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche Documentation** (ou **Documentation form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Documentation**

---

## Aperçu de l'Interface

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | DB Info | État record, tri, compteur |
| 3 | Champs Identificatifs | Site, Nom, Date |
| 4 | Champs Typologiques | Type, Source, Échelle |
| 5 | Champs Descriptifs | Dessinateur, Notes |

---

## Toolbar DBMS

### Boutons Standard

| Fonction | Description |
|----------|-------------|
| First/Prev/Next/Last rec | Navigation entre les enregistrements |
| New record | Créer un nouvel enregistrement |
| Save | Sauvegarder les modifications |
| Delete | Supprimer l'enregistrement |
| New search / Search | Fonctions de recherche |
| Order by | Trier les résultats |
| View all | Afficher tous les enregistrements |

---

## Champs de la Fiche

### Site

**Champ** : `comboBox_sito_doc`
**Base de données** : `sito`

Site archéologique de référence.

### Nom Documentation

**Champ** : `lineEdit_nome_doc`
**Base de données** : `nome_doc`

Nom identificatif du document.

**Conventions de nomenclature :**
- `P` = Plan (ex. P001)
- `C` = Coupe (ex. C001)
- `E` = Élévation (ex. E001)
- `R` = Relevé (ex. R001)

### Date

**Champ** : `dateEdit_data`
**Base de données** : `data`

Date d'exécution du dessin/relevé.

### Type Documentation

**Champ** : `comboBox_tipo_doc`
**Base de données** : `tipo_documentazione`

Typologie du document.

**Valeurs typiques :**
| Type | Description |
|------|-------------|
| Plan de couche | US unique |
| Plan de phase | Plusieurs US contemporaines |
| Plan général | Vue d'ensemble |
| Coupe stratigraphique | Profil vertical |
| Élévation | Parement mural |
| Relevé topographique | Planimétrie générale |
| Orthophoto | De photogrammétrie |
| Dessin d'objet | Céramique, métal, etc. |

### Source

**Champ** : `comboBox_sorgente`
**Base de données** : `sorgente`

Source/méthode de production.

**Valeurs :**
- Relevé direct
- Photogrammétrie
- Scanner laser
- GPS/Station totale
- Digitalisation CAO
- Orthophoto drone

### Échelle

**Champ** : `comboBox_scala`
**Base de données** : `scala`

Échelle de représentation.

**Échelles courantes :**
| Échelle | Usage typique |
|---------|---------------|
| 1:1 | Dessins d'objets |
| 1:5 | Détails |
| 1:10 | Coupes, détails |
| 1:20 | Plans de couche |
| 1:50 | Plans généraux |
| 1:100 | Planimétries |
| 1:200+ | Cartes topographiques |

### Dessinateur

**Champ** : `comboBox_disegnatore`
**Base de données** : `disegnatore`

Auteur du dessin/relevé.

### Notes

**Champ** : `textEdit_note`
**Base de données** : `note`

Notes supplémentaires sur le document.

---

## Workflow Opérationnel

### Enregistrement d'une Nouvelle Documentation

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouveau record**
   - Clic sur "New Record"

3. **Données identificatives**
   ```
   Site : Villa Romaine de Settefinestre
   Nom : P025
   Date : 15/06/2024
   ```

4. **Classification**
   ```
   Type : Plan de couche
   Source : Relevé direct
   Échelle : 1:20
   ```

5. **Auteur et notes**
   ```
   Dessinateur : M. Dupont
   Notes : Plan US 150. Met en évidence
   les limites du sol damé.
   ```

6. **Sauvegarde**
   - Clic sur "Save"

### Recherche de Documentation

1. Clic sur "New Search"
2. Remplir les critères :
   - Site
   - Type documentation
   - Échelle
   - Dessinateur
3. Clic sur "Search"
4. Naviguer parmi les résultats

---

## Export PDF

La fiche supporte l'exportation en PDF pour :
- Liste de documentation
- Fiches détaillées

---

## Bonnes Pratiques

### Nomenclature

- Utiliser des codes cohérents dans tout le projet
- Numérotation progressive par type
- Documenter les conventions adoptées

### Organisation

- Toujours relier au site de référence
- Indiquer l'échelle effective
- Enregistrer date et auteur

### Archivage

- Relier les fichiers numériques via la gestion des médias
- Maintenir des copies de sauvegarde
- Utiliser des formats standard (PDF, TIFF)

---

## Résolution des Problèmes

### Problème : Type documentation non disponible

**Cause** : Thésaurus non configuré.

**Solution** :
1. Ouvrir la Fiche Thésaurus
2. Ajouter les types manquants pour `documentazione_table`

### Problème : Fichier non affiché

**Cause** : Chemin incorrect ou fichier manquant.

**Solution** :
1. Vérifier que le fichier existe
2. Contrôler le chemin dans la configuration médias

---

## Références

### Base de données

- **Table** : `documentazione_table`
- **Classe mapper** : `DOCUMENTAZIONE`
- **ID** : `id_documentazione`

### Fichiers Source

- **UI** : `gui/ui/Documentazione.ui`
- **Contrôleur** : `tabs/Documentazione.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Documentazionesheet_pdf.py`

---

## Vidéo Tutorial

### Gestion Documentation Graphique
**Durée** : 6-8 minutes
- Enregistrement d'une nouvelle documentation
- Classification et métadonnées
- Recherche et consultation

`[Placeholder vidéo : video_documentation.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
