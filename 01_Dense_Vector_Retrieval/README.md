<p align = "center" draggable="false" ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 1: Dense Vector Retrieval</h1>

### [Quicklinks]()

| 📰 Module Sheet                                                                 | ⏺️ Recording | 🖼️ Slides | 👨‍💻 Repo       | 📝 Homework | 📁 Feedback |
| :------------------------------------------------------------------------------- | :----------- | :-------- | :------------ | :---------- | :---------- |
| [Dense Vector Retrieval](../00_Docs/Modules/01_Dense_Vector_Retrieval/README.md) |[Recording!](https://us02web.zoom.us/rec/share/sHWvo0Nd1aI0SEhKecOLEX9kFGVJJAdYfsKiuTmm8t85W48Z2lnjpnzTy8jAd8R5.PwuqibGwAZhvDd8c) <br> passcode: `C62n^@Q!`| [Session 1 Slides](https://canva.link/htfqf8i39yejyhn) | You are here! | [Session 1 Assignment](https://forms.gle/Z9qskfVaAvPjn6gz8) | [Feedback 6/2](https://forms.gle/21a2uoL9DVZPwgJP6) |


## 🏗️ How AIM Does Assignments

> 📅 **Assignments will always be released to students as live class begins.** We will never release assignments early.

Each assignment will have a few of the following categories of exercises:

- ❓ **Questions** - these will be questions that you will be expected to gather the answer to. These can appear as general questions, or questions meant to spark a discussion in your breakout rooms.

- 🏗️ **Activities** - these will be work or coding activities meant to reinforce specific concepts or theory components.

- 🚧 **Advanced Builds (optional)** - Take on a challenge. These builds require you to create something with minimal guidance outside of the documentation.

## Main Assignment

In this assignment, you will build a vector RAG application using LangChain v1, OpenAI embeddings, and Qdrant.

The main notebook is:

```text
01_Cat_Health_Vector_RAG_LangChain_Qdrant.ipynb
```

The notebook uses the bundled cat health guideline PDF in `data/cat_health_guidelines.pdf`.

### Setup

From this folder, install the environment with uv:

```bash
uv sync
```

Then open the notebook in Cursor or VS Code and select the Python/Jupyter environment created by uv.

You will also need an OpenAI API key available when running the notebook.

---

## 🏗️ Activity #1: Embedding Similarity

Run the embedding similarity primer in the notebook.

You will compare embeddings for terms like:

- `king`
- `queen`
- `banana`
- `cat`
- `veterinarian`
- `cat health guidelines`

#### ❓Question #1

Why is cosine similarity useful for dense vector retrieval?

##### ✅ Answer:

Embedding vectors vary in magnitude but direction captures meaning. 
Cosine similarity ignores magnitude and only measures the angle between 
vectors, so it reliably compares semantic similarity regardless of 
vector length. Two vectors pointing in the same direction means similar 
meaning, regardless of how large the numbers are.

## 🏗️ Activity #2: Build the Vector RAG Pipeline

Run the notebook sections that:

1. Load the PDF into LangChain `Document` objects
2. Split the document into chunks
3. Embed the chunks
4. Store the chunk embeddings in in-memory Qdrant
5. Retrieve relevant chunks with similarity scores
6. Generate an answer grounded in retrieved context

#### ❓Question #2

Why is metadata important for a RAG application?

##### ✅ Answer:
Metadata lets us trace where retrieved content came from (page number, source document), enables source filtering before retrieval, and helpfull for debugging poor retrieval results.

#### ❓Question #3

What tradeoff do we make when choosing chunk size and chunk overlap?

##### ✅ Answer: 
Larger chunks give more context per retrieval but reduce precision as irrelevant content gets included. Smaller chunks are more precise but may cut off important context. Overlap reduces the risk of splitting a key sentence across chunk boundaries, but increases storage and computation.As this document and app is related to medical where context determines accuracy so after expriment I am going with 1500 / 300 .

#### ❓Question #4

What does a similarity score help you understand, and what does it not prove by itself?

##### ✅ Answer:

It tells us how semantically similar a chunk is to the query. It doesn't prove the chunk actually answers the question, a highly similar chunk might be thematically related but not contain the specific answer.

## 🏗️ Activity #3: Vibe Check Retrieval Quality

Run the notebook's vibe check queries and inspect both:

- The retrieved context
- The generated answer

#### ❓Question #5

For the vibe check queries, did the retrieved context seem relevant before generation? Why or why not?

##### ✅ Answer:
For the first three questions — preventive care, symptoms, and feeding, the retrieved chunks were clearly relevant. They contained actual 
medical advice from the PDF that directly addressed each question, with 
scores consistently above 0.7.

For the last question about filing taxes, no relevant chunks came back 
and the assistant correctly said: "I don’t have enough information in the provided cat health guideline PDF to answer that."
---

## 🏗️ Activity #4: Tune Retrieval

Improve retrieval quality by changing one or more of:

- Chunk size
- Chunk overlap
- Retrieval `k`
- Query wording

Document what changed and whether retrieval improved.

##### Settings Changed:

- Chunk size: tested 1000, 1200, and 1500 characters
- Chunk overlap: tested 200, 250, and 300 characters
- Retrieval k: tested 2, 4, and 6 for each chunk setting
- Query used: "What should be included in a wellness exam for cats?"

##### Results:

1. Before (1000/200): Top scores at k=4 were 0.649, 0.640, 0.627, 
   0.619. Chunks retrieved scattered topics — cat exposure to other 
   cats, cost of care discussions, and pet insurance appeared 
   alongside clinical content. At k=6, Source 5 added vomiting and 
   hairball questions (score 0.618) and Source 6 added kitten 
   behavior questions (score 0.607) but scores dropped off quickly 
   and the added chunks were less relevant.

2. Middle (1200/250): Top scores at k=4 were 0.648, 0.642, 0.639, 
   0.631. Consistent improvement across sources 2, 3 and 4 compared 
   to 1000/200. Retrieved more clinically focused content — handling 
   preferences, disease detection for adult and senior cats, and 
   subtle signs of anxiety and illness. At k=6, scores stayed strong 
   at 0.629 and 0.627 for sources 5 and 6, meaning extra chunks 
   were still relevant rather than dropping off.

3. After (1500/300): Top scores at k=4 were 0.648, 0.641, 0.633, 
   0.626. Related clinical topics stayed together in the same chunk 
   — exercise tolerance and vomiting questions appeared in Source 1 
   together, and Source 2 captured the full lifestyle classification 
   for preventive care recommendations as a complete thought. At k=6, 
   sources 5 and 6 scored 0.620 and 0.617 and retrieved the human-cat 
   bond context and consultation agenda setting — both relevant to a 
   wellness exam. The strongest and most consistent results across 
   all k values came from this setting.

##### Did retrieval improve? 

Yes, with nuance. Similarity scores were close across all three chunk 
settings — the maximum difference was less than 0.02. The real 
improvement was in two areas.

First, content coherence. The 1000/200 setting retrieved scattered 
topics including cost of care and insurance discussions at k=4. The 
1500/300 setting kept clinically related content together — exercise 
tolerance and vomiting questions in the same chunk, and a complete 
lifestyle classification in Source 2.

Second, k stability. At k=6, the 1000/200 setting dropped to scores 
of 0.618 and 0.607 with less relevant content. The 1500/300 setting 
held scores of 0.620 and 0.617 with chunks still relevant to a 
wellness exam. This means larger chunks with more overlap produced 
more consistently useful results as k increased.

For this medical document, 1500/300 with k=4 gave the best balance — 
complete clinical context per chunk without adding noise from 
lower scoring sources.

---

## Optional Deep Dive: RAG From Scratch

If you want to look underneath the library abstractions, run the optional reference notebook:

```text
02_Cat_Health_Vector_RAG_From_Scratch.ipynb
```

It builds the same retrieval pipeline again with only:

- `pypdf` for extracting text from the PDF
- Python standard-library HTTP requests for calling OpenAI
- Handcrafted document, chunking, embedding, similarity-search, vector-store, and generation primitives

This notebook is a reference walkthrough, not an additional assignment. Its purpose is to make the responsibilities hidden by LangChain, Qdrant, and provider SDKs visible.

---

## Submitting Your Homework

### Main Assignment

Follow these steps to prepare and submit your homework:

1. Pull the latest updates from upstream into the main branch of your AIE9 repo:

```bash
git checkout main
git pull upstream main
git push origin main
```

2. Start Cursor from the `01_Dense_Vector_Retrieval` folder.
3. Complete the notebook.
4. Answer the questions in this `README.md`.
5. Add, commit, and push your modified work to your origin repository.

When submitting your homework, provide the GitHub URL to your AIE9 repo.
