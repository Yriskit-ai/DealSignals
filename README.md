# Deal Signal

**What do humans see that AI misses? What does AI see that humans ignore?**

This is a public research project exploring the intersection of artificial intelligence and human judgment in high-stakes deal-making. We're building the methodology—and eventually the tools—for AI-human symbiosis in investment decisions.

Follow along. Tell us where we're wrong. Build with us.

_"The numbers said yes. Everyone said yes. And they were all wrong."_

_Let's figure out why._

---

## ⚠️ What I'm Asking For

This project is early. The methodology is incomplete. The conclusions are provisional.

I'm asking anyway.

**If you are:**

- An investor who has killed a deal on a "gut feel" you couldn't fully justify
- A deal professional who's seen red flags ignored because they weren't quantifiable
- An AI practitioner who thinks this framing is naïve or wrong

**I want:**

- 30 minutes of your time
- Blunt feedback
- Examples of where this breaks

No pitch. No deck. Just conversation.

If you're willing, [open an issue titled "Conversation"](../../issues/new?title=Conversation) or email me directly at <leonard@yri.ai>.

---

## The Question

In 2021, BowX Acquisition Corp merged with WeWork at a $9 billion valuation.

The spreadsheets worked. The models projected growth. The AI (had it existed then) would have processed thousands of pages of SEC filings and found... what exactly?

Eighteen months later, WeWork's market cap was under $500 million. The company filed for bankruptcy in 2023.

**The numbers said yes. The humans said yes. Everyone was wrong.**

This project exists to understand why—and to build systems that do better.

---

## Why This Matters

AI has conquered the quantitative layer of deal analysis. Models can:

- Parse financial statements in seconds
- Flag covenant violations automatically
- Calculate Z-scores and probability of default
- Scan thousands of comparable transactions

**But deals still fail.** Not because the math was wrong, but because:

- A founder's body language in the investor presentation signaled something the transcript missed
- The third paragraph of footnote 47 contained a disclosure everyone glossed over
- The sponsor's reputation—whispered at industry events but never written down—was a leading indicator
- The market timing required judgment that no model could capture

The quantitative revolution is complete. **The qualitative frontier is wide open.**

---

## What We're Building

### The Research (Open)

A public, evolving methodology for AI-human symbiosis in deal decisioning:

- **Case Studies**: Real deals, analyzed retrospectively. What did AI find? What did it miss? What should humans have caught?
- **Frameworks**: Taxonomies of red flags, sponsor analysis patterns, decision architectures
- **Prompts**: The actual prompts we use—tested, refined, published
- **Journal**: Weekly logs of what we're learning, building, and getting wrong

---

## How We Work

### Principle 1: Retrospective Before Predictive

We start with deals where the outcome is known. WeWork failed. What signals existed in the documentation _before_ the collapse that AI should have surfaced? What signals required human interpretation?

Working backward from known outcomes lets us calibrate before we predict.

### Principle 2: Show the Misses

Most AI demos show the wins. We're equally interested in the failures:

- What did the AI confidently assert that was wrong?
- What did it miss entirely?
- Where did human judgment need to override?

Transparency about limitations builds trust—and better systems.

### Principle 3: The Inference Layer

Individual deal analysis is table stakes. The real value compounds:

- Pattern recognition across sponsors, markets, deal structures
- Institutional knowledge that takes humans decades to accumulate
- Derived signals from gaps and inconsistencies

This is the layer we're most interested in building—and the hardest to systematize.

### Principle 4: Build in Public, Ask in Public

This project only works with input from people who do this work:

- Deal professionals who see what we're missing
- AI practitioners who know better approaches
- Skeptics who think this is impossible

We're not publishing finished research. We're showing our work mid-process and asking for help.

---

## Current Focus: WeWork/BowX SPAC Merger (2021)

Our first case study examines the BowX Acquisition Corp merger with WeWork:

| Document              | What We're Looking For                                  |
| --------------------- | ------------------------------------------------------- |
| S-4 Filing            | Risk disclosures, footnotes, related party transactions |
| Investor Presentation | Claims vs. reality, language patterns, omissions        |
| SoftBank Term Sheets  | Deal structure, protection mechanisms, governance       |
| Media Coverage        | Narrative vs. documentation, timing of concerns         |
| Post-Mortem Analysis  | What was knowable? What required hindsight?             |

**The question**: Given only the documents available at the time of the deal, what could an AI system have surfaced that would have changed the decision?

[→ View the WeWork Case Study](/case-studies/wework-bowx/)

---

## Project Structure

```
DealSignals/
├── methodology/           # The evolving framework
│   ├── ai-human-symbiosis.md
│   ├── decision-architecture.md
│   └── red-flag-taxonomy.md
├── case-studies/          # Retrospective deal analysis
│   └── wework-bowx/
├── prompts/               # Tested prompts for deal analysis
├── tools/                 # Open source utilities
└── journal/               # Weekly build-in-public logs
```

---

## Who's Behind This

**Leonard** — Building deal intelligence tools and trying to understand where both humans and AI get decisions wrong.

[yri.ai](https://yri.ai) · [leonard@yri.ai](mailto:leonard@yri.ai)

---

## Get Involved

### Follow Along

- ⭐ **Star this repo** to track progress
- 🐦 **Follow on X** [@handle] for weekly updates
- 👀 **Watch** for release notifications

### Contribute

- **Open an issue** if you see something we're missing
- **Submit a PR** with case studies, prompts, or methodology improvements
- **Start a discussion** on approaches and frameworks

---

## The Uncomfortable Premise

This project assumes something that makes many AI practitioners uncomfortable:

**Human judgment isn't a bug to be engineered out—it's a feature to be integrated in.**

The best deal-makers aren't running better models. They're reading rooms, sensing hesitation, weighing reputations, and making calls that can't be reduced to data.

The question isn't "How do we replace human judgment?"

It's: **"How do we give human judgment better inputs—and help AI learn what humans see?"**

That's what we're building.

---

## License

Research and methodology: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)  
Code and tools: [MIT License](LICENSE)

---
