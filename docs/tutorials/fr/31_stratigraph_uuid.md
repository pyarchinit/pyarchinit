# PyArchInit - StratiGraph: Identificateurs UUID

## Sommaire
1. [Introduction](#introduction)
2. [Qu'est-ce que les UUID](#quest-ce-que-les-uuid)
3. [Pourquoi les UUID sont necessaires dans StratiGraph](#pourquoi-les-uuid-sont-necessaires-dans-stratigraph)
4. [Comment ils fonctionnent dans PyArchInit](#comment-ils-fonctionnent-dans-pyarchinit)
5. [Tables avec UUID](#tables-avec-uuid)
6. [Questions Frequentes](#questions-frequentes)

---

## Introduction

A partir de la version **5.0.1-alpha**, PyArchInit integre un systeme **d'identificateurs universels (UUID)** pour toutes les entites archeologiques. Cette fonctionnalite fait partie du projet europeen **StratiGraph** (Horizon Europe) et garantit que chaque enregistrement dans la base de donnees possede un identificateur stable et unique au niveau mondial.

<!-- VIDEO: Introduction aux UUID dans StratiGraph -->
> **Video Tutoriel**: [Inserer lien video introduction UUID]

---

## Qu'est-ce que les UUID

Un **UUID** (Universally Unique Identifier) est un code alphanumerique de 128 bits qui identifie de maniere unique une entite. PyArchInit utilise la version 4 (UUID v4), generee de maniere aleatoire.

### Exemple d'UUID

```
a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### Caracteristiques des UUID

| Caracteristique | Description |
|----------------|-------------|
| **Format** | 32 caracteres hexadecimaux separes par des tirets (8-4-4-4-12) |
| **Unicite** | La probabilite de collision est statistiquement negligeable (~1 sur 2^122) |
| **Independance** | Ne depend pas de la base de donnees, du serveur ou du moment de creation |
| **Persistance** | Une fois attribue, ne change jamais |
| **Version** | UUID v4 (genere aleatoirement) |

### Difference avec les ID traditionnels

| Type ID | Exemple | Stable entre BD? | Unique globalement? |
|---------|---------|------------------|---------------------|
| Auto-increment (id_us) | `1`, `2`, `3`... | Non | Non |
| Contrainte composite | `Site1-Zone1-US100` | Oui (semantique) | Depend |
| **UUID** | `a3f7b2c1-8d4e-...` | **Oui** | **Oui** |

Les ID auto-incrementaux (`id_us`, `id_invmat`, etc.) changent lorsqu'on copie une base de donnees ou qu'on importe des donnees. Les UUID restent **toujours les memes**, independamment de l'endroit ou se trouvent les donnees.

---

## Pourquoi les UUID sont necessaires dans StratiGraph

Le projet StratiGraph exige que les donnees archeologiques puissent etre:

### 1. Exportees vers le Knowledge Graph

Les donnees de PyArchInit sont exportees sous forme de **bundles** (paquets structures) vers un Knowledge Graph central. Chaque entite doit avoir un identificateur stable pour etre reconnue dans le graphe.

```
Entite locale (PyArchInit)  -->  UUID  -->  Knowledge Graph (StratiGraph)
     US 100                   a3f7b2c1...        E18 Physical Thing
```

### 2. Synchronisees entre appareils

Lorsqu'on travaille sur le terrain sans connexion internet, les donnees sont sauvegardees localement. Au retour de la connexion, les donnees sont synchronisees. Les UUID garantissent que le meme enregistrement soit reconnu et mis a jour (non duplique).

### 3. Mappees vers CIDOC-CRM

L'ontologie CIDOC-CRM requiert des **URI persistants** pour chaque entite. Les UUID sont utilises pour construire ces URI:

```
http://pyarchinit.org/entity/a3f7b2c1-8d4e-4f5a-9b6c-1234567890ab
```

### 4. Tracees dans le temps

Chaque modification, export ou synchronisation fait reference au meme UUID. Cela permet de:
- Reconstruire l'historique d'un enregistrement
- Verifier la provenance des donnees
- Relier des donnees entre differents projets

---

## Comment ils fonctionnent dans PyArchInit

### Generation automatique

Les UUID sont generes **automatiquement** a deux moments:

| Moment | Description |
|--------|-------------|
| **Creation nouvel enregistrement** | Lors de l'insertion d'un nouvel enregistrement (ex. nouvelle US), un UUID v4 est genere automatiquement |
| **Migration base de donnees existante** | Au premier demarrage apres la mise a jour, tous les enregistrements existants sans UUID recoivent un UUID genere |

L'utilisateur **n'a rien a faire**: les UUID sont entierement geres par le systeme.

### Ou se trouve l'UUID

Chaque table principale de la base de donnees possede une colonne `entity_uuid` de type TEXT. Le champ est visible dans la base de donnees mais n'apparait pas dans les fiches de saisie, car il est gere en interne.

### Migration automatique

Lors de la mise a jour de PyArchInit vers la version 5.0.1-alpha (ou ulterieure):

1. **Au premier demarrage**, le systeme verifie si les tables ont la colonne `entity_uuid`
2. Si elle manque, la colonne est **ajoutee automatiquement**
3. Les enregistrements existants sans UUID recoivent un **UUID genere**
4. Cette operation se produit **une seule fois** par session QGIS

Le processus est transparent et ne necessite aucune intervention manuelle. Il fonctionne avec **PostgreSQL** et **SQLite**.

---

## Tables avec UUID

La colonne `entity_uuid` est presente dans les 19 tables suivantes:

| Table | Contenu |
|-------|---------|
| `site_table` | Sites archeologiques |
| `us_table` | Unites Stratigraphiques (US/USM) |
| `inventario_materiali_table` | Inventaire du materiel |
| `tomba_table` | Sepultures |
| `periodizzazione_table` | Periodisation et phases |
| `struttura_table` | Structures |
| `campioni_table` | Echantillons |
| `individui_table` | Individus anthropologiques |
| `pottery_table` | Ceramique |
| `media_table` | Fichiers media |
| `media_thumb_table` | Miniatures media |
| `media_to_entity_table` | Relations media-entite |
| `fauna_table` | Donnees archeozoologiques (Faune) |
| `ut_table` | Unites Topographiques |
| `tma_materiali_archeologici` | TMA Materiaux Archeologiques |
| `tma_materiali_ripetibili` | TMA Materiaux Repetables |
| `archeozoology_table` | Archeozoologie |
| `documentazione_table` | Documentation |
| `inventario_lapidei_table` | Inventaire Lapidaire |

---

## Questions Frequentes

### Dois-je saisir manuellement les UUID?

**Non.** Les UUID sont generes automatiquement par le systeme. Il n'est pas necessaire (ni recommande) de les modifier manuellement.

### Que se passe-t-il si je copie la base de donnees?

Les UUID sont copies avec la base de donnees. C'est le comportement souhaite: le meme enregistrement conserve le meme UUID meme sur des copies differentes de la base de donnees.

### Puis-je voir les UUID dans les fiches?

Actuellement, les UUID ne sont pas visibles dans les fiches de saisie. Ils sont visibles directement dans la base de donnees (ex. via DB Manager dans QGIS) dans la colonne `entity_uuid` de chaque table.

### Les UUID ralentissent-ils la base de donnees?

Non. L'UUID est un simple champ TEXT et n'a pas d'impact significatif sur les performances de la base de donnees.

### Que se passe-t-il pour les bases de donnees existantes?

Les bases de donnees existantes sont mises a jour automatiquement au premier demarrage: la colonne `entity_uuid` est ajoutee et tous les enregistrements existants recoivent un UUID genere.

### Les UUID fonctionnent-ils avec PostgreSQL et SQLite?

Oui. Le systeme est compatible avec les deux types de bases de donnees supportes par PyArchInit.

---

*Documentation PyArchInit - StratiGraph UUID*
*Version: 5.0.1-alpha*
*Derniere mise a jour: Fevrier 2026*
