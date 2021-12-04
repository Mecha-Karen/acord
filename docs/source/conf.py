import pydata_sphinx_theme
import datetime
import os
import sys

sys.path.append(os.path.abspath('../extensions'))

project = 'Documentation'
copyright = '2021 - Present, Mecha Karen'
author = 'Mecha Karen'
release = '0.0.1a'

extensions = [
   'sphinx.ext.autodoc', 
   'sphinx.ext.coverage', 
   'sphinx.ext.napoleon',
   'sphinx.ext.extlinks',
   'sphinx.ext.intersphinx',
   'sphinx.ext.autosummary',
   'attributetable'
]

intersphinx_mapping = {
  'py': ('https://docs.python.org/3', None),
}

rst_prolog = """
.. |coro| replace:: This function is a |coroutine_link|_.
.. |func| replace:: This is a |function_link|_.
.. |maybecoro| replace:: This function *could be a* |coroutine_link|_.
.. |coroutine_link| replace:: *coroutine*
.. |function_link| replace:: *function*
.. _coroutine_link: https://docs.python.org/3/library/asyncio-task.html#coroutine
.. _function_link: https://docs.python.org/3/reference/compound_stmts.html#function
"""

templates_path = ['_templates']

exclude_patterns = ['*.md', '*.template']


html_theme = 'pydata_sphinx_theme'
html_logo = "_static/logo.png"

html_theme_options = {
   "favicons": [
      {
         "rel": "icon",
         "sizes": "16x16",
         "href": "logo.png",
      },
      {
         "rel": "icon",
         "sizes": "32x32",
         "href": "logo.png",
      },
      {
         "rel": "apple-touch-icon",
         "sizes": "180x180",
         "href": "logo.png"
      },
   ],

   "icon_links": [
      {
        "name": "GitHub",
        "url": "https://github.com/Mecha-Karen/",
        "icon": "fab fa-github",
      },
      {
        "name": "Discord",
        "url": "https://discord.com/invite/JBjMAMag7a",
        "icon": "fab fa-discord"
      },
      {
        "name": "Dashboard",
        "url": "https://mechakaren.xyz/dashboard",
        "icon": "fas fa-box"
      }
    ],

   "use_edit_page_button": True,
   "collapse_navigation": False,
   "show_prev_next": False,
   "navigation_depth": 3,
   "search_bar_text": "Search the docs ...",
   "footer_items": ["copyright", "last-updated"],
}

html_context = {
    "github_url": "https://github.com",
    "github_user": "Mecha-Karen",
    "github_repo": "acord",
    "github_version": "main",
    "doc_path": "source",
    "last_updated": datetime.datetime.utcnow().strftime('%d/%m/%Y'),
}

html_sidebars = {
    "**": ["search-field", "sidebar-nav-bs"],
    "index": ["search-field", "home-navbar"]
}

html_static_path = ['_static']
html_css_files = [
    'css/style.css',
    'css/codeblocks.css'
]

html_title = "Mecha Karen"

suppress_warnings = [
   "image.not_readable"
]