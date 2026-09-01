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

"""Log SIGSEGV (and other stops) via gdb.events.stop."""

import gdb


def on_stop(event):
    if isinstance(event, gdb.SignalEvent):
        gdb.write(f"python event: signal {event.stop_signal}\n")
    elif isinstance(event, gdb.BreakpointEvent):
        gdb.write("python event: breakpoint hit\n")


gdb.events.stop.connect(on_stop)
print("loaded: stop-event logger")
