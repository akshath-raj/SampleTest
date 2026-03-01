"""
src/core/exceptions.py

Domain-specific exception hierarchy for the code-reasoning agent.

Design principles
-----------------
* Every exception carries enough structured metadata (as constructor
  arguments stored on the instance) so that error-handlers can log or
  respond with context *without* having to parse the message string.
* HTTP-aware exceptions expose a ``status_code`` so the FastAPI exception
  handler can map them to the correct HTTP response without a lookup table.
* All public exceptions inherit from ``AgentBaseError`` so callers can
  catch the entire domain with a single ``except AgentBaseError`` when
  that is appropriate.
"""

from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------


class AgentBaseError(Exception):
    """
    Base class for all code-reasoning agent exceptions.

    Parameters
    ----------
    message:
        Human-readable description of the failure.
    details:
        Optional structured payload (e.g. a dict of context values) that
        will be forwarded to structured logging without appearing in the
        string representation.
    """

    #: Default HTTP status code — subclasses override where needed.
    status_code: int = 500

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details: dict[str, Any] = details or {}

    def __repr__(self) -> str:
        detail_part = f", details={self.details!r}" if self.details else ""
        return f"{type(self).__name__}({self.message!r}{detail_part})"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class ConfigurationError(AgentBaseError):
    """
    Raised when a required configuration value is absent or invalid *after*
    Pydantic validation (e.g. a runtime consistency check).
    """

    status_code = 500

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(
            f"Configuration error for '{field}': {reason}",
            details={"field": field, "reason": reason},
        )
        self.field = field
        self.reason = reason


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------


class IngestionError(AgentBaseError):
    """Base class for all ingestion-layer failures."""

    status_code = 422


class GitCloneError(IngestionError):
    """
    Raised when cloning a remote repository fails.

    Parameters
    ----------
    url:
        The repository URL that was attempted.
    cause:
        The underlying exception, if available.
    """

    def __init__(self, url: str, cause: Exception | None = None) -> None:
        msg = f"Failed to clone repository: {url}"
        if cause:
            msg += f" — {cause}"
        super().__init__(
            msg,
            details={"url": url, "cause": str(cause) if cause else None},
        )
        self.url = url
        self.cause = cause


class FileReadError(IngestionError):
    """Raised when a source file cannot be read or decoded."""

    def __init__(self, path: str, cause: Exception | None = None) -> None:
        msg = f"Cannot read file: {path}"
        if cause:
            msg += f" — {cause}"
        super().__init__(
            msg,
            details={"path": path, "cause": str(cause) if cause else None},
        )
        self.path = path
        self.cause = cause


class NotebookParseError(IngestionError):
    """Raised when a Jupyter notebook (.ipynb) cannot be parsed."""

    def __init__(self, path: str, cause: Exception | None = None) -> None:
        super().__init__(
            f"Failed to parse notebook: {path}",
            details={"path": path, "cause": str(cause) if cause else None},
        )
        self.path = path


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


class ParsingError(AgentBaseError):
    """Base class for all parsing-layer failures."""

    status_code = 422


class TreeSitterInitError(ParsingError):
    """Raised when the Tree-sitter parser fails to initialise for a language."""

    def __init__(self, language: str, cause: Exception | None = None) -> None:
        super().__init__(
            f"Tree-sitter failed to initialise for language '{language}'",
            details={"language": language, "cause": str(cause) if cause else None},
        )
        self.language = language


class SymbolExtractionError(ParsingError):
    """
    Raised when symbol extraction fails for a specific file.

    The agent should log this and fall back to regex-based extraction
    rather than aborting the entire ingestion pipeline.
    """

    def __init__(
        self, filename: str, language: str, cause: Exception | None = None
    ) -> None:
        super().__init__(
            f"Symbol extraction failed for '{filename}' (language: {language})",
            details={
                "filename": filename,
                "language": language,
                "cause": str(cause) if cause else None,
            },
        )
        self.filename = filename
        self.language = language


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


class StorageError(AgentBaseError):
    """Base class for storage-layer failures."""

    status_code = 503


class VectorStoreError(StorageError):
    """Raised when the vector store cannot be read, written, or queried."""

    def __init__(self, operation: str, cause: Exception | None = None) -> None:
        super().__init__(
            f"Vector store error during '{operation}'",
            details={"operation": operation, "cause": str(cause) if cause else None},
        )
        self.operation = operation


class VectorIndexEmptyError(VectorStoreError):
    """Raised when a search is attempted on an un-populated index."""

    def __init__(self) -> None:
        super().__init__(operation="search")
        self.message = (
            "Vector index is empty — call build_index() before searching."
        )


class GraphStoreError(StorageError):
    """Raised when the graph store cannot be read, written, or traversed."""

    def __init__(self, operation: str, cause: Exception | None = None) -> None:
        super().__init__(
            f"Graph store error during '{operation}'",
            details={"operation": operation, "cause": str(cause) if cause else None},
        )
        self.operation = operation


class CacheError(StorageError):
    """Raised when the on-disk pipeline cache cannot be loaded or saved."""

    def __init__(self, path: str, operation: str, cause: Exception | None = None) -> None:
        super().__init__(
            f"Cache {operation} failed for '{path}'",
            details={
                "path": path,
                "operation": operation,
                "cause": str(cause) if cause else None,
            },
        )
        self.path = path
        self.operation = operation


# ---------------------------------------------------------------------------
# LLM / Agent
# ---------------------------------------------------------------------------


class LLMError(AgentBaseError):
    """Base class for LLM-interaction failures."""

    status_code = 502


class LLMRateLimitError(LLMError):
    """Raised when the LLM provider responds with HTTP 429."""

    status_code = 429

    def __init__(self, model: str, retry_after: float | None = None) -> None:
        msg = f"Rate limit exceeded for model '{model}'"
        if retry_after:
            msg += f" — retry after {retry_after:.1f}s"
        super().__init__(
            msg,
            details={"model": model, "retry_after": retry_after},
        )
        self.model = model
        self.retry_after = retry_after


class LLMTimeoutError(LLMError):
    """Raised when an LLM API call exceeds the configured timeout."""

    status_code = 504

    def __init__(self, model: str, timeout_seconds: float) -> None:
        super().__init__(
            f"Request to model '{model}' timed out after {timeout_seconds:.1f}s",
            details={"model": model, "timeout_seconds": timeout_seconds},
        )
        self.model = model
        self.timeout_seconds = timeout_seconds


class LLMResponseParseError(LLMError):
    """Raised when the LLM's response cannot be parsed into the expected format."""

    status_code = 502

    def __init__(
        self, model: str, expected_format: str, raw_response: str | None = None
    ) -> None:
        super().__init__(
            f"Model '{model}' returned an unparseable response "
            f"(expected: {expected_format})",
            details={
                "model": model,
                "expected_format": expected_format,
                "raw_response": (raw_response or "")[:500],
            },
        )
        self.model = model
        self.expected_format = expected_format


class MaxRetriesExceededError(LLMError):
    """Raised when all configured retry attempts have been exhausted."""

    status_code = 503

    def __init__(self, model: str, attempts: int, last_error: Exception | None = None) -> None:
        super().__init__(
            f"All {attempts} retry attempts failed for model '{model}'",
            details={
                "model": model,
                "attempts": attempts,
                "last_error": str(last_error) if last_error else None,
            },
        )
        self.model = model
        self.attempts = attempts
        self.last_error = last_error


class EmbeddingError(LLMError):
    """Raised when embedding generation fails for a batch of texts."""

    def __init__(
        self, model: str, batch_size: int, cause: Exception | None = None
    ) -> None:
        super().__init__(
            f"Embedding generation failed for a batch of {batch_size} texts "
            f"(model: {model})",
            details={
                "model": model,
                "batch_size": batch_size,
                "cause": str(cause) if cause else None,
            },
        )
        self.model = model
        self.batch_size = batch_size


# ---------------------------------------------------------------------------
# Agent / session
# ---------------------------------------------------------------------------


class SessionError(AgentBaseError):
    """Base class for session-management errors."""

    status_code = 400


class SessionNotFoundError(SessionError):
    """Raised when a requested session ID does not exist."""

    status_code = 404

    def __init__(self, session_id: str) -> None:
        super().__init__(
            f"Session '{session_id}' not found.",
            details={"session_id": session_id},
        )
        self.session_id = session_id


class SessionCapacityError(SessionError):
    """Raised when the maximum number of concurrent sessions is reached."""

    status_code = 503

    def __init__(self, max_sessions: int) -> None:
        super().__init__(
            f"Maximum concurrent session capacity ({max_sessions}) reached.",
            details={"max_sessions": max_sessions},
        )
        self.max_sessions = max_sessions


class QueryReframeError(AgentBaseError):
    """Raised when the reframer agent produces an unparseable output."""

    status_code = 422

    def __init__(self, raw_output: str) -> None:
        super().__init__(
            "Reframer agent returned an unparseable response.",
            details={"raw_output": raw_output[:500]},
        )
        self.raw_output = raw_output


class ContextBuildError(AgentBaseError):
    """Raised when the selector cannot assemble any useful context for a query."""

    status_code = 422

    def __init__(self, query: str, reason: str) -> None:
        super().__init__(
            f"Failed to build context for query: {reason}",
            details={"query": query[:200], "reason": reason},
        )
        self.query = query
        self.reason = reason
