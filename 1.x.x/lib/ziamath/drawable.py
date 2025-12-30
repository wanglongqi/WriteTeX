from __future__ import annotations
from typing import Optional
import math
import xml.etree.ElementTree as ET

from ziafont.fonttypes import BBox
from ziafont.glyph import SimpleGlyph, fmt
from .config import config
from .styles import MathStyle


class Drawable:
    ''' Base class for drawable nodes '''
    mtag = 'drawable'
    nodes: list[Drawable] = []

    def __init__(self):
        self.bbox = BBox(0, 0, 0, 0)

    def firstglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the first glyph in this node '''
        return None

    def lastglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the last glyph in this node '''
        return None

    def lastchar(self) -> Optional[str]:
        ''' Get the last character in this node '''
        return None

    def xadvance(self) -> float:
        ''' X-advance for the glyph. Usually bbox.xmax '''
        return self.bbox.xmax

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the element. Must be subclassed. '''
        raise NotImplementedError


class Glyph(Drawable):
    ''' A single glyph

        Args:
            glyph: The glyph to draw
            char: unicode character represented by the glyph
            size: point size
            style: font MathStyle
    '''
    def __init__(self, glyph: SimpleGlyph, char: str, size: float,
                 style: Optional[MathStyle] = None, **kwargs):
        super().__init__()
        self.glyph = glyph
        self.char = char
        self.size = size
        self.phantom = kwargs.get('phantom', False)
        self.style = style if style else MathStyle()
        self._funits_to_pts = self.size / self.glyph.font.info.layout.unitsperem
        self.bbox = BBox(
            self.funit_to_points(self.glyph.path.bbox.xmin),
            self.funit_to_points(self.glyph.path.bbox.xmax),
            self.funit_to_points(self.glyph.path.bbox.ymin),
            self.funit_to_points(self.glyph.path.bbox.ymax))
        
    def funit_to_points(self, value: float) -> float:
        ''' Convert font units to SVG points '''
        return value * self._funits_to_pts

    def firstglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the first glyph in this node '''
        return self.glyph

    def lastglyph(self) -> Optional[SimpleGlyph]:
        ''' Get the last glyph in this node '''
        return self.glyph

    def lastchar(self) -> Optional[str]:
        ''' Get the last character in this node '''
        return self.char

    def xadvance(self) -> float:
        ''' X-advance for the glyph. Usually bbox.xmax '''
        return self.funit_to_points(self.glyph.advance())

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        symbols = svg.findall('symbol')
        symids = [sym.attrib.get('id') for sym in symbols]
        if self.glyph.id not in symids and config.svg2:
            svg.append(self.glyph.svgsymbol())
        if not self.phantom:
            path = self.glyph.place(x, y, self.size)
            if path is not None:
                svg.append(path)
            if self.style.mathcolor and len(svg) > 0:
                svg[-1].set('fill', str(self.style.mathcolor))
        x += self.funit_to_points(self.glyph.advance())
        return x, y


class HLine(Drawable):
    ''' Horizontal Line. '''
    def __init__(self, length: float, lw: float,
                 style: Optional[MathStyle] = None, **kwargs):
        super().__init__()
        self.length = length
        self.lw = lw
        self.phantom = kwargs.get('phantom', False)
        self.bbox = BBox(0, self.length, -self.lw/2, self.lw/2)
        self.style = style if style else MathStyle()

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        if not self.phantom:
            # Use rectangle so it can change color with 'fill' attribute
            # and not mess up glyphs with 'stroke' attribute
            bar = ET.SubElement(svg, 'rect')
            bar.attrib['x'] = fmt(x)
            bar.attrib['y'] = fmt(y)
            bar.attrib['width'] = fmt(self.length)
            bar.attrib['height'] = fmt(self.lw)
            if self.style.mathcolor:
                bar.attrib['fill'] = str(self.style.mathcolor)
        return x+self.length, y


class VLine(Drawable):
    ''' Vertical Line. '''
    def __init__(self, height: float, lw: float,
                 style: Optional[MathStyle] = None, **kwargs):
        super().__init__()
        self.height = height
        self.lw = lw
        self.phantom = kwargs.get('phantom', False)
        self.bbox = BBox(0, self.lw, 0, self.height)
        self.style = style if style else MathStyle()

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        if not self.phantom:
            # Use rectangle so it can change color with 'fill' attribute
            # and not mess up glyphs with 'stroke' attribute
            bar = ET.SubElement(svg, 'rect')
            bar.attrib['x'] = fmt(x-self.lw/2)
            bar.attrib['y'] = fmt(y)
            bar.attrib['width'] = fmt(self.lw)
            bar.attrib['height'] = fmt(self.height)
            if self.style.mathcolor:
                bar.attrib['fill'] = str(self.style.mathcolor)
        return x, y


class Box(Drawable):
    ''' Box '''
    def __init__(self, width: float, height: float, lw: float,
                 cornerradius: Optional[float] = None,
                 style: Optional[MathStyle] = None, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        self.cornerradius = cornerradius
        self.lw = lw
        self.phantom = kwargs.get('phantom', False)
        self.bbox = BBox(0, self.width, 0, self.height)
        self.style = style if style else MathStyle()

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        if not self.phantom:
            bar = ET.SubElement(svg, 'rect')
            bar.set('x', fmt(x))
            bar.set('y', fmt(y-self.height))
            bar.set('width', fmt(self.width))
            bar.set('height', fmt(self.height))
            bar.set('stroke-width', fmt(self.lw))
            bar.set('stroke', self.style.mathcolor)
            bar.set('fill', self.style.mathbackground)
            if self.cornerradius:
                bar.set('rx', fmt(self.cornerradius))

        return x+self.width, y


class Diagonal(Drawable):
    ''' Diagonal Line - corners of Box '''
    def __init__(self, width: float, height: float, lw: float,
                 arrow: bool = False,
                 style: Optional[MathStyle] = None, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        self.lw = lw
        self.arrow = arrow
        self.phantom = kwargs.get('phantom', False)
        self.bbox = BBox(0, self.width, 0, self.height)
        self.style = style if style else MathStyle()

        self.arroww = self.width
        self.arrowh = self.height
        if self.arrow:
            # Bbox needs to be a bit bigger to accomodate arrowhead
            theta = math.atan2(-self.height, self.width)
            self.arroww = (10+self.lw*2) * math.cos(theta)
            self.arrowh = (10+self.lw*2) * math.sin(theta)

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        if not self.phantom:
            bar = ET.SubElement(svg, 'path')
            if self.arrow:
                arrowdef = ET.SubElement(svg, 'defs')
                marker = ET.SubElement(arrowdef, 'marker')
                marker.set('id', 'arrowhead')
                marker.set('markerWidth', '10')
                marker.set('markerHeight', '7')
                marker.set('refX', '0')
                marker.set('refY', '3.5')
                marker.set('orient', 'auto')
                poly = ET.SubElement(marker, 'polygon')
                poly.set('points', '0 0 10 3.5 0 7')

            bar.set('d', f'M {fmt(x)} {fmt(y-self.height)} L {fmt(x+self.width)} {fmt(y)}')
            bar.set('stroke-width', fmt(self.lw))
            bar.set('stroke', self.style.mathcolor)
            if self.arrow:
                bar.set('marker-end', 'url(#arrowhead)')

        return x+self.width, y


class Ellipse(Drawable):
    ''' Ellipse '''
    def __init__(self, width: float, height: float, lw: float,
                 style: Optional[MathStyle] = None, **kwargs):
        super().__init__()
        self.width = width
        self.height = height
        self.lw = lw
        self.phantom = kwargs.get('phantom', False)
        self.bbox = BBox(0, self.width, 0, self.height)
        self.style = style if style else MathStyle()

    def draw(self, x: float, y: float, svg: ET.Element) -> tuple[float, float]:
        ''' Draw the node on the SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: SVG drawing as XML
        '''
        if not self.phantom:
            bar = ET.SubElement(svg, 'ellipse')
            bar.set('cx', fmt(x+self.width/2))
            bar.set('cy', fmt(y-self.height/2))
            bar.set('rx', fmt(self.width/2))
            bar.set('ry', fmt(self.height/2))
            bar.set('stroke-width', fmt(self.lw))
            bar.set('stroke', self.style.mathcolor)
            bar.set('fill', self.style.mathbackground)
        return x+self.width, y
