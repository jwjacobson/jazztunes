# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

html_title = "Jazztunes Docs"
project = "jazztunes"
copyright = "2024–2025, Jeff Jacobson"
author = "Jeff Jacobson"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"


html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#1E3A8A",  # blue-900
        "color-brand-content": "#1D4ED8",  # blue-700
        "color-admonition-background": "#FFF7ED",  # orange-50
        "color-background-primary": "#E0E7FF",  # indigo-100
        "color-background-secondary": "#FFF7ED",  # orange-50
        "color-foreground-primary": "#374151",  # primary text
        "color-foreground-secondary": "#525252",  # secondary text
        "color-inline-code": "#E0E7FF",  # indigo-100
        "color-link": "#1E3A8A",  # blue-900
        "color-link--hover": "#1D4ED8",  # blue-700
        "color-sidebar-background": "#C7D2FE",  # indigo-200
        "color-sidebar-link": "#1E3A8A",  # blue-900
        "color-sidebar-link--hover": "#1D4ED8",  # blue-700
        "color-sidebar-heading": "#1E3A8A",  # blue-900
    },
}
