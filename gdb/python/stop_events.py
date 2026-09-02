"""Log stops (signals, breakpoints) via gdb.events.stop.

The LLDB counterpart is a stop hook:
    (lldb) target stop-hook add -o "frame info"
"""

import gdb


def on_stop(event):
    if isinstance(event, gdb.SignalEvent):
        gdb.write(f"python event: signal {event.stop_signal}\n")
    elif isinstance(event, gdb.BreakpointEvent):
        gdb.write("python event: breakpoint hit\n")


gdb.events.stop.connect(on_stop)
print("loaded: stop-event logger")
