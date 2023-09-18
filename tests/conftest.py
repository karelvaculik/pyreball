import pytest

from pyreball.utils.param import _parameter_cache, get_parameter_value


@pytest.fixture(autouse=True)
def pre_test_cleanup():
    # call this snippet before each unit test.
    # get_parameter_value() is meant to be used only in a single session,
    # but test functions should represent independent session
    global _parameter_cache
    _parameter_cache.clear()
    yield
