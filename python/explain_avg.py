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

"""GDB command: explain-avg

Run this while stopped inside compute_average after the loop
(sum and n are valid). Prints correct vs buggy divisor.
"""

import gdb


class ExplainAvg(gdb.Command):
    """Compare sum/n vs the buggy sum/(n+1) in compute_average."""

    def __init__(self):
        super(ExplainAvg, self).__init__("explain-avg", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        n = int(gdb.parse_and_eval("n"))
        ssum = float(gdb.parse_and_eval("sum"))
        if n <= 0:
            gdb.write("n is 0; step through the loop first\n")
            return
        gdb.write(f"n={n}  sum={ssum}\n")
        gdb.write(f"  correct  sum/n     = {ssum / n:.1f}\n")
        gdb.write(f"  buggy    sum/(n+1) = {ssum / (n + 1):.1f}\n")


ExplainAvg()
print("loaded: command explain-avg")
