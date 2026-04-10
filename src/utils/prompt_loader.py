import yaml
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def load_prompt(prompt_name, override_language, **template_vars):
    """
    Load a prompt by name, merge language-specific overrides, fill template vars.

    prompt_name: e.g. "verb_exploder", "iplusone"
    override_language: e.g. "Hindi", "Turkish" — selects which override file to load
    **template_vars: runtime values like language, verb_input, learned_tokens, etc.
    """
    prompt_dir = PROMPTS_DIR / prompt_name

    # Load base
    with open(prompt_dir / "base.yaml") as f:
        base = yaml.safe_load(f)

    # Load language override if it exists
    lang_file = prompt_dir / f"{override_language.lower()}.yaml"
    overrides = {}
    if lang_file.exists():
        with open(lang_file) as f:
            overrides = yaml.safe_load(f) or {}

    # Merge: language overrides win over base defaults
    merged = {**base, **overrides}

    # Extract the prompt template, fill section variables then runtime vars
    # Runtime template_vars take precedence over YAML keys
    prompt_template = merged.pop("prompt")
    all_vars = {**merged, **template_vars}
    return prompt_template.format(**all_vars)


def load_system_prompt():
    with open(PROMPTS_DIR / "system.yaml") as f:
        data = yaml.safe_load(f)
    return data["prompt"]
