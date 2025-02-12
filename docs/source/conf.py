# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

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
        "color-brand-primary": "#A855F7",  # Pastel purple
        "color-brand-content": "#0E7490",  # Turquoise
        "color-admonition-background": "#FBCFE8",  # Lavender Blush
        "color-background-primary": "#F9FAFB",  # Soft White
        "color-background-secondary": "#E5E7EB",  # Warm Gray
        "color-foreground-primary": "#374151",  # Muted Charcoal
        "color-foreground-secondary": "#525252",  # Dark Gray
        "color-inline-code": "#BFDBFE",  # Powder Blue
        "color-link": "#0E7490",  # Turquoise
        "color-link--hover": "#0EA5E9",  # Brighter turquoise
        "color-sidebar-background": "#E6D6F2",  # Light pastel purple
        "color-sidebar-link": "#6B21A8",  # Darker purple
        "color-sidebar-link--hover": "#A855F7",  # Brighter purple
        "color-sidebar-heading": "#4C1D95",  # Darker purple
    },
}
