import os
from pathlib import Path

import pkg_resources
import pytest
from pyreball.__main__ import (
    _get_config_directory,
    _get_output_dir_and_file_stem,
    _parse_heading_info,
    _replace_ids,
    insert_heading_title_and_toc,
    parse_arguments,
)
from pyreball.constants import (
    CONFIG_INI_FILENAME,
    HTML_BEGIN_TEMPLATE_FILENAME,
    HTML_END_TEMPLATE_FILENAME,
    STYLES_TEMPLATE_FILENAME,
)


MODULE_PATH = "pyreball.__main__"


@pytest.mark.parametrize(
    "report_before,report_after",
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
                'Reference to chapter <a href="#ref-id123">id123</a>',
                '<h1 id="ch_id123_heading_1_1">My Chapter'
                '<a class="anchor-link" href="#ch_id123_heading_1_1">\u00B6</a></h1>',
                'Reference to chapter <a href="#ref-id123">id123</a> again',
                "</html>",
            ],
            [
                "<html>",
                'Reference to chapter <a href="#ch_heading_1_1">My Chapter</a>',
                '<h1 id="ch_heading_1_1">My Chapter<a class="anchor-link" href="#ch_heading_1_1">\u00B6</a></h1>',
                'Reference to chapter <a href="#ch_heading_1_1">My Chapter</a> again',
                "</html>",
            ],
        ),
    ],
)
def test__replace_ids(report_before, report_after, tmpdir):
    report_dir = Path(tmpdir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.py"

    with open(report_path, "w") as f:
        f.write("\n".join(report_before))

    _replace_ids(report_path)

    with open(report_path) as f:
        result = f.read().split("\n")

    assert result == report_after


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (
            '<h2 id="result_of_addition_2">Result of addition<a class="anchor-link" href="#result_of_addition_2">¶</a></h2>',
            (2, "result_of_addition_2", "Result of addition"),
        ),
        (
            '<h3 id="some_id">Whatever text - is necessary - 999'
            '<a class="anchor-link" href="#result_of_addition_2">¶</a></h3>',
            (3, "some_id", "Whatever text - is necessary - 999"),
        ),
        (
            '<h3 id="some_id">Whatever text - is necessary - 999'
            '<a class="anchor-link" href="#result_of_addition_2">¶</a></h3>',
            (3, "some_id", "Whatever text - is necessary - 999"),
        ),
        (
            '<h3 id="some_id">Whatever text - also <code>code</code> and <b><em>bold emphasis</em></b> - 999'
            '<a class="anchor-link" href="#result_of_addition_2">¶</a></h3>',
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
def test_insert_heading_title_and_toc__with_headings(include_toc, title_set, tmpdir):
    if title_set:
        title = '<title class="custom_pyreball_title">Custom Title</title>'
        expected_toc_heading = "Custom Title"
    else:
        title = "<title>Default Title</title>"
        expected_toc_heading = "Table of Contents"

    report_before = [
        "<html>",
        "<head>",
        title,
        "<head/>",
        "<body>",
        '<div class="main_container">',
        '<h1 id="1_heading_h1_1">1  heading h1<a class="anchor-link" href="#1_heading_h1_1">¶</a></h1>',
        '<h2 id="1_1_heading_h2_2">1.1  heading h2<a class="anchor-link" href="#1_1_heading_h2_2">¶</a></h2>',
        '<h2 id="1_2_heading_h2_3">1.2  heading h2<a class="anchor-link" href="#1_2_heading_h2_3">¶</a></h2>',
        '<h3 id="1_2_1_heading_h3_4">1.2.1  heading h3<a class="anchor-link" href="#1_2_1_heading_h3_4">¶</a></h3>',
        '<h3 id="1_2_2_heading_h3_5">1.2.2  heading h3<a class="anchor-link" href="#1_2_2_heading_h3_5">¶</a></h3>',
        '<h1 id="2_heading_h1_6">2  heading h1<a class="anchor-link" href="#2_heading_h1_6">¶</a></h1>',
        '<h1 id="3_heading_h1_7">3  heading h1<a class="anchor-link" href="#3_heading_h1_7">¶</a></h1>',
        '<h2 id="3_1_heading_h2_8">3.1  heading h2<a class="anchor-link" href="#3_1_heading_h2_8">¶</a></h2>',
        "</div>",
        "</body>",
        "</html>",
    ]

    report_dir = Path(tmpdir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.py"

    with open(report_path, "w") as f:
        f.write("\n".join(report_before))

    insert_heading_title_and_toc(report_path, include_toc=include_toc)

    with open(report_path) as f:
        result = f.read().split("\n")

    expected_title_and_toc = []
    if title_set and not include_toc:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">{expected_toc_heading}<a class="anchor-link" href="#toc_generated_0">¶</a></h1>'
        ]
    elif include_toc:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">{expected_toc_heading}<a class="anchor-link" href="#toc_generated_0">¶</a></h1>',
            '<a href="#1_heading_h1_1">1  heading h1</a><br/>',
            '<ul style="list-style-type:none; margin:0px">',
            '<li><a href="#1_1_heading_h2_2">1.1  heading h2</a></li>',
            '<li><a href="#1_2_heading_h2_3">1.2  heading h2</a></li>',
            '<ul style="list-style-type:none; margin:0px">',
            '<li><a href="#1_2_1_heading_h3_4">1.2.1  heading h3</a></li>',
            '<li><a href="#1_2_2_heading_h3_5">1.2.2  heading h3</a></li>',
            "</ul>",
            "</ul>",
            '<a href="#2_heading_h1_6">2  heading h1</a><br/>',
            '<a href="#3_heading_h1_7">3  heading h1</a><br/>',
            '<ul style="list-style-type:none; margin:0px">',
            '<li><a href="#3_1_heading_h2_8">3.1  heading h2</a></li>',
            "</ul>",
        ]

    report_after = (
        ["<html>", "<head>", title, "<head/>", "<body>", '<div class="main_container">']
        + expected_title_and_toc
        + [
            '<h1 id="1_heading_h1_1">1  heading h1<a class="anchor-link" href="#1_heading_h1_1">¶</a></h1>',
            '<h2 id="1_1_heading_h2_2">1.1  heading h2<a class="anchor-link" href="#1_1_heading_h2_2">¶</a></h2>',
            '<h2 id="1_2_heading_h2_3">1.2  heading h2<a class="anchor-link" href="#1_2_heading_h2_3">¶</a></h2>',
            '<h3 id="1_2_1_heading_h3_4">1.2.1  heading h3<a class="anchor-link" href="#1_2_1_heading_h3_4">¶</a></h3>',
            '<h3 id="1_2_2_heading_h3_5">1.2.2  heading h3<a class="anchor-link" href="#1_2_2_heading_h3_5">¶</a></h3>',
            '<h1 id="2_heading_h1_6">2  heading h1<a class="anchor-link" href="#2_heading_h1_6">¶</a></h1>',
            '<h1 id="3_heading_h1_7">3  heading h1<a class="anchor-link" href="#3_heading_h1_7">¶</a></h1>',
            '<h2 id="3_1_heading_h2_8">3.1  heading h2<a class="anchor-link" href="#3_1_heading_h2_8">¶</a></h2>',
            "</div>",
            "</body>",
            "</html>",
        ]
    )

    assert result == report_after


@pytest.mark.parametrize(
    "title_set",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize("include_toc", [True, False])
def test_insert_heading_title_and_toc__without_headings(include_toc, title_set, tmpdir):
    if title_set:
        title = '<title class="custom_pyreball_title">Custom Title</title>'
    else:
        title = "<title>Default Title</title>"

    report_before = [
        "<html>",
        "<head>",
        title,
        "<head/>",
        "<body>",
        '<div class="main_container">',
        "</div>",
        "</body>",
        "</html>",
    ]

    report_dir = Path(tmpdir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.py"

    with open(report_path, "w") as f:
        f.write("\n".join(report_before))

    insert_heading_title_and_toc(report_path, include_toc=include_toc)

    with open(report_path) as f:
        result = f.read().split("\n")

    expected_title_and_toc = []
    if title_set:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">Custom Title<a class="anchor-link" href="#toc_generated_0">¶</a></h1>'
        ]

    report_after = (
        ["<html>", "<head>", title, "<head/>", "<body>", '<div class="main_container">']
        + expected_title_and_toc
        + [
            "</div>",
            "</body>",
            "</html>",
        ]
    )

    assert result == report_after


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
    (fake_home_path / ".pyreball" / HTML_BEGIN_TEMPLATE_FILENAME).touch()
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
        STYLES_TEMPLATE_FILENAME,
        HTML_BEGIN_TEMPLATE_FILENAME,
        HTML_END_TEMPLATE_FILENAME,
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
        # missing required input-path
        [],
        # Empty string as input-path
        [""],
        # wrong param value
        ["--numbered-plots", "hello", "scripts/report.py"],
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
            {"input-path": Path("scripts/report.py")},
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
                "input-path": Path("scripts/report.py"),
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
                "input-path": Path("scripts/report.py"),
            },
        ),
        (
            ["--align-tables", "left", "scripts/report.py"],
            {"align_tables": "left", "input-path": Path("scripts/report.py")},
        ),
        # now --align-tables is considered scripts-args
        (
            ["scripts/report.py", "--align-tables", "left"],
            {
                "input-path": Path("scripts/report.py"),
                "script-args": ["--align-tables", "left"],
            },
        ),
        # with script-args
        (
            ["scripts/report.py", "-p", "20", "img.png"],
            {
                "input-path": Path("scripts/report.py"),
                "script-args": ["-p", "20", "img.png"],
            },
        ),
        # wrong page-width will be parsed as it is, but fixed later
        (
            ["--page-width", "20", "scripts/report.py"],
            {"page_width": 20, "input-path": Path("scripts/report.py")},
        ),
    ],
)
def test_parse_arguments__valid_arguments(args, expected_non_empty_result):
    expected_result = {
        "align_plots": None,
        "align_tables": None,
        "config_path": None,
        "full_tables": None,
        "input-path": None,
        "keep_stdout": None,
        "matplotlib_embedded": None,
        "matplotlib_format": None,
        "numbered_headings": None,
        "numbered_plots": None,
        "numbered_tables": None,
        "output_path": None,
        "page_width": None,
        "script-args": [],
        "sortable_tables": None,
        "toc": None,
    }
    expected_result.update(**expected_non_empty_result)
    assert parse_arguments(args) == expected_result
