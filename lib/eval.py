"""
Evaluation and scoring for Deal Signal experiments.
Implements the rubric from Methodology.md.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Literal
from enum import Enum
import json


class FailureMode(Enum):
    """Failure mode classification from methodology."""

    EXTRACTION_ERROR = "extraction_error"  # Wrong data pulled from document
    CALCULATION_ERROR = "calculation_error"  # Right inputs, wrong math
    REASONING_ERROR = "reasoning_error"  # Right facts, wrong conclusion
    OMISSION = "omission"  # Didn't look in the right place
    HALLUCINATION = "hallucination"  # Invented facts
    CONTAMINATION = "contamination"  # Used training knowledge, not documents
    RELEVANCE_ERROR = "relevance_error"  # Right fact, wrong emphasis
    CONFIDENCE_ERROR = "confidence_error"  # Wrong calibration


@dataclass
class Score:
    """Evaluation score for a single question-answer pair."""

    question_id: str

    # Primary metrics (from methodology)
    found: bool  # Did it attempt to answer?
    accurate: bool  # Factually correct?
    complete: float  # % of known facts (0.0-1.0)
    cited: int  # 0=no cite, 1=document only, 2=document+page+quote
    relevant: int  # 1-5 scale
    actionable: int  # 1-5 scale

    # Calibration
    stated_confidence: Optional[str] = None  # HIGH/MEDIUM/LOW from response
    actual_difficulty: Optional[str] = None  # From ground truth

    # Failure analysis
    failure_mode: Optional[FailureMode] = None
    failure_notes: Optional[str] = None

    # Metadata
    scorer: Optional[str] = None  # Who scored this
    scored_at: Optional[str] = None


@dataclass
class EvalResult:
    """Aggregated evaluation results for an experiment run."""

    run_id: str
    scores: list[Score]

    # Aggregates
    accuracy_rate: float  # % accurate
    completion_rate: float  # Average completeness
    citation_rate: float  # % with full citations (cited=2)
    hallucination_rate: float  # % with hallucination failure mode

    # By question type
    scores_by_category: dict  # category -> aggregated metrics


def score_response(
    question_id: str,
    response: str,
    ground_truth: dict,
    scorer: str = "human",
) -> Score:
    """
    Score a single response against ground truth.

    ground_truth should contain:
      - answer: str (the correct answer)
      - facts: list[str] (specific facts that should be mentioned)
      - citations: list[dict] (expected citations)
      - difficulty: str (HIGH/MEDIUM/LOW)
    """
    # This is a template - actual scoring requires human judgment
    # or a secondary LLM call with rubric

    return Score(
        question_id=question_id,
        found=len(response.strip()) > 0,
        accurate=False,  # Requires verification
        complete=0.0,  # Requires fact checking
        cited=0,  # Requires citation extraction
        relevant=3,  # Default middle score
        actionable=3,  # Default middle score
        scorer=scorer,
    )


def aggregate_scores(scores: list[Score], run_id: str) -> EvalResult:
    """Aggregate individual scores into run-level results."""
    n = len(scores)
    if n == 0:
        raise ValueError("No scores to aggregate")

    return EvalResult(
        run_id=run_id,
        scores=scores,
        accuracy_rate=sum(1 for s in scores if s.accurate) / n,
        completion_rate=sum(s.complete for s in scores) / n,
        citation_rate=sum(1 for s in scores if s.cited == 2) / n,
        hallucination_rate=sum(
            1 for s in scores if s.failure_mode == FailureMode.HALLUCINATION
        )
        / n,
        scores_by_category={},  # TODO: implement category grouping
    )


def save_eval(result: EvalResult, path: str) -> None:
    """Save evaluation results to JSON."""
    data = {
        "run_id": result.run_id,
        "accuracy_rate": result.accuracy_rate,
        "completion_rate": result.completion_rate,
        "citation_rate": result.citation_rate,
        "hallucination_rate": result.hallucination_rate,
        "scores": [
            {
                **asdict(s),
                "failure_mode": s.failure_mode.value if s.failure_mode else None,
            }
            for s in result.scores
        ],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def load_eval(path: str) -> EvalResult:
    """Load evaluation results from JSON."""
    with open(path) as f:
        data = json.load(f)

    scores = []
    for s in data["scores"]:
        fm = s.pop("failure_mode")
        score = Score(**s)
        score.failure_mode = FailureMode(fm) if fm else None
        scores.append(score)

    return EvalResult(
        run_id=data["run_id"],
        scores=scores,
        accuracy_rate=data["accuracy_rate"],
        completion_rate=data["completion_rate"],
        citation_rate=data["citation_rate"],
        hallucination_rate=data["hallucination_rate"],
        scores_by_category=data.get("scores_by_category", {}),
    )
