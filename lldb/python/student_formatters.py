"""LLDB data formatters for Score, Student, and Student * (linked list).

A "summary" is the one-line text LLDB shows for a value. A "synthetic
provider" replaces the children LLDB shows when the value is expanded.
Together they are the LLDB counterpart of a GDB pretty-printer.

Load with:
    (lldb) command script import lldb/python/student_formatters.py

__lldb_init_module registers everything, so the import is all you need.
"""

import lldb


MAX_NODES = 16


def _cstr(val):
    """Read a char[] SBValue as a Python str.

    GetSummary returns the quoted form, e.g. '"Grace"'.
    """
    summary = val.GetSummary()
    if not summary:
        return ""
    return summary.strip('"')


def _float(val):
    """SBValue holding a float -> Python float.

    SBValue has no GetValueAsDouble, so parse the printed value.
    """
    try:
        return float(val.GetValue())
    except (TypeError, ValueError):
        return 0.0


def _walk(ptr_val):
    """Follow ->next from a Student * and return the node values.

    Stops on NULL, on a cycle, or after MAX_NODES so a corrupted list
    cannot hang the debugger.
    """
    nodes = []
    seen = set()
    node = ptr_val.GetNonSyntheticValue()

    while node.IsValid() and node.GetValueAsUnsigned(0) != 0:
        addr = node.GetValueAsUnsigned(0)
        if addr in seen or len(nodes) >= MAX_NODES:
            break
        seen.add(addr)
        student = node.Dereference()
        nodes.append(student)
        node = student.GetNonSyntheticValue().GetChildMemberWithName("next")

    return nodes


def score_summary(valobj, internal_dict):
    """'quiz=90' instead of (label = "quiz", points = 90)."""
    raw = valobj.GetNonSyntheticValue()
    label = _cstr(raw.GetChildMemberWithName("label"))
    points = _float(raw.GetChildMemberWithName("points"))
    return f"{label}={points:.0f}"


def student_summary(valobj, internal_dict):
    """One-line description of a Student."""
    raw = valobj.GetNonSyntheticValue()
    name = _cstr(raw.GetChildMemberWithName("name"))
    sid = raw.GetChildMemberWithName("id").GetValueAsSigned()
    avg = _float(raw.GetChildMemberWithName("average"))
    n = raw.GetChildMemberWithName("n_scores").GetValueAsSigned()
    return f"Student({name!r}, id={sid}, avg={avg:.1f}, n={n})"


def student_list_summary(valobj, internal_dict):
    """One-line description of a Student * treated as a list head."""
    raw = valobj.GetNonSyntheticValue()
    if raw.GetValueAsUnsigned(0) == 0:
        return "Student * NULL"
    return f"Student list ({len(_walk(raw))} nodes)"


class StudentSynthetic:
    """Show only the scores that are in use, plus next as a leaf."""

    def __init__(self, valobj, internal_dict):
        self.valobj = valobj.GetNonSyntheticValue()
        self.n = 0

    def update(self):
        n = self.valobj.GetChildMemberWithName("n_scores").GetValueAsSigned()
        self.n = max(0, min(n, 4))
        # False tells LLDB the children may change, so re-run update on
        # the next stop.
        return False

    def has_children(self):
        return True

    def num_children(self):
        return self.n + 1

    def get_child_index(self, name):
        if name == "next":
            return self.n
        if name.startswith("scores["):
            try:
                return int(name[len("scores["):-1])
            except ValueError:
                return -1
        return -1

    def get_child_at_index(self, index):
        if index < 0 or index > self.n:
            return None
        if index == self.n:
            return self.valobj.GetChildMemberWithName("next")
        scores = self.valobj.GetChildMemberWithName("scores")
        return scores.GetChildAtIndex(index)


class StudentListSynthetic:
    """Expand a Student * into the students it links to."""

    def __init__(self, valobj, internal_dict):
        self.valobj = valobj.GetNonSyntheticValue()
        self.nodes = []

    def update(self):
        self.nodes = _walk(self.valobj)
        return False

    def has_children(self):
        return True

    def num_children(self):
        return len(self.nodes)

    def get_child_index(self, name):
        if name.startswith("[") and name.endswith("]"):
            try:
                return int(name[1:-1])
            except ValueError:
                return -1
        return -1

    def get_child_at_index(self, index):
        if index < 0 or index >= len(self.nodes):
            return None
        return self.nodes[index]


def __lldb_init_module(debugger, internal_dict):
    mod = __name__
    interpreter = debugger.GetCommandInterpreter()
    result = lldb.SBCommandReturnObject()
    # Recreate the category so --allow-reload replaces old registrations.
    interpreter.HandleCommand("type category delete gradebook", result)
    debugger.HandleCommand("type category define gradebook")
    # -p keeps the Student formatters off Student *, so the pointer gets
    # the list formatters below instead.
    commands = [
        f"type summary add -w gradebook -F {mod}.score_summary Score",
        f"type summary add -w gradebook -p -F {mod}.student_summary Student",
        f"type synthetic add -w gradebook -p -l {mod}.StudentSynthetic Student",
        f'type summary add -w gradebook -F {mod}.student_list_summary "Student *"',
        f'type synthetic add -w gradebook -l {mod}.StudentListSynthetic "Student *"',
    ]
    for command in commands:
        debugger.HandleCommand(command)
    debugger.HandleCommand("type category enable gradebook")
    print("loaded: LLDB formatters for Score, Student, Student *")
