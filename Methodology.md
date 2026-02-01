# Deal Signal Research Methodology

## The Research Question

**Given documents available before a deal closes, what can AI systems surface that would change the decision — and which AI architectures actually help?**

We're testing a progression of AI capabilities against a single deal with a known outcome. Each layer adds complexity. We measure whether that complexity improves results enough to justify the cost.

The deeper question: **Where does AI-human symbiosis actually happen?** Not "can AI read documents" but "at what point does AI surface things humans miss, and where do humans remain essential?"

## The Test Case

**BowX Acquisition Corp. / WeWork SPAC Merger (October 2021)**

| Attribute      | Value                                        |
| -------------- | -------------------------------------------- |
| **Deal Type**  | SPAC merger                                  |
| **Parties**    | BowX Acquisition Corp., WeWork, SoftBank     |
| **Close Date** | October 2021                                 |
| **Outcome**    | WeWork bankruptcy, November 2023             |
| **Documents**  | Public SEC filings, investor presentation    |
| **Constraint** | Only documents available before merger close |

**Why this deal:**

- Outcome is known and definitive
- Documents are public and comprehensive
- Sufficient complexity to stress-test systems
- The failure was foreseeable — signals existed

## Methodological Constraints

### The Contamination Problem

Modern LLMs were trained on data that includes WeWork's history:

- The 2019 failed IPO
- The SPAC merger coverage
- The 2023 bankruptcy
- Extensive post-mortem analysis

When we ask "What are the risks?", the model may pattern-match to what it knows happened rather than analyze the documents.

**Controls we will implement:**

1. **Factual extraction focus** — Questions requiring specific document citations are less susceptible to training contamination than general risk assessment
2. **Source verification** — Every claim must cite document, page, and quote. Claims without citations are flagged as potential contamination
3. **Contamination test** — Before document analysis, ask: "What do you know about WeWork's SPAC merger with BowX?" to establish baseline model knowledge
4. **Counterfactual probe** — Ask: "Based only on these documents, would you invest?" Compare reasoning to known outcome
5. **Novel question types** — Include questions that require document-specific calculations the model couldn't answer from training alone
6. **Explicit constraint** — Instruct models to analyze only from provided documents, note when they're uncertain whether knowledge comes from documents or training

**What we cannot control:**

The model's priors about SPACs, flexible workspace businesses, and aggressive growth projections are shaped by training that includes WeWork's failure. We acknowledge this and focus on document-specific extraction and calculation rather than gestalt risk assessment.

### Single Deal Limitation

Some layers (Memory, Inference, Context Graph) show their value across multiple deals. For single-deal testing:

- We test whether the layer's mechanics work
- We cannot fully test compounding effects
- We note where cross-deal data would likely help

### Retrospective Bias

We know the outcome. This affects:

- How we design questions (we know what mattered)
- How we score relevance (we know what was predictive)
- How we interpret results (confirmation bias risk)

**Mitigation:** Document ground truth and questions before running AI analysis. Don't revise based on what AI finds.

## Ground Truth

Before running any AI system, we establish what should be caught through expert human analysis.

### Ground Truth Categories

| Category        | Definition                             | Contamination Risk | Example                                               |
| --------------- | -------------------------------------- | ------------------ | ----------------------------------------------------- |
| **Stated**      | Explicitly written in filings          | Low                | "We have a history of net losses"                     |
| **Derived**     | Calculable from disclosed numbers      | Low                | Burn rate = cash used / time period                   |
| **Inferred**    | Patterns requiring interpretation      | Medium             | Projection growth rate vs. historical performance gap |
| **External**    | Requires knowledge beyond documents    | High               | Industry comp multiples, 2019 IPO comparison          |
| **Synthesized** | Requires connecting multiple documents | Medium             | S-4 vs. presentation discrepancies                    |

### Ground Truth Process

1. **Expert review** — Domain expert reads S-4, presentation, proxy, key exhibits
2. **Document answers** — For each question, document the answer with citations
3. **Categorize** — Mark each answer by category (Stated/Derived/Inferred/External/Synthesized)
4. **Lock** — Finalize ground truth before any AI testing
5. **Publish** — Ground truth is published as part of research

### Comparison to Actual Human Process

We also document what happened at the time:

- What did analysts and journalists write about the deal?
- What did proxy advisors recommend?
- What concerns did "no" voters cite?
- Where did the actual human due diligence process fail?

This establishes not just what _should_ have been caught, but what _was_ caught and ignored.

## Question Set

### Design Principles

Questions span multiple types:

- **Extraction** — Find specific facts in documents
- **Calculation** — Compute values from extracted data
- **Comparison** — Cross-reference multiple sources
- **Inference** — Draw conclusions from patterns
- **Simulation** — Project outcomes under different assumptions
- **Judgment** — Assess risk, make recommendations

Questions are designed to have clear right/wrong answers where possible, with human judgment reserved for genuinely ambiguous cases.

### Question Categories

**Financial Fundamentals**

1. What is WeWork's revenue for the most recent reported period?
2. What is the revenue growth rate year-over-year?
3. What are operating losses for the most recent period?
4. What is the cash burn rate?
5. What is the cash runway at current burn rate?
6. What is the path to profitability and timeline stated?
7. What are the key assumptions underlying the projections?

**Unit Economics** 8. What is contribution margin per membership? 9. What is revenue per available desk/workstation? 10. What is occupancy rate and how has it trended? 11. What is member churn rate? 12. What is the average revenue per member?

**Obligations and Exposure** 13. What are total lease obligations? 14. What is the duration profile of lease commitments? 15. What are the lease termination provisions? 16. What happens to the business at 70% occupancy? 17. What happens to the business at 50% occupancy?

**Deal Structure** 18. What is the implied enterprise value? 19. What valuation methodology is used to justify the price? 20. What comparable transactions or companies are cited? 21. What are the PIPE terms and who are the investors? 22. What is SoftBank's position before and after the merger? 23. What related-party transactions exist? 24. Who benefits most from this transaction closing?

**Risk and Red Flags** 25. What are the top 5 risk factors disclosed in the S-4? 26. What litigation or regulatory issues are disclosed? 27. What are the customer concentration dynamics? 28. What are the key-person dependencies? 29. What discrepancies exist between the S-4 and investor presentation? 30. What would cause this investment to go to zero?

**Counter-Factual and Judgment** 31. What would have to be true for the projections to be achieved? 32. What is the strongest argument for this deal? 33. What is the strongest argument against this deal? 34. Based only on these documents, should an investor approve the merger? 35. What questions would you ask management before deciding?

### Negative Test Questions

Questions the documents cannot answer, to test hallucination behavior:

36. What is WeWork's market share in flexible workspace?
37. What is the customer acquisition cost?
38. What are competitor occupancy rates?
39. What is Adam Neumann's ongoing involvement?
40. What did the 2019 IPO S-1 project for 2021 revenue?

Expected behavior: System should indicate information is not available in provided documents.

## Evaluation Criteria

### Primary Metrics

| Criteria       | Definition                       | Scoring          | Notes                                             |
| -------------- | -------------------------------- | ---------------- | ------------------------------------------------- |
| **Found**      | Surfaced relevant information    | Binary           | Did it attempt to answer?                         |
| **Accurate**   | Information is factually correct | Binary           | Verified against source                           |
| **Complete**   | Found all relevant information   | % of known facts | Compared to ground truth                          |
| **Cited**      | Traceable to source              | 0/1/2            | 0=no cite, 1=document only, 2=document+page+quote |
| **Relevant**   | Signal vs. noise ratio           | 1-5 scale        | Human scored                                      |
| **Actionable** | Would change a decision          | 1-5 scale        | Human scored, retrospective                       |

### Calibration Metrics

| Criteria                    | Definition                                               | Scoring                                     |
| --------------------------- | -------------------------------------------------------- | ------------------------------------------- |
| **Confidence accuracy**     | When system says "high confidence," is it more accurate? | Correlation coefficient                     |
| **Uncertainty recognition** | Does it know what it doesn't know?                       | % of uncertain items correctly flagged      |
| **Hallucination rate**      | False assertions presented as facts                      | % of claims that are fabricated             |
| **Refusal appropriateness** | Does it refuse when it should?                           | Precision/recall on negative test questions |

### Failure Mode Classification

Every error is classified:

| Failure Mode          | Definition                             | Example                                                         |
| --------------------- | -------------------------------------- | --------------------------------------------------------------- |
| **Extraction error**  | Wrong data pulled from document        | "Revenue was $5.2B" when document says $3.2B                    |
| **Calculation error** | Right inputs, wrong math               | Correctly extracted numbers, wrong growth rate                  |
| **Reasoning error**   | Right facts, wrong conclusion          | Sees high growth + high losses, concludes "strong fundamentals" |
| **Omission**          | Didn't look in the right place         | Missed risk buried in footnote                                  |
| **Hallucination**     | Invented facts                         | Cites a number that doesn't appear in documents                 |
| **Contamination**     | Used training knowledge, not documents | Knows something it couldn't know from documents alone           |
| **Relevance error**   | Right fact, wrong emphasis             | Focuses on minor issue, misses major red flag                   |
| **Confidence error**  | Wrong calibration                      | High confidence on wrong answer, low confidence on right answer |

### Cost Metrics

Tracked for every layer:

| Metric            | Definition                                  |
| ----------------- | ------------------------------------------- |
| **Input tokens**  | Tokens sent to model                        |
| **Output tokens** | Tokens generated by model                   |
| **Total tokens**  | Sum, for cost calculation                   |
| **API cost**      | $ at current pricing                        |
| **Latency**       | Wall-clock time to answer                   |
| **Human time**    | Time required for human review/intervention |

## Experimental Layers

### Layer Organization

Layers are organized into progressions:

**Foundation (Layers 0-2):** Baselines **Retrieval (Layers 3-4):** Getting the right context **Structure (Layers 5-6):** Organizing extracted information **Reasoning (Layers 7-11):** Thinking about information **Synthesis (Layers 12-15):** Connecting information **Accumulation (Layers 16-18):** Building persistent knowledge

**Cross-Cutting Concerns** are tested as variants within layers, not separate layers:

- Prompt optimization
- Multi-model comparison
- Confidence calibration

## Foundation Layers

### Layer 0: Human Expert Baseline

**What it is:** Domain expert analyzes documents, answers questions

**What it tests:** Upper bound of what's achievable with unlimited time and attention

**Setup:**

- Expert with relevant background (finance, M&A, real estate)
- Full document access
- Unlimited time
- No AI assistance

**Process:**

- Expert reads key documents
- Answers all questions with citations
- Documents reasoning for inference questions
- Notes uncertainty explicitly

**Output:**

- Complete ground truth answer set
- Time spent (for comparison)
- Difficulty ratings per question
- Notes on what required expertise vs. what was straightforward

**Why this matters:** Establishes ceiling. If expert can't find it, we don't fault AI for missing it.

### Layer 1: Contamination Baseline

**What it is:** Test what the model "knows" before seeing documents

**What it tests:** Training data contamination level

**Setup:**

- No documents provided
- Ask: "What do you know about the WeWork SPAC merger with BowX in 2021?"
- Ask: "What were the main risks identified in the WeWork SPAC merger?"
- Ask: "What happened to WeWork after the SPAC merger?"

**Process:**

- Record model's pre-existing knowledge
- Identify claims that could only come from training data
- Map to question set: which questions might be "answered" by training vs. documents?

**Output:**

- Model's baseline knowledge about the deal
- List of potentially contaminated question types
- Contamination risk rating per question

**Why this matters:** Can't interpret results without knowing what the model already "knows."

### Layer 2: Direct LLM (Naive)

**What it is:** Paste document text, ask question, get answer

**What it tests:** Raw model capability within context window, with minimal prompting

**Setup:**

- Full document (or as much as fits) in context
- Simple prompt: "Based on the following document, answer this question: [question]"
- No retrieval, no tools, no iteration
- No prompt optimization

**Variables to test:**

- Model (Claude Opus, Claude Sonnet, GPT-5x, Gemini, Additional Models TBD))
- Context handling (truncation strategy when document exceeds window)
- Document (S-4 full vs. S-4 summary sections vs. investor presentation)

**Process:**/Applications

- Run each question through each model/document combination
- Record full response
- Score against evaluation criteria

**Output:**

- Raw capability baseline
- Context window limitation documentation
- Model comparison on same questions

**Why this matters:** Establishes floor. What do you get with zero engineering?

### Layer 2b: Direct LLM (Optimized Prompt)

**What it is:** Same as Layer 2, but with engineered prompts

**What it tests:** How much does prompt engineering improve results at the simplest layer?

**Setup:**

- Same document/model combinations as Layer 2
- Optimized prompts:
  - Role definition ("You are a financial analyst conducting due diligence...")
  - Output format specification
  - Citation requirements
  - Confidence calibration instructions
  - Explicit instruction to use only document content

**Prompt template:**

```
You are a senior financial analyst conducting due diligence on a SPAC merger.
Your task is to analyze the provided document and answer the following question.

Rules:
1. Base your answer ONLY on the provided document
2. Cite specific page numbers and quotes for every claim
3. If the document does not contain the information, say "Not found in document"
4. Rate your confidence: HIGH (directly stated), MEDIUM (derived/calculated), LOW (inferred)
5. Note any caveats or limitations in the data

Document:
[document text]

Question: [question]

Provide your answer with citations:
```

**Process:**

- Same as Layer 2, with optimized prompts
- Compare results to Layer 2

**Output:**

- Improvement from prompt optimization
- Which question types benefit most from better prompts
- Prompt template library for future layers

**Why this matters:** Isolates prompt engineering value. Maybe we don't need complex architectures—just better prompts.

## Retrieval Layers

### Layer 3: Document Parsing Comparison (OCR)

**Status:** FAILED - Methodology limitation discovered

**What it is:** Compare OCR-based parsing against native PDF text extraction

**What it tests:** Does OCR parsing quality affect downstream accuracy?

**Setup:**

- Same source documents (PDF)
- OCR parsing via OCRmyPDF + Tesseract
- Compare against Layer 2 native PDF text extraction

**What we learned:**

The experiment revealed a fundamental methodology flaw: **OCR output for large documents exceeds LLM context limits.**

| Document | OCR Output Size | Result |
|----------|----------------|--------|
| S-4 (1,193 pages, 37MB PDF) | 4.4MB text (~1.1M tokens) | API failures (500 errors) |
| Investor Presentation (6.7MB PDF) | 3.8KB text | Completed successfully |

**Key findings:**

1. **OCR works** - Successfully extracted 57K lines from S-4, preserving page boundaries
2. **Context limits break the approach** - No current LLM can process 4.4MB of text in a single request
3. **Truncation defeats the purpose** - Truncating OCR output to fit context windows would make comparison unfair vs Layer 2's truncation
4. **The methodology assumed text would fit** - This was wrong for large SEC filings

**Partial results:**

- Investor Presentation: 120/120 questions completed (3 models × 40 questions)
- S-4: 0/120 questions completed (API payload too large)

**Conclusion:**

Layer 3's OCR-based approach is not viable for large documents without chunking/RAG (which is Layer 4's domain). The layer conflated two separate problems: parsing quality and context window limits.

**Why this matters:** This failure informed Layer 3.5's design - native multimodal APIs handle document parsing internally, avoiding the context limit problem.

---

### Layer 3.5: Native Multimodal Document Processing

**What it is:** Use LLM providers' native PDF/document capabilities instead of pre-parsing

**What it tests:** Can multimodal APIs process large documents that exceed text context limits?

**Setup:**

- Same source documents (original PDFs, not extracted text)
- Direct API access bypassing text extraction entirely
- Three approaches:

| Provider | Method | Capacity | Notes |
|----------|--------|----------|-------|
| **Claude Direct** | Native PDF via vision | ~100 pages | Processes PDF pages as images |
| **OpenAI Assistants** | File search + RAG | Unlimited | Automatic chunking and retrieval |
| **Gemini Direct** | 1M+ token context | ~800K tokens | Can fit large documents as text |

**Process:**

1. Upload original PDF to each provider's native document API
2. Run same 40-question evaluation set
3. Compare accuracy, latency, and cost across providers
4. Compare results to Layer 2 (text extraction) baseline

**Variables to test:**

- Provider comparison (Claude vs OpenAI vs Gemini)
- Document size handling (investor presentation vs full S-4)
- Question types that benefit from native document access (tables, figures, formatting)

**Output:**

- Native PDF processing accuracy vs text extraction accuracy
- Provider comparison on same documents
- Cost/latency/accuracy tradeoffs
- Which question types benefit from multimodal (visual elements, tables, charts)

**Why this matters:** 

If native multimodal APIs can match or exceed text extraction quality while handling larger documents, the entire parsing pipeline (Layer 3) becomes unnecessary. This could fundamentally simplify document analysis architectures.

**Implementation notes:**

Direct provider implementations exist in `dealsignals/providers/direct.py`:
- `ClaudeDirectProvider` - Anthropic native PDF support
- `OpenAIDirectProvider` - Assistants API with file_search
- `GeminiDirectProvider` - Native file upload with 1M context

---

### Layer 4: Retrieval (Basic RAG)

**What it is:** Chunk documents, embed, retrieve relevant chunks, generate answer

**What it tests:** Does retrieval help when documents exceed context window?

**Setup:**

- Best parser from Layer 3
- Chunking: fixed size with overlap
- Embedding: text-embedding-3-large (or comparable)
- Retrieval: vector similarity search
- Generation: top-k chunks in context, generate answer

**Variables to test:**

- Chunk size: 256 / 512 / 1024 / 2048 tokens
- Overlap: 0% / 10% / 25% / 50%
- Top-k: 3 / 5 / 10 / 20 chunks
- Embedding model comparison

**Process:**

- For each configuration, run all questions
- Track which chunks were retrieved
- Score answers
- Analyze retrieval precision (did it get the right chunks?)

**Output:**

- Optimal chunking configuration
- Retrieval precision vs. answer accuracy correlation
- Which questions require retrieval (couldn't fit in context) vs. which don't

**Why this matters:** RAG is the default architecture. We need to know if it actually helps and when.

### Layer 5: Retrieval (Advanced)

**What it is:** Hybrid retrieval with reranking

**What it tests:** Do retrieval improvements translate to answer improvements?

**Setup:**

- Same chunking as best Layer 4 configuration
- Hybrid retrieval: keyword (BM25) + vector similarity
- Reranking: cross-encoder reranker on retrieved candidates
- Query expansion: LLM rephrases question into multiple queries

**Variables to test:**

- Keyword weight vs. vector weight
- Reranker model
- Number of query variations
- Retrieval candidates before reranking (20 / 50 / 100)

**Process:**

- Same as Layer 4, with enhanced retrieval pipeline
- Compare to Layer 4 baseline

**Output:**

- Improvement from advanced retrieval
- Cost/latency vs. accuracy tradeoff
- Which question types benefit from hybrid/reranking

**Why this matters:** Lots of engineering goes into retrieval. Is it worth it?

## Structure Layers

### Layer 6: Structured Extraction

**What it is:** Extract facts into schema first, then answer from structured facts

**What it tests:** Does intermediate structure improve accuracy?

**Setup:**

- Define fact schema (adapted from Deal Arc):

```
Fact:
  - text: string (the assertion)
  - subject: enum (Target, Seller, Deal, Market, Counterparty)
  - category: enum (Financial, Risk, Term, Milestone, Legal, Operations)
  - nature: enum (Stated, Calculated, Inferred)
  - source_document: string
  - source_page: int
  - source_quote: string
  - confidence: float
  - valid_at: date (when was this true?)
  - extracted_values: dict (any numbers/dates pulled out)
```

- First pass: Extract all facts from documents
- Second pass: Answer questions by querying fact store

**Process:**

- Run extraction on all documents
- Store facts in queryable format
- For each question, retrieve relevant facts, generate answer
- Compare to RAG baseline (Layer 4/5)

**Output:**

- Extraction quality (precision, recall vs. ground truth facts)
- Answer quality from structured facts vs. raw retrieval
- Which question types benefit from structure

**Why this matters:** The Deal Arc architecture assumes structured extraction is valuable. Test it.

### Layer 7: Entity Resolution

**What it is:** Resolve entities and relationships from extracted facts

**What it tests:** Does knowing _who_ and _what_ improve analysis?

**Setup:**

- Build on Layer 6 extractions
- Entity types: Company, Person, Location, Agreement, Metric
- Relationships: owns, invested_in, employed_by, party_to, references
- Resolution: cluster mentions that refer to same entity

**Process:**

- Extract entities from facts
- Resolve duplicates/aliases ("WeWork" = "The We Company" = "Target")
- Build relationship graph
- Answer questions with entity context

**Output:**

- Entity resolution accuracy
- Relationship extraction accuracy
- Answer improvement from entity context
- Which questions require entity understanding

**Why this matters:** Real analysis requires knowing that "SoftBank" mentioned in three places is the same entity with cumulative exposure.

## Reasoning Layers

### Layer 8: Agentic (Reactive)

**What it is:** LLM with tools, calling them as needed

**What it tests:** Does tool access improve results when model decides what to use?

**Setup:**

- Base model with tool access
- Available tools:
  - `search_documents(query)` → relevant chunks
  - `get_section(document, section_name)` → specific section
  - `extract_table(document, page)` → structured table data
  - `calculate(expression)` → numerical computation
  - `get_facts(filter)` → query structured facts from Layer 6
- Reactive: model calls tools when it determines need
- No explicit planning phase

**Process:**

- For each question, let agent work until it produces answer
- Log all tool calls
- Compare to non-agentic baselines

**Output:**

- Tool usage patterns per question type
- Accuracy vs. non-agentic
- Cost/latency increase from agent loop

**Why this matters:** Agentic is the hype. Does it actually help?

### Layer 9: Agentic (Planning)

**What it is:** Explicit planning phase before execution

**What it tests:** Does thinking before acting improve results?

**Setup:**

- Same tools as Layer 8
- Three-phase process:
  1. **Plan:** Given the question, produce explicit plan
     - What information do I need?
     - Where is it likely to be?
     - What calculations are required?
     - What sequence of steps?
  2. **Execute:** Follow the plan using tools
  3. **Synthesize:** Combine findings into answer

**Variables to test:**

- Plan revision: can agent update plan mid-execution?
- Plan granularity: high-level vs. detailed step-by-step
- Plan validation: does a second model check the plan before execution?

**Process:**

- Log plans explicitly
- Compare plan quality to execution quality
- Compare to reactive agent (Layer 8)

**Output:**

- Planning overhead (time, tokens)
- Plan quality → answer quality correlation
- Which question types benefit from explicit planning

**Why this matters:** Planning is intuitively valuable but adds complexity. Quantify the tradeoff.

### Layer 10: Agentic (Extended Thinking)

**What it is:** Planning + execution with extended thinking / chain-of-thought

**What it tests:** Does deeper reasoning improve accuracy?

**Setup:**

- Same as Layer 9, with extended thinking enabled
- Model can "think" before responding at each step
- Thinking traces captured

**Variables to test:**

- Thinking budget (tokens allocated)
- Thinking at which stages (planning only, execution only, all stages)
- Thinking visibility (used for debugging, not shown to user)

**Process:**

- Run same questions as Layer 9
- Compare reasoning traces to outcomes
- Analyze where extended thinking helped vs. didn't

**Output:**

- Thinking budget → accuracy correlation
- Types of questions where thinking helps
- Cost/latency analysis

**Why this matters:** Extended thinking is expensive. When is it worth it?

### Layer 11: Agentic (CLI Tools)

**What it is:** Agent with command-line tools and code execution

**What it tests:** Does computational capability unlock new analyses?

**Setup:**

- All previous tools, plus:
  - `execute_python(code)` → run calculations, data manipulation
  - `parse_pdf_table(file, page)` → extract tables programmatically
  - `query_dataframe(df, query)` → SQL-like queries on extracted data
  - `write_file(path, content)` → save intermediate results
  - `read_file(path)` → retrieve intermediate results
- Full Python environment with pandas, numpy, financial libraries
- File system access for document processing

**Process:**

- Same questions, with computational tools available
- Track which questions benefit from code execution
- Compare to non-code agent (Layer 9/10)

**Output:**

- Which analyses require computation
- Code quality / correctness
- Accuracy on calculation-heavy questions

**Why this matters:** Some questions (DCF modeling, sensitivity analysis) may require real computation, not LLM math.

### Layer 12: Multi-Agent

**What it is:** Specialized agents that collaborate

**What it tests:** Do specialized agents outperform generalist?

**Setup:**

- Multiple specialized agents:
  - **Financial Analyst:** Focuses on numbers, models, projections
  - **Legal Reviewer:** Focuses on contracts, risks, disclosures
  - **Risk Assessor:** Focuses on red flags, downside scenarios
  - **Skeptic:** Challenges conclusions, finds counterarguments
- Orchestration patterns to test:
  - **Sequential:** Each agent reviews in order, builds on previous
  - **Parallel:** All agents analyze independently, synthesize at end
  - **Debate:** Agents challenge each other's conclusions
  - **Hierarchical:** Lead analyst delegates to specialists

**Process:**

- Run each orchestration pattern on question set
- Log inter-agent communication
- Compare to single-agent baselines

**Output:**

- Orchestration pattern effectiveness
- Which question types benefit from multi-agent
- Communication overhead

**Why this matters:** Multi-agent is theoretically powerful but coordination is hard. Does it work?

### Layer 13: Multi-Model Ensemble

**What it is:** Same question to multiple models, aggregate answers

**What it tests:** Does model diversity improve accuracy or surface uncertainty?

**Setup:**

- Multiple models (Claude Sonnet and Opus, GPT-5x, Gemini, Additional TBD)
- Same prompt to each model
- Aggregation strategies:
  - **Majority vote:** Most common answer wins
  - **Confidence weighted:** Weight by model's stated confidence
  - **Synthesis:** Final model synthesizes all answers
  - **Disagreement flagging:** Surface questions where models disagree

**Process:**

- Run all questions through all models
- Apply aggregation strategies
- Compare ensemble to best single model

**Output:**

- Ensemble vs. best single model accuracy
- Disagreement → uncertainty correlation
- Cost multiple (N models = Nx cost)

**Why this matters:** Model diversity might catch errors any single model makes. Or it might just add cost.

## Synthesis Layers

### Layer 14: Multi-Document Synthesis

**What it is:** Cross-reference multiple documents, detect discrepancies

**What it tests:** Does connecting information across documents surface new insights?

**Setup:**

- Multiple documents in scope: S-4, investor presentation, proxy, exhibits
- Explicit cross-referencing tasks:
  - "Compare financial projections in S-4 vs. presentation"
  - "Find risk factors mentioned in S-4 but not in presentation"
  - "Track how key metrics are described differently across documents"
- Contradiction detection
- Gap analysis

**Process:**

- Run synthesis questions
- Document all discrepancies found
- Compare to ground truth discrepancies

**Output:**

- Discrepancy detection precision/recall
- Which discrepancies are material vs. immaterial
- Synthesis-only insights (things invisible in single-document analysis)

**Why this matters:** Real due diligence compares documents. The presentation omits things the S-4 discloses.

### Layer 15: Temporal Analysis

**What it is:** Analyze documents in filing sequence, track evolution

**What it tests:** Does order and change detection matter?

**Setup:**

- Documents ordered by filing date
- Track changes between versions (S-4 amendments)
- Questions:
  - "What changed between S-4 amendment 1 and amendment 2?"
  - "How did risk disclosure language evolve?"
  - "What projections were revised?"

**Process:**

- Analyze documents in sequence
- Build change log
- Identify material changes

**Output:**

- Change detection accuracy
- Material vs. immaterial change classification
- Whether order of analysis affects conclusions

**Why this matters:** Amendments often contain material changes. Version comparison reveals what the company reconsidered.

### Layer 16: Quantitative Modeling

**What it is:** Build financial models from extracted data

**What it tests:** Can AI do analyst-level financial modeling?

**Setup:**

- Extract inputs: revenue, costs, growth rates, margins, assumptions
- Build models:
  - Pro forma projections (replicate company's model)
  - DCF valuation
  - Comparable company analysis
  - Sensitivity tables
- Verify: does reconstructed model match disclosed projections?

**Process:**

- Extract all model inputs
- Build models programmatically
- Compare outputs to disclosed figures
- Run sensitivity analyses

**Output:**

- Input extraction accuracy
- Model construction success rate
- Sensitivity analysis insights
- Valuation reasonableness checks

**Why this matters:** Real analysis builds models. If AI can't model, it can't really analyze.

### Layer 17: Simulation and Stress Testing

**What it is:** "What if" queries and scenario analysis

**What it tests:** Can we reason about futures, not just extract facts?

**Setup:**

- Extract baseline assumptions from Layer 16 models
- Define shock scenarios:
  - Occupancy: -10%, -20%, -40%
  - Revenue growth: 0%, -50%, -100% (flat, half, decline)
  - Cost inflation: +10%, +20%, +50%
  - Interest rates: +100bps, +200bps, +300bps
- Recalculate projections under shocks
- Identify break points and covenant breaches

**Process:**

- Run all shock scenarios
- Calculate revised metrics (cash runway, DSCR, valuation)
- Identify critical thresholds

**Output:**

- Break point identification
- Scenario probability assessment (if possible)
- Risk ranking based on sensitivity

**Why this matters:** Due diligence asks "what could go wrong?" This layer tries to quantify the answers.

## Accumulation Layers

### Layer 18: Memory (Persistent Facts)

**What it is:** Facts persist across analysis sessions

**What it tests:** Does accumulated structure reduce redundant work and improve consistency?

**Setup:**

- Facts extracted in earlier layers persist
- Questions can reference previously extracted facts
- Supersession tracking: if a fact is updated, history preserved
- Session continuity: build on prior analysis

**Process:**

- Run analysis in multiple sessions
- Measure redundant extraction (asking for same fact twice)
- Test consistency (same question, different sessions → same answer?)

**Output:**

- Redundancy reduction
- Consistency improvement
- Memory overhead (storage, retrieval complexity)

**Note:** Limited value on single deal. Full value requires cross-deal testing.

**Why this matters:** Real analysts don't re-read documents every time. Memory is how knowledge compounds.

### Layer 19: Inference (Pattern Recognition)

**What it is:** Patterns derived from accumulated facts

**What it tests:** Can we surface insights not explicitly in any document?

**Setup:**

- Analyze extracted facts for patterns:
  - Projections vs. historical performance gaps
  - Risk disclosure language patterns
  - Related-party transaction complexity
  - Governance structure red flags
- Compare to known failure patterns (from training or explicit rules)
- Flag anomalies

**Process:**

- Extract patterns from fact base
- Match against failure mode library
- Generate risk flags

**Output:**

- Pattern detection accuracy
- Novel pattern discovery
- False positive rate (flagging non-issues)

**Note:** Most valuable with cross-deal training data. For single deal, test against rules/heuristics.

**Why this matters:** The goal is to surface what humans miss. Pattern recognition is how.

### Layer 20: Context Graph

**What it is:** Decision traces — the reasoning connecting data to conclusions

**What it tests:** Does capturing reasoning improve auditability and catch errors?

**Setup:**

- Every extraction, calculation, and conclusion logged with provenance
- Graph structure:
  - Facts → Inferences → Conclusions
  - Each edge is a reasoning step
- Queryable:
  - "Why did we flag this risk?"
  - "What facts support this conclusion?"
  - "What would change if this assumption is wrong?"

**Process:**

- Build context graph during analysis
- Test provenance queries
- Test counterfactual queries
- Evaluate explanation quality

**Output:**

- Graph completeness (all reasoning captured?)
- Explanation quality (human evaluation)
- Error detection (does tracing reasoning catch mistakes?)

**Why this matters:** Black box analysis isn't acceptable for real decisions. Traceability is required.

### Layer 21: Data Graph (Entity-Relationship)

**What it is:** Structured entity relationships and derived values

**What it tests:** Does relationship modeling reveal structural risks?

**Setup:**

- Entities: WeWork, BowX, SoftBank, executives, funds, locations
- Relationships: owns, invested_in, controls, employed_by, guaranteed_by
- Derived values:
  - Total exposure per counterparty
  - Concentration metrics
  - Conflict of interest detection
- Graph queries:
  - "What is SoftBank's total exposure?"
  - "What entities does Adam Neumann control?"
  - "What related-party transactions exist?"

**Process:**

- Build entity-relationship graph from extractions
- Run graph queries
- Calculate derived metrics
- Compare to manually identified relationships

**Output:**

- Graph completeness
- Relationship accuracy
- Derived insight value
- Structural risk identification

**Why this matters:** Complex deals have complex structures. Graphs reveal what linear analysis misses.

## Cross-Cutting Concerns

These are tested as variants within layers, not separate layers.

### Prompt Optimization

**Tested at:** Layers 2, 8, 9, 14

**Question:** At each layer, how much does prompt engineering close the gap to the next layer?

**Method:**

- Naive prompt vs. optimized prompt at same layer
- If optimized prompt at Layer N matches Layer N+1 performance, the architectural complexity of N+1 may not be justified

### Confidence Calibration

**Tested at:** All layers

**Question:** Does the system know what it doesn't know?

**Method:**

- Every answer includes confidence rating (HIGH/MEDIUM/LOW)
- Track calibration: are HIGH confidence answers more accurate?
- Track uncertainty: does LOW confidence correlate with actual difficulty?

**Metrics:**

- Calibration curve (confidence vs. accuracy)
- Brier score
- ECE (Expected Calibration Error)

### Domain Knowledge Injection

**Tested at:** Layers 8-13

**Question:** Does explicit domain knowledge improve results?

**Method:**

- Baseline: general prompt
- Variant: inject domain knowledge
  - "Here's how to analyze a SPAC"
  - "Here are common red flags in flexible workspace businesses"
  - "Here's what went wrong in WeWork's 2019 IPO attempt"

**Measures:**

- Improvement from domain knowledge
- Which question types benefit
- Risk of contamination (domain knowledge includes outcome hints)

### Human-in-the-Loop

**Tested at:** Layers 9-17

**Question:** Where is the optimal human/AI handoff?

**Modes to test:**

| Mode                            | Description                                    |
| ------------------------------- | ---------------------------------------------- |
| **AI only**                     | No human intervention                          |
| **AI proposes, human verifies** | Human reviews AI conclusions                   |
| **Human guides, AI executes**   | Human sets direction, AI does analysis         |
| **Iterative dialogue**          | Human and AI collaborate interactively         |
| **Human reviews uncertainty**   | AI flags low-confidence items for human review |

**Measures:**

- Accuracy in each mode
- Human time required
- Which question types benefit from human involvement

### Iterative Refinement

**Tested at:** Layers 9-17

**Question:** How many passes until diminishing returns?

**Method:**

- Single pass vs. review-and-refine cycles
- Track improvement per iteration
- Identify convergence point

**Measures:**

- Accuracy by iteration count
- Token cost by iteration
- Diminishing returns threshold

### Counter-Argument Generation

**Tested at:** Layers 12, 14

**Question:** Can AI argue both sides?

**Method:**

- For judgment questions, generate:
  - Bull case (strongest argument for)
  - Bear case (strongest argument against)
  - What would have to be true for projections to be met
  - What would cause this to fail
- Evaluate: does it produce genuine arguments or just agree with any position?

**Measures:**

- Argument quality (human rated)
- Balance (does it really steelman both sides?)
- Actionability of counter-arguments

## Testing Modes

### Isolated Testing

Each layer runs independently. Layer 11 doesn't get Layer 6's extractions.

**Purpose:** Tests standalone value of each layer **Limitation:** Doesn't reflect real deployment where layers build on each other

### Cumulative Testing

Each layer builds on previous. Layer 11 gets Layer 6's extractions as input.

**Purpose:** Tests compounding effects **Limitation:** Errors propagate; hard to attribute improvement to specific layer

### A/B Comparison

Adjacent layers compared directly (Layer N vs. Layer N+1).

**Purpose:** Isolates marginal value of each complexity increase **Analysis:** Is the improvement worth the additional cost/complexity?

## What Gets Published

### Per Layer Publication

For each layer, we publish:

**1. Setup Documentation**

- Exact configuration
- Prompts used (full text)
- Code (open source where possible)
- Sufficient detail to reproduce

**2. Raw Output**

- Complete responses for each question
- No cherry-picking
- Includes failures

**3. Evaluation Results**

- Scores per question per criterion
- Aggregate metrics
- Statistical significance tests (where applicable)

**4. Cost Analysis**

- Token counts
- API costs
- Latency measurements
- Human time (where applicable)

**5. Failure Analysis**

- Categorized failures (by failure mode taxonomy)
- Example failures with analysis
- What went wrong and why

**6. Comparative Analysis**

- Improvement vs. previous layer
- Which questions improved, which didn't
- Statistical breakdown

**7. Implications**

- When to use this layer vs. simpler
- Cost/benefit assessment
- Recommendations

### Cumulative Publications

**Progress Updates:** Weekly/biweekly as layers complete **Interim Analysis:** After foundation, retrieval, reasoning, synthesis phases **Final Report:** Complete methodology findings and recommendations

### Open Artifacts

All published openly:

- Question set with ground truth
- Prompts library
- Evaluation rubrics
- Code for each layer
- Raw results data
- Analysis notebooks

## Limitations

### What This Methodology Cannot Tell Us

1. **Single deal generalizability** — Patterns may not generalize beyond WeWork/BowX
2. **Retrospective bias** — We know the outcome
3. **Contamination uncertainty** — Can't fully control for training data knowledge
4. **Question design dependence** — Results depend heavily on questions asked
5. **Implementation quality variance** — Our RAG may not represent best-possible RAG
6. **Model version dependence** — Results may vary with model updates
7. **Human scoring subjectivity** — "Relevance" and "Actionable" are judgment calls

### What Would Change Our Mind

- If Layer 2 (Direct LLM) scores >90% and later layers don't improve, complexity isn't worth it
- If contamination baseline shows the model "knows" the answer without documents, results are suspect
- If human-in-the-loop dramatically outperforms pure AI at every layer, the framing should shift from "AI analysis" to "AI assistance"
- If cost scales faster than accuracy, there's a practical ceiling to useful complexity

## Success Criteria

The research succeeds if we can answer with evidence:

1. **Which layers actually improve results?** Measured by evaluation criteria, statistically significant
2. **By how much?** Quantified improvement per layer
3. **On which question types?** Breakdown by question category
4. **At what cost?** Tokens, dollars, latency, human time
5. **What are the failure modes?** Categorized and analyzed
6. **Where do humans remain essential?** Question types and stages where AI underperforms
7. **What was knowable?** Could any configuration have caught the WeWork risks?

The last question is the point. Everything else is scaffolding.

## Appendix A: Document List

| Document                   | Description                           | Source               | Filing Date   |
| -------------------------- | ------------------------------------- | -------------------- | ------------- |
| S-4 Registration Statement | Merger terms, financials, projections | SEC EDGAR            | June 2021     |
| S-4 Amendments             | Revisions and updates                 | SEC EDGAR            | June-Oct 2021 |
| Investor Presentation      | Pitch deck, growth narrative          | SEC EDGAR (exhibit)  | June 2021     |
| Proxy Statement            | Voting details, board info            | SEC EDGAR            | Sept 2021     |
| SoftBank Agreements        | Related party terms                   | SEC EDGAR (exhibits) | June 2021     |

## Appendix B: Evaluation Rubric

### Relevance (1-5)

| Score | Definition                                 |
| ----- | ------------------------------------------ |
| 1     | Irrelevant to question, noise              |
| 2     | Tangentially related, mostly noise         |
| 3     | Related but misses key points              |
| 4     | Addresses question well, minor gaps        |
| 5     | Directly addresses question, comprehensive |

### Actionable (1-5)

| Score | Definition                                  |
| ----- | ------------------------------------------- |
| 1     | Would not inform decision                   |
| 2     | Minor background, no impact                 |
| 3     | Useful context, might influence             |
| 4     | Material information, would affect analysis |
| 5     | Critical insight, would change decision     |

---

## Appendix C: Failure Mode Examples

| Mode              | Example                                                                                       |
| ----------------- | --------------------------------------------------------------------------------------------- |
| Extraction error  | Reports revenue as $5.2B when document says $3.2B                                             |
| Calculation error | Correctly extracts $3.2B revenue and $2.8B prior year, calculates "20% growth" (actually 14%) |
| Reasoning error   | Notes high revenue growth and high losses, concludes "strong fundamentals"                    |
| Omission          | Answers question about risks without mentioning lease obligations                             |
| Hallucination     | Claims "occupancy rate of 73%" with no such figure in documents                               |
| Contamination     | States "the 2019 IPO failed" without that information in provided documents                   |
| Relevance error   | Asked about top risks, focuses on boilerplate legal disclaimers                               |
| Confidence error  | States "HIGH confidence" on hallucinated fact                                                 |

_This methodology will be refined as we learn. Refinements will be documented and versioned._
