# Text Utils

To create strings with various HTML elements simply, Pyreball provides various text utility functions.
These functions return a string that can be directly printed into the HTML file.

Each function takes zero or more values which are all automatically converted to strings and concatenated with a
separator passed through `sep` parameter. It is also possible to set the `class` HTML attribute through `cl` function
parameter, or any HTML attribute through a more general `attrs` parameter.

## Grouping Elements

To group or enclose zero or more elements into `<div>` or `<span>` elements, use corresponding
functions [`div()`](../api/pyreball_text/#pyreball.text.div) and [`span()`](../api/pyreball_text/#pyreball.text.span).

{{ inline_source("docs/examples/text_utils_grouping.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_grouping.html" height="200" width="100%" title="Iframe Example"></iframe>

## Setting HTML Attributes

[`div()`](../api/pyreball_text/#pyreball.text.div), [`span()`](../api/pyreball_text/#pyreball.text.span) and other
functions
provide parameters `cl`, `attrs` and `sep`. Let's see them in action.

{{ inline_source("docs/examples/text_utils_parameters.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_parameters.html" height="200" width="100%" title="Iframe Example"></iframe>

In particular, we set the class of the first `<div>` to value `text-centered`, for which there is actually an entry in
included CSS for aligning text to center.

In the case of the second `<div>`, we set `style` attribute through `attrs` parameter. Moreover, we set `sep` to `"\n"`,
which adds newlines to the output HTML file between the elements instead of putting all elements on a single line.
Therefore, it just formats differently the content of the HTML file. To insert a line break visually into the shown
HTML, it is necessary to print `<br>` element.

Last, but not least, we also set `sep` to `"\n"` in the [`print()`](../api/pyreball_html/#pyreball.html.print) function
to create a line break between the `<div>` elements themselves in the output HTML file.

## Basic Text Formatting

To format text, [`bold()`](../api/pyreball_text/#pyreball.text.bold)
and [`em()`](../api/pyreball_text/#pyreball.text.em)
can be used.

{{ inline_source("docs/examples/text_utils_formatting.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_formatting.html" height="100" width="100%" title="Iframe Example"></iframe>

## Code Formatting

When including a source code string into a text, [`code()`](../api/pyreball_text/#pyreball.text.code)
and [`code_block()`](../api/pyreball_text/#pyreball.text.code_block) can be used to format it.
The former wraps values into `<code>` element and can be used inline, whereas the latter wraps values into `<pre><code>`
and is displayed as a block element.

{{ inline_source("docs/examples/text_utils_code.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_code.html" height="200" width="100%" title="Iframe Example"></iframe>

## Creating Hyperlinks

There are two functions for creating hyperlinks. The first one is [`a()`](../api/pyreball_text/#pyreball.text.a),
which contains all the parameters as other text util functions:

{{ inline_source("docs/examples/text_utils_links_full.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_links_full.html" height="100" width="100%" title="Iframe Example"></iframe>

The second one is [`link()`](../api/pyreball_text/#pyreball.text.link), which is a shortcut that contains just two
parameters: `text` and `href`.

{{ inline_source("docs/examples/text_utils_links_shortcut.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_links_shortcut.html" height="100" width="100%" title="Iframe Example"></iframe>

## Lists

To create unordered and ordered lists, Pyreball provides [`ulist()`](../api/pyreball_text/#pyreball.text.ulist)
and [`olist()`](../api/pyreball_text/#pyreball.text.olist) functions, respectively.

{{ inline_source("docs/examples/text_utils_lists.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_lists.html" height="250" width="100%" title="Iframe Example"></iframe>

Each value is automatically wrapped into `<li>` element and then the whole groupt is wrapped either to `<ul>` or `<ol>`
element, depending on whether [`ulist()`](../api/pyreball_text/#pyreball.text.ulist)
or [`olist()`](../api/pyreball_text/#pyreball.text.olist) is used.
Because there are two types of elements used, `cl` and `attrs` parameters are use for the outer `<ul>` or `<ol>`
element, and special `li_cl` and `li_attrs` parameters are used for the inner `<li>` elements.

Pyreball also allows nesting the lists inside each other. Because HTML requires nested list to be wrapped together with
a parent element inside a common `<li>` element, Pyreball solves this by using a tuple in such a case, see example
below.

{{ inline_source("docs/examples/text_utils_nested_lists.py") }}

<iframe style="border:2px solid;" src="../examples/text_utils_nested_lists.html" height="250" width="100%" title="Iframe Example"></iframe>

Adding a list item without a sublist can be achieved by providing a single value (as in the case of item `A` in the
example above), or packing it into a tuple with an empty string (as in the case of `D` item). The latter approach might
be more appropriate when the data are generated automatically and the types of all items needs to be the same.

## Custom HTML Tags

It is possible to use [`tag()`](../api/pyreball_text/#pyreball.text.tag) function to create tags that are not
implemented
directly by `pyreball`.

For example, paired tag `<pre>` and unpaired tag `<hr>` can be created and used as follows:

{{ inline_source("docs/examples/custom_tags.py") }}

<iframe style="border:2px solid;" src="../examples/custom_tags.html" height="200" width="100%" title="Iframe Example"></iframe>
