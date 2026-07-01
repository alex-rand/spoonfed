"""Verb-exploder skill: generate a full conjugation grid for one verb and push to Anki.

Replicates the GUI flow in src/verb_exploder_frame.py without the GUI:
  1. Load the verb-exploder prompt (base + language override) for the given verb
  2. Generate sentences via the Claude CLI
  3. Add tense/polarity emojis (Turkish only)
  4. Generate ElevenLabs audio (slowed to 0.75x)
  5. Push cards to Anki using the 'Spoonfed Verb Exploder' cloze model with
     conjugation-derived tags (tense::*, person::*, polarity::*)

Usage:
  python .claude/skills/verb-exploder/run.py <verb> [--language Turkish] [--model sonnet]
"""
import argparse, csv, io, json, os, re, subprocess, sys, urllib.request
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

PROJECT_ROOT = Path.cwd()
load_dotenv(PROJECT_ROOT / ".env")
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from utils.prompt_loader import load_prompt
from utils.audio_generating_functions import generate_audio
from utils.anki_connect_functions import strip_html_and_cloze, remove_non_language_tokens

VOCAB_SAMPLE_SIZE = 150


# ── Turkish-specific helpers (mirror src/verb_exploder_frame.py) ────
TENSE_EMOJI = {
    'present continuous': '🔔', 'aorist': '⬇️', 'future': '➡️',
    'past definite': '⬅️', 'past narrative': '👂', 'necessitative': '⚠️',
    'ability': '🔑', 'conditional': '🔀', 'imperative': '🙏',
}
NEGATION_EMOJI = '🚫'
PERSON_MAP = {
    '1st person singular': '1sg', '2nd person singular': '2sg', '3rd person singular': '3sg',
    '1st person plural': '1pl', '2nd person plural': '2pl', '3rd person plural': '3pl',
}


def add_tense_emojis(sentence, conjugation):
    conj_lower = conjugation.lower()
    emoji = next((e for t, e in TENSE_EMOJI.items() if t in conj_lower), '')
    if not emoji:
        return sentence
    if 'negative' in conj_lower:
        return f"{emoji}{NEGATION_EMOJI} {sentence} {NEGATION_EMOJI}{emoji}"
    return f"{emoji} {sentence} {emoji}"


def conjugation_to_tags(conjugation):
    conj_lower = conjugation.lower()
    tags = []
    for t in TENSE_EMOJI:
        if t in conj_lower:
            tags.append(f"tense::{t.replace(' ', '-')}")
            break
    for label, short in PERSON_MAP.items():
        if label in conj_lower:
            tags.append(f"person::{short}")
            break
    if 'negative' in conj_lower:
        tags.append('polarity::negative')
    elif 'affirmative' in conj_lower:
        tags.append('polarity::affirmative')
    return tags


# ── AnkiConnect ─────────────────────────────────────────────────────
def anki(action, **params):
    payload = json.dumps({"action": action, "params": params, "version": 6}).encode()
    r = json.load(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:8765", payload)))
    if r.get("error"):
        raise Exception(r["error"])
    return r["result"]


def get_learned_deck(language):
    """Look up the learned deck for this language from database.db."""
    import sqlite3
    conn = sqlite3.connect(PROJECT_ROOT / "database.db")
    try:
        row = conn.execute(
            "SELECT learned_deck FROM language_configurations WHERE configuration_language = ?",
            (language,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        raise SystemExit(f"No language_configurations row for {language!r} in database.db")
    return row[0]


def load_learned_vocab(language, deck, sample_size=VOCAB_SAMPLE_SIZE):
    """Pull learned vocab from Anki — mirrors decks_homepage.load_vocab_from_deck.

    Reads the configured card-types/fields for this language from database.db,
    fetches matching notes from the Anki deck, strips HTML/cloze/non-language
    characters, tokenizes on whitespace, dedupes, and returns up to
    `sample_size` random tokens. Returns [] (silently) on any failure.
    """
    import sqlite3
    try:
        conn = sqlite3.connect(PROJECT_ROOT / "database.db")
        try:
            rows = conn.execute(
                """
                SELECT ct.card_type_name, cf.field_name
                FROM language_configurations lc
                JOIN card_types ct ON ct.configuration_id = lc.id
                JOIN card_fields cf ON cf.card_type_id = ct.card_type_id
                WHERE lc.configuration_language = ?
                """,
                (language,),
            ).fetchall()
        finally:
            conn.close()

        types_fields = {}
        for ct, fn in rows:
            types_fields.setdefault(ct, set()).add(fn)
        # The GUI auto-appends this card type; mirror that so verb-exploder
        # cards already in the deck contribute their text to the vocab pool.
        types_fields.setdefault("Spoonfed Verb Exploder", set()).add("Text")

        all_tokens = []
        for card_type, raw_fields in types_fields.items():
            fields = [f.strip() for rf in raw_fields for f in rf.split(",")]
            note_ids = anki("findNotes", query=f'"deck:{deck}" "note:{card_type}"')
            if not note_ids:
                continue
            for info in anki("notesInfo", notes=note_ids):
                for f in fields:
                    cell = info["fields"].get(f)
                    if not cell:
                        continue
                    txt = strip_html_and_cloze(str(cell["value"]))
                    txt = remove_non_language_tokens(txt, language)
                    all_tokens.extend(t for t in txt.split() if t)

        unique = pd.Series(all_tokens).drop_duplicates()
        if len(unique) > sample_size:
            unique = unique.sample(n=sample_size, replace=False)
        return unique.tolist()
    except Exception as e:
        print(f"  (vocab injection skipped: {e})")
        return []


# ── Pipeline ────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("verb", help="Infinitive of the target verb (e.g. gelmek)")
    ap.add_argument("--language", default="Turkish")
    ap.add_argument("--model", default="sonnet", help="Claude CLI model (sonnet/opus/haiku)")
    ap.add_argument("--profile", default="Alex", help="Anki profile name (used by audio fn)")
    ap.add_argument("--no-vocab", action="store_true", help="Skip known-vocab injection into the prompt")
    args = ap.parse_args()

    anki_model = "Spoonfed Verb Exploder"
    audio_source = "ElevenLabs"
    deck = get_learned_deck(args.language)

    if anki_model not in anki("modelNames"):
        raise SystemExit(
            f"Anki model '{anki_model}' not found. Open the Spoonfed GUI's verb-exploder "
            f"once to auto-create it, then re-run."
        )

    print(f"Verb-exploder: verb={args.verb!r} language={args.language!r} deck={deck!r} model={args.model}")

    # 1. Vocab injection (optional) + prompt
    vocab_instruction = ""
    if not args.no_vocab:
        print(f"Loading known vocab from '{deck}' (sample of {VOCAB_SAMPLE_SIZE})...")
        tokens = load_learned_vocab(args.language, deck)
        if tokens:
            print(f"  injecting {len(tokens)} known words into the prompt")
            vocab_instruction = (
                "The student already knows the following vocabulary words:\n"
                f"{', '.join(tokens)}\n\n"
                "When constructing sentences, prefer using words from this list for "
                "non-verb vocabulary (subjects, objects, adverbs, etc.). This is a "
                "soft preference — if a word outside this list makes the sentence "
                "more natural, that is acceptable."
            )

    prompt = load_prompt(
        "verb_exploder", args.language,
        language=args.language, verb_input=args.verb, vocab_instruction=vocab_instruction,
    )

    # 2. Claude CLI
    print(f"Calling Claude CLI ({args.model})... ~1-2 min for the full conjugation grid.")
    result = subprocess.run(
        ["claude", "-p", "--model", args.model, "--output-format", "json"],
        input=prompt, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise SystemExit(f"Claude CLI error: {result.stderr}")

    text = json.loads(result.stdout)["result"].strip()
    text = re.sub(r'^```(?:csv)?\n', '', text)
    text = re.sub(r'\n```$', '', text)

    # Tolerant CSV parse: the conjugation field naturally contains commas
    # ("present continuous, 1st person singular, affirmative") and the LLM
    # sometimes forgets to quote it. Collapse extras back into the last column.
    data = list(csv.reader(io.StringIO(text)))
    if not data:
        raise SystemExit("Claude returned no rows.")
    header = data[0]
    ncols = len(header)
    rows = []
    for r in data[1:]:
        if len(r) > ncols:
            r = r[: ncols - 1] + [", ".join(r[ncols - 1:])]
        elif len(r) < ncols:
            continue
        rows.append(r)
    df = pd.DataFrame(rows, columns=header)
    print(f"Parsed {len(df)} sentences.")

    # 3. Tense emojis (Turkish only — matches GUI behavior)
    if args.language == "Turkish":
        df['sentence'] = df.apply(
            lambda row: add_tense_emojis(row['sentence'], row['conjugation']), axis=1
        )

    # 4. Audio
    print(f"Generating ElevenLabs audio for {len(df)} sentences...")
    df = generate_audio(df, args.language, args.profile, audio_source)

    # 5. Push to Anki
    print(f"Pushing to '{deck}' / '{anki_model}'...")
    success, errors = 0, []
    for _, row in df.iterrows():
        extra = conjugation_to_tags(row['conjugation']) if args.language == "Turkish" else []
        # Record the verb lemma so the i+1 feature can treat it as a 'known verb'.
        verb_tag = f"verb::{args.verb.strip().replace(' ', '_')}"
        tags = ["spoonfed", args.model, audio_source, "verb-exploder"] + extra + [verb_tag]
        note = {
            "deckName": deck,
            "modelName": anki_model,
            "fields": {
                "Text": row['sentence'],
                "Translation": row['translation'],
                "Audio": row.get('audio', ''),
            },
            "tags": tags,
        }
        try:
            anki("addNote", note=note)
            success += 1
        except Exception as e:
            errors.append((row['conjugation'], str(e)))

    print(f"\nCreated {success}/{len(df)} cards.")
    if errors:
        print(f"Errors ({len(errors)}):")
        for c, e in errors[:10]:
            print(f"  - {c}: {e}")


if __name__ == "__main__":
    main()
