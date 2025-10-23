from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class Debugger:
    breakpoints: Set[int] = field(default_factory=set)
    stepping: bool = False

    def set_breakpoints(self, lines):
        for ln in lines:
            try:
                self.breakpoints.add(int(ln))
            except ValueError:
                pass

    def check_pause(self, line: int, variables: Dict[str, object], depth: int = 0):
        if self.stepping or line in self.breakpoints:
            self._repl(line, variables)

    # very simple console REPL
    def _repl(self, line: int, variables: Dict[str, object]):
        print(f"Paused at line {line}. Type 'help' for commands.")
        while True:
            try:
                cmd = input("(dbg) ").strip()
            except EOFError:
                cmd = "cont"
            if cmd in ("c", "cont", "continue"):
                self.stepping = False
                return
            if cmd in ("s", "step"):
                self.stepping = True
                return
            if cmd.startswith("b ") or cmd.startswith("break "):
                parts = cmd.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    self.breakpoints.add(int(parts[-1]))
                    print(f"Breakpoint set at line {parts[-1]}")
                else:
                    print("Usage: break <line>")
            elif cmd.startswith("cl ") or cmd.startswith("clear "):
                parts = cmd.split()
                if len(parts) >= 2 and parts[-1].isdigit():
                    ln = int(parts[-1])
                    self.breakpoints.discard(ln)
                    print(f"Breakpoint cleared at line {ln}")
                else:
                    print("Usage: clear <line>")
            elif cmd in ("l", "list"):
                if self.breakpoints:
                    print("Breakpoints:", sorted(self.breakpoints))
                else:
                    print("No breakpoints set.")
            elif cmd in ("v", "vars"):
                for k, v in variables.items():
                    print(f"{k} = {v!r}")
            elif cmd in ("w", "where"):
                print(f"At line {line}")
            elif cmd in ("q", "quit"):
                raise SystemExit(0)
            elif cmd in ("h", "help"):
                print("Commands:\n  continue|c\n  step|s\n  break <line>\n  clear <line>\n  list|l\n  vars|v\n  where|w\n  quit|q")
            else:
                print("Unknown command. Type 'help'.")
