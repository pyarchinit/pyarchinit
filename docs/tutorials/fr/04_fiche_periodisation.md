# Tutorial 04 : Fiche Périodisation

## Introduction

La **Fiche Périodisation** est un outil fondamental pour la gestion des phases chronologiques d'une fouille archéologique. Elle permet de définir les périodes et les phases qui caractérisent la séquence stratigraphique du site, en associant à chaque couple période/phase une datation chronologique et une description.

### Objectif de la Fiche

- Définir la séquence chronologique de la fouille
- Associer périodes et phases aux unités stratigraphiques
- Gérer la chronologie absolue (années) et relative (périodes historiques)
- Visualiser les US par période/phase sur la carte GIS
- Générer des rapports PDF de la périodisation

### Relation avec d'autres Fiches

La Fiche Périodisation est étroitement liée à :
- **Fiche US/USM** : Chaque US est assignée à une période et une phase
- **Fiche Site** : Les périodes sont spécifiques à chaque site
- **Matrice de Harris** : Les périodes colorent la Matrice par phase chronologique

---

## Accès à la Fiche

### Depuis le Menu

1. Ouvrir QGIS avec le plugin PyArchInit actif
2. Menu **PyArchInit** → **Archaeological record management** → **Excavation - Loss of use calculation** → **Period and Phase**

### Depuis la Toolbar

1. Repérer la toolbar PyArchInit
2. Cliquer sur l'icône **Périodisation**

---

## Interface Utilisateur

### Zones Principales

| Zone | Description |
|------|-------------|
| **1. DBMS Toolbar** | Barre d'outils pour navigation et gestion |
| **2. Indicateurs État** | DB Info, Status, Tri |
| **3. Données Identificatives** | Site, Période, Phase, Code période |
| **4. Données Descriptives** | Description textuelle de la période |
| **5. Chronologie** | Années initiale et finale |
| **6. Datation Étendue** | Sélection depuis vocabulaire époques historiques |

---

## Concepts Fondamentaux

### Période et Phase

Le système de périodisation dans PyArchInit est basé sur une structure hiérarchique à deux niveaux :

#### Période
La **Période** représente une macro-phase chronologique de la fouille. Elle est identifiée par un nombre entier (1, 2, 3, ...) et représente les grandes subdivisions de la séquence stratigraphique.

Exemples de périodes :
- Période 1 : Époque contemporaine
- Période 2 : Époque médiévale
- Période 3 : Époque romaine impériale
- Période 4 : Époque romaine républicaine

#### Phase
La **Phase** représente une subdivision interne de la période. Elle est également identifiée par un nombre entier et permet de détailler davantage la séquence.

Exemples de phases dans la Période 3 (Époque romaine impériale) :
- Phase 1 : IIIe-IVe siècle apr. J.-C.
- Phase 2 : IIe siècle apr. J.-C.
- Phase 3 : Ier siècle apr. J.-C.

### Code Période

Le **Code Période** est un identifiant numérique unique qui relie le couple période/phase aux US. Lorsqu'on assigne une période/phase à une US dans la Fiche US, c'est ce code qui est utilisé.

> **Important** : Le code période doit être unique pour chaque combinaison site/période/phase.

### Schéma Conceptuel

```
Site
└── Période 1 (Époque contemporaine)
│   ├── Phase 1 → Code 101
│   └── Phase 2 → Code 102
├── Période 2 (Époque médiévale)
│   ├── Phase 1 → Code 201
│   ├── Phase 2 → Code 202
│   └── Phase 3 → Code 203
└── Période 3 (Époque romaine)
    ├── Phase 1 → Code 301
    └── Phase 2 → Code 302
```

---

## Champs de la Fiche

### Champs Identificatifs

#### Site
- **Type** : ComboBox
- **Obligatoire** : Oui
- **Description** : Sélectionne le site archéologique

#### Période
- **Type** : ComboBox éditable
- **Obligatoire** : Oui
- **Valeurs** : Entiers de 1 à 15 (prédéfinis) ou valeurs personnalisées
- **Note** : Les nombres bas indiquent des périodes plus récentes

#### Phase
- **Type** : ComboBox éditable
- **Obligatoire** : Oui
- **Valeurs** : Entiers de 1 à 15 (prédéfinis) ou valeurs personnalisées

#### Code Période
- **Type** : LineEdit (texte)
- **Obligatoire** : Non (mais fortement conseillé)
- **Suggestion** : Utiliser une convention comme `[période][phase]` (ex. 101, 102, 201)

### Champs Descriptifs

#### Description
- **Type** : TextEdit (multiligne)
- **Obligatoire** : Non
- **Contenu suggéré** :
  - Caractéristiques générales de la période
  - Événements historiques corrélés
  - Typologies de structures/matériaux attendus
  - Références bibliographiques

### Champs Chronologiques

#### Chronologie Initiale
- **Type** : LineEdit (numérique)
- **Format** : Année numérique
- **Notes** :
  - Valeurs positives = apr. J.-C.
  - Valeurs négatives = av. J.-C.
  - Exemple : `-100` pour 100 av. J.-C., `200` pour 200 apr. J.-C.

#### Chronologie Finale
- **Type** : LineEdit (numérique)
- **Format** : Même convention que Chronologie Initiale

#### Datation Étendue (Époques Historiques)
- **Type** : ComboBox éditable avec vocabulaire préchargé
- **Description** : Sélection depuis un vocabulaire d'époques historiques prédéfinies
- **Fonctionnalité automatique** : En sélectionnant une époque, les champs Chronologie Initiale et Finale se remplissent automatiquement

### Vocabulaire Époques Historiques

| Catégorie | Exemples |
|-----------|----------|
| **Époque Contemporaine** | XXIe siècle, XXe siècle |
| **Époque Moderne** | XIXe-XVIe siècle |
| **Époque Médiévale** | XVe-VIIIe siècle |
| **Époque Antique** | VIIe-Ier siècle |
| **Empire Romain** | Périodes spécifiques (Julio-Claudien, Flavien, etc.) |
| **Préhistoire** | Paléolithique, Mésolithique, Néolithique, Âge du Bronze, Âge du Fer |

---

## Fonctionnalités GIS

La Fiche Périodisation offre des fonctionnalités de visualisation GIS pour voir les US associées à chaque période/phase.

### Boutons GIS

#### Visualiser Période Unique
- **Fonction** : Charge sur la carte QGIS toutes les US associées à la période/phase actuelle
- **Prérequis** : Le champ Code Période doit être rempli

#### Visualiser Toutes les Périodes - US
- **Fonction** : Charge sur la carte toutes les périodes comme couches séparées (uniquement US)
- **Résultat** : Une couche par combinaison période/phase

#### Visualiser Toutes les Périodes - USM
- **Fonction** : Charge sur la carte toutes les périodes comme couches séparées (uniquement USM)

---

## Export PDF

### Export Fiche Unique
- Génère un PDF avec les données de la période/phase actuelle
- Contenu : Informations identificatives, chronologie, description

### Export Liste Périodisation
- Génère un PDF avec la liste de toutes les périodes/phases du site
- Contenu : Tableau récapitulatif

---

## Intégration IA

La Fiche Périodisation inclut une intégration avec GPT pour obtenir des suggestions automatiques sur la description des périodes historiques.

### Fonctionnement

1. Sélectionner une époque historique depuis **Datation Étendue**
2. Cliquer sur le bouton **Suggestions**
3. Sélectionner le modèle GPT à utiliser (gpt-4o ou gpt-4)
4. Le système génère automatiquement :
   - Une description de la période historique
   - 3 liens Wikipédia pertinents
5. Le texte généré peut être inséré dans le champ Description

### Configuration API Key

Pour utiliser cette fonctionnalité :
1. Obtenir une API Key depuis OpenAI
2. Au premier usage, le système demande d'insérer la clé
3. La clé est sauvegardée dans `PYARCHINIT_HOME/bin/gpt_api_key.txt`

---

## Workflow Opérationnel

### Création d'une Nouvelle Périodisation

1. **Accéder à la Fiche** depuis le menu ou la toolbar
2. **Nouveau Record** - cliquer sur New record
3. **Sélection Site** - si non préconfiguré, sélectionner le site
4. **Définition Période et Phase** - entrer les numéros et le code
5. **Chronologie** - sélectionner la datation étendue ou entrer manuellement
6. **Description** - remplir ou utiliser les suggestions IA
7. **Sauvegarde** - cliquer sur Save

### Schéma de Périodisation Conseillé

| Période | Phase | Code | Description |
|---------|-------|------|-------------|
| 1 | 1 | 101 | Époque contemporaine - Labour |
| 1 | 2 | 102 | Époque contemporaine - Abandon |
| 2 | 1 | 201 | Époque médiévale - Phase tardive |
| 2 | 2 | 202 | Époque médiévale - Phase centrale |
| 3 | 1 | 301 | Époque romaine - Phase impériale |
| 3 | 2 | 302 | Époque romaine - Phase républicaine |

---

## Bonnes Pratiques

### Conventions de Numérotation

1. **Périodes** : Numéroter du plus récent (1) au plus ancien
2. **Phases** : Numéroter du plus récent (1) au plus ancien à l'intérieur de la période
3. **Codes** : Utiliser la formule `[période * 100 + phase]` pour des codes uniques

### Descriptions Efficaces

Une bonne description de période devrait inclure :
- Cadrage chronologique
- Caractéristiques principales de la période
- Types de structures/matériaux attendus
- Comparaisons avec d'autres sites contemporains
- Références bibliographiques

### Liaison avec les US

Après avoir créé la périodisation :
1. Ouvrir la Fiche US
2. Dans l'onglet **Périodisation**, assigner Période initiale/finale et Phase initiale/finale
3. Le système associera automatiquement l'US à la périodisation

---

## Résolution des Problèmes

### "Period code not add"
- **Cause** : Le champ Code Période est vide
- **Solution** : Remplir le champ Code Période avant d'utiliser les fonctions GIS

### Chronologie ne se remplit pas automatiquement
- **Cause** : L'époque sélectionnée n'a pas de données associées
- **Solution** : Vérifier que l'époque est présente dans le fichier CSV des époques

### Erreur de sauvegarde : enregistrement dupliqué
- **Cause** : Un enregistrement avec la même combinaison Site/Période/Phase existe déjà
- **Solution** : Vérifier les valeurs et utiliser une combinaison unique

---

## Résumé des Champs

| Champ | Type | Obligatoire | Base de données |
|-------|------|-------------|-----------------|
| Site | ComboBox | Oui | sito |
| Période | ComboBox | Oui | periodo |
| Phase | ComboBox | Oui | fase |
| Code Période | LineEdit | Non | cont_per |
| Description | TextEdit | Non | descrizione |
| Chronologie Initiale | LineEdit | Non | cron_iniziale |
| Chronologie Finale | LineEdit | Non | cron_finale |
| Datation Étendue | ComboBox | Non | datazione_estesa |

---

## Vidéo Tutorial

### Périodisation Complète
`[Placeholder : video_periodisation.mp4]`

**Contenus** :
- Création de périodisation
- Conventions de numérotation
- Utilisation du vocabulaire époques
- Visualisation GIS

**Durée prévue** : 10-12 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
