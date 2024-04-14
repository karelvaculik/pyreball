import argparse
import shutil
from pathlib import Path

from pyreball._common import get_default_path_to_config
from pyreball.constants import (
    CONFIG_INI_FILENAME,
    HTML_TEMPLATE_FILENAME,
    LINKS_INI_FILENAME,
    STYLES_TEMPLATE_FILENAME,
)
from pyreball.utils.logger import get_logger

logger = get_logger()


def copy_config_files(output_directory: Path) -> None:
    if output_directory.exists():
        logger.warning(
            f"Directory {output_directory} already exists, config will be over-written."
        )
    output_directory.mkdir(parents=True, exist_ok=True)
    default_path_to_config = get_default_path_to_config()
    shutil.copy2(default_path_to_config / CONFIG_INI_FILENAME, output_directory)
    shutil.copy2(default_path_to_config / LINKS_INI_FILENAME, output_directory)
    shutil.copy2(default_path_to_config / STYLES_TEMPLATE_FILENAME, output_directory)
    shutil.copy2(default_path_to_config / HTML_TEMPLATE_FILENAME, output_directory)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Pyreball Config Files.")
    parser.add_argument(
        "--output-dir", help="Output directory. By default, ~/.pyreball."
    )
    args = parser.parse_args()
    if args.output_dir:
        config_directory = Path(args.output_dir).absolute()
    else:
        config_directory = Path.home() / ".pyreball"
    copy_config_files(output_directory=config_directory)
    logger.info(f"Config directory {config_directory} generated.")


if __name__ == "__main__":
    main()
