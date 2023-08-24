from unittest.mock import patch

import pytest

from pyreball.text import (
    _construct_attrs_str,
    _construct_class_atr_string,
    _enclose_in_tags,
    bold,
    code,
    div,
    em,
    link,
    ol,
    span,
    ul,
)


def assert_strings_single_arg(func, patch_env, test_input, expected_result):
    with patch("pyreball.text.get_parameter_value", return_value=patch_env):
        assert func(test_input) == expected_result


def assert_strings_multiple_args(
    func, patch_env, test_input, input_kwargs, expected_result
):
    with patch("pyreball.text.get_parameter_value", return_value=patch_env):
        assert func(*test_input, **input_kwargs) == expected_result


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        (None, None),
        ("", 'class=""'),
        ([], 'class=""'),
        ("ab", 'class="ab"'),
        (["ab"], 'class="ab"'),
        (["ab", "e", "fg"], 'class="ab e fg"'),
    ],
)
def test__construct_class_atr_string(test_input, expected_result):
    assert _construct_class_atr_string(test_input) == expected_result


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
            {"x": "y", "checked": None, "a": "b", "valid": None},
            'x="y" checked a="b" valid',
        ),
    ],
)
def test__construct_attrs_str(test_input, expected_result):
    assert _construct_attrs_str(test_input) == expected_result


@pytest.mark.parametrize(
    "patch_env,input_args,input_kwargs,expected_result",
    [
        (
            False,
            ["a"],
            {"tag": "x", "cl": None, "attrs": None, "sep": ""},
            "a",
        ),
        (
            False,
            [1],
            {"tag": "x", "cl": None, "attrs": None, "sep": ""},
            "1",
        ),
        (
            True,
            ["abc"],
            {"tag": "x", "cl": None, "attrs": None, "sep": ""},
            "<x>abc</x>",
        ),
        (
            True,
            [2351],
            {"tag": "x", "cl": None, "attrs": None, "sep": ""},
            "<x>2351</x>",
        ),
        (
            False,
            [2351, "hello"],
            {"tag": "abc", "cl": None, "attrs": None, "sep": "\n"},
            "2351\nhello",
        ),
        (
            True,
            [2351, "hello"],
            {"tag": "abc", "cl": None, "attrs": None, "sep": "\n"},
            "<abc>2351\nhello</abc>",
        ),
        (
            True,
            [2351, "hello"],
            {"tag": "abc", "cl": ["cl1", "cl2"], "attrs": None, "sep": "\n"},
            '<abc class="cl1 cl2">2351\nhello</abc>',
        ),
        (
            True,
            [2351, "hello"],
            {"tag": "abc", "cl": None, "attrs": {"key": "val"}, "sep": "\n"},
            '<abc key="val">2351\nhello</abc>',
        ),
        (
            True,
            [2351, "hello"],
            {"tag": "abc", "cl": ["cl1", "cl2"], "attrs": {"key": "val"}, "sep": "\n"},
            '<abc class="cl1 cl2" key="val">2351\nhello</abc>',
        ),
    ],
)
def test__enclose_in_tags(patch_env, input_args, input_kwargs, expected_result):
    assert_strings_multiple_args(
        _enclose_in_tags, patch_env, input_args, input_kwargs, expected_result
    )


def test__enclose_in_tags__duplicate_class_setting():
    with patch("pyreball.text.get_parameter_value", return_value=True):
        with pytest.raises(ValueError):
            _enclose_in_tags(
                "value", tag="x", cl="my_class", attrs={"class": "my_cl"}, sep=""
            )


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
def test_ul(patch_env, test_input, expected_result):
    assert_strings_multiple_args(ul, patch_env, test_input, {}, expected_result)


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
def test_ol(patch_env, test_input, expected_result):
    assert_strings_multiple_args(ol, patch_env, test_input, {}, expected_result)


@pytest.mark.parametrize(
    "patch_env,test_input,expected_result",
    [
        (False, ["my text", "myurl"], '<a href="myurl">my text</a>'),
        (True, ["my text", "myurl"], '<a href="myurl">my text</a>'),
    ],
)
def test_link(patch_env, test_input, expected_result):
    assert_strings_multiple_args(link, patch_env, test_input, {}, expected_result)
