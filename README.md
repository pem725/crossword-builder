# Crossword Builder

A crossword puzzle generator designed for educational use. Create crossword puzzles from lecture notes, textbook content, or any source material to help students engage with vocabulary and concepts.

## Features

- **Source-Based Generation**: Extract key terms from text files, PDFs, or code
- **College-Level Clues**: Generates subtle, educational clues appropriate for undergraduate students
- **Multiple Output Formats**: ASCII grid for print, JSON for web integration
- **Claude Code Skill**: Integrated skill for seamless puzzle generation

## Installation

```bash
pip install -e .
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

### ASCII Grid (Print-Ready)

```
███│ 1 │ 2 │███│███
───┼───┼───┼───┼───
 3 │   │   │   │███
───┼───┼───┼───┼───
███│   │███│   │ 4
```

### JSON (Web Integration)

```json
{
  "size": {"rows": 15, "cols": 15},
  "grid": [[".", "A", "L", "G", "O", ...], ...],
  "clues": {
    "across": [{"number": 1, "clue": "...", "answer": "..."}],
    "down": [{"number": 2, "clue": "...", "answer": "..."}]
  }
}
```

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
│       └── term_extractor.py          # Text analysis
├── README.md
├── pyproject.toml
└── LICENSE
```

## License

GNU General Public License v3.0 - See LICENSE file for details.
