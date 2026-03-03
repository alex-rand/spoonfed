"""Export pipeline: lint, convert math, push to Anki via AnkiConnect, move files."""

import re
import shutil
from pathlib import Path

import yaml

from ankify import anki_connect
from ankify.lint import lint_files

DECK_NAME = "Knowledge Adventure"
MODEL_NAME = "Basic"
PENDING_DIR = Path("cards/pending")
PROCESSED_DIR = Path("cards/processed")


def convert_math(text: str) -> str:
    """Convert LaTeX math delimiters to Anki MathJax syntax.

    $$...$$ → \\[...\\]  (display math, converted first)
    $...$   → \\(...\\)  (inline math)
    """
    # Display math first (greedy would eat too much, use non-greedy)
    text = re.sub(r"\$\$(.+?)\$\$", r"\\[\1\\]", text, flags=re.DOTALL)
    # Inline math
    text = re.sub(r"\$(.+?)\$", r"\\(\1\\)", text, flags=re.DOTALL)
    return text


def export_all(
    dry_run: bool = False,
    keep: bool = False,
    pending_dir: Path | None = None,
    processed_dir: Path | None = None,
) -> tuple[int, int]:
    """Export all pending card files to Anki.

    Returns (files_processed, cards_created).
    """
    pending = pending_dir or PENDING_DIR
    processed = processed_dir or PROCESSED_DIR

    yaml_files = sorted(pending.glob("*.yaml"))
    if not yaml_files:
        return 0, 0

    # Lint all files first
    results = lint_files(yaml_files)
    errors = [r for r in results if r.has_errors]
    if errors:
        lines = []
        for r in errors:
            lines.append(f"\n{r.file}:")
            for m in r.messages:
                lines.append(str(m))
        raise ValueError("Lint errors found, aborting export:" + "\n".join(lines))

    if not dry_run:
        # Verify AnkiConnect is reachable and ensure deck exists
        try:
            decks = anki_connect.deck_names()
        except anki_connect.AnkiConnectError:
            raise

        if DECK_NAME not in decks:
            anki_connect.create_deck(DECK_NAME)

    files_processed = 0
    cards_created = 0

    for yaml_file in yaml_files:
        with open(yaml_file) as f:
            data = yaml.safe_load(f)

        file_tags = ["ankify"] + data.get("tags", [])

        for card in data["cards"]:
            front = convert_math(card["front"])
            back = convert_math(card["back"])

            if not dry_run:
                anki_connect.add_note(
                    deck=DECK_NAME,
                    model=MODEL_NAME,
                    fields={"Front": front, "Back": back},
                    tags=file_tags,
                )
            cards_created += 1

        files_processed += 1

        if not dry_run and not keep:
            dest = processed / yaml_file.name
            shutil.move(str(yaml_file), str(dest))

    return files_processed, cards_created
