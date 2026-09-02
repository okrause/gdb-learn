# Put ./gdb/python on sys.path so the helper modules are importable.
# Run gdb from the repo root.
python
import os
import sys

_py = os.path.join(os.getcwd(), "gdb", "python")
if _py not in sys.path:
    sys.path.insert(0, _py)
end
