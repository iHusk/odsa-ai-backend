"""
naive.py -- Naive RAG retrieval using pure semantic similarity.

This module implements the simplest RAG pattern: embed the question,
find the closest chunks in the vector store, and pass them to Claude
as context for generating an answer.

Usage:
    from src.s4_retrieval.naive import naive_rag, naive_retrieve

    results = naive_retrieve("What services does Northbrook offer?")
    response = naive_rag("What services does Northbrook offer?")
    print(response.answer)
"""

from dataclasses import dataclass

from src.s2_embeddings.embed import embed_texts
from src.s0_generation.generate import call_claude_with_usage
from src.s3_ingestion.store import get_collection


@dataclass
class RAGResponse:
    """Container for a RAG pipeline response with token usage metadata."""

    question: str
    answer: str
    sources: list[dict]
    input_tokens: int
    output_tokens: int
    model: str


def naive_retrieve(question: str, top_k: int = 5) -> list[dict]:
    """Retrieve the most semantically similar chunks for a question.

    Embeds the question using the same model that embedded the documents,
    then queries ChromaDB for the nearest neighbors.

    Args:
        question: The user's question.
        top_k: Number of chunks to retrieve (default: 5).

    Returns:
        A list of dicts, each containing:
            - text: The chunk content.
            - metadata: The chunk's stored metadata.
            - score: Cosine similarity (1 - distance), higher is better.
    """
    collection = get_collection()

    question_embedding = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    sources = [
        {
            "text": doc,
            "metadata": meta,
            "score": 1 - dist,
        }
        for doc, meta, dist in zip(documents, metadatas, distances)
    ]

    sources.sort(key=lambda s: s["score"], reverse=True)

    return sources


def build_prompt(question: str, sources: list[dict]) -> tuple[str, str]:
    """Build the system prompt and user message for Claude.

    Formats retrieved sources into a structured context block that
    Claude can reference when answering the question.

    Args:
        question: The user's question.
        sources: Retrieved chunks from naive_retrieve or filtered_retrieve.

    Returns:
        A tuple of (system_prompt, user_message).
    """
    system_prompt = (
        "You are a Q&A assistant for Northbrook Partners. "
        "Answer using ONLY the provided context. "
        "Cite your sources by name. "
        "If the context is insufficient, say: "
        "'I don't have enough information to answer that question.'"
    )

    context_blocks = []
    for source in sources:
        source_name = source["metadata"].get("source", "Unknown")
        score = source["score"]
        text = source["text"]
        context_blocks.append(f"[Source: {source_name}, Score: {score:.3f}]\n{text}")

    context_section = "\n\n---\n\n".join(context_blocks)

    user_message = f"Context:\n\n{context_section}\n\n---\n\nQuestion: {question}"

    return system_prompt, user_message


def naive_rag(question: str, top_k: int = 5) -> RAGResponse:
    """Run the full naive RAG pipeline: retrieve, build prompt, generate.

    This is the end-to-end function that students will call in their
    notebooks and labs. It retrieves relevant chunks, formats them as
    context, and sends the question to Claude for answering.

    Args:
        question: The user's question.
        top_k: Number of chunks to retrieve (default: 5).

    Returns:
        A RAGResponse with the answer, sources, and token usage.
    """
    sources = naive_retrieve(question, top_k)

    if not sources:
        return RAGResponse(
            question=question,
            answer="No relevant documents found.",
            sources=[],
            input_tokens=0,
            output_tokens=0,
            model="",
        )

    system_prompt, user_message = build_prompt(question, sources)

    result = call_claude_with_usage(
        prompt=user_message,
        system_prompt=system_prompt,
        temperature=0.0,
    )

    return RAGResponse(
        question=question,
        answer=result["text"],
        sources=sources,
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        model=result["model"],
    )
