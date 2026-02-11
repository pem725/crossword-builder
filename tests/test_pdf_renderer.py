"""Tests for PDF renderer."""

import os

import pytest

from src.crossword.renderers._base import RenderConfig
from src.crossword.renderers.pdf_renderer import render_pdf


class TestRenderPdf:
    def test_creates_file(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.pdf")
        result = render_pdf(minimal_puzzle, path)
        assert os.path.isfile(result)

    def test_returns_absolute_path(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.pdf")
        result = render_pdf(minimal_puzzle, path)
        assert os.path.isabs(result)

    def test_pdf_header(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "test.pdf")
        render_pdf(minimal_puzzle, path)
        with open(path, "rb") as f:
            header = f.read(5)
        assert header == b"%PDF-"

    def test_with_title_and_subtitle(self, minimal_puzzle, tmp_output):
        cfg = RenderConfig(title="Chapter 5 Review", subtitle="PSYC 405")
        path = os.path.join(tmp_output, "titled.pdf")
        render_pdf(minimal_puzzle, path, config=cfg)
        assert os.path.isfile(path)
        assert os.path.getsize(path) > 0

    def test_no_answer_key(self, minimal_puzzle, tmp_output):
        path_with = os.path.join(tmp_output, "with_key.pdf")
        path_without = os.path.join(tmp_output, "no_key.pdf")
        render_pdf(minimal_puzzle, path_with, include_key=True)
        render_pdf(minimal_puzzle, path_without, include_key=False)
        # PDF with key should be larger
        assert os.path.getsize(path_with) > os.path.getsize(path_without)

    def test_sample_puzzle(self, sample_puzzle, tmp_output):
        cfg = RenderConfig(title="Vocabulary Review", subtitle="PSYC 405")
        path = os.path.join(tmp_output, "sample.pdf")
        render_pdf(sample_puzzle, path, config=cfg)
        assert os.path.isfile(path)

    def test_creates_parent_dirs(self, minimal_puzzle, tmp_output):
        path = os.path.join(tmp_output, "nested", "dir", "test.pdf")
        result = render_pdf(minimal_puzzle, path)
        assert os.path.isfile(result)
