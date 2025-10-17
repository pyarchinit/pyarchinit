#!/usr/bin/env python3
"""
DocuGenius Core - Universal Documentation Generator with AI Support
Supports multiple programming languages and documentation formats
"""

import ast
import os
import sys
import json
import re
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from abc import ABC, abstractmethod
import hashlib
import concurrent.futures
from enum import Enum


def install_missing_modules():
    """Install missing required modules automatically"""
    required_modules = {
        'openai': 'openai>=1.0.0',
        'anthropic': 'anthropic>=0.18.0',
        'javalang': 'javalang',
        'esprima': 'esprima',
        'tree_sitter': 'tree-sitter',
        'watchdog': 'watchdog',
        'sphinx': 'sphinx',
        # Sphinx themes (verified working with HTML generation)
        'alabaster': 'alabaster',
        'sphinx_rtd_theme': 'sphinx_rtd_theme',
        'pydata_sphinx_theme': 'pydata-sphinx-theme',
        'furo': 'furo',
        'piccolo_theme': 'piccolo-theme',
        'sphinx_book_theme': 'sphinx-book-theme',
        'sphinx_material': 'sphinx-material',
        'sphinx_pdj_theme': 'sphinx-pdj-theme',
        'insipid_sphinx_theme': 'insipid-sphinx-theme',
        # Sphinx extensions
        'myst_parser': 'myst-parser',
        'sphinxcontrib.bibtex': 'sphinxcontrib-bibtex',
        'sphinxcontrib.napoleon': 'sphinxcontrib-napoleon',
        'sphinxcontrib.httpdomain': 'sphinxcontrib-httpdomain',
        'sphinxcontrib.plantuml': 'sphinxcontrib-plantuml',
        'sphinx_autodoc_typehints': 'sphinx-autodoc-typehints',
        'sphinx_copybutton': 'sphinx-copybutton',
        'sphinx_tabs': 'sphinx-tabs',
        'sphinxemoji': 'sphinxemoji'
    }

    missing = []
    for module_name, pip_package in required_modules.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pip_package)

    if missing:
        print(f"📦 Installing missing modules: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("✅ All required modules installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to install some modules. Install manually with: pip install {' '.join(missing)}")


# Install missing modules on import
install_missing_modules()

# Language parsers
try:
    import javalang  # For Java parsing
except ImportError:
    javalang = None

try:
    import esprima  # For JavaScript/TypeScript parsing
except ImportError:
    esprima = None

try:
    from tree_sitter import Language, Parser  # For multiple languages
except ImportError:
    Parser = None


class DocumentationType(Enum):
    """Supported documentation output formats"""
    MARKDOWN = "markdown"
    SPHINX_RST = "sphinx_rst"
    SPHINX_HTML = "sphinx_html"
    SPHINX_PDF = "sphinx_pdf"
    MKDOCS = "mkdocs"
    DOXYGEN = "doxygen"
    JAVADOC = "javadoc"
    JSDOC = "jsdoc"


class AIProvider(Enum):
    """Supported AI providers for enhanced documentation"""
    JETBRAINS_AI = "jetbrains_ai"
    OPENAI = "openai"
    CLAUDE = "claude"
    LOCAL_LLM = "local_llm"
    NONE = "none"


@dataclass
class ProjectConfig:
    """Project configuration for documentation generation"""
    project_path: Path
    project_name: str
    output_path: Path
    doc_type: DocumentationType = DocumentationType.MARKDOWN
    ai_provider: AIProvider = AIProvider.NONE
    ai_api_key: Optional[str] = None
    ai_model: Optional[str] = None
    max_tokens: int = 500
    include_private: bool = False
    include_tests: bool = False
    include_utility_scripts: bool = True
    recursive: bool = True
    file_patterns: List[str] = field(default_factory=lambda: ["*.py", "*.java", "*.js", "*.ts", "*.go", "*.rs"])
    ignore_patterns: List[str] = field(default_factory=lambda: [
        "__pycache__", ".git", "node_modules", ".idea", "target", "dist", "build",
        "venv", "_venv", ".venv", "env", ".env", "virtualenv",  # Python virtual environments
        ".gradle", ".mvn", "vendor",  # Other build/dependency directories
        ".pytest_cache", ".mypy_cache", ".tox",  # Python test/type check caches
        "site-packages", "lib/python"  # Additional Python library paths
    ])
    max_depth: int = 10
    generate_diagrams: bool = True
    generate_metrics: bool = True
    auto_update: bool = False
    sphinx_theme: str = "sphinx_rtd_theme"
    custom_templates: Optional[Path] = None
    target_language: Optional[str] = None  # Target language for translation (en, it, es, fr, de)
    tutorial_mode: str = 'both'  # 'tutorials_only', 'api_only', or 'both'


@dataclass
class CodeElement:
    """Universal code element representation"""
    name: str
    type: str  # class, function, method, variable, etc.
    file_path: Path
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    modifiers: List[str] = field(default_factory=list)  # public, private, static, etc.
    parent: Optional[str] = None
    children: List['CodeElement'] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    ai_description: Optional[str] = None


class LanguageAnalyzer(ABC):
    """Abstract base class for language-specific analyzers"""

    @abstractmethod
    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze a file and extract code elements"""
        pass

    @abstractmethod
    def get_file_patterns(self) -> List[str]:
        """Return file patterns this analyzer handles"""
        pass


class PythonAnalyzer(LanguageAnalyzer):
    """Python code analyzer using AST"""

    def get_file_patterns(self) -> List[str]:
        return ["*.py"]

    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze Python file using AST"""
        elements = []
        try:
            # Try UTF-8 first, then fallback to latin-1, then ignore errors
            source = None
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        source = f.read()
                    break
                except (UnicodeDecodeError, LookupError):
                    continue

            if source is None:
                # Last resort: read with error handling
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    source = f.read()

            tree = ast.parse(source, str(file_path))

            # Extract module docstring
            module_doc = ast.get_docstring(tree)
            if module_doc:
                elements.append(CodeElement(
                    name=file_path.stem,
                    type="module",
                    file_path=file_path,
                    line_start=1,
                    line_end=1,
                    docstring=module_doc
                ))

            # Visit all nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    elements.extend(self._analyze_class(node, file_path))
                elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    if not self._is_method(node, tree):
                        elements.append(self._analyze_function(node, file_path))

        except SyntaxError as e:
            print(f"⚠️  Syntax error in {file_path.name}: {e}")
        except Exception as e:
            print(f"⚠️  Error analyzing {file_path.name}: {e}")

        return elements

    def _analyze_class(self, node: ast.ClassDef, file_path: Path) -> List[CodeElement]:
        """Analyze a class node"""
        elements = []

        # Create class element
        class_elem = CodeElement(
            name=node.name,
            type="class",
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            decorators=[self._get_decorator_name(d) for d in node.decorator_list]
        )

        # Add base classes
        class_elem.attributes['bases'] = [self._get_name(base) for base in node.bases]

        # Analyze methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._analyze_function(item, file_path, parent=node.name)
                class_elem.children.append(method)
                elements.append(method)

        elements.insert(0, class_elem)
        return elements

    def _analyze_function(self, node, file_path: Path, parent: Optional[str] = None) -> CodeElement:
        """Analyze a function/method node"""

        # Extract parameters
        params = []
        for arg in node.args.args:
            param = {
                'name': arg.arg,
                'type': self._get_annotation(arg.annotation) if arg.annotation else None
            }
            params.append(param)

        # Create function element
        func_elem = CodeElement(
            name=node.name,
            type="method" if parent else "function",
            file_path=file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=ast.get_docstring(node),
            parameters=params,
            return_type=self._get_annotation(node.returns) if node.returns else None,
            decorators=[self._get_decorator_name(d) for d in node.decorator_list],
            parent=parent
        )

        # Check if async
        if isinstance(node, ast.AsyncFunctionDef):
            func_elem.modifiers.append("async")

        return func_elem

    def _is_method(self, node, tree):
        """Check if a function is a method inside a class"""
        for cls in ast.walk(tree):
            if isinstance(cls, ast.ClassDef):
                if node in cls.body:
                    return True
        return False

    def _get_decorator_name(self, decorator):
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return str(decorator)

    def _get_annotation(self, node):
        """Extract type annotation"""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif hasattr(ast, 'unparse'):
            return ast.unparse(node)
        return str(node)

    def _get_name(self, node):
        """Extract name from various node types"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return str(node)


class JavaAnalyzer(LanguageAnalyzer):
    """Java code analyzer"""

    def get_file_patterns(self) -> List[str]:
        return ["*.java"]

    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze Java file"""
        if not javalang:
            return []

        elements = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = javalang.parse.parse(source)

            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_elem = self._analyze_class(node, file_path, source)
                elements.append(class_elem)

            for path, node in tree.filter(javalang.tree.InterfaceDeclaration):
                interface_elem = self._analyze_interface(node, file_path, source)
                elements.append(interface_elem)

        except Exception as e:
            print(f"Error analyzing Java file {file_path}: {e}")

        return elements

    def _analyze_class(self, node, file_path: Path, source: str) -> CodeElement:
        """Analyze Java class"""
        class_elem = CodeElement(
            name=node.name,
            type="class",
            file_path=file_path,
            line_start=node.position.line if node.position else 1,
            line_end=node.position.line if node.position else 1,
            docstring=self._extract_javadoc(node, source),
            modifiers=node.modifiers if node.modifiers else []
        )

        # Analyze methods
        for method in node.methods:
            method_elem = self._analyze_method(method, file_path, source, node.name)
            class_elem.children.append(method_elem)

        return class_elem

    def _analyze_interface(self, node, file_path: Path, source: str) -> CodeElement:
        """Analyze Java interface"""
        return CodeElement(
            name=node.name,
            type="interface",
            file_path=file_path,
            line_start=node.position.line if node.position else 1,
            line_end=node.position.line if node.position else 1,
            docstring=self._extract_javadoc(node, source),
            modifiers=node.modifiers if node.modifiers else []
        )

    def _analyze_method(self, node, file_path: Path, source: str, parent: str) -> CodeElement:
        """Analyze Java method"""
        params = []
        for param in node.parameters:
            params.append({
                'name': param.name,
                'type': str(param.type)
            })

        return CodeElement(
            name=node.name,
            type="method",
            file_path=file_path,
            line_start=node.position.line if node.position else 1,
            line_end=node.position.line if node.position else 1,
            docstring=self._extract_javadoc(node, source),
            parameters=params,
            return_type=str(node.return_type) if node.return_type else "void",
            modifiers=node.modifiers if node.modifiers else [],
            parent=parent
        )

    def _extract_javadoc(self, node, source: str) -> Optional[str]:
        """Extract Javadoc comment for a node"""
        # Simplified - would need proper implementation
        return None


class JavaScriptAnalyzer(LanguageAnalyzer):
    """JavaScript/TypeScript code analyzer using esprima"""

    def get_file_patterns(self) -> List[str]:
        return ["*.js", "*.jsx", "*.ts", "*.tsx", "*.mjs"]

    def analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze JavaScript/TypeScript file"""
        if not esprima:
            return []

        elements = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            # Parse with esprima (supports ES6+)
            tree = esprima.parseScript(source, {'loc': True, 'comment': True, 'jsx': True})

            # Extract comments for JSDoc
            comments = {c.loc.start.line: c.value for c in tree.comments if c.type == 'Block'}

            # Analyze the AST
            for node in self._walk(tree):
                if node.type == 'FunctionDeclaration':
                    elements.append(self._analyze_function(node, file_path, comments))
                elif node.type == 'ClassDeclaration':
                    elements.extend(self._analyze_class(node, file_path, comments))
                elif node.type == 'VariableDeclarator' and node.init and node.init.type == 'ArrowFunctionExpression':
                    elements.append(self._analyze_arrow_function(node, file_path, comments))

        except Exception as e:
            print(f"⚠️  Error analyzing JavaScript file {file_path.name}: {e}")

        return elements

    def _walk(self, node, parent=None):
        """Recursively walk the AST"""
        if isinstance(node, dict):
            yield node
            for key, value in node.items():
                if isinstance(value, (dict, list)):
                    yield from self._walk(value, node)
        elif isinstance(node, list):
            for item in node:
                yield from self._walk(item, parent)

    def _analyze_class(self, node, file_path: Path, comments: dict) -> List[CodeElement]:
        """Analyze JavaScript/TypeScript class"""
        elements = []

        line_start = node.loc.start.line if hasattr(node, 'loc') and node.loc else 1
        line_end = node.loc.end.line if hasattr(node, 'loc') and node.loc else line_start

        class_elem = CodeElement(
            name=node.id.name if node.id else 'Anonymous',
            type="class",
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            docstring=self._get_jsdoc(line_start, comments)
        )

        # Extract superclass
        if hasattr(node, 'superClass') and node.superClass:
            if hasattr(node.superClass, 'name'):
                class_elem.attributes['bases'] = [node.superClass.name]

        # Analyze class methods
        if hasattr(node, 'body') and hasattr(node.body, 'body'):
            for item in node.body.body:
                if item.type == 'MethodDefinition':
                    method = self._analyze_method(item, file_path, comments, class_elem.name)
                    class_elem.children.append(method)
                    elements.append(method)

        elements.insert(0, class_elem)
        return elements

    def _analyze_method(self, node, file_path: Path, comments: dict, parent: str) -> CodeElement:
        """Analyze class method"""
        line_start = node.loc.start.line if hasattr(node, 'loc') and node.loc else 1
        line_end = node.loc.end.line if hasattr(node, 'loc') and node.loc else line_start

        params = []
        if hasattr(node, 'value') and hasattr(node.value, 'params'):
            for param in node.value.params:
                param_name = param.name if hasattr(param, 'name') else 'unknown'
                params.append({'name': param_name, 'type': None})

        modifiers = []
        if hasattr(node, 'static') and node.static:
            modifiers.append('static')
        if hasattr(node, 'kind'):
            modifiers.append(node.kind)  # 'get', 'set', 'constructor', 'method'

        return CodeElement(
            name=node.key.name if hasattr(node.key, 'name') else 'unknown',
            type="method",
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            docstring=self._get_jsdoc(line_start, comments),
            parameters=params,
            modifiers=modifiers,
            parent=parent
        )

    def _analyze_function(self, node, file_path: Path, comments: dict) -> CodeElement:
        """Analyze JavaScript function"""
        line_start = node.loc.start.line if hasattr(node, 'loc') and node.loc else 1
        line_end = node.loc.end.line if hasattr(node, 'loc') and node.loc else line_start

        params = []
        if hasattr(node, 'params'):
            for param in node.params:
                param_name = param.name if hasattr(param, 'name') else 'unknown'
                params.append({'name': param_name, 'type': None})

        modifiers = []
        if hasattr(node, 'async') and node.async_:
            modifiers.append('async')

        return CodeElement(
            name=node.id.name if node.id else 'anonymous',
            type="function",
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            docstring=self._get_jsdoc(line_start, comments),
            parameters=params,
            modifiers=modifiers
        )

    def _analyze_arrow_function(self, node, file_path: Path, comments: dict) -> CodeElement:
        """Analyze arrow function assigned to variable"""
        line_start = node.loc.start.line if hasattr(node, 'loc') and node.loc else 1
        line_end = node.loc.end.line if hasattr(node, 'loc') and node.loc else line_start

        params = []
        if hasattr(node.init, 'params'):
            for param in node.init.params:
                param_name = param.name if hasattr(param, 'name') else 'unknown'
                params.append({'name': param_name, 'type': None})

        return CodeElement(
            name=node.id.name if hasattr(node.id, 'name') else 'anonymous',
            type="function",
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            docstring=self._get_jsdoc(line_start, comments),
            parameters=params
        )

    def _get_jsdoc(self, line: int, comments: dict) -> Optional[str]:
        """Extract JSDoc comment for a line"""
        # Look for comment on the line before or same line
        for offset in range(0, 5):
            if line - offset in comments:
                comment = comments[line - offset]
                # Clean JSDoc formatting
                if comment.startswith('*'):
                    lines = comment.split('\n')
                    cleaned = []
                    for l in lines:
                        l = l.strip()
                        if l.startswith('*'):
                            l = l[1:].strip()
                        if l and not l.startswith('@'):
                            cleaned.append(l)
                    return ' '.join(cleaned) if cleaned else None
                return comment.strip()
        return None


class UniversalDocumentationGenerator:
    """Main documentation generator with multi-language support"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.analyzers: Dict[str, LanguageAnalyzer] = {
            'python': PythonAnalyzer(),
            'java': JavaAnalyzer() if javalang else None,
            'javascript': JavaScriptAnalyzer() if esprima else None,
        }
        self.elements: List[CodeElement] = []
        self.file_cache: Dict[str, str] = {}
        self.ai_client = self._initialize_ai_client()

    def _remove_emojis(self, text: str) -> str:
        """Remove emoji and special Unicode characters from text for LaTeX compatibility"""
        import re
        # Remove emoji and other unicode symbols that LaTeX can't handle
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002500-\U00002BEF"  # box drawing, geometric shapes, misc symbols
                                   u"\U00002702-\U000027B0"  # dingbats
                                   u"\U000024C2-\U0001F251"  # enclosed characters
                                   u"\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
                                   u"\U0001FA00-\U0001FA6F"  # chess symbols, etc
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub('', text)

    def _initialize_ai_client(self):
        """Initialize AI client based on configuration"""
        if self.config.ai_provider == AIProvider.OPENAI:
            try:
                from openai import OpenAI
                return OpenAI(api_key=self.config.ai_api_key)
            except ImportError:
                print("OpenAI library not installed. Install with: pip install openai>=1.0.0")
                return None
        elif self.config.ai_provider == AIProvider.CLAUDE:
            try:
                from anthropic import Anthropic
                return Anthropic(api_key=self.config.ai_api_key)
            except ImportError:
                print("Anthropic library not installed. Install with: pip install anthropic>=0.18.0")
                return None
        elif self.config.ai_provider == AIProvider.JETBRAINS_AI:
            # Would integrate with JetBrains AI API
            pass
        return None

    def _detect_documentation_language(self) -> str:
        """Detect the primary language of documentation based on code comments and docstrings"""
        import re

        # More distinctive words for each language (avoiding overlap and common tech terms)
        language_indicators = {
            'en': ['the ', ' this ', ' that ', ' with ', ' from ', ' have ', ' will ', ' what ', ' when ', ' which ', ' are ', ' were ', ' and ', ' for ', ' can ', ' has '],
            'it': [' il ', ' dello ', ' della ', ' degli ', ' che ', ' sono ', ' questo ', ' questa ', ' nei ', ' negli ', ' alle ', ' con ', ' per ', ' nel ', ' sulla '],
            'es': [' para ', ' pero ', ' como ', ' esta ', ' estos ', ' estas ', ' donde ', ' cuando ', ' porque ', ' hacer '],
            'fr': [' dans ', ' pour ', ' avec ', ' mais ', ' comme ', ' sont ', ' cette ', ' tous ', ' toutes ', ' dont ', ' où '],
            'de': [' der ', ' die ', ' das ', ' und ', ' ist ', ' den ', ' dem ', ' mit ', ' ein ', ' eine ', ' wird ', ' auf ', ' von ']
        }

        text_samples = []

        # Collect docstrings and comments from analyzed elements
        for element in self.elements[:min(100, len(self.elements))]:  # Sample first 100 elements
            if element.docstring and len(element.docstring) > 20:  # Only substantial docstrings
                text_samples.append(' ' + element.docstring.lower() + ' ')

        # Combine all text
        combined_text = ' '.join(text_samples)

        if not combined_text or len(combined_text) < 50:
            return 'en'  # Default to English if insufficient text

        # Count matches for each language (exact string matching with spaces)
        language_scores = {}
        for lang, indicators in language_indicators.items():
            score = 0
            for word in indicators:
                # Count occurrences of exact word patterns (with surrounding spaces)
                score += combined_text.count(word)
            language_scores[lang] = score

        # Get max score
        max_score = max(language_scores.values()) if language_scores else 0

        # If max score is very low or English has highest score, default to English
        if max_score < 5:
            detected_lang = 'en'
        else:
            detected_lang = max(language_scores, key=language_scores.get)
            # If scores are close, prefer English (within 30% margin)
            if language_scores['en'] > max_score * 0.7:
                detected_lang = 'en'

        print(f"🌐 Detected documentation language: {detected_lang.upper()} (score: {language_scores.get(detected_lang, 0)}, all scores: {language_scores})")
        sys.stdout.flush()

        return detected_lang

    def _translate_documentation(self, detected_lang: str, target_lang: str):
        """Translate documentation to target language using AI"""
        if not self.ai_client or not target_lang or detected_lang == target_lang:
            return

        print(f"🌍 Translating documentation from {detected_lang.upper()} to {target_lang.upper()}...")
        sys.stdout.flush()

        language_names = {
            'en': 'English',
            'it': 'Italian',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }

        source_lang_name = language_names.get(detected_lang, detected_lang)
        target_lang_name = language_names.get(target_lang, target_lang)

        # Translate docstrings and AI descriptions
        translated_count = 0
        for element in self.elements:
            if element.docstring or element.ai_description:
                text_to_translate = element.docstring or element.ai_description

                try:
                    prompt = f"""Translate the following technical documentation from {source_lang_name} to {target_lang_name}.
Maintain technical terms and code references exactly as they are.

Text to translate:
{text_to_translate}

Provide only the translation, without any explanation."""

                    if self.config.ai_provider == AIProvider.OPENAI:
                        response = self.ai_client.chat.completions.create(
                            model=self.config.ai_model or 'gpt-4o',
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=self.config.max_tokens or 500,
                            temperature=0.3
                        )
                        translated_text = response.choices[0].message.content.strip()

                    elif self.config.ai_provider == AIProvider.CLAUDE:
                        response = self.ai_client.messages.create(
                            model=self.config.ai_model or 'claude-3-5-sonnet-20241022',
                            max_tokens=self.config.max_tokens or 500,
                            temperature=0.3,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        translated_text = response.content[0].text.strip()
                    else:
                        continue

                    # Update element with translated text
                    if element.docstring:
                        element.docstring = translated_text
                    elif element.ai_description:
                        element.ai_description = translated_text

                    translated_count += 1
                    print(f"✓ Translated {element.name} ({translated_count}/{len(self.elements)})")
                    sys.stdout.flush()

                except Exception as e:
                    print(f"⚠ Translation error for {element.name}: {e}")
                    continue

        print(f"✅ Translated {translated_count} documentation entries to {target_lang_name}")
        sys.stdout.flush()

    def _log_progress(self, stage: str, message: str, percent: int):
        """Log progress in JSON format for easy parsing by Java UI"""
        progress_data = {
            'stage': stage,
            'message': message,
            'percent': percent,
            'timestamp': datetime.now().isoformat()
        }
        print(f"PROGRESS:{json.dumps(progress_data)}")
        print(message)  # Also print human-readable message

    def generate_documentation(self) -> Dict[str, Any]:
        """Main entry point for documentation generation"""
        self._log_progress("STARTING", "Starting documentation generation", 0)
        sys.stdout.flush()

        # Step 1: Scan and analyze all files
        self._log_progress("SCANNING", f"Scanning project: {self.config.project_path}", 10)
        sys.stdout.flush()
        self._scan_project()

        # Step 1.5: Detect documentation language
        detected_lang = self._detect_documentation_language()

        # Step 2: Enhance with AI if configured
        if self.config.ai_provider != AIProvider.NONE:
            self._log_progress("AI_ENHANCING", "Enhancing with AI", 50)
            sys.stdout.flush()
            self._enhance_with_ai()

        # Step 2.5: Translate documentation if target language specified
        # Allow disabling translation by setting target_language to "none" or when AI provider is NONE or JETBRAINS_AI
        should_translate = (
            self.config.target_language and
            self.config.target_language.lower() != 'none' and
            self.config.ai_provider not in [AIProvider.NONE, AIProvider.JETBRAINS_AI]
        )

        if should_translate:
            self._log_progress("TRANSLATING", "Translating documentation", 65)
            sys.stdout.flush()
            self._translate_documentation(detected_lang, self.config.target_language)

        # Step 3: Generate output based on format
        self._log_progress("GENERATING", "Generating documentation output", 70)
        sys.stdout.flush()
        output = self._generate_output()

        # Step 4: Generate AI-powered tutorials if AI is enabled
        if self.config.ai_provider != AIProvider.NONE and self.ai_client:
            self._log_progress("TUTORIALS", "Generating AI-powered tutorials", 80)
            sys.stdout.flush()
            tutorial_docs = self._generate_tutorials()
            output.update(tutorial_docs)

        # Step 5: Save documentation
        self._log_progress("SAVING", "Saving documentation files", 90)
        sys.stdout.flush()
        self._save_documentation(output)

        self._log_progress("COMPLETE", f"Documentation generated successfully at: {self.config.output_path}", 100)
        sys.stdout.flush()

        return {
            'status': 'success',
            'elements_count': len(self.elements),
            'output_path': str(self.config.output_path),
            'format': self.config.doc_type.value
        }

    def _scan_project(self):
        """Recursively scan project and analyze files"""
        print(f"📂 Scanning project: {self.config.project_path}")
        sys.stdout.flush()

        files_to_analyze = []

        # Collect all matching files
        for pattern in self.config.file_patterns:
            if self.config.recursive:
                files = list(self.config.project_path.rglob(pattern))
            else:
                files = list(self.config.project_path.glob(pattern))

            # Filter ignored patterns
            files = [f for f in files if not any(
                ignore in str(f) for ignore in self.config.ignore_patterns
            )]

            # Filter test files if include_tests is False
            if not self.config.include_tests:
                files = [f for f in files if not any(
                    test_pattern in f.name.lower() for test_pattern in ['test_', '_test.', 'tests.', '.test.', 'spec.', '.spec.']
                ) and 'test' not in f.parent.name.lower()]

            files_to_analyze.extend(files)

        total_files = len(files_to_analyze)
        print(f"📄 Found {total_files} files to analyze")
        sys.stdout.flush()

        # Analyze files with progress tracking
        analyzed_count = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_to_file = {
                executor.submit(self._analyze_file, file_path): file_path
                for file_path in files_to_analyze
            }

            for future in concurrent.futures.as_completed(future_to_file):
                file_path = future_to_file[future]
                analyzed_count += 1

                # Calculate progress (10-50% range for scanning phase)
                progress_percent = 10 + int((analyzed_count / total_files) * 40)

                try:
                    elements = future.result()
                    self.elements.extend(elements)
                    print(f"✓ Analyzed ({analyzed_count}/{total_files}): {file_path.name}")
                    sys.stdout.flush()

                    # Report progress for every file
                    self._log_progress(
                        "ANALYZING",
                        f"Analyzing file {analyzed_count}/{total_files}: {file_path.name}",
                        progress_percent
                    )
                    sys.stdout.flush()
                except Exception as e:
                    print(f"✗ Error analyzing {file_path}: {e}")
                    sys.stdout.flush()

    def _analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze a single file"""
        # Determine analyzer based on file extension
        ext = file_path.suffix.lower()

        elements = []
        if ext == '.py' and 'python' in self.analyzers and self.analyzers['python']:
            elements = self.analyzers['python'].analyze_file(file_path)
        elif ext == '.java' and 'java' in self.analyzers and self.analyzers['java']:
            elements = self.analyzers['java'].analyze_file(file_path)
        elif ext in ['.js', '.jsx', '.ts', '.tsx', '.mjs'] and 'javascript' in self.analyzers and self.analyzers['javascript']:
            elements = self.analyzers['javascript'].analyze_file(file_path)

        # Filter private members if include_private is False
        if not self.config.include_private and elements:
            filtered_elements = []
            for element in elements:
                # Check if element is private (starts with _ in Python, private/protected in Java/JS)
                is_private = (
                    element.name.startswith('_') and not element.name.startswith('__') or  # Python single underscore (not dunder)
                    'private' in element.modifiers or
                    'protected' in element.modifiers
                )

                if not is_private:
                    # Also filter children (methods of classes)
                    if element.children:
                        element.children = [
                            child for child in element.children
                            if not (child.name.startswith('_') and not child.name.startswith('__') or
                                    'private' in child.modifiers or
                                    'protected' in child.modifiers)
                        ]
                    filtered_elements.append(element)

            return filtered_elements

        return elements

    def _enhance_with_ai(self):
        """Enhance documentation using AI"""
        if not self.ai_client:
            return

        print(f"🤖 Enhancing documentation with AI ({self.config.ai_provider.value})")

        for element in self.elements:
            if not element.docstring:
                # Generate docstring using AI
                element.ai_description = self._generate_ai_description(element)

    def _generate_ai_description(self, element: CodeElement) -> str:
        """Generate AI-powered description for an element"""
        if not self.ai_client:
            return ""

        try:
            # Read source code context
            with open(element.file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                context = ''.join(lines[max(0, element.line_start-5):min(len(lines), element.line_end+5)])

            prompt = f"""Generate a professional documentation description for this {element.type} named '{element.name}'.

Context:
{context}

Provide a clear, concise description (2-3 sentences) explaining what this {element.type} does."""

            if self.config.ai_provider == AIProvider.OPENAI:
                # Use specified model or default to gpt-4o
                model = self.config.ai_model or 'gpt-4o'
                max_tokens = self.config.max_tokens or 500

                # Use streaming for real-time feedback
                print(f"🤖 Generating docs for {element.name}...", end=" ", flush=True)
                stream = self.ai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    stream=True
                )

                collected_content = []
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        collected_content.append(content)
                        print(content, end="", flush=True)

                print()  # New line after streaming
                sys.stdout.flush()
                return ''.join(collected_content).strip()

            elif self.config.ai_provider == AIProvider.CLAUDE:
                # Use specified model or default to claude-3-5-sonnet-20241022
                model = self.config.ai_model or 'claude-3-5-sonnet-20241022'
                max_tokens = self.config.max_tokens or 500

                # Use streaming for real-time feedback
                print(f"🤖 Generating docs for {element.name}...", end=" ", flush=True)
                collected_content = []

                with self.ai_client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    for text in stream.text_stream:
                        collected_content.append(text)
                        print(text, end="", flush=True)

                print()  # New line after streaming
                sys.stdout.flush()
                return ''.join(collected_content).strip()

        except Exception as e:
            print(f"AI generation error for {element.name}: {e}")

        return ""

    def _generate_output(self) -> Dict[str, str]:
        """Generate documentation in the specified format"""
        output = {}

        if self.config.doc_type == DocumentationType.MARKDOWN:
            output = self._generate_markdown()
        elif self.config.doc_type in [DocumentationType.SPHINX_RST, DocumentationType.SPHINX_HTML, DocumentationType.SPHINX_PDF]:
            # Generate Sphinx RST files
            output = self._generate_sphinx()

            # Also generate markdown files for all formats
            print("📝 Generating markdown documentation...")
            sys.stdout.flush()
            markdown_output = self._generate_markdown()
            output.update(markdown_output)
        elif self.config.doc_type == DocumentationType.MKDOCS:
            output = self._generate_mkdocs()

        return output

    def _generate_markdown(self) -> Dict[str, str]:
        """Generate Markdown documentation"""
        docs = {}

        # Remove emoji for Sphinx formats (LaTeX doesn't support them)
        # sphinxemoji only works in RST files, not in Markdown->LaTeX conversion
        is_sphinx = self.config.doc_type in [DocumentationType.SPHINX_RST, DocumentationType.SPHINX_HTML, DocumentationType.SPHINX_PDF]

        stats_emoji = "" if is_sphinx else "📊 "
        docs_emoji = "" if is_sphinx else "📚 "

        readme = f"""# {self.config.project_name} - Documentation

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## {stats_emoji}Project Statistics

- **Total Files Analyzed**: {len(set(e.file_path for e in self.elements))}
- **Total Classes**: {len([e for e in self.elements if e.type == 'class'])}
- **Total Functions**: {len([e for e in self.elements if e.type == 'function'])}
- **Total Methods**: {len([e for e in self.elements if e.type == 'method'])}

## {docs_emoji}Documentation

"""

        # Group elements by file
        elements_by_file = {}
        for element in self.elements:
            if element.file_path not in elements_by_file:
                elements_by_file[element.file_path] = []
            elements_by_file[element.file_path].append(element)

        # Generate documentation for each file
        for file_path, file_elements in elements_by_file.items():
            rel_path = file_path.relative_to(self.config.project_path)
            file_doc = self._generate_file_markdown(rel_path, file_elements)

            doc_filename = str(rel_path).replace(os.sep, '_').replace('.', '_') + '.md'
            docs[doc_filename] = file_doc

            readme += f"- [{rel_path}](docs/{doc_filename})\n"

        docs['README.md'] = readme

        # Generate API index
        docs['API_INDEX.md'] = self._generate_api_index()

        # Generate detailed API Reference with full documentation
        docs['API_REFERENCE.md'] = self._generate_detailed_api_reference()

        # Generate class diagram if requested
        if self.config.generate_diagrams:
            docs['CLASS_DIAGRAM.md'] = self._generate_class_diagram()

        return docs

    def _generate_file_markdown(self, file_path: Path, elements: List[CodeElement]) -> str:
        """Generate markdown for a single file"""
        doc = f"""# {file_path}

## Overview

This file contains {len(elements)} documented elements.

"""

        # Classes
        classes = [e for e in elements if e.type == 'class']
        if classes:
            doc += "## Classes\n\n"
            for cls in classes:
                doc += self._format_class_markdown(cls)

        # Functions
        functions = [e for e in elements if e.type == 'function']
        if functions:
            doc += "## Functions\n\n"
            for func in functions:
                doc += self._format_function_markdown(func)

        return doc

    def _format_class_markdown(self, cls: CodeElement) -> str:
        """Format class documentation in markdown"""
        doc = f"""### {cls.name}

"""
        if cls.docstring:
            doc += f"{cls.docstring}\n\n"
        elif cls.ai_description:
            doc += f"{cls.ai_description}\n\n"

        if cls.decorators:
            doc += f"**Decorators**: {', '.join(cls.decorators)}\n\n"

        if 'bases' in cls.attributes and cls.attributes['bases']:
            doc += f"**Inherits from**: {', '.join(cls.attributes['bases'])}\n\n"

        # Methods
        methods = [e for e in cls.children if e.type == 'method']
        if methods:
            doc += "#### Methods\n\n"
            for method in methods:
                doc += self._format_method_markdown(method)

        return doc

    def _format_function_markdown(self, func: CodeElement) -> str:
        """Format function documentation in markdown"""
        # Generate signature
        params = ', '.join([p['name'] for p in func.parameters])
        signature = f"{func.name}({params})"

        doc = f"""### {signature}

"""
        if func.docstring:
            doc += f"{func.docstring}\n\n"
        elif func.ai_description:
            doc += f"{func.ai_description}\n\n"

        if func.parameters:
            doc += "**Parameters:**\n"
            for param in func.parameters:
                param_type = f": {param['type']}" if param.get('type') else ""
                doc += f"- `{param['name']}{param_type}`\n"
            doc += "\n"

        if func.return_type:
            doc += f"**Returns:** `{func.return_type}`\n\n"

        return doc

    def _format_method_markdown(self, method: CodeElement) -> str:
        """Format method documentation in markdown"""
        params = ', '.join([p['name'] for p in method.parameters])
        doc = f"""##### {method.name}({params})

"""
        if method.docstring:
            doc += f"{method.docstring}\n\n"
        elif method.ai_description:
            doc += f"{method.ai_description}\n\n"

        return doc

    def _generate_detailed_api_reference(self, format='markdown') -> str:
        """Generate comprehensive API reference documentation with full details"""
        if format == 'rst':
            return self._generate_detailed_api_reference_rst()
        else:
            return self._generate_detailed_api_reference_md()

    def _generate_detailed_api_reference_md(self) -> str:
        """Generate detailed API reference in Markdown format"""
        api_ref = f"""# {self.config.project_name} - API Reference

Complete API documentation with classes, methods, and functions.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        # Group elements by file
        elements_by_file = {}
        for element in self.elements:
            if element.file_path not in elements_by_file:
                elements_by_file[element.file_path] = []
            elements_by_file[element.file_path].append(element)

        # Generate documentation for each file
        for file_path in sorted(elements_by_file.keys()):
            file_elements = elements_by_file[file_path]
            rel_path = file_path.relative_to(self.config.project_path)

            api_ref += f"\n## Module: `{rel_path}`\n\n"
            api_ref += f"**File Path:** `{rel_path}`\n\n"

            # Document all classes
            classes = [e for e in file_elements if e.type == 'class']
            if classes:
                api_ref += "### Classes\n\n"
                for cls in sorted(classes, key=lambda x: x.name):
                    api_ref += f"#### `{cls.name}`\n\n"

                    # Description
                    if cls.docstring:
                        api_ref += f"{cls.docstring}\n\n"
                    elif cls.ai_description:
                        api_ref += f"{cls.ai_description}\n\n"

                    # Inheritance
                    if 'bases' in cls.attributes and cls.attributes['bases']:
                        api_ref += f"**Inherits from:** `{', '.join(cls.attributes['bases'])}`\n\n"

                    # Decorators
                    if cls.decorators:
                        api_ref += f"**Decorators:** `{', '.join(cls.decorators)}`\n\n"

                    # Methods
                    methods = [e for e in cls.children if e.type == 'method']
                    if methods:
                        api_ref += "**Methods:**\n\n"
                        for method in sorted(methods, key=lambda x: x.name):
                            params_str = ', '.join([
                                f"{p['name']}" + (f": {p['type']}" if p.get('type') else "")
                                for p in method.parameters
                            ])
                            signature = f"{method.name}({params_str})"
                            if method.return_type:
                                signature += f" → {method.return_type}"

                            api_ref += f"##### `{signature}`\n\n"

                            if method.docstring:
                                api_ref += f"{method.docstring}\n\n"
                            elif method.ai_description:
                                api_ref += f"{method.ai_description}\n\n"

                            # Parameters details
                            if method.parameters:
                                api_ref += "**Parameters:**\n\n"
                                for param in method.parameters:
                                    param_type = f" ({param['type']})" if param.get('type') else ""
                                    api_ref += f"- `{param['name']}`{param_type}\n"
                                api_ref += "\n"

                            # Return type
                            if method.return_type:
                                api_ref += f"**Returns:** `{method.return_type}`\n\n"

                            # Modifiers
                            if method.modifiers:
                                api_ref += f"**Modifiers:** `{', '.join(method.modifiers)}`\n\n"

                            # Decorators
                            if method.decorators:
                                api_ref += f"**Decorators:** `{', '.join(method.decorators)}`\n\n"

                            api_ref += "---\n\n"

                    api_ref += "\n"

            # Document all functions
            functions = [e for e in file_elements if e.type == 'function']
            if functions:
                api_ref += "### Functions\n\n"
                for func in sorted(functions, key=lambda x: x.name):
                    params_str = ', '.join([
                        f"{p['name']}" + (f": {p['type']}" if p.get('type') else "")
                        for p in func.parameters
                    ])
                    signature = f"{func.name}({params_str})"
                    if func.return_type:
                        signature += f" → {func.return_type}"

                    api_ref += f"#### `{signature}`\n\n"

                    if func.docstring:
                        api_ref += f"{func.docstring}\n\n"
                    elif func.ai_description:
                        api_ref += f"{func.ai_description}\n\n"

                    # Parameters details
                    if func.parameters:
                        api_ref += "**Parameters:**\n\n"
                        for param in func.parameters:
                            param_type = f" ({param['type']})" if param.get('type') else ""
                            api_ref += f"- `{param['name']}`{param_type}\n"
                        api_ref += "\n"

                    # Return type
                    if func.return_type:
                        api_ref += f"**Returns:** `{func.return_type}`\n\n"

                    # Modifiers
                    if func.modifiers:
                        api_ref += f"**Modifiers:** `{', '.join(func.modifiers)}`\n\n"

                    # Decorators
                    if func.decorators:
                        api_ref += f"**Decorators:** `{', '.join(func.decorators)}`\n\n"

                    api_ref += "---\n\n"

            api_ref += "\n\\newpage\n\n"  # Page break for PDF generation

        return api_ref

    def _generate_detailed_api_reference_rst(self) -> str:
        """Generate detailed API reference in RST format"""
        api_ref = f"""{self.config.project_name} - API Reference
{'=' * (len(self.config.project_name) + 15)}

Complete API documentation with classes, methods, and functions.

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        # Group elements by file
        elements_by_file = {}
        for element in self.elements:
            if element.file_path not in elements_by_file:
                elements_by_file[element.file_path] = []
            elements_by_file[element.file_path].append(element)

        # Generate documentation for each file
        for file_path in sorted(elements_by_file.keys()):
            file_elements = elements_by_file[file_path]
            rel_path = file_path.relative_to(self.config.project_path)

            api_ref += f"\nModule: ``{rel_path}``\n"
            api_ref += "-" * (len(str(rel_path)) + 10) + "\n\n"
            api_ref += f"**File Path:** ``{rel_path}``\n\n"

            # Document all classes
            classes = [e for e in file_elements if e.type == 'class']
            if classes:
                api_ref += "Classes\n~~~~~~~\n\n"
                for cls in sorted(classes, key=lambda x: x.name):
                    api_ref += f"``{cls.name}``\n"
                    api_ref += "^" * (len(cls.name) + 4) + "\n\n"

                    # Description
                    if cls.docstring:
                        api_ref += f"{cls.docstring}\n\n"
                    elif cls.ai_description:
                        api_ref += f"{cls.ai_description}\n\n"

                    # Inheritance
                    if 'bases' in cls.attributes and cls.attributes['bases']:
                        api_ref += f"**Inherits from:** ``{', '.join(cls.attributes['bases'])}``\n\n"

                    # Methods
                    methods = [e for e in cls.children if e.type == 'method']
                    if methods:
                        api_ref += "**Methods:**\n\n"
                        for method in sorted(methods, key=lambda x: x.name):
                            params_str = ', '.join([
                                f"{p['name']}" + (f": {p['type']}" if p.get('type') else "")
                                for p in method.parameters
                            ])
                            signature = f"{method.name}({params_str})"
                            if method.return_type:
                                signature += f" → {method.return_type}"

                            api_ref += f"``{signature}``\n\n"

                            if method.docstring:
                                api_ref += f"   {method.docstring}\n\n"
                            elif method.ai_description:
                                api_ref += f"   {method.ai_description}\n\n"

                    api_ref += "\n"

            # Document all functions
            functions = [e for e in file_elements if e.type == 'function']
            if functions:
                api_ref += "Functions\n~~~~~~~~~\n\n"
                for func in sorted(functions, key=lambda x: x.name):
                    params_str = ', '.join([
                        f"{p['name']}" + (f": {p['type']}" if p.get('type') else "")
                        for p in func.parameters
                    ])
                    signature = f"{func.name}({params_str})"
                    if func.return_type:
                        signature += f" → {func.return_type}"

                    api_ref += f"``{signature}``\n\n"

                    if func.docstring:
                        api_ref += f"{func.docstring}\n\n"
                    elif func.ai_description:
                        api_ref += f"{func.ai_description}\n\n"

            api_ref += "\n.. raw:: latex\n\n   \\newpage\n\n"  # Page break for PDF

        return api_ref

    def _generate_api_index(self, format='markdown') -> str:
        """Generate API index in markdown or RST format"""
        if format == 'rst':
            # RST format
            index = """API Index
=========

Classes
-------

.. list-table::
   :header-rows: 1
   :widths: 25 30 15 30

   * - Name
     - File
     - Methods
     - Description
"""
            classes = [e for e in self.elements if e.type == 'class']
            for cls in sorted(classes, key=lambda x: x.name):
                rel_path = cls.file_path.relative_to(self.config.project_path)
                methods_count = len([e for e in cls.children if e.type == 'method'])
                description = (cls.docstring or cls.ai_description or "").split('\n')[0][:100]
                index += f"   * - {cls.name}\n     - {rel_path}\n     - {methods_count}\n     - {description}\n"

            index += """
Functions
---------

.. list-table::
   :header-rows: 1
   :widths: 30 30 20 20

   * - Name
     - File
     - Parameters
     - Returns
"""
            functions = [e for e in self.elements if e.type == 'function']
            for func in sorted(functions, key=lambda x: x.name):
                rel_path = func.file_path.relative_to(self.config.project_path)
                params = len(func.parameters)
                returns = func.return_type or "None"
                index += f"   * - {func.name}\n     - {rel_path}\n     - {params}\n     - {returns}\n"

            return index
        else:
            # Markdown format
            index = """# API Index

## Classes

| Name | File | Methods | Description |
|------|------|---------|-------------|
"""

            classes = [e for e in self.elements if e.type == 'class']
            for cls in sorted(classes, key=lambda x: x.name):
                rel_path = cls.file_path.relative_to(self.config.project_path)
                methods_count = len([e for e in cls.children if e.type == 'method'])
                description = (cls.docstring or cls.ai_description or "").split('\n')[0][:100]
                index += f"| {cls.name} | {rel_path} | {methods_count} | {description} |\n"

            index += """

## Functions

| Name | File | Parameters | Returns |
|------|------|------------|---------|
"""

            functions = [e for e in self.elements if e.type == 'function']
            for func in sorted(functions, key=lambda x: x.name):
                rel_path = func.file_path.relative_to(self.config.project_path)
                params = len(func.parameters)
                returns = func.return_type or "None"
                index += f"| {func.name} | {rel_path} | {params} | {returns} |\n"

            return index

    def _generate_class_diagram(self, format='markdown') -> str:
        """Generate Mermaid class diagram in markdown or RST format with AI-generated description"""
        classes = [e for e in self.elements if e.type == 'class']

        # Generate AI description if AI is configured
        ai_description = ""
        if self.config.ai_provider and self.config.ai_provider != AIProvider.NONE:
            ai_description = self._generate_ai_diagram_description(classes)

        if format == 'rst':
            # RST format
            diagram = """Class Diagram
=============

"""
            # Add AI-generated description
            if ai_description:
                diagram += f"{ai_description}\n\n"

            diagram += """.. mermaid::

   classDiagram
"""

            for cls in classes:
                # Add class
                diagram += f"      class {cls.name} {{\n"

                # Add methods
                for method in cls.children[:5]:  # Limit to 5 methods for readability
                    params = ', '.join([p['name'] for p in method.parameters])
                    diagram += f"         +{method.name}({params})\n"

                if len(cls.children) > 5:
                    diagram += f"         ... +{len(cls.children) - 5} more methods\n"

                diagram += "      }\n"

                # Add inheritance relationships
                if 'bases' in cls.attributes:
                    for base in cls.attributes.get('bases', []):
                        if base != 'object':
                            diagram += f"      {base} <|-- {cls.name}\n"

            return diagram
        else:
            # Markdown format
            diagram = """# Class Diagram

"""
            # Add AI-generated description
            if ai_description:
                diagram += f"{ai_description}\n\n"

            diagram += """```mermaid
classDiagram
"""

            for cls in classes:
                # Add class
                diagram += f"    class {cls.name} {{\n"

                # Add methods
                for method in cls.children[:5]:  # Limit to 5 methods for readability
                    params = ', '.join([p['name'] for p in method.parameters])
                    diagram += f"        +{method.name}({params})\n"

                if len(cls.children) > 5:
                    diagram += f"        ... +{len(cls.children) - 5} more methods\n"

                diagram += "    }\n"

                # Add inheritance relationships
                if 'bases' in cls.attributes:
                    for base in cls.attributes.get('bases', []):
                        if base != 'object':
                            diagram += f"    {base} <|-- {cls.name}\n"

            diagram += "```\n"
            return diagram

    def _generate_ai_diagram_description(self, classes: list) -> str:
        """Generate AI-powered description of the class structure and relationships"""
        if not self.ai_client:
            return ""

        try:
            # Prepare class information for AI
            class_info = []
            for cls in classes[:10]:  # Limit to 10 classes for token efficiency
                info = {
                    'name': cls.name,
                    'docstring': cls.docstring or "",
                    'methods': [m.name for m in cls.children[:5]],
                    'bases': cls.attributes.get('bases', []) if 'bases' in cls.attributes else []
                }
                class_info.append(info)

            # Create prompt for AI
            prompt = f"""Analyze this class structure and provide a concise architectural overview (max 3 paragraphs):

Classes:
{chr(10).join([f"- {c['name']}: {c['docstring'][:100] if c['docstring'] else 'No description'}" for c in class_info])}

Describe:
1. The overall architecture and design patterns used
2. Key responsibilities and relationships between classes
3. Main components and their interactions

Keep the description clear, professional, and focused on helping developers understand the codebase structure."""

            # Call AI based on provider
            description = ""
            if self.config.ai_provider == AIProvider.OPENAI:
                model = self.config.ai_model or 'gpt-4o'
                response = self.ai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                description = response.choices[0].message.content.strip()

            elif self.config.ai_provider == AIProvider.CLAUDE:
                model = self.config.ai_model or 'claude-3-5-sonnet-20241022'
                response = self.ai_client.messages.create(
                    model=model,
                    max_tokens=500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )
                description = response.content[0].text.strip()

            if description:
                print("✅ Generated AI architectural overview for class diagram")
                sys.stdout.flush()
                return f"## Architecture Overview\n\n{description}"

            return ""

        except Exception as e:
            print(f"⚠️  Could not generate AI diagram description: {e}")
            sys.stdout.flush()
            return ""

    def _generate_tutorials(self) -> Dict[str, str]:
        """Generate AI-powered tutorials using multi-agent system"""
        try:
            # Import tutorial generator
            tutorial_gen_path = Path(__file__).parent / 'tutorial_generator.py'
            if not tutorial_gen_path.exists():
                print("⚠️  Tutorial generator not found, skipping tutorial generation")
                return {}

            # Import dynamically
            import importlib.util
            spec = importlib.util.spec_from_file_location("tutorial_generator", tutorial_gen_path)
            tutorial_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tutorial_module)

            # Create config dict
            config = {
                'ai_provider': self.config.ai_provider.value,
                'ai_model': self.config.ai_model,
                'max_tokens': self.config.max_tokens,
                'target_language': self.config.target_language or 'en'
            }

            # Initialize tutorial generator
            tutorial_gen = tutorial_module.TutorialGenerator(
                project_path=self.config.project_path,
                elements=self.elements,
                config=config,
                ai_client=self.ai_client
            )

            # Generate tutorials with selected mode
            mode = self.config.tutorial_mode or 'both'
            print(f"📚 Generating AI-powered documentation with multi-agent system (mode: {mode})...")
            tutorial_docs = tutorial_gen.generate_complete_documentation(mode=mode)

            # Copy icon files to output directory
            if hasattr(tutorial_gen, 'project_context') and tutorial_gen.project_context.icon_files:
                self._copy_icon_files(tutorial_gen.project_context.icon_files)

            print(f"✅ Generated {len(tutorial_docs)} documents")
            return tutorial_docs

        except Exception as e:
            print(f"⚠️  Error generating tutorials: {e}")
            return {}

    def _copy_icon_files(self, icon_files: Dict[str, str]):
        """Copy project icon files to documentation output directory"""
        import shutil

        # Create icons directory in output
        icons_dir = self.config.output_path / 'icons'
        icons_dir.mkdir(parents=True, exist_ok=True)

        copied_count = 0
        for icon_name, icon_rel_path in icon_files.items():
            try:
                source_icon = self.config.project_path / icon_rel_path
                if source_icon.exists():
                    dest_icon = icons_dir / source_icon.name
                    shutil.copy2(source_icon, dest_icon)
                    copied_count += 1
            except Exception as e:
                print(f"⚠️  Could not copy icon {icon_rel_path}: {e}")

        if copied_count > 0:
            print(f"✅ Copied {copied_count} icon files to docs/icons/")

    def _generate_sphinx(self) -> Dict[str, str]:
        """Generate Sphinx documentation"""
        docs = {}

        # Create conf.py
        docs['conf.py'] = self._generate_sphinx_conf()

        # Check tutorial mode
        mode = self.config.tutorial_mode or 'both'

        # Generate API documentation only if mode allows it
        if mode in ['api_only', 'both']:
            # Create RST files for each module
            modules = {}
            for element in self.elements:
                module_name = element.file_path.stem
                if module_name not in modules:
                    modules[module_name] = []
                modules[module_name].append(element)

            # Filter out modules with minimal content (empty Java/JS files) and test files
            significant_modules = {}
            for module_name, module_elements in modules.items():
                # Skip test files if not included
                if not self.config.include_tests:
                    if any(skip in module_name.lower() for skip in ['test_', 'comprehensive_test']):
                        continue

                # Skip utility scripts if not included
                if not self.config.include_utility_scripts:
                    utility_patterns = ['setup', 'build', 'install', 'deploy', 'create_', 'generate_', 'make_']
                    if any(pattern in module_name.lower() for pattern in utility_patterns):
                        continue

                # Keep module if it has at least one element with docstring or substantial content
                if any(elem.docstring or elem.ai_description or elem.children for elem in module_elements):
                    significant_modules[module_name] = module_elements
                    docs[f"{module_name}.rst"] = self._generate_sphinx_module(module_name, module_elements)

            # Create index.rst with list of significant modules only
            docs['index.rst'] = self._generate_sphinx_index(list(significant_modules.keys()))

            # Generate RST versions of API index, API Reference, and class diagram for Sphinx
            docs['API_INDEX.rst'] = self._generate_api_index(format='rst')
            docs['API_REFERENCE.rst'] = self._generate_detailed_api_reference(format='rst')
            if self.config.generate_diagrams:
                docs['CLASS_DIAGRAM.rst'] = self._generate_class_diagram(format='rst')
        else:
            # tutorials_only mode: create minimal index without API docs
            docs['index.rst'] = self._generate_sphinx_index([])

        # Generate Makefile
        docs['Makefile'] = self._generate_sphinx_makefile()

        return docs

    def _generate_sphinx_conf(self) -> str:
        """Generate Sphinx configuration"""
        # Validate and fallback to installed theme
        installed_themes = [
            'alabaster', 'sphinx_rtd_theme', 'pydata_sphinx_theme',
            'furo', 'piccolo_theme', 'sphinx_book_theme',
            'sphinx_material', 'sphinx_pdj_theme', 'insipid_sphinx_theme'
        ]

        # Map theme package names to their actual theme names in conf.py
        theme_name_mapping = {
            'insipid_sphinx_theme': 'insipid',  # insipid_sphinx_theme uses 'insipid' as theme name
            'sphinx_rtd_theme': 'sphinx_rtd_theme',
            'pydata_sphinx_theme': 'pydata_sphinx_theme',
            'furo': 'furo',
            'piccolo_theme': 'piccolo_theme',
            'sphinx_book_theme': 'sphinx_book_theme',
            'sphinx_material': 'sphinx_material',
            'sphinx_pdj_theme': 'sphinx_pdj_theme',
            'alabaster': 'alabaster',
        }

        # Check if requested theme is installed
        theme = self.config.sphinx_theme
        if theme not in installed_themes:
            print(f"⚠️  Theme '{theme}' not in installed themes. Using 'sphinx_rtd_theme' instead.")
            print(f"   Available themes: {', '.join(installed_themes)}")
            sys.stdout.flush()
            theme = 'sphinx_rtd_theme'

        # Get the actual theme name to use in conf.py
        actual_theme_name = theme_name_mapping.get(theme, theme)

        return f"""# Sphinx configuration file
import os
import sys
sys.path.insert(0, os.path.abspath('{self.config.project_path}'))

project = '{self.config.project_name}'
copyright = '{datetime.now().year}, {self.config.project_name}'
author = '{self.config.project_name} Team'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'myst_parser',  # Support for Markdown files
    'sphinxemoji.sphinxemoji',  # Emoji support in HTML and PDF
]

# MyST parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

source_suffix = {{
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = '{actual_theme_name}'
html_static_path = ['_static']

# Alabaster theme options for better path wrapping
html_theme_options = {{
    'code_font_size': '0.8em',
    'page_width': '1200px',
}}

# PDF output with XeLaTeX for Unicode emoji support
latex_engine = 'xelatex'

latex_elements = {{
    'preamble': r'''
\\usepackage{{fontspec}}
\\setmainfont{{DejaVu Sans}}
\\setmonofont[Scale=0.85]{{DejaVu Sans Mono}}
\\usepackage{{seqsplit}}
\\usepackage{{xurl}}
\\usepackage{{breakurl}}
\\usepackage{{ragged2e}}
\\usepackage{{microtype}}
\\sloppy
\\emergencystretch=3em
\\tolerance=9999
\\hbadness=9999
% Wrap long paths and code with smaller font
\\renewcommand{{\\path}}[1]{{{{\\small\\seqsplit{{#1}}}}}}
\\renewcommand{{\\sphinxcode}}[1]{{{{\\small\\seqsplit{{#1}}}}}}
\\renewcommand{{\\sphinxupquote}}[1]{{{{\\small\\seqsplit{{#1}}}}}}
% Force verbatim to use smaller font and break long lines
\\makeatletter
\\renewcommand{{\\sphinxVerbatim}}[1][1]{{%
  \\par\\setbox\\sphinxcodeblockbox=\\hbox{{%
    \\fvset{{fontsize=\\small,baselinestretch=1}}%
    \\begin{{OriginalVerbatim}}[#1,commandchars=\\\\\\{{\\}}]%
}}
% Allow breaking in table of contents
\\renewcommand{{\\@pnumwidth}}{{2em}}
\\renewcommand{{\\@tocrmarg}}{{3em}}
\\makeatother
''',
    'fontpkg': r'\\usepackage{{fontspec}}',
    'printindex': r'\\footnotesize\\raggedright\\printindex',
    'tableofcontents': r'\\sphinxtableofcontents',
    'maxlistdepth': '10',
    'fncychap': '',
}}

# LaTeX document settings
latex_use_parts = False
latex_show_pagerefs = True
latex_show_urls = 'footnote'

latex_documents = [
    ('index', '{self.config.project_name}.tex', '{self.config.project_name} Documentation',
     '{self.config.project_name} Team', 'manual', True),
]
"""

    def _generate_sphinx_index(self, modules: List[str]) -> str:
        """Generate Sphinx index.rst with actual module list and tutorials"""
        # Translation dictionary for UI strings
        translations = {
            'en': {
                'tutorials': 'Tutorials:',
                'api_docs': 'API Documentation:',
                'indices': 'Indices and tables'
            },
            'fr': {
                'tutorials': 'Tutoriels :',
                'api_docs': 'Documentation API :',
                'indices': 'Indices et tables'
            },
            'it': {
                'tutorials': 'Tutorial:',
                'api_docs': 'Documentazione API:',
                'indices': 'Indici e tabelle'
            },
            'es': {
                'tutorials': 'Tutoriales:',
                'api_docs': 'Documentación API:',
                'indices': 'Índices y tablas'
            },
            'de': {
                'tutorials': 'Anleitungen:',
                'api_docs': 'API-Dokumentation:',
                'indices': 'Indizes und Tabellen'
            }
        }

        # Get target language or default to English
        lang = self.config.target_language or 'en'
        if lang not in translations:
            lang = 'en'

        t = translations[lang]

        # Generate toctree entries for all modules
        module_entries = '\n   '.join(sorted(modules))

        # Check for tutorial markdown files that will be generated by AI
        tutorial_files = [
            'TUTORIAL',
            'QUICK_START',
            'EXAMPLES',
            'TROUBLESHOOTING',
            'tutorial_beginner',
            'tutorial_intermediate',
            'tutorial_advanced',
            'API_REFERENCE'
        ]

        tutorial_entries = '\n   '.join(tutorial_files)

        return f"""{self.config.project_name} Documentation
{'=' * (len(self.config.project_name) + 14)}

.. toctree::
   :maxdepth: 2
   :caption: {t['tutorials']}

   {tutorial_entries}

.. toctree::
   :maxdepth: 2
   :caption: {t['api_docs']}

   {module_entries}

{t['indices']}
{'=' * len(t['indices'])}

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

    def _generate_sphinx_module(self, module_name: str, elements: List[CodeElement]) -> str:
        """Generate Sphinx RST for a module"""
        doc = f"""{module_name}
{'=' * len(module_name)}

.. automodule:: {module_name}
   :members:
   :undoc-members:
   :show-inheritance:

"""

        # Add custom documentation for elements
        for element in elements:
            if element.type == 'class':
                doc += f"""
.. autoclass:: {element.name}
   :members:
   :special-members: __init__
"""

        return doc

    def _generate_sphinx_makefile(self) -> str:
        """Generate Sphinx Makefile"""
        return """# Makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help Makefile

help:
\t@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

html:
\t@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

pdf:
\t@$(SPHINXBUILD) -M latexpdf "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
\t@$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

%: Makefile
\t@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
"""

    def _generate_mkdocs(self) -> Dict[str, str]:
        """Generate MkDocs documentation"""
        docs = {}

        # Generate mkdocs.yml
        docs['mkdocs.yml'] = f"""site_name: {self.config.project_name}
site_description: Documentation for {self.config.project_name}
repo_url: https://github.com/yourusername/{self.config.project_name}

theme:
  name: material
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - search.highlight
    - search.share

plugins:
  - search
  - mkdocstrings

nav:
  - Home: index.md
  - API Reference: api.md
  - Examples: examples.md
"""

        # Generate markdown files
        docs['docs/index.md'] = self._generate_markdown()['README.md']
        docs['docs/api.md'] = self._generate_api_index()

        return docs

    def _save_documentation(self, output: Dict[str, str]):
        """Save generated documentation to disk with language separation"""
        # Detect if we have multi-language documentation
        detected_lang = self._detect_documentation_language()
        target_lang = self.config.target_language

        # Determine if we need language separation
        has_multiple_languages = (detected_lang and target_lang and
                                 detected_lang != target_lang and
                                 target_lang.lower() != 'none')

        if has_multiple_languages:
            # Create language-specific directories
            print(f"📁 Creating multi-language documentation structure...")
            sys.stdout.flush()

            # Save original language docs
            lang_path_original = self.config.output_path / detected_lang
            lang_path_original.mkdir(parents=True, exist_ok=True)

            # Save translated language docs
            lang_path_target = self.config.output_path / target_lang
            lang_path_target.mkdir(parents=True, exist_ok=True)

            # Create language index
            self._create_language_index(detected_lang, target_lang)

            # Save files to appropriate language directory
            for filename, content in output.items():
                # Determine if content is in original or target language
                # Tutorial files go to target language if translated
                if target_lang and any(kw in filename.upper() for kw in ['TUTORIAL', 'QUICK_START', 'EXAMPLES']):
                    file_path = lang_path_target / filename
                else:
                    file_path = lang_path_original / filename

                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

            print(f"✅ Documentation saved in {detected_lang}/ and {target_lang}/ directories")
            sys.stdout.flush()
        else:
            # Single language - save normally
            self.config.output_path.mkdir(parents=True, exist_ok=True)

            for filename, content in output.items():
                file_path = self.config.output_path / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

        # If Sphinx HTML/PDF requested, build it
        if self.config.doc_type == DocumentationType.SPHINX_HTML:
            self._build_sphinx_html()
        elif self.config.doc_type == DocumentationType.SPHINX_PDF:
            self._build_sphinx_pdf()
            # Also generate separate PDFs for tutorial and API
            self._build_separate_pdfs()

    def _find_sphinx_build(self):
        """Find sphinx-build executable in PATH or virtual environments"""
        # Try direct command first
        try:
            result = subprocess.run(['which', 'sphinx-build'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        # Try common venv locations
        venv_paths = [
            Path.cwd() / '.venv' / 'bin' / 'sphinx-build',
            Path.cwd() / 'venv' / 'bin' / 'sphinx-build',
            Path.home() / '.local' / 'bin' / 'sphinx-build',
        ]

        for path in venv_paths:
            if path.exists():
                return str(path)

        # Use Python module execution as fallback
        return [sys.executable, '-m', 'sphinx']

    def _find_xelatex(self):
        """Find xelatex executable in PATH or common LaTeX installation locations"""
        # Try direct command first
        try:
            result = subprocess.run(['which', 'xelatex'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        # Try common LaTeX installation locations (macOS, Linux, Windows)
        latex_paths = [
            Path('/Library/TeX/texbin/xelatex'),  # macOS TeX Live
            Path('/usr/local/texlive/2024/bin/universal-darwin/xelatex'),  # macOS TeX Live alt
            Path('/usr/local/texlive/2023/bin/universal-darwin/xelatex'),  # macOS TeX Live 2023
            Path('/usr/bin/xelatex'),  # Linux
            Path('/usr/local/bin/xelatex'),  # Linux alt
            Path.home() / 'texlive' / '2024' / 'bin' / 'xelatex',  # User installation
        ]

        for path in latex_paths:
            if path.exists():
                return str(path)

        return None

    def _find_pdflatex(self):
        """Find pdflatex executable in PATH or common LaTeX installation locations"""
        # Try direct command first
        try:
            result = subprocess.run(['which', 'pdflatex'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        # Try common LaTeX installation locations (macOS, Linux, Windows)
        latex_paths = [
            Path('/Library/TeX/texbin/pdflatex'),  # macOS TeX Live
            Path('/usr/local/texlive/2024/bin/universal-darwin/pdflatex'),  # macOS TeX Live alt
            Path('/usr/local/texlive/2023/bin/universal-darwin/pdflatex'),  # macOS TeX Live 2023
            Path('/usr/bin/pdflatex'),  # Linux
            Path('/usr/local/bin/pdflatex'),  # Linux alt
            Path.home() / 'texlive' / '2024' / 'bin' / 'pdflatex',  # User installation
        ]

        for path in latex_paths:
            if path.exists():
                return str(path)

        return None

    def _build_sphinx_html(self):
        """Build Sphinx HTML documentation"""
        try:
            sphinx_cmd = self._find_sphinx_build()
            if isinstance(sphinx_cmd, list):
                # Python module execution
                cmd = sphinx_cmd + ['-b', 'html', str(self.config.output_path), str(self.config.output_path / '_build' / 'html')]
            else:
                # Direct executable
                cmd = [sphinx_cmd, '-b', 'html', str(self.config.output_path), str(self.config.output_path / '_build' / 'html')]

            subprocess.run(cmd, check=True, capture_output=True)
            print("✅ Sphinx HTML documentation built successfully")
        except FileNotFoundError:
            print("⚠️  Sphinx not installed. Install with: pip install sphinx")
            print("📝 Sphinx RST files generated successfully. Run sphinx-build manually to generate HTML.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building Sphinx HTML: {e}")

    def _build_sphinx_pdf(self):
        """Build Sphinx PDF documentation using XeLaTeX for emoji support"""
        try:
            # Find sphinx-build
            sphinx_cmd = self._find_sphinx_build()
            if isinstance(sphinx_cmd, list):
                # Python module execution
                cmd = sphinx_cmd + ['-b', 'latex', str(self.config.output_path), str(self.config.output_path / '_build' / 'latex')]
            else:
                # Direct executable
                cmd = [sphinx_cmd, '-b', 'latex', str(self.config.output_path), str(self.config.output_path / '_build' / 'latex')]

            subprocess.run(cmd, check=True, capture_output=True)

            # Try XeLaTeX first (supports Unicode emoji), fallback to pdflatex
            xelatex_cmd = self._find_xelatex()
            latex_cmd = xelatex_cmd if xelatex_cmd else self._find_pdflatex()
            latex_name = "xelatex" if xelatex_cmd else "pdflatex"

            if not latex_cmd:
                print("⚠️  XeLaTeX/pdflatex not installed. Install LaTeX distribution (e.g., TeX Live, MiKTeX)")
                print("📝 LaTeX files generated successfully. Run xelatex manually to generate PDF.")
                return

            # Build PDF from LaTeX
            latex_dir = self.config.output_path / '_build' / 'latex'
            pdf_output = latex_dir / f'{self.config.project_name}.pdf'
            print(f"🔨 Running {latex_name} on {self.config.project_name}.tex...")

            # Run latex twice for proper references
            for run in range(2):
                result = subprocess.run(
                    [latex_cmd, '-interaction=nonstopmode', f'{self.config.project_name}.tex'],
                    cwd=latex_dir,
                    capture_output=True
                )

            # Check if PDF was actually created (LaTeX may return non-zero even on success)
            if pdf_output.exists():
                print(f"✅ Sphinx PDF documentation built successfully using {latex_name} ({pdf_output.stat().st_size // 1024} KB)")
            else:
                raise subprocess.CalledProcessError(result.returncode, latex_cmd)
        except FileNotFoundError as e:
            tool_name = "sphinx" if "sphinx" in str(e) else "xelatex/pdflatex"
            if tool_name == "sphinx":
                print("⚠️  Sphinx not installed. Install with: pip install sphinx")
                print("📝 Sphinx RST files generated successfully. Run sphinx-build manually to generate PDF.")
            else:
                print("⚠️  XeLaTeX/pdflatex not installed. Install LaTeX distribution (e.g., TeX Live, MiKTeX)")
                print("📝 LaTeX files generated successfully. Run xelatex manually to generate PDF.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error building Sphinx PDF: {e}")
            print(f"💡 Tip: Make sure DejaVu Sans font is installed for emoji support")

    def _create_language_index(self, original_lang: str, target_lang: str):
        """Create an index page for multi-language documentation"""
        language_names = {
            'en': 'English',
            'it': 'Italian',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German'
        }

        index_content = f"""# {self.config.project_name} - Documentation

## Available Languages

- [{language_names.get(original_lang, original_lang)}]({original_lang}/README.md) - Original documentation
- [{language_names.get(target_lang, target_lang)}]({target_lang}/README.md) - Translated documentation

---

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        index_path = self.config.output_path / 'README.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)

        print(f"✅ Created multi-language index at {index_path}")
        sys.stdout.flush()

    def _find_pandoc(self) -> Optional[str]:
        """Find pandoc executable with extended PATH search"""
        # Try direct command first
        if shutil.which('pandoc'):
            return shutil.which('pandoc')

        # Try common paths
        common_paths = [
            '/usr/local/bin/pandoc',
            '/opt/homebrew/bin/pandoc',
            '/usr/bin/pandoc',
            str(Path.home() / '.local' / 'bin' / 'pandoc')
        ]

        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path

        return None

    def _build_separate_pdfs(self):
        """Generate separate PDFs for tutorial/manual and API documentation"""
        try:
            print("\n📚 Generating separate PDFs for Tutorial and API...")
            sys.stdout.flush()

            # Check if pandoc and pdflatex are available with extended PATH search
            pandoc_cmd = self._find_pandoc()
            if not pandoc_cmd:
                print("⚠️  pandoc not found. Install with: brew install pandoc (macOS)")
                print(f"   Searched paths: /usr/local/bin, /opt/homebrew/bin, /usr/bin")
                return

            print(f"✅ Found pandoc at: {pandoc_cmd}")
            sys.stdout.flush()

            latex_cmd = self._find_xelatex() or self._find_pdflatex()
            if not latex_cmd:
                print("⚠️  LaTeX not found. Install TeX Live or MiKTeX")
                return

            # Define tutorial and API file groups
            tutorial_files = []
            api_files = []

            # Scan for markdown files - exclude API files from tutorials
            for file_path in self.config.output_path.rglob('*.md'):
                filename = file_path.name.upper()
                filepath_str = str(file_path).upper()

                # Exclude Python source file documentation (contains .PY in path or filename)
                if '.PY' in filename or '/_' in str(file_path) or filepath_str.endswith('_PY.MD'):
                    api_files.append(file_path)
                    continue

                # Only add to tutorial if it's explicitly a tutorial file
                if any(kw in filename for kw in ['TUTORIAL', 'QUICK_START', 'EXAMPLE', 'TROUBLESHOOTING', 'BEGINNER', 'INTERMEDIATE', 'ADVANCED']):
                    # Make sure it's not an API file
                    if not any(kw in filename for kw in ['API', 'REFERENCE', 'INDEX', 'CLASS_DIAGRAM']):
                        # Extra check: exclude if it looks like source code documentation
                        if not ('_PY' in filename or 'GENERATOR' in filename):
                            tutorial_files.append(file_path)
                        else:
                            api_files.append(file_path)
                # Add to API files
                elif any(kw in filename for kw in ['API', 'REFERENCE', 'INDEX']):
                    api_files.append(file_path)

            # Also scan RST files - exclude API and test files
            for file_path in self.config.output_path.rglob('*.rst'):
                filename = file_path.name.upper()
                # Only add to tutorial if it's explicitly a tutorial file
                if any(kw in filename for kw in ['TUTORIAL', 'QUICK_START', 'EXAMPLE', 'TROUBLESHOOTING', 'BEGINNER', 'INTERMEDIATE', 'ADVANCED']):
                    # Make sure it's not an API file
                    if not any(kw in filename for kw in ['API', 'REFERENCE', 'INDEX', 'CLASS_DIAGRAM']):
                        tutorial_files.append(file_path)
                # Add to API files
                elif any(kw in filename for kw in ['API_REFERENCE', 'API_INDEX', 'CLASS_DIAGRAM']):
                    api_files.append(file_path)

            # Sort tutorial files in logical order
            def tutorial_sort_key(path):
                filename = path.name.upper()
                if 'QUICK_START' in filename:
                    return 0
                elif 'BEGINNER' in filename:
                    return 1
                elif 'INTERMEDIATE' in filename:
                    return 2
                elif 'ADVANCED' in filename:
                    return 3
                elif 'EXAMPLE' in filename:
                    return 4
                elif 'TROUBLESHOOTING' in filename:
                    return 5
                else:
                    return 6

            tutorial_files.sort(key=tutorial_sort_key)

            # Sort API files in logical order
            def api_sort_key(path):
                filename = path.name.upper()
                if 'API_INDEX' in filename:
                    return 0
                elif 'CLASS_DIAGRAM' in filename:
                    return 1
                elif 'API_REFERENCE' in filename:
                    return 2
                else:
                    return 3

            api_files.sort(key=api_sort_key)

            # Track success
            success_count = 0

            # Generate tutorial PDF
            if tutorial_files:
                tutorial_pdf = self.config.output_path / 'tutorial_manual.pdf'
                self._generate_combined_pdf(
                    tutorial_files,
                    tutorial_pdf,
                    f"{self.config.project_name} - Tutorial & Manual",
                    pandoc_cmd
                )
                if tutorial_pdf.exists():
                    success_count += 1

            # Generate API PDF
            if api_files:
                api_pdf = self.config.output_path / 'api_reference.pdf'
                self._generate_combined_pdf(
                    api_files,
                    api_pdf,
                    f"{self.config.project_name} - API Reference",
                    pandoc_cmd
                )
                if api_pdf.exists():
                    success_count += 1

            if success_count > 0:
                print(f"✅ Generated {success_count} separate PDF(s) successfully")
            else:
                print("⚠️  No PDFs were generated successfully")
            sys.stdout.flush()

        except Exception as e:
            print(f"⚠️  Error generating separate PDFs: {e}")
            sys.stdout.flush()

    def _generate_combined_pdf(self, markdown_files: List[Path], output_pdf: Path, title: str, pandoc_cmd: str):
        """Generate a single PDF from multiple markdown files"""
        try:
            # Escape special characters for YAML (different from LaTeX escaping)
            # In YAML, we need to escape quotes and backslashes properly
            yaml_title = title.replace('\\', '\\\\').replace('"', '\\"')

            # Escape LaTeX special characters in title for content (not YAML)
            escaped_title = title.replace('&', '\\&').replace('_', '\\_').replace('%', '\\%').replace('#', '\\#')

            # Create temporary combined markdown with proper YAML
            # Use date-only format to avoid YAML parsing issues with colons in time
            combined_content = f"---\ntitle: \"{yaml_title}\"\ndate: \"{datetime.now().strftime('%Y-%m-%d')}\"\n---\n\n"
            combined_content += f"# {title}\n\n"

            for md_file in sorted(markdown_files):
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Remove any existing YAML frontmatter from individual files
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            content = parts[2].strip()

                    # Extract title from first H1 heading in content, or use cleaned filename
                    chapter_title = None
                    for line in content.split('\n'):
                        if line.startswith('# '):
                            chapter_title = line[2:].strip()
                            break

                    # If no H1 found, create a clean title from filename
                    if not chapter_title:
                        # Clean up filename: remove file extensions from stem, replace underscores
                        clean_name = md_file.stem.replace('_py', '').replace('_md', '').replace('_rst', '')
                        chapter_title = clean_name.replace('_', ' ').title()

                    combined_content += f"\n\n# {chapter_title}\n\n"
                    combined_content += content
                    combined_content += "\n\n\\newpage\n\n"

            # Remove emojis and problematic Unicode characters for LaTeX compatibility
            combined_content = self._remove_emojis(combined_content)

            # Clean problematic characters for LaTeX (Windows paths, escape sequences)
            import re
            # Replace all backslashes with forward slashes EXCEPT \newpage (which we inserted)
            # This prevents issues with Windows paths (C:\), escape sequences (\n, \t), etc.
            combined_content = combined_content.replace('\\newpage', '___NEWPAGE___')  # Protect \newpage
            combined_content = combined_content.replace('\\', '/')  # Replace all backslashes
            combined_content = combined_content.replace('___NEWPAGE___', '\\newpage')  # Restore \newpage

            # Write temporary file
            temp_md = self.config.output_path / '_temp_combined.md'
            with open(temp_md, 'w', encoding='utf-8') as f:
                f.write(combined_content)

            # Convert to PDF
            print(f"📄 Generating {output_pdf.name}...")
            sys.stdout.flush()

            latex_engine = 'xelatex' if self._find_xelatex() else 'pdflatex'

            # Ensure absolute paths for pandoc
            abs_temp_md = temp_md.resolve()
            abs_output_pdf = output_pdf.resolve()

            # Prepare environment with extended PATH for LaTeX
            env = os.environ.copy()
            latex_paths = [
                '/Library/TeX/texbin',  # macOS TeX Live
                '/usr/local/texlive/2024/bin/universal-darwin',  # macOS TeX Live alt
                '/usr/local/texlive/2023/bin/universal-darwin',  # macOS TeX Live 2023
                '/usr/bin',  # Linux
                '/usr/local/bin',  # Linux alt
            ]
            # Add LaTeX paths to PATH if not already present
            current_path = env.get('PATH', '')
            for latex_path in latex_paths:
                if latex_path not in current_path:
                    current_path = f"{latex_path}:{current_path}"
            env['PATH'] = current_path

            result = subprocess.run([
                pandoc_cmd,
                str(abs_temp_md),
                '-o', str(abs_output_pdf),
                f'--pdf-engine={latex_engine}',
                '-V', 'geometry:margin=1in',
                '-V', 'documentclass=report',
                '-V', f'title={escaped_title}',
                '--metadata', f'date={datetime.now().strftime("%Y-%m-%d")}',
                '--toc',
                '--number-sections'
            ], capture_output=True, text=True, env=env)

            # Clean up temp file
            temp_md.unlink()

            # Check if PDF was actually created (LaTeX may return non-zero even on success)
            if output_pdf.exists():
                print(f"✅ Generated {output_pdf.name} ({output_pdf.stat().st_size // 1024} KB)")
                sys.stdout.flush()
            else:
                # Print detailed error information
                print(f"❌ Error generating {output_pdf.name}: Command returned exit code {result.returncode}")
                if result.stderr:
                    print(f"   stderr: {result.stderr[:500]}")  # First 500 chars of error
                if result.stdout:
                    print(f"   stdout: {result.stdout[:500]}")
                sys.stdout.flush()

        except subprocess.CalledProcessError as e:
            print(f"❌ Error generating {output_pdf.name}: {e}")
            sys.stdout.flush()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()

    def watch_for_changes(self):
        """Watch for file changes and auto-regenerate documentation"""
        if not self.config.auto_update:
            return

        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler

            class DocUpdateHandler(FileSystemEventHandler):
                def __init__(self, generator):
                    self.generator = generator
                    self.last_update = datetime.now()

                def on_modified(self, event):
                    if event.is_directory:
                        return

                    # Debounce - wait at least 2 seconds between updates
                    if (datetime.now() - self.last_update).seconds < 2:
                        return

                    # Check if file matches patterns
                    file_path = Path(event.src_path)
                    if any(file_path.match(pattern) for pattern in self.generator.config.file_patterns):
                        print(f"🔄 File changed: {file_path}, regenerating documentation...")
                        self.generator.generate_documentation()
                        self.last_update = datetime.now()

            handler = DocUpdateHandler(self)
            observer = Observer()
            observer.schedule(handler, str(self.config.project_path), recursive=True)
            observer.start()

            print(f"👁️ Watching for changes in {self.config.project_path}")
            print("Press Ctrl+C to stop...")

            try:
                while True:
                    pass
            except KeyboardInterrupt:
                observer.stop()
            observer.join()

        except ImportError:
            print("Watchdog not installed. Install with: pip install watchdog")


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(description="DocuGenius - Universal Documentation Generator")
    parser.add_argument('project_path', help='Path to project')
    parser.add_argument('--output', '-o', help='Output directory', default='docs')
    parser.add_argument('--format', '-f', choices=[t.value for t in DocumentationType],
                       default='markdown', help='Output format')
    parser.add_argument('--ai', choices=[p.value for p in AIProvider],
                       default='none', help='AI provider for enhanced documentation')
    parser.add_argument('--ai-key', help='API key for AI provider')
    parser.add_argument('--ai-model', help='AI model to use (e.g., gpt-4.1, gpt-4.1-mini, claude-sonnet-4-5, claude-opus-4-1, claude-sonnet-4)')
    parser.add_argument('--max-tokens', type=int, default=500, help='Maximum tokens for AI responses')
    parser.add_argument('--watch', action='store_true', help='Watch for changes')
    parser.add_argument('--sphinx-theme', default='sphinx_rtd_theme', help='Sphinx theme')
    parser.add_argument('--include-private', action='store_true', help='Include private members')
    parser.add_argument('--include-tests', action='store_true', help='Include test files')
    parser.add_argument('--include-utility-scripts', action='store_true', default=True, help='Include utility scripts (setup, build, etc.)')
    parser.add_argument('--target-lang', help='Target language for translation (en, it, es, fr, de)')
    parser.add_argument('--tutorial-mode', choices=['tutorials_only', 'api_only', 'both'],
                       default='both', help='AI documentation mode: tutorials only, API only, or both')

    args = parser.parse_args()

    # Create configuration
    config = ProjectConfig(
        project_path=Path(args.project_path).resolve(),
        project_name=Path(args.project_path).name,
        output_path=Path(args.output).resolve(),
        doc_type=DocumentationType(args.format),
        ai_provider=AIProvider(args.ai),
        ai_api_key=args.ai_key,
        ai_model=args.ai_model,
        max_tokens=args.max_tokens,
        include_private=args.include_private,
        include_tests=args.include_tests,
        include_utility_scripts=args.include_utility_scripts,
        sphinx_theme=args.sphinx_theme,
        auto_update=args.watch,
        target_language=args.target_lang,
        tutorial_mode=args.tutorial_mode
    )

    # Create generator and run
    generator = UniversalDocumentationGenerator(config)
    result = generator.generate_documentation()

    print(json.dumps(result, indent=2))

    # Start watching if requested
    if args.watch:
        generator.watch_for_changes()


if __name__ == '__main__':
    main()