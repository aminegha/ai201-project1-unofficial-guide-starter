import gradio as gr

from query import ask


def handle_query(question: str):
    """
    Gradio wrapper around the RAG ask() function.
    Returns answer, sources, and retrieved chunks for transparency.
    """
    result = ask(question)

    answer = result["answer"]

    sources = "\n".join(f"• {source}" for source in result["sources"])

    retrieved_text_blocks = []
    for item in result["retrieved_chunks"]:
        metadata = item["metadata"]

        block = (
            f"Rank: {item['rank']}\n"
            f"Distance: {item['distance']:.4f}\n"
            f"Source: {metadata['source']}\n"
            f"Chunk index: {metadata['chunk_index']}\n\n"
            f"{item['text']}"
        )

        retrieved_text_blocks.append(block)

    retrieved_chunks = "\n\n" + ("-" * 80 + "\n\n").join(retrieved_text_blocks)

    return answer, sources, retrieved_chunks


with gr.Blocks(title="WSU Off-Campus Housing Guide") as demo:
    gr.Markdown(
        """
        # WSU Off-Campus Housing Guide

        Ask questions about WSU off-campus housing experiences based on collected Reddit student discussions.

        The answer is generated only from retrieved source chunks. Sources and retrieved chunks are shown for transparency.
        """
    )

    question = gr.Textbox(
        label="Your question",
        placeholder="Example: Which apartments do students recommend near WSU?",
        lines=2,
    )

    ask_button = gr.Button("Ask")

    answer = gr.Textbox(
        label="Grounded Answer",
        lines=8,
    )

    sources = gr.Textbox(
        label="Retrieved Sources",
        lines=6,
    )

    retrieved_chunks = gr.Textbox(
        label="Retrieved Chunks",
        lines=15,
    )

    ask_button.click(
        handle_query,
        inputs=question,
        outputs=[answer, sources, retrieved_chunks],
    )

    question.submit(
        handle_query,
        inputs=question,
        outputs=[answer, sources, retrieved_chunks],
    )


if __name__ == "__main__":
    demo.launch()