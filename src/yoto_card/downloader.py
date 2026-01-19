"""Core playlist downloader using yt-dlp."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yt_dlp
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from yoto_card.config import DEFAULT_QUALITY, SUPPORTED_QUALITIES, get_ydl_options
from yoto_card.exceptions import DownloadError, PlaylistError, ValidationError
from yoto_card.metadata import (
    download_thumbnail,
    embed_metadata,
    extract_metadata,
    get_filename,
)
from yoto_card.utils import ensure_directory, validate_youtube_url


@dataclass
class SongResult:
    """Result of downloading a single song."""

    title: str
    artist: str
    success: bool
    filename: str | None = None
    error_message: str | None = None
    duration: int | None = None


@dataclass
class DownloadResult:
    """Result of downloading an entire playlist."""

    playlist_name: str
    total_songs: int
    successful_downloads: int = 0
    failed_downloads: int = 0
    song_results: list[SongResult] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_songs == 0:
            return 0.0
        return (self.successful_downloads / self.total_songs) * 100


class PlaylistDownloader:
    """Download YouTube Music playlists as MP3 files."""

    def __init__(
        self,
        output_dir: Path | str,
        quality: int = DEFAULT_QUALITY,
        continue_on_error: bool = True,
        verbose: bool = False,
    ):
        """Initialize the playlist downloader.

        Args:
            output_dir: Directory to save downloaded files.
            quality: Audio quality in kbps (128, 192, 256, 320).
            continue_on_error: Continue downloading if a song fails.
            verbose: Enable verbose logging.

        Raises:
            ValidationError: If quality is not supported.
        """
        self.output_dir = Path(output_dir)
        self.continue_on_error = continue_on_error
        self.verbose = verbose
        self.console = Console()

        if quality not in SUPPORTED_QUALITIES:
            raise ValidationError(f"Quality must be one of {SUPPORTED_QUALITIES}, got {quality}")
        self.quality = quality

        # Ensure output directory exists
        ensure_directory(self.output_dir)

    def download_playlist(self, playlist_url: str) -> DownloadResult:
        """Download all songs from a YouTube Music playlist.

        Args:
            playlist_url: URL of the YouTube Music playlist.

        Returns:
            DownloadResult with information about downloaded files.

        Raises:
            ValidationError: If URL is invalid.
            PlaylistError: If playlist extraction fails.
        """
        if not validate_youtube_url(playlist_url):
            raise ValidationError(f"Invalid YouTube URL: {playlist_url}")

        # Extract playlist information
        try:
            playlist_info = self._extract_playlist_info(playlist_url)
        except Exception as e:
            raise PlaylistError(f"Failed to extract playlist information: {e}") from e

        playlist_name = playlist_info.get("title", "Unknown Playlist")
        entries = playlist_info.get("entries", [])

        if not entries:
            raise PlaylistError("Playlist is empty or no videos found")

        result = DownloadResult(
            playlist_name=playlist_name,
            total_songs=len(entries),
        )

        # Create temp directory for thumbnails
        temp_dir = ensure_directory(self.output_dir / ".yoto_temp")

        # Download each song with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TimeRemainingColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Downloading {playlist_name}...",
                total=len(entries),
            )

            for i, entry in enumerate(entries, 1):
                if entry is None:
                    progress.update(task, advance=1)
                    continue

                video_url = entry.get("url")
                if not video_url:
                    progress.update(task, advance=1)
                    continue

                song_result = self._download_single_song(video_url, i, temp_dir)
                result.song_results.append(song_result)

                if song_result.success:
                    result.successful_downloads += 1
                else:
                    result.failed_downloads += 1
                    if not self.continue_on_error:
                        raise DownloadError(f"Failed to download song: {song_result.error_message}")

                progress.update(task, advance=1)

        # Cleanup temp directory
        try:
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

        return result

    def _extract_playlist_info(self, playlist_url: str) -> dict[str, Any]:
        """Extract playlist metadata using yt-dlp.

        Args:
            playlist_url: URL of the playlist.

        Returns:
            Dictionary with playlist information and entries.

        Raises:
            PlaylistError: If extraction fails.
        """
        ydl_options = {
            "quiet": not self.verbose,
            "no_warnings": not self.verbose,
            "extract_flat": "in_playlist",
            "skip_download": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                return info  # type: ignore[no-any-return]
        except Exception as e:
            raise PlaylistError(f"Failed to extract playlist: {e}") from e

    def _download_single_song(
        self, video_url: str, track_number: int, temp_dir: Path
    ) -> SongResult:
        """Download and process a single song.

        Args:
            video_url: URL of the song video.
            track_number: Track number in the playlist.
            temp_dir: Temporary directory for thumbnails.

        Returns:
            SongResult with download result information.
        """
        try:
            # Extract video information
            ydl_options = {
                "quiet": True,
                "no_warnings": True,
                "extract_flat": False,
                "skip_download": True,
            }

            with yt_dlp.YoutubeDL(ydl_options) as ydl:
                video_info = ydl.extract_info(video_url, download=False)

            # Extract metadata
            try:
                metadata = extract_metadata(video_info)
            except Exception as e:
                return SongResult(
                    title=video_info.get("title", "Unknown"),
                    artist=video_info.get("uploader", "Unknown"),
                    success=False,
                    error_message=f"Metadata extraction failed: {e}",
                )

            # Generate filename
            filename = get_filename(metadata)
            file_path = self.output_dir / filename

            # Download audio and convert to MP3
            try:
                download_options = get_ydl_options(self.output_dir, self.quality)
                download_options["quiet"] = True
                download_options["no_warnings"] = not self.verbose

                with yt_dlp.YoutubeDL(download_options) as ydl:
                    ydl.download([video_url])

                # Find the downloaded file (temp filename)
                video_title_sanitized = video_info.get("title", "").replace("/", "_")
                temp_file = self.output_dir / f"{video_title_sanitized}.mp3"

                if temp_file.exists():
                    # Rename to final filename
                    final_file = self.output_dir / filename
                    if temp_file != final_file:
                        temp_file.rename(final_file)
                    file_path = final_file

                # Download and embed metadata
                if metadata.thumbnail_url:
                    thumbnail_path = download_thumbnail(metadata.thumbnail_url, temp_dir)
                else:
                    thumbnail_path = None

                metadata.track_number = track_number
                embed_metadata(file_path, metadata, thumbnail_path)

                return SongResult(
                    title=metadata.title,
                    artist=metadata.artist,
                    success=True,
                    filename=filename,
                    duration=metadata.duration,
                )

            except Exception as e:
                return SongResult(
                    title=metadata.title,
                    artist=metadata.artist,
                    success=False,
                    error_message=str(e),
                    duration=metadata.duration,
                )

        except Exception as e:
            return SongResult(
                title="Unknown",
                artist="Unknown",
                success=False,
                error_message=str(e),
            )

    def print_results(self, result: DownloadResult) -> None:
        """Print download results in a formatted table.

        Args:
            result: DownloadResult object to display.
        """
        self.console.print()
        self.console.print(f"[bold cyan]Playlist:[/bold cyan] {result.playlist_name}")
        download_msg = (
            f"[bold green]Downloaded:[/bold green] "
            f"{result.successful_downloads}/{result.total_songs} ({result.success_rate:.1f}%)"
        )
        self.console.print(download_msg)

        if result.failed_downloads > 0:
            self.console.print(f"[bold red]Failed:[/bold red] {result.failed_downloads}")

        # Show summary table
        if result.song_results:
            table = Table(title="Download Summary", show_header=True, header_style="bold")
            table.add_column("Status")
            table.add_column("Artist")
            table.add_column("Title")
            table.add_column("Details")

            for song in result.song_results:
                status = "[green]✓[/green]" if song.success else "[red]✗[/red]"
                details = song.filename or song.error_message or ""
                table.add_row(status, song.artist, song.title, details)

            self.console.print(table)
