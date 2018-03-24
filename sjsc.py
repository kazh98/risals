#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
### sjsc: S-expressed JavaScript Compiler
###  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
###############################################################################
import re
from typing import Union, Reversible

###
### Fundamental Objects
###
class Cell(object):
    def __init__(self, car: object, cdr: object):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        rval = [str(self.car)]
        p = self.cdr
        while isinstance(p, Cell):
            rval.append(str(p.car))
            p = p.cdr
        if p is not None:
            rval.append('.')
            rval.append(str(p))
        return '(' + ' '.join(rval) + ')'


class Number(object):
    def __init__(self, token):
        self.token = token

    def __str__(self):
        return self.token
    

class Symbol(object):
    def __init__(self, token, atom):
        self.token = token
        self.atom = atom

    def __str__(self):
        return self.token
    
__atom_table = {}
def gensym(token: str) -> Symbol:
    if token not in __atom_table:
        __atom_table[token] = Symbol(token, len(__atom_table))
    return __atom_table[token]


###
### S-expression Reader
###
_WHITESPACE = re.compile(r'[ \t\r\n]*')
_NUMBER = re.compile(r'-?(0|[1-9][0-9]*)(\.[0-9])?([eE][+-]?[0-9]*)?')
_SYMBOL = re.compile(r'[A-Za-z:][A-Za-z:.!?\-]*')

class SexprReader(object):
    def __init__(self, raw: str):
        self.raw = raw
        self.pos = 0

    def peek(self) -> Union[str, None]:
        self.pos = _WHITESPACE.match(self.raw, self.pos).end()
        if self.pos >= len(self.raw):
            return None
        return self.raw[self.pos:self.pos + 1]
    
    def poll(self) -> Union[str, None]:
        self.pos += 1
        return self.peek()
    
    def next(self) -> object:
        ch = self.peek()
        if ch is None:
            raise StopIteration()
        if ch == '(':
            self.poll()
            lis = []
            while True:
                ch = self.peek()
                if ch is None:
                    raise Exception("syntax error")
                if ch == ')':
                    self.poll()
                    rval = None
                    for item in reversed(lis):
                        rval = Cell(item, rval)
                    return rval
                lis.append(self.next())
        m = _NUMBER.match(self.raw, self.pos)
        if m:
            self.pos = m.end()
            return Number(m.group())
        m = _SYMBOL.match(self.raw, self.pos)
        if m:
            self.pos = m.end()
            return gensym(m.group())
        raise Exception("syntax error")

    __next__ = next
    
    def __iter__(self):
        return self


###
###
###
if __name__ == '__main__':
    import itertools
    sb = []
    # while True:
    #     try:
    #         sb.append(input())
    #     except EOFError:
    #         break
    sb.append('  (quote a)')
    sb.append('  (quote b)')
    sb.append('')
    try:
        sr = SexprReader('\n'.join(sb))
        for n, ln in zip(itertools.count(), sr):
            print("%3d: %s" % (n, ln))
    except:
        print('===== ERROR =====')
        print(sr.raw[sr.pos:-1])
