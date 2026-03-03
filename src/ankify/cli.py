"""CLI entry points for ankify-lint and ankify-all."""

from pathlib import Path

import click

from ankify.lint import lint_file
from ankify.exporter import export_all, PENDING_DIR
from ankify.anki_connect import AnkiConnectError


@click.command("ankify-lint")
@click.argument("files", nargs=-1, type=click.Path(exists=True, path_type=Path))
def lint_cmd(files: tuple[Path, ...]) -> None:
    """Validate card YAML files.

    If no files are given, lints all *.yaml files in cards/pending/.
    """
    if files:
        paths = list(files)
    else:
        paths = sorted(PENDING_DIR.glob("*.yaml"))

    if not paths:
        click.echo("No card files found to lint.")
        return

    has_errors = False
    for path in paths:
        result = lint_file(path)
        if result.messages:
            click.echo(f"\n{result.file}:")
            for msg in result.messages:
                click.echo(str(msg))
            if result.has_errors:
                has_errors = True
        else:
            click.echo(f"{result.file}: OK")

    if has_errors:
        raise SystemExit(1)


@click.command("ankify-all")
@click.option("--dry-run", is_flag=True, help="Validate and show what would be created, but don't touch Anki.")
@click.option("--keep", is_flag=True, help="Don't move files to processed/ after export.")
def export_cmd(dry_run: bool, keep: bool) -> None:
    """Export all pending card files to Anki."""
    try:
        files_processed, cards_created = export_all(dry_run=dry_run, keep=keep)
    except AnkiConnectError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    except ValueError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    if files_processed == 0:
        click.echo("No pending card files found.")
        return

    prefix = "[DRY RUN] " if dry_run else ""
    click.echo(
        f"{prefix}\u2713 {files_processed} file{'s' if files_processed != 1 else ''} processed, "
        f"{cards_created} card{'s' if cards_created != 1 else ''} created"
    )
