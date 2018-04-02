#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json
from enum import Enum, unique
from .types import *
from typing import Iterator
__all__ = ['SJSyntaxError', 'SJStream']


class SJSyntaxError(ValueError):
    def __init__(self, code: str, pos: int, msg: str):
        ValueError.__init__(self, msg)
        self.lineno = code.count('\n', 0, pos) + 1
        self.offset = pos - code.rfind('\n', 0, pos)
        self.msg = msg


_WHITESPACE = re.compile(r'[ \t\r\n]*')
_TOKEN = re.compile(r'[^()[\]{}\",\'`; \t\r\n]+')
_STRING = re.compile(r'"([^"\\]|\\["\\/bfnrt]|\\u[0-9A-Fa-f]{4})*"', re.MULTILINE)
_NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?\Z')


@unique
class _ScanStatus(Enum):
    ROOT = 0
    LIST = 1
    OBJECT = 2
    ARRAY = 3


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
        raise NotImplementedError()
