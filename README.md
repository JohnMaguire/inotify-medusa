# inotify-medusa
An extremely simple script to setup a Linux inotify watch on a directory, and trigger Medusa post-processing on said directory when changes are detected.

Specifically, the script will look for either of the following events:

- IN_CREATE
- IN_MODIFY

After detecting an event, there is a wait for up to 1 second for any other closely-related events before kicking off post-processing.

## Future Improvements

- Instead of sending the entire directory to post-processing, send only a sub-tree containing the new files
- Add an optional longer delay before triggering post-processing to avoid post-processing files that may not be fully copied yet

## Notes

I've only tested this using the "hardlink" method. Please feel free to open an issue if you have trouble with this script and I'll try to help.

## Installation

This assumes you already have Docker setup. Ideally, put this container in the same network as your Medusa docker container if you have one.

Create a `docker-compose.yml` file with the following contents, or add to your existing `docker-compose.yml`:

```
version: '3'

services:
  inotify-medusa:
    container_name: inotify-medusa
    image: jmaguire/inotify-medusa
    restart: unless-stopped
    volumes:
      - /path/to/medusa/mount:/path/to/medusa/mount
    environment:
      - WATCH_DIRECTORY=/path/to/directory/inside/container
      - MEDUSA_HOST=http://medusa:8081
      - MEDUSA_API_TOKEN=API_TOKEN_HERE
      - MEDUSA_PROCESS_METHOD=hardlink
```

Then modify the volume to either match the volume line for Medusa if running it in a container, or use the same mount path as your host if running it on the host.

Next, configure the environment variables.

- `WATCH_DIRECTORY` - The watch directory is both what will be watched for changes, and the directory that will be sent to Medusa for post-processing.
- `MEDUSA_HOST` - A hostname and port combination that is accessible from the `inotify-medusa` container. Be sure to include the scheme (`http://` or `https://`)
- `MEDUSA_API_TOKEN` - An API token retrieved from the Medusa settings page.
- `MEUDSA_PROCESS_METHOD` - This can be move, copy, hardlink, symlink, or reflink. View the Medusa docs for the differences.

Optionally, you may configure the following environments as well. By default, they are all set to `false`.

- `MEDUSA_FORCE_REPLACE`
- `MEDUSA_DELETE_FILES`
- `MEDUSA_IS_PRIORITY`

Refer to the Medusa docs for these settings.

Finally, if the `DEBUG` environment variable is set to true, the logs will contain the response from Medusa's post-processing API.
