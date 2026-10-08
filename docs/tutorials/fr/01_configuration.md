# Tutorial 01 : Guide de Configuration PyArchInit

## Introduction

La fenêtre de configuration de PyArchInit permet de paramétrer tous les éléments nécessaires au bon fonctionnement du plugin. Avant de documenter une fouille archéologique, il est essentiel de configurer correctement la connexion à la base de données et les chemins des ressources.

---

## Accès à la Configuration

Pour accéder à la configuration :
1. Ouvrir QGIS
2. Menu **PyArchInit** → **Config**

Ou depuis la barre d'outils PyArchInit, cliquer sur l'icône **Paramètres**.

---

## Onglet Paramètres de Connexion

C'est l'onglet principal pour configurer la connexion à la base de données.

### Section DB Settings

| Champ | Description |
|-------|-------------|
| **Database** | Type de base de données : `sqlite` (local) ou `postgres` (serveur) |
| **Host** | Adresse du serveur PostgreSQL (ex. `localhost` ou IP) |
| **DBname** | Nom de la base de données (ex. `pyarchinit`) |
| **Port** | Port de connexion (défaut : `5432` pour PostgreSQL) |
| **User** | Nom d'utilisateur |
| **Password** | Mot de passe |
| **SSL Mode** | Mode SSL pour PostgreSQL : `allow`, `prefer`, `require`, `disable` |

### Choix de la Base de Données

**SQLite/Spatialite** (Recommandé pour utilisateur unique) :
- Base de données locale, aucun serveur requis
- Idéal pour projets individuels ou de petite taille
- Le fichier `.sqlite` est enregistré dans `pyarchinit_DB_folder`

**PostgreSQL/PostGIS** (Recommandé pour équipe) :
- Base de données sur serveur, accès multi-utilisateurs
- Nécessite PostgreSQL avec extension PostGIS
- Supporte la gestion des utilisateurs et permissions
- Idéal pour grands projets avec plusieurs opérateurs

### Section Path Settings

| Champ | Description |
|-------|-------------|
| **Thumbnail path** | Chemin pour les miniatures d'images |
| **Image resize** | Chemin pour les images redimensionnées |
| **Logo path** | Chemin du logo personnalisé pour les rapports |

#### Chemins Distants Supportés

PyArchInit supporte également le stockage distant :
- **Google Drive** : `gdrive://folder/path/`
- **Dropbox** : `dropbox://folder/path/`
- **Amazon S3** : `s3://bucket/path/`
- **Cloudinary** : `cloudinary://cloud_name/folder/`
- **WebDAV** : `webdav://server/path/`
- **HTTP/HTTPS** : `https://server/path/`

> **Configurer les médias sur WebDAV.** Pour utiliser un serveur WebDAV comme stockage d'images :
>
> 1. **Identifiants** — boîte de dialogue **Remote Storage Config**, onglet **WebDAV** : saisissez le *nom d'utilisateur* et le *mot de passe*.
> 2. **Verify SSL** (même onglet) — si le serveur utilise un **certificat auto-signé** (typique des serveurs sur une adresse IP brute ou un port HTTPS non standard), réglez **« Verify SSL » → No (Self-signed certificates)** : avec la vérification activée face à un serveur auto-signé, la connexion échoue silencieusement. Pour les serveurs disposant d'un certificat valide (par ex. Nextcloud/ownCloud), laissez-la sur **Yes (Verify certificates)**, qui est la valeur par défaut.
> 3. **Chemins** — dans les champs **Thumbnail path** et **Thumbnail resize**, utilisez le format `webdav://serveur:port/dossier/` (par ex. `webdav://192.0.2.10:5006/pyarchinit_media/thumb_resize/`).
> 4. **Redémarrez QGIS** après l'enregistrement pour que les nouveaux paramètres de stockage prennent effet.

### Dossier de données de pyArchInit 5 (`~/pyarchinit_5`)

pyArchInit 5 stocke toutes ses données de travail — `config.cfg`, bases de données, exports, sauvegardes, paradata et le dossier `bin/` contenant les outils IA — dans un dossier dédié du répertoire utilisateur : **`~/pyarchinit_5/`**.

Ce dossier est distinct du pyArchInit classique, qui continue d'utiliser **`~/pyarchinit/`**. Les deux versions ne partagent donc **pas** leurs données, ce qui permet d'exécuter pyArchInit 5 tandis que l'installation précédente et ses bases de données restent intactes.

**Premier démarrage — copie des données existantes.** Lors du premier démarrage de pyArchInit 5, si `~/pyarchinit_5` n'existe pas encore mais qu'une installation précédente `~/pyarchinit` est trouvée, une boîte de dialogue demande si la configuration et les bases de données doivent être copiées dans le nouveau dossier :

- Choisissez **Oui** pour copier `pyarchinit_DB_folder` (c'est-à-dire `config.cfg` et les bases SQLite) dans `~/pyarchinit_5`, afin de pouvoir continuer à travailler immédiatement avec vos données existantes.
- Le **dossier `bin/` n'est pas copié**, car il contient de volumineux assets IA (environnements virtuels SAM et céramique, modèles CLIP, index FAISS, fichiers de clés API). Recréez-les en exécutant à nouveau les fonctions IA concernées, ou copiez manuellement `~/pyarchinit/bin` dans `~/pyarchinit_5/bin`.
- Si vous choisissez **Non**, pyArchInit 5 crée simplement une nouvelle structure de dossiers vide, comme lors d'une installation fraîche.

> **Nouveauté 5.13.16-alpha — premier démarrage plus clair.**
> - La question « copier la configuration et les bases de données dans le nouveau dossier `~/pyarchinit_5` ? » apparaît désormais toujours au premier plan, devant toutes les fenêtres. Auparavant, surtout sous Windows, elle pouvait rester cachée derrière QGIS ou l'écran de démarrage (splash) et le démarrage semblait bloqué. Répondez **Oui** ou **Non** pour continuer.
> - Pendant l'installation des paquets Python manquants, l'écran de démarrage de pyArchInit reste au premier plan avec une barre de progression indiquant le paquet n sur N, le pourcentage et le temps écoulé. L'installation peut prendre plusieurs minutes : ne fermez pas QGIS. Sous Windows, aucune fenêtre de console ne s'ouvre pendant l'installation.

> **Nouveauté 5.13.17-alpha — QGIS 4 et plusieurs versions de QGIS sur le même ordinateur.**
> - Les paquets Python de pyArchInit sont installés avec le Python du QGIS que vous utilisez (par exemple Python 3.12 dans QGIS 4). Auparavant, avec QGIS 3 et QGIS 4 installés ensemble sous macOS, ils étaient installés pour le Python de QGIS 3 et QGIS 4 s'arrêtait avec l'erreur `No module named 'psycopg2._psycopg'`.
> - Si le dossier du plugin contient des paquets installés pour un autre Python (par exemple un profil QGIS 3 copié dans QGIS 4), au démarrage pyArchInit les déplace dans le dossier `ext_libs_cp39` (le nom indique la version de Python) et réinstalle ceux dont il a besoin : la première fois, cela peut prendre quelques minutes, avec la progression affichée sur l'écran de démarrage (splash). Le message apparaît dans le panneau des journaux de QGIS, onglet « PyArchInit ».
> - Les dossiers `ext_libs_cp…` peuvent être supprimés. Si vous utilisez le même plugin depuis deux versions de QGIS, pyArchInit remet en place le bon dossier au lieu de réinstaller.

**Emplacement personnalisé (avancé).** Pour utiliser un dossier de données différent, définissez la variable d'environnement `PYARCHINIT_HOME` avant de démarrer QGIS ; lorsqu'elle est définie, elle remplace l'emplacement par défaut `~/pyarchinit_5`.

### Boutons d'Action

| Bouton | Fonction |
|--------|----------|
| **Sauvegarder les paramètres** | Enregistre toutes les configurations |
| **Mettre à jour DB** | Met à jour le schéma sans perdre les données |
| **Aligner Postgres** | Aligne la structure PostgreSQL |
| **Aligner Spatialite** | Aligne la structure SQLite |

---

## Onglet Installation DB

Permet de créer une nouvelle base de données.

### Installation PostgreSQL/PostGIS

| Champ | Description |
|-------|-------------|
| **host** | Adresse du serveur (défaut : `localhost`) |
| **port** | Port PostgreSQL (5432) |
| **user** | Utilisateur avec droits de création |
| **password** | Mot de passe |
| **db name** | Nom de la nouvelle base |
| **Sélectionner SRID** | Système de référence spatiale |

### Installation SpatiaLite

| Champ | Description |
|-------|-------------|
| **db name** | Nom du fichier base de données |
| **Sélectionner SRID** | Système de référence spatiale |

### SRID Courants

| SRID | Description |
|------|-------------|
| 4326 | WGS 84 (coordonnées géographiques) |
| 32631 | WGS 84 / UTM zone 31N (France Nord) |
| 32632 | WGS 84 / UTM zone 32N (France Est) |
| 2154 | RGF93 / Lambert-93 (France métropolitaine) |

---

## Onglet Outils d'Importation

Permet d'importer des données depuis d'autres bases ou fichiers CSV.

### Base Source et Destination

Configurez séparément :
- **Base source** : D'où proviennent les données
- **Base destination** : Où importer les données

### Tables Disponibles pour Import

| Table | Description |
|-------|-------------|
| SITE | Sites archéologiques |
| US | Unités Stratigraphiques |
| PERIODISATION | Périodisation et phases |
| INVENTARIO_MATERIALI | Inventaire du mobilier |
| POTTERY | Céramique |
| STRUTTURA | Structures |
| TOMBA | Tombes |
| ALL | Toutes les tables |

### Options d'Import

| Option | Description |
|--------|-------------|
| **Replace** | Remplace les enregistrements existants |
| **Ignore** | Ignore les doublons |
| **Abort** | Interrompt en cas d'erreur |

---

### Exporter un site en em.json (Extended Matrix)

Depuis le menu **pyArchInit → Extended Matrix → Esporta sito in em.json…** (Exporter le site en em.json), un site entier passe dans le format de travail de l'Extended Matrix, celui qu'**EMStudio** ouvre nativement.

À quoi s'attendre :

- pyArchInit liste les sites de la base : on en choisit **un** ;
- le fichier naît dans `pyarchinit_EM_folder`, dans le dossier de données du plugin, au nom du site (tout alphabet : `Al-Khutm.em.json`, `Scavo_archeologico.em.json`) ;
- avant de le livrer, pyArchInit **relit le fichier** : un export qui ne se relit pas à l'identique n'est pas livré ;
- à la fin, il demande s'il faut l'**ouvrir tout de suite dans EMStudio** ; si EMStudio n'est pas installé, pyArchInit indique où se trouve le fichier et **propose de l'installer maintenant** (voir le paragraphe suivant).

Le fichier ne contient que le site choisi, et chaque unité y arrive pour ce qu'elle est :

- **seulement les lignes de ce site** : dans une base à plusieurs sites, la documentation et les périodes des autres sites n'entrent plus dans l'export ;
- **chaque unité avec le type qu'elle déclare** : les unités virtuelles restent virtuelles, les special finds et les continuités restent eux-mêmes, si bien qu'EMStudio dessine le bon symbole au lieu de tout transformer en couche ;
- **les paradonnées voyagent comme paradonnées**, non comme unités stratigraphiques ;
- une **colonne vide** de la fiche ne devient plus une propriété vide dans le graphe.

Ce que le panneau **« Vedi la matrice »** dessine est exactement ce que contient le fichier : y jeter un œil est le moyen le plus rapide de vérifier l'export avant de l'envoyer dans EMStudio ou dans une salle.

> **Note** : le GraphML ne survit que comme **import ponctuel depuis yEd** ; le format pour regarder et valider la matrice est em.json.

### Installer EMStudio depuis le menu

**EMStudio** est le visualiseur de l'Extended Matrix : un programme à part du projet Extended Matrix (licence GPL-3). pyArchInit ne le contient pas — il le **télécharge et le lance**, quand on le lui demande.

Avec **pyArchInit → Extended Matrix → Installa EMStudio…** (Installer EMStudio) :

1. pyArchInit lit les releases officielles d'EMStudio et **choisit le paquet pour cet ordinateur** (macOS Apple Silicon, Windows, Linux) ;
2. avant de télécharger, il affiche une fenêtre avec **version, nom du fichier, taille, adresse de téléchargement et dossier de destination** — `<dossier de données de pyArchInit>/tools/EMStudio` — et attend un oui ;
3. une fois le téléchargement terminé, il **vérifie l'empreinte sha256** déclarée par la release : un fichier qui ne correspond pas n'est pas installé ;
4. sur macOS, **retirer la quarantaine** fait partie de l'installation : la build n'est pas signée par Apple et, sans cette étape, le système dirait que l'application est « endommagée » ;
5. à la fin, il indique où l'installation a eu lieu. Si EMStudio était déjà là, il demande s'il faut retélécharger la dernière version.

Si l'export en em.json ne trouve pas EMStudio, il **propose de l'installer sur le champ** puis ouvre le fichier.

> **Limite connue** : la release du jour ne publie aucun paquet pour les **Mac Intel**. Dans ce cas, pyArchInit le dit et renvoie à la page des releases (github.com/ExtendedMatrix/EMStudio/releases), d'où le télécharger à la main.

### Voir la matrice dans QGIS

Depuis le menu **pyArchInit → Extended Matrix → Vedi la matrice…** (Voir la matrice), la matrice d'un site se dessine dans un **panneau ancré à droite** de la fenêtre de QGIS. Pas besoin d'EMStudio, ni d'un nœud StratiGraph, ni de se connecter, ni d'internet : pyArchInit exporte l'em.json du site dans un dossier temporaire et le dessine.

À quoi s'attendre :

- on choisit le **site** dans une liste ; le panneau s'ouvre avec la matrice déjà ajustée à la fenêtre et, en haut, une ligne qui dit **combien d'unités, combien d'époques et combien de rapports** ont été dessinés ;
- le dessin a **une bande horizontale par période/phase**, la **plus récente en haut**, chacune avec son nom, ses années et sa propre couleur ;
- chaque unité se trouve dans la bande de la période où elle est née, et dans la bande c'est la stratigraphie qui décide du niveau : **ce qui recouvre est dessiné au-dessus de ce qui est recouvert** ;
- chaque unité est dessinée avec la **symbologie de l'Extended Matrix**, celle des règles s3dgraphy (voir le tableau) ;
- la **molette de la souris** agrandit et réduit, un **double clic** remet toute la matrice dans la fenêtre (comme le bouton **Adatta** / Ajuster), un **clic sur une unité** montre sa fiche dans le cadre de droite : définition, interprétation, période et phase, datation, aire, structure.

| Unité | Symbole |
|---|---|
| US — unité stratigraphique | rectangle |
| USVs — unité virtuelle structurelle | parallélogramme bleu |
| USVn — unité virtuelle non structurelle | hexagone vert |
| SF — mobilier remarquable (special find) | octogone olive |
| BR / CON — continuité | losange noir |
| Extracteur | pentagone |
| Combinateur | hexagone en pointillé |
| Document | ellipse |
| Propriété | cercle en pointillé |

**Salva SVG…** (Enregistrer le SVG) et **Salva PNG…** (Enregistrer le PNG) enregistrent le dessin où l'on veut. Le **SVG est vectoriel** : il s'ouvre dans un navigateur ou dans Inkscape, s'agrandit autant qu'il faut sans se flouter et s'imprime à n'importe quelle taille, affiches comprises.

La même matrice s'ouvre aussi depuis la fenêtre **« Export Extended Matrix »** de la fiche US : le bouton **« Vedi la matrice »**, à côté d'**« Apri in EMStudio »**, s'allume après un export em.json réussi et dessine le fichier qui vient d'être exporté.

> **Note** : sur un site très grand, le panneau le dit de lui-même, par un message dans la barre de messages de QGIS, et conseille d'**enregistrer le SVG et de le regarder hors de QGIS** : parcourir à l'écran un dessin de milliers d'unités est lent.

> **Note** : la matrice se dessine aussi quand la fouille n'est pas en ordre. Les rapports qui pointent vers un élément de paradata restent dans le dessin, et les unités dont le niveau ne peut pas être décidé parce que les rapports contiennent une boucle sont dessinées quand même : le panneau ne refuse pas une fouille réelle.

### Livrer un site à une salle StratiGraph

Depuis **pyArchInit → Extended Matrix → Consegna sito alla stanza…** (Livrer le site à la salle), les unités stratigraphiques d'un site voyagent vers une **salle** d'un nœud StratiGraph (REST, une livraison à la fois — pas besoin de rester connecté).

À quoi s'attendre :

- on choisit le **site**, puis la fenêtre demande le **nœud** (p. ex. `http://127.0.0.1:8020` ; pour un nœud institutionnel `https://noeud.org/em` — écrire la racine fonctionne aussi, `/em` est trouvé tout seul), la **salle** et, seulement si le nœud l'exige, un **jeton** (mieux dans la variable d'environnement `STRATIGRAPH_TOKEN` : il n'est jamais enregistré) ;
- le résultat est une phrase : *« 129 appliquées sur 129 »* à la première livraison ; à la seconde *« 44 appliquées sur 129, 85 déjà présentes »* — **les répétitions ne dupliquent rien** : les nœuds fusionnent, les arcs déjà connus reviennent comme « déjà présents » ;
- les lignes qui ne peuvent pas devenir des unités de la salle (documents, extracteurs, propriétés) sont listées sous *Afficher les détails*, jamais inventées ;
- **qui signe est qui livre** : l'auteur est écrit par le nœud à partir de l'identité vérifiée, pas par le payload.

Avec **Extended Matrix → Apri il nodo (stanze)…** (Ouvrir le nœud (salles)), la salle s'ouvre **dans pyArchInit** (panneau latéral) : on utilise Qt WebEngine si le profil QGIS l'a, sinon Qt WebKit, que QGIS 3 livre encore — ainsi le panneau reste dans QGIS même là où WebEngine manque, et le navigateur externe n'est plus que l'ultime recours. Avec une salle configurée, c'est sa page qui s'ouvre directement ; sans salle, c'est la porte du nœud avec toutes les salles.

---

## Onglet Graphviz

Graphviz est nécessaire pour générer les diagrammes de la Matrice de Harris.

### Configuration

| Champ | Description |
|-------|-------------|
| **Chemin bin** | Chemin vers le dossier `/bin` de Graphviz |
| **Sauvegarder** | Enregistre le chemin dans PATH |

### Installation Graphviz

**Windows** : Télécharger depuis https://graphviz.org/download/

**macOS** :
```bash
brew install graphviz
```

**Linux (Ubuntu/Debian)** :
```bash
sudo apt-get install graphviz
```

---

## Onglet FTP vers Lizmap

Permet de publier les données sur un serveur Lizmap pour la visualisation web.

### Paramètres de Connexion FTP

| Champ | Description |
|-------|-------------|
| **Adresse IP** | Adresse du serveur FTP |
| **Port** | Port FTP (défaut : 21) |
| **User** | Nom d'utilisateur FTP |
| **Password** | Mot de passe FTP |

### Opérations Disponibles

- Connecter/Déconnecter
- Changer de répertoire
- Créer un répertoire
- Télécharger/Uploader des fichiers

---

## Espace de travail Paradata (PostgreSQL uniquement)

Dans l'**onglet DB Sync** de la fenêtre de configuration se trouve la section **Paradata Workspace**, qui permet de personnaliser le répertoire où sont enregistrés les fichiers `paradata_<site>.graphml` et `groups_<site>.graphml` lorsque l'on travaille avec une base de données PostgreSQL.

> **PostgreSQL uniquement** : les utilisateurs SQLite ne sont pas concernés. Avec SQLite, les fichiers paradata sont toujours stockés à côté du fichier `.sqlite` (comportement hérité, byte-identique).

### Chemin par défaut

Sans override, le chemin résolu est :

```
~/pyarchinit/pyarchinit_DB_folder/<host>_<port>_<dbname>/<site>/
```

Exemple : `~/pyarchinit/pyarchinit_DB_folder/localhost_5432_pyarchinit/Volterra/`

### Personnaliser le chemin

- **Parcourir...** ouvre une boîte de dialogue pour choisir un répertoire. Le chemin est immédiatement enregistré dans les QSettings de QGIS.
- Vous pouvez également **saisir** le chemin directement dans le champ texte : la valeur est persistée à la sortie du champ (signal `editingFinished`). Laisser le champ vide supprime l'override.
- **Réinitialiser** efface le champ, supprime la clé des QSettings et restaure le chemin par défaut.

### Chaîne de résolution (qui l'emporte)

Le chemin effectif suit une chaîne de fallback à 3 niveaux :

1. **Variable d'environnement `PYARCHINIT_WORKSPACE_DIR`** (priorité maximale — utile pour les scripts CI/test).
2. **QSettings `pyarchinit/paradata_workspace`** (override de l'UI — cette section).
3. **Valeur par défaut** `~/pyarchinit/pyarchinit_DB_folder/`.

Les valeurs vides sont ignorées : si `PYARCHINIT_WORKSPACE_DIR=""`, la résolution passe au niveau 2 ; si les QSettings sont également vides, on utilise la valeur par défaut.

### Quand le changement prend effet

Les modifications sont **immédiates** : le prochain accès à ParadataStore / GroupStore (par exemple, sauvegarde de paradata sur une fiche US ou export d'une Matrix) utilise le nouveau chemin. **Aucun redémarrage de QGIS n'est nécessaire.**

### Cas d'usage

- **Lecteur réseau partagé** : pointer le workspace vers un chemin réseau (ex. `/Volumes/team/pyarchinit_workspace`) pour partager les paradata entre utilisateurs sur un PostgreSQL centralisé.
- **Sauvegarde séparée** : garder les fichiers paradata en dehors du répertoire utilisateur pour faciliter les sauvegardes dédiées.
- **Tests isolés** : définir `PYARCHINIT_WORKSPACE_DIR` dans les scripts de test pour ne pas polluer le workspace par défaut.

---

## Workflow Recommandé pour Nouveau Projet

1. **Ouvrir la Configuration** depuis le menu PyArchInit
2. **Choisir le type de base de données** (SQLite ou PostgreSQL)
3. **Onglet Installation DB** : Créer une nouvelle base avec le SRID approprié
4. **Onglet Paramètres** : Configurer la connexion
5. **Définir les chemins** pour miniatures, images et logo
6. **Sauvegarder les paramètres**
7. **Tester la connexion** en ouvrant une fiche (ex. Site)

---

## Résolution des Problèmes

### Erreur de connexion PostgreSQL
- Vérifier que le serveur PostgreSQL est démarré
- Contrôler host, port et identifiants
- Vérifier que l'extension PostGIS est installée

### Base SQLite non trouvée
- Vérifier que le fichier existe dans `pyarchinit_DB_folder`
- Contrôler les permissions de lecture/écriture

### Graphviz ne fonctionne pas
- Vérifier l'installation de Graphviz
- Configurer manuellement le chemin
- Redémarrer QGIS après configuration

---

## Video Tutorial

### Configuration Complète
`[Placeholder : video_configuration.mp4]`

**Contenus** :
- Choix du type de base de données
- Configuration des connexions
- Installation Graphviz
- Test de connexion

**Durée prévue** : 15-20 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour mieux comprendre le processus d'installation et de configuration.

[Ouvrir l'Animation Installation](../../animations/pyarchinit_installation_animation.html)

Explorez l'animation interactive pour la gestion du stockage distant.

[Ouvrir l'Animation Stockage Distant](../../animations/pyarchinit_remote_storage_animation.html)
