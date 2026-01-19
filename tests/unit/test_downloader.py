"""Unit tests for downloader module."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from yoto_card.downloader import DownloadResult, PlaylistDownloader, SongResult
from yoto_card.exceptions import PlaylistError, ValidationError


class TestPlaylistDownloader:
    """Tests for PlaylistDownloader class."""

    def test_initialization(self, tmp_output_dir: Path) -> None:
        """Test downloader initialization."""
        downloader = PlaylistDownloader(tmp_output_dir, quality=320, verbose=False)

        assert downloader.output_dir == tmp_output_dir
        assert downloader.quality == 320
        assert downloader.verbose is False
        assert downloader.continue_on_error is True

    def test_invalid_quality(self, tmp_output_dir: Path) -> None:
        """Test with invalid quality."""
        with pytest.raises(ValidationError):
            PlaylistDownloader(tmp_output_dir, quality=500)

    def test_creates_output_directory(self) -> None:
        """Test that output directory is created."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "new_downloads"
            assert not output_path.exists()

            PlaylistDownloader(output_path)

            assert output_path.exists()

    def test_supports_string_path(self) -> None:
        """Test that string paths are accepted."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            downloader = PlaylistDownloader(tmpdir)
            assert isinstance(downloader.output_dir, Path)

    def test_invalid_url_validation(self, tmp_output_dir: Path) -> None:
        """Test URL validation in download_playlist."""
        downloader = PlaylistDownloader(tmp_output_dir)

        with pytest.raises(ValidationError):
            downloader.download_playlist("https://example.com/notayoutube")

    @patch("yoto_card.downloader.yt_dlp.YoutubeDL")
    def test_empty_playlist(self, mock_ydl_class: Mock, tmp_output_dir: Path) -> None:
        """Test handling empty playlist."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = {
            "title": "Empty Playlist",
            "entries": [],
        }
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = PlaylistDownloader(tmp_output_dir)

        with pytest.raises(PlaylistError):
            downloader.download_playlist("https://music.youtube.com/playlist?list=test")

    @patch("yoto_card.downloader.yt_dlp.YoutubeDL")
    def test_download_playlist_returns_result(
        self, mock_ydl_class: Mock, tmp_output_dir: Path, mock_playlist_info: dict
    ) -> None:
        """Test that download_playlist returns DownloadResult."""
        mock_ydl_instance = MagicMock()
        mock_ydl_instance.extract_info.return_value = mock_playlist_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance

        downloader = PlaylistDownloader(tmp_output_dir)

        # Mock the single song download
        with patch.object(downloader, "_download_single_song") as mock_single:
            mock_single.return_value = SongResult(
                title="Test",
                artist="Artist",
                success=True,
                filename="Artist - Test.mp3",
            )

            result = downloader.download_playlist("https://music.youtube.com/playlist?list=test")

        assert isinstance(result, DownloadResult)
        assert result.playlist_name == "Test Playlist"
        assert result.total_songs == 3


class TestSongResult:
    """Tests for SongResult dataclass."""

    def test_success_result(self) -> None:
        """Test successful song result."""
        result = SongResult(
            title="Test Song",
            artist="Test Artist",
            success=True,
            filename="Test Artist - Test Song.mp3",
        )

        assert result.title == "Test Song"
        assert result.artist == "Test Artist"
        assert result.success is True
        assert result.filename == "Test Artist - Test Song.mp3"
        assert result.error_message is None

    def test_failed_result(self) -> None:
        """Test failed song result."""
        result = SongResult(
            title="Test Song",
            artist="Test Artist",
            success=False,
            error_message="Download failed",
        )

        assert result.success is False
        assert result.error_message == "Download failed"
        assert result.filename is None


class TestDownloadResult:
    """Tests for DownloadResult dataclass."""

    def test_initialization(self) -> None:
        """Test DownloadResult initialization."""
        result = DownloadResult(
            playlist_name="Test Playlist",
            total_songs=10,
            successful_downloads=7,
            failed_downloads=3,
        )

        assert result.playlist_name == "Test Playlist"
        assert result.total_songs == 10
        assert result.successful_downloads == 7
        assert result.failed_downloads == 3

    def test_success_rate_calculation(self) -> None:
        """Test success rate calculation."""
        result = DownloadResult(
            playlist_name="Test",
            total_songs=10,
            successful_downloads=8,
        )

        assert result.success_rate == 80.0

    def test_success_rate_zero_songs(self) -> None:
        """Test success rate with zero songs."""
        result = DownloadResult(
            playlist_name="Empty",
            total_songs=0,
            successful_downloads=0,
        )

        assert result.success_rate == 0.0

    def test_success_rate_all_successful(self) -> None:
        """Test success rate when all download successfully."""
        result = DownloadResult(
            playlist_name="Test",
            total_songs=5,
            successful_downloads=5,
        )

        assert result.success_rate == 100.0

    def test_song_results_tracking(self) -> None:
        """Test tracking of individual song results."""
        song1 = SongResult(
            title="Song 1",
            artist="Artist",
            success=True,
            filename="Artist - Song 1.mp3",
        )
        song2 = SongResult(
            title="Song 2",
            artist="Artist",
            success=False,
            error_message="Failed",
        )

        result = DownloadResult(
            playlist_name="Test",
            total_songs=2,
            successful_downloads=1,
            failed_downloads=1,
            song_results=[song1, song2],
        )

        assert len(result.song_results) == 2
        assert result.song_results[0].success is True
        assert result.song_results[1].success is False
