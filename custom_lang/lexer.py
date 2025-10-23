from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


KEYWORDS = {
    "let": "LET",
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "print": "PRINT",
    "true": "TRUE",
    "false": "FALSE",
    "nil": "NIL",
    "break": "BREAK",
    "continue": "CONTINUE",
    "and": "AND",
    "or": "OR",
}


@dataclass
class Token:
    type: str
    lexeme: str
    literal: Optional[object]
    line: int
    column: int

    def __repr__(self) -> str:  # compact debug
        lit = f",{self.literal!r}" if self.literal is not None else ""
        return f"Token({self.type},{self.lexeme!r}{lit},@{self.line}:{self.column})"


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []

    def lex(self) -> List[Token]:
        while not self._is_at_end():
            self.start = self.current
            self._scan_token()
        self.tokens.append(Token("EOF", "", None, self.line, self.col))
        return self.tokens

    # internals
    def _is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def _advance(self) -> str:
        ch = self.source[self.current]
        self.current += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current]

    def _peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self.source[self.current] != expected:
            return False
        # update col as if consumed
        self.current += 1
        self.col += 1 if expected != "\n" else 0
        return True

    def _add(self, type_: str, literal: Optional[object] = None):
        text = self.source[self.start:self.current]
        # find starting column from current col minus length for single-line tokens
        # For multi-line strings, we tracked columns line-by-line via _advance.
        start_col = self.col - (len(text) if "\n" not in text else len(text.split("\n")[-1]))
        self.tokens.append(Token(type_, text, literal, self.line, max(1, start_col)))

    def _scan_token(self):
        c = self._advance()
        if c in (" ", "\r", "\t"):
            return
        if c == "\n":
            return
        if c == "/" and self._peek() == "/":  # line comment
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return
        if c == "/" and self._peek() == "*":  # block comment /* ... */
            self._advance()  # consume '*'
            self._block_comment()
            return

        # single-char tokens
        single = {
            "(": "LEFT_PAREN",
            ")": "RIGHT_PAREN",
            "{": "LEFT_BRACE",
            "}": "RIGHT_BRACE",
            ",": "COMMA",
            ";": "SEMICOLON",
        }
        if c in single:
            self._add(single[c])
            return

        # one or two char operators
        if c == "!":
            self._add("BANG_EQUAL" if self._match("=") else "BANG")
            return
        if c == "=":
            self._add("EQUAL_EQUAL" if self._match("=") else "EQUAL")
            return
        if c == "<":
            self._add("LESS_EQUAL" if self._match("=") else "LESS")
            return
        if c == ">":
            self._add("GREATER_EQUAL" if self._match("=") else "GREATER")
            return
        if c == "+":
            self._add("PLUS")
            return
        if c == "-":
            self._add("MINUS")
            return
        if c == "*":
            self._add("STAR")
            return
        if c == "/":
            self._add("SLASH")
            return
        if c == "%":
            self._add("PERCENT")
            return
        if c == "\"":
            self._string()
            return

        if c.isdigit():
            self._number()
            return
        if c.isalpha() or c == "_":
            self._identifier()
            return

        raise SyntaxError(f"Unexpected character {c!r} at line {self.line}")

    def _block_comment(self):
        depth = 1
        while depth > 0 and not self._is_at_end():
            ch = self._advance()
            if ch == "/" and self._peek() == "*":
                self._advance()
                depth += 1
            elif ch == "*" and self._peek() == "/":
                self._advance()
                depth -= 1
        if depth != 0:
            raise SyntaxError(f"Unterminated block comment at line {self.line}")

    def _string(self):
        start_line = self.line
        value_chars: List[str] = []
        while not self._is_at_end():
            ch = self._advance()
            if ch == "\"":
                break
            if ch == "\\":
                nxt = self._advance()
                escapes = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}
                value_chars.append(escapes.get(nxt, nxt))
            else:
                value_chars.append(ch)
        else:
            raise SyntaxError(f"Unterminated string starting at line {start_line}")
        self._add("STRING", "".join(value_chars))

    def _number(self):
        while self._peek().isdigit():
            self._advance()
        if self._peek() == "." and self._peek_next().isdigit():
            self._advance()
            while self._peek().isdigit():
                self._advance()
        num = float(self.source[self.start:self.current])
        if num.is_integer():
            num = int(num)
        self._add("NUMBER", num)

    def _identifier(self):
        while (self._peek().isalnum()) or self._peek() == "_":
            self._advance()
        text = self.source[self.start:self.current]
        type_ = KEYWORDS.get(text, "IDENTIFIER")
        lit = None
        if type_ == "TRUE":
            lit = True
        elif type_ == "FALSE":
            lit = False
        elif type_ == "NIL":
            lit = None
        self.tokens.append(Token(type_, text, lit, self.line, self.col - len(text)))
