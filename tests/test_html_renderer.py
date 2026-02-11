"""Tests for HTML renderer."""

import os

import pytest

from src.crossword.renderers._base import RenderConfig
from src.crossword.renderers.html_renderer import render_html


class TestRenderHtml:
    def test_creates_file(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        result = render_html(minimal_puzzle, path)
        assert os.path.isfile(result)

    def test_returns_absolute_path(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        result = render_html(minimal_puzzle, path)
        assert os.path.isabs(result)

    def test_valid_html_structure(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        render_html(minimal_puzzle, path)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        assert "<!DOCTYPE html>" in html
        assert "<html" in html
        assert "</html>" in html
        assert "<script>" in html
        assert "</script>" in html

    def test_contains_puzzle_data(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        render_html(minimal_puzzle, path)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        # Puzzle JSON should be embedded
        assert '"across"' in html
        assert '"down"' in html
        assert '"grid"' in html

    def test_contains_clue_text(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        render_html(minimal_puzzle, path)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        assert "Feline pet" in html
        assert "Drinking vessel" in html

    def test_title_and_subtitle(self, minimal_puzzle, tmp_output):
        cfg = RenderConfig(title="My Crossword", subtitle="Course 101")
        path = os.path.join(tmp_output, "titled.html")
        render_html(minimal_puzzle, path, config=cfg)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        assert "My Crossword" in html
        assert "Course 101" in html

    def test_self_contained_no_external_urls(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        render_html(minimal_puzzle, path)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        # Should not reference any CDN or external resources
        assert "http://" not in html
        assert "https://" not in html

    def test_interactive_elements(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.html")
        render_html(minimal_puzzle, path)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        assert "btn-check" in html
        assert "btn-reveal" in html
        assert "btn-clear" in html
        assert "localStorage" in html

    def test_html_escaping(self, minimal_puzzle, tmp_output):
        cfg = RenderConfig(title='Test <script>alert("xss")</script>')
        path = os.path.join(tmp_output, "escape.html")
        render_html(minimal_puzzle, path, config=cfg)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        # Raw <script> from title must be escaped
        assert '<script>alert("xss")</script>' not in html
        assert "&lt;script&gt;" in html

    def test_sample_puzzle(self, sample_puzzle, tmp_output):
        cfg = RenderConfig(title="Vocabulary Review", subtitle="PSYC 405")
        path = os.path.join(tmp_output, "sample.html")
        render_html(sample_puzzle, path, config=cfg)
        assert os.path.isfile(path)

    def test_creates_parent_dirs(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "nested", "dir", "test.html")
        result = render_html(minimal_puzzle, path)
        assert os.path.isfile(result)
