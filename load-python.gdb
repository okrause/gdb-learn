# Load from the gdb-learn directory so python/ is on sys.path.
python
import os
import sys

_root = os.getcwd()
_py = os.path.join(_root, "python")
if _py not in sys.path:
    sys.path.insert(0, _py)
end
