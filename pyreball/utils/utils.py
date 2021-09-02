import argparse
import json
import os
import re
import shutil
import sys
import configparser
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, Union, List, Any, cast, Tuple

from pyreball.utils.logger import get_logger

ParametersType = Dict[str, Optional[Union[str, int]]]

logger = get_logger()


class Parameter(ABC):

    @property
    @abstractmethod
    def param_key(self):
        ...

    @property
    @abstractmethod
    def config_param_key(self):
        ...

    @abstractmethod
    def add_argument_to_parser(self, parser: argparse.ArgumentParser) -> None:
        ...

    @abstractmethod
    def check_and_fix_value(self, value: Any, none_allowed: bool, warning_messages: List[str],
                            error_messages: List[str]) -> Any:
        ...


class ChoiceParameter(Parameter):

    def __init__(self, option_string: str, choices: List[str], default: str, help: str):
        self.option_string = option_string
        self._config_param_key = option_string.replace('--', '')
        self._param_key = self._config_param_key.replace('-', '_')
        self.choices = choices
        self.default = default
        self.help = help

    @property
    def param_key(self):
        return self._param_key

    @property
    def config_param_key(self):
        return self._config_param_key

    def add_argument_to_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(self.option_string, choices=self.choices, help=self.help)

    def check_and_fix_value(self, value: Any, none_allowed: bool, warning_messages: List[str],
                            error_messages: List[str]) -> Any:
        return check_choice_string_parameter(key=self.param_key, value=cast(Optional[str], value),
                                             value_choices=self.choices,
                                             default_value=self.default, none_allowed=none_allowed,
                                             warning_messages=warning_messages,
                                             error_messages=error_messages)


class IntegerParameter(Parameter):

    def __init__(self, option_string: str, boundaries: Tuple[Optional[int], Optional[int]], default: int, help: str):
        self.option_string = option_string
        self._config_param_key = option_string.replace('--', '')
        self._param_key = self._config_param_key.replace('-', '_')
        self.boundaries = boundaries
        self.default = default
        self.help = help

    @property
    def param_key(self):
        return self._param_key

    @property
    def config_param_key(self):
        return self._config_param_key

    def add_argument_to_parser(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(self.option_string, type=int, help=self.help)

    def check_and_fix_value(self, value: Any, none_allowed: bool, warning_messages: List[str],
                            error_messages: List[str]) -> Any:
        return check_integer_within_range(key=self.param_key, value=value, low=self.boundaries[0],
                                          high=self.boundaries[1], none_allowed=none_allowed,
                                          warning_messages=warning_messages, error_messages=error_messages)


def check_choice_string_parameter(key: str, value: Optional[str], value_choices: List[str], default_value: str,
                                  none_allowed: bool, warning_messages: List[str],
                                  error_messages: List[str]) -> Optional[str]:
    if value is None and not none_allowed:
        warning_messages.append(f'Parameter {key} was not set, setting its value to "{default_value}".')
        return default_value
    elif value is not None and value not in value_choices:
        error_messages.append(f'Parameter {key} is set to an unsupported value {value}, '
                              f'only these values are allowed: {", ".join(value_choices)}.')
    return value


def check_integer_within_range(key: str, value: Any, low: Optional[int], high: Optional[int],
                               none_allowed: bool, warning_messages: List[str],
                               error_messages: List[str]) -> Any:
    if value is None and none_allowed:
        return value
    try:
        value_int = int(value)
    except (ValueError, TypeError):
        error_messages.append(f'Could not parse {key} parameter as an integer.')
        return value
    else:
        if low is not None and value_int < low:
            value_int = low
            warning_messages.append(f'Parameter {key} is less than {low}, setting it to {low}.')
        if high is not None and value_int > high:
            value_int = high
            warning_messages.append(f'Parameter {key} is more than {high}, setting it to {high}.')
    return value_int


def check_and_fix_parameters(parameters: ParametersType,
                             parameter_specifications: List[Parameter],
                             none_allowed: bool) -> ParametersType:
    # collect the config values
    new_parameters: ParametersType = {}
    warning_messages: List[str] = []
    error_messages: List[str] = []

    for param_spec in parameter_specifications:
        new_parameters[param_spec.param_key] = param_spec.check_and_fix_value(parameters.get(param_spec.param_key),
                                                                              none_allowed=none_allowed,
                                                                              warning_messages=warning_messages,
                                                                              error_messages=error_messages)

    for msg in warning_messages:
        logger.warning(msg)
    for msg in error_messages:
        logger.error(msg)

    if len(error_messages) > 0:
        sys.exit(1)

    return new_parameters


def read_file_config(filename: str, directory: Path) -> configparser.ConfigParser:
    config_path = directory / filename
    if config_path.is_file():
        config = configparser.ConfigParser()
        config.read(config_path)
        return config
    else:
        logger.error(f'Could not find file {filename} in {directory}. Try re-generating configs by '
                     f'pyreball-generate-config command or re-installing pyreball.')
        sys.exit(1)


def get_file_config(filename: str, directory: Path, parameter_specifications: List[Parameter]) -> ParametersType:
    config = read_file_config(filename, directory)
    section_name = 'Parameters'
    if section_name not in config:
        logger.error(f'{section_name} section not found in {directory / filename} '
                     f'configuration file. Fix the file or try re-installing pyreball.')
        sys.exit(1)

    # collect the config values and use underscore instead of dashes
    config_params: ParametersType = {param_spec.param_key: config[section_name].get(param_spec.config_param_key)
                                     for param_spec in parameter_specifications}
    return check_and_fix_parameters(parameters=config_params, parameter_specifications=parameter_specifications,
                                    none_allowed=False)


def merge_values(primary_value: Any, secondary_value: Any) -> Any:
    return primary_value if primary_value is not None else secondary_value


def merge_parameter_dictionaries(primary_parameters: ParametersType,
                                 secondary_parameters: ParametersType,
                                 parameter_specifications: List[Parameter]) -> ParametersType:
    return {
        param_spec.param_key: merge_values(primary_value=primary_parameters.get(param_spec.param_key),
                                           secondary_value=secondary_parameters.get(param_spec.param_key))
        for param_spec in parameter_specifications
    }


def _map_env_value(value):
    if value == 'None':
        return None
    elif value == 'yes':
        return True
    elif value == 'no':
        return False
    else:
        return value


def get_parameter_value(key: str) -> Any:
    if not hasattr(get_parameter_value, 'data'):
        get_parameter_value.data = {k: _map_env_value(v) for k, v
                                    in json.loads(os.environ.get('_TMP_PYREBALL_GENERATOR_PARAMETERS', '{}')).items()}
        if 'html_dir_path' in get_parameter_value.data:
            get_parameter_value.data['html_dir_name'] = os.path.basename(get_parameter_value.data.get('html_dir_path'))
            get_parameter_value.data['html_file_path'] = get_parameter_value.data.get('html_dir_path') + '.html'
    return get_parameter_value.data.get(key)


def make_sure_dir_exists(directory: Optional[str]) -> None:
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def carefully_remove_directory_if_exists(directory: Path) -> None:
    """Remove directory if it exists and contains only files of given type.

    :param directory: path to a directory.
    """
    if directory.exists():
        # check that the folder contains only png and jpg files. Otherwise raise an error.
        for filename in directory.iterdir():
            if not re.search(r'.(png|jpg|svg)$', filename.name):
                raise ValueError(f"Cannot delete the original html directory {directory}. "
                                 f"It contains file {filename} and only png, jpg and svg files are assumed.")
        try:
            shutil.rmtree(directory)
        except OSError:
            # print also the directory so that we have enough info
            logger.error(f"Error raised when deleting directory: {directory}")
            raise


class Substitutor:
    """Multiple-string substitution class.

    It replaces strings for a different strings in a sequential order.
    It is possible to use regex as well.
    """
    def __init__(self, replacements: List[Tuple[str, str]]) -> None:
        self.patterns = [re.compile(r[0]) for r in replacements]
        self.replacements = [r[1] for r in replacements]

    def sub(self, text: str) -> str:
        for i in range(len(self.patterns)):
            text = self.patterns[i].sub(self.replacements[i], text)
        return text
