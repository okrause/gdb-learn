"""GDB breakpoint on announce_top: stop only when s is NULL.

stop() returning False logs and continues, so only the NULL case
interrupts you.
"""

import gdb


class NullGuard(gdb.Breakpoint):
    def stop(self):
        s = gdb.parse_and_eval("s")
        if int(s) == 0:
            gdb.write("announce_top: s is NULL (would SIGSEGV)\n")
            return True
        gdb.write("announce_top: s is valid, continuing\n")
        return False


NullGuard("announce_top")
print("loaded: NULL guard on announce_top")
