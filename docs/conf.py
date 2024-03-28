# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'firefly_client'
copyright = '2024, Caltech/IPAC Firefly Developers'
author = 'Caltech/IPAC Firefly Developers'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_automodapi.automodapi',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


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
