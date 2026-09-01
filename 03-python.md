# 3. GDB Python integration

GDB embeds a Python interpreter. The `gdb` module talks to the same session
you used in [01-inspect.md](01-inspect.md) and [02-crash-core.md](02-crash-core.md):
frames, symbols, breakpoints, and `print`. This part automates inspection,
adds commands, and changes how `Student` / `Score` display.

Official reference:
[Python API](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Python.html)
(GDB 7+; current GDB uses Python 3).

Work from this directory (`gdb-learn/`) so `python/` is importable. Helpers:

| File | What it registers |
|------|-------------------|
| `load-python.gdb` | Puts `./python` on `sys.path` |
| `python/student_printers.py` | Pretty-printers for `Student` and `Score` |
| `python/dump_roster.py` | Command `dump-roster` |
| `python/explain_avg.py` | Command `explain-avg` |
| `python/sname.py` | Convenience function `$sname(...)` |
| `python/null_guard.py` | Breakpoint on `announce_top` if `s` is NULL |
| `python/stop_events.py` | Logs stop events (signals / breakpoints) |

This is Python **controlling GDB**, not debugging a `.py` file with `pdb`.

## 0. Check that this GDB has Python

```bash
make gradebook crash_roster
gdb ./gradebook
```

```text
(gdb) python print("hello")
(gdb) python print(gdb.VERSION)
(gdb) show python
```

If `python` is unknown, install a GDB built with Python (`gdb` from
`build-essential` / distro packages on Linux is usually enough).

One-liners vs a block vs a REPL:

```text
(gdb) python print("hello")
(gdb) python
> print(gdb.selected_inferior())
> end
(gdb) python-interactive          # or: pi
>>> 1 + 1
>>> quit()
```

Load the path helper (do this at the start of later steps):

```text
(gdb) source load-python.gdb
```

You can also start with a script:

```bash
gdb -x load-python.gdb ./gradebook
```

## 1. Drive GDB from Python

Stay in `./gradebook`. After `source load-python.gdb`:

```text
(gdb) start
(gdb) python gdb.execute("info locals")
(gdb) python print(gdb.selected_frame().name())
(gdb) python print(gdb.parse_and_eval("roster"))
```

`gdb.execute("bt")` runs a CLI command. `to_string=True` captures output
instead of printing it:

```text
(gdb) python print(gdb.execute("info args", to_string=True))
```

`gdb.parse_and_eval("expr")` is what `print expr` uses: it returns a
`gdb.Value`.

```text
(gdb) break compute_average
(gdb) run
(gdb) python n = gdb.parse_and_eval("n"); print(n, n.type)
(gdb) python print(gdb.parse_and_eval("scores[0].points"))
```

Step the loop a few times (`next`), then:

```text
(gdb) python n=gdb.parse_and_eval("n"); s=gdb.parse_and_eval("sum"); print(float(s)/int(n), float(s)/(int(n)+1))
```

That is the correct average vs the buggy `sum / (n + 1)` without typing
`print` twice.

`gdb.Value` field access:

```text
(gdb) finish
(gdb) python s = gdb.parse_and_eval("s")
(gdb) python print(int(s["id"]), s["name"].string(), float(s["average"]))
```

Invalid memory (NULL `s` in `crash_roster`) raises `gdb.MemoryError`.

| Piece | Role |
|-------|------|
| `gdb.execute("bt")` | Run a CLI command |
| `gdb.parse_and_eval("s->average")` | Expression → `gdb.Value` |
| `gdb.selected_frame()` | Current stack frame |
| `gdb.selected_inferior()` | Process being debugged |
| `gdb.lookup_symbol("roster")` | Symbol lookup |
| `gdb.breakpoints()` | Existing breakpoints |

## 2. Custom command: `explain-avg`

```text
(gdb) python import explain_avg
(gdb) help explain-avg
```

Stop at the **return** of `compute_average` so `sum` is complete:

```text
(gdb) break compute_average
(gdb) run
(gdb) until 66
(gdb) explain-avg
```

Expected idea: `n=4`, `sum` around 363 for Ada, `sum/n` ≈ 90.8,
`sum/(n+1)` ≈ 72.6 (what `gradebook.c` actually returns).

`until 66` is the `return sum / (n + 1);` line in `gradebook.c`. If your
copy differs, `list compute_average` and `until` the `return` line.

## 3. Pretty-printers

Short version here; the full before/after session is
[04-pretty-printers.md](04-pretty-printers.md).

```text
(gdb) python import student_printers
(gdb) break print_roster
(gdb) run
(gdb) print *head
(gdb) print head->scores[0]
(gdb) print head
```

`print *head` uses the `Student` printer. `print head` uses the `Student *`
printer and walks `->next`. `print /r *head` shows the raw struct.

libstdc++ ships printers the same way, which is why `std::vector` looks
readable.

## 4. Walk the list: `dump-roster`

```text
(gdb) python import dump_roster
(gdb) dump-roster head
(gdb) dump-roster roster
```

Use `head` while stopped in `print_roster`, `roster` while stopped in `main`
after the three `push_front`s.

The command is a `gdb.Command` subclass. `help dump-roster` shows the
docstring.

## 5. Convenience function: `$sname`

```text
(gdb) python import sname
(gdb) print $sname(head)
(gdb) print $sname(head->next)
```

`$sname` is a `gdb.Function`. It returns `"(null)"` for a NULL pointer, which
matters in the crash program.

## 6. Python breakpoints: NULL guard

Quit gradebook GDB if it is still open. Start the crash program:

```bash
gdb -x load-python.gdb ./crash_roster
```

```text
(gdb) python import sname
(gdb) python import null_guard
(gdb) info breakpoints
(gdb) run
```

Default `./crash_roster` looks up id 999. `NullGuard.stop()` sees `s == 0`,
prints a message, and **stops** (`return True`) before the process has to
die. Then:

```text
(gdb) print s
(gdb) print $sname(s)
(gdb) frame 1
(gdb) print want_id
(gdb) print chosen
```

`stop()` returning `False` means “log and continue”. Try the success path:

```text
(gdb) set args 103
(gdb) run
```

You should see `announce_top: s is valid, continuing` and the Grace line,
without stopping in the guard.

## 7. Stop events

```text
(gdb) python import stop_events
(gdb) set args
(gdb) run
```

On `SIGSEGV` (if you continue into the NULL deref, or skip the guard), the
handler prints `python event: signal SIGSEGV`. Breakpoint hits log as
`python event: breakpoint hit`.

```python
def on_stop(event):
    if isinstance(event, gdb.SignalEvent):
        print("signal:", event.stop_signal)

gdb.events.stop.connect(on_stop)
```

## 8. Suggested full session (gradebook)

Run from `gdb-learn/`:

```text
gdb -x load-python.gdb ./gradebook
(gdb) python import student_printers
(gdb) python import dump_roster
(gdb) python import explain_avg
(gdb) python import sname
(gdb) break compute_average
(gdb) run
(gdb) python print(gdb.parse_and_eval("n"))
(gdb) until 66
(gdb) explain-avg
(gdb) continue
(gdb) continue
(gdb) continue
(gdb) break print_roster
(gdb) continue
(gdb) print *head
(gdb) dump-roster head
(gdb) print $sname(head)
(gdb) quit
```

Then the crash guard:

```text
gdb -x load-python.gdb ./crash_roster
(gdb) python import sname
(gdb) python import null_guard
(gdb) run
(gdb) print $sname(s)
(gdb) quit
```

## 9. Project `.gdbinit` / auto-load

You can put `source load-python.gdb` in a project `.gdbinit`. GDB may refuse
local init files until you add a safe path, for example in `~/.gdbinit`:

```text
add-auto-load-safe-path /path/to/gdb-learn
```

GDB can also auto-load `binary-gdb.py` next to an objfile. Treat that as
untrusted code; keep auto-load restricted.

## What it is good for

**Good fit:** pretty-printing your structs; walking lists; conditions that
are awkward as `break if`; dumping a roster; scripting a crash recipe.

**Not a replacement for:** compiling with `-g -O0`, or learning frames /
`print` first.

**Not the same as:** `pdb` on a Python program. For that you debug the
Python process (`gdb python`, or `pdb` itself).

Next: [04-pretty-printers.md](04-pretty-printers.md).
