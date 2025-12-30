''' Latex to MathML interface '''
import re
import latex2mathml.tokenizer
import latex2mathml.commands
from latex2mathml.converter import convert

from .config import config


def declareoperator(name: str) -> None:
    r''' Declare a new operator name, similar to Latex ``\DeclareMathOperator`` command.

        Args:
            name: Name of operator, should start with a ``\``.
                Example: ``declareoperator(r'\myfunc')``
    '''
    latex2mathml.commands.FUNCTIONS = latex2mathml.commands.FUNCTIONS + (name,)  # type: ignore


def tex2mml(tex: str, inline: bool = False) -> str:
    ''' Convert Latex to MathML. Do some hacky preprocessing to work around
        some issues with generated MathML that ziamath doesn't support yet.
    '''
    tex = re.sub(r'\\binom{(.+?)}{(.+?)}', r'\\left( \1 \\atop \2 \\right)', tex)
    # latex2mathml bug requires space after mathrm
    tex = re.sub(r'\\mathrm{(.+?)}', r'\\mathrm {\1}', tex)
    tex = tex.replace('||', '‖')
    tex = tex.replace(r'\begin{aligned}', r'\begin{align*}')
    tex = tex.replace(r'\end{aligned}', r'\end{align*}')

    if config.decimal_separator == ',':
        # Replace , with {,} to remove right space
        # (must be surrounded by digits)
        tex = re.sub(r'([0-9]),([0-9])', r'\1{,}\2', tex)

    mml = convert(tex, display='inline' if inline else 'block')

    # Tex \uparrow, \downarrow are not stretchy,
    # but in MathML they are (as drawn by Katex and Mathjax).
    # Keep the operators list as stretchy, but set to false when
    # processing tex.
    mml = re.sub(r'>&#x02191;', r' stretchy="false">&#x02191;', mml)  # \uparrow
    mml = re.sub(r'>&#x02193;', r' stretchy="false">&#x02193;', mml)  # \downarrow
    mml = re.sub(r'<mi>&#x027E8;', r'<mi stretchy="false">&#x027E8;', mml)  # \langle
    mml = re.sub(r'<mi>&#x027E9;', r'<mi stretchy="false">&#x027E9;', mml)  # \rangle

    # Replace some operators with "stretchy" variants
    mml = re.sub(r'<mo stretchy="false">&#x0005E;', r'<mo stretchy="false">&#710;', mml)  # hat
    mml = re.sub(r'<mo>&#x0005E;', r'<mo>&#x00302;', mml)  # widehat
    mml = re.sub(r'<mo>&#x0007E;', r'<mo>&#x00303;', mml)  # widetilde

    # shrink the huge column spacing in \align to something more reasonable
    mml = re.sub(r'columnspacing="0em 2em"', r'columnspacing="0em 0.3em"', mml)
    return mml
