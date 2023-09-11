# References

Sometimes it might be useful to create a link to a table, an image or a chapter in the HTML document.
Pyreball enables creation of such links with ease through [`Reference`](../api/pyreball_html/#pyreball.html.Reference)
class.

Specifically, one can create a reference object by calling `pb.Reference()`.
This object can be then passed to a function that creates a
table ([`print_table()`](../api/pyreball_html/#pyreball.html.print_table)),
a figure ([`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure)), or
a heading ([`print_h1()`](../api/pyreball_html/#pyreball.html.print_h1), ...,
[`print_h6()`](../api/pyreball_html/#pyreball.html.print_h6)).
Each such function then creates a target for the link.
To create a source, just retrieve the string representation of the reference (i.e.
use [`__str__()`](../api/pyreball_html/#pyreball.html.Reference.__str__) method), or invoke a
call on the reference object (i.e. use [`__call__()`](../api/pyreball_html/#pyreball.html.Reference.__call__) method).

The following snippet demonstrates a very simple usage of a reference object.

{{ inline_source("docs/examples/references_simple.py") }}

<iframe style="border:2px solid;" src="../examples/references_simple.html" height="300" width="100%" title="Iframe Example"></iframe>

The code above creates a reference object with default link text `My Table` and the reference object is assigned to the
table.
The code also creates three instances of the same link pointing to the
table. [`__str__()`](../api/pyreball_html/#pyreball.html.Reference.__str__) method uses the default string
that we passed to the constructor.
The last link was created by [`__call__()`](../api/pyreball_html/#pyreball.html.Reference.__call__) method, which takes
a parameter that is used to override the default link
text.

When default link text is not provided through the constructor, Pyreball uses table numbers as texts for links pointing
to tables. The same is applied for links pointing to figures. 
In case of headings, the default link text would be the text of the heading itself.

The artificial example below demonstrates some of these features.

{{ inline_source("docs/examples/references.py") }}

<iframe style="border:2px solid;" src="../examples/references.html" height="800" width="100%" title="Iframe Example"></iframe>

!!! note

    Creating references explicitly through the constructor of [`Reference`](../api/pyreball_html/#pyreball.html.Reference)
    class allows us to use the reference object even before the target object is created. 
    This would not be possible if the references were created by functions like 
    [`print_table()`](../api/pyreball_html/#pyreball.html.print_table).