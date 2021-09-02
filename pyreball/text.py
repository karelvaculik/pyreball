"""Text utils that can be used to prepare strings from formatting, list and link tags."""
from typing import Any
from pyreball.utils.utils import get_parameter_value


def bold(value: Any) -> str:
    if get_parameter_value('html_file_path'):
        return "<b>" + str(value) + "</b>"
    else:
        return str(value)


def em(value: Any) -> str:
    if get_parameter_value('html_file_path'):
        return "<em>" + str(value) + "</em>"
    else:
        return str(value)


def code(value: Any) -> str:
    if get_parameter_value('html_file_path'):
        return "<code>" + str(value) + "</code>"
    else:
        return str(value)


def ul(*args: Any) -> str:
    if get_parameter_value('html_file_path'):
        result = "<ul>"
        for value in args:
            if isinstance(value, str) and (value.startswith("<ol>") or value.startswith("<ul>")):
                # don't append <li> if it is a nested list
                result += str(value)
            else:
                result += "<li>" + str(value) + "</li>"
        result += "</ul>"
        return result
    else:
        return str(list(args))


def ol(*args: Any) -> str:
    if get_parameter_value('html_file_path'):
        result = "<ol>"
        for value in args:
            if isinstance(value, str) and (value.startswith("<ol>") or value.startswith("<ul>")):
                # don't append <li> if it is a nested list
                result += str(value)
            else:
                result += "<li>" + str(value) + "</li>"
        result += "</ol>"
        return result
    else:
        return str(list(args))


def link(text: str, url: str) -> str:
    return f'<a href="{url}">{text}</a>'
