# scripts/translate_ts_complete.py

## Overview

This file contains 9 documented elements.

## Classes

### TSTranslator

*No description available.*
Translates untranslated strings in Qt `.ts` localization files for the PyArchInit QGIS plugin using the OpenAI GPT-4o API. It parses `.ts` XML files, identifies strings requiring translation based on configurable skip terms and patterns, and updates the XML with translated content while applying domain-specific archaeological terminology. The class also supports dry-run mode, periodic checkpoint saves, automatic marking of technical terms, and tracks translation statistics across one or more target languages.

#### Methods

##### __init__(self, api_key, dry_run)

Initializes a `TSTranslator` instance by resolving the OpenAI API key from the `api_key` parameter or, if not provided, from the `OPENAI_API_KEY` environment variable. Raises a `ValueError` if no API key can be found. Sets up an `OpenAI` client, stores the `dry_run` flag, and initializes a `stats` dictionary tracking counts for `"translated"`, `"skipped"`, and `"errors"` operations.

##### apply_terminology(self, text, terminology)

Apply terminology replacements to a text.

##### translate_single(self, source_text, target_lang, target_code, terminology)

Translate a single string using GPT-4o.

##### process_ts_file(self, lang_key, limit)

Process a .ts file and translate untranslated strings.

##### mark_skip_terms(self, lang_key)

Mark skip terms as translated (copy source to translation).

##### run(self, languages, limit)

Run translation for specified languages.

## Functions

### main()

Parses command-line arguments for language code (`--lang`), translation limit (`--limit`), dry-run mode (`--dry-run`), and OpenAI API key (`--api-key`), then instantiates a `TSTranslator` and invokes its `run` method with the provided options. Returns `0` on success, or `1` if a `ValueError` is raised or the process is interrupted via `KeyboardInterrupt`. Intended as the script entry point, called via `sys.exit(main())` when the module is executed directly.

