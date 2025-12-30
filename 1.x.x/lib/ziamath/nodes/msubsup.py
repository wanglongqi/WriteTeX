''' <msub>, <msup>, <msubsup> Superscript and Subscript Elements '''
from __future__ import annotations
import xml.etree.ElementTree as ET

from ziafont.fonttypes import BBox

from ..mathfont import MathFont
from .. import operators
from .mnode import Mnode
from .nodetools import elementtext


def place_super(base: Mnode, superscript: Mnode, font: MathFont) -> tuple[float, float, float]:
    ''' Superscript. Can be above the operator (like sum) or regular super '''
    if base.params.get('movablelimits') == 'true' and base.style.displaystyle:
        x = (-(base.bbox.xmax - base.bbox.xmin) / 2
             - (superscript.bbox.xmax - superscript.bbox.xmin) / 2)
        supy = (-base.bbox.ymax
                - base.units_to_points(font.math.consts.upperLimitGapMin)
                + superscript.bbox.ymin)
        xadvance = 0.
    else:
        x = 0.
        if base.params.get('movablelimits') == 'true':
            x -= base.size_px(base.params.get('rspace', '0'))

        lastg = base.lastglyph()
        firstg = superscript.firstglyph()

        if lastg:
            if ((italicx := font.math.italicsCorrection.getvalue(lastg.index))
                    and base.lastchar() not in operators.integrals):
                x += base.units_to_points(italicx)

        shiftup = max(font.math.consts.superscriptShiftUp,
                      -firstg.bbox.ymin + font.math.consts.superscriptBottomMin if firstg else 0,
                      base.points_to_units(base.bbox.ymax) - font.math.consts.superscriptBaselineDropMax)

        if superscript.mtag in ['mi', 'mn']:
            if firstg and lastg and lastg.index >= 0 and font.math.kernInfo:  # assembled glyphs have idx<0
                kern, shiftup = font.math.kernsuper(lastg, firstg)
                x += base.units_to_points(kern)

        supy = base.units_to_points(-shiftup)
        xadvance = x + superscript.bbox.xmax

        if base.mtag == 'mi' and len(elementtext(base.element)) > 1:
            # Add a little space after functions, such as sin^2
            xadvance += base.size_px('verythinmathspace')

    return x, supy, xadvance


def place_sub(base: Mnode, subscript: Mnode, font: MathFont) -> tuple[float, float, float]:
    ''' Calculate subscript. Can be below the operator (like sum) or regular sub '''
    if base.params.get('movablelimits') == 'true' and base.style.displaystyle:
        x = -(base.bbox.xmax - base.bbox.xmin) / 2 - (subscript.bbox.xmax - subscript.bbox.xmin) / 2
        suby = (-base.bbox.ymin
                + base.units_to_points(font.math.consts.lowerLimitGapMin)
                + subscript.bbox.ymax)
        xadvance = 0.
    else:
        x = 0.

        if base.params.get('movablelimits') == 'true':
            x -= base.size_px(base.params.get('rspace', '0'))

        lastg = base.lastglyph()
        firstg = subscript.firstglyph()

        if lastg:
            if ((italicx := font.math.italicsCorrection.getvalue(lastg.index))
                    and base.lastchar() in operators.integrals):
                x -= base.units_to_points(italicx)  # Shift back on integrals

        if lastg and firstg and lastg.index > 0 and font.math.kernInfo:
            # Horizontal kern set by font
            # Ignoring vertical kern otherwise subscripts don't line up
            # across the row which looks weird
            kern, _ = font.math.kernsub(lastg, firstg)
            x += base.units_to_points(kern)

        if base.mtag in ['mi', 'mn'] or (base.mtag == 'mo' and not base.string):  # type: ignore
            shiftdn = font.math.consts.subscriptShiftDown
        elif base.mtag == 'mover' and base._isaccent:  # type: ignore
            shiftdn = font.math.consts.subscriptShiftDown
        else:
            shiftdn = max(font.math.consts.subscriptShiftDown,
                          firstg.bbox.ymax - font.math.consts.subscriptTopMax if firstg else 0,
                          font.math.consts.subscriptBaselineDropMin - base.points_to_units(base.bbox.ymin))

        suby = base.units_to_points(shiftdn)
        xadvance = x + subscript.xadvance()
    return x, suby, xadvance


class Msup(Mnode, tag='msup'):
    ''' Superscript Node '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        assert len(self.element) == 2
        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        kwargs['sup'] = True
        self.increase_child_scriptlevel(self.element[1])
        self.superscript = Mnode.fromelement(self.element[1], parent=self, **kwargs)
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        self.nodes.append(self.base)
        self.nodexy.append((0, 0))
        x = self.base.xadvance()

        supx, supy, xadv = place_super(self.base, self.superscript, self.font)
        self.nodes.append(self.superscript)
        self.nodexy.append((x+supx, supy))
        if self.base.bbox.ymax > self.base.bbox.ymin:
            xmin = min(self.base.bbox.xmin, x+supx+self.superscript.bbox.xmin)
            xmax = max(x + xadv, self.base.bbox.xmax, x+supx+self.superscript.bbox.xmax)
            ymin = min(self.base.bbox.ymin, -supy + self.superscript.bbox.ymin)
            ymax = max(self.base.bbox.ymax, -supy + self.superscript.bbox.ymax)
        else:  # Empty base
            xmin = self.superscript.bbox.xmin
            ymin = -supy
            xmax = x + xadv
            ymax = -supy + self.superscript.bbox.ymax
        self.bbox = BBox(xmin, xmax, ymin, ymax)


class Msub(Mnode, tag='msub'):
    ''' Subscript Node '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        assert len(self.element) == 2
        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        kwargs['sub'] = True
        self.increase_child_scriptlevel(self.element[1])
        self.subscript = Mnode.fromelement(self.element[1], parent=self, **kwargs)
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        self.nodes.append(self.base)
        self.nodexy.append((0, 0))
        if self.base.mtag == 'mover' and self.base._isaccent:  # type: ignore
            x = self.base.base_xadvance  # type: ignore
        else:
            x = self.base.xadvance()

        subx, suby, xadv = place_sub(self.base, self.subscript, self.font)
        self.nodes.append(self.subscript)
        self.nodexy.append((x + subx, suby))

        xmin = min(self.base.bbox.xmin, x+subx+self.subscript.bbox.xmin)
        xmax = max(x + xadv, self.base.bbox.xmax, x+subx+self.subscript.bbox.xmax)
        ymin = min(self.base.bbox.ymin, -suby+self.subscript.bbox.ymin)
        ymax = max(self.base.bbox.ymax, -suby+self.subscript.bbox.ymax)
        self.bbox = BBox(xmin, xmax, ymin, ymax)


class Msubsup(Mnode, tag='msubsup'):
    ''' Subscript and Superscript together '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        assert len(self.element) == 3
        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        kwargs['sup'] = True
        kwargs['sub'] = True
        self.increase_child_scriptlevel(self.element[1])
        self.increase_child_scriptlevel(self.element[2])
        self.subscript = Mnode.fromelement(
            self.element[1], parent=self, **kwargs)
        self.superscript = Mnode.fromelement(
            self.element[2], parent=self, **kwargs)
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        self.nodes.append(self.base)
        self.nodexy.append((0, 0))
        x = self.base.xadvance()
        subx, suby, xadvsub = place_sub(self.base, self.subscript, self.font)
        supx, supy, xadvsup = place_super(self.base, self.superscript, self.font)

        # Ensure subSuperscriptGapMin between scripts
        if ((suby - self.subscript.bbox.ymax) - (supy-self.superscript.bbox.ymin)
                < self.units_to_points(self.font.math.consts.subSuperscriptGapMin)):
            diff = (self.units_to_points(self.font.math.consts.subSuperscriptGapMin)
                    - (suby - self.subscript.bbox.ymax)
                    + (supy-self.superscript.bbox.ymin))
            suby += diff/2
            supy -= diff/2

        self.nodes.append(self.subscript)
        self.nodexy.append((x + subx, suby))
        self.nodes.append(self.superscript)
        self.nodexy.append((x + supx, supy))

        if self.base.bbox.ymax > self.base.bbox.ymin:
            xmin = self.base.bbox.xmin
            xmax = max(x + xadvsup, x + xadvsub)
            ymin = min(-self.base.bbox.ymin, -suby + self.subscript.bbox.ymin)
            ymax = max(self.base.bbox.ymax, -supy + self.superscript.bbox.ymax)
        else:  # Empty base
            xmin = 0
            ymin = -suby
            xmax = x + max(xadvsub, xadvsup)
            ymax = -supy + self.superscript.bbox.ymax

        self.bbox = BBox(xmin, xmax, ymin, ymax)


class Mmultiscripts(Mnode, tag='mmultiscripts'):
    ''' Multiple sub/superscripts in one element '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)

        self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        self.prescripts: list[ET.Element] = []
        self.postscripts: list[ET.Element] = []

        activescriptlist = self.postscripts
        for elm in self.element[1:]:
            if elm.tag == 'mprescripts':
                activescriptlist = self.prescripts
                continue
            activescriptlist.append(elm)
        self._setup(**kwargs)

    def _setup(self, **kwargs):
        ysub = self.units_to_points(self.font.math.consts.subscriptShiftDown)
        ysup = -self.units_to_points(self.font.math.consts.superscriptShiftUp)
        mingap = self.units_to_points(self.font.math.consts.subSuperscriptGapMin)
        x = xmax = 0
        ymax = self.base.bbox.ymax
        ymin = self.base.bbox.ymin

        for sub, sup in zip(self.prescripts[::2], self.prescripts[1::2]):
            self.increase_child_scriptlevel(sub)
            self.increase_child_scriptlevel(sup)
            subnode = Mnode.fromelement(sub, parent=self, **kwargs)
            supnode = Mnode.fromelement(sup, parent=self, **kwargs)
            width = max(subnode.bbox.xmax, supnode.bbox.xmax)
            self.nodes.append(subnode)
            ysub_y, ysup_y = ysub, ysup
            if ysub-subnode.bbox.ymax - (ysup-supnode.bbox.ymin) < mingap:
                overlap = ysub-subnode.bbox.ymax - (ysup-supnode.bbox.ymin)
                ysub_y -= overlap
                ysup_y -= mingap
            
            self.nodexy.append((x+width-subnode.bbox.xmax, ysub_y))
            self.nodes.append(supnode)
            self.nodexy.append((x+width-supnode.bbox.xmax, ysup_y))

            ymax = max(ymax, -ysup_y+supnode.bbox.ymax)
            ymin = min(ymin, -ysub_y+subnode.bbox.ymin)
            xmax = max(xmax, x+width)
            x += width
            x += self.units_to_points(self.font.math.consts.spaceAfterScript)

        self.nodes.append(self.base)
        self.nodexy.append((x, 0))
        x += self.base.xadvance()
        xmax = max(xmax, x+self.base.bbox.xmax)

        for sub, sup in zip(self.postscripts[::2], self.postscripts[1::2]):
            self.increase_child_scriptlevel(sub)
            self.increase_child_scriptlevel(sup)
            subnode = Mnode.fromelement(sub, parent=self, **kwargs)
            supnode = Mnode.fromelement(sup, parent=self, **kwargs)
            ysub_y, ysup_y = ysub, ysup
            if ysub-subnode.bbox.ymax - (ysup-supnode.bbox.ymin) < mingap:
                overlap = ysub-subnode.bbox.ymax - (ysup-supnode.bbox.ymin)
                ysub_y -= overlap
                ysup_y -= mingap

            self.nodes.append(subnode)
            self.nodexy.append((x, ysub_y))
            self.nodes.append(supnode)
            self.nodexy.append((x, ysup_y))

            ymax = max(ymax, -ysup_y+supnode.bbox.ymax)
            ymin = min(ymin, -ysub_y+subnode.bbox.ymin)
            xmax = max(xmax, x+subnode.bbox.xmax, x+supnode.bbox.xmax)
            x += max(subnode.xadvance(), supnode.xadvance())
            x += self.units_to_points(self.font.math.consts.spaceAfterScript)

        self.bbox = BBox(0, xmax, ymin, ymax)
