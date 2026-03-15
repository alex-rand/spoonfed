"""Tests for the exporter: math conversion and export pipeline."""

import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from ankify.exporter import convert_math, format_for_anki, export_all

FIXTURES = Path(__file__).parent / "fixtures"


# --- Math conversion ---


class TestConvertMath:
    def test_inline_math(self):
        assert convert_math("The value $x + 1$ is positive.") == r"The value \(x + 1\) is positive."

    def test_display_math(self):
        assert convert_math("$$x = 5$$") == r"\[x = 5\]"

    def test_mixed_math(self):
        result = convert_math("Given $a$, we get $$a^2$$")
        assert result == r"Given \(a\), we get \[a^2\]"

    def test_no_math(self):
        text = "No math here."
        assert convert_math(text) == text

    def test_multiline_display_math(self):
        text = "$$x =\n  5$$"
        assert convert_math(text) == "\\[x =\n  5\\]"

    def test_latex_commands(self):
        result = convert_math("$$\\frac{1}{2}$$")
        assert result == r"\[\frac{1}{2}\]"

    def test_escaped_dollars_not_converted(self):
        """Escaped \\$ should not trigger math mode. Documents known bug if fails."""
        text = r"Price is \$5"
        result = convert_math(text)
        assert result == text, (
            "BUG: convert_math treats escaped \\$ as math delimiter. "
            "Regex should use negative lookbehind for backslash."
        )

    def test_literal_dollar_signs(self):
        """Casual dollar amounts like $5 trigger math mode — documents known limitation."""
        text = "$5 per $10"
        result = convert_math(text)
        # This converts "5 per " into inline math — documenting the limitation
        assert "\\(" in result, (
            "Expected $5 per $10 to be (incorrectly) converted to math mode. "
            "If this fails, the regex was improved to handle non-math dollars."
        )

    def test_empty_display_math(self):
        """$$$$ ideally stays unchanged, but inline regex eats part of it — known bug."""
        result = convert_math("$$$$")
        # BUG: display regex doesn't match (no content between $$ $$),
        # then inline regex matches $<content>$ on the first 3 chars.
        # Ideal behavior would be unchanged, but we document actual behavior:
        assert result == r"\($\)$"

    def test_empty_inline_math(self):
        """$$ alone should not become inline math."""
        assert convert_math("$$") == "$$"


# --- Paragraph formatting ---


class TestFormatForAnki:
    def test_double_newline_becomes_br(self):
        text = "First paragraph.\n\nSecond paragraph."
        assert format_for_anki(text) == "First paragraph.<br><br>Second paragraph."

    def test_triple_newline_becomes_single_br_pair(self):
        text = "First.\n\n\nSecond."
        assert format_for_anki(text) == "First.<br><br>Second."

    def test_single_newline_preserved(self):
        text = "Line one.\nLine two."
        assert format_for_anki(text) == "Line one.\nLine two."

    def test_strips_surrounding_whitespace(self):
        text = "\n\n  Hello world.  \n\n"
        assert format_for_anki(text) == "Hello world."

    def test_no_paragraphs(self):
        text = "Just one paragraph."
        assert format_for_anki(text) == "Just one paragraph."


# --- Export pipeline ---


class TestExportAll:
    def setup_method(self):
        """Create temp directories for each test."""
        self.pending = Path("/tmp/ankify_test_pending")
        self.processed = Path("/tmp/ankify_test_processed")
        self.pending.mkdir(parents=True, exist_ok=True)
        self.processed.mkdir(parents=True, exist_ok=True)

    def teardown_method(self):
        """Clean up temp directories."""
        shutil.rmtree(self.pending, ignore_errors=True)
        shutil.rmtree(self.processed, ignore_errors=True)

    def test_no_files(self):
        files, cards = export_all(
            pending_dir=self.pending, processed_dir=self.processed
        )
        assert files == 0
        assert cards == 0

    def test_dry_run_does_not_call_anki(self):
        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            files, cards = export_all(
                dry_run=True,
                pending_dir=self.pending,
                processed_dir=self.processed,
            )

        assert files == 1
        assert cards == 2
        mock_ac.add_note.assert_not_called()
        # File should still be in pending (dry run doesn't move)
        assert (self.pending / "test.yaml").exists()

    def test_export_moves_files(self):
        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.return_value = 12345

            files, cards = export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

        assert files == 1
        assert cards == 2
        assert not (self.pending / "test.yaml").exists()
        assert (self.processed / "test.yaml").exists()

    def test_export_keep_flag(self):
        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.return_value = 12345

            files, cards = export_all(
                keep=True,
                pending_dir=self.pending,
                processed_dir=self.processed,
            )

        assert files == 1
        assert cards == 2
        assert (self.pending / "test.yaml").exists()

    def test_export_creates_deck_if_missing(self):
        shutil.copy(FIXTURES / "valid_minimal.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Default"]
            mock_ac.add_note.return_value = 12345

            export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

        mock_ac.create_deck.assert_called_once_with("Knowledge Adventure")

    def test_export_sends_correct_tags(self):
        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.return_value = 12345

            export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

        # Should include "ankify" plus file tags
        call_args = mock_ac.add_note.call_args_list
        for call in call_args:
            assert "ankify" in call.kwargs["tags"]
            assert "biology" in call.kwargs["tags"]
            assert "plants" in call.kwargs["tags"]

    def test_export_converts_math(self):
        shutil.copy(FIXTURES / "valid_math.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.return_value = 12345

            export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

        call_args = mock_ac.add_note.call_args_list
        # First card: inline math in front, display math in back
        first_call = call_args[0]
        assert "\\(" in first_call.kwargs["fields"]["Front"]
        assert "\\[" in first_call.kwargs["fields"]["Back"]

    def test_export_aborts_on_lint_errors(self):
        shutil.copy(
            FIXTURES / "invalid_missing_front.yaml", self.pending / "test.yaml"
        )

        with pytest.raises(ValueError, match="Lint errors"):
            export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

    def test_export_no_tags_gets_ankify(self):
        """File with no tags should still get the 'ankify' tag."""
        shutil.copy(FIXTURES / "valid_minimal.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.return_value = 12345

            export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

        call_args = mock_ac.add_note.call_args_list
        for call in call_args:
            assert call.kwargs["tags"] == ["ankify"]

    def test_multiple_files_exported(self):
        """Two files should both be processed with correct card counts."""
        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "a.yaml")
        shutil.copy(FIXTURES / "valid_minimal.yaml", self.pending / "b.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.return_value = 12345

            files, cards = export_all(
                pending_dir=self.pending, processed_dir=self.processed
            )

        assert files == 2
        assert cards == 3  # valid_basic has 2, valid_minimal has 1

    def test_export_anki_connect_failure(self):
        """AnkiConnectError from deck_names should propagate."""
        from ankify.anki_connect import AnkiConnectError

        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.AnkiConnectError = AnkiConnectError
            mock_ac.deck_names.side_effect = AnkiConnectError("Connection refused")

            with pytest.raises(AnkiConnectError, match="Connection refused"):
                export_all(
                    pending_dir=self.pending, processed_dir=self.processed
                )

    def test_export_partial_note_failure(self):
        """If add_note fails on 2nd card, exception propagates and file stays in pending."""
        from ankify.anki_connect import AnkiConnectError

        shutil.copy(FIXTURES / "valid_basic.yaml", self.pending / "test.yaml")

        with patch("ankify.exporter.anki_connect") as mock_ac:
            mock_ac.AnkiConnectError = AnkiConnectError
            mock_ac.deck_names.return_value = ["Knowledge Adventure"]
            mock_ac.add_note.side_effect = [12345, AnkiConnectError("Duplicate")]

            with pytest.raises(AnkiConnectError, match="Duplicate"):
                export_all(
                    pending_dir=self.pending, processed_dir=self.processed
                )

        # File should still be in pending since export failed mid-way
        assert (self.pending / "test.yaml").exists()
