# Changelog

## 1.0.0 (2023-09-19)

- Created documentation at readthedocs.
- Replaced `print_html()` function with `print()`.
- Replaced `print_code()` function with `print_code_block()`.
- Replaced `plot_graph()` with `print_figure()`.
- Removed `plot_multi_graph`. An example how to achieve the same is now in docs.
- Replaced code-prettify with highlight.js for code blocks.
- `print_h1`, ..., `print_h6` functions can now take a `Reference` object.
- Added new text elements `div()`, `span()`, `code()`, `code_block()`, `a()`, and `tag()`. 
  Replaced `ol()` and `ul()` with `olist()` and `ulist()`.
- Added new parameters to almost all HTML elements - in particular parameters `cl` and `attrs`.
- Updated various CLI arguments and config parameters.
- Updated template and config files.
- Updated support for newer versions of 3rd party dependencies in examples.

## 0.1.1 (2021-09-14)

- Added `replace_newlines_with_br` parameter to `print_div` to control replacement of newline characters.
- It is newly possible to pass custom script arguments.
- Replaced `--output-dir` parameter with `--output-path` parameter.

## 0.1.0 (2021-09-02)

- Initial version moved to github.