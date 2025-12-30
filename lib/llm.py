"""
Thin LLM wrapper for Deal Signal experiments.
Supports Claude, GPT, and other providers with unified interface.
"""

import os
import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    timestamp: str
    raw_response: Optional[dict] = None


@dataclass
class LLMConfig:
    """Configuration for LLM calls."""

    provider: str  # "anthropic", "openai", "google"
    model: str
    temperature: float = 0.0
    max_tokens: int = 4096


def call_llm(
    prompt: str,
    config: LLMConfig,
    system: Optional[str] = None,
) -> LLMResponse:
    """
    Call an LLM with the given prompt and config.

    Returns standardized LLMResponse regardless of provider.
    """
    import time

    start = time.time()

    if config.provider == "anthropic":
        response = _call_anthropic(prompt, config, system)
    elif config.provider == "openai":
        response = _call_openai(prompt, config, system)
    else:
        raise ValueError(f"Unknown provider: {config.provider}")

    response.latency_ms = int((time.time() - start) * 1000)
    response.timestamp = datetime.utcnow().isoformat()

    return response


def _call_anthropic(
    prompt: str, config: LLMConfig, system: Optional[str]
) -> LLMResponse:
    """Call Anthropic Claude API."""
    try:
        import anthropic
    except ImportError:
        raise ImportError("pip install anthropic")

    client = anthropic.Anthropic()

    messages = [{"role": "user", "content": prompt}]

    kwargs = {
        "model": config.model,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    return LLMResponse(
        content=response.content[0].text,
        model=config.model,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=0,  # Set by caller
        timestamp="",  # Set by caller
        raw_response=response.model_dump(),
    )


def _call_openai(prompt: str, config: LLMConfig, system: Optional[str]) -> LLMResponse:
    """Call OpenAI API."""
    try:
        import openai
    except ImportError:
        raise ImportError("pip install openai")

    client = openai.OpenAI()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    return LLMResponse(
        content=response.choices[0].message.content,
        model=config.model,
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        latency_ms=0,
        timestamp="",
        raw_response=response.model_dump(),
    )


def save_response(response: LLMResponse, path: str) -> None:
    """Save LLM response to JSON file."""
    with open(path, "w") as f:
        json.dump(asdict(response), f, indent=2)


def load_response(path: str) -> LLMResponse:
    """Load LLM response from JSON file."""
    with open(path) as f:
        data = json.load(f)
    return LLMResponse(**data)
