# Crossword Puzzle Generator from Source Files

Generate educational crossword puzzles by extracting key terms and concepts from source files. Designed for college-level students with moderate verbal fluency.

## When to Use This Skill

Use this skill when:
- The user wants to create a crossword puzzle from lecture notes, textbook content, or documentation
- The user provides source files (text, markdown, PDF, code files) to extract vocabulary from
- The user needs an educational assessment tool based on specific content

## Process Overview

### Step 1: Gather Source Material

Ask the user which files to analyze if not already specified. Accept:
- Text files (.txt, .md)
- Code files (extract comments, docstrings, function/class names)
- PDF documents
- Any readable file format

Read all specified source files thoroughly.

### Step 2: Extract Key Terms

Identify 15-25 meaningful terms from the source material:

**Good candidates:**
- Technical terminology specific to the subject
- Proper nouns (people, places, concepts)
- Domain-specific vocabulary
- Multi-word phrases that can be hyphenated or combined
- Words that appear multiple times (indicating importance)

**Avoid:**
- Common words (the, is, and, etc.)
- Words shorter than 4 letters (harder to place in grid)
- Obscure jargon that wouldn't be fair to expect
- Words longer than 15 letters (grid constraints)

### Step 3: Generate Clues

Create clues at a **college level with moderate verbal fluency**:

**Clue Style Guidelines:**
- Use indirect definitions rather than direct dictionary definitions
- Reference context from the source material
- Include subtle wordplay when appropriate (but not cryptic crossword level)
- Vary clue types: definitional, contextual, fill-in-the-blank, example-based

**Difficulty Calibration:**
- Assume SAT-level vocabulary (not GRE)
- Avoid requiring specialized knowledge beyond the source material
- Make 60% of clues straightforward, 30% moderate, 10% challenging

**Example Clue Formats:**
- Definitional: "Process of cell division producing gametes" → MEIOSIS
- Contextual: "In the reading, this structure stores genetic information" → NUCLEUS
- Fill-in-blank: "The ___ principle states that position and momentum cannot both be precisely known" → UNCERTAINTY
- Example-based: "Python, Java, and C++ are examples of these" → LANGUAGES

### Step 4: Generate the Crossword Grid

Create a valid crossword grid following these rules:

1. **Grid Size**: Start with 15x15 for 15-20 words, scale up for more
2. **Symmetry**: Use rotational symmetry (180-degree)
3. **Connectivity**: All words must intersect with at least one other word
4. **No isolated sections**: The puzzle must be fully connected
5. **Minimum word length**: 4 letters
6. **Black squares**: Use '.' for blocked cells

Use the Python helper module at `src/crossword/grid_generator.py` if available, or generate algorithmically.

### Step 5: Output Format

Provide the puzzle in this structure:

```
## [PUZZLE TITLE]

### Grid (Student Version)
[ASCII grid with numbers for word starts, empty squares for letters]

### Clues

**ACROSS**
1. [Clue for 1-Across]
4. [Clue for 4-Across]
...

**DOWN**
1. [Clue for 1-Down]
2. [Clue for 2-Down]
...

---

### Answer Key (for instructor)
[ASCII grid with all letters filled in]

### Word List
- WORD1: Brief definition/context
- WORD2: Brief definition/context
...
```

## Grid Rendering

Use these characters for the ASCII grid:
- `.` = Black/blocked square
- `[ ]` = Empty letter square (student version)
- `[A]` = Filled letter (answer key)
- Numbers indicate word starts

Example student grid:
```
. . [1] [2] . . [3] . .
. . [ ] [ ] . . [ ] . .
[4] [ ] [ ] [ ] [ ] [ ] [ ] [ ] .
. . [ ] . . . [ ] . .
```

## Additional Options

If the user requests:
- **Difficulty level**: Adjust clue subtlety (easy/medium/hard)
- **Word count**: Target specific number of terms
- **Theme**: Focus extraction on specific topics
- **Export format**: Provide JSON for web rendering

## JSON Export Format (if requested)

```json
{
  "title": "Puzzle Title",
  "size": {"rows": 15, "cols": 15},
  "grid": [[".", ".", "A", "B", ...], ...],
  "clues": {
    "across": [{"number": 1, "clue": "...", "answer": "...", "row": 0, "col": 2}],
    "down": [{"number": 1, "clue": "...", "answer": "...", "row": 0, "col": 2}]
  }
}
```

## Integration with Other Skills

This skill works well with:
- Document analysis skills (pre-process complex documents)
- Quiz generation skills (create companion assessments)
- Study guide skills (crossword as review activity)

When combining with other skills, the crossword can serve as:
- A pre-reading vocabulary introduction
- A post-reading comprehension check
- A unit review activity
