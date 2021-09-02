import sys
from pathlib import Path
import argparse
import os
import re
import json
from typing import Dict, Optional, Union, Tuple, cast
import xml
from xml.dom.minidom import parseString

import pkg_resources

from pyreball.constants import (
    PATH_TO_CONFIG_LOCATION,
    DEFAULT_PATH_TO_CONFIG,
    STYLES_TEMPLATE_FILENAME,
    CONFIG_INI_FILENAME,
)
from pyreball.utils.logger import get_logger
from pyreball.utils.utils import (
    get_file_config,
    check_and_fix_parameters,
    merge_parameter_dictionaries,
    ChoiceParameter,
    IntegerParameter,
    carefully_remove_directory_if_exists,
    Substitutor,
)
from pyreball.utils.template_utils import get_css, get_html_begin, get_html_end

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

JAVASCRIPT_SORTABLE_TABLE = """

    $(document).ready(function () {
        $('.sortable_table').DataTable({
            "paging": false,
            "searching": false,
            "info": false,
        });
    });

"""


def replace_ids(filename: Path) -> None:
    # collect all ids in form of table-N-M
    all_table_and_img_ids = set()
    with open(filename, "r") as f:
        for line in f:
            # note that we don't need to replace only "table" ids by also "img" etc.
            results = re.findall(r'table-id[\d]+-[\d]+', line)
            if results:
                all_table_and_img_ids.update(results)
            results = re.findall(r'img-id[\d]+-[\d]+', line)
            if results:
                all_table_and_img_ids.update(results)
    replacements = []
    for element_id in all_table_and_img_ids:
        re_results = re.search(r'(.+)-(id\d+)-(\d+)', element_id)

        if re_results:
            # this must be first
            replacements.append(("ref-" + re_results.group(2), re_results.group(1) + "-" + re_results.group(3)))
            # this must be second (because it would catch the first case as well)
            replacements.append((re_results.group(2) + '(-' + re_results.group(3) + ')?', re_results.group(3)))

    # replace all table-N-M with table-M and Table N with Table M
    substitutor = Substitutor(replacements=replacements)
    modified_lines = []
    with open(filename, "r") as f:
        for line in f:
            modified_lines.append(substitutor.sub(line))

    with open(filename, "w") as f:
        f.writelines(modified_lines)


def _get_node_text(node: xml.dom.minidom.Element) -> str:
    result = []
    for child in node.childNodes:
        if child.nodeType in (xml.dom.Node.TEXT_NODE, xml.dom.Node.CDATA_SECTION_NODE):
            result.append(child.data)
        else:
            result.extend(_get_node_text(child))
    return ''.join(result)


def _parse_heading_info(line: str) -> Optional[Tuple[int, str, str]]:
    heading_pattern = r'<h(\d).+</h(\d)>'
    m = re.search(heading_pattern, line)
    if m:
        heading_level = m.group(1)

        doc = parseString(m.group(0))
        heading = doc.getElementsByTagName("h" + heading_level)[0]
        heading_id = heading.getAttribute('id')
        content = _get_node_text(heading).replace('¶', '')
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
        m = re.match(r'^<title class="custom">([^<]*)</title>$', line)
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
        # only when headings were collected (only when include_toc=True) and there was not title set manually
        report_title = "Table of Contents"

    lines_index = container_start_index + 1

    # prepare new HTML lines with TOC
    if report_title is not None:
        lines.insert(
            lines_index,
            f'<h1 id="toc_generated_0">{report_title}<a class="anchor-link" href="#toc_generated_0">¶</a></h1>\n'
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
            lines.insert(lines_index, '</ul>\n')
            lines_index += 1
            current_level -= 1

        # prepare the line:
        if h[0] == 1:
            current_line = '<a href="#' + h[1] + '">' + h[2] + '</a><br/>\n'
        else:
            current_line = '<li><a href="#' + h[1] + '">' + h[2] + '</a></li>\n'
        lines.insert(lines_index, current_line)
        lines_index += 1

    # at the end, get back to level 1 if necessary
    while 1 < current_level:
        lines.insert(lines_index, '</ul>\n')
        lines_index += 1
        current_level -= 1

    with open(filename, "w") as f:
        f.writelines(lines)


parameter_specifications = [
    ChoiceParameter('--toc', choices=['yes', 'no'], default='no', help='Include table of contents.'),
    ChoiceParameter('--align-tables', choices=['left', 'center', 'right'], default='center',
                    help='Alignment of tables.'),
    ChoiceParameter('--numbered-tables', choices=['yes', 'no'], default='no', help='Number the tables.'),
    ChoiceParameter('--sortable-tables', choices=['yes', 'no'], default='no', help='Make the tables sortable.'),
    ChoiceParameter('--full-tables', choices=['yes', 'no'], default='no', help='Force all tables to be expanded.'),
    ChoiceParameter('--align-plots', choices=['left', 'center', 'right'], default='center', help='Alignment of plots.'),
    ChoiceParameter('--numbered-plots', choices=['yes', 'no'], default='no', help='Number the plots.'),
    ChoiceParameter('--matplotlib-format', choices=['png', 'svg'], default='svg', help='Format of matplotlib plots.'),
    ChoiceParameter('--matplotlib-embedded', choices=['yes', 'no'], default='no',
                    help='Whether to embedded matplotlib images directly into HTML. Only for svg format.'),
    ChoiceParameter('--numbered-headings', choices=['yes', 'no'], default='no', help='Number the headings.'),
    IntegerParameter('--page-width', boundaries=(40, 100), default=80,
                     help='Width of the page in percentage. An integer in the range 40..100.'),
    ChoiceParameter('--keep-stdout', choices=['yes', 'no'], default='no', help='Print the output to stdout too.'),
]


def parse_arguments() -> Dict[str, Optional[Union[str, int]]]:
    parser = argparse.ArgumentParser(description='Generate Python report.')
    for input_param in parameter_specifications:
        input_param.add_argument_to_parser(parser)
    parser.add_argument('--output-dir', help='Output directory. By default, the directory of the input file.')
    parser.add_argument('filename', help='Input file path.')
    args = parser.parse_args()
    return vars(args)


def get_config_directory() -> Path:
    """Get the location of the config files.

    If the configs were generated by pyreball-generate-config command, they should be found.
    If they were not generated or some of them no longer exist, the default package config will be used.
    """
    config_location_file_path = Path(PATH_TO_CONFIG_LOCATION)
    if config_location_file_path.exists():
        # the config was generated, let's find out its directory
        config_directory = Path(Path(PATH_TO_CONFIG_LOCATION).read_text())
        if not (config_directory / CONFIG_INI_FILENAME).exists() \
                or not (config_directory / STYLES_TEMPLATE_FILENAME).exists():
            logger.warning(f'{CONFIG_INI_FILENAME} or {STYLES_TEMPLATE_FILENAME} was not found in {config_directory}. '
                           f'Try re-generating the configs by pyreball-generate-config command. For now, we will '
                           f'use the default package configs.')
            config_directory = DEFAULT_PATH_TO_CONFIG
    else:
        config_directory = DEFAULT_PATH_TO_CONFIG
    return config_directory


def main() -> None:
    args_dict = parse_arguments()
    filename = Path(args_dict.pop('filename'))  # type: ignore
    output_dir = cast(Optional[str], args_dict.pop('output_dir'))
    cli_parameters = check_and_fix_parameters(parameters=args_dict, parameter_specifications=parameter_specifications,
                                              none_allowed=True)

    config_directory = get_config_directory()
    file_config_parameters = get_file_config(filename=CONFIG_INI_FILENAME, directory=config_directory,
                                             parameter_specifications=parameter_specifications)

    parameters = merge_parameter_dictionaries(primary_parameters=cli_parameters,
                                              secondary_parameters=file_config_parameters,
                                              parameter_specifications=parameter_specifications)

    if not filename.is_file():
        raise ValueError(f"File {filename} does not exist.")

    title = filename.stem
    if not output_dir:
        # use the directory of the input file
        output_dir_path = filename.resolve().parents[0]
    else:
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)
    path_str = str(output_dir_path / title)
    os.environ["_TMP_PYREBALL_GENERATOR_PARAMETERS"] = json.dumps({**parameters, 'html_dir_path': path_str})
    html_path = Path(path_str + ".html")

    # remove the directory with images if it exists:
    carefully_remove_directory_if_exists(directory=Path(path_str))

    script_definitions = (JAVASCRIPT_CHANGE_EXPAND + JAVASCRIPT_ON_LOAD + JAVASCRIPT_SORTABLE_TABLE
                          + JAVASCRIPT_ROLLING_PLOTS)

    css_definitions = get_css(filename=STYLES_TEMPLATE_FILENAME, directory=config_directory,
                              page_width=cast(int, parameters['page_width']))

    html_begin = get_html_begin(template_path=Path(pkg_resources.resource_filename('pyreball',
                                                                                   'cfg/html_begin.template')),
                                title=title, script_definitions=script_definitions, css_definitions=css_definitions)
    html_end = get_html_end(template_path=Path(pkg_resources.resource_filename('pyreball', 'cfg/html_end.template')))

    with open(html_path, 'w') as f:
        f.write(html_begin)
    try:
        # Use {sys.executable} instead of just "python" command as it may not work correctly as a PyCharm external tool
        os.system(f"{sys.executable} {filename}")
    finally:
        with open(html_path, 'a') as f:
            f.write(html_end)

    replace_ids(html_path)
    insert_heading_title_and_toc(filename=html_path, include_toc=parameters['toc'] == 'yes')


if __name__ == '__main__':
    main()
