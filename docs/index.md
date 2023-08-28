# Welcome to Pyreball

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
