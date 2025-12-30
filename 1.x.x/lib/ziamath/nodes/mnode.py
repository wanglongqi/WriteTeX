''' Math node - parent class of all math nodes '''
from __future__ import annotations
from typing import Optional, MutableMapping, Type
import logging
from xml.etree import ElementTree as ET

from ziafont.fonttypes import BBox
from ziafont.glyph import SimpleGlyph, fmt

from ..mathfont import MathFont
from ..drawable import Drawable
from ..styles import MathStyle, parse_style
from ..config import config
from .. import operators
from .nodetools import elementtext, infer_opform

_node_classes: dict[str, Type['Mnode']] = {}


class Mnode(Drawable):
    ''' Math Drawing Node

        Args:
            element: XML element for the node
            size: base font size in points
            parent: Mnode of parent
    '''
    mtag = 'mnode'

    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__()
        self.element = element
        self.font: MathFont = parent.font
        self.parent = parent
        self.size: float = parent.size
        self.style: MathStyle = parse_style(self.element, parent.style)
        self.params: MutableMapping[str, str] = {}
        self.nodes: list[Drawable] = []
        self.nodexy: list[tuple[float, float]] = []
        self.glyphsize = max(
            self.size * (self.font.math.consts.scriptPercentScaleDown/100)**self.style.scriptlevel,
            self.font.basesize*config.minsizefraction)
        if self.style.mathsize:
            self.glyphsize = self.size_px(self.style.mathsize)

        self._font_pts_per_unit = self.size / self.font.info.layout.unitsperem
        self._glyph_pts_per_unit = self.glyphsize / self.font.info.layout.unitsperem
        self.bbox = BBox(0, 0, 0, 0)

    def __init_subclass__(cls, tag: str) -> None:
        ''' Register this subclass so fromelement() can find it '''
        _node_classes[tag] = cls
        cls.mtag = tag

    @classmethod
    def fromelement(cls, element: ET.Element, parent: 'Mnode', **kwargs) -> 'Mnode':
        ''' Construct a new node from the element and its parent '''
        if element.tag in ['math', 'mtd', 'mtr', 'none']:
            element.tag = 'mrow'
        elif element.tag == 'ms':
            element.tag = 'mtext'
        elif element.tag == 'mi' and elementtext(element) in operators.names:
            # Workaround for some latex2mathml operators coming back as identifiers
            element.tag = 'mo'

        if element.tag == 'mo':
            infer_opform(0, element, parent)

        node = _node_classes.get(element.tag, None)
        if node:
            return node(element, parent, **kwargs)

        logging.warning('Undefined element %s', element)
        return _node_classes['mrow'](element, parent, **kwargs)

    def _setup(self, **kwargs) -> None:
        ''' Calculate node position assuming this node is at 0, 0. Also set bbox. '''
        self.bbox = BBox(0, 0, 0, 0)

    def units_to_points(self, value: float) -> float:
        ''' Convert value in font units to points at this glyph size '''
        return value * self._glyph_pts_per_unit

    def font_units_to_points(self, value: float) -> float:
        ''' Convert value in font units to points at the base font size '''
        return value * self._font_pts_per_unit

    def points_to_units(self, value: float) -> float:
        ''' Convert points back to font units '''
        return value / self._glyph_pts_per_unit

    def increase_child_scriptlevel(self, element: ET.Element, n: int = 1) -> None:
        ''' Increase the child element's script level one higher
            than this element, if not overridden in child's attributes
        '''
        element.attrib.setdefault('scriptlevel', str(self.style.scriptlevel+n))

    def leftsibling(self) -> Optional[Drawable]:
        ''' Left node sibling. The one that was just placed. '''
        try:
            node = self.parent.nodes[-1]
            if node.mtag == 'mrow' and node.nodes:
                node = node.nodes[-1]
        except (IndexError, AttributeError):
            node = None

        return node

    def firstglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the first glyph in this node '''
        try:
            return self.nodes[0].firstglyph()
        except IndexError:
            return None

    def lastglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the last glyph in this node '''
        try:
            return self.nodes[-1].lastglyph()
        except IndexError:
            return None

    def lastchar(self) -> Optional[str]:
        ''' Get the last character in this node '''
        try:
            return self.nodes[-1].lastchar()
        except IndexError:
            return None

    def size_px(self, size: str, fontsize: Optional[float] = None) -> float:
        ''' Get size in points from the attribute string '''
        if fontsize is None:
            fontsize = self.glyphsize

        numsize = {"veryverythinmathspace": f'{1/18}em',
                   "verythinmathspace": f'{2/18}em',
                   "thinmathspace": f'{3/18}em',
                   "mediummathspace": f'{4/18}em',
                   "thickmathspace": f'{5/18}em',
                   "verythickmathspace": f'{6/18}em',
                   "veryverythickmathspace": f'{7/18}em',
                   "negativeveryverythinmathspace": f'{-1/18}em',
                   "negativeverythinmathspace": f'{-2/18}em',
                   "negativethinmathspace": f'{-3/18}em',
                   "negativemediummathspace": f'{-4/18}em',
                   "negativethickmathspace": f'{-5/18}em',
                   "negativeverythickmathspace": f'{-6/18}em',
                   "negativeveryverythickmathspace": f'{-7/18}em',
                   }.get(size, size)

        try:
            # Plain number, or value in px
            pxsize = float(numsize.rstrip('px'))
        except ValueError as exc:
            pass
        else:
            return pxsize

        try:
            # Units are always last 2 chars
            units = numsize[-2:]
            value = float(numsize[:-2])
        except ValueError:
            return 0

        # Conversion values from:
        # https://tex.stackexchange.com/questions/8260/what-are-the-various-units-ex-em-in-pt-bp-dd-pc-expressed-in-mm
        UNITS_TO_PT = {
            'pt': 1,
            'mm': 2.84526,
            'cm': 28.45274,
            'ex': 4.30554,
            'em': 10.00002,
            'bp': 1.00374,
            'dd': 1.07,
            'pc': 12,
            'in': 72.27,
            'mu': 0.5555,
        }
        # Convert units to points, then to pixels (= 1.333 px/pt)
        pxsize = value * UNITS_TO_PT.get(units, 0) * 1.333

        if units in ['em', 'ex', 'mu']:
            # These are fontsize dependent, table is based
            # on 10-point font
            pxsize *= fontsize/10
        return pxsize

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        if config.debug.bbox:
            rect = ET.SubElement(svg, 'rect')
            rect.set('x', fmt(x + self.bbox.xmin))
            rect.set('y', fmt(y - self.bbox.ymax))
            rect.set('width', fmt((self.bbox.xmax - self.bbox.xmin)))
            rect.set('height', fmt((self.bbox.ymax - self.bbox.ymin)))
            rect.set('fill', 'none')
            rect.set('stroke', 'blue')
            rect.set('stroke-width', '0.2')
        if config.debug.baseline:
            base = ET.SubElement(svg, 'path')
            base.set('d', f'M {x} 0 L {x+self.bbox.xmax} 0')
            base.set('stroke', 'red')

        if self.style.mathbackground not in ['none', None]:
            rect = ET.SubElement(svg, 'rect')
            rect.set('x', fmt(x + self.bbox.xmin))
            rect.set('y', fmt(y - self.bbox.ymax))
            rect.set('width', fmt((self.bbox.xmax - self.bbox.xmin)))
            rect.set('height', fmt((self.bbox.ymax - self.bbox.ymin)))
            rect.set('fill', str(self.style.mathbackground))

        nodex = nodey = 0.
        for (nodex, nodey), node in zip(self.nodexy, self.nodes):
            node.draw(x+nodex, y+nodey, svg)
        return x+nodex, y+nodey
