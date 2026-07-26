FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition files first for caching layers
COPY pyproject.toml uv.lock /app/

# Install dependencies using uv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application source code
COPY . /app

# Final sync to install the project if needed
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place virtual environment binaries in PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 5000

CMD ["uvicorn", "warp_proxi:app", "--host", "0.0.0.0", "--port", "5000"]
