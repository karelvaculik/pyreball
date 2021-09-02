import pytest
from unittest.mock import patch

from pyreball.text import bold, em, code, ul, ol, link


def assert_strings_single_arg(func, patch_env, test_input, expected_result):
    with patch('pyreball.text.get_parameter_value', return_value=patch_env):
        assert func(test_input) == expected_result


def assert_strings_multiple_args(func, patch_env, test_input, expected_result):
    with patch('pyreball.text.get_parameter_value', return_value=patch_env):
        assert func(*test_input) == expected_result


@pytest.mark.parametrize("patch_env,test_input,expected_result", [
    (False, 'a', 'a'),
    (False, 1, '1'),
    (True, 'abc', '<b>abc</b>'),
    (True, 2351, '<b>2351</b>'),
])
def test_bold(patch_env, test_input, expected_result):
    assert_strings_single_arg(bold, patch_env, test_input, expected_result)


@pytest.mark.parametrize("patch_env,test_input,expected_result", [
    (False, 'a', 'a'),
    (False, 1, '1'),
    (True, 'abc', '<em>abc</em>'),
    (True, 2351, '<em>2351</em>'),
])
def test_em(patch_env, test_input, expected_result):
    assert_strings_single_arg(em, patch_env, test_input, expected_result)


@pytest.mark.parametrize("patch_env,test_input,expected_result", [
    (False, 'a', 'a'),
    (False, 1, '1'),
    (True, 'abc', '<code>abc</code>'),
    (True, 2351, '<code>2351</code>'),
])
def test_code(patch_env, test_input, expected_result):
    assert_strings_single_arg(code, patch_env, test_input, expected_result)


@pytest.mark.parametrize("patch_env,test_input,expected_result", [
    (False, ['a', 'b', 'c'], "['a', 'b', 'c']"),
    (False, ['a', 53, '<ul><li>b</li></ul>'], "['a', 53, '<ul><li>b</li></ul>']"),
    (True, ['a', 'b', 'c'], '<ul><li>a</li><li>b</li><li>c</li></ul>'),
    (True, ['a', 43, 42], '<ul><li>a</li><li>43</li><li>42</li></ul>'),
    (True, ['a', '<ul><li>b</li></ul>'], '<ul><li>a</li><ul><li>b</li></ul></ul>'),
    (True, ['<ol><li>x</li></ol>', 'a', '<ul><li>y</li><li>z</li></ul>'],
     '<ul><ol><li>x</li></ol><li>a</li><ul><li>y</li><li>z</li></ul></ul>'),
])
def test_ul(patch_env, test_input, expected_result):
    assert_strings_multiple_args(ul, patch_env, test_input, expected_result)


@pytest.mark.parametrize("patch_env,test_input,expected_result", [
    (False, ['a', 'b', 'c'], "['a', 'b', 'c']"),
    (False, ['a', 53, '<ol><li>b</li></ol>'], "['a', 53, '<ol><li>b</li></ol>']"),
    (True, ['a', 'b', 'c'], '<ol><li>a</li><li>b</li><li>c</li></ol>'),
    (True, ['a', 43, 42], '<ol><li>a</li><li>43</li><li>42</li></ol>'),
    (True, ['a', '<ol><li>b</li></ol>'], '<ol><li>a</li><ol><li>b</li></ol></ol>'),
    (True, ['<ol><li>x</li></ol>', 'a', '<ol><li>y</li><li>z</li></ol>'],
     '<ol><ol><li>x</li></ol><li>a</li><ol><li>y</li><li>z</li></ol></ol>'),
])
def test_ol(patch_env, test_input, expected_result):
    assert_strings_multiple_args(ol, patch_env, test_input, expected_result)


@pytest.mark.parametrize("patch_env,test_input,expected_result", [
    (False, ['my text', 'myurl'], '<a href="myurl">my text</a>'),
    (True, ['my text', 'myurl'], '<a href="myurl">my text</a>'),
])
def test_link(patch_env, test_input, expected_result):
    assert_strings_multiple_args(link, patch_env, test_input, expected_result)
