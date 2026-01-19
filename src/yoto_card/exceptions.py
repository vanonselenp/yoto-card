"""Custom exception classes for yoto-card."""


class YotoCardError(Exception):
    """Base exception class for all yoto-card errors."""

    pass


class ValidationError(YotoCardError):
    """Raised when input validation fails."""

    pass


class DownloadError(YotoCardError):
    """Raised when a download operation fails."""

    pass


class PlaylistError(YotoCardError):
    """Raised when playlist extraction fails."""

    pass


class MetadataError(YotoCardError):
    """Raised when metadata extraction or embedding fails."""

    pass
