# Layer 03 OCR Parsing - Failure Report

**Date:** 2026-01-24
**Status:** FAILED
**Branch:** layer-02-fair

## Executive Summary

Layer 03 attempted to compare OCR-based document parsing against native PDF text extraction. The experiment failed due to a fundamental methodology flaw: **OCR output for large documents exceeds LLM context limits**, making single-pass analysis impossible.

## What We Tried

### OCR Pipeline

1. **OCR Service:** Local OCRmyPDF 16.13.0 + Tesseract 5.5.2
2. **Documents:**
   - S-4 Filing (37MB PDF, 1,193 pages)
   - Investor Presentation (6.7MB PDF)
3. **Options:** `skip_text=true` to handle Tagged PDF errors
4. **Output Format:** Page-aware JSONL converted to `[Page N]` prefixed text

### OCR Results

| Document | PDF Size | Pages | OCR Time | Output Size | Output Lines |
|----------|----------|-------|----------|-------------|--------------|
| S-4 | 37MB | 1,193 | ~45 min | 4.4MB | 57,093 |
| Investor Pres | 6.7MB | ~50 | ~35 min | 3.8KB | 252 |

**OCR quality was good** - text extraction preserved page boundaries and captured document structure.

### LLM Experiment Results

| Document | Questions | Models | Completed | Failed | Cost |
|----------|-----------|--------|-----------|--------|------|
| Investor Pres | 40 | 3 | 120 | 0 | $1.32 |
| S-4 | 40 | 3 | 0 | 120 | $0.00 |

**Failure mode:** All S-4 requests returned HTTP 500 errors from ZenMux API due to payload size (4.4MB text = ~1.1M tokens).

## Why It Failed

### The Methodology Flaw

Layer 03 was designed assuming:
1. Parse documents with different methods
2. Feed parsed text to LLMs
3. Compare accuracy across parsing methods

This assumes **parsed text fits in LLM context windows**. For the S-4:
- OCR output: 4.4MB (~1.1M tokens)
- Claude context: 200K tokens
- GPT-4 context: 128K tokens
- Even Gemini's 1M context is borderline

### The Conflation Problem

Layer 03 conflated two separate concerns:
1. **Parsing quality** - How well does OCR extract text?
2. **Context limits** - Can LLMs process the extracted text?

These should be tested independently:
- Parsing quality → Compare extraction accuracy on sample pages
- Context limits → Use RAG/chunking (Layer 4) or native multimodal (Layer 3.5)

## Partial Results

### Investor Presentation (Completed)

120 responses saved to:
```
results/wework-bowx/layers/03-parsing/ocr/responses/20260124_032448/
```

Models tested:
- claude-sonnet-4-5
- gpt-5.2
- claude-opus-4-5

**Note:** Investor presentation had minimal extractable text (mostly images/charts), so OCR results were sparse. This actually demonstrates a key finding: **slide-heavy documents don't benefit from OCR**.

### S-4 (Failed)

No results. All 120 attempts (40 questions × 3 models) failed with 500 errors.

## Lessons Learned

1. **Test assumptions early** - Should have checked if OCR output fits context before building pipeline
2. **Large SEC filings need different approaches** - 1,000+ page documents require chunking or native multimodal
3. **OCR is not the bottleneck** - Parsing worked fine; the problem was downstream consumption
4. **Layer design should be atomic** - Don't combine parsing quality testing with full-document analysis

## Recommendations

### Immediate: Layer 3.5 (Multimodal)

Use native multimodal APIs that handle document parsing internally:
- **Claude Direct** - Native PDF via vision (~100 page limit)
- **OpenAI Assistants** - File search with automatic chunking
- **Gemini Direct** - 1M token context, native file upload

This bypasses the text extraction step entirely.

### Future: Separate Parsing Quality Testing

If OCR vs native parsing comparison is still desired:
1. Select representative page samples (not full document)
2. Compare extraction accuracy on those samples
3. Use human ground truth for specific tables/figures
4. This becomes a focused parsing benchmark, not a full Q&A experiment

## Files Generated

```
experiments/wework-bowx/data/layer-03/ocrmypdf_tesseract_v1/
├── investor_presentation_meta.json
├── investor_presentation_ocr.txt
├── investor_presentation_pages.jsonl
├── investor_presentation_searchable.pdf
├── investor_presentation_text.txt
├── s4_meta.json
├── s4_ocr.txt
├── s4_pages.jsonl
├── s4_searchable.pdf
└── s4_text.txt

results/wework-bowx/layers/03-parsing/ocr/
├── events.jsonl (480 events)
└── responses/20260124_032448/ (120 files for investor_pres only)
```

## Cost Summary

| Item | Cost |
|------|------|
| OCR processing | $0 (local) |
| LLM API (successful) | $1.32 |
| LLM API (failed) | $0.00 |
| **Total** | **$1.32** |

## Next Steps

1. ~~Retry S-4 with truncation~~ - Defeats the purpose of Layer 03
2. **Implement Layer 3.5** - Native multimodal document processing
3. Update experiment configs for Layer 3.5
4. Run Layer 3.5 with same 40-question evaluation set
