import argparse
import os
import shutil
from pathlib import Path

from pyreball.constants import (
    PATH_TO_CONFIG_LOCATION,
    DEFAULT_PATH_TO_CONFIG,
    CONFIG_INI_FILENAME,
    STYLES_TEMPLATE_FILENAME,
)
from pyreball.utils.logger import get_logger

logger = get_logger()


def copy_config_files(output_directory: Path) -> None:
    if output_directory.exists():
        logger.warning(f"Directory {output_directory} already exists, config will be over-written.")
    output_directory.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DEFAULT_PATH_TO_CONFIG / CONFIG_INI_FILENAME, output_directory)
    shutil.copy2(DEFAULT_PATH_TO_CONFIG / STYLES_TEMPLATE_FILENAME, output_directory)
    # mark down where we created the config files
    Path(PATH_TO_CONFIG_LOCATION).write_text(str(output_directory))


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate Pyreball Config Files.')
    parser.add_argument('--output-dir', help='Output directory. By default, ~/.pyreball.')
    args = parser.parse_args()
    if args.output_dir:
        config_directory = Path(args.output_dir).absolute()
    else:
        config_directory = Path(os.environ["HOME"]) / '.pyreball'
    copy_config_files(output_directory=config_directory)


if __name__ == '__main__':
    main()
