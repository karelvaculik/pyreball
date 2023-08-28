from unittest.mock import patch

import pytest

from pyreball.text import (
    _construct_attrs_str,
    _construct_class_attr_string,
    a,
    bold,
    code,
    div,
    em,
    link,
    olist,
    span,
    tag,
    ulist,
)


def assert_function_result(func, patch_env, test_input, input_kwargs, expected_result):
    with patch("pyreball.text.get_parameter_value", return_value=patch_env):
        assert func(*test_input, **input_kwargs) == expected_result


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
    with patch("pyreball.text.get_parameter_value", return_value=True):
        assert bold("a", "b", sep="\n") == "<b>a\nb</b>"


def test_em():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        assert em("a", "b", sep="\n") == "<em>a\nb</em>"


def test_code():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        assert code("a", "b", sep="\n") == "<code>a\nb</code>"


def test_div():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        assert div("a", "b", sep="\n") == "<div>a\nb</div>"


def test_span():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        assert span("a", "b", sep="\n") == "<span>a\nb</span>"


def test_a():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        result = a("a", "b", attrs={"href": "www.example.com"}, sep="\n")
        assert result == '<a href="www.example.com">a\nb</a>'


@pytest.mark.parametrize(
    "patch_env,test_input,expected_result",
    [
        (False, ["my text", "myurl"], "my text"),
        (True, ["my text", "myurl"], '<a href="myurl">my text</a>'),
    ],
)
def test_link(patch_env, test_input, expected_result):
    assert_function_result(link, patch_env, test_input, {}, expected_result)


@pytest.mark.parametrize(
    "patch_env,test_input,expected_result",
    [
        (
            False,
            ["a", "b", "c"],
            "['a', 'b', 'c']",
        ),
        (
            False,
            ["a", 53, "<ul><li>b</li></ul>"],
            "['a', 53, '<ul><li>b</li></ul>']",
        ),
        (
            True,
            ["a", "b", "c"],
            "<ul><li>a</li><li>b</li><li>c</li></ul>",
        ),
        (
            True,
            ["a", 43, 42],
            "<ul><li>a</li><li>43</li><li>42</li></ul>",
        ),
        (
            True,
            ["a", "<ul><li>b</li></ul>"],
            "<ul><li>a</li><ul><li>b</li></ul></ul>",
        ),
        (
            True,
            ["<ol><li>x</li></ol>", "a", "<ul><li>y</li><li>z</li></ul>"],
            "<ul><ol><li>x</li></ol><li>a</li><ul><li>y</li><li>z</li></ul></ul>",
        ),
    ],
)
def test_ulist__without_parameters(patch_env, test_input, expected_result):
    assert_function_result(ulist, patch_env, test_input, {}, expected_result)


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
    assert_function_result(ulist, True, test_input, input_kwargs, expected_result)


@pytest.mark.parametrize(
    "patch_env,test_input,expected_result",
    [
        (
            False,
            ["a", "b", "c"],
            "['a', 'b', 'c']",
        ),
        (
            False,
            ["a", 53, "<ol><li>b</li></ol>"],
            "['a', 53, '<ol><li>b</li></ol>']",
        ),
        (
            True,
            ["a", "b", "c"],
            "<ol><li>a</li><li>b</li><li>c</li></ol>",
        ),
        (
            True,
            ["a", 43, 42],
            "<ol><li>a</li><li>43</li><li>42</li></ol>",
        ),
        (
            True,
            ["a", "<ol><li>b</li></ol>"],
            "<ol><li>a</li><ol><li>b</li></ol></ol>",
        ),
        (
            True,
            ["<ol><li>x</li></ol>", "a", "<ol><li>y</li><li>z</li></ol>"],
            "<ol><ol><li>x</li></ol><li>a</li><ol><li>y</li><li>z</li></ol></ol>",
        ),
    ],
)
def test_olist__without_parameters(patch_env, test_input, expected_result):
    assert_function_result(olist, patch_env, test_input, {}, expected_result)


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
    assert_function_result(olist, True, test_input, input_kwargs, expected_result)


@pytest.mark.parametrize(
    "patch_env,input_args,input_kwargs,expected_result",
    [
        (
            False,
            ["a"],
            {"name": "x", "cl": None, "attrs": None, "sep": ""},
            "a",
        ),
        (
            False,
            [1],
            {"name": "x", "cl": None, "attrs": None, "sep": ""},
            "1",
        ),
        (
            True,
            ["abc"],
            {"name": "x", "cl": None, "attrs": None, "sep": ""},
            "<x>abc</x>",
        ),
        (
            True,
            [2351],
            {"name": "x", "cl": None, "attrs": None, "sep": ""},
            "<x>2351</x>",
        ),
        (
            False,
            [2351, "hello"],
            {"name": "abc", "cl": None, "attrs": None, "sep": "\n"},
            "2351\nhello",
        ),
        (
            True,
            [2351, "hello"],
            {"name": "abc", "cl": None, "attrs": None, "sep": "\n"},
            "<abc>\n2351\nhello\n</abc>",
        ),
        (
            True,
            [2351, "hello"],
            {"name": "abc", "cl": "cl1", "attrs": None, "sep": "\n"},
            '<abc class="cl1">\n2351\nhello\n</abc>',
        ),
        (
            True,
            [2351, "hello"],
            {"name": "abc", "cl": "cl1 cl2", "attrs": None, "sep": "\n"},
            '<abc class="cl1 cl2">\n2351\nhello\n</abc>',
        ),
        (
            True,
            [2351, "hello"],
            {"name": "abc", "cl": ["cl1", "cl2"], "attrs": None, "sep": "\n"},
            '<abc class="cl1 cl2">\n2351\nhello\n</abc>',
        ),
        (
            True,
            [2351, "hello"],
            {"name": "abc", "cl": None, "attrs": {"key": "val"}, "sep": "\n"},
            '<abc key="val">\n2351\nhello\n</abc>',
        ),
        (
            True,
            [2351, "hello"],
            {"name": "abc", "cl": ["cl1", "cl2"], "attrs": {"key": "val"}, "sep": "\n"},
            '<abc class="cl1 cl2" key="val">\n2351\nhello\n</abc>',
        ),
        (
            True,
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
def test_tag(patch_env, input_args, input_kwargs, expected_result):
    assert_function_result(tag, patch_env, input_args, input_kwargs, expected_result)


def test_tag__duplicate_class_setting():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        with pytest.raises(ValueError):
            tag("value", name="x", cl="my_class", attrs={"class": "my_cl"}, sep="")
