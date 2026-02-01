#!/usr/bin/env python3
"""
Layer 3.5: Native Multimodal Document Processing

Runs experiments using direct provider APIs that handle PDF documents natively,
bypassing text extraction entirely.

Providers:
- Claude Direct: Native PDF via vision (~100 page limit)
- OpenAI Direct: Assistants API with file_search (unlimited via RAG)
- Gemini Direct: 1M+ token context (native file upload)

Usage:
    python scripts/run_layer_35.py --provider claude --document s4
    python scripts/run_layer_35.py --provider openai --document investor
    python scripts/run_layer_35.py --provider gemini --document s4
    python scripts/run_layer_35.py --provider all --document all
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dealsignals.providers.direct import (
    ClaudeDirectProvider,
    GeminiDirectProvider,
    OpenAIDirectProvider,
    get_direct_provider,
)


def load_questions(questions_path: Path) -> list[dict]:
    """Load questions from YAML file."""
    with open(questions_path) as f:
        data = yaml.safe_load(f)

    questions = []
    for category_name, category_data in data.get("categories", {}).items():
        for q in category_data.get("questions", []):
            questions.append(
                {
                    "id": q["id"],
                    "text": q["text"],
                    "type": q.get("type", "extraction"),
                    "category": category_name,
                }
            )
    return questions


def load_system_prompt(prompts_dir: Path) -> str:
    """Load system prompt from file."""
    system_path = prompts_dir / "system.md"
    if system_path.exists():
        return system_path.read_text().strip()
    return ""


def run_experiment(
    provider_name: str,
    document_path: Path,
    questions: list[dict],
    system_prompt: str,
    output_dir: Path,
    document_id: str,
) -> dict:
    """Run experiment with a single provider and document."""

    # Initialize provider
    if provider_name == "claude":
        provider = ClaudeDirectProvider(model="claude-sonnet-4-20250514")
    elif provider_name == "openai":
        provider = OpenAIDirectProvider(model="gpt-4o")
    elif provider_name == "gemini":
        provider = GeminiDirectProvider(model="gemini-2.0-flash")
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

    # Check document support
    if not provider.supports_document_type(document_path):
        print(f"Provider {provider_name} does not support {document_path.suffix}")
        return {"error": f"Unsupported document type: {document_path.suffix}"}

    # Create output directory
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / provider_name / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results = {
        "provider": provider_name,
        "document": str(document_path),
        "document_id": document_id,
        "run_id": run_id,
        "started_at": datetime.utcnow().isoformat(),
        "questions": [],
        "summary": {
            "total": len(questions),
            "completed": 0,
            "failed": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "total_latency_ms": 0,
        },
    }

    print(f"\nRunning {provider_name} on {document_id} ({len(questions)} questions)")
    print(f"Output: {run_dir}")
    print("-" * 60)

    for i, q in enumerate(questions, 1):
        q_id = q["id"]
        question_text = q["text"]

        print(f"  [{provider_name}] {q_id}: started")

        try:
            start_time = time.time()
            response = provider.query_with_document(
                document_path=document_path,
                question=question_text,
                system_prompt=system_prompt,
            )
            elapsed = time.time() - start_time

            # Save response
            response_data = {
                "question_id": q_id,
                "question_text": question_text,
                "category": q["category"],
                "response": response.to_dict(),
            }

            # Save JSON
            json_path = run_dir / f"{document_id}_{q_id}.json"
            with open(json_path, "w") as f:
                json.dump(response_data, f, indent=2)

            # Save markdown
            md_path = run_dir / f"{document_id}_{q_id}.md"
            md_content = f"""# {q_id}: {question_text}

**Provider:** {provider_name}
**Document:** {document_id}
**Latency:** {response.latency_ms}ms
**Tokens:** {response.input_tokens} in / {response.output_tokens} out
**Cost:** ${response.cost_usd:.4f}

## Response

{response.content}
"""
            md_path.write_text(md_content)

            results["questions"].append(
                {
                    "id": q_id,
                    "status": "completed",
                    "latency_ms": response.latency_ms,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                }
            )
            results["summary"]["completed"] += 1
            results["summary"]["total_cost"] += response.cost_usd
            results["summary"]["total_tokens"] += response.total_tokens
            results["summary"]["total_latency_ms"] += response.latency_ms

            print(f"  [{provider_name}] {q_id}: completed ({response.latency_ms}ms)")

        except Exception as e:
            error_msg = str(e)
            print(f"  [{provider_name}] {q_id}: failed - {error_msg}")

            results["questions"].append(
                {
                    "id": q_id,
                    "status": "failed",
                    "error": error_msg,
                }
            )
            results["summary"]["failed"] += 1

    # Cleanup for OpenAI (delete assistant and vector store)
    if provider_name == "openai" and hasattr(provider, "cleanup"):
        try:
            provider.cleanup()
        except Exception:
            pass

    results["finished_at"] = datetime.utcnow().isoformat()

    # Save summary
    summary_path = run_dir / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("-" * 60)
    print(f"Completed: {results['summary']['completed']}/{results['summary']['total']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Total Cost: ${results['summary']['total_cost']:.4f}")
    print(f"Total Tokens: {results['summary']['total_tokens']:,}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run Layer 3.5 multimodal experiments")
    parser.add_argument(
        "--provider",
        choices=["claude", "openai", "gemini", "all"],
        default="claude",
        help="Which provider to use",
    )
    parser.add_argument(
        "--document",
        choices=["s4", "investor", "all"],
        default="investor",
        help="Which document to process",
    )
    parser.add_argument(
        "--questions",
        type=str,
        default="experiments/wework-bowx/ground-truth/questions.yaml",
        help="Path to questions YAML",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/wework-bowx/layers/03.5-multimodal",
        help="Output directory for results",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be done without running",
    )

    args = parser.parse_args()

    # Paths
    base_dir = Path(__file__).parent.parent
    questions_path = base_dir / args.questions
    output_dir = base_dir / args.output_dir
    prompts_dir = base_dir / "experiments/wework-bowx/layers/03.5-multimodal/prompts"
    data_dir = base_dir / ".data"

    # Documents
    documents = {
        "s4": data_dir / "S-4_A.pdf",
        "investor": data_dir / "WeWork-Management-Presentation-March-2021-vF-1.pdf",
    }

    # Providers
    providers = ["claude", "openai", "gemini"] if args.provider == "all" else [args.provider]

    # Documents to process
    doc_keys = ["s4", "investor"] if args.document == "all" else [args.document]

    # Load questions and prompt
    questions = load_questions(questions_path)
    system_prompt = load_system_prompt(prompts_dir)

    print(f"Layer 3.5: Native Multimodal Document Processing")
    print(f"=" * 60)
    print(f"Providers: {', '.join(providers)}")
    print(f"Documents: {', '.join(doc_keys)}")
    print(f"Questions: {len(questions)}")
    print(f"Output: {output_dir}")

    if args.dry_run:
        print("\n[DRY RUN] Would process:")
        for provider in providers:
            for doc_key in doc_keys:
                doc_path = documents[doc_key]
                print(f"  - {provider} + {doc_key} ({doc_path})")
        return 0

    # Check documents exist
    for doc_key in doc_keys:
        doc_path = documents[doc_key]
        if not doc_path.exists():
            print(f"ERROR: Document not found: {doc_path}")
            return 1

    # Run experiments
    all_results = []
    for provider in providers:
        for doc_key in doc_keys:
            doc_path = documents[doc_key]
            try:
                result = run_experiment(
                    provider_name=provider,
                    document_path=doc_path,
                    questions=questions,
                    system_prompt=system_prompt,
                    output_dir=output_dir,
                    document_id=doc_key,
                )
                all_results.append(result)
            except Exception as e:
                print(f"ERROR running {provider} on {doc_key}: {e}")
                all_results.append(
                    {
                        "provider": provider,
                        "document_id": doc_key,
                        "error": str(e),
                    }
                )

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    total_completed = 0
    total_failed = 0
    total_cost = 0.0
    for r in all_results:
        if "error" in r and "summary" not in r:
            print(f"  {r['provider']} + {r['document_id']}: ERROR - {r['error']}")
        else:
            s = r.get("summary", {})
            print(
                f"  {r['provider']} + {r['document_id']}: "
                f"{s.get('completed', 0)}/{s.get('total', 0)} "
                f"(${s.get('total_cost', 0):.4f})"
            )
            total_completed += s.get("completed", 0)
            total_failed += s.get("failed", 0)
            total_cost += s.get("total_cost", 0)

    print("-" * 60)
    print(f"Total Completed: {total_completed}")
    print(f"Total Failed: {total_failed}")
    print(f"Total Cost: ${total_cost:.4f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
