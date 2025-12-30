''' Glyph Substitution (GSUB) tables '''

from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from collections import namedtuple
import random
import logging

from .tables import Script, Feature, Coverage, Language, ClassDef, ClassDefBlank

if TYPE_CHECKING:
    from .fontread import FontReader


ChainedSeqRule = namedtuple('ChainedSeqRule', ['backtrack', 'input', 'lookahead', 'sequence'])
SequenceLookupRecord = namedtuple('SequenceLookupRecord', ['sequenceindex', 'lookupindex'])


# Features that cant' be turned off
PERM_FEATURES = ['ccmp', 'locl', 'rlig', 'rvrn', 'rclt']

# Features that are on by default
ON_FEATURES = ['calt', 'cpsp', 'clig', 'liga', 'rand']


class LookupSubtable:
    ''' Generic/unimplemented GSUB Lookup Sub Table '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.ofst = ofst
        self.fontfile = fontfile

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        logging.debug('Glyph substitution from unimplemented GSUB subtable type %s', self.ofst)
        return glyphids


class LookupSingleSub1(LookupSubtable):
    ''' GSUB Single Glyph Substitution  (LookupType 1, format 1) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.fmt = fontfile.readuint16(ofst)
        assert self.fmt == 1
        covofst = fontfile.readuint16()
        self.deltagid = fontfile.readint16()
        self.covtable = Coverage(ofst + covofst, fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        for i in range(len(glyphids)):
            covidx = self.covtable.covidx(glyphids[i])
            if covidx is not None:
                glyphids[i] += self.deltagid
        return glyphids


class LookupSingleSub2(LookupSubtable):
    ''' GSUB Single Glyph Substitution  (LookupType 1, format 2) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.fmt = fontfile.readuint16(ofst)
        assert self.fmt == 2
        covofst = fontfile.readuint16()
        glyphcount = fontfile.readuint16()
        self.subglyphids = []
        for _ in range(glyphcount):
            self.subglyphids.append(fontfile.readuint16())
        self.covtable = Coverage(ofst + covofst, fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str]=None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        for i in range(len(glyphids)):
            covidx = self.covtable.covidx(glyphids[i])
            if covidx is not None:
                glyphids[i] = self.subglyphids[covidx]
        return glyphids


class LookupMultipleSub(LookupSubtable):
    ''' GSUB Multiple Glyph Substitution  (LookupType 2) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.fmt = fontfile.readuint16(ofst)
        assert self.fmt == 1
        covofst = fontfile.readuint16()
        seqcount = fontfile.readuint16()
        seqofsts = []
        for _ in range(seqcount):
            seqofsts.append(fontfile.readuint16())
        self.subglyphids = []
        for seqofst in seqofsts:
            glyphcnt = fontfile.readuint16(ofst+seqofst)
            subglyphs = []
            for _ in range(glyphcnt):
                subglyphs.append(fontfile.readuint16())
            self.subglyphids.append(subglyphs)

        self.covtable = Coverage(ofst + covofst, fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        newglyphids = []
        for gid in glyphids:
            covidx = self.covtable.covidx(gid)
            if covidx is not None:
                newglyphids.extend(self.subglyphids[covidx])
            else:
                newglyphids.append(gid)
        return newglyphids


class LookupAlternate(LookupSubtable):
    ''' GSUB Alternate Glyph Substitution  (LookupType 3) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.fmt = fontfile.readuint16(ofst)
        assert self.fmt == 1
        covofst = fontfile.readuint16()
        cnt = fontfile.readuint16()
        altofsts = []
        for i in range(cnt):
            altofsts.append(fontfile.readuint16())
        self.altglyphs = []
        for altofst in altofsts:
            cnt = self.fontfile.readuint16(ofst+altofst)
            gids = []
            for i in range(cnt):
                gids.append(self.fontfile.readuint16())
            self.altglyphs.append(gids)
        self.covtable = Coverage(ofst + covofst, fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        for i, gid in enumerate(glyphids):
            covidx = self.covtable.covidx(gid)
            if covidx is not None:
                if name == 'rand':
                    glyphids[i] = random.choice(self.altglyphs[covidx])
                else:
                    altgids = self.altglyphs[covidx]
                    # TODO - user choice! return first one for now.
                    glyphids[i] = altgids[0]

        return glyphids


class LookupLigatureSub(LookupSubtable):
    ''' Ligature Substitution Subtable (LookupType 4) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.ofst = ofst
        self.fontfile = fontfile
        fmt = fontfile.readuint16(self.ofst)
        assert fmt == 1
        covofst = self.fontfile.readuint16()
        cnt = self.fontfile.readuint16()
        ligsetofsts = []
        for _ in range(cnt):
            ligsetofsts.append(self.fontfile.readuint16())

        self.ligsets = []
        for ofst in ligsetofsts:
            ofst = ofst + self.ofst
            cnt = self.fontfile.readuint16(ofst)
            ligofsts = []
            for _ in range(cnt):
                ligofsts.append(self.fontfile.readuint16())

            ligs = {}
            for ligofst in ligofsts:
                ligglyph = self.fontfile.readuint16(ofst+ligofst)
                compcount = self.fontfile.readuint16()
                compglyphs = []
                for _ in range(compcount-1):
                    compglyphs.append(self.fontfile.readuint16())
                ligs[tuple(compglyphs)] = ligglyph
            self.ligsets.append(ligs)
        self.covtable = Coverage(self.ofst+covofst, self.fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        newgids = []
        i = 0
        while i < len(glyphids):
            gid = glyphids[i]
            covidx = self.covtable.covidx(gid)
            if covidx is not None:
                ligset = self.ligsets[covidx]
                for ls, subglyph in ligset.items():
                    if glyphids[i+1:i+1+len(ls)] == list(ls):
                        newgids.append(subglyph)
                        i += len(ls)+1
                        break
                else:  # nobreak
                    newgids.append(gid)
                    i += 1
            else:
                newgids.append(gid)
                i += 1
        return newgids


class LookupChainedSub3(LookupSubtable):
    ''' Chained Contexts Subtable (LookupType 6, format 3) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.ofst = ofst
        self.fontfile = fontfile
        self.fmt = self.fontfile.readuint16(self.ofst)
        assert self.fmt == 3

        backtrackcnt = self.fontfile.readuint16()
        backofsts = []
        for i in range(backtrackcnt):
            backofsts.append(self.fontfile.readuint16())
        inptcnt = self.fontfile.readuint16()
        inptofsts = []
        for i in range(inptcnt):
            inptofsts.append(self.fontfile.readuint16())
        lookcnt = self.fontfile.readuint16()
        lookofsts = []
        for i in range(lookcnt):
            lookofsts.append(self.fontfile.readuint16())
        seqlookupcnt = self.fontfile.readuint16()
        self.seqlookups = []
        for i in range(seqlookupcnt):
            self.seqlookups.append(SequenceLookupRecord(
                self.fontfile.readuint16(),
                self.fontfile.readuint16()))

        self.backCoverage = []
        for bofst in backofsts:
            self.backCoverage.append(Coverage(self.ofst+bofst, self.fontfile))
        self.inptCoverage = []
        for iofst in inptofsts:
            self.inptCoverage.append(Coverage(self.ofst+iofst, self.fontfile))
        self.lookaheadCoverage = []
        for lofst in lookofsts:
            self.lookaheadCoverage.append(Coverage(self.ofst+lofst, self.fontfile))

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        ilen = len(self.inptCoverage)
        i = len(self.backCoverage)
        while i < len(glyphids) - len(self.lookaheadCoverage) - ilen + 1:
            covidx = [cov.covidx(glyphids[i+k]) for k, cov in enumerate(self.inptCoverage)]
            if None in covidx:
                i += 1
                continue
            covidx = [cov.covidx(glyphids[i-k-1]) for k, cov in enumerate(self.backCoverage)]
            if None in covidx:
                i += 1
                continue
            covidx = [cov.covidx(glyphids[i+ilen+k]) for k, cov in enumerate(self.lookaheadCoverage)]
            if None in covidx:
                i += 1
                continue

            # match!
            for seqlookup in self.seqlookups:
                glyphids[i+seqlookup.sequenceindex:i+1+ilen] = \
                    lookups[seqlookup.lookupindex].sub(glyphids[i:i+1+ilen], lookups)

            i += len(self.inptCoverage)

        return glyphids


class LookupChainedSub2(LookupSubtable):
    ''' Chained Contexts Subtable (LookupType 6, format 2) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.ofst = ofst
        self.fontfile = fontfile
        self.fmt = fontfile.readuint16(self.ofst)
        assert self.fmt == 2
        covofst = self.fontfile.readuint16()
        backtrackofst = self.fontfile.readuint16()
        inputofst = self.fontfile.readuint16()
        lookaheadofst = self.fontfile.readuint16()
        rulesetcnt = self.fontfile.readuint16()
        rulesetofsts = []
        for _ in range(rulesetcnt):
            rulesetofsts.append(self.fontfile.readuint16())

        self.rules: list[list[ChainedSeqRule]] = []
        for rulesetofst in rulesetofsts:
            if rulesetofst == 0:
                self.rules.append([])
                continue
            rulecnt = self.fontfile.readuint16(self.ofst+rulesetofst)
            ruleofsts = []
            for i in range(rulecnt):
                ruleofsts.append(self.fontfile.readuint16())

            ruleset = []
            for ruleofst in ruleofsts:
                backglyphcnt = self.fontfile.readuint16(self.ofst+rulesetofst+ruleofst)
                backseq = []
                for i in range(backglyphcnt):
                    backseq.append(self.fontfile.readuint16())
                inglyphcnt = self.fontfile.readuint16()
                inputseq = []
                for i in range(inglyphcnt-1):
                    inputseq.append(self.fontfile.readuint16())
                lookaheadglyphcnt = self.fontfile.readuint16()
                lookaheadseq = []
                for i in range(lookaheadglyphcnt):
                    lookaheadseq.append(self.fontfile.readuint16())
                seqlookupcnt = self.fontfile.readuint16()
                sequencelookup = []
                for i in range(seqlookupcnt):
                    sequencelookup.append(
                        SequenceLookupRecord(
                            self.fontfile.readuint16(),
                            self.fontfile.readuint16()))
                ruleset.append(
                    ChainedSeqRule(backseq, inputseq, lookaheadseq, sequencelookup))
            self.rules.append(ruleset)
        self.covtable = Coverage(self.ofst+covofst, self.fontfile)
        self.backtrackClass = ClassDef(self.ofst+backtrackofst, self.fontfile) if backtrackofst else ClassDefBlank(0, self.fontfile)
        self.inputClass = ClassDef(self.ofst+inputofst, self.fontfile) if inputofst else ClassDefBlank(0, self.fontfile)
        self.lookaheadClass = ClassDef(self.ofst+lookaheadofst, self.fontfile) if lookaheadofst else ClassDefBlank(0, self.fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        i = 0
        while i < len(glyphids):
            gid = glyphids[i]
            covidx = self.covtable.covidx(gid)
            if covidx is not None:
                classid = self.inputClass.get_class(gid)
                if classid is not None:
                    ruleset = self.rules[classid]
                    for rule in ruleset:
                        inpt = [self.inputClass.get_class(g)
                                for g in glyphids[i+1:i+1+len(rule.input)]]
                        if inpt != rule.input:
                            continue
                        backtrack = [self.backtrackClass.get_class(g)
                                     for g in glyphids[i-len(rule.backtrack):i]]
                        if backtrack[::-1] != rule.backtrack:  # Rule is reverse order
                            continue
                        aheadlen = len(rule.input) + len(rule.lookahead)
                        lookahead = [self.lookaheadClass.get_class(g)
                                     for g in glyphids[i+1+len(rule.input):i+1+aheadlen]]

                        if lookahead != rule.lookahead:
                            continue

                        # Match
                        for seqlookup in rule.sequence:
                            glyphids[i+seqlookup.sequenceindex:i+1+len(rule.input)] = \
                                lookups[seqlookup.lookupindex].sub(glyphids[i:i+1+len(rule.input)], lookups)
                i += 1
            else:
                i += 1
        return glyphids


class LookupChainedSub1(LookupSubtable):
    ''' Chained Contexts Subtable (LookupType 6, format 1) '''
    def __init__(self, ofst: int, fontfile: FontReader):
        super().__init__(ofst, fontfile)
        self.ofst = ofst
        self.fontfile = fontfile
        self.fmt = fontfile.readuint16(self.ofst)
        assert self.fmt == 1
        covofst = self.fontfile.readuint16()
        cnt = self.fontfile.readuint16()
        setofsts = []
        for i in range(cnt):
            setofsts.append(self.fontfile.readuint16())

        self.rules = []
        for setofst in setofsts:
            cnt = self.fontfile.readuint16(self.ofst+setofst)
            ruleofsts = []
            for _ in range(cnt):
                ruleofsts.append(self.fontfile.readuint16())
            ruleset = []
            for ruleofst in ruleofsts:
                backglyphcount = self.fontfile.readuint16(self.ofst+setofst+ruleofst)
                backtrackSeq = []
                for _ in range(backglyphcount):
                    backtrackSeq.append(self.fontfile.readuint16())
                inputglyphcount = self.fontfile.readuint16()
                inputSequence = []
                for _ in range(inputglyphcount-1):
                    inputSequence.append(self.fontfile.readuint16())
                lookaheadglyphcount = self.fontfile.readuint16()
                lookaheadSequence = []
                for _ in range(lookaheadglyphcount):
                    lookaheadSequence.append(self.fontfile.readuint16())
                seqlookupcnt = self.fontfile.readuint16()
                sequencelookup = []
                for _ in range(seqlookupcnt):
                    sequencelookup.append(SequenceLookupRecord(
                        self.fontfile.readuint16(),   # SequenceIndex
                        self.fontfile.readuint16()))  # LookupListIndex
                ruleset.append(ChainedSeqRule(
                    backtrackSeq, inputSequence, lookaheadSequence, sequencelookup))
            self.rules.append(ruleset)
        self.covtable = Coverage(self.ofst+covofst, self.fontfile)

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        i = 0
        while i < len(glyphids):
            gid = glyphids[i]
            covidx = self.covtable.covidx(gid)
            if covidx is not None:
                ruleset = self.rules[covidx]
                for rule in ruleset:
                    inpt = glyphids[i+1:i+1+len(rule.input)]
                    if inpt != rule.input:
                        i += 1
                        continue
                    backtrack = glyphids[i-len(rule.backtrack):i]
                    if backtrack[::-1] != rule.backtrack:  # Rule is reverse order
                        i += 1
                        continue
                    aheadlen = len(rule.input) + len(rule.lookahead)
                    lookahead = glyphids[i+1+len(rule.input):i+1+aheadlen]

                    if lookahead != rule.lookahead:
                        i += 1
                        continue

                    # Match
                    for seqlookup in rule.sequence:
                        glyphids[i+seqlookup.sequenceindex:i+1+len(rule.input)] = \
                            lookups[seqlookup.lookupindex].sub(glyphids[i:i+1+len(rule.input)], lookups)
                    i += len(rule.input)
            else:
                i += 1
        return glyphids


class GSUBLookup:
    ''' GSUB Lookup Table '''
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
        self.fmt = 1
        self.flag = self.fontfile.readuint16()
        subtablecnt = self.fontfile.readuint16()
        self.tableofsts = []
        for i in range(subtablecnt):
            self.tableofsts.append(self.fontfile.readuint16())
        self.markfilterset = None
        if self.flag & USE_MARK_FILTERING_SET:
            self.markfilterset = self.fontfile.readuint16()

        self.subtables: list[LookupSubtable] = []
        for i in range(subtablecnt):
            tblofst = self.ofst+self.tableofsts[i]
            self.fmt = self.fontfile.readuint16(tblofst)
            
            tabletype = self.type
            if self.type == 7:  # Extension Table - turns into another type
                tabletype = self.fontfile.readuint16()
                extofst = self.fontfile.readuint32()
                tblofst += extofst
                self.fmt = self.fontfile.readuint16(tblofst)

            if tabletype == 1:  # Single Substitution
                if self.fmt == 1:
                    self.subtables.append(LookupSingleSub1(tblofst, self.fontfile))
                else:
                    self.subtables.append(LookupSingleSub2(tblofst, self.fontfile))

            elif tabletype == 2:  # Multiple sub
                self.subtables.append(LookupMultipleSub(tblofst, self.fontfile))

            elif tabletype == 3:  # Alternates lookup
                self.subtables.append(LookupAlternate(tblofst, self.fontfile))

            elif tabletype == 4:  # Ligature sub
                self.subtables.append(LookupLigatureSub(tblofst, self.fontfile))

            elif tabletype == 6:  # Chained context sub
                if self.fmt == 1:
                    self.subtables.append(LookupChainedSub1(tblofst, self.fontfile))
                elif self.fmt == 2:
                    self.subtables.append(LookupChainedSub2(tblofst, self.fontfile))
                else:
                    self.subtables.append(LookupChainedSub3(tblofst, self.fontfile))
            else:
                logging.debug('Unimplemented GSUB Lookup Type %s', self.type)
                self.subtables.append(LookupSubtable(self.type, self.fontfile))

        self.fontfile.seek(fileptr)

    def __repr__(self):
        return f'<GSUBLookup Type {self.type}.{self.fmt}>'

    def sub(self, glyphids: list[int], lookups: list[GSUBLookup], name: Optional[str] = None) -> list[int]:
        ''' Apply glyph substitution to list of glyph ids '''
        glyphids = [g for g in glyphids]  # Make a copy
        for subtable in self.subtables:
            glyphids = subtable.sub(glyphids, lookups, name)
        return glyphids


class Gsub:
    ''' Glyph Substitution Table '''
    def __init__(self, ofst: int, fontfile: FontReader):
        self.fontfile = fontfile
        self.ofst = ofst
        self.language = Language()
        self.fontfile.seek(self.ofst)
        vermajor = self.fontfile.readuint16()
        verminor = self.fontfile.readuint16()
        scriptofst = self.fontfile.readuint16()
        featureofst = self.fontfile.readuint16()
        lookupofst = self.fontfile.readuint16()
        featurevariationsofst = None
        if verminor == 1:
            featurevariationsofst = self.fontfile.readuint32()
            logging.warning('GSUB has feature variations - unimplemented')

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
        self.featurelist = []
        if featureofst != 0:
            featurelisttableloc = self.ofst + featureofst
            featurecnt = self.fontfile.readuint16(featurelisttableloc)
            for i in range(featurecnt):
                self.featurelist.append(Feature(
                    self.fontfile.read(4).decode(),
                    self.fontfile.readuint16() + featurelisttableloc,
                    self.fontfile))

        # Read Lookups
        self.lookups = []
        if lookupofst != 0:
            lookuplisttableloc = self.ofst + lookupofst
            lookupcnt = self.fontfile.readuint16(lookuplisttableloc)
            for i in range(lookupcnt):
                self.lookups.append(GSUBLookup(
                    self.fontfile.readuint16() + lookuplisttableloc,
                    self.fontfile))

        # Put everything in a dictionary for access
        self.features = {}
        for scrname, script in self.scripts.items():
            langdict = {}
            for langname, lang in script.languages.items():
                langfeatures = [self.featurelist[i] for i in lang.featureidxs]
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

    def features_available(self) -> dict[str, list[GSUBLookup]]:
        ''' Dictionary of features available in the current script/language system '''
        return self.features.get(self.language.script, {}).get(self.language.language, {})

    def init_user_features(self) -> dict[str, bool]:
        ''' Initialize features that can be set by user '''
        avail = list(self.features_available().keys())
        avail = [feat for feat in avail if feat not in PERM_FEATURES]
        return {feat: feat in ON_FEATURES for feat in avail}

    def sub(self, glyphids: list[int], features: dict[str, bool]):
        ''' Apply glyph substitution to list of glyph ids. Features
            enable/disable certain substitutions.
        '''
        feattable = self.features_available()

        def apply_feature(name, glyphids):
            tables = feattable.get(name, [])
            for table in tables:
                newglyphids = table.sub(glyphids.copy(), self.lookups, name)
                if newglyphids != glyphids:
                    logging.debug('GSUB applied by feature %s in %s', name, table)
                glyphids = newglyphids
            return glyphids

        # Run permanent features first, in order defined by font
        for feat in feattable.keys():
            if feat in PERM_FEATURES:
                glyphids = apply_feature(feat, glyphids)

        # Then alernate/optional features, in order defined by font
        for feat in feattable.keys():
            if features.get(feat, False):
                glyphids = apply_feature(feat, glyphids)

        return glyphids
