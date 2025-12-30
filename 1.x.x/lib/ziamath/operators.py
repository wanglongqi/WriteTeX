''' MathML Operators Dictionary

    Defines how much space to put around operators such as in "x + y".
    Depends on where the operator falls in the mrow (prefix, infix, or postfix)

    See Appendix F of MathML2 Documentation:
    https://www.w3.org/TR/MathML2/appendixf.html
'''
from __future__ import annotations


operators = {
    ('(', 'prefix'):  {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    (')', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('[', 'prefix'):  {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    (']', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('{', 'prefix'):  {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('}', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('”', 'postfix'): {'fence': 'true',  'lspace': '0em', 'rspace': '0em'},  # &CloseCurlyDoubleQuote;
    ('’', 'postfix'): {'fence': 'true',  'lspace': '0em', 'rspace': '0em'},  # &CloseCurlyQuote;
    ('⟨', 'prefix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftAngleBracket;
    ('⌈', 'prefix'):  {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftCeiling;
    ('⟪', 'prefix'):  {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftDoubleBracket;
    ('⌊', 'prefix'):  {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftFloor;
    ('“', 'prefix'):  {'fence': 'true',  'lspace': '0em', 'rspace': '0em'},  # &OpenCurlyDoubleQuote;
    ('‘', 'prefix'): {'fence': 'true',  'lspace': '0em', 'rspace': '0em'},  # &OpenCurlyQuote;
    ('⟩', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &RightAngleBracket;
    ('⌉', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &RightCeiling;
    ('⟫', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &RightDoubleBracket;
    ('⌋', 'postfix'): {'fence': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &RightFloor;
    # ('&InvisibleComma;', 'infix'): {'separator': 'true',  'lspace': '0em', 'rspace': '0em'},
    (',', 'infix'): {'separator': 'true',  'lspace': '0em', 'rspace': 'verythickmathspace'},
    ('─', 'infix'): {'stretchy': 'true', 'minsize':'0',  'lspace': '0em', 'rspace': '0em'},  # '&HorizontalLine;'
    (';', 'infix'): {'separator': 'true',  'lspace': '0em', 'rspace': 'thickmathspace'},
    (';', 'postfix'): {'separator': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('≔', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Assign; or ':='
    ('∵', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Because;
    ('∴', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Therefore;
    ('❘', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &VerticalSeparator;
    ('//', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('∷', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Colon;
    ('&amp;', 'prefix'): {'lspace': '0em', 'rspace': 'thickmathspace'},
    ('&amp;', 'postfix'): {'lspace': 'thickmathspace', 'rspace': '0em'},
    ('⩮', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # *=
    ('-=', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('+=', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('/=', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('->', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    (':', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('..', 'postfix'): {'lspace': 'mediummathspace', 'rspace': '0em'},
    ('...', 'postfix'): {'lspace': 'mediummathspace', 'rspace': '0em'},
    ('∋', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SuchThat;
    ('⫤', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DoubleLeftTee;
    ('⊨', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DoubleRightTee;
    ('⊤', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownTee;
    ('⊣', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftTee;
    ('⊢', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightTee;
    ('⥰', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RoundImplies;
    ('|', 'infix'): {'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('‖', 'infix'): {'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('||', 'infix'): {'lspace': '0em', 'rspace': '0em'},
    ('⩔', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &Or;
    ('&&', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('⩓', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &And;
    ('&', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('!', 'prefix'): {'lspace': '0em', 'rspace': 'thickmathspace'},
    ('⫬', 'prefix'): {'lspace': '0em', 'rspace': 'thickmathspace'},  # &Not;
    ('∃', 'prefix'): {'lspace': '0em', 'rspace': 'thickmathspace'},  # &Exists;
    ('∀', 'prefix'): {'lspace': '0em', 'rspace': 'thickmathspace'},  # &ForAll;
    ('∄', 'prefix'): {'lspace': '0em', 'rspace': 'thickmathspace'},  # &NotExists;
    ('∈', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Element;
    ('∉', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotElement;
    ('∌', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotReverseElement;
    ('⋤', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSquareSubset;
    ('⋢', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'}, # &NotSquareSubsetEqual;
    ('⋥', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'}, # &NotSquareSuperset;
    ('⋣', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSquareSupersetEqual;
    ('⊄', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSubset;
    ('⊈', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSubsetEqual;
    ('⊅', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSuperset;
    ('⊉', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSupersetEqual;
    ('⊏', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SquareSubset;
    ('⊑', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SquareSubsetEqual;
    ('⊐', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SquareSuperset;
    ('⊒', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SquareSupersetEqual;
    ('⋐', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Subset;
    ('⊆', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SubsetEqual;
    ('⊃', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Superset;
    ('⊇', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SupersetEqual;
    ('⇐', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DoubleLeftArrow;
    ('⇔', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DoubleLeftRightArrow;
    ('⇒', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DoubleRightArrow;
    ('⥐', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownLeftRightVector;
    ('⥞', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownLeftTeeVector;
    ('↽', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownLeftVector;
    ('⥖', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownLeftVectorBar;
    ('⥟', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownRightTeeVector;
    ('⇁', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownRightVector;
    ('⥗', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DownRightVectorBar;
    ('←', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftArrow;
    ('⇤', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftArrowBar;
    ('⇆', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftArrowRightArrow;
    ('↔', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftRightArrow;
    ('⥎', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftRightVector;
    ('↤', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftTeeArrow;
    ('⥚', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftTeeVector;
    ('↼', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftVector;
    ('⥒', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftVectorBar;
    ('↙', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LowerLeftArrow;
    ('↘', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LowerRightArrow;
    ('→', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightArrow;
    ('⇥', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightArrowBar;
    ('⇄', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightArrowLeftArrow;
    ('↦', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightTeeArrow;
    ('⥛', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightTeeVector;
    ('⇀', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightVector;
    ('⥓', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightVectorBar;
    ('↖', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &UpperLeftArrow;
    ('↗', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &UpperRightArrow;''
    ('<', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('>', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('≠', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # != or &NotEqual
    ('⩵', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('≤', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},    # &leq 
    ('≥', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},    # & geq
    ('≡', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Congruent;
    ('≍', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &CupCap;
    ('≐', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DotEqual;
    ('∥', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &DoubleVerticalBar;
    ('=', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},   # &Equal;
    ('≂', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &EqualTilde;
    ('⇌', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Equilibrium;
    #('&GreaterEqual;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # Same as &ge;
    ('⋛', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &GreaterEqualLess;
    ('≧', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &GreaterFullEqual;
    ('⪢', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &GreaterGreater;
    ('≷', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &GreaterLess;
    ('⩾', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &GreaterSlantEqual;
    ('≳', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &GreaterTilde;
    ('≎', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &HumpDownHump;
    ('≏', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &HumpEqual;
    ('⊲', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftTriangle;
    ('⧏', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftTriangleBar;
    ('⊴', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LeftTriangleEqual;
    ('⋚', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LessEqualGreater;
    ('≦', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LessFullEqual;
    ('≶', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LessGreater;
    ('⪡', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LessLess;
    ('⩽', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LessSlantEqual;
    ('≲', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &LessTilde;
    ('≫', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NestedGreaterGreater;
    ('≪', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NestedLessLess;
    ('≢', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotCongruent;
    ('≭', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotCupCap;
    ('∦', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotDoubleVerticalBar;
    ('≄', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotEqualTilde;
    ('≯', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotGreater;
    ('≱', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotGreaterEqual;
    ('≩', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotGreaterFullEqual;
    # ('&NotGreaterGreater;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('≹', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotGreaterLess;
    # ('&NotGreaterSlantEqual;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('≵', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotGreaterTilde;
    # ('&NotHumpDownHump;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    # ('&NotHumpEqual;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('⋪', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  #&NotLeftTriangle;
    # ('&NotLeftTriangleBar;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('⋬', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotLeftTriangleEqual;
    ('≮', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotLess;
    ('≰', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotLessEqual;
    ('≸', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotLessGreater;
    # ('&NotLessLess;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ### ??? ('&NotLessSlantEqual;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('≴', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotLessTilde;
    # ('&NotNestedGreaterGreater;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    # ('&NotNestedLessLess;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('⊀', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotPrecedes;
    ('⪵', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotPrecedesEqual;
    ('⋠', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotPrecedesSlantEqual;
    ('⋫', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotRightTriangle;
    # ('&NotRightTriangleBar;', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},
    ('⋭', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotRightTriangleEqual;
    ('⊁', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSucceeds;
    ('⪶', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSucceedsEqual;
    ('⋡', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSucceedsSlantEqual;
    ('⋩', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotSucceedsTilde;
    ('≁', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotTilde;
    ('≇', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotTildeFullEqual;
    ('≉', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotTildeTilde;
    ('∤', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &NotVerticalBar;
    ('≺', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Precedes;
    ('⪯', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &PrecedesEqual;
    ('≼', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &PrecedesSlantEqual;
    ('≾', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &PrecedesTilde;
    ('∝', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Proportional;
    ('⇋', 'infix'): {'stretchy': 'true',  'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &ReverseEquilibrium;
    ('⊳', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightTriangle;
    ('⧐', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightTriangleBar;
    ('⊵', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &RightTriangleEqual;
    ('≻', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Succeeds;
    ('⪰', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SucceedsEqual;
    ('≽', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SucceedsSlantEqual;
    ('≿', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &SucceedsTilde;
    ('∼', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &Tilde;
    ('≃', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &TildeEqual;
    ('≅', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &TildeFullEqual;
    ('≈', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &TildeTilde;
    ('⊥', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &UpTee;
    ('∣', 'infix'): {'lspace': 'thickmathspace', 'rspace': 'thickmathspace'},  # &VerticalBar;
    ('⊔', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &SquareUnion;
    ('⋃', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &Union;
    ('⊎', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &UnionPlus;
    ('−', 'infix'): {'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},
    ('+', 'infix'): {'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},
    ('⋂', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &Intersection;
    ('∓', 'infix'): {'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &MinusPlus;
    ('±', 'infix'): {'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &PlusMinus;
    ('⊓', 'infix'): {'stretchy': 'true',  'lspace': 'mediummathspace', 'rspace': 'mediummathspace'},  # &SquareIntersection;
    ('⋁', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &Vee;
    ('⊖', 'prefix'): {'largeop': 'true', 'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &CircleMinus;
    ('⊕', 'prefix'): {'largeop': 'true', 'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &CirclePlus;
    ('∑', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &Sum;
    ('⋃', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},
    ('⊎', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},
    ('lim', 'prefix'): {'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},
    ('max', 'prefix'): {'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},
    ('min', 'prefix'): {'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},
    ('⊖', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},
    ('⊕', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},
    ('∫', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &Integral;
    ('∬', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('∭', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('∰', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},
    ('∲', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &ClockwiseContourIntegral;
    ('∮', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &ContourIntegral;
    ('∳', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &CounterClockwiseContourIntegral;
    ('∯', 'prefix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DoubleContourIntegral;
    ('∫', 'infix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &Integral;
    ('∲', 'infix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &ClockwiseContourIntegral;
    ('∮', 'infix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &ContourIntegral;
    ('∳', 'infix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &CounterClockwiseContourIntegral;
    ('∯', 'infix'): {'largeop': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DoubleContourIntegral;
    ('⋓', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Cup;
    ('⋒', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Cap;
    ('≀', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &VerticalTilde;
    ('⋀', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &Wedge;
    ('⊗', 'prefix'): {'largeop': 'true', 'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &CircleTimes;
    ('∐', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &Coproduct;
    ('∏', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &Product;
    ('⋂', 'prefix'): {'largeop': 'true', 'movablelimits': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},
    ('∐', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Coproduct;
    ('⋆', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Star;
    ('⊙', 'prefix'): {'largeop': 'true', 'movablelimits': 'true',  'lspace': '0em', 'rspace': 'thinmathspace'},  # &CircleDot;
    ('*', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},
    ('', 'infix'): {'lspace': '0em', 'rspace': '0em'},  # &InvisibleTimes;
    ('·', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &CenterDot;
    ('⊗', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &CircleTimes;
    ('⋁', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Vee;
    ('⋀', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Wedge;
    ('⋄', 'infix'): {'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Diamond;
    ('∖', 'infix'): {'stretchy': 'true',  'lspace': 'thinmathspace', 'rspace': 'thinmathspace'},  # &Backslash;
    ('/','infix'): {'lspace': '0em', 'rspace': '0em'},
    ('−', 'prefix'): {'lspace': '0em', 'rspace': 'veryverythinmathspace'},
    ('+', 'prefix'): {'lspace': '0em', 'rspace': 'veryverythinmathspace'},
    ('∓', 'prefix'): {'lspace': '0em', 'rspace': 'veryverythinmathspace'},
    ('±', 'prefix'): {'lspace': '0em', 'rspace': 'veryverythinmathspace'},
    ('.', 'infix'): {'lspace': '0em', 'rspace': '0em'},
    ('⨯', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &Cross;
    ('×', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('÷', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('**', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('⊙', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('∘', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &SmallCircle;
    ('□', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},  # &Square;
    ('∇', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},  # &Del;
    ('∂', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},  # &PartialD;
    ('ⅅ', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},  # &CapitalDifferentialD;
    ('ⅆ', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},  # &DifferentialD;
    ('√', 'prefix'): {'stretchy': 'true',  'lspace': '0em', 'rspace': 'verythinmathspace'},  # &Sqrt;
    ('⇓', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DoubleDownArrow;
    ('⟸', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DoubleLongLeftArrow;
    ('⟺', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DoubleLongLeftRightArrow;
    ('⟹', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DoubleLongRightArrow;
    ('⇑', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DoubleUpArrow;
    ('⇕', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DoubleUpDownArrow;
    ('↓', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DownArrow;
    ('⤓', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DownArrowBar;
    ('⇵', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DownArrowUpArrow;
    ('↧', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &DownTeeArrow;
    ('⥡', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftDownTeeVector;
    ('⇃', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftDownVector;
    ('⥙', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftDownVectorBar;
    ('⥑', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftUpDownVector;
    ('⥠', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftUpTeeVector;
    ('↿', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftUpVector;
    ('⥘', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LeftUpVectorBar;
    ('⟵', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LongLeftArrow;
    ('⟷', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LongLeftRightArrow;
    ('⟶', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &LongRightArrow;
    ('⥯', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &ReverseUpEquilibrium;
    ('⥝', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightDownTeeVector;
    ('⇂', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightDownVector;
    ('⥕', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightDownVectorBar;
    ('⥏', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightUpDownVector;
    ('⥜', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightUpTeeVector;
    ('↾', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightUpVector;
    ('⥔', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &RightUpVectorBar;
    ('↑', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &UpArrow;
    ('⤒', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &UpArrowBar;
    ('⇅', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &UpArrowDownArrow;
    ('↕', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &UpDownArrow;
    ('⥮', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &UpEquilibrium;
    ('↥', 'infix'): {'stretchy': 'true',  'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},  # &UpTeeArrow;
    ('^', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ("'", 'postfix'): {'lspace': 'verythinmathspace', 'rspace': '0em'},
    ('!', 'postfix'): {'lspace': 'verythinmathspace', 'rspace': '0em'},
    ('!!', 'postfix'): {'lspace': 'verythinmathspace', 'rspace': '0em'},
    ('~', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('@', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('--', 'postfix'): {'lspace': 'verythinmathspace', 'rspace': '0em'},
    ('--', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},
    ('++', 'postfix'): {'lspace': 'verythinmathspace', 'rspace': '0em'},
    ('++', 'prefix'): {'lspace': '0em', 'rspace': 'verythinmathspace'},
    (' ', 'infix'): {'lspace': '0em', 'rspace': '0em'},  # &ApplyFunction;
    ('?', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('_', 'infix'): {'lspace': 'verythinmathspace', 'rspace': 'verythinmathspace'},
    ('˘', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &Breve;
    ('¸', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &Cedilla;
    ('`', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DiacriticalGrave;
    ('˙', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DiacriticalDot;
    ('˝', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DiacriticalDoubleAcute;
    ('←', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftArrow;
    ('↔', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftRightArrow;
    ('⥎', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftRightVector;
    ('↼', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &LeftVector;
    ('´', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DiacriticalAcute;
    ('→', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &RightArrow;
    ('⇀', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  #&RightVector;
    ('˜', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DiacriticalTilde;
    ('¨', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &DoubleDot;
    ('ˇ', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &Hacek;
    ('̂', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &Hat;
    ('‾', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &OverBar;
    ('⏞', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &OverBrace;
    ('⎴', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &OverBracket;
    ('⏜', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  #&OverParenthesis;
    ('…', 'postfix'): {'accent': 'true',  'lspace': '0em', 'rspace': '0em'},  # &TripleDot;
    ('_', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &UnderBar;
    ('⏟', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &UnderBrace;
    ('⎵', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &UnderBracket;
    ('⏝', 'postfix'): {'accent': 'true', 'stretchy': 'true',  'lspace': '0em', 'rspace': '0em'},  # &UnderParenthesis;
}


integrals = ['∫', '∬', '∭', '∲', '∮', '∳', '∯', '∰', ]
fences = [op[0] for op, params in operators.items() if params.get('fence') == 'true'] + ['|', '∣', '❘', '‖']
leftfences = ['(', '[', '{', '⟨', '⌊', '⌈', '⟪']
names = set(op[0] for op in operators.keys())


def get_params(name: str, form: str) -> dict[str, str]:
    ''' Get parameters for the given operator name and form '''
    if form == 'none':
        # form of 'none' is given to single element mrows like {,}
        return {}

    params = operators.get((name, form), {})
    if not params:
        params = operators.get((name, 'infix'), {})
    if not params:
        params = operators.get((name, 'postfix'), {})
    if not params:
        params = operators.get((name, 'prefix'), {})

    return params.copy()
