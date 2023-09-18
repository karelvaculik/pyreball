import configparser
import logging
import os
from pathlib import Path
from unittest import mock

import pytest

from pyreball.utils.param import (
    _map_env_value,
    _matches_paging_sizes_string,
    carefully_remove_directory_if_exists,
    check_and_fix_parameters,
    check_choice_string_parameter,
    check_integer_within_range,
    check_paging_sizes_string_parameter,
    ChoiceParameter,
    get_external_links_from_config,
    get_file_config,
    get_parameter_value,
    IntegerParameter,
    make_sure_dir_exists,
    merge_parameter_dictionaries,
    merge_values,
    read_file_config,
    StringParameter,
    Substitutor,
)

MODULE_PATH = "pyreball.utils.param"


@pytest.fixture
def simple_parameter_specifications():
    return [
        ChoiceParameter(
            "--align", choices=["left", "center", "right"], default="center", help=""
        ),
        ChoiceParameter("--do-stuff", choices=["yes", "no"], default="yes", help=""),
        ChoiceParameter("--highlight", choices=["yes", "no"], default="no", help=""),
        ChoiceParameter("--organize", choices=["yes", "no"], default="no", help=""),
        IntegerParameter("--page-width", boundaries=(10, 20), default=15, help=""),
        StringParameter(
            "--paging-sizes",
            default="10,25,100,All",
            help="",
            validation_function=check_paging_sizes_string_parameter,
        ),
    ]


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        ("", False),
        ("23", True),
        ("23,452", True),
        ("23,452,100", True),
        ("23,452,100,All", True),
        ("23,all,100", True),
        ("ALL", True),
        ("unknown", False),
        ("23,452 100", False),
        ("23_452,100", False),
        ("Allright", False),
        ("23,", False),
        (",23", False),
        (",", False),
    ],
)
def test__matches_paging_sizes_string(test_input, expected_result):
    assert _matches_paging_sizes_string(test_input) == expected_result


@pytest.mark.parametrize(
    "value,none_allowed,err_msg,expected_result",
    [
        ("10,ALL", True, None, "10,ALL"),
        ("10,ALL", False, None, "10,ALL"),
        (None, True, None, None),
        (None, False, None, "30,40"),
        ("hello", True, "Parameter param1 is set to an unsupported", "hello"),
        ("hello", False, "Parameter param1 is set to an unsupported", "hello"),
    ],
)
def test_check_paging_sizes_string_parameter(
    value, none_allowed, err_msg, expected_result
):
    error_messages = []
    result_value = check_paging_sizes_string_parameter(
        "param1",
        value,
        "30,40",
        none_allowed,
        [],
        error_messages,
    )
    assert result_value == expected_result
    contains_error_msg = any(map(lambda msg: err_msg in msg, error_messages))
    assert contains_error_msg if err_msg else not contains_error_msg


@pytest.mark.parametrize(
    "value,none_allowed,warn_msg,err_msg,expected_result",
    [
        ("one", True, None, None, "one"),
        ("one", False, None, None, "one"),
        (None, True, None, None, None),
        (None, False, "Parameter param1 was not set", None, "three"),
        ("four", True, None, "Parameter param1 is set to an unsupported", "four"),
        ("four", False, None, "Parameter param1 is set to an unsupported", "four"),
    ],
)
def test_check_choice_string_parameter(
    value, none_allowed, warn_msg, err_msg, expected_result
):
    warning_messages = []
    error_messages = []
    result_value = check_choice_string_parameter(
        "param1",
        value,
        ["one", "two"],
        "three",
        none_allowed,
        warning_messages,
        error_messages,
    )
    assert result_value == expected_result
    contains_warning_msg = any(map(lambda msg: warn_msg in msg, warning_messages))
    contains_error_msg = any(map(lambda msg: err_msg in msg, error_messages))
    assert contains_warning_msg if warn_msg else not contains_warning_msg
    assert contains_error_msg if err_msg else not contains_error_msg


@pytest.mark.parametrize(
    "value,low,high,none_allowed,warn_msg,err_msg,expected_result",
    [
        (25, 20, 30, True, None, None, 25),
        (25, 20, 30, False, None, None, 25),
        (None, 20, 30, True, None, None, None),
        (None, 20, 30, False, None, "Could not parse param1", None),
        ("four", 20, 30, True, None, "Could not parse param1", "four"),
        ("four", 20, 30, False, None, "Could not parse param1", "four"),
        (
            10,
            20,
            30,
            True,
            "Parameter param1 is less than 20, setting it to 20.",
            None,
            20,
        ),
        (
            50,
            20,
            30,
            False,
            "Parameter param1 is more than 30, setting it to 30.",
            None,
            30,
        ),
        (25, None, None, False, None, None, 25),
        (
            25,
            None,
            20,
            False,
            "Parameter param1 is more than 20, setting it to 20.",
            None,
            20,
        ),
        (
            25,
            30,
            None,
            False,
            "Parameter param1 is less than 30, setting it to 30.",
            None,
            30,
        ),
    ],
)
def test_check_integer_within_range(
    value, low, high, none_allowed, warn_msg, err_msg, expected_result
):
    warning_messages = []
    error_messages = []
    result_value = check_integer_within_range(
        "param1", value, low, high, none_allowed, warning_messages, error_messages
    )
    assert result_value == expected_result
    contains_warning_msg = any(map(lambda msg: warn_msg in msg, warning_messages))
    contains_error_msg = any(map(lambda msg: err_msg in msg, error_messages))
    assert contains_warning_msg if warn_msg else not contains_warning_msg
    assert contains_error_msg if err_msg else not contains_error_msg


@pytest.mark.parametrize(
    "parameters,none_allowed,warn_msgs,err_msgs,expected_result",
    [
        # everything is fine
        (
            {
                "align": "center",
                "do_stuff": "no",
                "highlight": "yes",
                "organize": "yes",
                "page_width": 10,
                "paging_sizes": "All,100",
            },
            True,
            [],
            [],
            {
                "align": "center",
                "do_stuff": "no",
                "highlight": "yes",
                "organize": "yes",
                "page_width": 10,
                "paging_sizes": "All,100",
            },
        ),
        # None values are used for the missing ones
        (
            {
                "do_stuff": "no",
                "highlight": "yes",
                "page_width": 30,
            },
            True,
            ["Parameter page_width is more than"],
            [],
            {
                "align": None,
                "do_stuff": "no",
                "highlight": "yes",
                "organize": None,
                "page_width": 20,
                "paging_sizes": None,
            },
        ),
        # Default values are used for the missing ones
        (
            {
                "do_stuff": "no",
                "highlight": "yes",
                "page_width": 4,
            },
            False,
            [
                "Parameter align was not set",
                "Parameter organize was not set",
                "Parameter page_width is less than",
                "Parameter paging_sizes was not set",
            ],
            [],
            {
                "align": "center",
                "do_stuff": "no",
                "highlight": "yes",
                "organize": "no",
                "page_width": 10,
                "paging_sizes": "10,25,100,All",
            },
        ),
        # Unsupported values
        (
            {
                "do_stuff": "maybe",
                "highlight": "yes",
                "organize": "no",
                "page_width": "not_a_number",
                "paging_sizes": "All,100",
            },
            False,
            ["Parameter align was not set"],
            [
                "Parameter do_stuff is set to an unsupported",
                "Could not parse page_width parameter as an integer",
            ],
            "result_does_not_matter",
        ),
    ],
)
def test_check_and_fix_parameters(
    parameters,
    none_allowed,
    warn_msgs,
    err_msgs,
    expected_result,
    caplog,
    simple_parameter_specifications,
):
    caplog.set_level(logging.WARNING)
    if len(err_msgs) > 0:
        with pytest.raises(SystemExit):
            check_and_fix_parameters(
                parameters=parameters,
                parameter_specifications=simple_parameter_specifications,
                none_allowed=none_allowed,
            )
        for msg in warn_msgs:
            assert msg in caplog.text
        for msg in err_msgs:
            assert msg in caplog.text
    else:
        result_parameters = check_and_fix_parameters(
            parameters=parameters,
            parameter_specifications=simple_parameter_specifications,
            none_allowed=none_allowed,
        )
        for msg in warn_msgs:
            assert msg in caplog.text
        assert result_parameters == expected_result


def test_read_file_config__existing_file(tmpdir):
    filename = "conf"
    directory = Path(tmpdir)
    with open(directory / filename, "w") as f:
        f.writelines(["[Parameters]\n", "a = b\n"])
    config = read_file_config(filename, directory)
    assert config["Parameters"]["a"] == "b"


def test_read_file_config__non_existing_file(tmpdir, caplog):
    caplog.set_level(logging.ERROR)
    filename = "conf"
    directory = Path(tmpdir)
    with pytest.raises(SystemExit):
        read_file_config(filename, directory)
    assert "Could not find file" in caplog.text


def test_get_file_config__correct_specification(simple_parameter_specifications):
    config = configparser.ConfigParser()
    # 'align' is missing and 'page-size' is incorrect
    config["Parameters"] = {
        "do-stuff": "no",
        "highlight": "yes",
        "organize": "yes",
        "page-width": 22,
    }
    expected_config_parameters = {
        "align": "center",
        "do_stuff": "no",
        "highlight": "yes",
        "organize": "yes",
        "page_width": 20,
        "paging_sizes": "10,25,100,All",
    }
    with mock.patch(f"{MODULE_PATH}.read_file_config", return_value=config):
        config_parameters = get_file_config(
            filename="does_not_matter",
            parameter_specifications=simple_parameter_specifications,
            directory=Path("/does_not_matter"),
        )
        assert config_parameters == expected_config_parameters


def test_get_file_config__incorrect_specification(
    caplog, simple_parameter_specifications
):
    caplog.set_level(logging.ERROR)
    config = configparser.ConfigParser()
    config["unknown"] = {"organize": "yes"}
    with mock.patch(f"{MODULE_PATH}.read_file_config", return_value=config):
        with pytest.raises(SystemExit):
            get_file_config(
                filename="does_not_matter",
                parameter_specifications=simple_parameter_specifications,
                directory=Path("/does_not_matter"),
            )
        assert "Parameters section not found in" in caplog.text


def test_get_external_links_from_config__correct_specification():
    config = configparser.ConfigParser()
    config["Links"] = {
        "altair": "\na\nb",
        "bokeh": "\nc\nd\n",
        "datatables": "\ne\n",
        "highlight_js": "\nf\ng",
        "jquery": "\nh",
        "plotly": "\ni",
    }
    expected_result = {
        "altair": ["a", "b"],
        "bokeh": ["c", "d"],
        "datatables": ["e"],
        "highlight_js": ["f", "g"],
        "jquery": ["h"],
        "plotly": ["i"],
    }
    with mock.patch(f"{MODULE_PATH}.read_file_config", return_value=config):
        result = get_external_links_from_config(
            filename="does_not_matter",
            directory=Path("/does_not_matter"),
        )
        assert result == expected_result


def test_get_external_links_from_config__incorrect_section(
    caplog, simple_parameter_specifications
):
    caplog.set_level(logging.ERROR)
    config = configparser.ConfigParser()
    # Wrong section name
    config["Unsupported"] = {
        "altair": "\na\nb",
        "bokeh": "\nc\nd\n",
        "datatables": "\ne\n",
        "highlight_js": "\nf\ng",
        "jquery": "\nh",
        "plotly": "\ni",
    }
    with mock.patch(f"{MODULE_PATH}.read_file_config", return_value=config):
        with pytest.raises(SystemExit):
            get_external_links_from_config(
                filename="does_not_matter",
                directory=Path("/does_not_matter"),
            )
        assert "section not found in" in caplog.text


def test_get_external_links_from_config__incorrect_keys(
    caplog, simple_parameter_specifications
):
    caplog.set_level(logging.ERROR)
    config = configparser.ConfigParser()
    # contains only some items
    config["Links"] = {
        "altair": "\na\nb",
        "bokeh": "\nc\nd\n",
    }
    with mock.patch(f"{MODULE_PATH}.read_file_config", return_value=config):
        with pytest.raises(SystemExit):
            get_external_links_from_config(
                filename="does_not_matter",
                directory=Path("/does_not_matter"),
            )
        assert "Configuration with items must contain links" in caplog.text


@pytest.mark.parametrize(
    "test_input_1,test_input_2,expected_result",
    [
        (None, None, None),
        ("a", None, "a"),
        (None, "b", "b"),
        ("a", "b", "a"),
    ],
)
def test_merge_values(test_input_1, test_input_2, expected_result):
    assert merge_values(test_input_1, test_input_2) == expected_result


@pytest.mark.parametrize(
    "primary_parameters,secondary_parameters,expected_result",
    [
        (
            {
                "align": None,
                "do_stuff": "no",
                "highlight": "yes",
                "organize": None,
                "page_width": 10,
                "paging_sizes": None,
            },
            {
                "align": "center",
                "do_stuff": None,
                "highlight": "no",
                "organize": None,
                "page_width": 20,
                "paging_sizes": "10,25,100,All",
            },
            {
                "align": "center",
                "do_stuff": "no",
                "highlight": "yes",
                "organize": None,
                "page_width": 10,
                "paging_sizes": "10,25,100,All",
            },
        ),
    ],
)
def test_merge_parameter_dictionaries(
    primary_parameters,
    secondary_parameters,
    expected_result,
    simple_parameter_specifications,
):
    assert (
        merge_parameter_dictionaries(
            primary_parameters,
            secondary_parameters,
            parameter_specifications=simple_parameter_specifications,
        )
        == expected_result
    )


@pytest.mark.parametrize(
    "test_input,expected_result",
    [
        ("None", None),
        ("yes", True),
        ("no", False),
        ("anything", "anything"),
        (42, 42),
    ],
)
def test_map_env_value(test_input, expected_result):
    assert _map_env_value(test_input) == expected_result


def test_get_parameter_value():
    pars = '{"a": 2, "html_dir_path": "/tmp/dir"}'
    with mock.patch.dict(os.environ, {"_TMP_PYREBALL_GENERATOR_PARAMETERS": pars}):
        assert get_parameter_value("a") == 2
        assert get_parameter_value("html_dir_path") == "/tmp/dir"
        assert get_parameter_value("html_dir_name") == "dir"
        assert get_parameter_value("html_file_path") == "/tmp/dir.html"


def test_make_sure_dir_exists(tmpdir):
    directory = str(tmpdir / "mydir")
    assert not os.path.exists(directory)
    make_sure_dir_exists(directory)
    assert os.path.exists(directory)
    # when executed again, nothing breaks
    make_sure_dir_exists(directory)
    assert os.path.exists(directory)


@mock.patch(f"{MODULE_PATH}.shutil")
def test_carefully_remove_directory_if_exists__doesnt_exist(shutil_mock, tmpdir):
    directory = Path(tmpdir / "whatever")
    assert not directory.exists()
    carefully_remove_directory_if_exists(directory)
    shutil_mock.rmtree.assert_not_called()


@mock.patch(f"{MODULE_PATH}.shutil")
def test_carefully_remove_directory_if_exists__error_when_deleting(shutil_mock, tmpdir):
    shutil_mock.rmtree.side_effect = OSError
    directory = Path(tmpdir / "whatever")
    directory.mkdir(parents=True)
    assert directory.exists()
    with pytest.raises(OSError):
        carefully_remove_directory_if_exists(directory)


def test_carefully_remove_directory_if_exists__empty_dir(tmpdir):
    directory = Path(tmpdir / "whatever")
    directory.mkdir(parents=True)
    assert directory.exists()
    carefully_remove_directory_if_exists(directory)
    assert not directory.exists()


def test_carefully_remove_directory_if_exists__with_image_files(tmpdir):
    directory = Path(tmpdir / "whatever")
    directory.mkdir(parents=True)

    # Creates empty files
    filenames = ["img.png", "img.jpg", "img.svg"]
    for filename in filenames:
        with open(directory / filename, "w") as fp:
            pass

    assert directory.exists()
    assert len(list(directory.glob("*"))) == len(filenames)
    carefully_remove_directory_if_exists(directory)
    assert not directory.exists()


def test_carefully_remove_directory_if_exists__with_non_image_files(tmpdir):
    directory = Path(tmpdir / "whatever")
    directory.mkdir(parents=True)

    # Creates empty files
    filenames = ["img.png", "img.jpg", "img.svg", "important_script.py"]
    for filename in filenames:
        with open(directory / filename, "w") as fp:
            pass

    assert directory.exists()
    assert len(list(directory.glob("*"))) == len(filenames)
    with pytest.raises(ValueError) as excinfo:
        carefully_remove_directory_if_exists(directory)
    assert "Cannot delete the original html directory" in str(excinfo.value)
    assert directory.exists()


@pytest.mark.parametrize(
    "text,repls,expected_result",
    [
        ("", [("apple", "pear"), ("dark", "light"), ("red", "green")], ""),
        (
            "This apple is dark red",
            [("apple", "pear"), ("dark", "light"), ("red", "green")],
            "This pear is light green",
        ),
        (
            "This apple is dark red",
            [
                ("apple", "pear"),
                ("dark", "light"),
                ("red", "green"),
                ("pear", "orange"),
            ],
            "This orange is light green",
        ),
        (
            "my aa and also aab ccdd cc table-5035059472 and also table-5035059472-6",
            [(r"aab?", "XX"), (r"cc(dd)?", "YY"), ("table-5035059472(-6)?", "table-6")],
            "my XX and also XX YY YY table-6 and also table-6",
        ),
    ],
)
def test_substitutor(text, repls, expected_result):
    substitutor = Substitutor(repls)
    result = substitutor.sub(text)
    assert result == expected_result
