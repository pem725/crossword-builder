"""Crossword puzzle generation utilities."""

from .grid_generator import CrosswordGrid, generate_crossword
from .term_extractor import extract_terms_from_text


def render(puzzle, fmt, output_path, **kwargs):
    """Render a puzzle to a single format. Lazy-imports renderers."""
    from .renderers import render as _render
    return _render(puzzle, fmt, output_path, **kwargs)


def render_all(puzzle, output_dir, **kwargs):
    """Render a puzzle to all formats. Lazy-imports renderers."""
    from .renderers import render_all as _render_all
    return _render_all(puzzle, output_dir, **kwargs)


__all__ = [
    "CrosswordGrid",
    "generate_crossword",
    "extract_terms_from_text",
    "render",
    "render_all",
]
