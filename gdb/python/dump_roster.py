"""GDB command: dump-roster [head-expression]"""

import gdb

MAX_NODES = 16


class DumpRoster(gdb.Command):
    """Dump the student linked list from a head pointer.

    Usage: dump-roster [expression]
    Defaults to roster, falling back to head.
    """

    def __init__(self):
        super(DumpRoster, self).__init__("dump-roster", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        expr = (arg or "").strip()
        if not expr:
            try:
                gdb.parse_and_eval("roster")
                expr = "roster"
            except gdb.error:
                expr = "head"

        node = gdb.parse_and_eval(expr)
        seen = set()
        count = 0

        while node and int(node) != 0:
            addr = int(node)
            if addr in seen:
                gdb.write("cycle detected\n")
                break
            if count >= MAX_NODES:
                gdb.write("truncated\n")
                break
            seen.add(addr)

            s = node.dereference()
            name = s["name"].string()
            sid = int(s["id"])
            avg = float(s["average"])
            gdb.write(f"{sid:4d}  {name:14s}  {avg:4.1f}\n")

            node = s["next"]
            count += 1


DumpRoster()
print("loaded: command dump-roster")
