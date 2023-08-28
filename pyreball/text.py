"""Text utils for creating strings with HTML elements."""
import warnings
from typing import Any, Literal, Optional

from pyreball._common import AttrsConfig, ClassConfig
from pyreball.utils.utils import get_parameter_value


def _construct_attrs_str(attrs: AttrsConfig) -> Optional[str]:
    if not attrs:
        return None
    return " ".join(
        [f'{k}="{v}"' if v is not None else f"{k}" for k, v in attrs.items()]
    )


def _construct_class_attr_string(cl: ClassConfig) -> Optional[str]:
    if cl is None:
        return None
    if isinstance(cl, str):
        cl_values = cl
    else:
        cl_values = " ".join(cl)
    return _construct_attrs_str({"class": cl_values})


def bold(
    *values: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = ""
) -> str:
    """
    Create a `<bold>` element string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="b", cl=cl, attrs=attrs, sep=sep)


def em(
    *values: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = ""
) -> str:
    """
    Create a `<em>` element string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="em", cl=cl, attrs=attrs, sep=sep)


def code(
    *values: Any,
    cl: ClassConfig = None,
    attrs: AttrsConfig = None,
    sep: str = "",
    syntax_highlight: Optional[Literal["python"]] = "python",
) -> str:
    """
    Create a `<code>` element string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: Separator string to concatenate the values with.
        syntax_highlight: Syntax highlighting language. Currently only "python" is supported. If None,
            no highlight is applied. Highlight is achieved by adding values like `prettyprint` and `lang-py`
            to element's class.

    Returns:
        HTML string representing the tag with given values.
    """
    if syntax_highlight is not None:
        if syntax_highlight == "python":
            classes_to_be_added = ["language-python"]
        else:
            raise ValueError(
                f"Unsupported syntax highlighting language: {syntax_highlight}."
            )
        if cl is None:
            cl = classes_to_be_added
        elif isinstance(cl, str):
            cl = [cl] + classes_to_be_added
        else:
            cl += classes_to_be_added
    return tag(*values, name="code", cl=cl, attrs=attrs, sep=sep)


def div(
    *values: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = ""
) -> str:
    """
    Create a `<div>` element string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="div", cl=cl, attrs=attrs, sep=sep)


def span(
    *values: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = ""
) -> str:
    """
    Create a `<span>` element string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="span", cl=cl, attrs=attrs, sep=sep)


def a(
    *values: Any, cl: ClassConfig = None, attrs: AttrsConfig = None, sep: str = ""
) -> str:
    """
    Create a `<a>` element string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="a", cl=cl, attrs=attrs, sep=sep)


def link(text: str, href: str) -> str:
    """
    Create a `<a>` element string with given href and text.
    This function is a shortcut for `a()` function.

    Args:
        text: Text of the link.
        href: URL of the link.

    Returns:
        HTML string representing the tag with given values.
    """
    return a(text, attrs={"href": href})


def _enclose_into_li_tags(
    *values: Any,
    cl: ClassConfig = None,
    attrs: AttrsConfig = None,
    sep: str = "",
):
    result = ""
    for value in values:
        if isinstance(value, str) and (
            value.startswith("<ol") or value.startswith("<ul")
        ):
            # don't append <li> if it is a nested list
            result += str(value)
        else:
            result += tag(str(value), name="li", cl=cl, attrs=attrs, sep=sep)
    return result


def ulist(
    *values: Any,
    cl: ClassConfig = None,
    attrs: AttrsConfig = None,
    li_cl: ClassConfig = None,
    li_attrs: AttrsConfig = None,
    sep: str = "",
) -> str:
    """
    Create a `<ul>` element string with values being enclosed into `<li>` tags.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the `<ul>` tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the `<ul>` tag. Dictionary
            `{"key1": "value1", ..., "keyN": "valueN"}` is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes, set None for given key. Any quotes in values are not escaped.
        li_cl: The same as `cl` parameter, but for the `<li>` tag.
        li_attrs: The same as `attrs` parameter, but for the `<li>` tag.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    if get_parameter_value("html_file_path"):
        inner_content = _enclose_into_li_tags(
            *values, cl=li_cl, attrs=li_attrs, sep=sep
        )
        return tag(inner_content, name="ul", cl=cl, attrs=attrs, sep=sep)
    else:
        return str(list(values))


def olist(
    *values: Any,
    cl: ClassConfig = None,
    attrs: AttrsConfig = None,
    li_cl: ClassConfig = None,
    li_attrs: AttrsConfig = None,
    sep: str = "",
) -> str:
    """
    Create a `<ol>` element string with values being enclosed into `<li>` tags.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        cl: One or more class names to be added to the `<ol>` tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the `<ol>` tag. Dictionary
            `{"key1": "value1", ..., "keyN": "valueN"}` is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes, set None for given key. Any quotes in values are not escaped.
        li_cl: The same as `cl` parameter, but for the `<li>` tag.
        li_attrs: The same as `attrs` parameter, but for the `<li>` tag.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    if get_parameter_value("html_file_path"):
        inner_content = _enclose_into_li_tags(
            *values, cl=li_cl, attrs=li_attrs, sep=sep
        )
        return tag(inner_content, name="ol", cl=cl, attrs=attrs, sep=sep)
    else:
        return str(list(values))


def tag(
    *values: Any,
    name: str,
    cl: ClassConfig = None,
    attrs: AttrsConfig = None,
    sep: str = "",
    paired: bool = True,
) -> str:
    """
    Create a tag string with given values.

    Args:
        *values: One or more values to be enclosed in bold tag. All values are converted to strings.
        name: Name of the tag.
        cl: One or more class names to be added to the tag. If string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space. If None, no class is added.
        attrs: Additional attributes to be added to the tag. Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`. To construct boolean HTML attributes,
            set None for given key. Any quotes in values are not escaped.
        sep: Separator string to concatenate the values with.
        paired: If True, the values are enclosed in a pair of tags. Otherwise, unpaired tag is created.

    Returns:
        HTML string representing the tag with given values.
    """
    if get_parameter_value("html_file_path"):
        cl_str = _construct_class_attr_string(cl)
        if cl_str and attrs is not None and "class" in attrs:
            raise ValueError(
                "class attribute cannot be set through cl and attrs parameters at the same time!"
            )
        attrs_str = _construct_attrs_str(attrs)
        opening_tag = f"{name}{f' {cl_str}' if cl_str else ''}{f' {attrs_str}' if attrs_str else ''}"
        if paired:
            inner_contents = sep.join(map(str, values))
            return f"<{opening_tag}>{sep}{inner_contents}{sep}</{name}>"
        else:
            return f"<{opening_tag}>"
    else:
        return sep.join(map(str, values))


def ul(*args: Any) -> str:
    warnings.warn(
        "Function ul is now deprecated, use ulist instead.",
        DeprecationWarning,
        stacklevel=2,
    )
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


def ol(*args: Any) -> str:
    warnings.warn(
        "Function ol is now deprecated, use olist instead.",
        DeprecationWarning,
        stacklevel=2,
    )
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
