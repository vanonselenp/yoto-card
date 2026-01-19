"""Unit tests for utils module."""

from pathlib import Path

from yoto_card.utils import (
    ensure_directory,
    format_duration,
    get_valid_filename,
    sanitize_filename,
    validate_youtube_url,
)


class TestValidateYoutubeUrl:
    """Tests for validate_youtube_url function."""

    def test_valid_youtube_url(self) -> None:
        """Test with valid YouTube URLs."""
        assert validate_youtube_url("https://www.youtube.com/watch?v=test123") is True
        assert validate_youtube_url("https://youtu.be/test123") is True
        assert validate_youtube_url("https://music.youtube.com/playlist?list=test") is True
        assert validate_youtube_url("http://www.youtube.com/watch?v=test123") is True

    def test_invalid_youtube_url(self) -> None:
        """Test with invalid URLs."""
        assert validate_youtube_url("https://example.com/video") is False
        assert validate_youtube_url("https://vimeo.com/123456") is False
        assert validate_youtube_url("not a url at all") is False
        assert validate_youtube_url("") is False

    def test_youtube_music_url(self) -> None:
        """Test with YouTube Music URLs."""
        assert validate_youtube_url("https://music.youtube.com/channel/test") is True
        assert validate_youtube_url("https://youtube-nocookie.com/embed/test") is True


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""

    def test_removes_invalid_characters(self) -> None:
        """Test removal of invalid filename characters."""
        result = sanitize_filename('Test <File> "Name": Test')
        assert "<" not in result
        assert ">" not in result
        assert '"' not in result
        assert ":" not in result

    def test_handles_slashes(self) -> None:
        """Test handling of forward and back slashes."""
        result = sanitize_filename("Test/File\\Name")
        assert "/" not in result
        assert "\\" not in result

    def test_handles_pipe_character(self) -> None:
        """Test handling of pipe character."""
        result = sanitize_filename("Test|File|Name")
        assert "|" not in result

    def test_removes_trailing_spaces_and_dots(self) -> None:
        """Test removal of leading/trailing spaces and dots."""
        result = sanitize_filename("  Test Name.  ")
        assert result == "Test Name"

    def test_limits_length(self) -> None:
        """Test filename length limiting."""
        long_name = "a" * 300
        result = sanitize_filename(long_name)
        assert len(result) <= 200

    def test_preserves_valid_characters(self) -> None:
        """Test that valid characters are preserved."""
        filename = "Test-File_Name (2023)"
        result = sanitize_filename(filename)
        assert result == filename


class TestEnsureDirectory:
    """Tests for ensure_directory function."""

    def test_creates_directory(self, tmp_path: Path) -> None:
        """Test directory creation."""
        test_dir = tmp_path / "new_dir"
        assert not test_dir.exists()

        result = ensure_directory(test_dir)

        assert test_dir.exists()
        assert result == test_dir

    def test_handles_existing_directory(self, tmp_path: Path) -> None:
        """Test with existing directory."""
        test_dir = tmp_path / "existing"
        test_dir.mkdir()

        result = ensure_directory(test_dir)

        assert result == test_dir
        assert test_dir.exists()

    def test_creates_nested_directories(self, tmp_path: Path) -> None:
        """Test creation of nested directories."""
        test_dir = tmp_path / "level1" / "level2" / "level3"
        assert not test_dir.exists()

        result = ensure_directory(test_dir)

        assert test_dir.exists()
        assert result == test_dir


class TestFormatDuration:
    """Tests for format_duration function."""

    def test_format_seconds_only(self) -> None:
        """Test formatting seconds only."""
        assert format_duration(30) == "0:30"
        assert format_duration(59) == "0:59"

    def test_format_minutes_and_seconds(self) -> None:
        """Test formatting minutes and seconds."""
        assert format_duration(90) == "1:30"
        assert format_duration(600) == "10:00"

    def test_format_hours_minutes_seconds(self) -> None:
        """Test formatting with hours."""
        assert format_duration(3661) == "1:01:01"
        assert format_duration(7322) == "2:02:02"

    def test_handles_zero(self) -> None:
        """Test with zero seconds."""
        assert format_duration(0) == "0:00"

    def test_handles_invalid_input(self) -> None:
        """Test with invalid input."""
        assert format_duration("invalid") == "unknown"  # type: ignore
        assert format_duration(None) == "unknown"  # type: ignore


class TestGetValidFilename:
    """Tests for get_valid_filename function."""

    def test_returns_sanitized_filename(self) -> None:
        """Test that valid filename is returned."""
        result = get_valid_filename('Test <File> "Name": Test')
        assert "<" not in result
        assert ">" not in result

    def test_respects_max_length(self) -> None:
        """Test that max length is respected."""
        long_name = "a" * 300
        result = get_valid_filename(long_name, max_length=100)
        assert len(result) <= 100

    def test_default_max_length(self) -> None:
        """Test default max length."""
        long_name = "a" * 300
        result = get_valid_filename(long_name)
        assert len(result) <= 200
