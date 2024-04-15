import re
import sys
from pathlib import Path
from typing import Tuple

from pyreball.utils.logger import get_logger

logger = get_logger()


def get_html(template_path: Path, title: str, css_definitions: str) -> Tuple[str, str]:
    with open(template_path) as f:
        html_text = f.read()
        html_start, html_end = html_text.split("<!--PYREBALL_REPORT_CONTENTS-->")
        html_start = re.sub("<!--PYREBALL_PAGE_TITLE-->", title, html_start)
        html_start = re.sub(
            r"<!--PYREBALL_CSS_DEFINITIONS-->", css_definitions, html_start
        )
        return html_start, html_end


def get_css(filename: str, directory: Path, page_width: int = 60) -> str:
    try:
        with open(directory / filename) as f:
            css_string = f.read()
    except OSError:
        logger.error(
            f"There was a problem reading file {filename} in {directory}. "
            f"Try re-installing pyreball."
        )
        sys.exit(1)
    css_string = re.sub(r"{{page_width}}", str(int(page_width)), css_string)
    return css_string
