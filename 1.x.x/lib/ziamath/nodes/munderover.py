''' <mover> and <munder> Math Elements '''
from __future__ import annotations
from typing import Optional, Union
import xml.etree.ElementTree as ET
from copy import copy

from ziafont.fonttypes import BBox
from ziafont.glyph import SimpleGlyph

from ..mathfont import MathFont
from .. import drawable
from .nodetools import elementtext, node_is_singlechar
from . import Mnode


# Accents are drawn same scriptlevel as base
ACCENTS = [
    0x005E,  # \hat, \widehat
    0x02D9,  # \dot
    0x02C6,  # \hat
    0x02C7,  # \check
    0x007E,  # \tilde, \widetilde
    0x00B4,  # \acute
    0x0060,  # \grave
    0x00A8,  # \ddot
    0x20DB,  # \dddot
    0x20DC,  # \ddddot
    0x02D8,  # \breve
    0x00AF,  # \bar
    0x02DA,  # \mathring
    ]


def place_over(base: Mnode,
               over: Union[Mnode, drawable.HLine],
               font: MathFont) -> tuple[float, float]:
    ''' Place node over another one

        Args:
            base: Base node
            over: Node to draw over the base
            font: Font

        Returns:
            x, y: position for over node
    '''
    # Center the node by default
    x = (((base.bbox.xmax - base.bbox.xmin) - (over.bbox.xmax-over.bbox.xmin)) / 2
         - over.bbox.xmin)

    if ((lastg := base.lastglyph())
            and node_is_singlechar(base)
            and not isinstance(over, drawable.HLine)):
        # Italic adjustment and font-specific accent attachment,
        # if base is a single glyph
        if (italicx := font.math.italicsCorrection.getvalue(lastg.index)):
            x += base.units_to_points(italicx)

        # Use font-specific accent attachment if defined
        if (basex := font.math.topattachment(lastg.index)):
            x = base.units_to_points(basex)

            if (node_is_singlechar(over)
                    and (attachx := font.math.topattachment(over.lastglyph().index))):  # type: ignore
                x -= over.units_to_points(attachx)
            else:
                x -= (over.bbox.xmax-over.bbox.xmin)/2 + over.bbox.xmin/2

    y = -base.bbox.ymax - base.units_to_points(font.math.consts.overbarVerticalGap)
    y += over.bbox.ymin
    return x, y


def place_under(base: Mnode,
                under: Union[Mnode, drawable.HLine],
                font: MathFont) -> tuple[float, float]:
    ''' Place node under another one
        Args:
            base: Base node
            under: Node to draw under the base
            font: Font

        Returns:
            x, y: position for under node
    '''
    x = (((base.bbox.xmax - base.bbox.xmin) - (under.bbox.xmax-under.bbox.xmin)) / 2
         - under.bbox.xmin)

    if ((lastg := base.lastglyph())
            and node_is_singlechar(base)
            and not isinstance(under, drawable.HLine)):
        if (italicx := font.math.italicsCorrection.getvalue(lastg.index)):
            x -= base.units_to_points(italicx)

    y = -base.bbox.ymin + base.units_to_points(font.math.consts.underbarVerticalGap)
    y += (under.bbox.ymax)
    return x, y


class Mover(Mnode, tag='mover'):
    ''' Over node '''
    # Over/underbar character. Fonts not consistent with using stretchy/assembled
    # glyphs, so draw with HLine instead of glyph.
    BAR = '―'  # 0x2015

    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        self.over: Union[drawable.HLine, Mnode]

        kwargs = copy(kwargs)
        assert len(self.element) == 2
        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        if (self.element[1].tag in ['mover', 'munder']
                or (self.element[1].tag == 'mo' and len(elementtext(self.element[1])) == 1)):
            kwargs['width'] = self.base.bbox.xmax - self.base.bbox.xmin

        self._isaccent = False
        if not (len(elementtext(self.element[1])) == 1
                and ord(elementtext(self.element[1])) in ACCENTS):
            if self.element.get('accent', 'false').lower() == 'false':
                self.increase_child_scriptlevel(self.element[1])
            self._isaccent = True

        if elementtext(self.element[1]) == self.BAR:
            self.over = drawable.HLine(
                kwargs['width'],
                self.units_to_points(self.font.math.consts.overbarRuleThickness))
        else:
            if self.element[1].get('stretchy') == 'true':
                self.element[1].set('lspace', '0')
                self.element[1].set('rspace', '0')
            self.over = Mnode.fromelement(self.element[1], parent=self, **kwargs)

        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        overx, overy = place_over(self.base, self.over, self.font)
        basex = 0.
        if overx < 0:
            basex = -overx
            overx = 0.

        self.nodes.append(self.base)
        self.nodexy.append((basex, 0))
        self.nodes.append(self.over)
        self.nodexy.append((overx, overy))

        xmin = min(overx+self.over.bbox.xmin, basex+self.base.bbox.xmin)
        xmax = max(overx+self.over.bbox.xmax, basex+self.base.bbox.xmax)
        ymin = self.base.bbox.ymin
        ymax = -overy + self.over.bbox.ymax
        self.bbox = BBox(xmin, xmax, ymin, ymax)
        if not self._isaccent:
            self._xadvance = basex + self.base.xadvance()
            self.base_xadvance = self._xadvance  # For attaching subscripts
        else:
            self._xadvance = xmax
            self.base_xadvance = basex + self.base.xadvance()

    def xadvance(self) -> float:
        return self._xadvance

    def lastglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the last glyph in this node '''
        return self.base.lastglyph()


class Munder(Mnode, tag='munder'):
    ''' Under node '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        self.under: Union[drawable.HLine, Mnode]

        kwargs = copy(kwargs)
        assert len(self.element) == 2
        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        kwargs['sub'] = True
        if (self.element[1].tag in ['mover', 'munder', 'munderover']
                or (self.element[1].tag == 'mo' and len(elementtext(self.element[1])) == 1)):
            kwargs['width'] = self.base.bbox.xmax - self.base.bbox.xmin

        if elementtext(self.element[1]) == Mover.BAR:
            self.under = drawable.HLine(
                kwargs['width'],
                self.units_to_points(self.font.math.consts.underbarRuleThickness))
        else:
            if self.element[1].get('stretchy') == 'true':
                self.element[1].set('lspace', '0')
                self.element[1].set('rspace', '0')
            if self.element.get('accentunder', 'false').lower() == 'false':
                self.increase_child_scriptlevel(self.element[1])
                self._isaccent = True
            self.under = Mnode.fromelement(self.element[1], parent=self, **kwargs)
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        underx, undery = place_under(self.base, self.under, self.font)

        basex = 0.
        if underx < 0:
            basex = -underx
            underx = 0

        self.nodes.append(self.base)
        self.nodexy.append((basex, 0))
        self.nodes.append(self.under)
        self.nodexy.append((underx, undery))

        xmin = min(underx+self.under.bbox.xmin, basex+self.base.bbox.xmin)
        xmax = max(underx+self.under.bbox.xmax, basex+self.base.bbox.xmax)
        ymin = -undery + self.under.bbox.ymin
        ymax = self.base.bbox.ymax
        self.bbox = BBox(xmin, xmax, ymin, ymax)

    def lastglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the last glyph in this node '''
        return self.base.lastglyph()


class Munderover(Mnode, tag='munderover'):
    ''' Under bar and over bar '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        kwargs = copy(kwargs)
        assert len(self.element) == 3
        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        kwargs['sub'] = True
        if (self.element[1].tag in ['mover', 'munder', 'munderover']
                or (self.element[1].tag == 'mo' and len(elementtext(self.element[1])) == 1)):
            kwargs['width'] = self.base.bbox.xmax - self.base.bbox.xmin
        if self.element.get('accentunder', 'false').lower() == 'false':
            self.increase_child_scriptlevel(self.element[1])

        self.under = Mnode.fromelement(self.element[1], parent=self, **kwargs)

        kwargs.pop('width', None)
        kwargs.pop('sub', None)
        if (self.element[2].tag in ['mover', 'munder']
                or (self.element[2].tag == 'mo' and len(elementtext(self.element[2])) == 1)):
            kwargs['width'] = self.base.bbox.xmax - self.base.bbox.xmin

        if not (len(elementtext(self.element[2])) == 1
                and ord(elementtext(self.element[2])) in ACCENTS):
            if self.element[2].get('stretchy') == 'true':
                self.element[2].set('lspace', '0')
                self.element[2].set('rspace', '0')
            if self.element.get('accent', 'false').lower() == 'false':
                self.increase_child_scriptlevel(self.element[2])

        self.over = Mnode.fromelement(self.element[2], parent=self, **kwargs)
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        self.nodes = []
        overx, overy = place_over(self.base, self.over, self.font)
        underx, undery = place_under(self.base, self.under, self.font)

        basex = 0.
        if overx < 0 or underx < 0:
            basex = max(-overx, -underx)
            overx, underx = overx - min(overx, underx), underx - min(overx, underx)

        self.nodes.append(self.base)
        self.nodexy.append((basex, 0))
        self.nodes.append(self.over)
        self.nodes.append(self.under)
        self.nodexy.append((overx, overy))
        self.nodexy.append((underx, undery))
        xmin = min(underx, overx, basex+self.base.bbox.xmin)
        xmax = max(underx+self.under.bbox.xmax,
                   overx+self.over.bbox.xmax,
                   basex+self.base.bbox.xmax)
        ymin = -undery + self.under.bbox.ymin
        ymax = -overy + self.over.bbox.ymax
        self.bbox = BBox(xmin, xmax, ymin, ymax)

    def lastglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the last glyph in this node '''
        return self.base.lastglyph()
