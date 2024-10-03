FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app/src
COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN apt-get install certbot python3-certbot-nginx
RUN certbot --nginx -d dwbank.org -d www.dwbank.org
RUN certbot --nginx -d api.dwbank.org -d www.api.dwbank.org