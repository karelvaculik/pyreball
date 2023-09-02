# Pyreball

Pyreball is a Python reporting tool that generates HTML reports from Python scripts.

Main features:

- Plots in altair, plotly, bokeh, and matplotlib (and thus also seaborn etc.).
- Sortable and scrollable tables from pandas DataFrame.
- Basic text formatting such as headings, emphasis, and lists.
- Hyperlinks, references and table of contents.

The main motivation is to allow users to create persistent reports in the form of HTML pages from scripts retaining the
Python syntax.
The advantage of using *regular* Python scripts as the source of these HTML pages is that they are easy to maintain, can
be refactored quickly through various IDEs, etc.

Pyreball is designed not to require any dependencies, unless you decide to use them. For example, if you decide to print
pandas DataFrames to HTML tables and plot altair charts, you need to install pandas and altair.

Note that Pyreball is still in early stages of development, so there can be some breaking changes between released
versions.

## Installation

```shell
pip install pyreball
```

## First Report

Create a python script, for example named `report.py`:

{{ inline_source("docs/examples/example_init.py") }}

Now run `pyreball` on this script as

```
pyreball report.py
```

`pyreball` will create `report.html` that should look like this when opened in a browser:

<iframe style="border:2px solid;" src="examples/example_init.html" height="350" width="100%" title="Iframe Example"></iframe>

## Adding Tables and Plots

The core functionality of `pyreball` does not require any 3rd party dependencies.
However, it is possible to generate other types of elements with the help of libraries such
as [pandas](https://pandas.pydata.org/) or [seaborn](https://seaborn.pydata.org/).

Let's create another python script called `report_plot.py`:

{{ inline_source("docs/examples/example_init_deps.py") }}

Install `pandas` and `seaborn`, then run `pyreball`:

```
pip install pandas seaborn
pyreball report_plot.py
```

`report_plot.html` should look like this:

<iframe style="border:2px solid;" src="examples/example_init_deps.html" height="800" width="100%" title="Iframe Example"></iframe>
