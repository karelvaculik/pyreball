import typing
from pathlib import Path
from typing import Dict, List, Optional, Union

ClParameter = Optional[Union[str, List[str]]]
AttrsParameter = Optional[Dict[str, Optional[str]]]


@typing.no_type_check
def get_default_path_to_config() -> Path:
    """Get Path to the default config."""

    try:
        # Python >=3.9
        from importlib.resources import files  # type: ignore[attr-defined]

        return Path(files("pyreball") / "cfg")
    except ImportError:
        # Python 3.8
        import pkg_resources

        return Path(pkg_resources.resource_filename("pyreball", "cfg"))
