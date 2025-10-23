from __future__ import annotations
import argparse
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .debugger import Debugger


def run_file(path: str, debug: bool = False, breakpoints=None):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    tokens = Lexer(src).lex()
    program = Parser(tokens).parse()
    dbg = Debugger()
    if breakpoints:
        dbg.set_breakpoints(breakpoints)
    interp = Interpreter()
    if debug:
        interp.run(program, debugger=dbg)
    else:
        interp.run(program)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="custom-lang", description="Custom language interpreter with debugger")
    ap.add_argument("file", help="Source file to execute")
    ap.add_argument("--debug", action="store_true", help="Run with interactive debugger")
    ap.add_argument("--break", dest="breaks", nargs="*", help="Set breakpoints by line numbers")
    args = ap.parse_args(argv)
    run_file(args.file, debug=args.debug, breakpoints=args.breaks)


if __name__ == "__main__":
    main()
