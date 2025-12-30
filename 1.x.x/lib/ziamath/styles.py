''' Apply italic, bold, and other font styles by shifting the unstyled ASCII
    characters [A-Z, a-z, and 0-9] to their higher unicode alternatives. Note
    this does not check whether the new character glyph exists in the font.
'''
from __future__ import annotations
from typing import Optional, Any, MutableMapping
from collections import ChainMap, namedtuple
from dataclasses import dataclass, field, asdict
from xml.etree import ElementTree as ET

from .config import config


VARIANTS = ['serif', 'sans', 'script', 'double', 'mono', 'fraktur']
Styletype = namedtuple('Styletype', 'bold italic')


@dataclass
class MathVariant:
    ''' Math font variant, such as serif, sans, script, italic, etc. '''
    style: str = 'serif'
    italic: bool = False
    bold: bool = False
    normal: bool = False


@dataclass
class MathStyle:
    ''' Math Style parameters '''
    mathvariant: MathVariant = field(default_factory=MathVariant)
    displaystyle: bool = True
    mathcolor: str = 'black'
    mathbackground: str = 'none'
    mathsize: str = ''
    scriptlevel: int = 0


def parse_variant(variant: str, parent_variant: MathVariant) -> MathVariant:
    ''' Extract mathvariant from MathML attribute and parent's variant '''
    bold = True if 'bold' in variant else parent_variant.bold
    italic = True if 'italic' in variant else parent_variant.italic
    normal = True if 'normal' in variant else parent_variant.normal

    variant = variant.replace('bold', '').replace('italic', '').strip()
    if variant in VARIANTS:
        style = variant
    else:
        style = parent_variant.style

    return MathVariant(style=style, italic=italic, bold=bold, normal=normal)


def parse_displaystyle(params: MutableMapping[str, Any]) -> bool:
    ''' Extract displaystyle mode from MathML attributes '''
    dstyle = True
    if 'displaystyle' in params:
        dstyle = params.get('displaystyle') in ['true', True]
    elif 'display' in params:
        dstyle = params.get('display', 'block') != 'inline'
    return dstyle


def parse_style(element: ET.Element, parent_style: Optional[MathStyle] = None) -> MathStyle:
    ''' Read element style attributes into MathStyle '''
    params: MutableMapping[str, Any]
    if parent_style:
        params = ChainMap(element.attrib, asdict(parent_style))
        parent_variant = parent_style.mathvariant
    else:
        params = element.attrib
        parent_variant = MathVariant()

    args: dict[str, Any] = {}
    args['mathcolor'] = params.get('mathcolor', config.math.color)
    args['mathbackground'] = params.get('mathbackground', config.math.background)
    args['mathsize'] = params.get('mathsize', '')
    args['scriptlevel'] = int(params.get('scriptlevel', 0))
    args['mathvariant'] = parse_variant(element.attrib.get('mathvariant', config.math.variant), parent_variant) 
    args['displaystyle'] = parse_displaystyle(params)
    
    css = params.get('style', '')
    if css:
        cssparams = css.split(';')
        for cssparam in cssparams:
            if not cssparam:
                continue  # blank lines
            key, val = cssparam.split(':')
            key = key.strip()
            val = val.strip()
            if key.lower() == 'background':
                args['mathbackground'] = val
            elif key.lower() == 'color':
                args['mathcolor'] = val
    return MathStyle(**args)


LATIN_CAP_RANGE = (0x41, 0x5A)
LATIN_CAPS = \
    {'serif': {Styletype(bold=False, italic=False): 0x0000,
               Styletype(bold=True, italic=False): 0x1D400,
               Styletype(bold=False, italic=True): 0x1D434,
               Styletype(bold=True, italic=True): 0x1D468
               },
     'sans':  {Styletype(bold=False, italic=False): 0x1D5A0,
               Styletype(bold=True, italic=False): 0x1D5D4,
               Styletype(bold=False, italic=True): 0x1D608,
               Styletype(bold=True, italic=True): 0x1D63C
               },
     'script': {Styletype(bold=False, italic=False): 0x1D49C,
                Styletype(bold=True, italic=False): 0x1D4D0,
                Styletype(bold=True, italic=True): 0x1D4D0  # No separate italic
                },
     'fraktur': {Styletype(bold=False, italic=False): 0x1D504,
                 Styletype(bold=True, italic=False): 0x1D56C, 
                 Styletype(bold=True, italic=True): 0x1D56C  # No separate italic
                 },
     'mono': {Styletype(bold=False, italic=False): 0x1D670,
              },
     'double': {Styletype(bold=False, italic=False): 0x1D538,
                },
    }

LATIN_SMALL_RANGE = (0x61, 0x7a)
LATIN_SMALL = \
    {'serif': {Styletype(bold=False, italic=False): 0x0000,
               Styletype(bold=True, italic=False): 0x1D41A,
               Styletype(bold=False, italic=True): 0x1D44E,
               Styletype(bold=True, italic=True): 0x1D482
               },
     'sans':  {Styletype(bold=False, italic=False): 0x1D5BA,
               Styletype(bold=True, italic=False): 0x1D5EE,
               Styletype(bold=False, italic=True): 0x1D622,
               Styletype(bold=True, italic=True): 0x1D656
               },
     'script': {Styletype(bold=False, italic=False): 0x1D4B6,
                Styletype(bold=True, italic=False): 0x1D4EA,
                Styletype(bold=True, italic=True): 0x1D4EA  # No separate italic
                },
     'fraktur': {Styletype(bold=False, italic=False): 0x1D51E,
                 Styletype(bold=True, italic=False): 0x1D586,
                 Styletype(bold=True, italic=True): 0x1D586  # No separate italic
                 },
     'mono': {Styletype(bold=False, italic=False): 0x1D68A,
              },
     'double': {Styletype(bold=False, italic=False): 0x1D552,
                },
    }

GREEK_CAP_RANGE = (0x0391, 0x3AA)
GREEK_CAPS = \
    {'serif': {Styletype(bold=False, italic=False): 0x0000,
               Styletype(bold=True, italic=False): 0x1D6A8,
               Styletype(bold=False, italic=True): 0x1D6E2,
               Styletype(bold=True, italic=True): 0x1D71C
               },
     'sans': {Styletype(bold=False, italic=False): 0x0000,
              Styletype(bold=True, italic=False): 0x1D756,
              Styletype(bold=True, italic=True): 0x1D790
              },
    }

GREEK_LOWER_RANGE = (0x3b1, 0x3d0)
GREEK_LOWER = \
    {'serif': {Styletype(bold=False, italic=False): 0x0000,
               Styletype(bold=True, italic=False): 0x1D6C2,
               Styletype(bold=False, italic=True): 0x1D6FC,
               Styletype(bold=True, italic=True): 0x1D736
               },
     'sans': {Styletype(bold=False, italic=False): 0x0000,
              Styletype(bold=True, italic=False): 0x1D770,
              Styletype(bold=True, italic=True): 0x1D7AA
              },
    }

DIGIT_RANGE = (0x30, 0x39)
DIGITS = \
    {'serif': {Styletype(bold=False, italic=False): 0x0000,
               Styletype(bold=True, italic=False): 0x1D7CE,
               },
     'double': {Styletype(bold=False, italic=False): 0x1D7D8, },
     'mono': {Styletype(bold=False, italic=False): 0x1D7F6, },
     'sans': {Styletype(bold=False, italic=False): 0x1D7E2,
              Styletype(bold=True, italic=False): 0x1D7EC,
              Styletype(bold=True, italic=True): 0x1D7EC,
              },
    }


subtables = ((LATIN_CAP_RANGE, LATIN_CAPS),
             (LATIN_SMALL_RANGE, LATIN_SMALL),
             (GREEK_CAP_RANGE, GREEK_CAPS),
             (GREEK_LOWER_RANGE, GREEK_LOWER),
             (DIGIT_RANGE, DIGITS))


# These are the yellow characters in wikipedia's table
OFFSET_EXCEPTIONS = {
    'ϴ': 0x0391+0x11,
    '∇': 0x0391+0x19,
    '∂': 0x03B1+0x19,
    'ϵ': 0x03B1+0x1A,
    'ϑ': 0x03B1+0x1B,
    'ϰ': 0x03B1+0x1C,
    'ϕ': 0x03B1+0x1D,
    'ϱ': 0x03B1+0x1E,
    'ϖ': 0x03B1+0x1F}


EXCEPTIONS = {
    0x1D49C+0x01: 'ℬ',  # latin cap scripts
    0x1D49C+0x04: 'ℰ',
    0x1D49C+0x05: 'ℱ',
    0x1D49C+0x07: 'ℋ',
    0x1D49C+0x08: 'ℐ',
    0x1D49C+0x0B: 'ℒ',
    0x1D49C+0x0C: 'ℳ',
    0x1D49C+0x11: 'ℛ',
    0x1D504+0x02: 'ℭ',  # latin cap frakturs
    0x1D504+0x07: 'ℌ',
    0x1D504+0x08: 'ℑ',
    0x1D504+0x11: 'ℜ',
    0x1D504+0x19: 'ℨ',
    0x1D538+0x02: 'ℂ',  # latin cap doubles
    0x1D538+0x07: 'ℍ',
    0x1D538+0x0D: 'ℕ',
    0x1D538+0x0F: 'ℙ',
    0x1D538+0x10: 'ℚ',
    0x1D538+0x11: 'ℝ',
    0x1D538+0x19: 'ℤ',
    0x1D44E+0x07: 'ℎ',  # latin small italic
    0x1D4B6+0x04: 'ℯ',  # latin small script
    0x1D4B6+0x06: 'ℊ',
    0x1D4B6+0x0E: 'ℴ',
    }


def auto_italic(char: str) -> bool:
    ''' Determine whether the character should be automatically
        converted to italic
    '''
    ordchr = ord(char)
    for ordrange in (GREEK_LOWER_RANGE, LATIN_SMALL_RANGE, LATIN_CAP_RANGE):
        if ordrange[0] <= ordchr <= ordrange[1]:
            return True
    return False


def styledchr(char, variant: MathVariant):
    ''' Convert character to its styled (bold, italic, script, etc.) variant.
        See tables at: https://en.wikipedia.org/wiki/Mathematical_Alphanumeric_Symbols
    '''
    script = variant.style
    style = Styletype(variant.bold, variant.italic)
    styledchr = char  # Default is to return char unchanged

    charord = OFFSET_EXCEPTIONS.get(char, ord(char))
    for ordrange, table in subtables:
        if ordrange[0] <= charord <= ordrange[1]:
            ordoffset = charord - ordrange[0]
            scripttable = table.get(script, table.get('serif'))
            offset = scripttable.get(style, scripttable.get(Styletype(False, False)))  # type: ignore
            if offset:
                styledchr = chr(ordoffset + offset)
            styledchr = EXCEPTIONS.get(ord(styledchr), styledchr)
            break

    return styledchr


def styledstr(st: str, variant: MathVariant) -> str:
    ''' Apply unicode styling conversion to a string '''
    return ''.join([styledchr(s, variant) for s in st])
