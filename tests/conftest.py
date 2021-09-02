import pytest

from pyreball.utils.utils import get_parameter_value


@pytest.fixture(autouse=True)
def pre_test_cleanup():
    # call this snippet before each unit test:
    if hasattr(get_parameter_value, 'data'):
        # get_parameter_value is meant to be used only in a single session,
        # but test functions should represent independent session
        delattr(get_parameter_value, 'data')
    yield

