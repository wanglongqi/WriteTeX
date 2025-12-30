''' Common Font File Tables '''

from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from dataclasses import dataclass
from collections import namedtuple

if TYPE_CHECKING:
    from .fontread import FontReader


class Coverage:
    ''' Coverage Table - defines which glyphs apply to a lookup

        Parameters
        ----------
        ofst: Byte offset from start of file
        fontfile: Font file to read from
        nulltable: Set true if this table is null
    '''
    def __init__(self, ofst: int, fontfile: FontReader, nulltable: bool = False):
        self.ofst = ofst
        self.fontfile = fontfile
        self.nulltable = nulltable
        if not self.nulltable:
            fileptr = self.fontfile.tell()

            self.fontfile.seek(self.ofst)
            self.format = self.fontfile.readuint16()

            if self.format == 1:
                glyphcnt = self.fontfile.readuint16()
                self.glyphs = []
                for i in range(glyphcnt):
                    self.glyphs.append(self.fontfile.readuint16())

            elif self.format == 2:
                rangecnt = self.fontfile.readuint16()
                Range = namedtuple('Range', ['startglyph', 'endglyph', 'covidx'])
                self.ranges: list[Range] = []
                for i in range(rangecnt):
                    self.ranges.append(Range(
                        self.fontfile.readuint16(),
                        self.fontfile.readuint16(),
                        self.fontfile.readuint16()))
            else:
                raise ValueError(f'Bad coverage table format {self.format}')

            self.fontfile.seek(fileptr)  # Put file pointer back

    def covidx(self, glyph: int) -> Optional[int]:
        ''' Get coverage index for this glyph, or None if not in the coverage range '''
        if self.nulltable:
            return None

        if self.format == 1:
            try:
                idx: Optional[int] = self.glyphs.index(glyph)
            except (ValueError, IndexError):
                idx = None
        else:
            for r in self.ranges:
                if r.startglyph <= glyph <= r.endglyph:
                    idx = r.covidx + (glyph - r.startglyph)
                    break
            else:
                idx = None
        return idx

    def list_glyphs(self) -> list[int]:
        ''' List all glyph indexes covered by the table '''
        if self.format == 1:
            return [g for g in self.glyphs]  # make a copy

        glyphs = []
        for rng in self.ranges:
            glyphs.extend(list(range(rng.startglyph, rng.endglyph+1)))
        return glyphs

    def __repr__(self):
        return f'<CoverageTable {hex(self.ofst)}>'


class ClassDef:
    ''' Class Definition Table - defines a "class" of glyphs. '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()

        self.fontfile.seek(self.ofst)
        self.format = self.fontfile.readuint16()

        if self.format == 1:
            self.startglyph = self.fontfile.readuint16()
            glyphcnt = self.fontfile.readuint16()
            self.classvalues = []
            for i in range(glyphcnt):
                self.classvalues.append(self.fontfile.readuint16())

        elif self.format == 2:
            ClassRange = namedtuple('ClassRange', ['startglyph', 'endglyph', 'cls'])
            rangecnt = self.fontfile.readuint16()
            self.ranges = []
            for i in range(rangecnt):
                self.ranges.append(ClassRange(
                    self.fontfile.readuint16(),
                    self.fontfile.readuint16(),
                    self.fontfile.readuint16()))
        else:
            raise ValueError

        self.fontfile.seek(fileptr)  # Put file pointer back

    def get_class(self, glyphid: int) -> int:
        ''' Get class by glyph id '''
        if self.format == 1:
            if self.startglyph <= glyphid < self.startglyph + len(self.classvalues):
                return self.classvalues[glyphid - self.startglyph]
            else:
                return 0

        else:
            for i, rng in enumerate(self.ranges):
                if rng.startglyph <= glyphid <= rng.endglyph:
                    return rng.cls
            return 0

    def __repr__(self):
        return f'<ClassDefTable {hex(self.ofst)}>'


class ClassDefBlank(ClassDef):
    ''' Blank class definition '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile

    def get_class(self, glyphid: int) -> int:
        return 0


class Feature:
    ''' Feature Table for GPOS/GSUB '''
    def __init__(self, tag: str, ofst: int, fontfile: FontReader):
        self.tag = tag
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()
        self.fontfile.seek(self.ofst)
        self.featureparamofst = self.fontfile.readuint16()
        lookupcnt = self.fontfile.readuint16()
        self.lookupids = []
        for i in range(lookupcnt):
            self.lookupids.append(self.fontfile.readuint16())

        self.fontfile.seek(fileptr)  # Put file pointer back

    def __repr__(self):
        return f'<Feature {self.tag}, {hex(self.ofst)}>'


class Script:
    ''' GPOS/GSUB Script table '''
    def __init__(self, tag: str, ofst: int, fontfile: FontReader):
        self.tag = tag
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()
        self.fontfile.seek(self.ofst)
        self.defaultLangSysOfst = self.fontfile.readuint16()
        self.languages = {}

        if self.defaultLangSysOfst:
            self.languages[''] = LanguageSystem(
                '',
                self.defaultLangSysOfst + self.ofst,
                self.fontfile)

        langsyscnt = self.fontfile.readuint16()
        for i in range(langsyscnt):
            tag = self.fontfile.read(4).decode()
            self.languages[tag] = (LanguageSystem(
                tag,
                self.fontfile.readuint16() + self.ofst,
                self.fontfile))

        self.fontfile.seek(fileptr)  # Put file pointer back

    def __repr__(self):
        return f'<Script {self.tag}, {hex(self.ofst)}>'


class LanguageSystem:
    ''' GPOS/GSUB Language System Table '''
    def __init__(self, tag: str, ofst: int, fontfile: FontReader):
        self.tag = tag
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()
        self.fontfile.seek(self.ofst)
        self.fontfile.readuint16()  # lookupordeoffset (reserved)
        self.reqdFeatureIndex = self.fontfile.readuint16()
        featurecount = self.fontfile.readuint16()
        self.featureidxs = []
        for i in range(featurecount):
            self.featureidxs.append(self.fontfile.readuint16())

        self.fontfile.seek(fileptr)  # Put file pointer back

    def __repr__(self):
        return f'<LanguageSystem {self.tag}, {hex(self.ofst)}>'


@dataclass
class Language:
    ''' Font script and language '''
    script: str = 'latn'
    language: str = ''  # Default
