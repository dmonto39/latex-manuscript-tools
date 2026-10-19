# LaTeX Manuscript Tools

A collection of small, dependency-free Python utilities for cleaning LaTeX manuscripts and their bibliography files. Both utilities read their source files and write results to output files.

## Requirements

- Python 3.9 or later
- No third-party packages

## Utilities

### 1. Remove a LaTeX command wrapper

Removes the wrapper of a specified one-argument LaTeX command while preserving its contents. Useful for removing review markup such as `\addtext{...}` or `\todo{...}`.

Using the combined command-line entry point:

```bash
python main.py command manuscript.tex addtext
```

By default, this creates `manuscript_cleaned.tex` beside the input file. To use another command or output filename:

```bash
python main.py command manuscript.tex todo
python main.py command manuscript.tex addtext --output manuscript_final.tex
```

You can also run this utility directly:

```bash
python command_cleaner.py manuscript.tex addtext
```

The original `.tex` file is opened in read-only mode. The utility refuses to overwrite an existing output file. It removes only the selected wrapper; it does not remove its `\newcommand` definition from the preamble.

Example input:

```latex
Original text. \addtext{This paragraph was added during review.}
The result is \addtext{\textbf{important}} for the analysis.
```

Example output:

```latex
Original text. This paragraph was added during review.
The result is \textbf{important} for the analysis.
```

### 2. Remove uncited BibTeX entries

Keeps entries in a `.bib` file whose citation keys occur in LaTeX citation commands in the `.tex` file. It recognizes commands such as `\cite{...}`, `\citep{...}`, and `\citet{...}`, including multiple comma-separated keys and optional bracket arguments.

Using the combined command-line entry point:

```bash
python main.py bib article.tex references.bib
```

By default, the cleaner creates `references_cleaned.bib` in the same directory as the `.tex` file. To specify a different output file:

```bash
python main.py bib article.tex references.bib --output cleaned.bib
```

You can also run this utility directly:

```bash
python bib_cleaner.py article.tex references.bib --output cleaned.bib
```

The `.tex` and input `.bib` files are read as inputs. The output path is opened for writing and will be overwritten if it already exists, so choose a separate output filename and do not point it at your original `.bib` file. Inspect the generated bibliography before using it, especially if your project uses citation commands or bibliography dependencies not covered by the cleaner's matching pattern.

## Tests

The test suite uses Python's built-in `unittest` framework. From the project root, run:

```bash
python -m unittest discover -s tests -v
```

The tests cover command-wrapper removal, citation-key extraction, BibTeX entry extraction, malformed entries, and writing a cleaned bibliography while preserving the input files.

## Scope and limitations

These are lightweight text-processing utilities, not complete TeX or BibTeX parsers. The command cleaner does not distinguish executable text from LaTeX comments or verbatim environments. The bibliography cleaner uses regular expressions to identify citation commands and may not recognize every citation package or custom citation macro. Review the output before using it in a publication-ready manuscript.
