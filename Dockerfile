FROM python:3.11-slim

MAINTAINER "parker <mailto:contact@pkrm.dev>"

WORKDIR /

COPY . .
RUN pip install -r requirements.txt

ENV IN_DOCKER Yes

ENTRYPOINT [ "python" ]
CMD [ "-u", "app/wsgi.py" ]