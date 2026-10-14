"""Catch accidental broken setup URLs and inaccurate private-clone instructions."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT_DOCS = (
    "README.md",
    "docs/PI_MODE.md",
    "docs/SERVER_MODE.md",
    "docs/AUTOSTART.md",
    "python-display/README.md",
)


class DocumentationTests(unittest.TestCase):
    def test_current_setup_guides_use_public_canonical_clone(self):
        for doc in CURRENT_DOCS:
            with self.subTest(doc=doc):
                text = (ROOT / doc).read_text(encoding="utf-8")
                self.assertNotIn("git@github.com:harrydavies1/pi-server-dashboard.git", text)
                self.assertNotIn("For a private repository", text)
                self.assertIn("https://github.com/harrydavies1/NodeWatch.git", text)

    def test_documented_relative_markdown_links_exist(self):
        for doc in CURRENT_DOCS:
            text = (ROOT / doc).read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if target.startswith(("https:", "http:", "#", "mailto:")):
                    continue
                destination = target.split("#", 1)[0]
                if destination:
                    with self.subTest(document=doc, link=target):
                        self.assertTrue((ROOT / doc).parent.joinpath(destination).exists())


if __name__ == "__main__":
    unittest.main()
