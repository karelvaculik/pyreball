# Tables

Pyreball allows printing [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) objects
into HTML tables by using [`print_table()`](../api/pyreball_html/#pyreball.html.print_table) function.

## Basic Usage

The simplest usage is to provide just the `DataFrame` object:

{{ inline_source("docs/examples/table_simplest.py") }}

<iframe style="border:2px solid;" src="../examples/table_simplest.html" height="300" width="100%" title="Iframe Example"></iframe>

## Captions

All tables are numbered by default, which causes creation of `Table 1.` table caption above.
It is possible to provide custom caption via `caption` parameter, as well as to control the numbering of form `Table k.`
via `numbered` parameter.

{{ inline_source("docs/examples/table_captions.py") }}

<iframe style="border:2px solid;" src="../examples/table_captions.html" height="800" width="100%" title="Iframe Example"></iframe>

Note that internally all tables are numbered, even though the numbering might be turned off.

## Aligning

Tables can be horizontally aligned by `align` parameter, as shown in the following code example.

{{ inline_source("docs/examples/table_align.py") }}

<iframe style="border:2px solid;" src="../examples/table_align.html" height="700" width="100%" title="Iframe Example"></iframe>

## Sorting

It is possible to make the table sortable on all columns by setting `sortable` parameter to `True`,
or by setting `sorting_definition` parameter, which also sorts the table initially on the specified column.

{{ inline_source("docs/examples/table_sorting.py") }}

<iframe style="border:2px solid;" src="../examples/table_sorting.html" height="800" width="100%" title="Iframe Example"></iframe>

## Dealing with Large Tables

TBD
