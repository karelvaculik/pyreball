"""Main functions that serve as building blocks of the final html file."""

import builtins
import io
import json
import os
import random
import re
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

from pyreball._common import AttrsParameter, ClParameter
from pyreball.constants import NON_BREAKABLE_SPACE, PILCROW_SIGN
from pyreball.text import code_block, div
from pyreball.utils.param import get_parameter_value, make_sure_dir_exists, merge_values

if TYPE_CHECKING:
    # needed for mypy
    # noinspection PyUnresolvedReferences,PyPackageRequirements
    import altair  # type: ignore[unused-ignore]

    # noinspection PyPackageRequirements
    import bokeh  # type: ignore[unused-ignore]

    # noinspection PyPackageRequirements
    import matplotlib  # type: ignore[unused-ignore]

    # noinspection PyPackageRequirements
    import pandas  # type: ignore[unused-ignore]

    # noinspection PyPackageRequirements
    import plotly  # type: ignore[unused-ignore]

AltairFigType = Union[
    "altair.vegalite.v5.api.Chart",
    "altair.vegalite.v5.api.ConcatChart",
    "altair.vegalite.v5.api.FacetChart",
    "altair.vegalite.v5.api.HConcatChart",
    "altair.vegalite.v5.api.LayerChart",
    "altair.vegalite.v5.api.RepeatChart",
    "altair.vegalite.v5.api.VConcatChart",
]
FigType = Union[
    "matplotlib.figure.Figure",
    "plotly.graph_objs._figure.Figure",
    "altair.vegalite.v5.api.Chart",
    "altair.vegalite.v5.api.ConcatChart",
    "altair.vegalite.v5.api.FacetChart",
    "altair.vegalite.v5.api.HConcatChart",
    "altair.vegalite.v5.api.LayerChart",
    "altair.vegalite.v5.api.RepeatChart",
    "altair.vegalite.v5.api.VConcatChart",
]

_references: Set[str] = set()
_heading_memory: Dict[str, Any] = {}
_code_block_memory: Dict[str, Any] = {}
_table_memory: Dict[str, Any] = {}
_graph_memory: Dict[str, Any] = {}

ALIGN_CLASS_MAP = {
    "center": "pyreball-centered",
    "left": "pyreball-left-aligned",
    "right": "pyreball-right-aligned",
}


class Reference:
    """
    Class for creating references, i.e. anchors in HTML.
    """

    def __init__(self, default_text: Optional[str] = None) -> None:
        """
        Create a new reference.

        Args:
            default_text: Default text of the link.
                This text can be overriden by parameter of `__call__` method.
                If not provided, Pyreball automatically inserts a text.
                For tables, images and code blocks, their number is used.
                For headings, their text is used.
        """
        self.id = f"id{random.getrandbits(64)}"
        self.text = default_text

    def __str__(self) -> str:
        """
        Create a link string with default text.

        Returns:
            Link string.
        """
        return (
            f'<a href="#ref-{self.id}">'
            f"{self.id if self.text is None else self.text}"
            f"</a>"
        )

    def __call__(self, text: str) -> str:
        """
        Create a link string with given text.

        Args:
            text: Text of the link.

        Returns:
            Link string.
        """
        return f'<a href="#ref-{self.id}">{text}</a>'


def _check_and_mark_reference(reference: Reference) -> None:
    """Check and save a reference.

    This function is used when references are added to tables or figures.
    If a table or a figure is about to get a reference that was already used
    for another object, an error is raised.
    """
    if reference.id in _references:
        raise ValueError(
            "Reference is used for the second time. "
            "You have to create another reference for this object."
        )
    else:
        _references.add(reference.id)


def set_title(title: str) -> None:
    """
    Set page title.

    Note that this function does not have to be called at the beginning of the script.
    If this function is not called via pyreball and parameter keep_stdout
    is set to True, it just prints the title to stdout.

    Args:
        title: Title string.
    """
    if not get_parameter_value("html_file_path") or get_parameter_value("keep_stdout"):
        builtins.print(title)
    if get_parameter_value("html_file_path"):
        # it is assumed that the heading is already written into the file,
        # so find the line with title element and replace its contents
        with open(get_parameter_value("html_file_path")) as f:
            lines = f.readlines()

        # replace the title and also add "custom_pyreball_title" class,
        # so that we know it was replaced by this function
        lines = [
            re.sub(
                r"^<title>[^<]*</title>",
                f'<title class="custom_pyreball_title">{title}</title>',
                line,
            )
            for line in lines
        ]
        with open(get_parameter_value("html_file_path"), "w") as f:
            f.writelines(lines)


def _write_to_html(string: str, end: str = "\n") -> None:
    if get_parameter_value("html_file_path"):
        with open(get_parameter_value("html_file_path"), "a") as f:
            f.write(string)
            f.write(end)


def _tidy_title(title: str) -> str:
    """
    Transforms title into lowercase alphanumerical sequence separated by underscores.

    Args:
        title: The string that you want to transform.

    Returns:
        str: The transformed string.
    """
    new_title = re.sub(
        "([a-z])([A-Z])", r"\g<1> \g<2>", title
    )  # CamelCase -> words with spaces
    new_title = new_title.lower()  # to lower case
    new_title = re.sub(r"%", "_percent", new_title)  # replace % symbol with "_percent"
    new_title = re.sub(
        r"[=-\\.,]", " ", new_title
    )  # replace some special characters with spaces
    new_title = re.sub(
        r"[^\w\s]", "", new_title
    ).strip()  # remove remaining special characters
    new_title = re.sub(
        r"\s+", "_", new_title
    )  # replace sequences of spaces with an underscore
    return new_title


def _reduce_whitespaces(string: str) -> str:
    string = re.sub(r"\s+", " ", string)
    return string.strip()


def _get_heading_number(level: int, l_heading_counting: List[int]) -> str:
    return ".".join(map(str, l_heading_counting[:level]))


def _print_heading(
    string: str, level: int = 1, reference: Optional[Reference] = None
) -> None:
    if level > 6:
        raise ValueError("Heading level cannot be greater than 6.")
    if level < 1:
        raise ValueError("Heading level cannot be less than 1.")

    if "heading_index" not in _heading_memory:
        _heading_memory["heading_index"] = 1

    heading_index = _heading_memory["heading_index"]

    if get_parameter_value("numbered_headings"):
        if "heading_counting" not in _heading_memory:
            # what is the index of current h1, h2, h3, h4, h5, h6?
            _heading_memory["heading_counting"] = [0, 0, 0, 0, 0, 0]

        # increase the number in the level
        _heading_memory["heading_counting"][level - 1] = (
            _heading_memory["heading_counting"][level - 1] + 1
        )
        # reset all sub-levels
        _heading_memory["heading_counting"][level:] = [0] * (6 - level)
        # get the string of the numbered section and append non-breakable space
        heading_number_str = (
            _get_heading_number(level, _heading_memory["heading_counting"])
            + NON_BREAKABLE_SPACE
            + NON_BREAKABLE_SPACE
        )
    else:
        heading_number_str = ""

    string = heading_number_str + _reduce_whitespaces(string)
    # use heading_index in the id of the heading,
    # so there are no collisions in the case of same texts
    if reference:
        _check_and_mark_reference(reference)
        tidy_string = f"ch_{reference.id}_{_tidy_title(string)}_{heading_index}"
    else:
        tidy_string = f"ch_{_tidy_title(string)}_{heading_index}"

    if not get_parameter_value("html_file_path") or get_parameter_value("keep_stdout"):
        builtins.print(string.replace(NON_BREAKABLE_SPACE * 2, " "))

    if get_parameter_value("html_file_path"):
        header_contents = (
            f"{string}"
            f'<a class="pyreball-anchor-link" href="#{tidy_string}">{PILCROW_SIGN}</a>'
        )
        # For correct functioning of references,
        # it is expected that single line contains at most one heading,
        # and the heading is whole there with all links.
        _write_to_html(f'<h{level} id="{tidy_string}">{header_contents}</h{level}>')
        _heading_memory["heading_index"] += 1


def print_h1(string: str, reference: Optional[Reference] = None) -> None:
    """
    Print h1 heading.

    Args:
        string: Content of the heading.
        reference: Reference object.
    """
    _print_heading(string, level=1, reference=reference)


def print_h2(string: str, reference: Optional[Reference] = None) -> None:
    """
    Print h2 heading.

    Args:
        string: Content of the heading.
        reference: Reference object.
    """
    _print_heading(string, level=2, reference=reference)


def print_h3(string: str, reference: Optional[Reference] = None) -> None:
    """
    Print h3 heading.

    Args:
        string: Content of the heading.
        reference: Reference object.
    """
    _print_heading(string, level=3, reference=reference)


def print_h4(string: str, reference: Optional[Reference] = None) -> None:
    """
    Print h4 heading.

    Args:
        string: Content of the heading.
        reference: Reference object.
    """
    _print_heading(string, level=4, reference=reference)


def print_h5(string: str, reference: Optional[Reference] = None) -> None:
    """
    Print h5 heading.

    Args:
        string: Content of the heading.
        reference: Reference object.
    """
    _print_heading(string, level=5, reference=reference)


def print_h6(string: str, reference: Optional[Reference] = None) -> None:
    """
    Print h6 heading.

    Args:
        string: Content of the heading.
        reference: Reference object.
    """
    _print_heading(string, level=6, reference=reference)


def print_div(
    *values: Any,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    sep: str = "",
    end: str = "\n",
) -> None:
    """
    Print values into a div element.

    Any value that is not a string is converted to a string first.

    Args:
        *values: Zero or more values to be printed into the div.
        cl: One or more class names to be added to the `<div>` tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the `<div>` tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes, set `None` for given key.
            Any quotes in values are not escaped.
        sep: String separator of the values inside the tag. Defaults to an empty string.
        end: String appended after the tag. Defaults to a newline.
    """
    div_str = div(*values, cl=cl, attrs=attrs, sep=sep)
    print(div_str, end=end)


def _wrap_code_block_html(
    source_code_str: str,
    code_block_index: int = 0,
    caption: Optional[str] = None,
    reference: Optional[Reference] = None,
    align: str = "center",
    caption_position: str = "bottom",
    numbered: bool = True,
    sep: str = "",
) -> str:
    if reference:
        _check_and_mark_reference(reference)
        anchor_link = f"code-block-{reference.id}-{code_block_index}"
    else:
        anchor_link = f"code-block-{code_block_index}"

    caption_element = _prepare_caption_element(
        prefix="Source",
        caption=caption,
        numbered=numbered,
        index=code_block_index,
        anchor_link=anchor_link,
    )

    code_block_html = (
        f'<div class="pyreball-block-fit-content pyreball-centered">{sep}'
        f"{source_code_str}{sep}"
        f"</div>"
    )

    if caption_position == "top":
        code_block_html = caption_element + sep + code_block_html
    else:
        code_block_html = code_block_html + sep + caption_element

    code_block_html = (
        f'<div class="pyreball-block-fit-content {ALIGN_CLASS_MAP[align]}">{sep}'
        f"{code_block_html}{sep}</div>"
    )

    code_block_html = (
        f'<div class="pyreball-code-wrapper">{sep}{code_block_html}{sep}</div>'
    )

    return code_block_html


def print_code_block(
    *values: Any,
    caption: Optional[str] = None,
    reference: Optional[Reference] = None,
    align: Optional[str] = None,
    caption_position: Optional[str] = None,
    numbered: Optional[bool] = None,
    cl: ClParameter = None,
    attrs: AttrsParameter = None,
    pre_cl: ClParameter = None,
    pre_attrs: AttrsParameter = None,
    sep: str = "",
    end: str = "\n",
    syntax_highlight: Optional[str] = "python",
) -> None:
    """
    Print values as a source code into a preformatted block.

    This element is used to display a source code in a block.
    It is possible to highlight the code syntax by setting `syntax_highlight`
    parameter to an appropriate string.

    Args:
        *values: Zero or more values to be enclosed in the tag.
            All values are converted to strings.
        caption: Text caption.
        reference: Reference object.
        align: How to align the code block horizontally.
            Acceptable values are `'left'`, `'center'`, and `'right'`.
            Defaults to settings from config or CLI arguments if `None`.
        caption_position: Where to place the caption.
            Acceptable values are `'top'`, and `'bottom'`.
            Defaults to settings from config or CLI arguments if `None`.
        numbered: Whether the caption should be numbered.
            Defaults to settings from config or CLI arguments if `None`.
        cl: One or more class names to be added to the `<code>` tag.
            If a string is provided, it is used as it is.
            If a list of strings is provided, the strings are joined with space.
            If `None`, no class is added.
            If an empty list is provided, class attribute is added with an empty string.
        attrs: Additional attributes to be added to the `<code>` tag.
            Dictionary `{"key1": "value1", ..., "keyN": "valueN"}`
            is converted to `key1="value1" ... keyN="valueN"`.
            To construct boolean HTML attributes, set `None` for given key.
            Any quotes in values are not escaped.
        pre_cl: The same as `cl` parameter, but for the `<pre>` tag.
        pre_attrs: The same as `attrs` parameter, but for the `<pre>` tag.
        sep: String separator of the values inside the tag. Defaults to an empty string.
        end: String appended after the tag. Defaults to a newline.
        syntax_highlight: Syntax highlighting language.
            Supported values can be obtained from highlight.js table
            https://github.com/highlightjs/highlight.js/blob/main/SUPPORTED_LANGUAGES.md
            - see column "Aliases". If `None`, no highlighting is applied.
            When highlight is turned on, language name and `'block-highlight'`
            are added to the `<code>` element as classes.

    """

    source_code_str = code_block(
        *values,
        cl=cl,
        attrs=attrs,
        pre_cl=pre_cl,
        pre_attrs=pre_attrs,
        sep=sep,
        syntax_highlight=syntax_highlight,
    )
    if not get_parameter_value("html_file_path") or get_parameter_value("keep_stdout"):
        builtins.print(source_code_str)
    if get_parameter_value("html_file_path"):
        if "code_block_index" not in _code_block_memory:
            _code_block_memory["code_block_index"] = 1
        code_block_index = _code_block_memory["code_block_index"]

        align = cast(
            str,
            merge_values(
                primary_value=align,
                secondary_value=get_parameter_value("align_code_blocks"),
            ),
        )
        caption_position = cast(
            str,
            merge_values(
                primary_value=caption_position,
                secondary_value=get_parameter_value("code_block_captions_position"),
            ),
        )
        numbered = bool(
            merge_values(
                primary_value=numbered,
                secondary_value=get_parameter_value("numbered_code_blocks"),
            )
        )

        code_block_html = _wrap_code_block_html(
            source_code_str=source_code_str,
            code_block_index=code_block_index,
            caption=caption,
            reference=reference,
            align=align,
            caption_position=caption_position,
            numbered=numbered,
            sep=sep,
        )
        _write_to_html(code_block_html, end=end)

        _code_block_memory["code_block_index"] += 1


def print(*values: Any, sep: str = "", end: str = "\n") -> None:
    """Print values as strings to HTML file.

    Args:
        *values: Zero or more values to be printed.
            Each value is converted to a string first.
        sep: Separator string to concatenate the values with.
            Defaults to an empty space.
        end: String appended after the values. Defaults to a newline.
    """
    str_values = map(str, values)
    string = sep.join(str_values) + end
    if not get_parameter_value("html_file_path") or get_parameter_value("keep_stdout"):
        builtins.print(string)
    if get_parameter_value("html_file_path"):
        _write_to_html(string, end="")


def _prepare_caption_element(
    prefix: str, caption: Optional[str], numbered: bool, index: int, anchor_link: str
) -> str:
    if numbered:
        caption_text = f"{prefix} {index}"
        caption_text = f"{caption_text}: {caption}" if caption else f"{caption_text}."
    elif caption:
        caption_text = f"{caption}"
    else:
        caption_text = ""
    return (
        f'\n<div class="pyreball-text-centered">'
        f'<a id="{anchor_link}"><b>\n{caption_text}\n</b></a>'
        f"</div>\n"
    )


def _compute_length_menu_for_datatables(
    paging_sizes: List[Union[int, str]],
) -> Tuple[List[int], List[Union[int, str]]]:
    arr_1: List[int] = []
    arr_2: List[Union[int, str]] = []
    for size in paging_sizes:
        if isinstance(size, int):
            arr_1.append(size)
            arr_2.append(size)
        elif isinstance(size, str) and size.lower() == "all":
            arr_1.append(-1)
            arr_2.append(size)
        else:
            raise ValueError(f"Unsupported value in paging_sizes: {size}")
    return arr_1, arr_2


def _gather_datatables_setup(
    display_option: str = "full",
    scroll_y_height: str = "300px",
    scroll_x: bool = True,
    sortable: bool = False,
    sorting_definition: Optional[List[Tuple[int, str]]] = None,
    paging_sizes: Optional[List[Union[int, str]]] = None,
    search_box: bool = False,
    col_align_def: Optional[List[Dict[str, Any]]] = None,
    datatables_definition: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    if datatables_definition is not None:
        return datatables_definition

    datatables_setup: Dict[str, Any] = {}
    if display_option == "scrolling":
        datatables_setup["paging"] = False
        datatables_setup["scrollCollapse"] = True
        datatables_setup["scrollY"] = scroll_y_height
    elif display_option == "paging":
        datatables_setup["paging"] = True
        if paging_sizes is None:
            paging_sizes = [10, 25, 100, "All"]
        datatables_setup["lengthMenu"] = _compute_length_menu_for_datatables(
            paging_sizes
        )
    elif display_option == "full":
        datatables_setup["paging"] = False
    if scroll_x:
        datatables_setup["scrollX"] = True

    datatables_setup["info"] = False

    datatables_setup["searching"] = search_box

    if sortable or sorting_definition is not None:
        if sorting_definition is None:
            datatables_setup["order"] = []
        else:
            datatables_setup["order"] = sorting_definition
    else:
        datatables_setup["ordering"] = False

    if col_align_def is not None:
        datatables_setup["columnDefs"] = col_align_def

    return datatables_setup


def _check_col_alignment_value(value: str) -> None:
    allowed_values = ["left", "center", "right"]
    if value not in allowed_values:
        raise ValueError(
            "col_align must use only the following values: "
            f"{', '.join(allowed_values)}."
        )


def _prepare_col_alignment_definition(
    df: "pandas.DataFrame",
    col_align: Optional[Union[str, List[str]]] = None,
    index: bool = True,
) -> List[Dict[str, Any]]:
    if index:
        # when index is shown, we must also work with index columns
        df = df.reset_index()

    if col_align is None:
        # Pyreball's default alignment
        col_align = ["left"] * df.shape[1]
        for col in df.select_dtypes(include="number").columns:
            col_align[df.columns.get_loc(col)] = "right"
    elif isinstance(col_align, str):
        # All columns have the same alignment
        _check_col_alignment_value(col_align)
        return [{"targets": list(range(df.shape[1])), "className": f"dt-{col_align}"}]
    elif len(col_align) != df.shape[1]:
        # Alignment definition is a list and the length does not match
        raise ValueError(
            "col_align list must have the same length as the column list, "
            "including any index columns if they are shown too."
        )
    else:
        # it's a list with correct length, just check its values
        list(map(_check_col_alignment_value, col_align))

    # create alignment mapping in form <align_value> -> <col_indices>
    mapping: Dict[str, List[int]] = {}
    for i, al in enumerate(col_align):
        mapping.setdefault(al, []).append(i)

    # build final col definition for DataTables
    col_defs = []
    for key, value in mapping.items():
        col_defs.append({"targets": value, "className": f"dt-{key}"})
    return col_defs


def _prepare_table_html(
    df: "pandas.DataFrame",
    tab_index: int = 0,
    caption: Optional[str] = None,
    reference: Optional[Reference] = None,
    align: str = "center",
    caption_position: str = "top",
    numbered: bool = True,
    col_align: Optional[Union[str, List[str]]] = None,
    display_option: str = "full",
    scroll_y_height: str = "300px",
    scroll_x: bool = True,
    sortable: bool = False,
    sorting_definition: Optional[List[Tuple[int, str]]] = None,
    paging_sizes: Optional[List[Union[int, str]]] = None,
    search_box: bool = False,
    datatables_style: Union[str, List[str]] = "display",
    datatables_definition: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> str:
    table_classes = []
    if isinstance(datatables_style, list):
        table_classes += datatables_style
    else:
        table_classes.append(datatables_style)

    col_align_def = _prepare_col_alignment_definition(
        df=df, col_align=col_align, index=kwargs.get("index", True)
    )

    datatables_setup = _gather_datatables_setup(
        display_option=display_option,
        scroll_y_height=scroll_y_height,
        scroll_x=scroll_x,
        sortable=sortable,
        sorting_definition=sorting_definition,
        paging_sizes=paging_sizes,
        search_box=search_box,
        col_align_def=col_align_def,
        datatables_definition=datatables_definition,
    )

    if "border" not in kwargs:
        # If border is not set explicitly,
        # turn it off because it would clash with datatables styling
        kwargs["border"] = 0

    kwargs["sparsify"] = False
    df_html = df.to_html(classes=table_classes, **kwargs)
    if reference:
        _check_and_mark_reference(reference)
        anchor_link = f"table-{reference.id}-{tab_index}"
    else:
        anchor_link = f"table-{tab_index}"

    caption_element = _prepare_caption_element(
        prefix="Table",
        caption=caption,
        numbered=numbered,
        index=tab_index,
        anchor_link=anchor_link,
    )

    table_wrapper_inner_id = "pyreball-table-wrapper-inner-" + str(tab_index)
    table_html = (
        f'<div id="{table_wrapper_inner_id}" '
        f'class="pyreball-block-fit-content pyreball-centered">'
        f"{df_html}\n"
        f"</div>"
    )

    if caption_position == "top":
        table_html = caption_element + table_html
    else:
        table_html = table_html + caption_element

    table_html = (
        f'<div class="pyreball-block-fit-content {ALIGN_CLASS_MAP[align]}">'
        f"{table_html}</div>"
    )

    table_html = f'<div class="pyreball-table-wrapper">\n{table_html}\n</div>'

    if datatables_setup is not None:
        table_init = json.dumps(datatables_setup)
        js = f"new DataTable('#{table_wrapper_inner_id} > table', {table_init});"
        table_html += f"\n<script>{js}</script>"

    return table_html


def _parse_tables_paging_sizes(sizes: str) -> List[Union[int, str]]:
    return [
        value if value.lower() == "all" else int(value) for value in sizes.split(",")
    ]


def print_table(
    df: "pandas.DataFrame",
    caption: Optional[str] = None,
    reference: Optional[Reference] = None,
    align: Optional[str] = None,
    caption_position: Optional[str] = None,
    numbered: Optional[bool] = None,
    col_align: Optional[Union[str, List[str]]] = None,
    display_option: Optional[str] = None,
    paging_sizes: Optional[List[Union[int, str]]] = None,
    scroll_y_height: Optional[str] = None,
    scroll_x: Optional[bool] = None,
    sortable: Optional[bool] = None,
    sorting_definition: Optional[List[Tuple[int, str]]] = None,
    search_box: Optional[bool] = None,
    datatables_style: Optional[Union[str, List[str]]] = None,
    datatables_definition: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """Print pandas DataFrame into HTML.

    It uses DataTables JavaScript library to display the table.

    Args:
        df: Data frame to be printed.
        caption: Text caption.
        reference: Reference object.
        align: How to align the table horizontally.
            Acceptable values are `'left'`, `'center'`, and `'right'`.
            Defaults to settings from config or CLI arguments if `None`.
        caption_position: Where to place the caption.
            Acceptable values are `'top'`, and `'bottom'`.
            Defaults to settings from config or CLI arguments if `None`.
        numbered: Whether the caption should be numbered.
            Defaults to settings from config or CLI arguments if `None`.
        col_align: Alignment of individual columns. Can be provided as a list
            of values `'left'`, `'center'`, and `'right'`. The list must match the
            number of columns, including the index when displayed.
            When provided as a simple string, this value is used for all columns.
            When `None`, default Pyreball alignment is used, i.e. numeric columns
            are right-aligned and all other columns left-aligned.
        display_option: How to display the table. This option is useful for long tables,
            which should not be displayed fully. Acceptable values are:
            `'full'` (show the full table), `'scrolling'` (show the table
            in scrolling mode on y-axis), `'paging'` (show the table in paging mode).
            Defaults to settings from config or CLI arguments if `None`.
        paging_sizes: A list of page sizes to display in paging mode.
            Allowed values in the list are integer values and string
            `'All'` (the case is not important).
            When `display_option` is not `'paging'`, the value is ignored.
            Defaults to settings from config or CLI arguments if `None`.
            If it still remains `None`, values `[10, 25, 100, "All"]` are used.
        scroll_y_height: Height of the tables when `display_option` is set to
            `'scrolling'`. Any string compatible with CSS sizing can be used,
            e.g. `'300px'`, `'20em'`, etc. Ignored with other display options.
            Defaults to settings from config or CLI arguments if `None`.
        scroll_x: Whether to allow scrolling on the x-axis. If set to `False`,
            a wide table is allowed to overflow the main container.
            It is recommended to set this to `True`, especially with
            `display_option='scrolling'`, because otherwise the table header
            won't interact properly when scrolling horizontally.
        sortable: Whether to allow sortable columns.
            Defaults to settings from config or CLI arguments if `None`.
        sorting_definition: How to sort the table columns initially,
            in the form of a list of tuples `(<column_index>, <sorting>)`,
            where `<sorting>` is either `'asc'` or `'desc'`.
            When `None`, the columns are not pre-sorted.
        search_box: Whether to show the search box for the table.
            Defaults to settings from config or CLI arguments if `None`.
        datatables_style: One or more class names for styling tables using
            Datatables styling. See https://datatables.net/manual/styling/classes
            for possible values. Can be either a string with the class name,
            or a list of class name strings.
        datatables_definition: Custom setup for datatables in the form of a dictionary.
            This dictionary is serialized to json and passed to `DataTable` JavaScript
            object as it is. If set (i.e. not None), values of parameters
            `col_align`, `display_option`, `paging_sizes`, `scroll_y_height`,
            `scroll_x`, `sortable`, `sorting_definition`, and `search_box` are ignored.
            Note that `datatables_style` is independent of this parameter.
        **kwargs: Other parameters to pandas `to_html()` method. Note that parameter
            `sparsify` is explicitly set to `False` by Pyreball, because tables
            with multi-index would not be displayed correctly using DataTables library.
    """
    if not get_parameter_value("html_file_path") or get_parameter_value("keep_stdout"):
        builtins.print(df)
    if get_parameter_value("html_file_path"):
        if "table_index" not in _table_memory:
            _table_memory["table_index"] = 1
        table_index = _table_memory["table_index"]

        align = cast(
            str,
            merge_values(
                primary_value=align, secondary_value=get_parameter_value("align_tables")
            ),
        )
        caption_position = cast(
            str,
            merge_values(
                primary_value=caption_position,
                secondary_value=get_parameter_value("table_captions_position"),
            ),
        )
        numbered = bool(
            merge_values(
                primary_value=numbered,
                secondary_value=get_parameter_value("numbered_tables"),
            )
        )
        display_option = str(
            merge_values(
                primary_value=display_option,
                secondary_value=get_parameter_value("tables_display_option"),
            )
        )
        scroll_y_height = str(
            merge_values(
                primary_value=scroll_y_height,
                secondary_value=get_parameter_value("tables_scroll_y_height"),
            )
        )
        scroll_x = bool(
            merge_values(
                primary_value=scroll_x,
                secondary_value=get_parameter_value("tables_scroll_x"),
            )
        )
        sortable = bool(
            merge_values(
                primary_value=sortable,
                secondary_value=get_parameter_value("sortable_tables"),
            )
        )
        paging_sizes = merge_values(
            primary_value=paging_sizes,
            secondary_value=_parse_tables_paging_sizes(
                get_parameter_value("tables_paging_sizes")
            ),
        )
        search_box = bool(
            merge_values(
                primary_value=search_box,
                secondary_value=get_parameter_value("tables_search_box"),
            )
        )
        conf_datatables_style = get_parameter_value("tables_datatables_style")
        if conf_datatables_style:
            conf_datatables_style = re.split(r"[, ]", conf_datatables_style)
        datatables_style = cast(
            Union[str, List[str]],
            merge_values(
                primary_value=datatables_style,
                secondary_value=conf_datatables_style,
            ),
        )

        table_html = _prepare_table_html(
            df=df,
            tab_index=table_index,
            caption=caption,
            reference=reference,
            align=align,
            caption_position=caption_position,
            numbered=numbered,
            col_align=col_align,
            display_option=display_option,
            scroll_y_height=scroll_y_height,
            scroll_x=scroll_x,
            sortable=sortable,
            sorting_definition=sorting_definition,
            paging_sizes=paging_sizes,
            search_box=search_box,
            datatables_style=datatables_style,
            datatables_definition=datatables_definition,
            **kwargs,
        )
        _write_to_html(table_html)
        _table_memory["table_index"] += 1


def _construct_image_anchor_link(reference: Optional[Reference], fig_index: int) -> str:
    if reference:
        _check_and_mark_reference(reference)
        return f"img-{reference.id}-{fig_index}"
    else:
        return f"img-{fig_index}"


def _wrap_image_element_by_outer_divs(
    img_element: str, align: str, img_type: str
) -> str:
    img_element = (
        f'<div align="{align}"><div style="display: inline-block;">'
        f"{img_element}"
        f"</div></div>"
    )
    wrapper_classes = f"pyreball-image-wrapper pyreball-{img_type}-fig"
    return f'<div class="{wrapper_classes}">{img_element}</div>'


def _prepare_matplotlib_image_element(
    fig: "matplotlib.figure.Figure",
    fig_index: int,
    image_format: Optional[str] = None,
    embedded: Optional[bool] = None,
) -> str:
    if image_format is not None and image_format not in ["svg", "png"]:
        raise ValueError('Matplotlib format can be only "svg" or "png".')

    image_format = merge_values(
        primary_value=image_format,
        secondary_value=get_parameter_value("matplotlib_format"),
    )
    embedded = merge_values(
        primary_value=embedded,
        secondary_value=get_parameter_value("matplotlib_embedded"),
    )

    if embedded:
        if image_format == "svg":
            f = io.BytesIO()
            fig.savefig(f, format="svg")
            img_element = f.getvalue().decode("utf-8")
        else:
            raise ValueError(
                "Only svg format can be used for embedded matplotlib figures."
            )
    elif get_parameter_value("html_dir_path") and get_parameter_value("html_dir_name"):
        make_sure_dir_exists(get_parameter_value("html_dir_path"))
        img_file_name = f"img_{fig_index:03d}.{image_format}"
        fig.savefig(
            os.path.join(get_parameter_value("html_dir_path"), img_file_name),
            format=image_format,
            bbox_inches="tight",
        )
        img_element = (
            f'<img src="'
            f'{os.path.join(get_parameter_value("html_dir_name"), img_file_name)}'
            f'">'
        )
    else:
        raise RuntimeError("Failed to create a matplotlib image.")
    return img_element


def _prepare_altair_image_element(fig: AltairFigType, fig_index: int) -> str:
    vis_id = "altairvis" + str(fig_index)
    img_element = (
        f'<div id="{vis_id}">'
        f'</div><script type="text/javascript">\nvar spec = {fig.to_json()};\n'
    )
    img_element += 'var opt = {"renderer": "canvas", "actions": false};\n'
    img_element += f'vegaEmbed("#{vis_id}", spec, opt);'
    img_element += "</script>"
    return img_element


def _prepare_plotly_image_element(fig: "plotly.graph_objs.Figure") -> str:
    return cast(str, fig.to_html(full_html=False, include_plotlyjs=False))


def _prepare_bokeh_image_element(fig: "bokeh.plotting._figure.figure") -> str:
    # noinspection PyPackageRequirements
    from bokeh.embed import components  # type: ignore[unused-ignore]

    script, div = components(fig)
    return f"<div>{div}{script}</div>"


def _prepare_image_element(
    fig: FigType,
    fig_index: int,
    matplotlib_format: Optional[str] = None,
    embedded: Optional[bool] = None,
) -> Tuple[str, str]:
    # Create the html string according to the figure type.
    # (if we checked type of fig, we would have to add the libraries to requirements)
    if (
        type(fig).__name__ == "Figure" and type(fig).__module__ == "matplotlib.figure"
    ) or (
        type(fig).__name__ == "PairGrid" and type(fig).__module__ == "seaborn.axisgrid"
    ):
        img_element = _prepare_matplotlib_image_element(
            fig=fig,
            fig_index=fig_index,
            image_format=matplotlib_format,
            embedded=embedded,
        )
        img_type = "matplotlib"
    elif type(fig).__name__ in [
        "Chart",
        "ConcatChart",
        "FacetChart",
        "HConcatChart",
        "LayerChart",
        "RepeatChart",
        "VConcatChart",
    ]:
        img_element = _prepare_altair_image_element(fig=fig, fig_index=fig_index)
        img_type = "altair"
    elif (
        type(fig).__name__ == "Figure"
        and type(fig).__module__ == "plotly.graph_objs._figure"
    ):
        img_element = _prepare_plotly_image_element(fig=fig)
        img_type = "plotly"
    elif type(fig).__name__.lower() == "figure" and type(fig).__module__ in [
        "bokeh.plotting.figure",
        "bokeh.plotting._figure",
    ]:
        img_element = _prepare_bokeh_image_element(fig=fig)
        img_type = "bokeh"
    else:
        raise ValueError(f"Unknown figure type {type(fig)}.")

    return img_element, img_type


def _print_figure(
    fig: FigType,
    caption: Optional[str] = None,
    reference: Optional[Reference] = None,
    align: str = "center",
    caption_position: str = "bottom",
    numbered: bool = True,
    matplotlib_format: Optional[str] = None,
    embedded: Optional[bool] = None,
) -> None:
    if not get_parameter_value("html_file_path"):
        # only when we don't print to HTML
        if type(fig).__name__.lower() == "figure" and type(fig).__module__ in [
            "bokeh.plotting.figure",
            "bokeh.plotting._figure",
        ]:
            from bokeh.plotting import show

            show(fig)
        else:
            fig.show()
    else:
        if "fig_index" not in _graph_memory:
            _graph_memory["fig_index"] = 1
        fig_index = _graph_memory["fig_index"]

        anchor_link = _construct_image_anchor_link(
            reference=reference, fig_index=fig_index
        )
        img_element, img_type = _prepare_image_element(
            fig=fig,
            fig_index=fig_index,
            matplotlib_format=matplotlib_format,
            embedded=embedded,
        )
        caption_element = _prepare_caption_element(
            prefix="Figure",
            caption=caption,
            numbered=numbered,
            index=fig_index,
            anchor_link=anchor_link,
        )

        if caption_position == "bottom":
            img_with_caption = img_element + caption_element
        elif caption_position == "top":
            img_with_caption = caption_element + img_element
        else:
            raise ValueError(
                f"caption_position must be 'top' or 'bottom', not {caption_position}."
            )
        img_html = _wrap_image_element_by_outer_divs(
            img_element=img_with_caption,
            align=align,
            img_type=img_type,
        )

        _write_to_html(img_html)
        _graph_memory["fig_index"] += 1


def print_figure(
    fig: FigType,
    caption: Optional[str] = None,
    reference: Optional[Reference] = None,
    align: Optional[str] = None,
    caption_position: Optional[str] = None,
    numbered: Optional[bool] = None,
    matplotlib_format: Optional[str] = None,
    embedded: Optional[bool] = None,
) -> None:
    """
    Print a figure.

    Args:
        fig: A figure object.
        caption: Caption of the figure.
        reference: Reference object for link creation.
        align: How to align the graph horizontally.
            Acceptable values are `'left'`, `'center'`, and `'right'`.
            Defaults to settings from config or CLI arguments if `None`.
        caption_position: Where to place the caption.
            Acceptable values are `'top'`, and `'bottom'`.
            Defaults to settings from config or CLI arguments if `None`.
        numbered: Whether the caption should be numbered.
            Defaults to settings from config or CLI arguments if `None`.
        matplotlib_format: Format for matplotlib figures.
            Acceptable values are `'svg'`, and `'png'`.
            Defaults to settings from config or CLI arguments if `None`.
        embedded: Whether to embed the figure directly into HTML;
            Only applicable for matplotlib svg images.
            Defaults to settings from config or CLI arguments if `None`.
    """

    align = cast(
        str,
        merge_values(
            primary_value=align, secondary_value=get_parameter_value("align_figures")
        ),
    )
    caption_position = cast(
        str,
        merge_values(
            primary_value=caption_position,
            secondary_value=get_parameter_value("figure_captions_position"),
        ),
    )
    numbered = bool(
        merge_values(
            primary_value=numbered,
            secondary_value=get_parameter_value("numbered_figures"),
        )
    )

    _print_figure(
        fig=fig,
        caption=caption,
        reference=reference,
        align=align,
        caption_position=caption_position,
        numbered=numbered,
        matplotlib_format=matplotlib_format,
        embedded=embedded,
    )
