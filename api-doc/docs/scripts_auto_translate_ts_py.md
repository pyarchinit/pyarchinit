# scripts/auto_translate_ts.py

## Overview

This file contains 7 documented elements.

## Classes

### TSTranslator

*No description available.*
Automates the translation and review of Qt `.ts` (XML-based translation source) files for the PyArchInit QGIS plugin using the OpenAI API. It supports two operating modes: translating untranslated strings from Italian into a target language, and checking or improving existing translations, both processed in batches via `translate_batch`. The class tracks per-session statistics (`translated`, `checked`, `skipped`, `errors`) and respects a dry-run mode that previews pending work without modifying any files.

#### Methods

##### __init__(self, api_key, dry_run)

Initializes a `TSTranslator` instance by resolving the OpenAI API key from the `api_key` parameter or, if not provided, from the `OPENAI_API_KEY` environment variable; raises a `ValueError` if neither source yields a valid key. Creates an `OpenAI` client using the resolved key and stores the `dry_run` flag. Initializes a `stats` dictionary tracking four counters: `"translated"`, `"checked"`, `"skipped"`, and `"errors"`, all set to `0`.

##### translate_batch(self, texts, target_lang, target_code, check_mode)

Traduce un batch di testi usando GPT-4.1.

##### process_ts_file(self, lang_key, check_existing)

Processa un file .ts e lo traduce.

##### run(self, languages, check_mode)

Esegue la traduzione per le lingue specificate.

## Functions

### main()

*No description available.*
Entry point for the automatic `.ts` file translation CLI tool. Parses command-line arguments (`--lang`, `--check`, `--dry-run`, `--api-key`) to configure a `TSTranslator` instance, then invokes its `run()` method with the specified language and mode options. Returns `0` on success, or `1` if a `ValueError` is raised or the process is interrupted by the user.

