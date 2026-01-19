"""Yoto-card: Download YouTube Music playlists as MP3 files."""

__version__ = "0.1.0"

from yoto_card.downloader import DownloadResult, PlaylistDownloader, SongResult
from yoto_card.exceptions import (
    DownloadError,
    MetadataError,
    PlaylistError,
    ValidationError,
    YotoCardError,
)
from yoto_card.metadata import SongMetadata

__all__ = [
    "PlaylistDownloader",
    "DownloadResult",
    "SongResult",
    "SongMetadata",
    "YotoCardError",
    "DownloadError",
    "MetadataError",
    "PlaylistError",
    "ValidationError",
]
