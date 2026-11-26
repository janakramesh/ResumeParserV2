
"""
Detects resume section headings and maps them to canonical names.
"""

import re

from .section_aliases import SECTION_ALIASES


def normalize_heading(line: str) -> str:
    """
    Normalize a heading before matching it.

    Handles:
    - Uppercase and lowercase
    - Extra whitespace
    - Numbered headings
    - Bullet prefixes
    - Markdown heading markers
    - Trailing colons and punctuation
    """

    if not isinstance(line, str):
        return ""

    line = line.strip()

    # Remove Markdown heading markers
    line = re.sub(r"^#{1,6}\s*", "", line)

    # Remove common bullet prefixes
    line = re.sub(r"^[-*•▪]\s*", "", line)

    # Remove numbered prefixes: 1. Education, (1) Education
    line = re.sub(
        r"^(?:\(?\d{1,2}\)?[.)]?\s+)",
        "",
        line
    )

    # Remove trailing heading punctuation and decorative underline rules.
    line = line.rstrip(" \t:：|–—-•._=")

    # Normalize whitespace and case
    line = re.sub(r"\s+", " ", line)

    return line.casefold()


def detect_heading(line: str) -> str | None:
    """
    Detect whether a line represents a known resume section.

    Returns:
        Canonical section name if detected.
        None if the line is not a recognized heading.
    """

    normalized = normalize_heading(line)

    if not normalized:
        return None

    for section, aliases in SECTION_ALIASES.items():
        normalized_aliases = {
            normalize_heading(alias) for alias in aliases
        }

        if normalized in normalized_aliases:
            return section

    return None
