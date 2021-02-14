# -*- coding: utf-8 -*-
import ast
import inspect
import io
import keyword
import os
import re
import sys
import tokenize
import traceback

from yummy import terminal


class Highlighter(object):

    TOKEN_DEFAULT = "token_default"
    TOKEN_COMMENT = "token_comment"
    TOKEN_STRING = "token_string"
    TOKEN_NUMBER = "token_number"
    TOKEN_KEYWORD = "token_keyword"
    TOKEN_BUILTIN = "token_builtin"
    TOKEN_CLASS_NAME = "token_class_name"
    TOKEN_FUNCTION_NAME = "token_function_name"
    TOKEN_OP = "token_op"
    LINE_MARKER = "line_marker"
    LINE_NUMBER = "line_number"

    DEFAULT_THEME = {
        TOKEN_STRING: 'light_orange',
        TOKEN_NUMBER: 'light_green',
        TOKEN_COMMENT: 'dark_green',
        TOKEN_KEYWORD: 'pink',
        TOKEN_BUILTIN: 'red',
        TOKEN_DEFAULT: 'white',
        TOKEN_CLASS_NAME: 'purple',
        TOKEN_FUNCTION_NAME: 'purple',
        TOKEN_OP: "white",
        LINE_MARKER: 'red',
        LINE_NUMBER: 'dark_purple'
    }

    KEYWORDS = set(keyword.kwlist)
    BUILTINS = set(
        __builtins__.keys() if type(__builtins__) is dict else dir(__builtins__)
    )
    BUILTINS.add("@")

    def __init__(self):
        self._theme = self.DEFAULT_THEME.copy()

    def code_snippet(self, source, line, lines_before=2, lines_after=2):
        token_lines = self.highlighted_lines(source)
        token_lines = self.line_numbers(token_lines, line)

        offset = line - lines_before - 1
        offset = max(offset, 0)
        length = lines_after + lines_before + 1
        token_lines = token_lines[offset : offset + length]

        return token_lines

    def highlighted_lines(self, source):
        source = source.replace("\r\n", "\n").replace("\r", "\n")

        a = self.split_to_lines(source)
        return a

    def split_to_lines(self, source):
        lines = []
        current_line = 1
        current_col = 0
        buffer = ""
        current_type = None
        source_io = io.StringIO(unicode(source, 'utf8'))

        def readline():
            return source_io.readline().encode('utf8')

        tokens = tokenize.generate_tokens(readline)
        line = ""
        last = ""
        for token_info in tokens:
            token_type, token_string, start, end, xline = token_info
            lineno = start[0]
            if lineno == 0:
                # Encoding line
                continue

            if token_type == tokenize.ENDMARKER:
                # End of source
                lines.append(line)
                break

            if lineno > current_line:
                diff = lineno - current_line
                if diff > 1:
                    lines += [""] * (diff - 1)

                line += terminal.colorize(buffer.rstrip('\n'), self._theme[current_type])

                # New line
                lines.append(line)
                line = ""
                current_line = lineno
                current_col = 0
                buffer = ""

            if token_string in self.KEYWORDS:
                new_type = self.TOKEN_KEYWORD
            elif token_string in self.BUILTINS or token_string == "self":
                new_type = self.TOKEN_BUILTIN
            elif token_type == tokenize.STRING:
                new_type = self.TOKEN_STRING
            elif token_type == tokenize.NUMBER:
                new_type = self.TOKEN_NUMBER
            elif token_type == tokenize.COMMENT:
                new_type = self.TOKEN_COMMENT
            elif token_type == tokenize.OP:
                new_type = self.TOKEN_OP
            elif token_type == tokenize.NEWLINE:
                continue
            elif token_type == tokenize.NAME and last == "class":
                new_type = self.TOKEN_CLASS_NAME
            elif token_type == tokenize.NAME and last == "def":
                new_type = self.TOKEN_FUNCTION_NAME
            else:
                new_type = self.TOKEN_DEFAULT

            if current_type is None:
                current_type = new_type

            if start[1] > current_col:
                buffer += xline[current_col : start[1]]

            if current_type != new_type:
                line += terminal.colorize(buffer, self._theme[current_type])
                buffer = ""
                current_type = new_type

            if lineno < end[0]:
                # The token spans multiple lines
                lines.append(line)
                token_lines = token_string.split("\n")
                for l in token_lines[1:-1]:
                    lines.append(terminal.colorize(l, self._theme[current_type]))

                current_line = end[0]
                buffer = token_lines[-1][: end[1]]
                line = ""
                continue

            buffer += token_string
            current_col = end[1]
            current_line = lineno
            if not token_string.isspace():
                last = token_string

        return lines

    def line_numbers(self, lines, mark_line=None):
        max_line_length = len(str(len(lines)))

        snippet_lines = []
        marker = terminal.colorize("  → ", self._theme[self.LINE_MARKER])
        no_marker = "    "
        for i, line in enumerate(lines):
            if mark_line is not None:
                if mark_line == i + 1:
                    snippet = marker
                else:
                    snippet = no_marker

            line_number_theme = self.LINE_MARKER if (mark_line == i + 1) else self.LINE_NUMBER
            line_number = terminal.colorize(
                "{:>{}}".format(i + 1, max_line_length),
                self._theme[line_number_theme]
            )
            snippet += "{}{} {}".format(
                line_number,
                terminal.colorize('│', self._theme[self.LINE_NUMBER]),
                line,
            )
            snippet_lines.append(snippet)

        return snippet_lines
