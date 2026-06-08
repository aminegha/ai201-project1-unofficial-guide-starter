from pathlib import Path
import json
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_PATH = Path("data/chunks.json")
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "wsu_off_campus_housing"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks(chunks_path: Path) -> List[Dict[str, Any]]:
    """
    Load chunks created by ingest.py.
    """
    if not chunks_path.exists():
        raise FileNotFoundError(
            f"Could not find {chunks_path}. Run `python ingest.py` first."
        )

    with chunks_path.open("r", encoding="utf-8") as f:
        chunks = json.load(f)

    if not chunks:
        raise ValueError("No chunks found in data/chunks.json.")

    return chunks


def get_embedding_model() -> SentenceTransformer:
    """
    Load local embedding model.
    First run may take time because the model downloads.
    """
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def get_chroma_collection(reset: bool = False):
    """
    Create or load a persistent ChromaDB collection.
    """
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        )
    return collection


def build_vector_store(reset: bool = True) -> None:
    """
    Embed all chunks and store them in ChromaDB with source metadata.
    """
    chunks = load_chunks(CHUNKS_PATH)
    model = get_embedding_model()
    collection = get_chroma_collection(reset=reset)

    ids = [chunk["id"] for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    metadatas = [
        {
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "char_count": chunk["char_count"],
        }
        for chunk in chunks
    ]

    print(f"Loaded {len(chunks)} chunks.")
    print(f"Embedding with {EMBEDDING_MODEL_NAME}...")

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB collection '{COLLECTION_NAME}'.")


def retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve top-k relevant chunks for a query.
    Returns text, source metadata, and distance score.
    """
    model = get_embedding_model()
    collection = get_chroma_collection(reset=False)

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for i in range(len(results["documents"][0])):
        retrieved.append(
            {
                "rank": i + 1,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return retrieved


def print_results(query: str, top_k: int = 5) -> None:
    """
    Pretty-print retrieval results for manual inspection.
    """
    print("\n" + "=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    results = retrieve(query, top_k=top_k)

    for result in results:
        metadata = result["metadata"]

        print("\n" + "-" * 100)
        print(f"Rank: {result['rank']}")
        print(f"Distance: {result['distance']:.4f}")
        print(f"Source: {metadata['source']}")
        print(f"Chunk index: {metadata['chunk_index']}")
        print("-" * 100)
        print(result["text"])


if __name__ == "__main__":
    # Step 1: Build vector store from data/chunks.json
    build_vector_store(reset=True)

    # Step 2: Test retrieval with evaluation-style questions
    test_queries = [
        "Which off-campus apartments near WSU do students recommend?",
        "Which apartments or property managers do students warn against?",
        "What do students say about DABCO or Churchill Downs?",
        "What factors matter most when choosing off-campus housing near WSU?",
        "What do students say about one-bedroom or studio apartments in Pullman?",
    ]

    for query in test_queries:
        print_results(query, top_k=5)