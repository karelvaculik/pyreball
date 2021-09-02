from pathlib import Path

import pkg_resources

CONFIG_INI_FILENAME = 'config.ini'
STYLES_TEMPLATE_FILENAME = 'styles.template'
DEFAULT_PATH_TO_CONFIG = Path(pkg_resources.resource_filename('pyreball', 'cfg'))
PATH_TO_CONFIG_LOCATION = Path(pkg_resources.resource_filename('pyreball', 'config_location'))
