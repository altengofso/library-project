FROM python:3.10.12-slim-buster AS builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y && apt-get clean

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


FROM python:3.10.12-slim-buster

RUN mkdir -p /home/app

RUN addgroup --system app && adduser --system --group app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
ENV PROJECT=library
RUN mkdir "$APP_HOME"
RUN mkdir -p "$APP_HOME/$PROJECT"/static
WORKDIR "$APP_HOME"

RUN apt-get update && apt-get install -y --no-install-recommends netcat && apt-get clean
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

COPY ./entrypoint.sh .

RUN sed -i 's/\r$//g'  "$APP_HOME/entrypoint.sh"
RUN chmod +x  "$APP_HOME/entrypoint.sh"

COPY . "$APP_HOME"

WORKDIR "$APP_HOME/$PROJECT"

RUN python manage.py collectstatic --noinput

RUN chown -R app:app "$APP_HOME"

USER app

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
