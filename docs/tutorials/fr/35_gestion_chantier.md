# PyArchInit - Gestion de Chantier

## Sommaire

1. [Introduction](#introduction)
2. [Acces au module](#acces-au-module)
3. [Tableau de bord](#tableau-de-bord)
4. [Fiche Personnel](#fiche-personnel)
5. [Fiche Presences](#fiche-presences)
6. [Fiche Equipements](#fiche-equipements)
7. [Fiche Budget](#fiche-budget)
8. [Flux de travail operationnel](#flux-de-travail-operationnel)
9. [Foire aux questions](#foire-aux-questions)
10. [Notes techniques](#notes-techniques)

---

## Introduction

Le module **Gestion de Chantier** de PyArchInit fournit un ensemble integre d'outils pour la gestion administrative et logistique d'un chantier de fouille archeologique. Il centralise le suivi du personnel, des presences, des equipements, du budget et des metrages (computo metrico) au sein d'un tableau de bord unique, relie a chaque site enregistre dans la base de donnees.

Ce module est concu pour les responsables de chantier, les directeurs de fouille et les gestionnaires de projet qui doivent suivre en temps reel les ressources humaines, materielles et financieres associees aux operations de terrain.

### Composants du module

Le module se compose de **cinq formulaires** interconnectes :

| Composant | Fonction | Table BD |
|-----------|----------|----------|
| **Tableau de Bord** | Vue synthetique et metrages DEM | `budget_table`, `presenze_table`, `attrezzature_table`, `computo_metrico_table` |
| **Personnel** | Gestion CRUD du personnel | `personale_table` |
| **Presences** | Suivi journalier des presences | `presenze_table` |
| **Equipements** | Inventaire et maintenance du materiel | `attrezzature_table` |
| **Budget** | Suivi budgetaire previsionnel et effectif | `budget_table` |

<!-- IMAGE: Vue d'ensemble du module Gestion de Chantier avec les 5 icones dans la barre d'outils -->
> **Fig. 1** : Les cinq icones du module Gestion de Chantier dans la barre d'outils PyArchInit

---

## Acces au module

Le module est accessible via une barre d'outils dediee **pyArchInit - Gestione Cantiere** qui contient cinq boutons :

| # | Icone | Libelle | Action |
|---|-------|---------|--------|
| 1 | iconCantiere | **Tableau de Bord** | Ouvre le tableau de bord central |
| 2 | iconPersonale | **Personnel** | Ouvre la fiche Personnel |
| 3 | iconPresenze | **Presences** | Ouvre la fiche Presences |
| 4 | iconAttrezzature | **Equipements** | Ouvre la fiche Equipements |
| 5 | iconBudget | **Budget** | Ouvre la fiche Budget |

Les formulaires sont egalement accessibles depuis le menu : **PyArchInit** > **Archaeological GIS Tools**.

<!-- IMAGE: Barre d'outils Gestione Cantiere avec les 5 boutons annotes -->
> **Fig. 2** : La barre d'outils Gestion de Chantier avec les cinq boutons d'acces

---

## Tableau de bord

Le **Tableau de Bord** (Dashboard Cantiere) est le formulaire central du module. Il offre une vue synthetique et actualisee de l'etat du chantier pour un site et une annee donnes.

### Selecteurs principaux

En haut du formulaire se trouvent deux menus deroulants :

| Selecteur | Description |
|-----------|-------------|
| **Site** | Liste des sites enregistres dans la base de donnees. Pre-selectionne automatiquement le site configure dans les parametres |
| **Annee** | Annee de reference (les 10 dernieres annees). Filtre les donnees budgetaires |

Un bouton **Rafraichir** permet de recharger manuellement les donnees du tableau de bord.

<!-- IMAGE: Zone des selecteurs Site et Annee avec le bouton Rafraichir -->
> **Fig. 3** : Selecteurs de site et d'annee en haut du tableau de bord

### Resume budgetaire

La section budget affiche un resume financier pour le site et l'annee selectionnes :

| Element | Description |
|---------|-------------|
| **Montant prevu** | Somme des montants previsionels (`importo_previsto`) de toutes les lignes budgetaires |
| **Montant effectif** | Somme des depenses reelles (`importo_effettivo`) |
| **Barre de progression** | Pourcentage de consommation du budget (effectif / prevu x 100) |
| **Graphique en secteurs** | Repartition des depenses par categorie |

La barre de progression est plafonnee a 100 % pour la visualisation, mais les valeurs reelles sont toujours affichees dans les libelles.

<!-- IMAGE: Section resume budgetaire avec barre de progression et graphique en secteurs -->
> **Fig. 4** : Resume budgetaire montrant les montants, la barre de progression et le graphique en secteurs

### Resume du personnel

La section personnel interroge la table des presences pour la date du jour et affiche :

| Indicateur | Description |
|------------|-------------|
| **Presents** | Nombre de personnes en journee de travail (`lavorativa`) |
| **Conges** | Nombre de personnes en conge (`ferie`) |
| **Maladie** | Nombre de personnes en arret maladie (`malattia`) |
| **Heures du mois** | Total des heures ordinaires + supplementaires pour le mois en cours |
| **Cout du mois** | Somme des couts journaliers pour le mois en cours |

<!-- IMAGE: Section resume du personnel avec les indicateurs presenti/ferie/malattia -->
> **Fig. 5** : Resume du personnel avec les indicateurs journaliers et mensuels

### Resume des equipements

La section equipements interroge la table des attrezzature et affiche :

| Indicateur | Description |
|------------|-------------|
| **Total** | Nombre total d'equipements enregistres pour le site |
| **En usage** | Nombre d'equipements avec le statut `in_uso` |
| **En maintenance** | Nombre d'equipements avec le statut `manutenzione` |
| **Alertes de maintenance** | Message d'avertissement (en rouge) si des maintenances sont en retard |

Le systeme detecte automatiquement les equipements dont la date de prochaine maintenance (`data_prossima_manutenzione`) est depassee et qui ne sont pas hors service (`fuori_uso`).

<!-- IMAGE: Section resume des equipements avec alerte de maintenance en rouge -->
> **Fig. 6** : Resume des equipements avec un exemple d'alerte de maintenance en retard

### Metrages (Computo Metrico)

La section metrages permet de calculer des surfaces et des volumes a partir de couches raster (MNT/MNE) chargees dans le projet QGIS.

#### Modes de calcul

| Mode | Description |
|------|-------------|
| **Difference DEM** | Calcule la difference entre deux couches raster (pre et post). Utile pour estimer les volumes de terre deplacee |
| **DEM + Polygone** | Calcule les statistiques zonales d'un DEM au sein d'une couche polygonale. Permet de mesurer surface et volume pour des zones specifiques |

#### Couches d'entree

| Selecteur | Description |
|-----------|-------------|
| **DEM Pre** | Couche raster de reference (avant intervention) |
| **DEM Post** | Couche raster apres intervention (mode Difference DEM) |
| **Couche Polygone** | Couche vectorielle delimitant les zones de calcul (mode DEM + Polygone) |

#### Resultats

| Resultat | Description |
|----------|-------------|
| **Surface (m2)** | Surface totale calculee |
| **Volume (m3)** | Volume total calcule |

Le bouton **Calculer** lance le calcul selon le mode selectionne. Le bouton **Sauvegarder** enregistre le resultat dans la table `computo_metrico_table` avec la date, le type de calcul, la surface, le volume et des notes.

<!-- IMAGE: Section metrages avec selecteurs DEM et resultats de calcul -->
> **Fig. 7** : Section metrages montrant les selecteurs DEM, les modes de calcul et les resultats

### Historique des metrages

Un tableau en bas du formulaire affiche l'historique de tous les metrages enregistres pour le site :

| Colonne | Description |
|---------|-------------|
| **Date** | Date du calcul |
| **Type** | Type de calcul (Difference DEM / DEM + Polygone) |
| **Surface (m2)** | Surface calculee |
| **Volume (m3)** | Volume calcule |
| **Notes** | Commentaires libres |

<!-- IMAGE: Tableau historique des metrages avec plusieurs entrees -->
> **Fig. 8** : Historique des metrages pour un site donne

---

## Fiche Personnel

La **Fiche Personnel** permet la gestion CRUD (Creation, Lecture, Mise a jour, Suppression) des membres du personnel associes a chaque site.

### Champs disponibles

| Champ | Nom BD | Type | Description |
|-------|--------|------|-------------|
| **Site** | `sito` | Texte | Site de rattachement |
| **Prenom** | `nome` | Texte | Prenom du membre |
| **Nom** | `cognome` | Texte | Nom de famille |
| **Role** | `ruolo` | Texte | Role sur le chantier (directeur, archeologue, ouvrier, etc.) |
| **Qualification** | `qualifica` | Texte | Qualification professionnelle |
| **Code fiscal** | `codice_fiscale` | Texte | Identifiant fiscal |
| **Email** | `email` | Texte | Adresse electronique |
| **Telephone** | `telefono` | Texte | Numero de telephone |
| **Date de naissance** | `data_nascita` | Date | Date de naissance |
| **Adresse** | `indirizzo` | Texte | Adresse postale |
| **Type de contrat** | `tipo_contratto` | Texte | Type de contrat (CDD, CDI, stage, etc.) |
| **Debut de contrat** | `data_inizio_contratto` | Date | Date de debut |
| **Fin de contrat** | `data_fine_contratto` | Date | Date de fin |
| **Tarif horaire** | `tariffa_oraria` | Numerique | Cout horaire |
| **Tarif journalier** | `tariffa_giornaliera` | Numerique | Cout journalier |
| **IBAN** | `iban` | Texte | Coordonnees bancaires |
| **Notes** | `note` | Texte | Commentaires libres |
| **Actif** | `attivo` | Booleen | Indique si le membre est actuellement actif |

### Toolbar DBMS

La barre d'outils DBMS standard de PyArchInit est disponible avec les fonctions habituelles :

| Bouton | Fonction |
|--------|----------|
| **New record** | Creer un nouvel enregistrement |
| **Save** | Sauvegarder les modifications |
| **Delete record** | Supprimer l'enregistrement courant |
| **New search** | Passer en mode recherche |
| **Search !!!** | Executer la recherche |
| **Order by** | Trier les enregistrements |
| **View all records** | Afficher tous les enregistrements |
| **First / Prev / Next / Last** | Navigation entre les enregistrements |

<!-- IMAGE: Formulaire Personnel avec tous les champs remplis -->
> **Fig. 9** : Formulaire Personnel avec les champs descriptifs et la toolbar DBMS

---

## Fiche Presences

La **Fiche Presences** permet de saisir et suivre les presences journalieres du personnel sur le chantier.

### Champs disponibles

| Champ | Nom BD | Type | Description |
|-------|--------|------|-------------|
| **Site** | `sito` | Texte | Site de rattachement |
| **ID Personnel** | `id_personale` | Entier | Identifiant du membre du personnel |
| **Date** | `data` | Date | Date de la presence |
| **Heure d'arrivee** | `ora_ingresso` | Heure | Heure de pointage a l'entree |
| **Heure de depart** | `ora_uscita` | Heure | Heure de pointage a la sortie |
| **Heures ordinaires** | `ore_ordinarie` | Numerique | Nombre d'heures de travail normal |
| **Heures supplementaires** | `ore_straordinario` | Numerique | Nombre d'heures supplementaires |
| **Type de journee** | `tipo_giornata` | Liste | Type : `lavorativa` (travail), `ferie` (conges), `malattia` (maladie) |
| **Equipe** | `turno` | Texte | Equipe de travail |
| **Zone de travail** | `area_lavoro` | Texte | Zone d'affectation sur le chantier |
| **Notes** | `note` | Texte | Commentaires libres |
| **Cout de la journee** | `costo_giornata` | Numerique | Cout de la journee de travail |

### Types de journee

| Valeur | Signification |
|--------|---------------|
| `lavorativa` | Journee de travail effective |
| `ferie` | Journee de conge |
| `malattia` | Journee d'arret maladie |

<!-- IMAGE: Formulaire Presences avec un enregistrement de journee de travail -->
> **Fig. 10** : Formulaire Presences avec les champs horaires et le type de journee

---

## Fiche Equipements

La **Fiche Equipements** (Attrezzature) permet de gerer l'inventaire du materiel et le suivi de la maintenance.

### Champs disponibles

| Champ | Nom BD | Type | Description |
|-------|--------|------|-------------|
| **Site** | `sito` | Texte | Site de rattachement |
| **Code inventaire** | `codice_inventario` | Texte | Identifiant unique de l'equipement |
| **Nom** | `nome` | Texte | Designation de l'equipement |
| **Categorie** | `categoria` | Texte | Type d'equipement (topographie, excavation, securite, etc.) |
| **Marque** | `marca` | Texte | Marque du fabricant |
| **Modele** | `modello` | Texte | Reference du modele |
| **Numero de serie** | `numero_serie` | Texte | Numero de serie |
| **Propriete** | `proprieta` | Texte | Proprietaire de l'equipement (institution, location, etc.) |
| **Date d'achat** | `data_acquisto` | Date | Date d'acquisition |
| **Cout d'achat** | `costo_acquisto` | Numerique | Prix d'achat |
| **Cout location/jour** | `costo_noleggio_giorno` | Numerique | Cout de location journalier |
| **Etat** | `stato` | Liste | Etat actuel de l'equipement |
| **Assigne a** | `assegnato_a` | Texte | Personne ou equipe responsable |
| **Derniere maintenance** | `data_ultima_manutenzione` | Date | Date de la derniere maintenance effectuee |
| **Prochaine maintenance** | `data_prossima_manutenzione` | Date | Date prevue pour la prochaine maintenance |
| **Notes** | `note` | Texte | Commentaires libres |

### Etats possibles

| Valeur | Signification |
|--------|---------------|
| `in_uso` | En usage normal |
| `manutenzione` | En cours de maintenance |
| `fuori_uso` | Hors service |

<!-- IMAGE: Formulaire Equipements avec un enregistrement complet -->
> **Fig. 11** : Formulaire Equipements avec les informations d'inventaire et de maintenance

---

## Fiche Budget

La **Fiche Budget** permet le suivi financier du chantier en comparant les montants previsionnels aux depenses reelles.

### Champs disponibles

| Champ | Nom BD | Type | Description |
|-------|--------|------|-------------|
| **Site** | `sito` | Texte | Site de rattachement |
| **Annee** | `anno` | Entier | Annee de reference |
| **Categorie** | `categoria` | Texte | Categorie budgetaire (personnel, materiel, transport, etc.) |
| **Description** | `descrizione` | Texte | Libelle du poste budgetaire |
| **Montant prevu** | `importo_previsto` | Numerique | Montant previsionnel en euros |
| **Montant effectif** | `importo_effettivo` | Numerique | Montant depense en euros |
| **Date d'enregistrement** | `data_registrazione` | Date | Date de creation de la ligne |
| **Date de depense** | `data_spesa` | Date | Date de la depense effective |
| **Fournisseur** | `fornitore` | Texte | Nom du fournisseur |
| **Numero de facture** | `numero_fattura` | Texte | Reference de la facture |
| **Notes** | `note` | Texte | Commentaires libres |

<!-- IMAGE: Formulaire Budget avec un enregistrement de ligne budgetaire -->
> **Fig. 12** : Formulaire Budget avec les montants prevus et effectifs

---

## Flux de travail operationnel

### Configuration initiale d'un chantier

```
1. Creer le site dans la Fiche Site (voir Tutoriel 02)
2. Ouvrir la Fiche Personnel
3. Enregistrer tous les membres de l'equipe
4. Ouvrir la Fiche Equipements
5. Enregistrer tout le materiel de chantier
6. Ouvrir la Fiche Budget
7. Creer les lignes previsionnelles par categorie et annee
8. Ouvrir le Tableau de Bord pour verifier la vue d'ensemble
```

### Suivi quotidien

```
1. Ouvrir la Fiche Presences
2. Pour chaque membre present :
   - Creer un nouvel enregistrement
   - Selectionner le site et l'ID du personnel
   - Saisir la date, les heures d'arrivee et de depart
   - Indiquer le type de journee (travail/conges/maladie)
   - Renseigner les heures ordinaires et supplementaires
   - Saisir le cout de la journee
   - Sauvegarder
3. Consulter le Tableau de Bord pour verifier les indicateurs du jour
```

### Suivi de maintenance

```
1. Ouvrir la Fiche Equipements
2. Rechercher l'equipement concerne
3. Mettre a jour :
   - L'etat (in_uso / manutenzione / fuori_uso)
   - La date de derniere maintenance
   - La date de prochaine maintenance
4. Sauvegarder
5. Verifier les alertes dans le Tableau de Bord
```

### Calcul de metrages

```
1. Charger les couches raster (DEM pre et post) dans le projet QGIS
2. Ouvrir le Tableau de Bord
3. Selectionner le site et l'annee
4. Dans la section Metrages :
   - Choisir le mode de calcul (Difference DEM ou DEM + Polygone)
   - Selectionner les couches dans les menus deroulants
   - Cliquer sur Calculer
5. Verifier les resultats (surface en m2, volume en m3)
6. Cliquer sur Sauvegarder pour enregistrer dans l'historique
```

<!-- IMAGE: Diagramme du flux de travail operationnel complet -->
> **Fig. 13** : Flux de travail operationnel du module Gestion de Chantier

---

## Foire aux questions

### Le tableau de bord n'affiche aucune donnee

**Causes possibles** :
- Aucun site selectionne dans le menu deroulant
- La connexion a la base de donnees n'est pas etablie
- Aucune donnee saisie pour le site et l'annee selectionnes

**Solutions** :
1. Verifier que le selecteur de site contient un site valide
2. Verifier la connexion a la base de donnees dans les parametres PyArchInit
3. Saisir au moins une ligne de budget, une presence et un equipement pour le site
4. Cliquer sur le bouton Rafraichir

### L'alerte de maintenance ne s'affiche pas

Le systeme ne signale les retards de maintenance que si :
- La date de prochaine maintenance (`data_prossima_manutenzione`) est renseignee
- La date est anterieure a la date du jour
- L'equipement n'est pas marque comme `fuori_uso`

### Les couches DEM n'apparaissent pas dans les selecteurs

Les selecteurs DEM ne proposent que les **couches raster** chargees dans le projet QGIS actuel. Pour le selecteur de polygone, seules les **couches vectorielles** sont listees.

**Solutions** :
1. Charger les couches dans le projet QGIS avant d'ouvrir le Tableau de Bord
2. Si les couches ont ete ajoutees apres l'ouverture, fermer et rouvrir le Tableau de Bord

### La barre de progression du budget depasse 100 %

La barre de progression est visuellement plafonnee a 100 %, mais les montants affiches refletent les valeurs reelles. Un depassement indique que les depenses effectives depassent le budget previsionnel.

### Comment lier un enregistrement de presence a un membre du personnel ?

La fiche Presences utilise le champ **ID Personnel** (`id_personale`) pour referencer un membre de la table du personnel. Assurez-vous de saisir le meme identifiant que celui attribue automatiquement lors de la creation de la fiche Personnel.

---

## Notes techniques

### Tables de la base de donnees

| Table | Classe mappee | Description |
|-------|---------------|-------------|
| `personale_table` | `PERSONALE` | Personnel du chantier |
| `presenze_table` | `PRESENZE` | Presences journalieres |
| `attrezzature_table` | `ATTREZZATURE` | Inventaire des equipements |
| `budget_table` | `BUDGET` | Lignes budgetaires |
| `computo_metrico_table` | `COMPUTO_METRICO` | Historique des metrages |

### Fichiers source

| Fichier | Description |
|---------|-------------|
| `tabs/Cantiere.py` | Dialogue du tableau de bord |
| `tabs/Personale.py` | Formulaire CRUD du personnel |
| `tabs/Presenze.py` | Formulaire CRUD des presences |
| `tabs/Attrezzature.py` | Formulaire CRUD des equipements |
| `tabs/Budget.py` | Formulaire CRUD du budget |
| `gui/ui/Cantiere.ui` | Interface Qt du tableau de bord |
| `gui/ui/Personale.ui` | Interface Qt du personnel |
| `gui/ui/Presenze.ui` | Interface Qt des presences |
| `gui/ui/Attrezzature.ui` | Interface Qt des equipements |
| `gui/ui/Budget.ui` | Interface Qt du budget |

### Compatibilite base de donnees

Le module fonctionne avec les deux moteurs de base de donnees supportes par PyArchInit :

| Moteur | Support |
|--------|---------|
| **PostgreSQL / PostGIS** | Complet, avec support multi-utilisateurs |
| **SQLite / SpatiaLite** | Complet, utilisation locale |

### Internationalisation

Les formulaires CRUD (Personnel, Presences, Equipements, Budget) supportent 10 langues pour les libelles et les messages : IT, EN, DE, ES, FR, AR, CA, RO, PT, EL.

Le Tableau de Bord affiche ses libelles dans la langue configuree dans les parametres de locale de QGIS.

---

## Tutoriel video

### Gestion de Chantier - Vue d'ensemble
`[Espace reserve : video_gestion_chantier.mp4]`

**Contenu** :
- Presentation de la barre d'outils et des 5 formulaires
- Configuration initiale d'un chantier
- Saisie du personnel et des presences
- Inventaire des equipements et alertes de maintenance
- Suivi budgetaire et graphiques
- Calcul de metrages depuis des couches DEM

**Duree prevue** : 20-25 minutes

---

*Documentation PyArchInit - Gestion de Chantier*
*Version : 5.0.x*
*Derniere mise a jour : Fevrier 2026*
