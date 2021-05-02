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
    PATH="$PATH:/root/.poetry/bin" \
    # Natron
    NATRON_PATH="/natron/bin" \
    PATH="$PATH:/natron" \
    NATRON_PROJECT_PATH="/app/natron"

WORKDIR /

# Add dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    ca-certificates \
    python3-pip \
    wget \
    xz-utils

# do the natron things
RUN wget https://github.com/NatronGitHub/Natron/releases/download/v2.4.0/Natron-2.4.0-Linux-64-no-installer.tar.xz --no-check-certificate \
    && tar -xvf Natron-2.4.0-Linux-64-no-installer.tar.xz \
    && mv /Natron-2.4.0-Linux-64-no-installer /natron \
    && rm Natron-2.4.0-Linux-64-no-installer.tar.xz

# do the python things
RUN pip3 install 'poetry==1.1.5'
RUN pip3 install --no-cache-dir "uvicorn[standard]" gunicorn
RUN $NATRON_PATH/natron-python -m pip install numpy

# do the app things
COPY ./pyproject.toml /tmp/
COPY ./poetry.lock /tmp/
RUN cd /tmp && poetry export -f requirements.txt > requirements.txt
RUN pip3 install -r /tmp/requirements.txt

# Cleaning cache:
RUN apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# copy over the startup stuff
COPY ./gunicorn/gunicorn_conf.py /gunicorn_conf.py
COPY ./gunicorn/start.sh /start.sh
COPY ./gunicorn/start-reload.sh /start-reload.sh
RUN chmod +x /start.sh
RUN chmod +x /start-reload.sh

# Create directories
RUN mkdir -p /app/logs
RUN mkdir -p /app/data
RUN mkdir -p /app/natron
RUN mkdir -p /app/ingredients-db
RUN mkdir -p /app/output

WORKDIR /app
ENV PYTHONPATH=/app

# expose port so we can accept input
EXPOSE $PORT

# mount the volume locally in DEV mode
FROM base AS dev
VOLUME [ "/app/app" ]
VOLUME [ "/app/data" ]
VOLUME [ "/app/natron" ]
VOLUME [ "/app/ingredients-db" ]
VOLUME [ "/app/output" ]
CMD /start-reload.sh

# just start the app normally
FROM base AS prod
COPY ./app /app/app
COPY ./data /app/data
COPY ./natron /app/natron
COPY ./ingredients-db /app/ingredients-db
CMD ["/start.sh"]