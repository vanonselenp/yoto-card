"""Command-line interface for yoto-card."""

import sys
from pathlib import Path

import click

from yoto_card.downloader import PlaylistDownloader
from yoto_card.exceptions import YotoCardError
from yoto_card.utils import validate_youtube_url


@click.command()
@click.argument("playlist_url")
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=Path("./downloads"),
    help="Output directory for downloaded files.",
)
@click.option(
    "-q",
    "--quality",
    type=click.Choice(["128", "192", "256", "320"], case_sensitive=False),
    default="320",
    help="Audio quality in kbps.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
)
@click.option(
    "--continue-on-error",
    is_flag=True,
    default=True,
    help="Continue downloading if a song fails.",
)
def main(
    playlist_url: str,
    output_dir: Path,
    quality: str,
    verbose: bool,
    continue_on_error: bool,
) -> None:
    """Download YouTube Music playlists as high-quality MP3 files.

    PLAYLIST_URL: URL of a YouTube Music playlist.

    Examples:
        yoto-card "https://music.youtube.com/playlist?list=PLxxxxx"
        yoto-card "https://www.youtube.com/playlist?list=PLxxxxx" --output-dir ~/Music
        yoto-card "https://music.youtube.com/playlist?list=PLxxxxx" --quality 192
    """
    try:
        # Validate URL
        if not validate_youtube_url(playlist_url):
            click.secho(
                f"Error: Invalid YouTube URL: {playlist_url}",
                fg="red",
                err=True,
            )
            sys.exit(1)

        quality_int = int(quality)

        # Create downloader
        downloader = PlaylistDownloader(
            output_dir=output_dir,
            quality=quality_int,
            continue_on_error=continue_on_error,
            verbose=verbose,
        )

        click.echo(f"Starting download from: {playlist_url}")
        click.echo(f"Output directory: {output_dir.resolve()}")
        click.echo(f"Quality: {quality} kbps")
        click.echo()

        # Download playlist
        result = downloader.download_playlist(playlist_url)

        # Print results
        downloader.print_results(result)

        # Exit with appropriate code
        if result.failed_downloads > 0 and not continue_on_error:
            sys.exit(1)

        click.echo()
        msg = (
            f"Download complete! {result.successful_downloads} of {result.total_songs} "
            "songs downloaded."
        )
        click.secho(msg, fg="green")

    except YotoCardError as e:
        click.secho(f"Error: {e}", fg="red", err=True)
        sys.exit(1)
    except Exception as e:
        click.secho(f"Unexpected error: {e}", fg="red", err=True)
        if verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
