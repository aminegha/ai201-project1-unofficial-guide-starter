from pathlib import Path
import json
import random
import re
from typing import List, Dict


RAW_DIR = Path("documents/raw")
OUTPUT_PATH = Path("data/chunks.json")

# Planning.md says approx. 600–900 characters.
# We use 900 as the max and preserve full Reddit entries when possible.
CHUNK_SIZE = 900

# No overlap between normal Reddit comment chunks.
# Character overlap caused chunks to start in the middle of words.
CHUNK_OVERLAP = 0

MIN_CHUNK_LENGTH = 80


def clean_text(text: str) -> str:
    """
    Clean raw copied/extracted text from Reddit/WSU pages.
    Removes obvious web artifacts while keeping student opinions and context.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    replacements = {
        "&amp;": "&",
        "&nbsp;": " ",
        "&quot;": '"',
        "&#39;": "'",
        "&lt;": "<",
        "&gt;": ">",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove HTML tags if any accidentally copied.
    text = re.sub(r"<[^>]+>", " ", text)

    # Remove common Reddit/UI artifacts.
    ui_phrases = [
        "A place to post anything about WSU",
        "Use of flair highly encouraged",
        "FLAIR GUIDELINES",
        "CONTACT THE MODS",
        "Message the moderators",
        "Apply to be a mod",
    ]

    lines = []
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue

        if any(phrase.lower() in stripped.lower() for phrase in ui_phrases):
            continue

        lines.append(stripped)

    text = "\n".join(lines)

    # Remove repeated whitespace but preserve paragraph breaks.
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def is_low_value_text(text: str) -> bool:
    """
    Filter comments that are empty, mostly Reddit/meta content,
    or not useful for housing-related retrieval.
    """
    stripped = text.strip()
    lowered = stripped.lower()

    if not stripped:
        return True

    banned_phrases = [
        "are you mentally ill",
        "you might be",
        "retarded",
        "your comments make 0 sense",
        "get your money up pal",
        "use of flair highly encouraged",
        "message the moderators",
        "apply to be a mod",
        "contact the mods",
        "a place to post anything about wsu",
        "[deleted]",
        "[removed]",
    ]

    if any(phrase in lowered for phrase in banned_phrases):
        return True

    housing_keywords = [
        "apartment",
        "apartments",
        "rent",
        "rental",
        "lease",
        "leasing",
        "housing",
        "studio",
        "bedroom",
        "roommate",
        "roommates",
        "ruckus",
        "aspen",
        "dabco",
        "churchill",
        "birch",
        "flats",
        "grove",
        "evolve",
        "reaney",
        "summerhills",
        "summerhill",
        "boulder",
        "maintenance",
        "management",
        "parking",
        "bus",
        "walk",
        "walkability",
        "campus",
        "landlord",
        "property",
        "utilities",
        "washer",
        "dryer",
        "dishwasher",
        "furnished",
        "unfurnished",
    ]

    # Very short comments are weak unless they mention housing/apartment terms.
    if len(stripped) < 40 and not any(word in lowered for word in housing_keywords):
        return True

    return False


def load_documents(raw_dir: Path) -> List[Dict]:
    """
    Load all .txt documents from documents/raw.
    Each document keeps source filename as metadata.
    """
    documents = []

    for path in sorted(raw_dir.glob("*.txt")):
        raw_text = path.read_text(encoding="utf-8")
        cleaned_text = clean_text(raw_text)

        if cleaned_text:
            documents.append(
                {
                    "source": path.name,
                    "path": str(path),
                    "text": cleaned_text,
                }
            )

    return documents


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split by blank lines first, since extracted Reddit comments
    are separated as entries.
    """
    paragraphs = [p.strip() for p in text.split("\n\n")]
    return [p for p in paragraphs if len(p.strip()) > 0]


def split_long_text(text: str, max_size: int) -> List[str]:
    """
    Split unusually long text into sentence-aware pieces.
    This avoids cutting in the middle of words when possible.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    pieces = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(current) + len(sentence) + 1 <= max_size:
            current = (current + " " + sentence).strip()
        else:
            if current:
                pieces.append(current)
            current = sentence

    if current:
        pieces.append(current)

    # Fallback: if a single sentence is longer than max_size, split by words.
    final_pieces = []
    for piece in pieces:
        if len(piece) <= max_size:
            final_pieces.append(piece)
            continue

        words = piece.split()
        current_words = []

        for word in words:
            candidate = " ".join(current_words + [word])
            if len(candidate) <= max_size:
                current_words.append(word)
            else:
                if current_words:
                    final_pieces.append(" ".join(current_words))
                current_words = [word]

        if current_words:
            final_pieces.append(" ".join(current_words))

    return final_pieces


def chunk_document(text: str, source: str) -> List[Dict]:
    """
    Create chunks around 600–900 characters when possible.
    Prefer paragraph/comment boundaries instead of cutting mechanically.
    """
    paragraphs = split_into_paragraphs(text)
    paragraphs = [p for p in paragraphs if not is_low_value_text(p)]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        # If one paragraph/comment is very long, split it safely.
        if len(paragraph) > CHUNK_SIZE:
            if current.strip():
                chunks.append(current.strip())
                current = ""

            for piece in split_long_text(paragraph, CHUNK_SIZE):
                if len(piece) >= MIN_CHUNK_LENGTH and not is_low_value_text(piece):
                    chunks.append(piece.strip())

            continue

        # Add paragraph to current chunk if it fits.
        if len(current) + len(paragraph) + 2 <= CHUNK_SIZE:
            current = (current + "\n\n" + paragraph).strip()
        else:
            if current.strip():
                chunks.append(current.strip())

            # Start cleanly with the new paragraph.
            # No character overlap, to avoid mid-word chunks.
            current = paragraph

    if current.strip():
        chunks.append(current.strip())

    chunk_records = []

    for i, chunk in enumerate(chunks):
        if len(chunk) >= MIN_CHUNK_LENGTH and not is_low_value_text(chunk):
            chunk_records.append(
                {
                    "id": f"{source}_chunk_{i}",
                    "source": source,
                    "chunk_index": i,
                    "text": chunk,
                    "char_count": len(chunk),
                }
            )

    return chunk_records


def build_chunks() -> List[Dict]:
    documents = load_documents(RAW_DIR)
    all_chunks = []

    print(f"Loaded {len(documents)} documents.")

    for doc in documents:
        doc_chunks = chunk_document(doc["text"], doc["source"])
        all_chunks.extend(doc_chunks)
        print(f"{doc['source']}: {len(doc_chunks)} chunks")

    return all_chunks


def save_chunks(chunks: List[Dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")


def inspect_chunks(chunks: List[Dict], n: int = 5) -> None:
    print("\n" + "=" * 80)
    print(f"Total chunks: {len(chunks)}")
    print("=" * 80)

    if not chunks:
        print("No chunks created. Check documents/raw/*.txt")
        return

    sample = random.sample(chunks, min(n, len(chunks)))

    for chunk in sample:
        print("\n" + "-" * 80)
        print(f"ID: {chunk['id']}")
        print(f"Source: {chunk['source']}")
        print(f"Chunk index: {chunk['chunk_index']}")
        print(f"Characters: {chunk['char_count']}")
        print("-" * 80)
        print(chunk["text"])


if __name__ == "__main__":
    chunks = build_chunks()
    save_chunks(chunks, OUTPUT_PATH)
    inspect_chunks(chunks, n=5)

    print(f"\nSaved chunks to {OUTPUT_PATH}")

    if len(chunks) < 50:
        print(
            "\nWarning: Fewer than 50 chunks created. "
            "You may need more raw text or smaller chunks."
        )

    if len(chunks) > 2000:
        print(
            "\nWarning: More than 2000 chunks created. "
            "Your chunks may be too small."
        )