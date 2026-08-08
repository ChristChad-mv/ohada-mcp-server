FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# The public image contains only the server. The private corpus is mounted or
# added by the private deployment pipeline at /data/ohada_corpus.sqlite.
COPY pyproject.toml README.md /app/
COPY src/ /app/src/

# Install Python dependencies
RUN pip install --no-cache-dir .

# Environment defaults
ENV HOST=0.0.0.0
ENV PORT=8080
ENV MCP_PATH=/mcp
ENV OHADA_DB_PATH=/data/ohada_corpus.sqlite

EXPOSE 8080

CMD ["python", "-m", "ohada_mcp.server"]
