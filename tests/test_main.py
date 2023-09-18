import os
from pathlib import Path

import pkg_resources
import pytest
from pyreball.__main__ import (
    _contains_class,
    _get_config_directory,
    _get_output_dir_and_file_stem,
    _insert_heading_title_and_toc,
    _insert_js_and_css_links,
    _parse_heading_info,
    _replace_ids,
    parse_arguments,
)
from pyreball.constants import (
    CONFIG_INI_FILENAME,
    HTML_TEMPLATE_FILENAME,
    LINKS_INI_FILENAME,
    STYLES_TEMPLATE_FILENAME,
)


@pytest.mark.parametrize(
    "lines,expected_result",
    [
        (
            [
                "<html>",
                "</html>",
            ],
            [
                "<html>",
                "</html>",
            ],
        ),
        (
            [
                "<html>",
                'Reference to table <a href="#ref-id99">id99</a>',
                'Reference to image <a href="#ref-id17">id17</a>',
                '<a name="img-id17-5">Image caption</a><a name="table-id99-1">Table caption</a>',
                'Reference to table <a href="#ref-id123">id123</a> and image <a href="#ref-id42">id42</a>',
                '<a name="table-id123-2">Another table caption</a>',
                '<a name="img-id42-2">Another image caption</a>',
                'Reference again to table <a href="#ref-id123">id123</a> and image <a href="#ref-id42">id42</a>',
                "</html>",
            ],
            [
                "<html>",
                'Reference to table <a href="#table-1">1</a>',
                'Reference to image <a href="#img-5">5</a>',
                '<a name="img-5">Image caption</a><a name="table-1">Table caption</a>',
                'Reference to table <a href="#table-2">2</a> and image <a href="#img-2">2</a>',
                '<a name="table-2">Another table caption</a>',
                '<a name="img-2">Another image caption</a>',
                'Reference again to table <a href="#table-2">2</a> and image <a href="#img-2">2</a>',
                "</html>",
            ],
        ),
        (
            [
                "<html>",
                'Reference to code block <a href="#ref-id99">id99</a>',
                '<a name="code-block-id99-1">Code caption</a>',
                "</html>",
            ],
            [
                "<html>",
                'Reference to code block <a href="#code-block-1">1</a>',
                '<a name="code-block-1">Code caption</a>',
                "</html>",
            ],
        ),
        (
            [
                "<html>",
                'Reference to chapter <a href="#ref-id123">id123</a>',
                '<h1 id="ch_id123_heading_1_1">My Chapter'
                '<a class="pyreball-anchor-link" href="#ch_id123_heading_1_1">\u00B6</a></h1>',
                'Reference to chapter <a href="#ref-id123">id123</a> again',
                "</html>",
            ],
            [
                "<html>",
                'Reference to chapter <a href="#ch_heading_1_1">My Chapter</a>',
                '<h1 id="ch_heading_1_1">My Chapter<a class="pyreball-anchor-link" href="#ch_heading_1_1">\u00B6</a></h1>',
                'Reference to chapter <a href="#ch_heading_1_1">My Chapter</a> again',
                "</html>",
            ],
        ),
    ],
)
def test__replace_ids(lines, expected_result):
    result = _replace_ids(lines)
    assert result == expected_result


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (
            '<h2 id="result_of_addition_2">Result of addition<a class="pyreball-anchor-link" href="#result_of_addition_2">¶</a></h2>',
            (2, "result_of_addition_2", "Result of addition"),
        ),
        (
            '<h3 id="some_id">Whatever text - is necessary - 999'
            '<a class="pyreball-anchor-link" href="#result_of_addition_2">¶</a></h3>',
            (3, "some_id", "Whatever text - is necessary - 999"),
        ),
        (
            '<h3 id="some_id">Whatever text - is necessary - 999'
            '<a class="pyreball-anchor-link" href="#result_of_addition_2">¶</a></h3>',
            (3, "some_id", "Whatever text - is necessary - 999"),
        ),
        (
            '<h3 id="some_id">Whatever text - also <code>code</code> and <b><em>bold emphasis</em></b> - 999'
            '<a class="pyreball-anchor-link" href="#result_of_addition_2">¶</a></h3>',
            (3, "some_id", "Whatever text - also code and bold emphasis - 999"),
        ),
        ("<div>paragraph</div>", None),
    ],
)
def test_parse_heading_info(test_input, expected_result):
    assert _parse_heading_info(test_input) == expected_result


@pytest.mark.parametrize(
    "title_set",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize("include_toc", [True, False])
def test__insert_heading_title_and_toc__with_headings(include_toc, title_set):
    if title_set:
        title = '<title class="custom_pyreball_title">Custom Title</title>'
        expected_toc_heading = "Custom Title"
    else:
        title = "<title>Default Title</title>"
        expected_toc_heading = "Table of Contents"

    lines = [
        "<html>",
        "<head>",
        title,
        "<head/>",
        "<body>",
        '<div class="pyreball-main-container">',
        '<h1 id="1_heading_h1_1">1  heading h1<a class="pyreball-anchor-link" href="#1_heading_h1_1">¶</a></h1>',
        '<h2 id="1_1_heading_h2_2">1.1  heading h2<a class="pyreball-anchor-link" href="#1_1_heading_h2_2">¶</a></h2>',
        '<h2 id="1_2_heading_h2_3">1.2  heading h2<a class="pyreball-anchor-link" href="#1_2_heading_h2_3">¶</a></h2>',
        '<h3 id="1_2_1_heading_h3_4">1.2.1  heading h3<a class="pyreball-anchor-link" href="#1_2_1_heading_h3_4">¶</a></h3>',
        '<h3 id="1_2_2_heading_h3_5">1.2.2  heading h3<a class="pyreball-anchor-link" href="#1_2_2_heading_h3_5">¶</a></h3>',
        '<h1 id="2_heading_h1_6">2  heading h1<a class="pyreball-anchor-link" href="#2_heading_h1_6">¶</a></h1>',
        '<h1 id="3_heading_h1_7">3  heading h1<a class="pyreball-anchor-link" href="#3_heading_h1_7">¶</a></h1>',
        '<h2 id="3_1_heading_h2_8">3.1  heading h2<a class="pyreball-anchor-link" href="#3_1_heading_h2_8">¶</a></h2>',
        "</div>",
        "</body>",
        "</html>",
    ]

    result = _insert_heading_title_and_toc(lines=lines, include_toc=include_toc)

    expected_title_and_toc = []
    if title_set and not include_toc:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">{expected_toc_heading}<a class="pyreball-anchor-link" href="#toc_generated_0">¶</a></h1>\n'
        ]
    elif include_toc:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">{expected_toc_heading}<a class="pyreball-anchor-link" href="#toc_generated_0">¶</a></h1>\n',
            '<a href="#1_heading_h1_1">1  heading h1</a><br/>\n',
            '<ul style="list-style-type:none; margin:0px">\n',
            '<li><a href="#1_1_heading_h2_2">1.1  heading h2</a></li>\n',
            '<li><a href="#1_2_heading_h2_3">1.2  heading h2</a></li>\n',
            '<ul style="list-style-type:none; margin:0px">\n',
            '<li><a href="#1_2_1_heading_h3_4">1.2.1  heading h3</a></li>\n',
            '<li><a href="#1_2_2_heading_h3_5">1.2.2  heading h3</a></li>\n',
            "</ul>\n",
            "</ul>\n",
            '<a href="#2_heading_h1_6">2  heading h1</a><br/>\n',
            '<a href="#3_heading_h1_7">3  heading h1</a><br/>\n',
            '<ul style="list-style-type:none; margin:0px">\n',
            '<li><a href="#3_1_heading_h2_8">3.1  heading h2</a></li>\n',
            "</ul>\n",
        ]

    expected_result = (
        [
            "<html>",
            "<head>",
            title,
            "<head/>",
            "<body>",
            '<div class="pyreball-main-container">',
        ]
        + expected_title_and_toc
        + [
            '<h1 id="1_heading_h1_1">1  heading h1<a class="pyreball-anchor-link" href="#1_heading_h1_1">¶</a></h1>',
            '<h2 id="1_1_heading_h2_2">1.1  heading h2<a class="pyreball-anchor-link" href="#1_1_heading_h2_2">¶</a></h2>',
            '<h2 id="1_2_heading_h2_3">1.2  heading h2<a class="pyreball-anchor-link" href="#1_2_heading_h2_3">¶</a></h2>',
            '<h3 id="1_2_1_heading_h3_4">1.2.1  heading h3<a class="pyreball-anchor-link" href="#1_2_1_heading_h3_4">¶</a></h3>',
            '<h3 id="1_2_2_heading_h3_5">1.2.2  heading h3<a class="pyreball-anchor-link" href="#1_2_2_heading_h3_5">¶</a></h3>',
            '<h1 id="2_heading_h1_6">2  heading h1<a class="pyreball-anchor-link" href="#2_heading_h1_6">¶</a></h1>',
            '<h1 id="3_heading_h1_7">3  heading h1<a class="pyreball-anchor-link" href="#3_heading_h1_7">¶</a></h1>',
            '<h2 id="3_1_heading_h2_8">3.1  heading h2<a class="pyreball-anchor-link" href="#3_1_heading_h2_8">¶</a></h2>',
            "</div>",
            "</body>",
            "</html>",
        ]
    )

    assert result == expected_result


@pytest.mark.parametrize(
    "title_set",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize("include_toc", [True, False])
def test__insert_heading_title_and_toc__without_headings(include_toc, title_set):
    if title_set:
        title = '<title class="custom_pyreball_title">Custom Title</title>'
    else:
        title = "<title>Default Title</title>"

    lines = [
        "<html>",
        "<head>",
        title,
        "<head/>",
        "<body>",
        '<div class="pyreball-main-container">',
        "</div>",
        "</body>",
        "</html>",
    ]

    result = _insert_heading_title_and_toc(lines=lines, include_toc=include_toc)

    expected_title_and_toc = []
    if title_set:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">Custom Title<a class="pyreball-anchor-link" href="#toc_generated_0">¶</a></h1>\n'
        ]

    report_after = (
        [
            "<html>",
            "<head>",
            title,
            "<head/>",
            "<body>",
            '<div class="pyreball-main-container">',
        ]
        + expected_title_and_toc
        + [
            "</div>",
            "</body>",
            "</html>",
        ]
    )

    assert result == report_after


@pytest.mark.parametrize(
    "html_text,class_name,expected_result",
    [
        ("", "inline", False),
        ('<div class="inline"></div>', "inline", True),
        ('<div class="another"></div>', "another", True),
        ("<div class='inline'></div>", "inline", True),
        ('<div class="  hi inline ok  "></div>', "inline", True),
        ('<div class = "  hi \n inline ok \n  "></div>', "inline", True),
        ('<div class="  hi ok  ">inline</div>', "inline", False),
        ('<div class="  hi ok  " inline></div>', "inline", False),
        ('<div class="" inline></div>', "inline", False),
    ],
)
def test__contains_class(html_text, class_name, expected_result):
    assert _contains_class(html_text, class_name) == expected_result


@pytest.mark.parametrize(
    "html_content,external_links,expected_result",
    [
        (
            "",
            {"bokeh": ["l1", "l2"], "altair": ["l3"]},
            "",
        ),
        (
            (
                "<html><!--PYREBALL_HEAD_LINKS-->"
                '<div class="pyreball-bokeh-fig">'
                "</div></html>"
            ),
            {"bokeh": ["l1", "l2"], "altair": ["l3"]},
            '<html>l1\nl2<div class="pyreball-bokeh-fig"></div></html>',
        ),
        (
            (
                "<html><!--PYREBALL_HEAD_LINKS-->"
                '<div class="pyreball-altair-fig">'
                "</div>"
                '<div class="pyreball-table-wrapper">'
                "</div>"
                '<div class="pyreball-plotly-fig">'
                "</div>"
                '<div class="pyreball-code-wrapper">'
                "</div>"
                "</html>"
            ),
            {
                "altair": ["l1", "l2"],
                "jquery": ["l4"],
                "highlight_js": ["l3"],
                "datatables": ["l5"],
                "plotly": ["l6"],
            },
            (
                "<html>l4\nl1\nl2\nl5\nl3\nl6"
                '<div class="pyreball-altair-fig">'
                "</div>"
                '<div class="pyreball-table-wrapper">'
                "</div>"
                '<div class="pyreball-plotly-fig">'
                "</div>"
                '<div class="pyreball-code-wrapper">'
                "</div>"
                "</html>"
            ),
        ),
    ],
)
def test__insert_js_and_css_links(html_content, external_links, expected_result):
    assert _insert_js_and_css_links(html_content, external_links) == expected_result


def test__get_config_directory__custom_path_does_not_exist(tmpdir):
    tmpdir = Path(tmpdir)
    config_dir = "my_config_dir"
    with pytest.raises(NotADirectoryError):
        _get_config_directory(config_dir_path=tmpdir / config_dir)


def test__get_config_directory__custom_path_with_incomplete_files(tmpdir):
    tmpdir = Path(tmpdir)
    config_dir = "my_config_dir"
    (tmpdir / config_dir).mkdir()
    (tmpdir / config_dir / CONFIG_INI_FILENAME).touch()
    with pytest.raises(FileNotFoundError):
        _get_config_directory(config_dir_path=tmpdir / config_dir)


def test__get_config_directory__home_path_with_incomplete_files(tmpdir, mocker):
    tmpdir = Path(tmpdir)
    fake_home_path = tmpdir / "my_home"
    mocker.patch.object(Path, "home", return_value=fake_home_path)
    (fake_home_path / ".pyreball").mkdir(parents=True)
    (fake_home_path / ".pyreball" / HTML_TEMPLATE_FILENAME).touch()
    with pytest.raises(FileNotFoundError):
        _get_config_directory(config_dir_path=None)


@pytest.mark.parametrize(
    "config_path,home_config_exists,expected_result_unresolved",
    [
        # Path from CLI argument is used
        (Path("my_config_dir/"), False, Path("my_config_dir")),
        # Path from CLI argument is used
        (Path("my_config_dir"), True, Path("my_config_dir")),
        # Path from home
        (None, True, Path("my_home/.pyreball")),
        # Path from installation directory
        (None, False, Path(pkg_resources.resource_filename("pyreball", "cfg"))),
    ],
)
def test__get_config_directory__valid_conditions(
    config_path, home_config_exists, expected_result_unresolved, tmpdir, mocker
):
    tmpdir = Path(tmpdir)
    fake_home_path = tmpdir / "my_home"
    mocker.patch.object(Path, "home", return_value=fake_home_path)

    # Setup
    os.chdir(tmpdir)
    required_filename = [
        CONFIG_INI_FILENAME,
        LINKS_INI_FILENAME,
        STYLES_TEMPLATE_FILENAME,
        HTML_TEMPLATE_FILENAME,
    ]
    config_dir = "my_config_dir"
    (tmpdir / config_dir).mkdir()
    for filename in required_filename:
        (tmpdir / config_dir / filename).touch()
    if home_config_exists:
        (fake_home_path / ".pyreball").mkdir(parents=True)
        for filename in required_filename:
            (fake_home_path / ".pyreball" / filename).touch()

    expected_result = expected_result_unresolved.resolve()

    # Test
    result = _get_config_directory(config_dir_path=config_path)
    assert result == expected_result


def test__get_output_dir_and_file_stem__input_file_does_not_exist(tmpdir):
    input_path = Path(tmpdir) / "input.py"
    with pytest.raises(FileNotFoundError):
        _get_output_dir_and_file_stem(input_path=input_path, output_path_str=None)


@pytest.mark.parametrize(
    "input_path," "output_path_str," "expected_output_dir," "expected_filename_stem",
    [
        (Path("script.py"), None, "", "script"),
        (Path("a/b/script.py"), None, "a/b", "script"),
        (Path("script.py"), Path("output.html"), "", "output"),
        (Path("script.py"), Path("x/y/output.html"), "x/y", "output"),
        (Path("a/b/script.py"), Path("x/y/output.html"), "x/y", "output"),
        (Path("script.py"), Path("x/y"), "x/y", "script"),
        (Path("script.py"), Path("x/y/"), "x/y", "script"),
        (Path("script.py"), Path("output.unsupported"), "output.unsupported", "script"),
    ],
)
def test__get_output_dir_and_file_stem__valid_inputs(
    input_path,
    output_path_str,
    expected_output_dir,
    expected_filename_stem,
    tmpdir,
):
    os.chdir(tmpdir)
    input_path.parents[0].mkdir(parents=True, exist_ok=True)
    input_path.touch()

    result_output_dir_path, result_filename_stem = _get_output_dir_and_file_stem(
        input_path, output_path_str
    )
    expected_output_dir_path = tmpdir / expected_output_dir
    assert result_output_dir_path == expected_output_dir_path
    assert result_filename_stem == expected_filename_stem


@pytest.mark.parametrize(
    "args",
    [
        # missing required input_path
        [],
        # Empty string as input_path
        [""],
        # wrong param value
        ["--numbered-figures", "hello", "scripts/report.py"],
        # empty string for path option
        # white-space string for path option
        ["--output-path", "\n    \n", "scripts/report.py"],
        # The same for --config-path
        ["--config-path", "\n    \n", "scripts/report.py"],
    ],
)
def test_parse_arguments__invalid_arguments(args):
    with pytest.raises(SystemExit):
        assert parse_arguments(args)


@pytest.mark.parametrize(
    "args,expected_non_empty_result",
    [
        # only the required argument
        (
            ["scripts/report.py"],
            {"input_path": Path("scripts/report.py")},
        ),
        # with some table parameters
        (
            [
                "--tables-display-option",
                "paging",
                "--tables-scroll-y-height",
                "500px",
                "--tables-paging-sizes",
                "20,all",
                "scripts/report.py",
            ],
            {
                "tables_display_option": "paging",
                "tables_scroll_y_height": "500px",
                "tables_paging_sizes": "20,all",
                "input_path": Path("scripts/report.py"),
            },
        ),
        # with path arguments
        (
            [
                "--output-path",
                "my_output.html",
                "--config-path",
                "dir/my_config/",
                "scripts/report.py",
            ],
            {
                "output_path": Path("my_output.html"),
                "config_path": Path("dir/my_config/"),
                "input_path": Path("scripts/report.py"),
            },
        ),
        # --output-path can also link to a directory
        (
            [
                "--output-path",
                "my_dir/my_subdir",
                "scripts/report.py",
            ],
            {
                "output_path": Path("my_dir/my_subdir"),
                "input_path": Path("scripts/report.py"),
            },
        ),
        (
            ["--align-tables", "left", "scripts/report.py"],
            {"align_tables": "left", "input_path": Path("scripts/report.py")},
        ),
        # now --align-tables is considered scripts-args
        (
            ["scripts/report.py", "--align-tables", "left"],
            {
                "input_path": Path("scripts/report.py"),
                "script_args": ["--align-tables", "left"],
            },
        ),
        # with script_args
        (
            ["scripts/report.py", "-p", "20", "img.png"],
            {
                "input_path": Path("scripts/report.py"),
                "script_args": ["-p", "20", "img.png"],
            },
        ),
        # wrong page-width will be parsed as it is, but fixed later
        (
            ["--page-width", "20", "scripts/report.py"],
            {"page_width": 20, "input_path": Path("scripts/report.py")},
        ),
    ],
)
def test_parse_arguments__valid_arguments(args, expected_non_empty_result):
    expected_result = {
        "toc": None,
        "align_code_blocks": None,
        "code_block_captions_position": None,
        "numbered_code_blocks": None,
        "align_tables": None,
        "table_captions_position": None,
        "numbered_tables": None,
        "tables_display_option": None,
        "tables_scroll_y_height": None,
        "tables_scroll_x": None,
        "sortable_tables": None,
        "tables_paging_sizes": None,
        "tables_search_box": None,
        "tables_datatables_style": None,
        "align_figures": None,
        "figure_captions_position": None,
        "numbered_figures": None,
        "matplotlib_format": None,
        "matplotlib_embedded": None,
        "numbered_headings": None,
        "page_width": None,
        "keep_stdout": None,
        "output_path": None,
        "config_path": None,
        "input_path": None,
        "script_args": [],
    }
    expected_result.update(**expected_non_empty_result)
    assert parse_arguments(args) == expected_result
