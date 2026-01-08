# Output Formats

## ASCII Grid Rendering

### Characters

| Character | Meaning |
|-----------|---------|
| `███` | Blocked/black square |
| `[ ]` | Empty letter cell (student version) |
| `[A]` | Filled letter (answer key) |
| Numbers | Word start positions |

### Student Grid Example

```
███│ 1 │ 2 │███│███│ 3 │███
───┼───┼───┼───┼───┼───┼───
 4 │   │   │   │   │   │███
───┼───┼───┼───┼───┼───┼───
███│   │███│ 5 │   │   │
───┼───┼───┼───┼───┼───┼───
 6 │   │   │   │███│   │███
```

### Answer Key Example

```
███│ 1P│ 2Y│███│███│ 3L│███
───┼───┼───┼───┼───┼───┼───
 4C│  O│  T│  H│  O│  N│███
───┼───┼───┼───┼───┼───┼───
███│  D│███│ 5A│  R│  R│  Y
───┼───┼───┼───┼───┼───┼───
 6D│  E│  A│  D│███│  A│███
```

## JSON Export Format

For web integration, provide structured JSON:

```json
{
  "title": "Chapter 5 Vocabulary",
  "size": {
    "rows": 15,
    "cols": 15
  },
  "grid": [
    [".", "P", "Y", ".", ".", "L", "."],
    ["C", "O", "T", "H", "O", "N", "."],
    [".", "D", ".", "A", "R", "R", "Y"],
    ["D", "E", "A", "D", ".", "A", "."]
  ],
  "clues": {
    "across": [
      {
        "number": 4,
        "clue": "Popular programming language named after a comedy troupe",
        "answer": "PYTHON",
        "row": 1,
        "col": 0,
        "length": 6
      }
    ],
    "down": [
      {
        "number": 1,
        "clue": "Function without a name",
        "answer": "POD",
        "row": 0,
        "col": 1,
        "length": 3
      }
    ]
  }
}
```

### JSON Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Puzzle title |
| `size.rows` | int | Grid height |
| `size.cols` | int | Grid width |
| `grid` | string[][] | 2D array, "." for blocked |
| `clues.across` | array | Across clue objects |
| `clues.down` | array | Down clue objects |

### Clue Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `number` | int | Clue number |
| `clue` | string | Clue text |
| `answer` | string | Answer (uppercase) |
| `row` | int | Starting row (0-indexed) |
| `col` | int | Starting column (0-indexed) |
| `length` | int | Word length |

## Print-Ready Format

For classroom handouts, include:

1. **Header**: Title, date, instructions
2. **Grid**: Student version with clear numbering
3. **Clues**: Two-column layout (Across | Down)
4. **Footer**: Point value or time limit if applicable

Separate answer key on different page for instructor use.
