import requests

API_URL = "/api/v1/{api_token}/"


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
