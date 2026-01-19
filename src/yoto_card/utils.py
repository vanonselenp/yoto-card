"""Utility functions for yoto-card."""

import re
from pathlib import Path


def validate_youtube_url(url: str) -> bool:
    """Validate if a URL is a valid YouTube or YouTube Music URL.

    Args:
        url: The URL to validate.

    Returns:
        True if the URL is valid, False otherwise.
    """
    youtube_pattern = (
        r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie|music\.youtube)\.(com|be)/"
    )
    return bool(re.match(youtube_pattern, url))


def sanitize_filename(filename: str) -> str:
    """Remove or replace invalid characters from filename.

    Args:
        filename: The filename to sanitize.

    Returns:
        Sanitized filename safe for use on all operating systems.
    """
    # Remove or replace invalid characters for Windows/Unix and common problematic chars
    invalid_chars = r'[<>:"/\\|?*\[\]\x00-\x1f]'
    sanitized = re.sub(invalid_chars, "_", filename)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(". ")
    # Limit length to 200 characters (leaving room for extension)
    return sanitized[:200]


def ensure_directory(path: Path) -> Path:
    """Create a directory if it doesn't exist.

    Args:
        path: The directory path to create.

    Returns:
        The created or existing directory path.

    Raises:
        OSError: If directory creation fails.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError as e:
        raise OSError(f"Failed to create directory {path}: {e}") from e


def format_duration(seconds: int) -> str:
    """Format duration in seconds to a readable string.

    Args:
        seconds: Duration in seconds.

    Returns:
        Formatted duration string (e.g., "1:23:45" or "5:30").
    """
    if not isinstance(seconds, (int, float)):
        return "unknown"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def get_valid_filename(filename: str, max_length: int = 200) -> str:
    """Convert a string to a valid filename.

    Args:
        filename: The string to convert.
        max_length: Maximum filename length.

    Returns:
        A valid filename string.
    """
    sanitized = sanitize_filename(filename)
    return sanitized[:max_length]
