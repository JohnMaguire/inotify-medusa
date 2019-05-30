import logging

from inotify_simple import INotify, flags

from config import CONFIG
from medusa import process

logging.basicConfig(level=logging.DEBUG if CONFIG['debug'] else logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting inotify-medusa...")

    watch_dir = CONFIG['watch_dir']

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
        try:
            logger.debug(process(host=CONFIG['medusa_host'],
                                 api_token=CONFIG['api_token'],
                                 path=CONFIG['watch_dir'],
                                 process_method=CONFIG['process_method'],
                                 force_replace=CONFIG['force_replace'],
                                 is_priority=CONFIG['is_priority'],
                                 delete_files=CONFIG['delete_files']))
        except Exception:
            logger.exception("Failed to contact Medusa")
