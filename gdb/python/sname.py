"""GDB convenience function: $sname(student_ptr) -> name or (null).

GDB-only. LLDB has no convenience functions; use a summary or a custom
command there instead.
"""

import gdb


class StudentName(gdb.Function):
    def __init__(self):
        super(StudentName, self).__init__("sname")

    def invoke(self, val):
        if int(val) == 0:
            return "(null)"
        return val.dereference()["name"].string()


StudentName()
print("loaded: convenience function $sname")
