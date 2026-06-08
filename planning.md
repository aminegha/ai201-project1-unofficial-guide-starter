# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

I chose the domain of WSU off-campus housing experiences. This knowledge is valuable because students often need practical information about apartments before signing leases, such as management quality, maintenance problems, noise, rent, walkability, parking, and bus access. Official apartment websites and university pages provide listings and general renter guidance, but they do not capture the unofficial student perspective about which apartments or property managers students recommend or warn against.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Reddit: Best apartments for students off campus | Reddit thread where WSU students discuss the best off-campus apartments and mention factors such as walkability, price, roommates, and apartments to avoid. | https://www.reddit.com/r/wsu/comments/158bkq2/best_apartments_for_students_off_campus/ | 
| 2 | Reddit: Least terrible apartment complex | Reddit thread about apartment complexes in Pullman, including student complaints and comparisons. | https://www.reddit.com/r/wsu/comments/1q3zohy/least_terrible_apartment_complex/ | 
| 3 | Reddit: Housing | Reddit housing thread where students discuss Pullman apartments and housing options. | https://www.reddit.com/r/wsu/comments/1rg9jtm/housing/ | 
| 4 | Reddit: Reputable one-bedroom apartments | Reddit thread from a student asking about reputable one-bedroom apartments in Pullman. | https://www.reddit.com/r/wsu/comments/1jn66y7/anyone_know_reputable_one_bedroom_apartments_in/ | 
| 5 | Reddit: Best one-bedroom apartments | Reddit thread about one-bedroom apartment recommendations, including location, management, and bus access. | https://www.reddit.com/r/wsu/comments/1k3217j/best_one_bedroom_apartments/ | 
| 6 | Reddit: Apartment recommendations | Reddit thread asking for apartment recommendations with specific requirements such as studio or one-bedroom, washer/dryer, dishwasher, internet, and budget. | https://www.reddit.com/r/wsu/comments/1e9t3zw/apartment_recommendations/ | 
| 7 | Reddit: Living and rental cost around WSU | Reddit thread discussing living costs and rental costs around WSU/Pullman. | https://www.reddit.com/r/wsu/comments/18stqkq/help_me_evalaute_living_and_rental_cost_aroud_wsu/ | 
| 8 | WSU Off-Campus Living Marketplace | Official WSU off-campus living marketplace. Included for background context about WSU-supported off-campus housing resources. | https://offcampusliving.wsu.edu/ | 
| 9 | WSU Off-Campus Living Guide | Official WSU Off-Campus Living Guide with renter information, lease guidance, rights, and responsibilities. Included as background context, not student opinion. | https://offcampusliving.wsu.edu/assets/campus_assets/wsu/2020-2021-Off-Campus-Living-Guide.pdf | 
| 10 | Reddit: Is DABCO really that bad? | Reddit thread discussing DABCO/Churchill Downs apartments, including student opinions about whether the property management or apartment experience is actually bad. | https://www.reddit.com/r/wsu/comments/nftuii/is_dabco_really_that_bad_looking_at_churchill/ | 
| 11 | Reddit: Moving off campus before housing contract | Reddit thread about moving off campus before entering a housing contract, useful for understanding student concerns about lease timing, housing commitments, and switching from on-campus to off-campus housing. | https://www.reddit.com/r/wsu/comments/1m02cwg/moving_off_campus_before_entering_housing_contract/ | 
| 12 | Reddit: Looking into apartments | Reddit thread where a student asks about looking into apartments near WSU, useful for apartment recommendations, housing concerns, and decision factors. | https://www.reddit.com/r/wsu/comments/1mupkh7/looking_into_apartments/ | 
| 13 | Reddit: Housing questions | Reddit thread with housing-related questions from WSU students, useful for common concerns about off-campus living, apartment choices, and student advice. | https://www.reddit.com/r/wsu/comments/1ouycb7/housing_questions/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:** 

Approximately 600–900 characters per chunk, with a preference for preserving complete Reddit comments or small groups of related comments. 

**Overlap:** 

Approximately 100–150 characters of overlap when a longer document or long Reddit thread section must be split. 

**Reasoning:** 

Most of the unofficial sources are Reddit threads made of short comments rather than long articles. A chunk should usually preserve one full student comment because one comment often contains a complete opinion about an apartment, property manager, rent, bus access, or maintenance issue. If comments are very short, I may group a few related comments together so that each chunk has enough context for semantic search. The overlap helps when a relevant detail is split across two nearby comments or when a recommendation depends on the previous comment.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** 

I will use `all-MiniLM-L6-v2` through the `sentence-transformers` library. This model is recommended for the project, runs locally, and avoids paid API costs for embeddings. 

**Top-k:** 

I will start with `top-k = 5`, meaning the retriever will return the 5 most relevant chunks for each query. 

**Production tradeoff reflection:** 

For a production system, I would compare embedding models based on retrieval accuracy, cost, latency, context length, and how well they handle informal student language. A larger or more accurate embedding model might retrieve better results from noisy Reddit comments, but it could also be slower or more expensive. I would also consider whether the system needs multilingual support, whether embeddings should run locally for privacy, and whether hybrid search would help when users search for specific apartment names like DABCO, Churchill Downs, or The Grove. 
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which off-campus apartments or property managers do students recommend near WSU? | The answer should identify apartments or managers that students describe positively in the Reddit sources and cite the relevant threads. It should not invent recommendations that are not present in the retrieved documents. | 
| 2 | What do students say about DABCO or Churchill Downs? | The answer should summarize student opinions from the DABCO/Churchill Downs thread, including whether students describe the experience as bad, acceptable, or dependent on specific issues. | 
| 3 | What factors do students mention when choosing off-campus housing near WSU? | The answer should mention factors such as rent, location, walkability, bus access, parking, roommates, maintenance, management quality, and apartment amenities if they appear in the sources. | 
| 4 | What do students say about one-bedroom or studio apartments in Pullman? | The answer should summarize recommendations or concerns from the one-bedroom/studio-related Reddit threads and cite those sources. | 
| 5 | What official guidance does WSU provide for students living off campus? | The answer should use the WSU Off-Campus Living Marketplace and Off-Campus Living Guide to mention official resources, renter guidance, lease information, and housing listings. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Reddit comments may be noisy, informal, inconsistent, or contradictory. Different students may have different experiences with the same apartment or property manager, so the system needs to summarize opinions carefully instead of presenting one comment as universal truth. 

2. Retrieval may fail if chunks are too small or if apartment names appear in only a few comments. For example, if a chunk only contains a short phrase like “avoid that place,” it may not include enough context for the retriever to connect it to a specific apartment. 

3. Source attribution could be difficult if multiple Reddit comments from the same thread are grouped together. I need to preserve metadata such as source URL and chunk number so that every generated answer can cite where the information came from. 

4. Some official WSU pages provide general housing information but not student opinions. The system should distinguish between official background context and unofficial student experiences.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```text 
Raw Sources
(Reddit threads, WSU Off-Campus Living pages, WSU PDF guide) 
     | 
     v 
Document Ingestion 
(Python scripts, requests/manual text files, pdfplumber for PDF if needed) 
     | 
     v 
Cleaning + Preprocessing 
(Remove navigation text, repeated headers, irrelevant boilerplate) 
     | 
     v 
Chunking 
(Comment-aware / paragraph-aware chunks, approx. 600–900 characters, 100–150 overlap) 
     | 
     v 
Embedding + Vector Store 
(sentence-transformers: all-MiniLM-L6-v2 + ChromaDB) 
     | 
     v 
Retrieval 
(Semantic similarity search, top-k = 5, return text + source metadata) 
     | 
     v 
Grounded Generation 
(Groq llama-3.3-70b-versatile, answer only from retrieved chunks) 
     | 
     v 
User Interface 
(Simple CLI or Gradio interface showing answer + cited sources)
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I plan to use ChatGPT or GitHub Copilot to help implement the ingestion and chunking scripts. I will give the AI my Documents section, Chunking Strategy section, and Architecture diagram. I expect it to produce Python code that loads the source documents, cleans the text, preserves source metadata, and splits the documents into chunks of approximately 600–900 characters with 100–150 characters of overlap. I will verify the output by printing at least 5 random chunks and checking that they are readable, self-contained, and still connected to the correct source URL.

**Milestone 4 — Embedding and retrieval:**
I plan to use ChatGPT or GitHub Copilot to help implement the embedding and retrieval code. I will give the AI my Retrieval Approach section and ask it to use sentence-transformers with all-MiniLM-L6-v2 and ChromaDB. I expect it to produce code that embeds all chunks, stores them with metadata, and retrieves the top 5 chunks for a query. I will verify the output by testing at least 3 evaluation questions and checking whether the returned chunks are actually relevant.

**Milestone 5 — Generation and interface:**
I plan to use ChatGPT or GitHub Copilot to help implement the grounded generation and user interface. I will provide the grounding requirement that the LLM must answer only from retrieved chunks and must cite sources. I expect it to produce a function that combines retrieval with Groq’s llama-3.3-70b-versatile model and returns an answer plus source list. I will verify the output by asking both in-scope and out-of-scope questions. For out-of-scope questions, the system should say it does not have enough information instead of hallucinating.
