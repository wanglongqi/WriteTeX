#!/usr/bin/env python
# -*- coding:utf-8
"""
writetex.py
An Latex equation editor for Inkscape.

:Author: WANG Longqi <iqgnol@gmail.com>
:Date: 2018-11-24
:Version: v1.7.0

This file is a part of WriteTeX extension for Inkscape. For more information,
please refer to http://wanglongqi.github.io/WriteTeX.
"""
from __future__ import print_function
import inkex
import os
import tempfile
import sys
import copy
import subprocess
import re
from lxml import etree
# from distutils import spawn
WriteTexNS = u'http://wanglongqi.github.io/WriteTeX'
# from textext
SVG_NS = u"http://www.w3.org/2000/svg"
XLINK_NS = u"http://www.w3.org/1999/xlink"


class WriteTex(inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)
        self.arg_parser.add_argument("-f", "--formula",
                                     action="store", type=str,
                                     dest="formula", default="",
                                     help="LaTeX formula")
        self.arg_parser.add_argument("-p", "--preamble",
                                     action="store", type=str,
                                     dest="preamble", default="",
                                     help="Preamble File")
        self.arg_parser.add_argument("--read-as-line",
                                     action="store", type=str,
                                     dest="preline", default="",
                                     help="Read preamble as string")
        self.arg_parser.add_argument("-s", "--scale",
                                     action="store", type=str,
                                     dest="scale", default="",
                                     help="Scale Factor")
        self.arg_parser.add_argument("-i", "--inputfile",
                                     action="store", type=str,
                                     dest="inputfile", default="",
                                     help="Read From File")
        self.arg_parser.add_argument("-c", "--pdftosvg",
                                     action="store", type=str,
                                     dest="pdftosvg", default="",
                                     help="PDFtoSVG Converter")
        self.arg_parser.add_argument("--action", action="store",
                                     type=str, dest="action",
                                     default=None, help="")
        self.arg_parser.add_argument("-r", "--rescale",
                                     action="store", type=str,
                                     dest="rescale", default="",
                                     help="Rescale the object")
        self.arg_parser.add_argument("-l", "--latexcmd",
                                     action="store", type=str,
                                     dest="latexcmd", default="xelatex",
                                     help="Latex command used to compile")
        self.arg_parser.add_argument("-P", "--additionalpath",
                                     action="store", type=str,
                                     dest="additionalpath", default="",
                                     help="Additional search path")
        self.arg_parser.add_argument("-t", "--tosvg",
                                     action="store", type=str,
                                     dest="tosvg", default="false",
                                     help="Write output directly to a new node in svg file")

    def effect(self):
        WriteTex.handle_path(self.options.additionalpath)
        action = self.options.action.strip("\"")
        if action == "settings":
            print('Settings are auto applied, please switch to other tab for other functions.',
                file=sys.stderr)
            return
        self.options.scale = float(self.options.scale)
        if action == "viewold":
            for i in self.options.ids:
                node = self.svg.selected[i]
                if node.tag != '{%s}g' % SVG_NS:
                    continue
                if '{%s}text' % WriteTexNS in node.attrib:
                    if self.options.tosvg == "true":
                        doc = etree.fromstring(
                            '<text x="%g" y="%g">%s</text>' % (
                                self.svg.namedview.center[0],
                                self.svg.namedview.center[1],
                                node.attrib.get(
                                    '{%s}text' % WriteTexNS, '')))
                        p = node.getparent()
                        p.append(doc)
                    else:
                        print(node.attrib.get(
                            '{%s}text' % WriteTexNS, ''), file=sys.stderr)
                    return
            print("No text find.", file=sys.stderr)
            return
        else:
            if action == "new":
                self.text = self.options.formula
            else:
                f = open(self.options.inputfile)
                self.text = f.read()
                f.close()

            if self.text == "":
                print("empty LaTeX input. Nothing is changed.", file=sys.stderr)
                return

            tmp_dir = tempfile.mkdtemp("", "writetex-")
            tex_file = os.path.join(tmp_dir, "writetex.tex")
            svg_file = os.path.join(tmp_dir, "writetex.svg")
            pdf_file = os.path.join(tmp_dir, "writetex.pdf")
            log_file = os.path.join(tmp_dir, "writetex.log")
            out_file = os.path.join(tmp_dir, "writetex.out")
            err_file = os.path.join(tmp_dir, "writetex.err")
            aux_file = os.path.join(tmp_dir, "writetex.aux")

            if self.options.preline == "true":
                preamble = self.options.preamble
            else:
                if self.options.preamble == "":
                    preamble = ""
                else:
                    f = open(self.options.preamble)
                    preamble = f.read()
                    f.close()

            self.tex = r"""
            \documentclass[landscape,a3paper]{article}
            \usepackage{geometry}
            %s
            \pagestyle{empty}
            \begin{document}
            \noindent
            %s
            \end{document}
            """ % (preamble, self.text)

            tex = open(tex_file, 'w')
            tex.write(self.tex)
            tex.close()

            if self.options.latexcmd.lower() == "xelatex":
                cmd = " CMD executed: {}".format('xelatex "-output-directory=%s" -interaction=nonstopmode -halt-on-error "%s" > "%s"'
                                                 % (tmp_dir, tex_file, out_file))
                subprocess.call('xelatex "-output-directory=%s" -interaction=nonstopmode -halt-on-error "%s" > "%s"'
                                % (tmp_dir, tex_file, out_file), shell=True)
            elif self.options.latexcmd.lower() == "pdflatex":
                cmd = " CMD executed: {}".format('pdflatex "-output-directory=%s" -interaction=nonstopmode -halt-on-error "%s" > "%s"'
                                                 % (tmp_dir, tex_file, out_file))
                subprocess.call('pdflatex "-output-directory=%s" -interaction=nonstopmode -halt-on-error "%s" > "%s"'
                                % (tmp_dir, tex_file, out_file), shell=True)
            else:
                # Setting `latexcmd` to following string produces the same result as xelatex condition:
                # 'xelatex "-output-directory={tmp_dir}" -interaction=nonstopmode -halt-on-error "{tex_file}" > "{out_file}"'
                cmd = " CMD executed: {}".format(self.options.latexcmd.format(
                    tmp_dir=tmp_dir, tex_file=tex_file, out_file=out_file))
                subprocess.call(self.options.latexcmd.format(
                    tmp_dir=tmp_dir, tex_file=tex_file, out_file=out_file), shell=True)

            if not os.path.exists(pdf_file):
                print("Latex error: check your latex file and preamble.",
                      file=sys.stderr)
                print(cmd, file=sys.stderr)
                print(open(log_file).read(), file=sys.stderr)
                return
            else:
                if self.options.pdftosvg == '1':
                    subprocess.call('pdf2svg %s %s' %
                                    (pdf_file, svg_file), shell=True)
                    self.merge_pdf2svg_svg(svg_file)
                elif self.options.pdftosvg == '2':
                    subprocess.call('pstoedit -f plot-svg "%s" "%s"  -dt -ssp -psarg -r9600x9600 > "%s" 2> "%s"'
                                    % (pdf_file, svg_file, out_file, err_file), shell=True)
                    self.merge_pstoedit_svg(svg_file)
                else:
                    subprocess.call('pdftocairo -svg "%s" "%s"  > "%s" 2> "%s"'
                                    % (pdf_file, svg_file, out_file, err_file), shell=True)
                    self.merge_pdf2svg_svg(svg_file)

            os.remove(tex_file)
            os.remove(log_file)
            os.remove(out_file)
            if os.path.exists(err_file):
                os.remove(err_file)
            if os.path.exists(aux_file):
                os.remove(aux_file)
            if os.path.exists(svg_file):
                os.remove(svg_file)
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
            os.rmdir(tmp_dir)

    def merge_pstoedit_svg(self, svg_file):
        def svg_to_group(self, svgin):
            innode = svgin.tag.rsplit('}', 1)[-1]
            # replace svg with group by select specific elements
            if innode == 'svg':
                svgout = etree.Element(inkex.addNS('g'))
            else:
                svgout = etree.Element(inkex.addNS(innode))
                for att in svgin.attrib:
                    svgout.attrib[att] = svgin.attrib[att]

            for child in svgin.iterchildren():
                tag = child.tag.rsplit('}', 1)[-1]
                if tag in ['g', 'path', 'line']:
                    child = svg_to_group(self, child)
                    svgout.append(child)

            # TODO: add crop range code here.

            return svgout

        doc = etree.parse(svg_file)
        svg = doc.getroot()
        newnode = svg_to_group(self, svg)
        newnode.attrib['{%s}text' %
                       WriteTexNS] = self.text

        replace = False

        for i in self.options.ids:
            node = self.svg.selected[i]
            if node.tag != '{%s}g' % SVG_NS:
                continue
            if '{%s}text' % WriteTexNS in node.attrib:
                replace = True
                break

        if replace:
            try:
                if self.options.rescale == 'true':
                    newnode.attrib['transform'] = 'matrix(%f,0,0,%f,%f,%f)' % (
                        800*self.options.scale, 800*self.options.scale,
                        self.svg.namedview.center[0],
                        self.svg.namedview.center[1])
                else:
                    if 'transform' in node.attrib:
                        newnode.attrib['transform'] = node.attrib['transform']
                    else:
                        newnode.attrib['transform'] = 'matrix(%f,0,0,%f,%f,%f)' % (
                            800*self.options.scale, 800*self.options.scale,
                            self.svg.namedview.center[0],
                            self.svg.namedview.center[1])
                newnode.attrib['style'] = node.attrib['style']
            except:
                pass
            p = node.getparent()
            p.remove(node)
            p.append(newnode)
        else:
            newnode.attrib['transform'] = 'matrix(%f,0,0,%f,%f,%f)' % (
                800*self.options.scale, 800*self.options.scale,
                self.svg.namedview.center[0],
                self.svg.namedview.center[1])
            self.svg.get_current_layer().append(newnode)

    def merge_pdf2svg_svg(self, svg_file):
        # This is the smallest point coordinates assumed
        MAX_XY = [-10000000, -10000000]

        def svg_to_group(self, svgin):
            target = {}
            for node in svgin.xpath('//*[@id]'):
                target['#'+node.attrib['id']] = node

            for node in svgin.xpath('//*'):
                if ('{%s}href' % XLINK_NS) in node.attrib:
                    href = node.attrib['{%s}href' % XLINK_NS]
                    p = node.getparent()
                    p.remove(node)
                    trans = 'translate(%s,%s)' % (
                        node.attrib['x'], node.attrib['y'])
                    for i in target[href].iterchildren():
                        i.attrib['transform'] = trans
                        x, y = self.parse_transform(trans)
                        if x > MAX_XY[0]:
                            MAX_XY[0] = x
                        if y > MAX_XY[1]:
                            MAX_XY[1] = y
                        p.append(copy.copy(i))

            svgout = etree.Element(inkex.addNS('g'))
            for node in svgin:
                if node is svgout:
                    continue
                if node.tag == '{%s}defs' % SVG_NS:
                    continue
                svgout.append(node)
            return svgout

        doc = etree.parse(svg_file)
        svg = doc.getroot()
        newnode = svg_to_group(self, svg)
        newnode.attrib['{%s}text' %
                       WriteTexNS] = self.text

        replace = False

        for i in self.options.ids:
            node = self.svg.selected[i]
            if node.tag != '{%s}g' % SVG_NS:
                continue
            if '{%s}text' % WriteTexNS in node.attrib:
                replace = True
                break

        if replace:
            try:
                if self.options.rescale == 'true':
                    newnode.attrib['transform'] = 'matrix(%f,0,0,%f,%f,%f)' % (
                        self.options.scale, self.options.scale,
                        self.svg.namedview.center[0],
                        self.svg.namedview.center[1])
                else:
                    if 'transform' in node.attrib:
                        newnode.attrib['transform'] = node.attrib['transform']
                    else:
                        newnode.attrib['transform'] = 'matrix(%f,0,0,%f,%f,%f)' % (
                            self.options.scale, self.options.scale,
                            self.svg.namedview.center[0]-MAX_XY[0]*self.options.scale,
                            self.svg.namedview.center[1]-MAX_XY[1]*self.options.scale)
                newnode.attrib['style'] = node.attrib['style']
            except:
                pass
            p = node.getparent()
            p.remove(node)
            p.append(newnode)
        else:
            self.svg.get_current_layer().append(newnode)
            newnode.attrib['transform'] = 'matrix(%f,0,0,%f,%f,%f)' % (
                self.options.scale, self.options.scale,
                self.svg.namedview.center[0]-MAX_XY[0]*self.options.scale,
                self.svg.namedview.center[1]-MAX_XY[1]*self.options.scale)

    @staticmethod
    def parse_transform(transf):
        if transf == "" or transf is None:
            return(0, 0)
        stransf = transf.strip()
        result = re.match(
            r"(translate|scale|rotate|skewX|skewY|matrix)\s*\(([^)]*)\)\s*,?",
            stransf)
        if result.group(1) == "translate":
            args = result.group(2).replace(',', ' ').split()
            dx = float(args[0])
            if len(args) == 1:
                dy = 0.0
            else:
                dy = float(args[1])
            return (dx, dy)
        else:
            return (0, 0)

    @staticmethod
    def handle_path(newpath):
        paths = os.environ.get('PATH', '')
        # Do not add to path if already added
        if newpath in paths:
            return
        if newpath:
            os.environ['PATH'] += os.path.pathsep + newpath

if __name__ == '__main__':
    e = WriteTex()
    e.run()
