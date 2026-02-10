# Tutorial 19 : Travail Multi-utilisateur avec PostgreSQL

## Introduction

PyArchInit prend en charge le travail **multi-utilisateur** grâce à l'utilisation de **PostgreSQL/PostGIS** comme backend de base de données. Cette configuration permet à plusieurs opérateurs de travailler simultanément sur le même projet archéologique depuis des postes différents.

### Avantages du Multi-utilisateur

| Aspect | SQLite | PostgreSQL Multi-utilisateur |
|--------|--------|------------------------------|
| Utilisateurs simultanés | 1 | Illimités |
| Accès distant | Non | Oui |
| Gestion des permissions | Non | Oui |
| Sauvegarde centralisée | Manuelle | Automatisable |
| Performances | Bonnes | Excellentes |
| Évolutivité | Limitée | Élevée |

## Prérequis

### Serveur PostgreSQL

1. **PostgreSQL** 12 ou supérieur
2. **PostGIS** 3.0 ou supérieur
3. Serveur accessible sur le réseau (LAN ou Internet)

### Client

1. QGIS avec PyArchInit installé
2. Connexion réseau au serveur
3. Identifiants d'accès

## Configuration du Serveur

### Installation de PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib postgis
```

#### Windows
- Télécharger l'installateur depuis [postgresql.org](https://www.postgresql.org/download/windows/)
- Installer avec Stack Builder pour PostGIS

#### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Création de la Base de Données

```sql
-- Se connecter en tant que superutilisateur
sudo -u postgres psql

-- Créer la base de données
CREATE DATABASE pyarchinit_db;

-- Activer PostGIS
\c pyarchinit_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Créer l'utilisateur application
CREATE USER pyarchinit WITH PASSWORD 'mot_de_passe_securise';
GRANT ALL PRIVILEGES ON DATABASE pyarchinit_db TO pyarchinit;
```

### Configuration de l'Accès Réseau

Modifier `pg_hba.conf` :
```
# Permettre les connexions depuis le réseau local
host    pyarchinit_db    pyarchinit    192.168.1.0/24    md5

# Ou depuis n'importe quelle IP (moins sécurisé)
host    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

Modifier `postgresql.conf` :
```
listen_addresses = '*'
```

Redémarrer PostgreSQL :
```bash
sudo systemctl restart postgresql
```

## Configuration du Client PyArchInit

### Configuration Initiale

1. **PyArchInit** → **Configuration**
2. Onglet **Base de données**
3. Sélectionner **PostgreSQL**
4. Remplir les champs :

| Champ | Valeur |
|-------|--------|
| Serveur | Adresse IP ou hostname |
| Port | 5432 (par défaut) |
| Base de données | pyarchinit_db |
| Utilisateur | pyarchinit |
| Mot de passe | mot_de_passe_securise |

### Test de Connexion

1. Cliquer sur **Test Connexion**
2. Vérifier le message de succès
3. Sauvegarder la configuration

### Création du Schéma

Si nouvelle base de données :
1. Cliquer sur **Créer Schéma**
2. Attendre la création des tables
3. Vérifier la structure

## Gestion des Utilisateurs

### Création d'Utilisateurs Supplémentaires

```sql
-- Utilisateur avec accès complet
CREATE USER archeologue1 WITH PASSWORD 'motdepasse1';
GRANT ALL ON ALL TABLES IN SCHEMA public TO archeologue1;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO archeologue1;

-- Utilisateur en lecture seule
CREATE USER consultant1 WITH PASSWORD 'motdepasse2';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO consultant1;
```

### Niveaux d'Accès Suggérés

| Rôle | Permissions | Utilisation |
|------|-------------|-------------|
| Admin | ALL | Configuration, gestion |
| Archéologue | SELECT, INSERT, UPDATE, DELETE | Travail quotidien |
| Spécialiste | SELECT, INSERT, UPDATE (tables spécifiques) | Saisie de données spécialisées |
| Consultant | SELECT | Consultation des données |
| Backup | SELECT | Scripts de sauvegarde |

### Gestion des Rôles

```sql
-- Créer un rôle groupe
CREATE ROLE archeologues;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO archeologues;

-- Assigner des utilisateurs au groupe
GRANT archeologues TO archeologue1;
GRANT archeologues TO archeologue2;
```

## Workflow Multi-utilisateur

### Organisation du Travail

#### Par Zone
- Assigner différentes zones à différents opérateurs
- Éviter les chevauchements

#### Par Typologie
- Un opérateur : US dépôt
- Autre opérateur : US muraires
- Autre opérateur : Mobilier

#### Par Site
- Sites différents pour équipes différentes

### Gestion des Conflits

#### Verrouillage d'Enregistrement (conseillé)
1. Avant de modifier, vérifier que personne ne travaille sur le même enregistrement
2. Communiquer avec l'équipe

#### Résolution des Conflits
En cas de modifications concurrentes :
1. La dernière modification prévaut
2. Vérifier les données après chaque session
3. Utiliser le champ "date modification" pour tracer

### Synchronisation

Avec PostgreSQL, la synchronisation est automatique :
- Chaque modification est immédiatement visible par les autres
- Pas besoin de synchronisation manuelle
- Actualiser la fiche pour voir les mises à jour

## Sauvegarde et Sécurité

### Sauvegarde Automatique

Script de sauvegarde quotidienne :
```bash
#!/bin/bash
# backup_pyarchinit.sh
DATE=$(date +%Y%m%d)
BACKUP_DIR=/var/backups/pyarchinit
pg_dump -U pyarchinit -h localhost pyarchinit_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Conserver uniquement les 30 derniers jours
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
```

Planifier avec cron :
```bash
# crontab -e
0 2 * * * /path/to/backup_pyarchinit.sh
```

### Restauration

```bash
# Restaurer depuis une sauvegarde
gunzip backup_20260114.sql.gz
psql -U pyarchinit -h localhost pyarchinit_db < backup_20260114.sql
```

### Sécurité

1. **Mots de passe forts** : Minimum 12 caractères, mix majuscules/minuscules/chiffres
2. **Connexions SSL** : Activer SSL pour les connexions distantes
3. **Pare-feu** : Limiter l'accès au port 5432
4. **Mises à jour** : Maintenir PostgreSQL à jour
5. **Journal d'audit** : Activer la journalisation des connexions

### SSL pour Connexions Distantes

Dans `postgresql.conf` :
```
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

Dans `pg_hba.conf` :
```
hostssl    pyarchinit_db    pyarchinit    0.0.0.0/0    md5
```

## Surveillance

### Connexions Actives

```sql
SELECT
    usename,
    client_addr,
    state,
    query_start,
    query
FROM pg_stat_activity
WHERE datname = 'pyarchinit_db';
```

### Taille de la Base de Données

```sql
SELECT pg_size_pretty(pg_database_size('pyarchinit_db'));
```

### Verrous Actifs

```sql
SELECT
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted,
    a.usename,
    a.query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database = (SELECT oid FROM pg_database WHERE datname = 'pyarchinit_db');
```

## Migration depuis SQLite

### Export depuis SQLite

1. Ouvrir PyArchInit avec la base de données SQLite
2. **PyArchInit** → **Utilities** → **Export Database**
3. Exporter au format SQL

### Import dans PostgreSQL

1. Configurer la connexion PostgreSQL
2. Créer le schéma vide
3. Importer les données exportées

### Script de Migration

```python
# Exemple conceptuel
# Utiliser des outils spécifiques de migration
from sqlalchemy import create_engine

sqlite_engine = create_engine('sqlite:///pyarchinit.db')
pg_engine = create_engine('postgresql://user:pass@server/pyarchinit_db')

# Copier les tables
for table in tables:
    data = sqlite_engine.execute(f"SELECT * FROM {table}")
    pg_engine.execute(f"INSERT INTO {table} VALUES ...")
```

## Bonnes Pratiques

### 1. Planification

- Définir les rôles et responsabilités
- Établir des conventions de travail
- Documenter les procédures

### 2. Communication

- Canal de communication équipe (chat, email)
- Signaler le début/fin des sessions de travail
- Communiquer les zones en modification

### 3. Sauvegarde

- Sauvegardes quotidiennes automatiques
- Test périodique de restauration
- Sauvegarde hors site

### 4. Formation

- Formation sur le workflow multi-utilisateur
- Documentation des procédures
- Support technique disponible

## Résolution des Problèmes

### Connexion Refusée

**Causes** :
- Serveur non accessible
- Pare-feu bloquant
- Identifiants incorrects

**Solutions** :
- Vérifier la connectivité réseau
- Contrôler les règles du pare-feu
- Vérifier les identifiants

### Timeout de Connexion

**Causes** :
- Réseau lent
- Serveur surchargé
- Trop de connexions

**Solutions** :
- Optimiser le réseau
- Augmenter les ressources du serveur
- Limiter les connexions simultanées

### Verrouillage de Base de Données

**Cause** : Transactions non terminées

**Solution** :
```sql
-- Identifier les processus bloquants
SELECT * FROM pg_locks WHERE NOT granted;

-- Terminer le processus (avec précaution)
SELECT pg_terminate_backend(pid);
```

## Références

### Configuration
- `modules/db/pyarchinit_conn_strings.py` - Chaînes de connexion
- `gui/pyarchinit_Setting.py` - Interface de configuration

### Documentation Externe
- [Documentation PostgreSQL](https://www.postgresql.org/docs/)
- [Documentation PostGIS](https://postgis.net/documentation/)

---

## Vidéo Tutorial

### Configuration Multi-utilisateur
`[Placeholder : video_multiutilisateur_setup.mp4]`

**Contenus** :
- Installation de PostgreSQL
- Configuration du serveur
- Configuration du client
- Gestion des utilisateurs

**Durée prévue** : 20-25 minutes

### Workflow Collaboratif
`[Placeholder : video_multiutilisateur_workflow.mp4]`

**Contenus** :
- Organisation du travail
- Gestion des conflits
- Bonnes pratiques

**Durée prévue** : 12-15 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*

---

## Animation Interactive

Explorez l'animation interactive pour en savoir plus sur ce sujet.

[Ouvrir l'Animation Interactive](../../pyarchinit_concurrency_animation.html)
