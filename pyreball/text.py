"""Text utils that can be used to prepare strings from formatting, list and link tags."""
from typing import Any, Dict, List, Optional, Union

from pyreball.utils.utils import get_parameter_value

ClassConfig = Optional[Union[str, List[str]]]
AttrsConfig = Optional[Dict[str, Optional[str]]]


def _construct_attrs_str(attrs: AttrsConfig) -> Optional[str]:
    # TODO: should the quotes in cl be escaped?
    if not attrs:
        return None
    return " ".join(
        [f'{k}="{v}"' if v is not None else f"{k}" for k, v in attrs.items()]
    )


def _construct_class_atr_string(cl: ClassConfig) -> Optional[str]:
    if cl is None:
        return None
    if isinstance(cl, str):
        cl_values = cl
    else:
        cl_values = " ".join(cl)
    return _construct_attrs_str({"class": cl_values})


def _enclose_in_tags(
        *value: Any, tag: str, cl: ClassConfig, attrs: AttrsConfig, sep: str
) -> str:
    inner_contents = sep.join(map(str, value))
    if get_parameter_value("html_file_path"):
        cl_str = _construct_class_atr_string(cl)
        if cl_str and attrs is not None and "class" in attrs:
            raise ValueError("class attribute cannot be set through cl and attrs parameters at the same time!")
        attrs_str = _construct_attrs_str(attrs)
        opening_tag = f"{tag}{f' {cl_str}' if cl_str else ''}{f' {attrs_str}' if attrs_str else ''}"
        return f"<{opening_tag}>{inner_contents}</{tag}>"
    else:
        return inner_contents


def bold(*value: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = "") -> str:
    return _enclose_in_tags(*value, tag="b", cl=cl, attrs=attrs, sep=sep)


def em(*value: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = "") -> str:
    return _enclose_in_tags(*value, tag="em", cl=cl, attrs=attrs, sep=sep)


def code(*value: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = "") -> str:
    return _enclose_in_tags(*value, tag="code", cl=cl, attrs=attrs, sep=sep)


def div(*value: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = "") -> str:
    return _enclose_in_tags(*value, tag="div", cl=cl, attrs=attrs, sep=sep)


def span(*value: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = "") -> str:
    return _enclose_in_tags(*value, tag="span", cl=cl, attrs=attrs, sep=sep)


# TODO add the new parameters also to ul()
def ul(*args: Any) -> str:
    if get_parameter_value("html_file_path"):
        result = "<ul>"
        for value in args:
            if isinstance(value, str) and (
                    value.startswith("<ol>") or value.startswith("<ul>")
            ):
                # don't append <li> if it is a nested list
                result += str(value)
            else:
                result += "<li>" + str(value) + "</li>"
        result += "</ul>"
        return result
    else:
        return str(list(args))


# TODO add the new parameters also to ol()
def ol(*args: Any) -> str:
    if get_parameter_value("html_file_path"):
        result = "<ol>"
        for value in args:
            if isinstance(value, str) and (
                    value.startswith("<ol>") or value.startswith("<ul>")
            ):
                # don't append <li> if it is a nested list
                result += str(value)
            else:
                result += "<li>" + str(value) + "</li>"
        result += "</ol>"
        return result
    else:
        return str(list(args))


# TODO add the new parameters also to link()
def link(text: str, url: str) -> str:
    return f'<a href="{url}">{text}</a>'
