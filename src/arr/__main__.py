"""Allow `python -m arr` as a shortcut for the CLI."""

from arr.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
