"""Crossword puzzle renderers.

Provides ``render()`` for single-format output and ``render_all()`` for
generating every supported format at once.  Renderer dependencies are
imported lazily so users only need the libraries for the formats they use.
"""

from __future__ import annotations

import os
from typing import Optional

from ._base import RenderConfig

__all__ = ["render", "render_all", "RenderConfig"]

_FORMATS = ("png", "pdf", "html")


def render(
    puzzle,
    fmt: str,
    output_path: str,
    *,
    config: Optional[RenderConfig] = None,
    title: str = "",
    subtitle: str = "",
    show_answers: bool = False,
) -> str:
    """Render *puzzle* to a single file.

    Parameters
    ----------
    puzzle : CrosswordGrid
        The puzzle object (from ``grid_generator``).
    fmt : str
        One of ``"png"``, ``"pdf"``, or ``"html"``.
    output_path : str
        Destination file path.
    config : RenderConfig, optional
        Shared rendering configuration.  If *None* a default is created
        using *title* and *subtitle*.
    title : str
        Convenience shortcut – sets ``config.title`` when *config* is None.
    subtitle : str
        Convenience shortcut – sets ``config.subtitle`` when *config* is None.
    show_answers : bool
        For PNG: whether to show answer letters.  Ignored by PDF (which
        always renders both) and HTML (interactive).

    Returns
    -------
    str
        The absolute path of the written file.
    """
    fmt = fmt.lower().strip()
    if fmt not in _FORMATS:
        raise ValueError(f"Unknown format {fmt!r}; choose from {_FORMATS}")

    if config is None:
        config = RenderConfig(title=title, subtitle=subtitle)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)

    if fmt == "png":
        from .png_renderer import render_png

        render_png(puzzle, output_path, config=config, show_answers=show_answers)
    elif fmt == "pdf":
        from .pdf_renderer import render_pdf

        render_pdf(puzzle, output_path, config=config)
    elif fmt == "html":
        from .html_renderer import render_html

        render_html(puzzle, output_path, config=config)

    return os.path.abspath(output_path)


def render_all(
    puzzle,
    output_dir: str,
    *,
    basename: str = "crossword",
    config: Optional[RenderConfig] = None,
    title: str = "",
    subtitle: str = "",
) -> dict[str, str]:
    """Render *puzzle* to every supported format.

    Produces:
    - ``<basename>.png``       – student grid (blank)
    - ``<basename>_key.png``   – answer key grid
    - ``<basename>.pdf``       – full worksheet (grid + clues + key)
    - ``<basename>.html``      – interactive web puzzle

    Returns a dict mapping format labels to absolute file paths.
    """
    if config is None:
        config = RenderConfig(title=title, subtitle=subtitle)

    os.makedirs(output_dir, exist_ok=True)

    def _path(suffix: str) -> str:
        return os.path.join(output_dir, f"{basename}{suffix}")

    from .png_renderer import render_png

    png_path = _path(".png")
    render_png(puzzle, png_path, config=config, show_answers=False)

    png_key_path = _path("_key.png")
    render_png(puzzle, png_key_path, config=config, show_answers=True)

    from .pdf_renderer import render_pdf

    pdf_path = _path(".pdf")
    render_pdf(puzzle, pdf_path, config=config)

    from .html_renderer import render_html

    html_path = _path(".html")
    render_html(puzzle, html_path, config=config)

    return {
        "png": os.path.abspath(png_path),
        "png_key": os.path.abspath(png_key_path),
        "pdf": os.path.abspath(pdf_path),
        "html": os.path.abspath(html_path),
    }
