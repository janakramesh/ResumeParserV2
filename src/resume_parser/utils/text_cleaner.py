
import re


def normalize_resume_text(text: str) -> str:
    """
    Normalize resume text and remove common PDF template artifacts.
    Preserves actual resume content.
    """

    if not text:
        return ""

    # Normalize line endings.
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Normalize non-breaking spaces.
    text = text.replace("\u00a0", " ")

    # Remove multi-line template instructions beginning with (Tip: ...).
    text = re.sub(
        r"(?ims)^\s*\(Tip\s*:.*?\)\s*",
        "",
        text
    )

    # Remove standalone PDF page labels.
    text = re.sub(
        r"(?im)^\s*Page\s+\d+\s*$",
        "",
        text
    )

    # Remove trailing spaces from lines.
    lines = [line.rstrip() for line in text.split("\n")]

    # Remove excessive blank lines.
    cleaned_lines = []
    previous_blank = False

    for line in lines:
        if not line.strip():
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    text = "\n".join(cleaned_lines)

    # Normalize excessive spaces.
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Normalize excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def remove_pdf_line_hyphenation(text: str) -> str:
    """
    Join words broken by PDF line wrapping.
    """

    if not text:
        return ""

    return re.sub(
        r"(?<=[A-Za-z])-\n(?=[a-z])",
        lambda match: match.group(0),
        text
    )
