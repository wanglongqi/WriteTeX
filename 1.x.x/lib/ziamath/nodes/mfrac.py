''' <mfrac> math element '''
from xml.etree import ElementTree as ET

from ziafont.fonttypes import BBox

from ..styles import parse_style
from ..config import config
from ..drawable import HLine
from . import Mnode


class Mfrac(Mnode, tag='mfrac'):
    ''' Fraction node '''
    # TODO: bevelled attribute for x/y fractions with slanty bar
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        pre_style = parse_style(element, parent.style)

        # check original mml attribute for displaystyle to see if
        # it was explicitly turned on (eg dfrac) and not inherited
        if (element.attrib.get('displaystyle') != 'true'
            and ('sup' in kwargs
                 or 'sub' in kwargs
                 or 'frac' in kwargs
                 or not pre_style.displaystyle)):
            element.set('scriptlevel', str(pre_style.scriptlevel + 1))

        # super() after determining scriptlevel so that scale factors are calculated
        super().__init__(element, parent, **kwargs)
        assert len(self.element) == 2
        kwargs['frac'] = True
        kwargs.pop('sup', None)
        self.numerator = Mnode.fromelement(self.element[0], parent=self, **kwargs)
        self.denominator = Mnode.fromelement(self.element[1], parent=self, **kwargs)
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        # Keep fraction bar same thickness as minus sign
        fbar_glyphsize = max(
            self.size*(self.font.math.consts.scriptPercentScaleDown/100)**max(0, self.style.scriptlevel-1),
            self.font.basesize*config.minsizefraction)
        fracbar_pts_per_unit = fbar_glyphsize/self.font.info.layout.unitsperem
        linethick = fracbar_pts_per_unit * self.font.math.consts.fractionRuleThickness
        if 'linethickness' in self.element.attrib:
            # User parameter overrides thickness
            lt = self.element.get('linethickness', '')
            try:
                linethick = self.size_px(lt)
            except ValueError:
                linethick = {'thin': linethick * .5,
                             'thick': linethick * 2}.get(lt, linethick)

        if self.style.displaystyle:
            ynum = self.units_to_points(
                -self.font.math.consts.fractionNumeratorDisplayStyleShiftUp)
            ydenom = self.units_to_points(
                self.font.math.consts.fractionDenominatorDisplayStyleShiftDown)
            numgap = self.units_to_points(
                self.font.math.consts.fractionNumDisplayStyleGapMin)
            denomgap = self.units_to_points(
                self.font.math.consts.fractionDenomDisplayStyleGapMin)
        else:
            ynum = self.units_to_points(
                -self.font.math.consts.fractionNumeratorShiftUp)
            ydenom = self.units_to_points(
                self.font.math.consts.fractionDenominatorShiftDown)
            numgap = self.units_to_points(
                self.font.math.consts.fractionNumeratorGapMin)
            denomgap = self.units_to_points(
                self.font.math.consts.fractionDenominatorGapMin)

        denombox = self.denominator.bbox
        numbox = self.numerator.bbox
        if self.parent.mtag == 'mrow':
            # Make sure axisheight aligns across mrow even with different font sizes
            axheight = self.parent.units_to_points(self.font.math.consts.axisHeight)
        else:
            axheight = self.units_to_points(self.font.math.consts.axisHeight)

        ynum = min(ynum, -(axheight + numgap - numbox.ymin + linethick/2))
        ydenom = max(ydenom, (-axheight + denomgap + denombox.ymax + linethick/2))

        x = 0.
        if (leftsibling := self.leftsibling()):
            if leftsibling.mtag == 'mfrac':
                x = self.size_px('verythinmathspace')
            else:
                x = self.size_px('thinmathspace')

        width = max(numbox.xmax, denombox.xmax)
        xnum = x + (width - (numbox.xmax - numbox.xmin))/2
        xdenom = x + (width - (denombox.xmax - denombox.xmin))/2
        self.nodes.append(self.numerator)
        self.nodes.append(self.denominator)
        self.nodexy.append((xnum, ynum))
        self.nodexy.append((xdenom, ydenom))

        bary = -axheight - linethick/2
        self.nodes.append(HLine(width, linethick, style=self.style, **kwargs))
        self.nodexy.append((x, bary))

        # Calculate/cache bounding box
        xmin = 0
        xmax = x + max(numbox.xmax, denombox.xmax)
        xmax += self.size_px('thinmathspace')
        ymin = (-ydenom) + denombox.ymin
        ymax = (-ynum) + numbox.ymax
        self.bbox = BBox(xmin, xmax, ymin, ymax)
