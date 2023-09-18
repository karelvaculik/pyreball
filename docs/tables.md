# Tables

Pyreball allows printing [pandas DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html) objects
into HTML tables with [`print_table()`](../api/pyreball_html/#pyreball.html.print_table) function.
Moreover, Pyreball uses [DataTables](https://datatables.net/) library to add styling and interactivity to the tables.

## Basic Usage

The simplest usage is to provide just a `DataFrame` object:

{{ inline_source("docs/examples/table_simplest.py") }}

<iframe style="border:2px solid;" src="../examples/table_simplest.html" height="300" width="100%" title="Iframe Example"></iframe>

## Captions

All tables are numbered by default, which causes creation of `Table 1.` caption above.
It is possible to provide custom caption text via `caption` parameter.
To control whether `Table k.` prefix should be displayed, `numbered` Boolean parameter can be set accordingly.

{{ inline_source("docs/examples/table_captions.py") }}

<iframe style="border:2px solid;" src="../examples/table_captions.html" height="1000" width="100%" title="Iframe Example"></iframe>

!!! note

    All tables are internally numbered, even though the numbering might be turned off for specific tables, as shown
    in the previous example.

## Caption Position

By default, the caption is positioned above the table.
The position can be controlled by `caption_position`  parameter, which can be set either to `top` or `bottom`.

{{ inline_source("docs/examples/table_caption_position.py") }}

<iframe style="border:2px solid;" src="../examples/table_caption_position.html" height="600" width="100%" title="Iframe Example"></iframe>

## Aligning Tables

Tables can be horizontally aligned by `align` parameter, as shown in the following example.

{{ inline_source("docs/examples/table_align.py") }}

<iframe style="border:2px solid;" src="../examples/table_align.html" height="800" width="100%" title="Iframe Example"></iframe>

## Aligning Columns

Numeric columns are aligned to right and columns of other types to left, by default.
This behaviour can be changed through `col_align` parameter.
The parameter takes either a string (to set the same alignment for all columns), or a list of strings 
(to set the alignment of each column individually). 
When a list is provided and index is displayed, the list must contain also values for the index columns.


{{ inline_source("docs/examples/table_align_columns.py") }}

<iframe style="border:2px solid;" src="../examples/table_align_columns.html" height="800" width="100%" title="Iframe Example"></iframe>


## Sorting

It is possible to make the table sortable on all columns by setting `sortable` parameter to `True`,
or by setting `sorting_definition` parameter, which also sorts the table initially on the specified column(s).

Parameter `sorting_definition` expects a list of tuples, where each tuple contains a column index and string `asc`
or `desc`. The table is primarily sorted according to the first tuple, secondarily according to the second tuple, and so
on.

The following snippet shows the usage of both parameters.

!!! note

    Although the columns in `sorting_definition` are indexed from 0, it is necessary to take into account
    also the table index when it is displayed. To hide the index, set `index` parameter 
    of [`print_table()`](../api/pyreball_html/#pyreball.html.print_table) method to `False`. 
    `index` parameter is one of the `kwargs` parameters that are passed to [Pandas](https://pandas.pydata.org/)
    `to_html()` method, which is used internally by Pyreball.

{{ inline_source("docs/examples/table_sorting.py") }}

<iframe style="border:2px solid;" src="../examples/table_sorting.html" height="1200" width="100%" title="Iframe Example"></iframe>

## Dealing with Large Tables

Each table is fully displayed by default. This is caused by keeping the `display_option` parameter 
to its default value `full`.
However, this might not be practical for large tables.

One solution is to allow vertical scrolling of the table by setting `display_option` to `scrolling`.
To change the default height of the table, set also `scroll_y_height` parameter.

{{ inline_source("docs/examples/table_scrolling.py") }}

<iframe style="border:2px solid;" src="../examples/table_scrolling.html" height="800" width="100%" title="Iframe Example"></iframe>

!!! note

    By default, Pyreball turns on horizontall scrolling on each table  as can be seen in the previous example.
    You can turn it off by setting `scroll_x` parameter to `False`. This, however, might cause the table to overflow
    the container.

Another option is to set `display_option` to `paging`. This option can be further customized by providing custom page
sizes through `paging_sizes` parameter. Currently, `paging_sizes` takes a list of integers mixed with string `All` (the
case of the letters does not matter, so it can be `all` or `ALL` as well). When `All` is used, Pyreball interprets it as
showing all entries on a single page.

{{ inline_source("docs/examples/table_paging.py") }}

<iframe style="border:2px solid;" src="../examples/table_paging.html" height="800" width="100%" title="Iframe Example"></iframe>

## Searching

To allow searching within a table, just set `search_box` to `True`.

{{ inline_source("docs/examples/table_searching.py") }}

<iframe style="border:2px solid;" src="../examples/table_searching.html" height="360" width="100%" title="Iframe Example"></iframe>

## Complex Headers and Indices

[Pandas](https://pandas.pydata.org/) allows its users to create complex (multi-level) headers and indices.
Such tables can be also printed into HTML, which creates additional columns and header rows, as can be seen in the
following example. The code snippet also shows how to display index columns as regular columns.

{{ inline_source("docs/examples/table_multiindex.py") }}

<iframe style="border:2px solid;" src="../examples/table_multiindex.html" height="800" width="100%" title="Iframe Example"></iframe>

The example also shows that when defining sorting on columns via `sorting_definition` parameter,
a user must take into account index columns too.
Index columns must be also taken into account when setting `col_align` parameter.

!!! note

    Pyreball sets `sparsify` parameter of [Pandas](https://pandas.pydata.org/) `to_html()` method to `False`, 
    because [DataTables](https://datatables.net/) would not be able to display tables with a multi-index correctly,
    especially not with sortable columns. This is also the reason why the identical `team` values
    are not merged in the first table above.

## Styling

Tables are also styled with the help of [DataTables](https://datatables.net/) library.
The default styling class used is `display`.
To change the styling, use parameter `datatables_style`, which takes either a single string with a class name,
or a list of class names.
Usable class names are listed in the styling reference
of [Datatables documentation](https://datatables.net/manual/styling/classes).

{{ inline_source("docs/examples/table_styling.py") }}

<iframe style="border:2px solid;" src="../examples/table_styling.html" height="500" width="100%" title="Iframe Example"></iframe>

## Custom DataTables Configuration

Most of the parameters in the previous sections were just setting up the parameters of `DataTable` JavaScript object
in some predefined manner.
It is possible to completely override such parameters by providing custom dictionary via `datatables_definition`
parameter. This dictionary is then serialized into JSON and passed to the `DataTable` JavaScript object.

{{ inline_source("docs/examples/table_datatables_definition.py") }}

<iframe style="border:2px solid;" src="../examples/table_datatables_definition.html" height="660" width="100%" title="Iframe Example"></iframe>
