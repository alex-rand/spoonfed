"""Card file validator. Checks YAML structure, fields, and math delimiters."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ALLOWED_TOP_LEVEL_KEYS = {"cards", "source", "tags"}
MAX_BACK_LENGTH = 300


@dataclass
class LintMessage:
    file: str
    message: str
    severity: str  # "error" or "warning"

    def __str__(self) -> str:
        tag = "ERROR" if self.severity == "error" else "WARNING"
        return f"  [{tag}] {self.message}"


@dataclass
class LintResult:
    file: str
    messages: list[LintMessage] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(m.severity == "error" for m in self.messages)

    @property
    def has_warnings(self) -> bool:
        return any(m.severity == "warning" for m in self.messages)

    def error(self, message: str) -> None:
        self.messages.append(LintMessage(self.file, message, "error"))

    def warning(self, message: str) -> None:
        self.messages.append(LintMessage(self.file, message, "warning"))


def _check_math_delimiters(text: str, field_name: str, card_num: int, result: LintResult) -> None:
    """Check that math delimiters are balanced and not nested incorrectly."""
    # Check for raw Anki math syntax
    if re.search(r"(?<!\\)\\[(\[]", text) or re.search(r"(?<!\\)\\[)\]]", text):
        result.warning(
            f"Card {card_num} {field_name}: contains raw Anki math syntax "
            f"(\\(, \\), \\[, \\]). Use $...$ or $$...$$ instead."
        )

    # Check balanced $$ (display math) first, then $ (inline math)
    # We need to handle $$ before $ since $$ contains $
    # Strategy: find all $ positions, pair up $$ first, then single $
    positions = [m.start() for m in re.finditer(r"\$", text)]
    if not positions:
        return

    # Group consecutive $ pairs as $$
    i = 0
    tokens = []  # list of (position, type) where type is "$" or "$$"
    while i < len(positions):
        if i + 1 < len(positions) and positions[i + 1] == positions[i] + 1:
            tokens.append((positions[i], "$$"))
            i += 2
        else:
            tokens.append((positions[i], "$"))
            i += 1

    # Check that delimiters are balanced and not nested
    stack: list[str] = []
    for pos, token_type in tokens:
        if not stack:
            stack.append(token_type)
        elif stack[-1] == token_type:
            stack.pop()
        else:
            # Nesting: e.g. $$ inside $ or $ inside $$
            result.error(
                f"Card {card_num} {field_name}: nested math delimiters "
                f"at position {pos}. Do not nest $ inside $$ or vice versa."
            )
            return

    if stack:
        result.error(
            f"Card {card_num} {field_name}: unbalanced math delimiter "
            f"'{stack[-1]}' — missing closing delimiter."
        )


def lint_file(path: Path) -> LintResult:
    """Lint a single card YAML file. Returns a LintResult with any issues found."""
    result = LintResult(file=str(path))

    # Parse YAML
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        result.error(f"Invalid YAML: {e}")
        return result

    if not isinstance(data, dict):
        result.error("File must contain a YAML mapping at the top level.")
        return result

    # Check for extra top-level keys
    extra_keys = set(data.keys()) - ALLOWED_TOP_LEVEL_KEYS
    if extra_keys:
        result.warning(f"Unexpected top-level keys: {', '.join(sorted(extra_keys))}")

    # Validate source
    if "source" in data and not isinstance(data["source"], str):
        result.error("`source` must be a string.")

    # Validate tags
    if "tags" in data:
        if not isinstance(data["tags"], list) or not all(
            isinstance(t, str) for t in data["tags"]
        ):
            result.error("`tags` must be a list of strings.")

    # Validate cards
    if "cards" not in data:
        result.error("Missing required `cards` key.")
        return result

    cards = data["cards"]
    if not isinstance(cards, list) or len(cards) == 0:
        result.error("`cards` must be a non-empty list.")
        return result

    for i, card in enumerate(cards, start=1):
        if not isinstance(card, dict):
            result.error(f"Card {i}: must be a mapping with `front` and `back` keys.")
            continue

        # front
        front = card.get("front")
        if not front or not isinstance(front, str) or not front.strip():
            result.error(f"Card {i}: missing or empty `front`.")
        else:
            if not front.rstrip().endswith("?"):
                result.warning(f"Card {i}: `front` does not end with a question mark.")
            _check_math_delimiters(front, "front", i, result)

        # back
        back = card.get("back")
        if not back or not isinstance(back, str) or not back.strip():
            result.error(f"Card {i}: missing or empty `back`.")
        else:
            if len(back) > MAX_BACK_LENGTH:
                result.warning(
                    f"Card {i}: `back` is {len(back)} characters "
                    f"(>{MAX_BACK_LENGTH}). Consider making it more concise."
                )
            _check_math_delimiters(back, "back", i, result)

    return result


def lint_files(paths: list[Path]) -> list[LintResult]:
    """Lint multiple card files. Returns a list of LintResults."""
    return [lint_file(p) for p in paths]
