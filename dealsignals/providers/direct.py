"""
Direct API providers with native document support.

These providers bypass ZenMux and call APIs directly to access
features like PDF uploads, file search, and large context windows.
"""

import base64
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import anthropic
import google.generativeai as genai
import openai


@dataclass
class DocumentResponse:
    """Response from a document-based query."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    timestamp: str
    cost_usd: float

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp,
            "cost_usd": self.cost_usd,
        }


class DirectProvider(ABC):
    """Base class for direct API providers with document support."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def query_with_document(
        self,
        document_path: Path,
        question: str,
        system_prompt: str | None = None,
    ) -> DocumentResponse:
        """Query the model with a document."""
        pass

    @abstractmethod
    def supports_document_type(self, path: Path) -> bool:
        """Check if this provider supports the document type."""
        pass


class ClaudeDirectProvider(DirectProvider):
    """
    Direct Anthropic Claude API with native PDF support.

    Claude 3.5+ supports PDF documents as base64-encoded content blocks.
    Max ~100 pages per request, uses vision to read PDF pages.
    """

    # Pricing per 1M tokens (Claude Opus 4)
    PRICING = {
        "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    }

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-20250514"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    @property
    def name(self) -> str:
        return "claude-direct"

    def supports_document_type(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def query_with_document(
        self,
        document_path: Path,
        question: str,
        system_prompt: str | None = None,
    ) -> DocumentResponse:
        # Read and encode PDF
        with open(document_path, "rb") as f:
            pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

        # Build message with document block
        content = [
            {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": pdf_data,
                },
            },
            {
                "type": "text",
                "text": question,
            },
        ]

        start_time = time.time()

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt or "",
            messages=[{"role": "user", "content": content}],
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Extract response
        output_text = ""
        for block in response.content:
            if block.type == "text":
                output_text += block.text

        # Calculate cost
        pricing = self.PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        cost = (response.usage.input_tokens / 1_000_000) * pricing["input"] + (
            response.usage.output_tokens / 1_000_000
        ) * pricing["output"]

        return DocumentResponse(
            content=output_text,
            model=self.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat(),
            cost_usd=cost,
        )


class OpenAIDirectProvider(DirectProvider):
    """
    Direct OpenAI API with Assistants and file search.

    Uses the Assistants API with file_search tool for document Q&A.
    Supports PDF, DOCX, TXT, and many other formats.
    """

    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    }

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
        self._assistant_id: str | None = None
        self._vector_store_id: str | None = None

    @property
    def name(self) -> str:
        return "openai-direct"

    def supports_document_type(self, path: Path) -> bool:
        supported = {".pdf", ".docx", ".txt", ".html", ".htm", ".md"}
        return path.suffix.lower() in supported

    def _setup_assistant(self, document_path: Path) -> tuple[str, str]:
        """Create assistant and upload document to vector store."""
        # Create vector store (moved from beta to main client in openai v2.x)
        vector_store = self.client.vector_stores.create(name=f"DealSignals-{document_path.stem}")

        # Upload file to vector store
        with open(document_path, "rb") as f:
            file = self.client.files.create(file=f, purpose="assistants")

        self.client.vector_stores.files.create(
            vector_store_id=vector_store.id,
            file_id=file.id,
        )

        # Wait for processing
        while True:
            vs = self.client.vector_stores.retrieve(vector_store.id)
            if vs.file_counts.completed > 0:
                break
            time.sleep(1)

        # Create assistant
        assistant = self.client.beta.assistants.create(
            name="DealSignals Document Analyst",
            model=self.model,
            tools=[{"type": "file_search"}],
            tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        return assistant.id, vector_store.id

    def query_with_document(
        self,
        document_path: Path,
        question: str,
        system_prompt: str | None = None,
    ) -> DocumentResponse:
        start_time = time.time()

        # Setup assistant if needed
        if self._assistant_id is None:
            self._assistant_id, self._vector_store_id = self._setup_assistant(document_path)

        # Update assistant instructions if system prompt provided
        if system_prompt:
            self.client.beta.assistants.update(
                self._assistant_id,
                instructions=system_prompt,
            )

        # Create thread and run
        thread = self.client.beta.threads.create()

        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=self._assistant_id,
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Get response
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        output_text = ""
        for msg in messages.data:
            if msg.role == "assistant":
                for block in msg.content:
                    if block.type == "text":
                        output_text = block.text.value
                break

        # Get usage (approximate - Assistants API doesn't give exact tokens)
        input_tokens = run.usage.prompt_tokens if run.usage else 0
        output_tokens = run.usage.completion_tokens if run.usage else 0

        pricing = self.PRICING.get(self.model, {"input": 2.5, "output": 10.0})
        cost = (input_tokens / 1_000_000) * pricing["input"] + (
            output_tokens / 1_000_000
        ) * pricing["output"]

        return DocumentResponse(
            content=output_text,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat(),
            cost_usd=cost,
        )

    def cleanup(self):
        """Clean up assistant and vector store."""
        if self._assistant_id:
            self.client.beta.assistants.delete(self._assistant_id)
        if self._vector_store_id:
            self.client.vector_stores.delete(self._vector_store_id)


class GeminiDirectProvider(DirectProvider):
    """
    Direct Google Gemini API with 1M+ context window.

    Gemini 1.5 Pro has a 1M token context window, can fit entire
    SEC filings as plain text without chunking.
    """

    PRICING = {
        "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
        "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
        "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    }

    def __init__(self, api_key: str | None = None, model: str = "gemini-1.5-pro"):
        if api_key:
            genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)

    @property
    def name(self) -> str:
        return "gemini-direct"

    def supports_document_type(self, path: Path) -> bool:
        # Gemini can handle text extraction from various formats
        supported = {".pdf", ".txt", ".html", ".htm", ".md"}
        return path.suffix.lower() in supported

    def query_with_document(
        self,
        document_path: Path,
        question: str,
        system_prompt: str | None = None,
    ) -> DocumentResponse:
        start_time = time.time()

        # For Gemini, we upload the file directly
        uploaded_file = genai.upload_file(document_path)

        # Wait for processing
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(1)
            uploaded_file = genai.get_file(uploaded_file.name)

        # Build prompt
        prompt_parts = []
        if system_prompt:
            prompt_parts.append(system_prompt + "\n\n")
        prompt_parts.append(uploaded_file)
        prompt_parts.append(f"\n\nQuestion: {question}")

        # Generate response
        response = self.model.generate_content(prompt_parts)

        latency_ms = int((time.time() - start_time) * 1000)

        # Extract usage
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count

        pricing = self.PRICING.get(self.model_name, {"input": 1.25, "output": 5.0})
        cost = (input_tokens / 1_000_000) * pricing["input"] + (
            output_tokens / 1_000_000
        ) * pricing["output"]

        # Clean up uploaded file
        genai.delete_file(uploaded_file.name)

        return DocumentResponse(
            content=response.text,
            model=self.model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            timestamp=datetime.utcnow().isoformat(),
            cost_usd=cost,
        )


def get_direct_provider(provider_name: str, **kwargs) -> DirectProvider:
    """Factory function to get a direct provider by name."""
    providers = {
        "claude": ClaudeDirectProvider,
        "openai": OpenAIDirectProvider,
        "gemini": GeminiDirectProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(providers.keys())}")

    return providers[provider_name](**kwargs)
