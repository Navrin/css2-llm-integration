FROM debian:12-slim AS builder
LABEL authors="navrin"
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes pipx
ENV PATH="/root/.local/bin:${PATH}"

RUN pipx install poetry
RUN pipx inject poetry poetry-plugin-bundle
#RUN poetry bundle venv --python=/usr/bin/python3 --only=main /venv

WORKDIR /src
COPY poetry.lock .
COPY pyproject.toml .
RUN poetry install --no-root

COPY . /src
RUN poetry install --only-root
##COPY --from=builder /venv /venv
#COPY --from=builder /src /src
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
#ENTRYPOINT ["/venv/bin/streamlit run"]
ENTRYPOINT ["poetry", "run", "streamlit", "run", "/src/css2_llm_integration/entry.py", "--server.port=8501", "--server.address=0.0.0.0"]
