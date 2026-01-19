"""Configuration constants and yt-dlp options for yoto-card."""

from pathlib import Path
from typing import Any

# Audio quality settings
DEFAULT_QUALITY = 320  # kbps
SUPPORTED_QUALITIES = [128, 192, 256, 320]

# File naming template
FILENAME_TEMPLATE = "{artist} - {title}"

# Download settings
DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT = 30
SOCKET_TIMEOUT = 30

# Retry settings for individual song downloads
MAX_SONG_RETRIES = 2

# Progress and logging
VERBOSE_LOGGING = False

# FFmpeg audio codec options by quality
AUDIO_CODEC_OPTIONS = {
    128: "128",
    192: "192",
    256: "256",
    320: "320",
}


def get_ydl_options(
    output_path: str | Path, quality: int = DEFAULT_QUALITY
) -> dict[str, Any]:
    """Generate yt-dlp options dictionary.

    Args:
        output_path: Directory where downloaded files will be saved.
        quality: Audio quality in kbps (128, 192, 256, or 320).

    Returns:
        Dictionary of yt-dlp options.
    """
    if quality not in SUPPORTED_QUALITIES:
        quality = DEFAULT_QUALITY

    bitrate = AUDIO_CODEC_OPTIONS[quality]
    output_dir = Path(output_path)

    return {
        # Output file naming template
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        # Audio extraction
        "format": "bestaudio/best",
        # FFmpeg postprocessor for MP3 conversion
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            }
        ],
        # Retry and timeout settings
        "retries": DEFAULT_RETRIES,
        "socket_timeout": SOCKET_TIMEOUT,
        # Error handling
        "ignoreerrors": True,
        "skip_unavailable_fragments": True,
        # Quiet mode (we'll handle progress separately)
        "quiet": True,
        "no_warnings": False,
        # Don't add metadata yet (we'll do it with mutagen)
        "writeinfojson": False,
        # Fragment retry attempts
        "fragment_retries": DEFAULT_RETRIES,
    }
