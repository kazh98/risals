#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
### sjson: Symbolic JSON
###  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
###############################################################################
import re, json
from typing import Optional, Tuple


class SJSONSyntaxError(ValueError):
    def __init__(self, code: str, pos: int, msg: str):
        ValueError.__init__(self, msg)
        self.lineno = code.count('\n', 0, pos) + 1
        self.offset = pos - code.rfind('\n', 0, pos)
        self.msg = msg


class Cell(object):
    def __init__(self, car: object, cdr: object):
        self.car = car
        self.cdr = cdr

        
class Symbol(object):
    def __init__(self, raw: str, xid: int):
        self.raw = raw
        self.xid = xid

__symbol_table = {}
__symbol_count = 0
def gensym(raw: Optional[str]=None) -> Symbol:
    global __symbol_table, __symbol_count
    if raw is None:
        __symbol_count += 1
        return Symbol("<SYMBOL:%d>" % __symbol_count, __symbol_count)
    if raw in __symbol_table:
        return __symbol_table[raw]
    __symbol_count += 1
    rvalue = Symbol(raw, __symbol_count)
    __symbol_table[raw] = rvalue
    return rvalue


def encode(obj: object) -> str:
    sb = []
    def lp(o: object) -> None:
        nonlocal sb
        if isinstance(o, Cell):
            sb.append('(')
            lp(o.car)
            o = o.cdr
            while isinstance(o, Cell):
                sb.append(' ')
                lp(o.car)
                o = o.cdr
            if o is not None:
                sb.append(' . ')
                lp(o)
            sb.append(')')
            return
        if isinstance(o, Symbol):
            sb.append(o.raw)
            return
        if isinstance(o, str):
            sb += ['\"', json.dumps(o), '\"']
            return
        raise ValueError('given object is not encodable')
    lp(obj)
    return ''.join(sb)


WHITESPACE = re.compile(r'[ \t\r\n]*')
STRSPCHR = re.compile(r'["\\]', re.MULTILINE)
STRUCODE = re.compile(r'[0-9A-Fa-f]{4}')
NUMBER = re.compile(r'-?(0|[1-9][0-9]*)(\.[0-9])?([eE][+-]?[0-9]*)?')
SYMBOL = re.compile(r'''
[A-Za-z:+\-*/@!?]
[A-Za-z:+\-*/@!?.0-9]*'''[1:], re.VERBOSE)

def decode(code: str, pos: int=0) -> Tuple[object, int]:
    def peek() -> str:
        nonlocal pos
        pos = WHITESPACE.match(code, pos).end()
        if pos >= len(code):
            raise EOFError()
        return code[pos:pos + 1]
    
    def poll() -> str:
        nonlocal pos
        rval = peek()
        pos += 1
        return rval

    def nextList() -> Cell:
        ch = poll()
        if ch != '(':
            raise SJSONSyntaxError(code, pos, 'internal error')
        lis = []
        while True:
            ch = peek()
            if ch == '.':
                poll()
                if len(lis) <= 0:
                    raise SJSONSyntaxError(code, pos, 'lack of dotted prefix')
                try:
                    rval = next()
                    if poll() != ')': raise EOFError()
                except EOFError:
                    raise SJSONSyntaxError(code, pos, 'surplus of dotted suffix')
                for item in reversed(lis):
                    rval = Cell(item, rval)
                return rval
            if ch == ')':
                poll()
                rval = None
                for item in reversed(lis):
                    rval = Cell(item, rval)
                return rval
            try:
                lis.append(next())
            except EOFError:
                raise SJSONSyntaxError(code, pos, 'unclosed list')

    def nextSymbol() -> Symbol:
        nonlocal pos
        peek()
        m = SYMBOL.match(code, pos)
        if not m:
            SJSONSyntaxError('internal error')
        pos = m.end()
        return gensym(m.group())

    def nextString() -> str:
        nonlocal pos
        ch = poll()
        if ch != '\"':
            raise SJSONSyntaxError(code, pos, 'internal error')
        sb = []
        while True:
            m = STRSPCHR.search(code, pos)
            if not m:
                raise SJSONSyntaxError(code, pos, 'unclosed string')
            sb.append(code[pos:m.start()])
            pos = m.start()
            ch = poll()
            if ch == '\"':
                return ''.join(sb)
            if ch == '\\':
                ch = poll()
                if ch in '\"\\/':
                    sb.append(ch)
                elif ch == 'b':
                    sb.append('\b')
                elif ch == 'f':
                    sb.append('\f')
                elif ch == 'n':
                    sb.append('\n')
                elif ch == 'r':
                    sb.append('\r')
                elif ch == 't':
                    sb.append('\t')
                elif ch == 'u':
                    hd = STRUCODE.match(code, pos)
                    if not hd:
                        raise SJSONSyntaxError(code, pos, '\\u requires following 4 hexadecimal digits')
                    pos = hd.end()
                    hd = hd.group()
                    sb.append(chr(int(hd, 16)))
                else:
                    raise SJSONSyntaxError(code, pos, 'invalid escape sequence')
                continue
            raise Exception(code, pos, 'infinite loop has been detected')
    
    def next() -> object:
        ch = peek()
        if ch == '(':
            return nextList()
        if SYMBOL.match(ch):
            return nextSymbol()
        if ch == '\"':
            return nextString()
        raise SJSONSyntaxError(code, pos, 'invalid syntax')

    rval = next()
    return rval, pos


if __name__ == '__main__':
    import itertools
    DATA = """
(list and symbol)
(dotted . pair)
"SIMPLE STRING"
"COMPLEX
MULTI\\tLINED\\n\\"STRING\\u0022"
1234567890
-9876543210
12345.6789
-9.876543e21
-9.876543E+21
9.8765432e-1
true
false
null
"""[1:]
    pos = 0
    for n in itertools.count(1):
        try:
            rval, pos = decode(DATA, pos)
            print("%d: %s" % (n, encode(rval)))
        except EOFError:
            break
