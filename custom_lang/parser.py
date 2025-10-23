from __future__ import annotations
from typing import List, Optional
from .lexer import Token
from . import ast_nodes as A


class ParseError(SyntaxError):
    pass


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> A.Program:
        statements: List[A.Stmt] = []
        while not self._is_at_end():
            statements.append(self._declaration())
        return A.Program(statements=statements)

    # declarations and statements
    def _declaration(self) -> A.Stmt:
        if self._match("LET"):
            return self._var_decl()
        return self._statement()

    def _var_decl(self) -> A.Stmt:
        name = self._consume("IDENTIFIER", "Expect variable name.")
        initializer = None
        if self._match("EQUAL"):
            initializer = self._expression()
        line = name.line
        self._consume("SEMICOLON", "Expect ';' after variable declaration.")
        return A.VarDecl(name=name.lexeme, initializer=initializer, line=line)

    def _statement(self) -> A.Stmt:
        if self._match("PRINT"):
            expr = self._expression()
            line = expr.line
            self._consume("SEMICOLON", "Expect ';' after value.")
            return A.Print(expr=expr, line=line)
        if self._match("LEFT_BRACE"):
            return A.Block(statements=self._block(), line=self._previous().line)
        if self._match("IF"):
            self._consume("LEFT_PAREN", "Expect '(' after 'if'.")
            cond = self._expression()
            self._consume("RIGHT_PAREN", "Expect ')' after condition.")
            then_branch = self._statement()
            else_branch = None
            if self._match("ELSE"):
                else_branch = self._statement()
            return A.If(condition=cond, then_branch=then_branch, else_branch=else_branch, line=cond.line)
        if self._match("WHILE"):
            self._consume("LEFT_PAREN", "Expect '(' after 'while'.")
            cond = self._expression()
            self._consume("RIGHT_PAREN", "Expect ')' after condition.")
            body = self._statement()
            return A.While(condition=cond, body=body, line=cond.line)
        if self._match("BREAK"):
            tok = self._previous()
            self._consume("SEMICOLON", "Expect ';' after 'break'.")
            return A.Break(line=tok.line)
        if self._match("CONTINUE"):
            tok = self._previous()
            self._consume("SEMICOLON", "Expect ';' after 'continue'.")
            return A.Continue(line=tok.line)

        # assignment or expression stmt
        expr = self._expression()
        if self._match("EQUAL"):
            if not isinstance(expr, A.Var):
                raise ParseError(f"Invalid assignment target at line {expr.line}")
            value = self._expression()
            line = expr.line
            self._consume("SEMICOLON", "Expect ';' after assignment.")
            return A.Assign(name=expr.name, value=value, line=line)
        line = expr.line
        self._consume("SEMICOLON", "Expect ';' after expression.")
        return A.ExprStmt(expr=expr, line=line)

    def _block(self) -> List[A.Stmt]:
        statements: List[A.Stmt] = []
        while not self._check("RIGHT_BRACE") and not self._is_at_end():
            statements.append(self._declaration())
        self._consume("RIGHT_BRACE", "Expect '}' after block.")
        return statements

    # expressions: logical or -> logical and -> equality -> comparison -> term -> factor -> unary -> primary
    def _expression(self) -> A.Expr:
        return self._or()

    def _or(self) -> A.Expr:
        expr = self._and()
        while self._match("OR"):
            op = self._previous().lexeme
            right = self._and()
            expr = A.Logical(left=expr, op=op, right=right, line=expr.line)
        return expr

    def _and(self) -> A.Expr:
        expr = self._equality()
        while self._match("AND"):
            op = self._previous().lexeme
            right = self._equality()
            expr = A.Logical(left=expr, op=op, right=right, line=expr.line)
        return expr

    def _equality(self) -> A.Expr:
        expr = self._comparison()
        while self._match("BANG_EQUAL", "EQUAL_EQUAL"):
            op = self._previous().type
            right = self._comparison()
            expr = A.Binary(left=expr, op=op, right=right, line=expr.line)
        return expr

    def _comparison(self) -> A.Expr:
        expr = self._term()
        while self._match("GREATER", "GREATER_EQUAL", "LESS", "LESS_EQUAL"):
            op = self._previous().type
            right = self._term()
            expr = A.Binary(left=expr, op=op, right=right, line=expr.line)
        return expr

    def _term(self) -> A.Expr:
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            op = self._previous().type
            right = self._factor()
            expr = A.Binary(left=expr, op=op, right=right, line=expr.line)
        return expr

    def _factor(self) -> A.Expr:
        expr = self._unary()
        while self._match("STAR", "SLASH", "PERCENT"):
            op = self._previous().type
            right = self._unary()
            expr = A.Binary(left=expr, op=op, right=right, line=expr.line)
        return expr

    def _unary(self) -> A.Expr:
        if self._match("BANG", "MINUS"):
            op = self._previous().type
            right = self._unary()
            return A.Unary(op=op, right=right, line=right.line)
        return self._primary()

    def _primary(self) -> A.Expr:
        if self._match("NUMBER"):
            tok = self._previous()
            return A.Literal(value=tok.literal, line=tok.line)
        if self._match("STRING"):
            tok = self._previous()
            return A.Literal(value=tok.literal, line=tok.line)
        if self._match("TRUE", "FALSE", "NIL"):
            tok = self._previous()
            return A.Literal(value=tok.literal, line=tok.line)
        if self._match("IDENTIFIER"):
            tok = self._previous()
            return A.Var(name=tok.lexeme, line=tok.line)
        if self._match("LEFT_PAREN"):
            expr = self._expression()
            paren = self._consume("RIGHT_PAREN", "Expect ')' after expression.")
            return A.Grouping(expr=expr, line=paren.line)
        raise ParseError(f"Expect expression at line {self._peek().line}")

    # helpers
    def _match(self, *types: str) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, type_: str, message: str) -> Token:
        if self._check(type_):
            return self._advance()
        raise ParseError(message + f" at line {self._peek().line}")

    def _check(self, type_: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == type_

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == "EOF"

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
