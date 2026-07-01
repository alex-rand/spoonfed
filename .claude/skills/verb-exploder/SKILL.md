---
name: verb-exploder
description: Generate the full conjugation grid (78 sentences for Turkish) of a target verb via the verb-exploder pipeline, with ElevenLabs audio, and push to Anki using the 'Spoonfed Verb Exploder' cloze model. CLI equivalent of the GUI verb-exploder frame. Use when the user wants to drill all conjugations of a specific verb.
allowed-tools: Bash Read
argument-hint: <verb> [--language Turkish] [--model sonnet]
---

## What this skill does

Replicates the verb-exploder GUI flow (`src/verb_exploder_frame.py`) without the GUI:

1. Loads `prompts/verb_exploder/base.yaml` + the language override
2. Calls Claude CLI with the verb to generate the full conjugation grid (78 sentences for Turkish)
3. Adds tense/polarity emojis to each sentence (Turkish only)
4. Generates ElevenLabs audio (slowed 0.75x)
5. Pushes cards to Anki via AnkiConnect into the language's `learned_deck` (looked up from `database.db`), using the `Spoonfed Verb Exploder` cloze model. Each card is tagged with `tense::*`, `person::*`, and `polarity::*` derived from the conjugation label.

## How to run

Anki must be running with AnkiConnect on `localhost:8765`. The script is permanent and lives in this skill directory — just invoke it with the verb:

```bash
python .claude/skills/verb-exploder/run.py <verb>
```

For non-default options:

```bash
python .claude/skills/verb-exploder/run.py gelmek --language Turkish --model sonnet
```

The script accepts:
- positional `verb` (required) — the infinitive, e.g. `gelmek`, `yapmak`, `okumak`
- `--language` (default `Turkish`)
- `--model` (default `sonnet`; pass `opus` for higher quality / slower, `haiku` for cheaper / lower quality)
- `--profile` (default `Alex`) — Anki profile name, used by the audio function
- `--no-vocab` — skip the known-vocab injection (default behavior is to sample ~150 known words from the learned deck and prefer them in generated sentences, mirroring the GUI's checkbox)

Expected runtime: ~2-4 minutes total (Claude generation ~1-2 min, then ElevenLabs audio for 78 sentences ~1-2 min).

## After the run

Following each run, suggest the user invoke `/suspend-advanced-tenses` to suspend the conditional / imperative / necessitative / past-narrative cards that were just created — that workflow is the established companion to verb-exploder.

## Failure modes

- **`Anki model 'Spoonfed Verb Exploder' not found`**: the cloze model hasn't been created yet. Open the Spoonfed GUI once and trigger verb-exploder so the model is registered, then re-run.
- **`Connection refused on 8765`**: Anki isn't running, or the profile picker is still showing. AnkiConnect only binds the port after a profile is loaded.
- **No `language_configurations` row**: the requested `--language` isn't configured in `database.db`. Use `Turkish` (the default) or add a configuration first via the GUI.
- **Vocab injection**: enabled by default — the script pulls the same card-type/field configuration the GUI uses from `database.db`, fetches notes from Anki, strips HTML/cloze and non-language characters, tokenizes, and samples ~150 known words to inject into the prompt as a soft preference (same logic as `src/decks_homepage.py::load_vocab_from_deck`). Pass `--no-vocab` to disable.

## Notes

- This skill writes no temporary files. The script is permanent; no cleanup needed.
- Output is non-deterministic across runs (the LLM varies sentences each call), so re-running on the same verb produces new cards rather than duplicates of existing ones.
