import pytest
import logging
from pathlib import Path

from pyreball.utils.template_utils import get_css, get_html_begin, get_html_end


def test_get_html_begin(tmpdir):
    filename = "styles"
    template_path = Path(tmpdir) / filename
    with open(template_path, 'w') as f:
        f.write('<html>title: {{title}}, script: {{script_definitions}}, css: {{css_definitions}}')
    result = get_html_begin(template_path=template_path, title='t1', script_definitions='s1',
                            css_definitions='c1')
    assert result == '<html>title: t1, script: s1, css: c1'


def test_get_html_end(tmpdir):
    filename = "styles"
    template_path = Path(tmpdir) / filename
    with open(template_path, 'w') as f:
        f.write('</html>')
    result = get_html_end(template_path=template_path)
    assert result == '</html>'


def test_get_css__existing_file(tmpdir):
    filename = "styles"
    directory = Path(tmpdir)
    with open(directory / filename, 'w') as f:
        f.write('body {width: {{page_width}}%;}\n')
    styles = get_css(filename, directory, page_width=30)
    assert styles == 'body {width: 30%;}\n'


def test_get_css__non_existing_file(tmpdir, caplog):
    caplog.set_level(logging.ERROR)
    filename = "styles"
    directory = Path(tmpdir)
    with pytest.raises(SystemExit):
        get_css(filename, directory, page_width=30)
    assert 'There was a problem reading file' in caplog.text
