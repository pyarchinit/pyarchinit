#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GitHub Issue Tracker
Script per scaricare, visualizzare e gestire le issue di GitHub
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
import requests
from pathlib import Path

# Per l'interfaccia grafica opzionale
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                                 QHBoxLayout, QWidget, QPushButton, 
                                 QTableWidget, QTableWidgetItem, QLabel,
                                 QLineEdit, QComboBox, QTextEdit, QMessageBox,
                                 QHeaderView, QCheckBox, QGroupBox)
    from PyQt5.QtCore import Qt, QThread, pyqtSignal
    from PyQt5.QtGui import QColor
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class GitHubIssueManager:
    """Gestisce le issue di GitHub"""
    
    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        self.owner = owner
        self.repo = repo
        self.token = token
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        
        # Directory per salvare i dati localmente
        self.data_dir = Path.home() / ".github_issue_tracker" / f"{owner}_{repo}"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.issues_file = self.data_dir / "issues.json"
        self.resolved_file = self.data_dir / "resolved_issues.json"
        
    def fetch_issues(self, state: str = "open", labels: Optional[List[str]] = None) -> List[Dict]:
        """Scarica le issue da GitHub"""
        issues = []
        page = 1
        
        while True:
            params = {
                "state": state,
                "per_page": 100,
                "page": page
            }
            
            if labels:
                params["labels"] = ",".join(labels)
            
            try:
                response = requests.get(
                    f"{self.base_url}/issues",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                
                page_issues = response.json()
                if not page_issues:
                    break
                    
                issues.extend(page_issues)
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Errore nel recupero delle issue: {e}")
                break
                
        return issues
    
    def save_issues_locally(self, issues: List[Dict]):
        """Salva le issue localmente"""
        # Carica le issue risolte esistenti
        resolved_ids = self.get_resolved_issue_ids()
        
        # Aggiungi lo stato di risoluzione locale
        for issue in issues:
            issue['locally_resolved'] = issue['number'] in resolved_ids
            issue['resolution_date'] = resolved_ids.get(issue['number'], {}).get('date')
            issue['resolution_notes'] = resolved_ids.get(issue['number'], {}).get('notes', '')
        
        with open(self.issues_file, 'w', encoding='utf-8') as f:
            json.dump(issues, f, indent=2, ensure_ascii=False)
    
    def load_local_issues(self) -> List[Dict]:
        """Carica le issue salvate localmente"""
        if self.issues_file.exists():
            with open(self.issues_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def get_resolved_issue_ids(self) -> Dict[int, Dict]:
        """Ottiene gli ID delle issue risolte localmente"""
        if self.resolved_file.exists():
            with open(self.resolved_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def mark_issue_resolved(self, issue_number: int, notes: str = ""):
        """Segna una issue come risolta localmente"""
        resolved = self.get_resolved_issue_ids()
        resolved[str(issue_number)] = {
            'date': datetime.now().isoformat(),
            'notes': notes
        }
        
        with open(self.resolved_file, 'w', encoding='utf-8') as f:
            json.dump(resolved, f, indent=2)
        
        # Aggiorna anche il file delle issue
        issues = self.load_local_issues()
        for issue in issues:
            if issue['number'] == issue_number:
                issue['locally_resolved'] = True
                issue['resolution_date'] = resolved[str(issue_number)]['date']
                issue['resolution_notes'] = notes
                break
        
        self.save_issues_locally(issues)
    
    def unmark_issue_resolved(self, issue_number: int):
        """Rimuove il flag di risoluzione da una issue"""
        resolved = self.get_resolved_issue_ids()
        if str(issue_number) in resolved:
            del resolved[str(issue_number)]
            
            with open(self.resolved_file, 'w', encoding='utf-8') as f:
                json.dump(resolved, f, indent=2)
        
        # Aggiorna anche il file delle issue
        issues = self.load_local_issues()
        for issue in issues:
            if issue['number'] == issue_number:
                issue['locally_resolved'] = False
                issue['resolution_date'] = None
                issue['resolution_notes'] = ''
                break
        
        self.save_issues_locally(issues)
    
    def sync_with_github(self) -> Dict[str, List[Dict]]:
        """Sincronizza con GitHub e restituisce le differenze"""
        print("Sincronizzazione con GitHub...")
        
        # Scarica issue aperte e chiuse
        open_issues = self.fetch_issues("open")
        closed_issues = self.fetch_issues("closed")
        
        all_remote_issues = open_issues + closed_issues
        local_issues = self.load_local_issues()
        
        # Trova le differenze
        local_numbers = {issue['number'] for issue in local_issues}
        remote_numbers = {issue['number'] for issue in all_remote_issues}
        
        new_issues = [i for i in all_remote_issues if i['number'] not in local_numbers]
        closed_on_github = []
        
        # Controlla quali issue locali sono state chiuse su GitHub
        for local in local_issues:
            remote = next((r for r in all_remote_issues if r['number'] == local['number']), None)
            if remote and remote['state'] == 'closed' and local.get('state') == 'open':
                closed_on_github.append(remote)
        
        # Salva tutte le issue aggiornate
        self.save_issues_locally(all_remote_issues)
        
        return {
            'new': new_issues,
            'closed_on_github': closed_on_github,
            'total_open': len(open_issues),
            'total_closed': len(closed_issues)
        }


class IssueTrackerGUI(QMainWindow):
    """Interfaccia grafica per il tracker delle issue"""
    
    def __init__(self, manager: GitHubIssueManager):
        super().__init__()
        self.manager = manager
        self.current_filter = "all"
        self.initUI()
        self.load_issues()
        
    def initUI(self):
        self.setWindowTitle(f"GitHub Issue Tracker - {self.manager.owner}/{self.manager.repo}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Widget centrale
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        self.sync_btn = QPushButton("🔄 Sincronizza con GitHub")
        self.sync_btn.clicked.connect(self.sync_issues)
        toolbar_layout.addWidget(self.sync_btn)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Tutte", "Aperte", "Risolte Localmente", "Chiuse su GitHub"])
        self.filter_combo.currentTextChanged.connect(self.filter_issues)
        toolbar_layout.addWidget(QLabel("Filtra:"))
        toolbar_layout.addWidget(self.filter_combo)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca nelle issue...")
        self.search_input.textChanged.connect(self.search_issues)
        toolbar_layout.addWidget(self.search_input)
        
        toolbar_layout.addStretch()
        
        self.stats_label = QLabel()
        toolbar_layout.addWidget(self.stats_label)
        
        layout.addLayout(toolbar_layout)
        
        # Tabella delle issue
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Risolta", "#", "Titolo", "Stato", "Labels", "Data Apertura", "Note Risoluzione"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.itemDoubleClicked.connect(self.open_issue_details)
        layout.addWidget(self.table)
        
        # Area dettagli
        details_group = QGroupBox("Dettagli Issue")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)
        
        # Controlli per la risoluzione
        resolution_layout = QHBoxLayout()
        
        self.resolution_notes = QLineEdit()
        self.resolution_notes.setPlaceholderText("Note sulla risoluzione...")
        resolution_layout.addWidget(self.resolution_notes)
        
        self.mark_resolved_btn = QPushButton("✓ Segna come Risolta")
        self.mark_resolved_btn.clicked.connect(self.toggle_resolution)
        resolution_layout.addWidget(self.mark_resolved_btn)
        
        details_layout.addLayout(resolution_layout)
        layout.addWidget(details_group)
        
        self.update_stats()
        
    def load_issues(self):
        """Carica le issue nella tabella"""
        issues = self.manager.load_local_issues()
        self.populate_table(issues)
        
    def populate_table(self, issues: List[Dict]):
        """Popola la tabella con le issue"""
        self.table.setRowCount(len(issues))
        
        for row, issue in enumerate(issues):
            # Checkbox per lo stato di risoluzione
            checkbox = QCheckBox()
            checkbox.setChecked(issue.get('locally_resolved', False))
            checkbox.stateChanged.connect(lambda state, num=issue['number']: 
                                        self.quick_toggle_resolution(num, state))
            self.table.setCellWidget(row, 0, checkbox)
            
            # Numero issue
            self.table.setItem(row, 1, QTableWidgetItem(str(issue['number'])))
            
            # Titolo
            title_item = QTableWidgetItem(issue['title'])
            self.table.setItem(row, 2, title_item)
            
            # Stato
            state_item = QTableWidgetItem(issue['state'])
            if issue['state'] == 'closed':
                state_item.setBackground(QColor(255, 200, 200))
            elif issue.get('locally_resolved'):
                state_item.setBackground(QColor(200, 255, 200))
            self.table.setItem(row, 3, state_item)
            
            # Labels
            labels = ", ".join([label['name'] for label in issue.get('labels', [])])
            self.table.setItem(row, 4, QTableWidgetItem(labels))
            
            # Data apertura
            created_date = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
            self.table.setItem(row, 5, QTableWidgetItem(created_date.strftime('%Y-%m-%d')))
            
            # Note risoluzione
            notes = issue.get('resolution_notes', '')
            self.table.setItem(row, 6, QTableWidgetItem(notes))
            
        self.table.resizeColumnsToContents()
        
    def filter_issues(self, filter_text: str):
        """Filtra le issue visualizzate"""
        all_issues = self.manager.load_local_issues()
        
        if filter_text == "Aperte":
            filtered = [i for i in all_issues if i['state'] == 'open' and not i.get('locally_resolved')]
        elif filter_text == "Risolte Localmente":
            filtered = [i for i in all_issues if i.get('locally_resolved')]
        elif filter_text == "Chiuse su GitHub":
            filtered = [i for i in all_issues if i['state'] == 'closed']
        else:
            filtered = all_issues
            
        self.populate_table(filtered)
        
    def search_issues(self, search_text: str):
        """Cerca nelle issue"""
        all_issues = self.manager.load_local_issues()
        
        if not search_text:
            self.populate_table(all_issues)
            return
            
        search_lower = search_text.lower()
        filtered = [
            i for i in all_issues 
            if search_lower in i['title'].lower() or 
               search_lower in i.get('body', '').lower() or
               str(i['number']) == search_text
        ]
        
        self.populate_table(filtered)
        
    def open_issue_details(self, item):
        """Mostra i dettagli della issue selezionata"""
        row = item.row()
        issue_number = int(self.table.item(row, 1).text())
        
        issues = self.manager.load_local_issues()
        issue = next((i for i in issues if i['number'] == issue_number), None)
        
        if issue:
            details = f"Issue #{issue['number']}: {issue['title']}\n\n"
            details += f"Stato: {issue['state']}\n"
            details += f"Autore: {issue['user']['login']}\n"
            details += f"Data apertura: {issue['created_at']}\n\n"
            details += f"Descrizione:\n{issue.get('body', 'Nessuna descrizione')}\n\n"
            
            if issue.get('locally_resolved'):
                details += f"\n--- RISOLTA LOCALMENTE ---\n"
                details += f"Data: {issue.get('resolution_date', 'N/A')}\n"
                details += f"Note: {issue.get('resolution_notes', 'Nessuna nota')}"
                
            self.details_text.setText(details)
            
            # Aggiorna il bottone di risoluzione
            if issue.get('locally_resolved'):
                self.mark_resolved_btn.setText("✗ Rimuovi Risoluzione")
            else:
                self.mark_resolved_btn.setText("✓ Segna come Risolta")
                
    def toggle_resolution(self):
        """Toglie/mette il flag di risoluzione sulla issue selezionata"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Attenzione", "Seleziona una issue prima!")
            return
            
        issue_number = int(self.table.item(current_row, 1).text())
        issues = self.manager.load_local_issues()
        issue = next((i for i in issues if i['number'] == issue_number), None)
        
        if issue:
            if issue.get('locally_resolved'):
                self.manager.unmark_issue_resolved(issue_number)
                QMessageBox.information(self, "Successo", f"Issue #{issue_number} marcata come non risolta")
            else:
                notes = self.resolution_notes.text()
                self.manager.mark_issue_resolved(issue_number, notes)
                QMessageBox.information(self, "Successo", f"Issue #{issue_number} marcata come risolta")
                
            self.load_issues()
            self.update_stats()
            
    def quick_toggle_resolution(self, issue_number: int, state: int):
        """Toggle veloce dalla checkbox"""
        if state == Qt.Checked:
            self.manager.mark_issue_resolved(issue_number, "Risolta via checkbox")
        else:
            self.manager.unmark_issue_resolved(issue_number)
        self.update_stats()
        
    def sync_issues(self):
        """Sincronizza con GitHub"""
        self.sync_btn.setEnabled(False)
        self.sync_btn.setText("Sincronizzazione in corso...")
        
        try:
            result = self.manager.sync_with_github()
            
            message = f"Sincronizzazione completata!\n\n"
            message += f"Issue totali aperte: {result['total_open']}\n"
            message += f"Issue totali chiuse: {result['total_closed']}\n"
            message += f"Nuove issue: {len(result['new'])}\n"
            message += f"Issue chiuse su GitHub: {len(result['closed_on_github'])}"
            
            QMessageBox.information(self, "Sincronizzazione", message)
            
            self.load_issues()
            self.update_stats()
            
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Errore durante la sincronizzazione:\n{str(e)}")
            
        finally:
            self.sync_btn.setEnabled(True)
            self.sync_btn.setText("🔄 Sincronizza con GitHub")
            
    def update_stats(self):
        """Aggiorna le statistiche"""
        issues = self.manager.load_local_issues()
        total = len(issues)
        open_count = len([i for i in issues if i['state'] == 'open'])
        resolved = len([i for i in issues if i.get('locally_resolved')])
        
        self.stats_label.setText(
            f"Totale: {total} | Aperte: {open_count} | Risolte localmente: {resolved}"
        )


def main_cli():
    """Versione CLI del tracker"""
    print("GitHub Issue Tracker - CLI")
    print("-" * 50)
    
    # Configurazione
    owner = input("Owner/Organizzazione GitHub: ").strip()
    repo = input("Nome repository: ").strip()
    token = input("Token GitHub (opzionale, premi Enter per saltare): ").strip()
    
    manager = GitHubIssueManager(owner, repo, token if token else None)
    
    while True:
        print("\n" + "=" * 50)
        print("1. Sincronizza con GitHub")
        print("2. Mostra issue aperte")
        print("3. Mostra issue risolte localmente")
        print("4. Segna issue come risolta")
        print("5. Rimuovi flag risoluzione")
        print("6. Cerca issue")
        print("0. Esci")
        
        choice = input("\nScelta: ").strip()
        
        if choice == "0":
            break
            
        elif choice == "1":
            print("\nSincronizzazione in corso...")
            result = manager.sync_with_github()
            print(f"\nIssue aperte: {result['total_open']}")
            print(f"Issue chiuse: {result['total_closed']}")
            print(f"Nuove issue trovate: {len(result['new'])}")
            
        elif choice == "2":
            issues = manager.load_local_issues()
            open_issues = [i for i in issues if i['state'] == 'open' and not i.get('locally_resolved')]
            
            print(f"\nIssue aperte ({len(open_issues)}):")
            for issue in open_issues:
                print(f"#{issue['number']}: {issue['title']}")
                
        elif choice == "3":
            issues = manager.load_local_issues()
            resolved = [i for i in issues if i.get('locally_resolved')]
            
            print(f"\nIssue risolte localmente ({len(resolved)}):")
            for issue in resolved:
                print(f"#{issue['number']}: {issue['title']} - {issue.get('resolution_notes', 'Nessuna nota')}")
                
        elif choice == "4":
            issue_num = int(input("Numero issue da segnare come risolta: "))
            notes = input("Note (opzionale): ").strip()
            manager.mark_issue_resolved(issue_num, notes)
            print(f"Issue #{issue_num} segnata come risolta!")
            
        elif choice == "5":
            issue_num = int(input("Numero issue da riaprire: "))
            manager.unmark_issue_resolved(issue_num)
            print(f"Issue #{issue_num} riaperta!")
            
        elif choice == "6":
            search = input("Cerca (titolo/numero): ").strip().lower()
            issues = manager.load_local_issues()
            
            found = [
                i for i in issues 
                if search in i['title'].lower() or 
                   search in i.get('body', '').lower() or
                   str(i['number']) == search
            ]
            
            print(f"\nTrovate {len(found)} issue:")
            for issue in found:
                status = "RISOLTA" if issue.get('locally_resolved') else issue['state']
                print(f"#{issue['number']} [{status}]: {issue['title']}")


def main():
    """Entry point principale"""
    if len(sys.argv) > 1:
        # Modalità CLI con parametri
        if len(sys.argv) < 3:
            print("Uso: python github_issue_tracker.py <owner> <repo> [token]")
            sys.exit(1)
            
        owner = sys.argv[1]
        repo = sys.argv[2]
        token = sys.argv[3] if len(sys.argv) > 3 else None
        
        manager = GitHubIssueManager(owner, repo, token)
        
        if GUI_AVAILABLE:
            app = QApplication(sys.argv)
            window = IssueTrackerGUI(manager)
            window.show()
            sys.exit(app.exec_())
        else:
            print("GUI non disponibile. Usando CLI...")
            main_cli()
    else:
        # Modalità interattiva
        main_cli()


if __name__ == "__main__":
    main()