# Ground Truth: WeWork/BowX Case Study

## Purpose

This directory contains the **locked** ground truth for evaluating AI systems against the WeWork/BowX case study. These answers are established by human expert review **before** any AI testing begins.

## Files

| File | Description |
|------|-------------|
| `questions.yaml` | The 40 evaluation questions with metadata |
| `answers.yaml` | Expert answers with citations (to be completed) |

## Ground Truth Process

### 1. Document Review
Expert with relevant background (finance, M&A, real estate) reviews:
- S-4 Registration Statement and amendments
- Investor Presentation
- Proxy Statement
- SoftBank-related exhibits

### 2. Answer Documentation
For each question:
- Provide the factual answer
- Cite document, page, and quote
- Categorize: `stated` / `derived` / `inferred` / `external` / `synthesized`
- Rate difficulty: `easy` / `medium` / `hard`
- Note any caveats

### 3. Lock Before Testing
Once complete:
1. Set `locked: true` in `answers.yaml`
2. Record `locked_at` timestamp and `locked_by` name
3. **Do not modify** after any AI experiments run

## Answer Categories

| Category | Definition | Contamination Risk |
|----------|------------|-------------------|
| **Stated** | Explicitly written in filings | Low |
| **Derived** | Calculable from disclosed numbers | Low |
| **Inferred** | Patterns requiring interpretation | Medium |
| **External** | Requires knowledge beyond documents | High |
| **Synthesized** | Requires connecting multiple documents | Medium |

## Why Lock?

Locking prevents:
- Retrospective adjustment based on AI results
- Confirmation bias in answer refinement
- Moving goalposts during evaluation

If errors are found after locking, document them separately rather than modifying ground truth.

## Status

- [ ] Expert identified
- [ ] Documents obtained
- [ ] Questions reviewed
- [ ] Answers documented
- [ ] Citations verified
- [ ] File locked
