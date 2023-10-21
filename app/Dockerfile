FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

ENV POETRY_HOME=/opt/poetry

RUN pip install --upgrade pip
RUN curl -sSL https://install.python-poetry.org | python -
ENV PATH /opt/poetry/bin:$PATH

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
COPY app ./
RUN poetry install

CMD ["main.lambda_handler"]
