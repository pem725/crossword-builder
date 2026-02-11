"""Shared fixtures for renderer tests."""

import pytest

from src.crossword.grid_generator import CrosswordGrid, Direction, generate_crossword


@pytest.fixture
def sample_puzzle():
    """A small deterministic puzzle for testing renderers."""
    words = ["PYTHON", "LOOP", "CLASS", "METHOD", "OBJECT"]
    clues = {
        "PYTHON": "Popular programming language",
        "LOOP": "Repeating control structure",
        "CLASS": "Blueprint for objects",
        "METHOD": "Function inside a class",
        "OBJECT": "Instance of a class",
    }
    puzzle = generate_crossword(words, clues, grid_size=15)
    assert puzzle is not None, "generate_crossword must produce a puzzle"
    return puzzle


@pytest.fixture
def minimal_puzzle():
    """A very small hand-built puzzle (2 words intersecting)."""
    grid = CrosswordGrid(rows=5, cols=5)
    grid.place_word("CAT", 1, 1, Direction.ACROSS, clue="Feline pet")
    grid.place_word("CUP", 1, 1, Direction.DOWN, clue="Drinking vessel")
    grid.assign_numbers()
    return grid


@pytest.fixture
def tmp_output(tmp_path):
    """Return a temporary directory path for output files."""
    return tmp_path
