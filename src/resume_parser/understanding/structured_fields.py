
import re
from urllib.parse import urlparse
from .contact_extractor import (
    extract_phone_numbers,
    extract_primary_phone,
    extract_address,
)


EMAIL_PATTERN = re.compile(
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
    re.IGNORECASE
)

URL_PATTERN = re.compile(
    r"https?://[^\s<>]+",
    re.IGNORECASE
)

# Indian mobile numbers: supports +91, 91, and 10-digit formats.
INDIAN_PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+91[\s.-]*|91[\s.-]*|0)?"
    r"[6-9]\d{4}[\s.-]?\d{5}(?!\d)"
)

NON_NAME_LABELS = {
    "about", "contents", "cv", "index",
    "portfolio", "profile", "resume",
}

ROLE_WORDS = {
    "analyst", "architect", "consultant",
    "developer", "director", "engineer",
    "executive", "leader", "manager",
    "mentor", "professional", "specialist",
    "strategist", "technologist",
}


def _clean_url(url: str) -> str:
    url = (url or "").strip().rstrip(".,;)")
    if url and not url.lower().startswith(("http://", "https://")):
        url = "https://" + url
    return url


def _link_kind(url: str, label: str = "") -> str | None:
    host = urlparse(_clean_url(url)).netloc.lower().removeprefix("www.")
    combined = f"{host} {label}".lower()

    if "linkedin.com" in combined or "linkedin" in combined:
        return "linkedin"

    if "github.com" in combined or "github" in combined:
        return "github"

    return None


def _extract_name(header: str) -> str:
    single_word_fallback = ""

    for line in header.splitlines():
        candidate = line.strip().strip("|•—–- .")

        if (
            not candidate
            or candidate.casefold() in NON_NAME_LABELS
            or EMAIL_PATTERN.search(candidate)
            or INDIAN_PHONE_PATTERN.search(candidate)
            or re.search(r"https?://|@|[|/:]", candidate, re.I)
        ):
            continue

        tokens = candidate.split()

        normalized_tokens = [
            token.strip(".,'’").replace("-", "").replace("‐", "")
            for token in tokens
        ]

        if (
            2 <= len(tokens) <= 5
            and all(token.isalpha() for token in normalized_tokens)
            and not any(
                token.casefold() in ROLE_WORDS
                for token in normalized_tokens
            )
        ):
            return candidate

        if (
            len(tokens) == 1
            and normalized_tokens[0].isalpha()
            and not single_word_fallback
        ):
            single_word_fallback = candidate

    return single_word_fallback


def _extract_phone(text: str) -> str:
    """
    Extract and normalize an Indian mobile number.
    Returns an empty string if no valid number is found.
    """

    match = INDIAN_PHONE_PATTERN.search(text)

    if not match:
        return ""

    digits = re.sub(r"\D", "", match.group(0))

    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]

    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    if len(digits) == 10 and digits[0] in "6789":
        return "+91 " + digits

    return ""


def extract_structured_fields(
    sections: dict,
    hyperlinks: list | None = None
) -> dict:
    """
    Extract structured resume information.
    """

    header = sections.get("header", "") or ""

    all_text = "\n".join(
        str(value) for value in sections.values()
    )

    # Name
    name = _extract_name(header)

    # Phone number: use the new validated phone extractor.
    phone_numbers = extract_phone_numbers(all_text)
    phone_number = phone_numbers[0] if phone_numbers else ""

    # Keep section boundaries so labelled addresses can be searched
    # throughout the resume without letting header fallback scan later sections.
    address_text = "\n\n".join(
        value if section == "header"
        else f"{section.replace('_', ' ')}\n{value}"
        for section, value in sections.items()
        if value
    )
    address = extract_address(address_text)
    # Email
    email_match = EMAIL_PATTERN.search(all_text)
    email = email_match.group(0) if email_match else ""

    # GitHub and LinkedIn
    found = {
        "github": "",
        "linkedin": ""
    }

    candidates = []

    for item in hyperlinks or []:
        if isinstance(item, str):
            candidates.append((item, ""))

        elif isinstance(item, dict):
            candidates.append((
                item.get("url", ""),
                item.get("text", "")
            ))

    for match in URL_PATTERN.findall(all_text):
        candidates.append((match, ""))

    for url, label in candidates:
        kind = _link_kind(url, label)
        clean = _clean_url(url)

        if kind and clean and not found[kind]:
            found[kind] = clean

    # Education
    education = (
        sections.get("education", "") or ""
    ).strip()

    # Technical skills
    technical_skills = (
        sections.get("technical_skills", "") or ""
    ).strip()

    # Experience
    experience = (
        sections.get("experience", "") or ""
    ).strip()

    return {
        "name": name,
        "phone_number": phone_number,
        "phone_numbers": phone_numbers,
        "address": address,
        "email": email,
        "github": found["github"],
        "linkedin": found["linkedin"],
        "education": education,
        "technical_skills": technical_skills,
        "experience": experience,
    }
