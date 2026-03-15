# Ankify — Quick Anki Card Capture

This repo lets you capture things you learn as Anki flashcards via YAML files. You create the cards; a separate command (`ankify-all`) pushes them to Anki later.

## Your job as a Claude Code agent

When the user shares something they want to learn or remember, you should:

1. **Read `style-guide.md`** before writing any cards — follow it strictly
2. **Read example cards in `cards/examples/`** to match the user's preferred tone, formatting, and level of detail — these are the gold standard
3. **Distill** the information into clear Q&A pairs. Write in a conversational, first-person tone. Answers can be long — walk through reasoning, include quotes, reference prior knowledge.
4. **Add multilingual flavor** — cards should be primarily in English, but naturally incorporate a sentence or phrase from one or more of: French, Spanish, Mandarin, or Hindi, where it fits. Keep it conversational; don't force it.
5. **Write a YAML card file** to `cards/pending/` following the schema below
6. **Run `ankify-lint`** to validate your file
7. **Commit** the file

**Never run `ankify-all`** — that's for the user to do manually when Anki is open.

## Card file schema

Files go in `cards/pending/` with the naming convention `YYYY-MM-DD-<slug>.yaml`:

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

### Fields

- `cards` (required): array of 1+ cards, each with `front` and `back` strings
- `source` (optional): where the user learned this — for their own reference
- `tags` (optional): become Anki tags on the created cards

### Math notation

Use standard LaTeX delimiters in card text:

- `$...$` for inline math
- `$$...$$` for display/block math

The exporter handles conversion to Anki's format automatically. **Do not** write Anki-native math syntax (`\(...\)` or `\[...\]`).

Example:
```yaml
  - front: "What is the quadratic formula for solving $ax^2 + bx + c = 0$?"
    back: "$$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$"
```

## Validation

After creating a card file, always run:

```bash
ankify-lint cards/pending/<your-file>.yaml
```

Fix any errors before committing. Warnings are informational but worth reviewing.

## Development

```bash
pip install -e ".[dev]"   # install in dev mode
pytest                     # run tests
```
