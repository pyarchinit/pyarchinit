#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Report Text Cleaner
Agente di post-processing per pulire e riformattare il testo dei report archeologici
"""

import re


class ReportTextCleaner:
    """
    Pulisce e riformatta il testo generato dall'AI per una migliore formattazione Word
    """

    @staticmethod
    def clean_report_text(text):
        """
        Pulisce il testo del report rimuovendo formattazioni problematiche

        Args:
            text: Testo del report generato dall'AI

        Returns:
            Testo pulito e riformattato
        """
        if not text:
            return text

        lines = text.split('\n')
        cleaned_lines = []
        in_list = False
        list_buffer = []

        for i, line in enumerate(lines):
            line = line.strip()

            if not line:
                # Linea vuota - termina eventuale lista
                if in_list and list_buffer:
                    cleaned_lines.extend(list_buffer)
                    list_buffer = []
                    in_list = False
                cleaned_lines.append('')
                continue

            # Rimuovi trattini inappropriati all'inizio di paragrafi lunghi
            if line.startswith('- '):
                # Controlla se è una vera lista o un paragrafo
                if ReportTextCleaner._is_list_item(line, i, lines):
                    # È un elemento di lista - mantieni ma marca per processare insieme
                    if not in_list:
                        in_list = True
                    list_buffer.append(line)
                else:
                    # È un paragrafo - rimuovi il trattino
                    if in_list and list_buffer:
                        # Prima finisci la lista precedente
                        cleaned_lines.extend(list_buffer)
                        list_buffer = []
                        in_list = False

                    # Rimuovi il trattino e capitalizza
                    clean_line = line[2:].strip()
                    if clean_line and not clean_line[0].isupper():
                        clean_line = clean_line[0].upper() + clean_line[1:]
                    cleaned_lines.append(clean_line)
            else:
                # Linea normale
                if in_list and list_buffer:
                    cleaned_lines.extend(list_buffer)
                    list_buffer = []
                    in_list = False
                cleaned_lines.append(line)

        # Processa eventuali liste rimanenti
        if in_list and list_buffer:
            cleaned_lines.extend(list_buffer)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def _is_list_item(line, index, all_lines):
        """
        Determina se una linea è un vero elemento di lista o un paragrafo

        Args:
            line: La linea corrente
            index: Indice della linea
            all_lines: Tutte le linee del testo

        Returns:
            True se è un elemento di lista, False se è un paragrafo
        """
        # Se la linea è molto lunga (>80 caratteri), probabilmente è un paragrafo
        if len(line) > 80:
            return False

        # Controlla il contesto - se siamo in una sezione "ELENCO"
        # Cerca indietro per vedere se c'è un heading ELENCO
        for i in range(max(0, index - 5), index):
            if i < len(all_lines):
                prev_line = all_lines[i].strip().upper()
                if 'ELENCO' in prev_line or 'LISTA' in prev_line:
                    # Siamo in una vera lista
                    return True

        # Controlla le linee successive per vedere se continuano la lista
        consecutive_list_items = 0
        for i in range(index, min(index + 3, len(all_lines))):
            if all_lines[i].strip().startswith('- ') or all_lines[i].strip().startswith('• '):
                consecutive_list_items += 1

        # Se ci sono almeno 2 elementi consecutivi, è una lista
        if consecutive_list_items >= 2:
            return True

        # Controlla se contiene parole chiave che indicano un paragrafo completo
        paragraph_keywords = [
            'costituisce', 'presenta', 'mostra', 'evidenzia', 'suggerisce',
            'documenta', 'caratterizza', 'comprende', 'include', 'riferibile',
            'il ', 'la ', 'lo ', 'gli ', 'le ', 'un ', 'una ', 'nell\'',
            'è ', 'sono ', 'era ', 'erano ', 'con ', 'per ', 'tra ',
            'materiale', 'materiali', 'ceramiche', 'vaso', 'vasi',
            'decorazioni', 'forme', 'frequenza', 'continuità', 'presenza'
        ]

        line_lower = line.lower()
        for keyword in paragraph_keywords:
            if keyword in line_lower:
                return False

        # Se è molto breve (<30 caratteri) e semplice, probabilmente è un elemento di lista
        if len(line) < 30 and not any(c in line for c in [',', '.']):
            return True

        return False

    @staticmethod
    def clean_section_content(section_name, content):
        """
        Pulisce il contenuto di una sezione specifica

        Args:
            section_name: Nome della sezione
            content: Contenuto della sezione

        Returns:
            Contenuto pulito
        """
        if not content:
            return content

        # Prima pulizia generale
        content = ReportTextCleaner.clean_report_text(content)

        # Pulizia specifica per sezione
        if section_name == "ANALISI STRATIGRAFICA E INTERPRETAZIONE":
            content = ReportTextCleaner._clean_stratigraphic_section(content)
        elif section_name == "CATALOGO DEI MATERIALI":
            content = ReportTextCleaner._clean_materials_section(content)

        return content

    @staticmethod
    def _clean_stratigraphic_section(content):
        """
        Pulizia specifica per la sezione stratigrafica
        """
        lines = content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()

            # Rimuovi numerazione ridondante tipo "US 123:" all'inizio se già nel testo
            if re.match(r'^US\s+\d+:', line):
                # Mantieni solo se è un titolo di sottosezione
                if len(line) < 20:
                    cleaned_lines.append(line)
                else:
                    # Rimuovi il prefisso US se il contenuto lo ripete
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        cleaned_lines.append(parts[1].strip())
                    else:
                        cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def _clean_materials_section(content):
        """
        Pulizia specifica per la sezione materiali
        """
        # Rimuovi ripetizioni di "Totale:" o simili
        content = re.sub(r'Totale:\s*Totale:', 'Totale:', content)

        # Sistema le tabelle markdown
        lines = content.split('\n')
        cleaned_lines = []
        in_table = False

        for line in lines:
            line = line.strip()

            # Rileva tabelle markdown
            if '|' in line:
                if not in_table:
                    in_table = True
                # Assicura spazi corretti intorno ai pipe
                line = re.sub(r'\s*\|\s*', ' | ', line)
                cleaned_lines.append(line)
            else:
                if in_table:
                    in_table = False
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    @staticmethod
    def prepare_for_docx(text):
        """
        Prepara il testo per l'inserimento in un documento Word

        Args:
            text: Testo da preparare

        Returns:
            Dictionary con il testo suddiviso in paragrafi e metadata
        """
        if not text:
            return {'paragraphs': [], 'has_lists': False, 'has_tables': False}

        # Prima pulisci il testo
        text = ReportTextCleaner.clean_report_text(text)

        paragraphs = []
        lines = text.split('\n')

        current_paragraph = {
            'text': '',
            'style': 'normal',  # normal, heading1, heading2, list, table
            'level': 0
        }

        for line in lines:
            line = line.strip()

            if not line:
                # Fine del paragrafo corrente
                if current_paragraph['text']:
                    paragraphs.append(current_paragraph)
                    current_paragraph = {'text': '', 'style': 'normal', 'level': 0}
                continue

            # Identifica il tipo di contenuto
            if line.startswith('#'):
                # Heading markdown
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                paragraphs.append({
                    'text': text,
                    'style': f'heading{min(level, 3)}',
                    'level': level
                })
            elif line.startswith('- ') or line.startswith('• '):
                # Lista
                paragraphs.append({
                    'text': line[2:].strip(),
                    'style': 'list',
                    'level': 1
                })
            elif '|' in line and line.count('|') >= 2:
                # Tabella
                paragraphs.append({
                    'text': line,
                    'style': 'table',
                    'level': 0
                })
            else:
                # Paragrafo normale
                if current_paragraph['text']:
                    current_paragraph['text'] += ' ' + line
                else:
                    current_paragraph['text'] = line

        # Aggiungi l'ultimo paragrafo se presente
        if current_paragraph['text']:
            paragraphs.append(current_paragraph)

        # Determina se ci sono liste o tabelle
        has_lists = any(p['style'] == 'list' for p in paragraphs)
        has_tables = any(p['style'] == 'table' for p in paragraphs)

        return {
            'paragraphs': paragraphs,
            'has_lists': has_lists,
            'has_tables': has_tables
        }