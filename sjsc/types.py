#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Iterator
__all__ = ['Symbol', 'Cell', 'CellIterator']


class Symbol(object):
    _symbols = {}
    _counts = 0

    def __new__(cls, raw: str=None) -> 'Symbol':
        if raw is not None and raw in cls._symbols:
            return cls._symbols[raw]
        rvalue = super().__new__(cls)
        rvalue.id_ = cls._counts
        cls._counts += 1
        rvalue.raw = raw
        cls._symbols[raw] = rvalue
        return rvalue

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Symbol) and self.id_ == other.id_

    
class Cell(object):
    def __init__(self, car: object, cdr: object) -> None:
        self.car = car
        self.cdr = cdr
        return

    def is_proper(self) -> bool:
        p = self.cdr
        while p is not None:
            if not isinstance(p, Cell):
                return False
            p = p.cdr
        return True

    def reverse(self) -> 'Cell':
        rvalue, p = None, self
        while p is not None:
            if not isinstance(p, Cell):
                raise ValueError('Improper list cannot be reversed.')
            rvalue = Cell(p.car, rvalue)
            p = p.cdr
        return rvalue

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Cell) and (
            self.car == other.car and self.cdr == other.cdr)
    
    def __str__(self) -> str:
        sb = ['(', str(self.car)]
        p = self.cdr
        while isinstance(p, Cell):
            sb.extend([' ', str(p.car)])
            p = p.cdr
        if p is not None:
            sb.extend([' . ', str(p)])
        sb.append(')')
        return ''.join(sb)

    def __iter__(self) -> 'CellIterator':
        return CellIterator(self)


class CellIterator(Iterator[object]):
    def __init__(self, cell: Cell) -> None:
        self.target = cell
        return
    
    def __iter__(self) -> 'CellIterator':
        return self

    def __next__(self) -> object:
        if self.target is None:
            raise StopIteration()
        if not isinstance(self.target, Cell):
            raise ValueError('Improper list is not iterable.')
        rvalue = self.target.car
        self.target = self.target.cdr
        return rvalue
