"""Command-line entry point for the LaTeX manuscript utilities."""

import sys

import bib_cleaner
import command_cleaner


def print_usage() -> None:
    print(
        "Usage:\n"
        "  python main.py command <input.tex> <command-name> [--output OUTPUT.tex]\n"
        "  python main.py bib <input.tex> <input.bib> [--output OUTPUT.bib]\n\n"
        "Commands:\n"
        "  command   Remove a one-argument LaTeX wrapper command.\n"
        "  bib       Remove bibliography entries not cited in the .tex file.\n"
        "\nUse 'python main.py command --help' or 'python main.py bib --help' "
        "for command-specific options."
    )


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print_usage()
        return

    tool = sys.argv[1]
    remaining_args = sys.argv[2:]
    # Preserve each utility's argument parser and CLI behavior.
    sys.argv = [sys.argv[0], *remaining_args]

    if tool == "command":
        command_cleaner.main()
    elif tool == "bib":
        bib_cleaner.main()
    else:
        print(f"Unknown command: {tool}\n")
        print_usage()
        raise SystemExit(2)


if __name__ == "__main__":
    main()
