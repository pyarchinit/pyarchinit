# -*- coding: utf-8 -*-
"""
Script per generare i file HTML del thesaurus per PyArchInit.
Legge i dati dal database e genera file HTML per ogni lingua supportata.
"""

import os
import sqlite3
from collections import defaultdict

# Configurazione
LANGUAGES = ['IT', 'EN', 'DE', 'ES', 'FR', 'AR', 'CA']

# Mappatura codici tipologia -> nome campo leggibile
FIELD_NAMES = {
    # site_table (1.x)
    '1.1': 'Definizione sito',

    # us_table (2.x)
    '2.1': 'Settore',
    '2.2': 'Soprintendenza',
    '2.3': 'Definizione stratigrafica',
    '2.4': 'Definizione interpretata',
    '2.5': 'Funzione statica',
    '2.6': 'Consistenza legante USM',
    '2.7': 'Consistenza/texture',
    '2.8': 'Metodo di scavo',
    '2.9': 'Formazione',
    '2.10': 'Modo formazione',
    '2.11': 'Consistenza',
    '2.12': 'Stato di conservazione',
    '2.13': 'Campioni',
    '2.14': 'Componenti organici',
    '2.15': 'Inclusi',
    '2.16': 'Schedatore',
    '2.17': 'Rilevatore',
    '2.18': 'Responsabile',
    '2.19': 'Documentazione',
    '2.20': 'Unita tipo',
    '2.21': 'Settore 2',
    '2.22': 'Quadrato',
    '2.23': 'Ambiente',
    '2.24': 'Saggio',
    '2.25': 'Elem. datanti',
    '2.26': 'Osservazioni',
    '2.27': 'Interpretazione',
    '2.28': 'Tipo legante USM',
    '2.29': 'Posa in opera',
    '2.30': 'Lavorazione',
    '2.31': 'Aggregati legante',
    '2.32': 'Materiali',
    '2.33': 'Nota materiali',
    '201.201': 'Colore',
    '202.202': 'Aggregati',
    '203.203': 'Scavato',

    # inventario_materiali_table (3.x)
    '3.1': 'Classe materiale',
    '3.2': 'Tipo materiale',
    '3.3': 'Forma',
    '3.4': 'Stato conservazione',
    '3.5': 'Tipo misura',
    '3.6': 'Unita di misura',
    '301.301': 'Integro',

    # struttura_table (6.x)
    '6.1': 'Sigla struttura',
    '6.2': 'Categoria struttura',
    '6.3': 'Tipologia struttura',
    '6.4': 'Definizione',
    '6.5': 'Materiali impiegati',
    '6.6': 'Elementi strutturali',
    '6.7': 'Unita misura',
    '6.8': 'Unita di misura dim',

    # tomba_table (7.x)
    '7.1': 'Rito',
    '7.2': 'Orientamento',
    '7.3': 'Copertura',
    '7.4': 'Tipo tomba',
    '7.5': 'Segnacolo',
    '7.6': 'Deposizione',
    '7.7': 'Numero deposizioni',
    '701.701': 'Libera',
    '702.702': 'Corredo',

    # campioni_table (4.x)
    '4.1': 'Tipo campione',

    # documentazione_table (5.x)
    '5.1': 'Tipo documentazione',

    # individui_table (8.x)
    '8.1': 'Sesso',
    '8.2': 'Eta',

    # tafonomia_table (9.x)
    '9.1': 'Tipo scheletro',
    '9.2': 'Posizione scheletro',
    '9.3': 'Posizione arti superiori',
    '9.4': 'Posizione arti inferiori',
    '9.5': 'Posizione cranio',

    # TMA - Tabella Materiali Archeologici (10.x)
    '10.1': 'Denominazione Collocazione',
    '10.2': 'Localita',
    '10.3': 'Definizione',
    '10.4': 'Tipologia',
    '10.5': 'Cronologia',
    '10.6': 'Unita Tipo',
    '10.7': 'Area',
    '10.8': 'Classe',
    '10.9': 'Categoria',
    '10.10': 'Materiale',
    '10.11': 'Tecnica',
    '10.12': 'Stato Conservazione',
    '10.13': 'Descrizione',
    '10.14': 'Decorazione',
    '10.15': 'US',

    # Pottery (11.x)
    '11.1': 'Fabric',
    '11.2': 'Percent',
    '11.3': 'Material',
    '11.4': 'Form',
    '11.5': 'Specific Form',
    '11.6': 'Ware',
    '11.7': 'Munsell Color',
    '11.8': 'Surface Treatment',
    '11.9': 'External Decoration',
    '11.10': 'Internal Decoration',
    '11.11': 'Wheel Made',
    '11.12': 'Specific Shape',
    '11.13': 'Preservation',
    '11.14': 'Decoration Type',
    '11.15': 'Decoration Motif',
    '11.16': 'Decoration Position',

    # UT - Unita Topografica (12.x)
    '12.1': 'Tipo Ricognizione',
    '12.2': 'Vegetazione',
    '12.3': 'Metodo GPS',
    '12.4': 'Superficie',
    '12.5': 'Accessibilita',
    '12.6': 'Condizioni Meteo',

    # Fauna/Archeozoologia (13.x)
    '13.1': 'Contesto',
    '13.2': 'Metodologia Recupero',
    '13.3': 'Tipo Accumulo',
    '13.4': 'Tipo Deposizione',
    '13.5': 'Frammentazione',
    '13.6': 'Stato Conservazione',
    '13.7': 'Affidabilita',
    '13.8': 'Combustione',
    '13.9': 'Tipo Combustione',
    '13.10': 'Connessione Anatomica',

    # Inventario Lapidei (14.x)
    '14.1': 'Tipo Lapideo',
    '14.2': 'Materiale',
    '14.3': 'Lavorazione',
    '14.4': 'Stato Conservazione',
}

# Mappatura nome_tabella nel DB -> nome_tabella e descrizione
TABLE_NAMES = {
    # Sito
    'Sito': ('site_table', 'Sito'),
    'site_table': ('site_table', 'Sito'),

    # US/USM
    'US': ('us_table', 'Unita Stratigrafica'),
    'us_table': ('us_table', 'Unita Stratigrafica'),
    'us-table': ('us_table', 'Unita Stratigrafica'),
    'USM': ('us_table_usm', 'Unita Stratigrafica Muraria'),
    'us_table_usm': ('us_table_usm', 'Unita Stratigrafica Muraria'),

    # Struttura
    'Struttura': ('struttura_table', 'Struttura'),
    'struttura_table': ('struttura_table', 'Struttura'),

    # Tomba
    'Tomba': ('tomba_table', 'Tomba'),
    'tomba_table': ('tomba_table', 'Tomba'),

    # Inventario Materiali
    'Inventario Materiali': ('inventario_materiali_table', 'Inventario Materiali'),
    'inventario_materiali_table': ('inventario_materiali_table', 'Inventario Materiali'),

    # Campioni
    'Campioni': ('campioni_table', 'Campioni'),
    'campioni_table': ('campioni_table', 'Campioni'),

    # Documentazione
    'Documentazione': ('documentazione_table', 'Documentazione'),
    'documentazione_table': ('documentazione_table', 'Documentazione'),

    # Individui
    'Individui': ('individui_table', 'Individui'),
    'individui_table': ('individui_table', 'Individui'),

    # Inventario Lapidei
    'Inventario Lapidei': ('inventario_lapidei_table', 'Inventario Lapidei'),
    'inventario_lapidei_table': ('inventario_lapidei_table', 'Inventario Lapidei'),

    # Tafonomia
    'Tafonomia': ('tafonomia_table', 'Tafonomia'),
    'tafonomia_table': ('tafonomia_table', 'Tafonomia'),

    # Periodizzazione
    'Periodizzazione': ('periodizzazione_table', 'Periodizzazione'),
    'periodizzazione_table': ('periodizzazione_table', 'Periodizzazione'),

    # Fauna
    'Fauna': ('fauna_table', 'Archeozoologia/Fauna'),
    'fauna_table': ('fauna_table', 'Archeozoologia/Fauna'),
    'pyarchinit_fauna': ('fauna_table', 'Archeozoologia/Fauna'),

    # UT (Unita Topografica)
    'UT': ('ut_table', 'Unita Topografica'),
    'ut_table': ('ut_table', 'Unita Topografica'),

    # TMA (Tabella Materiali Archeologici)
    'TMA': ('tma_table', 'TMA Materiali Archeologici'),
    'tma_table': ('tma_table', 'TMA Materiali Archeologici'),
    'TMA materiali archeologici': ('tma_table', 'TMA Materiali Archeologici'),
    'tma_materiali_archeologici': ('tma_table', 'TMA Materiali Archeologici'),

    # TMA Materiali Ripetibili
    'TMA Materiali Ripetibili': ('tma_materiali_table', 'TMA Materiali Ripetibili'),
    'tma_materiali_table': ('tma_materiali_table', 'TMA Materiali Ripetibili'),
    'TMA materiali ripetibili': ('tma_materiali_table', 'TMA Materiali Ripetibili'),

    # Pottery
    'Pottery': ('pottery_table', 'Pottery/Ceramica'),
    'pottery_table': ('pottery_table', 'Pottery/Ceramica'),

    # Reperti
    'REPERTI': ('pyarchinit_reperti', 'Reperti'),
    'pyarchinit_reperti': ('pyarchinit_reperti', 'Reperti'),

    # Determinazione Sesso
    'Detsesso': ('detsesso_table', 'Determinazione Sesso'),
    'detsesso_table': ('detsesso_table', 'Determinazione Sesso'),

    # Determinazione Eta
    'Deteta': ('deteta_table', 'Determinazione Eta'),
    'deteta_table': ('deteta_table', 'Determinazione Eta'),

    # Scheda Individuo
    'Schedaind': ('schedaind_table', 'Scheda Individuo'),
    'schedaind_table': ('schedaind_table', 'Scheda Individuo'),
}

# Traduzioni delle etichette UI
UI_LABELS = {
    'IT': {
        'title': 'PyArchInit - Codici Thesaurus',
        'language': 'Italiano',
        'nav_title': 'Navigazione Tabelle',
        'lang_col': 'Lingua',
        'code_col': 'Sigla',
        'desc_col': 'Descrizione',
        'code_label': 'Codice',
        'generated': 'Generato automaticamente dal database thesaurus',
    },
    'EN': {
        'title': 'PyArchInit - Thesaurus Codes',
        'language': 'English',
        'nav_title': 'Table Navigation',
        'lang_col': 'Language',
        'code_col': 'Code',
        'desc_col': 'Description',
        'code_label': 'Code',
        'generated': 'Automatically generated from thesaurus database',
    },
    'DE': {
        'title': 'PyArchInit - Thesaurus Codes',
        'language': 'Deutsch',
        'nav_title': 'Tabellennavigation',
        'lang_col': 'Sprache',
        'code_col': 'Abkurzung',
        'desc_col': 'Beschreibung',
        'code_label': 'Code',
        'generated': 'Automatisch aus der Thesaurus-Datenbank generiert',
    },
    'ES': {
        'title': 'PyArchInit - Codigos Thesaurus',
        'language': 'Espanol',
        'nav_title': 'Navegacion de Tablas',
        'lang_col': 'Idioma',
        'code_col': 'Codigo',
        'desc_col': 'Descripcion',
        'code_label': 'Codigo',
        'generated': 'Generado automaticamente desde la base de datos del thesaurus',
    },
    'FR': {
        'title': 'PyArchInit - Codes Thesaurus',
        'language': 'Francais',
        'nav_title': 'Navigation des Tables',
        'lang_col': 'Langue',
        'code_col': 'Code',
        'desc_col': 'Description',
        'code_label': 'Code',
        'generated': 'Genere automatiquement a partir de la base de donnees du thesaurus',
    },
    'AR': {
        'title': 'PyArchInit - Thesaurus Codes',
        'language': 'Arabic',
        'nav_title': 'Table Navigation',
        'lang_col': 'Language',
        'code_col': 'Code',
        'desc_col': 'Description',
        'code_label': 'Code',
        'generated': 'Automatically generated from thesaurus database',
    },
    'CA': {
        'title': 'PyArchInit - Codis Thesaurus',
        'language': 'Catala',
        'nav_title': 'Navegacio de Taules',
        'lang_col': 'Idioma',
        'code_col': 'Codi',
        'desc_col': 'Descripcio',
        'code_label': 'Codi',
        'generated': 'Generat automaticament des de la base de dades del thesaurus',
    },
}

# Ordine delle tabelle nella navigazione
TABLE_ORDER = [
    'site_table',
    'us_table',
    'us_table_usm',
    'struttura_table',
    'tomba_table',
    'inventario_materiali_table',
    'inventario_lapidei_table',
    'campioni_table',
    'documentazione_table',
    'individui_table',
    'schedaind_table',
    'tafonomia_table',
    'detsesso_table',
    'deteta_table',
    'periodizzazione_table',
    'fauna_table',
    'ut_table',
    'tma_table',
    'tma_materiali_table',
    'pottery_table',
    'pyarchinit_reperti',
]


def get_html_template():
    """Restituisce il template HTML base."""
    return '''<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} ({lang})</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3498db;
        }}
        .language-info {{
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }}
        .nav {{
            background: #2c3e50;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 8px;
        }}
        .nav h3 {{
            color: #fff;
            margin-bottom: 10px;
        }}
        .nav a {{
            color: #3498db;
            text-decoration: none;
            margin-right: 15px;
            padding: 5px 10px;
            background: #34495e;
            border-radius: 4px;
            display: inline-block;
            margin-bottom: 5px;
        }}
        .nav a:hover {{
            background: #3498db;
            color: #fff;
        }}
        .table-section {{
            background: #fff;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .table-header {{
            background: #3498db;
            color: #fff;
            padding: 15px 20px;
        }}
        .table-header h2 {{
            margin: 0;
            font-size: 1.4em;
        }}
        .field-section {{
            border-bottom: 1px solid #eee;
            padding: 15px 20px;
        }}
        .field-section:last-child {{
            border-bottom: none;
        }}
        .field-header {{
            background: #ecf0f1;
            padding: 10px 15px;
            margin: -15px -20px 15px -20px;
            border-bottom: 1px solid #ddd;
        }}
        .field-header h3 {{
            color: #2c3e50;
            font-size: 1.1em;
            margin: 0;
        }}
        .field-header .code-type {{
            color: #7f8c8d;
            font-size: 0.85em;
            font-weight: normal;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 10px 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            color: #2c3e50;
            font-weight: 600;
            font-size: 0.9em;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .sigla {{
            font-family: 'Courier New', monospace;
            background: #e8f4fc;
            padding: 3px 8px;
            border-radius: 3px;
            color: #2980b9;
            font-weight: bold;
        }}
        .lingua {{
            background: #27ae60;
            color: #fff;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
        }}
        .empty-section {{
            padding: 20px;
            color: #999;
            font-style: italic;
        }}
        footer {{
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="language-info">Lingua: <strong>{language_name} ({lang})</strong></p>

        <div class="nav">
            <h3>{nav_title}</h3>
{nav_links}
        </div>

{table_sections}

        <footer>
            <p>PyArchInit Thesaurus Codes - Versione 4.9</p>
            <p>{generated}</p>
        </footer>
    </div>
</body>
</html>
'''


def generate_nav_links(tables_data, lang):
    """Genera i link di navigazione."""
    links = []
    for table_id in TABLE_ORDER:
        if table_id in tables_data:
            table_name = tables_data[table_id].get('display_name', table_id)
            links.append(f'            <a href="#{table_id}">{table_name}</a>')
    return '\n'.join(links)


def generate_table_section(table_id, table_data, labels):
    """Genera una sezione per una tabella."""
    html = f'''        <div class="table-section" id="{table_id}">
            <div class="table-header">
                <h2>{table_id} - {table_data.get('display_name', table_id)}</h2>
            </div>
'''

    if not table_data.get('fields'):
        html += f'''            <div class="field-section">
                <p class="empty-section">Codici in fase di definizione...</p>
            </div>
'''
    else:
        for field_code, field_entries in sorted(table_data['fields'].items(), key=lambda x: float(x[0]) if x[0].replace('.', '').isdigit() else 999):
            field_name = FIELD_NAMES.get(field_code, f'Campo {field_code}')
            html += f'''            <div class="field-section">
                <div class="field-header">
                    <h3>{field_name} <span class="code-type">({labels['code_label']}: {field_code})</span></h3>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 60px;">{labels['lang_col']}</th>
                            <th style="width: 100px;">{labels['code_col']}</th>
                            <th>{labels['desc_col']}</th>
                        </tr>
                    </thead>
                    <tbody>
'''
            # Rimuovi duplicati e ordina
            seen = set()
            unique_entries = []
            for entry in field_entries:
                key = (entry['sigla'].strip(), entry['sigla_estesa'])
                if key not in seen:
                    seen.add(key)
                    unique_entries.append(entry)

            for entry in sorted(unique_entries, key=lambda x: x['sigla'].strip()):
                sigla = entry['sigla'].strip()
                sigla_estesa = entry['sigla_estesa'] or sigla
                lingua = entry['lingua']
                html += f'''                        <tr><td><span class="lingua">{lingua}</span></td><td><span class="sigla">{sigla}</span></td><td>{sigla_estesa}</td></tr>
'''

            html += '''                    </tbody>
                </table>
            </div>
'''

    html += '        </div>\n\n'
    return html


def load_thesaurus_data(db_path):
    """Carica i dati del thesaurus dal database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT nome_tabella, tipologia_sigla, sigla, sigla_estesa, lingua
        FROM pyarchinit_thesaurus_sigle
        ORDER BY nome_tabella, tipologia_sigla, sigla
    ''')

    # Organizza i dati per lingua -> tabella -> campo -> entries
    data = defaultdict(lambda: defaultdict(lambda: {'display_name': '', 'fields': defaultdict(list)}))

    for row in cursor.fetchall():
        nome_tabella, tipologia_sigla, sigla, sigla_estesa, lingua = row

        # Normalizza nome tabella
        if nome_tabella in TABLE_NAMES:
            table_id, display_name = TABLE_NAMES[nome_tabella]
        else:
            table_id = nome_tabella
            display_name = nome_tabella

        # Aggiungi entry
        data[lingua][table_id]['display_name'] = display_name
        data[lingua][table_id]['fields'][tipologia_sigla].append({
            'sigla': sigla,
            'sigla_estesa': sigla_estesa,
            'lingua': lingua
        })

    conn.close()
    return data


def generate_html_for_language(lang, thesaurus_data, output_dir):
    """Genera il file HTML per una lingua specifica."""
    labels = UI_LABELS.get(lang, UI_LABELS['EN'])
    tables_data = thesaurus_data.get(lang, {})

    # Se non ci sono dati per questa lingua, usa IT come fallback
    if not tables_data and lang != 'IT':
        tables_data = thesaurus_data.get('IT', {})
        # Ma mostra comunque la lingua corretta nelle etichette

    # Genera le sezioni delle tabelle
    table_sections = ''
    for table_id in TABLE_ORDER:
        if table_id in tables_data:
            table_sections += generate_table_section(table_id, tables_data[table_id], labels)
        else:
            # Crea sezione vuota
            display_name = table_id.replace('_table', '').replace('_', ' ').title()
            table_sections += f'''        <div class="table-section" id="{table_id}">
            <div class="table-header">
                <h2>{table_id} - {display_name}</h2>
            </div>
            <div class="field-section">
                <p class="empty-section">Codici in fase di definizione...</p>
            </div>
        </div>

'''

    # Genera il file HTML
    html = get_html_template().format(
        lang_code=lang.lower(),
        lang=lang,
        title=labels['title'],
        language_name=labels['language'],
        nav_title=labels['nav_title'],
        nav_links=generate_nav_links(tables_data if tables_data else {t: {'display_name': t.replace('_table', '').title()} for t in TABLE_ORDER}, lang),
        table_sections=table_sections,
        generated=labels['generated']
    )

    # Salva il file
    output_file = os.path.join(output_dir, f'codici_{lang.lower()}_new.html')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generato: {output_file}")
    return output_file


def main():
    """Funzione principale."""
    # Determina i percorsi
    script_dir = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(script_dir)
    tabs_dir = os.path.join(plugin_dir, 'tabs')

    # Percorso database
    db_path = os.path.join(plugin_dir, 'resources', 'dbfiles', 'pyarchinit_db.sqlite')

    if not os.path.exists(db_path):
        # Prova percorso alternativo
        db_path = os.path.join(plugin_dir, 'pyarchinit_db.sqlite')

    if not os.path.exists(db_path):
        print(f"Database non trovato: {db_path}")
        return

    print(f"Caricamento dati da: {db_path}")

    # Carica dati
    thesaurus_data = load_thesaurus_data(db_path)

    print(f"Trovate {len(thesaurus_data)} lingue nel database")
    for lang, tables in thesaurus_data.items():
        total_entries = sum(
            len(entries)
            for table in tables.values()
            for entries in table.get('fields', {}).values()
        )
        print(f"  {lang}: {total_entries} voci in {len(tables)} tabelle")

    # Genera file HTML per ogni lingua
    print("\nGenerazione file HTML...")
    for lang in LANGUAGES:
        generate_html_for_language(lang, thesaurus_data, tabs_dir)

    print("\nCompletato!")


if __name__ == '__main__':
    main()
