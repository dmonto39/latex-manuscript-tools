import unittest

from command_cleaner import remove_latex_command


class RemoveLatexCommandTests(unittest.TestCase):
    def test_removes_simple_wrapper_and_preserves_content(self):
        self.assertEqual(
            remove_latex_command(r"Before \addtext{new text} after", "addtext"),
            "Before new text after",
        )

    def test_supports_a_different_command_name(self):
        self.assertEqual(remove_latex_command(r"\todo{Check this}", "todo"), "Check this")

    def test_preserves_nested_latex_commands_and_braces(self):
        self.assertEqual(
            remove_latex_command(
                r"\addtext{The result is \textbf{important} for the analysis.}",
                "addtext",
            ),
            r"The result is \textbf{important} for the analysis.",
        )

    def test_removes_multiple_occurrences(self):
        self.assertEqual(
            remove_latex_command(r"\addtext{one} and \addtext{two}", "addtext"),
            "one and two",
        )

    def test_handles_whitespace_before_argument(self):
        self.assertEqual(remove_latex_command("\\addtext   {text}", "addtext"), "text")

    def test_does_not_match_a_longer_command_name(self):
        text = r"\addtextExtra{keep this} and \addtext{remove this}"
        self.assertEqual(
            remove_latex_command(text, "addtext"),
            r"\addtextExtra{keep this} and remove this",
        )

    def test_does_not_remove_command_without_braced_argument(self):
        text = r"\addtext text"
        self.assertEqual(remove_latex_command(text, "addtext"), text)

    def test_leaves_unclosed_argument_unchanged(self):
        text = r"Before \addtext{unclosed text"
        self.assertEqual(remove_latex_command(text, "addtext"), text)

    def test_preserves_escaped_braces_in_argument(self):
        self.assertEqual(
            remove_latex_command(r"\addtext{Set \{x\} to 1}", "addtext"),
            r"Set \{x\} to 1",
        )

    def test_does_not_remove_another_command(self):
        text = r"\todo{keep this}"
        self.assertEqual(remove_latex_command(text, "addtext"), text)

    def test_supports_unicode(self):
        self.assertEqual(
            remove_latex_command(r"\addtext{Medición y análisis}", "addtext"),
            "Medición y análisis",
        )

    def test_rejects_empty_command_name(self):
        with self.assertRaises(ValueError):
            remove_latex_command(r"\addtext{text}", "")

    def test_rejects_command_name_with_leading_backslash(self):
        with self.assertRaises(ValueError):
            remove_latex_command(r"\addtext{text}", r"\addtext")


if __name__ == "__main__":
    unittest.main()
