''' <mrow> Math Elelment '''
from __future__ import annotations
from typing import Optional, Union
from copy import copy
from xml.etree import ElementTree as ET

from ziafont.fonttypes import BBox
from ziafont.glyph import SimpleGlyph, fmt

from ..drawable import Drawable
from .. import operators
from .nodetools import infer_opform, elementtext
from .mnode import Mnode


class Mrow(Mnode, tag='mrow'):
    ''' Math row, list of vertically aligned Mnodes '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        self._xadvance = 0.
        self._setup(**kwargs)

    def xadvance(self) -> float:
        ''' X-advance for the Mrow '''
        return self._xadvance

    def _break_lines(self) -> list[list[ET.Element]]:
        ''' Break mrow into lines - to handle mspace linebreak (// in latex) '''
        lines = []
        line: list[ET.Element] = []
        for i, child in enumerate(self.element):
            if child.tag == 'mi' and elementtext(child) in operators.names:
                # Workaround for some latex2mathml operators coming back as identifiers
                child.tag = 'mo'

            if child.tag == 'mo':
                infer_opform(i, child, self)
            if child.tag == 'mspace' and child.get('linebreak', None) == 'newline':
                lines.append(line)
                line = []
            else:
                line.append(child)
        lines.append(line)
        return lines

    def _setup_multilines(self, lines: list[list[ET.Element]], **kwargs) -> None:
        ''' Multiline mrow - process each line as an mrow so we can
            get its bounding box '''
        node: Union[Mnode, Drawable]
        for i, line in enumerate(lines):
            mrowelm = ET.Element('mrow')
            mrowelm.extend(line)
            node = Mrow(mrowelm, parent=self)
            self.nodes.append(node)

        y = 0
        if self.parent.parent.mtag != 'math':
            # Not a top-level set of rows. Center them vertically.
            height = sum(node.bbox.ymax - node.bbox.ymin + 2 * self.units_to_points(self.font.math.consts.mathLeading) for node in self.nodes[1:])
            for i, node in enumerate(self.nodes):
                if i > 0:
                    y += (node.bbox.ymax - self.nodes[i-1].bbox.ymin +
                          2 * self.units_to_points(self.font.math.consts.mathLeading))
                self.nodexy.append((0, y - height/2))
            ymin = -y + self.nodes[-1].bbox.ymin + height/2
            ymax = self.nodes[0].bbox.ymax + height/2

        else:
            # Top-level rows. First row is at y=0.
            for i, node in enumerate(self.nodes):
                if i > 0:
                    y += (node.bbox.ymax - self.nodes[i-1].bbox.ymin +
                        2 * self.units_to_points(self.font.math.consts.mathLeading))
                self.nodexy.append((0, y))
            ymin = -y+self.nodes[-1].bbox.ymin
            ymax = self.nodes[0].bbox.ymax
        xmin = min([n.bbox.xmin for n in self.nodes])
        xmax = max([n.bbox.xmax for n in self.nodes])
        self.bbox = BBox(xmin, xmax, ymin, ymax)
        self._xadvance = max([n.xadvance() for n in self.nodes])

    def _get_height_nostretch(self, line: list[ET.Element], **kwargs) -> tuple[float, float]:
        ''' Get height of mrow if no vertical stretchy elements are included.
            Use this to determine how much to stretch them.
        '''
        ymax = -9999
        ymin = 9999
        kwargs['nostretch'] = True  # Tell child elements not to include stretchy operators in bbox

        for child in line:
            text = elementtext(child)
            if child.tag == 'mo' and text == '':
                continue

            # Make string copy to not overwrite element attributes
            node = Mnode.fromelement(ET.fromstring(ET.tostring(child)),
                                     parent=self, **kwargs)
            ymax = max(ymax, node.bbox.ymax)
            ymin = min(ymin, node.bbox.ymin)
        return ymin, ymax

    def _setup_single_line(self, line: list[ET.Element], **kwargs) -> None:
        ''' Single line mrow '''
        rowymin, rowymax = self._get_height_nostretch(line, **kwargs)
        kwargs['rowymin'] = rowymin
        kwargs['rowymax'] = rowymax

        ymax = -9999
        ymin = 9999
        x = xmin = xmax = 0.

        for child in line:
            text = elementtext(child)
            if child.tag == 'mo' and text == '':
                continue

            node = Mnode.fromelement(child, parent=self, **kwargs)
            self.nodes.append(node)
            self.nodexy.append((x, 0))
            xmax = max(xmax, x + node.bbox.xmax)
            xmin = min([nxy[0]+n.bbox.xmin for nxy, n in zip(self.nodexy, self.nodes)])
            ymax = max(ymax, node.bbox.ymax)
            ymin = min(ymin, node.bbox.ymin)
            x += node.xadvance()
        self.bbox = BBox(xmin, xmax, ymin, ymax)
        self._xadvance = x

    def _setup(self, **kwargs) -> None:
        kwargs = copy(kwargs)
        self.nodes = []

        lines = self._break_lines()
        if len(lines) > 1:
            self._setup_multilines(lines, **kwargs)
        else:
            self._setup_single_line(lines[0], **kwargs)

    def firstglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the first glyph in this node '''
        i = 0
        while (i < len(self.nodes) and
               isinstance(self.nodes[i], Mnode) and
               self.nodes[i].mtag == 'mspace' and
               self.nodes[i].width <= 0):  # type: ignore
            i += 1  # Negative space shouldn't count as first glyph

        try:
            glyph = self.nodes[i].firstglyph()
        except IndexError:
            return None
        return glyph


class Merror(Mrow, tag='merror'):
    ''' Error node <merror>. Just an <mrow> with border and fill. '''
    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        xend, yend = super().draw(x, y, svg)
        border = ET.SubElement(svg, 'rect')
        border.set('x', fmt(x + self.bbox.xmin - 1))
        border.set('y', fmt(y - self.bbox.ymax - 1))
        border.set('width', fmt((self.bbox.xmax - self.bbox.xmin)+2))
        border.set('height', fmt((self.bbox.ymax - self.bbox.ymin)+2))
        border.set('fill', 'yellow')
        border.set('fill-opacity', '0.2')
        border.set('stroke', 'red')
        border.set('stroke-width', '1')
        return xend, yend