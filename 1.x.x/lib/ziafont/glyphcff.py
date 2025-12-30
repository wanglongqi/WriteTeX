''' CFF/Type 2 Charstring Glyphs '''

from __future__ import annotations
from typing import Union, TYPE_CHECKING

import struct
from enum import Enum
import warnings

from .glyph import SimpleGlyph
from .fonttypes import BBox
from .svgpath import Point, Moveto, Lineto, Cubic, SVGOpType

if TYPE_CHECKING:
    from .font import Font


class Operator(Enum):
    ''' Charstring Operators '''
    HSTEM = 1
    # reserved = 2
    VSTEM = 3
    VMOVETO = 4
    RLINETO = 5
    HLINETO = 6
    VLINETO = 7
    RRCURVETO = 8
    # reserved = 9
    CALLSUBR = 10
    RETURN = 11
    # escape = 12
    # reserved = 13
    ENDCHAR = 14
    # reserved = 15, 16, 17
    HSTEMHM = 18
    HINTMASK = 19
    CNTRMASK = 20
    RMOVETO = 21
    HMOVETO = 22
    VSTEMHM = 23
    RCURVELINE = 24
    RLINECURVE = 25
    VVCURVETO = 26
    HHCURVETO = 27
    # reserved = 28/short int
    CALLGSUBR = 29
    VHCURVETO = 30
    HVCURVETO = 31
    # 2-byte codes
    AND = 0x0c03
    OR = 0x0c04
    NOT = 0x0c05
    ABS = 0x0c09
    ADD = 0x0c0a
    SUB = 0x0c0c
    NEG = 0x0c0e
    EQ = 0x0c0f
    DROP = 0x0c12
    PUT = 0x0c14
    GET = 0x0c15
    IFELSE = 0x0c16
    RANDOM = 0x0c17
    MUL = 0x0c18
    SQRT = 0x0c1a
    DUP = 0x0c1b
    EXCH = 0x0c1c
    INDEX = 0x0c1d
    ROLL = 0x0c1e
    HFLEX = 0x0c22
    FLEX = 0x0c23
    HFLEX1 = 0x0c24
    FLEX1 = 0x0c25
    WIDTH = -999  # Not numbered in CFF spec


def readreal(buf: bytes) -> tuple[float, int]:
    ''' Read real/float value from buffer. Returns (value, #bytes read) '''
    nibbles = {
        0x0a: '.',
        0x0b: 'E',
        0x0c: 'E-',
        # 0x0d: RESERVED,
        0x0e: '-',
        0x0f: ''}  # END

    numstr = ''
    i = 0
    while True:
        nib1 = (buf[i] & 0xF0) >> 4
        nib2 = (buf[i] & 0x0F)
        if nib1 == 0x0f:
            break
        numstr += nibbles.get(nib1, str(nib1))
        if nib2 == 0x0f:
            break
        numstr += nibbles.get(nib2, str(nib2))
        i += 1

    return float(numstr), i+1


def read_glyph_cff(glyphid: int, font: Font) -> SimpleGlyph:
    ''' Read a glyph from the CFF table. '''
    charstr = font.cffdata.charstr_index[glyphid]  # type: ignore
    ops, width, bbox = charstr2path(charstr, font.cffdata)  # type: ignore
    glyph = SimpleGlyph(glyphid, ops, bbox, font)
    return glyph


def charstr2path(charstr: bytes, cff: CFF) -> tuple[list[SVGOpType], float, BBox]:
    ''' Convert the charstring operators into SVG path elements '''
    operators: list[SVGOpType] = []
    width = cff.defaultwidth
    p = Point(0, 0)
    chstate = CharString(charstr, cff)
    op = None
    for op, value in zip(chstate.operators, chstate.operands):
        if op == Operator.WIDTH:
            width = cff.nominalwidth + int(value[0])
        elif op == Operator.RMOVETO:
            p = p + Point(value[0], value[1])
            operators.append(Moveto(p))
        elif op == Operator.HMOVETO:
            p = p + Point(value[0], 0)
            operators.append(Moveto(p))
        elif op == Operator.VMOVETO:
            p = p + Point(0, value[0])
            operators.append(Moveto(p))
        elif op == Operator.HLINETO:
            for i, val in enumerate(value):
                if (i % 2) == 0:  # Alternate Horizontal and Vertical lines
                    p = p + Point(val, 0)
                else:
                    p = p + Point(0, val)
                operators.append(Lineto(p))

        elif op == Operator.VLINETO:
            for i, val in enumerate(value):
                if (i % 2) == 0:  # Alternate Horizontal and Vertical lines
                    p = p + Point(0, val)
                else:
                    p = p + Point(val, 0)
                operators.append(Lineto(p))

        elif op == Operator.RLINETO:
            for dx, dy in zip(value[::2], value[1::2]):
                p = p + Point(dx, dy)
                operators.append(Lineto(p))

        elif op in [Operator.RRCURVETO, Operator.RCURVELINE]:
            while len(value) > 2:
                dxa, dya, dxb, dyb, dxc, dyc, *_ = value
                p1 = p + Point(dxa, dya)
                p2 = p1 + Point(dxb, dyb)
                p = p2 + Point(dxc, dyc)
                operators.append(Cubic(p1, p2, p))
                value = value[6:]
            if op == Operator.RCURVELINE:
                assert len(value) >= 2
                # RCURVELINE ends with a line
                p = p + Point(value[0], value[1])
                operators.append(Lineto(p))

        elif op == Operator.RLINECURVE:
            while len(value) > 6:
                # Lines until last 6 arguments
                p = p + Point(value[0], value[1])
                operators.append(Lineto(p))
                value = value[2:]
            # Last 6 define Bezier
            dxa, dya, dxb, dyb, dxc, dyc, *_ = value
            p1 = p + Point(dxa, dya)
            p2 = p1 + Point(dxb, dyb)
            p = p2 + Point(dxc, dyc)
            operators.append(Cubic(p1, p2, p))

        elif op == Operator.HHCURVETO:
            if len(value) % 4 >= 1:
                dya = value[0]
                value = value[1:]
            else:
                dya = 0
            while len(value) >= 4:
                dxa, dxb, dyb, dxc, *_ = value
                p1 = p + Point(dxa, dya)
                p2 = p1 + Point(dxb, dyb)
                p = p2 + Point(dxc, 0)
                operators.append(Cubic(p1, p2, p))
                dya = 0
                value = value[4:]

        elif op == Operator.VVCURVETO:
            if len(value) % 4 >= 1:
                dxa = value[0]
                value = value[1:]
            else:
                dxa = 0
            while len(value) >= 4:
                dya, dxb, dyb, dyc, *_ = value
                p1 = p + Point(dxa, dya)
                p2 = p1 + Point(dxb, dyb)
                p = p2 + Point(0, dyc)
                operators.append(Cubic(p1, p2, p))
                value = value[4:]
                dxa = 0

        elif op == Operator.HVCURVETO:
            if len(value) % 8 >= 4:
                dx1, dx2, dy2, dy3, *_ = value
                p1 = p + Point(dx1, 0)
                p2 = p1 + Point(dx2, dy2)
                p = p2 + Point(0, dy3)
                if len(value) == 5:
                    p = p + Point(value[-1], 0)
                operators.append(Cubic(p1, p2, p))
                value = value[4:]
                while len(value) >= 8:
                    dya, dxb, dyb, dxc, dxd, dxe, dye, dyf, *_ = value
                    if len(value) == 9:
                        dxf = value[-1]
                    else:
                        dxf = 0

                    p1 = p + Point(0, dya)
                    p2 = p1 + Point(dxb, dyb)
                    p = p2 + Point(dxc, 0)
                    operators.append(Cubic(p1, p2, p))
                    p1 = p + Point(dxd, 0)
                    p2 = p1 + Point(dxe, dye)
                    p = p2 + Point(dxf, dyf)
                    operators.append(Cubic(p1, p2, p))
                    value = value[8:]

            else:
                while len(value) >= 8:
                    dxa, dxb, dyb, dyc, dyd, dxe, dye, dxf, *_ = value
                    if len(value) == 9:
                        dyf = value[-1]
                    else:
                        dyf = 0

                    p1 = p + Point(dxa, 0)
                    p2 = p1 + Point(dxb, dyb)
                    p = p2 + Point(0, dyc)
                    operators.append(Cubic(p1, p2, p))
                    p1 = p + Point(0, dyd)
                    p2 = p1 + Point(dxe, dye)
                    p = p2 + Point(dxf, dyf)
                    operators.append(Cubic(p1, p2, p))
                    value = value[8:]

        elif op == Operator.VHCURVETO:
            if len(value) % 8 >= 4:
                dy1, dx2, dy2, dx3, *_ = value
                p1 = p + Point(0, dy1)
                p2 = p1 + Point(dx2, dy2)
                p = p2 + Point(dx3, 0)
                if len(value) == 5:
                    p = p + Point(0, value[-1])
                operators.append(Cubic(p1, p2, p))
                value = value[4:]
                while len(value) >= 8:
                    dxa, dxb, dyb, dyc, dyd, dxe, dye, dxf, *_ = value
                    if len(value) == 9:
                        dyf = value[-1]
                    else:
                        dyf = 0

                    p1 = p + Point(dxa, 0)
                    p2 = p1 + Point(dxb, dyb)
                    p = p2 + Point(0, dyc)
                    operators.append(Cubic(p1, p2, p))
                    p1 = p + Point(0, dyd)
                    p2 = p1 + Point(dxe, dye)
                    p = p2 + Point(dxf, dyf)
                    operators.append(Cubic(p1, p2, p))
                    value = value[8:]

            else:
                while len(value) >= 8:
                    dya, dxb, dyb, dxc, dxd, dxe, dye, dyf, *_ = value
                    if len(value) == 9:
                        dxf = value[-1]
                    else:
                        dxf = 0

                    p1 = p + Point(0, dya)
                    p2 = p1 + Point(dxb, dyb)
                    p = p2 + Point(dxc, 0)
                    operators.append(Cubic(p1, p2, p))
                    p1 = p + Point(dxd, 0)
                    p2 = p1 + Point(dxe, dye)
                    p = p2 + Point(dxf, dyf)
                    operators.append(Cubic(p1, p2, p))
                    value = value[8:]

        elif op == Operator.FLEX:
            dx1, dy1, dx2, dy2, dx3, dy3, dx4, dy4, dx5, dy5, dx6, dy6, *_ = value
            p1 = p + Point(dx1, dy1)
            p2 = p1 + Point(dx2, dy2)
            p3 = p2 + Point(dx3, dy3)
            p4 = p3 + Point(dx4, dy4)
            p5 = p4 + Point(dx5, dy5)
            p = p5 + Point(dx6, dy6)
            operators.append(Cubic(p1, p2, p3))
            operators.append(Cubic(p4, p5, p))

        elif op == Operator.FLEX1:
            dx1, dy1, dx2, dy2, dx3, dy3, dx4, dy4, dx5, dy5, d6, *_ = value
            dx = dx1+dx2+dx3+dx4+dx5
            dy = dy1+dy2+dy3+dy4+dy5

            p1 = p + Point(dx1, dy1)
            p2 = p1 + Point(dx2, dy2)
            p3 = p2 + Point(dx3, dy3)
            p4 = p3 + Point(dx4, dy4)
            p5 = p4 + Point(dx5, dy5)
            if abs(dx) > abs(dy):
                p = p5 + Point(d6, 0)
            else:
                p = p5 + Point(0, d6)
            operators.append(Cubic(p1, p2, p3))
            operators.append(Cubic(p4, p5, p))

        elif op == Operator.HFLEX:
            dx1, dx2, dy2, dx3, dx4, dx5, dx6, *_ = value
            p1 = p + Point(dx1, 0)
            p2 = p1 + Point(dx2, dy2)
            p3 = p2 + Point(dx3, 0)
            p4 = p3 + Point(dx4, 0)
            p5 = p4 + Point(dx5, 0)
            p = p5 + Point(dx6, 0)
            operators.append(Cubic(p1, p2, p3))
            operators.append(Cubic(p4, p5, p))

        elif op == Operator.HFLEX1:
            dx1, dy1, dx2, dy2, dx3, dx4, dx5, dy5, dx6, *_ = value
            p1 = p + Point(dx1, dy1)
            p2 = p1 + Point(dx2, dy2)
            p3 = p2 + Point(dx3, 0)
            p4 = p3 + Point(dx4, 0)
            p5 = p4 + Point(dx5, dy5)
            p = p5 + Point(dx6, 0)
            operators.append(Cubic(p1, p2, p3))
            operators.append(Cubic(p4, p5, p))

        elif op not in [Operator.HSTEM, Operator.HINTMASK, Operator.VSTEM,
                        Operator.VSTEMHM, Operator.HSTEMHM, Operator.RETURN,
                        Operator.CNTRMASK, Operator.ENDCHAR]:
            raise NotImplementedError(f'Operator {op} not implemented')

    if op != Operator.ENDCHAR:
        warnings.warn('Glyph has no ENDCHAR')

    try:
        xmin = min(op.xmin() for op in operators)
        xmax = max(op.xmax() for op in operators)
        ymin = min(op.ymin() for op in operators)
        ymax = max(op.ymax() for op in operators)
    except ValueError:  # no operators
        ymin = ymax = xmin = xmax = 0
    return operators, width, BBox(xmin, xmax, ymin, ymax)


class CharString:
    ''' CharString reader '''
    def __init__(self, buf: bytes, cff: CFF):
        self.buf = buf
        self.cff = cff

        self.stack: list[float] = []
        self.operators: list[Union[Operator, int]] = []
        self.operands: list[list[float]] = []
        self.nhints = 0
        self.readcharstr(buf)

    def append(self, operator: Operator):
        ''' Append an operator, and clear the stack '''
        self.operators.append(operator)
        self.operands.append(self.stack)
        self.stack = []

    def addwidth(self):
        ''' Add width operator '''
        self.operators.append(Operator.WIDTH)
        self.operands.append([self.stack[0]])
        self.stack = self.stack[1:]

    @property
    def lenstack(self):
        ''' Length of stack '''
        return len(self.stack)

    def readcharstr(self, buf: bytes):
        ''' Read charstring bytes into operators/operands lists '''
        key: Union[Operator, int]
        while len(buf) > 0:
            if buf[0] <= 27 or 29 <= buf[0] <= 31:  # Operator
                key = buf[0]
                nbytes = 1
                if buf[0] == 12:
                    key = struct.unpack_from('>H', buf)[0]
                    nbytes = 2

                try:
                    key = Operator(key)
                except ValueError as exc:
                    break
                    # raise NotImplementedError(f'Unimplemented KEY {key}') from exc

                if len(self.operators) == 0:
                    # First operator can have extra width parameter.
                    # have to deduce its presence based on the
                    # operator and number of values in stack
                    if key in [Operator.CNTRMASK, Operator.ENDCHAR] and self.lenstack == 1:
                        self.addwidth()
                    elif ((key in [Operator.HMOVETO, Operator.VMOVETO] and self.lenstack > 1) or
                          (key in [Operator.RMOVETO] and self.lenstack > 2)):
                        self.addwidth()
                    elif (key in [Operator.HSTEM, Operator.HSTEMHM, Operator.VSTEM,
                                  Operator.VSTEMHM, Operator.HINTMASK] and
                          self.lenstack % 2 != 0):
                        self.addwidth()

                if key in [Operator.CALLSUBR, Operator.CALLGSUBR]:
                    if key == Operator.CALLSUBR:
                        sublist = self.cff.localsubs
                    else:
                        sublist = self.cff.globalsub

                    if self.cff.topdict.get('charstringtype', 2) == 1:
                        bias = 0
                    elif len(sublist) < 1240:
                        bias = 107
                    elif len(sublist) < 33900:
                        bias = 1131
                    else:
                        bias = 32768
                    idx = int(self.stack[-1] + bias)

                    subchstr = sublist[idx]
                    self.stack = self.stack[:-1]  # remove sub# from stack
                    self.readcharstr(subchstr)
                    buf = buf[nbytes:]
                    continue

                elif key in [Operator.HINTMASK, Operator.CNTRMASK]:
                    if (len(self.operators) > 0
                            and self.operators[-1] == Operator.HSTEMHM
                            and self.lenstack > 0):
                        # Implied VSTEM operator
                        self.nhints += self.lenstack // 2
                        self.append(Operator.VSTEMHM)
                    elif (len(self.operators) == 0
                            or (len(self.operators) == 1 and self.operators[0] == Operator.WIDTH)):
                        self.nhints += self.lenstack // 2
                        self.append(Operator.VSTEMHM)
                    # N-bits for the N hint masks just read in
                    hintbytes = self.nhints + 7 >> 3
                    self.stack = list(buf[1:hintbytes+1])
                    nbytes = hintbytes+1

                elif key in [Operator.HSTEM, Operator.HSTEMHM,
                             Operator.VSTEM, Operator.VSTEMHM]:
                    self.nhints += self.lenstack // 2

                if key not in [Operator.RETURN]:
                    self.append(key)

            # Opearands (numeric values)
            elif buf[0] == 28:
                self.stack.append(struct.unpack_from('>h', buf[1:])[0])  # signed short
                nbytes = 3
            elif 32 <= buf[0] <= 246:
                self.stack.append(buf[0] - 139)
                nbytes = 1
            elif 247 <= buf[0] <= 250:
                self.stack.append((buf[0]-247)*256 + buf[1] + 108)
                nbytes = 2
            elif 251 <= buf[0] <= 254:
                self.stack.append(-(buf[0]-251)*256 - buf[1] - 108)
                nbytes = 2
            elif buf[0] == 255:
                self.stack.append(struct.unpack_from('>l', buf[1:])[0] / 0x10000)
                nbytes = 5
            else:
                raise ValueError('Bad encoding byte: ' + str(buf[0]))

            buf = buf[nbytes:]


def readdict(buf: bytes) -> dict:
    ''' Read a CFF dictionary structure from the buffer '''
    data: dict[Union[int, str], Union[None, list[float], float]] = {}
    value: list[float] = []
    key: Union[int, str]
    while len(buf) > 0:
        # Operator (key)
        if buf[0] <= 21:
            key = buf[0]
            i = 1
            if buf[0] == 12:
                key = struct.unpack_from('>h', buf)[0]
                i = 2
            if len(value) == 0:
                data[key] = None
            elif len(value) == 1:
                data[key] = value[0]
            else:
                data[key] = value
            value = []

        # Opearand (value)
        elif buf[0] == 28:
            value.append(struct.unpack_from('>h', buf[1:])[0])  # signed short
            i = 3
        elif buf[0] == 29:
            value.append(struct.unpack_from('>l', buf[1:])[0])  # signed long
            i = 5
        elif 32 <= buf[0] <= 246:
            value.append(buf[0] - 139)
            i = 1
        elif 247 <= buf[0] <= 250:
            value.append((buf[0]-247)*256 + buf[1] + 108)
            i = 2
        elif 251 <= buf[0] <= 254:
            value.append(-(buf[0]-251)*256 - buf[1] - 108)
            i = 2
        elif buf[0] == 30:
            v, nbytes = readreal(buf[1:])
            value.append(v)
            i = (nbytes+1)
        else:
            warnings.warn('Bad encoding byte: ' + str(buf[0]))
            value.append(0)
            i = 1

        buf = buf[i:]
    return data


class CFF:
    ''' Compact Font Format table info '''
    def __init__(self, font: Font):
        self.cffofst = font.tables['CFF '].offset
        self.font = font
        self.fontfile = self.font.fontfile

        self.major = self.fontfile.readuint8(self.cffofst)
        self.minor = self.fontfile.readuint8()
        self.headsize = self.fontfile.readuint8()
        self.offsize = self.fontfile.readuint8()
        self.names = self.readindex()
        topdict_bytes = self.readindex()
        self.strings = self.readindex()
        self.globalsub: list[bytes] = self.readindex()
        self.topdicts: list[dict] = [self.read_topdict(readdict(t)) for t in topdict_bytes]
        self.set_topdict(0)

    def set_topdict(self, idx: int = 0) -> None:
        ''' Set which TOP DICT to use and load the corresponding
            PRIVATE DICT values.
        '''
        topdict = self.topdicts[idx]
        self.topdict = topdict
        charstr_ofst = self.cffofst + topdict['charstrings']
        self.charstr_index: list[bytes] = self.readindex(charstr_ofst)
        self.nglyphs = len(self.charstr_index)

        self.font.fontfile.seek(self.cffofst + topdict['private'][1])
        pdictbytes = self.font.fontfile.read(topdict['private'][0])
        self.privatedict = self.read_topdict(readdict(pdictbytes))
        self.localsubs: list[bytes] = []
        if 'subrs' in self.privatedict:
            self.localsubs = self.readindex(
                self.cffofst + topdict['private'][1] + self.privatedict['subrs'])

    @property
    def defaultwidth(self) -> int:
        ''' Get default glyph width '''
        return self.privatedict.get('defaultwidthx', 0)

    @property
    def nominalwidth(self) -> int:
        ''' Get nominal glyph width '''
        return self.privatedict.get('nominalwidthx', 0)

    def getstring(self, sid: int) -> bytes:
        ''' Get a string by String ID '''
        nstandardstrings = 391
        if sid > nstandardstrings:
            return self.strings[sid-nstandardstrings]
        else:
            return b'standard string'  # TODO

    def readindex(self, offset=None) -> list[bytes]:
        ''' Read an INDEX structure from the CFF data '''
        count = self.fontfile.readuint16(offset)
        offsize = self.fontfile.readuint8()  # should be 1-4
        if offsize == 0:
            return []

        offsets = []
        for i in range(count+1):
            if offsize == 1:
                offsets.append(self.fontfile.readuint8())
            elif offsize == 2:
                offsets.append(self.fontfile.readuint16())
            elif offsize == 3:
                offsets.append(self.fontfile.readuint24())
            elif offsize == 4:
                offsets.append(self.fontfile.readuint32())
            else:
                raise ValueError('Incorrect offset size ' + str(offsize))

        dataofst = self.fontfile.tell()-1  # Start of Object data (minus 1)
        values = []
        for i in range(count):
            self.fontfile.seek(dataofst + offsets[i])
            values.append(self.fontfile.read(offsets[i+1]-offsets[i]))
        return values

    def read_topdict(self, d: dict) -> dict:
        ''' Translate raw CFF dictionary into topdict with meaningful keys '''
        topdict_entries = {
            0: ('version', 'sid'),
            1: ('notice', 'sid'),
            2: ('fullname', 'sid'),
            3: ('familyname', 'sid'),
            4: ('weight', 'number'),
            5: ('fontbbox', 'array'),
            13: ('uniqueid', 'number'),
            14: ('xuid', 'array'),
            15: ('charset', 'number'),
            16: ('encoding', 'number'),
            17: ('charstrings', 'number'),
            18: ('private', 'array'),
            0x0c00: ('copyright', 'sid'),
            0x0c01: ('isfixedpitch', 'number'),
            0x0c02: ('italicangle', 'number'),
            0x0c03: ('underlineposition', 'number'),
            0x0c04: ('underlinethickness', 'number'),
            0x0c05: ('painttype', 'number'),
            0x0c06: ('charstringtype', 'number'),
            0x0c07: ('fontmatrix', 'array'),
            0x0c08: ('strokewidth', 'number'),
            0x0c14: ('syntheticbase', 'number'),
            0x0c15: ('postscript', 'sid'),
            0x0c16: ('basefontname', 'sid'),
            0x0c17: ('basefontblend' 'array'),
            # Private Dict Keys
            6: ('bluevalues', 'array'),
            7: ('otherblues', 'array'),
            8: ('familyblues', 'array'),
            9: ('familyotherblues', 'array'),
            10: ('stdhw', 'number'),
            11: ('stdvw', 'number'),
            19: ('subrs', 'number'),
            20: ('defaultwidthx', 'number'),
            21: ('nominalwidthx', 'number'),
            0x0c09: ('bluescale', 'number'),
            0x0c0a: ('blueshift', 'number'),
            0x0c0b: ('bluefuzz', 'number'),
            0x0c0c: ('stemsnaph', 'array'),
            0x0c0d: ('stemsnapv', 'array'),
            0x0c0e: ('forcebold', 'number'),
            0x0c11: ('languagegroup', 'number'),
            0x0c12: ('expansionfactor', 'number'),
            0x0c13: ('initialrandomseed', 'number'),
            # CIDfont
            0x0c1e: ('ROS', 'array'),
            0x0c1f: ('CIDFontVersion', 'number'),
            0x0c20: ('CIDFontRevision', 'number'),
            0x0c21: ('CIDFontType', 'number'),
            0x0c22: ('CIDCount', 'number'),
            0x0c23: ('UIDBase', 'number'),
            0x0c24: ('FDArray', 'array'),
            0x0c25: ('FDSelect', 'number'),
            0x0c26: ('FontName', 'sid')}

        newd = {}
        for key, value in d.items():
            newkey, dtype = topdict_entries.get(key, (key, 'number'))
            if newkey:
                if dtype == 'sid':
                    value = self.getstring(value)
                newd[newkey] = value

        assert newd.get('charstringtype', 2) == 2
        if 'ROS' in newd:
            raise NotImplementedError('CID fonts not implemented.')
        return newd
