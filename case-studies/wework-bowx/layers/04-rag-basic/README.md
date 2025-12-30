# Layer 4: Basic RAG

## Purpose

Test whether retrieval-augmented generation helps when documents exceed context window.

## Setup

- Best parser from Layer 3
- Chunk documents into segments
- Embed chunks with text-embedding model
- Retrieve relevant chunks via similarity search
- Generate answer from top-k chunks

## Variables

| Variable | Options to Test |
|----------|-----------------|
| Chunk size | 256, 512, 1024, 2048 tokens |
| Overlap | 0%, 10%, 25%, 50% |
| Top-k | 3, 5, 10, 20 chunks |
| Embedding model | text-embedding-3-large, others |

## Process

1. Parse documents (use best from Layer 3)
2. Chunk with each configuration
3. Embed all chunks
4. For each question:
   - Embed question
   - Retrieve top-k similar chunks
   - Generate answer with chunks in context
5. Score against ground truth

## Key Metrics

- Retrieval precision: Did it get the right chunks?
- Answer accuracy vs. Layer 2
- Which questions require retrieval vs. fit in context?

## Directory Structure

```
04-rag-basic/
├── README.md
├── run.py
├── chunks/
│   ├── 512-tokens/
│   └── 1024-tokens/
└── runs/
    ├── chunk512-top5/
    │   ├── config.yaml
    │   ├── retrieved-chunks.jsonl
    │   ├── responses.jsonl
    │   └── eval.json
    └── ...
```

## Status

- [ ] Chunking implemented
- [ ] Embedding pipeline ready
- [ ] Retrieval tested
- [ ] Runs complete
- [ ] Optimal config identified
