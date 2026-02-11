"""Shared configuration for crossword renderers."""

from dataclasses import dataclass, field


@dataclass
class RenderConfig:
    """Configuration shared across all renderers.

    Attributes:
        title: Puzzle title displayed above the grid.
        subtitle: Optional subtitle (e.g. course name).
        cell_size: Pixel size of each grid cell (PNG/PDF).
        dpi: Dots per inch for raster output.
        font_family: Preferred font family names in priority order.
        bg_color: Background colour for letter cells.
        block_color: Fill colour for blocked/black cells.
        line_color: Grid line colour.
        text_color: Default text (letters, numbers) colour.
        number_color: Clue-number colour (top-left corner of cells).
        title_font_size: Title text size in points.
        cell_font_size: Letter text size in points.
        number_font_size: Clue-number text size in points.
    """

    title: str = ""
    subtitle: str = ""

    # Sizing
    cell_size: int = 40
    dpi: int = 300

    # Font preferences (tried in order; last resort is Pillow default)
    font_family: list = field(
        default_factory=lambda: ["Helvetica", "Arial", "DejaVuSans", "FreeSans"]
    )

    # Colours (RGB tuples or hex strings for HTML)
    bg_color: tuple = (255, 255, 255)
    block_color: tuple = (0, 0, 0)
    line_color: tuple = (0, 0, 0)
    text_color: tuple = (0, 0, 0)
    number_color: tuple = (80, 80, 80)

    # Font sizes (points)
    title_font_size: int = 24
    cell_font_size: int = 18
    number_font_size: int = 9
