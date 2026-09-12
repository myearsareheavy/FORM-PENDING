"""Notebook editing is freeform and never auto-filled from dialogue."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from form_pending.notebook import Notebook


class NotebookTests(unittest.TestCase):
    def test_insert_and_backspace(self):
        nb = Notebook()
        nb.insert("Janet floor 4")
        self.assertEqual(nb.text, "Janet floor 4")
        nb.backspace()
        self.assertEqual(nb.text, "Janet floor ")
        nb.newline()
        nb.insert("stamp")
        self.assertEqual(nb.text, "Janet floor \nstamp")

    def test_cursor_arrows(self):
        nb = Notebook()
        nb.insert("ab\ncd")
        nb.cursor = 1
        nb.move_down()
        self.assertEqual(nb.cursor, 4)  # column 1 of "cd"
        nb.move_home()
        self.assertEqual(nb.text[nb.cursor :], "cd")
        nb.move_end()
        self.assertEqual(nb.cursor, len(nb.text))

    def test_delete_and_bounds(self):
        nb = Notebook()
        nb.insert("xy")
        nb.cursor = 0
        nb.delete()
        self.assertEqual(nb.text, "y")
        nb.cursor = 0
        nb.move_left()
        self.assertEqual(nb.cursor, 0)

    def test_cap(self):
        nb = Notebook(max_chars=8)
        nb.insert("abcdefghijkl")
        self.assertEqual(len(nb.text), 8)


if __name__ == "__main__":
    unittest.main()
