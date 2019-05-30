FROM python:3

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY inotify-medusa/ .
CMD [ "python", "./inotify-medusa.py" ]
