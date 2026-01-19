"""Unit tests for metadata module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from yoto_card.metadata import (
    SongMetadata,
    download_thumbnail,
    extract_metadata,
    get_filename,
)


class TestSongMetadata:
    """Tests for SongMetadata dataclass."""

    def test_creates_metadata(self) -> None:
        """Test creating SongMetadata."""
        metadata = SongMetadata(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration=180,
        )

        assert metadata.title == "Test Song"
        assert metadata.artist == "Test Artist"
        assert metadata.album == "Test Album"
        assert metadata.duration == 180

    def test_strips_whitespace(self) -> None:
        """Test that whitespace is stripped."""
        metadata = SongMetadata(
            title="  Test Song  ",
            artist="  Test Artist  ",
            album="  Test Album  ",
        )

        assert metadata.title == "Test Song"
        assert metadata.artist == "Test Artist"
        assert metadata.album == "Test Album"

    def test_optional_fields(self) -> None:
        """Test optional fields."""
        metadata = SongMetadata(
            title="Test Song",
            artist="Test Artist",
        )

        assert metadata.album is None
        assert metadata.thumbnail_url is None
        assert metadata.duration is None
        assert metadata.track_number is None


class TestExtractMetadata:
    """Tests for extract_metadata function."""

    def test_extracts_basic_metadata(self, mock_ydl_info: dict) -> None:
        """Test extracting metadata from yt-dlp info."""
        metadata = extract_metadata(mock_ydl_info)

        assert metadata.title == "Test Song Title"
        assert metadata.artist == "Test Artist"  # " - Topic" removed
        assert metadata.duration == 242

    def test_handles_missing_fields(self) -> None:
        """Test with minimal metadata."""
        info = {
            "title": "Song",
            "uploader": "Artist",
        }

        metadata = extract_metadata(info)

        assert metadata.title == "Song"
        assert metadata.artist == "Artist"
        assert metadata.album is None

    def test_handles_missing_required_fields(self) -> None:
        """Test with missing required fields."""
        info = {}

        metadata = extract_metadata(info)

        assert metadata.title == "Unknown"
        assert metadata.artist == "Unknown Artist"

    def test_removes_topic_suffix(self) -> None:
        """Test removal of ' - Topic' from artist name."""
        info = {
            "title": "Song",
            "uploader": "Artist Name - Topic",
        }

        metadata = extract_metadata(info)

        assert metadata.artist == "Artist Name"


class TestDownloadThumbnail:
    """Tests for download_thumbnail function."""

    @patch("yoto_card.metadata.requests.get")
    def test_downloads_thumbnail(self, mock_get: MagicMock, tmp_path: Path) -> None:
        """Test downloading thumbnail."""
        mock_response = MagicMock()
        mock_response.content = b"fake image data"
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_get.return_value = mock_response

        result = download_thumbnail("https://example.com/thumb.jpg", tmp_path)

        assert result is not None
        assert result.exists()
        assert result.suffix in [".jpg", ".png", ".webp"]

    @patch("yoto_card.metadata.requests.get")
    def test_handles_webp_content_type(self, mock_get: MagicMock, tmp_path: Path) -> None:
        """Test handling WebP content type."""
        mock_response = MagicMock()
        mock_response.content = b"fake webp data"
        mock_response.headers = {"content-type": "image/webp"}
        mock_get.return_value = mock_response

        result = download_thumbnail("https://example.com/thumb.webp", tmp_path)

        assert result is not None
        assert result.suffix == ".webp"

    @patch("yoto_card.metadata.requests.get")
    def test_handles_png_content_type(self, mock_get: MagicMock, tmp_path: Path) -> None:
        """Test handling PNG content type."""
        mock_response = MagicMock()
        mock_response.content = b"fake png data"
        mock_response.headers = {"content-type": "image/png"}
        mock_get.return_value = mock_response

        result = download_thumbnail("https://example.com/thumb.png", tmp_path)

        assert result is not None
        assert result.suffix == ".png"

    def test_handles_no_url(self, tmp_path: Path) -> None:
        """Test with no URL."""
        result = download_thumbnail(None, tmp_path)
        assert result is None

    def test_handles_empty_url(self, tmp_path: Path) -> None:
        """Test with empty URL."""
        result = download_thumbnail("", tmp_path)
        assert result is None

    @patch("yoto_card.metadata.requests.get")
    def test_handles_download_error(self, mock_get: MagicMock, tmp_path: Path) -> None:
        """Test handling download errors."""
        mock_get.side_effect = Exception("Network error")

        result = download_thumbnail("https://example.com/thumb.jpg", tmp_path)

        assert result is None


class TestGetFilename:
    """Tests for get_filename function."""

    def test_generates_filename(self) -> None:
        """Test filename generation."""
        metadata = SongMetadata(
            title="Test Song",
            artist="Test Artist",
        )

        filename = get_filename(metadata)

        assert filename == "Test Artist - Test Song.mp3"

    def test_sanitizes_invalid_characters(self) -> None:
        """Test that invalid characters are removed."""
        metadata = SongMetadata(
            title='Test <Song> "Title"',
            artist="Test: Artist|Name",
        )

        filename = get_filename(metadata)

        assert "<" not in filename
        assert ">" not in filename
        assert '"' not in filename
        assert ":" not in filename
        assert "|" not in filename
        assert filename.endswith(".mp3")

    def test_handles_missing_artist(self) -> None:
        """Test with missing artist."""
        metadata = SongMetadata(
            title="Test Song",
            artist="",
        )

        filename = get_filename(metadata)

        assert "Unknown Artist" in filename
        assert filename.endswith(".mp3")

    def test_handles_missing_title(self) -> None:
        """Test with missing title."""
        metadata = SongMetadata(
            title="",
            artist="Test Artist",
        )

        filename = get_filename(metadata)

        assert "Unknown Title" in filename
        assert filename.endswith(".mp3")

    def test_respects_filename_length_limit(self) -> None:
        """Test that filename respects OS limits."""
        metadata = SongMetadata(
            title="a" * 150,
            artist="b" * 150,
        )

        filename = get_filename(metadata)

        assert len(filename) <= 255
        assert filename.endswith(".mp3")
