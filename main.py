from __future__ import print_function
import argparse
import colorsys
import sys
import pyflate

# Short CSS class names...
CATEGORY_LITERAL = 'l'
CATEGORY_REF = 'r'

COLOR_MAP = [
    (0x00, 0x05, 0x60), # less than 1 bit   - midnight blue
    (0x02, 0x3D, 0x9A), # less than 2 bits  - dark blue
    (0x00, 0x5F, 0xD3), # less than 3 bits  - royal blue
    (0x01, 0x86, 0xC0), # less than 4 bits  - teal
    (0x4A, 0xB0, 0x3D), # less than 5 bits  - emerald green
    (0xB5, 0xD0, 0x00), # less than 6 bits  - chartreuse
    (0xEB, 0xD1, 0x09), # less than 7 bits  - yellow
    (0xFB, 0xA7, 0x0F), # less than 8 bits  - orange
    (0xEE, 0x00, 0x00),       # less than 9 bits  - bright red
    (0xD0, 0x00, 0x00),       # less than 10 bits - darker tones of red from this point
    (0xB2, 0x00, 0x00),       # less than 11 bits
    (0x95, 0x00, 0x00),       # less than 12 bits
    (0x77, 0x00, 0x00),       # less than 13 bits
    (0x5a, 0x00, 0x00),       # less than 14 bits
    (0x3C, 0x00, 0x00),       # less than 15 bits
    (0x1E, 0x00, 0x00),       # less than 16 bits
]

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('inputfile', help='Path to .png/.gz file.')
parser.add_argument('-n', '--no-color', action='store_true', help='Skip colors (just pretty-print)')
parser.add_argument('-r', '--no-format', action='store_true', help='Skip code formatting')
parser.add_argument('-b', '--bicolor', action='store_true', help='Just show literals vs. backreferences')
parser.add_argument('-h', '--html', action='store_true', help='HTML output')
args = parser.parse_args()

def ansi_color(is_fg, r, g, b):
    bg_fg = 38 if is_fg else 48
    return "\x1b[%d;2;%d;%d;%dm" % (bg_fg, r, g, b)

def ansi_reset():
    if args.no_color:
        return
    print('\x1b[0m', end='')

def color_on(num_decompressed_bytes, num_compressed_bits):
    if args.no_color:
        return

    if num_decompressed_bytes == 1:
        category = CATEGORY_LITERAL
    else:
        category = CATEGORY_REF

    ratio = num_compressed_bits / float(num_decompressed_bytes)
    badness = int(ratio)
    bg_color = (0, 0, 0) if badness >= len(COLOR_MAP) else COLOR_MAP[badness]

    if args.html:
        print("<span style='background-color: #%02x%02x%02x'>" % bg_color, end='')
    else:
        print(ansi_color(True, 255, 255, 255), end='') # White foreground
        print(ansi_color(False, *bg_color), end='') # Background color

def color_off():
    if args.no_color:
        return

    if args.html:
        print("</span>", end='')
    else:
        print(ansi_color(False, 0, 0, 0), end='') # Black background

literal_lengths_map, symbols = pyflate.doit(args.inputfile)

histogram = {}
for (symbol, num_bits) in symbols:
    for c in symbol:
        histogram[c] = histogram.get(c, 0) + 1

sorted_lengths = list(sorted(literal_lengths_map.iteritems(), key=lambda x: (x[1], x[0])))
min_bits = sorted_lengths[0][1]
max_bits = sorted_lengths[-1][1]
#for c, num_bits in sorted_lengths:
#    color_on(CATEGORY_LITERAL, num_bits)
#    print(' ', end='')
#    color_off()
#    print('cost of %r = %d bits, used %d times' % (c, num_bits, histogram.get(c, 0)))

if args.html:
    print("""<html>
                <head>
                    <style>
                        body {
                            background-color: #888888;
                            color: #ffffff;
                            font-size: 18px;

                            text-shadow: 0px 0px 5px black;
                        }
                        pre {
                            font-family: Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New;
                        }
                    </style>
                </head>
                <body>""")
    print("<pre>")


indent = 0
at_newline = False
last_char_newline = False
newline_unless_semicolon = False
bracket_stack = []
prev_char = None
for (symbol, num_compressed_bits) in symbols:
    num_decompressed_bytes = len(symbol)
    color_on(num_decompressed_bytes, num_compressed_bits)
    for c in symbol:
        if newline_unless_semicolon and c not in ',;':
            print()
            last_char_newline = True
            at_newline = True
        newline_unless_semicolon = False

        if c == '}':
            indent -= 1
            if prev_char not in ';}':
                print()
                color_off()
                print('    ' * indent, end='')
                last_char_newline = False
                color_on(num_decompressed_bytes, num_compressed_bits)
            newline_unless_semicolon = True
            bracket_stack.pop()
        if at_newline:
            color_off()
            print('    ' * indent, end='')
            last_char_newline = False
            color_on(num_decompressed_bytes, num_compressed_bits)
            at_newline = False

        if c == '{':
            indent += 1
            at_newline = True
            bracket_stack.append('{')
        if c == '`':
            if len(bracket_stack) == 0 or bracket_stack[-1] != '`':
                bracket_stack.append('`')
                indent += 1
            else:
                indent -= 1
                bracket_stack.pop()
        elif c == '(':
            bracket_stack.append('(')
        elif c == ')':
            bracket_stack.pop()
        elif c == ';':
            if len(bracket_stack) == 0 or bracket_stack[-1] in '{`':
                at_newline = True
        elif c == ',':
            if len(bracket_stack) == 0 or bracket_stack[-1] == '{':
                at_newline = True

        if c != '\x00':
            if c < ' ' or c > '~':
                c = repr(c)[1:-1]
            print(c, end='')
            last_char_newline = False

        if at_newline:
            color_off()
            print()
            last_char_newline = True
        prev_char = c
    color_off()

color_off()
if not last_char_newline:
    print()

if args.html:
    print('</pre></body></html>')
