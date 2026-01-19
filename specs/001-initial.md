  # Implementation Plan: YouTube Music Playlist Downloader

  ## Overview
  Create a CLI tool to download YouTube Music playlists as high-quality MP3 files with embedded metadata (artist, title, album art). Files will be named as "Artist - Title.mp3" at 320 kbps quality.

  ## User Requirements
  - Download all songs from a YouTube Music playlist URL
  - Save as 320 kbps MP3 files
  - Embed full metadata: title, artist, album, cover art
  - File naming: "Artist - Title.mp3"
  - Continue on errors, don't stop entire download
  - Show progress indication

  ## Project Structure to Create

  ```
  yoto-card/
  ├── src/yoto_card/
  │   ├── __init__.py           # Package initialization, version
  │   ├── __main__.py           # Entry point for python -m yoto_card
  │   ├── cli.py                # Click-based CLI interface
  │   ├── downloader.py         # Core PlaylistDownloader class with yt-dlp
  │   ├── metadata.py           # Metadata extraction and ID3 embedding
  │   ├── config.py             # Constants and yt-dlp configuration
  │   ├── exceptions.py         # Custom exception hierarchy
  │   └── utils.py              # Utilities (validation, sanitization)
  ├── tests/
  │   ├── conftest.py           # Pytest fixtures
  │   ├── unit/
  │   │   ├── test_downloader.py
  │   │   ├── test_metadata.py
  │   │   ├── test_utils.py
  │   │   └── test_cli.py
  │   └── integration/
  │       └── test_full_workflow.py
  ├── pyproject.toml            # Project config with dependencies
  └── README.md                 # Updated usage documentation
  ```

  ## Dependencies

  **Production**:
  - `yt-dlp>=2024.1.0` - YouTube downloader (actively maintained)
  - `mutagen>=1.47.0` - MP3 metadata and cover art embedding
  - `requests>=2.31.0` - Download thumbnails
  - `rich>=13.0.0` - Progress bars and colored output
  - `click>=8.1.0` - CLI framework

  **Development**:
  - `pytest>=7.4.0`, `pytest-cov>=4.1.0`, `pytest-mock>=3.12.0`
  - `ruff>=0.1.0` - Linting and formatting
  - `mypy>=1.7.0`, `types-requests` - Type checking

  ## Implementation Steps

  ### Phase 1: Project Initialization

  1. **Initialize uv project**
  ```bash
  uv init --name yoto-card
  ```

  2. **Configure pyproject.toml**
  - Add all dependencies (production + dev)
  - Set Python requirement: `>=3.10`
  - Configure CLI entry point: `yoto-card = "yoto_card.cli:main"`
  - Add tool configurations for ruff, pytest, mypy, coverage

  3. **Create directory structure**
  - Create all module files in `src/yoto_card/`
  - Create test directories: `tests/unit/`, `tests/integration/`

  4. **Install dependencies**
  ```bash
  uv sync
  ```

  ### Phase 2: Core Implementation

  **Order of implementation** (foundation first, build up):

  1. **exceptions.py** - Custom exception classes
  - `YotoCardError` (base)
  - `DownloadError`, `MetadataError`, `ValidationError`, `PlaylistError`

  2. **config.py** - Configuration constants
  - Audio quality settings (DEFAULT_QUALITY = 320)
  - File naming template: `"{artist} - {title}.mp3"`
  - yt-dlp base options dictionary
  - Retry settings, timeouts

  3. **utils.py** - Utility functions
  - `validate_youtube_url(url: str) -> bool` - Regex validation
  - `sanitize_filename(filename: str) -> str` - Remove invalid chars
  - `ensure_directory(path: Path) -> Path` - Create dir if needed
  - `format_duration(seconds: int) -> str` - Display formatting

  4. **metadata.py** - Metadata handling
  - `SongMetadata` dataclass (title, artist, album, thumbnail_url, duration, track_number)
  - `extract_metadata(video_info: dict) -> SongMetadata` - Parse yt-dlp info
  - `download_thumbnail(url: str, output_path: Path) -> Path | None` - Fetch cover art
  - `embed_metadata(audio_file: Path, metadata: SongMetadata, thumbnail_path: Path | None)` - Write ID3 tags with mutagen
  - `get_filename(metadata: SongMetadata) -> str` - Generate "Artist - Title.mp3"

  5. **downloader.py** - Core download logic
  - `PlaylistDownloader` class with constructor: `__init__(output_dir, quality=320, continue_on_error=True, verbose=False)`
  - `download_playlist(playlist_url: str) -> DownloadResult` - Main orchestration
  - `_build_ydl_options() -> dict` - Configure yt-dlp (format='bestaudio/best', postprocessors for MP3)
  - `_extract_playlist_info(url: str) -> dict` - Get playlist metadata
  - `_download_single_song(video_url: str, track_number: int) -> SongResult` - Download + process one song
  - Result dataclasses: `SongResult`, `DownloadResult` (track success/failures)
  - Use Rich Progress for visual feedback

  6. **cli.py** - Command-line interface
  - Click-based CLI with `main()` entry point
  - Arguments:
  - `playlist_url` (required)
  - `--output-dir/-o` (default: ./downloads)
  - `--quality` (default: 320, choices: 128, 192, 256, 320)
  - `--verbose/-v` (flag)
  - Validate URL before starting
  - Create output directory
  - Call `PlaylistDownloader.download_playlist()`
  - Display summary at end

  7. **__init__.py** - Package exports
  - Define `__version__ = "0.1.0"`
  - Export main classes: `PlaylistDownloader`, exceptions

  8. **__main__.py** - Entry point
  - Import and call `cli.main()`

  ### Phase 3: Testing

  1. **Unit tests** (with mocking):
  - `test_utils.py` - Test sanitization, validation, edge cases
  - `test_metadata.py` - Mock yt-dlp info, test extraction and embedding
  - `test_downloader.py` - Mock yt-dlp calls, test error handling, result tracking
  - `test_cli.py` - Use Click's CliRunner, test argument parsing

  2. **Integration tests**:
  - `test_full_workflow.py` - Test with a small, stable YouTube playlist
  - Verify file creation, metadata embedding, file naming

  3. **Fixtures in conftest.py**:
  - `tmp_output_dir` - Temporary directory
  - `sample_metadata` - Example SongMetadata objects
  - `mock_ydl_info` - Sample yt-dlp response dictionaries

  4. **Run tests and coverage**:
  ```bash
  uv run pytest --cov=src --cov-report=html
  ```
  Target: >85% coverage

  ### Phase 4: Documentation

  1. **Update README.md**:
  - Project description
  - Prerequisites (FFmpeg installation required by yt-dlp)
  - Installation: `uv sync`
  - Usage examples:
  ```bash
  uv run yoto-card "https://music.youtube.com/playlist?list=..."
  uv run yoto-card "URL" --output-dir ~/Music/Yoto
  ```
  - CLI arguments reference
  - Troubleshooting (FFmpeg, network errors)

  2. **Add docstrings**:
  - All modules, classes, functions
  - Include type hints in all signatures
  - Document exceptions raised

  ### Phase 5: Quality Assurance

  1. **Code quality**:
  ```bash
  uv run ruff format src tests
  uv run ruff check src tests --fix
  uv run mypy src
  ```

  2. **Manual testing**:
  - Test with various playlist URLs
  - Verify metadata embedding (check files in music player)
  - Test error scenarios (invalid URL, network issues)
  - Test with different quality settings

  ## Critical Files

  1. **pyproject.toml** - Project configuration and dependencies
  2. **src/yoto_card/downloader.py** - Core download orchestration (most complex)
  3. **src/yoto_card/metadata.py** - Metadata extraction and embedding
  4. **src/yoto_card/cli.py** - User interface
  5. **src/yoto_card/config.py** - Central configuration

  ## Key Technical Decisions

  1. **yt-dlp configuration**:
  - Format: `bestaudio/best`
  - Postprocessor: FFmpegExtractAudio to MP3 at 320kbps
  - Enable retries (3 attempts)
  - `ignoreerrors=True` for continue-on-error behavior

  2. **Metadata embedding with mutagen**:
  - Use ID3v2.4 tags (TIT2, TPE1, TALB)
  - Embed cover art as APIC frame
  - Pure Python, cross-platform

  3. **Progress with Rich**:
  - Progress bar for entire playlist
  - Update via yt-dlp progress_hooks
  - Summary table at end

  4. **Error handling**:
  - Try-except around each song download
  - Collect success/failure results
  - Continue with next song on error
  - Final summary shows what succeeded/failed

  ## Verification

  After implementation, verify:

  1. **Basic functionality**:
  ```bash
  # Download a small test playlist (3-5 songs)
  uv run yoto-card "https://music.youtube.com/playlist?list=TEST_PLAYLIST_ID" --output-dir test_downloads

  # Check files created
  ls -lh test_downloads/

  # Verify file naming format
  file test_downloads/*.mp3
  ```

  2. **Metadata embedding**:
  - Open downloaded files in a music player
  - Verify artist, title, album show correctly
  - Verify cover art displays

  3. **Tests pass**:
  ```bash
  uv run pytest -v
  uv run pytest --cov=src --cov-report=term
  ```

  4. **Code quality**:
  ```bash
  uv run ruff check src tests
  uv run mypy src
  ```

  5. **Error handling**:
  - Test with invalid URL (should show clear error)
  - Test with playlist containing unavailable videos (should skip and continue)

  ## Success Criteria

  - Downloads complete playlists successfully
  - Files are 320 kbps MP3s with full metadata
  - File names follow "Artist - Title.mp3" format
  - Progress bars display during downloads
  - Errors logged but don't stop entire download
  - All tests pass with >85% coverage
  - No type errors from mypy
  - Clean ruff linting
  - README has clear usage instructions
