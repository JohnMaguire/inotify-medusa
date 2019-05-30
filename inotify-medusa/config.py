import logging
import os
import sys

PROCESS_METHODS = (
    "copy",
    "symlink",
    "hardlink",
    "move",
    "reflink",
)

logger = logging.getLogger(__name__)


def getenv_required(name):
    value = os.getenv(name)
    if value is None:
        raise Exception("Expected {} environment variable".format(name))

    return value


def getenv_option(name, options):
    value = getenv_required(name)

    if value not in options:
        raise Exception("Expected {} to be one of: {}; but got: {}".format(
            name, ', '.join(options), value
        ))

    return value


def getenv_bool(name, default):
    value = os.getenv(name)
    if value is None:
        return default

    if value.lower() not in ('0', '1', 'false', 'true'):
        raise Exception("Expected {} to be boolean, but got: {}".format(
            name, value))

    return True if value.lower() in ('1', 'true') else False


def read_config():
    # Look for arguments
    try:
        debug = getenv_bool('DEBUG', False)
        watch_dir = getenv_required('WATCH_DIRECTORY')
        medusa_host = getenv_required('MEDUSA_HOST')
        api_token = getenv_required('MEDUSA_API_TOKEN')
        process_method = getenv_option('MEDUSA_PROCESS_METHOD',
                                       PROCESS_METHODS)
        force_replace = getenv_bool('MEDUSA_FORCE_REPLACE', False)
        delete_files = getenv_bool('MEDUSA_DELETE_FILES', False)
        is_priority = getenv_bool('MEDUSA_IS_PRIORITY', False)
    except Exception:
        logger.exception("Failed to load config")
        sys.exit(1)

    return locals()


CONFIG = read_config()
