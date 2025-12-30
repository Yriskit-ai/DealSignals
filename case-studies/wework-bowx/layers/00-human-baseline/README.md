# Layer 0: Human Expert Baseline

## Purpose

Establish the upper bound of what's achievable with unlimited time and expert attention.

## Setup

- Expert with relevant background (finance, M&A, real estate)
- Full document access
- Unlimited time
- No AI assistance

## Process

1. Expert reads all key documents
2. Answers all 40 questions with citations
3. Documents reasoning for inference questions
4. Notes uncertainty explicitly
5. Records time spent

## Output

| File | Description |
|------|-------------|
| `responses.yaml` | Expert answers to all questions |
| `time-log.md` | Time spent per question/category |
| `difficulty-ratings.yaml` | Expert assessment of question difficulty |
| `notes.md` | Observations about what required expertise vs. straightforward |

## Status

- [ ] Expert identified
- [ ] Documents reviewed
- [ ] Questions answered
- [ ] Citations verified
- [ ] Time logged
- [ ] Difficulty rated

## Why This Matters

If the expert can't find it, we don't fault AI for missing it. This establishes the ceiling for all subsequent layers.
