#!/usr/bin/env python3
"""
Project Context Analyzer
Analyzes project structure, README, code to build context for tutorial generation
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ProjectContext:
    """Complete project context for tutorial generation"""
    project_name: str
    project_type: str  # 'qgis_plugin', 'plugin', 'standalone', 'library', 'cli', 'web_app'
    description: str
    installation_method: str
    dependencies: List[str]
    main_features: List[str]
    ui_elements: Dict[str, List[str]]  # {dialog_name: [buttons, tabs, fields]}
    entry_points: List[str]  # Main classes/files
    readme_content: str
    existing_docs: Dict[str, str]  # {doc_type: content}
    code_structure: Dict[str, Any]
    icon_files: Dict[str, str]  # {icon_name: relative_path}

    def to_dict(self) -> Dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class ProjectContextAnalyzer:
    """Analyzes project to extract context for accurate tutorial generation"""

    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.context = None

    def analyze(self) -> ProjectContext:
        """Perform complete project analysis"""
        print(f"\n{'='*60}")
        print(f"🔍 ANALYZING PROJECT: {self.project_path.name}")
        print(f"{'='*60}\n")

        # 1. Detect project type
        project_type = self._detect_project_type()
        print(f"✅ Project type: {project_type}")

        # 2. Read README
        readme_content = self._read_readme()
        print(f"✅ README found: {len(readme_content)} chars")

        # 3. Extract project name and description
        project_name, description = self._extract_project_info(readme_content)
        print(f"✅ Project name: {project_name}")

        # 4. Find installation method
        installation = self._extract_installation_method(readme_content, project_type)
        print(f"✅ Installation: {installation[:50]}...")

        # 5. Extract dependencies
        dependencies = self._extract_dependencies(readme_content)
        print(f"✅ Dependencies: {len(dependencies)} found")

        # 6. Extract main features
        features = self._extract_features(readme_content)
        print(f"✅ Features: {len(features)} found")

        # 7. Analyze UI elements (dialogs, buttons, tabs)
        ui_elements = self._analyze_ui_elements()
        print(f"✅ UI elements: {len(ui_elements)} dialogs found")

        # 8. Find entry points
        entry_points = self._find_entry_points(project_type)
        print(f"✅ Entry points: {len(entry_points)} found")

        # 9. Read existing documentation
        existing_docs = self._read_existing_docs()
        print(f"✅ Existing docs: {len(existing_docs)} files")

        # 10. Analyze code structure
        code_structure = self._analyze_code_structure()
        print(f"✅ Code structure analyzed")

        # 11. Collect all icon files
        icon_files = self._collect_icon_files()
        print(f"✅ Icon files: {len(icon_files)} found")

        self.context = ProjectContext(
            project_name=project_name,
            project_type=project_type,
            description=description,
            installation_method=installation,
            dependencies=dependencies,
            main_features=features,
            ui_elements=ui_elements,
            entry_points=entry_points,
            readme_content=readme_content[:5000],  # First 5000 chars
            existing_docs=existing_docs,
            code_structure=code_structure,
            icon_files=icon_files
        )

        print(f"\n{'='*60}")
        print(f"✅ PROJECT ANALYSIS COMPLETE")
        print(f"{'='*60}\n")

        return self.context

    def _detect_project_type(self) -> str:
        """Detect project type from structure"""
        # Check for QGIS plugin
        if (self.project_path / 'metadata.txt').exists():
            return 'qgis_plugin'

        # Check for other plugin types
        if (self.project_path / 'plugin.xml').exists():
            return 'plugin'

        # Check for web app
        if any((self.project_path / f).exists() for f in ['app.py', 'wsgi.py', 'manage.py']):
            return 'web_app'

        # Check for CLI
        if (self.project_path / 'setup.py').exists() or (self.project_path / 'pyproject.toml').exists():
            # Check for entry_points
            setup_py = self.project_path / 'setup.py'
            if setup_py.exists():
                content = setup_py.read_text(errors='ignore')
                if 'console_scripts' in content or 'entry_points' in content:
                    return 'cli'
            return 'library'

        # Check for standalone
        if list(self.project_path.glob('*.py')):
            return 'standalone'

        return 'unknown'

    def _read_readme(self) -> str:
        """Read README file"""
        for readme_name in ['README.md', 'README.rst', 'README.txt', 'README']:
            readme_path = self.project_path / readme_name
            if readme_path.exists():
                try:
                    return readme_path.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue
        return ""

    def _extract_project_info(self, readme: str) -> Tuple[str, str]:
        """Extract project name and description from README"""
        lines = readme.split('\n')

        # Try to find project name from first heading
        project_name = self.project_path.name
        for line in lines[:10]:
            # Match markdown heading
            if match := re.match(r'^#+ (.+)', line):
                name = match.group(1).strip()
                # Remove badges, images
                name = re.sub(r'!\[.*?\].*?\)', '', name)
                name = re.sub(r'\[.*?\].*?\)', '', name)
                project_name = name.strip()
                break

        # Extract description (first paragraph after heading)
        description = ""
        in_content = False
        for line in lines:
            if line.startswith('#'):
                in_content = True
                continue
            if in_content and line.strip() and not line.startswith('![') and not line.startswith('[!['):
                description = line.strip()
                break

        return project_name, description

    def _extract_installation_method(self, readme: str, project_type: str) -> str:
        """Extract installation instructions from README"""
        # Look for installation section
        lines = readme.split('\n')
        in_install_section = False
        install_lines = []

        for i, line in enumerate(lines):
            if re.match(r'##+ .*install', line, re.IGNORECASE):
                in_install_section = True
                continue

            if in_install_section:
                if line.startswith('##'):
                    break
                install_lines.append(line)

        installation = '\n'.join(install_lines[:20]).strip()  # First 20 lines

        if not installation and project_type == 'qgis_plugin':
            installation = "Install via QGIS Plugin Manager or from ZIP file"

        return installation or "See README for installation instructions"

    def _extract_dependencies(self, readme: str) -> List[str]:
        """Extract dependencies from README"""
        deps = []
        lines = readme.split('\n')

        for i, line in enumerate(lines):
            if re.match(r'##+ .*depend', line, re.IGNORECASE):
                # Read next 20 lines
                for dep_line in lines[i+1:i+21]:
                    if dep_line.startswith('##'):
                        break
                    # Extract from list items
                    if match := re.match(r'[*\-]\s+(.+)', dep_line):
                        dep = match.group(1).strip()
                        # Clean up
                        dep = re.sub(r'\[.*?\]\(.*?\)', '', dep)
                        dep = re.sub(r'\*\*', '', dep)
                        if dep:
                            deps.append(dep)

        return deps[:15]  # Limit to 15

    def _extract_features(self, readme: str) -> List[str]:
        """Extract main features from README"""
        features = []
        lines = readme.split('\n')

        for i, line in enumerate(lines):
            if re.match(r'##+ .*feature', line, re.IGNORECASE):
                # Read next 30 lines
                for feat_line in lines[i+1:i+31]:
                    if feat_line.startswith('##'):
                        break
                    # Extract from list items
                    if match := re.match(r'[*\-]\s+(.+)', feat_line):
                        feat = match.group(1).strip()
                        # Clean up
                        feat = re.sub(r'\[.*?\]\(.*?\)', '', feat)
                        feat = re.sub(r'\*\*', '', feat)
                        if feat and len(feat) > 10:
                            features.append(feat)

        return features[:20]  # Limit to 20

    def _analyze_ui_elements(self) -> Dict[str, List[str]]:
        """Analyze UI elements (dialogs, buttons, tabs) from code and extract icons"""
        ui_elements = {}

        # Find UI files (PyQt/PySide dialogs, forms)
        ui_patterns = ['*_dialog.py', '*Dialog.py', '*_ui.py', '*UI.py', '*_form.py']
        ui_files = []
        for pattern in ui_patterns:
            ui_files.extend(self.project_path.rglob(pattern))

        # Also check .ui files (Qt Designer)
        ui_files.extend(self.project_path.rglob('*.ui'))

        # Build icon map (icon path -> icon file)
        icon_map = self._build_icon_map()

        for ui_file in ui_files[:30]:  # Limit to 30 files
            try:
                content = ui_file.read_text(encoding='utf-8', errors='ignore')
                dialog_name = ui_file.stem
                elements = []

                # Find buttons with icons
                # Pattern: QPushButton with setIcon or <iconset> in .ui files
                button_matches = re.findall(r'<widget class="QPushButton".*?<property name="text">.*?<string>(.+?)</string>.*?(?:<iconset.*?<normaloff>(.+?)</normaloff>)?', content, re.DOTALL)
                for btn_text, btn_icon in button_matches[:10]:
                    if btn_icon:
                        # Use icon path with special marker [ICON:path]
                        icon_ref = self._resolve_icon_path(btn_icon, icon_map)
                        elements.append(f"Button: [ICON:{icon_ref}] {btn_text}")
                    else:
                        elements.append(f"Button: {btn_text}")

                # Fallback: simple button text extraction
                if not button_matches:
                    buttons = re.findall(r'QPushButton.*?["\'](.+?)["\']', content)
                    elements.extend([f"Button: {b}" for b in buttons[:10]])

                # Find tabs
                tabs = re.findall(r'QTabWidget.*?addTab.*?["\'](.+?)["\']', content)
                tabs += re.findall(r'<widget class="QWidget" name="(.+?)"', content)  # From .ui tab names
                elements.extend([f"Tab: {t}" for t in tabs[:10]])

                # Find input fields
                fields = re.findall(r'QLineEdit.*?setObjectName.*?["\'](.+?)["\']', content)
                fields += re.findall(r'QComboBox.*?setObjectName.*?["\'](.+?)["\']', content)
                elements.extend([f"Field: {f}" for f in fields[:10]])

                if elements:
                    ui_elements[dialog_name] = list(set(elements))[:20]  # Unique, limit 20
            except Exception:
                continue

        return ui_elements

    def _build_icon_map(self) -> Dict[str, str]:
        """Build a map of icon paths to recognize common icons"""
        icon_map = {}

        # Common icon directories
        icon_dirs = ['resources/icons', 'icons', 'resources', 'images']

        for icon_dir in icon_dirs:
            icon_path = self.project_path / icon_dir
            if icon_path.exists():
                for icon_file in icon_path.rglob('*.png'):
                    icon_name = icon_file.stem.lower()
                    icon_map[icon_name] = str(icon_file.relative_to(self.project_path))

                for icon_file in icon_path.rglob('*.svg'):
                    icon_name = icon_file.stem.lower()
                    icon_map[icon_name] = str(icon_file.relative_to(self.project_path))

        return icon_map

    def _resolve_icon_path(self, icon_path: str, icon_map: Dict[str, str]) -> str:
        """Resolve icon path from Qt resource notation to actual file path"""
        # Qt resource format: :/icons/save.png or resources/icons/save.png
        icon_path_clean = icon_path.replace(':', '').replace('//', '/').strip()

        # Extract just the filename
        icon_filename = icon_path_clean.split('/')[-1].replace('.png', '').replace('.svg', '')

        # Look up in icon_map
        if icon_filename.lower() in icon_map:
            return icon_map[icon_filename.lower()]

        # Try to find the file directly
        for icon_dir in ['resources/icons', 'icons', 'resources', 'images', 'gui/icons', 'assets/icons']:
            possible_path = self.project_path / icon_dir / (icon_filename + '.png')
            if possible_path.exists():
                return str(possible_path.relative_to(self.project_path))

            possible_path = self.project_path / icon_dir / (icon_filename + '.svg')
            if possible_path.exists():
                return str(possible_path.relative_to(self.project_path))

        # Fallback: return with emoji
        emoji = self._icon_to_emoji(icon_path, icon_map)
        return f"EMOJI:{emoji}"

    def _icon_to_emoji(self, icon_path: str, icon_map: Dict[str, str]) -> str:
        """Convert icon path/name to emoji representation"""
        # Extract icon name from path
        icon_name = icon_path.split('/')[-1].replace('.png', '').replace('.svg', '').lower()

        # Map common icon names to emojis
        emoji_map = {
            'save': '💾',
            'open': '📂',
            'folder': '📁',
            'new': '✨',
            'delete': '🗑️',
            'remove': '❌',
            'add': '➕',
            'edit': '✏️',
            'search': '🔍',
            'filter': '🔎',
            'zoom': '🔍',
            'zoomin': '🔍+',
            'zoomout': '🔍-',
            'print': '🖨️',
            'pdf': '📄',
            'export': '📤',
            'import': '📥',
            'upload': '⬆️',
            'download': '⬇️',
            'left': '⬅️',
            'right': '➡️',
            'up': '⬆️',
            'down': '⬇️',
            'arrow': '→',
            'info': 'ℹ️',
            'help': '❓',
            'settings': '⚙️',
            'config': '⚙️',
            'database': '🗄️',
            'table': '📊',
            'chart': '📈',
            'graph': '📊',
            'map': '🗺️',
            'gis': '🗺️',
            'location': '📍',
            'point': '📍',
            'excel': '📊',
            'doc': '📄',
            'image': '🖼️',
            'photo': '📷',
            'camera': '📷',
            'video': '🎥',
            'play': '▶️',
            'stop': '⏹️',
            'pause': '⏸️',
            'record': '⏺️',
            'close': '✖️',
            'cancel': '🚫',
            'ok': '✅',
            'check': '✓',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
        }

        # Try to find matching emoji
        for keyword, emoji in emoji_map.items():
            if keyword in icon_name:
                return emoji

        # Default: generic icon
        return '🔘'

    def _find_entry_points(self, project_type: str) -> List[str]:
        """Find main entry points (main classes/files)"""
        entry_points = []

        if project_type == 'qgis_plugin':
            # Look for main plugin class
            for py_file in self.project_path.glob('*.py'):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if 'QgisInterface' in content or 'iface' in content:
                        entry_points.append(str(py_file.name))
                except Exception:
                    continue

        # Look for main.py, __main__.py, app.py
        for main_file in ['__main__.py', 'main.py', 'app.py', 'cli.py']:
            if (self.project_path / main_file).exists():
                entry_points.append(main_file)

        # Look for classes with "Main" in name
        for py_file in list(self.project_path.glob('*.py'))[:20]:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                if re.search(r'class\s+Main\w*', content):
                    entry_points.append(str(py_file.name))
            except Exception:
                continue

        return list(set(entry_points))[:10]  # Unique, limit 10

    def _read_existing_docs(self) -> Dict[str, str]:
        """Read existing documentation files"""
        docs = {}

        # Check for docs directory
        docs_dirs = ['docs', 'doc', 'documentation']
        for docs_dir in docs_dirs:
            docs_path = self.project_path / docs_dir
            if docs_path.exists() and docs_path.is_dir():
                # Read key documentation files
                for doc_file in docs_path.rglob('*.md'):
                    try:
                        content = doc_file.read_text(encoding='utf-8', errors='ignore')
                        docs[doc_file.stem] = content[:2000]  # First 2000 chars
                        if len(docs) >= 5:  # Limit to 5 docs
                            break
                    except Exception:
                        continue
                break

        return docs

    def _analyze_code_structure(self) -> Dict[str, Any]:
        """Analyze code structure (modules, classes, functions)"""
        structure = {
            'modules': [],
            'main_classes': [],
            'total_python_files': 0
        }

        python_files = list(self.project_path.rglob('*.py'))[:50]  # Limit to 50
        structure['total_python_files'] = len(python_files)

        for py_file in python_files:
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')

                # Find classes
                classes = re.findall(r'class\s+(\w+)', content)
                if classes:
                    structure['main_classes'].extend(classes[:5])

                # Track modules
                relative_path = py_file.relative_to(self.project_path)
                structure['modules'].append(str(relative_path))
            except Exception:
                continue

        # Deduplicate and limit
        structure['main_classes'] = list(set(structure['main_classes']))[:20]
        structure['modules'] = structure['modules'][:30]

        return structure

    def _collect_icon_files(self) -> Dict[str, str]:
        """Collect all icon files in the project for copying to docs"""
        icon_files = {}

        # Scan common icon directories
        icon_dirs = ['resources/icons', 'icons', 'resources', 'images', 'gui/icons', 'assets/icons', 'assets']

        for icon_dir in icon_dirs:
            icon_path = self.project_path / icon_dir
            if icon_path.exists() and icon_path.is_dir():
                # Collect PNG files
                for icon_file in icon_path.rglob('*.png'):
                    rel_path = str(icon_file.relative_to(self.project_path))
                    icon_name = icon_file.stem.lower()
                    icon_files[icon_name] = rel_path

                # Collect SVG files
                for icon_file in icon_path.rglob('*.svg'):
                    rel_path = str(icon_file.relative_to(self.project_path))
                    icon_name = icon_file.stem.lower()
                    if icon_name not in icon_files:  # Prefer PNG if both exist
                        icon_files[icon_name] = rel_path

        return icon_files

    def save_context(self, output_path: Path):
        """Save analyzed context to JSON file"""
        if not self.context:
            raise ValueError("No context to save. Run analyze() first.")

        output_path.write_text(self.context.to_json(), encoding='utf-8')
        print(f"✅ Context saved to: {output_path}")


if __name__ == '__main__':
    # Test with PyArchInit
    pyarchinit_path = Path("/Users/enzo/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/pyarchinit/")

    analyzer = ProjectContextAnalyzer(pyarchinit_path)
    context = analyzer.analyze()

    print("\n" + "="*60)
    print("PROJECT CONTEXT SUMMARY")
    print("="*60)
    print(f"Name: {context.project_name}")
    print(f"Type: {context.project_type}")
    print(f"Description: {context.description}")
    print(f"Features: {len(context.main_features)}")
    print(f"UI Elements: {len(context.ui_elements)} dialogs")
    print(f"Dependencies: {len(context.dependencies)}")
    print("\nUI Elements:")
    for dialog, elements in list(context.ui_elements.items())[:3]:
        print(f"  {dialog}: {len(elements)} elements")
        for elem in elements[:5]:
            print(f"    - {elem}")