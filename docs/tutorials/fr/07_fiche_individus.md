# Tutorial 07 : Fiche Individus

## Introduction

La **Fiche Individus** est le module de PyArchInit dédié à la documentation anthropologique des restes humains découverts lors de la fouille. Cette fiche enregistre les informations sur le sexe, l'âge, la position du corps et l'état de conservation du squelette.

### Concepts de Base

**Individu dans PyArchInit :**
- Un individu est un ensemble de restes osseux attribuables à une seule personne
- Il est lié à la Fiche Tombe (contexte sépulcral)
- Il est lié à la Fiche Structure (structure physique)
- Il peut être lié à l'Archéozoologie pour des analyses spécifiques

**Données Anthropologiques :**
- Estimation du sexe biologique
- Estimation de l'âge au décès
- Position et orientation du corps
- État de conservation et complétude

---

## Accès à la Fiche

### Via Menu
1. Menu **PyArchInit** dans la barre de menus de QGIS
2. Sélectionner **Fiche Individus** (ou **Individual form**)

### Via Toolbar
1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Individus** (figure humaine)

---

## Aperçu de l'Interface

La fiche présente une disposition organisée en sections fonctionnelles :

### Zones Principales

| # | Zone | Description |
|---|------|-------------|
| 1 | Toolbar DBMS | Navigation, recherche, sauvegarde |
| 2 | DB Info | État record, tri, compteur |
| 3 | Champs Identificatifs | Site, Zone, US, N° Individu |
| 4 | Liaison Structure | Sigle et numéro structure |
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
| New record | Nouveau | Créer un nouvel enregistrement individu |
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
| PDF export | Export PDF | Exporter en PDF |
| Open directory | Ouvrir dossier | Ouvrir le dossier d'export |

---

## Champs Identificatifs

Les champs identificatifs définissent de manière unique l'individu dans la base de données.

### Site

**Champ** : `comboBox_sito`
**Base de données** : `sito`

Sélectionne le site archéologique d'appartenance.

### Zone

**Champ** : `comboBox_area`
**Base de données** : `area`

Zone de fouille au sein du site. Les valeurs sont remplies depuis le thésaurus.

### US

**Champ** : `comboBox_us`
**Base de données** : `us`

Unité Stratigraphique de référence.

### Numéro Individu

**Champ** : `lineEdit_individuo`
**Base de données** : `nr_individuo`

Numéro progressif de l'individu. Le prochain numéro disponible est proposé automatiquement.

**Notes :**
- La combinaison Site + Zone + US + N° Individu doit être unique
- Le numéro est attribué automatiquement à la création

### Liaison Structure

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Sigle structure | `sigla_struttura` | Sigle de la structure (ex. TM) |
| N° structure | `nr_struttura` | Numéro de la structure |

Ces champs relient l'individu à la structure funéraire.

---

## Données de Documentation

### Date Documentation

**Champ** : `dateEdit_schedatura`
**Base de données** : `data_schedatura`

Date de remplissage de la fiche.

### Documenteur

**Champ** : `comboBox_schedatore`
**Base de données** : `schedatore`

Nom de l'opérateur qui remplit la fiche.

---

## Tab Données Descriptives

Le premier tab contient les données anthropologiques fondamentales.

### Estimation du Sexe

**Champ** : `comboBox_sesso`
**Base de données** : `sesso`

Estimation du sexe biologique basée sur des caractères morphologiques.

**Valeurs :**
| Valeur | Description |
|--------|-------------|
| Masculin | Caractères masculins évidents |
| Féminin | Caractères féminins évidents |
| Masculin probable | Prédominance de caractères masculins |
| Féminin probable | Prédominance de caractères féminins |
| Indéterminé | Non déterminable |

**Critères de détermination :**
- Morphologie du bassin
- Morphologie du crâne
- Robustesse générale du squelette
- Dimensions des os

### Estimation de l'Âge au Décès

| Champ | Base de données | Description |
|-------|-----------------|-------------|
| Âge minimum | `eta_min` | Limite inférieure de l'estimation |
| Âge maximum | `eta_max` | Limite supérieure de l'estimation |

**Méthodes d'estimation :**
- Symphyse pubienne
- Surface auriculaire
- Sutures crâniennes
- Développement dentaire (pour les sub-adultes)
- Épiphyses osseuses (pour les sub-adultes)

### Classes d'Âge

**Champ** : `comboBox_classi_eta`
**Base de données** : `classi_eta`

Classification par tranches d'âge.

**Valeurs typiques :**
| Classe | Âge approximatif |
|--------|------------------|
| Infans I | 0-6 ans |
| Infans II | 7-12 ans |
| Juvenis | 13-20 ans |
| Adultus | 21-40 ans |
| Maturus | 41-60 ans |
| Senilis | >60 ans |

### Observations

**Champ** : `textEdit_osservazioni`
**Base de données** : `osservazioni`

Champ textuel pour notes anthropologiques spécifiques.

**Contenus conseillés :**
- Pathologies observées
- Traumatismes
- Marqueurs occupationnels
- Anomalies squelettiques
- Notes sur la détermination du sexe et de l'âge

---

## Tab Orientation et Position

Ce tab documente la position et l'orientation du corps.

### État de Conservation

| Champ | Base de données | Valeurs |
|-------|-----------------|---------|
| Complet | `completo_si_no` | Oui / Non |
| Perturbé | `disturbato_si_no` | Oui / Non |
| En connexion | `in_connessione_si_no` | Oui / Non |

**Définitions :**
- **Complet** : tous les segments anatomiques sont représentés
- **Perturbé** : traces de remaniement post-dépositionnel
- **En connexion** : les articulations sont préservées

### Longueur Squelette

**Champ** : `lineEdit_lunghezza`
**Base de données** : `lunghezza_scheletro`

Longueur mesurée du squelette in situ (en cm ou m).

### Position du Squelette

**Champ** : `comboBox_posizione_scheletro`
**Base de données** : `posizione_scheletro`

Position générale du corps.

**Valeurs :**
- Décubitus dorsal (sur le dos)
- Décubitus ventral (face vers le bas)
- Latéral droit
- Latéral gauche
- Replié
- Irrégulier

### Position du Crâne

**Champ** : `comboBox_posizione_cranio`
**Base de données** : `posizione_cranio`

Orientation de la tête.

**Valeurs :**
- Tourné à droite
- Tourné à gauche
- Tourné vers le haut
- Tourné vers le bas
- Non déterminable

### Position Membres Supérieurs

**Champ** : `comboBox_arti_superiori`
**Base de données** : `posizione_arti_superiori`

Position des bras.

**Valeurs :**
- Étendus le long du corps
- Sur le bassin
- Sur le thorax
- Croisés sur le thorax
- Mixtes
- Non déterminable

### Position Membres Inférieurs

**Champ** : `comboBox_arti_inferiori`
**Base de données** : `posizione_arti_inferiori`

Position des jambes.

**Valeurs :**
- Étendus
- Fléchis
- Croisés
- Écartés
- Non déterminable

### Orientation Axe

**Champ** : `comboBox_orientamento_asse`
**Base de données** : `orientamento_asse`

Orientation de l'axe longitudinal du corps.

**Valeurs :**
- N-S (tête au Nord)
- S-N (tête au Sud)
- E-W (tête à l'Est)
- W-E (tête à l'Ouest)
- NE-SW, NW-SE, etc.

### Orientation Azimut

**Champ** : `lineEdit_azimut`
**Base de données** : `orientamento_azimut`

Valeur numérique de l'azimut en degrés (0-360).

---

## Tab Restes Ostéologiques

Ce tab est dédié à la documentation des segments anatomiques.

### Documentation des Segments

Permet d'enregistrer :
- Présence/absence des éléments osseux individuels
- État de conservation par segment
- Côté (droit/gauche) pour les éléments pairs

**Segments principaux :**
| Segment | Éléments |
|---------|----------|
| Crâne | Calvaria, mandibule, dents |
| Rachis | Vertèbres cervicales, thoraciques, lombaires, sacrum |
| Thorax | Côtes, sternum |
| Membres supérieurs | Clavicules, scapulas, humérus, radius, ulna, mains |
| Bassin | Os coxaux |
| Membres inférieurs | Fémurs, tibia, péroné, pieds |

---

## Tab Autres Caractéristiques

Ce tab contient des informations supplémentaires.

### Contenus

- Caractéristiques métriques spécifiques
- Indices anthropométriques
- Pathologies détaillées
- Relations avec d'autres individus

---

## Export et Impression

### Export PDF

Le bouton PDF ouvre un panneau avec des options :

| Option | Description |
|--------|-------------|
| Liste Individus | Liste synthétique |
| Fiches Individus | Fiches complètes détaillées |
| Imprimer | Générer le PDF |

### Contenu Fiche PDF

La fiche PDF inclut :
- Données identificatives
- Données anthropologiques (sexe, âge)
- Position et orientation
- État de conservation
- Observations

---

## Workflow Opérationnel

### Création d'un Nouvel Individu

1. **Ouverture fiche**
   - Via menu ou toolbar

2. **Nouveau record**
   - Clic sur "New Record"
   - Le numéro d'individu est proposé automatiquement

3. **Données identificatives**
   ```
   Site : Nécropole d'Isola Sacra
   Zone : 1
   US : 150
   N° Individu : 1
   Sigle structure : TM
   N° structure : 45
   ```

4. **Données documentation**
   ```
   Date : 15/03/2024
   Documenteur : M. Dupont
   ```

5. **Données anthropologiques** (Tab 1)
   ```
   Sexe : Masculin
   Âge min : 35
   Âge max : 45
   Classe âge : Adultus

   Observations : Stature estimée 170 cm.
   Arthrose lombaire. Caries multiples.
   ```

6. **Orientation et Position** (Tab 2)
   ```
   Complet : Oui
   Perturbé : Non
   En connexion : Oui
   Longueur : 165 cm
   Position : Décubitus dorsal
   Crâne : Tourné à droite
   Membres supérieurs : Étendus le long du corps
   Membres inférieurs : Étendus
   Orientation : E-W
   Azimut : 90
   ```

7. **Restes ostéologiques** (Tab 3)
   - Documenter les segments présents

8. **Sauvegarde**
   - Clic sur "Save"

### Recherche d'Individus

1. Clic sur "New Search"
2. Remplir les critères :
   - Site
   - Sexe
   - Classe d'âge
   - Position
3. Clic sur "Search"
4. Naviguer parmi les résultats

---

## Relations avec d'Autres Fiches

| Fiche | Relation |
|-------|----------|
| **Fiche Site** | Le site contient les individus |
| **Fiche Structure** | La structure contient l'individu |
| **Fiche Tombe** | La tombe documente le contexte |
| **Archéozoologie** | Pour analyses ostéologiques spécifiques |

### Flux de Travail Conseillé

1. Créer la **Fiche Structure** pour la tombe
2. Créer la **Fiche Tombe**
3. Créer la **Fiche Individus** pour chaque squelette
4. Relier l'individu à la tombe et à la structure

---

## Bonnes Pratiques

### Détermination du Sexe

- Utiliser plusieurs indicateurs morphologiques
- Indiquer le degré de fiabilité
- Spécifier les critères utilisés dans les observations

### Estimation de l'Âge

- Fournir toujours une fourchette (min-max)
- Indiquer les méthodes utilisées
- Pour les sub-adultes, spécifier le développement dentaire et épiphysaire

### Position et Orientation

- Documenter avec photos avant le prélèvement
- Utiliser des références cardinales
- Mesurer l'azimut avec une boussole

### Conservation

- Distinguer pertes taphonomiques des prélèvements anciens
- Documenter les perturbations post-dépositionnelles
- Enregistrer les conditions de récupération

---

## Résolution des Problèmes

### Problème : Numéro individu dupliqué

**Cause** : Un individu avec le même numéro existe déjà.

**Solution** :
1. Vérifier la numérotation existante
2. Utiliser le numéro proposé automatiquement
3. Contrôler la zone et l'US

### Problème : Structure non trouvée

**Cause** : La structure n'existe pas ou a un sigle différent.

**Solution** :
1. Vérifier l'existence de la Fiche Structure
2. Contrôler le sigle et le numéro
3. Créer d'abord la structure si nécessaire

### Problème : Classes d'âge non disponibles

**Cause** : Thésaurus non configuré.

**Solution** :
1. Vérifier la configuration du thésaurus
2. Contrôler la langue définie
3. Contacter l'administrateur

---

## Références

### Base de données

- **Table** : `individui_table`
- **Classe mapper** : `SCHEDAIND`
- **ID** : `id_scheda_ind`

### Fichiers Source

- **UI** : `gui/ui/Schedaind.ui`
- **Contrôleur** : `tabs/Schedaind.py`
- **Export PDF** : `modules/utility/pyarchinit_exp_Individui_pdf.py`

---

## Vidéo Tutorial

### Aperçu Fiche Individus
**Durée** : 5-6 minutes
- Présentation de l'interface
- Champs principaux
- Navigation entre les tabs

`[Placeholder vidéo : video_apercu_individus.mp4]`

### Documentation Anthropologique Complète
**Durée** : 12-15 minutes
- Création d'un nouveau record
- Détermination sexe et âge
- Documentation de la position
- Enregistrement des restes ostéologiques

`[Placeholder vidéo : video_documentation_individus.mp4]`

### Liaison Tombe-Individu
**Durée** : 5-6 minutes
- Relation entre les fiches
- Flux de travail correct
- Bonnes pratiques

`[Placeholder vidéo : video_liaison_tombe_individu.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
