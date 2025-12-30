''' Inspect and debug glyphs and font tables '''

from __future__ import annotations
from typing import TYPE_CHECKING, Sequence
import xml.etree.ElementTree as ET
import itertools

from .svgpath import fmt

if TYPE_CHECKING:
    from .glyph import SimpleGlyph
    from .font import Font


ARROW = '&#8594;'


# GSUB lookup table types
lookupnames = {
    1: 'Single Substitution (1 &#8594; 1)',
    2: 'Multiple Substitution (1 &#8594; N)',
    3: 'Alternate Substitution (1 &#8594; alternates)',
    4: 'Ligature Substitution (N &#8594; 1)',
    5: 'Contextual Substitution',
    6: 'Chained Context Substitution'
}


def table_header(*cols: Sequence[str]) -> str:
    ''' Make an HTML table header from the columns '''
    parts = [f'<th style="text-align: center;">{c}</th>' for c in cols]
    hdr = ''.join(parts)
    return f'<table>{hdr}'


def table_row(*cols: Sequence[str]) -> str:
    ''' Make an HTML table row from the columns '''
    parts = [f'<td>{c}</td>' for c in cols]
    row = ''.join(parts)
    return f'<tr>{row}</tr>'


def table_footer() -> str:
    ''' Make the HTML table footer '''
    return '</table>'



class DescribeFont:
    ''' Display Font Metadata in HTML table '''
    def __init__(self, font: Font):
        self.font = font

    def _repr_html_(self) -> str:
        return self.table()

    def format_languages(self):
        ''' Format the scripts/languages in the font '''
        out = ''
        for script in self.font.scripts():
            out += script
            langs = [lang for lang in self.font.languages(script) if lang]
            if langs:
                out += ' (' + ', '.join(langs).strip() + ')'
            out += '<br>'
        return out

    def table(self):
        ''' Generate the HTML table '''
        def table_row(a, b):
            return f'<tr><td>{a}</td><td>{b}</td></tr>'

        table = '<h2>Font Info</h2>'
        table += '<table>'
        table += table_row('Font Name', self.font.info.names.name)
        table += table_row('Family', self.font.info.names.family)
        table += table_row('Subfamily', self.font.info.names.subfamily)
        table += table_row('Description', self.font.info.names.description)
        table += table_row('Designer', self.font.info.names.designer)
        table += table_row('Manufacturer', self.font.info.names.manufacturer)
        table += table_row('License', self.font.info.names.license)
        table += table_row('Created', str(self.font.info.header.created))
        table += table_row('Modified', str(self.font.info.header.modified))
        table += table_row('Copyright', self.font.info.names.copyright)
        table += '</table>'
        table += '<h2>Technical</h2>'
        table += '<table>'
        table += table_row('Number of Glyphs', self.font.info.header.numglyphs)
        table += table_row('Tables', ', '.join(self.font.tables.keys()))
        if self.font.gsub is not None:
            table += table_row('GSUB features', ', '.join(self.font.gsub.features_available().keys()))
        else:
            table += table_row('GSUB features', 'None')

        if self.font.gpos is not None:
            table += table_row('GPOS features', ', '.join(self.font.gpos.features_available().keys()))
        else:
            table += table_row('GPOS features', 'None')
        table += table_row('Scripts/Languages', self.format_languages())
        table += '</table>'
        return table


class InspectGlyph:
    ''' Draw glyph svg with test/debug lines '''
    def __init__(self, glyph: SimpleGlyph, pxwidth: float = 400, pxheight: float = 400):
        self.glyph = glyph
        self.font = self.glyph.font
        self.pxwidth = pxwidth
        self.pxheight = pxheight

    def _repr_svg_(self):
        ''' Jupyter representation '''
        return self.svg()

    def svg(self) -> str:
        ''' Glyph SVG string '''
        return ET.tostring(self.svgxml(), encoding='unicode')

    def svgxml(self) -> ET.Element:
        ''' Glyph svg as XML element tree '''
        # Draw glyph at 1:1 scale in glyph units
        height = self.font.info.layout.ymax - self.font.info.layout.ymin
        width = height * self.pxwidth/self.pxheight

        # vertical positions
        ymargin = height / 20
        height *= 1.1
        bot = height - ymargin
        baseline = height + self.font.info.layout.ymin - ymargin
        descend = baseline - self.font.info.layout.descent
        ascend = baseline - self.font.info.layout.ascent
        top = baseline - self.font.info.layout.ymax

        # horizontal positions
        xadvance = self.glyph.advance()
        x0 = (width - xadvance)/2
        x1 = x0 + xadvance

        # drawing constants
        radius = fmt(width/150)
        txtmargin = fmt(25)
        txtsize = fmt(width/40)
        tick = width/50

        svg = ET.Element('svg')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('viewBox', f'0 0 {fmt(width)} {fmt(height)}')
        svg.set('width', fmt(self.pxwidth))
        svg.set('height', fmt(self.pxheight))

        # Height lines
        def hline(y, name, color):
            path = ET.SubElement(svg, 'path')
            path.attrib['d'] = f'M 0 {fmt(y)} l {fmt(width)} 0'
            path.attrib['stroke'] = color
            path.set('stroke-width', '1px')
            path.set('opacity', '.5')
            path.set('vector-effect', 'non-scaling-stroke')
            text = ET.SubElement(svg, 'text')
            text.set('x', fmt(txtmargin))
            text.set('y', fmt(y-20))
            text.set('font-size', txtsize)
            text.text = name
        hline(baseline, 'baseline', 'red')
        hline(bot, 'ymin', 'gray')
        hline(descend, 'descend', 'gray')
        hline(ascend, 'ascend', 'gray')
        hline(top, 'ymax', 'gray')

        # Vertical lines
        def vline(x, color):
            path = ET.SubElement(svg, 'path')
            path.attrib['d'] = f'M {fmt(x)} 0 l 0 {fmt(height)}'
            path.attrib['stroke'] = color
            path.set('stroke-width', '1px')
            path.set('opacity', '.5')
            path.set('vector-effect', 'non-scaling-stroke')
        vline(x0, 'gray')
        vline(x1, 'gray')

        # Ticks
        z = ET.SubElement(svg, 'path')
        z.set('d', (f'M {fmt(x0-tick)} {fmt(baseline)} '
                    f'L {fmt(x0)} {fmt(baseline)} {fmt(x0)} {fmt(baseline+tick)}'))
        z.set('stroke', '#444444')
        z.set('stroke-width', '4px')
        z.set('fill', 'none')
        z.set('vector-effect', 'non-scaling-stroke')
        z = ET.SubElement(svg, 'path')
        z.set('d', (f'M {fmt(x1+tick)} {fmt(baseline)} '
                    f'L {fmt(x1)} {fmt(baseline)} {fmt(x1)} {fmt(baseline+tick)}'))
        z.set('stroke', '#444444')
        z.set('stroke-width', '4px')
        z.set('fill', 'none')
        z.set('vector-effect', 'non-scaling-stroke')
        text = ET.SubElement(svg, 'text')
        text.set('x', fmt(x0))
        text.set('y', fmt(baseline+tick+100))
        text.set('font-size', txtsize)
        text.set('text-anchor', 'middle')
        text.set('alignment-baseline', 'top')
        text.text = '0'
        text = ET.SubElement(svg, 'text')
        text.set('x', fmt(x1))
        text.set('y', fmt(baseline+tick+100))
        text.set('font-size', txtsize)
        text.set('text-anchor', 'middle')
        text.set('alignment-baseline', 'top')
        text.text = str(int(xadvance))

        # Glyph Outline
        g = self.glyph.svgpath(x0=x0, y0=baseline,
                               scale_factor=1/self.glyph._points_per_unit)  # type: ignore
        if g is not None:
            g.set('fill', 'lightgray')
            g.set('stroke', 'black')
            g.set('stroke-width', '2px')
            g.set('vector-effect', 'non-scaling-stroke')
            svg.append(g)

        for op in self.glyph.operators:
            points, ctrls = op.points()
            for p, c in zip(points, ctrls):
                circ = ET.SubElement(svg, 'circle')
                circ.set('cx', fmt(x0 + p.x))
                circ.set('cy', fmt(baseline-p.y))
                circ.set('r', radius)
                circ.set('fill', '#393ee3' if c else '#d1211b')
                circ.set('stroke-width', '1px')
                circ.set('vector-effect', 'non-scaling-stroke')
        return svg


class DescribeGlyph:
    ''' HTML Table of Glyph information '''
    def __init__(self, glyph: SimpleGlyph):
        self.glyph = glyph

    def __repr__(self):
        chstr = ', '.join(list(self.glyph.char))
        ordstr = ', '.join(format(ord(k), '04X') for k in list(self.glyph.char))
        r = f'Index: {self.glyph.index}\n'
        r += f'Unicode: {ordstr}\n'
        r += f'Character: {chstr}\n'
        r += f'xmin: {self.glyph.bbox.xmin}\n'
        r += f'xmax: {self.glyph.bbox.xmax}\n'
        r += f'ymin: {self.glyph.bbox.ymin}\n'
        r += f'ymax: {self.glyph.bbox.ymax}\n'
        r += f'Advance: {self.glyph.advance()}\n'
        if hasattr(self.glyph, 'glyphs'):  # Compound
            comps = self.glyph.glyphs.glyphs
            ids = ', '.join(str(c.index) for c in comps)
            r += f'Component ids: {ids}\n'
        return r

    def _repr_html_(self):
        ''' Jupyter representation, HTML table '''
        return self.describe()

    def describe(self):
        ''' HTML table with glyph parameters '''
        chstr = ', '.join(list(self.glyph.char))
        ordstr = ', '.join(format(ord(k), '04X') for k in list(self.glyph.char))
        comprow = ''
        if hasattr(self.glyph, 'glyphs'):  # Compound
            comps = self.glyph.glyphs.glyphs
            ids = ', '.join(str(c.index) for c in comps)
            comprow = f'<tr><td>Component ids</td><td>{ids}</td></tr>'

        h = f'''
        <table>
        <tr><td>Index</td><td>{self.glyph.index}</td></tr>
        <tr><td>Unicode</td><td>{ordstr}</td></tr>
        <tr><td>Character</td><td>{chstr}</td></tr>
        <tr><td>xmin</td><td>{self.glyph.bbox.xmin}</td></tr>
        <tr><td>xmax</td><td>{self.glyph.bbox.xmax}</td></tr>
        <tr><td>ymin</td><td>{self.glyph.bbox.ymin}</td></tr>
        <tr><td>ymax</td><td>{self.glyph.bbox.ymax}</td></tr>
        <tr><td>Advance</td><td>{self.glyph.advance()}</td></tr>
        {comprow}
        </table>
        '''
        return h


class ShowGlyphs:
    ''' Show all glyphs in the font in HTML table '''
    def __init__(self, font, size: float = 36, columns: int = 15, nmax: int|None = None):
        self.font = font
        self.size = size
        self.columns = columns
        self.nmax = nmax

    def _repr_html_(self) -> str:
        return self.table()

    def table(self) -> str:
        ''' Build HTML table '''
        rows = []  # All rows
        row = []  # Current row
        nglyphs = self.font.info.header.numglyphs
        if self.nmax:
            nglyphs = min(nglyphs, self.nmax)
        for i in range(nglyphs):
            svg = self.font.glyph_fromid(i).svg(self.size)
            row.append(f'<td><div gid="{i}">{i}<br>{svg}</div></td>')
            if len(row) >= self.columns:
                rows.append(''.join(row))
                row = []
        rows.append(''.join(row))
        rowstrs = [f'<tr>{r}</tr>' for r in rows]
        return '<table>' + ''.join(rowstrs) + '</table>'


class ShowFeature:
    ''' Show all lookup tables in a feature '''
    def __init__(self, featname, font, size: float=36):
        self.featname = featname
        self.font = font
        self.size = size
        self.lookups = self.font.gsub.features_available()[self.featname]

    def _repr_html_(self) -> str:
        html = f'<h2>{self.featname}</h2>'
        for lookup in self.lookups:
            html += '<h3>' + lookupnames.get(lookup.type, '') + '</h3>'
            if lookup.type == 1:
                html += ShowLookup1(lookup, self.font, self.size).table()
            elif lookup.type == 3:
                html += ShowLookup3(lookup, self.font, self.size).table()
            elif lookup.type == 4:
                html += ShowLookup4(lookup, self.font, self.size).table()
            elif lookup.type == 6 and lookup.fmt == 3:
                html += ShowLookup63(lookup, self.font, self.size).table()
            else:
                html += '<p>N/A</p>'
        return html


class ShowLookup:
    ''' Show a Lookup table '''
    def __init__(self, lookup, font, size: float=36):
        self.lookup = lookup
        self.font = font
        self.size = size

    def _repr_html_(self) -> str:
        if self.lookup.type == 1:
            return ShowLookup1(self.lookup, self.font, self.size).table()
        elif self.lookup.type == 3:
            return ShowLookup3(self.lookup, self.font, self.size).table()
        elif self.lookup.type == 4:
            return ShowLookup4(self.lookup, self.font, self.size).table()
        elif self.lookup.type == 6 and self.lookup.fmt == 3:
            return ShowLookup63(self.lookup, self.font, self.size).table()
        else:
            return f'<h3>Lookup {self.lookup.type} - N/A</h3>'


class LookupDisplay:
    ''' Base class to show items in lookup table '''
    def __init__(self, lookup, font, size: float=36):
        self.lookup = lookup
        self.font = font
        self.size = size

    def svg_for_gid(self, gid):
        return self.font.glyph_fromid(gid).svg(self.size)

    def _repr_html_(self) -> str:
        return self.table()

    def table(self) -> str:
        return ''


class ShowLookup4(LookupDisplay):
    ''' Show items in Lookup Table type 4 (N->1 Ligature Substitution) '''
    def table(self) -> str:
        header = table_header('Glyphs In', '', 'Glyph Out', 'IDs In', '', 'ID Out')
        table = ''
        for subtable in self.lookup.subtables:
            for covidx, startglyph in enumerate(subtable.covtable.list_glyphs()):
                ligset = subtable.ligsets[covidx]
                for nextglyphs, repl in ligset.items():
                    origglyphs = [startglyph] + list(nextglyphs)

                    svg = ''
                    for gid in origglyphs:
                        svg += self.svg_for_gid(gid)
                    replsvg = self.svg_for_gid(repl)
                    table += table_row(
                        svg,
                        ARROW,
                        replsvg,
                        origglyphs,
                        ARROW,
                        repl
                    )
        return header + table + table_footer()


class ShowLookup1(LookupDisplay):
    ''' Show items in Lookup Table type 1 (1:1 substitution) '''
    def table(self) -> str:
        header = table_header('Glyph In', '', 'Glyph Out', 'ID In', '', 'ID Out')
        table = ''
        for subtable in self.lookup.subtables:
            glyphs = subtable.covtable.list_glyphs()
            subd_glyphs = self.lookup.sub(glyphs, [subtable])
            for gid1, gid2 in zip(glyphs, subd_glyphs):
                svg1 = self.svg_for_gid(gid1)
                svg2 = self.svg_for_gid(gid2)
                table += table_row(svg1, ARROW, svg2, gid1, ARROW, gid2)
        return header + table + table_footer()


class ShowLookup3(LookupDisplay):
    ''' Show items in Lookup Table type 3 (1:N substitution) '''
    def table(self) -> str:
        header = table_header('Glyph In', '', 'Alternates', 'ID', '', 'Alternates')
        table = ''
        for subtable in self.lookup.subtables:
            glyphs = subtable.covtable.list_glyphs()
            for glyph, altglyphs in zip(glyphs, subtable.altglyphs):

                svg = ''
                for gid in altglyphs:
                    svg += self.svg_for_gid(gid)

                glyphsvg = self.svg_for_gid(glyph)
                table += table_row(
                    glyphsvg,
                    ARROW,
                    svg,
                    gid,
                    ARROW,
                    altglyphs
                )
        return header + table + table_footer()


class ShowLookup63(LookupDisplay):
    ''' Show items in Lookup Table type 6.3 (context substitution) '''
    def table(self) -> str:
        header = table_header('Sequence In', '', 'Sequence Out', 'IDs In', '', 'IDs Out')
        table = ''
        for k, subtable in enumerate(self.lookup.subtables):
            table += table_row(f'Subtable {k}')
            backglyphs = [b.list_glyphs() for b in subtable.backCoverage]
            inptglyphs = [i.list_glyphs() for i in subtable.inptCoverage]
            fwdglyphs = [f.list_glyphs() for f in subtable.lookaheadCoverage]
            chain = backglyphs + inptglyphs + fwdglyphs
            for c in itertools.product(*chain):
                newglyphs = subtable.sub(list(c), self.font.gsub.lookups)

                oldsvg = ''
                for gid in c:
                    oldsvg += self.svg_for_gid(gid)

                newsvg = self.font.text(newglyphs, size=self.size).svg()

                table += table_row(
                    oldsvg,
                    ARROW,
                    newsvg,
                    str(c),
                    ARROW,
                    str(newglyphs)
                    )
        return header + table + table_footer()
    