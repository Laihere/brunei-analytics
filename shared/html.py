"""Raw HTML output for Quarto cells.

IPython's HTML object is shown as a `text/html` output, and Quarto adds RequireJS and jQuery
from a CDN to any page with one (it assumes a Jupyter widget). Our pages need neither, so
components return RawHTML instead: a Markdown output holding a raw HTML block, which Pandoc
passes through unchanged.
"""


class RawHTML:
    def __init__(self, data: str):
        self.data = data

    def _repr_markdown_(self) -> str:
        if not self.data:
            return ""
        return f"\n```{{=html}}\n{self.data}\n```\n"

    def __str__(self) -> str:
        return self.data
