from pathlib import Path

import pkg_resources

CONFIG_INI_FILENAME = "config.ini"
STYLES_TEMPLATE_FILENAME = "styles.template"
HTML_BEGIN_TEMPLATE_FILENAME = "html_begin.template"
HTML_END_TEMPLATE_FILENAME = "html_end.template"
DEFAULT_PATH_TO_CONFIG = Path(pkg_resources.resource_filename("pyreball", "cfg"))
