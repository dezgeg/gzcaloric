from __future__ import print_function
import argparse
import colorsys
import sys
import pyflate

# Short CSS class names...
CATEGORY_LITERAL = 'l'
CATEGORY_REF = 'r'

HUE_RED = 0
HUE_GREEN = 1. / 3.

parser = argparse.ArgumentParser()
parser.add_argument('inputfile', help='Path to .png/.gz file.')
parser.add_argument('-n', '--no-color', action='store_true', help='Skip colors (just pretty-print)')
parser.add_argument('-r', '--no-format', action='store_true', help='Skip code formatting')
parser.add_argument('-b', '--bicolor', action='store_true', help='Just show literals vs. backreferences')
args = parser.parse_args()

def ansi_color(is_fg, r, g, b):
    bg_fg = 38 if is_fg else 48
    return "\x1b[%d;2;%d;%d;%dm" % (bg_fg, r, g, b)

def ansi_reset():
    if args.no_color:
        return
    print('\x1b[0m', end='')

def color_on(category, num_bits):
    if args.no_color:
        return
    print(ansi_color(True, 0, 0, 0), end='') # Black foreground
    if category == CATEGORY_LITERAL:
        badness = (num_bits - min_bits) / float(max_bits - min_bits)
        bg_color = colorsys.hls_to_rgb((1. - badness) * HUE_GREEN, 0.5, 1.)
        print(ansi_color(False, *map(lambda x: x * 255, bg_color)), end='') # Background color
    else:
        print(ansi_color(False, 0, 0, 255), end='') # Background color

def color_off():
    if args.no_color:
        return
    print(ansi_color(False, 0, 0, 0), end='') # Black background
    #ansi_reset()

literal_lengths_map, symbols = pyflate.doit(args.inputfile)

histogram = {}
for (symbol, num_bits) in symbols:
    for c in symbol:
        histogram[c] = histogram.get(c, 0) + 1

sorted_lengths = list(sorted(literal_lengths_map.iteritems(), key=lambda x: (x[1], x[0])))
min_bits = sorted_lengths[0][1]
max_bits = sorted_lengths[-1][1]
for c, num_bits in sorted_lengths:
    color_on(CATEGORY_LITERAL, num_bits)
    print(' ', end='')
    ansi_reset()
    print('cost of %r = %d bits, used %d times' % (c, num_bits, histogram.get(c, 0)))

indent = 0
at_newline = False
newline_unless_semicolon = False
bracket_stack = []
for (symbol, num_bits) in symbols:
    if len(symbol) == 1:
        category = CATEGORY_LITERAL
    else:
        category = CATEGORY_REF

    for c in symbol:
        color_on(category, num_bits)

        if newline_unless_semicolon and c not in ',;':
            print()
            at_newline = True
        newline_unless_semicolon = False

        if at_newline:
            color_off()
            print('    ' * indent, end='')
            color_on(category, num_bits)
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
            color_on(category, num_bits)
            newline_unless_semicolon = True
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

        if c != '\x00':
            if c < ' ' or c > '~':
                c = repr(c)[1:-1]
            print(c, end='')

        if at_newline:
            color_off()
            print()
ansi_reset()
