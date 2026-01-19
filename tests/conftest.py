"""Pytest configuration and fixtures."""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def tmp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary output directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_metadata() -> dict[str, str]:
    """Sample metadata dictionary."""
    return {
        "title": "Test Song",
        "artist": "Test Artist",
        "album": "Test Album",
        "duration": 180,
    }


@pytest.fixture
def mock_ydl_info() -> dict:
    """Sample yt-dlp video info dictionary."""
    return {
        "id": "test123",
        "title": "Test Song Title",
        "uploader": "Test Artist - Topic",
        "duration": 242,
        "thumbnail": "https://example.com/thumbnail.jpg",
        "url": "https://www.youtube.com/watch?v=test123",
        "ext": "webm",
    }


@pytest.fixture
def mock_playlist_info() -> dict:
    """Sample yt-dlp playlist info dictionary."""
    return {
        "id": "PLtest123",
        "title": "Test Playlist",
        "entries": [
            {
                "id": "video1",
                "url": "https://www.youtube.com/watch?v=video1",
                "title": "Song 1",
                "uploader": "Artist 1",
                "duration": 180,
            },
            {
                "id": "video2",
                "url": "https://www.youtube.com/watch?v=video2",
                "title": "Song 2",
                "uploader": "Artist 2",
                "duration": 200,
            },
            {
                "id": "video3",
                "url": "https://www.youtube.com/watch?v=video3",
                "title": "Song 3",
                "uploader": "Artist 3",
                "duration": 220,
            },
        ],
    }
