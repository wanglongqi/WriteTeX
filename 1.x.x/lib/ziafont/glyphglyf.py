''' Glyph classes '''

from __future__ import annotations
from typing import Union, Optional, TYPE_CHECKING

from .glyph import SimpleGlyph, CompoundGlyph, EmptyGlyph
from .fonttypes import GlyphComp, BBox, Xform
from .svgpath import Moveto, Lineto, Quad, Point, SVGOpType

if TYPE_CHECKING:
    from .font import Font


def glyphoffset(font, index: int) -> Optional[int]:
    ''' Get offset (from beginning of file) of glyph,
        Return None if no glyph (empty/space) at this index.
    '''
    if font.info.header.indextolocformat == 1:
        offset = font.fontfile.readuint32(font.tables['loca'].offset + index * 4)
        nextofst = font.fontfile.readuint32()
    else:
        offset = font.fontfile.readuint16(font.tables['loca'].offset + index * 2) * 2
        nextofst = font.fontfile.readuint16() * 2

    if offset == nextofst:
        # Empty glyphs (ie space) have no length.
        return None
    else:
        return offset + font.tables['glyf'].offset


def read_glyph_glyf(glyphid: int, font: Font) -> SimpleGlyph:
    ''' Read a glyph from the glyf table. '''
    offset = glyphoffset(font, glyphid)

    if offset is None:
        return EmptyGlyph(glyphid, font)

    if offset >= font.tables['glyf'].offset + font.tables['glyf'].length:
        return EmptyGlyph(glyphid, font)

    assert offset >= font.tables['glyf'].offset
    assert offset < font.tables['glyf'].offset + font.tables['glyf'].length

    font.fontfile.seek(offset)

    numcontours = font.fontfile.readint16()
    xmin = font.fontfile.readint16()
    ymin = font.fontfile.readint16()
    xmax = font.fontfile.readint16()
    ymax = font.fontfile.readint16()
    charbox = BBox(xmin, xmax, ymin, ymax)
    glyph: Union[SimpleGlyph, CompoundGlyph]
    if numcontours == -1:
        glyph = read_compoundglyph(font, glyphid, charbox)
    else:
        glyph = read_simpleglyph(font, glyphid, numcontours, charbox)
    return glyph


def read_simpleglyph(font: Font, index: int, numcontours: int, charbox: BBox) -> SimpleGlyph:
    ''' Read a symple glyph from the fontfile. Assumes file pointer is set '''
    fontfile = font.fontfile
    ends = []
    for i in range(numcontours):
        ends.append(font.fontfile.readuint16())
    instlength = fontfile.readuint16()
    fontfile.seek(instlength + fontfile.tell())  # Skip instructions

    numpoints = max(ends) + 1

    # flags
    ONCURVE = 0x01
    XSHORT = 0x02
    YSHORT = 0x04
    REPEAT = 0x08
    XDUP = 0x10
    YDUP = 0x20

    flags = []
    i = 0
    while i < numpoints:
        flag = fontfile.readuint8()
        if (flag & REPEAT):
            nrepeats = fontfile.readuint8() + 1  # Include the first one too
        else:
            nrepeats = 1
        flags.extend([flag] * nrepeats)
        i += nrepeats

    ctvals = [(f & ONCURVE) == 0 for f in flags]  # True for control point, False for real point
    xvals = []
    xval = 0  # Points are stored as deltas. Add them up as we go to get real points.
    for flag in flags:
        if (flag & XSHORT):  # X is one-byte
            if (flag & XDUP):
                xval += fontfile.readuint8()
            else:
                xval -= fontfile.readuint8()
        elif not (flag & XDUP):
            xval += fontfile.readint16()
        # else: xval stays the same
        xvals.append(xval)

    yvals = []
    yval = 0  # Add up deltas
    for flag in flags:
        if (flag & YSHORT):  # Y is one-byte
            if (flag & YDUP):
                yval += fontfile.readuint8()
            else:
                yval -= fontfile.readuint8()
        elif not (flag & YDUP):
            yval += fontfile.readint16()
        # else: yval stays the same
        yvals.append(yval)

    points = []
    controls = []
    start = 0
    for end in ends:
        stop = end + 1
        points.append([Point(x, y) for x, y in zip(xvals[start:stop], yvals[start:stop])])
        controls.append(ctvals[start:stop])
        start = stop

    operators: list[SVGOpType] = []
    for p, c in zip(points, controls):
        npoints = len(p)
        if c[0]:
            # Path STARTS with a control point. Wrap last point in path.
            # Unna-Regular.ttf is an example.
            if c[-1]:
                pim = (p[0] + p[-1])/2
                operators.append(Moveto(pim))  # Last point is also control
            else:
                operators.append(Moveto(p[-1]))
        else:
            operators.append(Moveto(p[0]))

        i = 0
        while i < npoints:
            if c[i]:  # This is a control point
                if i == npoints-1:
                    # Last point is control. End point wraps to start point.
                    if c[0]:  # First point is also control, use midpoint
                        pim = (p[0] + p[-1])/2
                        operators.append(Quad(p[i], pim))
                    else:  # First point is real
                        operators.append(Quad(p[i], p[0]))
                    i += 1
                elif c[i+1]:
                    # Next point is also control.
                    # End of this bezier is implied between two controls
                    pim = (p[i] + p[i+1])/2
                    operators.append(Quad(p[i], pim))
                    i += 1
                else:
                    # Next point is real. It's the endpoint of bezier
                    operators.append(Quad(p[i], p[i+1]))
                    i += 2
            else:
                operators.append(Lineto(p[i]))
                i += 1

    glyph = SimpleGlyph(index, operators, charbox, font)
    return glyph


def read_compoundglyph(font: Font, index: int, charbox: BBox) -> CompoundGlyph:
    ''' Read compound glyph from the fontfile. Assumes filepointer is set '''
    fontfile = font.fontfile

    ARG_WORDS = 0x0001
    ARG_XY = 0x0002
    # ROUND = 0x0004
    SCALE = 0x0008
    MORE = 0x0020
    XYSCALE = 0x0040
    TWOBYTWO = 0x0080
    # INSTRUCTIONS = 0x0100
    # METRICS = 0x0200
    # OVERLAP = 0x0400

    glyphidxs = []
    xforms = []
    moreglyphs = True
    while moreglyphs:
        flag = fontfile.readuint16()
        moreglyphs = (flag & MORE) == MORE
        subindex = fontfile.readuint16()
        match = False
        if (flag & ARG_WORDS):
            if (flag & ARG_XY):
                e = fontfile.readint16()
                f = fontfile.readint16()
            else:
                match = True
                e = fontfile.readuint16()
                f = fontfile.readuint16()
        else:
            if (flag & ARG_XY):
                e = fontfile.readint8()
                f = fontfile.readint8()
            else:
                match = True
                e = fontfile.readint8()
                f = fontfile.readint8()

        # Read Transformation
        if (flag & SCALE):
            a = d = fontfile.readshort()
            b = c = 0.
        elif (flag & XYSCALE):
            a = fontfile.readshort()
            d = fontfile.readshort()
            b = c = 0.
        elif (flag & TWOBYTWO):
            a = fontfile.readshort()
            b = fontfile.readshort()
            c = fontfile.readshort()
            d = fontfile.readshort()
        else:
            a = d = 1.
            b = c = 0.

        xforms.append(Xform(a, b, c, d, e, f, match))
        glyphidxs.append(subindex)

    glyphs = []
    for idx in glyphidxs:
        glyphs.append(read_glyph_glyf(idx, font))

    comp = GlyphComp(glyphs, xforms, charbox)
    return CompoundGlyph(index, comp, font)
