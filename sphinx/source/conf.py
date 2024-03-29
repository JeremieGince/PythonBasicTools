# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import pprint
import sys
import shutil
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, basedir)
import pythonbasictools


_html_folders_formatted = {}
_allowed_special_methods = ["__init__", "__call__"]


def skip(app, what, name, obj, would_skip, options):
    if name in _allowed_special_methods:
        return False
    return would_skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
    app.connect('html-page-context', change_pathto)
    app.connect('build-finished', move_private_folders)


def change_pathto(app, pagename, templatename, context, doctree):
    """
    Replace pathto helper to change paths to folders with a leading underscore.
    """
    pathto = context.get('pathto')
    
    def gh_pathto(otheruri, *args, **kw):
        if otheruri.startswith('_'):
            otheruri_fmt = otheruri[1:]
            _html_folders_formatted[os.path.dirname(otheruri)] = os.path.dirname(otheruri_fmt)
        else:
            otheruri_fmt = otheruri
        return pathto(otheruri_fmt, *args, **kw)
    
    context['pathto'] = gh_pathto


def move_private_folders(app, e):
    """
    Remove leading underscore from folders in the output folder.
    """
    
    def join(dir):
        return os.path.join(app.builder.outdir, dir)
    
    for item in os.listdir(app.builder.outdir):
        if item.startswith('_') and os.path.isdir(join(item)) and item in _html_folders_formatted:
            shutil.move(join(item), join(item[1:]))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PythonBasicTools'
copyright = pythonbasictools.__copyright__.replace("Copyright ", "")
author = pythonbasictools.__author__
version = pythonbasictools.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.githubpages',
    'sphinxcontrib.bibtex',
    'sphinx_mdinclude',
]

bibtex_bibfiles = ['references.bib']

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'karma_sphinx_theme'
# html_theme = 'groundwork'
html_static_path = ['_static']
