''' Search system font paths for a font by name '''
from __future__ import annotations
from typing import Sequence, Optional
import os
import sys
import struct
from pathlib import Path

from .fonttypes import FontNames


FONTPATHS: list[Path]
_HOME = Path.home()

if sys.platform == 'win32':
    _WIN = Path(os.environ['WINDIR'])
    FONTPATHS = [
        _WIN.joinpath('Fonts')
    ]
else:
    FONTPATHS = [
        Path('/usr/share/fonts/'),
        Path('/usr/local/share/fonts/'),
        _HOME.joinpath('.local/share/fonts'),
        _HOME.joinpath('.fonts'),
    ]
    if sys.platform == 'darwin':
        FONTPATHS = [
            Path('/Library/Fonts/'),
            Path('/Network/Library/Fonts/'),
            Path('/System/Library/Fonts/'),
            Path('/opt/local/share/fonts'),
            _HOME.joinpath('Library/Fonts'),
        ] + FONTPATHS


def font_list(paths: Optional[Sequence[Path | str]] = None) -> list[Path]:
    ''' List all TTF and OTF files in system font paths '''
    if paths is None:
        searchpaths = FONTPATHS
    else:
        searchpaths = [Path(p) for p in paths] + FONTPATHS

    fontfiles = []
    for fontpath in searchpaths:
        for path, _, fnames in os.walk(fontpath):
            for fname in fnames:
                if fname.lower().endswith('.ttf') or fname.lower().endswith('.otf'):
                    fontfiles.append(Path(path, fname))
    return fontfiles


def readnames(path: Path) -> FontNames:
    ''' Quickly read NAME table from TTF without loading entire font '''
    with open(path, 'rb') as f:
        nameids = [''] * 15  # Empty strings for nameId table

        f.read(4)  # Skip scalartype
        try:
            numtables = struct.unpack('>H', f.read(2))[0]
        except struct.error:
            # empty/invalid font file
            return FontNames(*nameids)

        f.read(6)  # Skip searchrange, entrysel, rangeshift
        tableoffset = -1
        for i in range(numtables):
            try:
                tag = f.read(4).decode()
            except UnicodeDecodeError:
                return FontNames(*nameids)  # invalid font file
            else:
                if tag == 'name':
                    chksum = struct.unpack('>I', f.read(4))[0]
                    tableoffset = struct.unpack('>I', f.read(4))[0]
                    length = struct.unpack('>I', f.read(4))[0]
                    break
                else:
                    f.read(12) # Skip
        if tableoffset == -1:
            return FontNames(*nameids)  # invalid font file

        f.seek(tableoffset)
        namefmt = struct.unpack('>H', f.read(2))[0]
        count = struct.unpack('>H', f.read(2))[0]
        strofst = struct.unpack('>H', f.read(2))[0]

        namerecords = []
        for i in range(count):
            platformId = struct.unpack('>H', f.read(2))[0]
            platformSpecificId = struct.unpack('>H', f.read(2))[0]
            languageId = struct.unpack('>H', f.read(2))[0]
            nameId = struct.unpack('>H', f.read(2))[0]
            length = struct.unpack('>H', f.read(2))[0]
            offset = struct.unpack('>H', f.read(2))[0]
            namerecords.append((platformId, platformSpecificId, languageId,
                                nameId, length, offset))
        for record in namerecords:
            f.seek(tableoffset + strofst + record[5])
            name = f.read(record[4])
            if record[3] < 16:
                if record[0] in [0, 3]:  # Microsoft and Unicode formats
                    nameids[record[3]] = name.decode('utf-16be')

    return FontNames(*nameids)


def system_fonts(paths: Optional[Sequence[str | Path]] = None) -> dict[str | Path, Path]:
    ''' Get dictionary of fontname: fontpath for all system TTF/OTF fonts

        Args:
            paths: Additional paths to search
    '''
    fontdict = {}
    fontlist = font_list(paths)
    for f in fontlist:
        names = readnames(f)
        fontdict[names.name] = f

        if names.subfamily.lower() in ['regular', 'book', 'roman'] and names.family != names.name:
            fontdict[names.family] = f
        fontdict[f'{names.family}, {names.subfamily}'] = f
    return fontdict


def find_font(name: str | Path, paths: Optional[Sequence[str | Path]] = None) -> Optional[Path]:
    ''' Find a font's filename given the name defined in font file.
        Searches all TTF/OTF fonts in (os-dependent) system font paths,
        and the additional paths specified by `paths` parameter.

        Returns None if the font was not found.

        Args:
            name: Name of font, such as "DejaVu Sans"
            paths: Additional paths to search
    '''
    return system_fonts(paths).get(name, None)
