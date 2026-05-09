# scripts/github_issue_tracker.py

## Overview

This file contains 24 documented elements.

## Classes

### GitHubIssueManager

Gestisce le issue di GitHub

#### Methods

##### __init__(self, owner, repo, token)

Initializes a `GitHubIssueManager` instance for a specific GitHub repository identified by `owner` and `repo`. Sets up the base API URL (`https://api.github.com/repos/{owner}/{repo}`), configures request headers with the GitHub API v3 accept type, and conditionally adds a token-based `Authorization` header if `token` is provided. Creates a local data directory at `~/.github_issue_tracker/{owner}_{repo}` (including any missing parent directories) and defines the paths for the local `issues.json` and `resolved_issues.json` storage files.

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

Initializes an instance of `IssueTrackerGUI` by calling the parent `QMainWindow` constructor and storing the provided `GitHubIssueManager` instance in `self.manager`. Sets the default issue filter to `"all"`, then invokes `initUI()` to configure the window layout and properties, followed by `load_issues()` to populate the interface with issue data.

##### initUI(self)

Initializes and constructs the main window's user interface by setting the window title (derived from the repository owner and name), configuring the window geometry to 1200×800 pixels, and assembling all UI components into a central `QWidget` with a `QVBoxLayout`. Builds a toolbar containing a synchronization button, a filter combo box with options for all/open/locally resolved/GitHub-closed issues, a search input field, and a statistics label. Also creates a seven-column `QTableWidget` for displaying issues, a read-only details panel, a resolution notes input, a toggle resolution button, and finalizes setup by calling `update_stats()`.

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

