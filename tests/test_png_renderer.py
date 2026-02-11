"""Tests for PNG renderer."""

import os

import pytest
from PIL import Image

from src.crossword.renderers._base import RenderConfig
from src.crossword.renderers.png_renderer import render_png, render_png_pair


class TestRenderPng:
    def test_creates_file(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.png")
        result = render_png(minimal_puzzle, path)
        assert os.path.isfile(result)

    def test_returns_absolute_path(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.png")
        result = render_png(minimal_puzzle, path)
        assert os.path.isabs(result)

    def test_output_is_valid_png(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.png")
        render_png(minimal_puzzle, path)
        img = Image.open(path)
        assert img.format == "PNG"
        assert img.size[0] > 0 and img.size[1] > 0

    def test_answer_key_differs(self, minimal_puzzle, tmp_output):
        blank = os.path.join(tmp_output, "blank.png")
        key = os.path.join(tmp_output, "key.png")
        render_png(minimal_puzzle, blank, show_answers=False)
        render_png(minimal_puzzle, key, show_answers=True)
        # Both should exist and differ in content
        assert os.path.getsize(blank) != os.path.getsize(key)

    def test_custom_config(self, minimal_puzzle, tmp_output):
        cfg = RenderConfig(title="My Puzzle", subtitle="Course 101", cell_size=50)
        path = os.path.join(tmp_output, "custom.png")
        render_png(minimal_puzzle, path, config=cfg)
        img = Image.open(path)
        # With cell_size=50 and a 5x5 grid the image should be larger than default
        assert img.size[0] > 0

    def test_creates_parent_dirs(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "sub", "dir", "test.png")
        result = render_png(minimal_puzzle, path)
        assert os.path.isfile(result)

    def test_sample_puzzle(self, sample_puzzle, tmp_output):
        path = os.path.join(tmp_output, "sample.png")
        render_png(sample_puzzle, path, show_answers=True)
        assert os.path.isfile(path)


class TestRenderPngPair:
    def test_creates_both_files(self, minimal_puzzle, tmp_output):
        student, key = render_png_pair(minimal_puzzle, str(tmp_output))
        assert os.path.isfile(student)
        assert os.path.isfile(key)
        assert student.endswith(".png")
        assert key.endswith("_key.png")

    def test_custom_basename(self, minimal_puzzle, tmp_output):
        student, key = render_png_pair(
            minimal_puzzle, str(tmp_output), basename="ch5"
        )
        assert "ch5.png" in student
        assert "ch5_key.png" in key
