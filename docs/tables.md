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

<iframe style="border:2px solid;" src="../examples/table_captions.html" height="1000" width="100%" title="Iframe Example"></iframe>

Note that internally all tables are numbered, even though the numbering might be turned off.

## Caption Position

By default, the caption is positioned at the top of the table.
The position can be controlled by `caption_position`  parameter, which can be set either to `top` or `bottom`.,

{{ inline_source("docs/examples/table_caption_position.py") }}

<iframe style="border:2px solid;" src="../examples/table_caption_position.html" height="600" width="100%" title="Iframe Example"></iframe>

## Aligning

Tables can be horizontally aligned by `align` parameter, as shown in the following code example.

{{ inline_source("docs/examples/table_align.py") }}

<iframe style="border:2px solid;" src="../examples/table_align.html" height="800" width="100%" title="Iframe Example"></iframe>

## Sorting

It is possible to make the table sortable on all columns by setting `sortable` parameter to `True`,
or by setting `sorting_definition` parameter, which also sorts the table initially on the specified column(s).

Parameter `sorting_definition` expects a list of tuples, where each tuple contains a column index and string `asc`
or `desc`. The table is primarily sorted according to the first tuple, secondarily according to the second tuple, and so
on.

The following snippet shows the usage of both parameters.

!!! note

    Although the columns in `sorting_definition` are indexed from 0, it is necessary to take into account
    also the index when it is displayed. To hide the index, set `index` parameter 
    of [`print_table()`](../api/pyreball_html/#pyreball.html.print_table) method to `False`. 
    `index` parameter is one of the `kwargs` that are passed to pandas `to_html()` method.

{{ inline_source("docs/examples/table_sorting.py") }}

<iframe style="border:2px solid;" src="../examples/table_sorting.html" height="900" width="100%" title="Iframe Example"></iframe>

## Dealing with Large Tables

TBD

## Styling

TBD

For more options, see the styling reference
in [Datatables documentation](https://datatables.net/manual/styling/classes). 