"""Text utils for creating strings with HTML elements."""

from typing import Any, List, Optional

from pyreball._common import AttrsParameter, ClParameter


def _construct_attrs_str(attrs: AttrsParameter) -> Optional[str]:
    if not attrs:
        return None
    return " ".join(
        [f'{k}="{v}"' if v is not None else f"{k}" for k, v in attrs.items()]
    )


def _construct_class_attr_string(cl: ClParameter) -> Optional[str]:
    if cl is None:
        return None
    cl_values = cl if isinstance(cl, str) else " ".join(cl)
    return _construct_attrs_str({"class": cl_values})


def bold(
    *values: Any, cl: ClParameter = None, attrs: AttrsParameter = None, sep: str = ""
) -> str:
    """
    Create a `<bold>` element string with given values.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="b", cl=cl, attrs=attrs, sep=sep)


def em(
    *values: Any, cl: ClParameter = None, attrs: AttrsParameter = None, sep: str = ""
) -> str:
    """
    Create a `<em>` element string with given values.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="em", cl=cl, attrs=attrs, sep=sep)


def _collect_classes_for_code_strings(
    initial_class_list: List[str],
    cl: ClParameter,
    syntax_highlight: Optional[str],
) -> ClParameter:
    classes_to_be_added = initial_class_list[:]
    if syntax_highlight is not None:
        classes_to_be_added.append(syntax_highlight)
        if cl is None:
            cl = classes_to_be_added
        elif isinstance(cl, str):
            cl = [cl, *classes_to_be_added]
        else:
            cl = cl + classes_to_be_added
    return cl


def code(
    *values: Any,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    sep: str = "",
    syntax_highlight: Optional[str] = "python",
) -> str:
    """
    Create a `<code>` element string with given values.

    This element is used to display a source code inline.
    It is possible to highlight the code syntax by setting `syntax_highlight`
    parameter to an appropriate string.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.
        syntax_highlight: Syntax highlighting language.
            Supported values can be obtained from highlight.js table
            https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md
            - see column "Aliases". If `None`, no highlighting is applied.
            When highlight is turned on, language name and `'inline-highlight'`
            are added to the element as classes.

    Returns:
        HTML string representing the tag with given values.
    """
    cl = _collect_classes_for_code_strings(["inline-highlight"], cl, syntax_highlight)
    return tag(*values, name="code", cl=cl, attrs=attrs, sep=sep)


def code_block(
    *values: Any,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    pre_cl: ClParameter = None,
    pre_attrs: AttrsParameter = None,
    sep: str = "",
    syntax_highlight: Optional[str] = "python",
) -> str:
    """
    Create a `<pre><code>` pair element string with given values.

    This element is used to display a source code in a block.
    It is possible to highlight the code syntax by setting `syntax_highlight`
    parameter to an appropriate string.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the <code> tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
            A class is also added when `syntax_highlight` is set.
        attrs: Additional attributes to be added to the <code> tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        pre_cl: The same as `cl` parameter, but for the `<pre>` tag.
        pre_attrs: The same as `attrs` parameter, but for the `<pre>` tag.
        sep: String separator of the values. Defaults to an empty string.
        syntax_highlight: Syntax highlighting language.
            Supported values can be obtained from highlight.js table
            https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md
            - see column "Aliases". If `None`, no highlighting is applied.
            When highlight is turned on, language name and `'block-highlight'`
            are added to the element as classes.

    Returns:
        HTML string representing the tag with given values.
    """
    cl = _collect_classes_for_code_strings(["block-highlight"], cl, syntax_highlight)
    code_text = tag(*values, name="code", cl=cl, attrs=attrs, sep=sep)
    return tag(code_text, name="pre", cl=pre_cl, attrs=pre_attrs)


def div(
    *values: Any, cl: ClParameter = None, attrs: AttrsParameter = None, sep: str = ""
) -> str:
    """
    Create a `<div>` element string with given values.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="div", cl=cl, attrs=attrs, sep=sep)


def span(
    *values: Any, cl: ClParameter = None, attrs: AttrsParameter = None, sep: str = ""
) -> str:
    """
    Create a `<span>` element string with given values.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.

    Returns:
        HTML string representing the tag with given values.
    """
    return tag(*values, name="span", cl=cl, attrs=attrs, sep=sep)


def a(
    *values: Any, cl: ClParameter = None, attrs: AttrsParameter = None, sep: str = ""
) -> str:
    """
    Create a `<a>` element string with given values.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.

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
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    sep: str = "",
) -> str:
    result = ""
    for value in values:
        value_str = "".join(map(str, value)) if isinstance(value, tuple) else str(value)
        result += tag(value_str, name="li", cl=cl, attrs=attrs, sep=sep)
    return result


def ulist(
    *values: Any,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    li_cl: ClParameter = None,
    li_attrs: AttrsParameter = None,
    sep: str = "",
) -> str:
    """
    Create a `<ul>` element string with values being enclosed into `<li>` tags.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the `<ul>` tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the `<ul>` tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        li_cl: The same as `cl` parameter, but for the `<li>` tag.
        li_attrs: The same as `attrs` parameter, but for the `<li>` tag.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    inner_content = _enclose_into_li_tags(*values, cl=li_cl, attrs=li_attrs, sep=sep)
    return tag(inner_content, name="ul", cl=cl, attrs=attrs, sep=sep)


def olist(
    *values: Any,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    li_cl: ClParameter = None,
    li_attrs: AttrsParameter = None,
    sep: str = "",
) -> str:
    """
    Create a `<ol>` element string with values being enclosed into `<li>` tags.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        cl: One or more class names to be added to the `<ol>` tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the `<ol>` tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        li_cl: The same as `cl` parameter, but for the `<li>` tag.
        li_attrs: The same as `attrs` parameter, but for the `<li>` tag.
        sep: Separator string to concatenate the values with.

    Returns:
        HTML string representing the tag with given values.
    """
    inner_content = _enclose_into_li_tags(*values, cl=li_cl, attrs=li_attrs, sep=sep)
    return tag(inner_content, name="ol", cl=cl, attrs=attrs, sep=sep)


def tag(
    *values: Any,
    name: str,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    sep: str = "",
    paired: bool = True,
) -> str:
    """
    Create a tag string with given values.

    Args:

        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        name: Name of the tag.
        cl: One or more class names to be added to the tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with a space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes,
            set `None` for given key. Any quotes in values are not escaped.
        sep: String separator of the values. Defaults to an empty string.
        paired: If True, the values are enclosed in a pair of tags.
            Otherwise, unpaired tag is created.

    Returns:
        HTML string representing the tag with given values.
    """
    cl_str = _construct_class_attr_string(cl)
    if cl_str and attrs is not None and "class" in attrs:
        raise ValueError(
            "class attribute cannot be set through cl and attrs parameters "
            "at the same time!"
        )
    attrs_str = _construct_attrs_str(attrs)
    opening_tag = (
        f"{name}{f' {cl_str}' if cl_str else ''}{f' {attrs_str}' if attrs_str else ''}"
    )
    if paired:
        inner_contents = sep.join(map(str, values))
        return f"<{opening_tag}>{sep}{inner_contents}{sep}</{name}>"
    else:
        return f"<{opening_tag}>"
