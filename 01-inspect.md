# 1. Inspect a running program

`gradebook.c` builds a linked list of students and nested `Score` values.
Its average is deliberately wrong: it divides by `n + 1` instead of `n`.

```bash
make gradebook
lldb ./gradebook
```

## Load, list, and run

| Task | LLDB | GDB reference |
|------|------|---------------|
| Load a binary | `target create ./gradebook` | `file ./gradebook` |
| List a function | `source list -n main` | `list main` |
| Run | `run` | `run` |
| Stop at `main` | `breakpoint set -n main`, then `run` | `start` |
| Quit | `quit` | `quit` |

Try:

```text
(lldb) source list -n main
(lldb) breakpoint set -n main
(lldb) run
```

You should stop in `main` while `roster` is still `NULL`.

## Breakpoints

| Task | LLDB | GDB reference |
|------|------|---------------|
| Function | `breakpoint set -n compute_average` | `break compute_average` |
| Source line | `breakpoint set -f gradebook.c -l 52` | `break gradebook.c:52` |
| Conditional | `breakpoint set -n compute_average -c 'n == 4'` | `break compute_average if n == 4` |
| One-shot | `breakpoint set -o true -n find_top` | `tbreak find_top` |
| List | `breakpoint list` | `info breakpoints` |
| Manage ID 1 | `breakpoint delete 1`, `disable 1`, `enable 1` | `delete 1`, `disable 1`, `enable 1` |

```text
(lldb) breakpoint set -n compute_average
(lldb) breakpoint set -n find_top
(lldb) breakpoint list
(lldb) run
```

`continue` (`c`) reaches later calls.

## Step through code

| Task | LLDB | GDB reference |
|------|------|---------------|
| Step over a call | `thread step-over` or `n` | `next` |
| Step into a call | `thread step-in` or `s` | `step` |
| Finish the frame | `thread step-out` or `finish` | `finish` |
| Run to a line | `thread until 52` | `until 52` |
| Continue | `continue` or `c` | `continue` |
| One instruction | `thread step-inst` | `stepi` |

Use `n` to skim and `s` to enter `make_student` or `compute_average`.

## Inspect values and types

Stop in `compute_average`:

```text
(lldb) frame variable
(lldb) frame variable n sum i
(lldb) p scores[0]
(lldb) p scores[0].points
(lldb) p scores[0].label
(lldb) parray n scores
```

`frame variable` reads known variables without running arbitrary code.
`expression` (alias `p`) evaluates a C expression.

```text
(lldb) expression -f hex -- n
(lldb) expression -f binary -- n
(lldb) expression -f float -- sum
(lldb) frame variable -T scores
(lldb) type lookup Student
(lldb) type lookup Score
```

GDB equivalents are `info args`, `info locals`, `print`, `print *scores@n`,
`whatis`, and `ptype`.

To display a value after every stop, use a stop hook:

```text
(lldb) target stop-hook add -o "frame variable sum i"
(lldb) target stop-hook list
(lldb) target stop-hook delete 1
```

GDB uses `display sum` and `undisplay <number>`.

## Walk the linked list

```text
(lldb) breakpoint set -n print_roster
(lldb) run
(lldb) frame variable head
(lldb) p *head
(lldb) p *head->next
(lldb) p head->next->next->name
(lldb) p head->scores[2].points
```

Examine raw memory:

```text
(lldb) memory read -f c-string head->name
(lldb) memory read -c 16 -f x -s 1 head
```

LLDB also provides the GDB-compatible alias `x/16xb head`.

## Stack frames and recursion

```text
(lldb) bt
(lldb) frame select 1
(lldb) frame variable
(lldb) up
(lldb) down
```

GDB's `bt full` prints locals for all frames in one command. In LLDB, use
`bt`, select interesting frames, and run `frame variable`. When stopped in
`find_top`, the backtrace shows its recursive calls.

## Watchpoints

```text
(lldb) breakpoint set -n compute_average
(lldb) run
(lldb) watchpoint set variable sum
(lldb) continue
```

Inside `make_student`, `watchpoint set expression -- s->average` stops when
the average is stored. Hardware watchpoints are limited, and a watchpoint on a
local variable expires after its stack frame returns.

GDB uses `watch sum` and `watch s->average`.

## Confirm the bug and override one return

At the return line in `compute_average`:

```text
(lldb) thread until 52
(lldb) p sum
(lldb) p n
(lldb) p sum / n
(lldb) p sum / (n + 1)
(lldb) thread return sum / n
```

Grace's scores total 394. The correct average is 98.5, while the program
returns 78.8. `thread return` forces the scalar return value for this call.
GDB's equivalent is `return sum / n`.

The source fix is:

```c
return sum / n;
```

Do not apply it until you finish the exercises that rely on the bug.

## Useful extras

| Task | LLDB | GDB reference |
|------|------|---------------|
| Find a symbol | `image lookup -n compute_average` | `info functions compute_average` |
| Registers | `register read` | `info registers` |
| Disassemble | `disassemble -n compute_average` | `disassemble compute_average` |
| Curses UI | `gui` | `layout src` |
| Set arguments | `settings set target.run-args foo bar` | `set args foo bar` |
| Call a function | `expression (void)printf("%s\n", head->name)` | `call printf("%s\n", head->name)` |

Next: [Crash and core dumps](02-crash-core.md).
