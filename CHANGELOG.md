# Changelog

## 1.0.0 (2023-09-11)

- Added new text elements `div()` and `span()`. Added new parameters to HTML elements - in particular `cl` and `attrs`.
- Replaced `print_html()` function with `print()`.
- Replaced `print_code()` function with `print_source_code()`.
- Replaced `plot_graph()` with `print_figure()`.
- Removed `plot_multi_graph`.
- Replaced code-prettify with highlight.js for code blocks.
- `print_h1`, ..., `print_h6` functions can now take a `Reference` object.
- Added `--config-path` CLI option, changed how `pyreball-generate-config` command works and how the config paths are
  handled.
- Updated CLI arguments and config parameters for tables and figures.
- Updated template files.
- Updated to newer versions of 3rd party dependencies for example.
- Created documentation at readthedocs.

## 0.1.1 (2021-09-14)

- Added `replace_newlines_with_br` parameter to `print_div` to control replacement of newline characters.
- It is newly possible to pass custom script arguments.
- Replaced `--output-dir` parameter with `--output-path` parameter.

## 0.1.0 (2021-09-02)

- Initial version moved to github.