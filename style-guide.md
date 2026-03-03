# Card Style Guide

Read this before writing any Anki cards. Follow these guidelines strictly.

## Principles

1. **Minimum information principle** — one atomic fact per card. If a card tests two things, split it into two cards.
2. **No yes/no questions** — they're too easy to guess. Ask "what", "why", "how", or "which" instead.
3. **Prefer "why/how" over "what"** — understanding beats memorization.
4. **Be specific** — vague questions produce vague recall.
5. **Context in the question** — don't rely on the answer to provide the context that makes the question make sense.

## Question style

- Write as a direct question ending with `?`
- Include enough context that the question stands on its own
- Use present tense unless asking about a historical event
- Name the domain if it's ambiguous (e.g., "In Python, ..." or "In organic chemistry, ...")

## Answer style

- Keep answers concise — ideally under 2 sentences
- Lead with the core answer, then add brief context if helpful
- Use an em dash (—) to separate the core answer from elaboration
- For programming cards, include a short code snippet when it clarifies
- For math, use LaTeX: `$...$` for inline, `$$...$$` for display

## Good examples

```yaml
  - front: "Why does Python use indentation instead of braces for block structure?"
    back: "To enforce readable code — Guido van Rossum believed that code is read more often than written."

  - front: "What is the time complexity of lookup in a Python dictionary?"
    back: "O(1) average case — dictionaries use hash tables internally."

  - front: "In calculus, what does the derivative of a function represent geometrically?"
    back: "The slope of the tangent line to the function's curve at a given point."

  - front: "What is the difference between TCP and UDP?"
    back: "TCP is connection-oriented and guarantees delivery order; UDP is connectionless and faster but unreliable."

  - front: "Why do red blood cells lack a nucleus in mammals?"
    back: "To maximize space for hemoglobin — this increases oxygen-carrying capacity."
```

## Bad examples

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

  # BAD: Answer is too long / not concise
  - front: "What is recursion?"
    back: "Recursion is a programming technique where a function calls itself in order to solve a problem. It works by breaking down a complex problem into smaller, more manageable subproblems. Each recursive call works on a smaller version of the original problem until it reaches a base case, which is a simple enough case that can be solved directly without further recursion."

  # BAD: No context in the question
  - front: "What does it do?"
    back: "Converts glucose to ATP."
```

## Domain-specific rules

- **Programming**: always include a short code snippet in the answer when it would clarify
- **Math/Science**: use LaTeX notation for formulas (`$...$` or `$$...$$`)
- **Languages**: include the original language text alongside translations
- **History**: include the approximate date or time period in the question
