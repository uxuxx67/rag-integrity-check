"""Exception hierarchy for RAG Integrity Check."""


class RagIntegrityError(Exception):
    """Base class for all rag_integrity errors."""


class ConfigError(RagIntegrityError):
    """Raised when configuration is invalid."""


class RegressionError(RagIntegrityError):
    """Raised when a regression set file cannot be parsed or is malformed."""


class StorageError(RagIntegrityError):
    """Raised when the SQLite-backed history store cannot be read or written."""
