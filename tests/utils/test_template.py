import logging
from pathlib import Path

import pytest

from pyreball.utils.template import get_css, get_html


def test_get_html(tmpdir):
    filename = "styles"
    template_path = Path(tmpdir) / filename
    with open(template_path, "w") as f:
        f.write(
            "<html>title: <!--PYREBALL_PAGE_TITLE-->, "
            "css: <!--PYREBALL_CSS_DEFINITIONS-->"
            "<!--PYREBALL_REPORT_CONTENTS-->"
            "</html>"
        )
    result_begin, result_end = get_html(
        template_path=template_path,
        title="t1",
        css_definitions="c1",
    )
    assert result_begin == "<html>title: t1, css: c1"
    assert result_end == "</html>"


def test_get_css__existing_file(tmpdir):
    filename = "styles"
    directory = Path(tmpdir)
    with open(directory / filename, "w") as f:
        f.write("body {width: {{page_width}}%;}\n")
    styles = get_css(filename, directory, page_width=30)
    assert styles == "body {width: 30%;}\n"


def test_get_css__non_existing_file(tmpdir, caplog):
    caplog.set_level(logging.ERROR)
    filename = "styles"
    directory = Path(tmpdir)
    with pytest.raises(SystemExit):
        get_css(filename, directory, page_width=30)
    assert "There was a problem reading file" in caplog.text
