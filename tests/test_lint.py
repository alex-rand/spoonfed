"""Tests for the card file linter."""

from pathlib import Path

from ankify.lint import lint_file

FIXTURES = Path(__file__).parent / "fixtures"


# --- Valid files (no errors) ---


def test_valid_basic():
    result = lint_file(FIXTURES / "valid_basic.yaml")
    assert not result.has_errors
    assert not result.has_warnings


def test_valid_minimal():
    result = lint_file(FIXTURES / "valid_minimal.yaml")
    assert not result.has_errors


def test_valid_math():
    result = lint_file(FIXTURES / "valid_math.yaml")
    assert not result.has_errors
    assert not result.has_warnings


# --- Error cases ---


def test_invalid_bad_yaml():
    result = lint_file(FIXTURES / "invalid_bad_yaml.yaml")
    assert result.has_errors
    assert any("Invalid YAML" in m.message for m in result.messages)


def test_invalid_missing_cards():
    result = lint_file(FIXTURES / "invalid_missing_cards.yaml")
    assert result.has_errors
    assert any("`cards`" in m.message for m in result.messages)


def test_invalid_empty_cards():
    result = lint_file(FIXTURES / "invalid_empty_cards.yaml")
    assert result.has_errors
    assert any("non-empty" in m.message for m in result.messages)


def test_invalid_missing_front():
    result = lint_file(FIXTURES / "invalid_missing_front.yaml")
    assert result.has_errors
    assert any("`front`" in m.message for m in result.messages)


def test_invalid_missing_back():
    result = lint_file(FIXTURES / "invalid_missing_back.yaml")
    assert result.has_errors
    assert any("`back`" in m.message for m in result.messages)


def test_invalid_bad_tags():
    result = lint_file(FIXTURES / "invalid_bad_tags.yaml")
    assert result.has_errors
    assert any("`tags`" in m.message for m in result.messages)


def test_invalid_bad_source():
    result = lint_file(FIXTURES / "invalid_bad_source.yaml")
    assert result.has_errors
    assert any("`source`" in m.message for m in result.messages)


# --- Warning cases ---


def test_warning_no_question_mark():
    result = lint_file(FIXTURES / "warning_no_question_mark.yaml")
    assert not result.has_errors
    assert result.has_warnings
    assert any("question mark" in m.message for m in result.messages)


def test_warning_extra_keys():
    result = lint_file(FIXTURES / "warning_extra_keys.yaml")
    assert not result.has_errors
    assert result.has_warnings
    assert any("Unexpected top-level" in m.message for m in result.messages)


def test_warning_long_back():
    result = lint_file(FIXTURES / "warning_long_back.yaml")
    assert not result.has_errors
    assert result.has_warnings
    assert any("characters" in m.message for m in result.messages)


# --- Math delimiter checks ---


def test_invalid_unbalanced_math():
    result = lint_file(FIXTURES / "invalid_unbalanced_math.yaml")
    assert result.has_errors
    assert any("unbalanced" in m.message for m in result.messages)


def test_invalid_nested_math():
    result = lint_file(FIXTURES / "invalid_nested_math.yaml")
    assert result.has_errors
    assert any("nested" in m.message for m in result.messages)


def test_warning_raw_anki_math():
    result = lint_file(FIXTURES / "warning_raw_anki_math.yaml")
    assert result.has_warnings
    assert any("raw Anki math" in m.message for m in result.messages)
