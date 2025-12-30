''' Glyph classes '''

from __future__ import annotations
from typing import Sequence, Optional, TYPE_CHECKING
from types import SimpleNamespace

import os
import xml.etree.ElementTree as ET

from .fonttypes import GlyphComp, BBox
from .config import config
from .svgpath import fmt, SVGOpType
from .inspect import InspectGlyph, DescribeGlyph

if TYPE_CHECKING:
    from .font import Font


class SimpleGlyph:
    ''' Simple Glyph '''
    DFLT_SIZE_PT = 12   # Draw <symbols> in this point size

    def __init__(self, index: int, operators: Sequence[SVGOpType],
                 bbox: BBox, font: Font):
        self.index = index
        self.operators = operators
        self.bbox = bbox
        self.path = SimpleNamespace()
        self.path.bbox = bbox  # Only for backward-compatibility
        self.font = font
        basename, _ = os.path.splitext(os.path.basename(self.font.info.filename))
        basename = ''.join(c for c in basename if c.isalnum())
        self.id = f'{basename}_{index}'
        self._points_per_unit = self.DFLT_SIZE_PT / self.font.info.layout.unitsperem

    def _repr_svg_(self):
        return ET.tostring(self.svgxml(), encoding='unicode')

    @property
    def char(self) -> set[str]:
        ''' Get set of unicode character represented by this glyph '''
        if self.font.cmap:
            return self.font.cmap.char(self.index)
        return set()

    def funits_to_points(self, value: float, scale_factor: float = 1) -> float:
        ''' Convert font units to points '''
        return value * self._points_per_unit * scale_factor

    @property
    def viewbox(self) -> tuple[float, float, float, float]:
        ''' Get viewbox of Glyph '''
        xmin = min(self.funits_to_points(self.bbox.xmin), 0)
        xmax = self.funits_to_points(self.bbox.xmax)
        ymax = self.funits_to_points(max(self.font.info.layout.ymax, self.bbox.ymax))
        ymin = self.funits_to_points(min(self.font.info.layout.ymin, self.bbox.ymin))
        return xmin, xmax, ymin, ymax

    def place(self, x: float, y: float, point_size: float) -> Optional[ET.Element]:
        ''' Get <use> svg tag translated/scaled to the right position '''
        scale_factor = point_size / self.DFLT_SIZE_PT
        yshift = self.funits_to_points(
            max(self.bbox.ymax, self.font.info.layout.ymax), scale_factor)
        elm: Optional[ET.Element]
        if config.svg2:
            dx = min(self.funits_to_points(self.bbox.xmin, scale_factor), 0)
            elm = ET.Element('use')
            elm.attrib['href'] = f'#{self.id}'
            xmin, xmax, ymin, ymax = self.viewbox
            elm.attrib['href'] = f'#{self.id}'
            elm.attrib['x'] = fmt(x+dx)
            elm.attrib['y'] = fmt(y-yshift)
            elm.attrib['width'] = fmt((xmax-xmin)*scale_factor)
            elm.attrib['height'] = fmt((ymax-ymin)*scale_factor)
        else:
            elm = self.svgpath(x0=x, y0=y, scale_factor=scale_factor)
        return elm

    def advance(self, nextchr: 'SimpleGlyph'|None = None) -> int:
        ''' Get advance width in glyph units  '''
        nextid = nextchr.index if nextchr else None
        return self.font.advance(self.index, nextid)

    def svgpath(self, x0: float = 0, y0: float = 0, scale_factor: float = 1) -> Optional[ET.Element]:
        ''' Get svg <path> element for glyph, normalized to 12-point font '''
        path = ''
        for operator in self.operators:
            segment = operator.path(x0, y0, scale=self.funits_to_points(1, scale_factor))
            if segment[0] == 'M' and path != '':
                path += 'Z '  # Close intermediate segments
            path += segment
        if path == '':
            return None  # Don't return empty path
        path += 'Z '
        return ET.Element('path', attrib={'d': path})

    def svgsymbol(self) -> ET.Element:
        ''' Get svg <symbol> element for this glyph, scaled to 12-point font '''
        xmin, xmax, ymin, ymax = self.viewbox
        sym = ET.Element('symbol')
        sym.attrib['id'] = self.id
        sym.attrib['viewBox'] = f'{fmt(xmin)} {fmt(-ymax)} {fmt(xmax-xmin)} {fmt(ymax-ymin)}'
        if (path := self.svgpath()) is not None:
            sym.append(path)
        return sym

    def svg(self, point_size: Optional[float] = None) -> str:
        ''' Get SVG as string '''
        return ET.tostring(self.svgxml(point_size), encoding='unicode')

    def svgxml(self, point_size: Optional[float] = None) -> ET.Element:
        ''' Standalong SVG '''
        point_size = point_size if point_size else config.fontsize
        scale_factor = point_size / self.DFLT_SIZE_PT

        # Width varies by character, but height is constant for the whole font
        # View should include whole character, even if it goes negative/outside the advwidth
        xmin = self.funits_to_points(min(self.bbox.xmin, 0), scale_factor)
        xmax = self.funits_to_points(self.bbox.xmax, scale_factor)
        ymin = self.funits_to_points(min(self.bbox.ymin, self.font.info.layout.ymin), scale_factor)

        # ymax can go above font's ymax for extended (ie math) glyphs
        ymax = self.funits_to_points(max(self.bbox.ymax, self.font.info.layout.ymax), scale_factor)
        width = xmax - xmin
        height = ymax - ymin
        base = ymax

        svg = ET.Element('svg')
        svg.attrib['width'] = fmt(width)
        svg.attrib['height'] = fmt(height)
        svg.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
        svg.attrib['viewBox'] = f'{fmt(xmin)} 0 {fmt(width)} {fmt(height)}'
        if not config.svg2:
            svg.attrib['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
            elm = self.svgpath(x0=0, y0=base, scale_factor=scale_factor)
            if elm is not None:
                svg.append(elm)
        else:
            symbol = self.svgsymbol()
            svg.append(symbol)
            g = ET.SubElement(svg, 'use')
            g.attrib['href'] = f'#{self.id}'
            g.attrib['width'] = fmt(xmax-xmin)
            g.attrib['height'] = fmt(ymax-ymin)
            g.attrib['x'] = fmt(xmin)
            g.attrib['y'] = fmt(base-ymax)
        return svg

    def test(self, pxwidth: float = 400, pxheight: float = 400) -> InspectGlyph:
        ''' Get Glyph Test representation showing vertices and borders '''
        return InspectGlyph(self, pxwidth, pxheight)

    def describe(self) -> DescribeGlyph:
        ''' Get Glyph Test representation showing vertices and borders '''
        return DescribeGlyph(self)


class CompoundGlyph(SimpleGlyph):
    ''' Compound glyph, made of multiple other Glyphs '''
    def __init__(self, index: int, glyphs: GlyphComp, font: Font):
        self.index = index
        self.glyphs = glyphs
        operators = self._buildcompound()
        super().__init__(index, operators, self.glyphs.bbox, font)

    def _buildcompound(self) -> list[SVGOpType]:
        ''' Combine multiple glyphs into one set of contours '''
        xoperators = []
        for glyph, xform in zip(self.glyphs.glyphs, self.glyphs.xforms):
            if xform.match:
                raise NotImplementedError('Compound glyph match transform')

            m0 = max(abs(xform.a), abs(xform.b))
            n0 = max(abs(xform.c), abs(xform.d))
            m = 2*m0 if abs(abs(xform.a)-abs(xform.c)) <= 33/65536 else m0
            n = 2*n0 if abs(abs(xform.b)-abs(xform.d)) <= 33/65536 else n0
            for operator in glyph.operators:
                xoperators.append(operator.xform(xform.a, xform.b, xform.c,
                                                 xform.d, xform.e, xform.f, m, n))
        return xoperators


class EmptyGlyph(SimpleGlyph):
    ''' Glyph with no contours (like a space) '''
    def __init__(self, index: int, font: Font):
        super().__init__(index, [], BBox(0, 0, 0, 0), font)
