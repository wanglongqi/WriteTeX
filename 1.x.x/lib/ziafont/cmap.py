''' Font CMAP table - translate character into a glyph ID '''

from __future__ import annotations
from typing import Sequence, Optional


class Cmap12:
    ''' Format 12 cmap Table '''
    def __init__(self, platform: str, platformid: int, startcodes: Sequence[int],
                 endcodes: Sequence[int], glyphstarts: Sequence[int]):
        self.platform = platform
        self.platformid = platformid
        self.startcodes = startcodes
        self.endcodes = endcodes
        self.glyphstarts = glyphstarts

        self.glyphmap = {}
        for startid, start in enumerate(self.startcodes):
            for i in range(start, self.endcodes[startid]+1):
                self.glyphmap[i] = self.glyphstarts[startid] + (i-start)

        self.glyphmap_r: Optional[dict[int, set[str]]] = None  # Build on demand

    def __repr__(self):
        return f'<Cmap Format 12: {self.platform} id={self.platformid}'

    def glyphid(self, char: str) -> int:
        ''' Get glyph index from a character '''
        charid = ord(char)
        return self.glyphmap.get(charid, 0)       

    def char(self, glyphid: int) -> set[str]:
        ''' Get unicode character code from glyphid (reverse cmap lookup) '''
        if self.glyphmap_r is None:
            self.glyphmap_r = {}
            for key, val in self.glyphmap.items():
                if val not in self.glyphmap_r:
                    self.glyphmap_r[val] = set([chr(key)])
                else:
                    self.glyphmap_r[val].add(chr(key))
        return self.glyphmap_r.get(glyphid, set())


class Cmap4:
    ''' Format 4 cmap Table '''
    def __init__(self, platform: str, platformid: int, startcodes: Sequence[int],
                 endcodes: Sequence[int], idrangeoffset: Sequence[int],
                 iddeltas: Sequence[int], glyphidarray: Sequence[int]):
        self.platform = platform
        self.platformid = platformid
        self.startcodes = startcodes
        self.endcodes = endcodes
        self.idrangeoffset = idrangeoffset
        self.iddeltas = iddeltas
        self.glyphidarray = glyphidarray

        self.glyphmap = {}
        for seg, startcode in enumerate(self.startcodes):
            for i in range(startcode, self.endcodes[seg]+1):
                if self.idrangeoffset[seg] != 0:
                    idx = (seg 
                           - len(self.startcodes)
                           + self.idrangeoffset[seg]//2
                           + i - self.startcodes[seg])
                    gid = self.glyphidarray[idx]
                    gid = self.iddeltas[seg] + gid if gid > 0 else 0
                else:
                    gid = (self.iddeltas[seg] + i) % 0x10000
                self.glyphmap[i] = gid

        self.glyphmap_r: Optional[dict[int, set[str]]] = None  # Build on demand

    def __repr__(self):
        return f'<Cmap Format 4: {self.platform} id={self.platformid}'

    def glyphid(self, char: str) -> int:
        ''' Get glyph index from a character '''
        charid = ord(char)
        return self.glyphmap.get(charid, 0)       

    def char(self, glyphid: int) -> set[str]:
        ''' Get unicode character code from glyphid (reverse cmap lookup) '''
        if self.glyphmap_r is None:
            self.glyphmap_r = {}
            for key, val in self.glyphmap.items():
                if val not in self.glyphmap_r:
                    self.glyphmap_r[val] = set([chr(key)])
                else:
                    self.glyphmap_r[val].add(chr(key))
        return self.glyphmap_r.get(glyphid, set())
