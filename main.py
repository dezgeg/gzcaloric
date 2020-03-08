import sys
import pyflate

if len(sys.argv) != 2:
    program = sys.argv[0]
    print program +':', 'usage:', program, '<filename.gz>'
    sys.exit(0)

pyflate.doit()
