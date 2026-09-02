# 2. Analyze a crash and core dump

`crash_roster.c` looks up a student and passes the result to `announce_top`
without checking for `NULL`. A core dump is a snapshot of a process at the
moment it died. You need the dump and the exact binary that created it.

```bash
make crash_roster
```

| Run | Result |
|-----|--------|
| `./crash_roster` | Looks up missing ID 999 and dereferences `NULL` |
| `./crash_roster 103` | Prints Grace and exits successfully |
| `./crash_roster uaf` | Uses a pointer after freeing the list |

## Inspect the live crash

```text
lldb ./crash_roster
(lldb) run
```

LLDB stops on `SIGSEGV` in `announce_top`. Inspect the failure:

```text
(lldb) bt
(lldb) frame variable
(lldb) p s
(lldb) p s->name
(lldb) frame select 1
(lldb) frame variable want_id chosen roster
(lldb) p *roster
(lldb) disassemble -p
(lldb) register read
```

Confirm that:

- `s` and `chosen` are zero
- `want_id` is 999
- `roster` still points to Grace, Alan, and Ada
- the current instruction reads through the invalid pointer

Register names depend on the CPU, not the debugger. On x86-64, function
arguments often appear in `$rdi`, `$rsi`, and later registers. On AArch64
(including Apple Silicon), begin with `$x0`.

To stop on `SIGSEGV` without passing it to the program:

```text
(lldb) process handle -p false -s true -n true SIGSEGV
(lldb) run
```

GDB reference:

```text
gdb ./crash_roster
(gdb) handle SIGSEGV stop print nopass
(gdb) run
(gdb) bt
(gdb) info args
(gdb) frame 1
(gdb) info locals
```

Continuing a live process after the fatal signal normally lets it terminate.
A process loaded from a core is already dead, so it cannot step or continue.

## What is in a core

A core may contain thread stacks, registers, and mapped memory. Debug symbols
remain in the executable, so keep the exact unstripped binary from the crash:

```text
lldb ./crash_roster -c crash_roster.core
```

GDB loads the same pair with:

```text
gdb ./crash_roster crash_roster.core
```

## Generate a core on Linux

Kernel core dumps are often disabled. Enable them in the shell that launches
the program:

```bash
ulimit -c unlimited
ulimit -c
./crash_roster
ls -l core core.*
```

If no file appears, inspect:

```bash
cat /proc/sys/kernel/core_pattern
```

| Pattern | Destination |
|---------|-------------|
| `core` | `./core` |
| `core.%p` | `./core.<pid>` |
| `core.%e.%p` | `./core.crash_roster.<pid>` |
| `|...apport...` | Ubuntu apport handles the dump |
| `|...systemd-coredump` | Retrieve it with `coredumpctl` |

A leading `|` pipes the dump to a service rather than writing it in the
current directory.

### systemd-coredump

```bash
coredumpctl list crash_roster
coredumpctl debug crash_roster
coredumpctl dump crash_roster -o ./crash_roster.core
lldb ./crash_roster -c ./crash_roster.core
```

### Ubuntu apport

```bash
ls /var/crash
apport-unpack /var/crash/_*.crash /tmp/crash-unpacked
lldb ./crash_roster -c /tmp/crash-unpacked/CoreDump
```

### Change the kernel filename pattern

Only do this on a machine where changing the system-wide setting is
appropriate:

```bash
echo 'core.%e.%p' | sudo tee /proc/sys/kernel/core_pattern
ulimit -c unlimited
./crash_roster
ls -l core.crash_roster.*
```

## Save a core from LLDB

This avoids dependence on the kernel's core-file destination:

```text
lldb ./crash_roster
(lldb) run
# after SIGSEGV:
(lldb) process save-core crash_roster.core
(lldb) quit
lldb ./crash_roster -c crash_roster.core
```

GDB uses `generate-core-file crash_roster.core`.

## macOS notes

macOS does not have `/proc`, systemd-coredump, or apport. Fatal crashes
normally create `.ips` reports under `~/Library/Logs/DiagnosticReports/`;
those reports are useful for symbolication but are not LLDB core files.

For this tutorial, prefer `process save-core` after LLDB catches the live
crash. System-generated cores, when enabled with `ulimit -c unlimited`, are
normally written under `/cores` according to `sysctl kern.corefile`. Host
security settings can still prevent their creation.

## Post-mortem inspection

```text
lldb ./crash_roster -c crash_roster.core
(lldb) bt
(lldb) frame select 0
(lldb) frame variable
(lldb) p s
(lldb) type lookup Student
(lldb) frame select 1
(lldb) frame variable want_id chosen roster
(lldb) register read
(lldb) disassemble -p
(lldb) thread backtrace all
```

Use `memory read`, `expression`, `disassemble`, and frame navigation normally.
Only execution commands are unavailable.

## Optional use-after-free path

```text
lldb ./crash_roster
(lldb) settings set target.run-args uaf
(lldb) breakpoint set -n announce_top
(lldb) run
(lldb) frame variable s
(lldb) p s->name
(lldb) memory read -c 32 -f x -s 1 s
```

The pointer is non-NULL but no longer owns live storage. It may display old
data, garbage, or fault. GDB uses `set args uaf`, `break announce_top`, and
`x/32xb s`.

## Read the bug from the evidence

1. `main` sets `want_id` to 999.
2. `find_by_id` reaches the end of the list and returns `NULL`.
3. `announce_top(NULL)` reads `s->name` and faults.

The eventual source fix is a `chosen == NULL` check before `announce_top`.
Keep the bug while completing the remaining debugger exercises.

Next: [LLDB Python integration](03-python.md).
