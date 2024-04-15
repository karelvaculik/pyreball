from copy import copy

import pytest

from pyreball.text import (
    _collect_classes_for_code_strings,
    _construct_attrs_str,
    _construct_class_attr_string,
    a,
    bold,
    code,
    code_block,
    div,
    em,
    link,
    olist,
    span,
    tag,
    ulist,
)


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (None, None),
        ("", 'class=""'),
        ([], 'class=""'),
        ("ab", 'class="ab"'),
        ("ab xy", 'class="ab xy"'),
        (["ab"], 'class="ab"'),
        (["ab", "e", "fg"], 'class="ab e fg"'),
    ],
)
def test__construct_class_attr_string(test_input, expected_result):
    assert _construct_class_attr_string(test_input) == expected_result


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (
            None,
            None,
        ),
        (
            {},
            None,
        ),
        (
            {"x": "y"},
            'x="y"',
        ),
        (
            {"x": "y", "checked": None, "a": "b c", "valid": None},
            'x="y" checked a="b c" valid',
        ),
    ],
)
def test__construct_attrs_str(test_input, expected_result):
    assert _construct_attrs_str(test_input) == expected_result


def test_bold():
    assert bold("a", "b", sep="\n") == "<b>\na\nb\n</b>"


def test_em():
    assert em("a", "b", sep="\n") == "<em>\na\nb\n</em>"


@pytest.mark.parametrize(
    "initial_class_list,cl,syntax_highlight,expected_result",
    [
        ([], None, None, None),
        ([], [], None, []),
        ([], "cl1", None, "cl1"),
        ([], ["cl1"], None, ["cl1"]),
        ([], None, "python", ["python"]),
        ([], [], "python", ["python"]),
        ([], "cl1", "python", ["cl1", "python"]),
        ([], ["cl1"], "python", ["cl1", "python"]),
        (["x"], None, None, None),
        (["x"], [], None, []),
        (["x"], "cl1", None, "cl1"),
        (["x"], ["cl1"], None, ["cl1"]),
        (["x"], None, "python", ["x", "python"]),
        (["x"], [], "python", ["x", "python"]),
        (["x"], "cl1", "python", ["cl1", "x", "python"]),
        (["x"], ["cl1"], "python", ["cl1", "x", "python"]),
    ],
)
def test__collect_classes_for_code_strings(
    initial_class_list, cl, syntax_highlight, expected_result
):
    original_cl = copy(cl)
    original_initial_class_list = copy(initial_class_list)
    original_syntax_highlight = copy(syntax_highlight)
    result = _collect_classes_for_code_strings(initial_class_list, cl, syntax_highlight)
    assert result == expected_result
    # check that input values haven't changed
    assert original_cl == cl
    assert original_initial_class_list == initial_class_list
    assert original_syntax_highlight == syntax_highlight


def test_code__without_syntax_highlight():
    expected_result = "<code>\na\nb\n</code>"
    assert code("a", "b", sep="\n", syntax_highlight=None) == expected_result


def test_code__with_syntax_highlight():
    expected_result = '<code class="inline-highlight python">\na\nb\n</code>'
    assert code("a", "b", sep="\n", syntax_highlight="python") == expected_result


def test_code_block__without_syntax_highlight():
    expected_result = "<pre><code>\na\nb\n</code></pre>"
    assert code_block("a", "b", sep="\n", syntax_highlight=None) == expected_result


def test_code_block__with_syntax_highlight():
    expected_result = '<pre><code class="block-highlight python">\na\nb\n</code></pre>'
    assert code_block("a", "b", sep="\n", syntax_highlight="python") == expected_result


def test_code_block__with_syntax_highlight_and_attributes():
    expected_result = (
        '<pre class="pre1" pa="pv">'
        '<code class="code1 block-highlight python" ca="cv">\na\nb\n</code>'
        "</pre>"
    )
    result = code_block(
        "a",
        "b",
        cl="code1",
        attrs={"ca": "cv"},
        pre_cl="pre1",
        pre_attrs={"pa": "pv"},
        sep="\n",
        syntax_highlight="python",
    )
    assert result == expected_result


def test_div():
    assert div("a", "b", sep="\n") == "<div>\na\nb\n</div>"


def test_span():
    assert span("a", "b", sep="\n") == "<span>\na\nb\n</span>"


def test_a():
    expected_result = '<a href="www.example.com">\na\nb\n</a>'
    assert a("a", "b", attrs={"href": "www.example.com"}, sep="\n") == expected_result


def test_link():
    assert link("my text", "myurl") == '<a href="myurl">my text</a>'


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (
            ["a", "b", "c"],
            "<ul><li>a</li><li>b</li><li>c</li></ul>",
        ),
        (
            ["a", 43, 42],
            "<ul><li>a</li><li>43</li><li>42</li></ul>",
        ),
        (
            [("a", "<ul><li>b</li></ul>")],
            "<ul><li>a<ul><li>b</li></ul></li></ul>",
        ),
        (
            [("b", "<ol><li>x</li></ol>"), ("a", "<ul><li>y</li><li>z</li></ul>")],
            "<ul><li>b<ol><li>x</li></ol></li><li>a<ul><li>y</li><li>z</li></ul></li></ul>",
        ),
    ],
)
def test_ulist__without_parameters(test_input, expected_result):
    assert ulist(*test_input) == expected_result


def test_ulist__with_parameters():
    input_kwargs = {
        "cl": "ul_class",
        "attrs": {"x": "y"},
        "li_cl": "li_class",
        "li_attrs": {"a": "b"},
    }
    test_input = ["value1", "value2", "value3"]
    expected_result = (
        '<ul class="ul_class" x="y">'
        '<li class="li_class" a="b">value1</li>'
        '<li class="li_class" a="b">value2</li>'
        '<li class="li_class" a="b">value3</li>'
        "</ul>"
    )
    assert ulist(*test_input, **input_kwargs) == expected_result


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (
            ["a", "b", "c"],
            "<ol><li>a</li><li>b</li><li>c</li></ol>",
        ),
        (
            ["a", 43, 42],
            "<ol><li>a</li><li>43</li><li>42</li></ol>",
        ),
        (
            [("a", "<ol><li>b</li></ol>")],
            "<ol><li>a<ol><li>b</li></ol></li></ol>",
        ),
        (
            [("b", "<ol><li>x</li></ol>"), ("a", "<ol><li>y</li><li>z</li></ol>")],
            "<ol><li>b<ol><li>x</li></ol></li><li>a<ol><li>y</li><li>z</li></ol></li></ol>",
        ),
    ],
)
def test_olist__without_parameters(test_input, expected_result):
    assert olist(*test_input) == expected_result


def test_olist__with_parameters():
    input_kwargs = {
        "cl": "ul_class",
        "attrs": {"x": "y"},
        "li_cl": "li_class",
        "li_attrs": {"a": "b"},
    }
    test_input = ["value1", "value2", "value3"]
    expected_result = (
        '<ol class="ul_class" x="y">'
        '<li class="li_class" a="b">value1</li>'
        '<li class="li_class" a="b">value2</li>'
        '<li class="li_class" a="b">value3</li>'
        "</ol>"
    )
    assert olist(*test_input, **input_kwargs) == expected_result


@pytest.mark.parametrize(
    "input_args,input_kwargs,expected_result",
    [
        (
            ["abc"],
            {"name": "x", "cl": None, "attrs": None, "sep": ""},
            "<x>abc</x>",
        ),
        (
            [2351],
            {"name": "x", "cl": None, "attrs": None, "sep": ""},
            "<x>2351</x>",
        ),
        (
            [2351, "hello"],
            {"name": "abc", "cl": None, "attrs": None, "sep": "\n"},
            "<abc>\n2351\nhello\n</abc>",
        ),
        (
            [2351, "hello"],
            {"name": "abc", "cl": "cl1", "attrs": None, "sep": "\n"},
            '<abc class="cl1">\n2351\nhello\n</abc>',
        ),
        (
            [2351, "hello"],
            {"name": "abc", "cl": "cl1 cl2", "attrs": None, "sep": "\n"},
            '<abc class="cl1 cl2">\n2351\nhello\n</abc>',
        ),
        (
            [2351, "hello"],
            {"name": "abc", "cl": ["cl1", "cl2"], "attrs": None, "sep": "\n"},
            '<abc class="cl1 cl2">\n2351\nhello\n</abc>',
        ),
        (
            [2351, "hello"],
            {"name": "abc", "cl": None, "attrs": {"key": "val"}, "sep": "\n"},
            '<abc key="val">\n2351\nhello\n</abc>',
        ),
        (
            [2351, "hello"],
            {"name": "abc", "cl": ["cl1", "cl2"], "attrs": {"key": "val"}, "sep": "\n"},
            '<abc class="cl1 cl2" key="val">\n2351\nhello\n</abc>',
        ),
        (
            [],
            {
                "name": "abc",
                "cl": ["cl1", "cl2"],
                "attrs": {"key": "val"},
                "paired": False,
            },
            '<abc class="cl1 cl2" key="val">',
        ),
    ],
)
def test_tag(input_args, input_kwargs, expected_result):
    assert tag(*input_args, **input_kwargs) == expected_result


def test_tag__duplicate_class_setting():
    with pytest.raises(ValueError):
        tag("value", name="x", cl="my_class", attrs={"class": "my_cl"}, sep="")
