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
release = '1.0.0'

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

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'insegel'
html_static_path = ['_static']

# -- Options for PDF output


# sphinx apidoc -o docs/rst_files/ ./shortcircuitcalc #  for generating rst files
# sphinx-build -b rinoh . _build/rinoh #  for generating pdf
