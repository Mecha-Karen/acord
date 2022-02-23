"""
Allows us to use jinja within our .rst files

We can use this to our advantage as generated rst is processed afterwards
"""
from sphinx.application import Sphinx
import acord


def worker(app: Sphinx, docname: str, source: list):
    if app.builder.format != "html":
        return

    src = source[0]
    rendered_source = app.builder.templates.render_string(
        src, {
            "acord": acord,
            "getattr": getattr,
            "dir": dir,
            "disallow": ["final", ],
            "LINE_SEP": "\n",
        }
    )

    source[0] = rendered_source


def setup(app: Sphinx):
    app.connect("source-read", worker)
