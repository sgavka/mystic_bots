FROM postgres:17 as postgres-stage
FROM python:3.12-slim

# setup code workdir
RUN mkdir /code
WORKDIR /code
COPY . /code/

# install locales and clean up
RUN apt-get update && \
    apt-get install -y locales && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# Copy PostgreSQL binaries and libraries from the postgres image
COPY --from=postgres-stage /usr/lib/postgresql/17/ /usr/lib/postgresql/17/
COPY --from=postgres-stage /usr/bin/pg_* /usr/bin/
COPY --from=postgres-stage /usr/bin/psql /usr/bin/psql

# install requirements and clean up
RUN apt-get update && \
    apt-get install -y gettext && \
    rm -rf /var/lib/apt/lists/*

# install uv
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv

# install dependencies into /opt/venv (outside /code so volume mount doesn't hide it)
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-dev --no-install-project

# entrypoint setup
COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
