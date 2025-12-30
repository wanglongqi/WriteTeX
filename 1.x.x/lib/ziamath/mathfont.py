''' Math Font extends Ziafont with MATH table '''

from __future__ import annotations
from dataclasses import dataclass
from typing import Union
from pathlib import Path

from ziafont import Font
from ziafont.glyph import SimpleGlyph

from .mathtable import MathTable
from .styles import MathVariant, styledchr, DIGIT_RANGE


@dataclass
class AltFonts:
    bold: Font | None = None
    italic: Font | None = None
    bolditalic: Font | None = None


class MathFont(Font):
    ''' Extend ziafont by reading MATH table and a base font size

        Args:
            fname: File name of font
            basesize: Default font size
    '''
    def __init__(self, fname: Union[str, Path], basesize: float = 24):
        super().__init__(fname)
        self.basesize = basesize
        if 'MATH' not in self.tables:
            raise ValueError('Font has no MATH table!')

        self.math = MathTable(self)
        if 'math' in self.scripts():
            self.language('math', '')

        self.alt_fonts = AltFonts()

    def findglyph(self, char: str, variant: MathVariant) -> SimpleGlyph:
        ''' Find a glyph from this font or an alternate font '''
        styled = styledchr(char, variant)
        if styled == char and not (DIGIT_RANGE[0] <= ord(char) <= DIGIT_RANGE[1]):
            # Math font doesn't have a built-in variant
            if variant.italic and variant.bold and self.alt_fonts.bolditalic:
                font = self.alt_fonts.bolditalic
            elif variant.italic and not variant.bold and self.alt_fonts.italic:
                font = self.alt_fonts.italic
            elif not variant.italic and variant.bold and self.alt_fonts.bold:
                font = self.alt_fonts.bold
            else:
                font = self

        else:
            font = self
            char = styled

        return font.glyph(char)

    def language(self, script, language):
        super().language(script, language)
        if script == 'math':
            self.features['ssty'] = True  # Enable math script variants
