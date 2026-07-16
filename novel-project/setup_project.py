#!/usr/bin/env python3
"""Initialize novel-project bible structure with UTF-8 encoding."""

from pathlib import Path

ROOT = Path(__file__).parent
BIBLE = ROOT / "bible"
DRAFTS = ROOT / "drafts"
CHAPTERS = ROOT / "chapters"  # legacy

FILES = [
    BIBLE / "style-guide.md",
    BIBLE / "outline.md",
    BIBLE / "characters.md",
    BIBLE / "worldbuilding.md",
    BIBLE / "timeline.md",
    DRAFTS / "README.md",
    DRAFTS / "chapter-001.md",
]


def main() -> None:
    BIBLE.mkdir(parents=True, exist_ok=True)
    DRAFTS.mkdir(parents=True, exist_ok=True)
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    for path in FILES:
        if not path.exists():
            path.write_text(f"# {path.stem}\n\n【待撰写】\n", encoding="utf-8")
            print(f"created: {path}")
        else:
            text = path.read_text(encoding="utf-8", errors="replace")
            path.write_text(text, encoding="utf-8")
            print(f"verified utf-8: {path}")


if __name__ == "__main__":
    main()
