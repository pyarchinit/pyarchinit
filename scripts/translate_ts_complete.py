#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete translation script for PyArchInit .ts files using OpenAI GPT-4o.
This script translates untranslated strings one at a time for safety.

Archaeological terminology:
- Italian: US (Unità Stratigrafica), USM (Unità Stratigrafica Muraria)
- English: SU (Stratigraphic Unit), WSU (Wall Stratigraphic Unit)
- German: SE (Stratigraphische Einheit), MSE (Mauer-Stratigraphische Einheit) or keep US/USM
- French: US (Unité Stratigraphique), USM (Unité Stratigraphique de Maçonnerie)
- Spanish: UE (Unidad Estratigráfica), UEM (Unidad Estratigráfica Muraria)
- Arabic: SU, WSU (keep English abbreviations)
- Catalan: UE (Unitat Estratigràfica), UEM (Unitat Estratigràfica Murària)
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import time

sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed. Run: pip install openai")
    sys.exit(1)

PLUGIN_DIR = Path(__file__).parent.parent
I18N_DIR = PLUGIN_DIR / "i18n"

# Language configuration with terminology
LANGUAGES = {
    "en_US": {
        "name": "English",
        "code": "en",
        "file": "pyarchinit_plugin_en_US.ts",
        "terminology": {
            "US": "SU",
            "USM": "WSU",
            "Unità Stratigrafica": "Stratigraphic Unit",
            "Unità Stratigrafica Muraria": "Wall Stratigraphic Unit",
            "Scheda US": "SU Form",
            "Scheda USM": "WSU Form",
            "Lista US": "SU List",
            "Lista USM": "WSU List",
        }
    },
    "de_DE": {
        "name": "German",
        "code": "de",
        "file": "pyarchinit_plugin_de_DE.ts",
        "terminology": {
            "US": "SE",
            "USM": "MSE",
            "Unità Stratigrafica": "Stratigraphische Einheit",
            "Unità Stratigrafica Muraria": "Mauer-Stratigraphische Einheit",
            "Scheda US": "SE-Formular",
            "Scheda USM": "MSE-Formular",
            "Lista US": "SE-Liste",
            "Lista USM": "MSE-Liste",
        }
    },
    "fr_FR": {
        "name": "French",
        "code": "fr",
        "file": "pyarchinit_plugin_fr_FR.ts",
        "terminology": {
            "US": "US",
            "USM": "USM",
            "Unità Stratigrafica": "Unité Stratigraphique",
            "Unità Stratigrafica Muraria": "Unité Stratigraphique de Maçonnerie",
            "Scheda US": "Fiche US",
            "Scheda USM": "Fiche USM",
            "Lista US": "Liste US",
            "Lista USM": "Liste USM",
        }
    },
    "es_ES": {
        "name": "Spanish",
        "code": "es",
        "file": "pyarchinit_plugin_es_ES.ts",
        "terminology": {
            "US": "UE",
            "USM": "UEM",
            "Unità Stratigrafica": "Unidad Estratigráfica",
            "Unità Stratigrafica Muraria": "Unidad Estratigráfica Muraria",
            "Scheda US": "Ficha UE",
            "Scheda USM": "Ficha UEM",
            "Lista US": "Lista UE",
            "Lista USM": "Lista UEM",
        }
    },
    "ar_LB": {
        "name": "Arabic (Lebanon)",
        "code": "ar",
        "file": "pyarchinit_plugin_ar_LB.ts",
        "terminology": {
            "US": "SU",
            "USM": "WSU",
            "Unità Stratigrafica": "Stratigraphic Unit",
            "Unità Stratigrafica Muraria": "Wall Stratigraphic Unit",
            "Scheda US": "نموذج SU",
            "Scheda USM": "نموذج WSU",
            "Lista US": "قائمة SU",
            "Lista USM": "قائمة WSU",
        }
    },
    "ca_ES": {
        "name": "Catalan",
        "code": "ca",
        "file": "pyarchinit_plugin_ca_ES.ts",
        "terminology": {
            "US": "UE",
            "USM": "UEM",
            "Unità Stratigrafica": "Unitat Estratigràfica",
            "Unità Stratigrafica Muraria": "Unitat Estratigràfica Murària",
            "Scheda US": "Fitxa UE",
            "Scheda USM": "Fitxa UEM",
            "Lista US": "Llista UE",
            "Lista USM": "Llista UEM",
        }
    },
}

MODEL = "gpt-4o"

# Terms that should NOT be translated (keep as-is)
SKIP_TERMS = {
    # Technical/DB terms
    "localhost", "postgres", "password", "user", "port", "host", "DB", "pyarchinit",
    "pyarchinit2", "sqlite", "postgresql", "spatialite", "PostGIS", "SSL",
    "Host", "Database", "Port", "Username", "Password",
    # UI technical
    "nd", "N/D", "n/d", "...", "OK", "ok", "ID", "id", "Help",
    # Zoological orders (Latin - universal)
    "anseriformes", "charadriiformes", "columbiformes", "falconiformes",
    "galliformes", "gruiformes", "passeriformes", "strigiformes", "accipitriformes",
    "ungulata", "lagonorfa", "carnivora", "rodentia", "aves", "pisces",
    # Zoological families (Latin - universal)
    "bovidae", "canidae", "cervidae", "felidae", "equidae", "suidae",
    "leporidae", "muridae", "mustelidae", "ursidae",
    # Zoological genera/species (Latin - universal)
    "bos", "ovis", "capra", "sus", "equus", "cervus", "canis", "felis",
    "lepus", "vulpes", "ursus", "rattus", "mus",
    "bos taurus", "ovis aries", "capra hircus", "sus scrofa", "sus domesticus",
    "equus caballus", "equus asinus", "cervus elaphus", "canis familiaris",
    # Anatomical terms (Latin - universal)
    "radio", "tibia", "ulna", "vertebra", "axis", "pelvis", "fibula",
    "furcula", "cranium", "mandibula", "scapula", "humerus", "femur",
    "carpus", "tarsus", "metacarpus", "metatarsus", "phalanx",
    "telemetacarpo", "carpometacarpo", "tarsometatarso",
    # Abbreviations used in zooarchaeology
    "dx", "sx", "f_a", "f_p", "f_u", "c_u", "o_l", "o_q", "pdi",
    # Measurement codes
    "GLl", "GLm", "Bd", "Bp", "SD", "GL", "Dp", "Dd", "BT", "HTC",
    # Additional scientific/Italian terms that should stay
    "suidi", "ursidi", "mammifera", "turdidae",
    # Chart/stats terms (universal)
    "Histogram", "Scatterplot", "Boxplot", "Plot", "Bar", "Sql",
    "Cutoff", "Nugget", "Psill", "Sill", "Range", "Lag", "Kappa",
    "Automap", "Clipper", "Pychart", "Co-plot",
    # Geostatistics terms
    "Sph", "Ste", "Exp", "Gau", "Mat",
    # Software/UI terms that stay in English
    "Report", "run!", "Model", "map", "Tool", "Tools", "Status",
    "DBMS Toolbar", "DB Info", "Reload DB", "Connection test",
    "Last rec", "First rec", "Prev rec", "Next rec", "New record",
    "Delete record", "Save", "Order by", "new search", "help",
    "Area", "Glabella", "3d", "Ctrl+G", "formula", "Parameter vgm",
    "set size point", "DB name", "N. Inv",
    # Munsell colors
    "Munsell", "HUE", "VALUE", "CHROMA",
    # Single letters/abbreviations
    "N", "S", "E", "W", "NE", "NW", "SE", "SW",
    "cm", "mm", "m", "km", "kg", "g", "mg",
    # Software names
    "QGIS", "PyArchInit", "Graphviz", "DOT", "PDF", "CSV", "XML", "GML",
    # Date formats
    "dd/MM/yyyy", "yyyy-MM-dd", "dd-MM-yyyy",
    # Backup/PyArchInit specific
    "Pyarchinit Backup",
}

# Patterns that indicate the string shouldn't be translated
SKIP_PATTERNS = [
    r'^[\d\s\.\,\-\+\*\/\(\)\[\]\{\}\<\>\=\%\_\:]+$',  # Only numbers/symbols
    r'^[A-Z]{1,4}$',  # Short uppercase abbreviations
    r'^\d+$',  # Just numbers
    r'^https?://',  # URLs
    r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',  # Emails
    r'^#[0-9A-Fa-f]{6}$',  # Hex colors
    r'^[a-z]+_[a-z]+$',  # Latin binomial nomenclature (genus_species)
    r'^[a-z]+_[a-z]+_[a-z]+$',  # Trinomial nomenclature (genus_species_subspecies)
    r'^[a-z]_[a-z]+_[a-z]_[a-z]+$',  # Abbreviated trinomial (p_graculus_c_monedula)
    r'^cfr_[a-z_]+$',  # cfr_ prefixed scientific names
    r'^cf_[a-z_]+$',  # cf_ prefixed scientific names
    r'^[a-z]+idae$',  # Latin family names (-idae suffix)
    r'^[a-z]+iformes$',  # Latin order names (-iformes suffix)
    r'^[a-z]+inae$',  # Latin subfamily names (-inae suffix)
    r'^[a-z]+ifera$',  # Latin (-ifera suffix, like mammalifera)
    r'^[a-z]+_sp$',  # Species sp. notation
    r'^[a-z]+_cf_[a-z]+$',  # cf notation in species
    r'^mamm[a-z]+$',  # Mammal-related terms
]


class TSTranslator:
    def __init__(self, api_key=None, dry_run=False):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set. Use: export OPENAI_API_KEY='...'")

        self.client = OpenAI(api_key=self.api_key)
        self.dry_run = dry_run
        self.stats = {"translated": 0, "skipped": 0, "errors": 0}

    def apply_terminology(self, text, terminology):
        """Apply terminology replacements to a text."""
        result = text
        for italian, translated in terminology.items():
            # Word boundary replacement to avoid partial matches
            result = re.sub(r'\b' + re.escape(italian) + r'\b', translated, result)
        return result

    def translate_single(self, source_text, target_lang, target_code, terminology):
        """Translate a single string using GPT-4o."""

        # First check if we have a direct terminology match
        if source_text in terminology:
            return terminology[source_text]

        # Apply terminology to the source text for context
        text_with_terms = self.apply_terminology(source_text, terminology)

        # If after applying terminology the text is mostly the same, it might be a simple case
        # Build terminology context string
        term_context = "\n".join([f"- '{k}' -> '{v}'" for k, v in terminology.items()])

        prompt = f"""Translate this Italian text to {target_lang} for a QGIS archaeological data management plugin (PyArchInit).

IMPORTANT terminology (ALWAYS use these exact translations):
{term_context}

Context: This is a GUI label/message in archaeological software for managing excavations, finds, stratigraphic units, and documentation.

Text to translate: "{source_text}"

Respond with ONLY the {target_lang} translation, nothing else. No quotes, no explanation."""

        try:
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": f"You are an expert translator for archaeological software. Translate to {target_lang}. Use the exact terminology provided. Be concise."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )

            result = response.choices[0].message.content.strip()

            # Clean up common issues
            result = result.strip('"\'')

            # Validate: result should not be empty and should not be way longer than source
            if not result or len(result) > len(source_text) * 5:
                print(f"    [WARN] Suspicious translation for '{source_text[:30]}...': '{result[:30]}...'")
                return None

            return result

        except Exception as e:
            print(f"    [ERROR] API error: {e}")
            return None

    def process_ts_file(self, lang_key, limit=None):
        """Process a .ts file and translate untranslated strings."""
        lang_config = LANGUAGES[lang_key]
        ts_file = I18N_DIR / lang_config["file"]

        if not ts_file.exists():
            print(f"  File not found: {ts_file}")
            return False

        print(f"\n{'='*60}")
        print(f"Processing: {lang_config['name']} ({lang_key})")
        print(f"File: {ts_file.name}")
        print(f"{'='*60}")

        # Parse XML preserving structure
        ET.register_namespace('', '')
        tree = ET.parse(ts_file)
        root = tree.getroot()

        # Collect untranslated strings
        untranslated = []

        for context in root.findall('.//context'):
            for message in context.findall('message'):
                source_elem = message.find('source')
                translation_elem = message.find('translation')

                if source_elem is None or source_elem.text is None:
                    continue

                source_text = source_elem.text.strip()

                # Skip short strings
                if len(source_text) < 2:
                    continue

                # Skip if it's in the skip list (technical terms)
                if source_text.strip() in SKIP_TERMS:
                    continue

                # Skip if matches a skip pattern
                skip = False
                for pattern in SKIP_PATTERNS:
                    if re.match(pattern, source_text.strip()):
                        skip = True
                        break
                if skip:
                    continue

                # Check if translation is needed
                needs_translation = False
                current_translation = ""

                if translation_elem is None:
                    needs_translation = True
                elif translation_elem.get('type') == 'unfinished':
                    needs_translation = True
                    current_translation = translation_elem.text or ""
                elif not translation_elem.text or not translation_elem.text.strip():
                    needs_translation = True
                elif translation_elem.text.strip() == source_text:
                    # Same as source - probably not translated
                    needs_translation = True

                if needs_translation:
                    untranslated.append({
                        'source': source_text,
                        'message': message,
                        'translation_elem': translation_elem,
                        'current': current_translation
                    })

        total = len(untranslated)
        print(f"Untranslated strings found: {total}")

        if total == 0:
            print("  All strings are already translated!")
            return True

        if limit:
            untranslated = untranslated[:limit]
            print(f"Processing first {limit} strings...")

        if self.dry_run:
            print("  [DRY-RUN] Would translate:")
            for i, item in enumerate(untranslated[:20], 1):
                print(f"    {i}. {item['source'][:60]}...")
            if len(untranslated) > 20:
                print(f"    ... and {len(untranslated) - 20} more")
            return True

        # Translate strings one by one (safer than batching)
        terminology = lang_config.get("terminology", {})
        translated_count = 0

        for i, item in enumerate(untranslated, 1):
            source = item['source']
            print(f"  [{i}/{len(untranslated)}] Translating: {source[:50]}...", end=" ", flush=True)

            translation = self.translate_single(
                source,
                lang_config["name"],
                lang_config["code"],
                terminology
            )

            if translation:
                # Update XML
                message = item['message']
                translation_elem = item['translation_elem']

                if translation_elem is None:
                    translation_elem = ET.SubElement(message, 'translation')

                translation_elem.text = translation

                # Remove 'unfinished' type if present
                if 'type' in translation_elem.attrib:
                    del translation_elem.attrib['type']

                translated_count += 1
                self.stats["translated"] += 1
                print(f"-> {translation[:40]}...")
            else:
                self.stats["errors"] += 1
                print("[FAILED]")

            # Rate limiting - be gentle with API
            time.sleep(0.5)

            # Save periodically (every 50 translations)
            if translated_count > 0 and translated_count % 50 == 0:
                tree.write(ts_file, encoding='utf-8', xml_declaration=True)
                print(f"  [Checkpoint saved: {translated_count} translations]")

        # Final save
        tree.write(ts_file, encoding='utf-8', xml_declaration=True)
        print(f"\nSaved: {ts_file.name}")
        print(f"Translated: {translated_count}/{len(untranslated)}")

        return True

    def mark_skip_terms(self, lang_key):
        """Mark skip terms as translated (copy source to translation)."""
        lang_config = LANGUAGES[lang_key]
        ts_file = I18N_DIR / lang_config["file"]

        if not ts_file.exists():
            return 0

        tree = ET.parse(ts_file)
        root = tree.getroot()
        marked = 0

        for context in root.findall('.//context'):
            for message in context.findall('message'):
                source_elem = message.find('source')
                translation_elem = message.find('translation')

                if source_elem is None or source_elem.text is None:
                    continue

                source_text = source_elem.text.strip()

                # Check if this is a skip term
                is_skip = source_text in SKIP_TERMS
                if not is_skip:
                    for pattern in SKIP_PATTERNS:
                        if re.match(pattern, source_text):
                            is_skip = True
                            break

                if is_skip:
                    needs_update = False
                    if translation_elem is None:
                        translation_elem = ET.SubElement(message, 'translation')
                        needs_update = True
                    elif translation_elem.get('type') == 'unfinished':
                        needs_update = True
                    elif not translation_elem.text or not translation_elem.text.strip():
                        needs_update = True

                    if needs_update:
                        translation_elem.text = source_text
                        if 'type' in translation_elem.attrib:
                            del translation_elem.attrib['type']
                        marked += 1

        if marked > 0:
            tree.write(ts_file, encoding='utf-8', xml_declaration=True)

        return marked

    def run(self, languages=None, limit=None):
        """Run translation for specified languages."""
        if languages is None:
            languages = list(LANGUAGES.keys())

        print("\n" + "="*60)
        print("PyArchInit - Complete Translation with GPT-4o")
        print("="*60)

        for lang_key in languages:
            if lang_key not in LANGUAGES:
                print(f"Language not supported: {lang_key}")
                continue

            # First, mark skip terms as translated
            marked = self.mark_skip_terms(lang_key)
            if marked > 0:
                print(f"  Auto-marked {marked} technical terms as translated")

            self.process_ts_file(lang_key, limit=limit)

        # Final stats
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Translated: {self.stats['translated']}")
        print(f"Errors: {self.stats['errors']}")
        print("\nTo compile .qm files, run:")
        print("  cd i18n && for ts in *.ts; do pyside6-lrelease \"$ts\" -qm \"${ts%.ts}.qm\"; done")


def main():
    parser = argparse.ArgumentParser(description="Complete translation of .ts files with GPT-4o")
    parser.add_argument("--lang", help="Language code (e.g., en_US, fr_FR)")
    parser.add_argument("--limit", type=int, help="Limit number of translations per language")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--api-key", help="OpenAI API key (or use OPENAI_API_KEY env)")

    args = parser.parse_args()

    try:
        translator = TSTranslator(api_key=args.api_key, dry_run=args.dry_run)
        languages = [args.lang] if args.lang else None
        translator.run(languages=languages, limit=args.limit)

    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
