"""
extractor.py -- Use Claude to extract structured data from documents.

This module provides two functions:
  - extract_single: extract structured data from a single document string
  - extract_batch: process a list of files and return results for each

Usage:
    from src.s1_extraction.extractor import extract_single, extract_batch
    from src.s1_extraction.schemas import MemoExtraction

    memo = extract_single(document_text, MemoExtraction)
    results = extract_batch(["docs/memo1.txt", "docs/memo2.txt"], MemoExtraction)
"""

from dataclasses import dataclass
from pathlib import Path

import anthropic
from pydantic import BaseModel


SYSTEM_PROMPT = (
    "You are a document extraction assistant. "
    "Extract structured data from the provided document accurately and completely."
)

client = anthropic.Anthropic()


@dataclass
class ExtractionResult:
    """Container for the outcome of a single extraction attempt."""

    file_path: str
    success: bool
    data: BaseModel | None = None
    error: str | None = None


def extract_single(
    document_text: str, schema_class: type[BaseModel]
) -> BaseModel:
    """Extract structured data from a single document using Claude.

    Uses Claude's native structured output (output_format) to guarantee
    valid JSON matching the schema via constrained decoding. No manual
    JSON parsing or markdown stripping needed.

    Args:
        document_text: The raw text content to extract from.
        schema_class: The Pydantic model class defining the expected output shape.

    Returns:
        A validated instance of schema_class populated with extracted data.
    """
    response = client.messages.parse(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        temperature=0.0,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Extract structured data from this document:\n\n{document_text}",
            }
        ],
        output_format=schema_class,
    )
    return response.parsed_output


def extract_batch(
    file_paths: list[str], schema_class: type[BaseModel]
) -> list[ExtractionResult]:
    """Extract structured data from a batch of files.

    Processes each file sequentially, capturing successes and failures
    without crashing. Every file produces an ExtractionResult regardless
    of whether extraction succeeded or failed.

    Args:
        file_paths: List of file paths to process.
        schema_class: The Pydantic model class defining the expected output shape.

    Returns:
        A list of ExtractionResult objects, one per input file.
    """
    results: list[ExtractionResult] = []

    for i, path in enumerate(file_paths):
        print(f"Processing {i + 1}/{len(file_paths)}: {path}")

        try:
            document_text = Path(path).read_text()
            data = extract_single(document_text, schema_class)
            results.append(
                ExtractionResult(file_path=path, success=True, data=data)
            )
        except Exception as exc:
            results.append(
                ExtractionResult(
                    file_path=path, success=False, error=str(exc)
                )
            )

    return results
