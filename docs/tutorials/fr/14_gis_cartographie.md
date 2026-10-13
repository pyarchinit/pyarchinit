# Tutorial 14 : SIG et Cartographie

## Introduction

PyArchInit est profondément intégré avec **QGIS**, exploitant toutes ses fonctionnalités SIG pour la gestion spatiale des données archéologiques. Ce tutoriel couvre l'intégration cartographique, les couches prédéfinies et les fonctionnalités avancées comme la **segmentation automatique SAM**.

### Fonctionnalités SIG Principales

- Visualisation des US sur carte
- Couches vectorielles prédéfinies
- Styling QML personnalisé
- Cotes et mesures SIG
- Segmentation automatique (SAM)
- Export cartographique

## Couches Prédéfinies PyArchInit

### Couches Vectorielles Principales

| Couche | Géométrie | Description |
|--------|-----------|-------------|
| `pyunitastratigrafiche` | MultiPolygon | US dépôt |
| `pyunitastratigrafiche_usm` | MultiPolygon | US muraires |
| `pyarchinit_quote` | Point | Points de cote |
| `pyarchinit_siti` | Point | Localisation des sites |
| `pyarchinit_ripartizioni_spaziali` | Polygon | Zones de fouille |
| `pyarchinit_strutture_ipotesi` | Polygon | Structures hypothétiques |
| `pyarchinit_documentazione` | Point | Références documentation |

### Attributs Couche US

| Champ | Type | Description |
|-------|------|-------------|
| `gid` | Integer | ID unique |
| `scavo_s` | Text | Nom du site |
| `area_s` | Text | Numéro de zone |
| `us_s` | Text | Numéro US |
| `stratigraph_index_us` | Integer | Index stratigraphique |
| `tipo_us_s` | Text | Type US |
| `rilievo_originale` | Text | Relevé d'origine |
| `disegnatore` | Text | Auteur du relevé |
| `data` | Date | Date du relevé |

## Visualisation des US sur Carte

### Depuis le Tab "Map" de la Fiche US

1. Ouvrir une fiche US
2. Sélectionner le tab **Map**
3. Fonctions disponibles :

| Bouton | Fonction |
|--------|----------|
| View US | Visualiser l'US courante sur la carte |
| View All | Visualiser toutes les US de la zone |
| New Record | Créer une nouvelle géométrie |
| Pan to | Centrer la carte sur l'US |

### Visualisation depuis Recherche

1. Exécuter une recherche US
2. Bouton **"View Record"** → visualise unique
3. Bouton **"View All"** → visualise tous les résultats

### Choix du Style (US et USM)

Lorsque les US ou les US muraires (USM) des résultats de recherche sont chargées sur la carte, la fenêtre **Style Choice** apparaît ("How do you want to manage the layer style?"). Les boutons sont affichés en anglais :

| Bouton | Effet |
|--------|-------|
| **Save new style** | Crée le style à partir du champ choisi et l'enregistre dans la base de données sous un nom |
| **Load existing style** | Utilise comme modèle un style déjà prêt, choisi dans une liste (voir ci-dessous), et crée le style à partir du champ choisi sans l'enregistrer dans la base de données |
| **Use temporary style** | Crée le style à partir du champ choisi sans l'enregistrer dans la base de données |
| **Single symbol (outline only)** | Dessine uniquement le contour des géométries, sans remplissage |

Depuis la 5.13.19-alpha, **Load existing style** ouvre la fenêtre **Existing style** ("Choose the style to use as a template:", en anglais) avec la liste des styles disponibles : les styles enregistrés dans la base de données (*Database: nom*), les styles QML fournis avec pyArchInit (`us_*.qml`, listés comme *pyArchInit: …*) et **Other QML file…**, pour choisir n'importe quel fichier `.qml`. Le style choisi est chargé sur la couche (la transparence et le mode de fusion viennent avec lui, les étiquettes non : sur les vues US et USM de polygones, ce sont, depuis la 5.13.110-alpha, celles du paragraphe **Étiquettes** plus bas, le numéro de l'unité cerclé, quoi que dise le style modèle) et sert de **modèle** : après le choix du champ de catégorisation, les valeurs que le style possède déjà gardent sa couleur et son symbole, les autres reçoivent une copie de son symbole avec leur propre couleur. Si l'on annule le choix, cela fonctionne comme **Use temporary style**. Auparavant, il cherchait uniquement parmi les styles de la base de données et, n'en trouvant aucun, passait directement à la fenêtre de catégorisation.

Avec **Save new style**, **Load existing style** et **Use temporary style**, on choisit ensuite le champ de catégorisation (fenêtre **Sélectionner le Champ de Catégorisation**) : **Définition Stratigraphique**, **Type US**, **Définition Interprétative** ou **Période/Phase (cont_per)** (depuis la 5.13.19-alpha) ; chaque valeur du champ reçoit sa propre couleur, qui depuis la 5.13.19-alpha reste la même à chaque chargement de la couche. Avec **Période/Phase (cont_per)**, l'entrée de légende de chaque code affiche aussi la datation de la période/phase tirée de la périodisation. Seuls les champs présents dans la couche sont proposés.

**Ordre de dessin.** Depuis la 5.13.19-alpha, les unités sont dessinées dans l'ordre utilisé par le Time Manager : d'abord celles sans période, puis selon la chronologie de la période (d'après la périodisation de la période/phase initiale de l'US, ou d'après `cont_per`), puis selon `order_layer` (0 = la plus ancienne) et enfin le creusement au-dessus de son remplissage ; ainsi les unités les plus récentes sont au-dessus. Cela vaut pour toutes les options de style, y compris **Single symbol (outline only)**. Lorsque les couches sont chargées période par période, le style n'est demandé qu'une seule fois et utilisé pour toutes les périodes.

**Étiquettes.** Depuis la 5.13.110-alpha, avec le style choisi la vue US (et USM) reçoit aussi ses **étiquettes** : le numéro de l'unité en **gras dans un cercle blanc à bordure rouge sombre**, **une par unité**, sur son plus grand dessin s'il est visible (non entièrement recouvert par un dessin de niveau supérieur), avec la même recette que les planches de l'atlas du Time Manager (tutoriel 25). Quand deux numéros se chevaucheraient, l'un est déplacé et une ligne de rappel le relie à son dessin. Cela vaut pour les US et les USM, avec SQLite et avec PostgreSQL, et pour toutes les options de style, y compris **Single symbol (outline only)** ; si le style chargé avec **Load existing style** avait déjà des étiquettes, le numéro cerclé prend leur place. Les couches de points, comme les cotes, ne reçoivent pas d'étiquettes d'ici.

Depuis la 5.13.18-alpha, le style choisi (et le champ de catégorisation) est respecté aussi avec les bases de données SQLite, pour les US comme pour les USM ; auparavant la carte s'affichait toujours avec une couleur par US.

## Styling des Couches

### Fichiers QML

PyArchInit inclut des styles prédéfinis au format QML :
```
pyarchinit/styles/
├── pyunitastratigrafiche.qml
├── pyunitastratigrafiche_usm.qml
├── pyarchinit_quote.qml
└── ...
```

### Application du Style

1. Sélectionner la couche dans la légende
2. Clic droit → **Propriétés**
3. Tab **Style**
4. **Charger style** → sélectionner le QML

### Personnalisation

Les styles peuvent être personnalisés pour :
- Couleurs selon le type d'US
- Étiquettes avec numéro US
- Transparence
- Bordures et remplissages

## Cotes et Mesures

### Couche Cotes

La couche `pyarchinit_quote` mémorise :
- Coordonnées X, Y
- Cote Z (absolue)
- Type de point de cote
- US de référence
- Zone de référence

### Calcul Automatique des Cotes

Depuis la Fiche US, les cotes min/max sont calculées :
1. Requête aux points de cote associés à l'US
2. Extraction des valeurs minimum et maximum
3. Affichage dans le rapport

### Insertion des Cotes

1. Couche cotes en édition
2. Dessiner un point sur la carte
3. Remplir les attributs :
   - `sito_q`
   - `area_q`
   - `us_q`
   - `quota`
   - `unita_misura_q`

## Segmentation Automatique SAM

### Qu'est-ce que SAM ?

**SAM (Segment Anything Model)** est le modèle d'intelligence artificielle de Meta qui découpe une image en ses objets. Dans pyArchInit, la fenêtre SAM transforme une image en **polygones**, à partir :

- d'une **orthophoto** (un fichier raster : GeoTIFF, JPEG géoréférencé…) ;
- ou d'une **couche de tuiles ou d'un service** chargé dans QGIS : XYZ comme ESRI World Imagery ou Google, WMS, ArcGIS REST.

Pas seulement des pierres : aussi des **bâtiments, routes, champs, rivières, murs**. Les modèles forment deux familles :

- **SAM 2.1** (Meta) trouve les contours des objets — tous, ou ceux que vous indiquez par des points, un rectangle ou un polygone — mais ne dit pas ce qu'ils sont ;
- les **classes textuelles** (YOLOE-26 en local, SAM 3 dans le cloud) cherchent ce que vous écrivez (« building, road, river, field ») et chaque polygone porte son étiquette.

Les polygones vont dans la couche de votre choix : les couches US de pyArchInit, n'importe quelle couche de polygones du projet ou une nouvelle couche temporaire.

### Accès à la Fonction

1. Depuis la barre d'outils pyArchInit : bouton déroulant **Outils d'analyse** (Analysis Tools) → « SAM - Segmentation (stones, buildings, roads, fields…) ». C'est l'action par défaut du bouton : un clic sur l'icône ouvre directement la fenêtre.
2. Ou depuis le menu **pyArchInit** → « SAM - Segmentation (stones, buildings, roads, fields…) ».

La fenêtre s'intitule « SAM — Segmentation (stones, buildings, roads, fields, rivers…) ». Ses libellés n'existent qu'en italien et en anglais : avec QGIS en français, elle s'affiche en anglais, comme dans le schéma. Dans la suite, chaque libellé traduit est suivi du libellé anglais entre parenthèses.

### Interface SAM

```
┌────────────────────────────────────────────────────────────────────┐
│ SAM — Segmentation (stones, buildings, roads, fields, rivers…)     │
├────────────────────────────────────────────────────────────────────┤
│ Automatic segmentation — from an orthophoto or a tile layer        │
│ (ESRI, Google, WMS) to polygons, with SAM 2.1 (Meta) or with text  │
│ classes.                                                           │
├─ Local environment ────────────────────────────────────────────────┤
│ ready — ultralytics 8.4.x, torch 2.x, mps                          │
│                                     [Install / update]  [Show log] │
├─ Image ────────────────────────────────────────────────────────────┤
│ Raster layer: [orthophoto.tif                                 v]   │
│               orthophoto.tif — 12000 × 9000 px                     │
│ Area:         (o) current view   ( ) whole raster                  │
│ Resolution (map units/px): [0.100000]                              │
│ Max side (px):             [2048]                                  │
├─ What to segment ──────────────────────────────────────────────────┤
│ (o) Everything (automatic)                                         │
│ ( ) Points: click the objects on the map                           │
│ ( ) Box: draw a rectangle                                          │
│ ( ) Polygon: draw the area                                         │
│ ( ) Polygon from layer: [polygon layer                        v]   │
│ ( ) Text classes:       [building, road, river, field          ]   │
│ Threshold: [0.30]                                                  │
├─ Model ────────────────────────────────────────────────────────────┤
│ Model: [Locale: SAM 2.1 Tiny — ~78 MB                         v]   │
│        weights present ✓                      [Download weights]   │
│ API key: [••••••••]                                Replicate key   │
├─ Target ───────────────────────────────────────────────────────────┤
│ Layer: [pyunitastratigrafiche                                 v]   │
│ Site: [Excavation 2026]           Area: [1]                        │
│ Stratigraphic index: [1]          US type: [pietra            v]   │
│ Field for the label: [label                                   v]   │
├────────────────────────────────────────────────────────────────────┤
│ Ready                                                              │
│                                         [Start]  [Cancel]  [Close] │
└────────────────────────────────────────────────────────────────────┘
```

Cinq groupes, à remplir de haut en bas : « Environnement local » (*Local environment*), « Image » (*Image*), « Que segmenter » (*What to segment*), « Modèle » (*Model*), « Destination » (*Target*). En dessous se trouvent la ligne d'état (« Prêt », *Ready*), où défilent aussi les messages du travail en cours, et les boutons « Démarrer » (*Start*), « Annuler » (*Cancel*, visible seulement pendant le travail) et « Fermer » (*Close*). Certaines lignes n'apparaissent qu'au besoin : « Clé API : » (*API key:*) à la place de l'état des poids pour les modèles cloud ; « Site : » (*Site:*), « Zone : » (*Area:*), « Index stratigraphique : » (*Stratigraphic index:*) et « Type US : » (*US type:*) pour les couches US ; « Champ pour l'étiquette : » (*Field for the label:*) pour les autres couches. La fenêtre mémorise la dernière zone US, les classes, le côté maximal, le modèle choisi et les clés API.

Les entrées de la liste des modèles sont toujours écrites en italien (« Locale » = local), de même que quelques messages de service cités plus bas.

#### Environnement local

Les modèles locaux (SAM 2.1 et YOLOE) ne tournent pas dans le Python de QGIS, mais dans un **Python séparé**, que la fenêtre crée et vérifie elle-même. À l'ouverture, le groupe affiche « vérification… » (*checking…*), puis :

- en vert « prêt — ultralytics …, torch …, mps » (*ready — …*) : l'environnement est là ; le dernier mot est le périphérique de calcul (`mps`, `cuda` ou `cpu`) ;
- en orange « non installé : nécessaire pour les modèles locaux (SAM 2.1, YOLOE). Un Python système 3.10–3.13, ~1,5 Go de paquets. » (*not installed: needed for the local models (SAM 2.1, YOLOE). A system Python 3.10–3.13, ~1.5 GB of packages.*).

« Installer / mettre à jour » (*Install / update*) crée l'environnement ou met à jour ses paquets (voir plus bas « Installation Locale SAM ») ; « Afficher le journal » (*Show log*) ouvre et ferme le journal de l'installation, avec la sortie de pip ligne par ligne. Les modèles cloud n'ont pas besoin de l'environnement.

#### Image

- « Couche raster : » (*Raster layer:*) : l'image à segmenter, choisie parmi les rasters du projet : une orthophoto (fichier) ou une couche de tuiles/service. En dessous, en gris, il est écrit de quoi il s'agit : nom du fichier et dimensions en pixels (`orthophoto.tif — 12000 × 9000 px`) ou type de service, rendu depuis la vue (`tile / WMS (reso dalla vista)`, `ArcGIS REST (reso dalla vista)` — cette ligne est en italien, *reso dalla vista* = rendu depuis la vue).
- « Emprise : » (*Area:*) : « vue courante » (*current view*, ce que l'on voit sur la carte) ou « raster entier » (*whole raster*). « raster entier » n'est disponible que pour les fichiers : un service de tuiles n'a pas de bord, on travaille toujours sur la vue (ou sur un rectangle ou un polygone).
- « Résolution (unités de carte/px) : » (*Resolution (map units/px):*) : pour les tuiles seulement : combien d'unités de carte (mètres, ou degrés si la carte est en coordonnées géographiques) par pixel de l'image rendue. La valeur proposée est celle de la vue à l'ouverture de la fenêtre ou au choix de la couche : si vous zoomez ensuite, corrigez-la à la main. Plus elle est petite, plus il y a de détails.
- « Côté maximal (px) : » (*Max side (px):*) : le plus grand côté de l'image transmise au modèle : 2048 par défaut, de 512 à 8192. Au-delà, l'image est réduite ; SAM travaille de toute façon à 1024 px en interne.

### Modes de Segmentation

Le groupe « Que segmenter » (*What to segment*) propose six modes. Le choix du mode change la liste des modèles (voir « Modèles Disponibles ») et affiche dessous, en bleu, la consigne de ce mode.

#### 1. Tout automatique

« Tout (automatique) » (*Everything (automatic)*) : SAM 2.1 segmente chaque objet qu'il trouve dans l'« Emprise : » choisie (« vue courante » ou « raster entier »). Les polygones n'ont pas de classe : dans la couche temporaire, ils reçoivent l'étiquette « segment ». On lance avec « Démarrer » (*Start*).

#### 2. Points

« Points : cliquez sur les objets de la carte » (*Points: click the objects on the map*) : appuyez sur « Démarrer la sélection » (*Start selection*) ; la fenêtre se masque et la barre de messages de QGIS rappelle les commandes. Cliquez sur les objets un par un : chaque clic est un objet. Clic droit ou Entrée pour terminer, Retour arrière retire le dernier point, Échap annule. La fenêtre réapparaît et la segmentation s'exécute sur l'« Emprise : » choisie, un objet par point ; les points hors de l'image sont ignorés.

#### 3. Rectangle

« Rectangle : dessinez un rectangle » (*Box: draw a rectangle*) : appuyez sur « Démarrer la sélection » et tracez un rectangle sur la carte (Échap ou clic droit annule). L'image est découpée sur le rectangle et tout ce qu'il contient est segmenté.

#### 4. Polygone

« Polygone : dessinez la zone » (*Polygon: draw the area*) : appuyez sur « Démarrer la sélection » et cliquez les sommets ; clic droit, Entrée ou double-clic ferment le polygone (au moins trois sommets), Retour arrière retire le dernier sommet, Échap annule. Seul l'intérieur du polygone est segmenté.

#### 5. Polygone depuis une couche

« Polygone depuis une couche : » (*Polygon from layer:*) : choisissez une couche de polygones dans la liste déroulante à côté. On utilise l'entité sélectionnée de la couche, ou toutes si aucune n'est sélectionnée (plusieurs entités sont fusionnées en une seule). Comme pour le polygone dessiné, seul l'intérieur est segmenté : pratique pour travailler à l'intérieur d'un sondage, d'une zone de fouille ou d'une limite déjà dessinée. On lance avec « Démarrer ».

#### 6. Classes textuelles

« Classes textuelles : » (*Text classes:*) : écrivez dans le champ à côté ce qu'il faut chercher : des mots **anglais** séparés par des virgules (par défaut « building, road, river, field » ; autres exemples : stone, wall). Chaque classe devient une étiquette sur les polygones. Cela fonctionne avec YOLOE-26 en local ou avec SAM 3 de Roboflow dans le cloud, sur l'« Emprise : » choisie. On lance avec « Démarrer ».

**« Seuil : »** (*Threshold:* ; 0,30 par défaut, de 0,05 à 0,95) est la confiance minimale pour qu'un résultat soit conservé : plus bas, il donne plus de polygones, y compris incertains ; plus haut, il en donne moins mais plus sûrs. Le modèle cloud Replicate ne l'utilise pas.

### Modèles Disponibles

Le groupe « Modèle » (*Model*) contient une liste déroulante « Modèle : » (*Model:*) dont le contenu dépend du mode choisi :

| Modèle | Type | Prérequis | Modes |
|--------|------|-----------|-------|
| SAM 2.1 Tiny | Local | environnement local + poids ~78 Mo | tous sauf les classes textuelles ; le plus léger et le plus rapide |
| SAM 2.1 Small | Local | environnement local + poids ~92 Mo | tous sauf les classes textuelles |
| SAM 2.1 Base+ | Local | environnement local + poids ~162 Mo | tous sauf les classes textuelles |
| SAM 2.1 Large | Local | environnement local + poids ~449 Mo | tous sauf les classes textuelles ; le plus précis et le plus lent |
| Cloud: Replicate SAM-2 | Cloud | clé API Replicate | segmentation automatique seulement (en mode « Points », les clics sont ignorés, avec un avertissement) |
| YOLOE-26 S | Local | environnement local + poids ~31 Mo + MobileCLIP2 254 Mo (une fois) | classes textuelles |
| YOLOE-26 M | Local | environnement local + poids ~70 Mo + MobileCLIP2 254 Mo (une fois) | classes textuelles |
| YOLOE-26 L | Local | environnement local + poids ~79 Mo + MobileCLIP2 254 Mo (une fois) | classes textuelles |
| Cloud: Roboflow SAM 3 | Cloud | clé API Roboflow | classes textuelles |

Dans la liste déroulante, les entrées se lisent ainsi : « Locale: SAM 2.1 Tiny — ~78 MB », « Locale: YOLOE-26 S (classi a testo) — ~31 MB + MobileCLIP2 254 MB », « Cloud: Replicate SAM-2 (solo automatico, chiave API) », « Cloud: Roboflow SAM 3 (classi a testo, chiave API) » (*locale* = local, *classi a testo* = classes textuelles, *solo automatico* = automatique seulement, *chiave* = clé).

**Poids.** Pour un modèle local, l'état des poids s'affiche sous la liste : « poids présents ✓ » (*weights present ✓*, vert) ou « poids manquants (~N Mo) » (*weights missing (~N MB)*, orange), avec le bouton « Télécharger les poids » (*Download weights*). Le téléchargement, avec barre de progression, récupère les fichiers dans les assets publics d'ultralytics sur GitHub (aucun compte nécessaire). Pour YOLOE, l'encodeur de texte MobileCLIP2 (254 Mo) est téléchargé aussi, une seule fois pour S, M et L. Les poids se trouvent dans `~/pyarchinit_5/bin/models/sam/`.

**Clé API.** Pour un modèle cloud, le champ « Clé API : » (*API key:*) et le lien pour obtenir la clé remplacent l'état des poids (voir « Configuration API »).

### SAM-3 avec Text Prompt

Avec le mode « Classes textuelles », on ne demande pas « découpe tout », mais « trouve ces choses » :

- on écrit une ou plusieurs classes en anglais, séparées par des virgules : `building, road, river, field`, ou `stone, wall`… ;
- **YOLOE-26** (local, S/M/L) comprend les mots grâce à l'encodeur de texte MobileCLIP2 ; **SAM 3** de Roboflow (cloud) reçoit les mêmes classes comme prompts textuels (16 au maximum) ;
- chaque polygone porte la classe qui l'a trouvé : dans la couche temporaire, dans le champ `label` ; dans votre propre couche, dans le « Champ pour l'étiquette : » (*Field for the label:*). Dans les couches US de pyArchInit, la classe n'est pas écrite.

SAM 2.1 en mode « Tout (automatique) », en revanche, n'attribue pas de classes : il trouve des contours, pas des noms.

### Configuration API

Les clés ne servent qu'aux modèles cloud. Choisissez le modèle cloud dans la liste, collez la clé dans le champ « Clé API : » (*API key:* ; le texte reste masqué) et appuyez sur « Démarrer » : la clé est enregistrée dans les paramètres de QGIS et reproposée la fois suivante. Avec les modèles cloud, l'image préparée est envoyée au service.

#### Replicate API (SAM-2)
1. Créer un compte sur [replicate.com](https://replicate.com)
2. Créer un jeton sur [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens) (le lien « Clé Replicate » (*Replicate key*) à côté du champ ouvre la même page)
3. Le coller dans « Clé API : » avec le modèle « Cloud: Replicate SAM-2 »

#### Roboflow API (SAM-3)
1. Créer un compte sur [roboflow.com](https://roboflow.com)
2. Copier la clé depuis [app.roboflow.com/settings/api](https://app.roboflow.com/settings/api) (lien « Clé Roboflow » (*Roboflow key*) à côté du champ)
3. La coller dans « Clé API : » avec le modèle « Cloud: Roboflow SAM 3 »

### Installation Locale SAM

Aucune commande dans le terminal : l'environnement des modèles locaux s'installe depuis la fenêtre.

1. Il faut un **Python système 3.10–3.13** : les paquets ne sont pas installés dans le Python de QGIS, pour ne pas risquer de le casser. La fenêtre le cherche toute seule : sous **macOS** le Python de [python.org](https://www.python.org/downloads/) ou de Homebrew, sous **Windows** le lanceur `py` du Python de python.org, sous **Linux** `python3.10`…`python3.13` ou `python3` du système.
2. Appuyer sur « Installer / mettre à jour » (*Install / update*) dans le groupe « Environnement local » : l'environnement virtuel `~/pyarchinit_5/bin/sam_venv` est créé et on y installe `ultralytics` (qui apporte torch, torchvision, OpenCV, numpy) et `requests` : environ **1,5 Go** de paquets, une seule fois. Sous Linux sans carte NVIDIA, c'est la version CPU de torch qui est installée, bien plus légère.
3. « Afficher le journal » (*Show log*) montre pip au travail. À la fin, l'état passe au vert : « prêt — ultralytics …, torch …, mps ».
4. Télécharger les poids du modèle voulu avec « Télécharger les poids » (*Download weights*, groupe « Modèle »).

Un nouvel appui sur « Installer / mettre à jour » met les paquets à jour. Le périphérique de calcul est choisi automatiquement : **MPS** sur les Mac Apple Silicon, **CUDA** avec une carte NVIDIA, sinon **CPU** (cela fonctionne, mais plus lentement). Si MPS ou CUDA échouent, le travail repart tout seul sur le CPU.

| Quoi | Où |
|------|----|
| Environnement Python | `~/pyarchinit_5/bin/sam_venv` |
| Poids des modèles | `~/pyarchinit_5/bin/models/sam/` |
| Clés API | paramètres de QGIS |

`~/pyarchinit_5` est le dossier de données de pyArchInit (ou celui indiqué par la variable `PYARCHINIT_HOME`).

### Destination et Attributs

Le groupe « Destination » (*Target*) décide où vont les polygones. La liste « Couche : » (*Layer:*) contient les couches de polygones du projet et « — nouvelle couche temporaire — » (*— new temporary layer —*) ; si `pyunitastratigrafiche` est chargée, c'est elle qui est proposée.

| Destination | Ce qui est écrit |
|-------------|------------------|
| « — nouvelle couche temporaire — » | une couche mémoire `SAM_<raster>_<date_heure>`, dans le SCR de l'image, avec les champs `label` (la classe, ou « segment »), `score` (confiance), `area`, `source` (le modèle) et `created` (date et heure) |
| `pyunitastratigrafiche` / `pyunitastratigrafiche_usm` | `scavo_s` = « Site : » (*Site:* ; depuis la configuration, non modifiable), `area_s` = « Zone : » (*Area:* ; obligatoire), `stratigraph_index_us` = « Index stratigraphique : » (*Stratigraphic index:* ; 1 = pierres/objets, 2 = couche/surface), `tipo_us_s` = « Type US : » (*US type:* ; pietra, layer, accumulo, taglio, struttura), `disegnatore` = `SAM <modèle>` (ex. `SAM sam2.1_t.pt`), `data` = aujourd'hui ; `us_s` reste vide |
| une autre couche de polygones | la classe dans le « Champ pour l'étiquette : » (*Field for the label:*), un champ texte (est proposé `label`, `etichetta`, `classe`, `class`, `tipo` ou `nome` s'il existe ; vide = ne rien écrire) ; si la couche a des champs `score`, `area`, `source` ou `created`, ils sont remplis aussi |

- Dans les couches US, le numéro d'US s'attribue ensuite dans la table attributaire ; le message final le rappelle : « Attribuez ensuite les numéros d'US dans la table attributaire. » (*Then assign the US numbers in the attribute table.*).
- Les polygones sont reprojetés dans le SCR de la couche de destination et enregistrés tout de suite dans la couche (si la couche était déjà en mode édition, ses modifications en attente sont enregistrées aussi).
- La couche temporaire ne vit que jusqu'à la fermeture de QGIS : pour la garder, exportez-la dans un fichier (clic droit sur la couche → Exporter).

### Fonctionnement

1. **L'image.** Pour un fichier, l'emprise est découpée et, si besoin, réduite avec GDAL : les pixels sont les vrais pixels du fichier, pas ceux dessinés sur la carte (le style de la couche ne compte pas ; les rasters qui ne sont pas en 8 bits sont étirés sur 0–255). Les tuiles et les services n'ont pas de fichier : QGIS rend la vue avec son propre moteur de rendu, à la résolution choisie — cette couche seule, sans les autres couches de la carte — et c'est ce rendu qui est segmenté.
2. **La zone.** Avec un polygone (dessiné ou depuis une couche), on prend le rectangle qui le contient, on blanchit tout ce qui est à l'extérieur, et à la fin les résultats sont découpés sur le polygone.
3. **Le modèle.** Le travail est fait par `scripts/sam_worker.py`, qui tourne hors de QGIS avec le Python de `sam_venv` (ou appelle le service cloud) : QGIS ne se bloque pas. Ses messages de progression (les lignes `[sam] …` du worker, en italien) s'affichent dans la ligne d'état : modèle et périphérique, puis combien de polygones en combien de secondes. Les polygones de moins de 20 pixels sont écartés et les contours simplifiés.
4. **Le retour sur la carte.** Le worker renvoie les polygones en pixels ; pyArchInit les ramène en coordonnées grâce au géoréférencement de l'image, répare les géométries invalides et les reprojette dans le SCR de la couche de destination.

### Workflow SAM

**1. Préparation**
- Charger l'orthophoto, ou une couche de tuiles (ex. ESRI World Imagery en tuiles XYZ)
- Vérifier le système de référence du projet
- Pour écrire dans les US : charger `pyunitastratigrafiche` (ou `pyunitastratigrafiche_usm`) et contrôler le site dans la configuration
- La première fois, pour les modèles locaux : « Installer / mettre à jour », puis « Télécharger les poids »

**2. Configuration**
- « Image » : couche raster, emprise, résolution (pour les tuiles) et côté maximal
- « Que segmenter » : le mode, le seuil et, pour les classes textuelles, les classes
- « Modèle » : un modèle local dont les poids sont présents, ou un modèle cloud avec sa clé
- « Destination » : la couche et ses attributs

**3. Exécution**
- « Démarrer », ou « Démarrer la sélection » puis points, rectangle ou polygone sur la carte
- Suivre la ligne d'état ; « Annuler » interrompt le travail
- À la fin apparaît « Terminé : N polygones ajoutés à “couche” (modèle). » (*Done: N polygons added to “layer” (model).*)

**4. Post-traitement**
- Contrôler les polygones ; les éventuels avertissements apparaissent dans la barre de messages de QGIS
- Couches US : attribuer les numéros d'US (`us_s`) dans la table attributaire
- Corriger, fusionner ou supprimer les polygones erronés avec les outils d'édition de QGIS
- Couche temporaire : l'exporter si elle doit être conservée

## Intégration Cartographique

### Export des Données SIG

Depuis la Fiche US, tab Map :
- **Export GeoPackage** : Couche en GPKG
- **Export Shapefile** : Couche en SHP
- **Export GeoJSON** : Couche en JSON

### Import des Données SIG

Importer des géométries existantes :
1. Charger la couche dans QGIS
2. Sélectionner les entités
3. Utiliser la fonction import

### Géotraitement

Opérations spatiales disponibles :
- Buffer
- Intersection
- Union
- Différence
- Centroïdes

## Bonnes Pratiques

### 1. Orthophotos

- Résolution minimale : 1-2 cm/pixel
- Format : GeoTIFF géoréférencé
- Système de référence : cohérent avec le projet

### 2. Digitalisation

- Utiliser l'accrochage pour la précision
- Vérifier la topologie
- Maintenir la cohérence des attributs

### 3. Segmentation SAM

- Orthophoto de bonne qualité, éclairage uniforme, bon contraste entre objets et fond
- **Grandes orthophotos** : travailler par vue ou par rectangle, pas sur « raster entier ». SAM travaille à 1024 px en interne et, au-delà du « Côté maximal (px) : », l'image est réduite : sur une zone trop grande, les petits objets se perdent
- **Tuiles** : choisir un niveau de zoom où les objets se reconnaissent à l'œil (ex. 0,3–0,6 m/px pour les bâtiments et les routes). La « Résolution (unités de carte/px) : » propose celle de la vue ; si l'emprise est grande, l'image est réduite au côté maximal et la résolution réelle se dégrade
- **Classes textuelles** : des noms anglais simples (building, road, river, field, stone, wall)
- Les classes ne viennent que de YOLOE ou de SAM 3 : SAM 2.1 en mode « Tout (automatique) » trouve les contours mais n'attribue pas de classes
- **Matériel** : les Mac Apple Silicon utilisent MPS, une carte NVIDIA utilise CUDA, sinon le CPU, plus lent (préférer alors SAM 2.1 Tiny ou Small, YOLOE-26 S et de petites zones)
- Post-vérification toujours nécessaire

### 4. Organisation des Couches

- Grouper par typologie
- Utiliser des styles cohérents
- Maintenir l'ordre dans la légende

## Résolution des Problèmes

### Couches Non Affichées

**Causes possibles** :
- Étendue incorrecte
- Système de référence différent
- Filtre actif

**Solutions** :
- Zoom sur la couche
- Vérifier le CRS
- Supprimer les filtres

### SAM Ne Fonctionne Pas

| Message ou symptôme | Que faire |
|---------------------|-----------|
| « Environnement local » en orange : « non installé… » (*not installed…*), ou « L'environnement local n'est pas installé : appuyez sur “Installer / mettre à jour” (ou choisissez un modèle cloud). » (*The local environment is not installed: press “Install / update” (or choose a cloud model).*) | Appuyer sur « Installer / mettre à jour ». Il faut un Python système 3.10–3.13 ; s'il n'y en a pas, apparaît `Installation failed: Nessun Python 3.10–3.13 trovato: installa Python da python.org (o Homebrew) e riprova.` (aucun Python 3.10–3.13 trouvé : installez Python depuis python.org ou Homebrew). Si pip échoue, l'erreur est dans « Afficher le journal ». Sous Linux sans carte NVIDIA, c'est la version CPU de torch qui est installée |
| « poids manquants (~N Mo) » (*weights missing (~N MB)*), ou « Les poids du modèle manquent : appuyez sur “Télécharger les poids”. » (*The model weights are missing: press “Download weights”.*) | Appuyer sur « Télécharger les poids » (connexion Internet nécessaire) |
| « La clé API du service est nécessaire. » (*The service API key is needed.*) | Avec un modèle cloud, coller la clé dans « Clé API : » (voir « Configuration API ») |
| « Aucun polygone trouvé : essayez une zone plus petite, un seuil plus bas ou un autre modèle. » (*No polygon found: try a smaller area, a lower threshold or another model.*) | Emprise plus petite, « Seuil : » plus bas, un autre modèle (un SAM 2.1 plus grand, ou les classes textuelles) ; pour les tuiles, une résolution plus fine |
| « La zone choisie ne couvre pas le raster » (message en italien : `l'area scelta non copre il raster`) | La vue, le rectangle ou le polygone tombent hors du raster : zoomer sur le raster et réessayer |
| « Remplissez la zone pour la couche US. » (*Fill in the area for the US layer.*) | Saisir la « Zone : » dans le groupe « Destination » |
| « Raster pivoté : non pris en charge (reprojetez-le d'abord) » (message en italien : `raster ruotato: non supportato (riproiettalo prima)`) | Reprojeter le raster avec gdalwarp (menu Raster de QGIS) et utiliser le nouveau fichier |
| « Échec de la segmentation » (*Segmentation failed*) avec les dernières lignes du worker | Lire les lignes du message ; réessayer avec une emprise ou un « Côté maximal (px) : » plus petits, ou avec un modèle plus petit |

### Géométries Corrompues

**Causes possibles** :
- Erreurs de digitalisation
- Import problématique

**Solutions** :
- Utiliser "Réparer les géométries"
- Redessiner l'élément

### Couche chargée mais géométries non visibles (SQLite)

**Symptôme** :
- Une couche pyArchInit d'une base SQLite/SpatiaLite (ex. US `pyunitastratigrafiche`, USM, mobilier, US négatives) se charge et sa table attributaire affiche les enregistrements, mais rien n'est dessiné sur la carte et "Zoom sur la couche" ne fonctionne pas

**Cause** :
- L'index spatial (R*Tree) de la couche n'a pas été maintenu : ses triggers ont été perdus lorsqu'une table a été recréée (ex. par d'anciens scripts de mise à jour du schéma) ou les données ont été importées en les contournant
- QGIS sélectionne les entités à dessiner via cet index, elles restent donc invisibles
- Les bases créées à partir du modèle SQLite entre octobre 2025 et septembre 2026 sont également concernées

**Solution (automatique)** :
- À la connexion à une base SQLite, pyArchInit vérifie tous les index spatiaux (quelques instants ; rien n'est écrit si la base est saine) et reconstruit automatiquement ceux qui sont endommagés
- Depuis la version 5.13.16-alpha, la même vérification répare aussi les **vues spatiales** (`pyarchinit_us_view`, `pyarchinit_quote_view`, structures, mobilier, les vues UT, etc.) :
  - chaque vue est rattachée au ROWID de sa table géométrique
  - les enregistrements de vues qui n'existent plus sont supprimés
  - les vues standard manquantes sont recréées
  - les vues UT sont enregistrées comme vues spatiales
  - les tables géométriques sans index spatial en reçoivent un : nécessaire lorsque le GDAL fourni avec QGIS n'a pas les fonctions SpatiaLite (ex. QGIS sur macOS), où sans index ces couches ne dessinaient rien
- Avant de modifier quoi que ce soit, il enregistre UNE seule copie de sauvegarde à côté de la base : `<base>.sqlite.pre_spatial_index_repair_<date-heure UTC>`
- Le résultat est écrit dans le panneau de journal de QGIS (Vue → Panneaux → Journal des messages, onglet "PyArchInit")

**Que faire** :
- Rien à lancer manuellement : la vérification s'exécute automatiquement à la PREMIÈRE connexion à chaque base dans chaque session QGIS (donc après la mise à jour du plugin ou après le redémarrage de QGIS)
- Si les couches étaient déjà chargées, les retirer et les ajouter de nouveau (ou rouvrir le projet) après la réparation
- Si le journal "PyArchInit" signale qu'un index n'a PAS pu être réparé (ex. SpatiaLite impossible à charger), corriger la cause et redémarrer QGIS : la vérification n'est relancée que dans une nouvelle session
- Le fichier de sauvegarde peut être supprimé une fois les couches vérifiées
- Pour relancer la vérification (ex. après avoir restauré une sauvegarde), redémarrer QGIS
- Remarque : dans `inventario_materiali_view`, le point du site est répété pour chaque objet du mobilier, donc "Identifier les entités" sur ce point affiche l'un de ces objets

## Références

### Fichiers Source
- `modules/gis/pyarchinit_pyqgis.py` - Intégration SIG
- `tabs/Sam_Segmentation_Dialog.py` - Fenêtre SAM : groupes, modes, destination
- `modules/utility/sam_environment.py` - Environnement Python séparé, paquets et poids
- `modules/gis/sam_raster_source.py` - Image à segmenter (découpe GDAL ou rendu de la vue) et géoréférencement
- `modules/gis/sam_map_tools.py` - Outils de carte pour points, rectangle et polygone
- `scripts/sam_worker.py` - Worker hors de QGIS : SAM 2.1, YOLOE, Replicate, Roboflow

### Couches
- `pyunitastratigrafiche` - US dépôt
- `pyunitastratigrafiche_usm` - US muraires
- `pyarchinit_quote` - Cotes

---

## Vidéo Tutorial

### Intégration SIG
`[Placeholder : video_integration_sig.mp4]`

**Contenus** :
- Couches prédéfinies
- Visualisation des US
- Styling et étiquettes
- Export cartographique

**Durée prévue** : 15-18 minutes

### Segmentation SAM
`[Placeholder : video_sam_segmentation.mp4]`

**Contenus** :
- Configuration SAM
- Modes de segmentation
- Post-traitement
- Bonnes pratiques

**Durée prévue** : 12-15 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../animations/pyarchinit_image_classification_animation.html)
