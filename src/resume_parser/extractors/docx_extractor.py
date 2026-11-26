
from pathlib import Path
from dataclasses import dataclass

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl


@dataclass
class DOCXExtractionResult:
    file_name: str
    extracted_text: str
    total_paragraphs: int
    total_tables: int
    successful: bool
    error: str = ""
    hyperlinks: list[dict] = None


def extract_hyperlinks(paragraph):
    """Extract hyperlinks from a paragraph."""

    hyperlinks = []

    for hyperlink in paragraph._p.xpath(
        './/w:hyperlink'
    ):
        text = "".join(
            node.text or ""
            for node in hyperlink.xpath('.//w:t')
        )

        if text.strip():
            hyperlinks.append(text.strip())

    return hyperlinks


def extract_hyperlink_details(paragraph):
    """Return hyperlink display text and its actual relationship URL."""
    details = []
    for hyperlink in paragraph._p.xpath('.//w:hyperlink'):
        rel_id = hyperlink.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
        text = "".join(node.text or "" for node in hyperlink.xpath('.//w:t')).strip()
        if rel_id and rel_id in paragraph.part.rels:
            target = paragraph.part.rels[rel_id].target_ref
            if target:
                details.append({"url": target, "text": text})
    return details


def extract_paragraph_content(paragraph):
    """Extract paragraph text and hyperlinks."""

    text = paragraph.text.strip()

    hyperlinks = extract_hyperlinks(paragraph)

    # Avoid duplicating hyperlink text already included.
    for hyperlink in hyperlinks:
        if hyperlink not in text:
            text += f" {hyperlink}"

    return text


def iter_block_items(parent):
    """
    Iterate over paragraphs and tables in their original
    document order.
    """

    if hasattr(parent, "element"):
        parent_element = parent.element.body
    else:
        parent_element = parent._tc

    for child in parent_element.iterchildren():

        if isinstance(child, CT_P):
            yield Paragraph(child, parent)

        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def extract_table_content(table, output, depth=0, hyperlinks=None):
    """
    Extract table cells, including nested tables.
    """

    for row in table.rows:

        row_content = []

        for cell in row.cells:

            cell_content = []

            for block in iter_block_items(cell):

                if isinstance(block, Paragraph):

                    text = extract_paragraph_content(block)
                    if hyperlinks is not None:
                        hyperlinks.extend(extract_hyperlink_details(block))

                    if text:
                        cell_content.append(text)

                elif isinstance(block, Table):

                    nested_content = []
                    extract_table_content(
                        block,
                        nested_content,
                        depth + 1,
                        hyperlinks
                    )

                    cell_content.extend(nested_content)

            if cell_content:
                row_content.append(" | ".join(cell_content))

        if row_content:
            output.append(
                " | ".join(row_content)
            )


def extract_docx_text(file_path: Path) -> DOCXExtractionResult:
    """
    Extract text from DOCX documents.

    Supports:
    - Paragraphs
    - Headings
    - Tables
    - Nested tables
    - Hyperlinks
    - Headers and footers
    """

    file_path = Path(file_path)

    try:

        document = Document(file_path)

        extracted_content = []
        all_hyperlinks = []

        paragraph_count = 0
        table_count = 0

        # Extract body content in document order.
        for block in iter_block_items(document):

            if isinstance(block, Paragraph):

                text = extract_paragraph_content(block)
                all_hyperlinks.extend(extract_hyperlink_details(block))

                if text:

                    extracted_content.append(text)
                    paragraph_count += 1

            elif isinstance(block, Table):

                table_content = []

                extract_table_content(
                    block,
                    table_content,
                    hyperlinks=all_hyperlinks
                )

                if table_content:

                    extracted_content.append(
                        "\n".join(table_content)
                    )

                    table_count += 1

        # Extract headers and footers.
        for section_number, section in enumerate(
            document.sections, start=1
        ):

            if section.header:

                for paragraph in section.header.paragraphs:

                    text = extract_paragraph_content(paragraph)
                    all_hyperlinks.extend(extract_hyperlink_details(paragraph))

                    if text:
                        extracted_content.append(
                            f"[HEADER {section_number}] {text}"
                        )

            if section.footer:

                for paragraph in section.footer.paragraphs:

                    text = extract_paragraph_content(paragraph)
                    all_hyperlinks.extend(extract_hyperlink_details(paragraph))

                    if text:
                        extracted_content.append(
                            f"[FOOTER {section_number}] {text}"
                        )

        full_text = "\n".join(extracted_content).strip()

        if not full_text:
            raise ValueError(
                "No readable text found in DOCX document"
            )

        return DOCXExtractionResult(
            file_name=file_path.name,
            extracted_text=full_text,
            total_paragraphs=paragraph_count,
            total_tables=table_count,
            successful=True,
            hyperlinks=all_hyperlinks
        )

    except Exception as error:

        return DOCXExtractionResult(
            file_name=file_path.name,
            extracted_text="",
            total_paragraphs=0,
            total_tables=0,
            successful=False,
            error=str(error)
        )