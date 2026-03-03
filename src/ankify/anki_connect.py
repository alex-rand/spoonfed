"""Thin AnkiConnect HTTP client. No PyQt5 dependency."""

import json
import urllib.request
from typing import Any

ANKI_CONNECT_URL = "http://127.0.0.1:8765"


class AnkiConnectError(Exception):
    """Raised when AnkiConnect returns an error or is unreachable."""


def invoke(action: str, **params: Any) -> Any:
    """Send a request to AnkiConnect. Raises AnkiConnectError on failure."""
    payload = json.dumps({"action": action, "version": 6, "params": params})
    request = urllib.request.Request(
        ANKI_CONNECT_URL,
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read())
    except urllib.error.URLError as e:
        raise AnkiConnectError(
            "Could not connect to AnkiConnect. Is Anki running with the AnkiConnect add-on?"
        ) from e

    if result.get("error"):
        raise AnkiConnectError(result["error"])
    return result.get("result")


def add_note(deck: str, model: str, fields: dict[str, str], tags: list[str]) -> int:
    """Create a single note. Returns note ID."""
    return invoke(
        "addNote",
        note={
            "deckName": deck,
            "modelName": model,
            "fields": fields,
            "tags": tags,
        },
    )


def deck_names() -> list[str]:
    """List existing deck names."""
    return invoke("deckNames")


def create_deck(name: str) -> int:
    """Create a deck if it doesn't exist. Returns deck ID."""
    return invoke("createDeck", deck=name)
