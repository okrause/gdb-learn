# Copyright 2026 "Google LLC"
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""GDB command: dump-roster [head-expression]"""

import gdb


class DumpRoster(gdb.Command):
    """Dump the student linked list from a head pointer.

    Usage: dump-roster [expression]
    Default expression is roster (main) or head if that fails.
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
        while node and int(node) != 0:
            s = node.dereference()
            name = s["name"].string()
            sid = int(s["id"])
            avg = float(s["average"])
            gdb.write(f"{sid:4d}  {name:14s}  {avg:4.1f}\n")
            node = s["next"]


DumpRoster()
print("loaded: command dump-roster")
