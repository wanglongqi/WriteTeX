from collections import namedtuple
from dataclasses import dataclass


Table = namedtuple('Table', ['checksum', 'offset', 'length'])
BBox = namedtuple('BBox', ['xmin', 'xmax', 'ymin', 'ymax'])
AdvanceWidth = namedtuple('AdvanceWidth', ['width', 'leftsidebearing'])
Header = namedtuple(
    'Header', ['version', 'revision', 'checksumadjust', 'magic', 'flags',
               'created', 'modified', 'macstyle', 'lowestrecppem',
               'directionhint', 'indextolocformat', 'glyphdataformat',
               'numlonghormetrics', 'numglyphs'])
FontNames = namedtuple('FontNames', ['copyright', 'family', 'subfamily', 'unique',
                                     'name', 'nameversion', 'postscript', 'trademark',
                                     'manufacturer', 'designer', 'description', 'vendorurl',
                                     'designerurl', 'license', 'LicenseURL'])
Layout = namedtuple(
    'Layout', ['unitsperem', 'xmin', 'xmax', 'ymin', 'ymax',
               'ascent', 'descent', 'advwidthmax',
               'minleftbearing', 'minrightbearing'])
FontInfo = namedtuple(
    'FontInfo', ['filename', 'names', 'header', 'layout'])

GlyphComp = namedtuple('GlyphComp', ['glyphs', 'xforms', 'bbox'])
Xform = namedtuple('Xform', ['a', 'b', 'c', 'd', 'e', 'f', 'match'])
Symbols = namedtuple('Symbols', ['word', 'symbols', 'width', 'xmin', 'ymin', 'ymax'])
