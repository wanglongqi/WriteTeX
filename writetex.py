#!/usr/bin/env python
# -*- coding:utf-8
"""
writetex.py
An Latex equation editor for Inkscape.

:Author: WANG Longqi <iqgnol@gmail.com>
:Date: 2014-03-06

Update: 2014-03-07
    - Rewrite svg merge code, especially for pdf2svg's. 
    - Redesign UI. 
    - Ready for first public release.

This Inkscape extension is heavily influenced by Pauli Virtanen's textext,
which is one of my favorite Inkscape extensions. However,textext is not 
update for years and needs TK or PyGTK,which always needs some fix in path.
Therefore,I finally decided to write a new extension for this purpose. This 
extension is a native Inkscape extension; you do not need TK or PyGTK. 
Hope you like it!
"""

import inkex,os,tempfile,sys,copy
WriteTexNS=u'http://pecker.duapp.com'
# from textext
SVG_NS=u"http://www.w3.org/2000/svg"
XLINK_NS = u"http://www.w3.org/1999/xlink"

class WriteTex(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-f","--formula",
                        action="store",type="string",
                        dest="formula",default="",
                        help="LaTeX formula")
        self.OptionParser.add_option("-p","--preamble",
                        action="store",type="string",
                        dest="preamble",default="",
                        help="Preamble File")
        self.OptionParser.add_option("-s","--scale",
                        action="store",type="string",
                        dest="scale",default="",
                        help="Scale Factor")
        self.OptionParser.add_option("-i","--inputfile",
                        action="store",type="string",
                        dest="inputfile",default="",
                        help="Read From File")
        self.OptionParser.add_option("-c","--pdftosvg",
                        action="store",type="string",
                        dest="pdftosvg",default="",
                        help="PDFtoSVG Converter")                      
        self.OptionParser.add_option("--action",action="store",
                        type="string",dest="action",
                        default=None,help="")
        self.OptionParser.add_option("-r","--rescale",
                        action="store",type="string",
                        dest="rescale",default="",
                        help="PDFtoSVG Converter")
    def effect(self):
        self.options.scale=float(self.options.scale)
        action=self.options.action.strip("\"")
        if action=="viewold":
            for i in self.options.ids:
                node=self.selected[i]
                if node.tag != '{%s}g' % SVG_NS: continue                
                if '{%s}text'%WriteTexNS in node.attrib:
                    print >>sys.stderr,node.attrib.get('{%s}text'%WriteTexNS,'').decode('string-escape'),
                    return
            print >>sys.stderr,"No text find."  
            return
        else:
            if action == "new":
                self.text=self.options.formula
            else:
                f=open(self.options.inputfile)
                self.text=f.read()
                f.close()

            if self.text == "":
                print >>sys.stderr,"empty LaTeX input. Nothing is changed."
                return
                
            tmp_dir=tempfile.mkdtemp("","writetex-");
            tex_file=os.path.join(tmp_dir,"writetex.tex")
            svg_file=os.path.join(tmp_dir,"writetex.svg")
            pdf_file=os.path.join(tmp_dir,"writetex.pdf")
            log_file=os.path.join(tmp_dir,"writetex.log")
            out_file=os.path.join(tmp_dir,"writetex.out")
            err_file=os.path.join(tmp_dir,"writetex.err")
            aux_file=os.path.join(tmp_dir,"writetex.aux")
            
            if self.options.preamble=="":
                preamble=""
            else:
                f=open(self.options.preamble)
                preamble=f.read()
                f.close()
                
            self.tex=r"""
            \documentclass[landscape,a3paper]{article}
            \usepackage{geometry}
            %s
            \pagestyle{empty}
            \begin{document}
            \noindent
            %s
            \end{document}
            """ % (preamble,self.text) 
            
            tex=open(tex_file,'w')
            tex.write(self.tex)
            tex.close()

            os.popen('xelatex "-output-directory=%s" -interaction=nonstopmode -halt-on-error "%s" > "%s"' \
                      % (tmp_dir,tex_file,out_file))
            
            if self.options.pdftosvg=='1':                      
                os.popen('pdf2svg %s %s'%(pdf_file,svg_file)) 
                self.merge_pdf2svg_svg(svg_file)
            else:
                os.popen('pstoedit -f plot-svg "%s" "%s"  -dt -ssp -psarg -r9600x9600 > "%s" 2> "%s"' \
                          % ( pdf_file,svg_file,out_file,err_file))                
                self.merge_pstoedit_svg(svg_file)

            os.remove(tex_file)
            os.remove(svg_file)
            os.remove(pdf_file)
            os.remove(log_file)
            os.remove(out_file)
            if os.path.exists(err_file):
                os.remove(err_file)
            os.remove(aux_file)
            os.rmdir(tmp_dir)

        
    def merge_pstoedit_svg(self,svg_file):
        def svg_to_group(self,svgin):         
            innode=svgin.tag.rsplit('}',1)[-1]
            # replace svg with group by select specific elements
            if innode=='svg':
                svgout=inkex.etree.Element(inkex.addNS('g','WriteTexNS'))
            else:
                svgout=inkex.etree.Element(inkex.addNS(innode,'WriteTexNS'))
                for att in svgin.attrib:
                    svgout.attrib[att]=svgin.attrib[att]                
                
            for child in svgin.iterchildren():
                tag=child.tag.rsplit('}',1)[-1]
                if tag in ['g','path','line']:
                    child=svg_to_group(self,child)
                    svgout.append(child) 
            return svgout
                    
        doc=inkex.etree.parse(svg_file)
        svg=doc.getroot()
        newnode=svg_to_group(self,svg)
        newnode.attrib['{%s}text'%WriteTexNS]=self.text.encode('string-escape')
        
        replace=False
        
        for i in self.options.ids:
            node=self.selected[i]
            if node.tag != '{%s}g' % SVG_NS: continue            
            if '{%s}text'%WriteTexNS in node.attrib:
                replace=True                
                break
        
        if replace:
            try:                
                if self.options.rescale=='true':
                    newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(800*self.options.scale,800*self.options.scale,
                                                                        -200*self.options.scale,100*self.options.scale)
                else:
                    if node.attrib.has_key('transform'):
                        newnode.attrib['transform']=node.attrib['transform']
                    else:
                        newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(800*self.options.scale,800*self.options.scale,
                                                                        -200*self.options.scale,100*self.options.scale)
                newnode.attrib['style']=node.attrib['style']
            except:
                pass            
            p=node.getparent()
            p.remove(node)
            p.append(newnode)
        else:
            newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(800*self.options.scale,800*self.options.scale,
                                                                        -200*self.options.scale,100*self.options.scale)
            self.current_layer.append(newnode)

    def merge_pdf2svg_svg(self,svg_file):
        def svg_to_group(self,svgin):  
            target={}
            for node in svgin.xpath('//*[@id]'):
                target['#'+node.attrib['id']]=node
                
            for node in svgin.xpath('//*'):
                if node.attrib.has_key('{%s}href'%XLINK_NS):
                    href=node.attrib['{%s}href'%XLINK_NS]
                    p=node.getparent()
                    p.remove(node)
                    trans='translate(%s,%s)'%(node.attrib['x'],node.attrib['y'])
                    for i in target[href].iterchildren():
                        i.attrib['transform']=trans
                        p.append(copy.copy(i))

            svgout = inkex.etree.Element(inkex.addNS('g','WriteTexNS'))
            for node in svgin:
                if node is svgout: continue
                if node.tag == '{%s}defs' % SVG_NS:
                    continue
                svgout.append(node)
            return svgout
                    
        doc=inkex.etree.parse(svg_file)
        svg=doc.getroot()
        newnode=svg_to_group(self,svg)
        newnode.attrib['{%s}text'%WriteTexNS]=self.text.encode('string-escape')
        
        replace=False
            
        for i in self.options.ids:
            node=self.selected[i]
            if node.tag != '{%s}g' % SVG_NS: continue            
            if '{%s}text'%WriteTexNS in node.attrib:
                replace=True
                break
                
        if replace:
            try:
                if self.options.rescale=='true':
                    newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(self.options.scale,self.options.scale,
                                                                        -168*self.options.scale,-100*self.options.scale)
                else:
                    if node.attrib.has_key('transform'):
                        newnode.attrib['transform']=node.attrib['transform']
                    else:
                        newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(self.options.scale,self.options.scale,
                                                                        -168*self.options.scale,-100*self.options.scale)
                newnode.attrib['style']=node.attrib['style']  
            except:
                pass
            p=node.getparent()
            p.remove(node)
            p.append(newnode)
        else:
            self.current_layer.append(newnode)
            newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(self.options.scale,self.options.scale,
                                                                        -168*self.options.scale,-100*self.options.scale)

                   
if __name__ == '__main__':
    e=WriteTex()
    e.affect()