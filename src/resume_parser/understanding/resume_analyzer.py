from dataclasses import dataclass, field

from .section_splitter import (
    split_sections,
    split_sections_from_regions,
)
from .section_validator import validate_sections


@dataclass
class ResumeAnalysis:
    sections: dict[str, str] = field(default_factory=dict)
    validation: dict = field(default_factory=dict)
    total_sections: int = 0
    average_confidence: float = 0.0


def analyze_resume(
    text: str,
    text_regions: list[str] | None = None
) -> ResumeAnalysis:
    """
    Analyze extracted resume text.

    1. Identify section headings.
    2. Split the resume into sections.
    3. Validate each recognized section.
    4. Calculate average confidence.
    """

    if not isinstance(text, str):
        raise TypeError("Resume text must be a string")

    if text_regions is None:
        sections = split_sections(text)
    else:
        sections = split_sections_from_regions(text_regions)

    # Exclude the introductory content before the first
    # recognized heading from section validation.
    recognized_sections = {
        name: content
        for name, content in sections.items()
        if name != "header"
    }

    validation = validate_sections(recognized_sections)

    if validation:
        average_confidence = round(
            sum(result.confidence for result in validation.values())
            / len(validation),
            2,
        )
    else:
        average_confidence = 0.0

    return ResumeAnalysis(
        sections=sections,
        validation=validation,
        total_sections=len(recognized_sections),
        average_confidence=average_confidence,
    )