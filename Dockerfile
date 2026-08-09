FROM python:3.14-slim@sha256:a7fb1e634c4a578f9e0bd6327f11a3cde11b7a9395f48e24360c0988bcc5c2bc

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src \
    HOME=/tmp \
    HOST=0.0.0.0 \
    PORT=8080 \
    MCP_PATH=/mcp \
    OHADA_DB_PATH=/data/ohada_corpus.sqlite \
    OHADA_SYSCOHADA_DB_PATH=/data/syscohada.sqlite

RUN groupadd --gid 10001 ohada \
    && useradd --no-log-init --uid 10001 --gid 10001 --shell /usr/sbin/nologin ohada

WORKDIR /app

# Production dependencies are resolved in uv.lock and installed only when
# their package hashes match the reviewed export.
COPY requirements-prod.txt /app/requirements-prod.txt
RUN pip install --require-hashes --no-deps -r /app/requirements-prod.txt \
    && python -m pip uninstall --yes pip setuptools wheel

# The public image contains only the server. The private corpora are mounted
# read-only under /data or added by the private deployment pipeline.
COPY src/ /app/src/

USER 10001:10001

EXPOSE 8080

CMD ["python", "-m", "ohada_mcp.server"]
