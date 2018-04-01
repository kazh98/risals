#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json
from enum import Enum, unique
from .types import *
from typing import Optional, Tuple, Union, Iterator

__all__ = ['SJSyntaxError', 'SJStream']


class SJSyntaxError(ValueError):
    def __init__(self, code: str, pos: int, msg: str):
        ValueError.__init__(self, msg)
        self.lineno = code.count('\n', 0, pos) + 1
        self.offset = pos - code.rfind('\n', 0, pos)
        self.msg = msg


_WHITESPACE = re.compile(r'[ \t\r\n]*')
_LITERALEND = re.compile(r'[ \t\r\n)\]}:,]|\Z')
_STRING = re.compile(r'"([^"\\]|\\["\\/bfnrt]|\\u[0-9A-Fa-f]{4})*"', re.MULTILINE)
_NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?\Z')
_SYMBOL = re.compile(r'''(\+|-|\.\.\.|
[A-Za-z@!$%&*/\\<=>?^_~]
[A-Za-z@!$%&*/\\<=>?^_~0-9+-.]*)\Z''', re.VERBOSE)

class SJStream(Iterator[object]):
    def __init__(self, code: str, pos: int=0) -> None:
        self.code = code
        self.pos = pos
        return

    def peek(self) -> str:
        self.pos = _WHITESPACE.match(self.code, self.pos).end()
        if self.pos >= len(self.code):
            raise EOFError()
        return self.code[self.pos:self.pos + 1]

    def poll(self) -> str:
        rvalue = self.peek()
        self.pos += 1
        return rvalue
    
    def __iter__(self) -> Iterator[object]:
        return self

    def __next__(self) -> object:
        ch = self.peek()
        raise NotImplementedError()
    
    class SJScanStatus(object):
        def __init__(self):
            return


if __name__ == '__main__':
    import itertools
    DATA = """
+
-
...
'20
'null
'(a b c)
'[a, b, c]
'{"a": b, "c": null}
`(a b ,c)
`[a, b, ,c]
"""[1:]
