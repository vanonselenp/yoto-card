"""Integration tests for full download workflow."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from yoto_card.downloader import PlaylistDownloader
from yoto_card.metadata import SongMetadata, get_filename


@pytest.mark.integration
class TestFullWorkflow:
    """Integration tests for complete download workflow."""

    def test_metadata_extraction_and_filename(self) -> None:
        """Test extracting metadata and generating filename."""
        metadata = SongMetadata(
            title="Imagine",
            artist="John Lennon",
            album="Imagine",
            thumbnail_url="https://example.com/thumbnail.jpg",
            duration=183,
            track_number=1,
        )

        filename = get_filename(metadata)

        assert filename == "John Lennon - Imagine.mp3"
        assert metadata.title == "Imagine"
        assert metadata.artist == "John Lennon"

    def test_sanitization_in_filename(self) -> None:
        """Test that problematic characters are sanitized."""
        metadata = SongMetadata(
            title='Song "Title" [Explicit]',
            artist="Artist/Name: Special",
        )

        filename = get_filename(metadata)

        assert '"' not in filename
        assert "[" not in filename
        assert "]" not in filename
        assert "/" not in filename
        assert ":" not in filename
        assert filename.endswith(".mp3")

    @patch("yoto_card.downloader.yt_dlp.YoutubeDL")
    def test_downloader_initialization_and_validation(
        self, mock_ydl_class: MagicMock, tmp_path: Path
    ) -> None:
        """Test downloader initialization with valid parameters."""
        downloader = PlaylistDownloader(
            output_dir=tmp_path,
            quality=320,
            continue_on_error=True,
            verbose=False,
        )

        assert downloader.output_dir == tmp_path
        assert downloader.quality == 320
        assert downloader.continue_on_error is True

    @pytest.mark.slow
    @patch("yoto_card.downloader.yt_dlp.YoutubeDL")
    def test_playlist_structure_handling(
        self, mock_ydl_class: MagicMock, tmp_path: Path, mock_playlist_info: dict
    ) -> None:
        """Test handling of playlist structure from yt-dlp."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = PlaylistDownloader(tmp_path)

        # Verify that playlist info can be extracted
        info = downloader._extract_playlist_info("https://music.youtube.com/playlist?list=test")

        assert info["title"] == "Test Playlist"
        assert len(info["entries"]) == 3

    def test_output_directory_structure(self, tmp_path: Path) -> None:
        """Test that output directory is properly created and organized."""
        download_dir = tmp_path / "downloads"
        PlaylistDownloader(download_dir)

        assert download_dir.exists()
        assert download_dir.is_dir()

    def test_multiple_quality_options(self, tmp_path: Path) -> None:
        """Test that multiple quality options are supported."""
        for quality in [128, 192, 256, 320]:
            downloader = PlaylistDownloader(tmp_path, quality=quality)
            assert downloader.quality == quality

    @patch("yoto_card.downloader.yt_dlp.YoutubeDL")
    def test_youtube_url_variants(self, mock_ydl_class: MagicMock, tmp_path: Path) -> None:
        """Test support for different YouTube URL formats."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {
            "title": "Test",
            "entries": [],
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = PlaylistDownloader(tmp_path)

        # Test various URL formats
        urls = [
            "https://www.youtube.com/playlist?list=PLtest",
            "https://music.youtube.com/playlist?list=PLtest",
            "https://youtu.be/dQw4w9WgXcQ",
        ]

        for url in urls:
            # Should not raise ValidationError
            try:
                downloader.download_playlist(url)
            except Exception as e:
                # Expected to fail on actual extraction, but URL should be valid
                assert "Invalid YouTube URL" not in str(e)
