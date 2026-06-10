
# The Unofficial Guide — Project 1

---

## Domain

This system covers **WSU off-campus housing experiences**. The goal is to make student-generated housing advice searchable, especially opinions about apartment recommendations, property managers, rent, maintenance, walkability, bus access, and places students warn against.

This knowledge is valuable because students often need practical information before signing leases, but official apartment websites usually only show amenities, prices, and leasing information. They do not clearly capture student experiences about management quality, maintenance issues, noise, move-out charges, parking, or whether an apartment is actually worth living in.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit: Best apartments for students off campus | Reddit thread | https://www.reddit.com/r/wsu/comments/158bkq2/best_apartments_for_students_off_campus/ |
| 2 | Reddit: Least terrible apartment complex | Reddit thread | https://www.reddit.com/r/wsu/comments/1q3zohy/least_terrible_apartment_complex/ |
| 3 | Reddit: Housing | Reddit thread | https://www.reddit.com/r/wsu/comments/1rg9jtm/housing/ |
| 4 | Reddit: Reputable one-bedroom apartments in Pullman | Reddit thread | https://www.reddit.com/r/wsu/comments/1jn66y7/anyone_know_reputable_one_bedroom_apartments_in/ |
| 5 | Reddit: Best one-bedroom apartments | Reddit thread | https://www.reddit.com/r/wsu/comments/1k3217j/best_one_bedroom_apartments/ |
| 6 | Reddit: Apartment recommendations | Reddit thread | https://www.reddit.com/r/wsu/comments/1e9t3zw/apartment_recommendations/ |
| 7 | Reddit: Living and rental cost around WSU | Reddit thread | https://www.reddit.com/r/wsu/comments/18stqkq/help_me_evalaute_living_and_rental_cost_aroud_wsu/ |
| 8 | Reddit: Is DABCO really that bad? | Reddit thread | https://www.reddit.com/r/wsu/comments/nftuii/is_dabco_really_that_bad_looking_at_churchill/ |
| 9 | Reddit: Moving off campus before entering housing contract | Reddit thread | https://www.reddit.com/r/wsu/comments/1m02cwg/moving_off_campus_before_entering_housing_contract/ |
| 10 | Reddit: Looking into apartments | Reddit thread | https://www.reddit.com/r/wsu/comments/1mupkh7/looking_into_apartments/ |
| 11 | Reddit: Housing questions | Reddit thread | https://www.reddit.com/r/wsu/comments/1ouycb7/housing_questions/ |

All final sources are Reddit student discussion threads. I originally considered including official WSU off-campus housing pages, but I removed them to keep the corpus focused on unofficial student experiences.

---

## Chunking Strategy

**Chunk size:**  
The final chunking strategy uses a maximum chunk size of about **900 characters**, with a preference for preserving complete Reddit entries or small groups of related entries.

**Overlap:**  
The final implementation uses **0 character overlap** for normal chunks. I originally planned to use 100–150 characters of overlap, but during testing I found that character overlap caused some chunks to start in the middle of words or sentences. Since Reddit comments are already separated into entries, preserving comment boundaries worked better than overlapping characters.

**Why these choices fit your documents:**  
The corpus is made of Reddit threads, which contain short posts and comments rather than long structured articles. A single student comment often contains a complete opinion about an apartment, property manager, rent, walkability, or maintenance issue. Grouping short related entries into chunks gives the retriever enough semantic context, while avoiding overly large chunks that mix too many unrelated opinions. I also cleaned the extracted text by removing Reddit sidebar boilerplate, deleted/removed comments, HTML artifacts, and some low-value/off-topic comments.

**Final chunk count:**  
The final pipeline produced **67 chunks** across **11 Reddit source documents**.

Example chunks:

1. **Source:** `reddit_best_apartments_off_campus.txt`, chunk 0  
   This chunk includes comments warning against the Ruckus and Aspen Heights, while also mentioning Summerhills/Boulder Creek and The Flats positively.

2. **Source:** `reddit_best_apartments_off_campus.txt`, chunk 1  
   This chunk includes comments mentioning Reaney Park apartments, Birch Hills, The Flats, and DABCO properties, as well as criteria like walkability, grocery access, price range, roommates, and bathroom setup.

3. **Source:** `reddit_dabco_churchill_downs.txt`, chunk 5  
   This chunk includes a mixed opinion about DABCO: one comment describes DABCO as predatory but says renters can protect themselves by knowing tenant rights and documenting carefully.

4. **Source:** `reddit_best_one_bedroom_apartments.txt`, chunk 0  
   This chunk includes one-bedroom apartment recommendations such as DABCO properties, Birch Hills, and apartments near Reaney Park.

5. **Source:** `reddit_apartment_recommendations.txt`, chunk 0  
   This chunk includes a student looking for an unfurnished studio or one-bedroom with washer/dryer, dishwasher, good internet, and rent under about $850, along with replies about realistic pricing and Pimlico.

---

## Embedding Model

**Model used:**  
I used `all-MiniLM-L6-v2` through the `sentence-transformers` library.

This model was a good fit because it runs locally, does not require paid embedding API calls, and is lightweight enough for a small class project. I stored the embeddings in ChromaDB and used cosine distance with normalized embeddings.

**Production tradeoff reflection:**  
For a production system, I would compare embedding models based on retrieval accuracy, latency, cost, and how well they handle informal student language. Reddit comments contain slang, short comments, apartment nicknames, and contradictory opinions, so a stronger embedding model might improve retrieval quality. I would also consider whether the system should support multilingual queries, whether embeddings should run locally for privacy, and whether hybrid search would help with exact apartment names like DABCO, Ruckus, Aspen Heights, Birch Hills, and Churchill Downs.

---

## Grounded Generation

**System prompt grounding instruction:**  
The generation step uses Groq’s `llama-3.3-70b-versatile` model. The LLM receives only the retrieved chunks as context and is instructed not to answer from outside knowledge.

The core grounding instruction is:

```text
You are a grounded question-answering assistant for a RAG system.

Rules:
1. Answer using ONLY the provided context.
2. Do NOT use outside knowledge.
3. Do NOT make up apartment names, prices, policies, or recommendations.
4. If the context does not contain enough information, say:
   "I don't have enough information in the provided documents to answer that."
5. Cite sources inline in plain text only, like: (source: reddit_example.txt, chunk 2). Do not create markdown links.
6. Be concise but specific.
```

**How source attribution is surfaced in the response:**
Source attribution is handled in two ways. First, the prompt asks the LLM to cite source filenames and chunk numbers inline when making claims. Second, the program also collects and displays the retrieved source filenames and chunk numbers separately under a “Sources” section. This means source attribution is still visible even if the LLM forgets to cite every claim perfectly.

---

## Example System Responses

### Example 1

**Question:** Which off-campus apartments near WSU do students recommend?

**System response:**  
Students recommend the following off-campus apartments near WSU: Summerhills/Boulder Creek (source: reddit_best_apartments_off_campus.txt, chunk 0), Reaney Park apartments (source: reddit_best_apartments_off_campus.txt, chunk 1), Birch Hills (source: reddit_best_apartments_off_campus.txt, chunk 1 and reddit_best_one_bedroom_apartments.txt, chunk 0), The Flats (source: reddit_best_apartments_off_campus.txt, chunk 0 and chunk 1), DABCO apartments (source: reddit_best_apartments_off_campus.txt, chunk 1 and reddit_best_one_bedroom_apartments.txt, chunk 0), and Nez Perce (source: reddit_housing_questions.txt, chunk 4).

### Example 2

**Question:** What do students say about DABCO or Churchill Downs?

**System response:**  
Students have mixed opinions about DABCO and Churchill Downs. Some comments describe DABCO as predatory and recommend taking precautions such as knowing tenant rights, keeping records, and taking pictures (source: reddit_dabco_churchill_downs.txt, chunk 5). Other comments say Churchill Downs is fine and nice enough for the price, but warn that move-out charges may be an issue (source: reddit_dabco_churchill_downs.txt, chunk 9).

---

### Out-of-Scope Query

**Question:** What is the best laptop for computer science students?

**System response:**  
I don't have enough information in the provided documents to answer that.

**Why this is correct:**  
The document collection only covers WSU off-campus housing experiences, not laptops or computer science equipment. The model correctly refused instead of using general knowledge.

---

## Query Interface

The project includes a Gradio web interface in `app.py`. The user enters a housing-related question in a text box and clicks **Ask**. The interface returns three outputs:

1. **Grounded Answer:** the LLM-generated answer based only on retrieved chunks.
2. **Retrieved Sources:** the source filenames and chunk numbers used for the answer.
3. **Retrieved Chunks:** the full retrieved chunks with rank, distance score, source, and chunk index.

To run the interface:

```bash
python app.py
```
Then open the local Gradio URL, usually:

```text
http://127.0.0.1:7860
```


### Sample Interaction Transcript

**User input:**  
Which off-campus apartments near WSU do students recommend?

**Grounded Answer:**  
Students recommend the following off-campus apartments near WSU: Summerhills/Boulder Creek (source: reddit_best_apartments_off_campus.txt, chunk 0), Reaney Park apartments (source: reddit_best_apartments_off_campus.txt, chunk 1), Birch Hills (source: reddit_best_apartments_off_campus.txt, chunk 1 and reddit_best_one_bedroom_apartments.txt, chunk 0), The Flats (source: reddit_best_apartments_off_campus.txt, chunk 0 and chunk 1), DABCO apartments (source: reddit_best_apartments_off_campus.txt, chunk 1 and reddit_best_one_bedroom_apartments.txt, chunk 0), and Nez Perce (source: reddit_housing_questions.txt, chunk 4).

**Retrieved Sources:**  
- reddit_best_apartments_off_campus.txt — chunk 0  
- reddit_best_apartments_off_campus.txt — chunk 1  
- reddit_best_one_bedroom_apartments.txt — chunk 1  
- reddit_housing_questions.txt — chunk 4  
- reddit_best_one_bedroom_apartments.txt — chunk 0


---

## Evaluation Report

| # | Question                                                                | Expected answer                                                                                                                                                                                                                                                                                         | System response (summarized)                                                                                                                                                                                                                                                                                                                                                                     | Retrieval quality  | Response accuracy  |
| - | ----------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------ | ------------------ |
| 1 | Which off-campus apartments near WSU do students recommend?             | The answer should identify apartments or housing options that students mention positively, such as Summerhills/Boulder Creek, Reaney Park, Birch Hills, The Flats, DABCO properties, and possibly Nez Perce or other options depending on retrieved chunks.                                             | The system listed Summerhills/Boulder Creek, Reaney Park, Birch Hills, The Flats, DABCO apartments, and Nez Perce, with source filenames and chunk numbers.                                                                                                                                                                                                                                      | Relevant           | Accurate           |
| 2 | Which apartments or property managers do students warn against?         | The answer should identify apartments or property managers students warn against, such as Aspen Heights, Pullman Highland PM, Coug Housing, Ruckus/Timberline, or other rental companies depending on retrieved chunks. It should also note when opinions are mixed.                                    | The system warned against Aspen Heights, Pullman Highland PM, and Coug Housing. It also correctly noted that one retrieved comment contradicted the warning about Coug Housing by describing a positive experience.                                                                                                                                                                              | Partially relevant | Partially accurate |
| 3 | What do students say about DABCO or Churchill Downs?                    | The answer should say that DABCO/Churchill Downs receives mixed opinions. Some comments warn that DABCO can be predatory or may charge after move-out, so students should document carefully and know tenant rights. Other comments say Churchill Downs is fine, livable, or nice enough for the price. | The system summarized mixed opinions about DABCO and Churchill Downs, including warnings about DABCO being predatory and positive comments that Churchill Downs is fine or nice enough for the price. However, it slightly over-attributed the phrase “worst thing on earth” as something students said directly, when that phrase came from the original poster summarizing what they had read. | Relevant           | Partially accurate |
| 4 | What factors matter most when choosing off-campus housing near WSU?     | The answer should mention factors such as price, walkability/proximity to campus, grocery access, roommates, private vs. shared bathroom, bus access, management reliability, and apartment condition.                                                                                                  | The system mentioned proximity/walkability to campus, grocery access, price range, roommates, private vs. shared bathroom, management reliability, and apartment condition.                                                                                                                                                                                                                      | Relevant           | Accurate           |
| 5 | What do students say about one-bedroom or studio apartments in Pullman? | The answer should summarize one-bedroom and studio apartment comments, including DABCO, Summer Hills, Muse on Main, Pimlico, rent expectations, washer/dryer availability, and caution about rental companies or private landlords.                                                                     | The system mentioned DABCO apartments, Summer Hills, Muse on Main, Pimlico, washer/dryer availability, price points, and private landlords or rental-company caution.                                                                                                                                                                                                                            | Relevant           | Accurate           |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

### Retrieval test results

#### Retrieval Test 1

**Query:** Which off-campus apartments near WSU do students recommend?

Top retrieved chunks included:

* `reddit_best_apartments_off_campus.txt`, chunk 0, distance 0.2138
* `reddit_best_apartments_off_campus.txt`, chunk 1, distance 0.2553
* `reddit_best_one_bedroom_apartments.txt`, chunk 1, distance 0.2793

These chunks were relevant because they directly mention apartments students recommend or discuss positively, including Summerhills/Boulder Creek, Reaney Park, Birch Hills, The Flats, DABCO properties, and 710 Oak Street.

#### Retrieval Test 2

**Query:** What do students say about DABCO or Churchill Downs?

Top retrieved chunks included:

* `reddit_dabco_churchill_downs.txt`, chunk 2, distance 0.4196
* `reddit_dabco_churchill_downs.txt`, chunk 1, distance 0.4202
* `reddit_housing.txt`, chunk 4, distance 0.5924
* `reddit_dabco_churchill_downs.txt`, chunk 9, distance 0.6140
* `reddit_dabco_churchill_downs.txt`, chunk 5, distance 0.6165

These chunks were relevant because they came from the DABCO/Churchill Downs thread and included comments about DABCO’s reputation, tenant precautions, move-out charges, payment plans, and whether Churchill Downs is livable.

#### Retrieval Test 3

**Query:** What factors matter most when choosing off-campus housing near WSU?

Top retrieved chunks included:

* `reddit_housing_questions.txt`, chunk 0, distance 0.2994
* `reddit_best_apartments_off_campus.txt`, chunk 1, distance 0.3154
* `reddit_best_one_bedroom_apartments.txt`, chunk 1, distance 0.3440

These chunks were relevant because they mention price, rent limits, walkability, campus access, bus routes, parking, roommates, bathroom setup, and apartment condition.

---

## Failure Case Analysis

**Question that failed:**
What do students say about DABCO or Churchill Downs?

**What the system returned:**
The system returned a mostly correct answer saying that students have mixed opinions about DABCO and Churchill Downs. It said some comments describe DABCO as predatory while others say Churchill Downs is fine or nice enough for the price. However, it also said that “students say DABCO is the worst thing on earth,” which is not fully precise.

**Root cause (tied to a specific pipeline stage):**
This was a generation-level grounding issue. The relevant chunk was retrieved, but the LLM did not distinguish clearly between the original poster’s framing and the commenters’ actual experiences. In the retrieved context, the original poster wrote that they had read online that DABCO was “the worst thing on earth” and that people said to avoid them. The model summarized that as if students in the retrieved comments directly made that claim. The problem was not that retrieval failed; the problem was that generation compressed the post and comments together without preserving who said what.

**What you would change to fix it:**
I would improve the prompt to tell the model to distinguish between the original post and replies. I would also adjust the chunk formatting so that the original post and comments are labeled more clearly, such as “Original Poster” versus “Comment.” Another possible improvement is to use smaller comment-level chunks for threads where the difference between the question and the replies matters.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The planning document helped guide the implementation by forcing me to decide the domain, sources, chunking approach, retrieval model, and evaluation questions before writing code. This made the pipeline easier to build because I already knew that my documents were mostly short Reddit comments and that I needed comment-aware chunks rather than arbitrary fixed-size text splits. It also made evaluation easier because I had specific questions to test against.

**One way your implementation diverged from the spec, and why:**
The original plan included official WSU off-campus housing pages as background context, and it also planned to use 100–150 characters of overlap between chunks. During implementation, I removed the official WSU sources so the final corpus would focus entirely on unofficial student discussion, which better matched the project goal. I also removed overlap because the first chunking attempt caused some chunks to start in the middle of words, making them less readable and less useful for retrieval.

---

## AI Usage

**Instance 1**

* *What I gave the AI:*
  I gave the AI my Milestone 1 sources, my planning.md chunking strategy, and the project instructions for Milestone 3.

* *What it produced:*
  The AI helped generate an initial ingestion and chunking script that loaded `.txt` files from `documents/raw`, cleaned the text, split documents into chunks, saved them to `data/chunks.json`, and printed sample chunks for inspection.

* *What I changed or overrode:*
  I changed the chunking behavior after inspecting the output. The first version used character overlap, but some chunks started in the middle of words. I removed normal chunk overlap and added filtering for Reddit boilerplate and low-value comments.

**Instance 2**

* *What I gave the AI:*
  I gave the AI my Retrieval Approach section from planning.md and asked for code that embedded chunks using `all-MiniLM-L6-v2`, stored them in ChromaDB, and retrieved top-k chunks with source metadata.

* *What it produced:*
  The AI helped generate `retrieve.py`, which loads `data/chunks.json`, embeds chunks, creates a ChromaDB collection, and prints retrieval results with distance scores, source filenames, and chunk indexes.

* *What I changed or overrode:*
  I changed the ChromaDB setup to use cosine distance and normalized embeddings after seeing high distance scores in the first retrieval test. This made the distance scores more interpretable and improved the retrieval results.

**Instance 3**

* *What I gave the AI:*
  I gave the AI the Milestone 5 requirements and asked for a grounded generation pipeline using Groq and a simple Gradio interface.

* *What it produced:*
  The AI helped generate `query.py` for retrieval-augmented generation and `app.py` for the Gradio interface.

* *What I changed or overrode:*
  I adjusted the grounding prompt to make the model answer only from retrieved chunks and refuse out-of-scope questions. I also ensured that source filenames and chunk numbers are shown programmatically in addition to any citations generated by the model.
