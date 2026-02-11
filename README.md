# Crossword Builder

A crossword puzzle generator designed for educational use. Create crossword puzzles from lecture notes, textbook content, or any source material to help students engage with vocabulary and concepts.

## Features

- **Source-Based Generation**: Extract key terms from text files, PDFs, or code
- **College-Level Clues**: Generates subtle, educational clues appropriate for undergraduate students
- **Multiple Output Formats**: ASCII, JSON, PNG, PDF worksheet, and interactive HTML
- **Interactive HTML Puzzles**: Self-contained single-file puzzles with keyboard navigation, check/reveal, and localStorage progress saving
- **Print-Ready PDF**: Full worksheet with header, grid, two-column clues, and answer key page
- **Claude Code Skill**: Integrated skill for seamless puzzle generation

## Installation

```bash
# Core (no runtime dependencies)
pip install -e .

# With renderers (PNG, PDF)
pip install -e ".[render]"

# Development (renderers + pytest)
pip install -e ".[dev]"
```

## Usage

### As a Claude Code Skill

The primary way to use this tool is through the Claude Code skill:

1. Invoke the skill: `skill: crossword-from-source`
2. Provide your source files when prompted
3. Claude will extract terms, generate clues, and create the puzzle

### Programmatic Usage

```python
from src.crossword import generate_crossword, extract_terms_from_text

# Extract terms from your content
with open("lecture_notes.txt") as f:
    text = f.read()

terms = extract_terms_from_text(text, max_terms=20)
words = [t.term for t in terms]

# Generate clues (or let Claude do this for better quality)
clues = {
    "ALGORITHM": "Step-by-step procedure for solving a problem",
    "VARIABLE": "Named storage location that holds data",
    # ... more clues
}

# Generate the crossword
puzzle = generate_crossword(words, clues)

# Output
print(puzzle.to_ascii())  # Student version
print(puzzle.to_ascii(show_answers=True))  # Answer key
print(puzzle.get_clues_formatted())  # Clue list
```

### Rendering Output Files

```python
from src.crossword import render, render_all

# Single format
render(puzzle, "html", "output/ch5.html",
       title="Chapter 5: Motivation", subtitle="PSYC 405")

# All formats at once
files = render_all(puzzle, "output/", basename="ch5",
                   title="Chapter 5: Motivation", subtitle="PSYC 405")
# → {"png": "output/ch5.png", "png_key": "output/ch5_key.png",
#    "pdf": "output/ch5.pdf", "html": "output/ch5.html"}
```

### Command Line

```bash
python -m src.crossword.grid_generator
```

## Skill Integration

The skill at `.claude/skills/crossword-from-source/` can be combined with other educational skills:

- **Pre-reading**: Generate vocabulary crosswords before assigning readings
- **Post-lecture**: Create review puzzles from lecture notes
- **Assessment**: Use as low-stakes vocabulary checks

## Clue Guidelines

The generator creates clues at a college level with moderate verbal fluency:

| Difficulty | Percentage | Example Style |
|------------|------------|---------------|
| Straightforward | 60% | Direct definitions with context |
| Moderate | 30% | Indirect references, examples |
| Challenging | 10% | Wordplay, etymology hints |

## Output Formats

| Format | File | Dependency | Use case |
|--------|------|-----------|----------|
| ASCII | (inline) | None | Quick preview, terminal |
| JSON | (inline) | None | Web integration, data exchange |
| PNG | `.png` | Pillow | Embed in Canvas/LMS, slides |
| PDF | `.pdf` | fpdf2 | Classroom handouts |
| HTML | `.html` | None | Interactive online puzzles |

### Course Integration (Quarto / Netlify)

Generated HTML files are self-contained — place them in a `crosswords/` directory, add to `_quarto.yml` resources, and they're served as static files. Link from QMD content or embed via `<iframe>`.

## Project Structure

```
crossword-builder/
├── .claude/
│   └── skills/
│       └── crossword-from-source/     # Claude Code skill (folder)
│           ├── SKILL.md               # Main skill definition
│           └── references/
│               ├── clue-guidelines.md # Loaded when writing clues
│               └── output-formats.md  # Loaded for output formatting
├── src/
│   └── crossword/
│       ├── __init__.py
│       ├── grid_generator.py          # Core grid algorithm
│       ├── term_extractor.py          # Text analysis
│       └── renderers/
│           ├── __init__.py            # render() / render_all() dispatch
│           ├── _base.py               # Shared RenderConfig
│           ├── png_renderer.py        # Grid → PNG (Pillow)
│           ├── pdf_renderer.py        # Worksheet → PDF (fpdf2)
│           └── html_renderer.py       # Interactive HTML (no deps)
├── tests/
│   ├── conftest.py                    # Shared fixtures
│   ├── test_png_renderer.py
│   ├── test_pdf_renderer.py
│   ├── test_html_renderer.py
│   └── test_renderer_integration.py
├── README.md
├── pyproject.toml
└── LICENSE
```

## License

GNU General Public License v3.0 - See LICENSE file for details.
