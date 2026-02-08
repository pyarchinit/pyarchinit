# PyArchInit - StratiGraph : Panneau de Synchronisation

## Sommaire
1. [Introduction](#introduction)
2. [Acces au panneau](#acces-au-panneau)
3. [Comprendre l'interface](#comprendre-linterface)
4. [Exportation des bundles](#exportation-des-bundles)
5. [Synchronisation](#synchronisation)
6. [Gestion de la file d'attente](#gestion-de-la-file-dattente)
7. [Configuration](#configuration)
8. [Depannage](#depannage)
9. [Questions Frequentes](#questions-frequentes)

---

## Introduction

A partir de la version **5.0.2-alpha**, PyArchInit inclut un panneau **StratiGraph Sync** qui permet la synchronisation offline-first des donnees avec le Knowledge Graph de StratiGraph. Ce panneau fait partie du projet europeen **StratiGraph** (Horizon Europe) et implemente le flux de travail offline-first : vous travaillez localement sans internet, exportez des bundles quand vous etes pret, et le systeme se synchronise automatiquement lorsque la connectivite est retablie.

<!-- VIDEO : Introduction a StratiGraph Sync -->
> **Video Tutorial** : [Inserer le lien video introduction StratiGraph Sync]

### Apercu du flux de travail

```
1. Travail hors ligne   2. Exporter Bundle     3. Synchronisation
   (OFFLINE_EDITING)       (LOCAL_EXPORT)        (QUEUED_FOR_SYNC)
        |                      |                      |
   Saisie de donnees     Exporter + Valider     Upload quand en ligne
   normale dans          + Mettre en file       avec retry
   PyArchInit            d'attente              automatique
```

---

## Acces au panneau

Le panneau StratiGraph Sync est masque par defaut et peut etre active via un bouton dans la barre d'outils.

### Depuis la barre d'outils

1. Rechercher le bouton **StratiGraph Sync** dans la barre d'outils PyArchInit -- il a une icone verte avec des fleches de synchronisation et la lettre "S"
2. Cliquer sur le bouton pour **afficher** le panneau (c'est un bouton a bascule)
3. Cliquer a nouveau pour **masquer** le panneau

Le panneau apparait comme un **dock widget a gauche** dans l'interface QGIS. Vous pouvez le faire glisser et le repositionner comme tout autre panneau QGIS.

<!-- IMAGE : Bouton de la barre d'outils pour StratiGraph Sync -->
> **Fig. 1** : Le bouton StratiGraph Sync dans la barre d'outils (icone verte avec fleches de synchronisation et "S")

<!-- IMAGE : Panneau ancre sur le cote gauche de QGIS -->
> **Fig. 2** : Le panneau StratiGraph Sync ancre sur le cote gauche de la fenetre QGIS

---

## Comprendre l'interface

Le panneau StratiGraph Sync est divise en plusieurs sections, de haut en bas.

### Indicateur d'etat

L'**indicateur d'etat** en haut du panneau affiche l'etat actuel de synchronisation de vos donnees. Les etats possibles sont :

| Etat | Icone | Description |
|------|-------|-------------|
| **OFFLINE_EDITING** | Crayon | Vous travaillez localement, editant les donnees normalement |
| **LOCAL_EXPORT** | Paquet | Un bundle est en cours d'exportation depuis les donnees locales |
| **LOCAL_VALIDATION** | Coche | Le bundle exporte est en cours de validation |
| **QUEUED_FOR_SYNC** | Horloge | Le bundle a ete valide et attend d'etre televerse |
| **SYNC_SUCCESS** | Cercle vert | La derniere synchronisation s'est terminee avec succes |
| **SYNC_FAILED** | Cercle rouge | La derniere tentative de synchronisation a echoue |

### Indicateur de connexion

Sous l'indicateur d'etat, l'**indicateur de connexion** montre si le systeme peut atteindre le serveur StratiGraph :

| Statut | Signification |
|--------|---------------|
| **Online** | Le point de terminaison de health check est accessible ; la synchronisation automatique est active |
| **Offline** | Le point de terminaison de health check n'est pas accessible ; les bundles seront mis en file d'attente |

Le systeme verifie automatiquement la connectivite toutes les **30 secondes** (configurable).

### Compteur de file d'attente

Le **compteur de file d'attente** affiche deux nombres :

- **Bundles en attente** : Nombre de bundles attendant d'etre televerses
- **Bundles en echec** : Nombre de bundles dont le telechargement a echoue (seront automatiquement retentes)

### Derniere synchronisation

Affiche l'**horodatage** et le **resultat** (succes ou echec) de la derniere tentative de synchronisation.

### Boutons d'action

| Bouton | Action |
|--------|--------|
| **Export Bundle** | Cree un bundle depuis vos donnees locales, le valide et l'ajoute a la file de synchronisation |
| **Sync Now** | Force une tentative immediate de synchronisation (disponible uniquement en ligne) |
| **Queue...** | Ouvre la boite de dialogue de gestion de file d'attente affichant toutes les entrees |

### Journal d'activite

En bas du panneau, un **journal d'activite** deroulant affiche des entrees horodatees de l'activite recente, y compris les changements d'etat, les exportations, les validations et les tentatives de synchronisation.

<!-- IMAGE : Panneau complet avec toutes les sections annotees -->
> **Fig. 3** : Le panneau StratiGraph Sync complet avec toutes les sections etiquetees

---

## Exportation des bundles

L'exportation d'un bundle empaquete vos donnees archeologiques locales dans un format structure pret a etre televerse vers le Knowledge Graph de StratiGraph.

### Procedure etape par etape

1. S'assurer d'avoir sauvegarde tout le travail en cours dans PyArchInit
2. Ouvrir le panneau StratiGraph Sync (s'il n'est pas deja visible)
3. Cliquer sur le bouton **Export Bundle**
4. Le systeme effectue automatiquement trois operations :
   - **Exportation** : Les donnees locales sont empaquetees dans un fichier bundle
   - **Validation** : Le bundle est verifie pour la completude et l'integrite des donnees
   - **Mise en file d'attente** : Le bundle valide est ajoute a la file de synchronisation
5. Observer l'**indicateur d'etat** qui passe par : `LOCAL_EXPORT` -> `LOCAL_VALIDATION` -> `QUEUED_FOR_SYNC`
6. Le **journal d'activite** enregistre chaque etape avec un horodatage

### Que contient un bundle

Un bundle contient toutes les entites archeologiques qui ont des UUID (voir le Tutorial 31 pour les details sur les UUID). Chaque entite est identifiee par son `entity_uuid`, garantissant que le meme enregistrement est toujours reconnu sur le serveur.

<!-- IMAGE : Bouton Export Bundle et transition d'etat -->
> **Fig. 4** : Clic sur "Export Bundle" et observation des changements d'etat dans le panneau

---

## Synchronisation

### Synchronisation automatique

Lorsque le systeme detecte que vous etes **en ligne** (le health check reussit), il televerse automatiquement tous les bundles en attente de la file d'attente. Aucune intervention manuelle n'est requise.

Le processus de synchronisation automatique :

1. La verification de connectivite reussit (le point de terminaison de health check repond)
2. L'indicateur de connexion passe a **Online**
3. Les bundles en attente dans la file sont televerses un par un
4. Les bundles televerses avec succes sont marques comme `SYNC_SUCCESS`
5. L'horodatage et le resultat de la **derniere synchronisation** sont mis a jour

### Synchronisation manuelle

Si vous souhaitez forcer une tentative immediate de synchronisation :

1. S'assurer que l'indicateur de connexion affiche **Online**
2. Cliquer sur le bouton **Sync Now**
3. Le systeme tente immediatement de televerser tous les bundles en attente

Le bouton **Sync Now** n'est efficace que lorsque le systeme est en ligne.

### Retry automatique avec backoff exponentiel

Si un telechargement echoue, le systeme **n'abandonne pas**. Au lieu de cela, il retente automatiquement avec des delais croissants :

| Tentative | Delai |
|-----------|-------|
| 1er retry | 30 secondes |
| 2e retry | 60 secondes |
| 3e retry | 120 secondes |
| 4e retry | 5 minutes |
| 5e retry | 15 minutes |

Cela empeche de surcharger le serveur lorsqu'il est temporairement indisponible tout en assurant la livraison finale.

<!-- IMAGE : Bouton Sync Now et indicateur de connexion -->
> **Fig. 5** : Le bouton "Sync Now" et l'indicateur d'etat de connexion

---

## Gestion de la file d'attente

Le bouton **Queue...** ouvre une boite de dialogue detaillee ou vous pouvez inspecter tous les bundles dans la file de synchronisation.

### Colonnes de la boite de dialogue de file d'attente

| Colonne | Description |
|---------|-------------|
| **ID** | Identifiant unique de l'entree dans la file d'attente |
| **Status** | Etat actuel de l'entree (pending, syncing, success, failed) |
| **Attempts** | Nombre de tentatives de telechargement effectuees jusqu'a present |
| **Created** | Horodatage de l'ajout du bundle a la file d'attente |
| **Last Error** | Message d'erreur de la derniere tentative echouee (vide si aucune erreur) |
| **Bundle path** | Chemin du fichier bundle dans le systeme de fichiers |

### Interpreter les entrees de la file d'attente

- Les entrees **Pending** sont en attente de telechargement
- Les entrees **Success** ont ete televersees et confirmees par le serveur
- Les entrees **Failed** seront automatiquement retentees ; verifier la colonne **Last Error** pour les details
- Le nombre d'**Attempts** aide a comprendre combien de fois le systeme a tente de televerser un bundle particulier

### Stockage de la file d'attente

La base de donnees de la file d'attente est stockee comme fichier SQLite a :

```
$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite
```

Ce fichier persiste entre les sessions QGIS, donc les bundles en attente ne sont pas perdus si vous fermez QGIS.

<!-- IMAGE : Boite de dialogue de file d'attente montrant plusieurs entrees -->
> **Fig. 6** : La boite de dialogue de gestion de file d'attente avec les entrees de bundles

---

## Configuration

### URL de Health Check

Le systeme utilise une URL de health check pour determiner la connectivite avec le serveur StratiGraph. Vous pouvez la configurer dans les parametres QGIS :

| Parametre | Cle | Par defaut |
|-----------|-----|------------|
| URL Health check | `pyArchInit/stratigraph/health_check_url` | `http://localhost:8080/health` |

Pour modifier l'URL de health check :

1. Ouvrir **QGIS** -> **Preferences** -> **Options** (ou utiliser la console Python de QGIS)
2. Naviguer vers les parametres PyArchInit ou configurer via :

```python
from qgis.core import QgsSettings
s = QgsSettings()
s.setValue("pyArchInit/stratigraph/health_check_url", "https://votre-serveur.exemple.fr/health")
```

### Intervalle de verification

L'intervalle de verification de connectivite par defaut est de **30 secondes**. Ceci peut egalement etre configure via QgsSettings.

---

## Depannage

### Le panneau n'apparait pas

- S'assurer d'utiliser PyArchInit version **5.0.2-alpha** ou ulterieure
- Verifier que le bouton StratiGraph Sync est visible dans la barre d'outils
- Essayer de desactiver et reactiver le bouton
- Verifier **Vue** -> **Panneaux** dans QGIS pour voir si le dock widget est liste

### L'indicateur de connexion affiche toujours "Offline"

- Verifier que le serveur StratiGraph fonctionne et est accessible
- Verifier l'URL de health check dans les parametres (par defaut : `http://localhost:8080/health`)
- Tester l'URL manuellement dans un navigateur ou avec `curl` :

```bash
curl http://localhost:8080/health
```

- Si le serveur est sur une autre machine, s'assurer qu'aucune regle de pare-feu ne bloque la connexion

### L'exportation du bundle echoue

- S'assurer que la base de donnees est connectee et accessible
- Verifier que vos enregistrements ont des UUID valides (Tutorial 31)
- Consulter le journal d'activite pour les messages d'erreur specifiques
- S'assurer qu'il y a suffisamment d'espace disque pour le fichier bundle

### La synchronisation echoue a repetition

- Verifier la colonne **Last Error** dans la boite de dialogue de file d'attente pour les details
- Causes courantes :
  - Le serveur est temporairement indisponible (le systeme retentera automatiquement)
  - Problemes de connectivite reseau
  - Le serveur a rejete le bundle (verifier les logs du serveur)
- Si un bundle echoue constamment apres de nombreuses tentatives, envisager de le reexporter

### Problemes avec la base de donnees de la file d'attente

- La base de donnees de la file d'attente se trouve a `$PYARCHINIT_HOME/stratigraph_sync_queue.sqlite`
- Si elle est corrompue, vous pouvez la supprimer en toute securite -- les bundles en attente seront perdus, mais peuvent etre reexportes
- Sauvegarder ce fichier si vous devez preserver l'etat de la file d'attente

---

## Questions Frequentes

### Ai-je besoin d'internet pour utiliser PyArchInit ?

**Non.** PyArchInit est entierement fonctionnel hors ligne. Le panneau StratiGraph Sync ne gere que la synchronisation avec le serveur StratiGraph. Vous pouvez travailler entierement hors ligne et exporter/synchroniser quand vous etes pret.

### Que se passe-t-il si je ferme QGIS avec des bundles en attente ?

Les bundles en attente sont sauvegardes dans la base de donnees de la file d'attente et seront disponibles au redemarrage de QGIS. Le systeme reprend la synchronisation automatiquement lorsque la connectivite est retablie.

### Puis-je exporter plusieurs bundles ?

Oui. Chaque fois que vous cliquez sur "Export Bundle", un nouveau bundle est cree et ajoute a la file d'attente. Plusieurs bundles peuvent etre mis en file d'attente et seront televerses sequentiellement.

### Comment savoir si mes donnees ont ete synchronisees ?

Verifier l'indicateur de **derniere synchronisation** dans le panneau pour le resultat le plus recent. Vous pouvez egalement ouvrir la boite de dialogue **Queue...** pour voir l'etat de chaque bundle individuel.

### StratiGraph Sync fonctionne-t-il avec PostgreSQL et SQLite ?

Oui. Le systeme de synchronisation fonctionne avec les deux backends de base de donnees pris en charge par PyArchInit. Les bundles sont exportes dans un format independant de la base de donnees.

### Quelle est la relation entre les UUID et la synchronisation ?

Les UUID (Tutorial 31) fournissent les identifiants stables qui rendent la synchronisation possible. Chaque entite dans un bundle est identifiee par son UUID, permettant au serveur de faire correspondre, creer ou mettre a jour correctement les enregistrements.

---

*Documentation PyArchInit - StratiGraph Sync*
*Version : 5.0.2-alpha*
*Derniere mise a jour : Fevrier 2026*
