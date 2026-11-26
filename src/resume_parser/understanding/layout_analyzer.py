
"""
Analyzes PDF resume layouts and reconstructs text reading order.

Features:
- Extract text blocks and bounding boxes.
- Estimate single-column or two-column layouts.
- Identify full-width blocks.
- Reconstruct approximate reading order.
"""

from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass
class TextBlock:
    page_number: int
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    font_size: float

    @property
    def width(self):
        return self.x1 - self.x0

    @property
    def height(self):
        return self.y1 - self.y0


@dataclass
class PageLayout:
    page_number: int
    page_width: float
    page_height: float
    blocks: list
    columns: int


def extract_page_blocks(page, page_number):
    """Extract text blocks with their spatial information."""

    data = page.get_text("dict")
    blocks = []

    for block in data.get("blocks", []):

        if block.get("type") != 0:
            continue

        lines = []
        font_sizes = []

        for line in block.get("lines", []):

            line_text = "".join(
                span.get("text", "")
                for span in line.get("spans", [])
            )

            if line_text.strip():
                lines.append(line_text)

            for span in line.get("spans", []):

                if span.get("text", "").strip():
                    font_sizes.append(span.get("size", 0))

        text = "\n".join(lines).strip()

        if not text:
            continue

        bbox = block.get("bbox")

        if not bbox or len(bbox) != 4:
            continue

        blocks.append(
            TextBlock(
                page_number=page_number,
                text=text,
                x0=bbox[0],
                y0=bbox[1],
                x1=bbox[2],
                y1=bbox[3],
                font_size=(
                    sum(font_sizes) / len(font_sizes)
                    if font_sizes else 0
                )
            )
        )

    return blocks


def _is_full_width(block, page_width):
    """
    Identify blocks that span most of the page width.

    These blocks may represent page headings or paragraphs
    that sit above, below, or between columns.
    """

    return (
        block.x0 <= page_width * 0.15
        and block.x1 >= page_width * 0.85
    )


def detect_columns(blocks, page_width):
    """Estimate whether a page contains one or two columns."""

    if len(blocks) < 2 or page_width <= 0:
        return 1

    page_center = page_width / 2

    # Exclude full-width blocks before detecting columns.
    candidate_blocks = [
        block for block in blocks
        if not _is_full_width(block, page_width)
    ]

    left_blocks = [
        block for block in candidate_blocks
        if (block.x0 + block.x1) / 2 < page_center
    ]

    right_blocks = [
        block for block in candidate_blocks
        if (block.x0 + block.x1) / 2 >= page_center
    ]

    if not left_blocks or not right_blocks:
        return 1

    # Use median boundaries to reduce the effect of
    # unusually wide individual text blocks.
    left_right_edges = sorted(
        block.x1 for block in left_blocks
    )

    right_left_edges = sorted(
        block.x0 for block in right_blocks
    )

    median_left_edge = left_right_edges[
        len(left_right_edges) // 2
    ]

    median_right_edge = right_left_edges[
        len(right_left_edges) // 2
    ]

    # A visible horizontal gap is needed between columns.
    if median_left_edge < median_right_edge:
        return 2

    return 1


def analyze_page_layout(page, page_number):
    """Analyze the layout of one already-open PDF page."""

    blocks = extract_page_blocks(page, page_number)

    return PageLayout(
        page_number=page_number,
        page_width=page.rect.width,
        page_height=page.rect.height,
        blocks=blocks,
        columns=detect_columns(blocks, page.rect.width)
    )


def _sort_column_blocks(blocks):
    """Read a group of blocks from top to bottom."""

    return sorted(
        blocks,
        key=lambda block: (block.y0, block.x0)
    )


def _read_column_region(blocks, page_width):
    """
    Read a vertical region containing two columns.

    The left column is read first, followed by the right column.
    """

    page_center = page_width / 2

    left_blocks = []
    right_blocks = []

    for block in blocks:

        center_x = (block.x0 + block.x1) / 2

        if center_x < page_center:
            left_blocks.append(block)
        else:
            right_blocks.append(block)

    ordered = (
        _sort_column_blocks(left_blocks)
        + _sort_column_blocks(right_blocks)
    )

    return ordered


def reconstruct_reading_order(layout):
    """
    Reconstruct approximate reading order from a page layout.

    For two-column pages:
    - Full-width blocks act as vertical separators.
    - Each region is read left column first, then right column.

    For single-column pages:
    - Blocks are read from top to bottom.
    """

    blocks = layout.blocks

    if not blocks:
        return ""

    if layout.columns == 1:
        ordered_blocks = sorted(
            blocks,
            key=lambda block: (block.y0, block.x0)
        )

    else:
        full_width_blocks = [
            block for block in blocks
            if _is_full_width(block, layout.page_width)
        ]

        column_blocks = [
            block for block in blocks
            if not _is_full_width(block, layout.page_width)
        ]

        full_width_blocks.sort(
            key=lambda block: (block.y0, block.x0)
        )

        remaining_blocks = list(column_blocks)
        ordered_blocks = []

        for separator in full_width_blocks:

            # Collect blocks occurring before this separator.
            current_region = [
                block for block in remaining_blocks
                if block.y0 < separator.y0
            ]

            ordered_blocks.extend(
                _read_column_region(
                    current_region,
                    layout.page_width
                )
            )

            # Remove blocks already processed.
            processed_ids = {
                id(block) for block in current_region
            }

            remaining_blocks = [
                block for block in remaining_blocks
                if id(block) not in processed_ids
            ]

            # Preserve the full-width block at its vertical position.
            ordered_blocks.append(separator)

        # Process everything below the last full-width block.
        ordered_blocks.extend(
            _read_column_region(
                remaining_blocks,
                layout.page_width
            )
        )

    return "\n".join(
        block.text for block in ordered_blocks
    ).strip()


def analyze_pdf_layout(file_path: Path):
    """Analyze every page of a digital PDF."""

    file_path = Path(file_path)
    layouts = []

    with pymupdf.open(file_path) as pdf:

        if pdf.is_encrypted:
            raise ValueError("Password-protected PDF")

        if len(pdf) == 0:
            raise ValueError("PDF contains no pages")

        for page_number, page in enumerate(pdf, start=1):

            layouts.append(
                analyze_page_layout(page, page_number)
            )

    return layouts

def extract_layout_regions(layout):
    """
    Preserve separate text regions on a PDF page.

    For two-column pages, left and right column content
    is returned separately instead of being flattened.

    Full-width blocks are preserved between regions.
    """

    blocks = layout.blocks

    if not blocks:
        return []

    if layout.columns == 1:
        ordered = sorted(
            blocks,
            key=lambda block: (block.y0, block.x0)
        )
        text = "\n".join(block.text for block in ordered).strip()
        return [text] if text else []

    full_width_blocks = sorted(
        [
            block for block in blocks
            if _is_full_width(block, layout.page_width)
        ],
        key=lambda block: (block.y0, block.x0)
    )

    column_blocks = [
        block for block in blocks
        if not _is_full_width(block, layout.page_width)
    ]

    regions = []
    remaining_blocks = list(column_blocks)
    previous_y = float("-inf")

    def add_column_regions(region_blocks):
        if not region_blocks:
            return

        page_center = layout.page_width / 2

        left_blocks = [
            block for block in region_blocks
            if (block.x0 + block.x1) / 2 < page_center
        ]

        right_blocks = [
            block for block in region_blocks
            if (block.x0 + block.x1) / 2 >= page_center
        ]

        for column in (left_blocks, right_blocks):
            ordered = sorted(
                column,
                key=lambda block: (block.y0, block.x0)
            )

            text = "\n".join(
                block.text for block in ordered
            ).strip()

            if text:
                regions.append(text)

    for separator in full_width_blocks:
        current_region = [
            block for block in remaining_blocks
            if previous_y <= block.y0 < separator.y0
        ]

        add_column_regions(current_region)

        processed_ids = {
            id(block) for block in current_region
        }

        remaining_blocks = [
            block for block in remaining_blocks
            if id(block) not in processed_ids
        ]

        if separator.text.strip():
            regions.append(separator.text.strip())

        previous_y = separator.y1

    add_column_regions(remaining_blocks)

    return regions
