"""
Document parsing utilities for Deal Signal experiments.
Supports multiple parsing approaches for Layer 3 comparison.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json


@dataclass
class ParsedDocument:
    """Result of parsing a document."""

    source_path: str
    parser: str  # Which parser was used
    text: str  # Extracted text
    pages: list[str]  # Text per page (if available)
    tables: list[dict]  # Extracted tables (if available)
    metadata: dict  # Document metadata


def parse_pdf_basic(path: str) -> ParsedDocument:
    """
    Basic PDF text extraction using pypdf.
    Lowest cost, lowest quality baseline.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("pip install pypdf")

    reader = PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]

    return ParsedDocument(
        source_path=path,
        parser="pypdf",
        text="\n\n".join(pages),
        pages=pages,
        tables=[],
        metadata={
            "num_pages": len(reader.pages),
            "info": dict(reader.metadata) if reader.metadata else {},
        },
    )


def parse_pdf_pdfplumber(path: str) -> ParsedDocument:
    """
    PDF extraction using pdfplumber.
    Better table extraction than pypdf.
    """
    try:
        import pdfplumber
    except ImportError:
        raise ImportError("pip install pdfplumber")

    pages = []
    tables = []

    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            pages.append(page.extract_text() or "")

            # Extract tables from this page
            for table in page.extract_tables():
                tables.append(
                    {
                        "page": i + 1,
                        "data": table,
                    }
                )

    return ParsedDocument(
        source_path=path,
        parser="pdfplumber",
        text="\n\n".join(pages),
        pages=pages,
        tables=tables,
        metadata={"num_pages": len(pages)},
    )


def parse_pdf_marker(path: str) -> ParsedDocument:
    """
    PDF extraction using marker (ML-based).
    Higher quality, handles complex layouts.
    """
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
    except ImportError:
        raise ImportError("pip install marker-pdf")

    models = create_model_dict()
    converter = PdfConverter(artifact_dict=models)
    result = converter(path)

    return ParsedDocument(
        source_path=path,
        parser="marker",
        text=result.markdown,
        pages=[],  # Marker returns full document
        tables=[],  # Tables embedded in markdown
        metadata=result.metadata,
    )


def save_parsed(doc: ParsedDocument, output_dir: str) -> None:
    """Save parsed document to directory."""
    os.makedirs(output_dir, exist_ok=True)

    # Save full text
    text_path = os.path.join(output_dir, "text.txt")
    with open(text_path, "w") as f:
        f.write(doc.text)

    # Save pages separately
    if doc.pages:
        pages_dir = os.path.join(output_dir, "pages")
        os.makedirs(pages_dir, exist_ok=True)
        for i, page in enumerate(doc.pages):
            page_path = os.path.join(pages_dir, f"page_{i + 1:03d}.txt")
            with open(page_path, "w") as f:
                f.write(page)

    # Save tables
    if doc.tables:
        tables_path = os.path.join(output_dir, "tables.json")
        with open(tables_path, "w") as f:
            json.dump(doc.tables, f, indent=2)

    # Save metadata
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(
            {
                "source_path": doc.source_path,
                "parser": doc.parser,
                "metadata": doc.metadata,
            },
            f,
            indent=2,
        )


def load_parsed(output_dir: str) -> ParsedDocument:
    """Load parsed document from directory."""
    text_path = os.path.join(output_dir, "text.txt")
    meta_path = os.path.join(output_dir, "metadata.json")
    tables_path = os.path.join(output_dir, "tables.json")

    with open(text_path) as f:
        text = f.read()

    with open(meta_path) as f:
        meta = json.load(f)

    tables = []
    if os.path.exists(tables_path):
        with open(tables_path) as f:
            tables = json.load(f)

    # Load pages if they exist
    pages = []
    pages_dir = os.path.join(output_dir, "pages")
    if os.path.isdir(pages_dir):
        for page_file in sorted(os.listdir(pages_dir)):
            with open(os.path.join(pages_dir, page_file)) as f:
                pages.append(f.read())

    return ParsedDocument(
        source_path=meta["source_path"],
        parser=meta["parser"],
        text=text,
        pages=pages,
        tables=tables,
        metadata=meta["metadata"],
    )
