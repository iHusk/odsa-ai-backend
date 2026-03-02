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

import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ValidationError

from src.s0_generation.generate import call_claude


SYSTEM_PROMPT = (
    "You are a document extraction assistant. "
    "Return ONLY valid JSON matching the provided schema. "
    "No markdown, no explanation, just JSON."
)


@dataclass
class ExtractionResult:
    """Container for the outcome of a single extraction attempt."""

    file_path: str
    success: bool
    data: BaseModel | None = None
    error: str | None = None


def _strip_markdown_json(text: str) -> str:
    """Remove markdown code fences (```json ... ```) if present.

    Args:
        text: Raw response text from Claude.

    Returns:
        The JSON string with any surrounding markdown fences removed.
    """
    stripped = text.strip()
    match = re.match(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", stripped, re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def extract_single(
    document_text: str, schema_class: type[BaseModel]
) -> BaseModel:
    """Extract structured data from a single document using Claude.

    Sends the document text and the target JSON schema to Claude,
    then validates the response against the Pydantic model.

    Args:
        document_text: The raw text content to extract from.
        schema_class: The Pydantic model class defining the expected output shape.

    Returns:
        A validated instance of schema_class populated with extracted data.

    Raises:
        ValidationError: If Claude's response does not match the schema.
        json.JSONDecodeError: If Claude's response is not valid JSON.
    """
    schema_json = json.dumps(schema_class.model_json_schema(), indent=2)

    user_prompt = (
        f"Extract data from the following document into this JSON schema:\n\n"
        f"--- SCHEMA ---\n{schema_json}\n\n"
        f"--- DOCUMENT ---\n{document_text}"
    )

    response_text = call_claude(
        prompt=user_prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.0,
    )

    cleaned = _strip_markdown_json(response_text)
    parsed = json.loads(cleaned)
    return schema_class.model_validate(parsed)


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
