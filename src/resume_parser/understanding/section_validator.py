import re
from dataclasses import dataclass, field
import warnings


# Patterns that indicate content commonly found in each section.
SECTION_PATTERNS = {
    "personal_information": [
        r"\b[\w.+-]+@[\w.-]+\.\w+\b",
        r"\b(?:phone|mobile|contact)\b",
        r"\blinkedin\b",
        r"\bgithub\b",
        r"\+?\d[\d\s().-]{8,}\d",
    ],
    "summary": [
        r"\b(?:experienced|skilled|motivated|professional|specialist)\b",
        r"\b(?:years of experience|background in|expertise in)\b",
    ],
    "objective": [
        r"\b(?:seeking|looking for|career objective|to obtain)\b",
        r"\b(?:opportunity|position|role)\b",
    ],
    "technical_skills": [
        r"\b(?:python|java|javascript|c\+\+|sql|html|css|react|django|"
        r"fastapi|tensorflow|pytorch|opencv|docker|git|aws)\b",
        r"[,;|]",
    ],
    "experience": [
        r"\b(?:developer|engineer|manager|intern|analyst|designer|"
        r"consultant|technician)\b",
        r"\b(?:responsibilities|developed|managed|implemented|worked)\b",
        r"\b(?:20\d{2}|19\d{2})\s*[-–to]+\s*(?:20\d{2}|present|current)\b",
    ],
    "education": [
        r"\b(?:b\.?tech|m\.?tech|bachelor|master|phd|diploma|degree)\b",
        r"\b(?:university|college|school|institute)\b",
        r"\b(?:cgpa|gpa|percentage|graduation)\b",
    ],
    "projects": [
        r"\b(?:developed|built|designed|created|implemented)\b",
        r"\b(?:project|application|system|platform|website)\b",
        r"\b(?:using|technologies|tech stack)\b",
    ],
    "certifications": [
        r"\b(?:certified|certification|certificate|license|licensed)\b",
        r"\b(?:course|completed|issued by)\b",
    ],
    "achievements": [
        r"\b(?:award|achievement|won|winner|rank|recognized|"
        r"honored|honoured)\b",
    ],
    "languages": [
        r"\b(?:english|hindi|tamil|telugu|malayalam|kannada|"
        r"french|german|spanish)\b",
        r"\b(?:fluent|proficient|beginner|intermediate|native)\b",
    ],
    "publications": [
        r"\b(?:published|publication|journal|research paper|conference)\b",
        r"\bdoi\b",
    ],
    "interests": [
        r"\b(?:reading|writing|traveling|travelling|music|sports|"
        r"photography|volunteering|hiking)\b",
    ],
    "references": [
        r"\b(?:reference|referee|available upon request)\b",
        r"\b[\w.+-]+@[\w.-]+\.\w+\b",
    ],
}


@dataclass
class SectionValidation:
    section_name: str
    confidence: int
    is_valid: bool
    warnings: list[str] = field(default_factory=list)


def validate_section(section_name: str, content: str) -> SectionValidation:
    """
    Validate one extracted resume section.

    Confidence is a heuristic quality score from 0 to 100.
    It is not a probability.
    """

    if not isinstance(section_name, str):
        raise TypeError("section_name must be a string")

    if not isinstance(content, str):
        raise TypeError("content must be a string")

    section_name = section_name.strip().casefold()
    content = content.strip()

    if section_name not in SECTION_PATTERNS:
        return SectionValidation(
            section_name=section_name,
            confidence=0,
            is_valid=False,
            warnings=["Unrecognized section name"],
        )

    if not content:
        return SectionValidation(
            section_name=section_name,
            confidence=0,
            is_valid=False,
            warnings=["Section has no content"],
        )

    score = 40
    warnings = []

    # Check for section-specific content indicators.
    patterns = SECTION_PATTERNS[section_name]
    has_matching_content = any(
        re.search(pattern, content, re.IGNORECASE)
        for pattern in patterns
    )

    if has_matching_content:
        score += 30
    else:
        warnings.append(
            "No strong content indicators found for this section"
        )

    # Check whether the section contains enough meaningful content.
    non_empty_lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    has_structure = (
        len(non_empty_lines) >= 2
        or "," in content
        or ";" in content
        or "|" in content
    )

    if has_structure:
        score += 15
    else:
        warnings.append("Section contains very little structured content")

    if len(content) >= 20:
        score += 15
    else:
        warnings.append("Section content is unusually short")

    # Very short content should not be considered reliable.
    if len(content) < 10:
        score = min(score, 50)

    return SectionValidation(
        section_name=section_name,
        confidence=score,
        is_valid=score >= 60,
        warnings=warnings,
    )


def validate_sections(
    sections: dict[str, str]
) -> dict[str, SectionValidation]:
    """Validate all sections returned by the section splitter."""

    if not isinstance(sections, dict):
        raise TypeError("sections must be a dictionary")

    results = {}

    for section_name, content in sections.items():
        results[section_name] = validate_section(
            section_name,
            content,
        )

    return results