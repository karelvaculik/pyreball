# Custom Building Blocks

Although Pyreball provides several ways to customize the reports and construct various elements,
sometimes it might be necessary to create other building blocks.

This page shows an example with stacked figures that can be switched with buttons.
First, the code adds two JavaScript functions that enable the necessary interactivity.
Next, a function for wrapping multiple figures into a common block is implemented and used.
The user can then switch between figures by clicking the buttons `<` and `>`.

{{ inline_source("docs/examples/custom_multi_figure.py") }}

<iframe style="border:2px solid;" src="../examples/custom_multi_figure.html" height="1200" width="100%" title="Iframe Example"></iframe>
