from __future__ import print_function
import sys
import pyflate

# Short CSS class names...
CATEGORY_LITERAL = 'l'
CATEGORY_REF = 'r'

if len(sys.argv) != 2:
    program = sys.argv[0]
    print(program +':', 'usage:', program, '<filename.gz>')
    sys.exit(0)

literal_lengths_map, symbols = pyflate.doit(sys.argv[1])

#for c, num_bits in sorted(literal_lengths_map.iteritems(), key=lambda x: x[1]):
#    print('cost of %r = %d bits' % (c, num_bits))

indent = 0
at_newline = False
bracket_stack = []
for (symbol, num_bits) in symbols:
    if len(symbol) == 1:
        category = CATEGORY_LITERAL
    else:
        category = CATEGORY_REF

    for c in symbol:
        if at_newline:
            print('    ' * indent, end='')
            at_newline = False

        if c == '{':
            indent += 1
            at_newline = True
            bracket_stack.append('{')
        elif c == '}':
            indent -= 1
            print()
            print('    ' * indent, end='')
            at_newline = True
            bracket_stack.pop()
        elif c == '(':
            bracket_stack.append('(')
        elif c == ')':
            bracket_stack.pop()
        elif c == ';':
            at_newline = True
        elif c == ',':
            if len(bracket_stack) == 0 or bracket_stack[-1] == '{':
                at_newline = True

        print(c, end='')
        if at_newline:
            print()
