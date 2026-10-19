"""Remove a one-argument wrapper command from a LaTeX source file."""

from __future__ import annotations

import argparse
from pathlib import Path


def remove_latex_command(text: str, command_name: str) -> str:
    r"""Remove occurrences of a one-argument LaTeX command, preserving contents.

    ``command_name`` is given without the leading backslash.

    Examples:
        >>> remove_latex_command(r"Before \addtext{new text} after", "addtext")
        'Before new text after'
        >>> remove_latex_command(r"\todo{Use \textbf{bold} text}", "todo")
        'Use \\textbf{bold} text'

    This is a lightweight text parser, not a complete TeX parser. It tracks
    nested braces and escaped characters inside the wrapper argument, but it
    does not ignore comments or verbatim environments.
    """
    if not command_name or command_name.startswith("\\"):
        raise ValueError("command_name must be a non-empty name without a leading backslash")

    command = "\\" + command_name
    result: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        if text.startswith(command, i):
            end_command = i + len(command)

            # Do not match a prefix of a longer control-word name.
            if end_command == n or not (
                text[end_command].isalnum() or text[end_command] == "@"
            ):
                # TeX ignores whitespace after a control word before its argument.
                j = end_command
                while j < n and text[j].isspace():
                    j += 1

                if j < n and text[j] == "{":
                    depth = 1
                    k = j + 1

                    while k < n and depth > 0:
                        # Skip escaped characters, including \{ and \}.
                        if text[k] == "\\":
                            k += 2
                            continue

                        if text[k] == "{":
                            depth += 1
                        elif text[k] == "}":
                            depth -= 1
                        k += 1

                    if depth == 0:
                        result.append(text[j + 1 : k - 1])
                        i = k
                        continue

        result.append(text[i])
        i += 1

    return "".join(result)


def clean_tex_file(
    input_path: Path,
    output_path: Path,
    command_name: str,
) -> None:
    """Read a .tex file without modifying it and create a new cleaned file.

    The output path must not already exist. This prevents accidental
    overwriting and also ensures the input file is never written to.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output files must be different.")

    with input_path.open("r", encoding="utf-8") as file:
        original_text = file.read()

    cleaned_text = remove_latex_command(original_text, command_name)

    # Exclusive creation ('x') prevents overwriting an existing output file.
    with output_path.open("x", encoding="utf-8") as file:
        file.write(cleaned_text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Remove a one-argument LaTeX wrapper command while preserving its contents."
        )
    )
    parser.add_argument("input", help="Path to the input .tex file")
    parser.add_argument(
        "command",
        help="LaTeX command name without the backslash, e.g. addtext or todo",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output .tex file (default: <input>_cleaned.tex)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = (
        Path(args.output)
        if args.output
        else input_path.with_name(f"{input_path.stem}_cleaned{input_path.suffix}")
    )

    if not input_path.is_file():
        parser.error(f"Input file does not exist or is not a file: {input_path}")

    try:
        clean_tex_file(input_path, output_path, args.command)
    except (FileExistsError, ValueError) as error:
        parser.error(str(error))
    except OSError as error:
        parser.error(f"Could not process file: {error}")

    print(f"Cleaned LaTeX file saved to: {output_path}")


if __name__ == "__main__":
    main()
