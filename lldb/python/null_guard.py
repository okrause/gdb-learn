"""Breakpoint callback for announce_top: stop only when s is NULL.

The LLDB counterpart of gdb/python/null_guard.py. A callback that returns
False makes LLDB continue automatically, so valid calls do not interrupt
you and the NULL case does.

Load with:
    (lldb) command script import lldb/python/null_guard.py
"""


def null_guard(frame, bp_loc, internal_dict):
    s = frame.FindVariable("s")
    if s.GetValueAsUnsigned(0) == 0:
        print("announce_top: s is NULL (would SIGSEGV)")
        return True
    print("announce_top: s is valid, continuing")
    return False


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand("breakpoint set -n announce_top")
    # With no breakpoint id, this attaches to the breakpoint just created.
    debugger.HandleCommand(f"breakpoint command add -F {__name__}.null_guard")
    print("loaded: NULL guard on announce_top")
