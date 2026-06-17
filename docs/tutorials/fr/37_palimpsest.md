# Tutorial 37: Analyse des palimpsestes (palimpsestr / SEF)

## Introduction

PyArchInit intègre **palimpsestr**, une bibliothèque R qui applique le modèle
**SEF — Stratigraphic Entanglement Field** pour la *décomposition probabiliste
des palimpsestes* : elle sépare statistiquement les mobiliers d'un dépôt complexe
en **phases** latentes, en estimant pour chaque unité stratigraphique (US) sa
phase d'appartenance, sa résidualité et les éventuelles **intrusions**.

La fenêtre **palimpsestr** (icône à strates colorées dans la barre d'outils
pyArchInit) permet de :

- **Fit SEF** : estimer les phases et produire des couches vectorielles (phases,
  liens) ainsi qu'une table de diagnostic ;
- **Intrusions** : repérer les mobiliers/US chronologiquement hors de place ;
- **Rapport narratif (PDF/DOCX)** : un rapport interprétatif avec texte,
  graphiques de diagnostic et tableaux ;
- **Rapport IA** : un rapport descriptif généré par des agents IA spécialisés,
  dans n'importe quelle langue de pyArchInit ;
- travailler aussi bien sur **SQLite/Spatialite** que sur **PostgreSQL/PostGIS** ;
- utiliser une **chronologie absolue** (dates calibrées OxCal) à la place de la
  datation en texte libre.

> Nécessite palimpsestr **≥ 0.22.0** installé dans la bibliothèque R utilisée par
> le *Processing R Provider* de QGIS.

---

## 1. Prérequis

- **R** installé et le plugin **Processing R Provider** activé dans QGIS.
- Paquet R **palimpsestr ≥ 0.22.0** (≥ 0.22.1 pour le score taf ; ≥ 0.23.0 pour
  les coordonnées des mobiliers relevés point par point) (et ses dépendances :
  `sf`, `DBI`, `RSQLite` ; `RPostgres` pour PostgreSQL).
- Pour le **rapport PDF/DOCX** : **pandoc** et un moteur **LaTeX** (par ex.
  TinyTeX). En leur absence, la narration Markdown `.md` + les figures PNG sont
  tout de même produites.
- Pour la **chronologie OxCal** : paquet R **oxcAAR** et **Java** (le moteur
  OxCal est téléchargé automatiquement lors de la première utilisation par
  `oxcAAR::quickSetupOxcal()`).
- Pour le **rapport IA** : un fournisseur LLM configuré (OpenAI, Anthropic,
  Ollama ou LM Studio) via le sélecteur Fournisseur IA.

Les scripts R (`.rsx`) sont **inclus dans le plugin** et installés
automatiquement à l'ouverture de la fenêtre ; le bouton *Install/update R
scripts* les réinstalle manuellement.

---

## 2. Ouvrir la fenêtre

1. Barre d'outils pyArchInit → menu d'analyse → **palimpsestr - Analisi
   palinsesti** (palimpsestr - Analyse des palimpsestes).
2. La fenêtre affiche la base de données active (SQLite ou PostgreSQL) et les
   paramètres.

---

## 3. Paramètres de l'analyse

| Paramètre | Signification |
|---|---|
| **Nombre de phases (K)** | combien de phases latentes estimer (2–12) |
| **Modèle de classe** | `multinomial` (recommandé) ou `gaussien` (legacy) |
| **Composante de bruit/valeurs aberrantes** | active l'estimation des intrusions/résidualité |
| **Seuil d'intrusion** | postérieure minimale pour signaler un mobilier comme intrusion |
| **Mobiliers (source)** | **Les deux** / **Matériaux** / **Céramique** |
| **Site (filtre)** | limite l'analyse à un site (vide = tous) |

Le sélecteur **Mobiliers** est partagé par Fit, Intrusions et Rapport : tous
respectent la même sélection de mobiliers.

---

## 4. Fit SEF et Intrusions

- **Fit SEF model** : exécute la décomposition et charge dans le projet la couche
  *SEF phases* (points colorés par phase) et *SEF links*, ainsi que la table de
  diagnostic.
- **Detect intrusions** : charge une couche de points portant `intrusion_prob`,
  `direction` et `intrusion_type`.

---

## 5. Rapport narratif (PDF/DOCX)

1. Définissez la **Langue du rapport** (Italien/Anglais) et le **Format**
   (PDF+DOCX / PDF / DOCX).
2. Cliquez sur **Genera report (PDF/DOCX)** (Générer le rapport (PDF/DOCX)).
3. Le **panneau des résultats** affiche la narration en lisant le fichier `.md`
   qui est **toujours** écrit à côté de la sortie.
4. Les boutons **Apri PDF / Apri DOCX / Apri cartella** (Ouvrir PDF / Ouvrir
   DOCX / Ouvrir le dossier) s'activent selon les fichiers réellement produits.

> Si seules la narration `.md` et les figures apparaissent (pas de PDF/DOCX),
> c'est que pandoc/LaTeX manquent : la fenêtre essaie de les ajouter
> automatiquement au `PATH` ; sinon, installez-les (dans R :
> `tinytex::install_tinytex()`).

---

## 6. PostgreSQL / PostGIS

Les analyses fonctionnent aussi sur la connexion **PostgreSQL** active de
pyArchInit, pas seulement sur SQLite. La fenêtre convertit automatiquement l'URL
de connexion en une DSN libpq et la transmet aux algorithmes (paramètre
`PG_connection`) ; avec PostgreSQL actif, aucun fichier SQLite n'est demandé.

---

## 7. Chronologie absolue (OxCal)

La table facultative **`palimpsest_chronology`** fournit des dates **calibrées
par US** (années calendaires, av. J.-C. en négatif) que palimpsestr utilise **à
la place** de la `datazione` en texte libre.

1. Cliquez sur **Cronologia assoluta (OxCal)…** (Chronologie absolue (OxCal)…).
2. **Crea/aggiorna tabella** (Créer/mettre à jour la table) : crée
   `palimpsest_chronology` sur le backend actif (SQLite ou PostgreSQL), de
   manière idempotente.
3. **Calibration en direct** : saisissez pour chaque US les dates
   radiocarbones (BP ± erreur, code labo) et cliquez sur **Calibra e salva
   (OxCal)** (Calibrer et enregistrer (OxCal)) : un pilote R
   (`oxcAAR::oxcalCalibrate` + `palimpsestr::chronology_from_oxcal`) calcule les
   intervalles calendaires et les enregistre comme `start`/`end`.
4. **Import CSV** : sinon, importez un CSV déjà calibré avec les colonnes
   `sito, area, us, start, end, lab_code, source`.

Les données d'exemple se trouvent dans `docs/examples/` :
`palimpsest_oxcal_samples_villa_romana.csv` (échantillons C14 pour la
calibration) et `palimpsest_chronology_villa_romana.csv` (intervalles déjà
calibrés).

> Une fois remplie, la table est détectée **automatiquement** — aucune
> modification des algorithmes n'est nécessaire.

---

## 8. Rapport IA (analyse descriptive)

Le bouton **Report AI (analisi descrittiva)…** (Rapport IA (analyse
descriptive)…) génère un rapport **descriptif et didactique** avec un pipeline
d'**agents IA spécialisés** :

1. **Méthodologue** — explique les choix : le modèle (multinomial vs gaussien),
   la valeur de **K** et les preuves diagnostiques qui la justifient, la
   composante de bruit et le **seuil**, la sélection des mobiliers et l'usage de
   la chronologie OxCal ; indique les limites et les précautions.
2. **Analyste** — interprète les phases, la chronologie (avec les dates absolues
   si présentes), la résidualité/intrusions et le schéma spatial.
3. **Rédacteur** — compose un rapport unique et cohérent, en renvoyant aux
   figures.

Procédure :

1. Choisissez le **Fournisseur IA** et le modèle dans le sélecteur.
2. Choisissez la **Langue du rapport** (toutes les langues de pyArchInit :
   it, en, de, es, fr, pt, ca, ro, el, ar).
3. Cliquez sur **Genera report AI** (Générer le rapport IA) : le texte apparaît
   en temps réel.
4. Enregistrez en **DOCX** (avec les figures incorporées) ou en **Markdown**.

Le rapport explique explicitement **pourquoi** le modèle, le K et le seuil ont
été choisis, et interprète les résultats de façon compréhensible — l'idéal pour
le rapport de fouille.

---

## 9. Modifier les dates, le graphique OxCal, le PDF et une note sur le taf

- **Éditeur par US (Chronologie et taphonomie)** : la fenêtre **précharge toutes les US du site** avec deux colonnes d'information **Période** et **Nbr. trouvailles**, afin que vous puissiez attribuer le **taf** à chaque US (et pas seulement à celles datées). Le taf est pris en compte par Fit, Intrusions, Report et le rapport IA : il sous-pondère les US redéposées ou perturbées. Seules les US renseignées (avec un taf et/ou une date) sont enregistrées.

- **Les dates enregistrées sont modifiables** : la fenêtre *Cronologia assoluta*
  **charge à l'ouverture** les dates déjà présentes dans
  `palimpsest_chronology` (bouton *Ricarica dal DB*). Vous pouvez modifier à la
  main les colonnes **start/end** et appuyer sur **Salva modifiche (start/end)**,
  ou saisir de nouvelles dates C14 et appuyer sur *Calibra e salva*. Les dates
  **persistent** dans la base de données — inutile de les ressaisir à chaque
  fois.
- **Graphique de calibration** : après *Calibra e salva*, les boutons **Mostra
  grafico OxCal** / **Esporta grafico (PNG)** affichent un panneau par US avec la
  courbe de probabilité, la bande 95% HPD et l'intervalle calendaire.
- **Rapport IA en PDF** : outre DOCX et Markdown, le rapport IA peut être
  enregistré en **PDF** (bouton *Salva PDF…*), avec tableaux et figures
  incorporés.
- **Score taphonomique (taf)** : c'est une valeur **interprétative** dans `[0,1]`
  (0 = mobilier entièrement perturbé/redéposé, 1 = intact en place) qui pondère
  les mobiliers dans l'estimation. Il **n'est pas calculé automatiquement** :
  c'est l'archéologue qui l'attribue d'après le contexte de dépôt (par ex. 1.0
  pour les dépôts en place ; 0.5–0.7 pour les accumulations/nivellements ; 0.3
  pour les remblais nettement redéposés).
- **Coordonnées des mobiliers relevés point par point** (palimpsestr ≥ 0.23.0) :
  lorsqu'un mobilier est dessiné comme un point dans `pyarchinit_reperti` (lié à
  `inventario_materiali_table` par la jointure `pyarchinit_reperti_view`, c.-à-d.
  site + numéro d'inventaire = `id_rep`), l'analyse utilise ses propres x, y (et z
  d'après la `quota` du point) au lieu du centroïde de l'US. Les mobiliers sans
  point conservent le centroïde de l'US. Là où le relevé point par point est
  disponible, cela offre une résolution spatiale au niveau du mobilier et atténue
  la limite du centroïde signalée ci-dessous. Rien à configurer — la fenêtre
  détecte et utilise les points automatiquement.
- **Limites à garder à l'esprit** (le rapport IA les déclare automatiquement) :
  le modèle suppose une **stratigraphie horizontale** (z comme proxy
  chronologique ; prudence avec les remblais de creusements, les effondrements,
  les terrassements) ; la **résolution est bornée par la donnée** : avec des
  coordonnées de centroïde d'US et des dates liées à l'US, un PDI≈1 et une
  entropie≈0 reflètent l'**enregistrement**, et non une séquence parfaitement
  résolue (les mobiliers relevés point par point, lorsqu'ils sont présents,
  améliorent la résolution spatiale).

---

*Documentation PyArchInit — Juin 2026*
