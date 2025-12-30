''' Global configuration options '''
from dataclasses import dataclass


@dataclass
class Config:
    ''' Global configuration options for Ziafont

        Attributes
        ----------
        svg2: Use SVG2.0. Disable for better browser compatibility
            at the expense of SVG size
        debug: Debug mode, draws bounding boxes around text
        fontsize: Default font size in points
        precision: Decimal precision for SVG coordinates
    '''
    svg2: bool = True
    debug: bool = False
    fontsize: float = 48
    precision: float = 3


config = Config()
