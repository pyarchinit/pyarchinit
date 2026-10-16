# Tutoriel 36 : Export Extended Matrix et Bridge s3dgraphy

## Introduction

À partir de la version **5.2.0-alpha** PyArchInit intègre un **bridge bidirectionnel** avec la bibliothèque **s3dgraphy** (modèle de données Extended Matrix d'Emanuel Demetrescu). Le bridge permet de :

- **Exporter** le diagramme stratigraphique en Extended Matrix au format **em.json**, celui qu'ouvre EMStudio (l'ancien export GraphML est retiré)
- **Réimporter** les modifications faites dans yEd (déplacements d'US entre périodes/groupes) en mettant à jour la base SQL
- **Joindre des paradata** (Author / License / Embargo) au niveau du site
- **Regrouper** les US par dimension (struttura, area, attivita, settore, ambient, saggio, quad_par ou groupes ad-hoc)

Tag courant: `em-import-5.13.121-alpha` (2026-10-16).

---

## 1. Prérequis

- Base de données SQLite/Spatialite **ou PostgreSQL/PostGIS** : l'export em.json est le même sur les deux moteurs (la connexion est celle du projet ; `export_site` accepte `sqlite://` et `postgresql://`)
- **Migration Phase 1 node_uuid** appliquée automatiquement à l'ouverture du DB
- **EMStudio** pour ouvrir l'em.json (il s'installe depuis **Extended Matrix → Installa EMStudio…**), ou le panneau **Vedi la matrice…** dans QGIS, qui n'a besoin de rien. **yEd** (https://www.yworks.com/products/yed) ne sert que pour importer des fichiers GraphML dessinés avec lui (§5)

> ⚠️ Pour les DB antérieurs à 5.2.0-alpha, un redémarrage de QGIS peut être nécessaire.

---

## 2. Exporter Extended Matrix (bouton vert)

### 2.1 Ouvrir le dialogue

1. Ouvrir la **Fiche US** du site désiré
2. Cliquer sur le bouton vert **"Esporta Extended Matrix"** (sous l'onglet Rapporti)

### 2.2 Onglet "Export"

La fenêtre dit en haut à quoi sert chaque format. Elle contient :

- **Formati** (Formats) : **DOT (Graphviz) — matrice di Harris** et **em.json (Extended Matrix, per EMStudio)**, cochés au départ, plus **Matrice per fasi** (matrice par phases, analyse chronologique), facultative. Le GraphML ne s'exporte plus : le JSON de cette fenêtre **est l'em.json**, le fichier même que produit le menu **Extended Matrix → Esporta sito in em.json…** — même projecteur, même symbolique.
- **Opzioni** (Options) : **Controlla la sequenza stratigrafica e segnala i problemi** (contrôler la séquence stratigraphique et signaler les problèmes). C'est la seule option qui reste, et elle est vraiment lue : décochée, le contrôle n'a pas lieu. Les deux anciennes cases qui parlaient à yEd (indices d'auto-layout, couleurs par période) sont parties avec l'export GraphML.
- **Extended Matrix** : quatre boutons à côté de l'export — **Apri in EMStudio** et **Vedi la matrice** (tous deux s'allument après un export em.json réussi ; le second dessine la matrice dans QGIS, sans EMStudio), **Consegna alla stanza…** et **Apri la stanza**. Ce sont les mêmes entrées du menu pyArchInit, à portée de main.

En appuyant sur **Esporta**, le **dossier de destination** est demandé.

Auteurs, licences, embargos et groupes se gèrent dans la fenêtre **"Manage paradata"** (§3).

### 2.2.1 Sondages : un seul graphe pour tout le site

À partir de la version **5.13.109-alpha**, l'em.json porte **un seul graphe**, avec les unités de tous les sondages : il n'y a rien à choisir. La fenêtre « Esporta Extended Matrix » n'a plus le groupe « Saggi » (sondages), et les entrées de menu **Esporta sito in em.json…** et **Vedi la matrice…** ne demandent plus que le site.

Le sondage est le champ **Saggio** de la fiche US : il reste un champ comme les autres, qui peut servir de dimension pour regrouper les unités (`saggio`, §4) et qui entre dans le *briefing* de la narration (§10.4), mais il ne divise plus le fichier. Un fichier exporté avec les versions précédentes (jusqu'à la 5.13.108-alpha), avec un graphe par sondage, s'ouvre encore dans le panneau de la matrice (§10.8).

### 2.3 Cliquer sur "Esporta"

Les fichiers qui naissent, selon les formats cochés :
- `<site>.em.json` — Extended Matrix, à ouvrir dans EMStudio ou à livrer à une salle
- `Extended_Matrix_<site>[_<area>].dot` — Graphviz DOT, pour la matrice de Harris classique
- `Extended_Matrix_<site>[_<area>]_phased.json` — vue par époque

> **Les lieux voyagent dans l'em.json.** Le lieu du site, la chaîne toponymique et les groupes d'aires, de secteurs, de sondages et de pièces sortent avec les unités, reliés par des arcs `is_in_location` (§4).

Le récapitulatif final liste les fichiers et, pour l'em.json, **combien de nœuds et combien d'arcs** sont sortis, avec les avertissements s'il y en a.

> **Le GraphML ne s'exporte plus** : la matrice se regarde et se valide dans EMStudio, qui lit em.json. Les rangées temporelles (swimlanes) de l'ancien GraphML sont parties avec lui. Le GraphML ne survit qu'à l'**entrée**, pour les fichiers dessinés dans yEd (§5).

---

## 3. Dialogue "Manage paradata" (4 onglets)

### 3.1 Accès
Cliquez sur le bouton **"Manage paradata"** dans la fiche US (à côté du bouton vert Export).

### 3.2 Les 4 onglets

| Onglet | Contenu | Fichier généré |
|---|---|---|
| **Authors** | Ajouter auteurs (nom + ORCID + rôle) | `paradata_<site>.graphml` |
| **Licenses** | Licence du jeu (ex. CC-BY-NC-4.0 + URL) | idem |
| **Embargoes** | Dates d'embargo + motif | idem |
| **Groups** | Groupes ad-hoc (nom + sélection des US membres) | `groups_<site>.graphml` |

Les fichiers sont enregistrés à côté du DB SQLite et sont **versionnables en Git**.

---

## 4. Dimensions et types de groupe dans l'em.json

L'em.json qu'exporte pyArchInit porte les **groupes de lieu** (`LocationNodeGroup`) de la fiche US, distingués par le type `kind` : `toponym`, la chaîne nazione → regione → provincia → comune et le lieu du site (§4.1) ; `study`, les **aires**, les **secteurs** et les **sondages** ; `functional`, les **pièces**. Chaque unité est reliée aux groupes où elle se trouve par des arcs `is_in_location` ; l'identifiant du groupe indique le champ dont il est issu (par exemple `loc::area::study::1`). Le fichier ne porte pas de couleurs : c'est celui qui le lit qui les décide, EMStudio avec son propre style et le panneau de la matrice dans QGIS avec les règles visuelles de la bibliothèque s3dgraphy. L'ancien export GraphML colorait les groupes par dimension : cette palette a été retirée avec lui. La bibliothèque sait aussi regrouper par **structure**, **activité**, **carré** et par groupes ad-hoc, avec une appartenance primaire et les autres secondaires (`is_primary`) : pyArchInit ne le lui demande pas aujourd'hui, et dans le fichier cet attribut n'apparaît que sur les arcs de la chaîne toponymique, toujours faux.

### 4.1 Chaîne toponymique (5.6.0-alpha)

Les champs `site_table.{nazione, regione, provincia, comune}` sont automatiquement émis comme une chaîne récursive de `LocationNodeGroup(kind="toponym")` (parent : nazione → regione → provincia → comune). Les niveaux administratifs vides sont sautés sans rompre la chaîne. Une déduplication cross-site garantit que la même `comune` présente dans 2 sites devient **un seul nœud partagé** dans l'em.json.

---

## 4.2 Appartenance multidimensionnelle (5.6.0-alpha)

Une unité peut se trouver dans plusieurs groupes à la fois — une aire, un secteur, un sondage, une pièce, en plus du lieu du site — et elle a dans le fichier un arc `is_in_location` pour chacun, tous sur un pied d'égalité. Exemple : une US avec `area=1`, `settore=1` et `ambient=Ambiente 3` a trois arcs, vers « 1 » (aire, `study`), « 1 » (secteur, `study`) et « Ambiente 3 » (`functional`), plus celui vers le lieu du site, d'où remonte la chaîne toponymique. La distinction entre appartenance primaire et secondaire (`is_primary`, avec `struttura` en premier et `toponym` jamais primaire) relève du modèle de la bibliothèque, pour qui lui demande les groupes par dimension : dans l'em.json de pyArchInit, elle n'existe pas.

---

## 5. Round-trip (onglet Import)

> **Ce qu'on peut importer** : l'onglet Import lit désormais aussi **em.json** — celui d'EMStudio ou du nœud StratiGraph — et choisit le lecteur d'après l'extension du fichier ; un `.graphml` de yEd reste accepté pour les fichiers d'avant. La procédure ci-dessous, déplacer des US entre groupes, concerne la voie yEd/GraphML.

### 5.0 Importer un em.json d'EMStudio (même avec une base de données vide)

Un em.json écrit par **EMStudio** (et non par pyArchInit) s'importe dans la base de données de pyArchInit **même quand celle-ci est vide** (depuis la 5.13.121-alpha) : le site, les périodes, les fiches, les relations et les médias naissent du fichier, sans qu'il faille créer un site au préalable.

1. Ouvrir le menu **Plugins → pyArchInit - Archaeological GIS Tools** et choisir l'entrée **Extended Matrix → Importa em.json…** (Importer un em.json) : la fenêtre de l'Extended Matrix s'ouvre déjà sur l'onglet **Import**, même si la base ne contient aucun site. On arrive au même endroit depuis la fiche US : le bouton vert **Esporta Extended Matrix**, quand aucun site n'est choisi, ouvre la même fenêtre sur l'onglet Import au lieu de s'arrêter (l'**export**, lui, continue de demander un site).
2. Appuyer sur **Browse…** et choisir l'em.json.
3. Vérifier le **Sito target:** (site cible). S'il est vide — le cas d'une base sans site —, le nom du graphe écrit dans l'em.json est proposé (par exemple « Temple ») ou, à défaut, le nom du fichier sans « .em.json » ; il peut être modifié. Si le champ affiche déjà un site (avec une base qui en contient : celui de la fiche US d'où l'on part ou, depuis le menu, le premier par ordre alphabétique), aucun nom n'est proposé : saisir le nom du nouveau site ou choisir celui dans lequel importer. Dessous se trouvent deux cases, cochées par défaut : **Crea periodi mancanti se assenti** (Créer les périodes manquantes si absentes — si on la décoche et que le site n'a pas déjà les périodes du fichier, l'import s'arrête avec l'erreur « MissingEpochError ») et **Importa anche i media citati (file accanto all'em.json)** (Importer aussi les médias cités — fichiers à côté de l'em.json).
4. Appuyer sur **Anteprima** (Aperçu) : rien n'est écrit, et le résumé indique combien de fiches sont nouvelles, mises à jour et inchangées, combien de périodes sont nouvelles et, en liste, combien de fiches de quel type et combien de nœuds du fichier ne deviennent pas des fiches.
5. Appuyer sur **Applica** (Appliquer ; le bouton s'active après l'aperçu) : l'import est effectué et le même résumé s'affiche, suivi de celui des médias.

Ce qui se passe, en bref :

- **Ce qui devient une fiche.** Seulement les unités dont pyArchInit connaît le type (US, USM, USD, USVs, USVn, serUSVn, SF, VSF, RSF, USN, USNt…) et les paradata : propriétés (`property`), extracteurs (`Extractor`), combinateurs (`Combinar`) et documents (`DOC`). Les ressources, fichiers, modèles 3D, formes sémantiques, processus du jumeau numérique, groupes, époques et la narration ne deviennent **pas** des fiches : avant la 5.13.121-alpha, ils devenaient tous des « US ».
- **Les noms (champ US).** Le nom du nœud sans le préfixe du type : USV105 → 105, D.05 → 05, D.05.02 → 05.02. Les propriétés qui portent le même nom (par exemple « height », présente pour beaucoup d'unités) reçoivent entre parenthèses le nom de l'unité à laquelle elles appartiennent : « height (105) ». Si deux types différents donneraient le même numéro — le combinateur « C.10 » et le document « D.10 », l'US « SU002 » et l'USD « USD002 » —, le type le plus fort (l'US, puis les autres unités, puis les documents, les extracteurs, les combinateurs) garde le numéro et l'autre garde le nom complet d'EMStudio (« C.10 », « USD002 »), afin que les relations ne se confondent pas.
- **Les relations.** Entre deux US/USM, ce sont les relations habituelles de pyArchInit (« Copre » (couvre), « Taglia » (coupe)…), et la relation « vient après » (`is_after` : l'unité est plus récente que l'autre) entre deux US s'écrit « Copre ». Entre des unités de types différents, les relations physiques s'écrivent en toutes lettres (« Taglia », « Si appoggia a » (s'appuie contre)), la relation « vient après » avec `>` (`A > B` : A est plus récente que B), et la chaîne des paradata — unité → propriété → extracteur ou combinateur → document, et l'objet « partie de » un objet virtuel — avec `>>`. Les périodes, activités, groupes et ressources ne sont pas des relations. À l'export, ces signes redeviennent les arcs de l'Extended Matrix (`is_after`, `has_property`, `has_data_provenance`, `extracted_from`, `combines`, `is_part_of`).
- **Activité et description.** L'activité du nœud (le groupe ActivityNodeGroup) va dans le champ **Activité** de la fiche ; la description du nœud, dans le champ **Description**.
- **Périodisation.** Les époques d'EMStudio, qui n'ont qu'un nom et des dates, sont retrouvées par leur nom dans la périodisation du site ; celles qui n'y sont pas deviennent de nouvelles périodes, de la plus ancienne à la plus récente, numérotées après la dernière période du site, en phase 1, avec les dates de début et de fin et le nom comme datation étendue. Chaque unité prend ses période et phase initiales de l'époque où elle naît, et les finales de la dernière époque où elle survit (ou les mêmes que les initiales).
- **Fiche du site.** Si le site n'existe pas, il est créé, avec « Extended Matrix » comme définition et une description tirée du graphe : nom, code, auteurs et position (EPSG et origine).
- **Médias.** En suivant les liens de l'em.json — fiche → ressource → fichier, fiche → modèle 3D → ressource → fichier, et l'url du document —, les fichiers qui existent **à côté de l'em.json** (par leur chemin relatif à son dossier, ou par le seul nom du fichier dans ce dossier) deviennent des médias de la fiche : ils sont copiés dans le dossier des médias du projet, avec les vignettes (c'est le dossier de l'import QField, tutoriel 38 : à côté de celui des vignettes, **Thumbnail path** dans la configuration). Les images, vidéos et modèles 3D sont pris en compte ; les PDF restent dans le champ **Documentation** de la fiche du document ; les autres fichiers (par exemple `.mtl`, `.zip`) sont seulement comptés. Le résumé indique combien de médias sont nouveaux, combien étaient déjà présents et combien de fichiers cités n'ont pas été trouvés : pour les importer, placer l'em.json dans son dossier de projet, avec les fichiers à côté.
- **Réimporter.** Importer de nouveau le même fichier ne duplique ni les périodes ni les fiches : celles qui existent déjà ressortent comme « invariate » (inchangées) ou « aggiornate » (mises à jour), et là où la base et le fichier diffèrent, c'est le fichier qui l'emporte (le résumé les compte comme « conflitti », conflits).

La voie yEd/GraphML, pour déplacer des unités entre groupes, est celle qui suit.

Pour modifier la base SQL en déplaçant les US entre groupes en GraphML :

1. Ouvrir le GraphML dans **yEd**
2. Glisser une US dans un autre groupe, sauvegarder
3. Retour au dialogue → onglet **"Import"**
4. **Cocher** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Charger le GraphML modifié

Le système exécute une transaction atomique : en cas d'échec, **rollback complet** (le DB reste intact). Les groupes `adhoc` n'écrivent jamais en SQL — ils mettent à jour seulement `groups_<site>.graphml`.

À partir de 5.6.0-alpha le walker d'import est **récursif** et supporte les dossiers imbriqués (par exemple chaîne toponymique `nazione > regione > provincia > comune > US`). Si des cycles sont détectés dans le graphe des dossiers, une exception `CycleDetectedError` est levée et l'import est annulé avec rollback.

---

## 6. CLI (alternative au dialogue)

Pour les scripts / batch :

```bash
# Exporter
python scripts/s3dgraphy_sync.py export \
    --db <path> --sito <name> --mapping pyarchinit_us_mapping \
    --output <out.graphml> --group-by struttura

# Lister les groupes ad-hoc
python scripts/s3dgraphy_sync.py paradata list-groups \
    --db <path> --sito <name>

# Ajouter un auteur
python scripts/s3dgraphy_sync.py paradata add-author \
    --db <path> --sito <name> --name "Marco Pacifico" \
    --orcid "0000-0002-1234-5678" --role curator
```

Exit codes : 0 = succès, 1 = erreur de bridge, 2 = erreur argparse.

---

## 7. Résolution de problèmes

| Symptôme | Cause | Solution |
|---|---|---|
| "no such column: node_uuid" | Migration Phase 1 non exécutée | Redémarrer QGIS, rouvrir le DB |
| GraphML vide | DB sans rapporti / area filter trop strict | Vérifier us_table.rapporti |
| "rapporti doivent être TEXT" | Saisi un nombre comme integer | Les champs US/Area sont **TEXT**, pas integer |
| Mauvaise capitalisation des rapporti | "copre" en minuscules dans le DB | Utiliser "Copre", "Coperto da" en majuscules |
| `DeprecationWarning` sur fichier 5.5.x | Fichier legacy `ActivityNodeGroup + group_kind` | Le projector le promeut en mémoire vers `LocationNodeGroup`. Réexporter pour migrer le fichier sur disque. |
| Les lignes de la swimlane affichent un texte très long | Les versions précédentes utilisaient la Descrizione de la périodisation comme étiquette | Mettre à jour le plugin et réexporter, et/ou remplir **Datazione estesa** avec un nom court |
| Les époques de la swimlane sont dans le mauvais ordre (ex. Bronze au-dessus de l'Antiquité tardive) | Les lignes sont triées par **Chronologie Initiale** ; les dates av. J.-C. saisies comme nombres positifs (1650 au lieu de -1650) sont triées comme apr. J.-C. | Dans la Fiche Périodisation, saisir les années av. J.-C. comme nombres négatifs et réexporter. Le résumé de l'export affiche désormais un avertissement "⚠️ Periodizzazione: ..." avec la liste des périodes à corriger |

---

## 8. Documentation technique

Pour approfondir l'architecture, les décisions de design et la roadmap :

- Specs : `docs/superpowers/specs/2026-05-*-design.md`
- Plans : `docs/superpowers/plans/2026-05-*.md`
- Dev log : `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over différés :
- **AI08-F3** : heuristiques d'auto-layout (bin-packing des sous-groupes) — toujours différé
- **AI09** : TimeBranchNodeGroup mapping — futur
- **Phase 3** : SyncEngine + REST API — futur
- **Phase 4** : GraphDBBackend + SPARQL — futur

Livré :
- **AI07** (5.6.0-alpha, 2026-05-10) : migration `LocationNodeGroup` avec enum `kind` + chaîne toponymique + appartenances multidimensionnelles
- **AI08-F1** (fusionné dans AI07) : nesting hiérarchique natif via `is_primary`

---

## 5. yEd-aware Import — importer des graphmls édités en externe (5.8.x)

À partir de **5.8.0-alpha** le bridge est **bidirectionnel également pour les graphmls créés directement dans yEd** (c'est-à-dire sans passer d'abord par un export pyarchinit). Pyarchinit reconnaît automatiquement les graphmls « yEd-raw » — ceux qui ne portent pas les data keys `pyarchinit.*` — et les importe via un dispatch dédié qui mappe le préfixe du label de nœud → type stratigraphique, reconnaît les lignes de TableNode comme périodes, parcourt les group folders comme dimensions archéologiques et laisse l'utilisateur choisir une politique pour les edges qui touchent des folders.

### 5.1 Déploiement en 6 jalons

| Jalon | Tag | Apport |
|---|---|---|
| **yE-A** | `yed-import-foundation-5.7.5-alpha` | `yed_detector.py` — flag de flavor `yed-raw` / `pyarchinit-projected` |
| **yE-B** | `yed-import-classifier-5.7.6-alpha` | `yed_classifier.py` — enum `ClassificationKind` à 13 valeurs (US/USV/SF/VSF/RSF/DOC/COMB/PROP/...) + regex order-sensitive |
| **yE-C** | `yed-import-parsers-5.7.7-alpha` | `yed_table_parser.py` (PeriodCandidate depuis les lignes de TableNode) + `yed_group_walker.py` (FolderCandidate avec auto-dimension depuis le préfixe du label : VA01→attivita / AR01→area / etc.) |
| **yE-D** | `yed-import-pipeline-5.8.0-alpha` | `yed_import_pipeline.py` — orchestrateur `import_yed_raw()` + 5 write functions + `FolderEdgePolicy` (SKIP/FAN_OUT/REPRESENTATIVE/SYNTHETIC) + paradata via `ParadataStore` + sentinelle `_DryRunRollback` + DbHandle PG+SQLite |
| **yE-E** | `yed-import-dialog-5.8.2-alpha` | `gui/yed_import_dialog.py` — `YedImportDialog(QWizard)` à 5 pages (classifier / periods / folders / policy / preview) + dataclass `YedOverrides` + persistance sidecar `<graphml>.yed_overrides.json` |
| **yE-Closure** | `yed-import-closure-5.8.3-alpha` | Cette documentation + dev-log + CHANGELOG. |

### 5.2 Comment ça marche — flux utilisateur

1. **Ouvrez un graphml dans QGIS via le menu Import GraphML** (même path que le flux pyarchinit-projected existant).
2. Pyarchinit détecte automatiquement qu'il s'agit de yEd-raw (pas de keys `pyarchinit.*`) → dispatche vers le nouveau branch au lieu de retomber sur le path legacy.
3. L'assistant `YedImportDialog` s'ouvre avec **5 pages** :
   - **1/5 Classifier** — tableau avec une ligne par leaf node. Chaque ligne affiche `label` + `auto_kind` (par ex. `us_real` / `usv_virtual` / `property`) + une combobox d'override `user_kind`. Le bouton **Accepter auto** remet chaque ligne à son `auto_kind` (efface tous les overrides).
   - **2/5 Periods** — une ligne par TableNode-row parsée, colonnes éditables `periodo` + `fase`. Les dates (`datazione_iniziale`/`finale`) restent vides : les graphmls yEd-raw ne portent pas de dates.
   - **3/5 Folders** — une ligne par group folder. Combobox `dimension` (attivita / area / struttura / settore / ambient / saggio / quad_par / `skip` pour exclure). `value` éditable (default = `auto_value` dérivé du préfixe du label).
   - **4/5 Rapporti policy** — 4 radio buttons pour traiter les edges qui touchent des folders :
     - **SKIP** (default) : abandonne les edges folder-touching. Les edges leaf-to-leaf passent intactes.
     - **FAN_OUT** : une edge `folder_A → folder_B` se développe en `N×M` paires de leaves (produit cartésien des membres).
     - **REPRESENTATIVE** : utilise le premier membre de chaque folder comme proxy.
     - **SYNTHETIC** : crée une ligne us_table par folder (`unita_tipo='VA'` virtual activity) + reconnecte les edges via ces ancres.
   - **5/5 Preview** — dry-run de `import_yed_raw(overrides=..., dry_run=True)`. Affiche les counts (us / inv / period / paradata) **sans commit**. Cliquer **Finish** valide, **Cancel** abandonne.
4. Au clic sur **Finish**, l'assistant enregistre vos overrides dans un **sidecar JSON** `<graphml>.yed_overrides.json` à côté du fichier. Rouvrir le même graphml précharge le sidecar : vos overrides précédents reviennent pré-appliqués.

### 5.3 Routage des destinations

Le dispatch utilise `_classify_destination` (dans `yed_import_pipeline.py`) pour aiguiller chaque leaf :

| ClassificationKind | Destination | Note |
|---|---|---|
| US_REAL | `us_table` (`unita_tipo='US'`) | depuis label `^US\d+` |
| US_MASONRY | `us_table` (`unita_tipo='USM'`) | depuis `^USM|USR|USS` |
| US_DOCUMENTARY | `us_table` (`unita_tipo='USD'`) | depuis `^USD\d+` |
| USV_VIRTUAL | `us_table` (`unita_tipo='USV'`) | depuis `^USV\d+` |
| USV_FORMAL | `us_table` (`unita_tipo` dérivé du préfixe du label : USVs/USVn/USVc) | depuis `^USVs|USVn\d*$` |
| **REUSED_SPECIAL_FIND** (RSF — **5.8.1**) | `us_table` (`unita_tipo='RSF'`) | depuis `^RSF\d+` (s3dgraphy 0.1.42, spolia) |
| SPECIAL_FIND | `inventario_materiali_table` | depuis `^SF\d+` |
| VIRTUAL_FIND | `paradata` (via `ParadataStore`) | depuis `^VSF\d+` |
| DOCUMENT | `paradata` | depuis `^D\.\d+` |
| COMBINER | `paradata` | depuis `^C\.\d+` |
| PROPERTY | `paradata` | mot-clé dans le label (`material`/`position`/`width`/...) |

**Décision utilisateur 2026-05-13** : les USV* (virtuelles) sont des « unità tipo » (toujours des unités stratigraphiques) et vont dans `us_table`, pas dans paradata. Seuls DOC/COMB/PROP/VIRTUAL_FIND restent dans paradata.

### 5.4 Sidecar JSON — schéma

Versionné pour la forward-compat :

```json
{
  "version": 1,
  "saved_at": "2026-05-13T17:57:00+00:00",
  "graphml_path": "/absolute/path/to/file.graphml",
  "classifier": {
    "n0::n0::n0": "us_real",
    "n0::n0::n2": "us_real"
  },
  "periods": {
    "p0": {"periodo": 5, "fase": 7}
  },
  "folders": {
    "f0": {"dimension": "struttura", "value": "S01"}
  },
  "policy": "fan_out"
}
```

Seuls les champs MODIFIÉS par l'utilisateur sont persistés (diff). Les valeurs `ClassificationKind` inconnues (par ex. issues de futures releases de s3dgraphy) sont silencieusement skippées au chargement.

### 5.5 CLI pour ingest scripté

Pour CI / re-runs batch :

```bash
python scripts/import_yed_graphml.py /path/to/file.graphml \
    --site Al-Khutm \
    --db /path/to/khutm2.sqlite \
    --policy skip \
    --overrides /path/to/file.graphml.yed_overrides.json \
    --dry-run
```

Mutex `--db` / `--conn-str` pour backend SQLite vs PostgreSQL. `--overrides` est optionnel (pas d'overrides = defaults yE-D). `--auto-defaults` est un flag no-op forward-compat.

### 5.6 Limitations connues

- **Pas d'édition des dates dans l'assistant** : les graphmls yEd-raw ne portent pas `datazione_iniziale`/`datazione_finale`. La page Periods n'édite que `periodo` + `fase` (les targets FK).
- **API ParadataStore partielle** : l'upstream s3dgraphy ne fournit pas encore `add_virtual_us` / `add_document` / `add_combiner` / `add_property`. yE-D logge « skip — method missing » par leaf paradata mais comptabilise les tentatives dans le preview.
- **PropertyNode → Path B (pas de lien US)** : les nœuds PROPERTY sont écrits sans US cible. L'assistant émet un warning. Futur : follow-up yE-Closure pour ajouter « assign target » dans l'UI.
- **Multi-DB** : le sidecar JSON est par graphml, pas par DB. Importer le même graphml dans plusieurs DBs réutilise les mêmes overrides pour toutes.

### 5.7 Couverture de tests finale

| Suite | Test | Couverture |
|---|---|---|
| yE-A | `test_yed_detector.py` | détection de flavor |
| yE-B | `test_yed_classifier.py` | 13 ClassificationKind + regex order-sensitive |
| yE-C | `test_yed_table_parser.py` + `test_yed_group_walker.py` | parse PeriodCandidate + FolderCandidate |
| yE-D | `test_yed_rapporti_policy.py` (7) + `test_yed_import_pipeline.py` (15) + `test_yed_pipeline_integration.py` (9 incl. 2 L1 overrides e2e) | policies + write functions + dispatch |
| yE-E | `test_yed_import_dialog.py` (5 sidecar JSON) + `test_import_yed_graphml_cli.py` (3) | persistance sidecar + CLI |

**Suite totale post-rollout** : 354 passed / 42 skipped (PG-L1 requièrent psycopg2).

### 5.8 Mise à jour 5.8.5-alpha (yed-fastfix)

Pack de corrections comportementales au-dessus de `5.8.3-alpha` qui améliore la qualité du ré-export GraphML après un import yEd-aware. Changements visibles pour l'utilisateur final :

- **Paradata multi-folder** : les labels DOC / Combinar / Extractor / property partagés entre plusieurs folders yEd (ex. `material` référencé depuis VA01 + VA04 + VA05) créent désormais UNE ligne dans `us_table` PAR occurrence — visibilité multi-folder restaurée dans le GraphML ré-exporté. Compromis : la dédup par identité (fusion de `D.01` / `D.01-2` / `D.01bis` en une seule ligne) ne s'applique plus à la deuxième/troisième occurrence.
- **Rapporti réciproques** : chaque edge yEd `a → b` écrit le rapporto direct sur la ligne de `a` ET l'inverse sur la ligne de `b` (`<<` / « Coperto da » / etc.). Les DOC affichent maintenant toutes les connexions extractor entrantes dans le formulaire Scheda US.
- **Strip du préfixe `us` numérique** : `US100` → `us='100'` `unita_tipo='US'` (avant `us='US100'`). SF/VSF/RSF sont écrits en double dans `us_table` + `inventario_materiali`.
- **Auto-fill periodo/fase** : l'appartenance d'une ligne TableNode yEd à une période se propage vers `us_table.periodo_iniziale`/`fase_iniziale` + `periodizzazione.cont_per`.
- **Classifier BPMN-aware** : `D.NN` (BPMN data-object) → `DocumentNode`, `D.NN.MM` (plain) → `ExtractorNode` — préserve la distinction sémantique EM 1.5.
- **Ré-import idempotent** : ré-exécuter le même import saute les lignes déjà présentes ; aucun rollback pour collision UNIQUE lors d'une passe répétée.
- **Palette USV** : les nœuds USV s'affichent désormais avec le parallélogramme bleu canonique EM (auparavant rectangle à bordure rouge).

### 5.9 yE-F paradata multi-dossiers (5.9.0-alpha)

Évolution structurelle de `yed-fastfix-5.8.5-alpha` : le compromis du Bug R B1 (une ligne `us_table` par occurrence, avec `us='D.01_2'` / `us='D.01_3'`) a été dépassé. Une feuille paradata (DOC / Combinar / Extractor / property) partagée entre plusieurs dossiers yEd produit désormais **une seule ligne** dans `us_table` par label canonique, et la multi-appartenance est conservée dans une nouvelle colonne `other_locations`.

Changements visibles pour l'utilisateur final :

1. **Nouveau widget « Autres activités » dans la fiche US/USM** : dans l'onglet *Periodizzazione* apparaît un `QListWidget` étiqueté « Autres activités » — visible **uniquement** lorsque `unita_tipo` est une typologie paradata (`DOC`, `Combinar`, `Extractor`, `property`). L'utilisateur peut sélectionner plusieurs codes d'activité ; la sélection est sérialisée comme liste JSON dans la nouvelle colonne `other_locations`.
2. **Nouvelle entrée de menu QGIS** : `Plugins → pyArchInit → Migrazioni → Aggiungi colonna other_locations (yE-F)`. Doit être exécutée **une fois** sur chaque DB préexistante pour ajouter la nouvelle colonne (les DB créées après 5.9 ont déjà la colonne).
3. **Import yEd-aware amélioré** : une feuille paradata qui apparaît dans N dossiers yEd génère désormais **une seule** ligne `us_table` (plus de N lignes avec suffixe `_2`/`_3` comme en 5.8.5). Le premier dossier rencontré devient l'`attivita` principale ; les dossiers secondaires sont listés dans `other_locations`. À l'**export**, N copies visuelles yEd sont émises (une par dossier), toutes partageant le même `node_uuid` canonique pour garantir l'identité round-trip.

**Rétrocompatibilité** : les données produites par le Bug R B1 en 5.8.5-alpha (lignes avec suffixe `_2`/`_3`) restent lisibles sans aucune conversion automatique. La nouvelle logique s'applique aux nouveaux imports ; les lignes legacy continuent de se comporter comme avant.

Prédécesseur : voir la section 5.8 (`yed-fastfix-5.8.5-alpha`) pour le comportement remplacé.

---

## 6. Générer la continuité (fiches CON)

Dans le panneau **« Verifica rapporti »** — disponible sous forme d'onglet dans la boîte de dialogue d'import/export s3dgraphy — se trouve le bouton **« Genera continuità »** (libellé conservé en italien comme dans le plugin). Pour le site actuellement sélectionné, cette fonction crée automatiquement les **fiches de continuité** des US/USM dont la vie s'étend sur plus d'une période.

### 6.1 Ce qu'elle fait

1. Elle parcourt toutes les US/USM du site dont la **période initiale ≠ période finale** (c'est-à-dire dont la vie s'étend sur plusieurs périodes).
2. Pour chacune, elle crée ou met à jour une fiche de continuité nommée **`CON_<us>`** (p. ex. `US5` → `CON_US5`).
3. La fiche CON **hérite** de l'unité mère : site, aire (plus les aires secondaires), structure et tout l'arc des périodes (initiale → finale). Sa description est générée automatiquement.
4. Elle écrit une **relation de continuité réciproque** des deux côtés : sur la CON et sur son unité mère.

> **La phase, à elle seule, ne compte pas.** La règle regarde la **période** : une USM qui va de **2/3 à 2/4** — même période, seule la phase change — ne génère rien. Si vos unités survivent de phase en phase à l'intérieur d'une même période, cochez **« anche i salti di fase »** (« aussi les sauts de phase ») à côté du bouton : ces sauts comptent alors aussi, à condition que les **deux** phases soient renseignées. Une unité qui ne bouge pas — même période et même phase — n'est jamais une continuité. La case part **décochée**, et vaut pour l'aperçu et pour l'écriture ensemble.

### 6.2 Idempotence

L'opération est **idempotente** : la relancer ne duplique pas les fiches existantes — elle met à jour les `CON_<us>` existantes si les données de l'unité mère ont changé.

### 6.3 Aperçu (dry-run) et sauvegarde

Avant l'écriture, un **aperçu dry-run** est affiché avec les comptages : combien de fiches à **créer**, à **mettre à jour**, **inchangées** et combien d'**orphelines**. Les modifications ne sont appliquées **qu'après confirmation** (bouton « Genera »). À l'application, une **sauvegarde de la base de données** automatique est effectuée au préalable.

Une fiche CON est **orpheline** lorsque son unité mère ne s'étend plus sur plusieurs périodes (p. ex. ses périodes initiale et finale ont été rendues égales). Par défaut, les orphelines sont seulement **signalées** ; une **case à cocher** (« Rimuovi anche le CON orfane ») permet d'opter pour leur suppression.

**Une continuité écrite à la main est reconnue.** Une fiche CON dont les relations nomment une seule unité — `> 12`, ou « Continuité après 12 » — est la continuité de cette unité, quel que soit son nom : le générateur la **met à jour** (étendue des périodes, libellé canonique) et le nom reste le sien. Il n'en naît pas une seconde : la continuité est **une par unité**. Si une `CON_<us>` canonique existe aussi, c'est elle qui gagne et l'autre reste une orpheline à trancher à la main.

### 6.4 Dans l'export Extended Matrix

Les fiches `CON_<us>` ainsi générées apparaissent dans l'**em.json** de l'Extended Matrix comme **éléments de continuité** (l'export GraphML est retiré, §2.3).

---

## 7. Vérification des paradoxes temporels (stratigraphiques)

Dans le panneau **"Verifica rapporti"** (Vérifier les rapports — un onglet du dialogue d'import/export s3dgraphy), la vérification signale désormais aussi les **paradoxes temporels** : lorsque la période/phase attribuée à une unité contredit la stratigraphie observée. La stratigraphie est la donnée de référence, c'est pourquoi les corrections automatiques déplacent les **périodes**, pas les rapports.

### 7.1 Ce qu'elle détecte
- **Inversion temporelle** : deux unités datées liées par un rapport d'ordre (ex. US5 « couvre » US7) où l'unité la plus récente dans la stratigraphie s'avère entièrement plus **ancienne** par période.
- **Contemporanéité incohérente** : unités déclarées contemporaines (égalité physique / lien) mais avec des intervalles chronologiques **disjoints**.
- **Non évaluable** : rapport d'ordre dans lequel au moins une des deux unités n'a pas de période datable (uniquement signalé, aucune correction).

Note sur la limite : deux périodes **adjacentes qui se touchent** en un seul point chronologique sont considérées comme superposées → ce **n'est pas** un paradoxe (bénéfice du doute).

### 7.2 Correction automatique et suggestions
- Lorsqu'un seul déplacement résout le conflit, la vérification propose de déplacer l'unité **mono-période** en conflit avec la majorité de ses voisins, en choisissant la période au déplacement minimal ; pour les contemporanéités avec une unité non datable, elle copie la période du voisin daté.
- Dans les cas ambigus — égalité, unités **multi-périodes** (ex. fiches CON), aucune période valide — elle ne corrige pas automatiquement : elle fournit une **suggestion « quoi + comment »** (ex. « Déplace US5 vers une période ≥ 3, ou US7 vers une période ≤ 1, ou vérifie le rapport »).

### 7.3 Aperçu et sauvegarde
- L'**aperçu** montre les modifications de période proposées avant de les appliquer.
- Avant l'écriture des périodes, une **sauvegarde automatique de la base de données** est effectuée (SQLite et PostgreSQL).
- Après l'application, relance la vérification pour contrôler d'éventuels paradoxes résiduels.

---

## 8. Vérification de la chronologie (périodisation et fiches)

Dans le même panneau **"Verifica rapporti"** (Vérifier les rapports — un onglet du dialogue d'import/export s3dgraphy), depuis la version 5.13.64-alpha la vérification trouve et corrige aussi les problèmes de **chronologie** du site sélectionné. La vérification des paradoxes temporels (section 7) compare la période d'une unité avec la stratigraphie ; celle-ci compare la périodisation avec elle-même et avec les fiches US qui la copient.

### 8.1 Ce qu'elle détecte

L'arbre du panneau regroupe les problèmes par type. À côté des groupes de relations, quatre nouveaux groupes apparaissent :

| Groupe | Ce qui est signalé | Traitement |
|--------|--------------------|------------|
| **Phases à intervalles qui se chevauchent** | Deux lignes de la périodisation dont les intervalles d'années se recoupent | Manuel : le panneau ne propose de resserrer les intervalles que si, après resserrement, il reste un intervalle utilisable |
| **Datation de la fiche désalignée** | Le champ `datazione` de la fiche US dit autre chose que la `datazione_estesa` de sa période/phase | Automatique : la périodisation est la source et la fiche est la copie ; la copie est donc réécrite à partir de la source. Un champ vide est rempli de la même façon. Une US sans période est ignorée, car il n'y a rien à copier |
| **Périodisation dont le début suit la fin** | `cron_iniziale` supérieur à `cron_finale` | Manuel : il s'agit probablement de dates av. J.-C. sans le signe moins — le panneau propose de réécrire les deux années en négatif (`-1650` au lieu de `1650`) ; s'il s'agit plutôt d'une coquille, échangez les deux valeurs à la main |
| **Phase sans années** | Une phase dont les années sont absentes ou illisibles | Signalée seulement : il n'y a rien dont elles puissent hériter |

Un exemple pour les chevauchements. La base d'exemple en compte deux, et aucun n'a de proposition : les deux phases ont des intervalles **identiques**, et tout resserrement ferait finir une phase avant son début. Le panneau se contente de le dire ; la décision (fusionner les phases, corriger les années, laisser en l'état) revient à l'archéologue.

### 8.2 Correction automatique et suggestions

**Corrections automatiques et propositions.** Les corrections automatiques sont **déjà cochées** ; les propositions **ne le sont pas** et ne sont appliquées que si l'on coche la case. La règle était différente auparavant : un problème dont la correction demandait une décision humaine ne pouvait être que lu. Il a maintenant une case, laissée vide. Cela vaut aussi pour les deux catégories de relations plus anciennes qui offrent une suggestion, à savoir la contradiction directe et le cycle stratigraphique.

Pour utiliser le panneau :

1. Sélectionnez dans le panneau le **site** à vérifier. La vérification est **par site** : elle n'examine que le site choisi et ne corrige que celui-ci. Dans une base de dix sites, cela compte, car les mêmes numéros d'US existent dans tous.
2. Lisez la **ligne de synthèse** au-dessus de l'arbre : elle indique combien il y a de problèmes, combien sont corrigibles automatiquement et **combien sont des propositions à cocher à la main**.
3. Ouvrez les groupes et sélectionnez un problème pour lire son détail dans le panneau d'aperçu.
4. Contrôlez les cases. Les corrections automatiques sont déjà cochées : décochez celles que vous ne voulez pas appliquer. Cochez les propositions que vous approuvez.
5. Appliquez les corrections. Avant toute écriture, une **sauvegarde automatique** est créée (copie du fichier SQLite, ou `pg_dump` pour PostgreSQL dans `~/pyarchinit_5/pyarchinit_DB_folder/_pga_backups`) ; la sauvegarde, qui existait déjà pour les corrections des champs de période, couvre désormais aussi les corrections chronologiques.
6. Si le résultat ne convient pas, cliquez sur **Annulla ultimo fix** (annuler la dernière correction) : l'annulation rétablit aussi les corrections écrites dans la table de périodisation.

### 8.3 Aperçu et sauvegarde

**L'aperçu montre la date calculée.** Pour chaque unité citée par un problème, le panneau d'aperçu affiche sa date calculée dans une ligne comme celle-ci :

`US 4 · 1500–1549 · epoca · has_first_epoch → epoch_2_2`

La ligne indique, dans l'ordre, l'intervalle d'années, la règle qui l'a produit et la relation le long de laquelle la contrainte a voyagé, avec le nœud d'où elle vient. Quand les deux bornes de l'intervalle viennent de chemins différents, chacune est étiquetée (`inizio …` et `fine …`), de sorte qu'une date n'est jamais attribuée à la mauvaise relation. Aujourd'hui, dans une base normale, chaque unité tire ses dates de sa propre période : la plupart des lignes indiqueront donc `epoca`. L'intérêt de la ligne n'est pas de surprendre, mais de permettre de voir **d'où vient** une date.

---

## 9. Comment lire les arcs de la matrice

Certains choix du dessin de la matrice peuvent surprendre, mais ce ne sont pas des erreurs :

- **Une flèche ne passe jamais sous un nœud.** Quand la colonne d'arrivée est occupée, la flèche entre dans la case **par le côté** : c'est normal.
- **L'égalité n'est pas un chevauchement.** Une relation « Uguale a » (Égal à) ou « Si lega a » (Se lie à) place les deux unités sur la **même ligne**, côte à côte, reliées par **deux lignes horizontales** (le signe égal) **sans pointe de flèche**.
- **Les arcs redondants ne sont pas dessinés.** Si l'US 1 recouvre la 2 et la 2 recouvre la 3, la flèche de 1 à 3 n'apparaît pas, car elle n'ajoute rien. Dans un **cycle**, en revanche, tous les arcs restent, parce qu'un cycle est une erreur qu'il faut voir.
- **Les lignes disent quelle relation elles sont.** Grise et pleine : la séquence (recouvre, remplit, s'appuie). **Pointillée verte** : une coupe (`Taglia` / `Tagliato da`), quelle que soit la définition stratigraphique et dans toutes les langues. **Épaisse et noire** : la continuité — un petit losange noir sans nom (le nom apparaît au survol), dans la colonne de son unité, donc la ligne est droite. **Rouge** : une flèche qui remonte les bandes, c'est-à-dire une contradiction entre stratigraphie et chronologie ; une coupe qui remonte est rouge **et** reste pointillée.
- **Les paradonnées ne sont jamais une ligne pleine.** Elles prennent couleur et trait des règles de l'Extended Matrix (`em_visual_rules.json`) : brun-rouge pointillé « extrait de », orange tireté « provenance de la donnée », or tireté « propriété », gris tireté « connexion générique », rouge tomate tireté « combine » (plein dans le fichier : la seule dérogation, parce qu'un arc vers un document ne doit pas ressembler à une superposition).
- **Un bord brun est une maçonnerie.** Les USM — WSU, MSE, UEM, USZ, ΤΣΜ dans les autres langues — ont la même case que les US, avec le bord brun au lieu de rouge.

---

## 10. Narration avec l'IA

À partir de la version **5.13.106-alpha**, le panneau de la matrice dans QGIS (§2.2, « Vedi la matrice ») a deux onglets dans sa colonne de droite : **Units** (*Unità* ; traduction : Unités) — la fiche de l'unité choisie, le zoom sur la géométrie et les médias, comme avant — et **Narrative** (*Narrativa* ; traduction : Narration), qui est nouveau. L'onglet Narrative fait écrire à une IA l'**histoire du site**, un chapitre par époque, puis permet de la lire, de la faire valider par une personne et de l'exporter en HTML, en DOCX ou en PDF. Il lit et écrit **le même em.json** qu'ouvre EMStudio, au format de la bibliothèque s3dgraphy : la narration que vous voyez ici est celle qu'EMStudio montre dans son onglet *Narrative*.

> **Aucun nouveau paramètre.** L'onglet n'a pas de fenêtre de configuration propre : il utilise l'IA que vous avez déjà configurée ailleurs dans pyArchInit (§10.2).

> **L'IA écrit des brouillons, pas des textes définitifs.** Chaque paragraphe écrit par le modèle reste un « AI draft » (brouillon IA) tant qu'une personne ne l'a pas validé (§10.6), et dans les documents exportés il porte la marque ⚠.

Les noms des onglets et des boutons de l'onglet Narrative existent en italien et en anglais : **ils sont en italien si QGIS est en italien, en anglais avec toute autre langue** (donc en anglais avec QGIS en français). Les deux sont toujours indiqués ici. Les entrées de menu et les fenêtres de dialogue du plugin (comme « Vedi la matrice… » ou les trois boutons du §10.9) sont en revanche uniquement en italien ; la traduction française est donnée entre parenthèses.

### 10.1 Ouvrir l'onglet Narrative

1. Ouvrez le menu **Plugins → pyArchInit - Archaeological GIS Tools** et choisissez l'entrée **Extended Matrix → Vedi la matrice…** (Voir la matrice).
2. Choisissez le **site**.
3. pyArchInit exporte le site de la base de données vers `<home>/pyarchinit_EM_folder/<site>.em.json` — `<home>` est `~/pyarchinit_5`, ou le dossier indiqué par la variable d'environnement `PYARCHINIT_HOME` — et ouvre le panneau **« Matrice — `<site>` »**, ancré à droite de la fenêtre de QGIS. Le nom du fichier est celui du site, avec les caractères spéciaux remplacés par « _ » (par exemple « Scavo 1 » devient `Scavo_1.em.json`).
4. Dans la colonne de droite du panneau, cliquez sur l'onglet **Narrative**.

<!-- IMMAGINE: Capture d'écran du menu Plugins → pyArchInit - Archaeological GIS Tools avec l'entrée « Extended Matrix → Vedi la matrice… » -->
![Menu Vedi la matrice](images/36_extended_matrix_s3dgraphy/01_menu_vedi_matrice.png)
*Figure 1 : L'entrée « Extended Matrix → Vedi la matrice… » dans le menu du plugin*

<!-- IMMAGINE: Capture d'écran du panneau de la matrice ancré à droite, avec les onglets Units et Narrative -->
![Panneau à deux onglets](images/36_extended_matrix_s3dgraphy/03_pannello_due_schede.png)
*Figure 2 : Le panneau de la matrice avec les onglets Units et Narrative*

Il y a **un fichier par site, et il reste sur le disque** : il ne se trouve plus dans un dossier temporaire. C'est le fichier qu'ouvre EMStudio, et c'est là que la narration est écrite. Chaque fois que vous choisissez « Vedi la matrice… », le site est **réexporté depuis la base de données** et le fichier est réécrit ; la narration déjà présente est conservée (§10.8).

Vous pouvez aussi accéder à l'onglet depuis deux autres endroits :

- depuis l'entrée **Extended Matrix → Esporta sito in em.json…** (Exporter le site en em.json), qui, à la fin, propose le bouton « Narrativa con l'AI » (§10.9) ;
- depuis le bouton **Vedi la matrice** de la fenêtre « Esporta Extended Matrix » de la fiche US (§2.2) : il ouvre le même panneau sur le fichier que vous venez d'exporter, dans le dossier que vous avez choisi.

### 10.2 Quelle IA est utilisée

En haut de l'onglet Narrative, une ligne dit quelle IA il utilisera : **« Model: `<model>` (`<where it comes from>`) »**, suivie du rappel concernant EMStudio. S'il n'en trouve aucune, il écrit **« No AI configured: set it in the US form with “Report” (AI provider) or with “Query AI Database”. »** (c'est-à-dire : aucune IA n'est configurée ; réglez-la dans la fiche US avec le bouton « Report » (Provider AI) ou avec « Query AI Database ») et les boutons **Generate with AI** (Générer avec l'IA) et **Regenerate chapter** (Régénérer le chapitre) restent désactivés.

L'onglet lit les paramètres de l'IA **déjà enregistrés** par les autres fenêtres de pyArchInit, dans cet ordre, et utilise **le premier** qui a un modèle et — pour les fournisseurs en ligne — la clé API :

| # | Où elle est configurée | Comment l'onglet l'appelle (en / it) |
|---|------------------------|----------------------------------|
| 1 | Fiche US, bouton « Report » → fenêtre « Generatore di Report » (Générateur de rapports), groupe « Provider AI » | Report generator of the US form / Generatore di Report della scheda US |
| 2 | Fiche US, bouton « Query AI Database » | Query AI Database / Query AI Database |
| 3 | Fenêtre palimpsestr, bouton « Report AI (analisi descrittiva)… », sélecteur « Provider AI » | Palimpsest report / Relazione Palimpsest |
| 4 | Fenêtre « Generazione SQL con AI » (texte vers SQL : voir le tutoriel 30) | Text to SQL / Testo in SQL |

Les fournisseurs sont ceux des sélecteurs « Provider AI » : **OpenAI** et **Anthropic (Claude)** en ligne, avec la clé API saisie dans le champ « API key » ; **Ollama** et **LM Studio** sur votre propre ordinateur, sans clé. Le sélecteur enregistre votre choix dès que vous le changez. Si vous voulez un autre modèle, changez-le dans la fenêtre que l'onglet indique entre parenthèses (ou dans une fenêtre placée plus haut dans la liste). L'onglet relit les paramètres **à l'ouverture du panneau** : après les avoir modifiés, rouvrez la matrice.

### 10.3 L'onglet Narrative

```
┌─ Units ─┬─ Narrative ───────────────────────────────────────────────────────────────┐
│ Model: <model> (<where it comes from>) · If EMStudio has the                        │
│ file open, close it first: the last writer wins.                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Presentation — to be written                                                        │
│ Early 15th century — AI draft                                                       │
│ 15th century — endorsed                                                             │
│ Modern age — AI draft, truncated                                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ The text of the chosen chapter, units quoted by name.                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│ Chapter 3 of 9 · 15th century  *                                                    │
│ [Generate with AI]  [Regenerate chapter]  [Endorse…]                                │
│ [Prepare the chapters]  [Show on the map]  [Export…]  [Open in EMStudio]  [Cancel]* │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

\* La ligne de progression et le bouton « Cancel » ne sont visibles que pendant que l'IA écrit. Dans ce schéma, les lignes de la liste sont celles du site d'exemple.

<!-- IMMAGINE: Capture d'écran de l'onglet Narrative avec la liste des chapitres, le texte du chapitre choisi et les sept boutons -->
![Onglet Narrative](images/36_extended_matrix_s3dgraphy/04_scheda_narrativa.png)
*Figure 3 : L'onglet Narrative*

De haut en bas :

- **la ligne d'état** : le modèle utilisé (§10.2) et le rappel *« If EMStudio has the file open, close it first: the last writer wins. »* (si EMStudio a le fichier ouvert, fermez-le d'abord : c'est le dernier qui écrit qui l'emporte) ;
- **la liste des chapitres**, une ligne par chapitre : *Titre — état*. Un fichier d'une version précédente, divisé par sondage, montre tous les graphes : chaque ligne est précédée du nom du graphe entre crochets, par exemple `[Saggio A] 15th century — AI draft` ;
- **le texte du chapitre choisi** : la prose, avec les unités citées par leur nom — les noms sont des **liens** : un clic montre l'unité sur la carte (§10.10) ; sous le paragraphe où une unité est nommée pour la première fois apparaissent jusqu'à deux de ses photos (§10.11). Si le chapitre n'a pas encore de prose, vous voyez son espace réservé « [to be written: …] » ;
- **la ligne de progression**, seulement pendant la génération : « Chapter 3 of 9 · 15th century » ;
- **les boutons**, sur deux lignes.

Le résultat de chaque opération apparaît dans la barre de messages de QGIS, avec le titre « Narrative ».

Quand le fichier **n'a pas encore de narration**, la liste est vide et un texte dit : *« No narrative in the file: “Prepare the chapters” builds the outline (N chapters over epochs and activities), “Generate with AI” writes it. »* (c'est-à-dire : « Prepare the chapters » crée le plan, pour N chapitres répartis entre époques et activités ; « Generate with AI » l'écrit).

#### Les états d'un chapitre

| État (en / it) | Ce que cela signifie |
|----------------|----------------------|
| **to be written** / da scrivere | Le chapitre ne contient que l'espace réservé « [to be written: …] ». |
| **AI draft** / bozza AI | Il y a de la prose écrite par le modèle qu'aucune personne n'a validée. Un seul paragraphe suffit : si le chapitre compte ne serait-ce qu'un paragraphe non validé, c'est son état, même si le chapitre contient d'autre prose. |
| **endorsed** / convalidato | Toute la prose de l'IA a été validée par une personne. |
| **written** / scritto | Prose écrite par une personne (dans EMStudio). |
| **truncated** / troncato | S'ajoute à l'état (par exemple « AI draft, truncated ») : le modèle s'est arrêté parce qu'il a atteint la limite de longueur, et le texte s'arrête à mi-chemin. |

#### Les boutons

| Bouton (en) | En italien | Ce qu'il fait |
|-------------|------------|---------------|
| **Generate with AI** | Genera con l'AI | Écrit, **un à la fois**, tous les chapitres encore « to be written » — d'abord la **Presentation**, puis ceux d'époque (et d'activité) ; ceux qui sont déjà écrits ne sont pas touchés. S'il n'y a pas encore de narration, il crée d'abord le plan. Affiche la progression et le bouton **Cancel**. Actif seulement avec un fichier ouvert et une IA configurée. |
| **Regenerate chapter** | Rigenera capitolo | Réécrit **le chapitre choisi** dans la liste : le brouillon IA non validé est remplacé — mais seulement une fois que le modèle a répondu : si l'appel échoue, le brouillon d'avant reste — et les blocs déjà validés restent. Il s'active quand vous choisissez la Presentation ou un chapitre d'époque ou d'activité et qu'une IA est configurée ; pour « Where it is », il reste désactivé. |
| **Endorse…** | Convalida… | Ouvre un menu avec « This chapter » (Ce chapitre) et « All chapters » (Tous les chapitres), puis demande qui valide (§10.6). Actif quand il y a une narration. |
| **Prepare the chapters** | Prepara i capitoli | Crée **seulement le plan** des chapitres, sans IA : il fonctionne même si aucune IA n'est configurée, pour que vous puissiez écrire à la main dans EMStudio. Il ne touche pas à la prose déjà écrite et ajoute les chapitres des nouvelles époques. Résultat : « Chapters prepared: N. » |
| **Show on the map** | Mostra sulla mappa | Sélectionne et cadre sur la carte, **toutes ensemble**, les unités dont parle le chapitre choisi (§10.10) : celles citées dans la prose ou, si le chapitre n'est pas encore écrit, toutes celles de sa bande. Actif seulement si au moins une des unités dont parle le chapitre choisi est une ligne de la fiche US. |
| **Export…** | Esporta… | Enregistre la narration en HTML (avec la carte interactive du site, §10.7), en DOCX ou en PDF imprimable (§10.7), avec les photos des unités citées quand il y en a (§10.11). Actif quand il y a une narration. |
| **Open in EMStudio** | Apri in EMStudio | Ouvre l'em.json dans EMStudio. Si EMStudio est absent, la barre de messages renvoie à l'entrée de menu **Extended Matrix → Installa EMStudio…** (Installer EMStudio). |
| **Cancel** | Annulla | N'apparaît que pendant la génération : l'IA s'arrête **après le chapitre en cours** et ce qui a été écrit est enregistré. |

Pendant la génération, tous les boutons sont désactivés sauf **Cancel**.

### 10.4 Ce que l'IA écrit

**Quels chapitres.** Le plan est celui de la bibliothèque s3dgraphy (le gabarit « site_story ») :

- Depuis la **5.13.110-alpha**, la **Presentation** (Présentation) est un chapitre canonique que l'IA écrit comme les autres, à partir d'un briefing du site entier (voir « Le briefing de la Presentation » plus bas) ; auparavant elle restait un espace réservé. **Where it is** (Localisation) est l'autre chapitre canonique et reste un espace réservé « [to be written: …] » à écrire à la main dans EMStudio : il naît de la position du site, et la bibliothèque y met la carte. Il n'existe que si le graphe porte une position géographique. L'IA ne le génère pas.
- **Un chapitre par époque** (période/phase) qui a des unités, de la plus ancienne à la plus récente. Le titre est le nom de l'époque, c'est-à-dire la « Datazione estesa » (datation étendue) de la périodisation ; si elle manque, un nom générique comme « Period 8 Phase 1 » apparaît : renseignez-la dans la fiche Périodisation pour obtenir des titres lisibles. Une unité apparaît dans le chapitre de l'époque où elle naît et dans ceux des époques où elle survit.
- **Un chapitre par activité**, si le graphe contient des groupes d'activité. Un site exporté depuis la base de données n'en a normalement pas — le champ Activité de la fiche US voyage comme propriété de l'unité — et les chapitres sont alors ceux d'époque.

**Ce que reçoit le modèle.** Pour chaque chapitre d'époque ou d'activité, un *briefing* avec, pour chaque unité : nom, type et description ; les champs renseignés de la fiche US (définition stratigraphique et interprétative, interprétation, période et phase, datation, activité, structure, sondage, pièce, secteur, aire) ; les époques ; **les rapports stratigraphiques** avec les autres unités (recouvre, coupe, remplit, s'appuie sur, égal à…) avec leurs noms ; et, s'il y en a, les sources documentaires liées. Les unités sont présentées **de la plus ancienne à la plus récente**, en suivant les rapports. Au-delà de **80 unités** par chapitre, le briefing est coupé aux 80 premières. Il a aussi un plafond de longueur (environ 25 000 caractères) : au-delà, les longs textes des fiches sont raccourcis, les rapports répétés et les chaînes de preuves sont supprimés et, si cela ne suffit toujours pas, les unités les plus récentes sont omises. Dans les deux cas, le modèle est informé du nombre d'unités manquantes.

**Les règles.** Le modèle reçoit les cinq règles de la bibliothèque : n'écrire que ce que le contexte étaye (ni dates, ni matériaux, ni fonctions, ni événements inventés) ; préserver l'incertitude (une unité virtuelle est une hypothèse, non un fait) ; ne citer aucune source qui n'est pas présente ; écrire une prose continue, sans listes ni titres ; dire ouvertement quand le contexte est trop pauvre. On demande un à trois paragraphes.

**Le briefing de la Presentation.** La Presentation n'a pas d'unités propres : le modèle reçoit un briefing du **site entier**, tiré du graphe et non de la base de données, avec le nom du site ; la chaîne des toponymes (pays → région → province → commune) ; les lieux de la fiche US (aires, secteurs, sondages, pièces) ; les époques de la plus ancienne à la plus récente, chacune avec le nombre d'unités qui y sont présentes (une même unité peut se trouver dans plusieurs époques, la somme peut donc dépasser le total) ; le nombre d'unités et leurs types, et le nombre de rapports stratigraphiques ; les documents ; les personnes nommées dans les fiches US ; et les titres des chapitres du récit. Ses instructions sont celles de la Presentation, non les cinq règles ci-dessus : elles demandent deux à quatre paragraphes disant ce qu'est le site et où il se trouve, quelles époques couvre l'histoire, comment se lit ce récit (un chapitre par époque et par activité, les unités citées par leur nom et les brouillons signalés comme tels jusqu'à ce qu'une personne les valide) et sur quelles sources il s'appuie ; elles demandent aussi de n'utiliser que le briefing, sans inventer ni dates ni faits, et de laisser de côté une donnée qui paraît étrange au lieu de la commenter. La prose va **en tête** du chapitre ; les fiches des sources (les documents) restent après elle, et les espaces réservés « [to be written: a presentation of …] » et « [to be written: how this account is to be read…] » disparaissent.

**La langue.** La prose est dans la **langue de la narration**, qui est fixée quand le plan est créé pour la première fois : **l'italien si, à ce moment-là, QGIS est en italien, l'anglais avec toute autre langue** (le modèle ne reçoit ses instructions que dans ces deux langues). Une narration qui existe déjà garde sa langue même si vous changez ensuite celle de QGIS. Il en va de même pour les titres des chapitres canoniques et pour les espaces réservés.

**Comment la narration est enregistrée.** Au format de la bibliothèque, celui que lit EMStudio : un nœud de narration (`NarrativeNode`) qui contient les chapitres ; chaque paragraphe écrit par le modèle est un bloc « AI draft » attribué à l'**auteur IA** de ce modèle ; le **prompt** utilisé est enregistré comme un extracteur lié aux sources, de sorte que vous puissiez retrouver ce qui a été demandé. Les unités citées dans le texte sont des **mentions** (`[[name]]`) : dans le fichier, elles restent liées au nœud de l'unité, et dans l'onglet et dans les exports, elles apparaissent avec son nom. Une mention qui ne correspond à aucune unité du graphe est réduite à de simples mots, sans crochets.

**Coûts et durées.** Le modèle est appelé **une fois par chapitre**, Presentation comprise. Avec un fournisseur en ligne, chaque appel a un coût et un temps d'attente (lors des essais avec un modèle en ligne, quelques dizaines de secondes par chapitre : un site d'une dizaine d'époques demande quelques minutes) ; avec Ollama ou LM Studio, on ne paie rien, mais les durées dépendent de votre ordinateur.

### 10.5 Pas à pas

1. Ouvrez la matrice du site (§10.1) et cliquez sur l'onglet **Narrative**. Vérifiez en haut **quel modèle** il utilisera.
2. **Fermez EMStudio** s'il a le fichier ouvert : pyArchInit et EMStudio écrivent le même fichier, et c'est celui qui écrit en dernier qui l'emporte.
3. Facultatif : **Prepare the chapters** pour voir le plan, sans IA.
4. Cliquez sur **Generate with AI**. Suivez la progression : la Presentation, si elle est encore « to be written », passe en premier (« Chapter 1 of 9 · Presentation »), puis les chapitres d'époque (« Chapter 3 of 9 · … ») ; vous pouvez continuer à utiliser QGIS. À la fin, la barre de messages dit, par exemple, *« 7 chapters generated, 1 failed: Modern age — … »* (avec *« (cancelled) »* si vous avez annulé) et la liste se recharge : les chapitres écrits sont « AI draft ».
5. **Lisez** : choisissez un chapitre après l'autre et lisez le texte sous la liste. Confrontez-le à la stratigraphie : c'est un brouillon construit à partir des données de la fiche US. Pour voir où se trouvent les unités dont il parle, cliquez sur leurs noms ou utilisez **Show on the map** (Afficher sur la carte ; §10.10).
6. Si un chapitre ne vous convainc pas, choisissez sa ligne et cliquez sur **Regenerate chapter**. Le nouveau brouillon **remplace** le précédent non validé : si vous voulez conserver la version d'avant, exportez-la d'abord. Si un chapitre est « truncated », régénérez-le **avant** de le valider.
7. Quand un chapitre est correct, cliquez sur **Endorse…** (§10.6).
8. Exportez en HTML, en DOCX ou en PDF avec **Export…** (§10.7), ou ouvrez **Open in EMStudio** pour écrire à la main « Where it is » et peaufiner le reste.
9. Plus tard, vous pouvez rouvrir la matrice : la narration reste (§10.8).

<!-- IMMAGINE: Capture d'écran de la génération en cours : la ligne de progression « Chapter 3 of 9 · … » et le bouton Cancel -->
![Génération en cours](images/36_extended_matrix_s3dgraphy/05_generazione_in_corso.png)
*Figure 4 : Génération en cours, avec la ligne de progression et le bouton Cancel*

Un chapitre qui échoue n'arrête pas les autres : le récapitulatif dit lequel. Pour réessayer, il suffit de cliquer de nouveau sur **Generate with AI**, qui n'écrit que les chapitres encore « to be written ».

### 10.6 Valider : qui signe

Valider (bouton **Endorse…**) signifie qu'une **personne** assume la responsabilité du texte écrit par le modèle. Cela n'arrive jamais tout seul : ni en générant, ni en enregistrant.

1. Cliquez sur **Endorse…**. Un petit menu s'ouvre : **« This chapter »** — actif seulement si le chapitre choisi est un « AI draft » — ou **« All chapters »**, c'est-à-dire tous les brouillons IA pas encore validés, dans tous les graphes du fichier. La Presentation se valide comme n'importe quel autre chapitre : choisissez-la dans la liste et « This chapter » la valide à elle seule.
2. Une fenêtre demande **« Who endorses? Pick an author or type a new name. »** (Qui valide ? Choisissez un auteur ou saisissez un nouveau nom.) La liste contient les **auteurs humains déjà présents dans le graphe** — les personnes nommées dans la fiche US comme compilateur (*schedatore*), directeur US et responsable US — et vous pouvez saisir un nouveau nom, qui devient un nouvel auteur du graphe.
3. La barre de messages dit **« N blocks endorsed by `<name>`. »** (N blocs validés par le nom choisi), ou « Nothing to endorse. » (Rien à valider.) Le fichier est enregistré.

<!-- IMMAGINE: Capture d'écran du menu Endorse… (« This chapter » / « All chapters ») et de la fenêtre de choix de l'auteur -->
![Valider](images/36_extended_matrix_s3dgraphy/06_convalida.png)
*Figure 5 : Valider : le menu et le choix de l'auteur*

Les blocs passent de « AI draft » à « endorsed ». Dans le document exporté, la personne figure parmi les responsables (« a cura di », édité par) et le modèle comme assistant (« con l'assistenza di », avec l'assistance de), et les paragraphes validés ne portent plus la marque ⚠. Régénérer ne supprime pas les blocs validés : une signature est un acte, et elle ne se perd pas en réécrivant.

### 10.7 Exporter en HTML, en DOCX ou en PDF

Cliquez sur **Export…** : la fenêtre d'enregistrement s'ouvre avec trois formats : « HTML page » (page HTML ; `.html`), « Word document » (document Word ; `.docx`) et « Printable PDF » (PDF imprimable ; `.pdf`). Le nom proposé est `<site>_narrativa`, sans extension, dans le dossier de l'em.json : l'extension est ajoutée par le format choisi dans le filtre de la fenêtre ; une extension saisie à la main (`.html`, `.docx` ou `.pdf`) l'emporte sur le filtre. La barre de messages le confirme : « Narrative exported to `<path>` » (Narration exportée vers le chemin du fichier).

Le document contient :

- le titre de la narration (par exemple « Scavo archeologico — the story of the site » ; « the story of the site » : l'histoire du site), les responsables (« a cura di ») et le modèle comme assistant (« con l'assistenza di ») ;
- pour chaque chapitre, d'abord la prose, avec les unités citées par leur nom, puis la liste des unités du chapitre ; pour les unités citées qui ont des photos, une bande de photos prend la place de leur ligne (§10.11) ;
- **la carte du site** (depuis la 5.13.115-alpha, uniquement dans le HTML), dans un encadré fixe : à droite sur les écrans larges, en haut sur un téléphone. Avec la carte, la page s'élargit (depuis la 5.13.116-alpha) et le texte garde une colonne lisible. Au repos, elle montre toutes les unités du graphe en gris clair ; un clic sur le nom d'une unité dans le texte montre **seulement les unités de la période de ce chapitre** sous forme de contours avec le numéro dessus, l'unité cliquée **en couleur**, et cadre le groupe ; un clic sur le titre d'un chapitre fait de même, sans l'unité en couleur. La ligne sous la carte indique la période et le nombre d'unités ; « whole site » (tout le site) revient à la vue d'ensemble. Les géométries viennent des vues US et USM de la base de données du projet au moment de l'export (site du graphe, unités associées par aire et numéro) : une unité citée mais sans dessin a le lien et rien sur la carte ; sans base de données connectée, le document n'a pas de carte ;
- à la fin, la section **Fonti** (sources) : les documents sur lesquels s'appuie le récit et l'entrée « Prompt », qui renvoie au prompt enregistré dans le fichier.

Quelques points à connaître :

- les **brouillons non validés sont inclus**, chacun précédé de « ⚠︎ non validato da una persona » (non validé par une personne), et l'en-tête dit combien de blocs sont dans cet état. Pour un document sans marques, validez d'abord (§10.6). Dans le HTML, le brouillon se lit comme le reste du texte, avec la même police et le même fond : au-dessus du paragraphe figure la ligne d'avertissement et, à gauche, un filet ambre. Dans Word et dans le PDF, l'avertissement précède le paragraphe (dans le PDF, sur une ligne à part, sans le signe ⚠, §10.11) ;
- **tous les chapitres sont inclus**, même ceux qui sont encore « to be written » : leur espace réservé « [to be written: …] » reste dans le texte ;
- la prose est **en tête** du chapitre, avant la liste des unités ; dans une narration écrite avec une version précédente, elle peut encore être à la fin, et elle se remet à sa place en réexportant le site (§10.8) ou avec **Prepare the chapters** (Préparer les chapitres) ;
- les figures qu'un auteur a prévues dans EMStudio (par exemple la matrice d'une époque) ne sont pas dessinées par l'export de pyArchInit : un espace réservé reste dans le document ;
- le HTML est un fichier unique et autonome (les photos y sont aussi incorporées, et la carte est un SVG dans le fichier, sans bibliothèque externe : il s'ouvre aussi sur un téléphone sans réseau) ; le DOCX s'ouvre avec Word ou LibreOffice et nécessite le paquet `python-docx`, et le PDF la bibliothèque ReportLab (§10.11) : les deux font partie des dépendances du plugin.

<!-- IMMAGINE: Capture d'écran du document HTML exporté : un chapitre avec un brouillon précédé de « ⚠︎ non validato da una persona » -->
![Document HTML exporté](images/36_extended_matrix_s3dgraphy/07_documento_html.png)
*Figure 6 : Le document HTML exporté, avec un brouillon non validé signalé*

### 10.8 Réexporter le site : la narration reste

Réexporter le site depuis la base de données — avec **Vedi la matrice…**, avec **Esporta sito in em.json…** ou avec la fenêtre « Esporta Extended Matrix » de la fiche US — **conserve la narration** déjà présente dans le fichier de destination : prose, validations, auteur IA et prompts. Les époques apparues entre-temps reçoivent un chapitre « to be written ». Un avertissement le dit : **« Narrative kept from the previous file (N chapters). »** (Narration conservée depuis le fichier précédent (N chapitres).) Vous le voyez dans la barre de messages avec « Vedi la matrice… », dans le récapitulatif de la fenêtre « Esporta Extended Matrix » et, avec « Esporta sito in em.json… », dans les détails de la fenêtre finale.

Les **autres modifications** faites au fichier dans EMStudio — positions des nœuds, descriptions réécrites — **ne survivent pas**, comme avant : le fichier est régénéré à partir de la base de données. Seule la narration est conservée.

Avant de réécrire un fichier qui contient une narration, pyArchInit en fait une **copie de sécurité** à côté : `<site>.em.json.bak` (chaque nouvel export remplace la copie précédente).

Si le fichier d'avant était divisé par sondage (les versions jusqu'à la 5.13.108-alpha pouvaient exporter un graphe par sondage), à la première réexportation le nouveau fichier a **un seul graphe** pour tout le site : les graphes ont des noms différents et la narration **ne peut pas passer** dans le nouveau fichier. Un avertissement le dit : *« The previous file's narrative (graphs: …) did not travel into the new file (graphs: …): the file shape changed. Backup copy in … »* (La narration du fichier précédent (graphes : …) n'est pas passée dans le nouveau fichier (graphes : …) : la forme du fichier a changé. Copie de sauvegarde dans …). Le texte n'est pas perdu : il est dans la copie `.bak`, qui est toutefois remplacée par le prochain export d'un fichier qui contient une narration — mettez-la en lieu sûr. Si vous avez besoin de l'ancienne narration, ouvrez cette copie (renommée en un fichier `.em.json` portant un autre nom) ; sinon, régénérez les chapitres dans le nouveau fichier (§10.5). À partir de la 5.13.109-alpha, le fichier a toujours un seul graphe et la narration passe d'un export à l'autre.

Si le fichier précédent ne peut pas être lu (par exemple un fichier resté à moitié écrit), l'export se poursuit quand même : le fichier illisible est **renommé** `<site>.em.json.broken` et un avertissement dit *« The previous file cannot be read (…): its narrative, if any, was not kept. »* (Le fichier précédent est illisible (…) : sa narration, s'il y en avait une, n'a pas été conservée.)

> **La narration n'est pas dans la base de données de pyArchInit : elle vit uniquement dans l'em.json.** La sauvegarde de la base ne la copie pas. Copiez de temps en temps le dossier `pyarchinit_EM_folder`.

### 10.9 Depuis l'entrée « Esporta sito in em.json… »

L'entrée **Extended Matrix → Esporta sito in em.json…** écrit le même fichier `<site>.em.json` dans `pyarchinit_EM_folder`. À la fin, elle affiche « Esportato `<path>` » (Exporté), avec le décompte des nœuds, des arcs et des avertissements (le texte des avertissements se trouve dans les détails de la fenêtre), et **trois boutons** :

| Bouton | Ce qu'il fait |
|--------|---------------|
| **Apri in EMStudio** (Ouvrir dans EMStudio) | Ouvre le fichier dans EMStudio ; s'il n'est pas installé, propose de l'installer. |
| **Narrativa con l'AI** (Narration avec l'IA) | Apparaît **seulement si une IA est configurée** (§10.2) : ouvre le panneau de la matrice déjà sur l'onglet Narrative. |
| **Chiudi** (Fermer) | Ferme la fenêtre. |

<!-- IMMAGINE: Capture d'écran de la fenêtre finale de « Esporta sito in em.json… » avec les trois boutons -->
![Exporter le site en em.json : trois boutons](images/36_extended_matrix_s3dgraphy/08_esporta_tre_bottoni.png)
*Figure 7 : La fenêtre finale de « Esporta sito in em.json… »*

### 10.10 Les unités sur la carte

À partir de la version **5.13.108-alpha**, l'onglet Narrative amène sur la **carte de QGIS** les unités dont parle un chapitre, de deux façons :

- **Une seule unité : cliquez sur son nom.** Dans le texte du chapitre choisi, les noms des unités citées sont des **liens** : un clic sélectionne cette unité sur la couche US chargée et cadre la carte sur elle, avec un clignotement. Rien ne s'ouvre.
- **Toutes ensemble : « Show on the map »** (*Mostra sulla mappa* ; Afficher sur la carte), sur la deuxième ligne de boutons, entre « Prepare the chapters » (Préparer les chapitres) et « Export… » (Exporter…). Le bouton sélectionne et cadre ensemble toutes les unités dont parle le chapitre choisi : celles citées dans la prose ou, si la prose n'en cite aucune (par exemple parce que le chapitre n'est pas encore écrit), toutes les unités de sa bande (l'époque). La sélection est unique par couche — elle remplace celle qui existait — et le cadrage englobe toutes les géométries trouvées, qui clignotent.

<!-- IMMAGINE: Capture d'écran de QGIS avec les unités du chapitre sélectionnées sur la carte et, en haut, la barre de messages « Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9. » -->
![Les unités du chapitre sur la carte](images/36_extended_matrix_s3dgraphy/09_unita_sulla_mappa.png)
*Figure 8 : Les unités dont parle un chapitre, sélectionnées sur la carte, et la barre de messages*

Il faut qu'une couche contenant les géométries des US soit déjà chargée dans le projet, par exemple la **vue US** de pyArchInit : l'onglet la cherche parmi les couches chargées, comme le bouton « Zoom sulla geometria » (Zoom sur la géométrie) de l'onglet Units (tutoriel 01), en reconnaissant les unités grâce aux champs `sito`, `area` et `us`. **Le projet n'est pas modifié** : aucune couche n'est ajoutée, seuls la sélection et le cadrage de la carte changent. Depuis la **5.13.110-alpha**, si plusieurs couches portent les mêmes champs — comme la vue US (polygones) et la vue des cotes (points) —, l'onglet essaie d'abord la géométrie la plus pleine : polygones, puis lignes, puis points ; l'ordre des couches dans la légende ne compte que si tout le reste est égal. Cela vaut aussi pour le bouton « Zoom sulla geometria » : il n'est plus nécessaire de mettre la vue US en tête de la légende.

La barre de messages (« Narrative ») dit ce qui a été trouvé, par exemple « Highlighted 5 of 6 units in “US view” (7 geometries). Not drawn: 1.US9. » (5 unités sur 6 mises en évidence dans « US view », 7 géométries ; non dessinées : 1.US9). Le nom entre guillemets est celui de la couche où les unités ont été trouvées, tel qu'il apparaît dans le panneau des couches de QGIS ; une unité peut avoir plus d'une géométrie, donc les géométries peuvent être plus nombreuses que les unités. Seules les unités qui sont des lignes de la fiche US sont cherchées : un document ou un nœud de continuité n'a pas de géométrie et n'entre pas dans le décompte. Si plus de cinq unités ne sont pas dessinées, les noms s'arrêtent aux cinq premiers, suivis de « … » et du total.

Un clic sur un nom qui n'est pas une ligne de la fiche US ne trouve rien, et la barre de messages le dit. Si aucune couche chargée ne porte les champs pour reconnaître les unités, le message le dit : chargez la vue US (§10.13).

### 10.11 Les photos des unités et le PDF

À partir de la version **5.13.108-alpha**, la narration montre aussi les **photos** des unités dont elle parle — dans le texte de l'onglet et dans les exports — et peut en plus s'enregistrer en **PDF imprimable**.

**Dans le texte du chapitre.** Sous le paragraphe où une unité est nommée pour la première fois apparaissent **jusqu'à deux vignettes** de ses médias : ce sont les mêmes que dans l'onglet Units, lues dans le dossier des vignettes du projet, et dessous, en petits caractères, figurent le nom de l'unité et les noms des médias. Si l'unité est nommée de nouveau dans le même chapitre, les photos ne se répètent pas.

**Dans les exports.** Dans les trois formats, pour chaque unité citée dans la prose qui a des images sur le disque, une **bande avec une ou deux photos côte à côte** prend la place de la ligne de texte de l'unité, avec le nom de l'unité en légende : on utilise la copie réduite si elle existe, sinon la vignette. Les unités non citées dans la prose restent une ligne de texte. Les photos sont incorporées au fichier : le HTML et le DOCX sont écrits par la bibliothèque s3dgraphy, le PDF par pyArchInit.

**Le PDF imprimable.** C'est un document A4 que pyArchInit écrit avec ReportLab, dans la police Cambria comme les autres PDF du plugin (si le fichier de la police n'est pas dans le dossier `bin` de pyArchInit, il utilise Helvetica). Il contient le titre, les responsables (« edited by ») et le modèle comme assistant (« with the assistance of ») ; en tête, s'il y a des brouillons non validés, figure aussi un avis indiquant leur nombre ; puis tous les chapitres, comme dans les autres formats, chacun avec sa prose — les unités citées écrites par leur nom, et devant chaque paragraphe non validé une ligne « non validato da una persona » (non validé par une personne), sans le signe ⚠ — suivie des photos avec leur légende et des autres unités en petits caractères ; à la fin, les sources. En pied de page figurent « Generated by pyArchInit on … » (généré par pyArchInit le …) avec la date, et le numéro de page.

<!-- IMMAGINE: Captures d'écran côte à côte : le texte d'un chapitre avec les vignettes sous la première mention d'une unité, et une page du PDF imprimable avec la bande de photos et sa légende -->
![Photos des unités dans le texte et dans le PDF](images/36_extended_matrix_s3dgraphy/10_foto_e_pdf.png)
*Figure 9 : Les photos des unités dans le texte du chapitre et dans une page du PDF*

**Ce qu'il faut.** Les photos ne sont pas dans l'em.json : elles se lisent dans la base de données et les dossiers du projet. Il faut donc la base de données reliée (la matrice ouverte depuis le projet), les chemins **Thumbnail path** et **Image resize** réglés dans la configuration (tutoriel 01) et les fichiers sur le disque ; pour le texte, le dossier des vignettes suffit. Les images sur un stockage distant ne sont pas utilisées. S'il manque quelque chose, il n'y a aucun message : les photos n'apparaissent simplement pas, et l'export réussit quand même (§10.13).

### 10.12 Mises en garde

- **Fermez EMStudio avant de générer ou de valider.** Si EMStudio a le fichier ouvert, c'est celui qui écrit en dernier qui l'emporte.
- **Une IA n'écrit qu'à partir de ce qu'elle trouve dans le graphe, et elle peut se tromper.** Les règles l'encadrent, elles ne la rendent pas infaillible : lisez chaque chapitre avant de le valider.
- **Avec un fournisseur en ligne, les données quittent votre ordinateur.** Le briefing de chaque chapitre (noms, définitions, descriptions et rapports des unités) et celui de la Presentation (nom du site, toponymes, lieux, époques, documents et noms des personnes nommées dans les fiches US) sont envoyés au service choisi ; avec Ollama ou LM Studio, ils restent en local.
- **Le fichier est écrit à la fin.** La génération enregistre quand elle se termine, même si vous l'avez annulée : ne fermez pas QGIS pendant que l'IA écrit. L'enregistrement est sûr : le fichier est écrit à côté, relu, et ce n'est qu'alors qu'il remplace le vrai ; si quelque chose se passe mal, **le fichier précédent reste tel qu'il était**.
- **Ne rouvrez pas la matrice pendant que l'IA écrit.** L'onglet reste sur le fichier précédent et avertit : *« Generation in progress: wait for it to finish, or press Cancel, before changing file. »* (Génération en cours : attendez qu'elle se termine, ou appuyez sur Cancel, avant de changer de fichier.)
- **Le texte se modifie dans EMStudio**, pas dans pyArchInit.
- La narration et les nœuds qui la portent (auteur IA, prompts) **n'apparaissent pas dans le dessin de la matrice**.

### 10.13 Résolution de problèmes

| Message (en / it) | Cause | Solution |
|-------------------|-------|----------|
| « No AI configured… » / « Nessuna AI impostata… » | Aucune des quatre fenêtres du §10.2 n'a de modèle (et, pour OpenAI et Anthropic, la clé API). | Indiquez le fournisseur et le modèle — et la clé — dans l'une de ces fenêtres, puis **rouvrez la matrice** : l'onglet ne relit les paramètres qu'à l'ouverture. Même sans IA, vous pouvez préparer les chapitres, valider, exporter et ouvrir EMStudio. |
| « No narrative in the file… » / « Nessuna narrativa nel file… » | Le fichier n'a pas encore de narration (c'est normal la première fois). | Cliquez sur **Prepare the chapters** (plan) ou sur **Generate with AI** (plan et prose). Le nombre N compte les chapitres d'époque et d'activité que le plan aura (une époque sans unités n'en a pas) ; le message « Chapters prepared » compte aussi « Presentation » et, s'il existe, « Where it is ». « Generate with AI » écrit en plus la « Presentation », que N ne compte pas : la progression compte un chapitre de plus. |
| « EMStudio is not installed… » / « EMStudio non risulta installato… » | Le programme n'a pas été trouvé sur l'ordinateur. | Utilisez l'entrée de menu **Extended Matrix → Installa EMStudio…** (elle porte ce nom quelle que soit la langue de QGIS). |
| « truncated » / « troncato » à côté de l'état | Le modèle s'est arrêté à la limite de longueur et le texte s'arrête à mi-chemin. | Avant de valider, cliquez sur **Regenerate chapter** ; si cela se reproduit, terminez le chapitre dans EMStudio. |
| « N chapters generated, M failed: `<title>` — `<reason>` » / « N capitoli generati, M falliti: … » | Le fournisseur a refusé la requête (clé non valide, quota, modèle non disponible) ou le serveur local ne répond pas. « the model wrote nothing » signifie que la réponse était vide. | Éliminez la cause et cliquez de nouveau sur **Generate with AI** : il n'écrit que les chapitres restés « to be written ». |
| « The previous file cannot be read (…) » / « Il file precedente non si legge (…) » | Lors du réexport, le fichier existant n'était pas un em.json lisible. | L'export s'est poursuivi : le fichier illisible a été conservé à côté du nouveau sous le nom `….broken`, et la narration qu'il contenait, s'il y en avait une, n'est pas passée dans le nouveau fichier. Si vous en avez besoin, récupérez-la depuis ce fichier ou depuis une sauvegarde. |
| « The previous file's narrative (graphs: …) did not travel into the new file… » / « La narrativa del file precedente (grafi: …) non è passata nel file nuovo… » | Le fichier d'avant était divisé par sondage (versions jusqu'à la 5.13.108-alpha) : les graphes ont des noms différents et la narration ne peut pas passer. | Le fichier d'avant se trouve dans la copie `.bak` : ouvrez-la si vous avez besoin de l'ancienne narration, ou régénérez les chapitres dans le nouveau fichier. |
| « Could not write … The previous file is intact. » / « Non sono riuscito a scrivere … Il file precedente è intatto. » | L'enregistrement a échoué (disque plein, fichier verrouillé, autorisations). | Corrigez le problème et recommencez : les chapitres générés pendant cette session n'avaient pas été enregistrés. |
| « DocX export needs python-docx — install the extra: … » (toujours en anglais) | Le paquet `python-docx` n'est pas installé dans le Python de QGIS : il n'est nécessaire que pour le DOCX. | Installez `python-docx` (c'est l'une des dépendances du plugin), ou exportez en HTML, qui n'a besoin de rien. |
| « None of the loaded layers has the fields to recognise the units… » / « Nessuno dei layer caricati porta i campi per riconoscere le unità… » | Le projet ouvert n'a aucune couche portant les champs `sito`, `area` et `us` des unités (par exemple la vue US de pyArchInit) : l'onglet ne cherche que parmi les couches déjà chargées. | **Chargez la vue US** de pyArchInit (ou une couche avec les mêmes champs) dans le projet, puis cliquez de nouveau sur le nom ou sur **Show on the map** (Afficher sur la carte). L'onglet n'ajoute pas de couches de lui-même. Depuis la 5.13.110-alpha, il n'est pas nécessaire de la mettre en tête de la légende : à champs égaux, l'onglet essaie d'abord les polygones (§10.10). Chargée depuis la fiche US avec un style choisi (fenêtre « Style Choice », tutoriel 14), la vue US porte aussi le numéro de l'unité dans un cercle. Depuis la 5.13.111-alpha, la vue des cotes (points), chargée depuis la fiche US, porte aussi la cote (deux décimales) au-dessus du symbole. Le style et les étiquettes de la vue se définissent dans la fenêtre « View styles » (entrée de menu « View styles… », tutoriel 14) ; depuis la 5.13.112-alpha, un style par défaut enregistré là-bas commande au chargement. |
| Aucun message : les photos n'apparaissent ni dans le texte du chapitre ni dans les exports | Les photos se lisent dans la base de données du projet et dans ses dossiers, et il manque quelque chose : la base n'est pas reliée (la matrice a été ouverte sans elle), le chemin **Thumbnail path** n'existe pas sur cet ordinateur ou est un stockage distant, les fichiers ne sont pas sur le disque, ou l'unité n'est pas une ligne de la fiche US ou n'a pas de médias. | Regardez l'onglet **Units** : si l'unité y montre ses vignettes, vous les retrouverez ici aussi. Sinon, ouvrez la matrice depuis le projet, vérifiez **Thumbnail path** et **Image resize** dans la configuration (tutoriel 01) et que les fichiers sont bien sur l'ordinateur : les images sur un stockage distant n'entrent pas. L'export réussit quand même, sans photos. |

---

## Références

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Dépôt pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
