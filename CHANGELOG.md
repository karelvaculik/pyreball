# Changelog

## 0.2.0 (2023-08-18)

- Updated to newer versions of optional dependencies.
- Added new text elements `div` and `span`. Added new parameters to HTML elements - in particular `cl` and `attrs`.
- Deprecated `print_html` function. New `print` should be used instead.
- Deprecated `print_code` function. New `print_source_code` should be used instead.
- Replaced code-prettify with highlight.js for code blocks.

## 0.1.1 (2021-09-14)

- Added `replace_newlines_with_br` parameter to `print_div` to control replacement of newline characters.
- It is newly possible to pass custom script arguments.
- Replaced `--output-dir` parameter with `--output-path` parameter.

## 0.1.0 (2021-09-02)

- Initial version moved to github.