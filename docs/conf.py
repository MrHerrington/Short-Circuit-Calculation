# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'ShortCircuitCalc'
copyright = '2024, Ilya Belov'  # noqa
author = 'Ilya Belov'
version = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.mathjax',
              'sphinx.ext.napoleon',
              'sphinx_simplepdf']

add_module_names = False  # Shorten names
# If True, the default argument values of functions will be not evaluated
# on generating document. It preserves them as is in the source code.
autodoc_preserve_defaults = True
templates_path = ['_templates']
# root_doc = "rst_files/shortcircuitcalc"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = "_static/images/logo.png"
html_favicon = '_static/images/logo.png'
html_theme_options = {
    'navigation_depth': 5
}

# -- Options for PDF output

simplepdf_vars = {
    'primary': '#FFA900',
    'cover-bg': 'transparent',
    'cover-overlay': 'url(images/cover.jpg) no-repeat center'
}

# sphinx apidoc -o docs/rst_files/ ./shortcircuitcalc #  for generating rst files
# /docs make html #  for generating html
# /docs make simplepdf #  for generating pdf
