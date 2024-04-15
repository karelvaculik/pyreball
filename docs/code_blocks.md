# Code Blocks

Printing a snippet of a source code into HTML can be done in several ways with Pyreball.
Chapter [`Text Utils`](../text_utils/) already showed functions that can be used to
prepare code elements.

Another approach is to
use [`print_code_block()`](../api/pyreball_html/#pyreball.html.print_code_block)
function,
which prints the code block and brings some additional features.
The function wraps the values into `<pre>` and `<code>` elements and
uses [highlight.js](https://highlightjs.org/)
library to highlight the syntax.

Basic usage is demonstrated in the following example.

{{ inline_source("docs/examples/code_blocks_basic.py") }}

<iframe style="border:2px solid;" src="../examples/code_blocks_basic.html" height="160" width="100%" title="Iframe Example"></iframe>

The language can be again set via `syntax_highlight` parameter.
The supported languages are listed in the highlight.js'
[Supported Languages table](https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md).

As with tables, a custom caption can be added and its position can be controlled through
`caption` and `caption_position` parameters.
The horizontal alignment of the code block can be also changed using `align` parameter.
Last but not least, numbering can be turned off by setting `numbered` to False.

{{ inline_source("docs/examples/code_blocks_params.py") }}

<iframe style="border:2px solid;" src="../examples/code_blocks_params.html" height="400" width="100%" title="Iframe Example"></iframe>
