---
name: rag-design
description: Design a retrieval-augmented generation pipeline — chunking, embeddings, retriever, reranker, prompt assembly — with the right cuts for the use case.
---

# rag-design

> Design a RAG pipeline. Output is the architecture plus the cuts you'd make first if quality is low.

**Mode:** analytical — judgment inside a fixed frame. Keep the output shape; every verdict cites its evidence; unknowns are marked `[TBD]` or `[VERIFY]`, never filled in.

## When to use

- A new feature needs LLM answers grounded in a corpus.
- An existing RAG pipeline gives wrong or hallucinated answers and you want to know where to look.

Not this when: the whole corpus fits comfortably in the model's context window — then put it in the prompt with prompt caching and skip retrieval (fewer moving parts, no recall misses). For the eval harness, `polymath-ai:eval-plan`; for injection defenses, `polymath-ai:llm-guardrails`.

## Inputs

- The user question shape (closed-domain Q&A, open-ended summarization, etc.).
- The corpus: size, update rate, content type (docs, code, transcripts, mixed).
- Quality bar (precision-first vs recall-first).

## Procedure

0. **Access control first.** If documents have different readers, filter by the requesting user's permissions *inside* retrieval (metadata filter on ACLs/tenant) — never retrieve broadly and trust the prompt to withhold. A RAG system without this leaks documents to anyone who can ask.
1. **Decide the granularity of retrieval**.
   - **Whole document** — small corpora; the model is fine with long context.
   - **Section / chunk** — most corpora. 200–800 tokens per chunk. Overlap 10–20% so cross-chunk references survive. Prepend a one-line context (document title / section path) to each chunk before embedding so chunks stay meaningful out of context.
   - **Hierarchical** — sentence-level retrieval that returns the surrounding paragraph for context.
2. **Choose the index**:
   - **Dense (embeddings)** — pgvector / qdrant / pinecone. Great for paraphrase recall.
   - **Sparse (BM25)** — strong baseline; trivially explainable.
   - **Hybrid** — almost always wins.
3. **Embeddings**:
   - One embedding model + version per index; mixing wrecks recall.
   - Re-embed on chunking strategy change. Not optional.
   - Freshness: re-index changed documents and **delete** removed ones (tombstones) on a schedule that matches the corpus update rate — stale or deleted content resurfacing is a correctness and compliance bug.
4. **Reranker**:
   - For top-k 5–10, a cross-encoder reranker improves precision substantially.
   - Skip if the retriever already returns < 5 highly relevant chunks.
5. **Prompt assembly**:
   - Put the retrieved context first and the question last (vendor long-context guidance: queries at the end of long prompts answer better), each chunk delimited (`<source id="3">…</source>`) so the model can cite. Repeat a one-line version of the question before the context if instructions depend on it.
   - Tell the model to cite sources and to refuse if no source answers the question.
   - Retrieved text is untrusted: a document can contain instructions aimed at the model. Keep it in delimited data positions and never let it grant tools or permissions (`polymath-ai:llm-guardrails`).
6. **Failure-mode plan** — when quality is low, in this order:
   - Wrong chunks retrieved → debug retrieval before prompt.
   - Right chunks, wrong synthesis → adjust prompt; consider reranker.
   - Right chunks, hallucinated facts → add explicit "answer only from sources" + abstention path; consider citation requirement.
7. **Evaluation hook** — evaluate retrieval separately from generation (recall@k / MRR on question→relevant-chunk labels) so you know which half is failing; pair with `polymath-ai:eval-plan` for end-to-end quality. Don't deploy without a held-out set.

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
  Access:  retrieval filtered by the caller's ACL groups (metadata filter).
  Prompt:  <source id="N">…</source> blocks first, question last.
           Model instructed to cite [source N] and abstain if unanswered.
  Freshness: nightly re-index of changed docs; deletes propagate within 24h.

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
- Retrieving across all tenants/permissions and asking the prompt to keep secrets.
