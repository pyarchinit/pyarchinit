#!/usr/bin/env python3
"""
PyArchInit Documentation Builder

Cross-platform script to build HTML and PDF documentation.

Usage:
    python build_docs.py html          # Build HTML documentation
    python build_docs.py pdf           # Build PDF documentation (all languages)
    python build_docs.py pdf-it        # Build Italian PDF only
    python build_docs.py pdf-en        # Build English PDF only
    python build_docs.py clean         # Clean build directory
    python build_docs.py install       # Install dependencies

Requirements:
    - Python 3.8+
    - pip install sphinx myst-parser
    - For PDF: LaTeX installation (MacTeX on macOS, texlive on Linux)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
BUILD_DIR = SCRIPT_DIR / "_build"
SOURCE_DIR = SCRIPT_DIR

# Languages with Latin alphabet (work with pdflatex)
LANGUAGES = ['it', 'en', 'de', 'fr', 'es', 'ca']

LANGUAGE_NAMES = {
    'it': 'Italiano',
    'en': 'English',
    'de': 'Deutsch',
    'fr': 'Français',
    'es': 'Español',
    'ca': 'Català',
    'ar': 'العربية',  # Arabic requires xelatex
}


def run_command(cmd, cwd=None, capture=False):
    """Run a command and return success status."""
    print(f"  Running: {' '.join(str(c) for c in cmd)}")
    try:
        if capture:
            result = subprocess.run(cmd, cwd=cwd, check=True,
                                    capture_output=True, text=True)
            return True, result.stdout
        else:
            result = subprocess.run(cmd, cwd=cwd, check=True)
            return True, None
    except subprocess.CalledProcessError as e:
        print(f"  Error: {e}")
        if capture and e.stderr:
            print(f"  stderr: {e.stderr[:500]}")
        return False, None
    except FileNotFoundError:
        print(f"  Command not found: {cmd[0]}")
        return False, None


def check_sphinx_installed():
    """Check if Sphinx is installed."""
    try:
        import sphinx
        print(f"  Sphinx version: {sphinx.__version__}")
        return True
    except ImportError:
        print("  ERROR: Sphinx is not installed.")
        print("  Run: python build_docs.py install")
        return False


def check_latex_installed():
    """Check if LaTeX (xelatex) is installed."""
    if shutil.which('xelatex'):
        return True
    print("  WARNING: xelatex not found.")
    print("  Install LaTeX:")
    print("    macOS: brew install --cask mactex")
    print("    Ubuntu: sudo apt-get install texlive-xetex texlive-latex-extra")
    print("    Windows: Install MiKTeX from https://miktex.org/")
    return False


def install_dependencies():
    """Install Python dependencies for documentation building."""
    print("\n=== Installing dependencies ===")

    cmd = [sys.executable, '-m', 'pip', 'install',
           'sphinx', 'myst-parser']
    success, _ = run_command(cmd)

    if success:
        print("\nPython dependencies installed successfully!")

    print("\nFor PDF generation, you also need LaTeX:")
    print("  macOS: brew install --cask mactex")
    print("  Ubuntu: sudo apt-get install texlive-latex-recommended texlive-latex-extra latexmk")
    print("  Windows: Install MiKTeX from https://miktex.org/")


def clean_build():
    """Clean the build directory."""
    print("\n=== Cleaning build directory ===")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"  Removed: {BUILD_DIR}")
    print("  Done!")


def build_html():
    """Build HTML documentation."""
    print("\n=== Building HTML documentation ===")

    if not check_sphinx_installed():
        return False

    html_dir = BUILD_DIR / "html"
    html_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, '-m', 'sphinx',
        '-b', 'html',
        '-W', '--keep-going',  # Treat warnings as errors but continue
        str(SOURCE_DIR),
        str(html_dir)
    ]

    success, _ = run_command(cmd)

    if success:
        print(f"\nHTML documentation built successfully!")
        print(f"Open: file://{html_dir / 'index.html'}")
    return success


def copy_images_to_build():
    """Copy images to build folder for LaTeX compilation."""
    latex_dir = BUILD_DIR / "latex"

    # Copy language-specific images
    for lang in LANGUAGES:
        src_images = SOURCE_DIR / lang / "images"
        dst_images = latex_dir / lang / "images"
        if src_images.exists():
            dst_images.mkdir(parents=True, exist_ok=True)
            for img in src_images.rglob("*.png"):
                dst = dst_images / img.relative_to(src_images)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(img, dst)

        # Copy any loose images in language folder
        for img in (SOURCE_DIR / lang).glob("*.png"):
            shutil.copy2(img, latex_dir / lang / img.name)

    # Copy shared resources/icons
    icons_src = SOURCE_DIR.parent.parent / "resources" / "icons"
    if icons_src.exists():
        icons_dst = BUILD_DIR / "resources" / "icons"
        icons_dst.mkdir(parents=True, exist_ok=True)
        for icon in icons_src.glob("*.png"):
            shutil.copy2(icon, icons_dst / icon.name)

    print("  Images copied to build folder")


def build_pdf(language=None):
    """Build PDF documentation."""
    print("\n=== Building PDF documentation ===")

    if not check_sphinx_installed():
        return False

    if not check_latex_installed():
        print("\nContinuing anyway - will build LaTeX files...")

    languages = [language] if language else LANGUAGES

    latex_dir = BUILD_DIR / "latex"
    latex_dir.mkdir(parents=True, exist_ok=True)

    # Build LaTeX files
    print("\n--- Generating LaTeX files ---")
    cmd = [
        sys.executable, '-m', 'sphinx',
        '-b', 'latex',
        str(SOURCE_DIR),
        str(latex_dir)
    ]

    success, _ = run_command(cmd)
    if not success:
        print("Failed to generate LaTeX files")
        return False

    # Copy images to build folder
    print("\n--- Copying images ---")
    copy_images_to_build()

    # Build PDFs
    print("\n--- Compiling PDFs ---")
    results = {}

    for lang in languages:
        lang_name = LANGUAGE_NAMES.get(lang, lang)
        tex_file = f"PyArchInit_Tutorials_{lang.upper()}.tex"
        tex_path = latex_dir / tex_file

        if not tex_path.exists():
            print(f"  {lang_name}: .tex file not found, skipping")
            results[lang] = False
            continue

        print(f"\n  Building {lang_name} PDF...")

        # Use latexmk if available (handles multiple passes automatically)
        if shutil.which('latexmk'):
            cmd = ['latexmk', '-xelatex', '-interaction=nonstopmode',
                   '-halt-on-error', tex_file]
        else:
            # Run xelatex twice for references
            cmd = ['xelatex', '-interaction=nonstopmode', tex_file]
            run_command(cmd, cwd=latex_dir)

        success, _ = run_command(cmd, cwd=latex_dir)
        results[lang] = success

        if success:
            pdf_file = tex_path.with_suffix('.pdf')
            if pdf_file.exists():
                print(f"    Created: {pdf_file}")

    # Summary
    print(f"\n{'='*50}")
    print("Build Summary:")
    print(f"{'='*50}")
    for lang, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  {LANGUAGE_NAMES.get(lang, lang):20} [{status}]")

    return all(results.values())


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == 'help' or command == '-h' or command == '--help':
        print(__doc__)

    elif command == 'install':
        install_dependencies()

    elif command == 'clean':
        clean_build()

    elif command == 'html':
        success = build_html()
        sys.exit(0 if success else 1)

    elif command == 'pdf':
        success = build_pdf()
        sys.exit(0 if success else 1)

    elif command.startswith('pdf-'):
        lang = command.split('-')[1]
        if lang in LANGUAGES or lang == 'ar':
            success = build_pdf(lang)
            sys.exit(0 if success else 1)
        else:
            print(f"Unknown language: {lang}")
            print(f"Available: {', '.join(LANGUAGES)}")
            sys.exit(1)

    else:
        print(f"Unknown command: {command}")
        print("Use 'python build_docs.py help' for usage")
        sys.exit(1)


if __name__ == '__main__':
    main()
