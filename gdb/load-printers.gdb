# Path helper plus the pretty-printers.
#   gdb -x gdb/load-printers.gdb ./gradebook
source gdb/load-python.gdb
python
import student_printers
end
