PORT ?= 8000 

install:
	uv sync

lint:
	uv run ruff check
dev:
	uv run flask --app app --debug run --port 8000

start:
	uv run gunicorn --workers=4 -b 0.0.0.0:$(PORT) app:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) app:app