"""Integration tests: end-to-end pipeline through all renderers."""

import os

import pytest

from src.crossword import generate_crossword, render, render_all
from src.crossword.renderers import RenderConfig


class TestRenderDispatch:
    def test_render_png(self, sample_puzzle, tmp_output):
        path = render(sample_puzzle, "png", os.path.join(tmp_output, "out.png"))
        assert os.path.isfile(path)

    def test_render_pdf(self, sample_puzzle, tmp_output):
        path = render(sample_puzzle, "pdf", os.path.join(tmp_output, "out.pdf"))
        assert os.path.isfile(path)

    def test_render_html(self, sample_puzzle, tmp_output):
        path = render(sample_puzzle, "html", os.path.join(tmp_output, "out.html"))
        assert os.path.isfile(path)

    def test_render_unknown_format_raises(self, sample_puzzle, tmp_output):
        with pytest.raises(ValueError, match="Unknown format"):
            render(sample_puzzle, "docx", os.path.join(tmp_output, "out.docx"))

    def test_render_with_title(self, sample_puzzle, tmp_output):
        path = render(
            sample_puzzle,
            "html",
            os.path.join(tmp_output, "titled.html"),
            title="Chapter 5",
            subtitle="PSYC 405",
        )
        with open(path, "r") as f:
            assert "Chapter 5" in f.read()


class TestRenderAll:
    def test_produces_all_files(self, sample_puzzle, tmp_output):
        files = render_all(sample_puzzle, str(tmp_output), basename="ch5")
        assert set(files.keys()) == {"png", "png_key", "pdf", "html"}
        for path in files.values():
            assert os.path.isfile(path), f"Missing: {path}"

    def test_basenames_correct(self, sample_puzzle, tmp_output):
        files = render_all(sample_puzzle, str(tmp_output), basename="week03")
        assert files["png"].endswith("week03.png")
        assert files["png_key"].endswith("week03_key.png")
        assert files["pdf"].endswith("week03.pdf")
        assert files["html"].endswith("week03.html")

    def test_with_config(self, sample_puzzle, tmp_output):
        cfg = RenderConfig(title="Motivation", subtitle="PSYC 405")
        files = render_all(sample_puzzle, str(tmp_output), config=cfg)
        for path in files.values():
            assert os.path.isfile(path)


class TestEndToEnd:
    """Full pipeline: generate puzzle → render all formats."""

    def test_pipeline(self, tmp_output):
        words = ["NEURON", "SYNAPSE", "CORTEX", "AXON", "GLIA"]
        clues = {
            "NEURON": "Nerve cell",
            "SYNAPSE": "Junction between nerve cells",
            "CORTEX": "Outer layer of the brain",
            "AXON": "Long nerve fiber",
            "GLIA": "Support cells in the brain",
        }
        puzzle = generate_crossword(words, clues, grid_size=12)
        assert puzzle is not None

        files = render_all(
            puzzle,
            str(tmp_output),
            basename="neuro_review",
            title="Neuroscience Review",
            subtitle="PSYC 405",
        )
        assert len(files) == 4
        for path in files.values():
            assert os.path.isfile(path)
            assert os.path.getsize(path) > 0
