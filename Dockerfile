FROM natrongithub/natron-sdk-ubuntu20.04:latest AS base

ENV PORT=8000 \
    # python
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # poetry:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    PATH="$PATH:/root/.poetry/bin"

# Add dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y 

# do the python things
RUN pip install 'poetry==1.1.5'
RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn

# do the app things
COPY ./pyproject.toml /tmp/
COPY ./poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt > requirements.txt
RUN pip install -r /tmp/requirements.txt

# Cleaning cache:
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# copy over the startup stuff
COPY ./gunicorn/gunicorn_conf.py /gunicorn_conf.py
COPY ./gunicorn/start.sh /start.sh
COPY ./gunicorn/start-reload.sh /start-reload.sh
RUN chmod +x /start.sh
RUN chmod +x /start-reload.sh

# Create an app directory
RUN mkdir -p /app/logs

# copy everything into the container image
COPY . .
WORKDIR /app
ENV PYTHONPATH=/app

# expose port so we can accept input
EXPOSE $PORT

# mount the volume locally in DEV mode
FROM base AS dev
VOLUME [ "/app/app" ]
CMD /start-reload.sh

# just start the app normally
FROM base AS prod
COPY ./app /app/app
CMD ["/start.sh"]