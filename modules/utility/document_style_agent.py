#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Document Style Agent
Agente intelligente per correggere automaticamente gli stili nei documenti archeologici
"""

import re
from typing import List, Dict, Tuple, Optional


class DocumentStyleAgent:
    """
    Agente che analizza e corregge automaticamente gli stili dei documenti
    """

    def __init__(self):
        # Pattern per identificare i tipi di contenuto
        self.patterns = {
            'main_title': [
                r'^REPORT DI SCAVO ARCHEOLOGICO$',
                r'^RELAZIONE.*ARCHEOLOGICA?$'
            ],
            'section_title': [
                r'^INDICE$',
                r'^INTRODUZIONE$',
                r'^METODOLOGIA',
                r'^ANALISI STRATIGRAFICA',
                r'^CATALOGO DEI MATERIALI',
                r'^GESTIONE CASSETTE',
                r'^CONCLUSIONI',
                r'^APPENDICE',
                r'^BIBLIOGRAFIA$'
            ],
            'subsection_numeric': r'^\d+\.\s+.+',  # 1. Titolo, 2. Altro titolo
            'us_reference': r'^US\s+\d+:?\s*',  # US 815: descrizione
            'list_marker': r'^[-•]\s+',
            'elenco_header': r'ELENCO|LISTA',
            'sintesi_start': r'^(Sintesi|Lettura|Totale|Contesto):\s*',
        }

        # Regole per determinare lo stile corretto
        self.style_rules = []
        self._initialize_rules()

    def _initialize_rules(self):
        """Inizializza le regole per determinare gli stili"""

        # Regola 1: Titolo principale del documento
        self.style_rules.append({
            'name': 'main_title',
            'check': lambda text, ctx: any(re.match(p, text) for p in self.patterns['main_title']),
            'style': 'title',
            'priority': 100
        })

        # Regola 2: Titoli di sezione principali
        self.style_rules.append({
            'name': 'section_title',
            'check': lambda text, ctx: (
                any(re.match(p, text) for p in self.patterns['section_title']) and
                len(text) < 50
            ),
            'style': 'heading1',
            'priority': 90
        })

        # Regola 3: Sottosezioni numerate (1., 2., etc.)
        self.style_rules.append({
            'name': 'numeric_subsection',
            'check': lambda text, ctx: (
                re.match(self.patterns['subsection_numeric'], text) and
                len(text) < 100
            ),
            'style': 'heading2',
            'priority': 80
        })

        # Regola 4: Riferimenti US brevi
        self.style_rules.append({
            'name': 'us_reference',
            'check': lambda text, ctx: (
                re.match(self.patterns['us_reference'], text) and
                len(text) < 100 and
                ':' in text
            ),
            'style': 'heading3',
            'priority': 70
        })

        # Regola 5: Veri elementi di lista
        self.style_rules.append({
            'name': 'list_item',
            'check': lambda text, ctx: self._is_true_list_item(text, ctx),
            'style': 'list',
            'priority': 60
        })

        # Regola 6: Paragrafi lunghi (SEMPRE normal, MAI heading)
        self.style_rules.append({
            'name': 'long_paragraph',
            'check': lambda text, ctx: len(text) > 100,
            'style': 'normal',
            'priority': 95  # Alta priorità per override heading errati
        })

        # Regola 7: Titoli maiuscoli brevi
        self.style_rules.append({
            'name': 'uppercase_title',
            'check': lambda text, ctx: (
                text.isupper() and
                len(text.split()) <= 6 and
                len(text) < 50 and
                not any(char.isdigit() for char in text)
            ),
            'style': 'heading2',
            'priority': 75
        })

        # Regola 8: Paragrafi con articoli/verbi (indica contenuto descrittivo)
        self.style_rules.append({
            'name': 'descriptive_paragraph',
            'check': lambda text, ctx: self._is_descriptive_content(text),
            'style': 'normal',
            'priority': 50
        })

        # Regola 9: Default per contenuto normale
        self.style_rules.append({
            'name': 'default_normal',
            'check': lambda text, ctx: True,  # Sempre vero (fallback)
            'style': 'normal',
            'priority': 0
        })

    def _is_true_list_item(self, text: str, context: Dict) -> bool:
        """
        Determina se il testo è un vero elemento di lista
        """
        # Non ha senso come lista se è troppo lungo
        if len(text) > 80:
            return False

        # Controlla se siamo in un contesto di lista
        if context.get('in_list_section', False):
            return True

        # Se ha un marker di lista ed è breve
        if re.match(self.patterns['list_marker'], text):
            clean_text = re.sub(self.patterns['list_marker'], '', text)
            # È una lista se è breve e non contiene frasi complete
            if len(clean_text) < 50 and '.' not in clean_text[:-1]:
                return True

        return False

    def _is_descriptive_content(self, text: str) -> bool:
        """
        Determina se il testo è contenuto descrittivo (non un titolo)
        """
        # Indicatori di contenuto descrittivo
        descriptive_indicators = [
            r'\b(è|sono|era|erano|ha|hanno|aveva|avevano)\b',
            r'\b(il|la|lo|gli|le|un|una|uno)\s+\w+\s+\w+',
            r'\b(nel|nella|nell\'|del|della|dell\')\b',
            r'\b(presenta|mostra|evidenzia|documenta|costituisce|comprende)\b',
            r'\b(con|per|tra|fra|su|sopra|sotto)\b',
            r'[,;]',  # Punteggiatura complessa indica paragrafo
        ]

        text_lower = text.lower()
        for pattern in descriptive_indicators:
            if re.search(pattern, text_lower):
                return True

        # Se ha più di 10 parole, probabilmente è descrittivo
        if len(text.split()) > 10:
            return True

        return False

    def analyze_document(self, paragraphs: List[str]) -> List[Dict]:
        """
        Analizza un documento e determina gli stili corretti per ogni paragrafo

        Args:
            paragraphs: Lista di paragrafi del documento

        Returns:
            Lista di dizionari con stili suggeriti
        """
        results = []
        context = {'prev_style': None, 'in_list_section': False}

        for i, text in enumerate(paragraphs):
            text = text.strip()

            if not text:
                results.append({
                    'text': '',
                    'style': 'empty',
                    'confidence': 1.0
                })
                continue

            # Aggiorna contesto
            if re.search(self.patterns['elenco_header'], text.upper()):
                context['in_list_section'] = True
            elif not re.match(self.patterns['list_marker'], text):
                context['in_list_section'] = False

            # Applica regole in ordine di priorità
            best_style = self._determine_style(text, context)

            results.append({
                'text': text[:50] + '...' if len(text) > 50 else text,
                'style': best_style['style'],
                'rule': best_style['name'],
                'confidence': best_style.get('confidence', 0.8)
            })

            context['prev_style'] = best_style['style']

        return results

    def _determine_style(self, text: str, context: Dict) -> Dict:
        """
        Determina lo stile migliore per un testo basato sulle regole
        """
        # Ordina regole per priorità
        sorted_rules = sorted(self.style_rules, key=lambda r: r['priority'], reverse=True)

        for rule in sorted_rules:
            if rule['check'](text, context):
                return {
                    'name': rule['name'],
                    'style': rule['style'],
                    'confidence': 1.0 - (100 - rule['priority']) / 100
                }

        # Fallback
        return {
            'name': 'fallback',
            'style': 'normal',
            'confidence': 0.5
        }

    def correct_document_styles(self, paragraphs: List[Tuple[str, str]]) -> List[Tuple[str, str, str]]:
        """
        Corregge gli stili di un documento

        Args:
            paragraphs: Lista di tuple (testo, stile_attuale)

        Returns:
            Lista di tuple (testo, stile_originale, stile_corretto)
        """
        # Analizza solo i testi
        texts = [p[0] for p in paragraphs]
        analysis = self.analyze_document(texts)

        corrections = []
        for i, (text, current_style) in enumerate(paragraphs):
            suggested = analysis[i]

            # Mappa stili suggeriti a stili Word
            style_map = {
                'title': 'Title',
                'heading1': 'Heading 1',
                'heading2': 'Heading 2',
                'heading3': 'Heading 3',
                'list': 'List Bullet',
                'normal': 'Normal',
                'empty': None
            }

            new_style = style_map.get(suggested['style'], 'Normal')

            # Registra correzione solo se necessaria
            if new_style and new_style != current_style:
                corrections.append((text, current_style, new_style))
            else:
                corrections.append((text, current_style, current_style))

        return corrections

    def get_style_statistics(self, corrections: List[Tuple[str, str, str]]) -> Dict:
        """
        Genera statistiche sulle correzioni
        """
        stats = {
            'total': len(corrections),
            'corrected': 0,
            'by_type': {},
            'corrections': []
        }

        for text, old_style, new_style in corrections:
            if old_style != new_style:
                stats['corrected'] += 1

                key = f"{old_style} -> {new_style}"
                stats['by_type'][key] = stats['by_type'].get(key, 0) + 1

                stats['corrections'].append({
                    'text': text[:50] + '...' if len(text) > 50 else text,
                    'from': old_style,
                    'to': new_style
                })

        return stats


# Test function
def test_agent():
    """Test l'agente con esempi"""
    agent = DocumentStyleAgent()

    test_paragraphs = [
        "REPORT DI SCAVO ARCHEOLOGICO",
        "INTRODUZIONE",
        "La campagna 2025 ha interessato due nuclei contigui del settore occidentale.",
        "1. STRATIGRAFIA E RELAZIONI TRA AREE",
        "US 815: Pavimento TM IIIC",
        "- Item 1",
        "- Item 2",
        "Nell'Area ad Ovest del Piazzale XXXII è stata identificata una sequenza stratigrafica complessa che documenta diverse fasi.",
        "ELENCO DELLE US:",
        "- US 1049: Crollo",
        "- US 1181: Deposito"
    ]

    results = agent.analyze_document(test_paragraphs)

    print("ANALISI STILI:")
    print("-" * 60)
    for i, result in enumerate(results):
        if result['text']:
            print(f"{i+1}. {result['text']}")
            print(f"   Stile: {result['style']} (regola: {result['rule']}, conf: {result['confidence']:.2f})")

    return agent


if __name__ == "__main__":
    test_agent()