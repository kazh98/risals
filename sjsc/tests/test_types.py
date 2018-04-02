#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from sjsc.types import *


class TestSymbol(unittest.TestCase):
    def test_id(self):
        self.assertEqual(id(Symbol('A')), id(Symbol('A')))
        self.assertNotEqual(id(Symbol('A')), id(Symbol('B')))
        self.assertNotEqual(id(Symbol()), id(Symbol()))
        
    def test_id_(self):
        self.assertEqual(Symbol('A').id_, Symbol('A').id_)
        self.assertNotEqual(Symbol('A').id_, Symbol('B').id_)
        self.assertNotEqual(Symbol().id_, Symbol().id_)

    def test_eq(self):
        self.assertTrue(Symbol('A') == Symbol('A'))
        self.assertFalse(Symbol('A') == Symbol('B'))
        self.assertFalse(Symbol() == Symbol())
        
    def test_raw(self):
        self.assertEqual(Symbol('A').raw, 'A')


class TestCell(unittest.TestCase):
    def test_is_proper(self):
        self.assertTrue(Cell(1, Cell(2, Cell(3, None))).is_proper())
        self.assertFalse(Cell(1, Cell(2, 3)).is_proper())

    def test_reverse(self):
        self.assertEqual(Cell(1, Cell(2, Cell(3, None))).reverse(),
                         Cell(3, Cell(2, Cell(1, None))))
        with self.assertRaises(ValueError):
            Cell(1, Cell(2, 3)).reverse()

    def test_eq(self):
        self.assertTrue(Cell(1, Cell(2, Cell(3, None))) == Cell(1, Cell(2, Cell(3, None))))
        self.assertFalse(Cell(1, Cell(2, Cell(3, None))) == Cell(1, Cell(2, 3)))
        
    def test_str(self):
        self.assertEqual(str(Cell(1, Cell(2, Cell(3, None)))), "(1 2 3)")
        self.assertEqual(str(Cell(1, Cell(2, 3))), "(1 2 . 3)")
        self.assertEqual(str(Cell(Cell(1, Cell(2, None)), Cell(3, None))), "((1 2) 3)")

    def test_iter(self):
        self.assertEqual(list(Cell(1, Cell(2, Cell(3, None)))), [1, 2, 3])
        with self.assertRaises(ValueError):
            list(Cell(1, Cell(2, 3)))


if __name__ == '__main__':
    unittest.main()
