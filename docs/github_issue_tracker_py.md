# github_issue_tracker.py

## Overview

This file contains 96 documented elements.

## Classes

### GitHubIssueManager

Gestisce le issue di GitHub

#### Methods

##### __init__(self, owner, repo, token)

##### fetch_issues(self, state, labels)

Scarica le issue da GitHub

##### save_issues_locally(self, issues)

Salva le issue localmente

##### load_local_issues(self)

Carica le issue salvate localmente

##### get_resolved_issue_ids(self)

Ottiene gli ID delle issue risolte localmente

##### mark_issue_resolved(self, issue_number, notes)

Segna una issue come risolta localmente

##### unmark_issue_resolved(self, issue_number)

Rimuove il flag di risoluzione da una issue

##### sync_with_github(self)

Sincronizza con GitHub e restituisce le differenze

### IssueTrackerGUI

Interfaccia grafica per il tracker delle issue

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, manager)

##### initUI(self)

##### load_issues(self)

Carica le issue nella tabella

##### populate_table(self, issues)

Popola la tabella con le issue

##### filter_issues(self, filter_text)

Filtra le issue visualizzate

##### search_issues(self, search_text)

Cerca nelle issue

##### open_issue_details(self, item)

Mostra i dettagli della issue selezionata

##### toggle_resolution(self)

Toglie/mette il flag di risoluzione sulla issue selezionata

##### quick_toggle_resolution(self, issue_number, state)

Toggle veloce dalla checkbox

##### sync_issues(self)

Sincronizza con GitHub

##### update_stats(self)

Aggiorna le statistiche

### GitHubIssueManager

Gestisce le issue di GitHub

#### Methods

##### __init__(self, owner, repo, token)

##### fetch_issues(self, state, labels)

Scarica le issue da GitHub

##### save_issues_locally(self, issues)

Salva le issue localmente

##### load_local_issues(self)

Carica le issue salvate localmente

##### get_resolved_issue_ids(self)

Ottiene gli ID delle issue risolte localmente

##### mark_issue_resolved(self, issue_number, notes)

Segna una issue come risolta localmente

##### unmark_issue_resolved(self, issue_number)

Rimuove il flag di risoluzione da una issue

##### sync_with_github(self)

Sincronizza con GitHub e restituisce le differenze

### IssueTrackerGUI

Interfaccia grafica per il tracker delle issue

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, manager)

##### initUI(self)

##### load_issues(self)

Carica le issue nella tabella

##### populate_table(self, issues)

Popola la tabella con le issue

##### filter_issues(self, filter_text)

Filtra le issue visualizzate

##### search_issues(self, search_text)

Cerca nelle issue

##### open_issue_details(self, item)

Mostra i dettagli della issue selezionata

##### toggle_resolution(self)

Toglie/mette il flag di risoluzione sulla issue selezionata

##### quick_toggle_resolution(self, issue_number, state)

Toggle veloce dalla checkbox

##### sync_issues(self)

Sincronizza con GitHub

##### update_stats(self)

Aggiorna le statistiche

### GitHubIssueManager

Gestisce le issue di GitHub

#### Methods

##### __init__(self, owner, repo, token)

##### fetch_issues(self, state, labels)

Scarica le issue da GitHub

##### save_issues_locally(self, issues)

Salva le issue localmente

##### load_local_issues(self)

Carica le issue salvate localmente

##### get_resolved_issue_ids(self)

Ottiene gli ID delle issue risolte localmente

##### mark_issue_resolved(self, issue_number, notes)

Segna una issue come risolta localmente

##### unmark_issue_resolved(self, issue_number)

Rimuove il flag di risoluzione da una issue

##### sync_with_github(self)

Sincronizza con GitHub e restituisce le differenze

### IssueTrackerGUI

Interfaccia grafica per il tracker delle issue

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, manager)

##### initUI(self)

##### load_issues(self)

Carica le issue nella tabella

##### populate_table(self, issues)

Popola la tabella con le issue

##### filter_issues(self, filter_text)

Filtra le issue visualizzate

##### search_issues(self, search_text)

Cerca nelle issue

##### open_issue_details(self, item)

Mostra i dettagli della issue selezionata

##### toggle_resolution(self)

Toglie/mette il flag di risoluzione sulla issue selezionata

##### quick_toggle_resolution(self, issue_number, state)

Toggle veloce dalla checkbox

##### sync_issues(self)

Sincronizza con GitHub

##### update_stats(self)

Aggiorna le statistiche

### GitHubIssueManager

Gestisce le issue di GitHub

#### Methods

##### __init__(self, owner, repo, token)

##### fetch_issues(self, state, labels)

Scarica le issue da GitHub

##### save_issues_locally(self, issues)

Salva le issue localmente

##### load_local_issues(self)

Carica le issue salvate localmente

##### get_resolved_issue_ids(self)

Ottiene gli ID delle issue risolte localmente

##### mark_issue_resolved(self, issue_number, notes)

Segna una issue come risolta localmente

##### unmark_issue_resolved(self, issue_number)

Rimuove il flag di risoluzione da una issue

##### sync_with_github(self)

Sincronizza con GitHub e restituisce le differenze

### IssueTrackerGUI

Interfaccia grafica per il tracker delle issue

**Inherits from**: QMainWindow

#### Methods

##### __init__(self, manager)

##### initUI(self)

##### load_issues(self)

Carica le issue nella tabella

##### populate_table(self, issues)

Popola la tabella con le issue

##### filter_issues(self, filter_text)

Filtra le issue visualizzate

##### search_issues(self, search_text)

Cerca nelle issue

##### open_issue_details(self, item)

Mostra i dettagli della issue selezionata

##### toggle_resolution(self)

Toglie/mette il flag di risoluzione sulla issue selezionata

##### quick_toggle_resolution(self, issue_number, state)

Toggle veloce dalla checkbox

##### sync_issues(self)

Sincronizza con GitHub

##### update_stats(self)

Aggiorna le statistiche

## Functions

### main_cli()

Versione CLI del tracker

### main()

Entry point principale

### main_cli()

Versione CLI del tracker

### main()

Entry point principale

### main_cli()

Versione CLI del tracker

### main()

Entry point principale

### main_cli()

Versione CLI del tracker

### main()

Entry point principale

