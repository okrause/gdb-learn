"""GDB command: explain-avg

Run while stopped inside compute_average after the loop, so sum and n are
both valid. Prints the correct divisor next to the buggy one.
"""

import gdb


class ExplainAvg(gdb.Command):
    """Compare sum/n against the buggy sum/(n+1) in compute_average."""

    def __init__(self):
        super(ExplainAvg, self).__init__("explain-avg", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        n = int(gdb.parse_and_eval("n"))
        total = float(gdb.parse_and_eval("sum"))
        if n <= 0:
            gdb.write("n is 0; step through the loop first\n")
            return
        gdb.write(f"n={n}  sum={total}\n")
        gdb.write(f"  correct  sum/n     = {total / n:.1f}\n")
        gdb.write(f"  buggy    sum/(n+1) = {total / (n + 1):.1f}\n")


ExplainAvg()
print("loaded: command explain-avg")
