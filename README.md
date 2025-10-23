# Custom Language Interpreter (Python)

A small interpreter written in Python featuring a lexer, parser, AST, and execution engine with a simple interactive debugger.

## Features

- **Variables**: `let name = expr;`, re-assignment `name = expr;`
- **Expressions**: numbers, strings, booleans, `nil`, arithmetic, comparison, equality, logical and/or, grouping
- **Control**: `if` / `else`, `while`, `break`, `continue`
- **I/O**: `print(expr);`
- **Comments**: `// line` and `/* block */`
- **Debugger**: breakpoints by source line, step, continue, list breakpoints, show variables

## Project Layout

- **`custom_lang/lexer.py`**: Tokenizer
- **`custom_lang/ast_nodes.py`**: AST node definitions
- **`custom_lang/parser.py`**: Recursive-descent parser
- **`custom_lang/interpreter.py`**: AST interpreter and runtime
- **`custom_lang/debugger.py`**: Interactive source-level debugger
- **`custom_lang/cli.py`**: CLI entrypoint
- **`examples/loop.cl`**: Sample program

## Usage

Run example:

```bash
python -m custom_lang examples/loop.cl
```

Run with debugger and a breakpoint at line 6:

```bash
python -m custom_lang --debug --break 6 examples/loop.cl
```

Debugger commands:

- **continue|c**
- **step|s**
- **break <line>**
- **clear <line>**
- **list|l**
- **vars|v**
- **where|w**
- **quit|q**

## Notes

- Arithmetic uses Python's numeric semantics; division returns float.
- Strings can be concatenated with numbers via `+`.
- Logical `and`/`or` are parsed but currently use token types; use `==`, `!=`, `<`, `<=`, `>`, `>=` for comparisons.
