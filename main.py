import sys
import pyflate

if len(sys.argv) != 2:
    program = sys.argv[0]
    print program +':', 'usage:', program, '<filename.gz>'
    sys.exit(0)

literal_lengths_map, symbols = pyflate.doit(sys.argv[1])

for c, num_bits in sorted(literal_lengths_map.iteritems(), key=lambda x: x[1]):
    print('cost of %r = %d bits' % (c, num_bits))

for (symbol, num_bits) in symbols:
    if len(symbol) == 1:
        print('literal %r - %d bits' % (symbol, num_bits))
    else:
        print('copy %r - %d bits' % (symbol, num_bits))
