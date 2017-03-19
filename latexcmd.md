# Customize LaTeX command

> This is an advanced option, if you do not know what you are doing, probably you should leave the default value as is.

The `LaTeX` command used to complie LaTeX string into pdf is now adjustable. An example is shown here:

`xelatex "-output-directory={tmp_dir}" -interaction=nonstopmode -halt-on-error "{tex_file}" > "{out_file}"`

There are three options can be used to specified:

`{tmp_dir}`: this will be replaced by the directory of temporary directory used.

`{tex_file}`: this will be replaced by the path of the temporary TeX file.

`{out_file}`: this will replaced by the path of the output PDF file.

By default, `xelatex` and `pdflatex` are supported. You just need to type in `xelatex` or `pdflatex` to obtain the correct command for these two LaTeX commands. For other distribution, you will need to write you own command. Feel free to contribute your command for your preferred LaTeX distribution.

Best regards and happy LaTeXing.

## [Go back](/)
