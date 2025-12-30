"""
Cost tracking for Deal Signal experiments.
Tracks tokens, API costs, and latency per methodology requirements.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json


# Pricing per 1M tokens (as of Dec 2024, update as needed)
PRICING = {
    # Anthropic
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.00},
    # OpenAI
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    # Google
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
}


@dataclass
class CostEntry:
    """Cost tracking for a single LLM call."""

    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    input_cost: float  # USD
    output_cost: float  # USD
    total_cost: float  # USD
    latency_ms: int
    timestamp: str


@dataclass
class RunCosts:
    """Aggregated costs for an experiment run."""

    run_id: str
    entries: list[CostEntry]

    # Totals
    total_input_tokens: int
    total_output_tokens: int
    total_tokens: int
    total_cost: float
    total_latency_ms: int

    # Averages
    avg_latency_ms: float
    cost_per_question: float

    # Metadata
    model: str
    started_at: str
    completed_at: str


def calculate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    latency_ms: int = 0,
) -> CostEntry:
    """Calculate cost for a single LLM call."""
    pricing = PRICING.get(model, {"input": 0, "output": 0})

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]

    return CostEntry(
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        input_cost=input_cost,
        output_cost=output_cost,
        total_cost=input_cost + output_cost,
        latency_ms=latency_ms,
        timestamp=datetime.utcnow().isoformat(),
    )


def aggregate_costs(entries: list[CostEntry], run_id: str) -> RunCosts:
    """Aggregate cost entries into run-level totals."""
    if not entries:
        raise ValueError("No cost entries to aggregate")

    total_input = sum(e.input_tokens for e in entries)
    total_output = sum(e.output_tokens for e in entries)
    total_cost = sum(e.total_cost for e in entries)
    total_latency = sum(e.latency_ms for e in entries)

    return RunCosts(
        run_id=run_id,
        entries=entries,
        total_input_tokens=total_input,
        total_output_tokens=total_output,
        total_tokens=total_input + total_output,
        total_cost=total_cost,
        total_latency_ms=total_latency,
        avg_latency_ms=total_latency / len(entries),
        cost_per_question=total_cost / len(entries),
        model=entries[0].model,
        started_at=entries[0].timestamp,
        completed_at=entries[-1].timestamp,
    )


def save_costs(costs: RunCosts, path: str) -> None:
    """Save cost data to JSON."""
    data = {
        "run_id": costs.run_id,
        "model": costs.model,
        "totals": {
            "input_tokens": costs.total_input_tokens,
            "output_tokens": costs.total_output_tokens,
            "total_tokens": costs.total_tokens,
            "total_cost_usd": round(costs.total_cost, 4),
            "total_latency_ms": costs.total_latency_ms,
        },
        "averages": {
            "latency_ms": round(costs.avg_latency_ms, 2),
            "cost_per_question_usd": round(costs.cost_per_question, 6),
        },
        "timing": {
            "started_at": costs.started_at,
            "completed_at": costs.completed_at,
        },
        "entries": [asdict(e) for e in costs.entries],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def format_cost_summary(costs: RunCosts) -> str:
    """Format costs as human-readable summary."""
    return f"""
## Cost Summary: {costs.run_id}

| Metric | Value |
|--------|-------|
| Model | {costs.model} |
| Total Tokens | {costs.total_tokens:,} |
| Input Tokens | {costs.total_input_tokens:,} |
| Output Tokens | {costs.total_output_tokens:,} |
| Total Cost | ${costs.total_cost:.4f} |
| Cost/Question | ${costs.cost_per_question:.6f} |
| Avg Latency | {costs.avg_latency_ms:.0f}ms |
| Total Time | {costs.total_latency_ms / 1000:.1f}s |
""".strip()
