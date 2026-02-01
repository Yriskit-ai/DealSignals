# Layer 3.5: Native Multimodal Document Processing

## Overview

Layer 3.5 tests native multimodal document processing capabilities, bypassing text extraction entirely. Each provider handles PDF parsing internally using their native document APIs.

## Why Layer 3.5?

Layer 3 (OCR parsing) failed because OCR output (4.4MB for S-4) exceeded LLM context limits. Layer 3.5 addresses this by using providers' native document handling:

| Provider | Method | Capacity |
|----------|--------|----------|
| **Claude** | Native PDF via vision | ~100 pages |
| **OpenAI** | Assistants + file_search | Unlimited (RAG) |
| **Gemini** | 1M token context | ~800K tokens |

## Prerequisites

### API Keys

Set these environment variables:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
export GOOGLE_API_KEY=...
```

### Documents

Ensure PDFs exist in `.data/`:
- `.data/S-4_A.pdf` (37MB, 1,193 pages)
- `.data/WeWork-Management-Presentation-March-2021-vF-1.pdf` (6.7MB)

## Running Experiments

### Single Provider + Document
```bash
# Claude on investor presentation (smaller, good for testing)
python scripts/run_layer_35.py --provider claude --document investor

# OpenAI on S-4 (uses RAG, can handle full document)
python scripts/run_layer_35.py --provider openai --document s4

# Gemini on S-4 (large context window)
python scripts/run_layer_35.py --provider gemini --document s4
```

### All Combinations
```bash
# Run all providers on all documents (6 runs total)
python scripts/run_layer_35.py --provider all --document all
```

### Dry Run
```bash
python scripts/run_layer_35.py --provider all --document all --dry-run
```

## Output Structure

```
results/wework-bowx/layers/03.5-multimodal/
├── claude/
│   └── 20260124_123456/
│       ├── investor_q01.json
│       ├── investor_q01.md
│       ├── ...
│       └── summary.json
├── openai/
│   └── 20260124_123500/
│       └── ...
└── gemini/
    └── 20260124_123530/
        └── ...
```

## Provider Notes

### Claude Direct
- Uses native PDF document blocks (vision-based)
- Limited to ~100 pages per request
- Best for investor presentation
- May struggle with full S-4 (1,193 pages)

### OpenAI Assistants
- Creates vector store and assistant per document
- Automatic chunking and retrieval
- Can handle documents of any size
- Cleanup happens automatically after run

### Gemini Direct
- Uploads file to Gemini API
- 1M+ token context window
- Can potentially fit entire S-4 as text
- File deleted after processing

## Cost Estimates

| Provider | Model | Input $/1M | Output $/1M |
|----------|-------|------------|-------------|
| Claude | claude-sonnet-4 | $3.00 | $15.00 |
| OpenAI | gpt-4o | $2.50 | $10.00 |
| Gemini | gemini-2.0-flash | $0.10 | $0.40 |

For 40 questions per document:
- Investor presentation: ~$0.50-2.00 per provider
- S-4: ~$5-20 per provider (varies by context usage)

## Comparison to Layer 2

Layer 2 used pre-extracted text passed to ZenMux API. Layer 3.5 uses:
- Original PDF documents (no extraction)
- Direct provider APIs (no ZenMux)
- Native document handling (vision, RAG, or large context)

This tests whether native multimodal capabilities can match or exceed text extraction quality.

## Experiment Results (2026-01-29)

### Summary

| Provider | Document | Success | Cost | Tokens | Avg Latency |
|----------|----------|---------|------|--------|-------------|
| **Claude** | Investor Pres (7MB) | 40/40 | $9.84 | 3,226,632 | ~14s |
| **OpenAI** | Investor Pres (7MB) | 40/40 | $0.40 | 151,177 | ~8s |
| **Claude** | S-4 (38MB) | 0/40 | - | - | 413 error |
| **OpenAI** | S-4 (38MB) | 40/40 | $1.86 | 715,984 | ~22s |

### Key Findings

1. **Claude's native PDF vision has size limits**: The 38MB S-4 filing returns HTTP 413 "Request exceeds the maximum size". Claude's PDF vision is limited to ~100 pages or ~32MB base64 encoded.

2. **OpenAI file_search handles unlimited document sizes**: The Assistants API with file_search successfully processed both documents by automatically chunking into a vector store.

3. **Significant cost difference**: OpenAI is ~25x cheaper than Claude for the investor presentation ($0.40 vs $9.84) due to RAG efficiency vs full context.

4. **Token efficiency**: OpenAI used 151K tokens for investor pres vs Claude's 3.2M tokens - RAG retrieval is much more token-efficient than sending full PDF.

### Limitations Discovered

| Provider | Limitation | Workaround |
|----------|-----------|------------|
| Claude | ~32MB PDF size limit | Split large PDFs or use text extraction |
| Claude | High token cost (full PDF per query) | Consider caching or batching questions |
| OpenAI | First query slow (vector store setup) | Reuse assistant for multiple questions |

### Run Locations

Results are stored in:
```
results/wework-bowx/layers/03.5-multimodal/
├── claude/20260129_125822/  # Investor pres (complete)
├── openai/20260129_131214/  # Investor pres (complete)
└── openai/20260129_132010/  # S-4 (complete)
```

### Next Steps

1. Run Gemini on both documents (1M context may handle S-4)
2. Score results against ground truth (Q1-Q10)
3. Compare answer quality across providers
4. Test Claude with chunked S-4 if needed
