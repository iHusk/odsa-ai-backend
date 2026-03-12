"""
chunker.py -- Text chunking with metadata for vector ingestion.

This module provides two chunking strategies:
  - chunk_document: paragraph-aware chunking (merges small paragraphs, respects boundaries)
  - chunk_fixed: simple fixed-size chunking (every N tokens with overlap)

The paragraph-aware strategy is the default for the ingestion pipeline.
The fixed-size strategy exists for comparison in notebooks.

All sizing is token-based using the cl100k_base tokenizer (tiktoken).

Usage:
    from src.s3_ingestion.chunker import chunk_document, chunk_fixed, Chunk, count_tokens

    chunks = chunk_document(text, source="memo_001.txt", doc_type="memo")
    chunks_fixed = chunk_fixed(text, source="memo_001.txt")
"""

from dataclasses import dataclass

import tiktoken

_ENCODER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Count tokens using cl100k_base encoding."""
    return len(_ENCODER.encode(text))


@dataclass
class Chunk:
    """A piece of text with associated metadata for vector storage."""

    text: str
    metadata: dict


def _sanitize_metadata(metadata: dict) -> dict:
    """Ensure all metadata values are simple types that ChromaDB accepts.

    ChromaDB rejects None, lists, and nested dicts in metadata.
    This function replaces None with empty string and filters out
    any values that are not str, int, float, or bool.

    Args:
        metadata: Raw metadata dictionary.

    Returns:
        A cleaned dictionary with only simple-typed values.
    """
    clean = {}
    for key, value in metadata.items():
        if value is None:
            clean[key] = ""
        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value
        # Skip lists, dicts, and other complex types
    return clean


def chunk_document(
    text: str,
    source: str,
    chunk_size: int = 128,
    overlap: int = 25,
    doc_type: str = "unknown",
    extra_metadata: dict | None = None,
) -> list[Chunk]:
    """Split text into chunks using a paragraph-aware strategy.

    Strategy:
      1. Split on double newlines into paragraphs
      2. Merge small paragraphs until reaching chunk_size tokens
      3. When a merge would exceed chunk_size, save and start a new chunk
      4. Apply overlap by prepending the last `overlap` tokens from
         the previous chunk to the start of the next

    Args:
        text: The full document text to chunk.
        source: Source identifier (e.g., filename).
        chunk_size: Target maximum tokens per chunk.
        overlap: Number of tokens from the end of the previous chunk
                 to prepend to the next chunk.
        doc_type: Document type label for metadata (e.g., "memo", "policy").
        extra_metadata: Additional key-value pairs to include in each chunk's
                        metadata. Values must be simple types (str, int, float, bool).

    Returns:
        A list of Chunk objects with text and metadata.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    if not paragraphs:
        return []

    # Merge paragraphs into chunks
    raw_chunks = []
    current = paragraphs[0]

    for paragraph in paragraphs[1:]:
        merged = current + "\n\n" + paragraph

        if count_tokens(merged) <= chunk_size:
            current = merged
        else:
            raw_chunks.append(current)
            current = paragraph

    # Don't forget the last accumulated chunk
    raw_chunks.append(current)

    # Apply overlap between consecutive chunks
    final_texts = []
    for i, chunk_text in enumerate(raw_chunks):
        if i > 0 and overlap > 0:
            previous = raw_chunks[i - 1]
            prev_tokens = _ENCODER.encode(previous)
            overlap_tokens = prev_tokens[-overlap:]
            overlap_text = _ENCODER.decode(overlap_tokens)
            chunk_text = overlap_text + " " + chunk_text

        final_texts.append(chunk_text.strip())

    # Build Chunk objects with metadata
    base_metadata = {"source": source, "doc_type": doc_type}
    if extra_metadata:
        base_metadata.update(extra_metadata)

    chunks = []
    for i, chunk_text in enumerate(final_texts):
        metadata = {
            **base_metadata,
            "chunk_index": i,
            "token_count": count_tokens(chunk_text),
        }
        chunks.append(Chunk(text=chunk_text, metadata=_sanitize_metadata(metadata)))

    return chunks


def chunk_fixed(
    text: str,
    source: str,
    chunk_size: int = 128,
    overlap: int = 25,
    doc_type: str = "unknown",
) -> list[Chunk]:
    """Split text into fixed-size chunks with overlap.

    Token-based chunking -- every chunk_size tokens, with overlap tokens
    carried over from the previous chunk. This strategy ignores paragraph
    boundaries and exists for comparison with the paragraph-aware strategy
    in notebooks.

    Args:
        text: The full document text to chunk.
        source: Source identifier (e.g., filename).
        chunk_size: Number of tokens per chunk.
        overlap: Number of tokens to overlap between consecutive chunks.
        doc_type: Document type label for metadata.

    Returns:
        A list of Chunk objects with text and metadata.
    """
    if not text.strip():
        return []

    tokens = _ENCODER.encode(text)
    chunks = []
    start = 0
    chunk_index = 0
    stride = chunk_size - overlap

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = _ENCODER.decode(chunk_tokens).strip()

        if chunk_text:
            metadata = _sanitize_metadata({
                "source": source,
                "chunk_index": chunk_index,
                "doc_type": doc_type,
                "token_count": len(chunk_tokens),
            })
            chunks.append(Chunk(text=chunk_text, metadata=metadata))
            chunk_index += 1

        start += stride

    return chunks
