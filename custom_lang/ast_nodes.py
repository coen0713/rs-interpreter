from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional


# Expressions
@dataclass
class Expr:
    line: int


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Var(Expr):
    name: str


@dataclass
class Unary(Expr):
    op: str
    right: Expr


@dataclass
class Binary(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class Logical(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class Grouping(Expr):
    expr: Expr


# Statements
@dataclass
class Stmt:
    line: int


@dataclass
class Block(Stmt):
    statements: List[Stmt]


@dataclass
class VarDecl(Stmt):
    name: str
    initializer: Optional[Expr]


@dataclass
class Assign(Stmt):
    name: str
    value: Expr


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class Print(Stmt):
    expr: Expr


@dataclass
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Optional[Stmt]


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass
class Break(Stmt):
    pass


@dataclass
class Continue(Stmt):
    pass


@dataclass
class Program:
    statements: List[Stmt]
