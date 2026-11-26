import re
from urllib.parse import urlparse

EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
NON_NAME_LABELS = {
    "about",
    "contents",
    "cv",
    "index",
    "portfolio",
    "profile",
    "resume",
}
ROLE_WORDS = {
    "analyst",
    "architect",
    "consultant",
    "developer",
    "director",
    "engineer",
    "executive",
    "leader",
    "manager",
    "mentor",
    "professional",
    "specialist",
    "strategist",
    "technologist",
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
            or re.search(r"\+?\d[\d ()-]{7,}", candidate)
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


def extract_structured_fields(sections: dict, hyperlinks: list | None = None) -> dict:
    """Build the six user-facing resume fields from analyzed sections and links."""
    header = sections.get("header", "") or ""
    all_text = "\n".join(str(value) for value in sections.values())

    email_match = EMAIL_PATTERN.search(all_text)
    email = email_match.group(0) if email_match else ""

    name = _extract_name(header)

    found = {"github": "", "linkedin": ""}
    candidates = []
    for item in hyperlinks or []:
        if isinstance(item, str):
            candidates.append((item, ""))
        elif isinstance(item, dict):
            candidates.append((item.get("url", ""), item.get("text", "")))
    for match in URL_PATTERN.findall(all_text):
        candidates.append((match, ""))

    for url, label in candidates:
        kind = _link_kind(url, label)
        clean = _clean_url(url)
        if kind and clean and not found[kind]:
            found[kind] = clean

    education = (sections.get("education", "") or "").strip()
    technical_skills = (sections.get("technical_skills", "") or "").strip()

    return {
        "name": name,
        "email": email,
        "github": found["github"],
        "linkedin": found["linkedin"],
        "education": education,
        "technical_skills": technical_skills,
    }
