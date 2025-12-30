''' Read Math Table from Open Type Font file

    Reference: https://docs.microsoft.com/en-us/typography/opentype/spec/math
'''

from __future__ import annotations
from typing import Union, Sequence, Optional, TYPE_CHECKING
from collections import namedtuple
from dataclasses import dataclass
import xml.etree.ElementTree as ET

from ziafont.gpos import Coverage
from ziafont.fontread import FontReader
from ziafont.glyph import SimpleGlyph, CompoundGlyph
from ziafont.fonttypes import BBox

if TYPE_CHECKING:
    from .mathfont import MathFont


GlyphType = Union[SimpleGlyph, CompoundGlyph]

MathKernInfoRecord = namedtuple(
    'MathKernInfoRecord', ['topright', 'topleft', 'bottomright', 'bottomleft'])
GlyphPartRecord = namedtuple(
    'GlyphPartRecord', ['glyphId', 'startConnectorLength', 'endConnectorLength',
                        'fullAdvance', 'partFlags'])


def read_valuerecord(fontfile: FontReader) -> int:
    ''' Read a Math Value Record. deviceOffset is ignored. '''
    value = fontfile.readint16()
    fontfile.readint16()  # ignore
    return value


@dataclass
class MathConstants:
    ''' Data from the Math Constants Table '''
    scriptPercentScaleDown: int
    scriptScriptPercentScaleDown: int
    delimitedSubFormulaMinHeight: int
    displayOperatorMinHeight: int
    mathLeading: int
    axisHeight: int
    accentBaseHeight: int
    flattenedAccentBaseHeight: int
    subscriptShiftDown: int
    subscriptTopMax: int
    subscriptBaselineDropMin: int
    superscriptShiftUp: int
    superscriptShiftUpCramped: int
    superscriptBottomMin: int
    superscriptBaselineDropMax: int
    subSuperscriptGapMin: int
    superscriptBottomMaxWithSubscript: int
    spaceAfterScript: int
    upperLimitGapMin: int
    upperLimitBaselineRiseMin: int
    lowerLimitGapMin: int
    lowerLimitBaselineDropMin: int
    stackTopShiftUp: int
    stackTopDisplayStyleShiftUp: int
    stackBottomShiftDown: int
    stackBottomDisplayStyleShiftDown: int
    stackGapMin: int
    stackDisplayStyleGapMin: int
    stretchStackTopShiftUp: int
    stretchStackBottomShiftDown: int
    stretchStackGapAboveMin: int
    stretchStackGapBelowMin: int
    fractionNumeratorShiftUp: int
    fractionNumeratorDisplayStyleShiftUp: int
    fractionDenominatorShiftDown: int
    fractionDenominatorDisplayStyleShiftDown: int
    fractionNumeratorGapMin: int
    fractionNumDisplayStyleGapMin: int
    fractionRuleThickness: int
    fractionDenominatorGapMin: int
    fractionDenomDisplayStyleGapMin: int
    skewedFractionHorizontalGap: int
    skewedFractionVerticalGap: int
    overbarVerticalGap: int
    overbarRuleThickness: int
    overbarExtraAscender: int
    underbarVerticalGap: int
    underbarRuleThickness: int
    underbarExtraDescender: int
    radicalVerticalGap: int
    radicalDisplayStyleVerticalGap: int
    radicalRuleThickness: int
    radicalExtraAscender: int
    radicalKernBeforeDegree: int
    radicalKernAfterDegree: int
    radicalDegreeBottomRaisePercent: int


class MathTable:
    ''' OpenType Font MATH Table, provides font-specific kerning adjustments and
        glyph variants for math type setting.

        Args:
            font: Math Font
    '''
    def __init__(self, font: 'MathFont'):
        self.font = font
        self.ofst = font.tables['MATH'].offset
        self.fontfile = self.font.fontfile
        self.fontfile.seek(self.ofst)
        self.vermajor = self.fontfile.readuint16()
        self.verminor = self.fontfile.readuint16()
        assert self.vermajor == 1
        constsofst = self.fontfile.readuint16()
        glyphofst = self.fontfile.readuint16()
        variantsofst = self.fontfile.readuint16()
        self._readconsts(constsofst)
        self._readglyphinfo(glyphofst)
        self._readvariants(variantsofst)

    def _readconsts(self, ofst: int) -> None:
        ''' Read math constants table '''
        self.fontfile.seek(self.ofst + ofst)
        self.consts = MathConstants(
            scriptPercentScaleDown=self.fontfile.readint16(),
            scriptScriptPercentScaleDown=self.fontfile.readint16(),
            delimitedSubFormulaMinHeight=self.fontfile.readuint16(),
            displayOperatorMinHeight=self.fontfile.readuint16(),
            mathLeading=read_valuerecord(self.fontfile),
            axisHeight=read_valuerecord(self.fontfile),
            accentBaseHeight=read_valuerecord(self.fontfile),
            flattenedAccentBaseHeight=read_valuerecord(self.fontfile),
            subscriptShiftDown=read_valuerecord(self.fontfile),
            subscriptTopMax=read_valuerecord(self.fontfile),
            subscriptBaselineDropMin=read_valuerecord(self.fontfile),
            superscriptShiftUp=read_valuerecord(self.fontfile),
            superscriptShiftUpCramped=read_valuerecord(self.fontfile),
            superscriptBottomMin=read_valuerecord(self.fontfile),
            superscriptBaselineDropMax=read_valuerecord(self.fontfile),
            subSuperscriptGapMin=read_valuerecord(self.fontfile),
            superscriptBottomMaxWithSubscript=read_valuerecord(self.fontfile),
            spaceAfterScript=read_valuerecord(self.fontfile),
            upperLimitGapMin=read_valuerecord(self.fontfile),
            upperLimitBaselineRiseMin=read_valuerecord(self.fontfile),
            lowerLimitGapMin=read_valuerecord(self.fontfile),
            lowerLimitBaselineDropMin=read_valuerecord(self.fontfile),
            stackTopShiftUp=read_valuerecord(self.fontfile),
            stackTopDisplayStyleShiftUp=read_valuerecord(self.fontfile),
            stackBottomShiftDown=read_valuerecord(self.fontfile),
            stackBottomDisplayStyleShiftDown=read_valuerecord(self.fontfile),
            stackGapMin=read_valuerecord(self.fontfile),
            stackDisplayStyleGapMin=read_valuerecord(self.fontfile),
            stretchStackTopShiftUp=read_valuerecord(self.fontfile),
            stretchStackBottomShiftDown=read_valuerecord(self.fontfile),
            stretchStackGapAboveMin=read_valuerecord(self.fontfile),
            stretchStackGapBelowMin=read_valuerecord(self.fontfile),
            fractionNumeratorShiftUp=read_valuerecord(self.fontfile),
            fractionNumeratorDisplayStyleShiftUp=read_valuerecord(self.fontfile),
            fractionDenominatorShiftDown=read_valuerecord(self.fontfile),
            fractionDenominatorDisplayStyleShiftDown=read_valuerecord(self.fontfile),
            fractionNumeratorGapMin=read_valuerecord(self.fontfile),
            fractionNumDisplayStyleGapMin=read_valuerecord(self.fontfile),
            fractionRuleThickness=read_valuerecord(self.fontfile),
            fractionDenominatorGapMin=read_valuerecord(self.fontfile),
            fractionDenomDisplayStyleGapMin=read_valuerecord(self.fontfile),
            skewedFractionHorizontalGap=read_valuerecord(self.fontfile),
            skewedFractionVerticalGap=read_valuerecord(self.fontfile),
            overbarVerticalGap=read_valuerecord(self.fontfile),
            overbarRuleThickness=read_valuerecord(self.fontfile),
            overbarExtraAscender=read_valuerecord(self.fontfile),
            underbarVerticalGap=read_valuerecord(self.fontfile),
            underbarRuleThickness=read_valuerecord(self.fontfile),
            underbarExtraDescender=read_valuerecord(self.fontfile),
            radicalVerticalGap=read_valuerecord(self.fontfile),
            radicalDisplayStyleVerticalGap=read_valuerecord(self.fontfile),
            radicalRuleThickness=read_valuerecord(self.fontfile),
            radicalExtraAscender=read_valuerecord(self.fontfile),
            radicalKernBeforeDegree=read_valuerecord(self.fontfile),
            radicalKernAfterDegree=read_valuerecord(self.fontfile),
            radicalDegreeBottomRaisePercent=self.fontfile.readint16())

    def _readglyphinfo(self, ofst: int) -> None:
        ''' Read glyph info table '''
        self.fontfile.seek(self.ofst + ofst)
        # Read table offsets
        italics = self.fontfile.readuint16()
        topaccent = self.fontfile.readuint16()
        extendshape = self.fontfile.readuint16()
        kernofst = self.fontfile.readuint16()

        # Italics table
        self.fontfile.seek(self.ofst + ofst + italics)
        covofst = self.fontfile.readuint16()
        cnt = self.fontfile.readuint16()
        italicscorrections = []
        for i in range(cnt):
            italicscorrections.append(read_valuerecord(self.fontfile))
        italicscoverage = Coverage(self.ofst+ofst+italics+covofst,
                                   self.fontfile, nulltable=(italics==0))

        # Top Accent Attachment Table
        self.fontfile.seek(self.ofst + ofst + topaccent)
        covofst = self.fontfile.readuint16()
        cnt = self.fontfile.readuint16()
        accents = []
        for i in range(cnt):
            accents.append(read_valuerecord(self.fontfile))
        accentcoverage = Coverage(
            self.ofst+ofst+topaccent+covofst, self.fontfile, nulltable=(topaccent==0))

        # Extended Shape Coverage
        extshapes = Coverage(
            self.ofst+ofst+extendshape, self.fontfile, nulltable=(extendshape==0))

        # Kern Info
        if kernofst:
            kerninfo = MathKernInfoTable(
                self.ofst+ofst+kernofst, self.fontfile, nulltable=(kernofst==0))
        else:
            kerninfo = None

        self.italicsCorrection = MathSubTable(italicscorrections, italicscoverage)
        self.topAccentAttachment = MathSubTable(accents, accentcoverage)
        self._extendedShapeCoverage = extshapes
        self.kernInfo = kerninfo

    def _readvariants(self, ofst: int) -> None:
        ''' Read the variants table '''
        self.fontfile.seek(self.ofst + ofst)
        minoverlap = self.fontfile.readuint16()
        vertcovofst = self.fontfile.readuint16()
        horzcovofst = self.fontfile.readuint16()
        vertcount = self.fontfile.readuint16()
        horzcount = self.fontfile.readuint16()

        vertConstruction = []
        for i in range(vertcount):
            vofst = self.fontfile.readuint16()
            vertConstruction.append(
                MathConstructionTable(self.ofst+ofst+vofst, self.font, vert=True))
        horzConstruction = []
        for i in range(horzcount):
            hofst = self.fontfile.readuint16()
            horzConstruction.append(
                MathConstructionTable(self.ofst+ofst+hofst, self.font, vert=False))

        vertcoverage = Coverage(self.ofst + ofst + vertcovofst, self.fontfile)
        horzcoverage = Coverage(self.ofst + ofst + horzcovofst, self.fontfile)
        self._variantsvert = MathVariants(
            vertcoverage, vertConstruction, minoverlap, self.font, vert=True)
        self._variantshorz = MathVariants(
            horzcoverage, horzConstruction, minoverlap, self.font, vert=False)

    def kernsuper(self, glyph1: GlyphType, glyph2: GlyphType) -> tuple[int, int]:
        ''' Calculate superscript kerning between the two glyphs

            Args:
                glyph1: Last glyph in base
                glyph2: First glyph in superscript

            Returns:
                kern: Kerning shift to apply in x direction
                shift: Upward shift of superscript with respect to baseline
        '''
        if self.kernInfo is None:
            return 0, max(self.consts.superscriptShiftUp,
                          self.consts.superscriptBottomMin)

        glyph1_kern = self.kernInfo.glyph(glyph1.index)
        glyph2_kern2 = self.kernInfo.glyph(glyph2.index)

        # Extended shape, need to raise superscript up, but only if we're using
        # a variant
        if self._extendedShapeCoverage.covidx(glyph1.index) is not None:
            shiftup = glyph1.path.bbox.ymax - self.consts.superscriptShiftUp/2
        else:
            shiftup = self.consts.superscriptShiftUp

        height1 = shiftup + glyph2.path.bbox.ymin * self.consts.scriptPercentScaleDown/100
        height2 = glyph1.path.bbox.ymax - shiftup
        kern1 = kern2 = 0
        if glyph1_kern:
            kern1 += glyph1_kern.topright.getkern(height1)
            kern2 += glyph1_kern.topright.getkern(height2)
        if glyph2_kern2:
            kern1 += glyph2_kern2.bottomleft.getkern(height1)
            kern2 += glyph2_kern2.bottomleft.getkern(height2)
        return min(kern1, kern2), shiftup

    def kernsub(self, glyph1: GlyphType, glyph2: GlyphType) -> tuple[int, int]:
        ''' Calculate subscript kerning

            Args:
                glyph1: Last glyph in base
                glyph2: First glyph in subscript

            Returns:
                kern: Kerning shift to apply in x direction
                shift: Downward shift of subscript with respect to baseline
        '''
        if self.kernInfo is None:
            return 0, max(self.consts.subscriptTopMax,
                          self.consts.subscriptShiftDown)

        glyph1_kern = self.kernInfo.glyph(glyph1.index)
        glyph2_kern = self.kernInfo.glyph(glyph2.index)

        # Correction heights
        shiftdn = self.consts.subscriptShiftDown - glyph1.path.bbox.ymin
        height1 = -shiftdn + glyph2.path.bbox.ymax * self.consts.scriptPercentScaleDown/100
        height2 = glyph1.path.bbox.ymin + shiftdn
        kern1 = kern2 = 0
        if glyph1_kern:
            kern1 += glyph1_kern.bottomright.getkern(height1)
            kern2 += glyph1_kern.bottomright.getkern(height2)
        if glyph2_kern:
            kern1 += glyph2_kern.topleft.getkern(height1)
            kern2 += glyph2_kern.topleft.getkern(height2)
        return min(kern1, kern2), shiftdn

    def listvariants(self, glyphid: int, vert: bool = True) -> dict[int, int]:
        if vert:
            return self._variantsvert.listvariants(glyphid)
        return self._variantshorz.listvariants(glyphid)

    def variant(self, glyphid: int, height: float, vert: bool = True) -> GlyphType:
        ''' Get a height variant for the glyph

            glyphid: Glyph index
            height: Desired height of glyph in font units
            vert: Vertical variant or horizontal variant
        '''
        if vert:
            variant = self._variantsvert.getvariant(glyphid, height)
        else:
            variant = self._variantshorz.getvariant(glyphid, height)
        return variant

    def variant_minmax(self, glyphid: int, ymin: float, ymax: float,
                       vert: bool = True) -> GlyphType:
        ''' Get a height variant for the glyph that covers or exceeds the range (ymin, ymax)

            Args:
                glyphid: Glyph index
                ymin: Minimum y value to contain
                ymax: Maximum y value to contain
                vert: Vertical variant or horizontal variant
        '''
        if vert:
            variant = self._variantsvert.getvariant_minmax(glyphid, ymin=ymin, ymax=ymax)
        else:
            variant = self._variantshorz.getvariant_minmax(glyphid, ymin=ymin, ymax=ymax)
        return variant

    def isextended(self, glyphid: int) -> bool:
        ''' Determine if glyph is an extended shape (has stretchy variants) '''
        return self._extendedShapeCoverage.covidx(glyphid) is not None

    def topattachment(self, glyphid: int) -> Optional[float]:
        ''' Get x-position to align an accent over the given base glyph ''' 
        return self.topAccentAttachment.getvalue(glyphid)


class MathConstructionTable:
    ''' Math Construction Table, listing size variants for a glyph

        Args:
            ofst: Byte offset to table in font file
            font: Font
            vert: Vertical or horizontal variant
    '''
    def __init__(self, ofst: int, font: 'MathFont', vert: bool = True):
        fileptr = font.fontfile.tell()
        font.fontfile.seek(ofst)
        assemblyofst = font.fontfile.readuint16()
        varcount = font.fontfile.readuint16()
        self.variants = {}
        for i in range(varcount):
            varglyph = font.fontfile.readuint16()
            advmeas = font.fontfile.readuint16()
            self.variants[advmeas] = varglyph

        self.assembly: Optional[MathAssembly]
        if assemblyofst:
            self.assembly = MathAssembly(ofst+assemblyofst, font, vert=vert)
        else:
            self.assembly = None
        font.fontfile.seek(fileptr)


class AssembledGlyph(SimpleGlyph):
    ''' Assembled glyph from Math Assembly Table

        Args:
            index: glyph index
            glyphs: list of glyphs included in the assembly
            offsets: offset (either vertical or horizontal) for each
                glyph in the assembly
            vert: Vertical or horizontal assembly
            font: Font instance
    '''
    def __init__(self,
                 index: int,
                 glyphs: Sequence[GlyphType],
                 offsets: Sequence[float],
                 vert: bool,
                 font: 'MathFont'):
        self.index = index
        self.glyphs = glyphs
        self.offsets = offsets
        self.vert = vert

        if self.vert:
            xmin = min([g.path.bbox.xmin for g in glyphs])
            xmax = max([g.path.bbox.xmax for g in glyphs])
            ymin = int(glyphs[0].path.bbox.ymin + offsets[0])
            ymax = int(glyphs[-1].path.bbox.ymax + offsets[-1])
        else:
            xmin = int(glyphs[0].path.bbox.xmin)
            xmax = int(glyphs[-1].path.bbox.xmax + offsets[-1])
            ymin = min([g.path.bbox.ymin for g in glyphs])
            ymax = max([g.path.bbox.ymax for g in glyphs])
        bbox = BBox(xmin, xmax, ymin, ymax)
        self._xadvance = max([g.advance() for g in glyphs])
        super().__init__(index, [], bbox, font)

    def advance(self, nextchr=None) -> int:
        ''' X-advance '''
        if self.vert:
            return self._xadvance
        else:
            return self.bbox.xmax

    def svgpath(self, x0: float = 0, y0: float = 0,
                scale_factor: float = 1) -> Optional[ET.Element]:
        ''' Get svg <path> element for glyph, normalized to 12-point font '''
        element = ET.Element('g')

        for glyph, ofst in zip(self.glyphs, self.offsets):
            path = ''
            for operator in glyph.operators:
                if self.vert:
                    operator = operator.xform(1, 0, 0, 1, 0, ofst, 1, 1)
                else:
                    operator = operator.xform(1, 0, 0, 1, ofst, 0, 1, 1)
                segment = operator.path(x0, y0, scale=self.funits_to_points(1, scale_factor))
                if segment[0] == 'M' and path != '':
                    path += 'Z '  # Close intermediate segments
                path += segment
            if path == '':
                continue  # Don't add empty path
            path += 'Z '
            element.append(ET.Element('path', attrib={'d': path}))
        return element


class MathAssembly:
    ''' Math assembly table, for combining several glyphs to extend the size
        beyond the font built-in glyphs (for example, making a really big
        curly brace)

        Args:
            ofst: Byte offset into font file
            font: Font
            vert: Vertical or horizontal variant
    '''
    def __init__(self, ofst: int, font: 'MathFont', vert: bool = True):
        self.vert = vert
        self.font = font
        font.fontfile.seek(ofst)
        self.italicscorrection = read_valuerecord(font.fontfile)
        partcnt = font.fontfile.readuint16()
        self.parts = []
        for i in range(partcnt):
            self.parts.append(GlyphPartRecord(
                font.fontfile.readuint16(),
                font.fontfile.readuint16(),
                font.fontfile.readuint16(),
                font.fontfile.readuint16(),
                font.fontfile.readuint16()))

    def assemble(self, reqsize: float, minoverlap: float) -> AssembledGlyph:
        ''' Build glyph assembly, combining parts to create any required size

            Args:
                reqsize: Desired glyph size
                minoverlap: Minimum overlap from variants table
        '''
        size = 0.
        num_extenders = 0

        # Determine number of extender parts needed.
        while size < reqsize:
            # Min overlap give largest size with this many extenders

            testparts = []
            for part in self.parts:
                if part.partFlags:
                    testparts.extend([part]*num_extenders)
                else:
                    testparts.append(part)

            y = 0.
            for i, part in enumerate(testparts):
                if i > 0:
                    y -= minoverlap
                y += part.fullAdvance
            size = y
            num_extenders += 1

        # Decrease overlap since full extenders make it too tall
        try:
            dy = (size - reqsize) / (len(testparts)-1)
        except ZeroDivisionError:
            dy = (size - reqsize)

        # Build transforms for compound glyph
        offsets = []
        if self.vert:
            y = -reqsize/2 + self.font.math.consts.axisHeight
        else:
            y = 0.
        for i, part in enumerate(testparts):
            if i > 0:
                y -= minoverlap + dy
            if self.vert:
                offsets.append(y - self.font.glyph_fromid(part.glyphId).bbox.ymin)
            else:
                offsets.append(y)
            y += part.fullAdvance

        # Put together the CompoundGlyph
        glyphs = [self.font.glyph_fromid(part.glyphId) for part in testparts]

        # Make a unique ID, negative so it can't clash with other glyphs
        glyfid = -(testparts[0].glyphId + int(reqsize) << 16)
        return AssembledGlyph(glyfid, glyphs, offsets, vert=self.vert, font=self.font)


class MathVariants:
    ''' Math Variants Table. Provides different glyphs for different size symbols,
        such as curly braces and square roots.
    '''
    def __init__(self, coverage: Coverage, construction: Sequence[MathConstructionTable],
                 minoverlap: float, font: 'MathFont', vert: bool):
        self.coverage = coverage
        self.construction = construction
        self.minoverlap = minoverlap
        self.font = font
        self.vert = vert

    def listvariants(self, glyphid: int) -> dict[int, int]:
        ''' List all size variants '''
        covidx = self.coverage.covidx(glyphid)
        if covidx is None:
            return {}

        construction = self.construction[covidx]
        return construction.variants

    def getvariant(self, glyphid: int, size: float) -> GlyphType:
        ''' Get the proper size variant for the glyphid '''
        glf: GlyphType
        covidx = self.coverage.covidx(glyphid)
        if covidx is None:
            # Not covered by a variant
            return self.font.glyph_fromid(glyphid)

        construction = self.construction[covidx]
        variants = construction.variants
        try:
            variantid = variants[min(k for k in variants if k >= size)]

        except ValueError:
            # size is bigger than all variants. Use assembly table.
            if construction.assembly:
                glf = construction.assembly.assemble(size, self.minoverlap)
            else:
                glf = self.font.glyph_fromid(variants[max(variants.keys())])
        else:
            glf = self.font.glyph_fromid(variantid)

        return glf

    def getvariant_minmax(self, glyphid: int, ymin: float, ymax: float) -> GlyphType:
        ''' Get the smallest variant that encloses ymin and ymax '''
        glf: GlyphType
        covidx = self.coverage.covidx(glyphid)
        if covidx is None:
            # Not covered by a variant
            return self.font.glyph_fromid(glyphid)

        construction = self.construction[covidx]
        variants = construction.variants

        gids = list(variants.values())
        ymins = [self.font.glyph_fromid(gid).bbox.ymin for gid in gids]
        ymaxs = [self.font.glyph_fromid(gid).bbox.ymax for gid in gids]
        for gid, ymn, ymx in zip(gids, ymins, ymaxs):
            if ymn <= ymin and ymx >= ymax:
                glf = self.font.glyph_fromid(gid)
                break
        else:
            height = ymax-ymin
            if height > ymaxs[-1] - ymins[-1] and construction.assembly:
                if self.vert:
                    height = max(
                        -2*(ymin+self.font.math.consts.axisHeight),
                        2*(ymax-self.font.math.consts.axisHeight))
                glf = construction.assembly.assemble(height, self.minoverlap)
            else:
                glf = self.font.glyph_fromid(gids[-1])
        return glf


class MathKernTable:
    ''' Math Kerning Table, for adjusting sub/superscripts

        Args:
            ofst: Byte offset into font file
            fontfile: font file
    '''
    def __init__(self, ofst: int, fontfile: FontReader):
        fileptr = fontfile.tell()
        fontfile.seek(ofst)
        heightcnt = fontfile.readuint16()
        self.heights = []
        for i in range(heightcnt):
            self.heights.append(read_valuerecord(fontfile))
        self.kernvalues = []
        for i in range(heightcnt+1):
            self.kernvalues.append(read_valuerecord(fontfile))
        fontfile.seek(fileptr)

    def getkern(self, height: float) -> int:
        ''' Get kerning for this height '''
        if len(self.heights) == 0:
            return self.kernvalues[0]

        for i, h in enumerate(self.heights):
            if h > height:
                break
        else:
            i += 1
        return self.kernvalues[i]


class ZeroKern:
    ''' A kerning table with 0 kerning '''
    def getkern(self, height: float) -> int:
        ''' Get kerning for this height '''
        return 0


class MathKernInfoTable:
    ''' Math Kerning Info Table, listing of MathKernTables

        Args:
            ofst: Byte offset into font file
            fontfile: Font File
    '''
    def __init__(self, ofst: int, fontfile: FontReader, nulltable: bool = False):
        if nulltable:
            self.kerninfo = None
            self.coverage = None
        else:
            fontfile.seek(ofst)
            covofst = fontfile.readuint16()
            cnt = fontfile.readuint16()
            self.kerninfo = []
            for i in range(cnt):
                tr = fontfile.readuint16()
                tl = fontfile.readuint16()
                br = fontfile.readuint16()
                bl = fontfile.readuint16()
                self.kerninfo.append(MathKernInfoRecord(
                    MathKernTable(tr+ofst, fontfile) if tr else ZeroKern(),
                    MathKernTable(tl+ofst, fontfile) if tl else ZeroKern(),
                    MathKernTable(br+ofst, fontfile) if br else ZeroKern(),
                    MathKernTable(bl+ofst, fontfile) if bl else ZeroKern()))
            self.coverage = Coverage(ofst+covofst, fontfile)

    def glyph(self, glyphid: int) -> Optional[MathKernInfoRecord]:
        ''' Get kerning info record for this glyph '''
        if self.coverage is None:
            return None

        idx = self.coverage.covidx(glyphid)
        if idx is not None:
            return self.kerninfo[idx]
        return None


class MathSubTable:
    ''' Math Sub Table - generic list of values associated with glyphs '''
    def __init__(self, values: Sequence[float], coverage: Coverage):
        self.values = values
        self.coverage = coverage

    def getvalue(self, glyphid: int) -> Optional[float]:
        ''' Get a value from the table for the glyph '''
        idx = self.coverage.covidx(glyphid)
        if idx is not None:
            return self.values[idx]
        return None
