# FROM python:3.9

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# WORKDIR /app/src
# COPY requirements.txt /requirements.txt
# RUN pip install -r /requirements.txt

# COPY src /app/src
# CMD python manage.py runserver 0:8000

FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# RUN apt-get update && apt-get install --no-install-recommends -y \
#   vim-tiny \
#   binutils \
#   libproj-dev \
#   libgmp-dev\
#   gdal-bin \
#   libsqlite3-mod-spatialite\
#  && rm -rf /var/lib/apt/lists/*

WORKDIR /app/src
RUN python -m pip install --upgrade pip
RUN pip install pip-tools
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt