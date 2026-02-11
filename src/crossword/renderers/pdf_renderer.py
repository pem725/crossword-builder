"""Render a crossword puzzle as a PDF worksheet using fpdf2."""

from __future__ import annotations

import os
import tempfile
from typing import Optional

from fpdf import FPDF

from ._base import RenderConfig
from ..grid_generator import CrosswordGrid, Direction
from .png_renderer import render_png


def render_pdf(
    puzzle: CrosswordGrid,
    output_path: str,
    *,
    config: Optional[RenderConfig] = None,
    include_key: bool = True,
) -> str:
    """Render the crossword as a PDF worksheet.

    Page 1: title, subtitle, name/date fields, instructions,
            embedded grid PNG, and a two-column clue list.
    Page 2 (optional): answer key grid.

    Parameters
    ----------
    puzzle : CrosswordGrid
        The puzzle to render.
    output_path : str
        Destination PDF file path.
    config : RenderConfig, optional
        Rendering configuration.
    include_key : bool
        If True (default), append an answer-key page.

    Returns
    -------
    str
        Absolute path of the written PDF file.
    """
    if config is None:
        config = RenderConfig()

    puzzle.assign_numbers()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # --- Page 1: Student worksheet ---
    pdf.add_page()
    _add_header(pdf, config)
    _add_grid_image(pdf, puzzle, config, show_answers=False)
    _add_clues(pdf, puzzle)

    # --- Page 2: Answer key ---
    if include_key:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Answer Key", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(4)
        _add_grid_image(pdf, puzzle, config, show_answers=True)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    pdf.output(output_path)
    return os.path.abspath(output_path)


def _add_header(pdf: FPDF, config: RenderConfig) -> None:
    """Draw the worksheet header (title, subtitle, name/date fields)."""
    if config.title:
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 10, config.title, new_x="LMARGIN", new_y="NEXT", align="C")

    if config.subtitle:
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 7, config.subtitle, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.ln(4)

    # Name / Date fields
    pdf.set_font("Helvetica", "", 10)
    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    half = page_w / 2

    x_start = pdf.l_margin
    y = pdf.get_y()
    pdf.set_xy(x_start, y)
    pdf.cell(half, 7, "Name: ________________________________________", new_x="RIGHT", new_y="TOP")
    pdf.cell(half, 7, "Date: _______________", new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(3)

    # Instructions
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 5, "Fill in the crossword grid using the clues below.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def _add_grid_image(
    pdf: FPDF,
    puzzle: CrosswordGrid,
    config: RenderConfig,
    show_answers: bool,
) -> None:
    """Render the grid to a temp PNG and embed it in the PDF."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Use a print-friendly config for the embedded image
        img_config = RenderConfig(
            cell_size=config.cell_size,
            dpi=config.dpi,
            font_family=config.font_family,
            bg_color=config.bg_color,
            block_color=config.block_color,
            line_color=config.line_color,
            text_color=config.text_color,
            number_color=config.number_color,
            cell_font_size=config.cell_font_size,
            number_font_size=config.number_font_size,
        )
        render_png(puzzle, tmp_path, config=img_config, show_answers=show_answers)

        # Calculate image width to fit page (with margins)
        page_w = pdf.w - pdf.l_margin - pdf.r_margin
        # Let fpdf scale; cap at page width
        pdf.image(tmp_path, x=pdf.l_margin, w=min(page_w, 160))
        pdf.ln(4)
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def _add_clues(pdf: FPDF, puzzle: CrosswordGrid) -> None:
    """Render the two-column clue list (Across | Down)."""
    across = sorted(
        [pw for pw in puzzle.placed_words if pw.direction == Direction.ACROSS],
        key=lambda pw: pw.number,
    )
    down = sorted(
        [pw for pw in puzzle.placed_words if pw.direction == Direction.DOWN],
        key=lambda pw: pw.number,
    )

    page_w = pdf.w - pdf.l_margin - pdf.r_margin
    col_w = page_w / 2 - 4  # small gap between columns

    # Across header
    pdf.set_font("Helvetica", "B", 11)
    y_start = pdf.get_y()
    x_left = pdf.l_margin
    x_right = pdf.l_margin + page_w / 2 + 4

    pdf.set_xy(x_left, y_start)
    pdf.cell(col_w, 7, "ACROSS", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    for pw in across:
        clue = pw.clue if pw.clue else f"[Clue for {pw.word}]"
        text = f"{pw.number}. {clue} ({len(pw.word)})"
        pdf.set_x(x_left)
        pdf.multi_cell(col_w, 4.5, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

    across_end_y = pdf.get_y()

    # Down header
    pdf.set_xy(x_right, y_start)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(col_w, 7, "DOWN", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    for pw in down:
        clue = pw.clue if pw.clue else f"[Clue for {pw.word}]"
        text = f"{pw.number}. {clue} ({len(pw.word)})"
        pdf.set_x(x_right)
        pdf.multi_cell(col_w, 4.5, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(0.5)

    # Move to whichever column ended lower
    pdf.set_y(max(across_end_y, pdf.get_y()))
