"""LLDB command: explain-avg

Run while stopped inside compute_average after the loop, so sum and n are
both valid. Prints the correct divisor next to the buggy one.

Load with:
    (lldb) command script import lldb/python/explain_avg.py
"""


def _selected_frame(debugger):
    process = debugger.GetSelectedTarget().GetProcess()
    return process.GetSelectedThread().GetSelectedFrame()


def explain_avg(debugger, command, result, internal_dict):
    frame = _selected_frame(debugger)
    if not frame.IsValid():
        result.AppendMessage("no running process; use 'run' first")
        return

    n_val = frame.FindVariable("n")
    sum_val = frame.FindVariable("sum")
    if not n_val.IsValid() or not sum_val.IsValid():
        result.AppendMessage("not stopped in compute_average")
        return

    n = n_val.GetValueAsSigned()
    try:
        total = float(sum_val.GetValue())
    except (TypeError, ValueError):
        result.AppendMessage("cannot read sum")
        return

    if n <= 0:
        result.AppendMessage("n is 0; step through the loop first")
        return

    result.AppendMessage(f"n={n}  sum={total}")
    result.AppendMessage(f"  correct  sum/n     = {total / n:.1f}")
    result.AppendMessage(f"  buggy    sum/(n+1) = {total / (n + 1):.1f}")


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand(
        f"command script add -f {__name__}.explain_avg explain-avg"
    )
    print("loaded: command explain-avg")
