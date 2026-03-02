# Plan: `ankify` — A repo for quick Anki card capture via Claude Code

## Problem

As you learn things throughout the day, you want to tell Claude Code what you learned and have it create a structured file. Later, at your computer with Anki open, you run one command (`ankify-all`) to push all pending cards into your "Knowledge Adventure" deck. No LLM needed at export time — the files are the source of truth.

---

## Design Decisions

### File format: YAML

YAML is the right choice here because:
- Strictly parseable without any LLM interpretation
- Handles multiline text naturally (for longer answers)
- Human-readable if you ever want to review/edit cards before ankifying
- Well-supported by Python's standard ecosystem (`pyyaml` / `strictyaml`)

Each file represents one learning session or topic and holds one or more cards:

```yaml
# cards/pending/2026-03-01-photosynthesis.yaml
source: "Wikipedia article on photosynthesis"
tags:
  - biology
  - plants
cards:
  - front: "What is the primary pigment used in photosynthesis?"
    back: "Chlorophyll — it absorbs light primarily in blue and red wavelengths."
  - front: "In which cellular organelle does photosynthesis take place?"
    back: "Chloroplasts."
```

**Field rules:**
- `cards` (required): array of 1+ cards, each with `front` and `back` strings
- `source` (optional): where you learned this — purely for your own reference
- `tags` (optional): become Anki tags on the created cards (plus an auto-added `ankify` tag)

**File naming convention:** `YYYY-MM-DD-<slug>.yaml` — the date and a short kebab-case topic name. Claude Code generates this automatically.

### Card model: Anki's built-in "Basic"

No custom model needed. The built-in "Basic" model has `Front` and `Back` fields, which maps 1:1 to the YAML. This means zero Anki setup — the deck and model just work.

### Tracking processed files: move to `processed/`

After `ankify-all` successfully exports a file's cards, it moves the file from `cards/pending/` to `cards/processed/`. This is:
- Visible (you can see what's been done via `ls` or git status)
- Simple (no state database)
- Recoverable (files aren't deleted, just moved)
- Git-friendly (the move shows up as a rename in diffs)

---

## Repo Structure

```
ankify/
├── CLAUDE.md                      # Instructions for Claude Code agents
├── style-guide.md                 # Your preferences for card writing
├── cards/
│   ├── pending/                   # New card files land here
│   │   └── .gitkeep
│   └── processed/                 # Successfully ankified files move here
│       └── .gitkeep
├── src/
│   └── ankify/
│       ├── __init__.py
│       ├── cli.py                 # CLI entry points (ankify-all, ankify-lint)
│       ├── lint.py                # Card file validator
│       ├── exporter.py            # AnkiConnect integration + export logic
│       └── anki_connect.py        # Thin AnkiConnect HTTP client
├── tests/
│   ├── test_lint.py
│   ├── test_exporter.py
│   └── fixtures/                  # Sample valid/invalid YAML for tests
│       ├── valid_basic.yaml
│       ├── invalid_missing_front.yaml
│       └── ...
└── pyproject.toml                 # Package metadata, CLI entry points, deps
```

---

## Component Details

### 1. `CLAUDE.md` — Agent instructions

This is what a future Claude Code session reads automatically. It tells the agent:

1. **What this repo is for** — quick Anki card capture
2. **How to create a card file** — exact YAML schema, naming convention, where to put it (`cards/pending/`)
3. **To read `style-guide.md`** before writing any cards — and follow it strictly
4. **To run `ankify-lint`** after creating a file to validate it
5. **Never to run `ankify-all`** — that's for you to do manually when Anki is open

Key instruction: when the user shares something they want to learn, Claude Code should distill it into clear Q&A pairs following the style guide, write the YAML file, lint it, and commit.

### 2. `style-guide.md` — Your card writing preferences

A living document where you enshrine how you want cards written. Structured as:

- **Principles** — e.g., minimum information principle (one atomic fact per card), no yes/no questions, prefer "why/how" over "what"
- **Question style** — phrasing patterns, tense, specificity level
- **Answer style** — length, whether to include context, formatting
- **Good examples** — 5-10 exemplary cards showing ideal style
- **Bad examples** — common anti-patterns with explanations of what's wrong
- **Domain-specific rules** — any per-topic preferences (e.g., "for programming cards, always include a short code snippet in the answer")

This file starts as a template with sensible defaults. You edit it over time as your preferences crystallize. Claude Code reads it every time it generates cards.

### 3. `ankify-lint` — The card file linter

A CLI command that validates card files. Checks:

| Check | Severity | Description |
|---|---|---|
| Valid YAML | Error | File must parse as valid YAML |
| `cards` array exists | Error | Top-level `cards` key must be a non-empty list |
| Each card has `front` | Error | Every card must have a non-empty `front` string |
| Each card has `back` | Error | Every card must have a non-empty `back` string |
| `front` ends with `?` | Warning | Questions should end with a question mark |
| `back` not too long | Warning | Answers over 300 characters may be too verbose |
| `tags` is a list of strings | Error | If present, `tags` must be a string list |
| `source` is a string | Error | If present, `source` must be a string |
| No extra top-level keys | Warning | Catch typos in field names |

Usage:
```bash
ankify-lint                          # lint all files in cards/pending/
ankify-lint cards/pending/foo.yaml   # lint a specific file
```

Exit code 0 = all pass, 1 = errors found. This makes it usable as:
- A Claude Code hook (auto-runs after file creation)
- A pre-commit hook
- A CI check

### 4. `ankify-all` — The export command

The single command you run at your computer:

```bash
ankify-all
```

Steps:
1. Scan `cards/pending/` for `*.yaml` files
2. Lint every file — abort with report if any have errors
3. Connect to AnkiConnect at `http://127.0.0.1:8765` — abort with clear message if Anki isn't running
4. Ensure the "Knowledge Adventure" deck exists (create via `createDeck` if not)
5. For each file, for each card:
   - Call `addNote` with `deckName: "Knowledge Adventure"`, `modelName: "Basic"`, `fields: {Front: ..., Back: ...}`, `tags: [ankify, ...file_tags]`
6. Move the file from `cards/pending/` to `cards/processed/`
7. Print summary: `✓ 3 files processed, 12 cards created`

Flags:
- `--dry-run`: validate and show what would be created, but don't touch Anki
- `--keep`: don't move files to processed (useful for testing)

### 5. `anki_connect.py` — Thin AnkiConnect client

Stripped-down version of spoonfed's client. No PyQt5 dependency. Just:

```python
def invoke(action: str, **params) -> Any:
    """Send a request to AnkiConnect. Raises on error."""

def add_note(deck: str, model: str, fields: dict, tags: list[str]) -> int:
    """Create a single note. Returns note ID."""

def deck_names() -> list[str]:
    """List existing deck names."""

def create_deck(name: str) -> int:
    """Create a deck if it doesn't exist."""
```

### 6. Claude Code hook (optional but recommended)

A `.claude/hooks.json` entry that auto-runs the linter after any file write to `cards/pending/`:

```json
{
  "hooks": {
    "afterWrite": [
      {
        "match": "cards/pending/*.yaml",
        "command": "ankify-lint $FILE"
      }
    ]
  }
}
```

This gives the agent immediate feedback if it produced a malformed file.

---

## Dependencies

Minimal:
- `pyyaml` — YAML parsing
- `click` — CLI framework
- Python 3.10+ (for modern type hints)

No pandas, no PyQt5, no OpenAI SDK — this repo is intentionally lightweight since it's a data pipeline, not a generator.

---

## Implementation Order

1. **Scaffold the repo** — `pyproject.toml`, directory structure, `.gitkeep` files
2. **`anki_connect.py`** — the thin client (can test against a running Anki)
3. **`lint.py`** + `ankify-lint` CLI — the validator, with tests using fixture files
4. **`exporter.py`** + `ankify-all` CLI — the export pipeline, with `--dry-run` support
5. **`CLAUDE.md`** — agent instructions referencing the schema and style guide
6. **`style-guide.md`** — initial template with sensible defaults (you'll customize)
7. **Tests** — lint tests with valid/invalid fixtures, exporter tests with mocked AnkiConnect
8. **Hook setup** — `.claude/hooks.json` for auto-linting
