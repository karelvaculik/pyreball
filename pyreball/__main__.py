import argparse
import json
import os
import re
import sys
import xml
from pathlib import Path
from typing import cast, Dict, List, Optional, Tuple, Union
from xml.dom.minidom import parseString

import pkg_resources

from pyreball.constants import (
    CONFIG_INI_FILENAME,
    DEFAULT_PATH_TO_CONFIG,
    HTML_BEGIN_TEMPLATE_FILENAME,
    HTML_END_TEMPLATE_FILENAME,
    STYLES_TEMPLATE_FILENAME,
)
from pyreball.utils.logger import get_logger
from pyreball.utils.template_utils import get_css, get_html_begin, get_html_end
from pyreball.utils.utils import (
    carefully_remove_directory_if_exists,
    check_and_fix_parameters,
    check_paging_sizes_string_parameter,
    ChoiceParameter,
    get_file_config,
    IntegerParameter,
    merge_parameter_dictionaries,
    StringParameter,
    Substitutor,
)

logger = get_logger()

# keep the indentation in the following snippets!!!
JAVASCRIPT_CHANGE_EXPAND = """
    function change_expand(button, table_id){
        var table = document.getElementById(table_id);
        if (table.classList.contains("expanded")) {
            // collapse the table
            table.style.maxHeight = "390px";
            button.innerHTML = "⟱";
        } else {
            // expand the table
            table.style.maxHeight = "none";
            button.innerHTML = "⟰";
        }
        table.classList.toggle("expanded");
    }

"""
JAVASCRIPT_ON_LOAD = """

    window.onload = function() {
    //dom not only ready, but everything is loaded
      scrollers = document.getElementsByClassName("table-scroller");

      for (i = 0; i < scrollers.length; i++) {
        if (scrollers[i].scrollHeight == scrollers[i].clientHeight) {
            // hide the expand button
            expander_id = scrollers[i].id.replace('scroller', 'expander');
            expander = document.getElementById(expander_id);
            expander.style.display = "none";
        }
      }

    };
"""

JAVASCRIPT_ROLLING_PLOTS = """

    function next(div_id, button_next_id, button_prev_id) {
        var qElems = document.querySelectorAll(div_id + '>div');
        for (var i = 0; i < qElems.length; i++) {
            if (qElems[i].style.display != 'none') {
                qElems[i].style.display = 'none';
                qElems[i + 1].style.display = 'block';
                if (i == qElems.length - 2) {
                    document.getElementById(button_next_id).disabled = true;
                }
                document.getElementById(button_prev_id).disabled = false;
                break;
            }
        }
    }

    function previous(div_id, button_next_id, button_prev_id) {
        var qElems = document.querySelectorAll(div_id + '>div');
        for (var i = 0; i < qElems.length; i++) {
            if (qElems[i].style.display != 'none') {
                qElems[i].style.display = 'none';
                qElems[i - 1].style.display = 'block';
                if (i == 1) {
                    document.getElementById(button_prev_id).disabled = true;
                }
                document.getElementById(button_next_id).disabled = false;
                break;
            }
        }
    }

"""


def _replace_ids(html_path: Path) -> None:
    """
    Replace IDs of HTML elements to create working anchors based on references.

    Args:
        html_path: Path to the HTML file.
    """
    # collect all ids in form of "table-N-M", "img-N-M"
    all_table_and_img_ids = set()
    chapter_text_replacemenets = []
    with open(html_path, "r") as f:
        for line in f:
            # note that we don't need to replace only "table" ids by also "img" etc.
            results = re.findall(r"table-id[\d]+-[\d]+", line)
            if results:
                all_table_and_img_ids.update(results)
            results = re.findall(r"img-id[\d]+-[\d]+", line)
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
                    chapter_text_replacemenets.append(
                        (f">{link_id}<", f">{link_text}<")
                    )
    # Prepare all replacement definitions for a substitutor below
    replacements = []
    for element_id in all_table_and_img_ids:
        # Tables and images:
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
    modified_lines = []
    with open(html_path, "r") as f:
        for line in f:
            modified_lines.append(substitutor.sub(line))

    with open(html_path, "w") as f:
        f.writelines(modified_lines)


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


def insert_heading_title_and_toc(filename: Path, include_toc: bool = True):
    # fetch all lines
    with open(filename, "r") as f:
        lines = f.readlines()

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
        if '<div class="main_container">' in line:
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
                f'<a class="anchor-link" href="#toc_generated_0">¶</a></h1>\n'
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
    while 1 < current_level:
        lines.insert(lines_index, "</ul>\n")
        lines_index += 1
        current_level -= 1

    with open(filename, "w") as f:
        f.writelines(lines)


parameter_specifications = [
    ChoiceParameter(
        "--toc", choices=["yes", "no"], default="no", help="Include table of contents."
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
    ChoiceParameter(
        "--numbered-headings",
        choices=["yes", "no"],
        default="no",
        help="Number the headings.",
    ),
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
]


def _check_existence_of_config_files(
    config_dir_path: Path, recommendation_msg: str
) -> None:
    required_filename = [
        CONFIG_INI_FILENAME,
        STYLES_TEMPLATE_FILENAME,
        HTML_BEGIN_TEMPLATE_FILENAME,
        HTML_END_TEMPLATE_FILENAME,
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
    default_config_dir_path = DEFAULT_PATH_TO_CONFIG
    _check_existence_of_config_files(
        config_dir_path=default_config_dir_path,
        recommendation_msg="Try re-installing pyreball.",
    )
    return default_config_dir_path


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
    def __call__(self, parser, namespace, values, option_string=None):
        if values.strip() == "":
            raise argparse.ArgumentError(
                self, "Path argument cannot contain only whitespaces."
            )
        setattr(namespace, self.dest, Path(values))


def parse_arguments(args) -> Dict[str, Optional[Union[str, int]]]:
    parser = argparse.ArgumentParser(
        description=(
            "Generate Python report. "
            "All pyreball options must be specified before input-path argument. "
            "Any options or arguments after input-path are passed "
            "to the processed Python script. "
        )
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
        help="Input file path. Must represent an existing Python script.",
        action=PathAction,
    )
    parser.add_argument(
        "script-args",
        nargs=argparse.REMAINDER,
        help="Remaining arguments that are passed to the Python script.",
    )
    variables = vars(parser.parse_args(args))
    # positional arguments must be renamed manually
    variables["input_path"] = variables["input-path"]
    variables["script_args"] = variables["script-args"]
    del variables["input-path"]
    del variables["script-args"]
    return variables


def main() -> None:
    args_dict = parse_arguments(sys.argv[1:])
    script_args_string = " ".join(cast(List[str], args_dict.pop("script_args")))
    input_path = cast(Path, args_dict.pop("input_path"))
    input_path = input_path.expanduser().resolve()
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

    script_definitions = (
        JAVASCRIPT_CHANGE_EXPAND + JAVASCRIPT_ON_LOAD + JAVASCRIPT_ROLLING_PLOTS
    )

    css_definitions = get_css(
        filename=STYLES_TEMPLATE_FILENAME,
        directory=config_directory,
        page_width=cast(int, parameters["page_width"]),
    )

    html_begin = get_html_begin(
        template_path=Path(
            pkg_resources.resource_filename("pyreball", "cfg/html_begin.template")
        ),
        title=filename_stem,
        script_definitions=script_definitions,
        css_definitions=css_definitions,
    )
    html_end = get_html_end(
        template_path=Path(
            pkg_resources.resource_filename("pyreball", "cfg/html_end.template")
        )
    )

    with open(html_path, "w") as f:
        f.write(html_begin)
    try:
        # Use {sys.executable} instead of just "python" command as it may not work
        # correctly as a PyCharm external tool
        os.system(f"{sys.executable} {input_path} {script_args_string}")
    finally:
        with open(html_path, "a") as f:
            f.write(html_end)

    _replace_ids(html_path)
    insert_heading_title_and_toc(
        filename=html_path, include_toc=parameters["toc"] == "yes"
    )


if __name__ == "__main__":
    main()
