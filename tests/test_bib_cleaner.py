import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from bib_cleaner import (
    create_clean_bib,
    extract_bib_entries,
    extract_citation_keys,
)


class ExtractCitationKeysTests(unittest.TestCase):
    def test_extracts_single_and_multiple_citation_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tex = Path(temp_dir) / "article.tex"
            tex.write_text(
                r"\cite{smith2020} and \cite{jones2021,lee2022}",
                encoding="utf-8",
            )
            self.assertEqual(
                extract_citation_keys(tex),
                {"smith2020", "jones2021", "lee2022"},
            )

    def test_extracts_citet_citep_and_optional_arguments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tex = Path(temp_dir) / "article.tex"
            tex.write_text(
                r"\citep[see][p. 4]{alpha,beta} \citet{gamma} \cite*{delta}",
                encoding="utf-8",
            )
            self.assertEqual(
                extract_citation_keys(tex), {"alpha", "beta", "gamma", "delta"}
            )

    def test_ignores_empty_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tex = Path(temp_dir) / "article.tex"
            tex.write_text(r"\cite{alpha, ,beta}", encoding="utf-8")
            self.assertEqual(extract_citation_keys(tex), {"alpha", "beta"})

    def test_returns_empty_set_when_there_are_no_citations(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            tex = Path(temp_dir) / "article.tex"
            tex.write_text("No citations here.", encoding="utf-8")
            self.assertEqual(extract_citation_keys(tex), set())


class ExtractBibEntriesTests(unittest.TestCase):
    def test_extracts_entries_and_keys(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bib = Path(temp_dir) / "references.bib"
            bib.write_text(
                "@article{smith2020,\n  title = {A title},\n}\n\n"
                "@book{jones2021,\n  title = {Another title},\n}\n",
                encoding="utf-8",
            )
            entries = extract_bib_entries(bib)
            self.assertEqual([key for key, _ in entries], ["smith2020", "jones2021"])
            self.assertIn("title = {A title}", entries[0][1])
            self.assertIn("title = {Another title}", entries[1][1])

    def test_handles_nested_braces_and_braces_inside_quotes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bib = Path(temp_dir) / "references.bib"
            entry = (
                '@article{nested,\n'
                '  title = {A {nested} title},\n'
                '  note = "quoted } brace",\n'
                '}\n'
            )
            bib.write_text(entry, encoding="utf-8")
            entries = extract_bib_entries(bib)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0][0], "nested")
            self.assertIn('note = "quoted } brace"', entries[0][1])

    def test_raises_for_unclosed_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bib = Path(temp_dir) / "references.bib"
            bib.write_text("@article{broken, title = {Unclosed", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Could not find the end"):
                extract_bib_entries(bib)


class CreateCleanBibTests(unittest.TestCase):
    def test_keeps_cited_entries_and_reports_removed_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            tex = base / "article.tex"
            bib = base / "references.bib"
            output = base / "cleaned.bib"
            tex.write_text(r"\cite{keep_me}", encoding="utf-8")
            bib.write_text(
                "@article{keep_me, title = {Keep this}}\n\n"
                "@article{remove_me, title = {Remove this}}\n",
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                create_clean_bib(tex, bib, output)

            output_text = output.read_text(encoding="utf-8")
            self.assertIn("keep_me", output_text)
            self.assertNotIn("remove_me", output_text)
            self.assertIn("Removed entries:          1", stdout.getvalue())
            # Source files remain unchanged.
            self.assertIn("remove_me", bib.read_text(encoding="utf-8"))
            self.assertEqual(tex.read_text(encoding="utf-8"), r"\cite{keep_me}")

    def test_writes_empty_bibliography_when_no_entries_are_cited(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            tex = base / "article.tex"
            bib = base / "references.bib"
            output = base / "cleaned.bib"
            tex.write_text("No citations.", encoding="utf-8")
            bib.write_text("@article{unused, title = {Unused}}\n", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                create_clean_bib(tex, bib, output)

            self.assertEqual(output.read_text(encoding="utf-8"), "\n")


if __name__ == "__main__":
    unittest.main()
