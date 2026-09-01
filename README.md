# GNU GDB tutorial

Copy this directory to a Linux machine and work through the markdown files
in order. You need `gcc` and `gdb` (`sudo apt install build-essential gdb` on
Debian/Ubuntu).

## Files

| File | Role |
|------|------|
| `gradebook.c` | Linked list of students; averages are wrong on purpose |
| `crash_roster.c` | Same data model; default run hits `SIGSEGV` |
| `01-inspect.md` | Load, run, step, print variables, stack |
| `02-crash-core.md` | Live crash, then generate and load a core dump yourself |
| `03-python.md` | GDB Python API: commands, printers, breakpoints |
| `04-pretty-printers.md` | Pretty-printers for `Score`, `Student`, `Student *` |
| `load-python.gdb` | Puts `./python` on Python's `sys.path` |
| `load-printers.gdb` | Path helper plus `import student_printers` |
| `python/` | Example pretty-printers, commands, and hooks |
| `Makefile` | `make` builds both programs with `-g -O0` |

Do not commit binaries or core files. This folder is only a tutorial pack.

## Build

```bash
cd gdb-learn
make
```

Equivalent:

```bash
gcc -g -O0 -o gradebook gradebook.c
gcc -g -O0 -o crash_roster crash_roster.c
```

`-g` embeds file names, line numbers, and variable names. `-O0` keeps each C
line as a distinct instruction so `next` / `step` match the source.

## Run without GDB

```bash
./gradebook              # prints too-low averages (bug)
./crash_roster 103       # prints Grace, exits 0
./crash_roster           # segfault (exit 139)
```

## Order

1. [01-inspect.md](01-inspect.md) — `gdb ./gradebook`
2. [02-crash-core.md](02-crash-core.md) — crash, then produce a core dump on
   that Linux box (none is included here)
3. [03-python.md](03-python.md) — Python integration with the same programs
4. [04-pretty-printers.md](04-pretty-printers.md) — `print` via Python printers

Inside GDB, `(gdb)` is the prompt. `help` and `help running` work. Tab
completion works.
