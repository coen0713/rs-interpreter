from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
from . import ast_nodes as A


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


@dataclass
class Environment:
    values: Dict[str, Any]
    enclosing: Optional["Environment"] = None

    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: str, value: Any):
        if name in self.values:
            self.values[name] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise NameError(f"Undefined variable '{name}'.")

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise NameError(f"Undefined variable '{name}'.")

    def snapshot(self) -> Dict[str, Any]:
        data = {}
        if self.enclosing is not None:
            data.update(self.enclosing.snapshot())
        data.update(self.values)
        return data


class Interpreter:
    def __init__(self, output=print):
        self.globals = Environment(values={})
        self.env = self.globals
        self.output = output
        self._call_depth = 0  # reserved for future function support
        self.debugger = None

    def run(self, program: A.Program, debugger=None):
        self.debugger = debugger
        for stmt in program.statements:
            self._maybe_debug(stmt)
            self._execute(stmt)

    # Debug hook
    def _maybe_debug(self, stmt: A.Stmt):
        if self.debugger is not None:
            self.debugger.check_pause(stmt.line, self.env.snapshot(), depth=self._call_depth)

    # Statement execution
    def _execute(self, stmt: A.Stmt):
        if isinstance(stmt, A.Block):
            self._execute_block(stmt)
        elif isinstance(stmt, A.VarDecl):
            val = self._evaluate(stmt.initializer) if stmt.initializer is not None else None
            self.env.define(stmt.name, val)
        elif isinstance(stmt, A.Assign):
            val = self._evaluate(stmt.value)
            self.env.assign(stmt.name, val)
        elif isinstance(stmt, A.ExprStmt):
            self._evaluate(stmt.expr)
        elif isinstance(stmt, A.Print):
            val = self._evaluate(stmt.expr)
            self.output(val)
        elif isinstance(stmt, A.If):
            if self._is_truthy(self._evaluate(stmt.condition)):
                self._execute(stmt.then_branch)
            elif stmt.else_branch is not None:
                self._execute(stmt.else_branch)
        elif isinstance(stmt, A.While):
            while self._is_truthy(self._evaluate(stmt.condition)):
                try:
                    self._maybe_debug(stmt)
                    self._execute(stmt.body)
                except BreakSignal:
                    break
                except ContinueSignal:
                    continue
        elif isinstance(stmt, A.Break):
            raise BreakSignal()
        elif isinstance(stmt, A.Continue):
            raise ContinueSignal()
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")

    def _execute_block(self, block: A.Block):
        previous = self.env
        try:
            self.env = Environment(values={}, enclosing=previous)
            for s in block.statements:
                self._maybe_debug(s)
                self._execute(s)
        finally:
            self.env = previous

    # Expression evaluation
    def _evaluate(self, expr: A.Expr):
        if isinstance(expr, A.Literal):
            return expr.value
        if isinstance(expr, A.Var):
            return self.env.get(expr.name)
        if isinstance(expr, A.Grouping):
            return self._evaluate(expr.expr)
        if isinstance(expr, A.Unary):
            right = self._evaluate(expr.right)
            if expr.op == "BANG":
                return not self._is_truthy(right)
            if expr.op == "MINUS":
                return -self._num(right, expr.line)
            raise RuntimeError(f"Unknown unary op {expr.op}")
        if isinstance(expr, A.Binary):
            left = self._evaluate(expr.left)
            right = self._evaluate(expr.right)
            t = expr.op
            if t == "PLUS":
                if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                    return left + right
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                raise TypeError(f"Operands to '+' must be numbers or strings at line {expr.line}")
            if t == "MINUS":
                return self._num(left, expr.line) - self._num(right, expr.line)
            if t == "STAR":
                return self._num(left, expr.line) * self._num(right, expr.line)
            if t == "SLASH":
                return self._num(left, expr.line) / self._num(right, expr.line)
            if t == "PERCENT":
                return self._num(left, expr.line) % self._num(right, expr.line)
            if t == "GREATER":
                return self._num(left, expr.line) > self._num(right, expr.line)
            if t == "GREATER_EQUAL":
                return self._num(left, expr.line) >= self._num(right, expr.line)
            if t == "LESS":
                return self._num(left, expr.line) < self._num(right, expr.line)
            if t == "LESS_EQUAL":
                return self._num(left, expr.line) <= self._num(right, expr.line)
            if t == "EQUAL_EQUAL":
                return left == right
            if t == "BANG_EQUAL":
                return left != right
            raise RuntimeError(f"Unknown binary op {t}")
        if isinstance(expr, A.Logical):
            left = self._evaluate(expr.left)
            if expr.op == "or":
                if self._is_truthy(left):
                    return left
            else:  # and
                if not self._is_truthy(left):
                    return left
            return self._evaluate(expr.right)
        raise RuntimeError(f"Unknown expression type: {type(expr)}")

    # helpers
    @staticmethod
    def _is_truthy(value: Any) -> bool:
        if value is None:
            return False
        return bool(value)

    @staticmethod
    def _num(value: Any, line: int) -> float:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Operand must be a number at line {line}")
        return value
