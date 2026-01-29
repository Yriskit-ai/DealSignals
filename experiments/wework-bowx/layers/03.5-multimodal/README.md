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
