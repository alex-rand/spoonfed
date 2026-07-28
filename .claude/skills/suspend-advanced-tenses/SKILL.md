---
name: suspend-advanced-tenses
description: Suspend Anki cards tagged with unwanted tenses (conditional, necessitative, past-narrative). Use after generating cards via verb-exploder or any flow that may produce these tense tags. Optional space-separated tag arguments suspend additional tags.
allowed-tools: Bash
argument-hint: [optional extra tag(s)]
---

## What this skill does

Suspends every unsuspended Anki card whose tag is in the skip list via AnkiConnect. Default skip tags:

- `tense::conditional`
- `tense::necessitative`
- `tense::past-narrative`

Any arguments passed to the skill are appended as extra tags to suspend (space-separated, exact match).

## How to run

Anki must be running with AnkiConnect on `localhost:8765`. Run this once — it's the entire skill body:

```bash
python <<'PY'
import json, sys, urllib.request

DEFAULT_TAGS = [
    "tense::conditional",
    "tense::necessitative",
    "tense::past-narrative",
]
EXTRA_TAGS = sys.argv[1:]  # populated from skill arguments

def anki(action, **params):
    payload = json.dumps({"action": action, "params": params, "version": 6}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8765", payload)))
    if r.get("error"): raise Exception(r["error"])
    return r["result"]

total = 0
for tag in DEFAULT_TAGS + EXTRA_TAGS:
    cards = anki("findCards", query=f'tag:"{tag}" -is:suspended')
    if not cards:
        print(f"{tag}: already clean")
        continue
    anki("suspend", cards=cards)
    total += len(cards)
    print(f"{tag}: suspended {len(cards)} card(s)")
print(f"\nTotal newly suspended: {total}")
PY
```

If the user passed arguments, substitute them into the `EXTRA_TAGS` line before running (do not pass via `sys.argv` since the heredoc runs without args). E.g. for `/suspend-tenses tense::aorist polarity::affirmative`, change to:

```python
EXTRA_TAGS = ["tense::aorist", "polarity::affirmative"]
```

## Editing the skip list

To permanently add or remove a default tag, edit `DEFAULT_TAGS` in this file. Keep it tight — this is a per-user opinionated list, not a generic tool.

## Failure modes

- **Connection refused on 8765**: Anki isn't running, or the profile picker is still showing (AnkiConnect only binds after a profile is loaded). Ask the user to open Anki and select their profile.
- **`tag does not exist` errors**: AnkiConnect doesn't error on missing tags — `findCards` just returns `[]`. So "already clean" output is normal for tags that have never been used.
