''' <mn> number math element '''
import xml.etree.ElementTree as ET

from ziafont.fonttypes import BBox

from ..styles import auto_italic
from ..drawable import Glyph, HLine
from .nodetools import subglyph, elementtext
from .mnode import Mnode


class Mnumber(Mnode, tag='mn'):
    ''' Mnumber node <mn> '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        self.string = self._getstring()
        self._setup(**kwargs)

    def _getstring(self) -> str:
        ''' Get the styled string for this node '''
        text = elementtext(self.element)
        if (not self.style.mathvariant.italic
            and not self.style.mathvariant.normal):
                # Numbers that should really be identifiers
                # such as '1cm' with units
                self.style.mathvariant.italic = True

        return text

    def _setup(self, **kwargs) -> None:
        ymin = 9999.
        ymax = -9999.
        x = 0.

        if (leftsibling := self.leftsibling()) and leftsibling.mtag == 'mfenced':
            x = self.size_px('verythinmathspace')

        for i, char in enumerate(self.string):
            glyph = self.font.findglyph(char, self.style.mathvariant)
            if kwargs.get('sup') or kwargs.get('sub'):
                glyph = subglyph(glyph, self.font)

            self.nodes.append(
                Glyph(glyph, char, self.glyphsize, self.style, **kwargs))

            if self.nodes[-1].bbox.xmin < 0:
                # don't let glyphs run together if xmin < 0
                x -= self.nodes[-1].bbox.xmin
            

            self.nodexy.append((x, 0))
            nextglyph = self.font.findglyph(self.string[i+1], self.style.mathvariant) if i < len(self.string)-1 else None
            try:
                x += self.units_to_points(glyph.advance(nextchr=nextglyph))
            except IndexError:
                # nextglyph is in a different font
                x += self.units_to_points(glyph.advance())
            ymin = min(ymin, self.units_to_points(glyph.path.bbox.ymin))
            ymax = max(ymax, self.units_to_points(glyph.path.bbox.ymax))

        try:
            xmin = self.nodes[0].bbox.xmin
            xmax = self.nodexy[-1][0] + max(self.nodes[-1].bbox.xmax,
                                            self.units_to_points(glyph.advance()))
        except IndexError:
            xmin = 0.
            xmax = x
        self.bbox = BBox(xmin, xmax, ymin, ymax)


class Midentifier(Mnumber, tag='mi'):
    ''' Identifier node <mi> '''
    def _getstring(self) -> str:
        ''' Get the styled string for the identifier. Applies
            italics if single-char identifier, and extra whitespace
            if function (eg 'sin')
        '''
        text = elementtext(self.element)
        if (len(text) == 1
                and not self.style.mathvariant.italic
                and not self.style.mathvariant.normal
                and auto_italic(text)):
            self.style.mathvariant.italic = True

        if len(text) > 1:
            # pad with thin space
            text = '\U00002009' + text
            if self.parent.mtag not in ['msub', 'msup', 'msubsup']:
                text = text + '\U00002009'

        return text


class Mtext(Mnumber, tag='mtext'):
    ''' Text Node <mtext> '''
    SPACES_PER_TAB = 4
    def _getstring(self) -> str:
        string = ''
        if self.element.text:
            # Don't use elementtext() since it strips whitespace
            string = self.element.text
            string = string.replace('\n', '').replace('\t', ' '*self.SPACES_PER_TAB)
        return string

    def _setup(self, **kwargs) -> None:
        self.font.language('DFLT', '')  # Allow standard kerning to apply
        ymin = 9999.
        ymax = -9999.
        x = 0.

        i = 0
        while i < len(self.string):
            char = self.string[i]
            if char == '-':  # repeated hyphens build up into a long horizontal line
                dashwidth = self.font.glyph('-').bbox.xmax
                dashes = 1
                i += 1
                while i < len(self.string) and self.string[i] == '-':
                    i += 1
                    dashes += 1
                width = self.units_to_points(dashes * dashwidth)
                self.nodes.append(HLine(
                    width,
                    self.units_to_points(self.font.math.consts.fractionRuleThickness),
                    style=self.style,
                    **kwargs))
                self.nodexy.append((x, -self.units_to_points(self.font.math.consts.axisHeight +
                                                             self.font.math.consts.fractionRuleThickness/2)))
                x += width

            else:
                glyph = self.font.findglyph(char, self.style.mathvariant)
                if kwargs.get('sup') or kwargs.get('sub'):
                    glyph = subglyph(glyph, self.font)

                self.nodes.append(
                    Glyph(glyph, char, self.glyphsize, self.style, **kwargs))

                self.nodexy.append((x, 0))
                nextglyph = self.font.findglyph(self.string[i+1], self.style.mathvariant) if i < len(self.string)-1 else None
                try:
                    x += self.units_to_points(glyph.advance(nextchr=nextglyph))
                except IndexError:
                    # nextglyph is in a different font
                    x += self.units_to_points(glyph.advance())
                ymin = min(ymin, self.units_to_points(glyph.path.bbox.ymin))
                ymax = max(ymax, self.units_to_points(glyph.path.bbox.ymax))
                i += 1

        self.bbox = BBox(self.nodes[0].bbox.xmin, x, ymin, ymax)
        self.font.language('math', '')
