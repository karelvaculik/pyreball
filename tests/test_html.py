import datetime
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict
from unittest import mock

import altair as alt
import pandas as pd
import plotly.express as px
import pytest
import seaborn as sns
from bokeh.plotting import figure as bokeh_figure
from matplotlib import pyplot as plt

from pyreball.html import (
    _check_and_mark_reference,
    _code_block_memory,
    _compute_length_menu_for_datatables,
    _construct_image_anchor_link,
    _gather_datatables_setup,
    _get_heading_number,
    _graph_memory,
    _heading_memory,
    _parse_tables_paging_sizes,
    _prepare_altair_image_element,
    _prepare_bokeh_image_element,
    _prepare_caption_element,
    _prepare_col_alignment_definition,
    _prepare_image_element,
    _prepare_matplotlib_image_element,
    _prepare_plotly_image_element,
    _prepare_table_html,
    _print_figure,
    _print_heading,
    _reduce_whitespaces,
    _references,
    _table_memory,
    _tidy_title,
    _wrap_code_block_html,
    _wrap_image_element_by_outer_divs,
    _write_to_html,
    print as print_html,
    print_code_block,
    print_div,
    print_figure,
    print_h1,
    print_h2,
    print_h3,
    print_h4,
    print_h5,
    print_h6,
    print_table,
    Reference,
    set_title,
)


@pytest.fixture
def simple_html_file(tmpdir):
    html_file = Path(tmpdir) / "report.html"

    with open(html_file, "w") as f:
        f.write("<html>\n")

    return str(html_file)


def get_simple_dataframe():
    return pd.DataFrame({"x1": [1, 2, 3], "x2": ["a", "b", "c"]})


@pytest.fixture
def simple_dataframe():
    return get_simple_dataframe()


@pytest.fixture
def pre_test_print_heading_cleanup():
    # _print_heading is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    global _heading_memory
    _heading_memory.clear()
    yield


@pytest.fixture
def pre_test_check_and_mark_reference_cleanup():
    # _check_and_mark_reference is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    global _references
    _references.clear()
    yield


@pytest.fixture
def pre_test_print_code_block_cleanup():
    # print_code_block is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    global _code_block_memory
    _code_block_memory.clear()
    yield


@pytest.fixture
def pre_test_print_table_cleanup():
    # print_table is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    global _table_memory
    _table_memory.clear()
    yield


@pytest.fixture
def pre_test_print_figure_cleanup():
    # _print_figure is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    global _graph_memory
    _graph_memory.clear()
    yield


def test_reference__without_default_text():
    ref = Reference()
    ref_string = str(ref)
    regex_match = re.match(r'^<a href="#ref-id(\d+)">id(\d+)</a>$', ref_string)
    assert regex_match is not None
    assert regex_match.group(1) == regex_match.group(2)


def test_reference__with_default_text():
    ref = Reference("whatever")
    ref_string = str(ref)
    regex_match = re.match(r'^<a href="#ref-id(\d+)">whatever</a>$', ref_string)
    assert regex_match is not None


def test_reference__with_default_text_and_text_override():
    ref = Reference("whatever")
    ref_string = ref("nevermind")
    regex_match = re.match(r'^<a href="#ref-id(\d+)">nevermind</a>$', ref_string)
    assert regex_match is not None


def test__check_and_mark_reference(pre_test_check_and_mark_reference_cleanup):
    ref1 = Reference()
    ref2 = Reference()
    ref3 = Reference()
    ref1.id = "1"
    ref2.id = "1"
    ref3.id = "2"

    _check_and_mark_reference(ref1)
    with pytest.raises(ValueError):
        # a reference with this id was already marked
        _check_and_mark_reference(ref2)

    _check_and_mark_reference(ref3)
    with pytest.raises(ValueError):
        # a reference with this id was already marked
        _check_and_mark_reference(ref3)


def test_set_title__stdout(capsys):
    with mock.patch("pyreball.html.get_parameter_value", return_value=False):
        set_title("my title")
        captured = capsys.readouterr()
        assert captured.out.strip() == "my title"


@pytest.mark.parametrize("keep_stdout", [True])
def test_set_title__file_output(keep_stdout, capsys, simple_html_file):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        else:
            return None

    with open(simple_html_file, "a") as f:
        f.write("<title>old title</title>\n</html>")

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        set_title("new title with more words")
        with open(simple_html_file, "r") as f:
            result = f.read()
            expected_result = '<html>\n<title class="custom_pyreball_title">new title with more words</title>\n</html>'
            assert result == expected_result

    captured = capsys.readouterr()
    expected_stdout = "new title with more words" if keep_stdout else ""
    assert captured.out.strip() == expected_stdout


def test__write_to_html(simple_html_file):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        _write_to_html("<div>")
        with open(simple_html_file, "r") as f:
            result = f.read()
            assert result == "<html>\n<div>\n"


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        ("", ""),
        ("42%", "42_percent"),
        ("one 53 two &**) three.exe and,no", "one_53_two_three_exe_and_no"),
        ("This is a  \t 42simple \n Sen&*tence", "this_is_a_42simple_sentence"),
    ],
)
def test__tidy_title(test_input, expected_result):
    assert _tidy_title(test_input) == expected_result


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        ("", ""),
        ("  Hello    world   ", "Hello world"),
    ],
)
def test_reduce_whitespaces(test_input, expected_result):
    assert _reduce_whitespaces(test_input) == expected_result


@pytest.mark.parametrize(
    "test_input_1,test_input_2,expected_result",
    [
        (1, [1, 1, 1, 1], "1"),
        (1, [1, 2, 1, 1], "1"),
        (1, [1, 1, 2, 1], "1"),
        (1, [1, 1, 1, 2], "1"),
        (2, [1, 2, 3, 4], "1.2"),
        (2, [2, 1, 3, 4], "2.1"),
        (3, [1, 2, 3, 4], "1.2.3"),
        (4, [1, 2, 3, 4], "1.2.3.4"),
        (4, [4, 3, 2, 1], "4.3.2.1"),
    ],
)
def test_get_heading_number(test_input_1, test_input_2, expected_result):
    assert (
        _get_heading_number(level=test_input_1, l_heading_counting=test_input_2)
        == expected_result
    )


@pytest.mark.parametrize("level", [0, 7])
def test__print_heading__unsupported_level(level, pre_test_print_heading_cleanup):
    with pytest.raises(ValueError):
        _print_heading("whatever", level)


def test__print_heading__stdout(capsys, pre_test_print_heading_cleanup):
    def fake_get_parameter_value(key):
        return key in ["keep_stdout", "numbered_headings"]

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        _print_heading("simple heading", level=3)
        captured = capsys.readouterr()
        assert "0.0.1 simple heading" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch(
        "pyreball.html.get_parameter_value",
        side_effect=fake_get_parameter_value_different,
    ):
        _print_heading("another heading", level=5)
        captured = capsys.readouterr()
        assert "another heading" in captured.out


@pytest.mark.parametrize("keep_stdout", [False, True])
@pytest.mark.parametrize("use_reference", [False, True])
def test_print_h1_h6__file_output__no_numbers(
    keep_stdout,
    use_reference,
    capsys,
    simple_html_file,
    pre_test_print_heading_cleanup,
    pre_test_check_and_mark_reference_cleanup,
):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        else:
            return None

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        if use_reference:
            ref = Reference()
            ref.id = "id123"
            exp_id = "id123_"
        else:
            ref = None
            exp_id = ""

        print_h1("heading 1", reference=ref)
        print_h3("heading 3")
        print_h6("heading 6")
        print_h4("heading 4")
        print_h2("heading 2")
        print_h5("heading 5")

        expected_result = (
            "<html>\n"
            f'<h1 id="ch_{exp_id}heading_1_1">heading 1<a class="pyreball-anchor-link" href="#ch_{exp_id}heading_1_1">\u00B6</a></h1>\n'
            '<h3 id="ch_heading_3_2">heading 3<a class="pyreball-anchor-link" href="#ch_heading_3_2">\u00B6</a></h3>\n'
            '<h6 id="ch_heading_6_3">heading 6<a class="pyreball-anchor-link" href="#ch_heading_6_3">\u00B6</a></h6>\n'
            '<h4 id="ch_heading_4_4">heading 4<a class="pyreball-anchor-link" href="#ch_heading_4_4">\u00B6</a></h4>\n'
            '<h2 id="ch_heading_2_5">heading 2<a class="pyreball-anchor-link" href="#ch_heading_2_5">\u00B6</a></h2>\n'
            '<h5 id="ch_heading_5_6">heading 5<a class="pyreball-anchor-link" href="#ch_heading_5_6">\u00B6</a></h5>\n'
        )

        with open(simple_html_file, "r") as f:
            result = f.read()
            assert result == expected_result

        captured = capsys.readouterr()
        expected_stdout = (
            ("heading 1\nheading 3\nheading 6\n" "heading 4\nheading 2\nheading 5")
            if keep_stdout
            else ""
        )
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize("keep_stdout", [False, True])
@pytest.mark.parametrize("use_reference", [False, True])
def test_print_h1_h6__file_output__with_numbers(
    keep_stdout,
    use_reference,
    capsys,
    simple_html_file,
    pre_test_print_heading_cleanup,
    pre_test_check_and_mark_reference_cleanup,
):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        else:
            return key == "numbered_headings"

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        if use_reference:
            ref = Reference()
            ref.id = "id123"
            exp_id = "id123_"
        else:
            ref = None
            exp_id = ""

        print_h1("he 1", reference=ref)
        print_h2("he 2")
        print_h3("he 3")
        print_h3("he 3")
        print_h2("he 2")
        print_h1("he 1")
        print_h2("he 2")
        print_h2("he 2")
        print_h3("he 3")

        expected_result = (
            "<html>\n"
            f'<h1 id="ch_{exp_id}1_he_1_1">1\u00A0\u00A0he 1<a class="pyreball-anchor-link" href="#ch_{exp_id}1_he_1_1">\u00B6</a></h1>\n'
            '<h2 id="ch_1_1_he_2_2">1.1\u00A0\u00A0he 2<a class="pyreball-anchor-link" href="#ch_1_1_he_2_2">\u00B6</a></h2>\n'
            '<h3 id="ch_1_1_1_he_3_3">1.1.1\u00A0\u00A0he 3<a class="pyreball-anchor-link" href="#ch_1_1_1_he_3_3">\u00B6</a></h3>\n'
            '<h3 id="ch_1_1_2_he_3_4">1.1.2\u00A0\u00A0he 3<a class="pyreball-anchor-link" href="#ch_1_1_2_he_3_4">\u00B6</a></h3>\n'
            '<h2 id="ch_1_2_he_2_5">1.2\u00A0\u00A0he 2<a class="pyreball-anchor-link" href="#ch_1_2_he_2_5">\u00B6</a></h2>\n'
            '<h1 id="ch_2_he_1_6">2\u00A0\u00A0he 1<a class="pyreball-anchor-link" href="#ch_2_he_1_6">\u00B6</a></h1>\n'
            '<h2 id="ch_2_1_he_2_7">2.1\u00A0\u00A0he 2<a class="pyreball-anchor-link" href="#ch_2_1_he_2_7">\u00B6</a></h2>\n'
            '<h2 id="ch_2_2_he_2_8">2.2\u00A0\u00A0he 2<a class="pyreball-anchor-link" href="#ch_2_2_he_2_8">\u00B6</a></h2>\n'
            '<h3 id="ch_2_2_1_he_3_9">2.2.1\u00A0\u00A0he 3<a class="pyreball-anchor-link" href="#ch_2_2_1_he_3_9">\u00B6</a></h3>\n'
        )

        with open(simple_html_file, "r") as f:
            result = f.read()
            assert result == expected_result

        captured = capsys.readouterr()
        expected_stdout = (
            (
                "1 he 1\n1.1 he 2\n1.1.1 he 3\n1.1.2 he 3\n1.2 he 2\n"
                "2 he 1\n2.1 he 2\n2.2 he 2\n2.2.1 he 3"
            )
            if keep_stdout
            else ""
        )
        assert captured.out.strip() == expected_stdout


def test_print_div__stdout(capsys):
    def fake_get_parameter_value(key):
        return key == "keep_stdout"

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        print_div("arbitrary paragraph\nsecond line")
        captured = capsys.readouterr()
        assert "arbitrary paragraph\nsecond line" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch(
        "pyreball.html.get_parameter_value",
        side_effect=fake_get_parameter_value_different,
    ):
        print_div("another paragraph\nsecond line")
        captured = capsys.readouterr()
        assert "another paragraph\nsecond line" in captured.out


@pytest.mark.parametrize("keep_stdout", [False, True])
def test_print_div__file_output(keep_stdout, capsys, simple_html_file):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        else:
            return None

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        print_div("new\nparagraph")
        expected_div_element = "<div>new\nparagraph</div>"
        with open(simple_html_file, "r") as f:
            result = f.read()
            assert result == f"<html>\n{expected_div_element}\n"

        captured = capsys.readouterr()
        expected_stdout = expected_div_element if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize(
    "use_reference,align,caption_position,numbered,sep,expected_anchor_link,expected_result",
    [
        (
            True,
            "left",
            "bottom",
            True,
            "",
            "code-block-123-3",
            (
                '<div class="pyreball-code-wrapper">'
                '<div class="pyreball-block-fit-content pyreball-left-aligned">'
                '<div class="pyreball-block-fit-content pyreball-centered">'
                "<code>x = 1</code>"
                "</div>"
                "<span>caption</span>"
                "</div>"
                "</div>"
            ),
        ),
        (
            False,
            "center",
            "top",
            False,
            "\n",
            "code-block-3",
            (
                '<div class="pyreball-code-wrapper">\n'
                '<div class="pyreball-block-fit-content pyreball-centered">\n'
                "<span>caption</span>\n"
                '<div class="pyreball-block-fit-content pyreball-centered">\n'
                "<code>x = 1</code>\n"
                "</div>\n"
                "</div>\n"
                "</div>"
            ),
        ),
    ],
)
def test__wrap_code_block_html(
    pre_test_check_and_mark_reference_cleanup,
    use_reference,
    align,
    caption_position,
    numbered,
    sep,
    expected_anchor_link,
    expected_result,
):
    with mock.patch(
        "pyreball.html._prepare_caption_element", return_value="<span>caption</span>"
    ) as prepare_caption_element_mock:
        if use_reference:
            reference = Reference()
            reference.id = "123"
        else:
            reference = None
        source_code_str = "<code>x = 1</code>"
        code_block_index = 3
        result = _wrap_code_block_html(
            source_code_str,
            code_block_index=code_block_index,
            caption="my caption",
            reference=reference,
            align=align,
            caption_position=caption_position,
            numbered=numbered,
            sep=sep,
        )
        assert result == expected_result
        prepare_caption_element_mock.assert_called_with(
            prefix="Source",
            caption="my caption",
            numbered=numbered,
            index=code_block_index,
            anchor_link=expected_anchor_link,
        )


@pytest.mark.parametrize(
    "syntax_highlight",
    [
        "python",
        None,
    ],
)
def test_print_code_block__stdout(syntax_highlight, capsys):
    def fake_get_parameter_value(key):
        return key == "keep_stdout"

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        print_code_block("[1, 2, 3]", syntax_highlight=syntax_highlight)
        captured = capsys.readouterr()
        if syntax_highlight:
            assert '<pre><code class="python">[1, 2, 3]</code></pre>' in captured.out
        else:
            assert "<pre><code>[1, 2, 3]</code></pre>" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch(
        "pyreball.html.get_parameter_value",
        side_effect=fake_get_parameter_value_different,
    ):
        print_code_block("{'a': 4}", syntax_highlight=syntax_highlight)
        captured = capsys.readouterr()
        if syntax_highlight:
            assert "<pre><code class=\"python\">{'a': 4}</code></pre>" in captured.out
        else:
            assert "<pre><code>{'a': 4}</code></pre>" in captured.out


@pytest.mark.parametrize("keep_stdout", [False, True])
@pytest.mark.parametrize(
    "align,param_align,expected_used_align",
    [
        ("left", "center", "left"),
        (None, "right", "right"),
    ],
)
@pytest.mark.parametrize(
    "caption_position,param_caption_position,expected_caption_position",
    [
        ("top", "bottom", "top"),
        (None, "bottom", "bottom"),
    ],
)
@pytest.mark.parametrize(
    "numbered,param_numbered,expected_used_numbered",
    [
        (True, False, True),
        (None, True, True),
        (None, False, False),
    ],
)
def test_print_code_block(
    keep_stdout,
    align,
    param_align,
    expected_used_align,
    caption_position,
    param_caption_position,
    expected_caption_position,
    numbered,
    param_numbered,
    expected_used_numbered,
    capsys,
    simple_html_file,
    pre_test_print_code_block_cleanup,
    pre_test_check_and_mark_reference_cleanup,
):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        elif key == "align_code_blocks":
            return param_align
        elif key == "code_block_captions_position":
            return param_caption_position
        elif key == "numbered_code_blocks":
            return param_numbered
        else:
            return None

    syntax_highlight = None
    sep = ""

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        with mock.patch(
            "pyreball.html.code_block",
            side_effect=lambda x, **kwargs: f"<code>{x}</code>",
        ):
            with mock.patch(
                "pyreball.html._wrap_code_block_html",
                side_effect=lambda source_code_str, **kwargs: f"<div>{source_code_str}</div>",
            ) as _wrap_code_block_html_mock:
                ref = Reference()
                print_code_block(
                    "[1, 2, 3]",
                    caption="cap",
                    reference=ref,
                    align=align,
                    caption_position=caption_position,
                    numbered=numbered,
                    syntax_highlight=syntax_highlight,
                    sep=sep,
                )

                _wrap_code_block_html_mock.assert_called_with(
                    source_code_str="<code>[1, 2, 3]</code>",
                    code_block_index=1,
                    caption="cap",
                    reference=ref,
                    align=expected_used_align,
                    caption_position=expected_caption_position,
                    numbered=expected_used_numbered,
                    sep=sep,
                )
                # after writing the first block, the index is already incremented
                assert _code_block_memory["code_block_index"] == 2

                captured = capsys.readouterr()
                if keep_stdout:
                    assert "<code>[1, 2, 3]</code>" in captured.out.strip()
                else:
                    assert captured.out.strip() == ""

                # check table index if another table is written to html
                print_code_block("[1, 2, 3]")
                assert _code_block_memory["code_block_index"] == 3


def test_print__stdout(capsys):
    def fake_get_parameter_value(key):
        return key == "keep_stdout"

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        print_html("<p><b>whatever</b></p>")
        captured = capsys.readouterr()
        assert "<p><b>whatever</b></p>" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch(
        "pyreball.html.get_parameter_value",
        side_effect=fake_get_parameter_value_different,
    ):
        print_html("<h1>another string</h1>")
        captured = capsys.readouterr()
        assert "<h1>another string</h1>" in captured.out


@pytest.mark.parametrize(
    "values,sep,end,expected_printed_result",
    [
        (
            ["<p><b>whatever</b></p>"],
            "",
            "\n",
            "<p><b>whatever</b></p>\n",
        ),
        (
            ["<p><b>whatever</b></p>"],
            "",
            "<br>",
            "<p><b>whatever</b></p><br>",
        ),
        (
            ["<x>", 1, 2, "</x>"],
            "<br>",
            "\n",
            "<x><br>1<br>2<br></x>\n",
        ),
        (
            ["<x>", "hello\nworld", "</x>"],
            "<br>",
            "\n",
            "<x><br>hello\nworld<br></x>\n",
        ),
    ],
)
@pytest.mark.parametrize("keep_stdout", [False, True])
def test_print__file_output(
    values,
    sep,
    end,
    expected_printed_result,
    keep_stdout,
    capsys,
    simple_html_file,
):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        else:
            return None

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        print_html(*values, sep=sep, end=end)
        with open(simple_html_file, "r") as f:
            result = f.read()
            assert result == "<html>\n" + expected_printed_result

        captured = capsys.readouterr()
        expected_stdout = expected_printed_result.strip() if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize(
    "prefix,caption,numbered,index,anchor_link,expected_result",
    [
        (
            "tab",
            "",
            False,
            3,
            "myanchor",
            '\n<div class="pyreball-text-centered"><a id="myanchor"><b>\n\n</b></a></div>\n',
        ),
        (
            "tab",
            "my caption",
            False,
            3,
            "myanchor",
            '\n<div class="pyreball-text-centered"><a id="myanchor"><b>\nmy caption\n</b></a></div>\n',
        ),
        (
            "tab",
            "my caption",
            True,
            3,
            "myanchor2",
            '\n<div class="pyreball-text-centered"><a id="myanchor2"><b>\ntab 3: my caption\n</b></a></div>\n',
        ),
        (
            "img",
            "",
            True,
            5,
            "myanchor2",
            '\n<div class="pyreball-text-centered"><a id="myanchor2"><b>\nimg 5.\n</b></a></div>\n',
        ),
    ],
)
def test__prepare_caption_element(
    prefix, caption, numbered, index, anchor_link, expected_result
):
    assert (
        _prepare_caption_element(prefix, caption, numbered, index, anchor_link)
        == expected_result
    )


@pytest.mark.parametrize(
    "paging_sizes,expected_result",
    [
        ([1], ([1], [1])),
        ([10, "all", 100], ([10, -1, 100], [10, "all", 100])),
        (["ALL", 100], ([-1, 100], ["ALL", 100])),
        (["All", 100], ([-1, 100], ["All", 100])),
    ],
)
def test__compute_length_menu_for_datatables__valid_values(
    paging_sizes, expected_result
):
    assert _compute_length_menu_for_datatables(paging_sizes) == expected_result


@pytest.mark.parametrize(
    "paging_sizes",
    [
        [1, "UNK"],
        [{"x": "y"}],
    ],
)
def test__compute_length_menu_for_datatables__invalid_values(paging_sizes):
    with pytest.raises(ValueError):
        assert _compute_length_menu_for_datatables(paging_sizes)


@pytest.mark.parametrize(
    "display_option,"
    "scroll_y_height,"
    "scroll_x,"
    "sortable,"
    "sorting_definition,"
    "paging_sizes,"
    "search_box,"
    "col_align_def,"
    "datatables_definition,"
    "expected_result",
    [
        # display_option = scrolling
        (
            "scrolling",
            "300px",
            True,
            False,
            None,
            None,
            False,
            None,
            None,
            {
                "paging": False,
                "scrollCollapse": True,
                "scrollY": "300px",
                "scrollX": True,
                "ordering": False,
                "searching": False,
                "info": False,
            },
        ),
        # display_option = scrolling; different height
        (
            "scrolling",
            "500px",
            True,
            False,
            None,
            None,
            False,
            None,
            None,
            {
                "paging": False,
                "scrollCollapse": True,
                "scrollY": "500px",
                "scrollX": True,
                "ordering": False,
                "searching": False,
                "info": False,
            },
        ),
        # display_option = paging
        (
            "paging",
            "300px",
            True,
            False,
            None,
            None,
            False,
            None,
            None,
            {
                "paging": True,
                "lengthMenu": ([10, 25, 100, -1], [10, 25, 100, "All"]),
                "scrollX": True,
                "ordering": False,
                "searching": False,
                "info": False,
            },
        ),
        # display_option = paging + custom page sizes
        (
            "paging",
            "300px",
            True,
            False,
            None,
            [20, "All"],
            False,
            None,
            None,
            {
                "paging": True,
                "lengthMenu": ([20, -1], [20, "All"]),
                "scrollX": True,
                "ordering": False,
                "searching": False,
                "info": False,
            },
        ),
        # display_option = full
        (
            "full",
            "300px",
            True,
            False,
            None,
            None,
            False,
            None,
            None,
            {
                "paging": False,
                "scrollX": True,
                "ordering": False,
                "searching": False,
                "info": False,
            },
        ),
        # display_option = full; scroll_x = False, search_box = True
        (
            "full",
            "300px",
            False,
            False,
            None,
            None,
            True,
            None,
            None,
            {
                "paging": False,
                "ordering": False,
                "searching": True,
                "info": False,
            },
        ),
        # display_option = full; sortable
        (
            "full",
            "300px",
            True,
            True,
            None,
            None,
            False,
            None,
            None,
            {
                "paging": False,
                "scrollX": True,
                "order": [],
                "searching": False,
                "info": False,
            },
        ),
        # display_option = full; sorting_definition
        (
            "full",
            "300px",
            True,
            False,
            [[1, "asc"]],
            None,
            False,
            None,
            None,
            {
                "paging": False,
                "scrollX": True,
                "order": [[1, "asc"]],
                "searching": False,
                "info": False,
            },
        ),
        # display_option = full; col_align_def
        (
            "full",
            "300px",
            True,
            False,
            None,
            None,
            False,
            [
                {"targets": [0, 2], "className": "dt-left"},
                {"targets": [1, 3], "className": "dt-right"},
            ],
            None,
            {
                "paging": False,
                "scrollX": True,
                "ordering": False,
                "searching": False,
                "info": False,
                "columnDefs": [
                    {"targets": [0, 2], "className": "dt-left"},
                    {"targets": [1, 3], "className": "dt-right"},
                ],
            },
        ),
        # display_option = full; datatables_definition => overrides everything
        (
            "full",
            "300px",
            True,
            False,
            None,
            None,
            False,
            None,
            {"a": "b"},
            {"a": "b"},
        ),
        # display_option = full; datatables_definition
        # => overrides everything (even as empty dict)
        (
            "full",
            "300px",
            True,
            False,
            None,
            None,
            False,
            None,
            {},
            {},
        ),
    ],
)
def test__gather_datatables_setup(
    display_option,
    scroll_y_height,
    scroll_x,
    sortable,
    sorting_definition,
    paging_sizes,
    search_box,
    col_align_def,
    datatables_definition,
    expected_result,
):
    result = _gather_datatables_setup(
        display_option,
        scroll_y_height,
        scroll_x,
        sortable,
        sorting_definition,
        paging_sizes,
        search_box,
        col_align_def,
        datatables_definition,
    )
    assert result == expected_result


@pytest.mark.parametrize(
    "df,index,expected_result",
    [
        (
            pd.DataFrame([(10,)], columns=["a"]),
            True,
            [
                {"targets": [0, 1], "className": "dt-right"},
            ],
        ),
        (
            pd.DataFrame([(10, "a", 1.3)], columns=["a", "b", "c"]),
            True,
            [
                {"targets": [0, 1, 3], "className": "dt-right"},
                {"targets": [2], "className": "dt-left"},
            ],
        ),
        (
            pd.DataFrame([(10, "a", 1.3)], columns=["a", "b", "c"]),
            False,
            [
                {"targets": [0, 2], "className": "dt-right"},
                {"targets": [1], "className": "dt-left"},
            ],
        ),
        (
            pd.DataFrame(
                [("a", bool, datetime.datetime(2000, 1, 1))], columns=["a", "b", "c"]
            ),
            True,
            [
                {"targets": [0], "className": "dt-right"},
                {"targets": [1, 2, 3], "className": "dt-left"},
            ],
        ),
    ],
)
def test__prepare_col_alignment_definition__col_align_none(df, index, expected_result):
    assert _prepare_col_alignment_definition(df, None, index) == expected_result


@pytest.mark.parametrize(
    "col_align,index,expected_result",
    [
        ("left", False, [{"targets": [0, 1, 2, 3], "className": "dt-left"}]),
        ("center", False, [{"targets": [0, 1, 2, 3], "className": "dt-center"}]),
        ("right", False, [{"targets": [0, 1, 2, 3], "className": "dt-right"}]),
        ("right", True, [{"targets": [0, 1, 2, 3, 4], "className": "dt-right"}]),
    ],
)
def test__prepare_col_alignment_definition__col_align_str(
    col_align, index, expected_result
):
    df = pd.DataFrame([(10, "a", 1.3, "x")], columns=["a", "b", "c", "d"])
    assert _prepare_col_alignment_definition(df, col_align, index) == expected_result


def test__prepare_col_alignment_definition__col_align_str__wrong_value():
    df = pd.DataFrame([(10, "a", 1.3, "x")], columns=["a", "b", "c", "d"])
    with pytest.raises(ValueError) as excinfo:
        _prepare_col_alignment_definition(df, "unsupported")
    assert "must use only the following values" in str(excinfo.value)


@pytest.mark.parametrize(
    "col_align,index,expected_result",
    [
        (
            ["left"] * 4,
            False,
            [{"targets": [0, 1, 2, 3], "className": "dt-left"}],
        ),
        (
            ["left", "right"] * 2,
            False,
            [
                {"targets": [0, 2], "className": "dt-left"},
                {"targets": [1, 3], "className": "dt-right"},
            ],
        ),
        (
            ["left", "right", "center", "center"],
            False,
            [
                {"targets": [0], "className": "dt-left"},
                {"targets": [1], "className": "dt-right"},
                {"targets": [2, 3], "className": "dt-center"},
            ],
        ),
        (
            ["center", "left", "right", "center", "center"],
            True,
            [
                {"targets": [0, 3, 4], "className": "dt-center"},
                {"targets": [1], "className": "dt-left"},
                {"targets": [2], "className": "dt-right"},
            ],
        ),
    ],
)
def test__prepare_col_alignment_definition__col_align_list(
    col_align, index, expected_result
):
    df = pd.DataFrame([(10, "a", 1.3, "x")], columns=["a", "b", "c", "d"])
    assert _prepare_col_alignment_definition(df, col_align, index) == expected_result


def test__prepare_col_alignment_definition__col_align_list__wrong_size():
    df = pd.DataFrame([(10, "a", 1.3, "x")], columns=["a", "b", "c", "d"])
    col_align = ["left", "right", "left"]
    with pytest.raises(ValueError) as excinfo:
        _prepare_col_alignment_definition(df, col_align)
    assert "must have the same length" in str(excinfo.value)


def test__prepare_col_alignment_definition__col_align_list__wrong_values():
    df = pd.DataFrame([(10, "a", 1.3, "x")], columns=["a", "b", "c", "d"])
    col_align = ["left", "right", "left", "unsupported"]
    with pytest.raises(ValueError) as excinfo:
        _prepare_col_alignment_definition(df, col_align, False)
    assert "must use only the following values" in str(excinfo.value)


def test__prepare_table_html__reused_reference_error(
    pre_test_check_and_mark_reference_cleanup, simple_dataframe
):
    ref = Reference()
    _ = _prepare_table_html(simple_dataframe, reference=ref)

    with pytest.raises(ValueError) as excinfo2:
        _prepare_table_html(simple_dataframe, reference=ref)
    assert "Reference is used for the second time" in str(excinfo2.value)


@pytest.mark.parametrize(
    "align",
    [
        "center",
        "left",
        "right",
    ],
)
@pytest.mark.parametrize(
    "use_reference",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize(
    "sortable",
    [
        False,
        True,
    ],
)
@pytest.mark.parametrize(
    "caption_position",
    [
        "top",
        "bottom",
    ],
)
@pytest.mark.parametrize(
    "datatables_style",
    [
        "display",
        ["display", "compact"],
    ],
)
def test__prepare_table_html(
    align,
    use_reference,
    sortable,
    caption_position,
    datatables_style,
    pre_test_check_and_mark_reference_cleanup,
    simple_dataframe,
):
    if use_reference:
        reference = Reference()
        reference.id = "123"
    else:
        reference = None

    result = _prepare_table_html(
        df=simple_dataframe,
        caption="mycap",
        align=align,
        caption_position=caption_position,
        numbered=True,
        reference=reference,
        sortable=sortable,
        tab_index=5,
        datatables_style=datatables_style,
    )

    assert "<script>" in result
    # Remove the final row with script, because it cannot be parsed by ET
    result = re.sub("<script.*", "", result)
    html_root = ET.fromstring(result)

    assert (
        len(html_root.findall(f"./div/div/table/tbody/tr")) == simple_dataframe.shape[0]
    )

    if caption_position == "top":
        assert html_root.findall("./div/")[0].tag == "div"
    elif caption_position == "bottom":
        assert html_root.findall("./div/")[1].tag == "div"

    expected_table_classes = ["dataframe"]
    expected_table_classes.extend(
        [datatables_style] if isinstance(datatables_style, str) else datatables_style
    )
    assert html_root.findall(
        f"./div/div/table[@class='{' '.join(expected_table_classes)}']"
    )

    align_class = {
        "center": "pyreball-centered",
        "left": "pyreball-left-aligned",
        "right": "pyreball-right-aligned",
    }[align]
    assert html_root.findall(
        f"./div[@class='pyreball-block-fit-content {align_class}']"
    )

    anchor = "table-123-5" if use_reference else "table-5"
    assert html_root.findall(f"./div/div/a[@id='{anchor}']")


@pytest.mark.parametrize(
    "col_align,set_index,index,expected_col_align_def",
    [
        ("center", False, False, [{"targets": [0, 1, 2], "className": "dt-center"}]),
        ("center", True, False, [{"targets": [0, 1], "className": "dt-center"}]),
        ("center", True, True, [{"targets": [0, 1, 2], "className": "dt-center"}]),
        ("left", True, True, [{"targets": [0, 1, 2], "className": "dt-left"}]),
    ],
)
def test__prepare_table_html__col_align(
    col_align, set_index, index, expected_col_align_def
):
    # Just check that col_align_def is obtained correctly for various settings
    # of col_align and index
    with mock.patch(
        "pyreball.html._gather_datatables_setup", return_value=None
    ) as gather_datatables_setup_mock:
        params = dict(
            display_option="full",
            scroll_y_height="300px",
            scroll_x=True,
            sortable=True,
            sorting_definition=None,
            paging_sizes=None,
            search_box=False,
            datatables_definition=None,
        )
        if set_index:
            params["index"] = index

        _ = _prepare_table_html(
            df=pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
            col_align=col_align,
            caption="mycap",
            tab_index=5,
            **params,
        )
        gather_datatables_setup_mock.assert_called_with(
            display_option="full",
            scroll_y_height="300px",
            scroll_x=True,
            sortable=True,
            sorting_definition=None,
            paging_sizes=None,
            search_box=False,
            col_align_def=expected_col_align_def,
            datatables_definition=None,
        )


@pytest.mark.parametrize(
    "sizes,expected_result",
    [
        ("20", [20]),
        ("20,30", [20, 30]),
        ("20,30,100", [20, 30, 100]),
        ("20,30,100,All", [20, 30, 100, "All"]),
        ("20,all,100", [20, "all", 100]),
        ("ALL", ["ALL"]),
    ],
)
def test__parse_tables_paging_sizes(sizes, expected_result):
    assert _parse_tables_paging_sizes(sizes) == expected_result


def test_print_table__stdout(capsys, simple_dataframe):
    def fake_get_parameter_value(key):
        return key == "keep_stdout"

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        print_table(simple_dataframe)
        captured = capsys.readouterr()
        assert "x1 x2" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch(
        "pyreball.html.get_parameter_value",
        side_effect=fake_get_parameter_value_different,
    ):
        print_table(simple_dataframe)
        captured = capsys.readouterr()
        assert "x1 x2" in captured.out


@pytest.mark.parametrize("keep_stdout", [False, True])
@pytest.mark.parametrize(
    "function_param_name,function_param_value,param_name,param_value,expected_param_value",
    [
        ("align", "left", "align_tables", "center", "left"),
        ("align", None, "align_tables", "right", "right"),
        ("caption_position", "top", "table_captions_position", "bottom", "top"),
        ("caption_position", None, "table_captions_position", "bottom", "bottom"),
        ("numbered", True, "numbered_tables", False, True),
        ("numbered", None, "numbered_tables", True, True),
        ("numbered", None, "numbered_tables", False, False),
        ("display_option", "scrolling", "tables_display_option", "paging", "scrolling"),
        ("display_option", None, "tables_display_option", "paging", "paging"),
        ("scroll_y_height", "200px", "tables_scroll_y_height", "500px", "200px"),
        ("scroll_y_height", None, "tables_scroll_y_height", "500px", "500px"),
        ("scroll_x", True, "tables_scroll_x", False, True),
        ("scroll_x", None, "tables_scroll_x", True, True),
        ("scroll_x", None, "tables_scroll_x", False, False),
        ("sortable", True, "sortable_tables", False, True),
        ("sortable", None, "sortable_tables", True, True),
        ("sortable", None, "sortable_tables", False, False),
        ("paging_sizes", [100, 200], "tables_paging_sizes", "20,All", [100, 200]),
        ("paging_sizes", None, "tables_paging_sizes", "20,All", [20, "All"]),
        ("search_box", True, "tables_search_box", False, True),
        ("search_box", None, "tables_search_box", True, True),
        ("search_box", None, "tables_search_box", False, False),
        (
            "datatables_style",
            "display",
            "tables_datatables_style",
            "compact",
            "display",
        ),
        ("datatables_style", None, "tables_datatables_style", "compact", ["compact"]),
    ],
)
@pytest.mark.parametrize(
    "sorting_definition",
    [
        None,
        [(0, "asc")],
    ],
)
def test_print_table__file_output(
    keep_stdout,
    function_param_name,
    function_param_value,
    param_name,
    param_value,
    expected_param_value,
    sorting_definition,
    capsys,
    simple_html_file,
    simple_dataframe,
    pre_test_print_table_cleanup,
):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "keep_stdout":
            return keep_stdout
        elif key == param_name:
            return param_value
        elif key == "tables_paging_sizes":
            # let's provide some values here, so _parse_tables_paging_sizes doesn't fail
            return "10,20,all"
        else:
            return None

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        with mock.patch(
            "pyreball.html._prepare_table_html", return_value="<table>x</table>"
        ) as _prepare_table_html_mock:
            ref = Reference()

            default_function_params: Dict[str, Any] = dict(
                caption="cap",
                reference=ref,
                align="center",
                caption_position="top",
                numbered=True,
                col_align="center",
                display_option="full",
                scroll_y_height="300px",
                scroll_x=True,
                sortable=False,
                sorting_definition=sorting_definition,
                paging_sizes=None,
                search_box=False,
                datatables_style="display",
                datatables_definition=None,
                additional_kwarg=42,
            )
            default_function_params[function_param_name] = function_param_value
            if param_name != "tables_paging_sizes":
                default_function_params["paging_sizes"] = [10, 20]

            print_table(
                simple_dataframe,
                **default_function_params,
            )
            with open(simple_html_file, "r") as f:
                result = f.read()
                assert result == "<html>\n<table>x</table>\n"

            default_function_params[function_param_name] = expected_param_value

            _prepare_table_html_mock.assert_called_with(
                df=simple_dataframe,
                tab_index=1,
                **default_function_params,
            )

            # after writing the first table, the index is already incremented
            assert _table_memory["table_index"] == 2

            captured = capsys.readouterr()
            if keep_stdout:
                assert "x1 x2" in captured.out.strip()
            else:
                assert captured.out.strip() == ""

            # check table index if another table is written to html
            print_table(simple_dataframe)
            assert _table_memory["table_index"] == 3


@pytest.mark.parametrize(
    "reference,fig_index,expected_result",
    [
        (Reference("doesnotmatter"), 3, "img-id3553-3"),
        (None, 23, "img-23"),
    ],
)
def test__construct_image_anchor_link(
    reference, fig_index, expected_result, pre_test_check_and_mark_reference_cleanup
):
    if reference is not None:
        reference.id = "id3553"
    assert (
        _construct_image_anchor_link(reference=reference, fig_index=fig_index)
        == expected_result
    )


@pytest.mark.parametrize(
    "img_element,align,hidden,img_type,expected_result",
    [
        (
            "el1",
            "center",
            True,
            "xyz",
            (
                '<div class="pyreball-image-wrapper pyreball-xyz-fig" style="display: none;">'
                '<div align="center">'
                '<div style="display: inline-block;">el1</div></div></div>'
            ),
        ),
        (
            "el2",
            "left",
            True,
            "abc",
            (
                '<div class="pyreball-image-wrapper pyreball-abc-fig" style="display: none;">'
                '<div align="left">'
                '<div style="display: inline-block;">el2</div></div></div>'
            ),
        ),
        (
            "el3",
            "right",
            False,
            "abc",
            (
                '<div class="pyreball-image-wrapper pyreball-abc-fig"><div align="right">'
                '<div style="display: inline-block;">el3</div></div></div>'
            ),
        ),
    ],
)
def test__wrap_image_element_by_outer_divs(
    img_element, align, hidden, img_type, expected_result
):
    assert (
        _wrap_image_element_by_outer_divs(img_element, align, hidden, img_type)
        == expected_result
    )


def test__prepare_matplotlib_image_element__wrong_format():
    with pytest.raises(ValueError) as excinfo:
        _prepare_matplotlib_image_element(None, 0, "unknown_format", None)
    assert "Matplotlib format can be only" in str(excinfo.value)


def test__prepare_matplotlib_image_element__unsupported_param_values():
    with mock.patch("pyreball.html.get_parameter_value", return_value=False):
        with pytest.raises(RuntimeError) as excinfo:
            _prepare_matplotlib_image_element(mock.Mock(), 0, "png", False)
        assert "Failed to create a matplotlib image." in str(excinfo.value)


@pytest.mark.parametrize(
    "image_format,param_image_format,expected_used_image_format",
    [
        ("svg", "png", "svg"),
        (None, "png", "png"),
        (None, "svg", "svg"),
    ],
)
@pytest.mark.parametrize(
    "embedded,param_embedded,expected_used_embedded",
    [
        (True, False, True),
        (None, True, True),
        (None, False, False),
    ],
)
def test__prepare_matplotlib_image_element(
    image_format,
    param_image_format,
    expected_used_image_format,
    embedded,
    param_embedded,
    expected_used_embedded,
    simple_html_file,
):
    html_dir_path = simple_html_file.rsplit(".")[0]

    def fake_get_parameter_value(key):
        if key == "html_dir_path":
            return html_dir_path
        elif key == "html_dir_name":
            return os.path.basename(html_dir_path)
        elif key == "matplotlib_format":
            return param_image_format
        elif key == "matplotlib_embedded":
            return param_embedded
        else:
            return None

    def fake_savefig(fname, *, transparent=None, **kwargs):
        if isinstance(fname, str):
            with open(fname, "w") as f:
                f.write("image_contents")
        else:
            fname.write(b"io_image_contents")

    fig = mock.Mock()
    fig.savefig.side_effect = fake_savefig

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        if expected_used_embedded and expected_used_image_format != "svg":
            with pytest.raises(ValueError) as excinfo:
                _ = _prepare_matplotlib_image_element(
                    fig=fig, fig_index=4, image_format=image_format, embedded=embedded
                )
            assert (
                "Only svg format can be used for embedded matplotlib figures."
                in str(excinfo.value)
            )
        else:
            result = _prepare_matplotlib_image_element(
                fig=fig, fig_index=4, image_format=image_format, embedded=embedded
            )

            if expected_used_image_format == "svg" and expected_used_embedded:
                assert result == "io_image_contents"
            else:
                with open(
                    os.path.join(html_dir_path, f"img_004.{expected_used_image_format}")
                ) as f:
                    result_file_contents = f.read()
                assert result_file_contents == "image_contents"
                assert (
                    result == f'<img src="report/img_004.{expected_used_image_format}">'
                )


def test__prepare_altair_image_element():
    fig = mock.Mock()
    fig.to_json.return_value = "fig_json"
    expected_result = (
        '<div id="altairvis326"></div><script type="text/javascript">\nvar spec = fig_json;\n'
        'var opt = {"renderer": "canvas", "actions": false};\n'
        'vegaEmbed("#altairvis326", spec, opt);'
        "</script>"
    )
    assert _prepare_altair_image_element(fig, 326) == expected_result


def test__prepare_plotly_image_element():
    fig = mock.Mock()
    fig.to_html.return_value = "fig_html"
    result = _prepare_plotly_image_element(fig)
    assert result == "fig_html"
    fig.to_html.assert_called_with(full_html=False, include_plotlyjs=False)


def test__prepare_bokeh_image_element():
    with mock.patch("bokeh.embed.components", side_effect=lambda x: x):
        result = _prepare_bokeh_image_element(("a", "b"))
        assert result == "<div>ba</div>"


def test__prepare_image_element__unknown_figure_type():
    fig = list()
    with pytest.raises(ValueError) as excinfo:
        _prepare_image_element(
            fig=fig, fig_index=3, matplotlib_format="svg", embedded=True
        )
    assert "Unknown figure type" in str(excinfo.value)


@mock.patch(
    "pyreball.html._prepare_matplotlib_image_element", return_value="img_element"
)
def test__prepare_image_element__matplotlib(_prepare_matplotlib_image_element_mock):
    fig, _ = plt.subplots()
    result = _prepare_image_element(
        fig=fig, fig_index=3, matplotlib_format="svg", embedded=True
    )
    _prepare_matplotlib_image_element_mock.assert_called_with(
        fig=fig, fig_index=3, image_format="svg", embedded=True
    )
    assert result == ("img_element", "matplotlib")


@mock.patch(
    "pyreball.html._prepare_matplotlib_image_element", return_value="img_element"
)
def test__prepare_image_element__seaborn(
    _prepare_matplotlib_image_element_mock, simple_dataframe
):
    fig = sns.PairGrid(simple_dataframe)
    result = _prepare_image_element(
        fig=fig, fig_index=3, matplotlib_format="svg", embedded=True
    )
    _prepare_matplotlib_image_element_mock.assert_called_with(
        fig=fig, fig_index=3, image_format="svg", embedded=True
    )
    assert result == ("img_element", "matplotlib")


@mock.patch("pyreball.html._prepare_altair_image_element", return_value="img_element")
@pytest.mark.parametrize(
    "fig",
    [
        alt.Chart(get_simple_dataframe()),
        alt.ConcatChart(get_simple_dataframe()),
        alt.Chart(get_simple_dataframe()).facet(column="x2"),
        alt.HConcatChart(get_simple_dataframe()),
        alt.LayerChart(get_simple_dataframe()),
        alt.Chart(get_simple_dataframe()).repeat(row=["x1"]),
        alt.VConcatChart(get_simple_dataframe()),
    ],
)
def test__prepare_image_element__altair(_prepare_altair_image_element_mock, fig):
    result = _prepare_image_element(
        fig=fig, fig_index=3, matplotlib_format="svg", embedded=True
    )
    _prepare_altair_image_element_mock.assert_called_with(fig=fig, fig_index=3)
    assert result == ("img_element", "altair")


@mock.patch("pyreball.html._prepare_plotly_image_element", return_value="img_element")
def test__prepare_image_element__plotly(
    _prepare_plotly_image_element_mock, simple_dataframe
):
    fig = px.bar(simple_dataframe, x="x1", y="x2")
    result = _prepare_image_element(
        fig=fig, fig_index=3, matplotlib_format="svg", embedded=True
    )
    _prepare_plotly_image_element_mock.assert_called_with(fig=fig)
    assert result == ("img_element", "plotly")


@mock.patch("pyreball.html._prepare_bokeh_image_element", return_value="img_element")
def test__prepare_image_element__bokeh(
    _prepare_bokeh_image_element_mock, simple_dataframe
):
    fig = bokeh_figure(x_range=simple_dataframe["x2"])
    result = _prepare_image_element(
        fig=fig, fig_index=3, matplotlib_format="svg", embedded=True
    )
    _prepare_bokeh_image_element_mock.assert_called_with(fig=fig)
    assert result == ("img_element", "bokeh")


def test__print_figure__stdout__bokeh(simple_dataframe):
    def fake_get_parameter_value(key):
        return key == "keep_stdout"

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    fig = bokeh_figure(x_range=simple_dataframe["x2"])

    with mock.patch("bokeh.plotting.show") as show_mock:
        # when keep_stdout is set on
        with mock.patch(
            "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
        ):
            _print_figure(fig)
            show_mock.assert_called_once_with(fig)

        # when keep_stdout is set off, but we don't have html file either
        with mock.patch(
            "pyreball.html.get_parameter_value",
            side_effect=fake_get_parameter_value_different,
        ):
            _print_figure(fig)
            assert show_mock.call_count == 2


def test__print_figure__stdout__not_bokeh(simple_dataframe):
    def fake_get_parameter_value(key):
        return key == "keep_stdout"

    def fake_get_parameter_value_different(key):
        if key == "keep_stdout":
            return False
        else:
            return None

    with mock.patch.object(alt.Chart, "show") as show_mock:
        fig = alt.Chart(simple_dataframe)
        # when keep_stdout is set on
        with mock.patch(
            "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
        ):
            _print_figure(fig)
            show_mock.assert_called_once()

        # when keep_stdout is set off, but we don't have html file either
        with mock.patch(
            "pyreball.html.get_parameter_value",
            side_effect=fake_get_parameter_value_different,
        ):
            _print_figure(fig)
            assert show_mock.call_count == 2


@pytest.mark.parametrize("caption_position", ["top", "bottom"])
def test__print_figure__file_output(
    caption_position,
    simple_html_file,
    simple_dataframe,
    pre_test_print_figure_cleanup,
    pre_test_check_and_mark_reference_cleanup,
):
    # just test one fig to go through the pipeline
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        else:
            return None

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        with mock.patch("pyreball.html._write_to_html") as _write_to_html_mock:
            fig = alt.Chart(simple_dataframe).mark_bar().encode(x="x2", y="x1")
            ref = Reference()
            ref.id = "id123"
            _print_figure(
                fig=fig,
                caption="cap",
                reference=ref,
                align="left",
                caption_position=caption_position,
                numbered=True,
                matplotlib_format="does_not_matter",
                embedded=True,
                hidden=True,
            )

            _write_to_html_mock.assert_called_once()
            assert _graph_memory["fig_index"] == 2

            _print_figure(
                fig=fig,
                caption="cap",
                reference=Reference(),
                align="left",
                caption_position=caption_position,
                numbered=True,
                matplotlib_format="does_not_matter",
                embedded=True,
                hidden=True,
            )
            assert _graph_memory["fig_index"] == 3

            # try with the same reference one more time
            with pytest.raises(ValueError) as excinfo:
                _print_figure(
                    fig=fig,
                    caption="cap",
                    reference=ref,
                    align="left",
                    caption_position=caption_position,
                    numbered=True,
                    matplotlib_format="does_not_matter",
                    embedded=True,
                    hidden=True,
                )
            assert "Reference is used for the second time" in str(excinfo.value)


@pytest.mark.parametrize(
    "align,param_align,expected_used_align",
    [
        ("left", "center", "left"),
        (None, "right", "right"),
    ],
)
@pytest.mark.parametrize(
    "caption_position,param_caption_position,expected_caption_position",
    [
        ("top", "bottom", "top"),
        (None, "bottom", "bottom"),
    ],
)
@pytest.mark.parametrize(
    "numbered,param_numbered,expected_used_numbered",
    [
        (True, False, True),
        (None, True, True),
        (None, False, False),
    ],
)
def test_print_figure(
    align,
    param_align,
    expected_used_align,
    caption_position,
    param_caption_position,
    expected_caption_position,
    numbered,
    param_numbered,
    expected_used_numbered,
    simple_dataframe,
):
    def fake_get_parameter_value(key):
        if key == "html_file_path":
            return simple_html_file
        elif key == "align_figures":
            return param_align
        elif key == "figure_captions_position":
            return param_caption_position
        elif key == "numbered_figures":
            return param_numbered
        else:
            return None

    with mock.patch(
        "pyreball.html.get_parameter_value", side_effect=fake_get_parameter_value
    ):
        with mock.patch("pyreball.html._print_figure") as _print_figure_mock:
            ref = Reference()
            fig = alt.Chart(simple_dataframe).mark_bar().encode(x="x2", y="x1")
            print_figure(
                fig,
                caption="cap",
                reference=ref,
                align=align,
                caption_position=caption_position,
                numbered=numbered,
                matplotlib_format="does_not_matter",
                embedded=True,
            )

            _print_figure_mock.assert_called_with(
                fig=fig,
                caption="cap",
                reference=ref,
                align=expected_used_align,
                caption_position=expected_caption_position,
                numbered=expected_used_numbered,
                matplotlib_format="does_not_matter",
                embedded=True,
                hidden=False,
            )
