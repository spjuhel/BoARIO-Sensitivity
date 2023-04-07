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

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "pydata_sphinx_theme"

#html_theme_path = [sphinx_redactor_theme.get_html_theme_path()]
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

html_theme_options = {
	"show_prev_next": True,
	"show_scrolltop": True,

}

extensions = ['sphinx_collapse']
