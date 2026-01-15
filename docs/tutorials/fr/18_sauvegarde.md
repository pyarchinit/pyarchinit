# Tutorial 18 : Sauvegarde et Restauration

## Introduction

La gestion des **sauvegardes** est fondamentale pour la sécurité des données archéologiques. PyArchInit offre des outils pour effectuer des sauvegardes de la base de données et des fichiers associés, aussi bien pour SQLite que pour PostgreSQL.

### Importance de la Sauvegarde

- **Protection des données** : protection contre les pertes accidentelles
- **Versioning** : possibilité de revenir à des états antérieurs
- **Migration** : transfert entre systèmes
- **Archivage** : conservation des projets terminés

---

## Types de Sauvegarde

### Sauvegarde Base de Données SQLite

Pour les bases de données SQLite (fichier `.sqlite`) :
- Copie directe du fichier de base de données
- Simple et rapide
- Inclut toutes les données

### Sauvegarde Base de Données PostgreSQL

Pour les bases de données PostgreSQL :
- Export via `pg_dump`
- Format SQL ou personnalisé
- Peut inclure schéma et/ou données

### Sauvegarde Complète

Inclut :
- Base de données
- Fichiers médias (images, vidéos)
- Fichiers de configuration
- Rapports générés

---

## Accès aux Fonctions de Sauvegarde

### Via Panneau Configuration

1. Menu **PyArchInit** > **Sketchy GPT** > **Settings** (ou Settings directement)
2. Dans la fenêtre de configuration
3. Onglet ou section dédié à la sauvegarde

### Via Système de Fichiers

Pour SQLite, il est possible de copier directement :
```
[PYARCHINIT_HOME]/pyarchinit_DB_folder/pyarchinit_db.sqlite
```

---

## Sauvegarde SQLite

### Procédure Manuelle

1. **Fermer** toutes les fiches PyArchInit ouvertes
2. **Localiser** le fichier base de données :
   ```
   ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
   Sur Windows :
   ```
   C:\Users\[utilisateur]\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
   ```

3. **Copier** le fichier dans un dossier de sauvegarde :
   ```
   pyarchinit_db_backup_2024-01-15.sqlite
   ```

4. **Vérifier** l'intégrité en ouvrant la copie avec un outil SQLite

### Script Automatique (optionnel)

Pour des sauvegardes automatiques, créer un script :

**Linux/Mac (bash) :**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
SOURCE=~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite
DEST=~/pyarchinit_backups/pyarchinit_db_$DATE.sqlite
cp "$SOURCE" "$DEST"
echo "Sauvegarde terminée : $DEST"
```

**Windows (batch) :**
```batch
@echo off
set DATE=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set SOURCE=%USERPROFILE%\pyarchinit\pyarchinit_DB_folder\pyarchinit_db.sqlite
set DEST=%USERPROFILE%\pyarchinit_backups\pyarchinit_db_%DATE%.sqlite
copy "%SOURCE%" "%DEST%"
echo Sauvegarde terminée : %DEST%
```

---

## Sauvegarde PostgreSQL

### Utilisation de pg_dump

1. **Ouvrir** un terminal/invite de commandes

2. **Exécuter** pg_dump :
   ```bash
   pg_dump -h localhost -U postgres -d pyarchinit -F c -f backup_pyarchinit.dump
   ```

   Paramètres :
   - `-h` : hôte de la base de données
   - `-U` : utilisateur
   - `-d` : nom de la base de données
   - `-F c` : format personnalisé (compressé)
   - `-f` : fichier de sortie

3. **Entrer** le mot de passe quand demandé

### Sauvegarde Données Uniquement

```bash
pg_dump -h localhost -U postgres -d pyarchinit --data-only -f backup_donnees.sql
```

### Sauvegarde Schéma Uniquement

```bash
pg_dump -h localhost -U postgres -d pyarchinit --schema-only -f backup_schema.sql
```

---

## Sauvegarde des Fichiers Médias

### Dossier Médias

Les fichiers médias sont dans le dossier :
```
[PYARCHINIT_HOME]/pyarchinit_image_folder/
```

### Procédure

1. **Localiser** le dossier :
   ```
   ~/pyarchinit/pyarchinit_image_folder/
   ```

2. **Copier** l'intégralité du dossier :
   ```bash
   cp -r ~/pyarchinit/pyarchinit_image_folder ~/backup/pyarchinit_media_backup/
   ```

3. **Compresser** (optionnel) :
   ```bash
   tar -czvf pyarchinit_media_backup.tar.gz ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Restauration

### Restauration SQLite

1. **Fermer** QGIS et PyArchInit
2. **Renommer** la base de données actuelle (par sécurité) :
   ```bash
   mv pyarchinit_db.sqlite pyarchinit_db_old.sqlite
   ```
3. **Copier** la sauvegarde dans le dossier original :
   ```bash
   cp backup/pyarchinit_db_backup.sqlite pyarchinit_DB_folder/pyarchinit_db.sqlite
   ```
4. **Redémarrer** QGIS

### Restauration PostgreSQL

1. **Créer** une base de données vide (si nécessaire) :
   ```bash
   createdb -U postgres pyarchinit_restored
   ```

2. **Restaurer** la sauvegarde :
   ```bash
   pg_restore -h localhost -U postgres -d pyarchinit_restored backup_pyarchinit.dump
   ```

3. **Mettre à jour** la configuration de PyArchInit pour utiliser la nouvelle base de données

### Restauration des Fichiers Médias

1. **Copier** les fichiers de sauvegarde dans le dossier médias :
   ```bash
   cp -r backup/pyarchinit_media_backup/* ~/pyarchinit/pyarchinit_image_folder/
   ```

---

## Sauvegarde Complète du Projet

### Éléments à Inclure

| Élément | Chemin |
|---------|--------|
| Base de données SQLite | `pyarchinit_DB_folder/pyarchinit_db.sqlite` |
| Médias | `pyarchinit_image_folder/` |
| PDF générés | `pyarchinit_PDF_folder/` |
| Rapports | `pyarchinit_Report_folder/` |
| Configuration | `pyarchinit_Logo_folder/`, fichiers .txt |

### Script Sauvegarde Complète

**Linux/Mac :**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR=~/pyarchinit_backup_$DATE
mkdir -p "$BACKUP_DIR"

# Base de données
cp ~/pyarchinit/pyarchinit_DB_folder/pyarchinit_db.sqlite "$BACKUP_DIR/"

# Médias
cp -r ~/pyarchinit/pyarchinit_image_folder "$BACKUP_DIR/"

# PDF et Rapports
cp -r ~/pyarchinit/pyarchinit_PDF_folder "$BACKUP_DIR/"
cp -r ~/pyarchinit/pyarchinit_Report_folder "$BACKUP_DIR/"

# Compresser
tar -czvf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"

echo "Sauvegarde complète : $BACKUP_DIR.tar.gz"
```

---

## Bonnes Pratiques

### Fréquence des Sauvegardes

| Type d'activité | Fréquence conseillée |
|-----------------|----------------------|
| Fouille active | Quotidienne |
| Post-fouille | Hebdomadaire |
| Archivage | Avant chaque modification significative |

### Conservation

- Maintenir au moins **3 copies** en lieux différents
- Utiliser un **stockage cloud** pour la redondance
- **Vérifier périodiquement** l'intégrité des sauvegardes

### Nomenclature

Format conseillé :
```
[projet]_[type]_[date]_[version]
Exemple : villa_romaine_db_20240115_v1.sqlite
```

### Documentation

Créer un journal des sauvegardes :
```
Date : 2024-01-15
Type : Sauvegarde complète
Fichier : villa_romaine_backup_20240115.tar.gz
Taille : 2.5 Go
Notes : Pré-clôture campagne 2024
```

---

## Automatisation des Sauvegardes

### Cron Job (Linux/Mac)

Ajouter au crontab (`crontab -e`) :
```
# Sauvegarde quotidienne à 23h00
0 23 * * * /path/to/backup_script.sh
```

### Planificateur de Tâches (Windows)

1. Ouvrir le **Planificateur de tâches**
2. Créer une tâche de base
3. Définir le déclencheur (quotidien)
4. Action : Démarrer un programme > script batch

---

## Résolution des Problèmes

### Problème : Base de données corrompue après restauration

**Cause** : Fichier de sauvegarde incomplet ou endommagé.

**Solution** :
1. Vérifier l'intégrité avec `sqlite3 database.sqlite "PRAGMA integrity_check;"`
2. Utiliser une sauvegarde antérieure
3. Tenter une récupération avec les outils SQLite

### Problème : Taille de sauvegarde excessive

**Cause** : Nombreux fichiers médias ou base de données très volumineuse.

**Solution** :
1. Compresser les sauvegardes
2. Exécuter VACUUM sur la base de données
3. Archiver séparément les médias plus anciens

### Problème : pg_dump erreur de connexion

**Cause** : Paramètres de connexion incorrects.

**Solution** :
1. Vérifier hôte, port, utilisateur
2. Contrôler pg_hba.conf pour les permissions
3. Tester la connexion avec psql

---

## Migration entre Bases de Données

### De SQLite vers PostgreSQL

1. Exporter les données depuis SQLite
2. Créer le schéma dans PostgreSQL
3. Importer les données

PyArchInit gère cela via les paramètres de configuration.

### De PostgreSQL vers SQLite

1. Exporter les données depuis PostgreSQL
2. Créer la base de données SQLite
3. Importer les données

---

## Références

### Chemins Standards

| Système | Chemin de base |
|---------|----------------|
| Linux/Mac | `~/pyarchinit/` |
| Windows | `C:\Users\[utilisateur]\pyarchinit\` |

### Outils Utiles

- **SQLite Browser** : visualisation/modification de base de données SQLite
- **pgAdmin** : gestion PostgreSQL
- **7-Zip/tar** : compression des sauvegardes
- **rsync** : synchronisation incrémentale

---

## Vidéo Tutorial

### Sauvegarde et Sécurité des Données
**Durée** : 10-12 minutes
- Procédures de sauvegarde
- Restauration de base de données
- Automatisation

`[Placeholder vidéo : video_sauvegarde_restauration.mp4]`

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
