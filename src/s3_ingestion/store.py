"""
store.py -- ChromaDB storage, ingestion, and verification.

This module handles persisting chunks into a ChromaDB vector store and
provides utilities for verifying ingestion and resetting collections.

Usage:
    from src.s3_ingestion.store import ingest_chunks, verify_ingestion, reset_collection
    from src.s3_ingestion.chunker import chunk_document

    chunks = chunk_document(text, source="memo_001.txt", doc_type="memo")
    result = ingest_chunks(chunks)
    print(result)  # {"ingested": 12, "collection": "northbrook"}

    hits = verify_ingestion("What was discussed in the meeting?")
    print(hits["documents"])
"""

import chromadb
from dotenv import load_dotenv

from src.s2_embeddings.embed import embed_texts
from src.s3_ingestion.chunker import Chunk

load_dotenv()

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "northbrook"


def get_collection(collection_name: str = COLLECTION_NAME) -> chromadb.Collection:
    """Get or create a ChromaDB collection with cosine similarity.

    Creates a persistent ChromaDB client and returns the named collection,
    creating it if it does not already exist.

    Args:
        collection_name: Name of the collection to retrieve or create.

    Returns:
        A ChromaDB Collection configured for cosine similarity.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def ingest_chunks(
    chunks: list[Chunk],
    collection_name: str = COLLECTION_NAME,
) -> dict:
    """Embed and store chunks in ChromaDB.

    Extracts text and metadata from each chunk, generates embeddings in
    batches of 50, and adds everything to the collection.

    Args:
        chunks: List of Chunk objects to ingest.
        collection_name: Target collection name.

    Returns:
        A dict with "ingested" (count) and "collection" (name).
    """
    collection = get_collection(collection_name)

    texts = [chunk.text for chunk in chunks]
    metadatas = [chunk.metadata for chunk in chunks]
    ids = [
        f"{chunk.metadata['source']}_chunk{chunk.metadata['chunk_index']}"
        for chunk in chunks
    ]

    # Batch embeddings in groups of 50
    batch_size = 50
    all_embeddings = []
    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(0, len(texts), batch_size):
        batch_num = i // batch_size + 1
        print(f"Embedding batch {batch_num}/{total_batches}...")
        batch = texts[i : i + batch_size]
        embeddings = embed_texts(batch)
        all_embeddings.extend(embeddings)

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=all_embeddings,
        metadatas=metadatas,
    )

    return {"ingested": len(chunks), "collection": collection_name}


def verify_ingestion(
    query_text: str,
    n_results: int = 3,
    collection_name: str = COLLECTION_NAME,
) -> dict:
    """Run a similarity query against the collection to verify ingestion.

    Embeds the query text and retrieves the nearest chunks from the
    collection. Useful for quick sanity checks after ingestion.

    Args:
        query_text: The text to search for.
        n_results: Number of results to return.
        collection_name: Collection to query.

    Returns:
        The raw ChromaDB query results dict (ids, documents, metadatas, distances).
    """
    collection = get_collection(collection_name)
    query_embedding = embed_texts([query_text])[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    return results


def reset_collection(collection_name: str = COLLECTION_NAME) -> None:
    """Delete and recreate a collection for clean re-ingestion.

    Args:
        collection_name: Collection to reset.
    """
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    client.delete_collection(name=collection_name)
    client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
