"""python3 -m unittest discover -s .github/actions/release-notes"""
import unittest

from release_notes import TITLE, plain, release_note, render, summary

TERMINAL = {"cli": "⌨️ In Terminal"}


class Titles(unittest.TestCase):
    def test_kind_scope_and_text(self):
        title = TITLE.match("feat(Sessions)!: notes keep their time")
        self.assertEqual((title["kind"], title["scope"], title["text"]), ("feat", "Sessions", "notes keep their time"))

    def test_no_kind(self):
        self.assertIsNone(TITLE.match("Bump gradle from 9.7 to 9.8"))


class ReleaseNotes(unittest.TestCase):
    def test_first_paragraph_under_the_heading(self):
        body = "Why\n\n## Release note\n<!-- one line -->\n**Zoom** with the wheel.\n\nMore.\n\n## Testing\nx"
        self.assertEqual(release_note(body), "**Zoom** with the wheel.")

    def test_none_without_the_heading(self):
        self.assertIsNone(release_note("## Summary\nstuff"))

    def test_links_and_html_go(self):
        self.assertEqual(plain("See [the guide](https://x.y) <b>now</b> at https://www.x.y `<kbd>`"),
                         "See the guide now at x.y `<kbd>`")


class Render(unittest.TestCase):
    def test_headings_scope_sections_and_none(self):
        prs = [("1", "feat: map zoom", ""),
               ("2", "fix(cli): a flag", ""),
               ("3", "change(Sessions): faster search", ""),
               ("4", "fix: hidden", "## Release note\nnone"),
               ("5", "docs: guide", ""),
               ("6", "fix: a crash", "## Release note\n- one\n* two")]
        self.assertEqual(render(prs, TERMINAL), "\n".join([
            "This update has 1 new feature, 1 improvement and 2 bug fixes, plus more in Terminal.",
            "",
            "### ✨ New features", "- Map zoom",
            "",
            "### 🔧 Improvements", "- Faster search",
            "",
            "### 🐞 Bug fixes", "- one", "- two",
            "",
            "### ⌨️ In Terminal", "- A flag"]))

    def test_scope_without_a_section_is_only_a_label(self):
        self.assertIn("### 🐞 Bug fixes\n- A flag", render([("1", "fix(cli): a flag", "")], {}))

    def test_nothing_for_people(self):
        self.assertEqual(render([("1", "chore: tidy", "")], TERMINAL), "")


class Dependencies(unittest.TestCase):
    DEPS = "📦 Dependencies"

    def test_listed_last_and_counted(self):
        prs = [("1", "chore(deps): bump kotlin from 2.3 to 2.4", ""),
               ("2", "feat: map zoom", ""),
               ("3", "fix(cli): a flag", ""),
               ("4", "chore(deps): bump ktor from 3.5 to 3.6", "")]
        self.assertEqual(render(prs, TERMINAL, self.DEPS), "\n".join([
            "This update has 1 new feature and 2 dependency updates, plus more in Terminal.",
            "",
            "### ✨ New features", "- Map zoom",
            "",
            "### ⌨️ In Terminal", "- A flag",
            "",
            "### 📦 Dependencies", "- Bump kotlin from 2.3 to 2.4", "- Bump ktor from 3.5 to 3.6"]))

    def test_left_out_without_a_heading(self):
        self.assertEqual(render([("1", "chore(deps): bump kotlin from 2.3 to 2.4", "")], {}), "")

    def test_only_dependencies(self):
        self.assertEqual(render([("1", "chore(deps): bump kotlin from 2.3 to 2.4", "")], {}, self.DEPS),
                         "This update has 1 dependency update.\n\n### 📦 Dependencies\n- Bump kotlin from 2.3 to 2.4")

    def test_other_chores_and_none_stay_out(self):
        prs = [("1", "chore: tidy", ""), ("2", "chore(deps): bump ci tool", "## Release note\nnone"),
               ("3", "ci(deps): bump actions/checkout from 6 to 7", "")]
        self.assertEqual(render(prs, {}, self.DEPS), "")


class Summary(unittest.TestCase):
    def test_count_line(self):
        self.assertEqual(summary({"feat": 0, "change": 7, "fix": 1}), "This update has 7 improvements and 1 bug fix.")

    def test_only_a_scope_section(self):
        self.assertEqual(summary({"feat": 0, "change": 0, "fix": 0}, {"⌨️ In Terminal": 2}),
                         "This update has changes in Terminal.")


if __name__ == "__main__":
    unittest.main()
