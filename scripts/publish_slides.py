#!/usr/bin/env python3
"""Generate public Quarto slide sources with speaker notes removed."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "private_slides"
DEFAULT_DESTINATION = PROJECT_ROOT / "slides"

FENCED_DIV_OPEN = re.compile(
    r"^\s*(?P<fence>:{3,})\s*(?P<attributes>\{.+\}|notes)\s*$",
    re.IGNORECASE,
)
FENCED_DIV_CLOSE = re.compile(r"^\s*(?P<fence>:{3,})\s*$")


def is_notes_div(attributes: str) -> bool:
    """Return whether fenced-div attributes identify Reveal.js speaker notes."""
    normalized = attributes.strip().lower()
    return bool(
        re.search(r"(?:^|[\s{])\.notes(?:[\s}]|$)", normalized)
        or normalized in {"notes", "{notes}"}
    )


def strip_speaker_notes(text: str, source: Path) -> tuple[str, int]:
    """Remove fenced `.notes` divs while preserving all other slide content."""
    output: list[str] = []
    note_fence_length: int | None = None
    removed_blocks = 0

    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        opening = FENCED_DIV_OPEN.match(line)
        closing = FENCED_DIV_CLOSE.match(line)

        if note_fence_length is None:
            if opening and is_notes_div(opening.group("attributes")):
                note_fence_length = len(opening.group("fence"))
                removed_blocks += 1
                continue
            output.append(line)
            continue

        # Pandoc permits a closing fence to be longer than its opening fence.
        if closing and len(closing.group("fence")) >= note_fence_length:
            note_fence_length = None
            continue

    if note_fence_length is not None:
        raise ValueError(f"Unclosed speaker-notes block in {source}")

    return "".join(output), removed_blocks


def publish(source_dir: Path, destination_dir: Path) -> None:
    if not source_dir.is_dir():
        raise FileNotFoundError(
            f"Private slide directory not found: {source_dir}\n"
            "Create it from the current public slides before running this script."
        )

    slide_paths = sorted(source_dir.rglob("*.qmd"))
    if not slide_paths:
        raise FileNotFoundError(f"No .qmd slide files found in {source_dir}")

    total_blocks = 0
    for source_path in slide_paths:
        relative_path = source_path.relative_to(source_dir)
        destination_path = destination_dir / relative_path
        public_text, removed_blocks = strip_speaker_notes(
            source_path.read_text(encoding="utf-8"), source_path
        )
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path.write_text(public_text, encoding="utf-8")
        total_blocks += removed_blocks
        print(f"Published {relative_path} ({removed_blocks} notes blocks removed)")

    print(
        f"Published {len(slide_paths)} slide files to {destination_dir} "
        f"with {total_blocks} notes blocks removed."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate public Quarto slides from private sources without speaker notes."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    args = parser.parse_args()
    publish(args.source.resolve(), args.destination.resolve())


if __name__ == "__main__":
    main()
