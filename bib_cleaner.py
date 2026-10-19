import re
import argparse
from pathlib import Path


def extract_citation_keys(tex_file):
    """
    Extract citation keys from \\cite{...} commands.

    Supports:
        \\cite{key}
        \\cite{key1,key2,key3}
        \\cite [optional arguments] {key}
        \\citep{key1,key2}
        \\citet{key1,key2}

    Returns:
        set[str]: Set of cited BibTeX keys.
    """

    tex_text = Path(tex_file).read_text(encoding="utf-8")

    # Match \cite, \citep, \citet, etc.
    # Also allows optional [...] arguments before {...}.
    pattern = r'\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)*\{([^}]*)\}'

    matches = re.findall(pattern, tex_text)

    cited_keys = set()

    for match in matches:
        # A single \cite command can contain several keys:
        # \cite{key1,key2,key3}
        keys = match.split(",")

        for key in keys:
            key = key.strip()
            if key:
                cited_keys.add(key)

    return cited_keys


def extract_bib_entries(bib_file):
    """
    Extract complete BibTeX entries from a .bib file.

    Returns:
        list[tuple[str, str]]:
            [(bibtex_key, complete_entry), ...]
    """

    bib_text = Path(bib_file).read_text(encoding="utf-8")

    entries = []

    # Locate the beginning of BibTeX entries such as:
    # @article{key,
    # @inproceedings{key,
    # @book{key,
    entry_start_pattern = re.compile(r'@[a-zA-Z]+\s*\{')

    for match in entry_start_pattern.finditer(bib_text):
        start = match.start()

        # Find the opening brace
        open_brace = bib_text.find("{", match.start(), match.end())

        if open_brace == -1:
            continue

        # Extract the BibTeX key.
        comma = bib_text.find(",", open_brace)

        if comma == -1:
            continue

        key = bib_text[open_brace + 1:comma].strip()

        # Find the matching closing brace.
        depth = 0
        in_quotes = False
        escaped = False
        end = None

        for i in range(open_brace, len(bib_text)):
            char = bib_text[i]

            if escaped:
                escaped = False
                continue

            if char == "\\":
                escaped = True
                continue

            if char == '"':
                in_quotes = not in_quotes
                continue

            if not in_quotes:
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1

                    if depth == 0:
                        end = i + 1
                        break

        if end is None:
            raise ValueError(f"Could not find the end of BibTeX entry: {key}")

        entry = bib_text[start:end].strip()

        entries.append((key, entry))

    return entries


def create_clean_bib(tex_file, bib_file, output_bib_file):
    """
    Create a new .bib file containing only references cited in the .tex file.
    """

    cited_keys = extract_citation_keys(tex_file)
    bib_entries = extract_bib_entries(bib_file)

    print(f"Found {len(cited_keys)} cited references in the .tex file.")

    kept_entries = []
    removed_entries = []

    for key, entry in bib_entries:
        if key in cited_keys:
            kept_entries.append(entry)
        else:
            removed_entries.append(key)

    # Write a completely new file.
    # The original .tex and .bib files are never opened in write mode.
    with open(output_bib_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(kept_entries))
        f.write("\n")

    print(f"Original BibTeX entries: {len(bib_entries)}")
    print(f"Kept entries:             {len(kept_entries)}")
    print(f"Removed entries:          {len(removed_entries)}")
    print(f"New bibliography:         {output_bib_file}")

    if removed_entries:
        print("\nRemoved references:")
        for key in removed_entries:
            print(f"  - {key}")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Remove uncited references from a BibTeX file."
    )
    parser.add_argument(
        "tex_file",
        help="Path to the LaTeX .tex file."
    )
    parser.add_argument(
        "bib_file",
        help="Path to the original .bib file."
    )
    parser.add_argument(
        "-o", "--output",
        default="references_cleaned.bib",
        dest="output_bib_file",
        help="Output .bib file (default: references_cleaned.bib)."
    )

    return parser.parse_args()


def main():
    # This wraps the original command-line entry-point logic so the script
    # can also be called from the merged command-line dispatcher.
    args = parse_arguments()
    tex_filename = Path(args.tex_file)
    bib_filename = Path(args.bib_file)
    output_bib_filename = Path(args.output_bib_file)

    if not bib_filename.is_absolute():
        tex_dir = tex_filename.parent
        bib_filename = tex_dir.joinpath(bib_filename)

    if not output_bib_filename.is_absolute():
        tex_dir = tex_filename.parent
        output_bib_filename = tex_dir.joinpath(output_bib_filename)

    create_clean_bib(
        tex_file=tex_filename,
        bib_file=bib_filename,
        output_bib_file=output_bib_filename
    )

if __name__ == "__main__":
    main()
