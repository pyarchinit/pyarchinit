# Tutorial 30 : Requête IA Base de Données (Text2SQL)

## Introduction

**Requête IA Base de Données** est une fonctionnalité avancée de PyArchInit qui permet d'interroger la base de données archéologique en utilisant le **langage naturel**. Le système convertit automatiquement les questions en requêtes SQL grâce à l'intelligence artificielle.

### Comment ça Fonctionne

1. L'utilisateur écrit une question en français/anglais
2. L'IA analyse la demande
3. Génère la requête SQL correspondante
4. Exécute la requête sur la base de données
5. Renvoie les résultats

### Exemples de Questions

- *"Trouver tous les objets céramiques du site Villa Romaine"*
- *"Montrer les US de la période romaine dans la zone 1000"*
- *"Combien d'individus ont été trouvés dans les tombes ?"*
- *"Lister les structures avec une datation médiévale"*

## Accès

### Depuis la Fiche US/Objets
Onglet dédié **"AI Query"** ou **"Text2SQL"**

### Depuis le Menu
**PyArchInit** → **AI Query Database**

## Interface

### Panneau Requête

```
+--------------------------------------------------+
|         Génération SQL avec IA                    |
+--------------------------------------------------+
| Mode de Génération :                              |
|   (o) OpenAI GPT-4 (API déjà configurée)         |
|   ( ) Ollama (modèle local)                      |
|   ( ) API gratuite (si disponible)               |
+--------------------------------------------------+
| Modèle Ollama : [llama3.2 v] [Vérifier Ollama]   |
+--------------------------------------------------+
| Entrée :                                          |
|   Type de Base de Données : [sqlite | postgresql]|
|                                                  |
|   Décrivez la requête :                          |
|   +--------------------------------------------+ |
|   | Trouver tous les objets céramiques du site | |
|   | Villa Romaine avec datation entre Ier      | |
|   | et IIe siècle                              | |
|   +--------------------------------------------+ |
+--------------------------------------------------+
| [Générer SQL]  [Effacer]                         |
+--------------------------------------------------+
| Requête SQL Générée :                             |
|   +--------------------------------------------+ |
|   | SELECT * FROM inventario_materiali_table   | |
|   | WHERE sito = 'Villa Romaine'              | |
|   | AND tipo_reperto LIKE '%ceramic%'         | |
|   +--------------------------------------------+ |
| [Expliquer Requête] [Copier Requête] [Utiliser]  |
+--------------------------------------------------+
| Explication :                                     |
|   La requête sélectionne tous les champs de...   |
+--------------------------------------------------+
```

## Modes de Génération

### 1. OpenAI GPT-4

- **Prérequis** : Clé API OpenAI configurée
- **Qualité** : Excellente
- **Coût** : À la consommation (API)
- **Vitesse** : Rapide

### 2. Ollama (Local)

- **Prérequis** : Ollama installé et en cours d'exécution
- **Qualité** : Bonne-Excellente (selon le modèle)
- **Coût** : Gratuit
- **Vitesse** : Dépend du matériel

### 3. API Gratuite

- **Prérequis** : Connexion internet
- **Qualité** : Variable
- **Coût** : Gratuit
- **Limitations** : Limitation de débit possible

## Configuration

### OpenAI

1. Obtenir une clé API sur [OpenAI](https://platform.openai.com/)
2. Configurer dans **PyArchInit** → **Configuration** → **Clés API**
3. Sélectionner "OpenAI GPT-4" dans le mode

### Ollama

1. Installer Ollama depuis [ollama.ai](https://ollama.ai/)
2. Démarrer Ollama : `ollama serve`
3. Télécharger le modèle : `ollama pull llama3.2`
4. Sélectionner "Ollama" et vérifier la connexion

### Modèles Ollama Recommandés

| Modèle | Taille | Qualité SQL |
|--------|--------|-------------|
| llama3.2 | 2Go | Bonne |
| mistral | 4Go | Excellente |
| codellama | 7Go | Excellente pour SQL |
| qwen2.5-coder | 4Go | Excellente pour le code |

## Utilisation

### 1. Écrire la Question

Dans la zone de saisie, décrire ce que vous voulez chercher :
- Utiliser le langage naturel
- Être spécifique quand c'est possible
- Mentionner les tables/champs si connus

### 2. Générer le SQL

1. Cliquer sur **"Générer SQL"**
2. Attendre le traitement
3. Visualiser la requête générée

### 3. Vérifier la Requête

- Lire la requête SQL générée
- Cliquer sur **"Expliquer Requête"** pour comprendre
- Vérifier la logique

### 4. Exécuter la Requête

- **"Copier Requête"** : Copie dans le presse-papiers
- **"Utiliser Requête"** : Exécute directement dans le système

## Schéma de la Base de Données

### Tables Principales

Le système connaît le schéma PyArchInit :

| Table | Description |
|-------|-------------|
| site_table | Sites archéologiques |
| us_table | Unités Stratigraphiques |
| inventario_materiali_table | Objets |
| pottery_table | Céramique |
| tomba_table | Tombes |
| individui_table | Individus |
| struttura_table | Structures |
| periodizzazione_table | Périodisation |
| campioni_table | Échantillons |
| documentazione_table | Documentation |

### Champs Courants

L'IA connaît les champs principaux :
- `sito` - Nom du site
- `area` - Numéro de zone
- `us` - Numéro d'US
- `periodo_iniziale` / `fase_iniziale`
- `datazione_estesa`
- `descrizione` / `interpretazione`

## Exemples de Requêtes

### Recherche d'Objets

**Question** : *"Trouver tous les objets en bronze du site Rome Antique"*

```sql
SELECT * FROM inventario_materiali_table
WHERE sito = 'Rome Antique'
AND (tipo_reperto LIKE '%bronze%' OR definizione LIKE '%bronze%')
```

### Comptage d'US

**Question** : *"Combien d'US y a-t-il par période sur le site Villa Adriana ?"*

```sql
SELECT periodo_iniziale, COUNT(*) as num_us
FROM us_table
WHERE sito = 'Villa Adriana'
GROUP BY periodo_iniziale
```

### Recherche Spatiale

**Question** : *"Montrer les US de la zone 1000 avec des cotes inférieures à 10 mètres"*

```sql
SELECT * FROM us_table
WHERE area = '1000'
AND quota_min_usm < 10
```

## Bonnes Pratiques

### 1. Questions Efficaces

- Être spécifique : noms de sites, numéros, dates
- Indiquer ce que vous voulez : liste, comptage, détails
- Mentionner les filtres souhaités

### 2. Vérification des Résultats

- Toujours contrôler la requête générée
- Utiliser "Expliquer Requête" si ce n'est pas clair
- Tester sur un sous-ensemble avant les requêtes complexes

### 3. Itération

- Si le résultat n'est pas correct, reformuler la question
- Ajouter des détails si la requête est trop large
- Simplifier si la requête est trop complexe

## Résolution des Problèmes

### Requête Non Générée

**Causes** :
- API non configurée
- Connexion manquante
- Question non compréhensible

**Solutions** :
- Vérifier la configuration de l'API
- Contrôler la connexion
- Reformuler la question

### Résultats Erronés

**Causes** :
- Question ambiguë
- Champ/table inexistant

**Solutions** :
- Être plus spécifique
- Vérifier les noms des tables/champs

### Ollama Ne Répond Pas

**Causes** :
- Ollama n'est pas en cours d'exécution
- Modèle non téléchargé

**Solutions** :
- Démarrer `ollama serve`
- Télécharger le modèle requis

## Références

### Fichiers Source
- `modules/utility/textTosql.py` - Classe MakeSQL
- `modules/utility/database_schema.py` - Schéma de la base de données

### APIs Externes
- [API OpenAI](https://platform.openai.com/)
- [Ollama](https://ollama.ai/)

---

## Vidéo Tutorial

### Requête IA Base de Données
`[Placeholder : video_ai_query.mp4]`

**Contenus** :
- Configuration de l'API
- Écriture de questions efficaces
- Interprétation des résultats
- Bonnes pratiques

**Durée prévue** : 15-18 minutes

---

*Dernière mise à jour : Janvier 2026*
*PyArchInit - Système de Gestion des Données Archéologiques*
