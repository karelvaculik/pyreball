# Basic Printing

## Printing to an HTML File

To create any HTML report, core printing functionality of Pyreball must be used.
The basic approach is to use [`print()`](../api/pyreball_html/#pyreball.html.print) function, which can be used to print
values into the output HTML file.

Simple usage is demonstrated in the following script:

{{ inline_source("docs/examples/basic_print.py") }}

Which just adds the text into the HTML document:

<iframe style="border:2px solid;" src="../examples/basic_print.html" height="100" width="100%" title="Iframe Example"></iframe>

It is possible to pass multiple arguments, each of which is converted to a string if necessary.
The following example encloses several values into a `<div>` element.

{{ inline_source("docs/examples/basic_print_multi.py") }}

<iframe style="border:2px solid;" src="../examples/basic_print_multi.html" height="100" width="100%" title="Iframe Example"></iframe>

The previous example can be reproduced with a shortcut
function [`print_div()`](../api/pyreball_html/#pyreball.html.print_div):

{{ inline_source("docs/examples/basic_print_div.py") }}

<iframe style="border:2px solid;" src="../examples/basic_print_div.html" height="100" width="100%" title="Iframe Example"></iframe>

[`print_div()`](../api/pyreball_html/#pyreball.html.print_div) function combines
[`print()`](../api/pyreball_html/#pyreball.html.print) and [`div()`](../api/pyreball_text/#pyreball.text.div) function.
[`div()`](../api/pyreball_text/#pyreball.text.div) is one of the text util functions which are demonstrated in
[`Text Utils`](../text_utils/) chapter.

Another shortcut function is [`print_code_block()`](../api/pyreball_html/#pyreball.html.print_code_block).

{{ inline_source("docs/examples/basic_print_code.py") }}

<iframe style="border:2px solid;" src="../examples/basic_print_code.html" height="150" width="100%" title="Iframe Example"></iframe>

[`print_code_block()`](../api/pyreball_html/#pyreball.html.print_code_block) wraps the values into `<pre>`
and `<code>` elements and uses [highlight.js](https://highlightjs.org/) library to highlight the syntax.
Pyreball currently supports only Python language with default theme.

## Adding a Title

To add a title to the page, use [`set_title()`](../api/pyreball_html/#pyreball.html.set_title) function.

{{ inline_source("docs/examples/basic_print_title.py") }}

<iframe style="border:2px solid;" src="../examples/basic_print_title.html" height="200" width="100%" title="Iframe Example"></iframe>

It creates a `<h1>` title at the top of the page and sets also the `<title>` element with the same value.
Note that [`set_title()`](../api/pyreball_html/#pyreball.html.set_title) does not need to be called at the top of the
script, but it is recommended to do so for better readability.

## Adding Headings

Every report should be structured properly into sections and subsections.
This can be achieved simply by
using [`print_h1()`](../api/pyreball_html/#pyreball.html.print_h1), ...,
[`print_h6()`](../api/pyreball_html/#pyreball.html.print_h6) functions.

{{ inline_source("docs/examples/basic_print_headings.py") }}

<iframe style="border:2px solid;" src="../examples/basic_print_headings.html" height="500" width="100%" title="Iframe Example"></iframe>

As can be seen from the generated HTML document, these functions don't just wrap text into `<h*>` elements.
Pyreball also creates a table of contents with links to individual headings.
Moreover, it adds a [pilcrow sign](https://en.wikipedia.org/wiki/Pilcrow) to each heading to create an anchor.

The table of contents, as well as heading numbers can be turned off by using either
Pyreball's [CLI parameters](../cli_parameters/) or [config file](../config_file/).

## Title vs. Headings

The main difference between [`set_title()`](../api/pyreball_html/#pyreball.html.set_title)
and [`print_h1()`](../api/pyreball_html/#pyreball.html.print_h1), ...,
[`print_h6()`](../api/pyreball_html/#pyreball.html.print_h6) functions is
that [`set_title()`](../api/pyreball_html/#pyreball.html.set_title) can be applied anywhere and it always changes the
title at the very beginning of the document, whereas [`print_h1()`](../api/pyreball_html/#pyreball.html.print_h1), ...,
[`print_h6()`](../api/pyreball_html/#pyreball.html.print_h6) functions create headings sequentially as they are called.

Moreover, title created by [`set_title()`](../api/pyreball_html/#pyreball.html.set_title) is not included in the table
of contents and it also sets the value of `<title>` element.

Last, but not least, when title is set, it is also used instead of the `Table of Contents` heading, see example below.

{{ inline_source("docs/examples/basic_print_title_with_headings.py") }}

<iframe style="border:2px solid;" src="../examples/basic_print_title_with_headings.html" height="400" width="100%" title="Iframe Example"></iframe>