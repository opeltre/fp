# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'fp'
copyright = '2024, Olivier Peltre'
author = 'Olivier Peltre'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

default_role = 'code'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinx.ext.napoleon',
]

add_module_names = False
autodoc_typehints = "description"


# -- Templates ----------------------------------------------------------------

templates_path = ['_templates']

# These not
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- HTML output ---------------------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']
html_css_files = [
    'css/custom.css',
]
