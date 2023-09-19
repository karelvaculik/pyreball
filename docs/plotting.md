# Plotting

Pyreball currently supports plotting figures created
by [Matplotlib](https://matplotlib.org/), [Seaborn](https://seaborn.pydata.org/), [Vega-Altair](https://altair-viz.github.io/index.html),
[Plotly](https://plotly.com/), and [Bokeh](https://bokeh.org/).

There is a single function [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure) for all these libraries.
Similarly to [`print_table()`](../api/pyreball_html/#pyreball.html.print_table), it uses
parameters `caption`, `align`, `caption_position` and `numbered` with the same meaning.
In contrast to table captions, the default position of figure captions is `bottom`.

## Matplotlib

When plotting with Matplotlib, it is necessary to create a figure object and pass it
to [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure).

In case of Matplotlib, a user can select the format of the figure via `matplotlib_format` parameter: either `"png"`
or `"svg"`.
In case of `"svg"`, it is also possible to choose whether the figure should be embedded into the HTML file 
or saved into a separate file and referenced in the HTML file by setting `embedded` accordingly.
Figures in `"png"` format cannot be embedded into the HTML file.

When the figure is stored into a file, the file is saved in a directory with name equal to the filename stem of the HTML
file. For example, for HTML file `report.html`, the image file will be stored in directory `report`.

The following code shows an example of a bar chart created with Matplotlib and stored in a `"png"` format.

{{ inline_source("docs/examples/plotting_matplotlib_png.py") }}

<iframe style="border:2px solid;" src="../examples/plotting_matplotlib_png.html" height="540" width="100%" title="Iframe Example"></iframe>

The next example shows the same chart, but embedded directly into the HTML document in `"svg"` format.

{{ inline_source("docs/examples/plotting_matplotlib_svg.py") }}

<iframe style="border:2px solid;" src="../examples/plotting_matplotlib_svg.html" height="540" width="100%" title="Iframe Example"></iframe>

## Seaborn

Seaborn is based on Matplotlib and therefore the code is very similar. It is also necessary to create a figure,
which is then passed to Pyreball. It is also possible to use parameters `matplotlib_format` and `embedded`.

{{ inline_source("docs/examples/plotting_seaborn.py") }}

<iframe style="border:2px solid;" src="../examples/plotting_seaborn.html" height="540" width="100%" title="Iframe Example"></iframe>

## Vega-Altair

For Vega-Altair charts, Pyreball does not offer any special parameters like for Matplotlib and Seaborn charts.
The charts are always embedded into the HTML and kept interactive.

{{ inline_source("docs/examples/plotting_vega_altair.py") }}

<iframe style="border:2px solid;" src="../examples/plotting_vega_altair.html" height="540" width="100%" title="Iframe Example"></iframe>

The previous example used `altair.Chart` object, but other types of charts are also supported,
e.g. `altair.ConcatChart`, `altair.HConcatChart`.

## Plotly

Pyreball supports interactive charts created by Plotly, too.

{{ inline_source("docs/examples/plotting_plotly.py") }}

<iframe style="border:2px solid;" src="../examples/plotting_plotly.html" height="540" width="100%" title="Iframe Example"></iframe>

## Bokeh

Another library for plotting interactive charts supported by Pyreball is Bokeh.

{{ inline_source("docs/examples/plotting_bokeh.py") }}

<iframe style="border:2px solid;" src="../examples/plotting_bokeh.html" height="700" width="100%" title="Iframe Example"></iframe>
