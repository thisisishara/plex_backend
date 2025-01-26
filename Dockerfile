FROM sanicframework/sanic:24.12-py3.11

RUN apk update && apk add --no-cache build-base gcc python3-dev musl-dev linux-headers
RUN pip install --no-cache-dir --upgrade pip && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir poetry
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY poetry.lock pyproject.toml /app/
RUN poetry install --no-root --no-ansi

COPY ./plex/ /app/
RUN poetry build

RUN pip install dist/*.whl && rm -rf dist

EXPOSE ${PLEX_ROUTER_PORT}
CMD ["plex", "run"]
