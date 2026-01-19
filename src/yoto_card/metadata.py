"""Metadata extraction and embedding for yoto-card."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from mutagen.id3 import APIC, ID3, TALB, TIT2, TPE1, TRCK
from mutagen.mp3 import MP3

from yoto_card.exceptions import MetadataError
from yoto_card.utils import sanitize_filename


@dataclass
class SongMetadata:
    """Metadata for a single song."""

    title: str
    artist: str
    album: str | None = None
    thumbnail_url: str | None = None
    duration: int | None = None
    track_number: int | None = None

    def __post_init__(self) -> None:
        """Validate and clean metadata."""
        self.title = self.title.strip()
        self.artist = self.artist.strip()
        if self.album:
            self.album = self.album.strip()


def extract_metadata(video_info: dict[str, Any]) -> SongMetadata:
    """Extract metadata from yt-dlp video info dictionary.

    Args:
        video_info: Dictionary from yt-dlp containing video information.

    Returns:
        SongMetadata object with extracted information.

    Raises:
        MetadataError: If required metadata is missing.
    """
    try:
        # Extract title and artist from various possible fields
        title = video_info.get("title", "Unknown")
        artist = video_info.get("uploader", "Unknown Artist")

        # Improve artist extraction: remove common suffixes
        if artist.endswith(" - Topic"):
            artist = artist[:-8].strip()

        album = video_info.get("album")
        thumbnail_url = video_info.get("thumbnail")
        duration = video_info.get("duration")
        track_number = video_info.get("track_number")

        return SongMetadata(
            title=title,
            artist=artist,
            album=album,
            thumbnail_url=thumbnail_url,
            duration=duration,
            track_number=track_number,
        )
    except Exception as e:
        raise MetadataError(f"Failed to extract metadata: {e}") from e


def download_thumbnail(url: str | None, output_path: Path) -> Path | None:
    """Download and save thumbnail image.

    Args:
        url: URL of the thumbnail to download.
        output_path: Directory where the thumbnail will be saved.

    Returns:
        Path to the downloaded thumbnail, or None if download fails.
    """
    if not url:
        return None

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Determine file extension from URL or content-type
        extension = ".jpg"
        content_type = response.headers.get("content-type", "")
        if "png" in content_type:
            extension = ".png"
        elif "webp" in content_type:
            extension = ".webp"

        thumbnail_path = output_path / f"thumbnail{extension}"
        thumbnail_path.write_bytes(response.content)
        return thumbnail_path
    except Exception:
        # Log warning but don't fail - thumbnail is optional
        return None


def embed_metadata(
    audio_file: Path,
    metadata: SongMetadata,
    thumbnail_path: Path | None = None,
) -> None:
    """Embed metadata into MP3 file using ID3 tags.

    Args:
        audio_file: Path to the MP3 file.
        metadata: SongMetadata object with information to embed.
        thumbnail_path: Optional path to cover art image file.

    Raises:
        MetadataError: If metadata embedding fails.
    """
    try:
        # Load or create ID3 tags
        try:
            tags: ID3 = ID3(str(audio_file))
        except Exception:
            # Create new ID3 tag
            audio = MP3(str(audio_file), ID3=ID3)
            if audio.tags is None:
                audio.add_tags()
            if audio.tags is not None:
                tags = audio.tags
            else:
                tags = ID3()

        # Set basic metadata
        tags.add(TIT2(encoding=3, text=[metadata.title]))
        tags.add(TPE1(encoding=3, text=[metadata.artist]))

        if metadata.album:
            tags.add(TALB(encoding=3, text=[metadata.album]))

        if metadata.track_number:
            tags.add(TRCK(encoding=3, text=[str(metadata.track_number)]))

        # Embed cover art if available
        if thumbnail_path and thumbnail_path.exists():
            try:
                image_data = thumbnail_path.read_bytes()
                # Determine MIME type
                mime_type = "image/jpeg"
                if thumbnail_path.suffix.lower() == ".png":
                    mime_type = "image/png"
                elif thumbnail_path.suffix.lower() == ".webp":
                    mime_type = "image/webp"

                # Create APIC (cover art) frame
                apic = APIC(
                    encoding=3,
                    mime=mime_type,
                    type=3,  # 3 = cover (front)
                    desc="",
                    data=image_data,
                )
                tags.add(apic)
            except Exception:
                # Log warning but don't fail - cover art is optional
                pass

        # Save tags
        tags.save(str(audio_file), v2_version=4)
    except Exception as e:
        raise MetadataError(f"Failed to embed metadata into {audio_file}: {e}") from e


def get_filename(metadata: SongMetadata) -> str:
    """Generate MP3 filename from metadata.

    Args:
        metadata: SongMetadata object.

    Returns:
        Filename in format "Artist - Title.mp3".
    """
    artist = sanitize_filename(metadata.artist or "Unknown Artist")
    title = sanitize_filename(metadata.title or "Unknown Title")

    # Combine and ensure reasonable length
    filename = f"{artist} - {title}.mp3"

    # If filename is too long, truncate base name but keep .mp3
    if len(filename) > 255:  # NTFS/ext4 limit
        # Keep room for " - " (3 chars) + ".mp3" (4 chars) = 7 chars
        max_base_length = 255 - 7
        # Split between artist and title roughly
        artist_max = max(min(len(artist), max_base_length // 2), 10)
        title_max = max_base_length - artist_max - 3  # -3 for " - "

        artist = artist[:artist_max]
        title = title[:title_max]
        filename = f"{artist} - {title}.mp3"

    return filename
