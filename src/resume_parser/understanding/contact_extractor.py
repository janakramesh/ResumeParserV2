
import re

import phonenumbers
from phonenumbers import PhoneNumberFormat

from .heading_detector import detect_heading

# --------------------------------------------------
# PHONE NUMBER EXTRACTION
# --------------------------------------------------

def extract_phone_numbers(text: str) -> list[str]:
    """
    Extract valid phone numbers.
    Prioritizes Indian numbers and supports international numbers.
    Returns unique numbers in E.164 format.
    """

    if not text:
        return []

    normalized_text = re.sub(
        r"\(\s*\+\s*(91)\s*\)",
        r"+\1",
        text,
    )

    normalized_text = re.sub(
        r"\(\s*(91)\s*\)",
        r"+\1",
        normalized_text,
    )

    candidates = []

    for region in ("IN", None):
        try:
            matcher = phonenumbers.PhoneNumberMatcher(
                normalized_text,
                region,
                leniency=phonenumbers.Leniency.VALID,
            )

            for match in matcher:
                number = match.number

                if not phonenumbers.is_valid_number(number):
                    continue

                if number.country_code == 91:
                    candidates.insert(0, number)
                else:
                    candidates.append(number)

        except Exception:  # noqa: BLE001
            continue

    results = []
    seen = set()

    for number in candidates:
        formatted = phonenumbers.format_number(
            number,
            PhoneNumberFormat.E164,
        )

        if formatted not in seen:
            seen.add(formatted)
            results.append(formatted)

    return results


def extract_primary_phone(text: str) -> str:
    """Return the first detected phone number."""

    numbers = extract_phone_numbers(text)
    return numbers[0] if numbers else ""


# --------------------------------------------------
# ADDRESS EXTRACTION
# --------------------------------------------------

ADDRESS_LABEL_GROUPS = {
    "permanent": ("permanent address", "permanent residence"),
    "present": ("present address", "present residence"),
    "current": ("current address", "current residence"),
    "residential": ("residential address", "residential location"),
    "other": (
        "home address",
        "correspondence address",
        "contact address",
        "mailing address",
        "communication address",
        "postal address",
        "address",
        "location",
    ),
}

ADDRESS_PRIORITY = {
    label: priority
    for priority, group in enumerate(ADDRESS_LABEL_GROUPS.values())
    for label in group
}

NON_RESIDENTIAL_SECTIONS = {
    "experience",
    "education",
    "projects",
    "achievements",
    "certifications",
}

ADDRESS_COMPONENT_FIELDS = {
    "apartment", "apt", "building", "block", "flat", "floor",
    "house", "house no", "landmark", "plot", "street", "unit",
}

CONTACT_FIELD_PATTERN = re.compile(
    r"^\s*(?:e-?mail|phone|mobile|telephone|linkedin|github|"
    r"website|date of birth|dob|nationality|gender)\b\s*[:=—–-]",
    re.IGNORECASE,
)

ADDRESS_STRUCTURE_PATTERN = re.compile(
    r"\b(?:street|road|lane|avenue|drive|court|apartment|apt|flat|"
    r"house|building|tower|block|sector|floor|unit|plot|residency|"
    r"colony|village|town|district|postcode|postal code|zip)\b"
    r"|\b\d+[A-Za-z]?(?:[-/]\w+)?\b",
    re.IGNORECASE,
)

PAGE_MARKER_PATTERN = re.compile(
    r"^\s*(?:---\s*)?page\s+\d+(?:\s*---)?\s*$",
    re.IGNORECASE,
)

CONTACT_HINT_PATTERN = re.compile(
    r"\b(?:e-?mail|phone|mobile|telephone|linkedin|github|contact)\b"
    r"|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
    re.IGNORECASE,
)

NARRATIVE_MARKER_PATTERN = re.compile(
    r"\b(?:I|we|he|she|they|my|our|his|her|is|are|was|were|has|have|"
    r"had|focus|job|career|project|experience|worked|working|managed|"
    r"achieved|increased|decreased|implemented|developed|delivered|"
    r"responsible|contributed)\b",
    re.IGNORECASE,
)


def _normalize_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def _is_section_heading(line: str) -> bool:
    return detect_heading(line) is not None


def _is_page_marker(line: str) -> bool:
    return PAGE_MARKER_PATTERN.fullmatch(line.strip()) is not None


def _clean_address_candidate(line: str) -> str:
    """Remove email addresses, URLs, phone numbers and social labels."""

    line = _normalize_line(line)

    trailing_contact = re.search(
        r"\s+(?:e-?mail|phone|mobile|telephone|linkedin|github|website)"
        r"\s*[:=]",
        line,
        re.IGNORECASE,
    )
    if trailing_contact:
        line = line[:trailing_contact.start()]

    line = re.sub(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"https?://\S+|www\.\S+",
        "",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"\b[\w-]+\.(?:com|org|net|edu|gov|io|co|uk)\b",
        "",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"\b(?:\S*email\S*|\S*linkedin\S*|\S*tinkedin\S*|"
        r"linkedin|github|portfolio|website)\b",
        "",
        line,
        flags=re.IGNORECASE,
    )

    line = re.sub(
        r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)",
        "",
        line,
    )

    line = re.sub(
        r"^[\s|,;:—–()-]+|[\s|,;:—–()-]+$",
        "",
        line,
    )

    return _normalize_line(line)



def _is_narrative_line(line: str) -> bool:
    if "%" in line or "?" in line or "!" in line:
        return True

    if NARRATIVE_MARKER_PATTERN.search(line):
        return True

    return False


def _is_plausible_address(line: str, *, labelled: bool = False) -> bool:
    """Reject prose while allowing address fragments under a label."""

    if (
        not line
        or len(line) > 240
        or _is_page_marker(line)
        or _is_narrative_line(line)
    ):
        return False

    if "@" in line or "http" in line.casefold():
        return False

    if not re.search(r"[A-Za-z]", line):
        return False

    if labelled:
        return True

    parts = [part.strip() for part in line.split(",") if part.strip()]
    has_compound_location = len(parts) >= 2
    has_address_structure = ADDRESS_STRUCTURE_PATTERN.search(line) is not None
    return has_address_structure or has_compound_location


def _get_address_label_pattern():
    labels = "|".join(
        re.escape(label)
        for label in sorted(ADDRESS_PRIORITY, key=len, reverse=True)
    )

    return re.compile(
        rf"^\s*(?:.*[|;]\s*)?(?P<label>{labels})"
        r"(?:\s*(?:[:：=]|[-–—])\s*|\s+|$)(?P<value>.*)$",
        re.IGNORECASE,
    )


def _is_field_boundary(line: str) -> bool:
    if CONTACT_FIELD_PATTERN.match(line):
        return True

    field_match = re.match(
        r"^\s*(?P<field>[A-Za-z][A-Za-z0-9 /&.-]{1,30})\s*[:=]",
        line,
    )
    if not field_match:
        return False

    field = _normalize_line(field_match.group("field")).casefold()
    return field not in ADDRESS_COMPONENT_FIELDS


def _extract_labelled_address(lines: list[str]) -> str:
    """Find labelled addresses across sections using label priority."""

    label_pattern = _get_address_label_pattern()
    found = {}
    section = ""

    for index, line in enumerate(lines):
        heading = detect_heading(line)
        if heading:
            section = heading
            continue

        match = label_pattern.match(_normalize_line(line))
        if not match:
            continue

        label = match.group("label").casefold()
        if (
            label in {"address", "location"}
            and section in NON_RESIDENTIAL_SECTIONS
        ):
            continue

        address_parts = []
        first_part = _clean_address_candidate(match.group("value"))
        if first_part and _is_plausible_address(first_part, labelled=True):
            address_parts.append(first_part)

        for next_line in lines[index + 1:]:
            candidate_line = _normalize_line(next_line)
            if not candidate_line:
                break

            if (
                _is_section_heading(candidate_line)
                or label_pattern.match(candidate_line)
                or _is_field_boundary(candidate_line)
                or _is_narrative_line(candidate_line)
            ):
                break

            candidate = _clean_address_candidate(candidate_line)
            if not _is_plausible_address(candidate, labelled=True):
                break

            address_parts.append(candidate)

        result = ", ".join(address_parts)
        if result:
            found.setdefault(label, result)

    for label in sorted(ADDRESS_PRIORITY, key=ADDRESS_PRIORITY.get):
        if label in found:
            return found[label]

    return ""


def _extract_header_address(lines: list[str]) -> str:
    """Use only the introductory header when no labelled value exists."""

    for line in lines:
        candidate = _normalize_line(line)
        if _is_page_marker(candidate):
            continue

        if _is_section_heading(candidate):
            break

        candidate = _clean_address_candidate(candidate)
        if _is_plausible_address(candidate):
            return candidate

    return ""


def _extract_contact_line_address(lines: list[str]) -> str:
    """Find a location attached to contact details in identity sections."""
    identity_sections = {
        "",
        "header",
        "personal_information",
        "technical_skills",
        "summary",
        "objective",
    }
    section = ""

    for line in lines:
        candidate_line = _normalize_line(line)
        if _is_page_marker(candidate_line):
            continue

        heading = detect_heading(candidate_line)
        if heading:
            section = heading
            continue

        if (
            section not in identity_sections
            or not CONTACT_HINT_PATTERN.search(candidate_line)
        ):
            continue

        candidate = _clean_address_candidate(candidate_line)
        if _is_plausible_address(candidate):
            return candidate

    return ""


def extract_address(text: str) -> str:
    """
    Address extraction priority:
    1. Permanent address
    2. Present address
    3. Other labelled address
    4. Header-based fallback
    5. Contact-line location in an identity section
    """

    if not text:
        return ""

    lines = text.splitlines()

    labelled_address = _extract_labelled_address(lines)
    if labelled_address:
        return labelled_address

    header_address = _extract_header_address(lines)
    if header_address:
        return header_address

    return _extract_contact_line_address(lines)



# --------------------------------------------------
# COMBINED CONTACT EXTRACTION
# --------------------------------------------------

def extract_contact_information(text: str) -> dict:
    """Extract phone number and address."""

    return {
        "phone_number": extract_primary_phone(text),
        "phone_numbers": extract_phone_numbers(text),
        "address": extract_address(text),
    }
