''' Main math rendering class '''

from __future__ import annotations
from typing import Union, Literal, Tuple, Optional, Dict
from contextlib import contextmanager
import warnings
import re
from collections import ChainMap
from math import inf, cos, sin, radians
from itertools import zip_longest
import importlib.resources as pkg_resources
import xml.etree.ElementTree as ET

import ziafont as zf
from ziafont.glyph import fmt
from .mathfont import MathFont
from .nodes import Mnode
from .styles import parse_style
from .escapes import unescape
from .config import config
from .tex import tex2mml


Halign = Literal['left', 'center', 'right']
Valign = Literal['top', 'center', 'base', 'axis', 'bottom']


def denamespace(element: ET.Element) -> ET.Element:
    ''' Recursively remove namespace {...} from beginning of xml
        element names, so they can be searched easily.
    '''
    if element.tag.startswith('{'):
        element.tag = element.tag.split('}')[1]
    for elm in element:
        denamespace(elm)
    return element


def apply_mstyle(element: ET.Element) -> ET.Element:
    ''' Take attributes defined in <mstyle> elements and add them
        to all the child elements, removing the original <mstyle>
    '''
    def flatten_attrib(element: ET.Element) -> None:
        for child in element:
            if element.tag == 'mstyle':
                child.attrib = dict(ChainMap(child.attrib, element.attrib))
            flatten_attrib(child)

    flatten_attrib(element)

    elmstr = ET.tostring(element).decode('utf-8')
    elmstr = re.sub(r'<mstyle.+?>', '', elmstr)
    elmstr = re.sub(r'</mstyle>', '', elmstr)
    return ET.fromstring(elmstr)


class EqNumbering:
    ''' Manage automatic equation numbers '''
    count: int = 1
    enable: bool = True

    @classmethod
    def number(cls) -> Optional[int]:
        ''' Get next number in the sequence '''
        if EqNumbering.enable:
            number = EqNumbering.count
            EqNumbering.count += 1
            return number
        return None

    @classmethod
    @contextmanager
    def pause(cls):
        ''' Context manager to pause equation numbering '''
        EqNumbering.enable = False
        yield
        EqNumbering.enable = True

    @classmethod
    def reset(cls, number: int = 1) -> None:
        ''' Reset the current number '''
        EqNumbering.count = number

    @classmethod
    def text(cls, number = None) -> Optional[str]:
        ''' Get text to use as equation label '''
        if EqNumbering.enable:
            if number is None:
                number = EqNumbering.number()
            return config.numbering.getlabel(number)
        return None


def reset_numbering(number: int = 1):
    ''' Reset equation numbering '''
    EqNumbering.reset(number)



class Math:
    ''' MathML Element Renderer

        Args:
            mathml: MathML expression, in string or XML Element
            size: Base font size, pixels
            font: Filename of font file. Must contain MATH typesetting table.
            title: Text for title alt-text tag in the SVG
    '''
    def __init__(self,
                 mathml: Union[str, ET.Element],
                 size: Optional[float] = None,
                 font: Optional[str] = None,
                 title: Optional[str] = None,
                 number: Optional[str] = None):
        self.size = size if size else config.math.fontsize
        font = font if font else config.math.mathfont
        self.title = title

        if number is None and config.numbering.autonumber:
            self.eqnumber = EqNumbering.text()
        else:
            self.eqnumber = number

        self.font: MathFont
        if font is None:
            self.font = loadedfonts['default']
        elif font in loadedfonts:
            self.font = loadedfonts[font]
        else:
            self.font = MathFont(font, self.size)
            loadedfonts[font] = self.font

        def register_altfont(path):
            if path in loadedfonts:
                font = loadedfonts[path]
            else:
                # Lazy-load the alt fonts
                font = zf.Font(path)
                loadedfonts[path] = font
            return font

        if config.math.bold_font:
            self.font.alt_fonts.bold = register_altfont(config.math.bold_font)
        if config.math.italic_font:
            self.font.alt_fonts.italic = register_altfont(config.math.italic_font)
        if config.math.bolditalic_font:
            self.font.alt_fonts.bolditalic = register_altfont(config.math.bolditalic_font)

        if isinstance(mathml, str):
            mathml = unescape(mathml)
            mathml = ET.fromstring(mathml)
        mathml = denamespace(mathml)
        mathml = apply_mstyle(mathml)

        self.mathml = mathml
        self.style = parse_style(mathml)
        self.element = mathml
        self.mtag = 'math'
        self.node = Mnode.fromelement(mathml, parent=self)  # type: ignore

    @classmethod
    def fromlatex(cls, latex: str, size: Optional[float] = None, mathstyle: Optional[str] = None,
                  font: Optional[str] = None, color: Optional[str] = None, inline: bool = False):
        ''' Create Math Renderer from a single LaTeX expression. Requires
            latex2mathml Python package.

            Args:
                latex: Latex string
                size: Base font size
                mathstyle: Style parameter for math, equivalent to "mathvariant" MathML attribute
                font: Font file name
                color: Color parameter, equivalent to "mathcolor" attribute
                inline: Use inline math mode (default is block mode)
        '''
        mathml: Union[str, ET.Element]
        mathml = tex2mml(latex, inline=inline)
        if mathstyle:
            mathml = ET.fromstring(mathml)
            mathml.attrib['mathvariant'] = mathstyle
            mathml = ET.tostring(mathml, encoding='unicode')
        if color:
            mathml = ET.fromstring(mathml)
            mathml.attrib['mathcolor'] = color
        return cls(mathml, size, font)

    @classmethod
    def fromlatextext(cls, latex: str, size: float = 24, mathstyle: Optional[str] = None,
                      textstyle: Optional[str] = None, font: Optional[str] = None,
                      color: Optional[str] = None):
        ''' Create Math Renderer from a sentence containing zero or more LaTeX
            expressions delimited by $..$, resulting in single MathML element.
            Requires latex2mathml Python package.

            Args:
                latex: string
                size: Base font size
                mathstyle: Style parameter for math, equivalent to "mathvariant" MathML attribute
                textstyle: Style parameter for text, equivalent to "mathvariant" MathML attribute
                font: Font file name
                color: Color parameter, equivalent to "mathcolor" attribute
        '''
        warnings.warn(r'fromlatextext is deprecated. Use ziamath.Text or \text{} command.', DeprecationWarning, stacklevel=2)

        # Extract each $..$, convert to MathML, but the raw text in <mtext>, and join
        # into a single <math>
        parts = re.split(r'(\$+.*?\$+)', latex)
        texts = parts[::2]
        maths = [tex2mml(p.replace('$', ''), inline=not p.startswith('$$')) for p in parts[1::2]]
        mathels = [ET.fromstring(m) for m in maths]   # Convert to xml, but drop opening <math>

        mml = ET.Element('math')
        for text, mathel in zip_longest(texts, mathels):
            if text:
                mtext = ET.SubElement(mml, 'mtext')
                if textstyle:
                    mtext.attrib['mathvariant'] = textstyle
                mtext.text = text
            if mathel is not None:
                child = mathel[0]
                if mathstyle:
                    child.attrib['mathvariant'] = mathstyle
                if (dstyle := mathel.attrib.get('display')):
                    child.attrib['displaystyle'] = {'inline': 'false',
                                                    'block': 'true'}.get(dstyle, 'true')
                mml.append(child)
        if color:
            mml.attrib['mathcolor'] = color
        return cls(mml, size, font)

    def svgxml(self) -> ET.Element:
        ''' Get standalone SVG of expression as XML Element Tree '''
        svg = ET.Element('svg')
        svg.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
        if not config.svg2:
            svg.attrib['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'

        if isinstance(self.title, str):
            title = ET.SubElement(svg, 'title')
            title.text = self.title

        bbox = self.node.bbox
        width = bbox.xmax - bbox.xmin + 2  # Add a 1-px border
        height = bbox.ymax - bbox.ymin + 2

        if self.eqnumber is not None:
            colwidth = self.node.size_px(config.numbering.columnwidth, self.size)
            x = (colwidth - width) / 2
            width = colwidth

            with EqNumbering.pause():
                eqnode = Latex(self.eqnumber, size=self.size)
            eqnode.drawon(svg, width, 0, halign='right')
            y0 = min(-bbox.ymax-1, -eqnode.node.bbox.ymax-1)
            y1 = max(-bbox.ymin, -eqnode.node.bbox.ymin)
            height = max(height, y1-y0)
            viewbox = f'0 {fmt(y0)} {fmt(width)} {fmt(height)}'
        else:
            x = 1
            viewbox = f'{fmt(bbox.xmin-1)} {fmt(-bbox.ymax-1)} {fmt(width)} {fmt(height)}'

        self.node.draw(x, 0, svg)

        svg.attrib['width'] = fmt(width)
        svg.attrib['height'] = fmt(height)
        svg.attrib['viewBox'] = viewbox

        if self.eqnumber is not None and config.debug.bbox:
            rect = ET.SubElement(svg, 'rect')
            rect.attrib['x'] = '0'
            rect.attrib['y'] = fmt(y0)
            rect.attrib['width'] = fmt(width)
            rect.attrib['height'] = fmt(height)
            rect.attrib['fill'] = 'yellow'
            rect.attrib['opacity'] = '.2'
            rect.attrib['stroke'] = 'red'

        return svg

    def drawon(self, svg: ET.Element, x: float = 0, y: float = 0,
               halign: Halign = 'left', valign: Valign = 'base') -> ET.Element:
        ''' Draw the math expression on an existing SVG

            Args:
                x: Horizontal position in SVG coordinates
                y: Vertical position in SVG coordinates
                svg: The image (top-level svg XML object) to draw on
                halign: Horizontal alignment
                valign: Vertical alignment

            Note: Horizontal alignment can be the typical 'left', 'center', or 'right'.
            Vertical alignment can be 'top', 'bottom', or 'center' to align with the
            expression's bounding box, or 'base' to align with the bottom
            of the first text element, or 'axis', aligning with the height of a minus
            sign above the baseline.
        '''
        width, height = self.getsize()
        yshift = {'top': self.node.bbox.ymax,
                  'center': height/2 + self.node.bbox.ymin,
                  'axis': self.node.units_to_points(self.font.math.consts.axisHeight),
                  'bottom': self.node.bbox.ymin}.get(valign, 0)
        xshift = {'center': -width/2,
                  'right': -width}.get(halign, 0)

        svgelm = ET.SubElement(svg, 'g')  # Put it in a group
        self.node.draw(x+xshift, y+yshift, svgelm)
        return svgelm

    def svg(self) -> str:
        ''' Get expression as SVG string '''
        return ET.tostring(self.svgxml(), encoding='unicode')

    def save(self, fname):
        ''' Save expression to SVG file '''
        with open(fname, 'w') as f:
            f.write(self.svg())

    def _repr_svg_(self):
        ''' Jupyter SVG representation '''
        return self.svg()

    def mathmlstr(self) -> str:
        ''' Get MathML as string '''
        return ET.tostring(self.mathml).decode('utf-8')

    @classmethod
    def mathml2svg(cls, mathml: Union[str, ET.Element],
                   size: Optional[float] = None, font: Optional[str] = None):
        ''' Shortcut to just return SVG string directly '''
        return cls(mathml, size=size, font=font).svg()

    def getsize(self) -> tuple[float, float]:
        ''' Get size of rendered text '''
        return (self.node.bbox.xmax - self.node.bbox.xmin,
                self.node.bbox.ymax - self.node.bbox.ymin)

    def getyofst(self) -> float:
        ''' Y-shift from bottom of bbox to 0 '''
        return self.node.bbox.ymin


class Latex(Math):
    ''' Render Math from LaTeX

        Args:
            latex: Latex string
            size: Base font size
            mathstyle: Style parameter for math, equivalent to "mathvariant" MathML attribute
            font: Font file name
            color: Color parameter, equivalent to "mathcolor" attribute
            inline: Use inline math mode (default is block mode)
            title: Text for title alt-text tag in the SVG
        '''
    def __init__(self, latex: str, size: Optional[float] = None, mathstyle: Optional[str] = None,
                 font: Optional[str] = None, color: Optional[str] = None, inline: bool = False,
                 title: Optional[str] = None,
                 number: Optional[str] = None):
        self.latex = latex

        if number is not None:
            number = EqNumbering.text(number)
        elif (tags := re.findall(r'\\tag\{(.*)\}', self.latex)):
            if len(tags) > 1:
                raise ValueError(r'Multiple \tag')
            number = EqNumbering.text(tags[0])
            self.latex = re.sub(r'\\tag\{(.*)\}', '', self.latex)

        mathml: Union[str, ET.Element]
        mathml = tex2mml(self.latex, inline=inline)
        if mathstyle:
            mathml = ET.fromstring(mathml)
            mathml.attrib['mathvariant'] = mathstyle
            mathml = ET.tostring(mathml, encoding='unicode')
        if color:
            mathml = ET.fromstring(mathml)
            mathml.attrib['mathcolor'] = color
        super().__init__(mathml, size, font, title=title, number=number)


class Text:
    ''' Mixed text and latex math. Inline math delimited by single $..$, and
        display-mode math delimited by double $$...$$. Can contain multiple
        lines. Drawn to SVG.

        Args:
            s: string to write
            textfont: font filename or family name for text
            mathfont: font filename for math
            mathstyle: Style parameter for math
            size: font size in points
            linespacing: spacing between lines
            color: color of text
            halign: horizontal alignment
            valign: vertical alignment
            rotation: Rotation angle in degrees
            rotation_mode: Either 'default' or 'anchor', to
                mimic Matplotlib behavoir. See:
                https://matplotlib.org/stable/gallery/text_labels_and_annotations/demo_text_rotation_mode.html
            title: Text for title alt-text tag in the SVG
    '''
    def __init__(self, s, textfont: Optional[str] = None, mathfont: Optional[str] = None,
                 mathstyle: Optional[str] = None, size: Optional[float] = None, linespacing: Optional[float] = None,
                 color: Optional[str] = None,
                 halign: str = 'left', valign: str = 'base',
                 rotation: float = 0, rotation_mode: str = 'anchor',
                 title: Optional[str] = None):
        self.str = s
        self.mathfont = mathfont
        self.mathstyle = mathstyle
        self.size = size if size else config.text.fontsize
        self.linespacing = linespacing if linespacing else config.text.linespacing
        self.color = color
        self.textcolor = color if color else config.text.color
        self._halign = halign
        self._valign = valign
        self.rotation = rotation
        self.rotation_mode = rotation_mode
        self.textfont: Optional[Union[MathFont, zf.Font]]
        self.title = title

        # textfont can be a path to font, or style type like "serif".
        # If style type, use Stix font variation
        textfont = textfont if textfont else config.text.textfont
        textstyle = config.text.variant
        if loadedtextfonts.get(textfont) == 'notfound':  # type: ignore
            self.textfont = None
            self.textstyle = textfont
        elif textfont is None:
            self.textfont = None
            self.textstyle = textstyle
        elif textfont in loadedtextfonts:
            self.textfont = loadedtextfonts[textfont]
        else:
            try:
                self.textfont = zf.Font(textfont)
                self.textstyle = textstyle
                loadedtextfonts[str(textfont)] = self.textfont
            except FileNotFoundError:
                # Mark as not found to not search again
                loadedtextfonts[textfont] = 'notfound'  # type: ignore
                self.textfont = None
                self.textstyle = textfont

    def svg(self) -> str:
        ''' Get expression as SVG string '''
        return ET.tostring(self.svgxml(), encoding='unicode')

    def _repr_svg_(self):
        ''' Jupyter SVG representation '''
        return self.svg()

    def svgxml(self) -> ET.Element:
        ''' Get standalone SVG of expression as XML Element Tree '''
        svg = ET.Element('svg')
        if self.title is not None:
            title = ET.SubElement(svg, 'title')
            title.text = self.title
        _, (x1, x2, y1, y2) = self._drawon(svg)
        svg.attrib['width'] = fmt(x2-x1)
        svg.attrib['height'] = fmt(y2-y1)
        svg.attrib['xmlns'] = 'http://www.w3.org/2000/svg'
        if not config.svg2:
            svg.attrib['xmlns:xlink'] = 'http://www.w3.org/1999/xlink'
        svg.attrib['viewBox'] = f'{fmt(x1)} {fmt(y1)} {fmt(x2-x1)} {fmt(y2-y1)}'
        return svg

    def save(self, fname):
        ''' Save expression to SVG file '''
        with open(fname, 'w') as f:
            f.write(self.svg())

    def drawon(self, svg: ET.Element, x: float = 0, y: float = 0,
               halign: Optional[str] = None, valign: Optional[str] = None) -> ET.Element:
        ''' Draw text on existing SVG element

            Args:
                svg: Element to draw on
                x: x-position
                y: y-position
                halign: Horizontal alignment
                valign: Vertical alignment
        '''
        svgelm, _ = self._drawon(svg, x, y, halign, valign)
        return svgelm

    def _drawon(self, svg: ET.Element, x: float = 0, y: float = 0,
                halign: Optional[str] = None, valign: Optional[str] = None) -> Tuple[ET.Element, Tuple[float, float, float, float]]:
        ''' Draw text on existing SVG element

            Args:
                svg: Element to draw on
                x: x-position
                y: y-position
                halign: Horizontal alignment
                valign: Vertical alignment
        '''
        halign = self._halign if halign is None else halign
        valign = self._valign if valign is None else valign

        lines = self.str.splitlines()
        svglines = []
        svgelm = ET.SubElement(svg, 'g')

        # Split into lines and "parts"
        linesizes = []
        for line in lines:
            svgparts = []
            parts = re.split(r'(\$+.*?\$+)', line)
            partsizes = []
            for part in parts:
                if not part:
                    continue
                if part.startswith('$$') and part.endswith('$$'):  # Display-mode math
                    math = Math.fromlatex(part.replace('$', ''),
                                          font=self.mathfont,
                                          mathstyle=self.mathstyle,
                                          inline=False,
                                          size=self.size, color=self.color)
                    svgparts.append(math)
                    partsizes.append(math.getsize())

                elif part.startswith('$') and part.endswith('$'):  # Text-mode Math
                    math = Math.fromlatex(part.replace('$', ''),
                                          font=self.mathfont,
                                          mathstyle=self.mathstyle,
                                          inline=True,
                                          size=self.size, color=self.color)
                    svgparts.append(math)
                    partsizes.append(math.getsize())
                else:  # Text
                    part = part.replace('<', '&lt;').replace('>', '&gt;')
                    if self.textfont:
                        # A specific font file is defined, use ziafont and ignore textstyle
                        txt = zf.Text(part, font=self.textfont, size=self.size, color=self.textcolor)
                        partsizes.append(txt.getsize())
                        svgparts.append(txt)
                    else:
                        # use math font with textstyle
                        txt = Math.fromlatex(f'\\text{{{part}}}',
                                             font=self.mathfont,
                                             mathstyle=self.textstyle,
                                             size=self.size,
                                             color=self.textcolor)
                        partsizes.append(txt.getsize())
                    svgparts.append(txt)

            if len(svgparts) > 0:
                svglines.append(svgparts)
                linesizes.append(partsizes)

        lineofsts = [min([p.getyofst() for p in line]) for line in svglines]
        lineheights = [max(p[1] for p in line) for line in linesizes]
        linewidths = [sum(p[0] for p in line) for line in linesizes]

        if valign == 'bottom':
            ystart = y - (len(lines)-1)*self.size*self.linespacing + lineofsts[-1]
        elif valign == 'top':
            ystart = y + lineheights[0] + lineofsts[0]
        elif valign == 'center':
            ystart = y + (lineheights[0] + lineofsts[0] - (len(lines)-1)*self.size*self.linespacing + lineofsts[-1])/2
        else:  # 'base'
            ystart = y

        xmin = ymin = inf
        xmax = ymax = -inf
        yloc = ystart
        for i, line in enumerate(svglines):
            xloc = x
            xloc += {'left': 0,
                     'right': -linewidths[i],
                     'center': -linewidths[i]/2}.get(halign, 0)

            xmin = min(xmin, xloc)
            xmax = max(xmax, xloc+linewidths[i])

            for part, size in zip(line, linesizes[i]):
                part.drawon(svgelm, xloc, yloc)
                xloc += size[0]
            yloc += self.size * self.linespacing

        ymin = y - lineheights[0] - lineofsts[0]
        ymax = yloc - self.size*self.linespacing - lineofsts[-1]
        if self.rotation:
            costh = cos(radians(self.rotation))
            sinth = sin(radians(self.rotation))
            p1 = (xmin-x, ymin-y)  # Corners relative to rotation point
            p2 = (xmax-x, ymin-y)
            p3 = (xmax-x, ymax-y)
            p4 = (xmin-x, ymax-y)
            x1 = x + (p1[0]*costh + p1[1]*sinth)
            x2 = x + (p2[0]*costh + p2[1]*sinth)
            x3 = x + (p3[0]*costh + p3[1]*sinth)
            x4 = x + (p4[0]*costh + p4[1]*sinth)
            y1 = y - (p1[0]*sinth - p1[1]*costh)
            y2 = y - (p2[0]*sinth - p2[1]*costh)
            y3 = y - (p3[0]*sinth - p3[1]*costh)
            y4 = y - (p4[0]*sinth - p4[1]*costh)
            bbox = (min(x1, x2, x3, x4), max(x1, x2, x3, x4),
                    min(y1, y2, y3, y4), max(y1, y2, y3, y4))

            xform = ''
            if self.rotation_mode == 'default':
                dx = {'left': x - bbox[0],
                      'right': x - bbox[1],
                      'center': x - (bbox[1]+bbox[0])/2}.get(halign, 0)
                dy = {'top': y - bbox[2],
                      'bottom': y - bbox[3],
                      'base': -sinth*dx,
                      'center': y - (bbox[3]+bbox[2])/2}.get(valign, 0)
                xform = f'translate({dx} {dy})'
                bbox = (bbox[0]+dx, bbox[1]+dx,
                        bbox[2]+dy, bbox[3]+dy)

            xform += f' rotate({-self.rotation} {x} {y})'
            if config.debug.bbox:
                rect = ET.SubElement(svg, 'rect')
                rect.attrib['x'] = fmt(bbox[0])
                rect.attrib['y'] = fmt(bbox[2])
                rect.attrib['width'] = fmt(bbox[1]-bbox[0])
                rect.attrib['height'] = fmt(bbox[3]-bbox[2])
                rect.attrib['fill'] = 'none'
                rect.attrib['stroke'] = 'red'

            svgelm.set('transform', xform)
            xmin, xmax, ymin, ymax = bbox

        return svgelm, (xmin, xmax, ymin, ymax)

    def getsize(self) -> tuple[float, float]:
        ''' Get pixel width and height of Text. '''
        svg = ET.Element('svg')
        _, (xmin, xmax, ymin, ymax) = self._drawon(svg)
        return (xmax-xmin, ymax-ymin)

    def bbox(self) -> tuple[float, float, float, float]:
        ''' Get bounding box (xmin, xmax, ymin, ymax) of Text. '''
        svg = ET.Element('svg')
        _, (xmin, xmax, ymin, ymax) = self._drawon(svg)
        return (xmin, xmax, ymin, ymax)

    def getyofst(self) -> float:
        ''' Y offset from baseline to bottom of bounding box '''
        return -self.bbox()[3]


# Cache the loaded fonts to prevent reloading all the time
with pkg_resources.path('ziamath.fonts', 'STIXTwoMath-Regular.ttf') as p:
    fontname = p
loadedfonts: Dict[str, MathFont] = {'default': MathFont(fontname)}
loadedtextfonts: Dict[str, zf.Font] = {}
