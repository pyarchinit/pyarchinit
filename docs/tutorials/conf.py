# Configuration file for the Sphinx documentation builder.
# PyArchInit Tutorial Documentation

import os
import sys
from datetime import datetime

# -- Project information -----------------------------------------------------
project = 'PyArchInit Tutorials'
copyright = f'{datetime.now().year}, PyArchInit Team'
author = 'PyArchInit Team'
version = '5.0'
release = '5.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
]

myst_enable_extensions = [
    'colon_fence',
    'deflist',
]

myst_heading_anchors = 3

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**/.DS_Store', 'README.md', '**/images/**']
language = 'en'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for LaTeX/PDF output --------------------------------------------
latex_engine = 'xelatex'

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '11pt',
    'fontpkg': r'''
\usepackage{fontspec}
\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Times New Roman}
\setsansfont{Helvetica}
\setmonofont{Menlo}
''',
    'preamble': r'''
\usepackage{longtable}
\usepackage{booktabs}
% Draft mode - shows filename boxes instead of loading images
% This allows builds to succeed even when image files are missing
\setkeys{Gin}{draft=true}
''',
    'figure_align': 'htbp',
    'extraclassoptions': 'openany,oneside',
    'fncychap': '',
}

latex_documents = [
    ('it/index', 'PyArchInit_Tutorials_IT.tex', 'PyArchInit Tutorial - Italiano',
     'PyArchInit Team', 'manual'),
    ('en/index', 'PyArchInit_Tutorials_EN.tex', 'PyArchInit Tutorials - English',
     'PyArchInit Team', 'manual'),
    ('de/index', 'PyArchInit_Tutorials_DE.tex', 'PyArchInit Tutorials - Deutsch',
     'PyArchInit Team', 'manual'),
    ('fr/index', 'PyArchInit_Tutorials_FR.tex', 'PyArchInit Tutorials - Francais',
     'PyArchInit Team', 'manual'),
    ('es/index', 'PyArchInit_Tutorials_ES.tex', 'PyArchInit Tutorials - Espanol',
     'PyArchInit Team', 'manual'),
    ('ca/index', 'PyArchInit_Tutorials_CA.tex', 'PyArchInit Tutorials - Catala',
     'PyArchInit Team', 'manual'),
]

latex_logo = None
latex_show_pagerefs = False
latex_show_urls = 'footnote'

# -- Options for EPUB output -------------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright
epub_show_urls = 'footnote'

# -- Additional settings -----------------------------------------------------
suppress_warnings = ['myst.header', 'ref.myst', 'toc.secnum', 'image.not_readable']
numfig = False
