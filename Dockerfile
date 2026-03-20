FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev

COPY . .

RUN uv sync --locked --no-dev

FROM python:3.13-slim-bookworm

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:${PATH}"

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
