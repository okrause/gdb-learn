# 4. Pretty-printers (Python)

A pretty-printer is a Python object GDB calls instead of dumping a struct
field-by-field. This tutorial uses `python/student_printers.py` with the
`Student` / `Score` types from `gradebook.c`.

Official docs:
[Pretty Printing API](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Pretty-Printing-API.html).

Work from `gdb-learn/` so imports resolve.

## What the example registers

| C type | Printer | `print` looks like |
|--------|---------|----------------------|
| `Score` | `ScorePrinter` | `quiz=90` |
| `Student` | `StudentPrinter` | `Student('Grace', id=103, avg=78.8, n=4)` plus children |
| `Student *` | `StudentListPrinter` | walks `->next` as a list |

`to_string()` is the one-line summary. `children()` is what GDB expands.
`display_hint()` is `"map"` or `"array"` so the CLI formats children like
fields vs an index list.

Registration uses `gdb.printing.register_pretty_printer` (same path
libstdc++ uses for `std::vector`). `info pretty-printer` then shows a
collection named `gradebook`.

## 1. See the default dump (no printer)

```bash
make gradebook
gdb ./gradebook
```

```text
(gdb) break print_roster
(gdb) run
(gdb) print *head
(gdb) print head->scores[0]
(gdb) print head
```

You should get a raw struct: `name`, `id`, `scores` with `label`/`points`,
`n_scores`, `average`, `next`. Keep this GDB session open for the next step
(or `run` again after loading printers).

## 2. Load the printers and print again

```text
(gdb) source load-python.gdb
(gdb) python import student_printers
loaded: pretty-printers Score, Student, Student *
(gdb) info pretty-printer
```

You want `gradebook` in the list (global pretty-printers). Then:

```text
(gdb) print *head
(gdb) print head->scores[0]
(gdb) print head->scores[1]
(gdb) print head
(gdb) print head->next
```

Expected shape (averages are still the **buggy** ones from `gradebook.c`):

```text
(gdb) print *head
$1 = Student('Grace', id=103, avg=78.8, n=4) = {
  ["scores[0]"] = quiz=100,
  ["scores[1]"] = hw=98,
  ["scores[2]"] = mid=97,
  ["scores[3]"] = fin=99,
  ["next"] = 0x...
}

(gdb) print head->scores[0]
$2 = quiz=100

(gdb) print head
$3 = Student linked list = {
  [0] = Student('Grace', ...),
  [1] = Student('Alan', ...),
  [2] = Student('Ada', ...)
}
```

`print *head` uses `Student`. `print head` uses `Student *` and walks the
list. The `Student` printer shows `next` as an address (or `NULL`), not as
another nested list, so `print *head` does not recurse.

## 3. Raw vs pretty, enable vs disable

Force the old dump without unloading the printer:

```text
(gdb) print /r *head
(gdb) print /r head->scores[0]
```

`/r` is “raw” (disable pretty-printing for this command).

Disable only this collection:

```text
(gdb) disable pretty-printer global gradebook
(gdb) print *head
(gdb) enable pretty-printer global gradebook
(gdb) print *head
```

If `disable` cannot find `gradebook`, run `info pretty-printer` and use the
name GDB printed.

## 4. Pointer vs struct, NULL list

```text
(gdb) print (Student *)0
```

The `Student *` printer should report `Student * NULL` instead of
`0x0`. Still in `print_roster`:

```text
(gdb) print head->next->next->next
```

That is Ada’s `next`, which is NULL.

## 5. How the Python objects fit together

Open `python/student_printers.py` while you experiment.

1. `print expr` builds a `gdb.Value`.
2. GDB asks each registered pretty-printer `__call__(val)`.
3. `GradebookPrinter` looks at the type name (`Score`, `Student`,
   `Student *`) and returns a printer instance or `None`.
4. GDB calls `to_string()`, then `children()` if you expand the value.

Minimal printer (only a summary, no children):

```python
class ScorePrinter:
    def __init__(self, val):
        self.val = val

    def to_string(self):
        return f"{self.val['label'].string()}={float(self.val['points']):.0f}"
```

`StudentPrinter.children` yields `(name, gdb.Value)` pairs. Yielding
`scores[i]` (type `Score`) means those children are pretty-printed too.

`StudentListPrinter` walks `node = node["next"]`, with a cycle check and a
16-node cap so a corrupted list cannot hang GDB.

## 6. Suggested session (copy this)

From `gdb-learn/`:

```text
gdb -x load-printers.gdb ./gradebook
(gdb) info pretty-printer
(gdb) break print_roster
(gdb) run
(gdb) print *head
(gdb) print head->scores[0]
(gdb) print head
(gdb) print /r *head
(gdb) disable pretty-printer global gradebook
(gdb) print *head
(gdb) enable pretty-printer global gradebook
(gdb) print (Student *)0
(gdb) quit
```

`load-printers.gdb` is `load-python.gdb` plus `import student_printers`.

## 7. Reload after you edit the printer

If you change `python/student_printers.py` in another window:

```text
(gdb) python import importlib, student_printers; importlib.reload(student_printers)
```

`register_pretty_printer(..., replace=True)` replaces the previous
`gradebook` collection so you should not get duplicates.

## Next

You can combine this with [03-python.md](03-python.md): `dump-roster` walks
the list as a command; the `Student *` printer walks it when you `print`.
