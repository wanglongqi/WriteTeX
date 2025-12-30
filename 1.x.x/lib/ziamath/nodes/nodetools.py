''' Common tools for evaluating nodes '''
from typing import Union, TYPE_CHECKING
from xml.etree import ElementTree as ET

from ziafont.glyph import SimpleGlyph

from ..mathfont import MathFont

if TYPE_CHECKING:
    from .mnode import Mnode
    from ..drawable import Drawable


def infer_opform(i: int, child: ET.Element, mrow: 'Mnode') -> None:
    ''' Infer form (prefix, postfix, infix) of operator child within
        element mrow. Appends 'form' attribute to child.

        Args:
            i: Index of child within parent
            child: XML element of child
            mrow: Mnode of parent element
    '''
    # Infer form for operators
    if 'form' not in child.attrib:
        if mrow.element.tag in ['msub', 'msup', 'msubsup']:
            form = 'prefix'
        elif len(mrow.element) == 1:
            form = 'none'
        elif i == 0:
            form = 'prefix'
        elif i == len(mrow.element) - 1:
            form = 'postfix'
        else:
            form = 'infix'
        child.set('form', form)


def elementtext(element: ET.Element) -> str:
    ''' Get text of XML element '''
    try:
        txt = element.text.strip()  # type: ignore
    except AttributeError:
        txt = ''
    return txt


def node_is_singlechar(node: Union['Mnode', 'Drawable']) -> bool:
    ''' Node is a single character '''
    if node.mtag == 'mrow':
        if len(node.element) > 1:  # type:ignore
            return False
        else:
            return node_is_singlechar(node.nodes[0])  # type:ignore
    return hasattr(node, 'string') and len(node.string) == 1  # type:ignore


def subglyph(glyph: SimpleGlyph, font: MathFont) -> SimpleGlyph:
    r''' Substitute glyphs using font GSUB ssty feature. This
        substitutes glyphs like \prime for use in sub/superscripts.
    '''
    if font.gsub:
        glyphids = font.gsub.sub([glyph.index], font.features)
        if glyphids[0] != glyph.index:
            glyph = font.glyph_fromid(glyphids[0])
    return glyph
