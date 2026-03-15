"""Tests for CLI entry points (ankify-lint, ankify-all)."""

import shutil
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from ankify.cli import lint_cmd, export_cmd

FIXTURES = Path(__file__).parent / "fixtures"


class TestLintCmd:
    def test_lint_cmd_valid_file_exit_0(self):
        runner = CliRunner()
        result = runner.invoke(lint_cmd, [str(FIXTURES / "valid_basic.yaml")])
        assert result.exit_code == 0
        assert "OK" in result.output

    def test_lint_cmd_invalid_file_exit_1(self):
        runner = CliRunner()
        result = runner.invoke(lint_cmd, [str(FIXTURES / "invalid_missing_front.yaml")])
        assert result.exit_code == 1
        assert "ERROR" in result.output

    def test_lint_cmd_no_files_empty_dir(self, tmp_path):
        """When no files exist in pending dir, prints 'No card files found'."""
        runner = CliRunner()
        with patch("ankify.cli.PENDING_DIR", tmp_path):
            result = runner.invoke(lint_cmd, [])
        assert result.exit_code == 0
        assert "No card files found" in result.output


class TestExportCmd:
    def test_export_cmd_dry_run(self, tmp_path):
        """--dry-run should not call AnkiConnect, and should show summary output."""
        pending = tmp_path / "pending"
        processed = tmp_path / "processed"
        pending.mkdir()
        processed.mkdir()
        shutil.copy(FIXTURES / "valid_basic.yaml", pending / "test.yaml")

        runner = CliRunner()
        with patch("ankify.exporter.PENDING_DIR", pending), \
             patch("ankify.exporter.PROCESSED_DIR", processed), \
             patch("ankify.exporter.anki_connect") as mock_ac:

            result = runner.invoke(export_cmd, ["--dry-run"])

        assert result.exit_code == 0
        assert "DRY RUN" in result.output
        assert "2 cards" in result.output
        mock_ac.add_note.assert_not_called()
