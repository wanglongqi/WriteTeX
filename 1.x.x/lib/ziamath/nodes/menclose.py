''' <menclose> element '''
import xml.etree.ElementTree as ET

from ziafont.fonttypes import BBox

from .. import drawable
from . import Mnode


class Menclose(Mnode, tag='menclose'):
    ''' Enclosure '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        if len(self.element) > 1:
            row = ET.Element('mrow')
            row.extend(list(self.element))
            self.base = Mnode.fromelement(row, parent=self, **kwargs)
        else:
            self.base = Mnode.fromelement(self.element[0], parent=self, **kwargs)

        self.notation = element.get('notation', 'box').split()
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        pad = 2 * self.units_to_points(self.font.math.consts.radicalRuleThickness)
        height = self.base.bbox.ymax - self.base.bbox.ymin + pad * 2
        width = self.base.bbox.xmax - self.base.bbox.xmin + pad * 2
        lw = self.units_to_points(self.font.math.consts.radicalRuleThickness)
        basex = pad
        xarrow = yarrow = 0.

        if 'box' in self.notation:
            self.nodes.append(drawable.Box(width, height, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymax+height-pad))
        if 'circle' in self.notation:
            self.nodes.append(drawable.Ellipse(width, height, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymax+height-pad))
        if 'roundedbox' in self.notation:
            self.nodes.append(drawable.Box(width, height, lw, style=self.style,
                                           cornerradius=lw*4, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymax+height-pad))

        if ('top' in self.notation
                or 'longdiv' in self.notation
                or 'actuarial' in self.notation):
            self.nodes.append(drawable.HLine(width, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymax-pad))
        if ('bottom' in self.notation
                or 'madruwb' in self.notation
                or 'phasorangle' in self.notation):
            self.nodes.append(drawable.HLine(width, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymin+pad))
        if ('right' in self.notation
                or 'madruwb' in self.notation
                or 'actuarial' in self.notation):
            self.nodes.append(drawable.VLine(height, lw, style=self.style, **kwargs))
            self.nodexy.append((self.base.bbox.xmax+pad*2, -self.base.bbox.ymax-pad))
        if ('left' in self.notation
                or 'longdiv' in self.notation):
            self.nodes.append(drawable.VLine(height, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymax-pad))
        if 'verticalstrike' in self.notation:
            self.nodes.append(drawable.VLine(height, lw, style=self.style, **kwargs))
            self.nodexy.append((width/2, -self.base.bbox.ymax-pad))
        if 'horizontalstrike' in self.notation:
            self.nodes.append(drawable.HLine(width, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymin-height/2))

        if 'updiagonalstrike' in self.notation:
            self.nodes.append(drawable.Diagonal(width, -height, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymin-height+pad))
        if 'downdiagonalstrike' in self.notation:
            self.nodes.append(drawable.Diagonal(width, height, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymin+pad))
        if 'phasorangle' in self.notation:
            self.nodes.append(drawable.Diagonal(height/3, -height, lw, style=self.style, **kwargs))
            self.nodexy.append((0, -self.base.bbox.ymin-height+pad))
            basex += height/4  # Shift base right a bit so it fits under angle

        if 'updiagonalarrow' in self.notation:
            diag = drawable.Diagonal(width, -height, lw, style=self.style, arrow=True, **kwargs)
            self.nodes.append(diag)
            self.nodexy.append((0, -self.base.bbox.ymin-height+pad))
            xarrow = diag.arroww
            yarrow = diag.arrowh

        self.nodes.append(self.base)
        self.nodexy.append((basex, 0))

        self.bbox = BBox(0, basex+width+xarrow, self.base.bbox.ymin-pad, height-pad+yarrow)
