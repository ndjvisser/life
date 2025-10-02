"""Shared domain-layer exception hierarchy."""

from __future__ import annotations


class DomainError(Exception):
    """Base class for domain-specific errors in the shared kernel."""


class ValidationError(DomainError):
    """Raised when value objects fail validation rules."""


class RepositoryError(DomainError):
    """Raised for repository contract or persistence violations."""


class TransactionError(DomainError):
    """Raised when unit of work or transaction boundaries are violated."""
