# Card Style Guide

Read this before writing any Anki cards. Follow these guidelines strictly.

**Before writing cards, also review the example files in `cards/examples/`.** These are real cards written by the user and represent the target style, tone, and formatting. When in doubt, match the examples over the abstract rules below.

## Principles

1. **Minimum information principle** — one atomic fact per card. If a card tests two things, split it into two cards.
2. **No yes/no questions** — they're too easy to guess. Ask "what", "why", "how", or "which" instead.
3. **Prefer "why/how" over "what"** — understanding beats memorization.
4. **Be specific** — vague questions produce vague recall.
5. **Context in the question** — don't rely on the answer to provide the context that makes the question make sense.
6. **Multilingual reinforcement** — the user reads English, French, Spanish, Mandarin, and Hindi. Cards should be primarily in English, but naturally incorporate a sentence or phrase from one or more of these other languages where it fits (e.g. a relevant term in its original language, a short aside, a translation of a key concept). Keep it in a simple conversational register — don't force it.

## Question style

- Write as a direct question ending with `?`
- Include enough context that the question stands on its own
- Use present tense unless asking about a historical event
- Name the domain if it's ambiguous (e.g., "In Python, ..." or "In organic chemistry, ...")

## Answer style

- **No length limit** — answers can be as long as they need to be. Short and punchy is fine; walking through a full proof or derivation step-by-step is also fine. Match the complexity of the material.
- Write in a **conversational, first-person tone** — "I think the basic thing is", "the thing to notice is", "See?", "we've already shown". The cards are for the user, not a textbook.
- Lead with the core answer, then elaborate as needed
- Use an em dash (—) to separate the core answer from elaboration
- **Quotes and attributions** are welcome when they add value
- **Reference prior knowledge** freely — "we've seen how...", "recall that..."
- For programming cards, include a short code snippet when it clarifies
- For math, use LaTeX: `$...$` for inline, `$$...$$` for display

## Examples

See `cards/examples/` for the canonical reference. Those are real cards written by the user and override anything here.

## Anti-patterns

```yaml
  # BAD: Yes/no question
  - front: "Is Python dynamically typed?"
    back: "Yes."

  # BAD: Too vague
  - front: "What is a tree?"
    back: "A data structure."

  # BAD: Tests two facts
  - front: "What is the capital of France and what is its population?"
    back: "Paris, with a population of about 2.1 million."

  # BAD: Dry textbook voice instead of conversational
  - front: "What is recursion?"
    back: "Recursion is a programming technique where a function calls itself in order to solve a problem. It works by breaking down a complex problem into smaller, more manageable subproblems."

  # BAD: No context in the question
  - front: "What does it do?"
    back: "Converts glucose to ATP."
```

## Domain-specific rules

- **Programming**: always include a short code snippet in the answer when it would clarify
- **Math/Science**: use LaTeX notation for formulas (`$...$` or `$$...$$`). Proofs and derivations should be written out step-by-step.
- **Languages**: include the original language text alongside translations
- **History**: include the approximate date or time period in the question
- **Religion/Philosophy**: direct quotes from primary texts are encouraged
