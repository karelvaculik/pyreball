import re
import sys
from pathlib import Path

from pyreball.utils.logger import get_logger

logger = get_logger()


def get_html_begin(template_path: Path, title: str, script_definitions: str, css_definitions: str) -> str:
    with open(template_path, 'r') as f:
        html_start = f.read()
        html_start = re.sub(r'{{title}}', title, html_start)
        html_start = re.sub(r'{{script_definitions}}', script_definitions, html_start)
        html_start = re.sub(r'{{css_definitions}}', css_definitions, html_start)
        return html_start


def get_html_end(template_path: Path) -> str:
    with open(template_path, 'r') as f:
        html_end = f.read()
        return html_end


def get_css(filename: str, directory: Path, page_width: int = 60) -> str:
    try:
        with open(directory / filename) as f:
            css_string = f.read()
    except OSError:
        logger.error(f'There was a problem reading file {filename} in {directory}. Try re-installing pyreball.')
        sys.exit(1)
    css_string = re.sub(r'{{page_width}}', str(int(page_width)), css_string)
    return css_string
