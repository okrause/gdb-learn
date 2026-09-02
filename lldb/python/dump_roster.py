"""LLDB command: dump-roster [head-expression]

Walks the student linked list and prints one line per student. The LLDB
counterpart of gdb/python/dump_roster.py.

Load with:
    (lldb) command script import lldb/python/dump_roster.py
"""

MAX_NODES = 16


def _cstr(val):
    summary = val.GetSummary()
    if not summary:
        return ""
    return summary.strip('"')


def _float(val):
    try:
        return float(val.GetValue())
    except (TypeError, ValueError):
        return 0.0


def _selected_frame(debugger):
    process = debugger.GetSelectedTarget().GetProcess()
    return process.GetSelectedThread().GetSelectedFrame()


def dump_roster(debugger, command, result, internal_dict):
    frame = _selected_frame(debugger)
    if not frame.IsValid():
        result.AppendMessage("no running process; use 'run' first")
        return

    expr = command.strip()
    if not expr:
        # main calls the head 'roster'; print_roster calls it 'head'.
        expr = "roster" if frame.FindVariable("roster").IsValid() else "head"

    node = frame.EvaluateExpression(expr)
    if not node.IsValid():
        result.AppendMessage(f"cannot evaluate {expr!r}")
        return

    node = node.GetNonSyntheticValue()
    seen = set()
    count = 0

    while node.IsValid() and node.GetValueAsUnsigned(0) != 0:
        addr = node.GetValueAsUnsigned(0)
        if addr in seen:
            result.AppendMessage("cycle detected")
            break
        if count >= MAX_NODES:
            result.AppendMessage("truncated")
            break
        seen.add(addr)

        student = node.Dereference().GetNonSyntheticValue()
        name = _cstr(student.GetChildMemberWithName("name"))
        sid = student.GetChildMemberWithName("id").GetValueAsSigned()
        avg = _float(student.GetChildMemberWithName("average"))
        result.AppendMessage(f"{sid:4d}  {name:14s}  {avg:4.1f}")

        node = student.GetChildMemberWithName("next")
        count += 1


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        f"command script add -f {__name__}.dump_roster dump-roster"
    )
    print("loaded: command dump-roster")
