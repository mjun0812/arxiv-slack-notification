FROM python:3.11-bullseye


# 標準出力・標準エラーのストリームのバッファリングを行わない
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ Asia/Tokyo

ARG POETRY_VERSION="1.5.0"
ENV POETRY_HOME=/opt/poetry
ENV PATH=$POETRY_HOME/bin:$PATH

RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

RUN apt-get update \
    && apt install -y supervisor cron busybox-static curl zsh \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/*

# UTF-8 を扱う設定
RUN apt update && apt install -y locales
RUN sed -i -E 's/# (ja_JP.UTF-8)/\1/' /etc/locale.gen && \
    dpkg-reconfigure locales && \
    update-locale LANG=ja_JP.UTF-8
ENV LC_ALL ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP.UTF-8

# install python dependency
COPY pyproject.toml poetry.lock ./
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=${POETRY_VERSION} python - \
    && poetry config virtualenvs.create false \
    && poetry install

COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY --chmod=644 ./docker/cron.conf /etc/cron.d/
RUN crontab /etc/cron.d/cron.conf

CMD ["/usr/bin/supervisord"]
