# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'BoARIO Sensivity Report'
copyright = '2023, S. Juhel, V. Viguie'
author = 'S. Juhel, V. Viguie'
release = '0.1'
html_last_updated_fmt = "%b %d, %Y"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "pydata_sphinx_theme"

html_static_path = ["_static"]
html_css_files = ["css/custom.css"]
html_js_files = [
    'js/custom.js'
]


html_theme_options = {
	"show_prev_next": True,
}

extensions = ['sphinx_collapse']

master_doc = "index"

html_theme_options = {
	"navbar_end": ["navbar-icon-links", "last-updated", "theme-switcher"],
    "secondary_sidebar_items" : ["page-toc", "sourcelink"],
    "show_nav_level": 3
}
