from typing import Dict, List, Any

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve, build_vector_store, get_chroma_collection


load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"
TOP_K = 5


def ensure_vector_store_ready() -> None:
    """
    Make sure the ChromaDB vector store exists and has chunks.
    If it does not exist or is empty, rebuild it from data/chunks.json.
    """
    collection = get_chroma_collection(reset=False)

    if collection.count() == 0:
        print("Vector store is empty. Building it from data/chunks.json...")
        build_vector_store(reset=True)


def format_context(retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Format retrieved chunks for the LLM prompt.
    Each chunk includes source metadata so the model can ground its answer.
    """
    context_blocks = []

    for item in retrieved_chunks:
        metadata = item["metadata"]
        source = metadata["source"]
        chunk_index = metadata["chunk_index"]
        text = item["text"]

        block = (
            f"[Source: {source}, chunk {chunk_index}]\n"
            f"{text}"
        )
        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)


def get_sources(retrieved_chunks: List[Dict[str, Any]]) -> List[str]:
    """
    Programmatically collect unique sources from retrieved chunks.
    This guarantees source attribution even if the LLM forgets to cite.
    """
    sources = []

    for item in retrieved_chunks:
        metadata = item["metadata"]
        source_label = f"{metadata['source']} — chunk {metadata['chunk_index']}"

        if source_label not in sources:
            sources.append(source_label)

    return sources


def generate_answer(question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    Generate a grounded answer using Groq.
    The model is instructed to answer only from retrieved context.
    """
    client = Groq()

    context = format_context(retrieved_chunks)

    system_prompt = """
You are a grounded question-answering assistant for a RAG system.

Rules:
1. Answer using ONLY the provided context.
2. Do NOT use outside knowledge.
3. Do NOT make up apartment names, prices, policies, or recommendations.
4. If the context does not contain enough information, say:
   "I don't have enough information in the provided documents to answer that."
5. Cite sources inline in plain text only, like: (source: reddit_example.txt, chunk 2). Do not create markdown links.
6. Be concise but specific.
""".strip()

    user_prompt = f"""
Question:
{question}

Retrieved context:
{context}

Answer:
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
        max_tokens=700,
    )

    return response.choices[0].message.content.strip()


def ask(question: str, top_k: int = TOP_K) -> Dict[str, Any]:
    """
    End-to-end RAG function:
    question -> retrieve chunks -> generate grounded answer -> return answer + sources.
    """
    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "sources": [],
            "retrieved_chunks": [],
        }

    ensure_vector_store_ready()

    retrieved_chunks = retrieve(question, top_k=top_k)
    answer = generate_answer(question, retrieved_chunks)
    sources = get_sources(retrieved_chunks)

    return {
        "answer": answer,
        "sources": sources,
        "retrieved_chunks": retrieved_chunks,
    }


def print_answer(question: str) -> None:
    """
    CLI helper for testing grounded generation.
    """
    result = ask(question)

    print("\n" + "=" * 100)
    print(f"QUESTION: {question}")
    print("=" * 100)

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(f"- {source}")

    print("\nRETRIEVED CHUNKS:")
    for chunk in result["retrieved_chunks"]:
        metadata = chunk["metadata"]
        print(
            f"- distance={chunk['distance']:.4f}, "
            f"source={metadata['source']}, "
            f"chunk={metadata['chunk_index']}"
        )


if __name__ == "__main__":
    test_questions = [
        "Which off-campus apartments near WSU do students recommend?",
        "What do students say about DABCO or Churchill Downs?",
        "Which apartments or property managers do students warn against?",
        "What is the best laptop for computer science students?",
    ]

    for q in test_questions:
        print_answer(q)