# Layer 2: Direct LLM

## Purpose

Test raw model capability within context window. Establishes the floor—what do you get with zero engineering?

## Variants

### 2a: Naive Prompt
- Simple prompt: "Based on the following document, answer this question: [question]"
- No retrieval, no tools, no iteration
- Minimal instruction

### 2b: Optimized Prompt
- Role definition, output format, citation requirements
- Confidence calibration instructions
- Explicit document-only instruction

## Setup

- Full document (or as much as fits) in context
- Single turn: question in, answer out
- No iteration or follow-up

## Variables

| Variable | Options |
|----------|---------|
| Model | Claude Sonnet, Claude Opus, GPT-4o, Gemini 1.5 Pro |
| Prompt | Naive, Optimized |
| Document | S-4 full, S-4 summary, Investor presentation |

## Directory Structure

```
02-direct-llm/
├── README.md
├── prompts/
│   ├── naive.md
│   └── optimized.md
├── run.py
└── runs/
    ├── naive-claude-sonnet/
    │   ├── config.yaml
    │   ├── responses.jsonl
    │   ├── eval.json
    │   └── costs.json
    └── optimized-claude-sonnet/
        └── ...
```

## Key Questions

1. How much does prompt optimization improve results?
2. Which question types benefit most from better prompts?
3. What's the accuracy floor with zero engineering?

## Status

- [ ] Prompts written
- [ ] run.py implemented
- [ ] Naive runs complete
- [ ] Optimized runs complete
- [ ] Evaluation scored
- [ ] Analysis written
