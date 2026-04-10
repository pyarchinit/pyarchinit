# PyArchInit - Gestion de Chantier

## Sommaire

1. [Introduction](#introduction)
2. [Acces au module](#acces-au-module)
3. [Tableau de bord](#tableau-de-bord)
4. [Fiche Personnel](#fiche-personnel)
5. [Fiche Presences](#fiche-presences)
6. [Fiche Equipements](#fiche-equipements)
7. [Fiche Budget](#fiche-budget)
8. [Visualisation 2D et 3D des metrages](#visualisation-2d-et-3d-des-metrages)
9. [Export PDF et CSV du tableau de bord](#export-pdf-et-csv-du-tableau-de-bord)
10. [Flux de travail operationnel](#flux-de-travail-operationnel)
11. [Foire aux questions](#foire-aux-questions)
12. [Notes techniques](#notes-techniques)

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

Depuis la version 5.1, a cote du bouton **Calculer** sont egalement disponibles les boutons **Afficher 2D**, **Afficher 3D** et **Creer maillage 3D** permettant de visualiser le resultat du calcul directement sur la carte et dans une vue tridimensionnelle interactive. Voir la section [Visualisation 2D et 3D des metrages](#visualisation-2d-et-3d-des-metrages).

<!-- IMAGE: Section metrages avec selecteurs DEM, resultats et nouveaux boutons 2D/3D -->
> **Fig. 7** : Section metrages avec selecteurs DEM, modes de calcul et nouveaux boutons de visualisation 2D / 3D

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

### Nouvelle mise en page a onglets du Tableau de bord

A partir de la version actuelle, la fenetre **Tableau de bord** a ete reorganisee en **trois onglets** pour faire place au nouveau panneau **Analyse des Couts** sans alourdir la vue. La ligne d'en-tete avec **Site**, **Annee** et le bouton **Actualiser** reste visible au-dessus des onglets, ce qui permet de changer de site ou d'annee a tout moment : tous les onglets sont mis a jour automatiquement.

| Onglet | Contenu |
|--------|---------|
| **Resume** | Vue affichee a l'ouverture du tableau de bord. En haut, sur toute la largeur, le **Resume du Budget** (barre de progression et diagramme circulaire) ; en dessous, cote a cote, les resumes **Personnel** et **Equipement** |
| **Metrage** | Regroupe tout le flux de calcul DEM : listes deroulantes **DEM Pre**, **DEM Post** et **Polygone**, boutons radio **Difference DEM** / **DEM sur Polygone**, bouton **Calculer**, etiquettes de **surface** et **volume**, le nouveau groupe **Analyse des Couts** (EUR/m3, m3/jour -> cout total, jours estimes, cout journalier), bouton **Enregistrer**, boutons **Afficher 2D** / **Afficher 3D** / **Exporter 2DM + 3D** et le **tableau d'historique** en bas |
| **Export** | Les boutons d'**export PDF** et **CSV** accompagnes d'une courte description |

<!-- IMAGE: Nouvelle mise en page a onglets du Tableau de bord (Resume / Metrage / Export) -->
> **Fig. 8a** : La nouvelle mise en page a onglets du Tableau de bord avec l'en-tete Site / Annee / Actualiser toujours visible

**Fix** : les DEM ne disparaissent plus lorsque l'on appuie sur **Calculer** (regression de la 5.0.13-alpha ou le rafraichissement automatique des listes deroulantes reinitialisait la selection courante).

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

## Visualisation 2D et 3D des metrages

Depuis la version 5.1, apres un clic sur le bouton **Calculer** du panneau Metrages, le Tableau de Bord ne se contente plus d'afficher les resultats numeriques (surface et volume) : il cree automatiquement un ensemble de couches cartographiques et met a disposition une vue 3D interactive.

### Ce qui se passe au clic sur "Calculer"

Apres un calcul de difference de DEM, le Tableau de Bord execute automatiquement les etapes suivantes :

1. **Sauvegarde permanente du raster de difference** : le raster calcule (DEM post - DEM pre) est enregistre en GeoTIFF permanent sous `<PYARCHINIT_HOME>/site_dashboard/<nom du site>/`. Le raster n'est plus perdu a la fermeture de QGIS et peut etre reutilise a tout moment.
2. **Ajout au projet QGIS** : le raster est ajoute au panneau Couches dans un groupe dedie appele **"Site Dashboard - Computi"**, afin que tous les calculs restent organises.
3. **Symbologie automatique** : une **rampe de couleurs divergente** est appliquee au raster :
   - **Rouge** pour les zones de deblai (valeurs negatives, terre enlevee)
   - **Bleu** pour les zones de remblai (valeurs positives, terre ajoutee)
   - **Transparent / neutre** pour les cellules sans variation significative (|diff| <= 1 cm)
4. **Polygonisation de la zone d'intervention** : les cellules raster avec |diff| > 1 cm sont converties en une couche vectorielle de polygones, egalement ajoutee au groupe "Site Dashboard - Computi" avec un style mis en evidence, afin de montrer d'un seul coup d'oeil l'etendue globale de l'intervention.
5. **Zoom automatique** : la carte principale de QGIS est automatiquement zoomee sur l'emprise du calcul.

### Prerequis

Pour utiliser les nouvelles visualisations 2D / 3D, il faut :

- Avoir **deux couches raster DEM** chargees dans le projet QGIS (typiquement un DEM **pre**-fouille et un DEM **post**-fouille)
- Les selectionner dans les listes deroulantes **DEM Pre** et **DEM Post** du panneau Metrages
- Le systeme de coordonnees (SCR) des deux rasters doit etre coherent

### Nouveaux boutons

A cote du bouton **Calculer** sont desormais disponibles trois nouveaux boutons :

| Bouton | Description |
|--------|-------------|
| **Afficher 2D** | Recentre la carte QGIS sur l'emprise du dernier calcul. Utile pour revenir rapidement au metrage actif apres avoir travaille dans d'autres zones. |
| **Afficher 3D** | Ouvre une boite de dialogue 3D interactive qui utilise le DEM **pre** comme terrain, avec le raster de difference drappe par-dessus. Elle inclut : un spinbox pour l'**exageration verticale**, des cases a cocher pour afficher / masquer individuellement les couches et un bouton **Reinitialiser la vue**. |
| **Creer maillage 3D** | Construit des maillages TIN a partir des DEMs pre et post (via les algorithmes QGIS Processing). Les maillages peuvent etre affiches dans la vue 3D pour comparer visuellement les deux surfaces et le volume entre elles. |

<!-- IMAGE: Les nouveaux boutons Afficher 2D, Afficher 3D et Creer maillage 3D a cote du bouton Calculer -->
> **Fig. 14** : Les nouveaux boutons **Afficher 2D**, **Afficher 3D** et **Creer maillage 3D** a cote du bouton **Calculer**

<!-- IMAGE: Boite de dialogue 3D avec le DEM pre comme terrain et le raster de difference drappe -->
> **Fig. 15** : La boite de dialogue 3D interactive des metrages avec exageration verticale et controle des couches

### Flux de travail typique

1. Charger les deux rasters DEM (pre et post) dans le projet QGIS
2. Ouvrir le **Tableau de bord**
3. Dans la section **Metrages**, selectionner les deux DEMs dans **DEM Pre** et **DEM Post**
4. Cliquer sur **Calculer** : le raster de difference et le polygone d'intervention sont crees automatiquement et la carte se recentre sur l'emprise
5. Lire les valeurs numeriques (surface, volume, deblai, remblai) directement dans le panneau
6. Cliquer sur **Afficher 3D** pour ouvrir la vue tridimensionnelle
7. (Optionnel) Cliquer sur **Creer maillage 3D** pour generer et afficher les maillages TIN des deux DEMs
8. Cliquer sur **Sauvegarder** pour archiver le resultat dans l'historique

### Organisation sur le disque

Tous les rasters et couches generes par le metrage sont stockes dans :

```
<PYARCHINIT_HOME>/site_dashboard/<nom du site>/
```

ou `<PYARCHINIT_HOME>` est le dossier de travail configure dans les parametres de PyArchInit et `<nom du site>` est le site actuellement selectionne dans le tableau de bord. Cela permet de conserver un historique physique de tous les calculs et de reutiliser les couches dans d'autres projets QGIS.

### Mise a jour : "Afficher 2D" -- Boite de dialogue de coupe analytique

A partir de la prochaine version, le bouton **Afficher 2D** du panneau Metrages ne se contente plus de recentrer la carte sur le dernier calcul : il ouvre desormais une **boite de dialogue analytique basee sur matplotlib** qui presente les resultats de la fouille sous forme de coupe archeologique classique.

La boite de dialogue est disponible **uniquement lorsque le calcul a ete effectue en mode "Difference DEM"** (avec DEM pre et DEM post). Si vous avez utilise le mode **DEM + Polygone**, le bouton conserve son comportement precedent et se contente de zoomer la carte QGIS sur l'emprise du calcul.

Lorsqu'elle est disponible, la boite de dialogue contient les panneaux suivants :

| Panneau | Description |
|---------|-------------|
| **Carte de chaleur de la difference DEM** | Carte de chaleur 2D du raster deblai/remblai avec une rampe de couleurs divergente (rouge pour deblai, bleu pour remblai) |
| **Histogramme** | Distribution des profondeurs de **deblai** et des hauteurs de **remblai**, pour obtenir immediatement un resume statistique du volume deplace |
| **Coupe longitudinale (E-O)** | La coupe archeologique classique : le **DEM pre** est dessine en **bleu**, le **DEM post** en **rouge** et le volume excave est **rempli** entre les deux lignes |
| **Coupe transversale (N-S)** | Meme logique que la coupe E-O mais dans la direction Nord-Sud |
| **Spinbox ligne / colonne** | Permettent de faire defiler interactivement la position des deux coupes sur le raster pour explorer toute la fouille |
| **Bouton "Enregistrer PNG"** | Exporte l'ensemble de la figure (carte de chaleur, histogramme et les deux coupes) sous forme d'image PNG, prete a etre inseree dans le rapport de fouille |

<!-- IMAGE: Boite de dialogue analytique Afficher 2D avec carte de chaleur, histogramme et coupes E-O / N-S -->
> **Fig. 18** : La nouvelle boite de dialogue analytique **Afficher 2D** avec carte de chaleur de la difference DEM, histogramme deblai / remblai et les deux coupes longitudinale et transversale (DEM pre en bleu, DEM post en rouge, volume excave rempli entre les deux lignes)

### Mise a jour : "Afficher 3D" -- Repli matplotlib

Le bouton **Afficher 3D** gere maintenant automatiquement deux scenarios selon la version de QGIS installee :

1. **QGIS avec le module 3D natif (Qt3D disponible)** : comme auparavant, la boite de dialogue `Qgs3DMapCanvas` embarquee est ouverte, avec terrain genere a partir du DEM pre, exageration verticale et controle des couches.
2. **QGIS sans le module 3D (erreur "QGIS 3D module not available")** : le Tableau de Bord bascule automatiquement vers un **visualiseur 3D base sur matplotlib**. Comme matplotlib fait partie des dependances deja installees par le plugin, ce visualiseur **fonctionne toujours**, meme sur les builds QGIS minimaux compiles sans support 3D.

Le visualiseur de repli offre :

| Controle | Description |
|----------|-------------|
| **Mode d'affichage** | Trois modes selectionnables : **Pre + Post** (les deux surfaces superposees), **Difference uniquement** (uniquement la surface deblai/remblai), **Pre uniquement** (le DEM pre comme surface de reference) |
| **Exageration verticale** | Un curseur pour accentuer la difference d'altitude entre les deux surfaces -- utile lorsque la fouille est peu profonde |
| **Rotation interactive** | En cliquant-glissant avec la souris, il est possible de faire pivoter la scene 3D en temps reel pour explorer la fouille sous n'importe quel angle |

<!-- IMAGE: Visualiseur 3D matplotlib de repli en mode Pre + Post -->
> **Fig. 19** : Le visualiseur 3D matplotlib de repli, utilise lorsque le module Qt3D natif de QGIS n'est pas disponible : il montre les surfaces pre et post avec une exageration verticale reglable

### Mise a jour : "Creer maillage 3D" -- Symbologie terrain automatique

Le bouton **Creer maillage 3D** applique maintenant automatiquement une **rampe de couleurs de type terrain** au groupe de datasets d'elevation du maillage (**Bed Elevation**). Auparavant le maillage apparaissait comme une surface plate et peu lisible ; il devient desormais immediatement une carte d'altitudes expressive :

- **Vert** pour les altitudes les plus basses
- **Orange** pour les altitudes intermediaires
- **Marron** pour les altitudes les plus elevees

De cette facon, le maillage est immediatement visible et significatif dans la carte QGIS, meme avant d'ouvrir la vue 3D. Apres l'avoir construit, il suffit de cliquer sur **Afficher 3D** pour le voir rendu en tant que surface tridimensionnelle, que ce soit via le module 3D natif de QGIS ou via le visualiseur matplotlib de repli decrit ci-dessus.

<!-- IMAGE: Maillage 3D avec la nouvelle rampe terrain vert / orange / marron -->
> **Fig. 20** : Le maillage 3D avec la nouvelle rampe de couleurs de type terrain appliquee automatiquement a son dataset d'elevation

### Mise a jour : polygone comme masque de decoupe

Si, en plus des deux DEM, vous selectionnez egalement une couche vectorielle dans le combobox **Couche polygone** du panneau Computo Metrico tout en laissant active la modalite **Difference DEM**, le polygone est desormais utilise comme **masque de decoupe** : les deux DEM sont decoupes sur le polygone avant le calcul de la difference, de sorte que la section analytique 2D, le repli 3D matplotlib et le maillage TIN travaillent uniquement sur la zone d'intervention. Le flux typique est : tracer un polygone autour de la fouille, selectionner les DEM pre et post, choisir le polygone dans le combobox **Couche polygone** et appuyer sur **Calculer**. Les deux rasters decoupes sont automatiquement ajoutes au groupe **"Cruscotto Cantiere - Computi"** dans le panneau des couches, prets a etre reutilises.

### Mise a jour : "Creer maillage 3D" -- plus de plantages

Les versions precedentes pouvaient faire planter QGIS sur certains builds a cause d'un segfault C++ a l'interieur des algorithmes Processing utilises pour construire le maillage. La generation a ete reecrite en **Python pur** : le Tableau de Bord lit le DEM avec GDAL et ecrit directement un fichier 2DM contenant un **maillage de quadrangles en grille reguliere**, sans dependre des algorithmes natifs. Le resultat est sur sur n'importe quelle version de QGIS. Les maillages comportant plus d'environ **15 000 cellules** sont automatiquement sous-echantillonnes pour garder la construction rapide et le fichier leger, tandis que les cellules nodata sont ignorees : quand un masque polygonal est actif, le maillage suit donc exactement la forme de la zone d'intervention decoupee. Dans le rare cas ou la generation echoue pour d'autres raisons (disque plein, permissions), la boite de dialogue suggere maintenant d'ouvrir directement **Afficher 3D**, qui utilise le visualiseur matplotlib de repli et ne necessite aucune couche maillage.

### Mise a jour : rafraichissement automatique des combos au clic sur "Calculer"

Le panneau Computo Metrico **rafraichit maintenant automatiquement les listes DEM et polygone a chaque clic sur "Calculer"** : il n'est plus necessaire de fermer et rouvrir le Tableau de Bord apres avoir charge un nouveau raster ou dessine un nouveau polygone dans le projet. Il suffit d'ajouter la couche dans QGIS, de revenir sur le panneau et d'appuyer sur **Calculer** -- les combobox **DEM Pre**, **DEM Post** et **Couche polygone** sont repeuples a la volee avec l'etat courant du projet. Le diagnostic eventuel du decoupage (succes, SCR incompatible, intersection vide) est affiche dans la **barre de messages de QGIS**, de sorte que l'on sache toujours precisement quelles couches ont ete reellement utilisees dans le calcul.

### Mise a jour : bouton renomme "Exporter 2DM + 3D"

Le bouton precedemment intitule **Creer maillage 3D** a ete renomme **Exporter 2DM + 3D** pour refleter son nouveau comportement : il **ne charge plus** le maillage comme couche dans le projet QGIS (l'API mesh native peut provoquer des plantages sur certains builds de QGIS) et effectue a la place deux actions sures et complementaires. Il ecrit les fichiers **2DM** sur le disque a partir des DEM pre et post (utiles pour l'import dans un logiciel externe de post-traitement) et ouvre directement la **vue 3D matplotlib** sur les DEM decoupes, ce qui permet d'evaluer visuellement le resultat immediatement. Le risque de plantage est ainsi totalement ecarte, car l'API mesh de QGIS n'est jamais sollicitee.

### Mise a jour : decoupe du polygone avec diagnostic visible

Lorsque vous selectionnez une couche dans le combobox **Couche polygone** en meme temps que les deux DEM, le decoupage des rasters sur le polygone est desormais **trace dans la barre de messages de QGIS** : en cas de succes, la liste des fichiers decoupes ecrits sur le disque est affichee, tandis qu'en cas d'echec la raison precise est indiquee (par exemple polygone dans un SCR different de celui des DEM, aucune intersection geometrique entre polygone et raster, fichier source introuvable ou illisible). Il est ainsi immediat de comprendre pourquoi un decoupage n'a pas ete applique et que corriger (reprojeter le polygone, le deplacer au-dessus de la zone des DEM, verifier le chemin du fichier), sans avoir a ouvrir les logs ou la console Python.

### Mise a jour : decoupe du polygone aussi en mode "DEM sur Polygone"

La decoupe du polygone fonctionne maintenant egalement lorsque le bouton radio **DEM sur Polygone** est selectionne (mode zonal-stats avec un seul DEM) : le raster est decoupe a l'emprise du polygone **avant** d'etre transmis aux visualiseurs **Afficher 2D**, **Afficher 3D** et **Exporter 2DM + 3D**, de sorte que la coupe et la vue 3D affichent uniquement la zone d'intervention au lieu du DEM entier comme auparavant. Le message de diagnostic du decoupage apparait dans la **barre de messages de QGIS**, exactement comme en mode Difference DEM. Dans ce scenario a un seul DEM, le visualiseur **Afficher 2D** s'adapte automatiquement : la heat-map affiche les altitudes avec une rampe de couleurs **terrain**, l'histogramme represente la distribution des altitudes avec la ligne de la moyenne, et les deux coupes longitudinale/transversale tracent une seule ligne d'altitude (sans remplissage entre pre et post, car il n'y a pas de DEM post).

### Mise a jour : Analyse des Couts du Computo Metrico

Un nouveau bloc **Analyse des Couts** a ete ajoute au panneau Computo Metrico du Tableau de Bord avec deux parametres d'entree : **Cout unitaire** (en euros/m3) et **Productivite** (en m3/jour). A chaque pression sur **Calculer**, le panneau met automatiquement a jour trois valeurs derivees visibles d'un coup d'oeil : **Cout total** (volume x cout unitaire), **Jours estimes** (volume / productivite) et **Cout journalier** (cout unitaire x productivite). Les deux entrees sont sauvegardees automatiquement **par chantier** dans les parametres de QGIS (cles `pyArchInit/site_dashboard/costs/<chantier>/...`), il suffit donc de les saisir une seule fois par chantier : en changeant de chantier, les valeurs enregistrees sont rechargees automatiquement, et les trois totaux sont recalcules en temps reel a chaque nouveau metrage.

### Mise a jour : decoupe pre/post alignee

Le calcul de la difference DEM exige que les deux DEM (pre et post) soient exactement alignes sur la meme grille de pixels. Dans les versions precedentes, lorsqu'un polygone de decoupe etait utilise, les deux DEM decoupes pouvaient se retrouver sur des grilles legerement differentes et le calcul `pre - post` etait errone ou vide. Desormais, les deux decoupes utilisent la **resolution native du DEM pre** comme reference (memes `xRes` / `yRes` et meme alignement de grille), de sorte que les deux rasters decoupes sont toujours parfaitement alignes au pixel pres et que la difference produit un resultat valide. Meme les tranchees minimes dans lesquelles seulement "10 seaux de terre" (environ 1 m3) ont ete enleves sont desormais correctement detectees par le metrage.

### Mise a jour : nouveau combo "Murs / Structures"

Un deuxieme combo **Murs / Structures** a ete ajoute au panneau Computo Metrico : il permet de selectionner une couche de polygones representant des murs, des structures en elevation, des piliers ou d'autres elements construits qui **ne doivent pas etre comptabilises** dans le calcul des metres cubes de fouille. Lorsque l'on clique sur **Calculer**, les polygones des murs sont rasterises en NODATA sur le raster de difference decoupe et leurs cellules sont exclues du total du volume ; le message de diagnostic apparait dans la barre de messages de QGIS (par exemple `walls masked: muri_trincea_42`). Flux de travail archeologique typique : charger DEM pre + DEM post + polygone de la zone de fouille + polygone des murs decouverts, les selectionner tous les deux dans les deux combos et appuyer sur **Calculer** -- le volume fouille exclut automatiquement le volume des structures.

---

## Export PDF et CSV du tableau de bord

Le Tableau de Bord peut exporter un resume complet des donnees de gestion dans deux formats : **PDF** (document pagine, ideal pour remise au client ou archivage) et **CSV** (ideal pour analyses ulterieures dans Excel ou autres tableurs).

### Export PDF

Le bouton **Exporter PDF** genere un rapport complet du chantier. Depuis la version 5.1, le PDF inclut :

- **Page de couverture renouvelee** avec le nom du site, l'annee de reference et la date de generation
- **Resume du budget** avec tableaux detailles par categorie et totaux (prevu vs reel)
- **Resume du personnel** avec statistiques de presence, heures travaillees et couts
- **Resume des equipements** avec etat de l'inventaire et maintenances en retard
- **Nouvelle section "Computo Metrico"** contenant :
  - Tableau detaille de tous les calculs sauvegardes
  - **Totaux** : surface totale (m2) et volume total (m3)
  - **Statistiques** : volume de deblai, volume de remblai, surface concernee
- **Nouvelle section "Analyse des Couts"** (inseree entre **Computo Metrico** et **Statistiques**) avec une parameter card des valeurs configurees (cout unitaire en euros/m3 et productivite en m3/jour), un tableau detaille par enregistrement (date, type, volume, cout, jours estimes, cout journalier) et une ligne de **totaux** en bas du tableau ; le bloc **Statistiques** a ete etendu avec **cout total** et **jours totaux** de chantier
- **Prise en charge complete des caracteres speciaux** : le rendu PDF a ete corrige pour toutes les langues prises en charge, y compris les lettres accentuees du roumain (**a**, **a**, **i**, **s**, **t**), les caracteres **grecs**, **arabes**, **portugais** et **catalans**.

### Export CSV

Le bouton **Exporter CSV** genere un fichier CSV compatible avec les principaux tableurs. Depuis la version 5.1 :

- **Encodage UTF-8 avec BOM** : garantit qu'Excel (notamment en version europeenne) ouvre le fichier correctement sans corrompre les lettres accentuees et les caracteres speciaux
- **Separateur `;`** (point-virgule) : compatible avec la localisation europeenne d'Excel
- **Section COMPUTO METRICO** : comprend toutes les donnees de metrage, avec type, surface, volume et notes pour chaque calcul
- **Nouvelle section `=== ANALYSE DES COUTS ===`** : commence par les deux parametres (cout unitaire en euros/m3 et productivite en m3/jour) et est suivie du tableau detaille par enregistrement (date, type, volume, cout, jours estimes, cout journalier), pret a etre filtre ou agrege dans Excel
- **Bloc SUMMARY final etendu** : un resume agrege avec totaux et statistiques, utile pour des analyses rapides sans avoir a ecrire de formules ; il inclut maintenant egalement **Cout total** et **Jours totaux** calcules a partir de la nouvelle Analyse des Couts

<!-- IMAGE: PDF exporte avec la nouvelle section Computo Metrico -->
> **Fig. 16** : Exemple de PDF exporte avec la nouvelle section **Computo Metrico** (tableau, totaux et statistiques)

<!-- IMAGE: CSV exporte ouvert dans Excel avec la section COMPUTO METRICO et le bloc SUMMARY -->
> **Fig. 17** : Exemple de CSV exporte ouvert dans Excel avec la section **COMPUTO METRICO** et le bloc **SUMMARY** final

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
