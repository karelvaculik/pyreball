import argparse
import json
import os
import re
import sys
import textwrap
import typing
import xml
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union, cast
from xml.dom.minidom import parseString

from pyreball._common import get_default_path_to_config
from pyreball.constants import (
    CONFIG_INI_FILENAME,
    HTML_TEMPLATE_FILENAME,
    LINKS_INI_FILENAME,
    STYLES_TEMPLATE_FILENAME,
)
from pyreball.utils.logger import get_logger
from pyreball.utils.param import (
    ChoiceParameter,
    IntegerParameter,
    StringParameter,
    Substitutor,
    carefully_remove_directory_if_exists,
    check_and_fix_parameters,
    check_paging_sizes_string_parameter,
    get_external_links_from_config,
    get_file_config,
    merge_parameter_dictionaries,
)
from pyreball.utils.template import get_css, get_html

logger = get_logger()


def _replace_ids(lines: List[str]) -> List[str]:
    """
    Replace IDs of HTML elements to create working anchors based on references.

    Args:
        lines: Lines of the html file.

    Returns:
        Updated lines of the html file.
    """
    # collect all ids in form of "table-N-M", "img-N-M"
    all_table_and_img_ids = set()
    chapter_text_replacemenets = []
    for line in lines:
        # we need to replace "table", "img", "code-block" and chapter IDs.
        results = re.findall(r"table-id[\d]+-[\d]+", line)
        if results:
            all_table_and_img_ids.update(results)
        results = re.findall(r"img-id[\d]+-[\d]+", line)
        if results:
            all_table_and_img_ids.update(results)
        results = re.findall(r"code-block-id[\d]+-[\d]+", line)
        if results:
            all_table_and_img_ids.update(results)
        # now collect heading references:
        results = re.findall(r"ch_id[\d]+_[^\"]+", line)
        if results:
            all_table_and_img_ids.update(results)
            # obtain also the heading text
            search_result_text = re.search(results[0] + r"\">([^<]+)<", line)
            link_text = search_result_text.group(1) if search_result_text else ""
            search_result_id = re.search(r"_(id[\d]+)_", results[0])
            link_id = search_result_id.group(1) if search_result_id else ""
            if link_id and link_text:
                chapter_text_replacemenets.append((f">{link_id}<", f">{link_text}<"))
    # Prepare all replacement definitions for a substitutor below
    replacements = []
    for element_id in all_table_and_img_ids:
        # Tables, images and code blocks:
        re_results = re.search(r"(.+)-(id\d+)-(\d+)", element_id)
        if re_results:
            # this must be first
            replacements.append(
                (
                    f"ref-{re_results.group(2)}",
                    f"{re_results.group(1)}-{re_results.group(3)}",
                )
            )
            # this must be second (because it would catch the first case as well)
            replacements.append(
                (
                    f"{re_results.group(2)}(-{re_results.group(3)})?",
                    re_results.group(3),
                )
            )

        # Headings
        re_results = re.search(r"ch_(id\d+)_(.+)", element_id)
        if re_results:
            # this must be first
            replacements.append(
                (
                    f"ref-{re_results.group(1)}",
                    f"ch_{re_results.group(2)}",
                )
            )
            # this must be second (because it would catch the first case as well)
            replacements.append((element_id, f"ch_{re_results.group(2)}"))
    # add also replacements for links to chapters
    replacements += chapter_text_replacemenets

    # replace all table-N-M with table-M and Table N with Table M
    substitutor = Substitutor(replacements=replacements)
    return [substitutor.sub(line) for line in lines]


def _get_node_text(node: xml.dom.minidom.Element) -> str:
    result = []
    for child in node.childNodes:
        if child.nodeType in (xml.dom.Node.TEXT_NODE, xml.dom.Node.CDATA_SECTION_NODE):
            result.append(child.data)
        else:
            result.extend(_get_node_text(child))
    return "".join(result)


def _parse_heading_info(line: str) -> Optional[Tuple[int, str, str]]:
    heading_pattern = r"<h(\d).+</h(\d)>"
    m = re.search(heading_pattern, line)
    if m:
        heading_level = m.group(1)

        doc = parseString(m.group(0))
        heading = doc.getElementsByTagName(f"h{heading_level}")[0]
        heading_id = heading.getAttribute("id")
        content = _get_node_text(heading).replace("¶", "")
        return int(heading_level), heading_id, content
    else:
        return None


def _insert_heading_title_and_toc(
    lines: List[str], include_toc: bool = True
) -> List[str]:
    # try to extract the title from <title> element:
    report_title = None
    for line in lines:
        m = re.match(r'^<title class="custom_pyreball_title">([^<]*)</title>$', line)
        if m:
            report_title = m.group(1)
            break

    # get all headings in the report
    container_start_index = 0
    headings = []
    for i, line in enumerate(lines):
        if '<div class="pyreball-main-container">' in line:
            container_start_index = i

        if include_toc:
            heading_info = _parse_heading_info(line)
            if heading_info:
                headings.append(heading_info)

    if len(headings) > 0 and report_title is None:
        # only when headings were collected (only when include_toc=True)
        # and there was not title set manually
        report_title = "Table of Contents"

    lines_index = container_start_index + 1

    # prepare new HTML lines with TOC
    if report_title is not None:
        lines.insert(
            lines_index,
            (
                f'<h1 id="toc_generated_0">{report_title}'
                f'<a class="pyreball-anchor-link" href="#toc_generated_0">¶</a></h1>\n'
            ),
        )
        lines_index += 1
    current_level = 1
    for h in headings:
        # do we need to add also <ul> ?
        while h[0] > current_level:
            lines.insert(lines_index, '<ul style="list-style-type:none; margin:0px">\n')
            lines_index += 1
            current_level += 1

        # do we need to add also </ul> ?
        while h[0] < current_level:
            lines.insert(lines_index, "</ul>\n")
            lines_index += 1
            current_level -= 1

        # prepare the line:
        if h[0] == 1:
            current_line = f'<a href="#{h[1]}">{h[2]}</a><br/>\n'
        else:
            current_line = f'<li><a href="#{h[1]}">{h[2]}</a></li>\n'
        lines.insert(lines_index, current_line)
        lines_index += 1

    # at the end, get back to level 1 if necessary
    while current_level > 1:
        lines.insert(lines_index, "</ul>\n")
        lines_index += 1
        current_level -= 1

    return lines


def _contains_class(html_text: str, class_name: str) -> bool:
    """
    Check whether the given HTML text contains the given class name in any element.

    Args:
        html_text: HTML text.
        class_name: Class to be found.

    Returns:
        True if the HTML text contains the given class name.
    """
    pattern = (
        r'class\s*=\s*["\']\s*(?:\S+\s+)*'
        + re.escape(class_name)
        + r'(?:\s+\S+)*\s*["\']'
    )
    return re.search(pattern, html_text) is not None


def _insert_js_and_css_links(
    html_content: str, external_links: Dict[str, List[str]]
) -> str:
    groups_of_links_to_add = set()
    add_jquery = False
    if (
        _contains_class(html_text=html_content, class_name="inline-highlight")
        or _contains_class(html_text=html_content, class_name="block-highlight")
        or _contains_class(html_text=html_content, class_name="pyreball-code-wrapper")
    ):
        add_jquery = True
        groups_of_links_to_add.add("highlight_js")
    if _contains_class(html_text=html_content, class_name="pyreball-table-wrapper"):
        add_jquery = True
        groups_of_links_to_add.add("datatables")
    if _contains_class(html_text=html_content, class_name="pyreball-altair-fig"):
        groups_of_links_to_add.add("altair")
    if _contains_class(html_text=html_content, class_name="pyreball-plotly-fig"):
        groups_of_links_to_add.add("plotly")
    if _contains_class(html_text=html_content, class_name="pyreball-bokeh-fig"):
        groups_of_links_to_add.add("bokeh")

    # gather all links; jquery must be first
    links_to_add = "\n".join(
        (external_links["jquery"] if add_jquery else [])
        + [
            el
            for group in sorted(groups_of_links_to_add)
            for el in external_links[group]
        ]
    )
    html_content = re.sub("<!--PYREBALL_HEAD_LINKS-->", links_to_add, html_content)
    return html_content


def _insert_inline_highlight_script(html_content: str) -> str:
    if _contains_class(html_text=html_content, class_name="inline-highlight"):
        script_text = textwrap.dedent(
            """
        <script>
            $(document).ready(function () {
                $('code.inline-highlight').each(function (i, block) {
                    hljs.highlightBlock(block);
                });
            });
        </script>"""
        )
        html_content = re.sub(
            "<!--PYREBALL_INLINE_HIGHLIGHT_SCRIPT-->", script_text, html_content
        )
    else:
        html_content = re.sub(
            "<!--PYREBALL_INLINE_HIGHLIGHT_SCRIPT-->", "", html_content
        )

    return html_content


def _finish_html_file(
    html_path: Path, include_toc: bool, external_links: Dict[str, List[str]]
) -> None:
    """
    Load the printed HTML and finish substitutions to make it complete.

    Args:
        html_path: Path to the HTML file.
        include_toc: Whether to include the table of contents.
    """
    with open(html_path) as f:
        lines = f.readlines()

    lines = _replace_ids(lines)
    lines = _insert_heading_title_and_toc(lines=lines, include_toc=include_toc)

    html_content = "".join(lines)
    html_content = _insert_js_and_css_links(html_content, external_links)
    html_content = _insert_inline_highlight_script(html_content)

    with open(html_path, "w") as f:
        f.write(html_content)


parameter_specifications = [
    IntegerParameter(
        "--page-width",
        boundaries=(40, 100),
        default=80,
        help=(
            "Width of the page container in percentage. "
            "An integer in the range 40..100. "
            "If set outside the range, the value will be shifted towards the range."
        ),
    ),
    ChoiceParameter(
        "--keep-stdout",
        choices=["yes", "no"],
        default="no",
        help="Print the output to stdout too.",
    ),
    ChoiceParameter(
        "--toc", choices=["yes", "no"], default="no", help="Include table of contents."
    ),
    ChoiceParameter(
        "--numbered-headings",
        choices=["yes", "no"],
        default="no",
        help="Number the headings.",
    ),
    ChoiceParameter(
        "--align-code-blocks",
        choices=["left", "center", "right"],
        default="center",
        help="Alignment of code blocks.",
    ),
    ChoiceParameter(
        "--code-block-captions-position",
        choices=["top", "bottom"],
        default="top",
        help="Position of the code block captions.",
    ),
    ChoiceParameter(
        "--numbered-code-blocks",
        choices=["yes", "no"],
        default="no",
        help="Number the code blocks.",
    ),
    ChoiceParameter(
        "--align-tables",
        choices=["left", "center", "right"],
        default="center",
        help="Alignment of tables.",
    ),
    ChoiceParameter(
        "--table-captions-position",
        choices=["top", "bottom"],
        default="top",
        help="Position of the table captions.",
    ),
    ChoiceParameter(
        "--numbered-tables",
        choices=["yes", "no"],
        default="no",
        help="Number the tables.",
    ),
    ChoiceParameter(
        "--tables-display-option",
        choices=["full", "paging", "scrolling"],
        default="full",
        help="How to display tables. Either full, with scrollbar, or with paging.",
    ),
    StringParameter(
        "--tables-paging-sizes",
        default="10,25,100,All",
        help=(
            "The paging sizes that can be selected. "
            "Allowed values are integers and string 'all' "
            "(no matter the case of letters), "
            "written as a non-empty comma-separated list. "
            "Ignored when tables-display-option is not 'paging'."
        ),
        validation_function=check_paging_sizes_string_parameter,
    ),
    StringParameter(
        "--tables-scroll-y-height",
        default="300px",
        help=(
            "Height of the tables when 'scrolling' display option is set. "
            "Any string compatible with CSS sizing can be used, "
            "e.g. '300px', '20em', etc. "
            "Ignored with other display options."
        ),
    ),
    ChoiceParameter(
        "--tables-scroll-x",
        choices=["yes", "no"],
        default="yes",
        help="Whether to allow horizontal scrolling on tables.",
    ),
    ChoiceParameter(
        "--sortable-tables",
        choices=["yes", "no"],
        default="no",
        help="Whether to make the tables sortable.",
    ),
    ChoiceParameter(
        "--tables-search-box",
        choices=["yes", "no"],
        default="no",
        help="Whether to show search box for tables.",
    ),
    StringParameter(
        "--tables-datatables-style",
        default="display",
        help=(
            "Datatables class(es) that affect the tables styling. "
            "If multiple classes are provided, "
            "separate them either with commas or spaces."
        ),
    ),
    ChoiceParameter(
        "--align-figures",
        choices=["left", "center", "right"],
        default="center",
        help="Alignment of figures.",
    ),
    ChoiceParameter(
        "--figure-captions-position",
        choices=["top", "bottom"],
        default="bottom",
        help="Position of the figure captions.",
    ),
    ChoiceParameter(
        "--numbered-figures",
        choices=["yes", "no"],
        default="no",
        help="Number the figures.",
    ),
    ChoiceParameter(
        "--matplotlib-format",
        choices=["png", "svg"],
        default="svg",
        help="Format of matplotlib figures.",
    ),
    ChoiceParameter(
        "--matplotlib-embedded",
        choices=["yes", "no"],
        default="no",
        help=(
            "Whether to embedded matplotlib figures directly into HTML. "
            "Only for svg format."
        ),
    ),
]


def _check_existence_of_config_files(
    config_dir_path: Path, recommendation_msg: str
) -> None:
    required_filename = [
        CONFIG_INI_FILENAME,
        LINKS_INI_FILENAME,
        STYLES_TEMPLATE_FILENAME,
        HTML_TEMPLATE_FILENAME,
    ]
    for filename in required_filename:
        if not (config_dir_path / filename).exists():
            raise FileNotFoundError(
                f"Config directory '{config_dir_path}' "
                f"does not contain all necessary files: "
                f"{', '.join(required_filename)}. {recommendation_msg}"
            )


def _get_config_directory(config_dir_path: Optional[Path] = None) -> Path:
    """Get the directory with the config files.

    If config path is provided by user, it is used primarily.
    If not, pyreball will try to check if config under home directory exists.
    If it does not exist, it will fall back to the default config directory
    in installation directory.
    In all cases, tbe function checks whether all config files exist.

    Args:
        config_dir_path: Optional path to the config file set by user
            through CLI argument. Can be a relative or absolute path
            and can contain ~ for home dir.

    Returns:
        An absolute path to the config directory.
    """
    rec_msg = "Try to regenerate the configs by pyreball-generate-config command."
    # Try to use the config directory from CLI argument
    if config_dir_path is not None:
        config_dir_path = config_dir_path.expanduser().resolve()
        if not config_dir_path.exists():
            raise NotADirectoryError(
                f"Provided config directory '{config_dir_path}' does not exist"
            )
        else:
            _check_existence_of_config_files(
                config_dir_path=config_dir_path, recommendation_msg=rec_msg
            )
            return config_dir_path

    # Try to use config directory from home directory if it exists
    home_config_dir_path = Path.home() / ".pyreball"
    if home_config_dir_path.exists():
        _check_existence_of_config_files(
            config_dir_path=home_config_dir_path, recommendation_msg=rec_msg
        )
        return home_config_dir_path

    # Fallback to the default config directory in installation directory
    default_config_dir_path = get_default_path_to_config()
    _check_existence_of_config_files(
        config_dir_path=default_config_dir_path,
        recommendation_msg="Try re-installing pyreball.",
    )
    return default_config_dir_path  # type: ignore[no-any-return]


def _get_output_dir_and_file_stem(
    input_path: Path, output_path_str: Optional[Path]
) -> Tuple[Path, str]:
    """
    Obtain the output directory for the HTML file and output filename stem.

    Args:
        input_path: Path to the input script. Can be a relative or absolute path
            and can contain ~ for home dir.
        output_path_str: Optional path denoting the output path.
            Either as path to an HTML file or a directory.
            Can be a relative or absolute path and can contain ~ for home dir.

    Returns:
        A tuple of (output_dir_path, filename_stem) where output_dir_path
        is an absolute path to the output directory, and filename_stem
        is the output filename stem.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"File {input_path} does not exist.")

    if not output_path_str:
        # use the directory of the input file
        output_dir_path = input_path.parents[0].resolve()
        filename_stem = input_path.stem
    else:
        output_path = output_path_str.expanduser().resolve()
        if output_path.suffix == ".html":
            filename_stem = output_path.stem
            output_dir_path = output_path.parents[0]
        else:
            output_dir_path = output_path
            filename_stem = input_path.stem
        output_dir_path.mkdir(parents=True, exist_ok=True)

    return output_dir_path, filename_stem


class PathAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Optional[Union[str, Sequence[Any]]],
        option_string: Optional[str] = None,
    ) -> None:
        if values is None:
            setattr(namespace, self.dest, values)
        elif isinstance(values, str):
            if values.strip() == "":
                raise argparse.ArgumentError(
                    self, "Path argument cannot contain only whitespaces."
                )
            setattr(namespace, self.dest, Path(values))
        else:
            raise ValueError("Unexpected argument type for values.")


def parse_arguments(args: List[str]) -> Dict[str, Optional[Union[str, int]]]:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Python report. "
            "Any options or arguments after '--' are passed "
            "to the processed Python script / module. "
        )
    )
    parser.add_argument(
        "-m",
        dest="mod",
        help=(
            "Run library module as a script. "
            "It calls Python command with -m option. "
            "It must represent an existing Python module, not package. "
            "Can be used only when input-path argument is not used."
        ),
    )
    for input_param in parameter_specifications:
        input_param.add_argument_to_parser(parser)
    parser.add_argument(
        "--output-path",
        help=(
            "Output path. Either path representing an HTML file or a directory. "
            "Any path with suffix different from '.html' will be considered "
            "a directory path. "
            "All parent directories are automatically created if they do not exist."
        ),
        action=PathAction,
    )
    parser.add_argument(
        "--config-path",
        help=(
            "Path to config directory. "
            "If not provided, Pyreball will try to use $HOME/.pyreball directory. "
            "If it does not exist, it will then try to use the default "
            "config directory in installation directory. "
        ),
        action=PathAction,
    )
    parser.add_argument(
        "input-path",
        help=(
            "Input file path. Must represent an existing Python script. "
            "Can be used only when -m option is not used."
        ),
        action=PathAction,
        nargs="?",
    )
    if "--" in args:
        index_of_double_dash = args.index("--")
        index_of_double_dash_plus = index_of_double_dash + 1
        script_args = args[index_of_double_dash_plus:]
        args = args[:index_of_double_dash]
    else:
        script_args = []
    variables = vars(parser.parse_args(args))
    # positional arguments must be renamed manually
    variables["input_path"] = variables["input-path"]
    variables["script_args"] = script_args
    if variables["input_path"] == "--":
        variables["input_path"] = None
    if variables["input_path"] is None and variables["mod"] is None:
        parser.error(
            "Input must be set either through input-path argument or -m option."
        )
    elif variables["input_path"] is not None and variables["mod"] is not None:
        parser.error(
            "It is not possible to set both input-path argument and -m option."
        )
    del variables["input-path"]
    return variables


def _convert_module_to_path(mod: str) -> Path:
    return Path(mod.replace(".", os.sep) + ".py")


@typing.no_type_check
def _get_path_to_html_template() -> Path:
    try:
        # Python >=3.9
        from importlib.resources import files  # type: ignore[attr-defined]

        return Path(files("pyreball") / "cfg" / HTML_TEMPLATE_FILENAME)
    except ImportError:
        # Python 3.8
        import pkg_resources

        return Path(
            pkg_resources.resource_filename("pyreball", f"cfg/{HTML_TEMPLATE_FILENAME}")
        )


def main() -> None:
    args_dict = parse_arguments(sys.argv[1:])
    script_args_string = " ".join(cast(List[str], args_dict.pop("script_args")))
    if args_dict["input_path"]:
        input_path = cast(Path, args_dict.pop("input_path"))
        input_path = input_path.expanduser().resolve()
        path_arg = str(input_path)
    elif args_dict["mod"]:
        input_module = cast(str, args_dict.pop("mod"))
        input_path = _convert_module_to_path(input_module)
        input_path = input_path.expanduser().resolve()
        path_arg = f"-m {input_module}"
    else:
        raise RuntimeError("input-path nor module is specified.")
    output_path = cast(Optional[Path], args_dict.pop("output_path"))
    config_path = cast(Optional[Path], args_dict.pop("config_path"))

    output_dir_path, filename_stem = _get_output_dir_and_file_stem(
        input_path, output_path
    )
    # Directory, where HTML's images would be stored;
    # It basically contains both the output directory and HTML filename stem
    # in one value.
    html_dir_path_str = str(output_dir_path / filename_stem)
    html_path = output_dir_path / f"{filename_stem}.html"

    cli_parameters = check_and_fix_parameters(
        parameters=args_dict,
        parameter_specifications=parameter_specifications,
        none_allowed=True,
    )

    config_directory = _get_config_directory(config_path)
    file_config_parameters = get_file_config(
        filename=CONFIG_INI_FILENAME,
        directory=config_directory,
        parameter_specifications=parameter_specifications,
    )
    external_links = get_external_links_from_config(
        filename=LINKS_INI_FILENAME,
        directory=config_directory,
    )

    parameters = merge_parameter_dictionaries(
        primary_parameters=cli_parameters,
        secondary_parameters=file_config_parameters,
        parameter_specifications=parameter_specifications,
    )

    os.environ["_TMP_PYREBALL_GENERATOR_PARAMETERS"] = json.dumps(
        {**parameters, "html_dir_path": html_dir_path_str}
    )

    # remove the directory with images if it exists:
    carefully_remove_directory_if_exists(directory=Path(html_dir_path_str))

    css_definitions = get_css(
        filename=STYLES_TEMPLATE_FILENAME,
        directory=config_directory,
        page_width=cast(int, parameters["page_width"]),
    )

    html_begin, html_end = get_html(
        template_path=_get_path_to_html_template(),
        title=filename_stem,
        css_definitions=css_definitions,
    )

    with open(html_path, "w") as f:
        f.write(html_begin)
    try:
        # Use {sys.executable} instead of just "python" command as it may not work
        # correctly as a PyCharm external tool
        os.system(f"{sys.executable} {path_arg} {script_args_string}")
    finally:
        with open(html_path, "a") as f:
            f.write(html_end)

    _finish_html_file(
        html_path=html_path,
        include_toc=parameters["toc"] == "yes",
        external_links=external_links,
    )


if __name__ == "__main__":
    main()
