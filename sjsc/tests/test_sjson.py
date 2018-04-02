#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sjsc.types import *
from sjsc.sjson import *
import unittest


def _d(s: str) -> object:
    return next(SJStream(s))


class TestSJStream(unittest.TestCase):
    def test_list(self):
        self.assertEqual(_d('(list and symbol)'),
                         Cell(Symbol('list'), Cell(Symbol('and'), Cell(Symbol('symbol'), None))))
        self.assertEqual(_d('(dotted . pair)'),
                         Cell(Symbol('dotted'), Symbol('pair')))
        self.assertEqual(_d('((1 2) 3)'),
                         Cell(Cell(1, Cell(2, None)), Cell(3, None)))

    def test_object(self):
        self.assertEqual(_d('{}'), {})
        self.assertEqual(_d('{"a": carrot, "b": apple, "c": banana}'),
                         {'a': Symbol('carrot'), 'b': Symbol('apple'), 'c': Symbol('banana')})
        
    def test_array(self):
        self.assertEqual(_d('[]'), [])
        self.assertEqual(_d('[1, 2, 3, 4, 5]'), [1, 2, 3, 4, 5])
        
    def test_str(self):
        self.assertEqual(_d('\"SIMPLE STRING\"'), 'SIMPLE STRING')
        self.assertEqual(_d('\"COMPLEX\\nMULTI\\tLINED\\n\\"STRING\\u0022\\n\"'),
                         'COMPLEX\nMULTI\tLINED\n\"STRING\"\n')
        
    def test_int(self):
        self.assertEqual(_d('1234567890'), 1234567890)
        self.assertEqual(_d('-9876543210'), -9876543210)

    def test_float(self):
        self.assertEqual(_d('12345.125'), 12345.125)
        self.assertEqual(_d('-98765.875'), -98765.875)
        self.assertEqual(_d('-0.0125e1'), -0.125)
        self.assertEqual(_d('1.25e-1'), 0.125)
        self.assertEqual(_d('+0.0125E1'), 0.125)

    def test_values(self):
        self.assertEqual(_d('true'), True)
        self.assertEqual(_d('false'), False)
        self.assertEqual(_d('null'), None)


if __name__ == '__main__':
    unittest.main()

