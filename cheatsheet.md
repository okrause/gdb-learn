# LLDB ↔ GDB cheatsheet

LLDB commands are `noun verb` (`breakpoint set`, `frame variable`), and
almost all of them have short aliases. GDB commands are single words with
options. LLDB ships a partial set of GDB-style aliases (`b`, `r`, `n`,
`s`, `c`, `bt`, `p`), but the longer GDB commands do **not** carry over,
so learn the LLDB spelling for anything past the basics.

## Starting and loading

| Task | LLDB | GDB |
|------|------|-----|
| Load a program | `lldb ./gradebook` | `gdb ./gradebook` |
| Load later | `target create ./gradebook` | `file ./gradebook` |
| Load a core | `lldb ./crash_roster -c core` | `gdb ./crash_roster core` |
| Attach to a pid | `lldb -p 1234` | `gdb -p 1234` |
| Run a command file | `lldb -s cmds.lldb ./prog` | `gdb -x cmds.gdb ./prog` |
| Run one command | `lldb -o "bt" ./prog` | `gdb -ex "bt" ./prog` |
| Batch (no prompt) | `lldb -b -o "run" ./prog` | `gdb -batch -ex run ./prog` |
| Auto-loaded init | `~/.lldbinit` | `~/.gdbinit` |
| Quit | `quit` | `quit` |

## Running and stepping

| Task | LLDB | GDB |
|------|------|-----|
| Run | `run` / `process launch` | `run` |
| Run with args | `run 103` | `run 103` |
| Set args | `settings set target.run-args 103` | `set args 103` |
| Stop at `main` first | `breakpoint set -n main` then `run` | `start` |
| Next line (over calls) | `thread step-over` / `n` | `next` |
| Step into | `thread step-in` / `s` | `step` |
| Return from function | `thread step-out` / `finish` | `finish` |
| Run to a line | `thread until 67` | `until 67` |
| Continue | `continue` / `c` | `continue` |
| One instruction | `thread step-inst` | `stepi` |
| One instruction, over calls | `thread step-inst-over` | `nexti` |

## Breakpoints and watchpoints

| Task | LLDB | GDB |
|------|------|-----|
| On a function | `breakpoint set -n compute_average` | `break compute_average` |
| On a line | `breakpoint set -f gradebook.c -l 67` | `break gradebook.c:67` |
| Conditional | `breakpoint set -n compute_average -c 'n == 4'` | `break compute_average if n == 4` |
| One-shot | `breakpoint set -o true -n main` | `tbreak main` |
| Auto-continue | `breakpoint set -n f -G true` | `break f` + `commands` / `continue` |
| List | `breakpoint list` | `info breakpoints` |
| Delete / disable / enable | `breakpoint delete 1` / `disable 1` / `enable 1` | `delete 1` / `disable 1` / `enable 1` |
| Watch a variable | `watchpoint set variable sum` | `watch sum` |
| List watchpoints | `watchpoint list` | `info watchpoints` |
| Ignore N hits | `breakpoint set -n f -i 5` | `ignore 1 5` |

## Looking at values

| Task | LLDB | GDB |
|------|------|-----|
| Args and locals | `frame variable` / `v` | `info args` + `info locals` |
| One variable | `frame variable sum` | `print sum` |
| Evaluate an expression | `expression sum / n` / `p sum / n` | `print sum / n` |
| Formatted | `expression -f hex -- n` | `print/x n` |
| Array slice | `parray 4 scores` | `print *scores@4` |
| Type of a value | `expression -- sizeof(Student)`, `frame variable -T sum` | `whatis sum` |
| Type layout | `type lookup Student` | `ptype Student` |
| Auto-display each stop | `target stop-hook add -o "frame variable sum"` | `display sum` |
| Change a value | `expression n = 3` | `set variable n = 3` |
| Force a return value | `thread return sum / n` | `return sum / n` |
| Call a function | `expression (void)printf("%s\n", head->name)` | `call printf("%s\n", head->name)` |

## Memory and registers

| Task | LLDB | GDB |
|------|------|-----|
| Hex bytes | `memory read -c 16 -f x -s 1 head` | `x/16xb head` |
| GDB-style shorthand | `x/16xb head` (alias) | `x/16xb head` |
| C string | `memory read -f c-string head->name` | `x/s head->name` |
| Registers | `register read` | `info registers` |
| One register | `register read pc` | `print $pc` |
| Disassemble at pc | `disassemble -p` | `x/i $pc` |
| Disassemble a function | `disassemble -n compute_average` | `disassemble compute_average` |

## Stack and threads

| Task | LLDB | GDB |
|------|------|-----|
| Backtrace | `thread backtrace` / `bt` | `backtrace` / `bt` |
| Backtrace with locals | `bt` then `frame variable` per frame | `bt full` |
| Select a frame | `frame select 1` | `frame 1` |
| Up / down | `up` / `down` | `up` / `down` |
| Current frame info | `frame info` | `info frame` |
| List threads | `thread list` | `info threads` |
| All thread backtraces | `thread backtrace all` | `thread apply all bt` |

## Source and symbols

| Task | LLDB | GDB |
|------|------|-----|
| List source | `source list` / `l` | `list` |
| List a function | `source list -n compute_average` | `list compute_average` |
| List a range | `source list -f gradebook.c -l 57 -c 11` | `list 57,68` |
| Find a symbol | `image lookup -n compute_average` | `info functions compute_average` |
| Loaded modules | `image list` | `info sharedlibrary` |
| Search help | `apropos breakpoint` | `apropos breakpoint` |
| Curses UI | `gui` | `layout src` (TUI) |

## Signals and crashes

| Task | LLDB | GDB |
|------|------|-----|
| Do not pass a signal | `process handle -p false -s true -n true SIGSEGV` | `handle SIGSEGV stop print nopass` |
| Save a core dump | `process save-core crash.core` | `generate-core-file crash.core` |
| Signal that stopped us | `thread info` | `info signals` / stop message |

## Scripting

| Task | LLDB | GDB |
|------|------|-----|
| Python REPL | `script` | `python-interactive` (`pi`) |
| One Python line | `script print(1)` | `python print(1)` |
| Module | `import lldb` | `import gdb` |
| Load a script file | `command script import path.py` | `source path.py` |
| Add a command | `command script add -f mod.fn name` | subclass `gdb.Command` |
| Read a variable | `frame.FindVariable("n")` | `gdb.parse_and_eval("n")` |
| Value type | `lldb.SBValue` | `gdb.Value` |
| Run a CLI command | `debugger.HandleCommand("bt")` | `gdb.execute("bt")` |
| Breakpoint callback | `breakpoint command add -F mod.fn` | `gdb.Breakpoint.stop()` |
| On every stop | `target stop-hook add` | `gdb.events.stop.connect` |
| One-line value display | `type summary add -F mod.fn Type` | pretty-printer `to_string` |
| Custom children | `type synthetic add -l mod.Class Type` | pretty-printer `children` |
| List them | `type summary list`, `type synthetic list` | `info pretty-printer` |
| Raw, unformatted | `frame variable -R head` | `print /r *head` |

## Things with no clean counterpart

| Feature | Notes |
|---------|-------|
| GDB convenience functions (`$sname(x)`) | No LLDB equivalent; use a summary or a custom command |
| LLDB categories (`type category enable`) | GDB groups printers per objfile instead |
| LLDB `dwim-print` (`p` picking expression vs variable) | GDB `print` always evaluates as an expression |
