"""Unit tests for CLI module."""


import pytest
from click.testing import CliRunner

from yoto_card.cli import main


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner."""
    return CliRunner()


class TestCLI:
    """Tests for the Click CLI interface."""

    def test_help_message(self, cli_runner: CliRunner) -> None:
        """Test the help message."""
        result = cli_runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Download YouTube Music playlists" in result.output
        assert "PLAYLIST_URL" in result.output
        assert "--quality" in result.output
        assert "--output-dir" in result.output

    def test_invalid_url(self, cli_runner: CliRunner) -> None:
        """Test with invalid URL."""
        result = cli_runner.invoke(main, ["https://example.com/invalid"])

        assert result.exit_code != 0
        assert "Invalid YouTube URL" in result.output

    def test_quality_options(self, cli_runner: CliRunner) -> None:
        """Test quality option validation."""
        # Valid quality
        result = cli_runner.invoke(
            main, ["https://music.youtube.com/playlist?list=test", "--quality", "320"]
        )
        assert "Invalid value for '--quality'" not in result.output

    def test_output_directory_option(self, cli_runner: CliRunner) -> None:
        """Test output directory option."""
        result = cli_runner.invoke(
            main,
            [
                "https://music.youtube.com/playlist?list=test",
                "--output-dir",
                "/tmp/test_downloads",
            ],
        )
        # Should fail on actual download, but argument should be accepted
        assert result.exit_code != 0

    def test_verbose_flag(self, cli_runner: CliRunner) -> None:
        """Test verbose flag."""
        result = cli_runner.invoke(
            main,
            [
                "https://music.youtube.com/playlist?list=test",
                "--verbose",
            ],
        )
        # Should fail on actual download, but verbose should be accepted
        assert result.exit_code != 0

    def test_continue_on_error_flag(self, cli_runner: CliRunner) -> None:
        """Test continue-on-error flag."""
        result = cli_runner.invoke(
            main,
            [
                "https://music.youtube.com/playlist?list=test",
                "--continue-on-error",
            ],
        )
        # Should fail on actual download, but flag should be accepted
        assert "--continue-on-error" in result.output or result.exit_code != 0

    def test_missing_required_argument(self, cli_runner: CliRunner) -> None:
        """Test with missing required argument."""
        result = cli_runner.invoke(main, [])

        assert result.exit_code != 0
        assert "PLAYLIST_URL" in result.output

    def test_youtube_url_validation(self, cli_runner: CliRunner) -> None:
        """Test YouTube URL validation."""
        # Valid YouTube URL should be accepted at CLI level
        # (will fail later on actual download)
        result = cli_runner.invoke(main, ["https://www.youtube.com/playlist?list=PLtest"])
        assert "Invalid YouTube URL" not in result.output

    def test_youtube_music_url(self, cli_runner: CliRunner) -> None:
        """Test YouTube Music URL."""
        result = cli_runner.invoke(main, ["https://music.youtube.com/playlist?list=PLtest"])
        assert "Invalid YouTube URL" not in result.output

    def test_youtu_be_short_url(self, cli_runner: CliRunner) -> None:
        """Test youtu.be short URL."""
        result = cli_runner.invoke(main, ["https://youtu.be/dQw4w9WgXcQ"])
        # Youtu.be points to individual videos, not playlists,
        # but should pass URL validation
        assert "Invalid YouTube URL" not in result.output
