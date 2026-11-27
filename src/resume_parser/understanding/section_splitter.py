
"""
Splits cleaned resume text into individual sections.

Uses heading_detector to recognize section boundaries.
"""

import re
from collections import defaultdict

from .heading_detector import detect_heading, normalize_heading


TRAINING_EXPERIENCE_HEADINGS = {
    "training and internship",
    "training & internship",
}

EXPERIENCE_EVIDENCE_PATTERN = re.compile(
    r"\b(?:intern|trainee|developer|engineer|analyst|manager|consultant|"
    r"architect|designer|technician|supervisor)\b"
    r"|\b(?:19|20)\d{2}\b|\b(?:present|current)\b",
    re.IGNORECASE,
)

EXPERIENCE_TAIL_ARTIFACTS = (
    re.compile(r"^(?:https?://|www\.)\S+$", re.IGNORECASE),
    re.compile(r"^powered by\b", re.IGNORECASE),
    re.compile(r"^(?:---\s*)?page\s+\d+(?:\s*---)?$", re.IGNORECASE),
    re.compile(r"^\d{1,3}$"),
    re.compile(
        r"^please note:\s*if you (?:have )?received this document in error\b",
        re.IGNORECASE,
    ),
    re.compile(r"^connect to linkedin\b", re.IGNORECASE),
)

TABLE_SECTION_HEADERS = {
    ("year", "title", "location", "company"): "experience",
    ("year", "title", "location", "organized by"): "certifications",
    (
        "year",
        "examinations milestone",
        "board/university",
        "grade %",
    ): "education",
    ("project name", "details", "technology"): "projects",
}


def _trim_experience_tail(lines: list[str]) -> list[str]:
    """Drop trailing page and template artifacts without altering job content."""
    for index, line in enumerate(lines):
        if normalize_heading(line) not in TRAINING_EXPERIENCE_HEADINGS:
            continue

        training_content = "\n".join(lines[index + 1:])
        if not EXPERIENCE_EVIDENCE_PATTERN.search(training_content):
            lines = lines[:index]
            break

    end = len(lines)

    while end:
        line = lines[end - 1].strip()
        if not line or any(pattern.match(line) for pattern in EXPERIENCE_TAIL_ARTIFACTS):
            end -= 1
            continue
        break

    return lines[:end]


def _detect_table_section(lines: list[str], start: int):
    for headers, section_name in TABLE_SECTION_HEADERS.items():
        end = start + len(headers)

        if end > len(lines):
            continue

        normalized_lines = tuple(
            normalize_heading(line) for line in lines[start:end]
        )

        if normalized_lines == headers:
            return section_name, len(headers)

    return None, 0


def split_sections(text: str) -> dict[str, str]:
    """
    Split resume text into sections.

    Args:
        text: Cleaned resume text.

    Returns:
        Dictionary containing section names and their content.

    Example:
        {
            "header": "John Doe\\nPython Developer",
            "technical_skills": "Python, Java",
            "education": "B.Tech Computer Science"
        }

    Repeated sections are merged instead of overwritten.
    """

    if not isinstance(text, str):
        raise TypeError("Resume text must be a string.")

    if not text.strip():
        return {}

    sections = defaultdict(list)

    current_section = "header"

    lines = text.splitlines()
    line_number = 0

    while line_number < len(lines):
        table_section, header_length = _detect_table_section(
            lines,
            line_number
        )

        if table_section:
            current_section = table_section
            sections[current_section]
            line_number += header_length
            continue

        line = lines[line_number]
        heading = detect_heading(line)

        if heading:
            current_section = heading

            # Ensure empty sections are also represented.
            sections[current_section]
            if (
                heading == "experience"
                and normalize_heading(line) in TRAINING_EXPERIENCE_HEADINGS
            ):
                sections[current_section].append(line)

        else:
            sections[current_section].append(line)

        line_number += 1

    # Convert lists of lines into clean section strings.
    result = {}

    for section, lines in sections.items():
        section_lines = (
            _trim_experience_tail(lines)
            if section == "experience"
            else lines
        )
        content = "\n".join(section_lines).strip()

        result[section] = content

    return result




def split_sections_from_regions(text_regions: list[str]) -> dict[str, str]:
    """
    Process ordered PDF text regions while preserving section
    context across region boundaries.
    """

    if not isinstance(text_regions, list):
        raise TypeError("Text regions must be a list.")

    cleaned_regions = []

    for region in text_regions:
        if not isinstance(region, str):
            raise TypeError("Every text region must be a string.")

        lines = [
            line for line in region.splitlines()
            if not (
                line.strip().startswith("--- PAGE ")
                and "| REGION " in line
            )
        ]

        region_text = "\n".join(lines).strip()

        if region_text:
            cleaned_regions.append(region_text)

    if not cleaned_regions:
        return {}

    # Preserve section context across consecutive PDF regions.
    combined_text = "\n".join(cleaned_regions)

    return split_sections(combined_text)
