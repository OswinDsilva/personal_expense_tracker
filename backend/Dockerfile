FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /usr/src/app

EXPOSE 8000

COPY pyproject.toml uv.lock ./

RUN uv sync

COPY . .

CMD ["sh","-c","uv run alembic upgrade head && uv run uvicorn backend.main:app --host 0.0.0.0 --reload"]
