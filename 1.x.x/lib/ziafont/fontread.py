''' CLass for reading bytes from a font file '''
from __future__ import annotations
import struct
from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional


class FontReader(BytesIO):
    ''' Class for reading from Font File '''
    # TTF/OTF is big-endian (>)

    def readuint32(self, offset: Optional[int] = None) -> int:
        ''' Read 32-bit unsigned integer '''
        if offset:
            self.seek(offset)
        return struct.unpack('>I', self.read(4))[0]

    def readuint24(self, offset: Optional[int] = None) -> int:
        ''' Read 24-bit unsigned integer '''
        if offset:
            self.seek(offset)
        return int.from_bytes(self.read(3), 'big')

    def readuint16(self, offset: Optional[int] = None) -> int:
        ''' Read 16-bit unsigned integer '''
        if offset:
            self.seek(offset)
        return struct.unpack('>H', self.read(2))[0]

    def readuint8(self, offset: Optional[int] = None) -> int:
        ''' Read 8-bit unsigned integer '''
        if offset:
            self.seek(offset)
        return struct.unpack('>B', self.read(1))[0]

    def readint8(self, offset: Optional[int] = None) -> int:
        ''' Read 8-bit signed integer '''
        if offset:
            self.seek(offset)
        return struct.unpack('>b', self.read(1))[0]

    def readdate(self, offset: Optional[int] = None) -> datetime:
        ''' Read datetime '''
        if offset:
            self.seek(offset)
        mtime = self.readuint32() * 0x100000000 + self.readuint32()
        fontepoch = datetime(1904, 1, 1)
        mdate = fontepoch + timedelta(seconds=mtime)
        return mdate

    def readint16(self, offset: Optional[int] = None) -> int:
        ''' Read 16-bit signed integer '''
        if offset:
            self.seek(offset)
        return struct.unpack('>h', self.read(2))[0]

    def readshort(self, offset: Optional[int] = None) -> float:
        ''' Read "short" fixed point number (S1.14) '''
        if offset:
            self.seek(offset)
        x = self.readint16()
        return float(x) * 2**-14

    def readvaluerecord(self, fmt: int) -> dict[str, int]:
        ''' Read a GPOS "ValueRecord" into a dictionary. Zero values will be omitted. '''
        record = {}
        if fmt & 0x0001:
            record['x'] = self.readint16()
        if fmt & 0x0002:
            record['y'] = self.readint16()
        if fmt & 0x0004:
            record['xadvance'] = self.readint16()
        if fmt & 0x0008:
            record['yadvance'] = self.readint16()
        if fmt & 0x0010:
            record['xpladeviceoffset'] = self.readuint16()
        if fmt & 0x0020:
            record['ypladeviceoffset'] = self.readuint16()
        if fmt & 0x0040:
            record['xadvdeviceoffset'] = self.readuint16()
        if fmt & 0x0080:
            record['yadvdeviceoffset'] = self.readuint16()
        return record
