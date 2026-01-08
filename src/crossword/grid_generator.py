"""
Crossword grid generation algorithm.

This module provides functionality to generate valid crossword puzzle grids
from a list of words. It uses a backtracking algorithm to place words
while maintaining crossword validity constraints.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import random


class Direction(Enum):
    ACROSS = "across"
    DOWN = "down"


@dataclass
class PlacedWord:
    """Represents a word placed in the grid."""
    word: str
    row: int
    col: int
    direction: Direction
    number: int = 0
    clue: str = ""


@dataclass
class CrosswordGrid:
    """
    Represents a crossword puzzle grid.

    Attributes:
        rows: Number of rows in the grid
        cols: Number of columns in the grid
        grid: 2D list of characters (None for empty, '.' for blocked)
        placed_words: List of words placed in the grid
    """
    rows: int
    cols: int
    grid: list = field(default_factory=list)
    placed_words: list = field(default_factory=list)

    def __post_init__(self):
        if not self.grid:
            self.grid = [[None for _ in range(self.cols)] for _ in range(self.rows)]

    def can_place_word(self, word: str, row: int, col: int, direction: Direction) -> bool:
        """Check if a word can be placed at the given position."""
        word = word.upper()

        if direction == Direction.ACROSS:
            # Check bounds
            if col + len(word) > self.cols:
                return False
            # Check for letter before word start
            if col > 0 and self.grid[row][col - 1] not in (None, '.'):
                return False
            # Check for letter after word end
            if col + len(word) < self.cols and self.grid[row][col + len(word)] not in (None, '.'):
                return False

            for i, letter in enumerate(word):
                current = self.grid[row][col + i]
                if current == '.':
                    return False
                if current is not None and current != letter:
                    return False
                # If empty, check adjacent cells (above and below)
                if current is None:
                    # Check above
                    if row > 0 and self.grid[row - 1][col + i] not in (None, '.'):
                        # Only allow if this is an intersection
                        pass
                    # Check below
                    if row < self.rows - 1 and self.grid[row + 1][col + i] not in (None, '.'):
                        pass
        else:  # DOWN
            if row + len(word) > self.rows:
                return False
            # Check for letter before word start
            if row > 0 and self.grid[row - 1][col] not in (None, '.'):
                return False
            # Check for letter after word end
            if row + len(word) < self.rows and self.grid[row + len(word)][col] not in (None, '.'):
                return False

            for i, letter in enumerate(word):
                current = self.grid[row + i][col]
                if current == '.':
                    return False
                if current is not None and current != letter:
                    return False

        return True

    def place_word(self, word: str, row: int, col: int, direction: Direction, clue: str = "") -> PlacedWord:
        """Place a word in the grid."""
        word = word.upper()

        if direction == Direction.ACROSS:
            for i, letter in enumerate(word):
                self.grid[row][col + i] = letter
        else:
            for i, letter in enumerate(word):
                self.grid[row + i][col] = letter

        placed = PlacedWord(word=word, row=row, col=col, direction=direction, clue=clue)
        self.placed_words.append(placed)
        return placed

    def find_intersections(self, word: str) -> list:
        """Find all possible positions where word can intersect with existing words."""
        word = word.upper()
        positions = []

        for placed in self.placed_words:
            for i, letter in enumerate(word):
                for j, placed_letter in enumerate(placed.word):
                    if letter == placed_letter:
                        # Calculate intersection position
                        if placed.direction == Direction.ACROSS:
                            # New word goes DOWN
                            new_row = placed.row - i
                            new_col = placed.col + j
                            new_dir = Direction.DOWN
                        else:
                            # New word goes ACROSS
                            new_row = placed.row + j
                            new_col = placed.col - i
                            new_dir = Direction.ACROSS

                        if new_row >= 0 and new_col >= 0:
                            if self.can_place_word(word, new_row, new_col, new_dir):
                                positions.append((new_row, new_col, new_dir))

        return positions

    def assign_numbers(self):
        """Assign clue numbers to placed words."""
        # Find all starting positions
        starts = {}
        for pw in self.placed_words:
            key = (pw.row, pw.col)
            if key not in starts:
                starts[key] = []
            starts[key].append(pw)

        # Sort by position (top to bottom, left to right)
        sorted_starts = sorted(starts.keys(), key=lambda x: (x[0], x[1]))

        # Assign numbers
        number = 1
        for pos in sorted_starts:
            for pw in starts[pos]:
                pw.number = number
            number += 1

    def to_ascii(self, show_answers: bool = False) -> str:
        """Convert grid to ASCII representation."""
        self.assign_numbers()

        # Create number map for display
        number_map = {}
        for pw in self.placed_words:
            key = (pw.row, pw.col)
            if key not in number_map:
                number_map[key] = pw.number

        lines = []
        for r in range(self.rows):
            row_chars = []
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell is None or cell == '.':
                    row_chars.append('███')
                elif show_answers:
                    num = number_map.get((r, c), '')
                    if num:
                        row_chars.append(f'{num:>2}{cell}')
                    else:
                        row_chars.append(f'  {cell}')
                else:
                    num = number_map.get((r, c), '')
                    if num:
                        row_chars.append(f'{num:>2} ')
                    else:
                        row_chars.append('   ')
            lines.append('│'.join(row_chars))

        separator = '┼'.join(['───'] * self.cols)
        return ('\n' + separator + '\n').join(lines)

    def to_json(self) -> dict:
        """Export grid as JSON-compatible dictionary."""
        self.assign_numbers()

        # Convert grid to strings
        json_grid = []
        for row in self.grid:
            json_row = []
            for cell in row:
                json_row.append('.' if cell is None else cell)
            json_grid.append(json_row)

        across = []
        down = []

        for pw in self.placed_words:
            entry = {
                "number": pw.number,
                "clue": pw.clue,
                "answer": pw.word,
                "row": pw.row,
                "col": pw.col,
                "length": len(pw.word)
            }
            if pw.direction == Direction.ACROSS:
                across.append(entry)
            else:
                down.append(entry)

        return {
            "size": {"rows": self.rows, "cols": self.cols},
            "grid": json_grid,
            "clues": {
                "across": sorted(across, key=lambda x: x["number"]),
                "down": sorted(down, key=lambda x: x["number"])
            }
        }

    def get_clues_formatted(self) -> str:
        """Get formatted clue list."""
        self.assign_numbers()

        across = sorted([pw for pw in self.placed_words if pw.direction == Direction.ACROSS],
                       key=lambda x: x.number)
        down = sorted([pw for pw in self.placed_words if pw.direction == Direction.DOWN],
                     key=lambda x: x.number)

        lines = ["**ACROSS**"]
        for pw in across:
            clue = pw.clue if pw.clue else f"[Clue for {pw.word}]"
            lines.append(f"{pw.number}. {clue} ({len(pw.word)} letters)")

        lines.append("")
        lines.append("**DOWN**")
        for pw in down:
            clue = pw.clue if pw.clue else f"[Clue for {pw.word}]"
            lines.append(f"{pw.number}. {clue} ({len(pw.word)} letters)")

        return "\n".join(lines)


def generate_crossword(words: list, clues: Optional[dict] = None,
                       grid_size: int = 15, max_attempts: int = 100) -> Optional[CrosswordGrid]:
    """
    Generate a crossword puzzle from a list of words.

    Args:
        words: List of words to include in the puzzle
        clues: Optional dictionary mapping words to clues
        grid_size: Size of the grid (will be square)
        max_attempts: Maximum placement attempts before giving up

    Returns:
        CrosswordGrid if successful, None if unable to place all words
    """
    if not words:
        return None

    clues = clues or {}

    # Sort words by length (longer first for better placement)
    sorted_words = sorted(words, key=len, reverse=True)

    grid = CrosswordGrid(rows=grid_size, cols=grid_size)

    # Place the first (longest) word in the center
    first_word = sorted_words[0].upper()
    center_row = grid_size // 2
    center_col = (grid_size - len(first_word)) // 2
    grid.place_word(first_word, center_row, center_col, Direction.ACROSS,
                   clues.get(sorted_words[0], ""))

    # Try to place remaining words
    placed_count = 1
    for word in sorted_words[1:]:
        word_upper = word.upper()
        positions = grid.find_intersections(word_upper)

        if positions:
            # Shuffle to add variety
            random.shuffle(positions)
            row, col, direction = positions[0]
            grid.place_word(word_upper, row, col, direction, clues.get(word, ""))
            placed_count += 1
        else:
            # Try random placement if no intersection found
            for _ in range(max_attempts):
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - 1)
                direction = random.choice([Direction.ACROSS, Direction.DOWN])

                if grid.can_place_word(word_upper, row, col, direction):
                    grid.place_word(word_upper, row, col, direction, clues.get(word, ""))
                    placed_count += 1
                    break

    # Trim the grid to fit content
    grid = _trim_grid(grid)

    return grid


def _trim_grid(grid: CrosswordGrid) -> CrosswordGrid:
    """Trim empty rows and columns from the grid edges."""
    min_row, max_row = grid.rows, 0
    min_col, max_col = grid.cols, 0

    for r in range(grid.rows):
        for c in range(grid.cols):
            if grid.grid[r][c] is not None and grid.grid[r][c] != '.':
                min_row = min(min_row, r)
                max_row = max(max_row, r)
                min_col = min(min_col, c)
                max_col = max(max_col, c)

    if min_row > max_row:
        return grid

    # Add 1 cell padding
    min_row = max(0, min_row - 1)
    max_row = min(grid.rows - 1, max_row + 1)
    min_col = max(0, min_col - 1)
    max_col = min(grid.cols - 1, max_col + 1)

    new_rows = max_row - min_row + 1
    new_cols = max_col - min_col + 1

    new_grid = CrosswordGrid(rows=new_rows, cols=new_cols)

    for r in range(new_rows):
        for c in range(new_cols):
            new_grid.grid[r][c] = grid.grid[r + min_row][c + min_col]

    # Update placed word positions
    for pw in grid.placed_words:
        pw.row -= min_row
        pw.col -= min_col
        new_grid.placed_words.append(pw)

    return new_grid


if __name__ == "__main__":
    # Example usage
    test_words = ["PYTHON", "ALGORITHM", "FUNCTION", "VARIABLE", "LOOP",
                  "CLASS", "METHOD", "OBJECT", "STRING", "INTEGER"]

    test_clues = {
        "PYTHON": "A popular programming language named after a comedy troupe",
        "ALGORITHM": "Step-by-step procedure for solving a problem",
        "FUNCTION": "Reusable block of code that performs a specific task",
        "VARIABLE": "Named storage location in memory",
        "LOOP": "Structure that repeats code execution",
        "CLASS": "Blueprint for creating objects",
        "METHOD": "Function defined inside a class",
        "OBJECT": "Instance of a class",
        "STRING": "Sequence of characters",
        "INTEGER": "Whole number data type"
    }

    puzzle = generate_crossword(test_words, test_clues)

    if puzzle:
        print("=== CROSSWORD PUZZLE ===\n")
        print(puzzle.to_ascii(show_answers=False))
        print("\n")
        print(puzzle.get_clues_formatted())
        print("\n=== ANSWER KEY ===\n")
        print(puzzle.to_ascii(show_answers=True))
