# Copyright 2026 "Google LLC"
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Pretty-printers for Score, Student, and Student * (linked list).

GDB calls lookup(val) whenever print needs to display a value. Return a
printer object or None to use the default dump.

Register with gdb.printing (libstdc++ uses the same mechanism).
"""

import gdb
import gdb.printing


class ScorePrinter:
    """One-line 'quiz=90' instead of {label = "quiz", points = 90}."""

    def __init__(self, val):
        self.val = val

    def to_string(self):
        label = self.val["label"].string()
        points = float(self.val["points"])
        return f"{label}={points:.0f}"


class StudentPrinter:
    """Summary line plus expandable scores and next pointer."""

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
        nxt = self.val["next"]
        if int(nxt) == 0:
            yield ("next", "NULL")
        else:
            yield ("next", str(nxt))

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
            if i >= 16:
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
        if inner_name:
            return inner_name + " *"
        return None
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


gdb.printing.register_pretty_printer(
    None, GradebookPrinter(), replace=True
)
print("loaded: pretty-printers Score, Student, Student *")
