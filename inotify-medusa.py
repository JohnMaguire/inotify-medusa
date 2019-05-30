import logging
import os

import requests
from inotify_simple import INotify, flags

API_URL = "/api/v1/{api_token}/"

PROCESS_METHODS = (
    "copy",
    "symlink",
    "hardlink",
    "move",
    "reflink",
)

logging.basicConfig(level=logging.DEBUG)
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


def process(host,
            api_token,
            path,
            process_method,
            force_replace=False,
            is_priority=False,
            delete_files=False,
            ):
    """Send a command to Medusa to post-process a directory.

    Keyword arguments:
      host -- Hostname to contact Medusa on (e.g. http://medusa)
      api_token -- API token for Medusa API
      path -- The directory to run post-processing on.
      process_method -- How should files be post-processed (must be one of:
                          copy, symlink, hardlink, move, reflink)
      force_replace -- Force post-processed files to be processed again.
      is_priority -- Replace files even if they already exist higher quality.
      delete_files -- Delete files and folders like auto processing.
    """
    params = {
        "cmd": "postprocess",
        "type": "manual",
        "path": path,
        "force_replace": int(force_replace),
        "process_method": process_method,
        "is_priority": int(is_priority),
        "delete_files": int(delete_files),
        "failed": 0,
        "return_data": 1,
    }

    response = requests.get(host + API_URL.format(api_token=api_token),
                            params=params)

    return response.json()


if __name__ == "__main__":
    logger.info("Starting inotify-medusa...")

    # Look for arguments
    watch_dir = getenv_required('WATCH_DIRECTORY')
    medusa_host = getenv_required('MEDUSA_HOST')
    api_token = getenv_required('MEDUSA_API_TOKEN')
    process_method = getenv_option('MEDUSA_PROCESS_METHOD', PROCESS_METHODS)
    force_replace = getenv_bool('MEDUSA_FORCE_REPLACE', False)
    delete_files = getenv_bool('MEDUSA_DELETE_FILES', False)
    is_priority = getenv_bool('MEDUSA_IS_PRIORITY', False)

    # Setup inotify
    logger.info("Starting watch for directory %s", watch_dir)

    inotify = INotify()
    watch_flags = flags.CREATE | flags.MODIFY

    wd = inotify.add_watch(watch_dir, watch_flags)

    logger.info("Watching directory %s", watch_dir)

    # Loop forever for inotify events
    while True:
        # Block, and wait 1 second before unblocking to allow multiple files to
        # queue up at the same time.
        _ = inotify.read(read_delay=1000)

        logger.info("Watch directory updated, running post-processing")

        # Since we got events, run post-processing
        logger.debug((process(medusa_host,
                              api_token,
                              watch_dir,
                              process_method,
                              force_replace,
                              is_priority,
                              delete_files)))
