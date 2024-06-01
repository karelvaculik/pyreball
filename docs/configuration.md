# Configuration and CLI Arguments

Pyreball uses a few configuration and template files when generating an HTML file.
Its behaviour can be also controlled via optional CLI arguments.
This section describes how to work with these files and CLI arguments.

## CLI Arguments

Pyreball contains various arguments that can be displayed by:

```shell
pyreball --help
```

Typical `pyreball` call could be summarized as:

```shell
pyreball <pyreball options> <Python script path> <Python script args>
```

The simplest call is only with the Python script path.
This positional argument can be, however, replaced with `-m` option, which specifies 
a module.
The following two example commands show alternative ways of specifying the path:
```shell
pyreball my_package/my_script.py
pyreball -m my_package.my_script
```

Pyreball behaviour can be controlled via various pyreball options that are further described below.
There can be also arguments for the script (module) itself, in which case they need to be separated from other arguments and options by `--`.
Internally, Pyreball uses current executable `python` and executes the script with it, passing the script arguments to the script (module).

An example of a script with custom arguments:

{{ inline_source("docs/examples/script_with_args.py") }}

Then we can pass arguments as follows:

```shell
pyreball --page-width=90 script_with_args.py -- --sum 23 25 24
```

<iframe style="border:2px solid;" src="../examples/script_with_args.html" height="200" width="100%" title="Iframe Example"></iframe>

In this example, script `script_with_args.py` uses option `--sum` followed by one or more numbers.

By default, Pyreball re-uses the input script path to construct the output HTML file path, only changing the `.py`
suffix to `.html`.
If `-m` option is used to specify a module, the module path is converted to regular path and the process is the same.
The output path can be modified by option `--output-path`.
If the output path ends with `.html`, it is interpreted as HTML file path. If not, it is interpreted as a directory,
where the HTML file should be created. In such a case, the HTML file will have the same filename stem as the input
script (e.g., `my_report.py` will produce `my_report.html`).

Another optional argument is `--config-path`, which can be used to override the directory path with configuration files.
More information about configuration files and how `--config-path` is used can be found in the following sections.

Other CLI options are tightly coupled with settings in configuration files and function parameters and are thus
described at one place in
section [config.ini vs. CLI arguments vs. function arguments](#configini-vs-cli-arguments-vs-function-arguments).

## Config Files

When Pyreball is installed, it also creates a config directory with a few files in the installation directory.
This directory contains HTML and CSS templates as well as configuration files `config.ini` and `external_links.ini`.

### Template files

There are currently two template files:

* `css.template` - Contains CSS definitions that are inserted into the final HTML file. Only width of the main container
  is dynamically set here at the moment.
* `html.template` - Contains the template of the HTML file. It contains three placeholders:
    * `<!--PYREBALL_PAGE_TITLE-->` - Here goes the title set
      by [`set_title()`](../api/pyreball_html/#pyreball.html.set_title)
      function
      or Table-of-Contents title. If the title is not set, nor Table-of-Contents is created, the filename stem is used
      at least as the value of `<title>` element.
    * `<!--PYREBALL_HEAD_LINKS-->` - Placeholder for necessary `<link>` and `<script>` elements with 3rd party library
      links. Pyreball decides dynamically which links need to be added. Links from `external_links.ini` are used here.
    * `<!--PYREBALL_CSS_DEFINITIONS-->` - The CSS definitions from `styles.template` are inserted here.
    * `<!--PYREBALL_REPORT_CONTENTS-->` - Everything that Pyreball generates from the source Python script goes here.
      Specifically, Pyreball initializes the HTML file with the text placed before this placeholder, then adds contents
      from the Python script, and finishes the HTML by adding the text placed after this placeholder.
    * `<!--PYREBALL_INLINE_HIGHLIGHT_SCRIPT-->` - Placeholder for inline JavaScript code that highlights syntax of
      inline code snippets. Pyreball decides dynamically whether the script should be included or not.

### external_links.ini File

When using 3rd party libraries to display various elements, necessary JavaScript and CSS links need to be added to the
HTML page. Such links are selected from `external_links.ini` file.
Each key-value pair represents a library with relevant links. For example, if your Pyreball report creates
a [Bokeh](https://bokeh.org/) figure in the HTML, relevant JavaScript references for [Bokeh](https://bokeh.org/) are
added to the HTML `<head>` element.
Some libraries, e.g. [DataTables](https://datatables.net/), require also [jQuery](https://jquery.com/), which is listed
separately in `external_links.ini`.

All links in `external_links.ini` are fixed except for Bokeh links.
Bokeh links contain placeholder `{BOKEH_VERSION}`, which is replaced by the version of installed `bokeh` package during report generation by Pyreball.

### config.ini File

`config.ini` file controls behaviour of Pyreball as well as how various elements should be displayed in the final HTML.
The default `config.ini` looks like this:

{{ inline_source("src/pyreball/cfg/config.ini", "cfg") }}

Detailed description is provided in
section [config.ini vs. CLI arguments vs. function arguments](#configini-vs-cli-arguments-vs-function-arguments).

### Modifying Config Files

If you need to modify any configuration files, it is not recommended to modify them directly, because they serve
as default settings.
It is rather recommended to generate a copy of these defaults and modify it.
This can be achieved by running `pyreball-generate-config` command, which is also available after installing Pyreball.

When executed without any arguments, it copies the default configuration files into `~/.pyreball` directory, where
you can change them:

```shell
pyreball-generate-config
```

The output directory can be changed with `--output-dir` parameter. For example, to copy the files into `config`
subdirectory of the current working directory, run:

```shell
pyreball-generate-config --output-dir ./config
```

!!! warning

    Improper modification of the configuration files might break the functionality of Pyreball.

## config.ini vs. CLI arguments vs. function arguments

Several aspects of Pyreball's behaviour can be changed through `config.ini` file, `pyreball` CLI arguments, or function
parameters. The following table shows parameter alternatives for these three options.

!!! note

    Acceptable values mentioned in the table below are primarily intended for `config.ini` and CLI arguments.
    The function arguments might be slightly different, so it's recommended to see appropriate API documentation
    of the given function. For example, instead of values `yes` and `no`, the functions usually use Boolean values 
    `True` and `False`.

| `config.ini` key               | CLI argument                     | Function argument                                                                                  | Description                                                                                                                                                                                                                                              |
|--------------------------------|----------------------------------|----------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `page-width`                   | `--page-width`                   | _N/A_                                                                                              | Width of the page container in percentage. Allowed values: An integer in the range 40..100.                                                                                                                                                              |
| `keep-stdout`                  | `--keep-stdout`                  | _N/A_                                                                                              | Whether to print the output to stdout too: `yes`, `no`.                                                                                                                                                                                                  |
| `toc`                          | `--toc `                         | _N/A_                                                                                              | Include table of contents. It is included only when there are some headings. Allowed values: `yes`, `no`.                                                                                                                                                |
| `numbered-headings`            | `--numbered-headings`            | _N/A_                                                                                              | Whether to number headings. Allowed values: `yes`, `no`.                                                                                                                                                                                                 |
| `align-code-blocks`            | `--align-code-blocks`            | `align` in [`print_code_block()`](../api/pyreball_html/#pyreball.html.print_code_block)            | Horizontal alignment of code blocks. Allowed values: `left`, `center`, `right`.                                                                                                                                                                          |
| `code-block-captions-position` | `--code-block-captions-position` | `caption_position` in [`print_code_block()`](../api/pyreball_html/#pyreball.html.print_code_block) | Caption position for code blocks. Allowed values: `top`, `bottom`.                                                                                                                                                                                       |
| `numbered-code-blocks`         | `--numbered-code-blocks`         | `numbered` in [`print_code_block()`](../api/pyreball_html/#pyreball.html.print_code_block)         | Whether to number code blocks. Allowed values: `yes`, `no`.                                                                                                                                                                                              |
| `align-tables`                 | `--align-tables`                 | `align` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)                      | Horizontal alignment of tables. Allowed values: `left`, `center`, `right`.                                                                                                                                                                               |
| `table-captions-position`      | `--table-captions-position`      | `caption_position` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)           | Caption position for tables. Allowed values: `top`, `bottom`.                                                                                                                                                                                            |
| `numbered-tables`              | `--numbered-tables`              | `numbered` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)                   | Whether to number tables. Allowed values: `yes`, `no`.                                                                                                                                                                                                   |
| `tables-display-option`        | `--tables-display-option`        | `display_option` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)             | How to display tables. This option is useful for long tables, which should not be displayed fully. Allowed values are: `full` (show the full table), `scrolling` (show the table in scrolling mode on y-axis), `paging` (show the table in paging mode). |
| `tables-paging-sizes`          | `--tables-paging-sizes`          | `paging_sizes` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)               | The paging sizes that can be selected. Ignored when `tables-display-option` is not `paging`. Allowed values are integers and string `all` (no matter the case of letters), written as a non-empty comma-separated list.                                  |
| `tables-scroll-y-height`       | `--tables-scroll-y-height`       | `scroll_y_height` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)            | Height of the tables when `tables-display-option` is set to `scrolling`. Any string compatible with CSS sizing can be used, e.g. `300px`, `20em`, etc.                                                                                                   |
| `tables-scroll-x`              | `--tables-scroll-x`              | `scroll_x` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)                   | Whether to allow scrolling on the x-axis. If turned off, a wide table is allowed to overflow the main container. It is recommended to turn this on. Allowed values: `yes`, `no`.                                                                         |
| `sortable-tables`              | `--sortable-tables`              | `sortable` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)                   | Whether to make columns in tables sortable. Allowed values: `yes`, `no`.                                                                                                                                                                                 |
| `tables-search-box`            | `--tables-search-box`            | `search_box` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)                 | Whether to show the search box for tables. Allowed values: `yes`, `no`.                                                                                                                                                                                  |
| `tables-datatables-style`      | `--tables-datatables-style`      | `datatables_style` in [`print_table()`](../api/pyreball_html/#pyreball.html.print_table)           | Datatables class(es) that affect the styling of tables. If multiple classes are provided, they must be separated either with commas or spaces. See [DataTables documentation](https://datatables.net/manual/styling/classes) for possible values.        |
| `align-figures`                | `--align-figures`                | `align` in [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure)                    | Horizontal alignment of figures. Allowed values: `left`, `center`, `right`.                                                                                                                                                                              |
| `figure-captions-position`     | `--figure-captions-position`     | `caption_position` in [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure)         | Caption position for figures. Allowed values: `top`, `bottom`.                                                                                                                                                                                           |
| `numbered-figures`             | `--numbered-figures`             | `numbered` in [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure)                 | Whether to number figures. Allowed values: `yes`, `no`.                                                                                                                                                                                                  |
| `matplotlib-format`            | `--matplotlib-format`            | `matplotlib_format` in [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure)        | Format of matplotlib (and thus also seaborn) figures. Allowed values: `png`, `svg`.                                                                                                                                                                      |
| `matplotlib-embedded`          | `--matplotlib-embedded`          | `embedded` in [`print_figure()`](../api/pyreball_html/#pyreball.html.print_figure)                 | Whether to embedded matplotlib (and thus also seaborn) figures directly into HTML. Only for svg format. Allowed values: `yes`, `no`.                                                                                                                     |

The reason for having multiple options for setting these values is to allow the user to set some properties globally,
while others locally as needed for particular scripts.

When evaluating which value is used, the following order is considered:

1. If the function parameter is not `None`, use it. Otherwise,
2. If the CLI option is used, use its value. Otherwise,
3. If `--config-path` CLI option is used, use value of `config.ini` referenced by this option. Otherwise,
4. If `~/.pyreball` directory with `config.ini` file exists, use value from this config file. Otherwise,
5. Use value of the default `config.ini` from the installation directory.
