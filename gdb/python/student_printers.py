"""GDB pretty-printers for Score, Student, and Student * (linked list).

GDB calls the collection for every value it needs to display. Return a
printer object, or None to fall back to the default struct dump.

Load with:
    (gdb) source gdb/load-python.gdb
    (gdb) python import student_printers
"""

import gdb
import gdb.printing

MAX_NODES = 16


class ScorePrinter:
    """One-line 'quiz=90' instead of {label = "quiz", points = 90}."""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        label = self.val["label"].string()
        points = float(self.val["points"])
        return f"{label}={points:.0f}"


class StudentPrinter:
    """Summary line plus the scores in use and next as a leaf."""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        name = self.val["name"].string()
        sid = int(self.val["id"])
        avg = float(self.val["average"])
        n = int(self.val["n_scores"])
        return f"Student({name!r}, id={sid}, avg={avg:.1f}, n={n})"

    def children(self):
        n = int(self.val["n_scores"])
        scores = self.val["scores"]
        for i in range(n):
            yield (f"scores[{i}]", scores[i])
        # Printed as an address so expanding a Student does not recurse
        # into the whole list.
        nxt = self.val["next"]
        yield ("next", "NULL" if int(nxt) == 0 else str(nxt))

    def display_hint(self):
        return "map"


class StudentListPrinter:
    """Print Student * by walking ->next (stops on NULL, cycle, or cap)."""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        if int(self.val) == 0:
            return "Student * NULL"
        return "Student linked list"

    def children(self):
        node = self.val
        seen = set()
        i = 0
        while node and int(node) != 0:
            addr = int(node)
            if addr in seen:
                yield (f"[{i}]", "cycle")
                break
            seen.add(addr)
            yield (f"[{i}]", node.dereference())
            node = node.dereference()["next"]
            i += 1
            if i >= MAX_NODES:
                yield ("[...]", "truncated")
                break

    def display_hint(self):
        return "array"


def _type_name(val):
    try:
        t = val.type.strip_typedefs().unqualified()
    except Exception:
        return None
    if t.code == gdb.TYPE_CODE_PTR:
        inner = t.target().strip_typedefs().unqualified()
        inner_name = inner.name or inner.tag
        return inner_name + " *" if inner_name else None
    return t.name or t.tag


class GradebookPrinter(gdb.printing.PrettyPrinter):
    """Named collection so 'info pretty-printer' shows 'gradebook'."""

    def __init__(self):
        super(GradebookPrinter, self).__init__("gradebook")

    def __call__(self, val):
        name = _type_name(val)
        if name == "Score":
            return ScorePrinter(val)
        if name == "Student":
            return StudentPrinter(val)
        if name == "Student *":
            return StudentListPrinter(val)
        return None


gdb.printing.register_pretty_printer(None, GradebookPrinter(), replace=True)
print("loaded: GDB pretty-printers for Score, Student, Student *")
