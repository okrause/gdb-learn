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

"""Breakpoint on announce_top: stop only when s is NULL."""

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
print("loaded: breakpoint NullGuard on announce_top")
