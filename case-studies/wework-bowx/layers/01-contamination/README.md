# Layer 1: Contamination Baseline

## Purpose

Test what the model "knows" about WeWork/BowX before seeing any documents. Establishes training data contamination level.

## Setup

- No documents provided to the model
- Ask baseline knowledge questions
- Record pre-existing knowledge

## Contamination Test Questions

1. "What do you know about the WeWork SPAC merger with BowX in 2021?"
2. "What were the main risks identified in the WeWork SPAC merger?"
3. "What happened to WeWork after the SPAC merger?"

## Process

1. Run contamination questions on each model (no documents)
2. Record model's pre-existing knowledge
3. Identify claims that could only come from training data
4. Map to question set: which questions might be "answered" by training vs. documents?

## Output

| File | Description |
|------|-------------|
| `prompt.md` | Exact prompt used |
| `runs/` | Raw responses per model |
| `contamination-map.yaml` | Which questions are at risk |

## Interpretation

High contamination on a question type means:
- Results on that question may reflect training, not document analysis
- Flag in final evaluation
- Focus on questions with low contamination risk for capability assessment

## Status

- [ ] Prompts finalized
- [ ] Claude Sonnet run
- [ ] GPT-4 run
- [ ] Contamination map created
- [ ] Analysis complete
