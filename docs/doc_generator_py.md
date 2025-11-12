# doc_generator.py

## Overview

This file contains 69 documented elements.

## Classes

### AdvancedCodeAnalyzer

Analizzatore avanzato che estrae tutta la documentazione dal codice

**Inherits from**: ast.NodeVisitor

#### Methods

##### __init__(self, source_code, filepath)

##### get_line_range(self, node)

Ottiene le linee di codice per un nodo

##### extract_type_hints(self, node)

Estrae type hints dai parametri

##### ast_to_string(self, node)

Converte un nodo AST in stringa (fallback per Python < 3.9)

##### extract_return_type(self, node)

Estrae il tipo di ritorno

##### extract_decorators(self, node)

Estrae i decoratori

##### parse_docstring(self, docstring)

Parse docstring per estrarre descrizione, parametri, return, esempi

##### visit_ClassDef(self, node)

Visita una definizione di classe

##### extract_function_info(self, node, is_method)

Estrae informazioni dettagliate da una funzione

##### visit_FunctionDef(self, node)

Visita una definizione di funzione

##### visit_AsyncFunctionDef(self, node)

Visita una definizione di funzione asincrona

##### visit_Import(self, node)

Visita un import

##### visit_ImportFrom(self, node)

Visita un import from

##### calculate_complexity(self, node)

Calcola la complessità ciclomatica

##### analyze(self)

Ritorna l'analisi completa

### PyArchInitDocGenerator

Generatore di documentazione specifico per PyArchInit

#### Methods

##### __init__(self, project_path)

##### analyze_project(self, limit)

Analizza l'intero progetto PyArchInit

##### generate_main_documentation(self)

Genera la documentazione principale

##### generate_config_file(self)

Genera file di configurazione per auto-update

### AdvancedCodeAnalyzer

Analizzatore avanzato che estrae tutta la documentazione dal codice

**Inherits from**: ast.NodeVisitor

#### Methods

##### __init__(self, source_code, filepath)

##### get_line_range(self, node)

Ottiene le linee di codice per un nodo

##### extract_type_hints(self, node)

Estrae type hints dai parametri

##### ast_to_string(self, node)

Converte un nodo AST in stringa (fallback per Python < 3.9)

##### extract_return_type(self, node)

Estrae il tipo di ritorno

##### extract_decorators(self, node)

Estrae i decoratori

##### parse_docstring(self, docstring)

Parse docstring per estrarre descrizione, parametri, return, esempi

##### visit_ClassDef(self, node)

Visita una definizione di classe

##### extract_function_info(self, node, is_method)

Estrae informazioni dettagliate da una funzione

##### visit_FunctionDef(self, node)

Visita una definizione di funzione

##### visit_AsyncFunctionDef(self, node)

Visita una definizione di funzione asincrona

##### visit_Import(self, node)

Visita un import

##### visit_ImportFrom(self, node)

Visita un import from

##### calculate_complexity(self, node)

Calcola la complessità ciclomatica

##### analyze(self)

Ritorna l'analisi completa

### PyArchInitDocGenerator

Generatore di documentazione specifico per PyArchInit

#### Methods

##### __init__(self, project_path)

##### analyze_project(self, limit)

Analizza l'intero progetto PyArchInit

##### generate_main_documentation(self)

Genera la documentazione principale

##### generate_config_file(self)

Genera file di configurazione per auto-update

### AdvancedCodeAnalyzer

Analizzatore avanzato che estrae tutta la documentazione dal codice

**Inherits from**: ast.NodeVisitor

#### Methods

##### __init__(self, source_code, filepath)

##### get_line_range(self, node)

Ottiene le linee di codice per un nodo

##### extract_type_hints(self, node)

Estrae type hints dai parametri

##### ast_to_string(self, node)

Converte un nodo AST in stringa (fallback per Python < 3.9)

##### extract_return_type(self, node)

Estrae il tipo di ritorno

##### extract_decorators(self, node)

Estrae i decoratori

##### parse_docstring(self, docstring)

Parse docstring per estrarre descrizione, parametri, return, esempi

##### visit_ClassDef(self, node)

Visita una definizione di classe

##### extract_function_info(self, node, is_method)

Estrae informazioni dettagliate da una funzione

##### visit_FunctionDef(self, node)

Visita una definizione di funzione

##### visit_AsyncFunctionDef(self, node)

Visita una definizione di funzione asincrona

##### visit_Import(self, node)

Visita un import

##### visit_ImportFrom(self, node)

Visita un import from

##### calculate_complexity(self, node)

Calcola la complessità ciclomatica

##### analyze(self)

Ritorna l'analisi completa

### PyArchInitDocGenerator

Generatore di documentazione specifico per PyArchInit

#### Methods

##### __init__(self, project_path)

##### analyze_project(self, limit)

Analizza l'intero progetto PyArchInit

##### generate_main_documentation(self)

Genera la documentazione principale

##### generate_config_file(self)

Genera file di configurazione per auto-update

## Functions

### main()

Main entry point

### main()

Main entry point

### main()

Main entry point

