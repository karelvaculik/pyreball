import os
import re
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET

import altair as alt
from bokeh.plotting import figure as bokeh_figure
from matplotlib import pyplot as plt
import pandas as pd
import plotly.express as px
import pytest
import seaborn as sns

from pyreball.html import (Reference, create_reference, _check_and_mark_reference, set_title, _write_to_html,
                           _tidy_title, _reduce_whitespaces, _get_heading_number, _print_heading, print_h1,
                           print_h2, print_h3, print_h4, print_h5, print_h6, print_div, print_code, print_html,
                           _prepare_caption_element, _prepare_table_html, print_table, _construct_plot_anchor_link,
                           _wrap_plot_element_by_outer_divs, _prepare_matplotlib_plot_element,
                           _prepare_altair_plot_element, _prepare_plotly_plot_element, _prepare_bokeh_plot_element,
                           _prepare_image_element, _plot_graph, plot_graph, plot_multi_graph)


@pytest.fixture
def simple_html_file(tmpdir):
    html_file = Path(tmpdir) / "report.html"

    with open(html_file, 'w') as f:
        f.write('<html>\n')

    return str(html_file)


def get_simple_dataframe():
    return pd.DataFrame({'x1': [1, 2, 3], 'x2': ['a', 'b', 'c']})


@pytest.fixture
def simple_dataframe():
    return get_simple_dataframe()


@pytest.fixture
def pre_test_print_heading_cleanup():
    # _print_heading is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    if hasattr(_print_heading, 'heading_index'):
        delattr(_print_heading, 'heading_index')
    if hasattr(_print_heading, 'heading_counting'):
        delattr(_print_heading, 'heading_counting')
    yield


@pytest.fixture
def pre_test_check_and_mark_reference_cleanup():
    # _check_and_mark_reference is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    if hasattr(_check_and_mark_reference, 'used_references'):
        delattr(_check_and_mark_reference, 'used_references')
    yield


@pytest.fixture
def pre_test_print_table_cleanup():
    # print_table is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    if hasattr(print_table, 'table_index'):
        delattr(print_table, 'table_index')
    yield


@pytest.fixture
def pre_test_plot_graph_cleanup():
    # _plot_graph is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    if hasattr(_plot_graph, 'plot_index'):
        delattr(_plot_graph, 'plot_index')
    yield


@pytest.fixture
def pre_test_plot_multi_graph_cleanup():
    # plot_multi_graph is meant to be used only in a single session,
    # but test functions don't respect this so we do manual cleanup
    if hasattr(plot_multi_graph, 'multi_plot_index'):
        delattr(plot_multi_graph, 'multi_plot_index')
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


def test_create_reference():
    ref = create_reference()
    assert isinstance(ref, Reference)

    ref_string = str(create_reference("whatever"))
    regex_match = re.match(r'^<a href="#ref-id(\d+)">whatever</a>$', ref_string)
    assert regex_match is not None


def test__check_and_mark_reference(pre_test_check_and_mark_reference_cleanup):
    ref1 = Reference()
    ref2 = Reference()
    ref3 = Reference()
    ref1.id = '1'
    ref2.id = '1'
    ref3.id = '2'

    _check_and_mark_reference(ref1)
    with pytest.raises(ValueError):
        # a reference with this id was already marked
        _check_and_mark_reference(ref2)

    _check_and_mark_reference(ref3)
    with pytest.raises(ValueError):
        # a reference with this id was already marked
        _check_and_mark_reference(ref3)


def test_set_title__stdout(capsys):
    set_title("my title")
    captured = capsys.readouterr()
    assert captured.out.strip() == "my title"


@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
def test_set_title__file_output(keep_stdout, capsys, simple_html_file):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        else:
            return None

    with open(simple_html_file, 'a') as f:
        f.write("<title>old title</title>\n</html>")

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        set_title("new title with more words")
        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == "<html>\n<title class=\"custom\">new title with more words</title>\n</html>"

    captured = capsys.readouterr()
    expected_stdout = "new title with more words" if keep_stdout else ""
    assert captured.out.strip() == expected_stdout


def test__write_to_html(simple_html_file):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        _write_to_html("<div>")
        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == "<html>\n<div>\n"


@pytest.mark.parametrize("test_input,expected_result", [
    ('', ''),
    ('42%', '42_percent'),
    ('one 53 two &**) three.exe and,no', 'one_53_two_three_exe_and_no'),
    ('This is a  \t 42simple \n Sen&*tence', 'this_is_a_42simple_sentence'),
])
def test__tidy_title(test_input, expected_result):
    assert _tidy_title(test_input) == expected_result


@pytest.mark.parametrize("test_input,expected_result", [
    ('', ''),
    ('  Hello    world   ', 'Hello world'),
])
def test_reduce_whitespaces(test_input, expected_result):
    assert _reduce_whitespaces(test_input) == expected_result


@pytest.mark.parametrize("test_input_1,test_input_2,expected_result", [
    (1, [1, 1, 1, 1], "1"),
    (1, [1, 2, 1, 1], "1"),
    (1, [1, 1, 2, 1], "1"),
    (1, [1, 1, 1, 2], "1"),
    (2, [1, 2, 3, 4], "1.2"),
    (2, [2, 1, 3, 4], "2.1"),
    (3, [1, 2, 3, 4], "1.2.3"),
    (4, [1, 2, 3, 4], "1.2.3.4"),
    (4, [4, 3, 2, 1], "4.3.2.1"),
])
def test_get_heading_number(test_input_1, test_input_2, expected_result):
    assert _get_heading_number(level=test_input_1, l_heading_counting=test_input_2) == expected_result


@pytest.mark.parametrize("level", [
    0,
    7
])
def test__print_heading__unsupported_level(level, pre_test_print_heading_cleanup):
    with pytest.raises(ValueError):
        _print_heading("whatever", level)


def test__print_heading__stdout(capsys, pre_test_print_heading_cleanup):
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        _print_heading("simple heading", level=3)
        captured = capsys.readouterr()
        assert "### simple heading" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
        _print_heading("another heading", level=5)
        captured = capsys.readouterr()
        assert "##### another heading" in captured.out


@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
def test_print_h1_h6__file_output__no_numbers(keep_stdout, capsys, simple_html_file, pre_test_print_heading_cleanup):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_h1('heading 1')
        print_h3('heading 3')
        print_h6('heading 6')
        print_h4('heading 4')
        print_h2('heading 2')
        print_h5('heading 5')

        expected_result = (
            '<html>\n'
            '<h1 id="heading_1_1">heading 1<a class="anchor-link" href="#heading_1_1">\u00B6</a></h1>\n'
            '<h3 id="heading_3_2">heading 3<a class="anchor-link" href="#heading_3_2">\u00B6</a></h3>\n'
            '<h6 id="heading_6_3">heading 6<a class="anchor-link" href="#heading_6_3">\u00B6</a></h6>\n'
            '<h4 id="heading_4_4">heading 4<a class="anchor-link" href="#heading_4_4">\u00B6</a></h4>\n'
            '<h2 id="heading_2_5">heading 2<a class="anchor-link" href="#heading_2_5">\u00B6</a></h2>\n'
            '<h5 id="heading_5_6">heading 5<a class="anchor-link" href="#heading_5_6">\u00B6</a></h5>\n'
        )

        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == expected_result

        captured = capsys.readouterr()
        expected_stdout = ("# heading 1\n### heading 3\n###### heading 6\n"
                           "#### heading 4\n## heading 2\n##### heading 5") if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
def test_print_h1_h6__file_output__with_numbers(keep_stdout, capsys, simple_html_file, pre_test_print_heading_cleanup):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        else:
            return key == 'numbered_headings'

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_h1('he 1')
        print_h2('he 2')
        print_h3('he 3')
        print_h3('he 3')
        print_h2('he 2')
        print_h1('he 1')
        print_h2('he 2')
        print_h2('he 2')
        print_h3('he 3')

        expected_result = (
            '<html>\n'
            '<h1 id="1_he_1_1">1\u00A0\u00A0he 1<a class="anchor-link" href="#1_he_1_1">\u00B6</a></h1>\n'
            '<h2 id="1_1_he_2_2">1.1\u00A0\u00A0he 2<a class="anchor-link" href="#1_1_he_2_2">\u00B6</a></h2>\n'
            '<h3 id="1_1_1_he_3_3">1.1.1\u00A0\u00A0he 3<a class="anchor-link" href="#1_1_1_he_3_3">\u00B6</a></h3>\n'
            '<h3 id="1_1_2_he_3_4">1.1.2\u00A0\u00A0he 3<a class="anchor-link" href="#1_1_2_he_3_4">\u00B6</a></h3>\n'
            '<h2 id="1_2_he_2_5">1.2\u00A0\u00A0he 2<a class="anchor-link" href="#1_2_he_2_5">\u00B6</a></h2>\n'
            '<h1 id="2_he_1_6">2\u00A0\u00A0he 1<a class="anchor-link" href="#2_he_1_6">\u00B6</a></h1>\n'
            '<h2 id="2_1_he_2_7">2.1\u00A0\u00A0he 2<a class="anchor-link" href="#2_1_he_2_7">\u00B6</a></h2>\n'
            '<h2 id="2_2_he_2_8">2.2\u00A0\u00A0he 2<a class="anchor-link" href="#2_2_he_2_8">\u00B6</a></h2>\n'
            '<h3 id="2_2_1_he_3_9">2.2.1\u00A0\u00A0he 3<a class="anchor-link" href="#2_2_1_he_3_9">\u00B6</a></h3>\n'
        )

        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == expected_result

        captured = capsys.readouterr()
        expected_stdout = ("# he 1\n## he 2\n### he 3\n### he 3\n## he 2\n"
                           "# he 1\n## he 2\n## he 2\n### he 3") if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize("replace_newlines_with_br", [
    True,
    False,
])
def test_print_div__stdout(replace_newlines_with_br, capsys):
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_div("arbitrary paragraph\nsecond line", replace_newlines_with_br=replace_newlines_with_br)
        captured = capsys.readouterr()
        assert "arbitrary paragraph\nsecond line" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
        print_div("another paragraph\nsecond line", replace_newlines_with_br=replace_newlines_with_br)
        captured = capsys.readouterr()
        assert "another paragraph\nsecond line" in captured.out


@pytest.mark.parametrize("replace_newlines_with_br", [
    True,
    False,
])
@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
def test_print_div__file_output(keep_stdout, replace_newlines_with_br, capsys, simple_html_file):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        else:
            return None

    expected_newline_separator = '<br>' if replace_newlines_with_br else '\n'

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_div("new\nparagraph", replace_newlines_with_br=replace_newlines_with_br)
        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == f"<html>\n<div>new{expected_newline_separator}paragraph</div>\n"

        captured = capsys.readouterr()
        expected_stdout = "new\nparagraph" if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize("highlight_syntax", [
    True,
    False,
])
def test_print_code__stdout(highlight_syntax, capsys):
    # highlight_syntax should not matter here
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_code("[1, 2, 3]", highlight_syntax=highlight_syntax)
        captured = capsys.readouterr()
        assert "[1, 2, 3]" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
        print_code("{'a': 4}", highlight_syntax=highlight_syntax)
        captured = capsys.readouterr()
        assert "{'a': 4}" in captured.out


@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
@pytest.mark.parametrize("highlight_syntax,expected_result", [
    (True, '<pre class="prettyprint lang-py">[1, 2, 3]</pre>'),
    (False, '<pre>[1, 2, 3]</pre>'),
])
def test_print_code__file_output(keep_stdout, highlight_syntax, expected_result, capsys, simple_html_file):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_code("[1, 2, 3]", highlight_syntax=highlight_syntax)
        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == f"<html>\n{expected_result}\n"

        captured = capsys.readouterr()
        expected_stdout = "[1, 2, 3]" if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


def test_print_html__stdout(capsys):
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_html("<p><b>whatever</b></p>")
        captured = capsys.readouterr()
        assert "<p><b>whatever</b></p>" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
        print_html("<h1>another string</h1>")
        captured = capsys.readouterr()
        assert "<h1>another string</h1>" in captured.out


@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
def test_print_html__file_output(keep_stdout, capsys, simple_html_file):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_html("<p><b>whatever</b></p>")
        with open(simple_html_file, 'r') as f:
            result = f.read()
            assert result == "<html>\n<p><b>whatever</b></p>\n"

        captured = capsys.readouterr()
        expected_stdout = "<p><b>whatever</b></p>" if keep_stdout else ""
        assert captured.out.strip() == expected_stdout


@pytest.mark.parametrize("prefix,caption,numbered,index,anchor_link,expected_result", [
    ('tab', '', False, 3, 'myanchor',
     '\n<div class="text-centered"><a name="myanchor"><b>\n\n</b></a></div>\n'),
    ('tab', 'my caption', False, 3, 'myanchor',
     '\n<div class="text-centered"><a name="myanchor"><b>\nmy caption\n</b></a></div>\n'),
    ('tab', 'my caption', True, 3, 'myanchor2',
     '\n<div class="text-centered"><a name="myanchor2"><b>\ntab 3: my caption\n</b></a></div>\n'),
    ('img', '', True, 5, 'myanchor2',
     '\n<div class="text-centered"><a name="myanchor2"><b>\nimg 5.\n</b></a></div>\n'),
])
def test__prepare_caption_element(prefix, caption, numbered, index, anchor_link, expected_result):
    assert _prepare_caption_element(prefix, caption, numbered, index, anchor_link) == expected_result


def test__prepare_table_html__wrong_sorting_definitions(pre_test_check_and_mark_reference_cleanup, simple_dataframe):
    with pytest.raises(ValueError) as excinfo:
        _prepare_table_html(simple_dataframe, sorting_definition=('unknown', 'asc'))
    assert "is not a column in provided data frame" in str(excinfo.value)

    with pytest.raises(ValueError) as excinfo2:
        _prepare_table_html(simple_dataframe, sorting_definition=('x1', 'unknown'))
    assert "sorting_definition must be either None or a pair" in str(excinfo2.value)


def test__prepare_table_html__reused_reference_error(pre_test_check_and_mark_reference_cleanup, simple_dataframe):
    ref = Reference()
    _ = _prepare_table_html(simple_dataframe, reference=ref)

    with pytest.raises(ValueError) as excinfo2:
        _prepare_table_html(simple_dataframe, reference=ref)
    assert "Reference is used for the second time" in str(excinfo2.value)


@pytest.mark.parametrize("align", [
    'center',
    'left',
    'right',
])
@pytest.mark.parametrize("full_table", [
    False,
    True,
])
@pytest.mark.parametrize("use_reference", [
    True,
    False,
])
@pytest.mark.parametrize("sortable", [
    False,
    True,
])
@pytest.mark.parametrize("sorting_definition", [
    None,
    ('x2', 'desc'),
    ('x1', 'asc'),
])
def test__prepare_table_html(align, full_table, use_reference, sortable, sorting_definition,
                             pre_test_check_and_mark_reference_cleanup, simple_dataframe):
    if use_reference:
        reference = Reference()
        reference.id = '123'
    else:
        reference = None

    result = _prepare_table_html(df=simple_dataframe, caption="mycap", align=align, full_table=full_table,
                                 numbered=True, reference=reference, sortable=sortable, tab_index=5,
                                 sorting_definition=sorting_definition)

    if sorting_definition is not None:
        # ET cannot parse the the <script> tag, so check sorting here and then continue with rest
        result, script_tag = result.rsplit('\n', 1)
        ind = simple_dataframe.columns.get_loc(sorting_definition[0]) + 1
        assert f"table.order( [ {ind}, \'{sorting_definition[1]}\' ] )" in script_tag

    html_root = ET.fromstring(result)

    assert len(html_root.findall(f"./div/div[2]/table/tbody/tr")) == simple_dataframe.shape[0]

    sortable_table_class = ' sortable_table' if sortable and not sorting_definition else ''
    assert html_root.findall(f"./div/div[2]/table[@class='dataframe centered{sortable_table_class}']")

    align_class = {'center': 'centered', 'left': 'left-aligned', 'right': 'right-aligned'}[align]
    assert html_root.findall(f"./div[@class='table-wrapper-inner {align_class}']")

    table_wrapper_div_class = 'table-scroller' if full_table else 'table-scroller-collapsed'
    assert html_root.findall(f"./div/div[2][@class='{table_wrapper_div_class}']")

    anchor = 'table-123-5' if use_reference else 'table-5'
    assert html_root.findall(f"./div/div[1]/a[@name='{anchor}']")


def test_print_table__stdout(capsys, simple_dataframe):
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    # when keep_stdout is set on
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        print_table(simple_dataframe)
        captured = capsys.readouterr()
        assert "x1 x2" in captured.out

    # when keep_stdout is set off, but we don't have html file either
    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
        print_table(simple_dataframe)
        captured = capsys.readouterr()
        assert "x1 x2" in captured.out


@pytest.mark.parametrize("keep_stdout", [
    False,
    True
])
@pytest.mark.parametrize("align,param_align,expected_used_align", [
    ("left", "center", "left"),
    (None, "right", "right"),
])
@pytest.mark.parametrize("numbered,param_numbered,expected_used_numbered", [
    (True, False, True),
    (None, True, True),
    (None, False, False),
])
@pytest.mark.parametrize("full_table,param_full_table,expected_used_full_table", [
    (True, False, True),
    (None, True, True),
    (None, False, False),
])
@pytest.mark.parametrize("sortable,param_sortable,expected_used_sortable", [
    (True, False, True),
    (None, True, True),
    (None, False, False),
])
@pytest.mark.parametrize("sorting_definition", [
    None,
    ('x1', 'asc'),
])
def test_print_table__file_output(align, param_align, expected_used_align, numbered, param_numbered,
                                  expected_used_numbered, full_table, param_full_table, expected_used_full_table,
                                  sortable, param_sortable, expected_used_sortable, sorting_definition,
                                  keep_stdout, capsys, simple_html_file, simple_dataframe,
                                  pre_test_print_table_cleanup):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == 'keep_stdout':
            return keep_stdout
        elif key == "align_tables":
            return param_align
        elif key == "numbered_tables":
            return param_numbered
        elif key == "full_tables":
            return param_full_table
        elif key == "sortable_tables":
            return param_sortable
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        with mock.patch('pyreball.html._prepare_table_html',
                        return_value='<table>x</table>') as _prepare_table_html_mock:
            ref = Reference()
            print_table(simple_dataframe, caption="cap", reference=ref, align=align, numbered=numbered,
                        full_table=full_table, sortable=sortable, sorting_definition=sorting_definition,
                        additional_kwarg=42)
            with open(simple_html_file, 'r') as f:
                result = f.read()
                assert result == "<html>\n<table>x</table>\n"

            _prepare_table_html_mock.assert_called_with(df=simple_dataframe, caption="cap", align=expected_used_align,
                                                        full_table=expected_used_full_table,
                                                        numbered=expected_used_numbered,
                                                        reference=ref, sortable=expected_used_sortable,
                                                        tab_index=1, sorting_definition=sorting_definition,
                                                        additional_kwarg=42)

            # after writing the first table, the index is already incremented
            assert print_table.table_index == 2

            captured = capsys.readouterr()
            if keep_stdout:
                assert "x1 x2" in captured.out.strip()
            else:
                assert captured.out.strip() == ""

            # check table index if another table is written to html
            print_table(simple_dataframe)
            assert print_table.table_index == 3


@pytest.mark.parametrize("reference,plot_ind,expected_result", [
    (Reference("doesnotmatter"), 3, 'img-id3553-3'),
    (None, 23, 'img-23'),
])
def test__construct_plot_anchor_link(reference, plot_ind, expected_result, pre_test_check_and_mark_reference_cleanup):
    if reference is not None:
        reference.id = "id3553"
    assert _construct_plot_anchor_link(reference=reference, plot_ind=plot_ind) == expected_result


@pytest.mark.parametrize("img_element,align,hidden,expected_result", [
    ("el1", "center", True,
     '<div class="image-wrapper" style="display: none;"><div align="center">'
     '<div style="display: inline-block;">el1</div></div></div>'),
    ("el2", "left", True,
     '<div class="image-wrapper" style="display: none;"><div align="left">'
     '<div style="display: inline-block;">el2</div></div></div>'),
    ("el3", "right", False,
     '<div class="image-wrapper"><div align="right">'
     '<div style="display: inline-block;">el3</div></div></div>'),
])
def test__wrap_plot_element_by_outer_divs(img_element, align, hidden, expected_result):
    assert _wrap_plot_element_by_outer_divs(img_element, align, hidden) == expected_result


def test__prepare_matplotlib_plot_element__wrong_format():
    with pytest.raises(ValueError) as excinfo:
        _prepare_matplotlib_plot_element(None, 0, "unknown_format", None)
    assert "Matplotlib format can be only" in str(excinfo.value)


def test__prepare_matplotlib_plot_element__unsupported_param_values():
    with pytest.raises(RuntimeError) as excinfo:
        _prepare_matplotlib_plot_element(mock.Mock(), 0, "png", False)
    assert "Failed to create a matplotlib image." in str(excinfo.value)


@pytest.mark.parametrize("plot_format,param_plot_format,expected_used_plot_format", [
    ("svg", "png", "svg"),
    (None, "png", "png"),
    (None, "svg", "svg"),
])
@pytest.mark.parametrize("embedded,param_embedded,expected_used_embedded", [
    (True, False, True),
    (None, True, True),
    (None, False, False),
])
def test__prepare_matplotlib_plot_element(plot_format, param_plot_format, expected_used_plot_format,
                                          embedded, param_embedded, expected_used_embedded,
                                          simple_html_file):
    html_dir_path = simple_html_file.rsplit('.')[0]

    def fake_get_parameter_value(key):
        if key == 'html_dir_path':
            return html_dir_path
        elif key == 'html_dir_name':
            return os.path.basename(html_dir_path)
        elif key == "matplotlib_format":
            return param_plot_format
        elif key == "matplotlib_embedded":
            return param_embedded
        else:
            return None

    def fake_savefig(fname, *, transparent=None, **kwargs):
        if isinstance(fname, str):
            with open(fname, 'w') as f:
                f.write("image_contents")
        else:
            fname.write(b"io_image_contents")

    fig = mock.Mock()
    fig.savefig.side_effect = fake_savefig

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        if expected_used_embedded and expected_used_plot_format != "svg":
            with pytest.raises(ValueError) as excinfo:
                _ = _prepare_matplotlib_plot_element(fig=fig, l_plot_index=4, plot_format=plot_format,
                                                     embedded=embedded)
            assert "Only svg format can be used for embedded matplotlib plots." in str(excinfo.value)
        else:
            result = _prepare_matplotlib_plot_element(fig=fig, l_plot_index=4, plot_format=plot_format,
                                                      embedded=embedded)

            if expected_used_plot_format == "svg" and expected_used_embedded:
                assert result == "io_image_contents"
            else:
                with open(os.path.join(html_dir_path, f'img_004.{expected_used_plot_format}')) as f:
                    result_file_contents = f.read()
                assert result_file_contents == 'image_contents'
                assert result == f'<img src="report/img_004.{expected_used_plot_format}">'


def test__prepare_altair_plot_element():
    fig = mock.Mock()
    fig.to_json.return_value = "fig_json"
    expected_result = (
        '<div id="altairvis326"></div><script type="text/javascript">\nvar spec = fig_json;\n'
        'var opt = {"renderer": "canvas", "actions": false};\n'
        'vegaEmbed("#altairvis326", spec, opt);'
        '</script>'
    )
    assert _prepare_altair_plot_element(fig, 326) == expected_result


def test__prepare_plotly_plot_element():
    fig = mock.Mock()
    fig.to_html.return_value = "fig_html"
    result = _prepare_plotly_plot_element(fig)
    assert result == "fig_html"
    fig.to_html.assert_called_with(full_html=False, include_plotlyjs=False)


def test__prepare_bokeh_plot_element():
    with mock.patch('bokeh.embed.components', side_effect=lambda x: x):
        result = _prepare_bokeh_plot_element(('a', 'b'))
        assert result == '<div>ba</div>'


def test__prepare_image_element__unknown_figure_type():
    fig = list()
    with pytest.raises(ValueError) as excinfo:
        _prepare_image_element(fig=fig, plot_index=3, matplotlib_format="svg", embedded=True)
    assert "Unknown figure type" in str(excinfo.value)


@mock.patch('pyreball.html._prepare_matplotlib_plot_element', return_value="img_element")
def test__prepare_image_element__matplotlib(_prepare_matplotlib_plot_element_mock):
    fig, _ = plt.subplots()
    result = _prepare_image_element(fig=fig, plot_index=3, matplotlib_format="svg", embedded=True)
    _prepare_matplotlib_plot_element_mock.assert_called_with(fig=fig, l_plot_index=3, plot_format="svg",
                                                             embedded=True)
    assert result == "img_element"


@mock.patch('pyreball.html._prepare_matplotlib_plot_element', return_value="img_element")
def test__prepare_image_element__seaborn(_prepare_matplotlib_plot_element_mock, simple_dataframe):
    fig = sns.PairGrid(simple_dataframe)
    result = _prepare_image_element(fig=fig, plot_index=3, matplotlib_format="svg", embedded=True)
    _prepare_matplotlib_plot_element_mock.assert_called_with(fig=fig, l_plot_index=3, plot_format="svg",
                                                             embedded=True)
    assert result == "img_element"


@mock.patch('pyreball.html._prepare_altair_plot_element', return_value="img_element")
@pytest.mark.parametrize("fig", [
    alt.Chart(get_simple_dataframe()),
    alt.ConcatChart(get_simple_dataframe()),
    alt.Chart(get_simple_dataframe()).facet(column='x2'),
    alt.HConcatChart(get_simple_dataframe()),
    alt.LayerChart(get_simple_dataframe()),
    alt.Chart(get_simple_dataframe()).repeat(row=['x1']),
    alt.VConcatChart(get_simple_dataframe()),
])
def test__prepare_image_element__altair(_prepare_altair_plot_element_mock, fig):
    result = _prepare_image_element(fig=fig, plot_index=3, matplotlib_format="svg", embedded=True)
    _prepare_altair_plot_element_mock.assert_called_with(fig=fig, l_plot_index=3)
    assert result == "img_element"


@mock.patch('pyreball.html._prepare_plotly_plot_element', return_value="img_element")
def test__prepare_image_element__plotly(_prepare_plotly_plot_element_mock, simple_dataframe):
    fig = px.bar(simple_dataframe, x='x1', y='x2')
    result = _prepare_image_element(fig=fig, plot_index=3, matplotlib_format="svg", embedded=True)
    _prepare_plotly_plot_element_mock.assert_called_with(fig=fig)
    assert result == "img_element"


@mock.patch('pyreball.html._prepare_bokeh_plot_element', return_value="img_element")
def test__prepare_image_element__bokeh(_prepare_bokeh_plot_element_mock, simple_dataframe):
    fig = bokeh_figure(x_range=simple_dataframe['x2'])
    result = _prepare_image_element(fig=fig, plot_index=3, matplotlib_format="svg", embedded=True)
    _prepare_bokeh_plot_element_mock.assert_called_with(fig=fig)
    assert result == "img_element"


def test__plot_graph__stdout__bokeh(simple_dataframe):
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    fig = bokeh_figure(x_range=simple_dataframe['x2'])

    with mock.patch('bokeh.plotting.show') as show_mock:
        # when keep_stdout is set on
        with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
            _plot_graph(fig)
            show_mock.assert_called_once_with(fig)

        # when keep_stdout is set off, but we don't have html file either
        with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
            _plot_graph(fig)
            assert show_mock.call_count == 2


def test__plot_graph__stdout__not_bokeh(simple_dataframe):
    def fake_get_parameter_value(key):
        return key == 'keep_stdout'

    def fake_get_parameter_value_different(key):
        if key == 'keep_stdout':
            return False
        else:
            return None

    with mock.patch.object(alt.Chart, 'show') as show_mock:
        fig = alt.Chart(simple_dataframe)
        # when keep_stdout is set on
        with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
            _plot_graph(fig)
            show_mock.assert_called_once()

        # when keep_stdout is set off, but we don't have html file either
        with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value_different):
            _plot_graph(fig)
            assert show_mock.call_count == 2


def test__plot_graph__file_output(simple_html_file, simple_dataframe, pre_test_plot_graph_cleanup):
    # just test one fig to go through the pipeline
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        with mock.patch('pyreball.html._write_to_html') as _write_to_html_mock:
            fig = alt.Chart(simple_dataframe).mark_bar().encode(x='x2', y='x1')
            ref = Reference()
            ref.id = "id123"
            _plot_graph(fig=fig, caption="cap", reference=ref, align="left", numbered=True,
                        matplotlib_format="does_not_matter", embedded=True, hidden=True)

            _write_to_html_mock.assert_called_once()
            assert _plot_graph.plot_index == 2

            _plot_graph(fig=fig, caption="cap", reference=Reference(), align="left", numbered=True,
                        matplotlib_format="does_not_matter", embedded=True, hidden=True)
            assert _plot_graph.plot_index == 3

            # try with the same reference one more time
            with pytest.raises(ValueError) as excinfo:
                _plot_graph(fig=fig, caption="cap", reference=ref, align="left", numbered=True,
                            matplotlib_format="does_not_matter", embedded=True, hidden=True)
            assert "Reference is used for the second time" in str(excinfo.value)


@pytest.mark.parametrize("align,param_align,expected_used_align", [
    ("left", "center", "left"),
    (None, "right", "right"),
])
@pytest.mark.parametrize("numbered,param_numbered,expected_used_numbered", [
    (True, False, True),
    (None, True, True),
    (None, False, False),
])
def test_plot_graph(align, param_align, expected_used_align, numbered, param_numbered, expected_used_numbered,
                    simple_dataframe):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == "align_plots":
            return param_align
        elif key == "numbered_plots":
            return param_numbered
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        with mock.patch('pyreball.html._plot_graph') as _plot_graph_mock:
            ref = Reference()
            fig = alt.Chart(simple_dataframe).mark_bar().encode(x='x2', y='x1')
            plot_graph(fig, caption="cap", reference=ref, align=align, numbered=numbered,
                       matplotlib_format="does_not_matter", embedded=True)

            _plot_graph_mock.assert_called_with(fig=fig, caption="cap", reference=ref, align=expected_used_align,
                                                numbered=expected_used_numbered, matplotlib_format="does_not_matter",
                                                embedded=True, hidden=False)


@pytest.mark.parametrize("align,param_align,expected_used_align", [
    ("left", "center", "left"),
    (None, "right", "right"),
])
@pytest.mark.parametrize("numbered,param_numbered,expected_used_numbered", [
    (True, False, True),
    (None, True, True),
    (None, False, False),
])
def test_plot_multi_graph(align, param_align, expected_used_align, numbered, param_numbered, expected_used_numbered,
                          simple_dataframe, pre_test_plot_multi_graph_cleanup):
    def fake_get_parameter_value(key):
        if key == 'html_file_path':
            return simple_html_file
        elif key == "align_plots":
            return param_align
        elif key == "numbered_plots":
            return param_numbered
        else:
            return None

    with mock.patch('pyreball.html.get_parameter_value', side_effect=fake_get_parameter_value):
        with mock.patch('pyreball.html._plot_graph') as _plot_graph_mock:
            with mock.patch('pyreball.html._write_to_html') as _write_to_html_mock:
                fig = alt.Chart(simple_dataframe).mark_bar().encode(x='x2', y='x1')
                figs = [fig, fig, fig]
                plot_multi_graph(figs, captions=["cap1", "cap2", "cap3"], align=align, numbered=numbered)

                assert _plot_graph_mock.call_count == 3

                assert plot_multi_graph.multi_plot_index == 2
