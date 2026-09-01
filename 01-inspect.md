# 1. Inspect a running program

Program: `gradebook.c`. It builds a linked list of students, each with nested
`Score` structs. **Averages are wrong on purpose** (`sum / (n + 1)` instead of
`sum / n`) so you have something real to inspect.

```bash
make gradebook
gdb ./gradebook
```

## Load, list, run

| Command | What it does |
|---------|----------------|
| `file ./gradebook` | Load a binary (already done if you started `gdb ./gradebook`) |
| `list` / `list main` / `l 49,67` | Show source |
| `run` / `r` | Start from the beginning |
| `start` | Run and stop at the first line of `main` |
| `quit` / `q` | Exit |

```text
(gdb) list main
(gdb) start
```

You should stop in `main` with `roster` still `NULL`.

## Breakpoints

| Command | What it does |
|---------|----------------|
| `break main` | Stop at function entry |
| `break gradebook.c:66` | Stop at a line |
| `break compute_average` | Stop every time that function runs |
| `break compute_average if n == 4` | Conditional |
| `info breakpoints` | List them |
| `delete 1` / `disable 1` / `enable 1` | Manage them |
| `tbreak compute_average` | One-shot breakpoint |

```text
(gdb) break compute_average
(gdb) break find_top
(gdb) info breakpoints
(gdb) run
```

You hit `compute_average` first (Ada is built first). `continue` (`c`) hits it
again for Alan and Grace.

## Stepping vs running

| Command | What it does |
|---------|----------------|
| `next` / `n` | Next **line in this function** (does not enter callees) |
| `step` / `s` | Step **into** a function call |
| `finish` | Run until the **current function returns** |
| `until 90` | Run until that line (useful to skip a loop) |
| `continue` / `c` | Run until the next breakpoint |
| `stepi` / `nexti` | Step one **machine instruction** |

Rule of thumb: `next` to skim, `step` when you want to see inside
`compute_average` or `make_student`.

From `main`:

```text
(gdb) start
(gdb) next          # skip declarations
(gdb) next          # until push_front / make_student
(gdb) step          # into make_student
(gdb) next
(gdb) step          # into compute_average
```

## Looking up values

Stop inside `compute_average` (`break compute_average` then `run`).

```text
(gdb) info args
(gdb) info locals
(gdb) print n
(gdb) print sum
(gdb) print i
(gdb) print scores[0]
(gdb) print scores[0].points
(gdb) print scores[0].label
(gdb) print *scores@n          # GDB array slice: n Score objects
```

Formats:

```text
(gdb) p/x n            # hex
(gdb) p/t n            # binary
(gdb) p/f sum          # float
(gdb) p (int)sum
(gdb) whatis scores
(gdb) ptype Student    # full struct layout
(gdb) ptype Score
```

Watch a value update as you step:

```text
(gdb) display sum
(gdb) display i
(gdb) next
(gdb) next
```

`display` reprints those expressions after every stop. `undisplay 1` removes
one.

Walk the linked list after the three `push_front`s (for example at
`print_roster`):

```text
(gdb) break print_roster
(gdb) run
(gdb) print *head
(gdb) print *head->next
(gdb) print head->next->next->name
(gdb) print head->scores[2].points
(gdb) p head->average
(gdb) p head->n_scores
```

Examine raw memory:

```text
(gdb) x/s head->name            # C string at that address
(gdb) x/16xb head               # 16 bytes of the struct in hex
```

`x` syntax: `x/<count><format><size>`  
formats: `x` hex, `d` decimal, `f` float, `s` string, `i` instruction.

## Call stack

`compute_average` is not called from `main` directly:

```text
(gdb) backtrace
(gdb) bt full          # locals in every frame
(gdb) frame 1          # jump to make_student
(gdb) info locals
(gdb) print name
(gdb) print *s
(gdb) up
(gdb) down
```

When you stop in `find_top`, `bt` shows **recursion**. Use `frame N` and
`print head->name` in each frame.

## Watchpoints

```text
(gdb) break compute_average
(gdb) run
(gdb) watch sum
(gdb) continue
```

GDB stops whenever `sum` is written. Local watchpoints expire when the
function returns — that is expected.

Inside `make_student`:

```text
(gdb) watch s->average
```

stops when the buggy average is stored.

## Confirm the bug, then change state

Inside `compute_average`, after the loop (`until` the `return` line):

```text
(gdb) print sum
(gdb) print n
(gdb) print sum / n          # correct average
(gdb) print sum / (n + 1)    # what the code does
(gdb) return sum / n         # force the correct return this time
```

Grace’s scores are `100, 98, 97, 99` → sum `394`. Correct avg `98.5`. The
program prints `78.8` because `394 / 5`.

Fix in source:

```c
return sum / n;   /* not (n + 1) */
```

Rebuild (`make gradebook`) and `run` again in the same GDB session; GDB
reloads the new binary.

## Extra commands

| Command | What it does |
|---------|----------------|
| `info functions` | List symbols |
| `info variables` | Globals |
| `info registers` | CPU registers |
| `disassemble compute_average` | Machine code |
| `layout src` | TUI: source + command pane (`Ctrl-X A` to leave) |
| `set args foo bar` | `argc` / `argv` (this demo has none) |
| `call printf("%s\n", head->name)` | Call a function from the debugger |

## Suggested first session

```text
gdb ./gradebook
(gdb) list compute_average
(gdb) break compute_average
(gdb) run
(gdb) info args
(gdb) info locals
(gdb) ptype Score
(gdb) print *scores@n
(gdb) display sum
(gdb) next
(gdb) next
(gdb) next
(gdb) print sum / n
(gdb) print sum / (n + 1)
(gdb) finish
(gdb) print s->name
(gdb) print s->average
(gdb) continue          # Alan
(gdb) continue          # Grace
(gdb) break find_top
(gdb) continue
(gdb) backtrace
(gdb) print head->name
(gdb) continue          # recurse
(gdb) bt
(gdb) quit
```

Unfixed run (what you should see without GDB):

```text
 103  Grace           78.8  quiz=100,hw=98,mid=97,fin=99
 102  Alan            58.6  quiz=70,hw=75,mid=68,fin=80
 101  Ada             72.6  quiz=90,hw=88,mid=94,fin=91
Top student: Grace (avg 78.8)
```

After you fix the divisor, Grace should be about **98.5**.

Next: [02-crash-core.md](02-crash-core.md), then [03-python.md](03-python.md).
