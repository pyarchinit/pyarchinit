# modules/utility/document_style_agent.py

## Overview

This file contains 7 documented elements.

## Classes

### DocumentStyleAgent

Agente che analizza e corregge automaticamente gli stili dei documenti

#### Methods

##### __init__(self)

Initializes an instance of the document style analysis and correction agent. Sets up `self.patterns`, a dictionary of compiled regular expression patterns used to identify content types such as main titles, section titles, numeric subsections, US references, list markers, and summary headers. Also initializes `self.style_rules` as an empty list and delegates the population of style determination rules to `_initialize_rules()`.

##### analyze_document(self, paragraphs)

Analizza un documento e determina gli stili corretti per ogni paragrafo

Args:
    paragraphs: Lista di paragrafi del documento

Returns:
    Lista di dizionari con stili suggeriti

##### correct_document_styles(self, paragraphs)

Corregge gli stili di un documento

Args:
    paragraphs: Lista di tuple (testo, stile_attuale)

Returns:
    Lista di tuple (testo, stile_originale, stile_corretto)

##### get_style_statistics(self, corrections)

Genera statistiche sulle correzioni

## Functions

### test_agent()

Test l'agente con esempi

