# LLDB tutorial

This tutorial teaches native-code debugging with LLDB. It uses two small C
programs and keeps the equivalent GDB commands as a reference.

The main instructions target Linux. macOS notes are included where process
launching, signals, or core dumps differ.

## Requirements

- A C compiler and `make`
- LLDB
- Optional: GDB for the reference commands

On Debian or Ubuntu:

```bash
sudo apt install build-essential lldb gdb
```

On macOS, install the Xcode command-line tools:

```bash
xcode-select --install
```

## Files

| Path | Role |
|------|------|
| `gradebook.c` | Linked list of students; averages are wrong on purpose |
| `crash_roster.c` | Similar data model; the default run hits `SIGSEGV` |
| `01-inspect.md` | Breakpoints, stepping, values, memory, and stack frames |
| `02-crash-core.md` | Live crash analysis and Linux core dumps |
| `03-python.md` | LLDB's Python API, commands, and breakpoint callbacks |
| `04-pretty-printers.md` | LLDB summaries and synthetic children |
| `lldb/` | Primary LLDB command files and Python helpers |
| `gdb/` | Equivalent GDB helpers retained as reference |
| `cheatsheet.md` | LLDB-to-GDB command mapping |
| `Makefile` | Builds both programs with debug information |

Run commands from the repository root so the command files can resolve paths
such as `lldb/python/`.

## Build

```bash
make
```

Equivalent:

```bash
cc -g -O0 -Wall -o gradebook gradebook.c
cc -g -O0 -Wall -o crash_roster crash_roster.c
```

`-g` emits symbols, source locations, and variable information. `-O0` keeps
the generated code close to the source, which makes stepping easier to follow.

## Run without a debugger

```bash
./gradebook              # prints deliberately incorrect averages
./crash_roster 103       # prints Grace and exits successfully
./crash_roster           # crashes by dereferencing NULL
```

## Tutorial order

1. [Inspect a running program](01-inspect.md): `lldb ./gradebook`
2. [Analyze a crash and core dump](02-crash-core.md): `lldb ./crash_roster`
3. [Automate LLDB with Python](03-python.md)
4. [Add data formatters](04-pretty-printers.md)

Inside LLDB, `(lldb)` is the prompt. Use `help`, `help breakpoint set`, and
`apropos <word>` to discover commands. Tab completion is available.

## GDB reference

Each lesson includes a compact GDB equivalent. The complete command mapping is
in [cheatsheet.md](cheatsheet.md), and runnable GDB scripts are under `gdb/`.
For example:

```bash
gdb -x gdb/load-python.gdb ./gradebook
gdb -x gdb/load-printers.gdb ./gradebook
```
