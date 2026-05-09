# Tutoriel 36 : Export Extended Matrix et Bridge s3dgraphy

## Introduction

À partir de la version **5.2.0-alpha** PyArchInit intègre un **bridge bidirectionnel** avec la bibliothèque **s3dgraphy** (modèle de données Extended Matrix d'Emanuel Demetrescu). Le bridge permet de :

- **Exporter** le diagramme stratigraphique en Extended Matrix au format GraphML (avec swimlanes temporelles, réduction transitive, edge styling EM 1.5)
- **Réimporter** les modifications faites dans yEd (déplacements d'US entre périodes/groupes) en mettant à jour la base SQL
- **Joindre des paradata** (Author / License / Embargo) au niveau du site
- **Regrouper** les US par dimension (struttura, area, attivita, settore, ambient, saggio, quad_par ou groupes ad-hoc)

Tag courant: `phase2-ai08f2-hotfix-5.5.2-alpha` (2026-05-09).

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
- **"Select Output Directory"** : dossier de destination

### 2.3 Limite single-dimension (5.5.2-alpha)

Si vous cochez **2 ou plus** de checkboxes de regroupement, un avertissement apparaît :

> *"Export multi-dim pas encore supporté. Continuer avec SEULEMENT la première dimension sélectionnée ?"*

Choisissez **Oui** (export avec la première dimension cochée) ou **Annuler** (modifier la sélection). L'imbrication hiérarchique (struttura > attivita > US) arrive avec AI08-F1.

### 2.4 Cliquer sur "Export"

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

## 4. Style visuel par dimension (5.5.1-alpha)

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

L'alpha 50% laisse visibles les swimlane des époques derrière le rectangle du groupe.

---

## 5. Round-trip (onglet Import)

Pour modifier la base SQL en déplaçant les US entre groupes en GraphML :

1. Ouvrir le GraphML dans **yEd**
2. Glisser une US dans un autre groupe, sauvegarder
3. Retour au dialogue → onglet **"Import"**
4. **Cocher** la checkbox *"Update SQL on import (struttura/area/...)"*
5. Charger le GraphML modifié

Le système exécute une transaction atomique : en cas d'échec, **rollback complet** (le DB reste intact). Les groupes `adhoc` n'écrivent jamais en SQL — ils mettent à jour seulement `groups_<site>.graphml`.

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
| Dossier de groupe vide dans yEd | Vous avez coché 2+ dimensions (limite 5.5.2-alpha) | N'en cocher qu'une, réessayer |
| "rapporti doivent être TEXT" | Saisi un nombre comme integer | Les champs US/Area sont **TEXT**, pas integer |
| Mauvaise capitalisation des rapporti | "copre" en minuscules dans le DB | Utiliser "Copre", "Coperto da" en majuscules |

---

## 8. Documentation technique

Pour approfondir l'architecture, les décisions de design et la roadmap :

- Specs : `docs/superpowers/specs/2026-05-*-design.md`
- Plans : `docs/superpowers/plans/2026-05-*.md`
- Dev log : `docs/superpowers/dev-log/T5.4_PyArchInit_Dev_Log.md`

Carry-over différés :
- **AI07** : migration `LocationNodeGroup` (deadline upstream 2026-05-23)
- **AI08-F1** : nesting hiérarchique (pour multi-dim export propre)
- **AI08-F3** : heuristiques d'auto-layout (bin-packing des sous-groupes)
- **AI09** : TimeBranchNodeGroup mapping
- **Phase 3** : SyncEngine + REST API
- **Phase 4** : GraphDBBackend + SPARQL

---

## Références

- Issue upstream LocationNodeGroup: https://github.com/zalmoxes-laran/s3Dgraphy/issues/5
- Dépôt pyarchinit: https://github.com/pyarchinit/pyarchinit
- yEd Graph Editor: https://www.yworks.com/products/yed
- s3dgraphy library: https://github.com/zalmoxes-laran/s3Dgraphy
