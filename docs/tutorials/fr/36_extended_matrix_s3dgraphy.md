# Tutoriel 36 : Export Extended Matrix et Bridge s3dgraphy

## Introduction

À partir de la version **5.2.0-alpha** PyArchInit intègre un **bridge bidirectionnel** avec la bibliothèque **s3dgraphy** (modèle de données Extended Matrix d'Emanuel Demetrescu). Le bridge permet de :

- **Exporter** le diagramme stratigraphique en Extended Matrix au format GraphML (avec swimlanes temporelles, réduction transitive, edge styling EM 1.5)
- **Réimporter** les modifications faites dans yEd (déplacements d'US entre périodes/groupes) en mettant à jour la base SQL
- **Joindre des paradata** (Author / License / Embargo) au niveau du site
- **Regrouper** les US par dimension (struttura, area, attivita, settore, ambient, saggio, quad_par ou groupes ad-hoc)

Tag courant: `phase2-ai07-locationnodegroup-5.6.0-alpha` (2026-05-10).

---

## 1. Prérequis

- Base de données SQLite (PostgreSQL pas encore supporté)
- **Migration Phase 1 node_uuid** appliquée automatiquement à l'ouverture du DB
- **yEd Graph Editor** pour visualiser la sortie (https://www.yworks.com/products/yed)

> ⚠️ Pour les DB antérieurs à 5.2.0-alpha, un redémarrage de QGIS peut être nécessaire.

---

## 2. Exporter Extended Matrix (bouton vert)

### 2.1 Ouvrir le dialogue

1. Ouvrir la **Fiche US** du site désiré
2. Cliquer sur le bouton vert **"Esporta Extended Matrix"** (sous l'onglet Rapporti)

### 2.2 Onglet "Export"

Le dialogue affiche :

- **Output formats** : cocher DOT / GraphML / JSON / phased JSON (recommandé : GraphML)
- **Group US by (optional)** : 7 checkboxes pour les dimensions de regroupement + 1 "ad-hoc"
  - Les dimensions remplies dans le DB sont **auto-cochées** à l'ouverture
- **Sélecteur de dimension primaire** (par défaut `struttura`) : lorsqu'une US a des appartenances sur 2+ dimensions, la dimension primaire l'emporte comme dossier yEd visible (parent hiérarchique). Les autres dimensions apparaissent comme badges en ligne sous le nœud US. `toponym` n'est jamais primaire, quel que soit le choix.
- **"Select Output Directory"** : dossier de destination

À partir de 5.6.0-alpha, vous pouvez cocher **2+ dimensions** : l'export fonctionne nativement grâce au modèle m:n avec `is_primary` (voir section "Appartenance multidimensionnelle").

### 2.3 Cliquer sur "Export"

4 fichiers sont générés avec préfixe `Extended_Matrix_<site>[_<area>]` :
- `.dot` — Graphviz DOT
- `.graphml` — Extended Matrix pour yEd (cible principale)
- `_s3dgraphy.json` — format natif s3dgraphy
- `_phased.json` — vue par époque

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

## 4. Style visuel par dimension (5.5.1-alpha + 5.6.0-alpha)

Chaque dimension de regroupement a une couleur distinctive en GraphML :

| Dimension | Fill (50% transparence) | Border |
|---|---|---|
| `area` | rose pastel `#FFE0E680` | `#C84A5F` |
| `struttura` | orange pastel `#FFE6CC80` | `#C66B33` |
| `attivita` | jaune pastel `#FFF5CC80` | `#A89A33` |
| `settore` | vert pastel `#E6FFCC80` | `#6BC633` |
| `ambient` | aqua pastel `#CCFFE680` | `#33A86B` |
| `saggio` | bleu pastel `#CCF5FF80` | `#3389A8` |
| `quad_par` | violet pastel `#E0CCFF80` | `#6633C6` |
| `adhoc` | gris pastel `#F5F5F580` | `#666666` |

À partir de 5.6.0-alpha, les `LocationNodeGroup` sont distingués par `kind` :

| `kind` | Fill (50% transparence) | Border |
|---|---|---|
| `toponym` | lavande pastel `#E6E6FA80` | `#9370DB` |
| `study` | ivoire pastel `#FFFFE080` | `#888888` |
| `functional` | cyan pastel `#E0FFFF80` | `#008B8B` |

L'alpha 50% laisse visibles les swimlane des époques derrière le rectangle du groupe.

### 4.1 Chaîne toponymique (5.6.0-alpha)

Les champs `site_table.{nazione, regione, provincia, comune}` sont automatiquement émis comme une chaîne récursive de `LocationNodeGroup(kind="toponym")` (parent : nazione → regione → provincia → comune). Les niveaux administratifs vides sont sautés sans rompre la chaîne. Une déduplication cross-site garantit que la même `comune` présente dans 2 sites devient **un seul nœud partagé** dans le GraphML.

---

## 4.2 Appartenance multidimensionnelle (5.6.0-alpha)

À partir de 5.6.0-alpha une US peut appartenir à **plusieurs dimensions simultanément** grâce au modèle m:n avec le drapeau `is_primary`. Seule la dimension primaire devient le dossier yEd visible ; les autres apparaissent comme **badges en ligne** sous le nœud US et comme JSON dans `<data key="s3d:other_locations">` pour les outils en aval.

Exemple : une US avec `struttura=basilica` et `area=B` (primaire `struttura`) produit :
- dossier yEd "struttura: basilica" comme parent visible ;
- sous le nœud US, un badge en ligne `also: B (study), TestCity (toponym)` ;
- dans le GraphML, l'attribut `s3d:other_locations` avec un tableau JSON des appartenances secondaires.

La dimension primaire se contrôle via le sélecteur de §2.2.

---

## 5. Round-trip (onglet Import)

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

## Références

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Dépôt pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
