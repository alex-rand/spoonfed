---
name: generate-bespoke-cards
description: Generate bespoke Anki flashcards with ElevenLabs audio for any language configuration. Use when the user wants to create custom cards outside the GUI app.
allowed-tools: Bash Read Write Edit Grep Glob
argument-hint: [language] [topic/word/instruction]
---

## What this skill does

Generates custom Anki flashcards by:
1. Generating sentences via the Claude CLI
2. Creating ElevenLabs TTS audio (slowed to 0.75x)
3. Pushing finished cards to Anki via AnkiConnect (must be running on localhost:8765)

## Project location

The project lives at the current working directory. Key files:
- `src/utils/audio_generating_functions.py` — `generate_audio(df, language, profile, tts_api)` handles TTS
- `src/utils/anki_connect_functions.py` — reference for AnkiConnect patterns
- `.env` — contains `ELEVENLABS_API_KEY`
- `adhoc_generate.py` — reference script showing the full workflow

## How to generate cards

Write and run a Python script in the project root. Use this template:

```python
"""Ad-hoc card generation script."""
import os, sys, json, subprocess, re, csv, io, urllib.request
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from utils.audio_generating_functions import generate_audio

def anki_invoke(action, **params):
    payload = json.dumps({"action": action, "params": params, "version": 6}).encode("utf-8")
    response = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8765", payload)))
    if response.get("error"):
        raise Exception(response["error"])
    return response["result"]

# ── CONFIG (adjust per request) ─────────────────────────────────────
LANGUAGE = "$0"           # e.g. "Turkish", "Hindi", "French"
DECK_NAME = "..."         # Anki deck name
ANKI_MODEL = "..."        # Anki note type
ANKI_PROFILE = "Alex"
AUDIO_SOURCE = "ElevenLabs"

# ── STEP 1: Look up config from database ────────────────────────────
# Query database.db for the language configuration:
#   sqlite3 database.db "SELECT * FROM language_configurations WHERE configuration_language = '<LANGUAGE>'"
# This gives: id | user_id | config_name | language | learned_deck | new_deck
# Use learned_deck as DECK_NAME.
#
# Then determine the Anki model by checking EXPORT_CONFIG in src/iplusone.py
# or querying AnkiConnect: anki_invoke("modelNames")

# ── STEP 2: Generate sentences via Claude CLI ───────────────────────
prompt = """<Describe what sentences to generate. Include language, constraints, 
and CSV output format: sentence,translation,new_word>"""

result = subprocess.run(
    ["claude", "-p", "--model", "haiku", "--output-format", "json"],
    input=prompt, capture_output=True, text=True,
)
if result.returncode != 0:
    raise RuntimeError(f"Claude CLI error: {result.stderr}")

text = json.loads(result.stdout)["result"].strip()
text = re.sub(r'^```(?:csv)?\n', '', text)
text = re.sub(r'\n```$', '', text)

data = list(csv.reader(io.StringIO(text)))
df = pd.DataFrame(data[1:], columns=data[0])
print(df.to_string(index=False))

# ── STEP 3: Generate audio ──────────────────────────────────────────
df = generate_audio(df, LANGUAGE, ANKI_PROFILE, AUDIO_SOURCE)

# ── STEP 4: Push to Anki ────────────────────────────────────────────
for _, row in df.iterrows():
    note = {
        "deckName": DECK_NAME,
        "modelName": ANKI_MODEL,
        "fields": { ... },  # See field mapping below
        "tags": ["spoonfed", "haiku", "ElevenLabs", "adhoc"],
    }
    result = anki_invoke("addNote", note=note)
    print(f"Created note {result}: {row['sentence'][:50]}...")
```

## Language-specific field mappings

Look these up from `src/iplusone.py` EXPORT_CONFIG, but the known ones are:

**Turkish** (`turkish-back` model):
- Deck: `Turkish::Known`
- Front: English translation
- Back: Turkish sentence + audio

**Hindi** (`Basic-10b04` model):
- Deck: `Hindi::Known` (check database.db)
- Front: Hindi sentence
- Back: English translation
- Definition: audio

**French**: Check database.db and EXPORT_CONFIG for current mapping.

## Cleanup

After the script runs successfully, **delete it**. This skill should not leave any persistent code in the repo. Every invocation writes a temporary script, runs it, and removes it.

## Important notes

- Anki MUST be running for AnkiConnect to work (localhost:8765)
- The `.env` file must contain `ELEVENLABS_API_KEY`
- Audio is auto-slowed to 0.75x via ffmpeg (requires ffmpeg installed)
- Always verify the generated sentences look correct before pushing to Anki
- Use `haiku` model for simple sentences, `sonnet` for more complex/nuanced ones
- The `generate_audio` function strips HTML/cloze notation automatically, so plain sentences work fine
