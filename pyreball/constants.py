from pathlib import Path

import pkg_resources

CONFIG_INI_FILENAME = "config.ini"
LINKS_INI_FILENAME = "external_links.ini"
STYLES_TEMPLATE_FILENAME = "css.template"
HTML_TEMPLATE_FILENAME = "html.template"
DEFAULT_PATH_TO_CONFIG = Path(pkg_resources.resource_filename("pyreball", "cfg"))

PILCROW_SIGN = "¶"
NON_BREAKABLE_SPACE = "\u00A0"
