''' <mspace>, <mpadded>, <mphantom> Math Elements '''
from xml.etree import ElementTree as ET

from ziafont.fonttypes import BBox

from .mnode import Mnode
from .mrow import Mrow


class Mspace(Mnode, tag='mspace'):
    ''' Blank space '''
    def __init__(self, element: ET.Element, parent: 'Mnode', **kwargs):
        super().__init__(element, parent, **kwargs)
        self.width = self.size_px(element.get('width', '0'))
        self.height = self.size_px(element.get('height', '0'))
        self.depth = self.size_px(element.get('depth', '0'))
        self._setup(**kwargs)

    def _setup(self, **kwargs) -> None:
        self.bbox = BBox(0, self.width, -self.depth, self.height)


class Mpadded(Mrow, tag='mpadded'):
    ''' Mpadded element - Mrow with extra whitespace '''
    def _setup(self, **kwargs):
        super()._setup(**kwargs)
        width = self.element.get('width', None)
        lspace = self.element.get('lspace', 0)
        height = self.element.get('height', None)
        depth = self.element.get('depth', None)
        voffset = self.element.get('voffset', 0)
        xmin, xmax, ymin, ymax = self.bbox

        def adjust(valstr: str, param: float) -> float:
            if valstr.startswith('+') or valstr.startswith('-'):
                # +X or -X means increment or decrement
                sign = valstr[0]
                if sign == '+':
                    param += self.size_px(valstr[1:])
                else:
                    param -= self.size_px(valstr[1:])
            elif valstr.endswith('%'):
                param *= float(valstr[:-1])/100
            else:
                param = self.size_px(valstr)
            return param

        if lspace:
            xshift = adjust(lspace, 0)
            for i, (x, y) in enumerate(self.nodexy):
                self.nodexy[i] = (x + xshift, y)
        if voffset:
            yshift = adjust(voffset, 0)
            for i, (x, y) in enumerate(self.nodexy):
                self.nodexy[i] = (x, y-yshift)
        if width:
            xmax = xmin + adjust(width, xmax-xmin)
        if height:
            ymax = adjust(height, ymax)
        if depth:
            ymin = -adjust(depth, ymin)
        self.bbox = BBox(xmin, xmax, ymin, ymax)
        self._xadvance = xmax


class Mphantom(Mrow, tag='mphantom'):
    ''' Phantom element. Takes up space but not drawn. '''
    def _setup(self, **kwargs) -> None:
        kwargs['phantom'] = True
        super()._setup(**kwargs)
