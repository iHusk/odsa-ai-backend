"""
filtered.py -- Metadata-filtered RAG retrieval.

This module extends naive RAG by adding ChromaDB `where` clauses to
filter chunks before ranking by similarity. This lets users narrow
retrieval to specific document types, categories, or other metadata.

Usage:
    from src.s4_retrieval.filtered import filtered_rag, compare_retrieval

    response = filtered_rag(
        "What are the fee structures?",
        filters={"category": "pricing"},
    )

    comparison = compare_retrieval(
        "What are the fee structures?",
        filters={"category": "pricing"},
    )
"""

from src.s2_embeddings.embed import embed_texts
from src.s0_generation.generate import call_claude_with_usage
from src.s3_ingestion.store import get_collection
from src.s4_retrieval.naive import RAGResponse, build_prompt, naive_retrieve


def filtered_retrieve(
    question: str, filters: dict, top_k: int = 5
) -> list[dict]:
    """Retrieve chunks filtered by metadata before ranking by similarity.

    Works like naive_retrieve but adds a ChromaDB `where` clause so
    only chunks matching the filter criteria are considered.

    Args:
        question: The user's question.
        filters: ChromaDB where clause (e.g., {"category": "pricing"}).
        top_k: Number of chunks to retrieve (default: 5).

    Returns:
        A list of dicts, each containing:
            - text: The chunk content.
            - metadata: The chunk's stored metadata.
            - score: Cosine similarity (1 - distance), higher is better.
        Returns an empty list if the filter matches no documents.
    """
    collection = get_collection()

    question_embedding = embed_texts([question])[0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=top_k,
        where=filters,
        include=["documents", "metadatas", "distances"],
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    if not documents:
        return []

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


def filtered_rag(
    question: str, filters: dict, top_k: int = 5
) -> RAGResponse:
    """Run the full filtered RAG pipeline: filter, retrieve, generate.

    Same as naive_rag but restricts retrieval to chunks matching the
    provided metadata filters.

    Args:
        question: The user's question.
        filters: ChromaDB where clause (e.g., {"category": "pricing"}).
        top_k: Number of chunks to retrieve (default: 5).

    Returns:
        A RAGResponse with the answer, sources, and token usage.
    """
    sources = filtered_retrieve(question, filters, top_k)

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


def compare_retrieval(
    question: str, filters: dict, top_k: int = 5
) -> dict:
    """Run both naive and filtered retrieval and compare results.

    This is the comparison helper students use in Lab 2 to evaluate
    whether metadata filtering improves retrieval quality for a given
    question.

    Args:
        question: The user's question.
        filters: ChromaDB where clause for the filtered pipeline.
        top_k: Number of chunks to retrieve from each pipeline (default: 5).

    Returns:
        A dict containing:
            - question: The input question.
            - filters: The filters applied to the filtered pipeline.
            - naive_sources: Results from naive_retrieve.
            - filtered_sources: Results from filtered_retrieve.
            - naive_top_score: Highest similarity score from naive retrieval.
            - filtered_top_score: Highest similarity score from filtered retrieval.
            - overlap: Number of chunks appearing in both result sets.
    """
    naive_results = naive_retrieve(question, top_k)
    filtered_results = filtered_retrieve(question, filters, top_k)

    naive_texts = {s["text"] for s in naive_results}
    filtered_texts = {s["text"] for s in filtered_results}
    overlap = len(naive_texts & filtered_texts)

    naive_top_score = naive_results[0]["score"] if naive_results else 0.0
    filtered_top_score = filtered_results[0]["score"] if filtered_results else 0.0

    return {
        "question": question,
        "filters": filters,
        "naive_sources": naive_results,
        "filtered_sources": filtered_results,
        "naive_top_score": naive_top_score,
        "filtered_top_score": filtered_top_score,
        "overlap": overlap,
    }
