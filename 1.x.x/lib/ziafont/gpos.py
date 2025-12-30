''' Glyph Positioning System (GPOS) tables '''

from __future__ import annotations
from typing import Optional, Union
import logging
from collections import namedtuple

from .fontread import FontReader
from .tables import Coverage, ClassDef, Feature, Script, Language
from .glyph import SimpleGlyph


PositionDelta = namedtuple('PositionDelta', ['dx', 'dy', 'dadvance'])

# Features that cant' be turned off
PERM_FEATURES = ['mark', 'mkmk', 'curs']

# Features that are on by default
ON_FEATURES = ['kern']


class Gpos:
    ''' Glyph Positioning System Table '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile
        self.language = Language()
        self.fontfile.seek(self.ofst)

        self.vermajor = self.fontfile.readuint16()
        self.verminor = self.fontfile.readuint16()
        scriptofst = self.fontfile.readuint16()
        featureofst = self.fontfile.readuint16()
        lookupofst = self.fontfile.readuint16()
        if self.verminor > 0:
            self.variationofst = self.fontfile.readuint32()
            logging.warning('GPOS has feature variations - unimplemented')

        # Read scripts
        self.scripts = {}
        if scriptofst != 0:
            scriptlisttableloc = self.ofst + scriptofst
            scriptcnt = self.fontfile.readuint16(scriptlisttableloc)
            for i in range(scriptcnt):
                tag = self.fontfile.read(4).decode()
                self.scripts[tag] = Script(
                    tag,
                    self.fontfile.readuint16() + scriptlisttableloc,
                    self.fontfile)

        # Read features
        featurelist = []
        if featureofst != 0:
            featurelisttableloc = self.ofst + featureofst
            featurecnt = self.fontfile.readuint16(featurelisttableloc)
            for i in range(featurecnt):
                featurelist.append(Feature(
                    self.fontfile.read(4).decode(),
                    self.fontfile.readuint16() + featurelisttableloc,
                    self.fontfile))

        # Read Lookups
        self.lookups = []
        if lookupofst != 0:
            lookuplisttableloc = self.ofst + lookupofst
            lookupcnt = self.fontfile.readuint16(lookuplisttableloc)
            for i in range(lookupcnt):
                self.lookups.append(GposLookup(
                    self.fontfile.readuint16() + lookuplisttableloc,
                    self.fontfile))

        # Put everything in a dictionary for access
        self.features = {}
        for scrname, script in self.scripts.items():
            langdict = {}
            for langname, lang in script.languages.items():
                langfeatures = [featurelist[i] for i in lang.featureidxs]
                featnames = [f.tag for f in langfeatures]
                featdict = {}
                for feat in featnames:
                    lookups = langfeatures[featnames.index(feat)].lookupids
                    tables = [self.lookups[i] for i in lookups]
                    featdict[feat] = tables
                langdict[langname] = featdict
            self.features[scrname] = langdict

        if self.features and 'latn' not in self.features:
            self.language.script = list(self.features.keys())[0]

    def features_available(self):
        ''' Dictionary of features active in the current script/language system '''
        return self.features.get(self.language.script, {}).get(self.language.language, {})

    def init_user_features(self) -> dict[str, bool]:
        ''' Initialize features that can be set by user '''
        avail = list(self.features_available().keys())
        avail = [feat for feat in avail if feat not in PERM_FEATURES]
        return {feat: feat in ON_FEATURES for feat in avail}

    def position(self, glyphs: list[SimpleGlyph], features: dict[str, bool]) -> list[tuple[int, int]]:
        ''' Calculate x, y position of each glyph using the given features '''
        gids = [glyph.index for glyph in glyphs]
        delta: list[PositionDelta] = [PositionDelta(0,0,0) for _ in gids]
        advances = [glyph.advance() for glyph in glyphs]

        feattable = self.features_available()
        for feat in feattable.keys():
            if feat in PERM_FEATURES or features.get(feat, False):        
                tables = feattable.get(feat, [])
                for table in tables:
                    ddelta = table.adjust(*gids, advances=advances, lookups=self.lookups)
                    delta = merge_deltas(delta, ddelta)

        xy: list[tuple[int, int]] = []
        x = 0
        for d, glyph in zip(delta, glyphs):
            x += d.dx
            xy.append((x, d.dy))
            x += glyph.advance() + d.dadvance
        return xy

    def __repr__(self):
        return f'<GPOS Table v{self.vermajor}.{self.verminor}>'


class GposLookup:
    ''' GPOS Lookup Table '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()

        RIGHT_TO_LEFT = 0x0001
        IGNORE_BASE_GLYPHS = 0x0002
        IGNORE_LIGATURES = 0x0004
        IGNORE_MARKS = 0x0008
        USE_MARK_FILTERING_SET = 0x0010
        MARK_ATTACHMENT_TYPE_MASK = 0xFF00

        self.fontfile.seek(self.ofst)
        self.type = self.fontfile.readuint16()
        self.flag = self.fontfile.readuint16()
        subtablecnt = self.fontfile.readuint16()
        self.tableofsts = []
        for _ in range(subtablecnt):
            self.tableofsts.append(self.fontfile.readuint16())
        self.markfilterset = None
        if self.flag & USE_MARK_FILTERING_SET:
            self.markfilterset = self.fontfile.readuint16()

        self.subtables: list[GposSubtable] = []
        for tblofst in self.tableofsts:
            tabletype = self.type
            fmt = self.fontfile.readuint16(self.ofst + tblofst)
            if self.type == 9:  # Extension table - converts to another type
                assert fmt == 1
                tabletype = self.fontfile.readuint16()
                tblofst += self.fontfile.readuint32()
                fmt = self.fontfile.readuint16(self.ofst+tblofst)

            if tabletype == 1 and fmt == 1:
                self.subtables.append(SingleAdjustmentSubtable(
                    tblofst + self.ofst, self.fontfile))
            elif tabletype == 1 and fmt == 2:
                self.subtables.append(SingleAdjustmentSubtable2(
                    tblofst + self.ofst, self.fontfile))
            elif tabletype == 2:  # Pair adjustment positioning
                self.subtables.append(PairAdjustmentSubtable(
                        tblofst + self.ofst, self.fontfile))
            elif tabletype == 4:  # Mark-to-base
                self.subtables.append(MarkToBaseSubtable(
                        tblofst + self.ofst, self.fontfile))
            elif tabletype == 6:  # Mark-to-mark
                self.subtables.append(MarkToMarkSubtable(
                        tblofst + self.ofst, self.fontfile))
            else:
                logging.debug('Unimplemented GPOS Lookup Type %s', self.type)

        self.fontfile.seek(fileptr)  # Put file pointer back

    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        ''' Get dx, dy, dxadvance for the glyph '''
        deltas: list[PositionDelta] = [PositionDelta(0,0,0) for _ in glyphids]
        for subtable in self.subtables:
            d = subtable.adjust(*glyphids, advances=advances, lookups=lookups)
            deltas = merge_deltas(deltas, d)
        return deltas

    def __repr__(self):
        return f'<GPOSLookup Type {self.type} {hex(self.ofst)}>'


def merge_delta(d1: PositionDelta, d2: PositionDelta) -> PositionDelta:
    return PositionDelta(d1.dx+d2.dx,
                         d1.dy+d2.dy,
                         d1.dadvance+d2.dadvance)


def merge_deltas(deltas1: list[PositionDelta], deltas2: list[PositionDelta]) -> list[PositionDelta]:
    return [merge_delta(d1, d2)
            for d1, d2 in zip(deltas1, deltas2)]


def valuerec_to_delta(vrec: dict[str, int]|None) -> PositionDelta:
    if vrec is None:
        return PositionDelta(0, 0, 0)
    return PositionDelta(
        vrec.get('x', 0),
        vrec.get('y', 0),
        vrec.get('xadvance', 0))


class GposSubtable:
    ''' Base class for GPOS subtables (mostly for type hints) '''
    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        return []


class SingleAdjustmentSubtable(GposSubtable):
    ''' Single adjustment subtable (GPOS Lookup 1.1) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()

        self.fontfile.seek(self.ofst)
        fmt = self.fontfile.readuint16()
        assert fmt == 1
        self.covofst = self.fontfile.readuint16()
        valueformat = self.fontfile.readuint16()
        self.valuerecord = self.fontfile.readvaluerecord(valueformat)
        self.coverage = Coverage(self.covofst+self.ofst, self.fontfile)
        self.fontfile.seek(fileptr)  # Put file pointer back

    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        ''' Get dx, dy, dxadvance for the glyph '''
        adjusts: list[PositionDelta] = []

        for gid in glyphids:
            if self.coverage.covidx(gid) is not None:
                pos = PositionDelta(
                    self.valuerecord.get('x', 0),
                    self.valuerecord.get('y', 0),
                    self.valuerecord.get('xadvance', 0))
                logging.debug('Positioning glyph %s: (%s, %s, %s)',
                              gid, pos.dx, pos.dy, pos.dadvance)

            else:
                pos = PositionDelta(0, 0, 0)
            adjusts.append(pos)
        return adjusts


class SingleAdjustmentSubtable2(GposSubtable):
    ''' Single adjustment subtable (GPOS Lookup 1.2) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()

        self.fontfile.seek(self.ofst)
        fmt = self.fontfile.readuint16()
        assert fmt == 2
        self.covofst = self.fontfile.readuint16()
        valueformat = self.fontfile.readuint16()
        valuecount = self.fontfile.readuint16()
        self.valuerecords = []
        for _ in range(valuecount):
            self.valuerecords.append(self.fontfile.readvaluerecord(valueformat))
        self.coverage = Coverage(self.covofst+self.ofst, self.fontfile)
        self.fontfile.seek(fileptr)  # Put file pointer back

    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        ''' Get dx, dy, dxadvance for the glyph '''
        adjusts: list[PositionDelta] = []

        for gid in glyphids:
            if (covidx := self.coverage.covidx(gid) is not None):
                pos = PositionDelta(
                    self.valuerecords[covidx].get('x', 0),
                    self.valuerecords[covidx].get('y', 0),
                    self.valuerecords[covidx].get('xadvance', 0))
                logging.debug('Positioning glyph %s: (%s, %s, %s)',
                              gid, pos.dx, pos.dy, pos.dadvance)

            else:
                pos = PositionDelta(0, 0, 0)
            adjusts.append(pos)
        return adjusts


class PairAdjustmentSubtable(GposSubtable):
    ''' Pair Adjustment Table (GPOS Lookup Type 2)
        Informs kerning between pairs of glyphs
    '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile
        fileptr = self.fontfile.tell()

        self.fontfile.seek(self.ofst)
        self.posformat = self.fontfile.readuint16()
        self.covofst = self.fontfile.readuint16()
        self.valueformat1 = self.fontfile.readuint16()
        self.valueformat2 = self.fontfile.readuint16()

        if self.posformat == 1:
            pairsetcount = self.fontfile.readuint16()
            pairsetofsts = []
            for i in range(pairsetcount):
                pairsetofsts.append(self.fontfile.readuint16())

            PairValue = namedtuple('PairValue', ['secondglyph', 'value1', 'value2'])
            
            self.pairsets = []
            for i in range(pairsetcount):
                self.fontfile.seek(pairsetofsts[i] + self.ofst)
                paircnt = self.fontfile.readuint16()
                pairs = []
                for p in range(paircnt):
                    pairs.append(PairValue(
                        self.fontfile.readuint16(),
                        self.fontfile.readvaluerecord(self.valueformat1),
                        self.fontfile.readvaluerecord(self.valueformat2)))
                self.pairsets.append(pairs)

        elif self.posformat == 2:
            classdef1ofst = self.fontfile.readuint16()
            classdef2ofst = self.fontfile.readuint16()
            class1cnt = self.fontfile.readuint16()
            class2cnt = self.fontfile.readuint16()

            self.classrecords = []
            for i in range(class1cnt):
                class2recs = []
                for j in range(class2cnt):
                    class2recs.append(
                        (self.fontfile.readvaluerecord(self.valueformat1),
                         self.fontfile.readvaluerecord(self.valueformat2)))
                self.classrecords.append(class2recs)

            self.class1def = ClassDef(self.ofst + classdef1ofst, self.fontfile)
            self.class2def = ClassDef(self.ofst + classdef2ofst, self.fontfile)

        else:
            raise ValueError('Invalid posformat in PairAdjustmentSubtable')

        self.coverage = Coverage(self.covofst+self.ofst, self.fontfile)
        self.fontfile.seek(fileptr)  # Put file pointer back

    def get_adjust(self, glyph1: int, glyph2: int) -> tuple[Optional[dict], Optional[dict]]:
        ''' Get kerning adjustment for glyph1 and glyph2 pair '''
        v1 = v2 = None

        # Look up first glyph in coverage table
        covidx = self.coverage.covidx(glyph1)
        if covidx is not None:

            # Look up second glyph
            if self.posformat == 1:
                for p in self.pairsets[covidx]:
                    if p.secondglyph == glyph2:
                        v1 = p.value1
                        v2 = p.value2
                        break

            else:
                c1 = self.class1def.get_class(glyph1)
                c2 = self.class2def.get_class(glyph2)
                if c1 is not None and c2 is not None:
                    v1, v2 = self.classrecords[c1][c2]

        return v1, v2

    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        ''' Get dx, dy, dxadvance for the glyph '''
        deltas: list[PositionDelta] = [PositionDelta(0,0,0)]
        valuerec1 = valuerec2 = None
        for gid, gid0 in zip(glyphids[1:], glyphids[:-1]):
            covidx = self.coverage.covidx(gid0)
            if covidx is None:
                deltas.append(PositionDelta(0, 0, 0))
            else:
                if self.posformat == 1:
                    for p in self.pairsets[covidx]:
                        if p.secondglyph == gid:
                            valuerec1 = p.value1
                            valuerec2 = p.value2
                            break
                else:
                    c1 = self.class1def.get_class(gid0)
                    c2 = self.class2def.get_class(gid)
                    if c1 is not None and c2 is not None:
                        valuerec1, valuerec2 = self.classrecords[c1][c2]

                deltas[-1] = merge_delta(deltas[-1], valuerec_to_delta(valuerec1))
                deltas.append(valuerec_to_delta(valuerec2))

        return deltas

    def __repr__(self):
        return f'<PairAdjustmentSubtable {hex(self.ofst)}>'


def read_markarray_table(ofst, fontfile):
    ''' Read MarkArray table from font file '''
    cnt = fontfile.readuint16(ofst)
    MarkRecord = namedtuple('MarkRecord', ['markclass', 'anchortable'])
    markrecords = []
    for _ in range(cnt):
        markclass = fontfile.readuint16()
        anchorofst = fontfile.readuint16()
        ptr = fontfile.tell()
        anchortable = read_anchortable(ofst+anchorofst, fontfile)
        markrecords.append(MarkRecord(markclass, anchortable))
        ptr = fontfile.seek(ptr)
    return markrecords


def read_anchortable(ofst, fontfile):
    ''' Read anchor table from font file '''
    Anchor = namedtuple('Anchor', ['x', 'y', 'anchorpoint', 'xofst', 'yofst'])
    fmt = fontfile.readuint16(ofst)
    point = None
    xofst = yofst = None
    x = fontfile.readint16()
    y = fontfile.readint16()
    if fmt == 2:
        point = fontfile.readuint16()
    elif fmt == 3:
        xofst = fontfile.readuint16()
        yofst = fontfile.readuint16()
        logging.warning('Anchor references Device Table - unimplemented')
    return Anchor(x, y, point, xofst, yofst)


def read_basearray(ofst, fontfile, markclasscount):
    ''' Read BaseArray table used by Mark-to-Base Lookup '''
    basecnt = fontfile.readuint16(ofst)
    basearray = []
    for i in range(basecnt):
        anchortables = []
        for j in range(markclasscount):
            baseanchorofst = fontfile.readuint16()
            ptr = fontfile.tell()
            if baseanchorofst == 0:
                anchortables.append(None)
            else:
                anchortables.append(read_anchortable(
                    ofst+baseanchorofst, fontfile))
            fontfile.seek(ptr)
        basearray.append(anchortables)
    return basearray


class MarkToBaseSubtable(GposSubtable):
    ''' Mark-To-Base Positioning Table (GPOS Lookup Type 4) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile

        self.fmt = self.fontfile.readuint16(self.ofst)
        assert self.fmt == 1
        markcovofst = self.fontfile.readuint16()
        basecovofst = self.fontfile.readuint16()
        markclasscnt = self.fontfile.readuint16()
        markarrayofst = self.fontfile.readuint16()
        basearrayofst = self.fontfile.readuint16()

        self.markarray = read_markarray_table(self.ofst+markarrayofst, self.fontfile)
        self.basearray = read_basearray(self.ofst+basearrayofst, self.fontfile, markclasscnt)
        self.markcoverage = Coverage(self.ofst+markcovofst, self.fontfile)
        self.basecoverage = Coverage(self.ofst+basecovofst, self.fontfile)

    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        ''' Get dx, dy, dxadvance for the glyph '''
        deltas: list[PositionDelta] = [PositionDelta(0,0,0)]
        for i, (gid, gid0) in enumerate(zip(glyphids[1:], glyphids[:-1])):
            markid = self.markcoverage.covidx(gid)
            baseid = self.basecoverage.covidx(gid0)
            if markid is None or baseid is None:
                deltas.append(PositionDelta(0, 0, 0))
            else:
                markanchor = self.markarray[markid]
                baseanchor = self.basearray[baseid][markanchor.markclass]
                if baseanchor is None:
                    deltas.append(PositionDelta(0, 0, 0))
                else:
                    dx = baseanchor.x - markanchor.anchortable.x - advances[i]
                    dy = baseanchor.y - markanchor.anchortable.y
                    deltas.append(PositionDelta(dx, dy, -dx))
                    logging.debug('Positioning Mark %s on Base %s: (%s, %s)',
                                  gid, gid0, dx, dy)

        return deltas


class MarkToMarkSubtable(GposSubtable):
    ''' Mark-To-Mark Positioning Table (GPOS Lookup Type 6) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile

        self.fmt = self.fontfile.readuint16(self.ofst)
        assert self.fmt == 1
        mark1covofst = self.fontfile.readuint16()
        mark2covofst = self.fontfile.readuint16()
        markclasscnt = self.fontfile.readuint16()
        mark1arrayofst = self.fontfile.readuint16()
        mark2arrayofst = self.fontfile.readuint16()

        mark2count = self.fontfile.readuint16(self.ofst+mark2arrayofst)
        self.mark2array = []
        for i in range(mark2count):
            anchorofsts = []
            for j in range(markclasscnt):
                anchorofsts.append(self.fontfile.readuint16())
            anchortables = []
            ptr = self.fontfile.tell()
            for anchorofst in anchorofsts:
                anchortables.append(read_anchortable(
                    self.ofst+mark2arrayofst+anchorofst,
                    self.fontfile))
            self.mark2array.append(anchortables)
            self.mark1array = read_markarray_table(
                self.ofst+mark1arrayofst, self.fontfile)
            self.fontfile.seek(ptr)

        self.mark1coverage = Coverage(
            self.ofst+mark1covofst, self.fontfile)
        self.mark2coverage = Coverage(
            self.ofst+mark2covofst, self.fontfile)

    def adjust(self, *glyphids: int, advances: list[int], lookups: list[GposLookup]) -> list[PositionDelta]:
        ''' Get dx, dy, dxadvance for the glyph '''
        deltas: list[PositionDelta] = [PositionDelta(0,0,0)]
        for i, (gid, gid0) in enumerate(zip(glyphids[1:], glyphids[:-1])):
            mark1id = self.mark1coverage.covidx(gid)
            mark2id = self.mark2coverage.covidx(gid0)
            if mark1id is None or mark2id is None:
                deltas.append(PositionDelta(0, 0, 0))
            else:
                mark1anchor = self.mark1array[mark1id]
                mark2anchor = self.mark2array[mark2id][mark1anchor.markclass]
                if mark2anchor is None:
                    deltas.append(PositionDelta(0, 0, 0))
                else:
                    dx = mark2anchor.x - mark1anchor.anchortable.x - advances[i]
                    dy = mark2anchor.y - mark1anchor.anchortable.y
                    deltas.append(PositionDelta(dx, dy, -dx))
                    logging.debug('Positioning Mark %s on Mark %s: (%s, %s)',
                                  gid, gid0, dx, dy)

        return deltas
