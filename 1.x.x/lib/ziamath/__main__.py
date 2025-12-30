''' Command line interface to ziamath.

    python -m ziamath
'''

import sys
import argparse
from xml.etree.ElementTree import ParseError

import ziamath as zm


def main():
    parser = argparse.ArgumentParser(
        description='Convert MathML and Latex to standalone SVG')

    parser.add_argument(
        'file',
        nargs='?',
        help='Input file containing MathML or Latex. If empty stdin is used',
        type=argparse.FileType('r'),
        default=sys.stdin)

    parser.add_argument(
        '-o',
        dest='output',
        nargs='?',
        help='Output file. If empty, stdout is used',
        type=argparse.FileType('w'),
        default=sys.stdout)

    parser.add_argument(
        '--latex',
        help='Use Latex input mode',
        action='store_true')

    parser.add_argument(
        '--svg1',
        help='Keep SVG1.x compatibility',
        action='store_true')

    parser.add_argument(
        '--font',
        '-f',
        default=None,
        help='Font file (TTF/OTF). Must contain MATH table')

    parser.add_argument(
        '--size',
        '-s',
        type=int,
        default=None,
        help='Font size in points')

    parser.add_argument(
        '--precision',
        '-p',
        type=int,
        default=None,
        help='Decimal precision for SVG coordinates')

    parser.add_argument(
        '--version',
        action='version',
        version=zm.__version__)
 
    parser.add_argument(
        '--debug',
        '-d',
        action='store_true',
        help='Debug mode')

    args = parser.parse_args()
    if args.file.isatty():
        parser.print_help()
        return 0

    if args.svg1:
        zm.config.svg2 = False
    if args.precision:
        zm.config.precision = args.precision
    if args.debug:
        zm.config.debug.baseline = True
        zm.config.debug.bbox = True

    kwargs = {'font': args.font,
              'size': args.size}

    mathinput = args.file.read()    
    if args.latex:
        svg = zm.Latex(mathinput, **kwargs).svg()
    else:
        try:
            svg = zm.Math(mathinput, **kwargs).svg()
        except ParseError:
            svg = zm.Latex(mathinput, **kwargs).svg()

    print(svg, file=args.output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
