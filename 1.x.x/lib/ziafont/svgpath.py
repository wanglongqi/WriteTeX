''' SVG path elements '''

from __future__ import annotations
from typing import Union
from .config import config


def fmt(f: float) -> str:
    ''' String formatter, stripping trailing zeros '''
    p = f'.{config.precision}f'
    s = format(float(f), p)
    return s.rstrip('0').rstrip('.')  # Strip trailing zeros


class Point:
    ''' (X, Y) Point class '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f'Point({self.x}, {self.y})'

    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

    def __truediv__(self, i):
        return Point(self.x / i, self.y / i)

    def xform(self, a: float, b: float, c: float, d: float,
              e: float, f: float, m: float, n: float) -> Point:
        ''' Apply Transform (for compound glyph) '''
        x = m * (a/m * self.x + c/m * self.y + e)
        y = n * (b/n * self.x + d/n * self.y + f)
        return Point(x, y)


class Moveto:
    ''' SVG Move To '''
    def __init__(self, p: Point):
        self.p = p

    def __repr__(self):
        return f'Moveto({self.p.x}, {self.p.y})'

    def path(self, x0: float = 0, y0: float = 0, scale: float = 1) -> str:
        ''' Get SVG path '''
        return f'M {fmt(x0 + self.p.x * scale)} {fmt(y0 - self.p.y * scale)} '

    def xform(self, a: float, b: float, c: float, d: float,
              e: float, f: float, m: float, n: float) -> Moveto:
        ''' Transform the SVG path '''
        return Moveto(self.p.xform(a, b, c, d, e, f, m, n))

    def ymin(self) -> float:
        ''' Minimum Y value '''
        return self.p.y

    def ymax(self) -> float:
        ''' Maximum Y value '''
        return self.p.y

    def xmin(self) -> float:
        ''' Minimum X value '''
        return self.p.x

    def xmax(self) -> float:
        ''' Maximum X value '''
        return self.p.x

    def points(self) -> tuple[list[Point], list[bool]]:
        ''' Get control points '''
        return [self.p], [False]  # [points], [control?]


class Lineto:
    ''' SVG Line To '''
    def __init__(self, p: Point):
        self.p = p

    def __repr__(self):
        return f'Lineto({self.p.x}, {self.p.y})'

    def path(self, x0: float = 0, y0: float = 0, scale: float = 1) -> str:
        ''' Get SVG path '''
        return f'L {fmt(x0 + self.p.x * scale)} {fmt(y0 - self.p.y * scale)} '

    def xform(self, a: float, b: float, c: float, d: float,
              e: float, f: float, m: float, n: float) -> Lineto:
        ''' Transform the SVG path '''
        return Lineto(self.p.xform(a, b, c, d, e, f, m, n))

    def ymin(self) -> float:
        ''' Minimum Y value '''
        return self.p.y

    def ymax(self) -> float:
        ''' Maximum Y value '''
        return self.p.y

    def xmin(self) -> float:
        ''' Minimum X value '''
        return self.p.x

    def xmax(self) -> float:
        ''' Maximum X value '''
        return self.p.x

    def points(self) -> tuple[list[Point], list[bool]]:
        ''' Get control points '''
        return [self.p], [False]  # [points], [control?]


class Quad:
    ''' SVG Quadratic Bezier.
        First point of Bezier should already be set in path.
        p1 is control points, p2 is endpoint.
    '''
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def __repr__(self):
        return f'Quad({self.p1.x}, {self.p1.y}; {self.p2.x} {self.p2.y})'

    def path(self, x0: float = 0, y0: float = 0, scale: float = 1) -> str:
        ''' Get SVG path '''
        return (f'Q {fmt(x0 + self.p1.x * scale)} {fmt(y0-self.p1.y * scale)} '
                f'{fmt(x0+self.p2.x * scale)} {fmt(y0-self.p2.y * scale)} ')

    def xform(self, a: float, b: float, c: float, d: float,
              e: float, f: float, m: float, n: float) -> Quad:
        ''' Transform the SVG path '''
        return Quad(self.p1.xform(a, b, c, d, e, f, m, n),
                    self.p2.xform(a, b, c, d, e, f, m, n))

    def ymin(self) -> float:
        ''' Minimum Y value '''
        return min(self.p1.y, self.p2.y)

    def ymax(self) -> float:
        ''' Maximum Y value '''
        return max(self.p1.y, self.p2.y)

    def xmin(self) -> float:
        ''' Minimum X value '''
        return min(self.p1.x, self.p2.x)

    def xmax(self) -> float:
        ''' Maximum X value '''
        return max(self.p1.x, self.p2.x)

    def points(self) -> tuple[list[Point], list[bool]]:
        ''' Get control points '''
        return [self.p1, self.p2], [True, False]  # [points], [control?]


class Cubic:
    ''' SVG Cubic Bezier.
        First point of Bezier should already be set in path.
        p1, p2 are control points, p3 is endpoint.
    '''
    def __init__(self, p1: Point, p2: Point, p3: Point):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def __repr__(self):
        return f'Cubic({self.p1.x}, {self.p1.y}; {self.p2.x}, {self.p2.y}; {self.p3.x} {self.p3.y})'

    def path(self, x0: float = 0, y0: float = 0, scale: float = 1) -> str:
        ''' Get SVG path '''
        return (f'C {fmt(x0+self.p1.x * scale)} {fmt(y0-self.p1.y * scale)} '
                f'{fmt(x0+self.p2.x * scale)} {fmt(y0-self.p2.y * scale)} '
                f'{fmt(x0+self.p3.x * scale)} {fmt(y0-self.p3.y * scale)} ')

    def xform(self, a: float, b: float, c: float, d: float,
              e: float, f: float, m: float, n: float) -> Cubic:
        ''' Transform the SVG path '''
        return Cubic(self.p1.xform(a, b, c, d, e, f, m, n),
                     self.p2.xform(a, b, c, d, e, f, m, n),
                     self.p3.xform(a, b, c, d, e, f, m, n))

    def ymin(self) -> float:
        ''' Minimum Y value '''
        return min(self.p1.y, self.p2.y, self.p3.y)

    def ymax(self) -> float:
        ''' Maximum Y value '''
        return max(self.p1.y, self.p2.y, self.p3.y)

    def xmin(self) -> float:
        ''' Minimum X value '''
        return min(self.p1.x, self.p2.x, self.p3.x)

    def xmax(self) -> float:
        ''' Maximum X value '''
        return max(self.p1.x, self.p2.x, self.p3.x)

    def points(self) -> tuple[list[Point], list[bool]]:
        ''' Get control points '''
        return [self.p1, self.p2, self.p3], [True, True, False]  # [points], [control?]


SVGOpType = Union[Moveto, Lineto, Quad, Cubic]
