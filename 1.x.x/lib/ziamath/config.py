''' Global configuration options '''
from typing import Optional, Callable
from dataclasses import dataclass, field

from ziafont import config as zfconfig


@dataclass
class DebugConfig:
    baseline: bool = False
    bbox: bool = False

    def on(self):
        self.baseline = True
        self.bbox = True

    def off(self):
        self.baseline = False
        self.bbox = False


@dataclass
class TextStyle:
    textfont: Optional[str] = None
    variant: str = 'serif'
    fontsize: float = 24
    color: str = 'black'
    linespacing: float = 1


@dataclass
class MathStyle:
    mathfont: Optional[str] = None
    variant: str = ''
    fontsize: float = 24
    color: str = 'black'
    background: str = 'none'
    bold_font: Optional[str] = None
    italic_font: Optional[str] = None
    bolditalic_font: Optional[str] = None


@dataclass
class NumberingStyle:
    ''' Style for equation numbers

        Args:
            autonumber: Automatically number all equations
            format: String formatter for equation numbers
            format_func: Function to return a formatted equation label
            columnwidth: Width of column or page. Equation numbers
                right-aligned with the columnwidth.
    '''
    autonumber: bool = False
    format: str = '({0})'
    format_func: Optional[Callable] = None
    columnwidth: str = '6.5in'

    def getlabel(self, i):
        ''' Get equation label for equation number i'''
        if self.format_func:
            return self.format_func(i)
        return self.format.format(i)


@dataclass
class Config:
    ''' Global configuration options for Ziamath

        Attributes
        ----------
        minsizefraction: Smallest allowed text size, as fraction of
            base size, for text such as subscripts and superscripts
        debug: Debug mode, draws bounding boxes around <mrows>
        svg2: Use SVG2.0. Disable for better browser compatibility,
            at the expense of SVG size
        precision: SVG decimal precision for coordinates
        decimal_separator: Use `.` or `,` as decimal separator. (only
            affects Latex math)
    '''
    math: MathStyle = field(default_factory=MathStyle)
    text: TextStyle = field(default_factory=TextStyle)
    minsizefraction: float = .3
    decimal_separator = '.'
    debug: DebugConfig = field(default_factory=DebugConfig)
    numbering: NumberingStyle = field(default_factory=NumberingStyle)

    @property
    def svg2(self) -> bool:
        return zfconfig.svg2

    @svg2.setter
    def svg2(self, value: bool) -> None:
        zfconfig.svg2 = value

    @property
    def precision(self) -> float:
        return zfconfig.precision

    @precision.setter
    def precision(self, value: float) -> None:
        zfconfig.precision = value


config = Config()
