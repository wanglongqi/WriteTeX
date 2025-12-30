from .mathtable import MathTable
from .styles import styledchr
from .zmath import Math, Latex, Text, reset_numbering
from .tex import declareoperator
from .config import config

__version__ = '0.12'


declareoperator(r'\tg')
declareoperator(r'\ctg')
declareoperator(r'\arcctg')
declareoperator(r'\arctg')
declareoperator(r'\arg')
declareoperator(r'\cotg')
declareoperator(r'\sh')
declareoperator(r'\ch')
declareoperator(r'\cth')
declareoperator(r'\th')
