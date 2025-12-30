''' MathML Escape Codes

Python's XML parser doesn't like these, so they must be replaced
before parsing.
'''

import re
from . import escape_codes

ESCAPES = escape_codes.ESCAPES
ESCAPES.update({
    ':=': '≔',
    r'\*=': '⩮',  # NOTE: * is escaped for use in re
    '==': '⩵',
    '!=': '≠',
    '&InvisibleComma;': '',
    '&InvisibleTimes;': '',
    # These are picked up by XML parser already
    # '&lt;' : '<',
    # '&gt;' : '>',
    # '&amp;': '&',
    })

regex = re.compile('|'.join(map(re.escape, ESCAPES.keys())))


def unescape(xmlstr: str) -> str:
    ''' Remove MathML escape codes from xml string '''
    xml = regex.sub(lambda match: ESCAPES[match.group(0)], xmlstr)

    # Replace hyphens with real minus signs, but only within numbers/operators
    # (due to re.escape, the compiled regex used above won't
    #  work for these substitutions)
    xml = re.sub(r'<mn.*>\s*-', '<mn>−', xml)
    xml = re.sub(r'<mo.*>\s*-\s*</mo>', '<mo> − </mo>', xml)
    return xml
