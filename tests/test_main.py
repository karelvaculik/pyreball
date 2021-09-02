from pathlib import Path

import pytest
from pyreball.__main__ import _parse_heading_info, replace_ids, insert_heading_title_and_toc, _get_node_text


@pytest.mark.parametrize("report_before,report_after", [
    (
            [
                '<html>',
                '</html>',
            ],
            [
                '<html>',
                '</html>',
            ]
    ),
    (
            [
                '<html>',
                'Reference to table <a href="#ref-id99">id99</a>',
                'Reference to image <a href="#ref-id17">id17</a>',
                '<a name="img-id17-5">Image caption</a><a name="table-id99-1">Table caption</a>',
                'Reference to table <a href="#ref-id123">id123</a> and image <a href="#ref-id42">id42</a>',
                '<a name="table-id123-2">Another table caption</a>',
                '<a name="img-id42-2">Another image caption</a>',
                'Reference again to table <a href="#ref-id123">id123</a> and image <a href="#ref-id42">id42</a>',
                '</html>',
            ],
            [
                '<html>',
                'Reference to table <a href="#table-1">1</a>',
                'Reference to image <a href="#img-5">5</a>',
                '<a name="img-5">Image caption</a><a name="table-1">Table caption</a>',
                'Reference to table <a href="#table-2">2</a> and image <a href="#img-2">2</a>',
                '<a name="table-2">Another table caption</a>',
                '<a name="img-2">Another image caption</a>',
                'Reference again to table <a href="#table-2">2</a> and image <a href="#img-2">2</a>',
                '</html>',
            ]
    )
])
def test_replace_ids(report_before, report_after, tmpdir):
    report_dir = Path(tmpdir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.py"

    with open(report_path, "w") as f:
        f.write('\n'.join(report_before))

    replace_ids(report_path)

    with open(report_path) as f:
        result = f.read().split('\n')

    assert result == report_after


@pytest.mark.parametrize("test_input,expected_result", [
    ('<h2 id="result_of_addition_2">Result of addition<a class="anchor-link" href="#result_of_addition_2">¶</a></h2>',
     (2, 'result_of_addition_2', 'Result of addition')),
    ('<h3 id="some_id">Whatever text - is necessary - 999'
     '<a class="anchor-link" href="#result_of_addition_2">¶</a></h3>',
     (3, 'some_id', 'Whatever text - is necessary - 999')),
    ('<h3 id="some_id">Whatever text - is necessary - 999'
     '<a class="anchor-link" href="#result_of_addition_2">¶</a></h3>',
     (3, 'some_id', 'Whatever text - is necessary - 999')),
    ('<h3 id="some_id">Whatever text - also <code>code</code> and <b><em>bold emphasis</em></b> - 999'
     '<a class="anchor-link" href="#result_of_addition_2">¶</a></h3>',
     (3, 'some_id', 'Whatever text - also code and bold emphasis - 999')),
    ('<div>paragraph</div>',
     None),
])
def test_parse_heading_info(test_input, expected_result):
    assert _parse_heading_info(test_input) == expected_result


@pytest.mark.parametrize("title_set", [
    True,
    False,
])
@pytest.mark.parametrize("include_toc", [
    True,
    False
])
def test_insert_heading_title_and_toc__with_headings(include_toc, title_set, tmpdir):
    if title_set:
        title = '<title class="custom">Custom Title</title>'
        expected_toc_heading = 'Custom Title'
    else:
        title = '<title>Default Title</title>'
        expected_toc_heading = 'Table of Contents'

    report_before = [
        '<html>',
        '<head>',
        title,
        '<head/>',
        '<body>',
        '<div class="main_container">',
        '<h1 id="1_heading_h1_1">1  heading h1<a class="anchor-link" href="#1_heading_h1_1">¶</a></h1>',
        '<h2 id="1_1_heading_h2_2">1.1  heading h2<a class="anchor-link" href="#1_1_heading_h2_2">¶</a></h2>',
        '<h2 id="1_2_heading_h2_3">1.2  heading h2<a class="anchor-link" href="#1_2_heading_h2_3">¶</a></h2>',
        '<h3 id="1_2_1_heading_h3_4">1.2.1  heading h3<a class="anchor-link" href="#1_2_1_heading_h3_4">¶</a></h3>',
        '<h3 id="1_2_2_heading_h3_5">1.2.2  heading h3<a class="anchor-link" href="#1_2_2_heading_h3_5">¶</a></h3>',
        '<h1 id="2_heading_h1_6">2  heading h1<a class="anchor-link" href="#2_heading_h1_6">¶</a></h1>',
        '<h1 id="3_heading_h1_7">3  heading h1<a class="anchor-link" href="#3_heading_h1_7">¶</a></h1>',
        '<h2 id="3_1_heading_h2_8">3.1  heading h2<a class="anchor-link" href="#3_1_heading_h2_8">¶</a></h2>',
        '</div>',
        '</body>',
        '</html>',
    ]

    report_dir = Path(tmpdir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.py"

    with open(report_path, "w") as f:
        f.write('\n'.join(report_before))

    insert_heading_title_and_toc(report_path, include_toc=include_toc)

    with open(report_path) as f:
        result = f.read().split('\n')

    expected_title_and_toc = []
    if title_set and not include_toc:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">{expected_toc_heading}<a class="anchor-link" href="#toc_generated_0">¶</a></h1>'
        ]
    elif include_toc:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">{expected_toc_heading}<a class="anchor-link" href="#toc_generated_0">¶</a></h1>',
            '<a href="#1_heading_h1_1">1  heading h1</a><br/>',
            '<ul style="list-style-type:none; margin:0px">',
            '<li><a href="#1_1_heading_h2_2">1.1  heading h2</a></li>',
            '<li><a href="#1_2_heading_h2_3">1.2  heading h2</a></li>',
            '<ul style="list-style-type:none; margin:0px">',
            '<li><a href="#1_2_1_heading_h3_4">1.2.1  heading h3</a></li>',
            '<li><a href="#1_2_2_heading_h3_5">1.2.2  heading h3</a></li>',
            '</ul>',
            '</ul>',
            '<a href="#2_heading_h1_6">2  heading h1</a><br/>',
            '<a href="#3_heading_h1_7">3  heading h1</a><br/>',
            '<ul style="list-style-type:none; margin:0px">',
            '<li><a href="#3_1_heading_h2_8">3.1  heading h2</a></li>',
            '</ul>',
        ]

    report_after = [
                       '<html>',
                       '<head>',
                       title,
                       '<head/>',
                       '<body>',
                       '<div class="main_container">'
                   ] + expected_title_and_toc + [
                       '<h1 id="1_heading_h1_1">1  heading h1<a class="anchor-link" href="#1_heading_h1_1">¶</a></h1>',
                       '<h2 id="1_1_heading_h2_2">1.1  heading h2<a class="anchor-link" href="#1_1_heading_h2_2">¶</a></h2>',
                       '<h2 id="1_2_heading_h2_3">1.2  heading h2<a class="anchor-link" href="#1_2_heading_h2_3">¶</a></h2>',
                       '<h3 id="1_2_1_heading_h3_4">1.2.1  heading h3<a class="anchor-link" href="#1_2_1_heading_h3_4">¶</a></h3>',
                       '<h3 id="1_2_2_heading_h3_5">1.2.2  heading h3<a class="anchor-link" href="#1_2_2_heading_h3_5">¶</a></h3>',
                       '<h1 id="2_heading_h1_6">2  heading h1<a class="anchor-link" href="#2_heading_h1_6">¶</a></h1>',
                       '<h1 id="3_heading_h1_7">3  heading h1<a class="anchor-link" href="#3_heading_h1_7">¶</a></h1>',
                       '<h2 id="3_1_heading_h2_8">3.1  heading h2<a class="anchor-link" href="#3_1_heading_h2_8">¶</a></h2>',
                       '</div>',
                       '</body>',
                       '</html>',
                   ]

    assert result == report_after


@pytest.mark.parametrize("title_set", [
    True,
    False,
])
@pytest.mark.parametrize("include_toc", [
    True,
    False
])
def test_insert_heading_title_and_toc__without_headings(include_toc, title_set, tmpdir):
    if title_set:
        title = '<title class="custom">Custom Title</title>'
    else:
        title = '<title>Default Title</title>'

    report_before = [
        '<html>',
        '<head>',
        title,
        '<head/>',
        '<body>',
        '<div class="main_container">',
        '</div>',
        '</body>',
        '</html>',
    ]

    report_dir = Path(tmpdir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report.py"

    with open(report_path, "w") as f:
        f.write('\n'.join(report_before))

    insert_heading_title_and_toc(report_path, include_toc=include_toc)

    with open(report_path) as f:
        result = f.read().split('\n')

    expected_title_and_toc = []
    if title_set:
        expected_title_and_toc = [
            f'<h1 id="toc_generated_0">Custom Title<a class="anchor-link" href="#toc_generated_0">¶</a></h1>'
        ]

    report_after = [
                       '<html>',
                       '<head>',
                       title,
                       '<head/>',
                       '<body>',
                       '<div class="main_container">'
                   ] + expected_title_and_toc + [
                       '</div>',
                       '</body>',
                       '</html>',
                   ]

    assert result == report_after
