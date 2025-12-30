''' <mfenced> math element '''
from typing import Union
from itertools import chain, zip_longest
from contextlib import suppress
import xml.etree.ElementTree as ET

from ziafont.fonttypes import BBox

from .. import operators
from ..drawable import Glyph
from .mnode import Mnode


class Mfenced(Mnode, tag='mfenced'):
    ''' Mfence element. Puts contents in parenthesis or other fence glyphs, with
        optional separators between components.
    '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        self.openchr = element.get('open', '(')
        self.closechr = element.get('close', ')')
        self.separators = element.get('separators', ',').replace(' ', '')
        self._xadvance = 0.
        self._setup(**kwargs)

    def xadvance(self) -> float:
        ''' X-advance for the Mrow '''
        return self._xadvance

    def _setup(self, **kwargs) -> None:
        separator_elms = [ET.fromstring(f'<mo>{k}</mo>') for k in self.separators]
        fencedelms: Union[list[ET.Element], ET.Element] = []
        # Insert separators
        if len(self.element) > 1 and len(self.separators) > 0:
            fencedelms = list(chain.from_iterable(zip_longest(
                    self.element, separator_elms, fillvalue=separator_elms[-1])))   # flatten
            fencedelms = fencedelms[:len(self.element)*2-1]  # Remove any separators at end
        else:
            # Single element in fence, no separators
            fencedelms = self.element

        mrowelm = ET.Element('mrow')
        mrowelm.extend(fencedelms)

        # Make a copy of mrowelm because it can get modified
        # and we need the original later
        mrow = Mnode.fromelement(ET.fromstring(ET.tostring(mrowelm)), parent=self)
        # standard size fence glyph
        openglyph = self.font.glyph(self.openchr)
        mglyph = Glyph(
            openglyph, self.openchr, self.glyphsize, self.style, **kwargs)
        if len(mrow.nodes) == 0:
            # Opening fence with nothing in it
            fencebbox = mglyph.bbox
            xadvance = mglyph.xadvance()
            oglyph = Glyph(openglyph, self.openchr, self.glyphsize,
                           self.style, **kwargs)
        else:
            ymin = self.points_to_units(mrow.bbox.ymin)
            if 'minsize' in self.element.attrib:
                ymax = self.points_to_units(self.size_px(self.element.get('minsize', '0'))) + ymin
                openglyph = self.font.math.variant_minmax(openglyph.index, ymin, ymax)
            else:
                ymax = self.points_to_units(mrow.bbox.ymax)# + ymin
                openglyph = self.font.math.variant_minmax(openglyph.index,
                                                          ymin,
                                                          ymax)

            oglyph = Glyph(openglyph, self.openchr, self.glyphsize,
                           self.style, **kwargs)
            
            if self.closechr:
                closeglyph = self.font.glyph(self.closechr)
                if 'minsize' in self.element.attrib:
                    closeglyph = self.font.math.variant(closeglyph.index, ymax-ymin)
                else:
                    closeglyph = self.font.math.variant_minmax(closeglyph.index,
                                                           ymin,
                                                           ymax)
                cglyph = Glyph(closeglyph, self.closechr, self.glyphsize,
                               self.style, **kwargs)

            # Rebuild the mrow with the height parameter to get stretchy
            # \middle fences
            mrowelm = ET.Element('mrow')
            mrowelm.extend(fencedelms)
            mrow = Mnode.fromelement(mrowelm, parent=self, height=oglyph.bbox.ymax-oglyph.bbox.ymin)
            fencebbox = mrow.bbox
            xadvance = mrow.xadvance()

        self.nodes = []
        x = xmax = yofst = base = 0.
        yglyphmin = yglyphmax = 0.
        with suppress(AttributeError):
            if self.parent.leftsibling():
                x += self.size_px('verythinmathspace')

        if self.openchr:
            self.nodes.append(oglyph)
            self.nodexy.append((x, yofst))
            params = operators.get_params(self.openchr, 'prefix')
            x += self.units_to_points(openglyph.advance())
            x += self.size_px(params.get('rspace', '0'))
            xmax = x
            yglyphmin = min(-yofst+oglyph.bbox.ymin, yglyphmin)
            yglyphmax = max(-yofst+oglyph.bbox.ymax, yglyphmax)
        
        x += mrow.bbox.xmin
        if len(fencedelms) > 0:
            self.nodes.append(mrow)
            self.nodexy.append((x, base))
            xmax = max(xmax, x+mrow.bbox.xmax)
            x += xadvance

        if self.closechr:
            with suppress(IndexError, AttributeError):
                # Mfrac, Msub adds space to right, remove it for fence
                if mrow.nodes[-1].mtag in ['msub', 'msup', 'msubsup']:
                    x -= self.units_to_points(self.font.math.consts.spaceAfterScript)
                elif mrow.nodes[-1].mtag == 'mfrac':
                    x -= self.size_px('thinmathspace')

            if (lastg := mrow.lastglyph()):
                if (italicx := self.font.math.italicsCorrection.getvalue(lastg.index)):
                    x += mrow.units_to_points(italicx)

            params = operators.get_params(self.closechr, 'postfix')
            x += self.size_px(params.get('lspace', '0'))

            self.nodes.append(cglyph)
            self.nodexy.append((x, yofst))
            x += self.units_to_points(closeglyph.advance())
            xmax = max(xmax, x)
            yglyphmin = min(-yofst+cglyph.bbox.ymin, yglyphmin)
            yglyphmax = max(-yofst+cglyph.bbox.ymax, yglyphmax)

        self.bbox = BBox(0, xmax, min(yglyphmin, fencebbox.ymin), max(yglyphmax, fencebbox.ymax))
        self._xadvance = xmax
