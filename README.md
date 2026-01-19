# yoto-card

Download YouTube Music playlists as high-quality MP3 files with embedded metadata.

## Features

- **Download complete playlists** from YouTube Music or YouTube
- **320 kbps MP3 quality** (also supports 128, 192, 256 kbps)
- **Embedded metadata** including:
  - Title and artist name
  - Album information (when available)
  - Cover art
  - Track numbers
- **Filename format**: `Artist - Title.mp3`
- **Error resilience**: Continue downloading if a song fails
- **Progress indication**: Visual progress bars during downloads
- **Cross-platform**: Works on macOS, Linux, and Windows

## Prerequisites

- **Python 3.10+**: Required for the application
- **FFmpeg**: Required by yt-dlp for audio conversion
  - macOS: `brew install ffmpeg`
  - Ubuntu/Debian: `sudo apt-get install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/yoto-card.git
cd yoto-card

# Install with uv
uv sync
```

### Using pip

```bash
pip install -e .
```

## Usage

### Basic Usage

Download a playlist to the default `./downloads` directory:

```bash
uv run yoto-card "https://music.youtube.com/playlist?list=PLxxxxxxxxxxxxx"
```

### Advanced Options

```bash
# Specify output directory
uv run yoto-card "PLAYLIST_URL" --output-dir ~/Music/MyPlaylist

# Set audio quality (default: 320)
uv run yoto-card "PLAYLIST_URL" --quality 192

# Enable verbose output
uv run yoto-card "PLAYLIST_URL" --verbose

# Continue on errors (default: true)
uv run yoto-card "PLAYLIST_URL" --continue-on-error
```

### Command Reference

```
Usage: yoto-card [OPTIONS] PLAYLIST_URL

Options:
  -o, --output-dir DIRECTORY      Output directory for downloaded files
                                  (default: ./downloads)
  -q, --quality [128|192|256|320] Audio quality in kbps (default: 320)
  -v, --verbose                   Enable verbose output
  --continue-on-error             Continue if a song fails (default: true)
  --help                          Show help message
```

## Examples

### Download to custom location

```bash
uv run yoto-card "https://music.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  --output-dir ~/Music/Favorites
```

### Download with lower quality to save space

```bash
uv run yoto-card "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  --quality 192
```

### Download with verbose logging

```bash
uv run yoto-card "https://music.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" \
  --verbose
```

## Supported URL Formats

The application supports multiple YouTube URL formats:

- YouTube Music playlists: `https://music.youtube.com/playlist?list=PLxxxxx`
- YouTube playlists: `https://www.youtube.com/playlist?list=PLxxxxx`
- YouTube videos: `https://www.youtube.com/watch?v=xxxxx`
- Shortened URLs: `https://youtu.be/xxxxx`

## Troubleshooting

### FFmpeg Not Found

If you get an error about FFmpeg not being found:

1. **macOS**: `brew install ffmpeg`
2. **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
3. **Windows**: Install from [ffmpeg.org](https://ffmpeg.org/download.html)

Verify installation:
```bash
ffmpeg -version
```

### Network Issues

If downloads fail due to network issues:

- Check your internet connection
- Try again with `--verbose` to see detailed error messages
- Some playlists may have region restrictions or age restrictions

### Files Not Being Downloaded

- Verify the playlist URL is correct
- Check that the playlist is public
- Try with a different playlist URL to verify the tool is working

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_cli.py

# Run with coverage
uv run pytest --cov=src/yoto_card --cov-report=html
```

### Code Quality

```bash
# Format code
uv run ruff format src tests

# Lint code
uv run ruff check src tests --fix

# Type checking
uv run mypy src
```

## Project Structure

```
yoto-card/
├── src/yoto_card/          # Main package
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # Entry point
│   ├── cli.py               # Click CLI interface
│   ├── downloader.py        # Core download logic
│   ├── metadata.py          # Metadata extraction and embedding
│   ├── config.py            # Configuration constants
│   ├── exceptions.py        # Custom exceptions
│   └── utils.py             # Utility functions
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── pyproject.toml           # Project configuration
├── README.md                # This file
└── LICENSE                  # MIT License
```

## API Usage

You can also use yoto-card as a Python library:

```python
from pathlib import Path
from yoto_card import PlaylistDownloader

# Create downloader
downloader = PlaylistDownloader(
    output_dir=Path("./downloads"),
    quality=320,
    continue_on_error=True,
    verbose=False
)

# Download playlist
result = downloader.download_playlist(
    "https://music.youtube.com/playlist?list=PLxxxxx"
)

# Print results
downloader.print_results(result)

# Access download statistics
print(f"Downloaded: {result.successful_downloads}/{result.total_songs}")
print(f"Success rate: {result.success_rate:.1f}%")
```

## Dependencies

### Production

- **yt-dlp** (≥2024.1.0): YouTube downloader
- **mutagen** (≥1.47.0): MP3 metadata embedding
- **requests** (≥2.31.0): HTTP requests
- **rich** (≥13.0.0): Progress bars and formatting
- **click** (≥8.1.0): CLI framework

### Development

- **pytest** (≥7.4.0): Testing framework
- **pytest-cov** (≥4.1.0): Coverage reporting
- **pytest-mock** (≥3.12.0): Mocking utilities
- **ruff** (≥0.1.0): Code formatter and linter
- **mypy** (≥1.7.0): Type checking

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and personal use only. Respect copyright and the terms of service of YouTube and YouTube Music. The authors are not responsible for misuse of this software.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
