---
name: rag-design
description: Design a retrieval-augmented generation pipeline — chunking, embeddings, retriever, reranker, prompt assembly — with the right cuts for the use case.
---

# rag-design

> Design a RAG pipeline. Output is the architecture plus the cuts you'd make first if quality is low.

## When to use

- A new feature needs LLM answers grounded in a corpus.
- An existing RAG pipeline gives wrong or hallucinated answers and you want to know where to look.

## Inputs

- The user question shape (closed-domain Q&A, open-ended summarization, etc.).
- The corpus: size, update rate, content type (docs, code, transcripts, mixed).
- Quality bar (precision-first vs recall-first).

## Procedure

1. **Decide the granularity of retrieval**.
   - **Whole document** — small corpora; the model is fine with long context.
   - **Section / chunk** — most corpora. 200–800 tokens per chunk. Overlap 10–20% so cross-chunk references survive.
   - **Hierarchical** — sentence-level retrieval that returns the surrounding paragraph for context.
2. **Choose the index**:
   - **Dense (embeddings)** — pgvector / qdrant / pinecone. Great for paraphrase recall.
   - **Sparse (BM25)** — strong baseline; trivially explainable.
   - **Hybrid** — almost always wins.
3. **Embeddings**:
   - Pick one provider for stability; mixing wrecks recall.
   - Re-embed on chunking strategy change. Not optional.
4. **Reranker**:
   - For top-k 5–10, a cross-encoder reranker improves precision substantially.
   - Skip if the retriever already returns < 5 highly relevant chunks.
5. **Prompt assembly**:
   - Put the question first, then the retrieved context, with each chunk delimited (`<source id="3">…</source>`) so the model can cite.
   - Tell the model to cite sources and to refuse if no source answers the question.
6. **Failure-mode plan** — when quality is low, in this order:
   - Wrong chunks retrieved → debug retrieval before prompt.
   - Right chunks, wrong synthesis → adjust prompt; consider reranker.
   - Right chunks, hallucinated facts → add explicit "answer only from sources" + abstention path; consider citation requirement.
7. **Evaluation hook** — pair with `polymath-ai:eval-plan`. Don't deploy without a held-out set.

## Output

```text
RAG design: <use case>

Corpus shape: <e.g. 30k internal docs, mostly Markdown, monthly updates>

Pipeline:
  Chunking: 600-token chunks, 120-token overlap. Split on Markdown headings.
  Embedding: <provider> (one model, version pinned).
  Index: pgvector + BM25 hybrid.
  Retrieval: top 20 candidates per source.
  Rerank: cross-encoder reranker, keep top 6.
  Prompt: question first, then <source id="N">…</source> blocks.
            Model instructed to cite [source N] and abstain if unanswered.

First-quality-cut order (if eval is low):
  1. Inspect 20 wrong-answer cases: did retrieval surface a relevant chunk?
  2. If no — investigate chunking + embeddings.
  3. If yes — investigate prompt + reranker.
```

## Anti-patterns to avoid

- Choosing a vector DB before knowing the corpus size.
- Dense-only retrieval without measuring against BM25.
- Mixing embedding model versions across a corpus.
- Skipping evaluation and shipping vibes.
