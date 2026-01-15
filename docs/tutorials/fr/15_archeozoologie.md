# Tutorial 15 : Fiche Archéozoologie (Faune)

## Introduction

La **Fiche Archéozoologie/Faune** (FICHE FR - Fauna Record) est le module de PyArchInit dédié à l'analyse et à la documentation des restes faunistiques. Elle permet d'enregistrer des données archéozoologiques détaillées pour l'étude des économies de subsistance anciennes.

### Concepts de Base

**Archéozoologie :**
- Étude des restes animaux provenant de contextes archéologiques
- Analyse des relations homme-animal dans le passé
- Reconstitution des régimes alimentaires, de l'élevage, de la chasse

**Données enregistrées :**
- Identification taxinomique (espèce)
- Parties squelettiques présentes
- NMI (Nombre Minimum d'Individus)
- État de conservation
- Traces taphonomiques
- Marques de boucherie

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche Faune** (ou **Fauna form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Faune** (os stylisé)

---

## Aperçu de l'Interface

La fiche est organisée en onglets thématiques :

### Onglets Principaux

| # | Onglet | Contenu |
|---|--------|---------|
| 1 | Données Identificatives | Site, Zone, US, Contexte |
| 2 | Données Archéozoologiques | Espèce, NMI, Parties squelettiques |
| 3 | Données Taphonomiques | Conservation, Fragmentation, Traces |
| 4 | Données Contextuelles | Contexte de dépôt, Associations |
| 5 | Statistiques | Graphiques et quantifications |

---

## Toolbar

La toolbar fournit les fonctions standard :

| Icône | Fonction |
|-------|----------|
| First/Prev/Next/Last | Navigation enregistrements |
| New | Nouvel enregistrement |
| Save | Sauvegarder |
| Delete | Supprimer |
| Search | Rechercher |
| View All | Afficher tous |
| PDF | Export PDF |

---

## Onglet Données Identificatives

### Sélection US

**Champ** : `comboBox_us_select`

Sélectionne l'US de provenance. Affiche les US disponibles au format "Site - Zone - US".

### Site

**Champ** : `comboBox_sito`
**Base de données** : `sito`

Site archéologique.

### Zone

**Champ** : `comboBox_area`
**Base de données** : `area`

Zone de fouille.

### Sondage

**Champ** : `comboBox_saggio`
**Base de données** : `saggio`

Sondage/tranchée de provenance.

### US

**Champ** : `comboBox_us`
**Base de données** : `us`

Unité Stratigraphique.

### Datation US

**Champ** : `lineEdit_datazione`
**Base de données** : `datazione_us`

Cadre chronologique de l'US.

### Responsable

**Champ** : `comboBox_responsabile`
**Base de données** : `responsabile_scheda`

Auteur de l'enregistrement.

### Date de Rédaction

**Champ** : `dateEdit_data`
**Base de données** : `data_compilazione`

Date de rédaction de la fiche.

---

## Onglet Données Archéozoologiques

### Contexte

**Champ** : `comboBox_contesto`
**Base de données** : `contesto`

Type de contexte de dépôt.

**Valeurs :**
- Habitat
- Rejet/Dépotoir
- Comblement
- Couche de vie
- Sépulture
- Rituel

### Espèce

**Champ** : `comboBox_specie`
**Base de données** : `specie`

Identification taxinomique.

**Espèces courantes en archéozoologie :**
| Espèce | Nom scientifique |
|--------|------------------|
| Bovin | Bos taurus |
| Ovin | Ovis aries |
| Caprin | Capra hircus |
| Porcin | Sus domesticus |
| Équidé | Equus caballus |
| Cerf | Cervus elaphus |
| Sanglier | Sus scrofa |
| Lièvre | Lepus europaeus |
| Chien | Canis familiaris |
| Chat | Felis catus |
| Volaille | Gallus gallus |

### Nombre Minimum d'Individus (NMI)

**Champ** : `spinBox_nmi`
**Base de données** : `numero_minimo_individui`

Estimation du nombre minimum d'individus représentés.

### Parties Squelettiques

**Champ** : `tableWidget_parti`
**Base de données** : `parti_scheletriche`

Tableau pour enregistrer les parties anatomiques présentes.

**Colonnes :**
| Colonne | Description |
|---------|-------------|
| Élément | Os/partie anatomique |
| Côté | Dx/Gx/Axial |
| Quantité | Nombre de fragments |
| NMI | Contribution au NMI |

### Mesures des Os

**Champ** : `tableWidget_misure`
**Base de données** : `misure_ossa`

Mesures ostéométriques standard.

---

## Onglet Données Taphonomiques

### État de Fragmentation

**Champ** : `comboBox_frammentazione`
**Base de données** : `stato_frammentazione`

Degré de fragmentation des restes.

**Valeurs :**
- Complet
- Peu fragmenté
- Fragmenté
- Très fragmenté

### État de Conservation

**Champ** : `comboBox_conservazione`
**Base de données** : `stato_conservazione`

Conditions générales de conservation.

**Valeurs :**
- Excellent
- Bon
- Moyen
- Mauvais
- Très mauvais

### Traces de Combustion

**Champ** : `comboBox_combustione`
**Base de données** : `tracce_combustione`

Présence de traces de feu.

**Valeurs :**
- Absentes
- Noircissement
- Carbonisation
- Calcination

### Signes Taphonomiques

**Champ** : `comboBox_segni_tafo`
**Base de données** : `segni_tafonomici_evidenti`

Traces d'altération post-dépositionnelle.

**Types :**
- Weathering (agents atmosphériques)
- Root marks (racines)
- Gnawing (rongements)
- Trampling (piétinement)

### Altérations Morphologiques

**Champ** : `textEdit_alterazioni`
**Base de données** : `alterazioni_morfologiche`

Description détaillée des altérations observées.

---

## Onglet Données Contextuelles

### Méthodologie de Récupération

**Champ** : `comboBox_metodologia`
**Base de données** : `metodologia_recupero`

Méthode de collecte des restes.

**Valeurs :**
- À vue
- Tamisage à sec
- Flottation
- Tamisage à l'eau

### Restes en Connexion Anatomique

**Champ** : `checkBox_connessione`
**Base de données** : `resti_connessione_anatomica`

Présence de parties en connexion.

### Classes d'Objets Associés

**Champ** : `textEdit_associazioni`
**Base de données** : `classi_reperti_associazione`

Autres matériaux associés aux restes faunistiques.

### Observations

**Champ** : `textEdit_osservazioni`
**Base de données** : `osservazioni`

Notes générales.

### Interprétation

**Champ** : `textEdit_interpretazione`
**Base de données** : `interpretazione`

Interprétation du contexte faunistique.

---

## Onglet Statistiques

Fournit des outils pour :
- Graphiques de distribution par espèce
- Calcul des NMI totaux
- Comparaisons entre US/phases
- Export des données statistiques

---

## Workflow Opérationnel

### Enregistrement des Restes Faunistiques

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouvel enregistrement**
   - Cliquer sur "New Record"

3. **Données identificatives**
   ```
   Site : Villa Romaine
   Zone : 1000
   US : 150
   Responsable : G. Dupont
   Date : 20/07/2024
   ```

4. **Données archéozoologiques** (Onglet 2)
   ```
   Contexte : Rejet/Dépotoir
   Espèce : Bos taurus
   NMI : 3

   Parties squelettiques :
   - Humérus / Dx / 2 / 1
   - Tibia / Gx / 3 / 2
   - Métapode / - / 5 / 1
   ```

5. **Données taphonomiques** (Onglet 3)
   ```
   Fragmentation : Fragmenté
   Conservation : Bon
   Combustion : Absentes
   Signes taphonomiques : Root marks
   ```

6. **Interprétation**
   ```
   Rejet de déchets alimentaires.
   Présence de traces de boucherie
   sur quelques os longs.
   ```

7. **Sauvegarde**
   - Cliquer sur "Save"

---

## Bonnes Pratiques

### Identification

- Utiliser des collections de référence
- Indiquer le degré de certitude de l'identification
- Enregistrer également les restes non identifiables

### NMI

- Calculer pour chaque espèce séparément
- Considérer le côté et l'âge des restes
- Documenter la méthode de calcul

### Taphonomie

- Observer systématiquement chaque reste
- Documenter les traces avant le lavage
- Photographier les cas significatifs

### Contexte

- Toujours relier à l'US de provenance
- Enregistrer la méthode de récupération
- Noter les associations significatives

---

## Export PDF

La fiche permet de générer :
- Fiches détaillées individuelles
- Listes par US ou phase
- Rapports statistiques

---

## Résolution des Problèmes

### Problème : Espèce non disponible

**Cause** : Liste des espèces incomplète.

**Solution** :
1. Vérifier le thésaurus faune
2. Ajouter les espèces manquantes
3. Contacter l'administrateur

### Problème : NMI non calculé

**Cause** : Parties squelettiques non enregistrées.

**Solution** :
1. Remplir le tableau des parties squelettiques
2. Indiquer le côté et la quantité
3. Le système calculera automatiquement

---

## Références

### Base de données

- **Table** : `fauna_table`
- **Classe mapper** : `FAUNA`
- **ID** : `id_fauna`

### Fichiers Source

- **Contrôleur** : `tabs/Fauna.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Faunasheet_pdf.py`

---

## Vidéo Tutorial

### Enregistrement Archéozoologique
**Durée** : 12-15 minutes
- Identification taxinomique
- Enregistrement des parties squelettiques
- Analyse taphonomique

`[Placeholder vidéo : video_archeozoologie.mp4]`

### Statistiques Faunistiques
**Durée** : 8-10 minutes
- Calcul NMI
- Graphiques de distribution
- Export des données

`[Placeholder vidéo : video_faune_statistiques.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
