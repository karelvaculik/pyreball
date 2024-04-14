# Pyreball

<p style="text-align: center">

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)
[![pypi](https://img.shields.io/pypi/v/pyreball.svg)](https://pypi.python.org/pypi/pyreball)
[![Tests](https://github.com/karelvaculik/pyreball/actions/workflows/tests.yml/badge.svg)](https://github.com/karelvaculik/pyreball/actions/workflows/tests.yml)

</p>

Pyreball is a Python reporting tool that generates HTML reports from Python scripts.

Main features:

- Plots in [Vega-Altair](https://altair-viz.github.io/index.html), [Plotly](https://plotly.com/), [Bokeh](https://bokeh.org/), and [Matplotlib](https://matplotlib.org/) (and thus also [Seaborn](https://seaborn.pydata.org/) etc.).
- Interactive tables based on [DataTables](https://datatables.net/) library and created from [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).
- Basic text formatting such as headings, emphasis, and lists.
- Hyperlinks, references and table of contents.

The main motivation is to allow users to create persistent reports in the form of HTML pages from scripts retaining the
Python syntax.
The advantage of using *regular* Python scripts as the source of these HTML pages is that they are easy to maintain, can
be refactored quickly through various IDEs, etc.

Pyreball is designed not to require any dependencies, unless you decide to use them. For example, if you decide to print
pandas DataFrames to HTML tables and plot altair charts, you need to install pandas and altair.

## Install

```shell
pip install pyreball
```

## Quick Example

Create a regular python script, for example `report.py`:

```python
import matplotlib.pyplot as plt
import pandas as pd
import pyreball as pb
import seaborn as sns

pb.set_title("Pyreball Illustration")

pb.print_h1("Introduction")

pb.print_div(
    "Pyreball has many features, among others:",
    pb.ulist(
        "Plots in altair, plotly, bokeh, and matplotlib (and thus also seaborn etc.).",
        "Sortable and scrollable tables from pandas DataFrame.",
        f'Basic text formatting such as {pb.bold("headings")}, {pb.em("emphasis")}, and {pb.code("lists")}.',
        f'{pb.link("hyperlinks", "https://www.python.org/")}, references and table of contents.',
    ),
)

pb.print_h1("Tables and Plots")

# Print a table
df = pd.DataFrame({"x": [1, 2, 3], "y": [4, 6, 5]})
pb.print_table(df, caption="A data table.")

# Plot a graph
fig, ax = plt.subplots()
sns.lineplot(x="x", y="y", ax=ax, data=df)
ax.set(xlabel="x", ylabel="y")
pb.print_figure(fig, caption="The first plot.")
```

In this particular example, we are using a few 3rd party packages, so let's install them too:

```shell
pip install pandas matplotlib seaborn
```

Then generate an HTML report by running:

```shell
pyreball report.py
```

`pyreball` command will generate `report.html` with the final report that should look like this:

![Pyreball Screenshot](pyreball_result_screenshot.png)

## Documentation

See [documentation](https://pyreball.readthedocs.io/) for more examples and information about Pyreball.

## Setting up Pyreball in PyCharm

There is no plugin but you can use it as an "external tool".

In PyCharm, go `PyCharm -> Preferences... -> Tools -> External Tools` and add a new tool with the following settings:

- Name: `pyreball`
- Description: `pyreball`
- Program: `$PyInterpreterDirectory$/pyreball`
- Arguments: `$FilePath$`
- Working directory: `$ProjectFileDir$`

Then it is possible to run `pyreball` on the open Python script by clicking
`Tools -> External Tools -> pyreball` or by right-clicking on the script and then selecting
`External Tools -> pyreball` from the context menu.

The work can be simplified even further by creating action icon for `pyreball` in the main toolbar. Navigate to
appropriate menu by opening
`PyCharm -> Preferences -> Appearance & Behavior -> Menus and Toolbars -> Main Toolbar ...`, where you *add action*
that will point to external tool `pyreball`. It is also possible to set up a keyboard shortcut for this external tool
in `PyCharm -> Preferences -> Keymap`.
