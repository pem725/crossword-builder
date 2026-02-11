"""Render a crossword grid to PNG using Pillow."""

from __future__ import annotations

import os
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from ._base import RenderConfig
from ..grid_generator import CrosswordGrid, Direction


def _load_font(names: list[str], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a TrueType font by name, falling back to Pillow default."""
    for name in names:
        # Try common system paths
        for ext in (".ttf", ".otf"):
            for directory in _font_dirs():
                path = os.path.join(directory, name + ext)
                if os.path.isfile(path):
                    try:
                        return ImageFont.truetype(path, size)
                    except (OSError, IOError):
                        continue
        # Try loading by name directly (works on some systems)
        try:
            return ImageFont.truetype(name, size)
        except (OSError, IOError):
            continue
    # Fallback
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _font_dirs() -> list[str]:
    """Return platform-appropriate font directories."""
    import sys
    dirs = []
    if sys.platform == "darwin":
        dirs += [
            "/System/Library/Fonts",
            "/System/Library/Fonts/Supplemental",
            "/Library/Fonts",
            os.path.expanduser("~/Library/Fonts"),
        ]
    elif sys.platform == "win32":
        dirs.append(r"C:\Windows\Fonts")
    else:
        dirs += [
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/truetype/dejavu",
            "/usr/share/fonts",
            "/usr/local/share/fonts",
        ]
    return dirs


def render_png(
    puzzle: CrosswordGrid,
    output_path: str,
    *,
    config: Optional[RenderConfig] = None,
    show_answers: bool = False,
) -> str:
    """Render the crossword grid to a PNG file.

    Parameters
    ----------
    puzzle : CrosswordGrid
        The puzzle to render.
    output_path : str
        Destination PNG file path.
    config : RenderConfig, optional
        Rendering configuration.
    show_answers : bool
        If True, letters are drawn inside cells.

    Returns
    -------
    str
        Absolute path of the written PNG.
    """
    if config is None:
        config = RenderConfig()

    puzzle.assign_numbers()

    cs = config.cell_size
    rows, cols = puzzle.rows, puzzle.cols
    grid_w = cols * cs
    grid_h = rows * cs

    # Title area
    title_h = 0
    if config.title or config.subtitle:
        title_h = cs * 2  # reserve space

    img_w = grid_w + 2 * cs  # 1-cell padding on each side
    img_h = grid_h + title_h + 2 * cs

    img = Image.new("RGB", (img_w, img_h), config.bg_color)
    draw = ImageDraw.Draw(img)

    # Fonts
    title_font = _load_font(config.font_family, config.title_font_size)
    subtitle_font = _load_font(config.font_family, config.title_font_size - 6)
    cell_font = _load_font(config.font_family, config.cell_font_size)
    num_font = _load_font(config.font_family, config.number_font_size)

    # Draw title
    y_offset = cs // 2
    if config.title:
        bbox = draw.textbbox((0, 0), config.title, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((img_w - tw) / 2, y_offset), config.title, fill=config.text_color, font=title_font)
        y_offset += config.title_font_size + 8
    if config.subtitle:
        bbox = draw.textbbox((0, 0), config.subtitle, font=subtitle_font)
        tw = bbox[2] - bbox[0]
        draw.text(((img_w - tw) / 2, y_offset), config.subtitle, fill=config.number_color, font=subtitle_font)

    # Grid origin
    gx = cs  # left padding
    gy = title_h + cs  # top padding + title area

    # Build number map
    number_map: dict[tuple[int, int], int] = {}
    for pw in puzzle.placed_words:
        key = (pw.row, pw.col)
        if key not in number_map:
            number_map[key] = pw.number

    # Draw cells
    for r in range(rows):
        for c in range(cols):
            x = gx + c * cs
            y = gy + r * cs
            cell = puzzle.grid[r][c]

            if cell is None or cell == ".":
                # Blocked cell
                draw.rectangle([x, y, x + cs, y + cs], fill=config.block_color)
            else:
                # Letter cell
                draw.rectangle([x, y, x + cs, y + cs], fill=config.bg_color, outline=config.line_color, width=1)

                # Number
                num = number_map.get((r, c))
                if num is not None:
                    draw.text((x + 2, y + 1), str(num), fill=config.number_color, font=num_font)

                # Letter
                if show_answers:
                    bbox = draw.textbbox((0, 0), cell, font=cell_font)
                    lw = bbox[2] - bbox[0]
                    lh = bbox[3] - bbox[1]
                    lx = x + (cs - lw) / 2
                    ly = y + (cs - lh) / 2 + 2  # slight offset for number space
                    draw.text((lx, ly), cell, fill=config.text_color, font=cell_font)

    # Outer grid border
    draw.rectangle([gx, gy, gx + grid_w, gy + grid_h], outline=config.line_color, width=2)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    img.save(output_path, dpi=(config.dpi, config.dpi))
    return os.path.abspath(output_path)


def render_png_pair(
    puzzle: CrosswordGrid,
    output_dir: str,
    *,
    basename: str = "crossword",
    config: Optional[RenderConfig] = None,
) -> tuple[str, str]:
    """Render both student (blank) and answer-key PNGs.

    Returns (student_path, key_path).
    """
    if config is None:
        config = RenderConfig()

    os.makedirs(output_dir, exist_ok=True)

    student = os.path.join(output_dir, f"{basename}.png")
    key = os.path.join(output_dir, f"{basename}_key.png")

    render_png(puzzle, student, config=config, show_answers=False)
    render_png(puzzle, key, config=config, show_answers=True)

    return os.path.abspath(student), os.path.abspath(key)
