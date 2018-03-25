#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
### sjson: Symbolic JSON
###  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
###############################################################################
import re, json
from typing import Optional, Tuple, Union


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
        if o is None:
            sb.append('null')
            return
        if o is True:
            sb.append('true')
            return
        if o is False:
            sb.append('false')
            return
        if isinstance(o, Symbol):
            sb.append(o.raw)
            return
        if isinstance(o, str):
            sb.append(json.dumps(o))
            return
        if isinstance(o, int) or isinstance(o, float):
            sb.append(repr(o))
            return
        raise ValueError('given object is not encodable')
    lp(obj)
    return ''.join(sb)


WHITESPACE = re.compile(r'[ \t\r\n]*')
STRING = re.compile(r'"([^"\\]|\\["\\/bfnrt]|\\u[0-9A-Fa-f]{4})*"', re.MULTILINE)
NUMBER = re.compile(r'-?(?:0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?')
SYMBOL = re.compile(r'''
[A-Za-z@!$%&*/:<=>?^_~]
[A-Za-z@!$%&*/:<=>?^_~0-9+-.]*'''[1:], re.VERBOSE)
SPSYMS = re.compile(r'(\+|-|\.\.\.)')

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

    def nextSymbol() -> Union[Symbol, bool, None]:
        nonlocal pos
        peek()
        m = SYMBOL.match(code, pos) or SPSYMS.match(code, pos)
        if not m:
            raise SJSONSyntaxError(code, pos, 'internal error')
        pos = m.end()
        m = m.group()
        if m == 'null':
            return None
        if m == 'true':
            return True
        if m == 'false':
            return False
        return gensym(m)

    def nextString() -> str:
        nonlocal pos
        peek()
        m = STRING.match(code, pos)
        if not m:
            raise SJSONSyntaxError(code, pos, 'invalid string notation')
        pos = m.end()
        return json.loads(m.group())

    def nextNumber() -> Union[int, float]:
        nonlocal pos
        peek()
        m = NUMBER.match(code, pos)
        if not m:
            raise SJSONSyntaxError(code, pos, 'internal error')
        pos = m.end()
        dec, exp = m.groups()
        if dec or exp:
            return float(m.group())
        else:
            return int(m.group())
    
    def next() -> object:
        ch = peek()
        if ch == '(':
            return nextList()
        if ch == '\"':
            return nextString()
        if ch in '0123456789':
            return nextNumber()
        if ch == '-':
            if pos + 1 < len(code) and code[pos + 1:pos + 2] in '0123456789':
                return nextNumber()
            else:
                return nextSymbol()
        if SYMBOL.match(ch) or ch in '+.':
            return nextSymbol()
        raise SJSONSyntaxError(code, pos, 'invalid syntax')

    rval = next()
    return rval, pos


if __name__ == '__main__':
    import itertools
    DATA = """
(list and symbol)
(dotted . pair)
"SIMPLE STRING"
"COMPLEX\\nMULTI\\tLINED\\n\\"STRING\\u0022\\n"
1234567890
-9876543210
12345.6789
-9.876543e21
-9.876543E+21
9.8765432e-1
+
-
...
true
false
null
"""[1:]
    pos = 0
    for n in itertools.count(1):
        try:
            rval, pos = decode(DATA, pos)
            print("%2d: %s, %s" % (n, encode(rval), type(rval)))
        except EOFError:
            break
