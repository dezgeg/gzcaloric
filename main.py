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

def ansi_color(is_fg, r, g, b):
    bg_fg = 38 if is_fg else 48
    return "\x1b[%d;2;%d;%d;%dm" % (bg_fg, r, g, b)

def ansi_reset():
    print('\x1b[0m', end='')

def color_on(color_tuple):
    print(ansi_color(True, 0, 0, 0), end='') # Black foreground
    print(ansi_color(False, *color_tuple), end='') # Background color

def color_off():
    print(ansi_color(False, 0, 0, 0), end='') # Black background
    #ansi_reset()

indent = 0
at_newline = False
bracket_stack = []
for (symbol, num_bits) in symbols:
    if len(symbol) == 1:
        category = CATEGORY_LITERAL
        color = (255, 0, 0)
    else:
        category = CATEGORY_REF
        color = (0, 0, 255)

    for c in symbol:
        color_on(color)
        if at_newline:
            color_off()
            print('    ' * indent, end='')
            color_on(color)
            at_newline = False

        if c == '{':
            indent += 1
            at_newline = True
            bracket_stack.append('{')
        elif c == '}':
            indent -= 1
            color_off()
            print()
            color_off()
            print('    ' * indent, end='')
            color_on(color)
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
            color_off()
            print()
ansi_reset()
