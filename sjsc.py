#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################################
### sjsc: Symbolic JavaScript Compiler
###  - 2018 Risa YASAKA and Kazuhiro HISHINUMA.
###############################################################################
import sjson
from sjson import Cell, Symbol, gensym
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Reversible


VOID_SYMBOL = gensym()
INIT_SCRIPT = """
(@defun @list args
  (@defun @lp (args)
    (@if (@null? args)
      null
      (@cons (@car args) (@lp (@cdr args)))))
  (@lp args))

(@defun @reverse (lis)
  (@defun @lp (lis res)
    (@if (@null? lis)
      res
      (@lp (@cdr lis) (@cons (@car lis) res))))
  (@lp lis null))
"""[1:]



class SJSCRuntimeError(RuntimeError):
    def __init__(self, msg: str):
        RuntimeError.__init__(self, msg)

        
def _tolist(lis: Reversible[object]) -> Cell:
    rvalue = None
    for e in reversed(lis):
        rvalue = Cell(e, rvalue)
    return rvalue
        
def _list(obj: object) -> Cell:
    p = obj
    while p is not None:
        if not isinstance(obj, Cell):
            raise SJSCRuntimeError('given object must be a proper list')
        p = p.cdr
    return obj

def _purelist(obj: object, l: Optional[int]=None) -> List[object]:
    rvalue = []
    while obj is not None:
        if not isinstance(obj, Cell):
            raise SJSCRuntimeError('given object must be a proper list')
        rvalue.append(obj.car)
        obj = obj.cdr
    if l is not None and len(rvalue) != l:
        raise SJSCRuntimeError('the number of elements in given list is insufficient')
    return rvalue

def _length(obj: object) -> int:
    rvalue = 0
    while obj is not None:
        if not isinstance(obj, Cell):
            raise SJSCRuntimeError('given object must be a proper list')
        obj = obj.cdr
        rvalue += 1
    return rvalue


class Function(object):
    def __init__(self, vlist, plist):
        self.vlist = vlist
        self.plist = _list(plist)

    def __call__(self, env, args):
        rvalue = VOID_SYMBOL
        env._stack_push()
        env._bind(self.vlist, args)
        procs = self.plist
        while procs is not None:
            rvalue = env._eval(procs.car)
            procs = procs.cdr
        env._stack_pop()
        return rvalue

def nif_cons(env, args):
    args = _purelist(args, 2)
    return Cell(args[0], args[1])

def nif_car(env, args):
    args = _purelist(args, 1)
    if not isinstance(args[0], Cell):
        raise SJSCRuntimeError('The argument given to @car must be a cons cell')
    return args[0].car
    
def nif_cdr(env, args):
    args = _purelist(args, 1)
    if not isinstance(args[0], Cell):
        raise SJSCRuntimeError('The argument given to @car must be a cons cell')
    return args[0].cdr

def nif_nullp(env, args):
    args = _purelist(args, 1)
    return args[0] is None

def nif_pairp(env, args):
    args = _purelist(args, 1)
    return isinstance(args[0], Cell)

def nif_eqp(env, args):
    args = _purelist(args, 2)
    if isinstance(args[0], Symbol):
        return isinstance(args[1], Symbol) and args[0].xid == args[1].xid
    if isinstance(args[0], int) or isinstance(args[0], float) or isinstance(args[0], str):
        return args[0] == args[1]
    return args[0] is args[1]


class Syntax(ABC):
    @abstractmethod
    def __call__(self, env, args):
        raise NotImplementedError()

class QuoteSyntax(Syntax):
    def __call__(self, env, args):
        args = _purelist(args, 1)
        return args[0]

class IfSyntax(Syntax):
    def __call__(self, env, args):
        args = _purelist(args)
        if not 2 <= len(args) <= 3:
            raise SJSCRuntimeError('invalid @if')
        test = env._eval(args[0])
        if test:
            return env._eval(args[1])
        elif len(args) >= 3:
            return env._eval(args[2])
        return VOID_SYMBOL

class DefunSyntax(Syntax):
    def __call__(self, env, args):
        if _length(args) < 2:
            raise SJSCRuntimeError('@defun syntax requires at least two arguments')
        if not isinstance(args.car, Symbol):
            raise SJSCRuntimeError('function name must be a Symbol')
        env._bind(args.car, Function(args.cdr.car, args.cdr.cdr))
        return VOID_SYMBOL


class Environment(object):
    def __init__(self):
        self.scope = {}
        self.stack = [{}]
        self.bind('@cons', nif_cons)
        self.bind('@car', nif_car)
        self.bind('@cdr', nif_cdr)
        self.bind('@null?', nif_nullp)
        self.bind('@pair?', nif_pairp)
        self.bind('@eq?', nif_eqp)
        self.bind('@quote', QuoteSyntax())
        self.bind('@if', IfSyntax())
        self.bind('@defun', DefunSyntax())
        self.eval(INIT_SCRIPT)

    def hasvar(self, var):
        return gensym(var).xid in self.scope

    def getvar(self, var):
        return self.scope[gensym(var).xid]

    def _stack_push(self):
        self.stack.append({})
        return

    def _stack_pop(self):
        stack = self.stack.pop()
        for key, value in stack.items():
            if value is VOID_SYMBOL:
                del self.scope[key]
            else:
                self.scope[key] = value
        return

    def _bind(self, var, val) -> Dict[int, object]:
        stack = self.stack[-1]
        if isinstance(var, Symbol):
            if var.xid not in stack:
                if var.xid in self.scope:
                    stack[var.xid] = self.scope[var.xid]
                else:
                    stack[var.xid] = VOID_SYMBOL
            if val is VOID_SYMBOL:
                del self.scope[var.xid]
            else:
                self.scope[var.xid] = val
            return
        if var is None and val is None:
            return
        if isinstance(var, Cell) and isinstance(val, Cell):
            self._bind(var.car, val.car)
            self._bind(var.cdr, val.cdr)
            return
        if isinstance(var, Cell) and val is None:
            raise SJSCRuntimeError('the number of arguments is insufficient')
        if var is None and val is not None:
            raise SJSCRuntimeError('the number of arguments is surplus')
        raise SJSCRuntimeError('unknown error')

    def bind(self, var: str, val: object) -> None:
        self._bind(gensym(var), val)
        return
    
    def _eval(self, obj: object) -> object:
        if isinstance(obj, Cell):
            func = self._eval(obj.car)
            args = _list(obj.cdr)
            if isinstance(func, Syntax):
                return func(self, args)
            if callable(func):
                evaluated = []
                while args is not None:
                    evaluated.append(self._eval(args.car))
                    args = args.cdr
                return func(self, _tolist(evaluated))
            raise SJSCRuntimeError('given object was not callable')
        if isinstance(obj, Symbol):
            if obj.xid in self.scope:
                return self.scope[obj.xid]
            raise SJSCRuntimeError('unbound variable ``%s\"' % obj.raw)
        return obj
    
    def eval(self, code: str) -> None:
        pos = 0
        while True:
            try:
                obj, pos = sjson.decode(code, pos, quoteSymbol='@quote')
                result = self._eval(obj)
            except EOFError:
                break
            if result is not VOID_SYMBOL:
                try:
                    print(sjson.encode(result))
                except:
                    print(result)
        return


if __name__ == '__main__':
    env = Environment()
    code = """
(@if false 0 1)
(@cons 'a 'b)
(@defun fun (u) u)
(fun 15)
(@list 'a 'b 'c 'd 'e)
(@reverse '(a b c d e))
(@eq? '(a b c) '(a b c))
"""[1:]
    env.eval(code)
