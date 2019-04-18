[WriteTeX](https://wanglongqi.github.io/WriteTeX/)
========

If you like this plugin, please star this project. It helps me to evaluate whether this plugin is needed. Thanks!

如果你喜欢这个插件，请star这个项目，这可以帮助我了解这个插件的需求。谢谢！

You may also want to check [WriteTeX<sup>2</sup>](https://github.com/wanglongqi/WriteTeX2).

<img src=https://github.com/wanglongqi/WriteTeX/raw/master/writetex.png width=300px alt=Logo>

An Inkscape extension: Latex/Tex editor for Inkscape, inspired by [textext](http://pav.iki.fi/software/textext/).

This extension uses Inkscape build-in extension system, does not require TK or PyGtk as textext. Live preview feature is supported. You can obtain original TeX source from View Original TeX tab.

## Installation
Just drop `writetex.py` and `writetex.inx` to Inkscape extension folder, which is normally at `$inkscapeFolder$/share/extensions`. 

**Make sure one `LaTeX` command and one `PDFtoSVG` converter are in your path.**

### Notes on `PDFTOSVG`

`PDFTOSVG` must be installed and added to your search path, otherwise you will get error like "IOError: Error reading file `somesvg.svg`". One supported `PDFTOSVG` is `pdf2svg`, which can be downloaded following locations:

- For Windows user, `pdf2svg` can be downloaded from [here](https://github.com/wanglongqi/WriteTeX/releases/download/v1.1/pdf2svg-x64.7z) or [here](https://github.com/dawbarton/pdf2svg). 
- For Mac user, `pdf2svg` can be installed by homebrew, or download from [here](https://github.com/wanglongqi/WriteTeX/releases/download/v1.6.1/pdf2svg-MacOSX.7z).

## More info
Can be found in the [website](https://wanglongqi.github.io/WriteTeX/).
