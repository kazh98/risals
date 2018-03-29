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
QUOTE_SYMBOL = gensym('@quote')
QUASIQUOTE_SYMBOL = gensym('@quasiquote')
UNQUOTE_SYMBOL = gensym('@unquote')
INIT_SCRIPT = """
(@set! @defmacro
  (@syntax (name args . procs)
    `(@set! ,name (@syntax ,args . ,procs))))
(@defmacro @defun (name args . procs)
  `(@set! ,name (@lambda ,args . ,procs)))

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

def nif_symbolp(env, args):
    args = _purelist(args, 1)
    return isinstance(args[0], Symbol)

def nif_eqp(env, args):
    args = _purelist(args, 2)
    if isinstance(args[0], Symbol):
        return isinstance(args[1], Symbol) and args[0].xid == args[1].xid
    if isinstance(args[0], int) or isinstance(args[0], float) or isinstance(args[0], str):
        return args[0] == args[1]
    return args[0] is args[1]

def nif_gensym(env, args):
    return gensym()

    
class Syntax(ABC):
    @abstractmethod
    def __call__(self, env, args):
        raise NotImplementedError()

class Macro(Syntax):
    def __init__(self, vlist, plist):
        self.vlist = vlist
        self.plist = plist
    
    def __call__(self, env, args):
        rvalue = VOID_SYMBOL
        env._stack_push()
        env._bind(self.vlist, args)
        procs = self.plist
        while procs is not None:
            rvalue = env._eval(procs.car)
            procs = procs.cdr
        env._stack_pop()
        return env._eval(rvalue)

class QuoteSyntax(Syntax):
    def __call__(self, env, args):
        args = _purelist(args, 1)
        return args[0]

class QuasiquoteSyntax(Syntax):
    def __call__(self, env, args):
        def quasiquote(obj):
            if not isinstance(obj, Cell):
                return obj
            lis = []
            while isinstance(obj, Cell):
                if isinstance(obj.car, Symbol) and obj.car.xid == UNQUOTE_SYMBOL.xid:
                    rvalue = env._eval(_purelist(obj.cdr, 1)[0])
                    break
                lis.append(quasiquote(obj.car))
                obj = obj.cdr
                rvalue = obj
            for e in reversed(lis):
                rvalue = Cell(e, rvalue)
            return rvalue
        args = _purelist(args, 1)
        return quasiquote(args[0])

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

class LambdaSyntax(Syntax):
    def __call__(self, env, args):
        args = _list(args)
        if not isinstance(args, Cell):
            raise SJSCRuntimeError('invalid @lambda')
        return Function(args.car, args.cdr)

class SyntaxSyntax(Syntax):
    def __call__(self, env, args):
        args = _list(args)
        if not isinstance(args, Cell):
            raise SJSCRuntimeError('invalid @syntax')
        return Macro(args.car, args.cdr)

class SetSyntax(Syntax):
    def __call__(self, env, args):
        args = _purelist(args, 2)
        if not isinstance(args[0], Symbol):
            raise SJSCRuntimeError('variable name must be specified as a symbol')
        env._bind(args[0], env._eval(args[1]))
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
        self.bind('@symbol?', nif_symbolp)
        self.bind('@eq?', nif_eqp)
        self.bind('@gensym', nif_gensym)
        self.bind('@quote', QuoteSyntax())
        self.bind('@quasiquote', QuasiquoteSyntax())
        self.bind('@if', IfSyntax())
        self.bind('@lambda', LambdaSyntax())
        self.bind('@syntax', SyntaxSyntax())
        self.bind('@set!', SetSyntax())
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
                obj, pos = sjson.decode(code, pos, quote=QUOTE_SYMBOL, quasiquote=QUASIQUOTE_SYMBOL, unquote=UNQUOTE_SYMBOL)
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
(@list 'a 'b 'c 'd 'e)
(@reverse '(a b c d e))
(@eq? '(a b c) '(a b c))
((@lambda (u) u) 1)
"""[1:]
    env.eval(code)
