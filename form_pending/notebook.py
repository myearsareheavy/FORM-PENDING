"""Freeform player notebook. Never writes quests, tasks, or auto-notes."""

from __future__ import annotations


class Notebook:
    def __init__(self, max_chars: int = 8000):
        self.text = ""
        self.cursor = 0
        self.max_chars = max_chars
        self.scroll = 0

    def clear(self):
        self.text = ""
        self.cursor = 0
        self.scroll = 0

    def _clamp(self):
        self.cursor = max(0, min(self.cursor, len(self.text)))

    def insert(self, s: str):
        if not s:
            return
        s = "".join(ch for ch in s if ch == "\n" or (ch.isprintable() and ch != "\t"))
        s = s.replace("\t", "    ")
        room = self.max_chars - len(self.text)
        if room <= 0:
            return
        s = s[:room]
        self.text = self.text[: self.cursor] + s + self.text[self.cursor :]
        self.cursor += len(s)

    def backspace(self):
        if self.cursor <= 0:
            return
        self.text = self.text[: self.cursor - 1] + self.text[self.cursor :]
        self.cursor -= 1

    def delete(self):
        if self.cursor >= len(self.text):
            return
        self.text = self.text[: self.cursor] + self.text[self.cursor + 1 :]

    def newline(self):
        self.insert("\n")

    def move_left(self):
        if self.cursor > 0:
            self.cursor -= 1

    def move_right(self):
        if self.cursor < len(self.text):
            self.cursor += 1

    def move_home(self):
        line, _col, start, _end = self._cursor_line()
        self.cursor = start

    def move_end(self):
        _line, _col, _start, end = self._cursor_line()
        self.cursor = end

    def lines(self):
        if self.text == "":
            return [""]
        parts = self.text.split("\n")
        return parts

    def _cursor_line(self):
        """Return (line_index, column, line_start_index, line_end_index)."""
        i = 0
        for li, line in enumerate(self.lines()):
            end = i + len(line)
            if self.cursor <= end:
                return li, self.cursor - i, i, end
            i = end + 1
        lines = self.lines()
        last = lines[-1]
        start = len(self.text) - len(last)
        return len(lines) - 1, len(last), start, len(self.text)

    def move_up(self):
        li, col, _s, _e = self._cursor_line()
        if li == 0:
            self.cursor = 0
            return
        prev = self.lines()[li - 1]
        target_col = min(col, len(prev))
        # start index of previous line
        start = sum(len(l) + 1 for l in self.lines()[: li - 1])
        self.cursor = start + target_col

    def move_down(self):
        lines = self.lines()
        li, col, _s, _e = self._cursor_line()
        if li >= len(lines) - 1:
            self.cursor = len(self.text)
            return
        nxt = lines[li + 1]
        target_col = min(col, len(nxt))
        start = sum(len(l) + 1 for l in lines[: li + 1])
        self.cursor = start + target_col

    def ensure_scroll(self, visible: int):
        li, _c, _s, _e = self._cursor_line()
        if li < self.scroll:
            self.scroll = li
        if li >= self.scroll + visible:
            self.scroll = li - visible + 1
        max_scroll = max(0, len(self.lines()) - visible)
        self.scroll = max(0, min(self.scroll, max_scroll))
