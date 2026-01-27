# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Make local extension modules under _ext/ importable
import os
import sys
sys.path.insert(0, os.path.abspath('_ext'))

project = 'firefly_client'
copyright = '2026, Caltech/IPAC Firefly Developers'
author = 'Caltech/IPAC Firefly Developers'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_automodapi.automodapi',
    'myst_parser',
    'nbsphinx',
    'script_pages', # custom extension for auto-generating RST files for examples/*.py scripts
]

templates_path = ['_templates']
exclude_patterns = [
    '_build', 'Thumbs.db', '.DS_Store',
    # exclude any docs in subdirectories under usage/examples/ since they are
    # not included in any toctree and are for internal use only
    'usage/examples/*/**'
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_static_path = ['_static']
html_js_files = ["custom-icon.js"]

html_last_updated_fmt = ''

# See https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/layout.html
html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/Caltech-IPAC/firefly_client",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/firefly-client",
            "icon": "fa-custom fa-pypi",
        },
    ],
    "footer_start": ["copyright", "last-updated"],
    "footer_end": ["sphinx-version", "theme-version"],
}


# -- Options for extensions -------------------------------------------------
myst_heading_anchors = 3

# nbsphinx configuration: render notebooks and Python scripts
# Do not execute notebooks during docs build; use stored outputs if present.
nbsphinx_execute = 'never'

# Allow build to continue even if some notebooks error (useful for demos).
nbsphinx_allow_errors = True

# Ensure Pygments syntax highlighting for Jupyter code cells.
nbsphinx_codecell_lexer = 'ipython'

# Remove the .txt suffix that gets added to source files
html_sourcelink_suffix = ''
