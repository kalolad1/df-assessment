.PHONY: run lint test install clean seed

install:
	uv sync --all-extras

lint:
	uv run ruff format .
	uv run ruff check . --fix
	uv run pyright

test:
	uv run pytest -v -s --disable-warnings

clean:
	rm -rf data/test.db
	rm -rf data/app.db
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

run:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down