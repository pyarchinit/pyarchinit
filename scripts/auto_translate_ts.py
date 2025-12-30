#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per tradurre automaticamente i file .ts usando OpenAI GPT-4.1

Uso:
    python scripts/auto_translate_ts.py [--lang LANG] [--check] [--dry-run]

Esempi:
    python scripts/auto_translate_ts.py                    # Traduce tutte le lingue
    python scripts/auto_translate_ts.py --lang fr_FR      # Solo francese
    python scripts/auto_translate_ts.py --check           # Controlla/migliora traduzioni esistenti
    python scripts/auto_translate_ts.py --dry-run         # Mostra cosa farebbe senza salvare

Richiede:
    pip install openai
    export OPENAI_API_KEY="your-api-key"
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import time

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

try:
    from openai import OpenAI
except ImportError:
    print("Errore: openai non installato. Esegui: pip install openai")
    sys.exit(1)

# Directory del plugin
PLUGIN_DIR = Path(__file__).parent.parent
I18N_DIR = PLUGIN_DIR / "i18n"

# Configurazione lingue
LANGUAGES = {
    "fr_FR": {
        "name": "Francese",
        "code": "fr",
        "file": "pyarchinit_plugin_fr_FR.ts",
        "action": "translate"  # translate = nuova traduzione
    },
    "es_ES": {
        "name": "Spagnolo",
        "code": "es",
        "file": "pyarchinit_plugin_es_ES.ts",
        "action": "translate"
    },
    "ar_LB": {
        "name": "Arabo (Libano)",
        "code": "ar",
        "file": "pyarchinit_plugin_ar_LB.ts",
        "action": "translate"
    },
    "de_DE": {
        "name": "Tedesco",
        "code": "de",
        "file": "pyarchinit_plugin_de_DE.ts",
        "action": "check"  # check = controlla/migliora esistenti
    },
    "en_US": {
        "name": "Inglese",
        "code": "en",
        "file": "pyarchinit_plugin_en_US.ts",
        "action": "check"
    },
    "ca_ES": {
        "name": "Catalano",
        "code": "ca",
        "file": "pyarchinit_plugin_ca_ES.ts",
        "action": "translate"
    },
}

# Modello OpenAI (gpt-4o è il più recente e veloce)
MODEL = "gpt-4o"


class TSTranslator:
    def __init__(self, api_key=None, dry_run=False):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY non impostata. Usa: export OPENAI_API_KEY='...'")

        self.client = OpenAI(api_key=self.api_key)
        self.dry_run = dry_run
        self.stats = {"translated": 0, "checked": 0, "skipped": 0, "errors": 0}

    def translate_batch(self, texts, target_lang, target_code, check_mode=False):
        """Traduce un batch di testi usando GPT-4.1."""
        if not texts:
            return []

        if check_mode:
            prompt = f"""Sei un traduttore esperto per software di archeologia (PyArchInit - plugin QGIS).
Controlla e migliora queste traduzioni in {target_lang}.
Il contesto è un'applicazione GIS per la gestione di scavi archeologici.

Per ogni riga, restituisci la traduzione corretta (o migliorata se necessario).
Se la traduzione è già buona, restituiscila invariata.
Mantieni la terminologia tecnica archeologica appropriata.

Testi da controllare (formato: originale ||| traduzione attuale):
"""
            for i, (source, translation) in enumerate(texts, 1):
                prompt += f"{i}. {source} ||| {translation}\n"

            prompt += f"\nRispondi SOLO con le traduzioni, una per riga, numerate (1. traduzione, 2. traduzione, ecc.):"
        else:
            prompt = f"""Sei un traduttore esperto per software di archeologia (PyArchInit - plugin QGIS).
Traduci questi testi dall'italiano al {target_lang}.
Il contesto è un'applicazione GIS per la gestione di scavi archeologici.

Terminologia importante:
- US = Unità Stratigrafica (mantieni come US o traduci appropriatamente)
- USM = Unità Stratigrafica Muraria
- Sito = Site/Sito archeologico
- Scavo = Excavation
- Reperto = Find/Artifact
- Tomba = Tomb/Burial
- Periodizzazione = Periodization
- Struttura = Structure
- Campione = Sample

Testi da tradurre:
"""
            for i, text in enumerate(texts, 1):
                prompt += f"{i}. {text}\n"

            prompt += f"\nRispondi SOLO con le traduzioni in {target_lang}, una per riga, numerate (1. traduzione, 2. traduzione, ecc.):"

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": f"Sei un traduttore professionale specializzato in software archeologico. Traduci in {target_lang} ({target_code})."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000
            )

            result_text = response.choices[0].message.content.strip()

            # Parse le risposte numerate
            translations = []
            lines = result_text.split('\n')
            for line in lines:
                # Rimuovi numerazione (1. , 2. , ecc.)
                cleaned = re.sub(r'^\d+[\.\)]\s*', '', line.strip())
                if cleaned:
                    translations.append(cleaned)

            return translations

        except Exception as e:
            print(f"    Errore API OpenAI: {e}")
            self.stats["errors"] += len(texts)
            return [""] * len(texts)

    def process_ts_file(self, lang_key, check_existing=False):
        """Processa un file .ts e lo traduce."""
        lang_config = LANGUAGES[lang_key]
        ts_file = I18N_DIR / lang_config["file"]

        if not ts_file.exists():
            print(f"  File non trovato: {ts_file}")
            return False

        print(f"\n{'='*60}")
        print(f"Elaborazione: {lang_config['name']} ({lang_key})")
        print(f"File: {ts_file.name}")
        print(f"Modalità: {'Controllo/Miglioramento' if check_existing else 'Traduzione'}")
        print(f"{'='*60}")

        # Parse XML
        tree = ET.parse(ts_file)
        root = tree.getroot()

        # Raccogli stringhe da tradurre
        to_translate = []
        message_elements = []

        for context in root.findall('.//context'):
            context_name = context.find('name').text if context.find('name') is not None else "Unknown"

            for message in context.findall('message'):
                source_elem = message.find('source')
                translation_elem = message.find('translation')

                if source_elem is None or source_elem.text is None:
                    continue

                source_text = source_elem.text.strip()

                # Salta stringhe vuote o troppo corte
                if len(source_text) < 2:
                    continue

                # Salta se è solo numeri o simboli
                if re.match(r'^[\d\s\.\,\-\+\*\/\(\)\[\]\{\}]+$', source_text):
                    continue

                current_translation = ""
                if translation_elem is not None and translation_elem.text:
                    current_translation = translation_elem.text.strip()

                # Determina se tradurre
                needs_work = False

                if check_existing:
                    # In modalità check, lavora solo su traduzioni esistenti
                    if current_translation and current_translation != source_text:
                        needs_work = True
                        to_translate.append((source_text, current_translation))
                else:
                    # In modalità traduzione, lavora su stringhe non tradotte
                    is_unfinished = translation_elem is not None and translation_elem.get('type') == 'unfinished'
                    if not current_translation or is_unfinished or current_translation == source_text:
                        needs_work = True
                        to_translate.append(source_text)

                if needs_work:
                    message_elements.append((message, translation_elem))

        print(f"Stringhe da elaborare: {len(to_translate)}")

        if not to_translate:
            print("  Nessuna stringa da elaborare.")
            return True

        if self.dry_run:
            print("  [DRY-RUN] Nessuna modifica effettuata.")
            for i, item in enumerate(to_translate[:10], 1):
                if check_existing:
                    print(f"    {i}. {item[0][:50]}... -> {item[1][:30]}...")
                else:
                    print(f"    {i}. {item[:50]}...")
            if len(to_translate) > 10:
                print(f"    ... e altre {len(to_translate) - 10} stringhe")
            return True

        # Traduci in batch (max 20 per richiesta per evitare limiti)
        batch_size = 20
        all_translations = []

        for i in range(0, len(to_translate), batch_size):
            batch = to_translate[i:i + batch_size]
            print(f"  Elaborazione batch {i//batch_size + 1}/{(len(to_translate) + batch_size - 1)//batch_size}...")

            translations = self.translate_batch(
                batch,
                lang_config["name"],
                lang_config["code"],
                check_mode=check_existing
            )
            all_translations.extend(translations)

            # Rate limiting
            time.sleep(1)

        # Applica traduzioni
        for idx, (message, translation_elem) in enumerate(message_elements):
            if idx < len(all_translations) and all_translations[idx]:
                if translation_elem is None:
                    translation_elem = ET.SubElement(message, 'translation')

                translation_elem.text = all_translations[idx]

                # Rimuovi attributo 'unfinished' se presente
                if 'type' in translation_elem.attrib:
                    del translation_elem.attrib['type']

                if check_existing:
                    self.stats["checked"] += 1
                else:
                    self.stats["translated"] += 1

        # Salva file
        tree.write(ts_file, encoding='utf-8', xml_declaration=True)
        print(f"  Salvato: {ts_file.name}")

        return True

    def run(self, languages=None, check_mode=False):
        """Esegue la traduzione per le lingue specificate."""
        if languages is None:
            languages = list(LANGUAGES.keys())

        print("\n" + "="*60)
        print("PyArchInit - Traduzione Automatica con GPT-4.1")
        print("="*60)

        for lang_key in languages:
            if lang_key not in LANGUAGES:
                print(f"Lingua non supportata: {lang_key}")
                continue

            lang_config = LANGUAGES[lang_key]

            # Usa check_mode dal parametro o dalla configurazione della lingua
            use_check = check_mode or lang_config.get("action") == "check"

            self.process_ts_file(lang_key, check_existing=use_check)

        # Statistiche finali
        print("\n" + "="*60)
        print("RIEPILOGO")
        print("="*60)
        print(f"Stringhe tradotte: {self.stats['translated']}")
        print(f"Stringhe controllate: {self.stats['checked']}")
        print(f"Errori: {self.stats['errors']}")
        print("\nPer compilare i file .qm esegui:")
        print("  python scripts/update_translations.py")


def main():
    parser = argparse.ArgumentParser(description="Traduzione automatica file .ts con GPT-4.1")
    parser.add_argument("--lang", help="Codice lingua (es: fr_FR, es_ES, ar_LB)")
    parser.add_argument("--check", action="store_true", help="Controlla/migliora traduzioni esistenti")
    parser.add_argument("--dry-run", action="store_true", help="Mostra cosa farebbe senza modificare")
    parser.add_argument("--api-key", help="OpenAI API key (o usa OPENAI_API_KEY env)")

    args = parser.parse_args()

    try:
        translator = TSTranslator(api_key=args.api_key, dry_run=args.dry_run)

        languages = [args.lang] if args.lang else None
        translator.run(languages=languages, check_mode=args.check)

    except ValueError as e:
        print(f"Errore: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
