
"""
Splits cleaned resume text into individual sections.

Uses heading_detector to recognize section boundaries.
"""

from collections import defaultdict

from .heading_detector import detect_heading, normalize_heading


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

        else:
            sections[current_section].append(line)

        line_number += 1

    # Convert lists of lines into clean section strings.
    result = {}

    for section, lines in sections.items():
        content = "\n".join(lines).strip()

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
