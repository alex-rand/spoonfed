# Plan: Make Anki deck name configurable

## Current state

The deck name `"Knowledge Adventure"` is hard-coded in `src/ankify/exporter.py:12` as `DECK_NAME`. It's used in `export_all()` to create the deck and add notes. There's no way for a user to override it.

## Approach: per-file `deck` field in YAML

Allow an optional `deck` field in each card YAML file. Different card files can target different decks. The existing hard-coded value (`"Knowledge Adventure"`) becomes the default when `deck` is not specified.

### Why per-file YAML field (vs CLI flag or config file)

- **Per-file**: Different topics can go to different decks naturally. The deck travels with the card file — no ambiguity.
- **CLI `--deck` flag**: Would override all files uniformly — less flexible, but could be added later as an additional override.
- **Config file**: Adds complexity for a single setting. Overkill for now.

## Changes

### 1. `src/ankify/lint.py`
- Add `"deck"` to `ALLOWED_TOP_LEVEL_KEYS` (line 9): `{"cards", "source", "tags", "deck"}`
- Add validation after the `tags` block (~line 123): if `deck` is present, it must be a non-empty string

### 2. `src/ankify/exporter.py`
- Keep `DECK_NAME` as the default fallback
- In `export_all()`, read `deck = data.get("deck", DECK_NAME)` per file (around line 85)
- Move deck existence check inside the per-file loop — track which decks have been ensured with a set, create each unique deck only once
- Use the per-file `deck` variable in the `add_note()` call instead of `DECK_NAME`

### 3. `CLAUDE.md`
- Add `deck` to the "Fields" documentation as optional, with description and default

### 4. Test fixtures
- Add `tests/fixtures/valid_with_deck.yaml` — valid file with a `deck` field
- Add `tests/fixtures/invalid_bad_deck.yaml` — file where `deck` is not a string (e.g., a list)

### 5. `tests/test_lint.py`
- Test: valid file with `deck` produces no errors/warnings
- Test: invalid `deck` value produces an error

### 6. `tests/test_exporter.py`
- Test: `export_all` uses per-file deck name when `deck` is specified in YAML
- Test: default deck is used when `deck` is omitted
