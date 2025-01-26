from plex.cli import plex_cli


def run() -> None:
    """Runs the CLI on entrypoint script execution."""
    plex_cli()


if __name__ == "__main__":
    plex_cli()
