# 3. LLDB Python integration

LLDB embeds Python and exposes the debugger through the `lldb` module.
Scripts can inspect `SBValue` objects, add commands, attach callbacks to
breakpoints, and control data formatting.

Official reference: [LLDB Python API](https://lldb.llvm.org/python_api.html).

Run from the repository root. The primary helpers are:

| File | Registers |
|------|-----------|
| `lldb/commands.lldb` | `dump-roster` and `explain-avg` |
| `lldb/formatters.lldb` | `Score`, `Student`, and `Student *` formatters |
| `lldb/lldbinit` | Commands and formatters together |
| `lldb/nullguard.lldb` | Conditional Python callback for `announce_top` |
| `lldb/stop-hook.lldb` | A command that runs after every stop |

This is Python controlling LLDB, not Python's `pdb`.

## Check Python support

```bash
make gradebook crash_roster
lldb ./gradebook
```

```text
(lldb) script print("hello")
(lldb) script import lldb; print(lldb.debugger.GetVersionString())
(lldb) script
>>> 1 + 1
>>> quit()
```

`script <code>` runs one line. `script` alone opens a Python REPL.

GDB reference: `python print("hello")` runs one line and
`python-interactive` opens its REPL.

## Load the tutorial helpers

Start with all normal gradebook helpers:

```bash
lldb -s lldb/lldbinit ./gradebook
```

Or load pieces in an existing session:

```text
(lldb) command source lldb/commands.lldb
(lldb) command source lldb/formatters.lldb
```

For GDB, use `gdb -x gdb/load-python.gdb ./gradebook`, then import modules
from `gdb/python/`.

## Drive LLDB from Python

Stop in `main`, then obtain the selected frame:

```text
(lldb) breakpoint set -n main
(lldb) run
(lldb) script target=lldb.debugger.GetSelectedTarget(); process=target.GetProcess(); frame=process.GetSelectedThread().GetSelectedFrame(); print(frame.GetFunctionName())
(lldb) script print(frame.FindVariable("roster"))
```

Run an LLDB command:

```text
(lldb) script lldb.debugger.HandleCommand("frame variable")
```

Evaluate a C expression and inspect the resulting `SBValue`:

```text
(lldb) breakpoint set -n compute_average
(lldb) continue
(lldb) script frame=lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
(lldb) script n=frame.FindVariable("n"); print(n.GetValueAsSigned(), n.GetTypeName())
(lldb) script score=frame.EvaluateExpression("scores[0].points"); print(score.GetValue())
```

Refresh `frame` after selecting a different frame or stopping again:

```text
(lldb) script frame=lldb.debugger.GetSelectedTarget().GetProcess().GetSelectedThread().GetSelectedFrame()
```

Useful API objects:

| Python | Role |
|--------|------|
| `lldb.debugger.GetSelectedTarget()` | Current `SBTarget` |
| `target.GetProcess()` | Current `SBProcess` |
| `thread.GetSelectedFrame()` | Current `SBFrame` |
| `frame.FindVariable("n")` | Variable as an `SBValue` |
| `frame.EvaluateExpression("sum / n")` | Evaluate C and return `SBValue` |
| `debugger.HandleCommand("bt")` | Run a CLI command |

Unlike GDB, invalid memory usually produces an invalid `SBValue` or an
`SBError`; check `value.IsValid()` and `value.GetError().Success()`.
GDB's closest APIs are `gdb.selected_frame()`, `gdb.parse_and_eval()`, and
`gdb.execute()`.

## Custom command: `explain-avg`

`lldb/python/explain_avg.py` registers a plain Python function as an LLDB
command:

```text
(lldb) command source lldb/commands.lldb
(lldb) breakpoint set -n compute_average
(lldb) run
(lldb) thread until 52
(lldb) explain-avg
```

For Ada, expect a sum near 363, a correct average near 90.8, and the buggy
average near 72.6.

The GDB reference implementation is `gdb/python/explain_avg.py`:

```text
(gdb) source gdb/load-python.gdb
(gdb) python import explain_avg
(gdb) explain-avg
```

LLDB commands conventionally use a function with the signature
`(debugger, command, result, internal_dict)` and register it from
`__lldb_init_module`.

## Walk the list with `dump-roster`

Stop where a list variable is visible:

```text
(lldb) breakpoint set -n print_roster
(lldb) run
(lldb) dump-roster head
```

The command follows `next`, detects cycles, and stops after 16 nodes so a
corrupted list cannot hang the debugger.

GDB loads the corresponding `gdb/python/dump_roster.py` module and uses the
same `dump-roster head` command.

## Python breakpoint callback: NULL guard

```bash
lldb -s lldb/nullguard.lldb ./crash_roster
```

```text
(lldb) breakpoint list
(lldb) run
```

The callback returns `True` when `s` is NULL, stopping before the crash. It
returns `False` for a valid value, which auto-continues:

```text
(lldb) settings set target.run-args 103
(lldb) run
```

GDB's `gdb/python/null_guard.py` subclasses `gdb.Breakpoint` and implements
`stop()`. The effect is the same even though the APIs differ.

## Run a command after every stop

```text
(lldb) command source lldb/stop-hook.lldb
(lldb) target stop-hook list
(lldb) breakpoint set -n compute_average
(lldb) run
```

The hook runs `frame info` after each stop. Delete it with
`target stop-hook delete 1`.

GDB's event API can distinguish typed events:

```text
(gdb) source gdb/load-python.gdb
(gdb) python import stop_events
```

LLDB stop hooks are command lists rather than a direct equivalent of
`gdb.events.stop.connect`.

## No LLDB convenience functions

GDB can register `$sname(head)` through `gdb.Function`. LLDB has no matching
`$function(...)` extension point. Use the `Student *` summary from the next
lesson, `dump-roster`, or a custom LLDB command instead.

## Init files and trust

`lldb -s lldb/lldbinit` explicitly loads this project's command file.
`~/.lldbinit` is automatically loaded for all sessions; only source scripts
you trust. LLDB normally warns rather than loading a `.lldbinit` from the
current directory unless `target.load-cwd-lldbinit` is enabled. This tutorial
uses an explicit `-s` command file so loading is always intentional.

GDB uses `~/.gdbinit` and has an `add-auto-load-safe-path` allow-list for
local auto-load files.

Next: [LLDB data formatters](04-pretty-printers.md).
