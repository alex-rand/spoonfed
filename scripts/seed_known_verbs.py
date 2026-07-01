"""Seed 'known verbs' tags onto verb-exploder cards.

Verb-exploder cards created before the verb:: tagging feature have no lemma
tag, so the i+1 'restrict verbs to verb-exploder verbs' feature can't see them.
This one-off utility tags each card with `verb::<infinitive>` so they join the
known-verbs collection.

Every verb-exploder card embeds its infinitive in the cloze hint, e.g.
  {{c1::gidiyorum::…gitmek…}}
so the lemma is read directly and exactly from each card — no guessing.

DRY-RUN by default. Pass --apply to actually add the tags.

Usage:
  python scripts/seed_known_verbs.py --deck "Turkish::Known"
  python scripts/seed_known_verbs.py --deck "Turkish::Known" --apply
  python scripts/seed_known_verbs.py --deck "Turkish::Known" --only gelmek gitmek --apply
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from collections import Counter

ANKI_URL = "http://127.0.0.1:8765"
VE_MODEL = "Spoonfed Verb Exploder"
TAG_PREFIX = "verb::"
# Infinitive lives in the cloze hint: {{cN::<form>::…<infinitive>…}}
HINT_RE = re.compile(r"\{\{c\d+::[^:]*::\s*…?\s*([^…:}]+?)\s*…?\s*\}\}")


def anki(action, **params):
    payload = json.dumps({"action": action, "params": params, "version": 6}).encode("utf-8")
    try:
        resp = json.load(urllib.request.urlopen(urllib.request.Request(ANKI_URL, payload)))
    except urllib.error.URLError:
        sys.exit("ERROR: cannot reach AnkiConnect at 127.0.0.1:8765 — is Anki open?")
    if resp.get("error") is not None:
        sys.exit(f"AnkiConnect error: {resp['error']}")
    return resp["result"]


def lemma_of(text_field):
    m = HINT_RE.search(text_field or "")
    return m.group(1).strip().lower() if m else None


def main():
    ap = argparse.ArgumentParser(description="Seed verb:: tags onto verb-exploder cards.")
    ap.add_argument("--deck", required=True, help="Deck containing verb-exploder cards")
    ap.add_argument("--only", nargs="+", help="Restrict to these infinitives (default: all found)")
    ap.add_argument("--apply", action="store_true", help="Write tags (omit for dry-run)")
    args = ap.parse_args()
    only = {v.lower() for v in args.only} if args.only else None

    ids = anki("findNotes", query=f'"deck:{args.deck}" "note:{VE_MODEL}"')
    if not ids:
        sys.exit(f"No '{VE_MODEL}' cards found in deck '{args.deck}'.")
    infos = anki("notesInfo", notes=ids)

    by_verb = {}        # lemma -> list of note ids needing the tag
    counts = Counter()  # lemma -> total cards seen
    already = Counter()
    unparsed = 0
    for info in infos:
        lm = lemma_of(info.get("fields", {}).get("Text", {}).get("value", ""))
        if not lm:
            unparsed += 1
            continue
        if only and lm not in only:
            continue
        counts[lm] += 1
        tag = f"{TAG_PREFIX}{lm.replace(' ', '_')}"
        if tag in info.get("tags", []):
            already[lm] += 1
        else:
            by_verb.setdefault(lm, []).append(info["noteId"])

    print(f"Deck '{args.deck}': {len(infos)} verb-exploder cards, {unparsed} without a parseable hint.")
    print(f"Mode: {'APPLY' if args.apply else 'DRY-RUN (no changes)'}\n")
    total = 0
    for lm in sorted(counts):
        need = len(by_verb.get(lm, []))
        print(f"  {lm:16} {counts[lm]:4d} cards  (already tagged={already[lm]:3d}, to tag={need:3d})")
        if args.apply and need:
            anki("addTags", notes=by_verb[lm], tags=f"{TAG_PREFIX}{lm.replace(' ', '_')}")
        total += need

    print(f"\n{len(counts)} distinct verbs. {'Tagged' if args.apply else 'Would tag'} {total} cards.")
    if not args.apply:
        print("Re-run with --apply to write the tags.")


if __name__ == "__main__":
    main()
