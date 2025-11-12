# .docugenius/docugenius_core.py

## Overview

This file contains 84 documented elements.

## Classes

### DocumentationType

Supported documentation output formats

**Inherits from**: Enum

### AIProvider

Supported AI providers for enhanced documentation

**Inherits from**: Enum

### ProjectConfig

Project configuration for documentation generation

**Decorators**: dataclass

### CodeElement

Universal code element representation

**Decorators**: dataclass

### LanguageAnalyzer

Abstract base class for language-specific analyzers

**Inherits from**: ABC

#### Methods

##### analyze_file(self, file_path)

Analyze a file and extract code elements

##### get_file_patterns(self)

Return file patterns this analyzer handles

### PythonAnalyzer

Python code analyzer using AST

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze Python file using AST

### JavaAnalyzer

Java code analyzer

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze Java file

### JavaScriptAnalyzer

JavaScript/TypeScript code analyzer using esprima

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze JavaScript/TypeScript file

### UniversalDocumentationGenerator

Main documentation generator with multi-language support

#### Methods

##### __init__(self, config)

##### generate_documentation(self)

Main entry point for documentation generation

##### watch_for_changes(self)

Watch for file changes and auto-regenerate documentation

### DocUpdateHandler

**Inherits from**: FileSystemEventHandler

#### Methods

##### __init__(self, generator)

##### on_modified(self, event)

### DocumentationType

Supported documentation output formats

**Inherits from**: Enum

### AIProvider

Supported AI providers for enhanced documentation

**Inherits from**: Enum

### ProjectConfig

Project configuration for documentation generation

**Decorators**: dataclass

### CodeElement

Universal code element representation

**Decorators**: dataclass

### LanguageAnalyzer

Abstract base class for language-specific analyzers

**Inherits from**: ABC

#### Methods

##### analyze_file(self, file_path)

Analyze a file and extract code elements

##### get_file_patterns(self)

Return file patterns this analyzer handles

### PythonAnalyzer

Python code analyzer using AST

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze Python file using AST

### JavaAnalyzer

Java code analyzer

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze Java file

### JavaScriptAnalyzer

JavaScript/TypeScript code analyzer using esprima

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze JavaScript/TypeScript file

### UniversalDocumentationGenerator

Main documentation generator with multi-language support

#### Methods

##### __init__(self, config)

##### generate_documentation(self)

Main entry point for documentation generation

##### watch_for_changes(self)

Watch for file changes and auto-regenerate documentation

### DocUpdateHandler

**Inherits from**: FileSystemEventHandler

#### Methods

##### __init__(self, generator)

##### on_modified(self, event)

### DocumentationType

Supported documentation output formats

**Inherits from**: Enum

### AIProvider

Supported AI providers for enhanced documentation

**Inherits from**: Enum

### ProjectConfig

Project configuration for documentation generation

**Decorators**: dataclass

### CodeElement

Universal code element representation

**Decorators**: dataclass

### LanguageAnalyzer

Abstract base class for language-specific analyzers

**Inherits from**: ABC

#### Methods

##### analyze_file(self, file_path)

Analyze a file and extract code elements

##### get_file_patterns(self)

Return file patterns this analyzer handles

### PythonAnalyzer

Python code analyzer using AST

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze Python file using AST

### JavaAnalyzer

Java code analyzer

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze Java file

### JavaScriptAnalyzer

JavaScript/TypeScript code analyzer using esprima

**Inherits from**: LanguageAnalyzer

#### Methods

##### get_file_patterns(self)

##### analyze_file(self, file_path)

Analyze JavaScript/TypeScript file

### UniversalDocumentationGenerator

Main documentation generator with multi-language support

#### Methods

##### __init__(self, config)

##### generate_documentation(self)

Main entry point for documentation generation

##### watch_for_changes(self)

Watch for file changes and auto-regenerate documentation

### DocUpdateHandler

**Inherits from**: FileSystemEventHandler

#### Methods

##### __init__(self, generator)

##### on_modified(self, event)

## Functions

### install_missing_modules()

Install missing required modules automatically

### main()

Command-line interface

### tutorial_sort_key(path)

**Parameters:**
- `path`

### api_sort_key(path)

**Parameters:**
- `path`

### install_missing_modules()

Install missing required modules automatically

### main()

Command-line interface

### tutorial_sort_key(path)

**Parameters:**
- `path`

### api_sort_key(path)

**Parameters:**
- `path`

### install_missing_modules()

Install missing required modules automatically

### main()

Command-line interface

### tutorial_sort_key(path)

**Parameters:**
- `path`

### api_sort_key(path)

**Parameters:**
- `path`

