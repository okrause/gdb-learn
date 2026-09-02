# 4. LLDB data formatters

LLDB calls one-line displays *summaries* and customized child views
*synthetic providers*. Together they fill the role of a GDB pretty-printer.
This lesson uses `lldb/python/student_formatters.py`.

Official reference:
[LLDB variable formatting](https://lldb.llvm.org/use/variable.html).

## What the example registers

| C type | Summary | Synthetic children |
|--------|---------|--------------------|
| `Score` | `quiz=90` | Default fields |
| `Student` | `Student('Grace', id=103, avg=78.8, n=4)` | Used scores plus `next` |
| `Student *` | `Student list (3 nodes)` | Students reached through `next` |

The registrations belong to the `gradebook` category, so they can be enabled,
disabled, and deleted as a group.

## See the default values

```bash
make gradebook
lldb ./gradebook
```

```text
(lldb) breakpoint set -n print_roster
(lldb) run
(lldb) frame variable head
(lldb) p *head
(lldb) p head->scores[0]
```

Without custom formatters LLDB shows all struct fields.

## Load the formatters

In the same session:

```text
(lldb) command source lldb/formatters.lldb
(lldb) type summary list
(lldb) type synthetic list
(lldb) type category list
```

Or start with:

```bash
lldb -s lldb/formatters.lldb ./gradebook
```

Print the values again:

```text
(lldb) frame variable head
(lldb) p *head
(lldb) p head->scores[0]
(lldb) p head
```

The expected shape is:

```text
(Student *) head = 0x... Student list (3 nodes) {
  [0] = Student('Grace', id=103, avg=78.8, n=4) {...}
  [1] = Student('Alan', id=102, avg=58.6, n=4) {...}
  [2] = Student('Ada', id=101, avg=72.6, n=4) {...}
}
```

Exact punctuation varies by LLDB version. The important parts are the summary,
the three linked students, and only the active scores.

## Raw values and category control

Bypass synthetic children and summaries:

```text
(lldb) frame variable -R head
(lldb) frame variable -R *head
```

Disable and re-enable the entire formatter group:

```text
(lldb) type category disable gradebook
(lldb) frame variable head
(lldb) type category enable gradebook
(lldb) frame variable head
```

`type category delete gradebook` removes its registrations from the session.

GDB reference:

```text
gdb -x gdb/load-printers.gdb ./gradebook
(gdb) info pretty-printer
(gdb) print head
(gdb) print /r *head
(gdb) disable pretty-printer global gradebook
(gdb) enable pretty-printer global gradebook
```

## Pointer, struct, and NULL

`Student` and `Student *` have different formatters. The pointer formatter
walks the list, while the struct formatter displays one student:

```text
(lldb) p *head
(lldb) p head
(lldb) p (Student *)0
```

The final command should show `Student * NULL`. The list walk tracks visited
addresses and caps output at 16 nodes, which prevents a corrupt cycle from
hanging LLDB.

## How the Python pieces fit

When LLDB displays a value:

1. A summary function receives an `SBValue` and returns text.
2. A synthetic-provider object receives the same value.
3. `update()` refreshes cached children after a stop.
4. `num_children()` and `get_child_at_index()` expose the custom view.

A summary is small:

```python
def score_summary(valobj, internal_dict):
    raw = valobj.GetNonSyntheticValue()
    label = raw.GetChildMemberWithName("label").GetSummary().strip('"')
    points = float(raw.GetChildMemberWithName("points").GetValue())
    return f"{label}={points:.0f}"
```

The module's `__lldb_init_module` function registers summaries and synthetic
providers when `command script import` loads it.

GDB combines the one-line text and children in one pretty-printer object with
`to_string()` and `children()`. See `gdb/python/student_printers.py`.

## Reload after editing

LLDB can reload a Python command script:

```text
(lldb) command script import --allow-reload lldb/python/student_formatters.py
```

The module first replaces the named category, preventing duplicate
registrations. Restarting LLDB is also a reliable clean reload.

## Suggested session

```text
lldb -s lldb/formatters.lldb ./gradebook
(lldb) breakpoint set -n print_roster
(lldb) run
(lldb) type category list
(lldb) p *head
(lldb) p head->scores[0]
(lldb) p head
(lldb) frame variable -R head
(lldb) type category disable gradebook
(lldb) frame variable head
(lldb) type category enable gradebook
(lldb) p (Student *)0
(lldb) quit
```

Use [cheatsheet.md](cheatsheet.md) when translating another GDB workflow.
